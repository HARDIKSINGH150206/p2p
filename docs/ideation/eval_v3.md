# Evaluation of proposal_v3 (Iteration 3 of 3, final). Approval threshold: weighted score >= 8.5

Verification against `data/` this round: B07 daily electricity on weekends is 580-661 kWh every weekend from 22 Aug to 17 Oct, except Sat 19 Sep at 1,143 kWh. B07 footfall on 19 Sep is 34,562. `calendar.xlsx` has the 19 Sep event row (Saturday, weekend). `hourly_streams` columns match what v3 cites (`timestamp`, `received_at`, `building_id`, `electricity_kwh`, `water_litres`, `solar_generation_kwh`, `footfall`). The v2 events (B04 inverter, B05 composter, B06 leak, B02 stuck meter, B03 holiday) were verified in eval_v2 and are unchanged. `manual_logs` has 415 rows, and most notes are filler ("approx", "daily total", "counted at end of day"), which supports the "about 13 usable notes" assumption. The 19 Sep date falls in the proposed test window (18 Sep to 17 Oct), so the surge is genuinely unseen by training. The plausibility-run figures quoted in v3 (ridge about 0.01 s vs boosting about 0.15 s, the B03 exam-day result) are not re-run here. v3 itself says they are exploratory and not to be quoted, which is acceptable.

## 1. Summary
| Version | Weighted score | Status | Biggest strength | Biggest weakness |
|---|---|---|---|---|
| v3 (prev v2 = 8.0) | **8.3 / 10** | REVISION REQUIRED (final iteration, not approved) | The three gaps from v2 are closed honestly: a forward-looking B07 card on a verified real event, a non-leaky Outage Drill with naive baselines, and named 30+ scale constraints. The proposal discloses where the forecast may lose to naive. | The forecast is the weakest link. It is a ridge model fed with load and footfall already seen at the forecast origin, 6 h ahead only, so it is close to persistence. v3 itself says it "still missed a large part of the surge" and may not beat last-week naive. The demo hero beat therefore shows an honest but unimpressive result, and the incentive loop is still unmeasured. |

## 2. Rubric Table
| Criterion | Weight | Score/10 | Justification | Required improvement |
|---|---|---|---|---|
| 1. Relevance to problem and sustainability | 0.20 | 8.5 | All eight constraints are mapped. Energy, water and waste are covered with verified events. A forward-looking card now exists. Weak spots: the forecast horizon is 6 h, the bottom of the "6-12 h" range, with no 12 h run. Camera frames and real edge hardware are not demonstrated (stated honestly). The "three heterogeneous sources" fusion is hourly, daily and notes, which is credible. | Show a 6 h and a 12 h horizon in the same table (a cheap loop). |
| 2. Impact and scalability | 0.20 | 8.0 | Impact is computed from data and the assumptions are labelled. The 30+ constraints are now concrete (alias table, per-building models with cold start, buffer replay, central aggregation). The incentive ranking is only a baseline, headed "no behaviour change measured", and it is P1 and the first cut, so the behavioural-loop constraint may show only as static text in the demo. Rs 12,000 per building is an assumption with line items. Impact is "avoidable if caught" on past events, not a prospective total. | Keep the incentive ranking in the build as a visible panel, not static text, or explicitly accept that this criterion stays at 8. |
| 3. Effective use of AI, prompting and dataset | 0.20 | 8.5 | All 7 tables are used. The time-ordered split with MAE/WAPE against two naive baselines is the right evaluation, and it is reported only from real runs. The Drill is leak-free and benchmarked. The classifier is evaluated on a stratified held-out set. The LLM is optional with deterministic fallbacks. The sensor-fault link to the calibration note is a good use of notes. Limits: the "AI" is mostly classical ML (justified, since the edge constraint rules out heavy models), and the LLM role is thin. Attribution rests on about 13 notes plus the calendar, so most other residuals will read "unexplained". | None blocking. Show the count of residual flags attributed vs unexplained on screen, so the limit is visible rather than hidden. |
| 4. Technical feasibility and functionality | 0.20 | 8.0 | The scope is now credible: hardcoded alias dict, regex table, ridge only, no model search, Drill as a mask-and-impute, and a classifier on 5 tabular features. The 12/18/20/10/10 plus 15 min buffer plan fills about 90 min, so slack is thin. Fallbacks are explicit (seasonal naive, flat impute, exam-stretch card). The Streamlit step (20 min for Brief, B07 card, Impact, assumptions, scenario label) is the likeliest to overrun. Nothing is built yet, and a described feature is not a built feature. | Pre-decide that Impact and the B07 card are static plots from precomputed CSVs if step 3 slips. |
| 5. Presentation, demo and pitch | 0.20 | 8.5 | The hook is verified and concrete. Each beat has one takeaway sentence. The Drill with "reconnect and see measured error vs baselines" is a real wow moment. Risk: four beats plus a cutaway in 2:30 is dense (roughly 40 s, 30 s, 40 s, 10 s, 30 s). The B07 beat's payoff depends on a forecast result that v3 admits is partial, so the message must be "ramp picked up, surge flagged and named", not "predicted". | Rehearse the B07 beat around what the numbers actually show. If ridge does not beat naive, say so on screen as planned. |

