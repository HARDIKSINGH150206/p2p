# Evaluation of proposal_v2 (Iteration 2 of max 3). Approval threshold: weighted score >= 8.5

Verification done against `data/` (daily_summary, manual_logs, buildings). Every event cited in the v2 hook checks out: B04 solar 336.3, 321.6, 0, 0, 0, 141.8 on 4-9 Oct. B05 composted_kg 0 on 7-13 Sep, landfill 325-434 kg/day against a median of 99.75, and the excess over 100 kg sums to 1,929 kg. B06 water 104.9k, 97.3k, 125.0k, 97.7k and 136.6k L on 5-9 Aug against a median of 70,195. B02 water 0 on 3-4 Sep. B03 electricity 433.5 on 2 Oct against 497-523 kWh before. The notes are all present with the stated wording, and the "Innovation Centre" alias is real. The v1 factual errors are fixed.

## 1. Summary
| Version | Weighted score | Status | Biggest strength | Biggest weakness |
|---|---|---|---|---|
| v2 (prev v1 = 7.2) | **8.0 / 10** | REVISION REQUIRED | The evidence base is now verified and honest. The hook uses real events, the sensor-fault attribution is a good touch, and the plan has cut lines, a buffer and a guaranteed classifier. | The product is still mostly retrospective detection (zero-solar and zero-compost days are trivially visible). The "predictive" 6-12 h forecast is not tied to any demonstrated spike, and the Outage Drill's error metric is flattered by leakage of the hidden day's total. |

## 2. Rubric Table
| Criterion | Weight | Score/10 | Justification | Required improvement |
|---|---|---|---|---|
| 1. Relevance to problem and sustainability | 0.20 | 8.5 | All 8 constraints are mapped. Energy, water and waste are covered with real events. The classifier is now guaranteed, and two failure modes have mitigations. The remaining gap is "short-horizon forecasting, not monitoring". The headline cards (B04, B05) are after-the-fact detections, not predicted spikes. | Add one forward-looking card, for example a forecast of the exam-day or event surge (B07 alumni meet 19 Sep, 1,500+ people) with the actual outcome shown against the held-out forecast. |
| 2. Impact and scalability | 0.20 | 7.5 | Impact is computed from data (1.9 t landfill, about 900 kWh, 0.2 ML, all verified). Constants and the recovery slider are labelled. A measurement design (own baseline, difference-in-differences) is stated, which fixes the v1 gap. But it is "stated, not run". The accept-action counterfactual on a known outage is a replay, not evidence of a behavioural nudge. The budget (Rs 12,000) and the 3-vs-30 scaling are arithmetic from assumptions. The 3-vs-30 bar is trivial: linear in t by construction. | Scale argument should name real constraints, such as the alias row, per-building models and the late-arrival buffer, and not only a timing bar. Mark the Rs and CO2 as guide constants (done). Show the baseline-ranking numbers produced from real data, with the caveat that no behaviour change is measured. |
| 3. Effective use of AI, prompting, dataset | 0.20 | 8.5 | All 7 tables are used non-decoratively. Time-ordered split against naive baselines. A real stratified classifier metric. LLM is optional, with regex and template fallback, and the toggle is shown. The calibration-note link is a strong use of manual_logs. Concerns: (a) the attribution rules only have about 8 usable notes, so most flagged residuals will be "unexplained" (v2 acknowledges the B03 edge case honestly); (b) hourly forecast versus daily anomaly detection are two separate pipelines with no stated link; (c) the LLM is thin. | State exactly what the hourly forecast is evaluated on (MAE and WAPE versus naive, per building) and show it in the demo. Do not leave it as a claimed model. |
| 4. Technical feasibility and functionality | 0.20 | 7.5 | Five tasks at 15/20/15/10/10 min plus 15 min of buffer fits 90 min, but only if nothing slips. Task 2 (forecast, attribution and action cards with evidence lines, in 20 min) and task 1 (alias map for 37 spellings, units, dedupe, reindex, note parsing, in 15 min) are each optimistic. Cut lines are explicit and sensible, and the fallbacks (seasonal naive, flat/24 impute) are good. A described feature is still not a built feature, and nothing is built yet. | Pre-bake the alias map and parsed notes as a lookup of 13 notes (a hardcoded regex table is fine). Reduce task 2 to a ridge model plus a threshold rule. Decide now that the incentive ranking is cut first, not last. |
| 5. Presentation, demo, pitch | 0.20 | 8.0 | The hook is verified, concrete and strong, and the Drill is a genuine "wow". Three beats plus a 10 s cutaway is feasible. Risks: Beat 1 packs two cards plus the LLM toggle into 50 s; the Drill's "measured error" can look suspiciously good (see Critical Failures); the final 45 s covers impact, incentive design, failure modes and scale on one slide. | Give each beat one clear sentence of takeaway. Show the Drill error against a stated naive baseline (flat/24) so the number means something. |

