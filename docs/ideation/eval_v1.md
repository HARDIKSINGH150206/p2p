# Evaluation of proposal_v1 (Iteration 1 of max 3). Approval threshold: weighted score >= 8.5

## 1. Summary
| Version | Weighted score | Status | Biggest strength | Biggest weakness |
|---|---|---|---|---|
| v1 | **7.2 / 10** | REVISION REQUIRED | Outage Drill: a measured, data-grounded proof of the intermittent-connectivity and integrity constraint, plus using manual_logs notes as attributed causes. | The hook scene contradicts the dataset (wrong buildings, wrong dates). Scope is five modules in ~1.5 h, and the classifier is demoted to P1. |

## 2. Rubric Table
| Criterion | Weight | Score | Justification | Required improvement |
|---|---|---|---|---|
| 1. Relevance to problem and sustainability | 0.20 | 8.0 | Covers energy, water and waste. Maps well onto fusion, forecast, root cause, outage handling and incentive. The edge classifier (>=5 classes, >85%, <2 s) is a mandatory constraint but is only P1, and the failure-mode and cost/scale items are a "static slide". The persona is concrete. | Make the classifier and failure modes light but guaranteed deliverables. State a per-building budget number. |
| 2. Impact and scalability | 0.20 | 7.0 | Impact is formula-driven from data, which is credible. But the "avoidable kWh" is residual-over-forecast, and the recovery share is an unmeasured slider. The behavioural loop is only a leaderboard with no measurement design (how would the nudge effect be measured?). The scaling argument is one sentence. | Define how incentive impact is measured, for example a before/after or pilot design plus the demo's accept-action counterfactual. Give a concrete 3 to 30+ cost and compute table. |
| 3. Effective use of AI, prompting, dataset | 0.20 | 7.5 | All tables are used, with real held-out metrics against a naive baseline and a deterministic fallback for the LLM. The runtime LLM is thin (2-sentence brief), which is honest. Forecast against the "anomaly" label is circular, since the notes define the anomalies. The hook cites facts not in the data (see Critical Failures). The classifier is the strongest and easiest ML here but is optional. | Promote the classifier to a guaranteed small P0 (~8 min). Use the LLM for note parsing with a regex fallback, and show both. |
| 4. Technical feasibility and functionality | 0.20 | 6.5 | Five modules (fusion with alias/unit cleaning, forecast, anomaly attribution, Outage Drill with replay, impact/leaderboard) plus a Streamlit UI in ~1.5 h is tight, and the stated 20/25/20/15/10 min budget sums to 90 min with no slack for debugging or the video. The doc itself says this is tight. The build plan is in 4-hour-timeline terms (finish by 1:15 PM) rather than the 1.5 h left. Fallbacks exist and are sensible. | Cut to a minimum vertical slice. Defer the confidence band and the leaderboard. Pre-agree a hard cut line at each module. |
| 5. Presentation, demo, pitch | 0.20 | 7.0 | The Outage Drill is a real "wow" and the 2:30 timeline is well laid out. But the opening scene is factually wrong against the data (below), and a judge who checks will lose trust. The demo packs ~8 beats in 2:30. | Rewrite the hook around real events. Cut the demo to 3 beats (Brief, Drill, Impact) and show the classifier in a 10 s cutaway. |

Weighted score = (8.0 + 7.0 + 7.5 + 6.5 + 7.0) / 5 = **7.2**.

## 3. Critical Failures
1. **Factual claims not supported by the data (high).** Checked against `buildings.xlsx` and the 13 free-text notes in `manual_logs.xlsx`:
   - "B05's solar inverter has been dead since Friday": B05 has no solar (`has_solar`=0, 0 kW). The inverter error is **B04** (note dated 2026-10-07, reset 2026-10-09).
   - "B07's water meter is stuck": the stuck water meter note is **B02 / Acad Block B** (2026-09-03). B07 has no such note.
   - "Composter motor burnt last week", "inverter dead since Friday" and "exam week Wednesday" are presented as one coincident Monday scene. The real events are weeks apart (composter B05 Sep 8 to Sep 14, inverter Oct 7 to Oct 9). Presenting a composite as one real event in the demo is a fabrication risk. Minimum fix: use the real building, date and note for each event, or label the scene as an illustrative composite.
2. **Mandatory constraint under-delivered (medium).** The edge classifier (>=5 classes, >85%, <2 s) is P1 and may not be built. It is the cheapest ML and should be guaranteed. Minimum fix: make it P0-lite.
3. **Feasibility / scope (medium).** The plan sums to 90 min with zero buffer for five modules. Minimum fix: reduce scope as in Section 5.
4. **Impact/behavioural measurement (low-medium).** "Measurably nudges" is not specified beyond an accept-action button that simply recomputes a hypothetical. Minimum fix: state an explicit measurement design (baseline period, per-building saved-vs-baseline, a pilot comparison) and label demo numbers as scenarios.
5. Not found: dataset is used non-decoratively; the runtime LLM has a fallback; privacy and bias are addressed (aggregate footfall only, per-building baseline). Also the recovery-share slider is labelled as an assumption, which is acceptable.

