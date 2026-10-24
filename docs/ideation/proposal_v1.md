**Version:** v1

## 1. Product name + one-line pitch
**CircuGrid Brief**: an offline-proof campus grid that forecasts tomorrow's spikes, names the cause, ranks the fix.

(Pitch word count: 14.)

## 2. Runners-up
- **Smart-bin classifier + compost router as the whole product:** too narrow. Dataset separates classes easily, so the ML is not impressive, and it ignores energy, water and forecasting (3 of 8 constraints visible at best).
- **Pure anomaly dashboard on daily_summary (leaks, outliers, composter failure):** low build risk but it is "monitoring", which the problem statement explicitly rejects. It has no forecast, no outage story and weak AI/prompting.

(Considered and cut: a pure gamification leaderboard app, because the incentive has to be driven by a measurable forecast/baseline and is not a product by itself.)

## 3. Primary user & painful moment
- **Persona:** Facilities engineer for an 8-building campus (assumption: 1 to 2 people covering everything, auditing building by building).
- **Scene:** It is Monday, 8:30 AM. Hostel B05's solar inverter has been dead since Friday, the hostel composter motor burnt out last week, and B07's water meter is stuck. Nobody knows. The facilities engineer finds out only when the landfill bill or a warden's verbal complaint arrives. Meanwhile an exam week starts Wednesday and nobody knows which building will spike.
- **Workaround:** Manual walk-through audits plus paper or WhatsApp-style logs. Fails because (a) it lags real consumption by days (per PROBLEM.md), (b) the evidence is scattered: in `manual_logs.xlsx` the same building appears under 37 spellings in mixed units, and the key events are free-text notes with no value, (c) a building that goes offline simply drops out of the picture.

## 4. Root cause
- Data lives in four disconnected, differently-shaped sources (hourly meters, daily summaries, staff logs, bin sensors), so nobody correlates a log note with a meter spike.
- Dashboards show "what happened"; no tool says "what will happen in the next 12 h and why", so action is always reactive.
- Gateways drop and replay late (`received_at` lag usually ~1 h, max ~12 h; 184 duplicate rows), so tools either discard the building or double-count.

## 5. Solution
- Fuse hourly streams, daily summaries, calendar and cleaned manual logs into one deduplicated, gap-tolerant, confidence-tagged building feed (nothing is discarded when a building is offline).
- Each morning, produce a per-building "Brief": 12 h load forecast, anomalies attributed to a probable cause (log note, event, day type, weather), and a ranked action list quantified in kWh, Rs and kg CO2.
- Close the loop with a building leaderboard of "saved vs own forecast baseline" and a quantified, data-computed impact view.

## 6. Novelty
- **The twist: "Outage Drill".** One button knocks a building offline for N hours, using real data as hidden ground truth. The grid keeps that building on the dashboard by imputing from fused sources (footfall, same-day-type profile, daily total constraint, manual logs) with a widening confidence band, then on "reconnect" replays the buffered rows by `received_at` and shows the reconciliation error against what really happened. Proves the integrity claim with a measured number instead of a diagram.
- **Differentiator 1:** Manual free-text notes (leak, composter motor burnt, inverter error, meter stuck, AC left on) are parsed into structured events and used as attributed causes for meter anomalies. Most teams ignore `manual_logs`.
- **Differentiator 2:** Every recommendation carries an "evidence" line (which signal, which date, which log note, how much above baseline) so the explanation is the product, not an afterthought.

## 7. Core features
**P0 (must be in the demo)**
1. **Fusion and Outage Drill.**
   - Does: cleans and merges sources; dedupes hourly rows; flags late arrivals; normalises 37 building aliases and units; imputes missing or offline hours with confidence; drill and replay with reconciliation error.
   - Columns: hourly_streams (`timestamp`, `received_at`, `building_id`, electricity, water, solar, `footfall`), daily_summary (`building_id`, `date`, electricity, water, `occupancy_avg`), manual_logs (building name, stream, value, unit, `note`), calendar (`day_type`).
