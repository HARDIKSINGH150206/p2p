# PRD — Predictive Circular-Resource Grid
One-line: an AI control room that fuses campus energy, water and waste data, forecasts spikes, explains anomalies and nudges occupants to cut waste.
Last updated: 11:30 IST
> Assumption: we are building Concept A (recommended in Phase 1). Nothing is coded yet, so features are 📋 Planned unless stated.

## Problem
Campus facilities rely on manual per-building audits that lag by days, cannot forecast spikes (exams, events, mess rush) and cannot say *why* usage rose (problem statement). Data is noisy: 184 duplicate hourly rows, late arrivals, nulls, 37 spellings of 8 buildings in manual logs.

## Personas
| Persona | Pain |
|---|---|
| Facilities manager | Finds out about leaks/faults days late; no ranked list of what to fix |
| Hostel warden / mess supervisor | Wet waste and energy spike with no warning; logs are manual and inconsistent |
| Student / building occupant | No visibility of own building's footprint, no reason to change habits |

## Goals / Non-goals
- Goals: working end-to-end app on the real dataset covering the 8 problem-statement constraints at prototype level.
- Non-goals (4 h): real edge hardware deployment, real camera/computer vision, live sensors, user accounts, mobile app, proven behaviour change.

## Features
| Feature | Description | Priority | Status |
|---|---|---|---|
| Data profiling | Shape, nulls, quality issues, insights | P0 | ✅ Built (docs/DATA_NOTES.md) |
| Data cleaning + fusion | Dedup hourly, handle late data, normalise manual-log names/units, fill gaps, keep offline buildings | P0 | 📋 Planned |
| Live Grid dashboard | Campus + per-building energy/water/solar/footfall, offline/buffered status | P0 | 📋 Planned |
| Smart-bin classifier | 6-class model on 5 sensor features, held-out accuracy, confusion matrix, ms/event | P0 | 📋 Planned |
| Forecast | 6–12 h ahead per building vs naive baseline, with MAE | P0 | 📋 Planned |
| Root-cause + actions | Anomaly flags matched to manual notes/calendar, ranked explainable recommendations | P1 | 📋 Planned |
| Impact view | CO2, Rs, water-energy, compost computed from data, assumptions shown | P0 | 📋 Planned |
| Incentive leaderboard | Building score from diversion/contamination/usage vs baseline | P1 | 📋 Planned |
| LLM recommendation text | Optional, template fallback offline | P2 | 📋 Planned |
| Test predictions CSV | `waste_events_test_predictions.csv` (event_id, predicted_class) | P1 | 📋 Planned |

## User flow
1. Open app (`streamlit run app.py`); see campus KPIs on top.
2. Pick building / date range in sidebar.
3. Review Live Grid, including any building flagged offline.
4. Open Forecast to see next 6–12 h demand and baseline comparison.
5. Open Root-Cause to see flagged anomalies with probable cause and ranked actions.
6. Open Smart Bin to see classifier accuracy and classify sample events.
7. Open Impact/Incentives to see savings and the building leaderboard.

## Success metrics (measurable)
- Classifier accuracy on held-out split of train file (target >85% per problem statement; actual TBD).
- Forecast MAE vs naive baseline on held-out last days (TBD).
- Per-event inference time in ms (TBD).
- Share of records recovered by cleaning (rows deduped, names resolved) — computed by pipeline.
- Anomalies matched to a manual note or calendar event (count, TBD).

## Sustainability impact
Computed from `daily_summary` with data-guide constants (0.70 kg CO2/kWh, Rs 8/kWh, 0.85 kWh/1000 L, 4:1 compost). Baselines from data:
| Item | Value | How |
|---|---|---|
| Grid electricity, 120 days | 750,969 kWh | sum of electricity_kwh (nulls excluded) |
| Implied CO2 / cost | 525.7 t / Rs 6.0 M | kWh × 0.70 / × 8 |
| Solar generated | 109,417 kWh (14.6%) | sum of solar_generation_kwh; ≈76.6 t CO2 avoided |
| Composted | 69,898 kg → ≈17,475 kg compost | composted_kg / 4 |
| Landfill | 35,339 kg | sum of landfill_kg |
Savings from our recommendations are 📋 Planned and will be shown as scenarios ("Estimate (assumption: X% reduction)"), not claimed results.
