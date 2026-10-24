# Required documents for P2P

The five competition deliverables. Upload each file individually as listed; do not upload the images separately.

| # | Requirement | File | Notes |
|---|---|---|---|
| 1 | Prompt Workbook | `Prompt_Workbook.pdf` | Tools, prompt log (as typed + engineered), iterations, honest misses. **Public chat share links: not included, see below.** Source: `docs/PROMPT_WORKBOOK.md` |
| 2 | Technical Report (PDF, strictly 3 pages) | `Technical_Report.pdf` | System architecture, data handling, models and evaluation, scale, failure modes. Verified to be exactly 3 pages |
| 3 | UI Screenshots Package (single PDF) | `UI_Screenshots_Package.pdf` | Telemetry dashboard, circular waste allocations, facility alerts, forecast, drill, landing page. 12 pages, all screenshots combined |
| 4 | Project Overview (PDF) | `Project_Overview.pdf` | Initial idea, development process, tools, implemented features, final outcome |
| 5 | Test dataset predictions (CSV) | `waste_events_test_predictions.csv` | Columns `event_id`, `predicted_class`; 1,601 rows, one per unlabelled test event |

## Before you submit

- **Public chat share links (workbook requirement).** They can only be created from the chat interface by the account owner, so none were invented. Create them, then fill the table in section 1a of `docs/PROMPT_WORKBOOK.md` and regenerate (`python tools/build_submission.py`).
- **Human-contribution fields.** The workbook has `TODO (team):` lines for what you decided, edited or rejected. The AI does not fill them.
- The classifier hold-out accuracy is **84.96%**, just under the 85% target; the documents say so.

## Regenerating

All PDFs are built from live data by one script, so the numbers match the running app.

```bash
uvicorn src.api:app --port 8000 &                    # app must be running
node tools/shoot.mjs http://localhost:8000 /tmp/shots 1500 1000   # screenshots (needs Chrome)
python tools/build_submission.py /tmp/shots /tmp/build           # builds this folder
```
