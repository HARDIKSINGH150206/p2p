"""
P2P Data Cleaning Pipeline (Steps 1-2 deliverable)
==================================================
Reads the raw xlsx tables from  <repo>/Data/  and writes cleaned, analysis-ready
CSV tables + a JSON log to  <repo>/Data_cleaning/cleaned/.

Repairs implemented (evidence in Docs/DATA_QUALITY_REPORT.md):
  1. Deterministic dedup of hourly telemetry (184 conflicting retransmissions).
  2. Full 8 x 2,880-hour grid rebuild; 32 dropped hours + 69 NaN metrics repaired
     from authoritative daily totals (clean-day agreement: 0.03 kWh) distributed
     over missing slots with per-building/per-day-type hourly profiles; fallback
     profile fill when the daily anchor is null. Footfall gets profile fill.
  3. Manual logs: 37 building-name aliases -> 8 canonical ids; unit conversions
     (units->kWh, kL->L, bags->kg); narrative notes separated from readings.
  4. Imputation of 36 daily nulls (building x day-type medians) and ~2% sensor
     nulls in waste events (per-class medians from train; same rule for test).

Run:  python Data_cleaning/data_pipeline.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
OUT = Path(__file__).resolve().parent / "cleaned"

HOURS = pd.date_range("2026-06-20 00:00", "2026-10-17 23:00", freq="h")   # 2,880 hrs
METRICS = ["electricity_kwh", "water_litres", "solar_generation_kwh", "footfall"]
PROF_METRICS = ["electricity_kwh", "water_litres", "solar_generation_kwh"]
SENSOR_COLS = ["weight_g", "moisture_pct", "metal_signal", "transparency", "acoustic_hardness"]
CLASSES = {"food_organic", "paper_cardboard", "plastic", "glass", "metal", "ewaste"}

LOG: dict = {}


def put(key, value):
    LOG[key] = value


def load_raw() -> dict:
    d = {}
    for name in ["buildings", "calendar", "daily_summary", "hourly_streams",
                 "manual_logs", "waste_events_train", "waste_events_test"]:
        d[name] = pd.read_excel(DATA / f"{name}.xlsx")
    d["calendar"]["date"] = pd.to_datetime(d["calendar"]["date"])
    d["daily_summary"]["date"] = pd.to_datetime(d["daily_summary"]["date"])
    h = d["hourly_streams"]
    h["timestamp"] = pd.to_datetime(h["timestamp"])
    h["received_at"] = pd.to_datetime(h["received_at"])
    d["waste_events_train"]["timestamp"] = pd.to_datetime(d["waste_events_train"]["timestamp"])
    d["waste_events_test"]["timestamp"] = pd.to_datetime(d["waste_events_test"]["timestamp"])
    d["manual_logs"]["logged_at"] = pd.to_datetime(d["manual_logs"]["logged_at"], errors="coerce")
    return d


# ============================================================ 1. DEDUP ======
def dedup_hourly(h: pd.DataFrame) -> pd.DataFrame:
    """Winner per (building_id, timestamp): more non-null metrics wins;
    on a tie the latest received_at wins. Deterministic and auditable."""
    h = h.copy()
    h["_completeness"] = h[METRICS].notna().sum(axis=1)
    n_pairs = int(h.duplicated(subset=["building_id", "timestamp"], keep=False).sum() // 2)
    h = (h.sort_values(["building_id", "timestamp", "_completeness", "received_at"])
           .drop_duplicates(subset=["building_id", "timestamp"], keep="last")
           .drop(columns="_completeness"))
    put("hourly.duplicate_pairs_resolved", n_pairs)
    put("hourly.rows_after_dedup", int(len(h)))
    return h


# ================================================= 2. GRID REBUILD+REPAIR ===
def build_profiles(h: pd.DataFrame) -> dict:
    """Median hourly profile per building per day_type (and a day-type-agnostic
    fallback) computed ONLY from fully-complete days (24 slotted days, no NaN)."""
    cal = pd.read_excel(DATA / "calendar.xlsx", parse_dates=["date"])
    dtype_map = dict(zip(cal.date.dt.normalize(), cal.day_type))

    h = h.copy()
    h["d"] = h.timestamp.dt.normalize()
    h["day_type"] = h["d"].map(dtype_map)
    h["hour"] = h.timestamp.dt.hour
    complete = h.dropna(subset=METRICS)
    per_day = complete.groupby(["building_id", "d"]).size()
    complete_days = per_day[per_day == 24].reset_index()[["building_id", "d"]]
    comp = complete.merge(complete_days[["building_id", "d"]], on=["building_id", "d"])
    prof_dt = comp.groupby(["building_id", "day_type", "hour"])[PROF_METRICS + ["footfall"]].median()
    prof_g = comp.groupby(["building_id", "hour"])[PROF_METRICS + ["footfall"]].median()
    put("profiles.complete_days_used", int(len(complete_days)))
    return {"by_daytype": prof_dt, "global": prof_g, "dtype_map": dtype_map,
            "b_medians": h.groupby("building_id")[PROF_METRICS + ["footfall"]].median()}


def repair_hourly(h: pd.DataFrame, daily: pd.DataFrame, profiles: dict) -> pd.DataFrame:
    """Reindex to the full grid, then repair lost hours + NaN metrics.
    Anchor-present days: redistribute daily_total - observed_sum over the day's
    missing slots, weighted by the building/day-type profile (solar restricted
    to daytime where possible). Anchor-null days: pure profile fill.
    Finally a conflict-resolution sweep forces any remaining stream-vs-daily
    disagreement on anchor-present days proportional to the authoritative daily
    total, so dashboard campus totals stay consistent."""
    prof_dt, prof_g = profiles["by_daytype"], profiles["global"]
    dtype_map, b_med = profiles["dtype_map"], profiles["b_medians"]

    rows = []
    for bid in sorted(h.building_id.unique()):
        sub = h[h.building_id == bid].set_index("timestamp")
        rows.append(sub.reindex(HOURS).reset_index().rename(columns={"index": "timestamp"})
                    .drop(columns=["building_id"], errors="ignore"))
        rows[-1].insert(1, "building_id", bid)
    g = pd.concat(rows, ignore_index=True)
    g["d"] = g.timestamp.dt.normalize()
    g["day_type"] = g["d"].map(dtype_map)
    g["hour"] = g.timestamp.dt.hour
    put("grid.total_slots", int(len(g)))

    # provenance: which slots existed in the raw stream at all?
    stream_keys = pd.MultiIndex.from_arrays([h.building_id, h.timestamp])
    keys = pd.MultiIndex.from_arrays([g.building_id, g.timestamp])
    not_in_stream = ~keys.isin(stream_keys.unique())
    pre_nan = g[METRICS].isna().any(axis=1)
    g["repaired"] = not_in_stream | pre_nan
    put("grid.slots_inserted_for_outages", int(not_in_stream.sum()))
    put("grid.rows_value_repaired_inplace", int((~not_in_stream & pre_nan).sum()))
    put("grid.nan_cells_before_repair", int(h[METRICS].isna().sum().sum()))

    daily_anchor = daily.set_index(["building_id", "date"])

    def prof_val(bid, dt, hour, metric):
        w = prof_dt.get((bid, dt, hour), None)
        w = w[metric] if w is not None else np.nan
        if pd.isna(w):
            w = prof_g.loc[(bid, hour), metric] if (bid, hour) in prof_g.index else np.nan
        if pd.isna(w):
            w = b_med.loc[bid, metric]
        return float(w)

    stats = {"anchor_null_days": 0, "profile_filled_slots": 0,
             "deficit_kwh_redistributed": 0.0, "deficit_l_redistributed": 0.0,
             "solar_deficit_kwh_redistributed": 0.0, "solar_uniform_night_cases": 0}
    for (bid, day), grp in g.groupby(["building_id", "d"], sort=True):
        if not grp[METRICS].isna().any(axis=1).any():
            continue
        anchor = daily_anchor.loc[(bid, day)] if (bid, day) in daily_anchor.index else None
        for metric in PROF_METRICS:
            target_idx = grp.index[grp[metric].isna()]
            if len(target_idx) == 0:
                continue
            day_total = anchor[metric] if anchor is not None and pd.notna(anchor.get(metric)) else np.nan
            hours_arr = g.loc[target_idx, "hour"].values
            if pd.notna(day_total):
                deficit = max(float(day_total) - float(grp[metric].sum()), 0.0)
                weights = np.array([prof_val(bid, grp.at[i, "day_type"], grp.at[i, "hour"], metric)
                                    for i in target_idx], dtype=float)
                weights[weights < 0] = 0.0
                daytime_targets = ((hours_arr >= 5) & (hours_arr <= 19)).any()
                if metric == "solar_generation_kwh" and daytime_targets:
                    night = (hours_arr < 5) | (hours_arr > 19)
                    weights[night] = 0.0                                   # keep physics
                if weights.sum() <= 0:
                    weights = np.ones(len(weights))
                    if metric == "solar_generation_kwh":
                        stats["solar_uniform_night_cases"] += 1
                g.loc[target_idx, metric] = deficit * weights / weights.sum()
                if metric == "electricity_kwh":
                    stats["deficit_kwh_redistributed"] += deficit
                elif metric == "water_litres":
                    stats["deficit_l_redistributed"] += deficit
                else:
                    stats["solar_deficit_kwh_redistributed"] += deficit
            else:
                stats["anchor_null_days"] += 1
                for i in target_idx:
                    g.at[i, metric] = max(prof_val(bid, grp.at[i, "day_type"],
                                                   grp.at[i, "hour"], metric), 0.0)
                    stats["profile_filled_slots"] += 1
        for i in grp.index[grp["footfall"].isna()]:
            g.at[i, "footfall"] = max(prof_val(bid, grp.at[i, "day_type"],
                                               grp.at[i, "hour"], "footfall"), 0.0)

    # --- conflict-resolution sweep: on anchor-present days the hourly stream and
    #     the daily table can disagree on a *complete* day (the "conflicting
    #     readings" scenario). Authoritative rule: scale proportionally to daily.
    sweep = {"electricity_kwh_days": 0, "water_litres_days": 0, "solar_days": 0}
    for (bid, day), grp in g.groupby(["building_id", "d"], sort=True):
        anchor = daily_anchor.loc[(bid, day)] if (bid, day) in daily_anchor.index else None
        if anchor is None:
            continue
        for metric, eps, logkey in [("electricity_kwh", 0.05, "electricity_kwh_days"),
                                    ("water_litres", 0.5, "water_litres_days"),
                                    ("solar_generation_kwh", 0.02, "solar_days")]:
            day_total = anchor[metric] if pd.notna(anchor.get(metric)) else np.nan
            if pd.isna(day_total):
                continue
            s = float(grp[metric].sum())
            if abs(s - float(day_total)) > eps and s > 0:
                g.loc[grp.index, metric] = (g.loc[grp.index, metric] * (float(day_total) / s))
                sweep[logkey] += 1
    put("repair.stats", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in stats.items()})
    put("repair.conflicts_resolved", sweep)

    g["received_at"] = g.received_at.fillna(
        g.timestamp + pd.Timedelta(hours=1))                 # nominal lag for inserted rows
    g["footfall"] = g["footfall"].clip(lower=0).round().astype("int64")
    g[["electricity_kwh", "water_litres", "solar_generation_kwh"]] = \
        g[["electricity_kwh", "water_litres", "solar_generation_kwh"]].clip(lower=0).round(2)
    return g[["timestamp", "received_at", "building_id"] + METRICS + ["d", "day_type", "hour",
                                                                     "repaired"]]


# ================================================= 3. MANUAL LOGS ===========
ALIAS_MAP = {
    "b01": "B01", "acad block a": "B01", "academic block a": "B01", "block a": "B01",
    "b02": "B02", "acad block b": "B02", "academic block b": "B02", "block b": "B02",
    "b03": "B03", "central library": "B03", "central lib": "B03", "library": "B03",
    "b04": "B04", "engineering labs & innovation centre": "B04",
    "innovation centre": "B04", "eng labs": "B04", "labs": "B04",
    "b05": "B05", "bh": "B05", "boys hostel": "B05", "boys hostle": "B05",
    "b06": "B06", "gh": "B06", "girls hostel": "B06", "girls hostle": "B06",
    "b07": "B07", "fc": "B07", "food court": "B07", "canteen": "B07",
    "b08": "B08", "admin": "B08", "admin block": "B08",
}
UNIT_FIX = {"units": ("kWh", 1.0), "kwh": ("kWh", 1.0),
            "kl": ("L", 1000.0), "l": ("L", 1.0),
            "bags": ("kg", 8.0), "kg": ("kg", 1.0)}


def clean_manual_logs(m: pd.DataFrame) -> pd.DataFrame:
    m = m.copy()
    m["building_clean"] = m.building.str.strip().str.lower()
    unknown = sorted(set(m.building_clean.unique()) - set(ALIAS_MAP))
    put("manual.unmapped_buildings", unknown)
    m["building_id"] = m["building_clean"].map(ALIAS_MAP)
    unit_norm = m.unit.str.strip().str.lower().map(UNIT_FIX)
    m["unit_canonical"] = unit_norm.map(lambda t: t[0] if isinstance(t, tuple) else np.nan)
    m["unit_factor"] = unit_norm.map(lambda t: t[1] if isinstance(t, tuple) else np.nan)
    m["value_cleaned"] = m["value"] * m["unit_factor"].fillna(1.0)
    m["date"] = m.logged_at.dt.normalize()
    m["is_note"] = m["stream"].str.strip().str.lower().eq("note")
    put("manual.rows", int(len(m)))
    put("manual.notes_separated", int(m.is_note.sum()))
    put("manual.readings_normalized", int((~m.is_note).sum()))
    return m[["log_id", "logged_at", "date", "building_id", "building", "logger_role",
              "stream", "value", "unit", "value_cleaned", "unit_canonical",
              "is_note", "note"]]


# ================================================= 4. IMPUTATION ============
def clean_daily(ds: pd.DataFrame, cal: pd.DataFrame) -> pd.DataFrame:
    ds = ds.copy()
    dtype_map = dict(zip(cal.date, cal.day_type))
    ds["day_type"] = ds.date.map(dtype_map)
    cols = ["occupancy_avg", "electricity_kwh", "water_litres", "wet_organic_kg"]
    nulls_before = int(ds[cols].isna().sum().sum())
    for col in cols:
        ds[col] = ds.groupby(["building_id", "day_type"])[col].transform(
            lambda s: s.fillna(s.median()))
        ds[col] = ds[col].fillna(ds[col].median())          # degenerate-group fallback
    put("daily.nulls_imputed", nulls_before)
    put("daily.nulls_after", int(ds[cols].isna().sum().sum()))
    return ds.drop(columns=["day_type"])


def clean_waste_events(train: pd.DataFrame, test: pd.DataFrame) -> tuple:
    tr, te = train.copy(), test.copy()
    put("waste.train_nulls_before", int(tr[SENSOR_COLS].isna().sum().sum()))
    put("waste.test_nulls_before", int(te[SENSOR_COLS].isna().sum().sum()))
    med_per_class = tr.groupby("category")[SENSOR_COLS].median()
    med_global = tr[SENSOR_COLS].median()
    for df in (tr, te):
        for col in SENSOR_COLS:
            if "category" in df.columns:
                df[col] = df[col].fillna(df.category.map(med_per_class[col]))
            df[col] = df[col].fillna(med_global[col])
    put("waste.train_nulls_after", int(tr[SENSOR_COLS].isna().sum().sum()))
    put("waste.test_nulls_after", int(te[SENSOR_COLS].isna().sum().sum()))
    return tr, te


# ================================================= 5. VERIFICATION ==========
def verify(g, daily_raw, ds_clean, m, tr, te) -> bool:
    daily_raw = daily_raw.copy()
    daily_raw["date"] = pd.to_datetime(daily_raw["date"])

    agg = (g.groupby(["building_id", "d"])[["electricity_kwh", "water_litres",
                                            "solar_generation_kwh"]].sum()
             .reset_index().rename(columns={"d": "date"}))
    j = agg.merge(daily_raw[["building_id", "date", "electricity_kwh", "water_litres"]],
                  on=["building_id", "date"], how="left", suffixes=("_hourly", "_raw"))
    j = j.merge(ds_clean[["building_id", "date", "electricity_kwh", "water_litres"]]
                .rename(columns={"electricity_kwh": "e_daily", "water_litres": "w_daily"}),
                on=["building_id", "date"], how="left")
    j["e_anchor"] = j["electricity_kwh_raw"]
    j["w_anchor"] = j["water_litres_raw"]
    j["ed"] = (j["electricity_kwh_hourly"] - j["e_daily"]).abs()
    j["wd"] = (j["water_litres_hourly"] - j["w_daily"]).abs()
    jf = j.dropna(subset=["e_anchor", "w_anchor"])                  # anchor-present days

    print("\n" + "=" * 72 + "\nVERIFICATION\n" + "=" * 72)
    ok = True

    def check(name, cond, extra=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {extra}")

    check("hourly grid 8x2880", len(g) == 23040 and g.timestamp.nunique() == 2880,
          f"rows={len(g)} hours={g.timestamp.nunique()}")
    check("no duplicate (building,timestamp)", not g.duplicated(['building_id', 'timestamp']).any())
    n_nan = int(g[METRICS].isna().sum().sum())
    check("zero NaN metric cells", n_nan == 0, f"(remaining={n_nan})")
    check("all metrics non-negative", (g[METRICS] >= 0).all().all())
    check("footfall is integer", g.footfall.dtype.kind in "iu")
    check("reconciliation on anchor-present days |dKwh|<=0.5",
          (jf.ed <= 0.5).all(), f"max={jf.ed.max():.3f} kWh")
    check("reconciliation on anchor-present days |dL|<=5",
          (jf.wd <= 5).all(), f"max={jf.wd.max():.2f} L")
    check("manual logs -> 8 canonical ids, all mapped",
          m.building_id.nunique() == 8 and m.building_id.notna().all(),
          f"ids={m.building_id.nunique()}")
    check("manual units normalized to {kWh,L,kg}",
          m.unit_canonical.dropna().isin(["kWh", "L", "kg"]).all())
    check("waste train sensors complete", not tr[SENSOR_COLS].isna().any().any())
    check("waste test sensors complete", not te[SENSOR_COLS].isna().any().any())
    check("waste classes intact", set(tr.category.unique()) == CLASSES)
    print("\nRESULT: " + ("ALL CHECKS PASSED" if ok else "CHECKS CONTAIN FAILURES"))
    put("verification.passed", ok)
    return ok


# ================================================= 6. MAIN ==================
def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    print("P2P data cleaning pipeline\n")
    raw = load_raw()
    print("loaded rows:", {k: len(v) for k, v in raw.items()})

    h = dedup_hourly(raw["hourly_streams"])
    profiles = build_profiles(h)
    g = repair_hourly(h, raw["daily_summary"], profiles)

    ds_raw = raw["daily_summary"]
    ds = clean_daily(ds_raw, raw["calendar"])
    m = clean_manual_logs(raw["manual_logs"])
    tr, te = clean_waste_events(raw["waste_events_train"], raw["waste_events_test"])

    passed = verify(g, ds_raw, ds, m, tr, te)

    if m.building_id.isna().any():
        raise SystemExit("Unmapped manual-log buildings remain; aborting write-out.")

    writes = {
        "buildings.csv": raw["buildings"],
        "calendar.csv": raw["calendar"].assign(date=lambda x: x.date.dt.date),
        "daily_clean.csv": ds.assign(date=lambda x: x.date.dt.date),
        "hourly_clean.csv": g.assign(
            timestamp=lambda x: x.timestamp.dt.strftime("%Y-%m-%d %H:%M"),
            received_at=lambda x: x.received_at.dt.strftime("%Y-%m-%d %H:%M"),
            d=lambda x: x.d.dt.date),
        "manual_logs_clean.csv": m.assign(
            logged_at=lambda x: x.logged_at.dt.strftime("%Y-%m-%d %H:%M")),
        "waste_events_train_clean.csv": tr,
        "waste_events_test_clean.csv": te,
    }
    for fname, df in writes.items():
        df.to_csv(OUT / fname, index=False)
    with open(OUT / "cleaning_log.json", "w", encoding="utf-8") as fh:
        json.dump(LOG, fh, indent=2, default=str)

    print("\nwrote ->", OUT)
    for f in sorted(OUT.iterdir()):
        print(f"    {f.name:32s} {f.stat().st_size/1024:9.1f} KB")
    print("\ncleaning_log.json summary:")
    print(json.dumps(LOG, indent=2, default=str))
    if not passed:
        raise SystemExit("Verification failed - cleaned outputs are INVALID.")


if __name__ == "__main__":
    main()