Weighted score = (8.5 + 8.0 + 8.5 + 8.0 + 8.5) / 5 = **8.3**. This is a real improvement from 8.0, but it is below the 8.5 threshold. Scores were not raised just because changes were made. Impact and Feasibility each gained 0.5 for concrete fixes, and no other criterion moved.

## 3. Critical Failures
None of the listed critical failures is unresolved in blocking form. Remaining issues, with severity:
1. **Forecast is near-persistence and may not beat naive (medium).** The features include electricity and footfall at the origin, so for a 6 h horizon the model largely extends the current level. The proposal handles this honestly (reports vs naive, claims only a "baseline for residual detection"). Minimum fix: report 6 h and 12 h, and state plainly which model wins per building. This does not violate a rule, but it caps criteria 1 and 3.
2. **Incentive loop is not demonstrated (low-medium).** The measurement design is stated, and a baseline ranking is P1. It is the first cut, so it may not appear. The problem statement says "measurably nudges". A designed-but-unrun loop is acceptable for a prototype if clearly labelled, and v3 labels it.
3. **Thin build slack (low-medium).** About 90 min planned against about 1.5 h available; the buffer is the only slack.
4. **Not found:** fabricated statistics (every cited figure checked is real; model metrics are deferred to build-time runs), unavailable APIs, an LLM without a fallback, dataset misuse, rule violations, ignored privacy (footfall and occupancy are aggregates; no individual-level data).

## 4. Skeptic Answers
- **Would the user adopt it over today's alternative?** Plausibly yes for the notes-plus-meters Brief with evidence lines. The forecast alone would not justify adoption until it clearly beats last-week naive.
- **Weakest assumption:** that a 6 h origin-conditioned ridge adds value beyond persistence or seasonal naive, and that about 13 notes yield attributions that look non-empty beyond the staged events.
- **Single biggest reason it fails:** time. Five modules in 75 min plus a 2:30 video with four beats.
- **Value if the AI part fails?** Yes. Cleaning, rule-based attribution, the Drill, the classifier and the impact figures are deterministic or local. The LLM is optional and the forecast has a naive fallback.
- **What a judge attacks first:** "Your forecast needs the current load as input, so is it forecasting or extrapolating?", then "where is the behaviour change?", then "where is the edge hardware?".
- **ONE change that raises the score most:** make the forecast result unambiguous and strong. Report 6 h and 12 h horizons, and use features available at the origin that are genuinely forward-looking (calendar day type, scheduled events, the exam flag), so the surge is anticipated rather than followed. The unprecedented event itself cannot be learned, so frame the 19 Sep card as detection and naming, and use the exam stretch as the prospective forecast demonstration.

