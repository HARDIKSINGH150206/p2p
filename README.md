# CircuGrid Brief
An offline-proof campus grid that forecasts spikes, names the cause and ranks the fix.
Srujana 2026 "Prompt to Product: Prompt for the Planet" — problem: *Predictive Circular-Resource Grid for a Multi-Building Campus* (see `PROBLEM.md`).

> **Status:** idea locked, docs written, build starting. See `docs/PRD.md` for the status of each feature (nothing in the app is built yet).

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
uvicorn src.api:app --reload   # once phase 4 is merged
```
Optional: put `ANTHROPIC_API_KEY` in `.env` for LLM-written brief text. Without it the app uses regex/template fallbacks.

## Data
Raw files live in `data/` (7 xlsx, 20 Jun–17 Oct 2026, 8 buildings, synthetic). Never edited; cleaned outputs go to `data/processed/`. Notes: `docs/DATA_NOTES.md`.

## Docs
[Team workflow](docs/TEAM_WORKFLOW.md) · [Contracts](docs/CONTRACTS.md) · [PRD](docs/PRD.md) · [Phases](docs/PHASES.md) · [Development](docs/DEVELOPMENT.md) · [Architecture](docs/ARCHITECTURE_AND_DATAFLOW.md) · [Problem & novelty](docs/PROBLEM_AND_NOVELTY.md) · [Ideation result](docs/ideation/FINAL.md) · [Prompt workbook](docs/PROMPT_WORKBOOK.md)

## Team
Hardik (ML/backend: forecast, attribution, outage drill, demo) · Jhashank (classifier, impact, API, frontend). Split and branching: docs/TEAM_WORKFLOW.md.
