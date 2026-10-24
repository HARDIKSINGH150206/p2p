# Hardik prompt log

TODO (team): log prompts here (verbatim-ish, purpose, output).

## Phase 2A — forecast + attribution (~12:45 IST)
- **Prompt:** "start with my phases now ... before pushing pull the latest code"
- **Purpose:** Build src/forecast.py (ridge 6/12 h vs naive, time-ordered split) and src/insights.py (daily anomaly episodes, ordered attribution, action cards).
- **Produced:** both modules; 10 attributed episodes incl. B04 27 Aug sensor fault, B05 composter 7–13 Sep, B06 leak, B07 19 Sep, B04 inverter 6–9 Oct. Iteration: solar attribution switched from calendar event to weather (9 Oct rain 30.8 mm).
- **Real result (not hand-written):** ridge beats last-week naive in 5/8 buildings on 6 h WAPE; on 19 Sep for B07 yesterday-naive (WAPE 0.369) beat ridge (0.416). Reported as is.
- **TODO (team):**
