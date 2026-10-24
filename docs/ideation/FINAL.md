# FINAL — CircuGrid Brief (v3, NOT formally approved)
Best version after 3 rounds: **v3, real weighted score 8.3/10** (threshold 8.5 not reached; status REVISION REQUIRED per evaluator). No unresolved blocking critical failure.

## Score table (eval_v3)
| Criterion | Score/10 |
|---|---|
| Relevance & sustainability | 8.5 |
| Impact & scalability | 8.0 |
| AI, prompting & dataset | 8.5 |
| Technical feasibility | 8.0 |
| Demo & pitch | 8.5 |
| **Weighted** | **8.3** |

## Score history
| Version | Score | Status | Key change |
|---|---|---|---|
| v1 | 7.2 | Revision required | First proposal; hook contradicted data, classifier only P1, scope too big |
| v2 | 8.0 | Revision required | Verified real events, classifier P0-lite, cut lines + buffer, measurement design |
| v3 | 8.3 | Revision required (final iteration) | Forward-looking B07 card, leak-free Outage Drill, named 30+ scale constraints |

## Remaining non-critical limitations (evaluator)
- Forecast is a 6 h origin-conditioned ridge, close to persistence; may not beat last-week naive. Show 6 h and 12 h, claim only what numbers show; 19 Sep = detection and naming, exam stretch = prospective forecast.
- Incentive loop is a baseline ranking only ("no behaviour change measured"); keep as visible panel.
- Attribution rests on ~13 notes; show attributed vs "unexplained" counts on screen.
- Thin build slack; use precomputed CSV + static plots if the Streamlit step slips.
- Demo is dense; cut classifier cutaway to one line if over 2:30.

---

# Full proposal (v3)

**Version:** v3

## 1. Product name + one-line pitch
**CircuGrid Brief**: an offline-proof campus grid that forecasts spikes, names the cause, ranks the fix.

(Pitch word count: 14.)

## 2. Runners-up
- **Smart-bin classifier + compost router as the whole product:** too narrow. Classes separate easily, and it ignores energy, water and forecasting. Kept as a small guaranteed panel (P0-lite) instead.
- **Pure anomaly dashboard on daily_summary:** low build risk but it is "monitoring", which the problem statement rejects. No forecast, no outage story.
- (Cut: a standalone gamification app. The incentive needs a per-building forecast baseline to be measurable, so it lives inside the product.)

