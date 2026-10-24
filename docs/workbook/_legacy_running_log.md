# Prompt Workbook

## 1. AI Tools Used
- Claude Code (Claude Sonnet 5.5) — coding agent in terminal.

## 2. Prompt Log

### Entry 1 — 11:2x IST
- **Prompt:** Pasted CLAUDE.md (hackathon brief, time plan, Phase 0–3 instructions, workbook rules).
- **Purpose:** Set project rules; kick off Phase 0 (data understanding).
- **Produced:** (also read provided `docs/PROBLEM_STATEMENT_AND_CONSTRAINTS.md` + `README_data_guide.md`) venv + deps; `docs/DATA_NOTES.md` (shape, dtypes, nulls, quality issues, 5 insights); `.gitignore`; this workbook.
- **TODO (team):** what we decided / edited / rejected.

### Entry 2 — ~11:30 IST
- **Prompt:** (CLAUDE.md Phase 1) Propose 2–3 product concepts, recommend one, wait for pick.
- **Purpose:** Choose product direction against the 8 problem-statement constraints.
- **Produced:** 3 concepts presented in chat (A: full Grid dashboard, B: edge classifier + forecaster focus, C: incentive/gamification focus). Recommendation: A, built vertically.
- **TODO (team):** which concept we picked and why.

### Entry 3 — ~11:35 IST
- **Prompt:** "Generate the project documentation. Hard limit: finish in 10 minutes, then go back to building." (PRD, DEVELOPMENT, ARCHITECTURE_AND_DATAFLOW, PROBLEM_AND_NOVELTY, CLAUDE.md update; ground rules: no invented numbers, mark Built/In progress/Planned.)
- **Purpose:** Documentation backbone for judges and team.
- **Produced:** 4 docs in `docs/`; root `CLAUDE.md` created (original content + Project State + Docs Index; the two placeholders filled with pointers); corrected two figures in DATA_NOTES (65% / 95%). All features marked Planned since no app code exists yet; Concept A assumed as the pick.
- **TODO (team):** confirm Concept A; edit docs as needed.

### Ideation loop (prompts/ideator.md ↔ prompts/evaluator.md), threshold >= 8.5
- **Round 1 (~11:55 IST):** ideator v1 → evaluator **7.2**. Top feedback: hook contradicted the data (B05 has no solar; wrong building/dates), classifier only P1, scope too big. Changed in v2: rebuilt hook from verified events, classifier P0-lite, cut lines. TODO (team):
- **Round 2:** v2 → **8.0**. Top feedback: headline cards retrospective, Outage Drill error leaked the daily total, tasks optimistic. Changed in v3: forward-looking B07 19 Sep card, leak-free Drill with naive baselines, hardcoded alias/note tables, named 30+ constraints. TODO (team):
- **Round 3 (~12:10 IST):** v3 → **8.3** (not approved; best version). Top feedback: forecast near-persistence, incentive loop unmeasured. TODO (team):
- **Strategy:** we used two separate fresh Claude subagents as a generator–critic pair: an ideator prompt (product-manager role, hard constraints, fixed output format) and an independent evaluator prompt (judge role, rubric-weighted score, critical-failure checks, handoff block). The evaluator never saw the ideator's reasoning, and its handoff block was fed back verbatim, so each round fixed the weakest criterion instead of adding scope. Evaluator checked claims against the real data, which caught fabricated-looking details in v1.

### Entry — ~12:15 IST
- **Prompt:** "we will be taking this idea ... updating all the documentation ... prd document ... phase documentation ... readme ... pushing in https://github.com/HARDIKSINGH150206/p2p.git"
- **Purpose:** Lock CircuGrid Brief and align docs; set up repo remote.
- **Produced:** rewrote PRD, DEVELOPMENT, ARCHITECTURE_AND_DATAFLOW, PROBLEM_AND_NOVELTY for CircuGrid; new `docs/PHASES.md`, `README.md`, pinned `requirements.txt`; CLAUDE.md Project State/Docs Index updated; remote added and pushed.
- **TODO (team):**

### Entry — ~12:35 IST
- **Prompt:** "STOP ... make the development into phases so me and my teammate can work together ... feature branch ... phase wise branches ... Jhashank and Hardik ... push".
- **Purpose:** Replace sequential plan with a parallel two-person plan.
- **Produced:** docs/TEAM_WORKFLOW.md, docs/CONTRACTS.md, rewritten docs/PHASES.md, per-person workbook files, requirements/README/CLAUDE.md updates; committed src/pipeline.py as shared base. Stack changed to FastAPI + HTML at the user's request.
- **TODO (team):**

## 3. Iterations
_None yet._
