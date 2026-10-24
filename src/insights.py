"""Daily anomaly episodes -> ordered attribution -> ranked action cards with evidence lines.

Baseline: per building, per stream, median of days in the same regime (break / weekend+holiday / working / exam).
A day is flagged when its robust z-score passes Z_FLAG in the stream's bad direction.
Attribution order: (1) same-building manual note near the episode and compatible with the stream,
(2) calendar event on an episode day, (3) day-type regime shift, (4) heavy rain, else unexplained.
"""
import numpy as np
import pandas as pd

from .pipeline import load_processed
from .forecast import run_forecast

CO2_PER_KWH, RS_PER_KWH, KWH_PER_1000L = 0.70, 8.0, 0.85
Z_FLAG = 5.0
# stream -> (bad direction, min days) ; solar/compost fail low, others spike high
STREAMS = {
    "solar_generation_kwh": -1, "composted_kg": -1,
    "electricity_kwh": +1, "water_litres": +1, "landfill_kg": +1,
}
COMPAT = {  # note causes that can explain a stream's anomaly
    "solar_generation_kwh": {"solar_inverter_fault", "solar_inverter_fixed"},
    "composted_kg": {"composter_down", "composter_fixed"},
    "landfill_kg": {"composter_down", "composter_fixed"},
    "water_litres": {"water_leak", "meter_issue"},
    "electricity_kwh": {"sensor_calibration", "energy_left_on", "event_surge", "meter_issue"},
}
REGIME = {"working": "working", "exam": "exam", "weekend": "weekend", "holiday": "weekend", "semester_break": "break"}


def _episodes(d, cal):
    d = d.merge(cal[["date", "day_type", "event", "rainfall_mm"]], on="date", how="left")
    d["regime"] = d.day_type.map(REGIME)
    rows = []
    for bid, g in d.groupby("building_id"):
        for s, direction in STREAMS.items():
            if s == "solar_generation_kwh" and g[s].max() == 0:
                continue
            if s == "composted_kg" and g[s].max() == 0:
                continue
            base = g.groupby("regime")[s].transform("median")
            mad = g.groupby("regime")[s].transform(lambda x: (x - x.median()).abs().median())
            scale = np.maximum(mad, 0.05 * base.abs()) + 1e-6  # floor so tiny MAD does not explode z
            z = direction * 0.6745 * (g[s] - base) / scale
            flag = z > Z_FLAG
            gg = g.assign(stream=s, base=base, z=z, flag=flag)
            gg = gg.sort_values("date")
            cur = None
            for _, r in gg.iterrows():
                if r.flag:
                    if cur and (pd.Timestamp(r.date) - pd.Timestamp(cur["end"])).days <= 1:
                        cur["days"].append(r)
                        cur["end"] = r.date
                    else:
                        cur = {"building_id": bid, "stream": s, "start": r.date, "end": r.date, "days": [r]}
                        rows.append(cur)
                else:
                    pass
    return rows


def _attribute(ep, notes):
    s, bid = ep["stream"], ep["building_id"]
    a, b = pd.Timestamp(ep["start"]) - pd.Timedelta(days=1), pd.Timestamp(ep["end"]) + pd.Timedelta(days=1)
    n = notes[(notes.building_id == bid) & (pd.to_datetime(notes.date) >= a) & (pd.to_datetime(notes.date) <= b)]
    hit = n[n.cause.isin(COMPAT[s])]
    if len(hit):
        r = hit.iloc[0]
        return "note", r.cause, f"manual log {r.log_id} ({r.date}): \"{r.note}\""
    if s == "solar_generation_kwh":  # events/regimes do not plausibly explain solar; weather does
        if max(r.rainfall_mm for r in ep["days"]) > 20:
            rr = max(ep["days"], key=lambda r: r.rainfall_mm)
            return "weather", "heavy_rain", f"rainfall {rr.rainfall_mm} mm on {rr.date} (calendar)"
        return "none", "unexplained", "no note or weather explains it"
    for r in ep["days"]:
        if isinstance(r.event, str):
            return "event", "calendar_event", f"calendar {r.date}: {r.event}"
    if ep["days"][0].regime in ("exam", "break"):
        return "regime", "day_type_shift", f"episode falls in {ep['days'][0].regime} regime"
    if max(r.rainfall_mm for r in ep["days"]) > 20:
        return "weather", "heavy_rain", "rainfall above 20 mm on an episode day"
    return "none", "unexplained", "no note, event, regime shift or weather explains it"


