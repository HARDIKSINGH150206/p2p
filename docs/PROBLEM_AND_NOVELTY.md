# Problem & Novelty
One-line: turn noisy campus utility and waste data into forecasts, explained causes and actions.
Last updated: 12:15 IST

## Problem (our words)
Campuses track electricity, water and waste by hand per building, so problems are seen days late, spikes are not predicted and nobody knows the cause. Data from sensors, meters and staff logs disagrees, arrives late or is missing.

## Why it matters (from DATA_NOTES.md, 120 days, 8 buildings)
- 2 hostels + food court use ~65% of electricity (486k of 751k kWh) and ~95% of wet organic waste.
- Solar covers ~14.6% of consumption; 5 of 8 buildings have none.
- Composting diverts 69.9 t, yet 26.6 t still goes to landfill from the 3 composter buildings.
- Manual notes record a leak, a dead composter and a solar inverter fault that raw dashboards would not explain.

## Existing approaches and gaps (general)
- Manual audits: lagging, inconsistent. Basic dashboards: show what, not why. Single-stream tools: ignore links between energy, water and waste.

## Our solution (CircuGrid Brief)
1. Fuse hourly meters, daily summaries, calendar and messy manual logs; offline buildings stay on the grid.
2. Forecast 6–12 h, attribute anomalies to a cause (note, event, day type, sensor fault) with an evidence line, rank actions.
3. Show impact computed from the data, an edge-sized bin classifier, and an incentive baseline.

## Novelty (status: all 📋 Planned)
- **Outage Drill:** knock a building offline, impute from visible hours + day-type profile, reconnect and show measured error vs naive baselines.
- Free-text notes become attributed causes, including sensor-fault causes (B04 6,234 kWh on 27 Aug linked to the calibration note, not counted as waste).
- Evidence line on every recommendation.
- Verified real events used as the demo (B04 inverter 6–9 Oct, B05 composter 7–14 Sep, B07 alumni meet 19 Sep).

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
