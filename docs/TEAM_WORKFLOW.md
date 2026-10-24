# Team Workflow — Hardik & Jhashank
One-line: phase branches, parallel work, small PRs merged into `main` phase by phase.
Last updated: 12:35 IST

## Rules
1. `main` always runs. Never push directly to `main` after this commit; open a PR.
2. One branch per phase: `phase/<name>` (names in docs/PHASES.md). Branch from latest `main`.
3. Each phase owns its own files (listed in PHASES.md), so two people rarely touch the same file. Shared files (`CLAUDE.md`, `docs/PRD.md`, `requirements.txt`) → change only your own line/row, and `git pull --rebase origin main` before pushing.
4. Build against `docs/CONTRACTS.md` (function signatures + JSON shapes). If you must change a contract, tell the other person first and edit CONTRACTS.md in the same PR.
5. Raw `data/` is read-only. `data/processed/` is git-ignored: everyone regenerates it with `python -m src.pipeline`.
6. Prompt workbook: log prompts in your own file (`docs/workbook/hardik.md` or `docs/workbook/jhashank.md`) to avoid merge conflicts; we merge them into `docs/PROMPT_WORKBOOK.md` at the end. Leave `TODO (team):` lines.
7. Every number shown must be computed from data. No invented metrics.

## Daily loop (per phase)
```
git checkout main && git pull
git checkout -b phase/<name>
# work, commit small
git push -u origin phase/<name>
# open PR -> other person skims (5 min max) -> merge (squash) -> delete branch
git checkout main && git pull
```
- PR title: `phase/<name>: what works now`. Body: what was built, how to run/check it, real metrics if any.
- Merge when: `python -m src.pipeline` and the app still start, and the phase's exit check in PHASES.md passes. Do not wait for polish.
- Merge conflicts: the person merging second rebases (`git pull --rebase origin main`) and resolves.

## Sync points
- 12:45 pipeline on `main` (done) — both start.
- 1:00 first merges (forecast, classifier, API stub).
- 1:15 FEATURE FREEZE: only bug-fix PRs after this.
- 1:50 submit.

## Setup (each person)
```
git clone https://github.com/HARDIKSINGH150206/p2p.git && cd p2p
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.pipeline      # builds data/processed/
```