2. **Forecast, root cause and ranked actions.**
   - Does: per-building 6 to 12 h ahead electricity and water forecast (gradient boosting or ridge on lag, hour-of-day, day type, event, temp, footfall lag); anomaly detection against the forecast residual; attribution to ranked causes; action cards with kWh, Rs, CO2 and an evidence line.
   - Columns: hourly_streams (electricity, water, footfall), calendar (`day_type`, `event`, `avg_temp_c`, `rainfall_mm`, `humidity_pct`), daily_summary (electricity, solar, landfill, composted), manual_logs notes, buildings (`has_composter`, solar kW).
3. **Impact and leaderboard.**
   - Does: per-building "kWh saved vs own baseline if actions were taken", with composting-gap and solar-gap numbers; ranked leaderboard that updates when a user accepts an action; assumptions panel.
   - Columns: daily_summary (`wet_organic_kg`, `composted_kg`, `landfill_kg`, `recycled_kg`, `contamination_pct`, electricity, water), buildings (`has_composter`, solar), plus the guide constants (0.70 kg CO2/kWh, Rs 8/kWh, 0.85 kWh per 1000 L).

**P1 (only if time allows)**
1. **Edge bin classifier panel:** 6-class classifier on 5 sensor features, shows held-out accuracy, per-event latency in ms, and compost-vs-recycle routing of the 1,601 test events (also writes `waste_events_test_predictions.csv`). Columns: waste_events_train/test sensor columns and `category`.
2. **Failure-modes and scale panel:** static slide-style panel (sensor drift detected via residual drift, gaming via per-building baseline plus manual-log cross-check, 3 to 30+ buildings via per-building independent models) with a per-building budget stated as an explicit assumption.

## 8. Dataset usage
- **Cleaning:** dedupe on (`timestamp`, `building_id`) keeping latest `received_at`; reindex to the full hourly grid (2,880 h x 8) so gaps are explicit; the one 6,234 kWh B04 day on 2026-08-27 is flagged by robust z-score and checked against hourly sums; the 959,417 manual value is rejected as a unit error (plausibility range per stream).
- **Forecast:** time-ordered split (train on the first ~90 days, test on the last ~30). Report MAE and MAPE (or WAPE) vs a naive baseline (same hour yesterday / same hour last week). Only those real held-out numbers are shown. The accuracy-vs-compute trade-off is shown by timing a ridge model versus gradient boosting on the same split.
- **Outage Drill validation:** pick a building and window, hide the true values, impute, then compare to truth after replay (MAE and coverage of the confidence band). The metric is computed live from the data.
- **Attribution:** residual (actual minus forecast) above a threshold is linked to, in order, a matching manual note within +/- 1 day for that building, a calendar event, a day-type shift (exam, break), or weather. If none, labelled "unexplained".
- **Impact:** computed only from daily_summary and buildings. Example formulas below in section 11.
- **Classifier (P1):** stratified held-out split of train; report accuracy and per-class recall. Test set has no labels, so nothing is claimed about it except predicted-class distribution.

## 9. AI usage
- **(a) At runtime:** Optional Claude call turns the structured evidence for an anomaly (building, residual, matched note, event) into a 2-sentence plain-language brief and a maintenance-ticket draft. It also parses ambiguous free-text manual notes into event types. **Fallback:** a deterministic keyword/regex parser for notes (leak, motor, inverter, stuck meter, AC) and template strings for the brief. The app runs fully with no key or internet; ML (forecast, anomaly, classifier) is scikit-learn and local.
- **(b) To build:** Claude Code is used for cleaning pipeline, forecast, attribution, and UI, with prompts logged in `docs/PROMPT_WORKBOOK.md`. Prompts constrain it to the allowed columns and to compute every shown number from data.

## 10. User flow
1. Open the app. The top banner shows the campus Brief: next-12 h forecast per building, a red flag on B05 and the top 3 ranked actions, with Rs and CO2 at stake (within 20 s).
2. Click B05 to see forecast vs actual with confidence band, the anomaly, and the attributed cause with its evidence line.
3. Click "Outage Drill", choose a building and 6 h window. The building stays on the grid with a widening band and an "offline, estimated" badge.
4. Click "Reconnect and reconcile". Buffered rows replay by `received_at`; the dashboard shows the reconciliation error against truth.
5. Accept an action. The leaderboard and Impact view update (kWh, Rs, CO2, kg diverted from landfill).
6. (P1) Open the Bin panel to see classifier accuracy, latency per event and compost routing.