def _card(ep, kind, cause, evidence, notes, fc):
    s, bid = ep["stream"], ep["building_id"]
    days = ep["days"]
    actual = sum(r[s] for r in days)
    base = sum(r.base for r in days)
    delta = actual - base
    out = {"id": f"{bid}_{s}_{ep['start']}", "building_id": bid, "stream": s, "date_range": [ep["start"], ep["end"]],
           "n_days": len(days), "cause": cause, "attribution": kind, "evidence": evidence,
           "baseline": round(base, 1), "actual": round(actual, 1), "max_z": round(float(max(r.z for r in days)), 1),
           "kwh": None, "rs": None, "co2_kg": None, "litres": None, "kg": None}
    if s == "solar_generation_kwh":
        lost = base - actual
        out.update(kwh=round(lost, 1), rs=round(lost * RS_PER_KWH), co2_kg=round(lost * CO2_PER_KWH, 1))
        out["title"] = f"{bid} solar down {len(days)} day(s): ~{lost:.0f} kWh lost"
        out["action"] = ("Weather-driven dip; no action." if cause == "heavy_rain" else "Check inverter and restore generation; log the fix in manual_logs.")
    elif s == "composted_kg":
        out["kg"] = round(base - actual, 1)
        out["title"] = f"{bid} composting stopped {len(days)} day(s): {base - actual:.0f} kg not composted"
        out["action"] = "Repair composter; route wet waste to another composter meanwhile."
    elif s == "landfill_kg":
        out["kg"] = round(delta, 1)
        out["title"] = f"{bid} landfill +{delta:.0f} kg over baseline in {len(days)} day(s)"
        out["action"] = "Check composter and segregation at source."
    elif s == "water_litres":
        kwh = delta / 1000 * KWH_PER_1000L
        out.update(litres=round(delta), kwh=round(kwh, 1), rs=round(kwh * RS_PER_KWH), co2_kg=round(kwh * CO2_PER_KWH, 1))
        out["title"] = f"{bid} water +{delta / 1000:.0f} kL over baseline in {len(days)} day(s)"
        out["action"] = "Inspect pipes/meter for leak; read meter manually to confirm."
    else:  # electricity
        if cause == "sensor_calibration":
            out["title"] = f"{bid} electricity reading {actual:.0f} kWh is a sensor fault, not consumption"
            out["action"] = "Verify power analyzer calibration; exclude reading from savings."
            out["confidence"] = "high"
            return out
        out.update(kwh=round(delta, 1), rs=round(delta * RS_PER_KWH), co2_kg=round(delta * CO2_PER_KWH, 1))
        out["title"] = f"{bid} electricity +{delta:.0f} kWh over baseline on {ep['start']}"
        out["action"] = ("Pre-plan load and staffing for known events; " if cause == "calendar_event" else "Investigate load; ") + "shift flexible loads off the peak."
        if bid == "B07" and fc:
            m = [x for x in fc["metrics"] if x["building_id"] == "B07" and x["window"] == "alumni_19sep" and x["horizon_h"] == 6]
            out["forecast_check"] = {x["model"]: {"mae": x["mae"], "wape": x["wape"]} for x in m}
    out["confidence"] = {"note": "high", "event": "medium", "regime": "low", "weather": "low", "none": "none"}[kind]
    return out


def brief(top=12):
    _, m, d = load_processed()
    cal = pd.read_excel("data/calendar.xlsx")
    notes = m[m.stream == "note"].copy()
    try:
        fc = run_forecast(include_hgb_timing=False)
    except Exception:
        fc = None
    eps = _episodes(d, cal)
    cards, counts = [], {"attributed": 0, "unexplained": 0}
    for ep in eps:
        # ignore the B04 daily electricity outlier calibration reading only via attribution (kept as a card)
        kind, cause, ev = _attribute(ep, notes)
        counts["unexplained" if kind == "none" else "attributed"] += 1
        cards.append(_card(ep, kind, cause, ev, notes, fc))
    order = {"high": 0, "medium": 1, "low": 2, "none": 3}
    cards.sort(key=lambda c: (order[c["confidence"]], -c["max_z"]))
    return {"cards": cards[:top], "n_episodes": len(eps), "attribution_counts": counts}


if __name__ == "__main__":
    import json
    r = brief(top=40)
    print(r["attribution_counts"], r["n_episodes"])
    for c in r["cards"]:
        print(c["confidence"], c["date_range"], c["building_id"], c["stream"], c["cause"], "|", c["title"], "| z", c["max_z"])
