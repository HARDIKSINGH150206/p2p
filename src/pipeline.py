"""Load raw xlsx, clean and fuse. Raw files in data/ are never modified; outputs go to data/processed/."""
import re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data"
PROC = ROOT / "data" / "processed"

ALIASES = {
    "b01": "B01", "academic block a": "B01", "acad block a": "B01", "block a": "B01",
    "b02": "B02", "academic block b": "B02", "acad block b": "B02", "block b": "B02",
    "b03": "B03", "central library": "B03", "central lib": "B03", "library": "B03",
    "b04": "B04", "engineering labs & innovation centre": "B04", "eng labs": "B04",
    "labs": "B04", "innovation centre": "B04",
    "b05": "B05", "boys hostel": "B05", "boys hostle": "B05", "bh": "B05",
    "b06": "B06", "girls hostel": "B06", "girls hostle": "B06", "gh": "B06",
    "b07": "B07", "food court": "B07", "fc": "B07", "canteen": "B07",
    "b08": "B08", "admin block": "B08", "admin": "B08",
}
UNIT_FACTOR = {"kWh": 1.0, "units": 1.0, "L": 1.0, "kL": 1000.0, "kg": 1.0, "bags": 8.0}
UNIT_TARGET = {"electricity": "kWh", "water": "L", "waste": "kg"}
# regex table for the free-text notes: (pattern, cause tag)
NOTE_CAUSES = [
    (r"leak|wet patch|meter running fast", "water_leak"),
    (r"composter.*(not working|burnt)", "composter_down"),
    (r"composter.*(replaced|working again)", "composter_fixed"),
    (r"inverter.*(error|red)", "solar_inverter_fault"),
    (r"inverter.*(reset|generating)", "solar_inverter_fixed"),
    (r"calibrat", "sensor_calibration"),
    (r"stuck at zero|display flickers|reading seems|reading looked odd", "meter_issue"),
    (r"ac and lights|left on", "energy_left_on"),
    (r"alumni|expecting \d+", "event_surge"),
]
# plausibility ceilings per stream (after unit conversion) to reject unit errors
PLAUSIBLE_MAX = {"electricity": 20000, "water": 1_000_000, "waste": 2000}


def load_raw():
    names = ["buildings", "calendar", "daily_summary", "hourly_streams",
             "manual_logs", "waste_events_train", "waste_events_test"]
    return {n: pd.read_excel(RAW / f"{n}.xlsx") for n in names}


def clean_hourly(h, calendar):
    """Dedupe on (timestamp, building) keeping latest received_at, reindex to the full hourly grid."""
    h = h.copy()
    h["timestamp"] = pd.to_datetime(h["timestamp"])
    h["received_at"] = pd.to_datetime(h["received_at"])
    n_raw = len(h)
    h = h.sort_values("received_at").drop_duplicates(["timestamp", "building_id"], keep="last")
    n_dup = n_raw - len(h)
    h["lag_h"] = (h["received_at"] - h["timestamp"]).dt.total_seconds() / 3600
    idx = pd.MultiIndex.from_product(
        [pd.date_range("2026-06-20 00:00", "2026-10-17 23:00", freq="h"), sorted(h.building_id.unique())],
        names=["timestamp", "building_id"])
    g = h.set_index(["timestamp", "building_id"]).reindex(idx).reset_index()
    cols = ["electricity_kwh", "water_litres", "solar_generation_kwh", "footfall"]
    g["missing"] = g[cols].isna().any(axis=1)
    g = g.sort_values(["building_id", "timestamp"])
    for c in cols:  # gap-fill so models never drop an offline building; raw NaN kept via `missing`
        g[c + "_filled"] = g.groupby("building_id")[c].transform(lambda s: s.interpolate(limit=6, limit_direction="both").ffill().bfill())
    g["date"] = g.timestamp.dt.strftime("%Y-%m-%d")
    cal = calendar.rename(columns={"date": "date"})
    g = g.merge(cal[["date", "day_type", "event", "avg_temp_c", "rainfall_mm", "humidity_pct"]], on="date", how="left")
    g["hour"] = g.timestamp.dt.hour
    stats = {"hourly_rows_raw": int(n_raw), "hourly_duplicates_removed": int(n_dup),
             "hourly_grid_rows": int(len(g)), "hourly_gap_rows": int(g.missing.sum()),
             "late_arrival_max_h": round(float(h.lag_h.max()), 1)}
    return g, stats


def clean_manual(m):
    m = m.copy()
    m["building_id"] = m.building.str.strip().str.lower().map(ALIASES)
    stats = {"manual_rows": int(len(m)), "manual_alias_unresolved": int(m.building_id.isna().sum()),
             "manual_distinct_spellings": int(m.building.nunique())}
    m["value_std"] = np.where(m.value.notna(), m.value * m.unit.map(UNIT_FACTOR).fillna(1.0), np.nan)
    ceil = m.stream.map(PLAUSIBLE_MAX)
    m["rejected"] = m.value_std > ceil
    stats["manual_values_rejected"] = int(m.rejected.sum())
    m["date"] = m.logged_at.str[:10]
    def tag(t):
        if not isinstance(t, str):
            return None
        for pat, cause in NOTE_CAUSES:
            if re.search(pat, t, re.I):
                return cause
        return "other_note"
    m["cause"] = [tag(t) if s == "note" else None for t, s in zip(m.note, m.stream)]
    stats["manual_notes_parsed"] = int((m.stream == "note").sum())
    return m, stats


def clean_daily(d):
    """Flag robust-z outliers per building as suspected sensor faults (linked to notes later)."""
    d = d.copy()
    for c in ["electricity_kwh", "water_litres"]:
        med = d.groupby("building_id")[c].transform("median")
        mad = d.groupby("building_id")[c].transform(lambda s: (s - s.median()).abs().median()) + 1e-9
        d[c + "_z"] = 0.6745 * (d[c] - med) / mad
    d["outlier_elec"] = d.electricity_kwh_z.abs() > 12
    return d


def build():
    PROC.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    h, s1 = clean_hourly(raw["hourly_streams"], raw["calendar"])
    m, s2 = clean_manual(raw["manual_logs"])
    d = clean_daily(raw["daily_summary"])
    h.to_csv(PROC / "hourly_clean.csv", index=False)
    m.to_csv(PROC / "manual_clean.csv", index=False)
    d.to_csv(PROC / "daily_clean.csv", index=False)
    stats = {**s1, **s2, "daily_elec_outliers": int(d.outlier_elec.sum())}
    pd.Series(stats).to_json(PROC / "pipeline_stats.json")
    return raw, h, m, d, stats


def load_processed():
    h = pd.read_csv(PROC / "hourly_clean.csv", parse_dates=["timestamp", "received_at"])
    m = pd.read_csv(PROC / "manual_clean.csv")
    d = pd.read_csv(PROC / "daily_clean.csv")
    return h, m, d


if __name__ == "__main__":
    _, _, m, d, st = build()
    for k, v in st.items():
        print(k, v)
    print(d[d.outlier_elec][["date", "building_id", "electricity_kwh"]])
    print(m[m.stream == "note"][["date", "building_id", "cause"]].to_string())
