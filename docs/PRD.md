# PRD — CircuGrid Brief
One-line: an offline-proof campus grid that forecasts spikes, names the cause and ranks the fix, built on the 8-building campus dataset.
Last updated: 12:15 IST
Source of truth for scope: `docs/ideation/FINAL.md` (v3, evaluator 8.3/10, not formally approved). Status = actual code state: nothing is built yet.

## Problem
Facilities teams audit buildings by hand, so faults and surges are seen days late and nobody links staff notes to meter data (problem statement). Real examples in the data: B04 solar was 0 kWh on 6–8 Oct while a staff note said "inverter showing red error light"; B05's composter was down 7–13 Sep (composted_kg = 0) and nobody noticed.

## Personas
| Persona | Pain |
|---|---|
| Facilities engineer (assumption: 1–2 people for 8 buildings) | Walk-through audits; evidence scattered across meters, notes, 37 building spellings |
| Hostel warden / mess supervisor | Surges (e.g. B07 alumni meet, 19 Sep) and composter failures appear after the fact |
| Sustainability / campus admin | Needs numbers (kWh, Rs, CO2, landfill) with stated assumptions |

## Goals / Non-goals
- Goals: working Streamlit app on the real data covering the problem statement's constraints at prototype level; every number computed from data.
- Non-goals (this build): real edge hardware or camera frames, live feeds, accounts, measured behaviour change, large model search.

## Features
| Feature | Description | Priority | Status |
|---|---|---|---|
| Data profiling | Shape, nulls, quality issues, insights | P0 | ✅ Built (DATA_NOTES.md) |
| Fusion + cleaning | Dedupe hourly, reindex to full grid, alias dict (37→8), unit fix, 13-note regex table, outlier/sensor-fault flag | P0 | ✅ Built (src/pipeline.py) |
| Brief: forecast + root cause + actions | Ridge 6 h (and 12 h) forecast vs 2 naive baselines, threshold anomalies, attribution (note → event → day type → weather → unexplained), ranked actions with evidence lines | P0 | ✅ Built, merged (src/forecast.py, src/insights.py) |
| Forward-looking card | B07 19 Sep held-out forecast vs actual, MAE/WAPE vs naive | P0 | 📋 Planned |
| Outage Drill | Hide hours, impute from visible hours + day-type profile, replay, error vs baselines | P0 | ✅ Built, merged (src/drill.py) |
| Impact view | kWh, Rs, CO2, landfill, water from data; assumptions; labelled scenario | P0 | ✅ Built (src/impact.py; rough HTML tab) |
| Edge bin classifier panel | 6 classes, stratified held-out accuracy, ms/event, compost/recycle routing, predictions CSV | P0-lite | ✅ Built (src/classifier.py): hold-out acc 84.96%, CV 84.6% — just under the 85% target |
| Incentive ranking | Saved vs own baseline per occupant, "no behaviour change measured" | P1 (first cut) | ✅ Built (src/incentive.py) |
| Sensor-drift check | Rolling residual mean | P1 | 📋 Planned |
| LLM brief text | Optional Claude call; regex/template fallback | P2 | 📋 Planned |

## User flow
1. Open app: Brief shows B04 inverter and B05 composter cards within 20 s.
2. Click B07 19 Sep card: forecast vs actual, calendar-event cause, MAE/WAPE vs naive.
3. Outage Drill: pick building + 6 h window → "offline, estimated" → Reconnect → error vs baselines.
4. Impact: kWh, Rs, CO2, landfill; scenario label.
5. Bin panel: accuracy, ms/event, routing.

## Success metrics (measured in app)
- Classifier held-out accuracy (target >85% from problem statement; actual TBD).
- Forecast MAE/WAPE vs naive per building (TBD).
- Drill MAE/MAPE vs baselines (TBD).
- Flags attributed vs "unexplained" (TBD).
- Rows deduped, aliases resolved (from pipeline).

## Sustainability impact
Formulas (guide constants: 0.70 kg CO2/kWh, Rs 8/kWh, 0.85 kWh/1000 L, compost 4:1) applied to real events, computed live: excess B05 landfill 7–13 Sep; lost B04 solar 6–8 Oct; B06 excess water 5–10 Aug. Campus baseline from data: 750,969 kWh (≈525.7 t CO2, Rs 6.0 M); solar 109,417 kWh (14.6%); composted 69,898 kg. Savings are "avoidable if caught" and scenarios, with a recovery-share slider (assumption).
