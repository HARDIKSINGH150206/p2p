"""
Full data-integrity + EDA sweep across all 7 P2P dataset files.
Run:  python eda_check.py
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows console (cp1252) safety

DATA = Path(__file__).resolve().parents[1] / "Data"  # datasets live under <repo>/Data/


def r(name):
    return pd.read_excel(DATA / name)

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 60)


def hdr(title):
    print("\n" + "=" * 78)
    print(f"### {title}")
    print("=" * 78)


# ─────────────────────────── 1. BUILDINGS ───────────────────────────
hdr("1. BUILDINGS")
b = r("buildings.xlsx")
print(b.to_string(index=False))
print("nulls:", b.isna().sum().sum(), "| dup building_id:", b.duplicated("building_id").sum())

# ─────────────────────────── 2. CALENDAR ───────────────────────────
hdr("2. CALENDAR")
c = r("calendar.xlsx")
c["date"] = pd.to_datetime(c["date"])
print("range:", c.date.min().date(), "->", c.date.max().date(), "| rows:", len(c))
print("date diffs unique:", c.date.sort_values().diff().dt.days.dropna().value_counts().to_dict())
print("dup dates:", c.date.duplicated().sum())
print("day_type:", c.day_type.value_counts().to_dict())
print("nulls:", c.isna().sum().to_dict())
ev = c.dropna(subset=["event"])
print("event rows:", len(ev), "| events during exam days:", len(ev[ev.day_type == "exam"]))
for col in ["avg_temp_c", "rainfall_mm", "humidity_pct"]:
    print(f"{col}: min={c[col].min()} max={c[col].max()} nulls={c[col].isna().sum()}")

# ─────────────────────────── 3. DAILY SUMMARY ───────────────────────────
hdr("3. DAILY SUMMARY")
ds = r("daily_summary.xlsx")
ds["date"] = pd.to_datetime(ds["date"])
print("shape:", ds.shape, "| buildings:", ds.building_id.nunique(), "| dates:", ds.date.nunique())
print("rows per building:", ds.groupby("building_id").size().to_dict())
print("nulls:", ds.isna().sum().div(len(ds)).mul(100).round(2)[lambda s: s > 0].to_dict(),
      "(percent of rows)")
num = ds.select_dtypes("number")
print("negative values:", (num < 0).sum()[lambda s: s > 0].to_dict() or "none",
      "| occupancy rows <=0:", int((ds.occupancy_avg <= 0).sum()))

# waste-mass identity check: total generated vs (composted + recycled + landfill)
ds["waste_total_kg"] = ds[["wet_organic_kg", "dry_recyclable_kg", "ewaste_kg", "hazardous_kg"]].sum(axis=1)
ds["diverted_kg"] = ds[["composted_kg", "recycled_kg"]].sum(axis=1)
ds["residual_calc"] = (ds.waste_total_kg - ds.diverted_kg).clip(lower=0)
diff = (ds.landfill_kg - ds.residual_calc).abs()
print("landfill identity check: rows where |landfill - (total-diverted)| > 0.2 kg:",
      (diff > 0.2).sum(), "of", len(ds))

# circular-resource-rule checks
solar_expected = dict(zip(b.building_id, b.has_solar))
comp_expected = dict(zip(b.building_id, b.has_composter))
solar_bad = ds[(ds.building_id.map(solar_expected) == 0) & (ds.solar_generation_kwh > 0)]
comp_bad = ds[(ds.building_id.map(comp_expected) == 0) & (ds.composted_kg > 0)]
print("solar>0 for no-solar buildings:", len(solar_bad), "| composted>0 for no-composter buildings:", len(comp_bad))
solar_missing = ds[(ds.building_id.map(solar_expected) == 1) & (ds.solar_generation_kwh == 0)]
print("solar==0 full days for solar buildings (could be weather):", len(solar_missing))

# zero-waste rows sanity (labs/admin produce little; check for dead days)
zero_days = ds[ds.waste_total_kg < 0.5]
print("near-zero waste days per building:", zero_days.groupby("building_id").size().to_dict())

# ─────────────────────────── 4. HOURLY STREAMS ───────────────────────────
hdr("4. HOURLY STREAMS")
h = r("hourly_streams.xlsx")
h.columns = ["timestamp", "received_at", "building_id", "electricity_kwh", "water_litres",
             "solar_generation_kwh", "footfall"]
h["timestamp"] = pd.to_datetime(h["timestamp"])
h["received_at"] = pd.to_datetime(h["received_at"])
print("shape:", h.shape, "| buildings:", h.building_id.nunique(),
      "| range:", h.timestamp.min(), "->", h.timestamp.max())

# duplicates
dup_key = h.duplicated(subset=["building_id", "timestamp"], keep=False)
print("rows involved in dup (building,timestamp):", int(dup_key.sum()), "pairs:", dup_key.sum() // 2)
# are dup values identical?
dups = h[dup_key].sort_values(["building_id", "timestamp"])
mismatch = dups.groupby(["building_id", "timestamp"]).electricity_kwh.nunique()
print("dup groups with differing electricity:", int((mismatch > 1).sum()), "of", len(mismatch))
retrans = dups.groupby(["building_id", "timestamp"])["received_at"].nunique()
print("dup groups with >1 distinct received_at (retransmission):", int((retrans > 1).sum()))

# exact full-row duplicates
print("exact full-row dups:", h.duplicated().sum())

# coverage / gaps
print("rows per building:", h.groupby("building_id").size().to_dict())
full_grid = pd.date_range("2026-06-20", "2026-10-17 23:00", freq="h")
for bid in sorted(h.building_id.unique()):
    have = set(h.loc[h.building_id == bid, "timestamp"])
    miss = len(full_grid.difference(have))
    print(f"  {bid}: missing hours = {miss} of {len(full_grid)}")
# contiguous dropout runs per building (missing houses on the hourly grid)
def runs_of(mask):
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        return 0, 0
    splits = np.split(idx, np.where(np.diff(idx) != 1)[0] + 1)
    lens = [len(s) for s in splits]
    return max(lens), sum(lens)

miss_by_b = {}
for bid in sorted(h.building_id.unique()):
    have = full_grid.isin(set(h.loc[h.building_id == bid, "timestamp"]))
    longest, total = runs_of(np.asarray(~have))
    miss_by_b[bid] = (longest, total)
print("dropout stats per building (longest outage h, total outage h):", miss_by_b)

# received lag behaviour
lag = (h.received_at - h.timestamp).dt.total_seconds() / 3600
lag = lag[lag >= 0]
print("received-lag (h): median={:.2f} p95={:.2f} max={:.2f}".format(
    lag.median(), lag.quantile(0.95), lag.max()))
print("lag buckets:", pd.cut(lag, [-0.01, 1, 4, 12, 48, 1e6],
      labels=["<=1h", "1-4h", "4-12h", "12-48h", ">48h"]).value_counts().to_dict())
neg_lag = (h.received_at < h.timestamp).sum()
print("received_at BEFORE timestamp (corrupt rows):", neg_lag)

# value quality
print("nulls:", h.isna().sum().to_dict())
print("negative readings:", (h[["electricity_kwh", "water_litres", "solar_generation_kwh", "footfall"]] < 0).sum().sum())
print("solar at night (hours 0-5 or 19-23):",
      h[(h.solar_generation_kwh > 0) & (h.timestamp.dt.hour.isin(list(range(0, 6)) + list(range(19, 24))))].shape[0])
# solar buildings only
solar_h = h[(h.building_id.map(solar_expected) == 0) & (h.solar_generation_kwh > 0)]
print("solar>0 at no-solar buildings:", len(solar_h))

# daytime zero-solar hours for solar buildings
solar_bids = [bid for bid in b.building_id if solar_expected[bid] == 1]
day = h[h.building_id.isin(solar_bids) & h.timestamp.dt.hour.isin(range(8, 17))]
print("daytime (8-17h) rows for solar buildings:", len(day),
      "| zero-solar daytime rows:", int((day.solar_generation_kwh == 0).sum()))

# footfall patterns
print("footfall: max per hour:", h.footfall.max(), "| null/null combos ok")

# ─────────────────────────── 5. MANUAL LOGS ───────────────────────────
hdr("5. MANUAL LOGS")
m = r("manual_logs.xlsx")
print("shape:", m.shape, "| distinct building strings:", m.building.nunique())
print("stream counts:", m["stream"].value_counts().to_dict())
print("unit counts:", m.unit.value_counts().to_dict())
print("null values:", m.isna().sum().to_dict())
notes = m[m["stream"] == "note"]
print("note rows:", len(notes), "| note rows with a numeric value:", int(notes.value.notna().sum()))
print("value null per stream:", m.groupby("stream").value.apply(lambda s: s.isna().sum()).to_dict())
# unit vs stream mismatch (e.g. electricity logged in kL)
expected_units = {"electricity": ["kWh", "units"], "water": ["L", "kL"],
                  "waste": ["kg", "bags"], "note": [None, "none"]}
bad = m[m.apply(
    lambda r: isinstance(r.unit, str) and expected_units.get(r.stream, [r.unit])[0] is not None
              and r.unit not in expected_units.get(r.stream, []), axis=1)]
print("stream/unit mismatches:", len(bad))
if len(bad):
    print(bad[["logged_at", "building", "stream", "value", "unit"]].head(10).to_string(index=False))
# plausibility: electricity in kWh vs units; kL vs L magnitudes
e = m[m["stream"] == "electricity"].dropna(subset=["value"])
print("electricity value range:", e.value.min(), "-", e.value.max(), "| kL-as-water max:",
      m[(m.stream == 'water') & (m.unit == 'kL')].value.max())
print("logged_at range:", m.logged_at.min(), "-", m.logged_at.max())
print("distinct logs per building-string top8:", m.building.value_counts().head(8).to_dict())

# ─────────────────────────── 6. WASTE EVENTS ───────────────────────────
hdr("6. WASTE EVENTS (train & test)")
tr = r("waste_events_train.xlsx")
te = r("waste_events_test.xlsx")
print("train:", tr.shape, "| test:", te.shape)
print("train class balance:", tr.category.value_counts().to_dict())
print("train nulls:", tr.isna().sum().to_dict() or "none")
print("test nulls:", te.isna().sum().to_dict() or "none")
feats = ["weight_g", "moisture_pct", "metal_signal", "transparency", "acoustic_hardness"]
for f in feats:
    print(f"  {f:17s} train: min={tr[f].min():8.3f} max={tr[f].max():8.3f} | "
          f"test: min={te[f].min():8.3f} max={te[f].max():8.3f}")
print("test out-of-range moisture (<0 or >100):",
      int(((te.moisture_pct < 0) | (te.moisture_pct > 100)).sum()),
      "| transparency outside 0-1:", int(((te.transparency < 0) | (te.transparency > 1)).sum()),
      "| acoustic outside 0-1:", int(((te.acoustic_hardness < 0) | (te.acoustic_hardness > 1)).sum()))
print("event_id overlap train-test:", len(set(tr.event_id) & set(te.event_id)))
print("event_id dup in train:", tr.event_id.duplicated().sum(), "| in test:", te.event_id.duplicated().sum())
print("train date range:", tr.timestamp.min(), "->", tr.timestamp.max())
print("train rows per building:", tr.building_id.value_counts().to_dict())

# per-class sensor signature means
print("\nper-class sensor means (train):")
print(tr.groupby("category")[feats].mean().round(2).to_string())

# quick separation sanity: fit tiny model (may be slow → skip heavy; just logistic quick check)
try:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import cross_val_score
    X = tr[feats].values
    y = tr.category.values
    scores = cross_val_score(HistGradientBoostingClassifier(max_iter=200), X, y, cv=5, scoring="accuracy")
    print("\nbaseline CV accuracy (HistGradientBoosting, NaN-native): %.3f +/- %.3f" % (scores.mean(), scores.std()))
except ImportError:
    print("\nsklearn not available - skipping baseline CV")

# ─────────────────────────── 7. CROSS-FILE CHECKS ───────────────────────────
hdr("7. CROSS-FILE CHECKS")
# dates align with calendar
print("daily_summary dates ⊆ calendar dates:", ds.date.isin(set(c.date)).all())
# hourly date range vs calendar
print("hourly timestamps ⊆ calendar window:",
      h.timestamp.max() <= c.date.max() + pd.Timedelta(hours=23),
      h.timestamp.min() >= c.date.min())
# manual log date range within calendar
mg = pd.to_datetime(m.logged_at, errors="coerce")
print("manual logs inside calendar window:", (mg >= c.date.min()).sum(), "/", len(m), "valid-range")
# spot-check: hourly totals vs daily summary for one building-week
h["d"] = h.timestamp.dt.floor("D")
agg = (h.groupby(["building_id", "d"])[["electricity_kwh", "water_litres", "solar_generation_kwh"]].sum()
        .add_suffix("_hourly"))
j = agg.reset_index().merge(ds, left_on=["building_id", "d"], right_on=["building_id", "date"])
j = j.dropna(subset=["electricity_kwh", "water_litres"])
j["e_diff"] = (j.electricity_kwh_hourly - j.electricity_kwh).abs()
print("hourly-day sums join:", len(j), "building-days | median abs diff kWh:", round(j.e_diff.median(), 2))
print("rows with diff>5 kWh:", int((j.e_diff > 5).sum()))
print("\nDONE.")