## 3. Primary user & painful moment
- **Persona:** Facilities engineer for the 8-building campus (assumption: 1 to 2 people covering everything by walk-through audits).
- **Scene (real data, verified):** The facilities engineer opens the app on the morning of Thu 2026-10-08, mid-semester exams, Day 8. B04 Engineering Labs has produced **0 kWh of solar on 6, 7 and 8 Oct** (`daily_summary`; its normal is about 300 kWh/day; it restarts at 142 on 9 Oct). The only evidence is a staff note logged 7 Oct 11:30: "Rooftop solar inverter showing red error light since Tuesday" (filed under B04), and a second one on 9 Oct: "Solar inverter reset by vendor, generating again" (filed as "Innovation Centre", an alias of B04). The meters never raised a flag and the note sits in a spreadsheet with 37 spellings of 8 buildings.
- **Second real moment (the Brief's second card):** B05 Boys Hostel composter motor burnt, note 8 Sep ("working since yesterday" so failure 7 Sep), replaced 14 Sep. `composted_kg` is 0 from 7 to 13 Sep (normal about 247 kg/day) and B05 `landfill_kg` jumps from about 100 to 325-434 kg/day. Nobody saw it for 7 days in the data.
- **Forward-looking moment (new, third card):** Sat 2026-09-19, Alumni meet ("food court very busy", calendar). B07 Food Court used **1,143 kWh** that day against 580-660 kWh on every other weekend day (daily from `hourly_streams`); footfall 34,562 against about 20,000; `wet_organic_kg` 514 against 242-303 on neighbouring days. The load doubled from 06:00 on. A manager who knows it is coming can pre-book composter capacity and shift loads; a dashboard shows it the next day.
- **Workaround and why it fails:** manual audits and staff notes. (a) It lags consumption by days (PROBLEM.md); (b) evidence is scattered: free-text notes with no value, mixed units, 37 spellings; (c) a building that goes offline drops out of the picture.

## 4. Root cause
- Four disconnected differently-shaped sources (hourly meters, daily summaries, staff logs, bin sensors), so no one links a log note to a meter signal.
- Dashboards show what happened; no tool says "what will happen in the next 6 h and why", so action is always reactive.
- Gateways drop and replay late (`received_at` lag usually about 1 h, max about 12 h; 184 duplicate rows), so tools either discard the building or double-count.

## 5. Solution
- Fuse hourly streams, daily summaries, calendar and cleaned manual logs into one deduplicated, gap-tolerant, confidence-tagged building feed (no building is discarded when offline).
- Each morning a per-building Brief: a 6 h-ahead load forecast, anomalies attributed to a probable cause (log note, event, day type, weather, or sensor fault), ranked actions in kWh, Rs and kg CO2, each with an evidence line.
- A bin-level edge classifier routes waste (compost vs recycle). A baseline-relative incentive ranking is computed on real data as a first cut (no behaviour change measured).

## 6. Novelty
- **The twist: "Outage Drill".** One button knocks a building offline for N hours using real data as hidden ground truth. The grid keeps it on screen by imputing the hidden hours from **the visible hours of that same day plus a day-type hourly profile** (profile scaled to the visible hours only), marked "offline, estimated". On "reconnect" the buffered rows replay by `received_at`, and the app shows the **measured error on the hidden hours (MAE and MAPE) next to naive baselines** (flat visible-hours mean, same hours last week, unscaled day-type profile). A second bar, "scaled to the daily total", is shown but labelled **"best case once the summary arrives"**. No hidden-hour information leaks into the headline number.
- **Differentiator 1:** Free-text manual notes become structured, attributed causes, including **sensor-fault causes**: the B04 6,234 kWh reading on 2026-08-27 (neighbour days about 700) is matched to the same-day note "Power analyzer was being calibrated today, reading looked odd", so it is labelled *sensor fault, not real consumption*, excluded from avoidable-kWh, and the action is "verify analyzer" (not "cut load"). Most teams ignore manual_logs.
- **Differentiator 2:** Every recommendation has an evidence line (signal, date, note id, size vs baseline), so the explanation is the product.

## 7. Core features
**P0 (must be in the demo)**
1. **Brief: fusion, forecast, root cause, ranked actions, and the forward-looking card.**
   - Does: clean and merge; dedupe hourly rows on (`timestamp`, `building_id`); normalise aliases and units via a **hardcoded alias dict and a regex table for the 13 free-text notes** (not a general parser); a **ridge** 6 h-ahead hourly forecast (features: hour, day type, temp, electricity and footfall known at the forecast origin, same hour last week), plus a **threshold rule** (residual above a robust multiple of the building's training residual spread) for anomalies; attribution; action cards with evidence.
   - **Forward-looking card (B07, 19 Sep):** the held-out forecast is drawn against actuals for the Alumni-meet day, with MAE and WAPE for that day and for the whole held-out window, per building, against both naive baselines (same hour last week, same hour yesterday), plus fit time for ridge vs a gradient-boosted model. All numbers are computed at build time from real runs; none are asserted in this proposal. What the card claims (and no more): the forecast uses footfall and load already observed at the origin, so it picks up the ramp and the residual flags the surge; it cannot predict that an unprecedented event will occur (there is one alumni meet in the data). If the ridge does not beat the naive baselines on a building or window, the card says so.
   - Columns: hourly_streams (`timestamp`, `received_at`, `building_id`, electricity, water, solar, `footfall`), daily_summary (electricity, water, solar, `wet_organic_kg`, `composted_kg`, `landfill_kg`, `occupancy_avg`), manual_logs (`building`, `stream`, `value`, `unit`, `note`, `logged_at`), calendar (`day_type`, `event`, `avg_temp_c`, `rainfall_mm`, `humidity_pct`), buildings (`has_composter`, solar kW).
2. **Outage Drill** (as in section 6). Columns: hourly_streams, calendar `day_type`; daily_summary only for the labelled best-case bar.
3. **Impact view.** Data-computed impact (section 11), labelled assumptions, and the accept-action replay shown on screen as **"Scenario: replay of 7-14 Sep with an earlier fix, not a measured outcome"**.

**P0-lite (mandatory constraint; fixed 10 to 15 min, a single panel and one script)**
4. **Edge bin classifier panel.** 6 classes (food_organic, plastic, paper_cardboard, metal, ewaste, glass) on the 5 sensor features (weight, moisture, metal, transparency, acoustic hardness; median-imputed for the ~2% nulls). Shows: **stratified held-out accuracy** (80/20 split of train) with per-class recall and confusion matrix, **per-event inference latency in ms** (timed single-row `predict`, p50 and p95, on a small decision tree or random forest), and **compost-vs-recycle routing** (food_organic goes to the composter if `has_composter`, else flagged; the rest go to recycle) over the 1,601 unlabelled test events as a predicted-class distribution (no accuracy claimed there). Writes `waste_events_test_predictions.csv`.
   - Cut line: if over time, show accuracy + ms only and skip routing.

**P1 (only if time allows; otherwise static text). The first cut is the incentive ranking.**
1. Baseline ranking: per building, saved = own forecast baseline minus actual, per occupant, from real data, headed "no behaviour change measured".
2. Sensor-drift check: rolling residual mean per building flags drift.

## 8. Dataset usage
- **Cleaning:** dedupe on (`timestamp`, `building_id`) keeping latest `received_at`; reindex to the full 2,880 h x 8 grid so gaps are explicit; B04 2026-08-27 flagged by robust z-score and linked to the calibration note; the 959,417 manual value is rejected as a unit error (plausibility range per stream).
- **Forecast validation (what is evaluated, shown in the demo):** time-ordered split (first 90 days, 20 Jun to 17 Sep, train; 18 Sep to 17 Oct test, which contains the 19 Sep alumni meet and the 28 Sep to 9 Oct exam stretch). 6 h-ahead hourly electricity per building. MAE and WAPE per building and per window (all test, 19 Sep, exam days) versus two naive baselines. Ridge vs boosting fit time. Reported only from these runs.
- **Plausibility check done while writing this proposal (exploratory, to be recomputed in the build, not quoted in the demo):** a 6 h-ahead ridge with origin footfall reduced the 19 Sep error for B07 versus both naive baselines but still missed a large part of the surge; and on exam days a plain last-week naive was as good as or better than ridge for some buildings (for example B03). The product therefore claims a calibrated baseline for residual detection, not a forecast that beats seasonal naive everywhere; the Brief shows whichever model wins per building.
- **Outage Drill validation:** hide a window, impute from visible hours and the day-type profile (profile built from training days only), replay, compare to truth. Exploratory check on B04 (6 h window, 17 test days): the visible-hours-scaled profile had an error close to the daily-total best case and far below flat visible-hours and last-week baselines; the numbers are recomputed live in the app.
- **Attribution (ordered rules):** residual above threshold linked to, in order: (1) a same-building manual note within +/-1 day, matched through the regex table (leak, composter, inverter, meter stuck, calibrat, AC), (2) a calendar event (this is how the 19 Sep surge is named), (3) a day-type shift (exam, break), (4) weather, else "unexplained". Honest edge case: B03 Central Library 2026-10-02 (Gandhi Jayanti holiday; note "Holiday but AC and lights were left ON") shows 434 kWh against a 498-523 kWh run the days before, so the data may show no excess; in that case the Brief shows "note with no meter signal" instead of claiming a saving.
- **Verified real events used (all checked in data and notes):** B04 inverter Oct 6-9 (solar 0, 0, 0, 142); B05 composter Sep 7-14; B06 leak, notes 5, 7 and 10 Aug (water above the roughly 70,000 L/day median, peaks of about 125,000 and 137,000 L on 7 and 9 Aug); B02 water meter stuck at zero, 3 Sep (water 0 on 3 and 4 Sep, normal about 5,900 L/day); B04 calibration 27 Aug; **new:** B07 Alumni meet Sat 19 Sep (calendar `event`; 1,143 kWh vs 580-660 on other weekend days; footfall 34,562 vs about 20,000; `wet_organic_kg` 514); mid-sem exam stretch 28 Sep to 9 Oct (9 `exam` days in calendar, 2 Oct is a holiday).
- **Impact:** from daily_summary and buildings only.
- **Classifier:** stratified held-out accuracy and per-class recall; ms per event measured.

## 9. AI usage
- **(a) At runtime:** Optional Claude call turns structured evidence (building, residual, matched note id, event) into a 2-sentence brief and a ticket draft. **Fallback for every LLM use:** the regex note table (leak, motor, inverter, meter stuck, calibrat, AC) and template strings for brief and ticket. A header toggle "LLM on / off" is shown for at most 10 s. Forecast, anomaly, drill and classifier are scikit-learn and local; no key is needed.
- **(b) To build:** Claude Code builds cleaning, models and UI, with prompts logged in `docs/PROMPT_WORKBOOK.md`. Prompts constrain it to the allowed columns and require that every shown number is computed from data.

## 10. User flow
1. Open the app: Brief banner shows the B04 inverter card (solar 0 for 3 days, note id, lost kWh) and the B05 composter card (within 20 s).
2. Click the B07 19 Sep card: forecast vs actual, the calendar-event cause, and MAE/WAPE vs naive.
3. Click "Outage Drill" (building and 6 h window), see "offline, estimated"; click "Reconnect and reconcile" and read the error against baselines.
4. Open Impact: kWh, Rs, CO2, landfill, plus the labelled scenario replay.
5. Open the Bin panel: accuracy, ms per event, routing.

## 11. Impact & scalability
- **Metric (all from data):**
  - Waste (B05): excess landfill during the composter outage = sum over 7 to 13 Sep of (`landfill_kg` minus the building's normal level of about 100 kg), around 1.9 t, and 0 kg composted vs normal about 247 kg/day (computed live). CO2 equivalent not claimed; only kg shown.
  - Energy (B04 solar): lost generation = normal about 300 kWh/day times the outage days (about 900 kWh, 6 to 8 Oct, computed live); CO2 = kWh x 0.70 kg; Rs = kWh x 8 (guide constants).
  - Water (B06 leak): litres above the building median during 5 to 10 Aug (computed live, order of 0.2 ML); embedded energy = litres/1000 x 0.85 kWh.
  - Excluded: the B04 27 Aug spike (sensor fault) is not counted as savings.
  - Unexploited composting: composter-less buildings' `wet_organic_kg` (candidate sites), and landfill share of the 3 composter buildings (from DATA_NOTES, about 26.6 t of 35.3 t).
- **Assumptions (labelled in-app):** share of excess recovered by acting (slider, default is an assumption), tariff and emission factor from the data guide.
- **Incentive (honest status):** the per-building ranking of saved vs own forecast baseline is run on the real held-out period (P1, first cut) and headed **"no behaviour change measured: this is a baseline, not an effect"**. Pilot design is stated, not run: 4-week baseline, 8-week nudge staggered across buildings (B05/B06 first, B01/B02 later as concurrent controls), difference-in-differences on saved vs baseline, normalised per `occupancy_avg`. The accept-action replay of the Sep 7-14 outage is on-screen-labelled "Scenario".
- **Per-building budget (assumption, line items):** about Rs 12,000: ESP32 + CT clamp/pulse flow meter Rs 3,500; bin-sensor kit (load cell, moisture, metal, acoustic; no camera) Rs 3,000 for 2 bins; Raspberry-Pi-class edge box Rs 5,000; misc Rs 500; software free. All are assumptions, not quotes.
- **What actually changes at 30+ buildings (named, not a bar chart):**
  1. **Alias rows:** the hand-built alias dict (37 spellings to 8 buildings) does not scale; at 30+ it becomes a `building_alias` table that is filled once at onboarding and unmatched names are queued for review, not silently dropped. This is the real manual cost per building.
  2. **Per-building models:** one small ridge per building (fit time measured in-app, ridge about 0.01 s and boosting about 0.15 s per building in the plausibility run); fine centrally for 30 and local on an edge box for 300. The weakness is cold start: a new building has no history, so it uses the day-type profile (the Drill's imputer) until about 2 weeks of data exist.
  3. **Late-arrival buffer replay:** ordering and dedupe by `received_at` per gateway; the replay window (here up to about 12 h) and its memory grow with the number of gateways, so the buffer is bounded and per-building.
  4. **Central aggregation:** only the Brief rows (cause, kWh, Rs, evidence line) go to the central Streamlit service; raw streams stay on the edge box.
- **Deployment path:** swap xlsx for a BMS/meter export or MQTT gateway; per-building inference on an RPi-class box; central Streamlit service (assumption, not in the prototype).

## 12. Build plan (about 90 min total including 15 min buffer)
1. **Fusion + cleaning + hardcoded alias dict and 13-note regex table (12 min):** units, dedupe, reindex, calibration cause, save to `data/processed/`.
2. **Ridge 6 h forecast + threshold rule + action cards (18 min):** time split vs two naive baselines, MAE/WAPE per building and window, one HGB fit timing, residual-to-cause, evidence lines. No model search.
3. **Streamlit shell + Brief (incl. B07 19 Sep card) + Impact (20 min):** cards, charts, formulas, assumptions panel, scenario label.
4. **Outage Drill (10 min):** mask, visible-hours profile impute, replay, error vs baselines, best-case bar labelled.
5. **Edge classifier panel (10 min):** train, held-out accuracy, ms timing, routing.
6. **Buffer (15 min, plus about 5 min slack):** debug and screen-record the demo. Prompt workbook entries are written as each step is done.
- **Cut lines (in order):** incentive ranking (first cut, already P1); drop sensor-drift; drop the HGB timing line; drop routing; drop LLM toggle UI (fallback text only); never cut the Drill, the 19 Sep forecast card or classifier accuracy.
- **Fallbacks:** weak forecast, use seasonal naive (same hour last week) as the shown model and report ridge beside it; if the Drill is hard, impute flat visible-hours mean with the day-type shape and report error anyway; if the 19 Sep card fails, show the exam-stretch forecast vs actual instead.

## 13. Demo strategy (2:30), one takeaway sentence per beat
- **0:00 to 0:40 Beat 1, Brief.** B04 solar 0 for 6 to 8 Oct with the real inverter note and lost kWh and Rs; B05 composter card. Takeaway: "The meters never flagged it; the notes did, and we joined them." LLM on/off toggle: at most 10 s.
- **0:40 to 1:10 Beat 2, Forward look.** B07 19 Sep: forecast vs actual with MAE/WAPE vs naive on screen. Takeaway: "Spikes get named by cause the morning they start, with a measured error versus naive."
- **1:10 to 1:50 Beat 3, Outage Drill.** B04 offline for 6 h, stays on the grid; reconnect; error vs baselines, best-case bar labelled. Takeaway: "Offline buildings stay on the grid, and the error is measured honestly."
- **1:50 to 2:00 Cutaway.** Classifier panel: accuracy, ms per event, routing.
- **2:00 to 2:30 Beat 4, Impact.** kWh, Rs, CO2, landfill from data; scenario label; one line on the 30+ constraints. Takeaway: "Every number is computed from the campus's own data."

## 14. Risks & ethics (failure modes with mitigations)
- **Failure mode 1: sensor drift / sensor fault (e.g. the 27 Aug B04 analyzer reading).** Mitigation: robust outlier flag cross-checked against manual notes and hourly sums; flagged readings are excluded from forecasts and savings; rolling residual mean flags slow drift and triggers a recalibration ticket.
- **Failure mode 2: gaming the incentive (staff logging low values) and model degradation over a semester.** Mitigation: savings are computed from meters, not logs, with logs used only as cross-checks; baseline is retrained on a rolling window and reset after a holiday or exam regime, with MAE tracked vs naive baseline so degradation is visible.
- **Forecast weaker than hoped (already seen in the plausibility run for some buildings and exam days):** report real metrics vs naive; show the fallback; claim the baseline-for-residuals role only.
- **Privacy/bias:** `footfall` and occupancy are aggregates, no individuals. Per-building own-baseline avoids penalising large buildings. Camera frames and real edge hardware are not demoed (design assumption; the classifier uses the given sensor features only).

## 15. Self-assessment
- **Relevance & sustainability: 8.5/10.** Energy, water, waste, a forward-looking card on a real event, a guaranteed classifier.
- **Impact & scalability: 8/10.** Computed impact, named scale constraints, a baseline ranking on real data; still no measured behaviour change.
- **AI, prompting & dataset use: 8.5/10.** All 7 tables, real held-out metrics versus naive, a non-leaky drill, LLM toggle with deterministic fallbacks.
- **Technical feasibility: 8/10.** Hardcoded alias and note tables, ridge only, a pre-declared first cut, 15 min buffer plus slack.
- **Presentation/demo: 8.5/10.** Four short beats, each with one takeaway, a verified hook and a forward-looking beat.

## 16. Changelog (vs v2; evaluator 8.0/10)
1. **Retrospective cards, no forecast shown:** added a forward-looking card on the B07 Alumni meet, Sat 19 Sep 2026. Verified in `calendar.xlsx` (event "Alumni meet (food court very busy)", weekend) and in the data: B07 1,143 kWh vs 580-660 on other weekend days, footfall 34,562 vs about 20,000, `wet_organic_kg` 514. Checked the forecast is plausible before promising it: a 6 h-ahead ridge using origin load and footfall tracks the ramp better than naive but still under-predicts, and the onset of a one-off event cannot be learned, so the claim is limited to "ramp picked up, surge flagged and named by the calendar event". Exam stretch (28 Sep to 9 Oct, 9 exam days) is the fallback window. The card reports MAE and WAPE vs both naive baselines and ridge-vs-boosting fit time, computed at build time; no numbers invented. Also disclosed that ridge may not beat last-week naive on exam days for some buildings.
2. **Drill leakage:** imputation now uses the visible hours of that day plus a day-type profile built on training days; headline error shown against flat visible-hours, last-week and unscaled-profile baselines. The daily-total variant is kept only as a bar labelled "best case once the summary arrives". An exploratory check suggests the honest variant is close to the best case; the live app recomputes it.
3. **Optimistic tasks 1 and 2:** hardcoded alias dict and a 13-note regex table; ridge-only forecast plus a threshold rule, no model search; incentive ranking declared the first cut (moved to P1). Build re-timed 12/18/20/10/10 min plus 15 min buffer and about 5 min slack.
4. **Scale and incentive:** named four concrete changes at 30+ buildings (alias table and onboarding queue, per-building models with cold start, late-arrival buffer replay, central aggregation of Brief rows only), replacing the linear timing bar. The baseline ranking runs on real data and is headed "no behaviour change measured". The accept-action replay is on-screen-labelled "Scenario".
5. **Dense demo:** four beats with one takeaway sentence each; LLM toggle at most 10 s; classifier cutaway kept at 10 s.
- **Preserved:** all verified events; the B04 27 Aug sensor-fault link; the B03 "note with no meter signal"; the Drill; evidence lines; data-computed impact with labelled assumptions; the P0-lite classifier; deterministic LLM fallbacks; time-ordered split vs naive baselines; per-building baselines; both failure modes; cut lines and buffer.