Weighted score = (8.5 + 7.5 + 8.5 + 7.5 + 8.0) / 5 = **8.0**.

## 3. Critical Failures
No v1 critical failure remains in its previous form: the hook now matches the data, the classifier is P0-lite, the scope is cut and buffered, and impact numbers are computed. Remaining issues, none blocking alone, but together they keep the score below 8.5:
1. **Outage Drill metric leakage (medium).** Imputation "scaled to that day's daily total" uses a total that includes the hidden hours. In a real outage the daily summary would also be missing or partial. The reported MAE and MAPE would therefore be optimistic and could be attacked as circular. Minimum fix: either scale to the daily total of the *unmasked* hours only (for example estimate from the neighbouring same-day-type days and the visible hours), or compare against a naive flat baseline and label the daily-total variant as "best case, when the summary arrives after reconnect".
2. **"Predictive" not demonstrated (medium).** The two headline cards are 3-day and 7-day-old failures (zero solar, zero compost). A judge reading "Short-horizon forecasting, not just monitoring" will see monitoring. Minimum fix: one forward-looking card or chart showing a real forecast of a known surge (B07 alumni-meet day, or an exam-week stretch) against what actually happened, with the held-out MAE or WAPE versus naive.
3. **Incentive loop unmeasured in the demo (low-medium).** The measurement design is sound, but the demo shows only a replay counterfactual. The v2 text labels it as a scenario, which is acceptable. It must be labelled as such on screen. Not blocking.
4. **Feasibility (low-medium).** Tasks 1 and 2 are optimistic. Cut lines mitigate.
5. Not found: fabricated statistics (all checked numbers are real, and the constants are cited from the guide); a runtime LLM without a fallback; dataset misuse; rule violations; privacy or bias problems. The Rs 12,000 budget is explicitly an assumption, which is acceptable.

## 4. Skeptic Answers
- **Would the user adopt it over today's alternative?** Plausibly. The "explained, evidence-line" Brief beats walk-through audits. Trust still hinges on the forecast beating seasonal-naive, which is untested until it is built.
- **Weakest assumption:** that sparse notes (about 13) plus thresholds yield an attribution that looks non-empty beyond the five staged events. The rest of the flagged days will show "unexplained", or "note with no meter signal" in the B03 case.
- **Single biggest reason it fails:** time. Fusion plus forecast plus attribution plus Drill plus classifier plus UI in 75 min, if tasks 1 and 2 overrun.
- **Value if the AI part fails?** Yes. The cleaning, rule-based attribution, drill, classifier, impact and templates need no LLM. The forecast has a naive fallback.
- **What a judge attacks first:** "Your Drill error is computed using the day's total, so it is circular", then "where is the forecast ahead of a spike?", then "where is the behaviour change?"
- **ONE change that raises the score most:** make the forecast visible and predictive. Show a real held-out forecast of a surge with MAE versus naive, and fix the Drill's leakage so its error is believable.

