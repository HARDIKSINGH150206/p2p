# Phases — CircuGrid Brief
One-line: execution plan with deadlines, deliverables and exit checks per phase.
Last updated: 12:15 IST

Hard deadline 2:00 PM IST. MVP by 12:45, feature freeze 1:15, submit by 1:50. Plan from FINAL.md is ~90 min of work, so we are already tight: expect to use cut lines.

| Phase | Window | Goal | Exit check | Status |
|---|---|---|---|---|
| 0 Data understanding | done 11:30 | DATA_NOTES.md | Quality issues + insights written | ✅ Done |
| 1 Ideation | done 12:01 | Ideator↔evaluator loop, idea locked | FINAL.md (8.3/10) | ✅ Done |
| 2 Docs + repo | 12:15–12:20 | PRD, dev, arch, novelty, README, phases; push to GitHub | Pushed | 🚧 In progress |
| 3a Fusion + cleaning | 12:20–12:32 (12 min) | Dedupe, reindex, alias dict, 13-note regex, outlier flag → data/processed/ | Row counts printed; B04 27 Aug linked to note | 📋 Planned |
| 3b Forecast + attribution | 12:32–12:50 (18 min) | Ridge 6/12 h vs 2 naive, threshold rule, causes, action cards | MAE/WAPE table real | 📋 Planned |
| 3c Streamlit shell + Brief + Impact | 12:50–1:10 (20 min) | app.py runs, B04/B05/B07 cards, impact formulas, scenario label | `streamlit run app.py` works | 📋 Planned |
| 3d Outage Drill | 1:10–1:20 (10 min) | Mask/impute/replay, error vs baselines | Numbers on screen | 📋 Planned |
| 3e Bin classifier panel | 1:20–1:30 (10 min) | Held-out accuracy, ms/event, routing, predictions CSV | Accuracy computed | 📋 Planned |
| 4 Buffer + freeze | 1:15 target | Bug fixes only | App stable | 📋 Planned |
| 5 Demo assets | 1:15–1:50 | DEMO_SCRIPT.md, video, screenshots, workbook, 3-page PDF report | Submitted by 1:50 | 📋 Planned |

Note: 3a–3e as timed run to ~1:30, past the 1:15 freeze. To fit, run 3d and 3e in parallel with 3c where possible, or apply cut lines.

## Cut lines (in order)
1. Incentive ranking (already P1) 2. Sensor-drift check 3. HGB timing line 4. Bin routing 5. LLM toggle UI (fallback text only). Never cut: Drill, B07 card, classifier accuracy.

## Fallbacks
- Weak forecast → show seasonal naive as the model and ridge beside it.
- Drill hard → flat visible-hours mean with day-type shape.
- B07 card fails → exam-stretch (28 Sep–9 Oct) forecast vs actual.
- Streamlit step slips → static plots from precomputed CSVs.

## Per-phase rules
After each phase: app runnable, commit, push, update PRD Status + CLAUDE.md Project State, log prompt in PROMPT_WORKBOOK.md.