## 11. Impact & scalability
- **Metric (all from data):**
  - Electricity: avoidable kWh = sum over flagged anomaly hours of (actual minus forecast baseline). CO2 = kWh x 0.70; Rs = kWh x 8.
  - Water: avoidable litres from leak-flagged hours; energy embedded = litres/1000 x 0.85 kWh.
  - Waste: unexploited composting = `wet_organic_kg` in buildings with `has_composter` minus `composted_kg`, plus `wet_organic_kg` in composter-less buildings (candidate for a new unit). Compost yield uses the 4:1 ratio from the data guide. Landfill avoided in kg and as a share of total landfill.
  - Solar: gap = share of consumption not covered; reported, not claimed as saved.
- **Assumptions (labelled in-app):** share of flagged excess actually recovered (a user-set slider, default stated as an assumption), emission factor and tariff from the data guide.
- **Scales to:** any campus or building cluster. Per-building models are independent and trained on tiny tabular series, so 3 to 30+ buildings means adding rows and not redesigning. Compute for ridge or small boosted trees is milliseconds per building (timed in-app).
- **Path to deployment:** swap xlsx for an existing BMS/meter export or MQTT gateway; run per-building inference on a Raspberry-Pi-class box; central view is a lightweight Streamlit service (explicit assumption, not in the prototype).

## 12. Build plan (to finish before 1:15 PM)
1. **Cleaning/fusion pipeline (20 min):** alias map, unit normalisation, dedupe, hourly reindex, note parsing, save to `data/processed/`.
2. **Forecast + anomaly + attribution (25 min):** lag-feature model, time-split metrics, residual-to-cause linker, action cards.
3. **Streamlit shell + Brief + building view (20 min):** top metrics, forecast chart, evidence cards.
4. **Outage Drill + replay (15 min):** mask, impute, replay, error metric.
5. **Impact + leaderboard (10 min):** formulas and assumptions panel.
6. **P1 classifier panel (10 min, only if time):** Random Forest or decision tree, accuracy, ms per event.
- **Fallbacks:** if the forecast is weak, fall back to a seasonal-naive plus day-type profile (same hour, same day type) and report it as the honest baseline; if the Drill is hard, impute with a day-type hourly profile scaled to the daily total and skip the confidence band (show a +/- residual std band instead).

## 13. Demo strategy (2:30)
- **0:00 to 0:20 Hook:** the Monday-morning scene on screen with the real B05 flag, inverter fault and composter failure that no one saw; Brief shows the Rs and CO2 at stake.
- **0:20 to 1:10 Wow:** B05 forecast, anomaly, attributed cause with evidence; then the Outage Drill and reconcile with the measured error.
- **1:10 to 1:40 AI:** model metric vs baseline (real held-out numbers), Claude-written brief toggled on and off to show the offline fallback, brief look at the prompt workbook.
- **1:40 to 2:30 Impact:** Impact view (kWh, Rs, CO2, landfill), leaderboard, failure modes and 3 to 30+ scaling argument in one slide.

## 14. Risks & ethics
- **Forecast weaker than hoped (synthetic data may be noisy):** report real metrics against the naive baseline, not a made-up target; show the fallback model.
- **Scope creep across 8 constraints:** only 3 P0s; edge classifier and failure-mode panel are P1; unsupported constraints (camera frames, true edge hardware) are stated as design assumptions and not demoed.
- **Privacy/bias/gaming:** `footfall` and occupancy are aggregate counts, no individual data. Leaderboard compares each building to its own baseline, so large hostels are not penalised for size. Gaming (e.g. staff logging low values) is cross-checked against meter data.

## 15. Self-assessment
- **Relevance & sustainability: 8/10.** Hits energy, water and waste directly; the impact is computed, but recovery share is an assumption.
- **Impact & scalability: 7/10.** Clear per-building scaling argument, but no real deployment validation.
- **AI, prompting & dataset use: 8/10.** Uses all 7 tables (classifier is P1) and real held-out metrics; LLM is a thin layer.
- **Technical feasibility: 7/10.** Standard tools, but five modules in 1.5 h is tight; fallbacks exist.
- **Presentation/demo: 8/10.** Concrete scene, 20-second value, and a visible Drill moment; risk is overloaded demo.
