# Problem & Novelty
One-line: turn noisy campus utility and waste data into forecasts, explained causes and actions.
Last updated: 11:30 IST

## Problem (our words)
Campuses track electricity, water and waste by hand per building, so problems are seen days late, spikes are not predicted and nobody knows the cause. Data from sensors, meters and staff logs disagrees, arrives late or is missing.

## Why it matters (from DATA_NOTES.md, 120 days, 8 buildings)
- 2 hostels + food court use ~65% of electricity (486k of 751k kWh) and ~95% of wet organic waste.
- Solar covers ~14.6% of consumption; 5 of 8 buildings have none.
- Composting diverts 69.9 t, yet 26.6 t still goes to landfill from the 3 composter buildings.
- Manual notes record a leak, a dead composter and a solar inverter fault that raw dashboards would not explain.

## Existing approaches and gaps (general)
- Manual audits: lagging, inconsistent. Basic dashboards: show what, not why. Single-stream tools: ignore links between energy, water and waste.

## Our solution
1. Clean and fuse hourly, daily, bin and manual data without dropping offline buildings.
2. Classify bin events, forecast demand 6–12 h ahead, flag and explain anomalies.
3. Show impact computed from the data and rank building actions with a leaderboard.

## Novelty (each tied to a feature; status as of now)
- Fusion of 4 asynchronous sources incl. messy manual logs — 📋 Planned.
- Anomaly cause attributed using manual notes + calendar events — 📋 Planned.
- Edge-sized classifier with measured latency — 📋 Planned.
- Offline-safe recommendations (LLM optional, templates fallback) — 📋 Planned.
- Impact tied to energy–water–waste together, assumptions visible — 📋 Planned.

## Impact & scalability
- Beneficiaries: facilities teams, hostel/mess staff, occupants.
- Size: baseline spend on this campus is Rs 6.0 M electricity over 120 days (computed); any saving is a scenario, not a result.
- Path to deployment: pilot on a few buildings with real meters and bins → extend by building_id (Planned).

## Judging criteria map
| Criterion | How we address it | Evidence |
|---|---|---|
| Relevance & sustainability | Energy, water, waste, composting, solar | DATA_NOTES.md, Impact tab 📋 |
| Impact & scalability | Per-building design, scenarios | ARCHITECTURE doc, Impact tab 📋 |
| AI, prompting, dataset | ML models on all 7 files, prompt workbook | PROMPT_WORKBOOK.md, models 📋 |
| Feasibility / works | Streamlit app on real data | app.py 📋 |
| Demo & pitch | 2:20 script | DEMO_SCRIPT.md 📋 |
