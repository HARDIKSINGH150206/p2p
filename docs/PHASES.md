# Phases — CircuGrid Brief (parallel plan: Hardik + Jhashank)
One-line: phase branches split between two people, built in parallel against docs/CONTRACTS.md, merged phase by phase.
Last updated: 12:35 IST

Deadline 2:00 PM. Freeze 1:15. Submit by 1:50. Working rules: docs/TEAM_WORKFLOW.md. Interfaces: docs/CONTRACTS.md.
Stack change agreed: backend = FastAPI (JSON API) so the rough HTML frontend and the final frontend both consume the same API. Streamlit is dropped.

| Phase | Branch | Owner | Files owned | Goal | Exit check | Est. | Status |
|---|---|---|---|---|---|---|---|
| 0 Data + ideation + docs | main | both | docs/, prompts/ | Locked idea, docs | Done | — | ✅ |
| 1 Pipeline | main | Hardik | src/pipeline.py | Dedupe, reindex, alias, units, note regex, outlier flag | Runs; stats printed (184 dups removed, 13 notes parsed) | — | ✅ Built (committed to main) |
| 2A Forecast + attribution | phase/forecast-attribution | **Hardik** | src/forecast.py, src/insights.py | Ridge 6h/12h per building vs 2 naive baselines, threshold anomalies, ordered attribution, action cards with evidence, B07 19 Sep card, B04 27 Aug sensor-fault | `run_forecast()` and `brief()` return contract shapes with real metrics | 35 min | 📋 |
| 2B Outage Drill | phase/outage-drill | **Hardik** | src/drill.py | Mask, impute from visible hours + day-type profile, replay, error vs baselines | `run_drill("B04","2026-10-08 10:00",6)` returns errors | 20 min | 📋 |
| 3A Bin classifier | phase/bin-classifier | **Jhashank** | src/classifier.py | 6-class model, stratified hold-out accuracy, ms/event, routing, predictions CSV | `run_classifier()` returns accuracy; CSV written | 20 min | 📋 |
| 3B Impact (+ incentive P1) | phase/impact | **Jhashank** | src/impact.py, src/incentive.py | Real-event impact (B05 landfill, B04 solar, B06 water), campus baseline, assumptions | `impact()` matches contract; numbers traceable | 20 min | 📋 |
| 4 API + rough HTML | phase/api-rough-ui | **Jhashank** (start with stubs now, wire real modules as they merge) | src/api.py, web/index.html | FastAPI endpoints + one plain HTML page showing every panel | `uvicorn src.api:app` serves `/` and all endpoints | 25 min | 📋 |
| 5 Integration + bugfix | phase/integration | both | — | Wire all real modules, fix, README run steps | End-to-end demo flow works | 15 min | 📋 |
| 6 Final frontend | phase/final-ui | **Jhashank** (+ Hardik reviews) | web/ | Polished UI on same API | Demo flow clean | after freeze, polish only | 📋 |
| 7 Demo assets | phase/demo | **Hardik** (+ Jhashank screenshots) | docs/DEMO_SCRIPT.md | 2:20 script, screenshots list, video, 3-page report, merge workbooks | Submitted by 1:50 | 1:15–1:50 | 📋 |

Load: Hardik ≈ 55 min of ML/backend (2A, 2B), Jhashank ≈ 65 min (3A, 3B, 4). If Hardik finishes first, Hardik takes Phase 5 and the 12 h horizon / drift check; if Jhashank is behind, move 3B's incentive (P1) to Hardik.

## Cut lines (in order)
Incentive ranking → drift check → HGB timing → routing → LLM text. Never cut: Drill, B07 card, classifier accuracy.

## Fallbacks
Weak forecast → show seasonal naive as the model, ridge beside it. Drill hard → flat visible-hours mean with day-type shape. B07 card fails → exam-stretch (28 Sep–9 Oct) forecast vs actual. If 2A slips, API ships with the stub for it and the rest still demos.

## Per-phase rule
On merge: update the PRD Status column and CLAUDE.md Project State for your phase.

## Update 12:55
Team decision: everything is built directly on `main` by Hardik; Jhashank's branches are not merged. Done: 1, 2A, 2B, 3A, 3B, 4 (rough). Remaining: final frontend, demo script/video, report, workbook merge.
