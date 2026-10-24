# Data Notes (Phase 0)

Campus (8 buildings) resource + waste data, 2026-06-20 → 2026-10-17 (120 days). Raw files in `data/` are untouched.

| File | Shape | What it is |
|---|---|---|
| buildings.xlsx | 8×10 | Building master: type, area, design capacity, solar kW, has_composter (B05, B06, B07 only) |
| calendar.xlsx | 120×7 | Per-day day_type (working 55, semester_break 30, weekend 24, exam 9, holiday 2), events, temp, rain, humidity |
| daily_summary.xlsx | 960×14 | Per building-day: occupancy, electricity, water, solar, waste by stream, composted, recycled, contamination %, landfill |
| hourly_streams.xlsx | 23,192×7 | Hourly electricity/water/solar/footfall per building, with `received_at` (ingestion time) |
| manual_logs.xlsx | 415×8 | Free-form staff logs: messy building names, mixed units, free-text notes |
| waste_events_train.xlsx | 6,314×10 | Sensor-bin events (weight, moisture, metal, transparency, acoustic hardness) **with `category` label** |
| waste_events_test.xlsx | 1,601×9 | Same, **no label** (to predict) |

## Quality issues
- **Nulls:** daily_summary: occupancy 5, electricity 11, water 11, wet_organic 9. hourly: 69 rows missing elec/water/footfall. Waste events: ~2% null per sensor feature (train and test).
- **Hourly duplicates:** 184 duplicate (timestamp, building) rows (23,192 vs 23,040 expected = 2,880 hours × 8). Late arrivals: `received_at` lag is usually ~1h, max ~12h.
- **Outlier:** daily B04 (Eng Labs) 2026-08-27 electricity = 6,234 kWh (typical B04 ≈ 590/day).
- **manual_logs:** 37 spellings for 8 buildings ("BH", "Girls hostle", "FC", "Canteen", "block A"...). Units mixed (kWh, units, kL, L, kg, bags). 13 rows are free-text `note` with no value, and contain real operational events (water leak, composter motor burnt, solar inverter error, meter stuck, AC left on during holiday). One value is 959,417 (unit error).
- **Class balance (train):** food_organic 1852, plastic 1722, paper_cardboard 1461, metal 608, ewaste 351, glass 320.
- Ranges: contamination_pct 4–26, moisture/metal 0–100, transparency/acoustic 0–1.

## Insights
1. **Three buildings dominate:** B05 + B06 (hostels) + B07 (food court) account for ~65% of electricity (486k of 751k kWh) and ~95% of wet organic waste (≈84k of ≈89k kg, nulls excluded).
2. **Composting works where composters exist:** composter buildings (B05–B07) compost ≈69.9 t over the period vs 0 elsewhere. Landfill from the 3 composter buildings is still ≈26.6 t of the ≈35.3 t total.
3. **Solar covers little:** B01/B04/B07 generate ≈109 MWh vs ≈751 MWh total consumption (~14%). 5 buildings have no solar.
4. **Sensor features separate classes cleanly:** food_organic = high moisture (67%), metal = high metal_signal (79) and hardness, glass = high transparency (0.64) + hardness (0.80), ewaste = heavy (606 g) + metal 56. A classifier on these 5 features should work well; test set is time-spanning (same period) so evaluate on held-out part of train.
5. **Operational anomalies are hidden in manual notes** (leaks, composter failure, inverter fault) and should align with spikes/drops in daily/hourly data → anomaly detection + log-to-insight use case.

TODO (team): confirm which insights matter for the problem statement.
