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

## Phases 3A, 3B, 4 built by Hardik on main (~12:55 IST)
- **Prompt:** "start building everything and merge directly in main ... we won't merge Jhashank's commits ... finally the frontend".
- **Produced:** src/classifier.py, src/impact.py, src/incentive.py, src/api.py, web/index.html (rough). Pushed directly to main on the team's decision.
- **Real results:** classifier hold-out accuracy 84.96% (n=1263, stratified 80/20), 5-fold CV 84.6% (RF/ET/HGB all ~84%, so no tuning on hold-out); p50 latency 4.98 ms/event; 500/408/395/160/72/66 predicted test events by class. Incentive ranking shows B02/B06/B03/B07 above-baseline use; labelled "no behaviour change measured".
- **TODO (team):** note the 85% target is just missed; decide how to word it in the pitch.

## Final frontend (~1:20 PM IST)
- **Prompt:** "we will be using the same frontend that we used in DigiVault-BFB" (+ earlier: node diagram similar).
- **Purpose:** Port DigiVault-BFB's dark theme, workspace shell and the draggable wired-card custody graph to a no-build vanilla HTML/CSS/JS frontend served by FastAPI.
- **Produced:** web/index.html, style.css, app.js. Graph: 5 sources -> fused hub -> 6 output cards with live numbers from our API; views for Brief, Forecast, Drill, Impact, Bin. Verified in headless Chrome: no console errors after fixing one syntax slip (a shell-expanded dollar-paren in a line I appended).
- **Honesty fix:** accuracy shown to 2 decimals (84.96%) because 1 decimal rounds to 85.0% and would imply the target was met.
- **TODO (team):**
