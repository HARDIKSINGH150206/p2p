# Hardik prompt log

TODO (team): log prompts here (verbatim-ish, purpose, output).

## Phase 2A — forecast + attribution (~12:45 IST)
- **Prompt:** "start with my phases now ... before pushing pull the latest code"
- **Purpose:** Build src/forecast.py (ridge 6/12 h vs naive, time-ordered split) and src/insights.py (daily anomaly episodes, ordered attribution, action cards).
- **Produced:** both modules; 10 attributed episodes incl. B04 27 Aug sensor fault, B05 composter 7–13 Sep, B06 leak, B07 19 Sep, B04 inverter 6–9 Oct. Iteration: solar attribution switched from calendar event to weather (9 Oct rain 30.8 mm).
- **Real result (not hand-written):** ridge beats last-week naive in 5/8 buildings on 6 h WAPE; on 19 Sep for B07 yesterday-naive (WAPE 0.369) beat ridge (0.416). Reported as is.
## Phase 2B — Outage Drill (~12:55 IST)
- **Prompt:** continue with my phases (2B).
- **Purpose:** src/drill.py: mask hours, impute from visible hours of that day + train-only day-type profile, compare vs 4 baselines; `benchmark()` averages over all 30 test days.
- **Real result:** B04 6 h window 10:00 over 30 test days: headline MAE 1.37 kWh (MAPE 4.2%) vs flat-visible-mean 14.2, last-week 4.3, unscaled profile 4.8. The daily-total "best case" was NOT better (1.83) because daily_summary totals do not exactly match hourly sums; label kept, noted.
- **Dependency note:** drill.py defines TEST_START locally so it does not depend on the unmerged forecast branch.
- **TODO (team):**