## 5. Top 3-5 Improvements (ranked by score impact)
1. Evaluate and show 6 h and 12 h horizons per building against both naive baselines. Anchor the forward-looking claim on the exam stretch (a recurring, calendar-known regime) and use 19 Sep as the detection-and-naming card. (+criteria 1, 3, 5)
2. Promote the incentive ranking to a visible panel (cheap, one groupby over data already computed), still headed "no behaviour change measured". (+criterion 2)
3. Show an attributed vs "unexplained" count for flagged residuals. (+criterion 3)
4. Pre-declare static-plot fallbacks for Streamlit step 3 and cap the demo at three beats plus two cutaways if the video exceeds 2:30. (+criteria 4, 5)

## 6. Iteration Tracking
| Version | Previous -> current | Improved | Declined / unchanged | Unresolved |
|---|---|---|---|---|
| v1 | n/a -> 7.2 | n/a | n/a | n/a |
| v2 | 7.2 -> 8.0 | Relevance 8.0 -> 8.5, Impact 7.0 -> 7.5, AI/data 7.5 -> 8.5, Feasibility 6.5 -> 7.5, Demo 7.0 -> 8.0 | none | Drill leakage, forecast not shown predictively, thin scale argument |
| v3 | 8.0 -> 8.3 | Impact 7.5 -> 8.0 (named scale constraints, baseline ranking on real data, scenario labelling). Feasibility 7.5 -> 8.0 (hardcoded tables, ridge only, declared cut order). Demo 8.0 -> 8.5 (verified forward card, takeaway per beat, leak-free Drill). | Relevance 8.5 and AI/data 8.5 unchanged (forecast still weak and honest about it). | Forecast adds little over naive and is 6 h only. Incentive unmeasured and likely static. Thin build slack. |

Resolved from v2: Drill leakage (fixed with baselines and a labelled best-case bar), no forward-looking card (added on a verified event), optimistic tasks 1 and 2 (de-scoped), thin scale argument (four named constraints), dense beats (one takeaway each).

## 7. Final Decision
STATUS: REVISION REQUIRED

Iteration 3 is the final iteration, and v3 does not reach 8.5. It is not approved. **Best version: v3, real weighted score 8.3/10** (v2 = 8.0, v1 = 7.2). No unresolved blocking critical failure remains, so v3 is the version to build from. The remaining gap is the forecast framing and the incentive loop, not the facts or the feasibility.

## 8. Handoff to Prompt 1
```
Current score: 8.3/10 (needs >= 8.5; iteration 3 of 3, final). Previous: 8.0 (v2), 7.2 (v1). Weakest criteria: Impact & scalability (8.0) and Technical feasibility (8.0).

Best version: v3 (8.3). NOT approved. Build from it, applying the changes below as scope notes rather than another full cycle.

Problems -> required changes:
1. The 6 h origin-conditioned ridge is close to persistence, and the horizon is only 6 h. -> Report 6 h and 12 h per building vs both naive baselines. Add forward-looking features (day type, exam flag, calendar event). Present the exam stretch as the prospective forecast and 19 Sep as detection and naming. Claim only what the numbers show.
2. The incentive loop is P1 and likely static text. -> Keep the baseline ranking as a visible panel, headed "no behaviour change measured".
3. Attribution depends on about 13 notes. -> Show attributed vs "unexplained" counts on screen.
4. Build slack is thin. -> Precompute CSVs and use static plots for Impact and the B07 card if Streamlit step 3 slips. Keep the cut order already declared.
5. Demo is dense. -> If over 2:30, cut the classifier cutaway to one line and keep the Drill, the Brief and the B07 card.

PRESERVE: all verified events (B04 inverter 6-9 Oct, B05 composter 7-14 Sep, B06 leak, B02 stuck meter, B04 27 Aug calibration, B07 19 Sep, B03 note with no meter signal); the leak-free Outage Drill with naive baselines and the labelled best-case bar; evidence lines; data-computed impact with labelled assumptions and the on-screen "Scenario" label; the P0-lite classifier (held-out accuracy, ms per event, routing); deterministic LLM fallbacks; time-ordered split vs naive baselines; the four named 30+ constraints; both failure modes with mitigations; cut lines and the 15 min buffer.

Submit the complete revised proposal and address each point in the changelog.
```
