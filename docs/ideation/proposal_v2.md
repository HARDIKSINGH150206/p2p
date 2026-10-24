**Version:** v2

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
- **Second real moment (shown as the Brief's second card):** B05 Boys Hostel composter motor burnt, note 8 Sep ("working since yesterday" so failure 7 Sep), replaced 14 Sep. `composted_kg` is 0 from 7 to 13 Sep (normal about 247 kg/day) and B05 `landfill_kg` jumps from about 100 to 325-434 kg/day. Nobody saw it for 7 days in the data.
- **Workaround and why it fails:** manual audits and staff notes. (a) It lags consumption by days (PROBLEM.md); (b) evidence is scattered: free-text notes with no value, mixed units, 37 spellings; (c) a building that goes offline drops out of the picture.

## 4. Root cause
- Four disconnected differently-shaped sources (hourly meters, daily summaries, staff logs, bin sensors), so no one links a log note to a meter signal.
- Dashboards show what happened; no tool says "what will happen in 6 to 12 h and why", so action is always reactive.
- Gateways drop and replay late (`received_at` lag usually about 1 h, max about 12 h; 184 duplicate rows), so tools either discard the building or double-count.

## 5. Solution
- Fuse hourly streams, daily summaries, calendar and cleaned manual logs into one deduplicated, gap-tolerant, confidence-tagged building feed (no building is discarded when offline).
- Each morning a per-building Brief: 6 to 12 h load forecast, anomalies attributed to a probable cause (log note, event, day type, weather, or sensor fault), ranked actions in kWh, Rs and kg CO2, each with an evidence line.
- A bin-level edge classifier routes waste (compost vs recycle), and a baseline-relative incentive loop with a defined measurement design closes the loop.

## 6. Novelty
- **The twist: "Outage Drill".** One button knocks a building offline for N hours using real data as hidden ground truth. The grid keeps it on screen by imputing from a day-type hourly profile scaled to that day's daily total (footfall as a secondary scaler if it helps), marked "offline, estimated". On "reconnect" the buffered rows replay by `received_at`, and the app shows the **measured reconciliation error** (MAE and MAPE vs truth, for the hidden hours). Proof by number, not diagram.
- **Differentiator 1:** Free-text manual notes become structured, attributed causes, including **sensor-fault causes**: the B04 6,234 kWh reading on 2026-08-27 (neighbour days about 700) is matched to the same-day note "Power analyzer was being calibrated today, reading looked odd", so it is labelled *sensor fault, not real consumption*, excluded from avoidable-kWh, and a maintenance action is "verify analyzer" (not "cut load"). Most teams ignore manual_logs.
- **Differentiator 2:** Every recommendation has an evidence line (signal, date, note id, size vs baseline), so the explanation is the product.

## 7. Core features
**P0 (must be in the demo)**
1. **Brief: fusion, forecast, root cause, ranked actions.**
   - Does: clean and merge; dedupe hourly rows on (`timestamp`, `building_id`); normalise aliases and units; forecast 6 to 12 h ahead (ridge or gradient boosting on hour, day type, lags, footfall, temp); residual anomalies (daily series for flagged events, hourly for forecast); attribution; action cards with evidence.
   - Columns: hourly_streams (`timestamp`, `received_at`, `building_id`, electricity, water, solar, `footfall`), daily_summary (electricity, water, solar, `wet_organic_kg`, `composted_kg`, `landfill_kg`, `occupancy_avg`), manual_logs (`building`, `stream`, `value`, `unit`, `note`, `logged_at`), calendar (`day_type`, `event`, `avg_temp_c`, `rainfall_mm`, `humidity_pct`), buildings (`has_composter`, solar kW).
2. **Outage Drill.** Mask a building-window, impute (simple day-type profile scaled to daily total), replay by `received_at`, show measured error. No confidence band. Columns: hourly_streams, daily_summary electricity/water, calendar `day_type`.
3. **Impact + incentive loop.** Data-computed impact (section 11) and a per-building "saved vs own baseline" ranking, with an accept-action counterfactual. No animation.

**P0-lite (mandatory constraint; fixed 15 min, a single panel and one script)**
4. **Edge bin classifier panel.** 6 classes (food_organic, plastic, paper_cardboard, metal, ewaste, glass) on the 5 sensor features (weight, moisture, metal, transparency, acoustic hardness; median-imputed for the ~2% nulls). Shows: **stratified held-out accuracy** (80/20 split of train) with per-class recall and confusion matrix, **per-event inference latency in ms** (timed single-row `predict`, p50 and p95, on a small decision tree or random forest, aiming well under 2 s), and **compost-vs-recycle routing** (food_organic goes to the composter if `has_composter`, else flagged; the rest go to recycle) over the 1,601 unlabelled test events as a predicted-class distribution (no accuracy claimed there). Writes `waste_events_test_predictions.csv`.
   - Cut line: if over time, show accuracy + ms only and skip routing.

**P1 (only if time allows; otherwise static text)**
1. Sensor-drift check: rolling residual mean per building flags drift.
2. Hourly-forecast model timing table (ridge vs gradient boosting).

## 8. Dataset usage
- **Cleaning:** dedupe on (`timestamp`, `building_id`) keeping latest `received_at`; reindex to the full 2,880 h x 8 grid so gaps are explicit; B04 2026-08-27 flagged by robust z-score and linked to the calibration note; the 959,417 manual value is rejected as a unit error (plausibility range per stream).
- **Forecast validation:** time-ordered split (first about 90 days train, last about 30 test) vs a naive baseline (same hour last week; same hour yesterday). Report MAE and WAPE only from those real held-out runs. The accuracy-vs-compute trade-off is justified by timing ridge vs boosted trees per building.
- **Outage Drill validation:** hide a window, impute, replay, compare to truth after replay; MAE and MAPE computed live.
- **Attribution (ordered rules):** residual above threshold linked to, in order: (1) a same-building manual note within +/-1 day (leak, composter, inverter, meter stuck, calibration, AC/holiday), (2) a calendar event, (3) a day-type shift (exam, break), (4) weather, else "unexplained". Honest edge case: B03 Central Library 2026-10-02 (Gandhi Jayanti holiday; note "Holiday but AC and lights were left ON") shows 434 kWh against a 498-523 kWh run the days before, so the data may show no excess; in that case the Brief shows "note with no meter signal" instead of claiming a saving. Whatever the build shows is what the demo shows.
- **Verified real events used (all checked in data and notes):** B04 inverter Oct 6-9 (solar 0, 0, 0, 142); B05 composter Sep 7-14; B06 leak, notes 5, 7 and 10 Aug (water above the roughly 70,000 L/day median, with peaks of about 125,000 and 137,000 L on 7 and 9 Aug); B02 water meter stuck at zero, 3 Sep (water 0 on 3 and 4 Sep, normal about 5,900 L/day); B04 calibration 27 Aug.
- **Impact:** from daily_summary and buildings only.
- **Classifier:** stratified held-out accuracy and per-class recall; ms per event measured.

## 9. AI usage
- **(a) At runtime:** Optional Claude call turns structured evidence (building, residual, matched note id, event) into a 2-sentence brief and a ticket draft, and parses ambiguous free-text notes. **Fallback for every LLM use:** keyword/regex note parser (leak, motor, inverter, meter stuck, calibrat, AC), and template strings for brief and ticket. A header toggle "LLM on / off" is in the demo. Forecast, anomaly, drill and classifier are scikit-learn and local; no key is needed.
- **(b) To build:** Claude Code builds cleaning, models and UI, with prompts logged in `docs/PROMPT_WORKBOOK.md`. Prompts constrain it to the allowed columns and require that every shown number is computed from data.

## 10. User flow
1. Open the app: Brief banner shows the B04 inverter card (solar 0 for 3 days, note id, lost kWh) and the B05 composter card (within 20 s).
2. Click a card to see forecast vs actual, the attributed cause and its evidence line.
3. Click "Outage Drill" (building and 6 h window), see "offline, estimated"; click "Reconnect and reconcile" and read the measured error.
4. Accept an action; the Impact view and the baseline ranking update.
5. Open the Bin panel: accuracy, ms per event, routing.

## 11. Impact & scalability
- **Metric (all from data):**
  - Waste (B05): excess landfill during the composter outage = sum over 7 to 13 Sep of (`landfill_kg` minus the building's normal level of about 100 kg), around 1.9 t, and 0 kg composted vs normal about 247 kg/day (computed live). CO2 equivalent not claimed; only kg shown.
  - Energy (B04 solar): lost generation = normal about 300 kWh/day times the outage days (about 900 kWh, 6 to 8 Oct, computed live); CO2 = kWh x 0.70 kg; Rs = kWh x 8 (guide constants).
  - Water (B06 leak): litres above the building median during 5 to 10 Aug (computed live, order of 0.2 ML); embedded energy = litres/1000 x 0.85 kWh.
  - Excluded: the B04 27 Aug spike (sensor fault) is not counted as savings.
  - Unexploited composting: composter-less buildings' `wet_organic_kg` (candidate sites), and landfill share of the 3 composter buildings (from DATA_NOTES, about 26.6 t of 35.3 t).
- **Assumptions (labelled in-app):** share of excess recovered by acting (slider, default is an assumption), tariff and emission factor from the data guide.
- **Incentive impact measurement design:**
  - Baseline: each building's own forecast (day type, hour, weather) trained only on a period before the nudge, so hostels are not penalised for size.
  - Metric: saved = forecast baseline minus actual, summed over a window, in kWh, litres, kg landfill, normalised per occupant (`occupancy_avg`).
  - Pilot design (stated, not run): 4-week baseline, 8-week nudge on buildings in a staggered rollout (B05/B06 first, B01/B02 later as concurrent controls), difference-in-differences on saved vs baseline; credits redeemable per verified saving. In the demo we show the counterfactual: replay the Sep 7-14 composter outage with the "accept action" fix on the day-2 alert (saves the later 5-day excess, computed from data).
- **Per-building budget (assumption, line items):** about Rs 12,000: ESP32 + CT clamp/pulse flow meter Rs 3,500; bin-sensor kit (load cell, moisture, metal, acoustic; no camera) Rs 3,000 for 2 bins; Raspberry-Pi-class edge box Rs 5,000; misc Rs 500; software free (Python/Streamlit). All are assumptions, not quotes.
- **Scale 3 to 30+ (timed in-app):** one small model per building trained on its own tabular series. Measure seconds to fit and predict per building; extrapolate linearly: if one building fits in t seconds, 3 buildings take 3t and 30 take 30t (run in parallel on per-building edge boxes: constant). Show the timed per-building ms and a 3-vs-30 bar (arithmetic from the timed number). Adding a building is one alias row, one row in `buildings`, no redesign.
- **Deployment path:** swap xlsx for a BMS/meter export or MQTT gateway; per-building inference on an RPi-class box; central Streamlit service (assumption, not in the prototype).

## 12. Build plan (about 90 min total including 15 min buffer)
1. **Fusion + cleaning + note parsing (15 min):** alias map, units, dedupe, reindex, note events (with calibration cause), save to `data/processed/`.
2. **Forecast + attribution + action cards (20 min):** ridge lag model, time split vs naive, residual-to-cause, evidence lines.
3. **Streamlit shell + Brief + Impact (15 min):** cards, charts, formulas, assumptions panel, baseline ranking (no animation).
4. **Outage Drill (10 min):** mask, profile-scaled impute, replay, error.
5. **Edge classifier panel (10 min):** train, held-out accuracy, ms timing, routing.
6. **Buffer (15 min):** debug and screen-record the demo. Prompt workbook entries are written as each step is done.
- **Cut lines (in order):** drop P1 items; drop routing; drop the baseline ranking (show impact only); drop LLM toggle UI (fallback text only); never cut the Drill or classifier accuracy.
- **Fallbacks:** weak forecast, use seasonal naive (same hour, same day type) and report it as the baseline; if the Drill is hard, impute flat daily-total / 24 with the day-type shape and report error anyway.

## 13. Demo strategy (2:30)
- **0:00 to 0:50 Beat 1, Brief:** B04 solar 0 for 6 to 8 Oct with the real inverter note and lost kWh and Rs; B05 composter card; LLM toggle shows the same card with and without Claude.
- **0:50 to 1:35 Beat 2, Outage Drill:** knock B04 offline for 6 h, stays on the grid; reconnect; measured MAE and MAPE on screen.
- **1:35 to 1:45 Cutaway:** classifier panel: accuracy, ms per event, routing.
- **1:45 to 2:30 Beat 3, Impact:** kWh, Rs, CO2, landfill from data; incentive measurement design; failure modes and 3 vs 30+ in one slide.

## 14. Risks & ethics (failure modes with mitigations)
- **Failure mode 1: sensor drift / sensor fault (e.g. the 27 Aug B04 analyzer reading).** Mitigation: robust outlier flag cross-checked against manual notes and hourly sums; flagged readings are excluded from forecasts and savings; rolling residual mean flags slow drift and triggers a recalibration ticket.
- **Failure mode 2: gaming the incentive (staff logging low values) and model degradation over a semester.** Mitigation: savings are computed from meters, not logs, with logs used only as cross-checks; baseline is retrained on a rolling window and reset after a holiday or exam regime, with MAE tracked vs naive baseline so degradation is visible.
- **Forecast weaker than hoped:** report real metrics vs naive; show the fallback.
- **Privacy/bias:** `footfall` and occupancy are aggregates, no individuals. Per-building own-baseline avoids penalising large buildings. Camera frames and real edge hardware are not demoed (design assumption; the classifier uses the given sensor features only).

## 15. Self-assessment
- **Relevance & sustainability: 8.5/10.** Energy, water, waste, with the classifier now guaranteed; events are real.
- **Impact & scalability: 8/10.** Impact computed from data, measurement design stated, budget and timed scale argument; still no real pilot.
- **AI, prompting & dataset use: 8.5/10.** All 7 tables, real held-out metrics, LLM toggle with deterministic fallbacks.
- **Technical feasibility: 8/10.** Five small tasks plus a 15 min buffer, explicit cut lines, no band/animation.
- **Presentation/demo: 8/10.** Three beats, a 10 s cutaway, a hook built from verified data.

## 16. Changelog (vs v1; evaluator 7.2/10)
1. **Hook contradicted the data:** rebuilt from verified events. The v1 B05-solar scene is removed (B05 has no solar). The hook is B04 solar 0 on 6-8 Oct with the inverter notes of 7 and 9 Oct; second card is B05 composter 7-14 Sep. Also verified: B06 leak 5-10 Aug, B02 meter stuck 3 Sep, B04 calibration 27 Aug, B03 holiday AC 2 Oct (flagged as possibly no meter signal). No events are presented as coincident. The B04 6,234 kWh outlier is linked to the calibration note as a sensor fault and excluded from savings.
2. **Scope:** five modules plus UI in 90 min replaced with 5 tasks (75 min) plus a 15 min buffer and explicit cut lines. Confidence band and leaderboard animation dropped. Drill uses a day-type profile scaled to the daily total.
3. **Classifier:** promoted from P1 to P0-lite with 6 classes, stratified held-out accuracy, ms per event and compost-vs-recycle routing; own 10 min slot.
4. **Behavioural loop and cost/scale:** added the incentive measurement design (own baseline, saved vs baseline, staggered pilot with difference-in-differences, accept-action counterfactual), a per-building budget with line items labelled assumption, a timed 3-vs-30+ compute argument, and two failure modes each with a concrete mitigation.
5. **Demo overload:** three beats (Brief, Outage Drill, Impact) plus a 10 s classifier cutaway; LLM on/off toggle kept. Preserved: Drill with measured error, note parsing with evidence lines, data-computed impact with labelled assumptions, deterministic fallbacks, time-ordered split with naive baseline, per-building baselines, privacy handling.
