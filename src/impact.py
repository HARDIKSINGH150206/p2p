"""Sustainability impact computed from daily_summary + attributed episodes. Constants from the data guide."""
import pandas as pd

from .pipeline import load_processed
from .insights import brief, CO2_PER_KWH, RS_PER_KWH, KWH_PER_1000L

ASSUMPTIONS = {"co2_kg_per_kwh": CO2_PER_KWH, "rs_per_kwh": RS_PER_KWH, "kwh_per_1000l": KWH_PER_1000L, "compost_ratio": 4,
               "source": "docs/README_data_guide.md section 6",
               "recovery_share_default": 0.8, "recovery_share_note": "Assumption: share of the excess that would have been avoided by acting early (user slider)"}
# episodes that matter for the demo narrative: (stream, cause)
KEEP = {("solar_generation_kwh", "solar_inverter_fault"), ("landfill_kg", "composter_down"), ("composted_kg", "composter_down"),
        ("water_litres", "water_leak"), ("electricity_kwh", "event_surge")}


def impact():
    _, _, d = load_processed()
    kwh = d.electricity_kwh.sum()
    solar = d.solar_generation_kwh.sum()
    base = {
        "days": int(d.date.nunique()), "electricity_kwh": round(float(kwh)), "co2_t": round(float(kwh) * CO2_PER_KWH / 1000, 1),
        "cost_rs": round(float(kwh) * RS_PER_KWH), "solar_kwh": round(float(solar)), "solar_share_pct": round(float(solar / kwh) * 100, 1),
        "solar_co2_avoided_t": round(float(solar) * CO2_PER_KWH / 1000, 1),
        "composted_kg": round(float(d.composted_kg.sum())), "compost_produced_kg": round(float(d.composted_kg.sum()) / 4),
        "landfill_kg": round(float(d.landfill_kg.sum())), "water_litres": round(float(d.water_litres.sum())),
        "note": "electricity_kwh sum includes the flagged B04 2026-08-27 sensor-fault reading (6,234 kWh)" if d.outlier_elec.any() else "",
    }
    cards = brief(top=60)["cards"]
    events = []
    for c in cards:
        if (c["stream"], c["cause"]) in KEEP:
            events.append({k: c[k] for k in ["id", "title", "building_id", "stream", "cause", "date_range", "kwh", "rs", "co2_kg", "litres", "kg", "evidence"]}
                          | {"assumption": "excess/lost vs same-regime median baseline; avoidable share is an assumption (slider)"})
    return {"baseline": base, "events": events, "assumptions": ASSUMPTIONS,
            "excluded": "B04 2026-08-27 reading is a sensor fault (calibration note) and is not counted as savings"}


if __name__ == "__main__":
    import json
    r = impact()
    print(json.dumps(r["baseline"], indent=1))
    for e in r["events"]:
        print(e["title"], e["kwh"], e["rs"], e["co2_kg"], e["kg"], e["litres"])