Note on the data: the B04 6,234 kWh outlier on 2026-08-27 coincides with a note ("power analyzer being calibrated, reading looked odd"), so it is likely a sensor artefact rather than real consumption. v1 flags it as an outlier but does not link it to this note. This would be a good attribution example (a "sensor fault, not waste" cause).

## 4. Skeptic Answers
- **Would the user adopt it over today's alternative?** Plausibly, since it replaces manual audits, but adoption depends on trust in forecasts. v1 has no evidence yet that the forecast beats seasonal-naive. This will show up only after the model is built.
- **Weakest assumption:** that residuals against a forecast can be attributed to 13 sparse manual notes. Most flagged hours will be "unexplained", so the attribution may look empty. Also that synthetic data has learnable spikes.
- **Single biggest reason it fails:** time. Five modules in 90 min with no slack, and a weak or missing classifier.
- **Value if the AI part fails?** Yes, partially. The cleaning and fusion, impact formulas and Outage Drill need no LLM. The forecast has a seasonal-naive fallback.
- **What a judge attacks first:** the hook (B05 has no solar), then "where is the 85% edge classifier", then "how do you measure that the leaderboard changes behaviour?"
- **ONE change that raises the score most:** fix the evidence base and shrink the scope. Use only real, verified events for the hook and attribution, and drop to a 3-beat demo with the classifier guaranteed.

## 5. Top 3-5 Improvements (ranked by score impact)
1. **Correct the hook and attribution examples to real events** (B04 inverter Oct 7 to 9, B05 composter Sep 8 to 14, B06 leak Aug 5 to 10, B02 meter stuck Sep 3, B03 holiday AC Oct 2, B04 calibration Aug 27). Verify each against the data before the demo. (+criteria 1, 3, 5)
2. **Reduce scope to a feasible 90 min plan with cut lines:** drop the confidence-band and the leaderboard animation, keep Drill with a simple profile-scaled imputation, and add a ~15 min integration/debug buffer. (+criterion 4)
3. **Make the classifier a P0-lite panel** (RandomForest, stratified held-out accuracy, per-event ms, 6 classes) and show it as the edge-inference evidence. (+criteria 1, 3, 4)
4. **Add a short, concrete measurement/cost/scale spec:** per-building budget figure with line items (explicitly an assumption), a 3 vs 30 building compute table timed in-app, and the incentive measurement design with the failure modes (sensor drift, gaming) each with a mitigation. (+criteria 2, 1)
5. **Tighten the demo to 3 beats** with timestamps, and show the LLM on/off toggle quickly. (+criterion 5)

## 6. Iteration Tracking
First iteration; no previous scores. v1 = 7.2.

## 7. Final Decision
STATUS: REVISION REQUIRED

## 8. Handoff to Prompt 1
```
Current score: 7.2/10 (needs >= 8.5). Weakest criterion: Technical feasibility (6.5), then Impact (7.0) and Demo (7.0).

Problems -> required changes:
1. Hook scene contradicts the data (B05 has no solar; the inverter fault is B04, Oct 7-9; the stuck water meter is B02, Sep 3 not B07; events presented as coincident are weeks apart). -> Rebuild the hook and every attribution example from real, verified notes/dates (list in eval_v1.md Section 5.1), or label as an illustrative composite. Also link the B04 6,234 kWh outlier (Aug 27) to the "power analyzer being calibrated" note as a sensor-fault cause.
2. Scope: five modules + UI in ~90 min, no buffer. -> Resubmit a plan fitting the REMAINING ~1.5 h with a 15 min debug/video buffer and explicit cut lines; drop confidence band and leaderboard animation; Drill uses simple day-type profile scaled to daily total.
3. Edge classifier (mandatory) is only P1. -> Make it a P0-lite panel: 6 classes, stratified held-out accuracy, per-event latency (ms), compost-vs-recycle routing.
4. Behavioural loop and cost/scale are thin. -> Add the incentive impact-measurement design (baseline, saved vs own baseline, pilot/before-after), a stated per-building budget with line items marked as an assumption, a timed 3 vs 30+ compute argument, and 2 failure modes each with a concrete mitigation.
5. Demo is overloaded. -> 3 beats (Brief with real flagged event, Outage Drill with measured error, Impact) plus a 10 s classifier cutaway; keep the LLM on/off toggle.

PRESERVE: the Outage Drill concept and measured reconciliation error; manual_logs note parsing as attributed causes with an evidence line; data-computed impact with labelled assumptions; deterministic fallbacks for every LLM use; time-ordered split with naive baseline; per-building baseline fairness; privacy handling.

Submit the complete revised proposal and address each point in the changelog.
```