## 5. Top 3-5 Improvements (ranked by score impact)
1. **Add a forward-looking forecast beat with real held-out numbers** (an exam-week or B07 event day, for example), including MAE and WAPE versus the naive baselines and the ridge-versus-boosting timing. (+criteria 1, 3, 5)
2. **Remove the Drill's leakage:** impute from visible hours plus the day-type profile, and report error against flat/24 and last-week-same-hour baselines. (+criteria 3, 5)
3. **De-risk tasks 1 and 2:** hardcode the 37-to-8 alias map and a 13-note regex table, make the forecast ridge-only, and pre-declare the incentive ranking as the first cut. (+criterion 4)
4. **Make the scale argument concrete:** name what changes for 30+ buildings (alias rows, per-building models, buffer replay, central aggregation) and avoid a purely linear bar. Run the baseline ranking on real data, and label it as "no behaviour change measured". (+criterion 2)
5. **Tighten beat timing:** one takeaway sentence per beat, and cut the LLM toggle from Beat 1 if it eats more than 10 s. (+criterion 5)

## 6. Iteration Tracking
| Version | Previous -> current | Improved | Declined / unchanged | Unresolved |
|---|---|---|---|---|
| v2 | 7.2 -> 8.0 | Relevance 8.0 -> 8.5 (classifier guaranteed, failure modes). Impact 7.0 -> 7.5 (measurement design and budget, still unrun). AI/data 7.5 -> 8.5 (verified events, calibration link, held-out classifier). Feasibility 6.5 -> 7.5 (scope cut, buffer, cut lines). Demo 7.0 -> 8.0 (verified hook, 3 beats). | None declined. Impact and Feasibility remain the lowest. | v1 critical failures resolved (hook, classifier, scope, measurement design). New: Drill leakage, forecast not shown predictively, thin scale argument. |

## 7. Final Decision
STATUS: REVISION REQUIRED

(8.0 is below the 8.5 threshold. No hard critical failure, but the gaps above remain.)

## 8. Handoff to Prompt 1
```
Current score: 8.0/10 (needs >= 8.5). Previous: 7.2. Weakest criteria: Impact & scalability (7.5) and Technical feasibility (7.5), then Demo (8.0).

Problems -> required changes:
1. The headline cards are retrospective (zero solar, zero compost), so the "forecasting, not monitoring" constraint is not demonstrated. -> Add one forward-looking beat: a real held-out forecast of a known surge (exam-week stretch or the B07 alumni-meet day on 19 Sep) shown against actuals, with MAE and WAPE versus both naive baselines and the ridge-versus-boosting timing. Reported only from real runs.
2. Outage Drill imputation is scaled to a daily total that includes the hidden hours, so the measured error is circular. -> Impute from the visible hours of that day plus a day-type profile (or flat/24) and report the error against naive baselines. If the daily-total variant is kept, label it "best case once the summary arrives".
3. Tasks 1 and 2 (alias map, note parsing, forecast, attribution, action cards in 35 min) are optimistic. -> Hardcode the alias map and a regex table for the 13 notes, make the forecast ridge-only plus a threshold rule, and declare the incentive ranking the first cut.
4. Scale and incentive are still arithmetic and a replay. -> Name concretely what changes at 30+ buildings (alias rows, per-building models, buffer replay, central aggregation), run the baseline ranking on real data, and label it "no behaviour change measured". Label the accept-action replay as a scenario on screen.
5. Demo beats are dense. -> One takeaway sentence per beat; the LLM toggle takes at most 10 s.

PRESERVE: all verified events and the sensor-fault link of the B04 27 Aug outlier to the calibration note; the "note with no meter signal" honesty for B03; the Outage Drill concept; evidence lines; data-computed impact with labelled assumptions; the P0-lite classifier (held-out accuracy, ms per event, routing); deterministic LLM fallbacks; time-ordered split against naive baselines; per-building baseline fairness; the two failure modes and mitigations; cut lines and buffer.

Submit the complete revised proposal and address each point in the changelog.
```
