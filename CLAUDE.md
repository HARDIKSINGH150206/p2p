# CLAUDE.md — Srujana 2026 "Prompt to Product: Prompt for the Planet"

## Project State
- **Chosen product (idea locked): CircuGrid Brief** — an offline-proof campus grid that forecasts spikes, names the cause, ranks the fix. (Ideation v3, evaluator score 8.3/10, see docs/ideation/FINAL.md.)
- **Status: idea locked, awaiting GO.** (Older bullets below describing Concept A are superseded by this.)
- Stack (changed): Python, FastAPI backend + plain HTML frontend (final UI later), pandas, scikit-learn; optional Claude API via `.env` with offline fallback.
- Team: Hardik (phases 2A forecast/attribution, 2B drill, 7 demo) and Jhashank (3A classifier, 3B impact, 4 API + rough HTML, 6 final UI). Parallel, one branch per phase, merge by PR. See docs/TEAM_WORKFLOW.md, docs/PHASES.md, docs/CONTRACTS.md.
- Key files: `data/*.xlsx` (raw), `docs/ideation/FINAL.md` (locked proposal), `docs/PRD.md`, `docs/PHASES.md`, planned `src/pipeline.py`, `src/models.py`, `src/insights.py`, `app.py`.
- Built on main: data profiling, docs, src/pipeline.py, src/forecast.py, src/insights.py, src/drill.py, src/classifier.py (hold-out acc 84.96%), src/impact.py, src/incentive.py, src/api.py (FastAPI), landing page `/` (web/index.html, landing.css, landing.js: tilt-in dashboard hero, wired-card graph, feature tabs, campus map, live API panel, data tabs, constraints table, CTA) and workspace `/app` (web/app.html, workspace.js); shared graph in web/common.js, theme in web/style.css. Style ported from DigiVault-BFB / Aceternity inference template. `?demo=1` auto-connects the graph; `?flat` skips the hero tilt. Teammate PR #1 `Data_cleaning/` merged but separate from src/pipeline.py. Jhashank's commits are NOT being merged (team decision); we build everything on main.
- Next: DEMO_SCRIPT.md, 3-page report, workbook merge. Run: `python -m src.pipeline && uvicorn src.api:app`.
- Blockers: none; build is already tight against the 1:15 freeze, use cut lines.

## Docs Index
- [Team workflow](docs/TEAM_WORKFLOW.md) · [Contracts](docs/CONTRACTS.md) · [PRD](docs/PRD.md) · [Phases](docs/PHASES.md) · [Development](docs/DEVELOPMENT.md) · [Architecture & Dataflow](docs/ARCHITECTURE_AND_DATAFLOW.md) · [Problem & Novelty](docs/PROBLEM_AND_NOVELTY.md)
- [Data notes](docs/DATA_NOTES.md) · [Prompt workbook](docs/PROMPT_WORKBOOK.md) · [Ideation FINAL](docs/ideation/FINAL.md) · [Demo script](docs/DEMO_SCRIPT.md) (not yet written)

**Rule:** After any feature change, update the Status column in PRD.md and the Project State section here.

---

## Context
We are a student team at a 4-hour hackathon. HARD DEADLINE: 2:00 PM IST today.
Theme: sustainable innovation. Judges score from a 2:30 demo video (not live), out of 100:
relevance to problem & sustainability (20), impact & scalability (20), effective use of AI +
prompting + DATASET (20), technical feasibility / it actually works (20), demo & pitch quality (20).
Rules: build from scratch now, no copied repos, no fabricated metrics, every team member must
understand the code. A simple WORKING product beats an ambitious broken one.

## Problem statement
See `docs/PROBLEM_STATEMENT_AND_CONSTRAINTS.md` (Predictive Circular-Resource Grid for a Multi-Building Campus).

## Dataset
Located in `data/`. 7 xlsx files: buildings, calendar, daily_summary, hourly_streams, manual_logs, waste_events_train, waste_events_test (see `docs/DATA_NOTES.md`).

## Time plan (enforce this — warn us if we're slipping)
- by 11:45 → Phase 0 + Phase 1 done
- by 12:45 → MVP runs end-to-end on the real dataset
- by 1:15  → FEATURE FREEZE. Only bug fixes + polish after this.
- 1:15–1:50 → record video, finish workbook. Submit by 1:50 (buffer).

## Phase 0 — Understand the data (do first, ~10 min)
Load every file in `data/`. Report: shape, columns + dtypes, nulls, value ranges, obvious
quality issues, and 3–5 insights relevant to the problem. Write it to `docs/DATA_NOTES.md`.
Do NOT modify files in `data/`; write cleaned data to `data/processed/`.

## Phase 1 — Pick the product (~5 min)
Propose 2–3 product concepts. For each: one-line pitch, how it uses the dataset, the AI feature,
sustainability impact, and build risk (low/med/high). Recommend one. STOP and wait for our pick.

## Phase 2 — Build
Default stack (unless we say otherwise): Python + Streamlit single app (`app.py`), pandas,
plotly for charts, scikit-learn if any modelling is needed. Must run with `streamlit run app.py`.
- Keep the app runnable after EVERY step. Build vertically: one working feature, then the next.
- If using an LLM API inside the product, read the key from `.env` and ALWAYS have a non-LLM
  fallback so the demo never breaks without internet/key.
- Every number shown in the UI must be computed from the dataset. Never invent stats.
  If you train a model, show a real held-out metric and say what it was evaluated on.
- Include an "Impact" view: quantify the sustainability benefit from the data (e.g. CO2 / water /
  waste / energy / cost saved), and show the assumptions used.
- Clean, demo-friendly UI: clear title, short explanation, sidebar inputs, big key metrics on top.
- After each working feature: `git add -A && git commit -m "<what works now>"` and tell us to push.
- `requirements.txt` kept up to date. README with setup + run steps.

## Prompt Workbook — MANDATORY, update after EVERY task
Maintain `docs/PROMPT_WORKBOOK.md` with these sections, appending as we go:
1. **AI Tools Used** — Claude Code (+ any others we tell you about).
2. **Prompt Log** — for each request we give you: time, our prompt (verbatim, or close to it),
   purpose, what you produced (files/functions, short summary — no huge code dumps).
3. **Iterations** — when we re-prompt or correct you, log what changed and why.
4. **Human Contribution** — leave a `TODO (team):` line under each entry for us to fill in
   what we decided / edited / rejected. Never fill this in on our behalf.

## Phase 3 — Demo assets (start at feature freeze)
Write `docs/DEMO_SCRIPT.md`: a 2:20 video script with timestamps covering
(1) product overview ~20s, (2) live demo of key features ~70s, (3) how we used AI + prompting ~25s,
(4) innovation, impact & scalability ~25s. Include exact on-screen clicks to perform.
Also list 4–5 screenshots to capture.

## Working style
- Be concise. Do, don't lecture. Ask only when a decision is truly ours.
- If something will take >15 min, say so and offer a simpler alternative.
- Never delete or overwrite `data/` raw files. Never commit `.env`.
