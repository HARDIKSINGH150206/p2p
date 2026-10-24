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

## Landing page (~1:35 PM IST)
- **Prompt:** "https://ui.aceternity.com/pages/inference-landing-page ... this should be the landing page ... professional ... node diagram will be same"
- **Purpose:** Build a landing page in the style of that template (dark, tilt-in dashboard hero, tabbed features, drag-and-wire canvas, dot map, developer panel, comparison table, dithered CTA), with the same wired graph.
- **Produced:** web/index.html, landing.css, landing.js; split shared graph into common.js; moved workspace to /app (app.html, workspace.js); new GET /api/buildings. Pricing section replaced by an honest 'against the problem statement' status table and a labelled hardware-budget assumption; no invented users or testimonials.
- **Checked:** headless Chrome desktop + 390px mobile, no console errors (one harmless ResizeObserver notice).
- **TODO (team):**

## Overview dashboard + hardening (~1:45 PM IST)
- **Prompt:** "make the dashboard and harden the frontend ... should wow ... most professional ... visually appealing"
- **Produced:** web/dashboard.js + dashboard.css (Overview): KPI cards with count-up and sparklines; stacked daily chart with metric tabs, building toggles, hover tooltip and real event pins (staff notes, calendar); building-day anomaly heatmap normalised by day type; Needs-attention panel; 8 building cards; waste-flow bars; accuracy ring; B07 forecast mini-chart. Backend: /api/timeseries, /api/health, background cache warm-up, gzip.
- **Hardening:** HTML-escaping of dataset text, network-error boxes with Retry, skeleton loaders, reduced-motion support, focus outlines, responsive breakpoints, no content hidden by animation.
- **Known gaps:** B04's share on cards still includes the flagged 6,234 kWh reading (chart shows it at median); not tested by hand-clicking.
- **TODO (team):**

## Interactive dashboard + landing SaaS sections (~2:40 PM IST)
- **Prompt:** "make the landing page according to the reference and professional... the dashboard component that is not working make it work ... most sections look hard coded"
- **Method:** wrote a Chrome DevTools test driver (no Playwright available) and clicked every control: all views, tabs, toggles, tooltips, graph, drill. Result: nothing was throwing errors; the problem was that the dashboard felt hard-coded (every card opened the same page, Forecast/Brief had no selectors).
- **Produced:** building detail drawer (card/heatmap row/attention item), Forecast explorer for any building x horizon x window via new /api/forecast/{bid}, Brief filters, favicon; landing: live stats strip, 3-step how-it-works, deployment plans (hardware = N x Rs 12,000 assumption, subscription pricing explicitly 'not set'), live-data FAQ, full footer.
- **Bug found by test:** duplicate element ids (section and inner list both 'plans'/'faq') made the script overwrite the section; fixed by renaming inner ids.
- **Final checks:** 0 console errors on /app and /.
- **TODO (team):**
