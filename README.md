# CircuGrid Brief
An offline-proof campus grid that forecasts spikes, names the cause and ranks the fix.
Srujana 2026 "Prompt to Product: Prompt for the Planet" — problem: *Predictive Circular-Resource Grid for a Multi-Building Campus* (see `PROBLEM.md`).

> **Status:** backend + ML + rough HTML UI built and runnable; final frontend next. Feature status: `docs/PRD.md`.

## What it will do
- **Brief:** fuses hourly meters, daily summaries, calendar and manual logs; forecasts 6–12 h ahead; attributes anomalies to a cause with an evidence line; ranks actions.
- **Outage Drill:** takes a building offline, keeps it on the grid with estimates, then shows the measured error on reconnect.
- **Impact:** kWh, Rs, CO2, landfill and water computed from the dataset, with assumptions shown.
- **Bin classifier:** 6 waste classes from 5 sensor features, with held-out accuracy and ms per event.

## Setup
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.pipeline      # build data/processed/
uvicorn src.api:app --reload   # landing: http://localhost:8000  workspace: http://localhost:8000/app
```
Optional: put `ANTHROPIC_API_KEY` in `.env` for LLM-written brief text. Without it the app uses regex/template fallbacks.

## Data
Raw files live in `data/` (7 xlsx, 20 Jun–17 Oct 2026, 8 buildings, synthetic). Never edited; cleaned outputs go to `data/processed/`. Notes: `docs/DATA_NOTES.md`.

## Docs
[Team workflow](docs/TEAM_WORKFLOW.md) · [Contracts](docs/CONTRACTS.md) · [PRD](docs/PRD.md) · [Phases](docs/PHASES.md) · [Development](docs/DEVELOPMENT.md) · [Architecture](docs/ARCHITECTURE_AND_DATAFLOW.md) · [Problem & novelty](docs/PROBLEM_AND_NOVELTY.md) · [Ideation result](docs/ideation/FINAL.md) · [Prompt workbook](docs/PROMPT_WORKBOOK.md)

## Team
Hardik (ML/backend: forecast, attribution, outage drill, demo) · Jhashank (classifier, impact, API, frontend). Split and branching: docs/TEAM_WORKFLOW.md.

## Deploy
The app is one process: FastAPI serves the JSON API and the static frontend. `data/processed/` is rebuilt from the raw xlsx on first start, and the slow models are warmed in the background (the first load takes a few seconds).
- **Docker (any host):** `docker build -t circugrid . && docker run -p 8000:8000 circugrid`
- **Render:** New Web Service from this repo; `render.yaml` selects the Dockerfile and `/api/health` as the health check.
- **Railway / Fly / Heroku-style:** the `Procfile` starts `uvicorn src.api:app` on `$PORT`.
- Needs Python 3.11+ (pinned dependencies target 3.12). No API keys or environment variables are required.

## Deploy
One process serves the API and the frontend. `data/processed/` is rebuilt from the raw xlsx on first start; models warm in the background (first load takes a few seconds). No keys needed. Python 3.11+.
- Docker: `docker build -t circugrid . && docker run -p 8000:8000 circugrid`
- Render: new Web Service from this repo (`render.yaml` uses the Dockerfile, health check `/api/health`).
- Railway/Fly/Heroku-style: `Procfile` starts uvicorn on `$PORT`.
