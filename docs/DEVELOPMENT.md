# Development Guide
One-line: how to set up, run and understand the code.
Last updated: 11:30 IST

## Tech stack
| Layer | Tool | Why |
|---|---|---|
| UI | Streamlit | Single-file app, fast to build and demo |
| Data | pandas, openpyxl | Dataset is .xlsx |
| Charts | plotly | Interactive, demo-friendly |
| ML | scikit-learn | Small tabular models, runs on CPU/edge-class hardware |
| LLM (optional) | Claude API via .env | Recommendation text; template fallback |

## Repo structure
```
CLAUDE.md                  project rules + state
data/                      raw xlsx (never edit)
data/processed/            cleaned outputs (📋 empty so far)
docs/                      PRD, dev, architecture, novelty, notes, workbook
.venv/                     local env (git-ignored)
app.py                     Streamlit entry (📋 Planned)
requirements.txt           dependencies (📋 to write)
```

## Setup & run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # not written yet; currently: pandas openpyxl streamlit plotly scikit-learn python-dotenv
streamlit run app.py              # app.py not written yet
```

## Environment variables
- `ANTHROPIC_API_KEY` (optional, in `.env`, never committed). Without it the app uses template-based recommendations.

## Data processing (📋 Planned; issues found in DATA_NOTES.md)
| Step | Why |
|---|---|
| Deduplicate hourly on (timestamp, building_id) | 184 duplicate rows |
| Order by timestamp, not received_at | Late arrivals up to ~12 h |
| Reindex to full hourly grid, flag gaps | Detect offline buildings, keep them |
| Map 37 building spellings to B01–B08 | manual_logs aliasing |
| Convert units (units→kWh, kL→L, bags→kg ~8 kg) | Per data guide |
| Flag outliers (e.g. B04 on 2026-08-27, 959,417 log) | Avoid corrupting totals |

## Model / logic
- Classifier: 📋 Planned. Features: weight_g, moisture_pct, metal_signal, transparency, acoustic_hardness; target: category (6). Evaluation: held-out split of train file. Metric: not yet computed.
- Forecast: 📋 Planned. Hourly lag + hour/day-type/calendar features, 6–12 h horizon, compared with naive baseline. Metric: not yet computed.
- Anomaly: 📋 Planned. Deviation from building/hour-of-week baseline, matched to manual notes and calendar events.

## Known limitations / next steps
- Dataset is synthetic; results show feasibility, not field performance.
- Test file is unlabelled, so no test accuracy.
- No real edge device benchmark; latency measured on the dev laptop only.
- Next: cleaning pipeline → dashboard → classifier → forecast → root-cause → impact.
