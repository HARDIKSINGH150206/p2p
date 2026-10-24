# Development Guide — CircuGrid Brief
One-line: how to set up, run and understand the code.
Last updated: 12:15 IST

## Tech stack
| Layer | Tool | Why |
|---|---|---|
| UI | Streamlit | One app, fast demo |
| Data | pandas, openpyxl | xlsx inputs |
| Charts | plotly | Interactive |
| ML | scikit-learn (Ridge, tree/RandomForest, optional HistGradientBoosting timing) | Small CPU models; edge-sized |
| LLM (optional) | Claude API via .env | Brief wording only; regex/template fallback |

## Repo structure
```
CLAUDE.md                project rules + state
README.md                setup and overview
PROBLEM.md               problem statement
prompts/                 ideator + evaluator prompts
data/                    raw xlsx (read-only); data/processed/ cleaned outputs
docs/                    PRD, PHASES, dev, architecture, novelty, notes, workbook, ideation/
src/pipeline.py          📋 cleaning + fusion + alias/note tables
src/models.py            📋 forecast, anomaly, drill, classifier
src/insights.py          📋 attribution, actions, impact
app.py                   📋 Streamlit entry
requirements.txt         pinned deps
```

## Setup & run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py     # app.py not written yet
```

## Environment variables
- `ANTHROPIC_API_KEY` (optional, `.env`, never committed). Absent → regex note table + template strings; everything else runs locally.

## Data processing (📋 Planned)
| Step | Why |
|---|---|
| Dedupe hourly on (timestamp, building_id), keep latest received_at | 184 duplicates |
| Reindex to 2,880 h × 8 buildings | Make gaps explicit; offline buildings stay |
| Alias dict (37 spellings→B01–B08), unit conversion (units→kWh, kL→L, bag≈8 kg) | manual_logs variance |
| Regex table for 13 free-text notes | Structured causes |
| Robust-z outlier flag; B04 2026-08-27 linked to calibration note; reject 959,417 value | Sensor faults not counted as savings |

## Model / logic
- Forecast: ridge, per building, 6 h (and 12 h) ahead; features hour, day type, temp, origin load + footfall, same hour last week. Time split: train 20 Jun–17 Sep, test 18 Sep–17 Oct. Metrics MAE/WAPE vs same-hour-last-week and same-hour-yesterday. Metric values: not computed yet.
- Anomaly: residual above robust multiple of training residual spread; attribution ordered rules.
- Drill: day-type hourly profile (train days) scaled to visible hours only.
- Classifier: 5 sensor features, 80/20 stratified split of train file; test file unlabelled (no accuracy claimed there).

## Known limitations / next steps
- Synthetic data; forecast may not beat naive everywhere; only ~13 usable notes; no camera/edge hardware; latency measured on laptop.
- Steps and timings: see docs/PHASES.md.
