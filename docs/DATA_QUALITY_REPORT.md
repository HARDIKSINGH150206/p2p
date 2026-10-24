# Data Quality & Integrity Report — P2P Campus Telemetry Dataset

**Scope:** All 7 dataset files in `Data/` (120 days, 20 Jun – 17 Oct 2026, 8 buildings)
**Tooling:** `Data_cleaning/eda_check.py` (reproduce with `python Data_cleaning/eda_check.py`)
**Companion implementation:** `Data_cleaning/data_pipeline.py` performs every repair listed here.

---

## 1. Verdict

The dataset is coherent, join-safe, and deliberately salted with four engineering
stressors that mirror the problem statement's data challenges. No fatal corruption
exists, but four concrete cleaning jobs must be solved (Section 6). One
reconciliation property discovered during audit is the single most valuable
fact for the entire fusion architecture (Section 5).

| File | Rows | Integrity status |
|---|---|---|
| `buildings.xlsx` | 8 | Clean — no nulls, no duplicate ids |
| `calendar.xlsx` | 120 | Clean — contiguous dates, no gaps, no dups |
| `daily_summary.xlsx` | 960 | Near-clean — ~1% nulls, one mass-identity mismatch |
| `hourly_streams.xlsx` | 23,192 | Engineered mess — duplicates, dropouts, NaNs (Section 4) |
| `manual_logs.xlsx` | 415 | Human chaos — 37 building aliases, mixed units (Section 5) |
| `waste_events_train.xlsx` | 6,314 | Trap file — 5.8:1 class imbalance + ~2% missing sensors |
| `waste_events_test.xlsx` | 1,601 | Same 2% missingness pattern as train |

---

## 2. Cross-file integrity (all PASS)

- All `daily_summary` dates ⊆ `calendar` dates; hourly timestamps inside calendar window
- All 415 manual logs fall inside the 120-day window
- `event_id` train↔test overlap: **0**; duplicate ids: **0**
- Reference rules hold globally: solar > 0 only at B01/B04/B07 (0 violations),
  composted > 0 only at B05/B06/B07 (0 violations)
- Event volume per building follows population intuition: Food Court (1,583 train events)
  > hostels (~1,100) > admin (178)

## 3. Campus-level totals over 120 days

| Quantity | Total | Note |
|---|---|---|
| Grid electricity | 750,969 kWh | ~6.3 MWh/day campus |
| Solar generation | 109,417 kWh | 14.6% solar share (B01/B04/B07 only) |
| Water | 20,961 kL | |
| Waste generated | 125,006 kg | wet 61.4 t / dry 43.4 t / ewaste+hazard small |
| Diverted (composted+recycled) | 90,309 kg | **72.2% diversion rate baseline** |
| Landfill residual | 34,315 kg | |

## 4. `hourly_streams.xlsx` — the four engineered stressors (measured)

| Stressor | Measurement |
|---|---|
| Conflicting retransmissions | 184 duplicate (building, timestamp) pairs, of which **183 carry different values** — not exact copies. Deterministic winner rule required; keeping latest `received_at` alone is insufficient |
| Real packet loss | 32 missing hours across B02(5), B03(4), B04(14), B06(2), B07(7). Longest contiguous outage: **7 h** (B04, B07) — matches the problem statement's "buildings lose connectivity for hours at a time" |
| Buffered bursts | 186 rows delivered 4–12 h late (median base latency is a tight ~1.1 h) |
| Missing readings | 69 NaNs in electricity/water/footfall; solar is never NaN |

Sanity checks that passed: 0 rows with `received_at` before `timestamp`; 0 negative
readings; 0 solar generation at night; 27 daytime zero-solar hours (consistent with
overcast/monsoon days).

## 5. Key fusion finding — hourly ↔ daily reconciliation

On clean building-days, `hourly_streams` daily sums match `daily_summary` totals with a
**median absolute error of 0.03 kWh / 1.0 L**. The ~68–71 divergent building-days
(>5 kWh) all coincide with dropout or NaN days, and the hourly sum is **always lower**
than the daily value.

**Implication (design decision):** `daily_summary` is the authoritative source for
gap repair. Corrupt/conflicting/missing hourly readings are re-derived from daily
totals; on days when a daily value itself is null (11 electricity, 11 water rows),
profile-based imputation is the fallback. This satisfies the "reconcile conflicting
or delayed updates without corrupting the dashboard" constraint with evidence rather
than assumption.

Secondary integrity note in `daily_summary`: waste mass identity
`composted + recycled + landfill = generated` holds only approximately — 100/960 rows
differ by >0.2 kg; net 642 kg (0.5%) shortfall over the term. Treated as a metering
inconsistency (the "conflicting readings" scenario), not silently ignored.

## 6. Cleaning jobs (implemented in `data_pipeline.py`)

1. **Deduplicate** hourly telemetry — deterministic rule: prefer the row with more
   non-null metrics; tie-break on latest `received_at`.
2. **Rebuild the hourly grid** to the full 8 × 2,880 hours; repair the 32 lost hours
   and 69 NaN metrics from authoritative daily totals, distributed over the missing
   slots using that building's median hourly profile (per day type). Fallback:
   profile-average fill when the daily anchor is itself null. Footfall (no daily
   source) gets profile-median fill.
3. **Normalize manual logs** — 37 building strings → 8 canonical ids
   (`Acad Block A`, `block A`, `academic block a` … all → `B01`; `BH`/`Boys Hostle` →
   `B05`; `FC`/`Canteen` → `B07`; etc.), convert `units`→kWh (×1), `kL`→L (×1000),
   `bags`→kg (×8), separate the 13 narrative notes from numeric readings.
4. **Impute** the 36 daily nulls (building + day-type medians) and ~2% sensor nulls
   in waste events (per-class medians from train; same imputer applied to test).

## 7. Waste classifier signal (EDA baseline)

| Finding | Value |
|---|---|
| Class balance | food_organic 1,852 · plastic 1,722 · paper 1,461 · metal 608 · ewaste 351 · glass 320 (**5.8 : 1**) |
| Sensor ranges | all in valid physical range (0–100 %, 0–1 coeff, 5–2,293 g) |
| Class separability | strong signatures — metal_signal 79 (metal) vs 56 (ewaste); transparency 0.64 (glass) / 0.49 (plastic) vs ≤0.14 (others); food moisture 67 |
| Baseline CV accuracy | `HistGradientBoostingClassifier` on 5 raw sensors, 5-fold: **0.837 ± 0.005** |

The 85% problem-statement target therefore requires ~1.5 pp of deliberate work
(feature interactions, imbalance handling, tuning) — reachable, and grading should
report macro-F1 + confusion matrix, not accuracy alone.
