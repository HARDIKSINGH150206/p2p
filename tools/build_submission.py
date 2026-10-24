"""Builds the five competition deliverables into ./Required_Documents_for_P2P.
Needs the app running on :8000 (numbers are read from the API), screenshots from tools/shoot.mjs, and Chrome."""
import json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
import markdown
from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Required_Documents_for_P2P"
SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "screenshots" / "pack"
TMP = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / ".build_tmp"
BASE = "http://localhost:8000"
OUT.mkdir(exist_ok=True); TMP.mkdir(exist_ok=True)

def api(p): return json.load(urllib.request.urlopen(BASE + p, timeout=120))
st, br, fc, im, cl = api("/api/stats"), api("/api/brief"), api("/api/forecast"), api("/api/impact"), api("/api/classifier")
dr = json.loads(urllib.request.urlopen(urllib.request.Request(BASE + "/api/drill", data=b"{}", headers={"content-type": "application/json"}), timeout=120).read())
bl = im["baseline"]; best = fc["best_model_6h_all_test"]; n_ridge = sum(v == "ridge" for v in best.values())
m = dr["benchmark"]["mean_errors"]
al = {x["model"]: x["wape"] for x in fc["metrics"] if x["building_id"] == "B07" and x["window"] == "alumni_19sep" and x["horizon_h"] == 6}
acc = f'{cl["accuracy"]*100:.2f}%'

CSS = """
@page{size:A4;margin:13mm 14mm}*{box-sizing:border-box}
body{font-family:'Inter','Helvetica Neue',Arial,sans-serif;color:#15171a;font-size:9.4pt;line-height:1.42;margin:0}
h1{font-size:21pt;margin:0 0 2px;letter-spacing:-.02em}h2{font-size:12.5pt;margin:13px 0 5px;padding-bottom:3px;border-bottom:1.5px solid #0099ff;letter-spacing:-.01em}h3{font-size:10.2pt;margin:9px 0 3px}
p{margin:4px 0}ul{margin:3px 0 3px 17px;padding:0}li{margin:1.5px 0}.sub{color:#555;font-size:10pt;margin:0 0 6px}.meta{color:#666;font-size:8.2pt}
table{border-collapse:collapse;width:100%;margin:5px 0;font-size:8.5pt}th,td{border:1px solid #d6d9de;padding:3px 6px;text-align:left;vertical-align:top}th{background:#f1f4f8;font-weight:600}
code,pre{font-family:'JetBrains Mono',Menlo,Consolas,monospace;font-size:8pt;background:#f3f5f8;border-radius:3px}code{padding:0 3px}pre{padding:6px 8px;overflow:hidden;white-space:pre-wrap}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:14px}.kpi{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin:6px 0}.kpi div{border:1px solid #d6d9de;border-radius:6px;padding:5px 8px}.kpi b{font-size:13pt;display:block}.kpi span{font-size:7.8pt;color:#555}
.note{border-left:3px solid #f0b24a;background:#fff8ec;padding:4px 8px;margin:6px 0;font-size:8.6pt}.pb{break-after:page}blockquote{margin:5px 0;padding:4px 10px;border-left:3px solid #0099ff;background:#f5f9ff;color:#2a3340}
"""
def page(title, body, css=""):
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{CSS}{css}</style></head><body>{body}</body></html>"
def pdf(html, name):
    h = TMP / (Path(name).stem + ".html"); h.write_text(html, encoding="utf-8")
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={OUT / name}", f"file://{h}"], check=True, capture_output=True, timeout=180)
    n = len(PdfReader(str(OUT / name)).pages); print(name, n, "pages"); return n

# ---------------------------------------------------------------- 2. Technical report (exactly 3 pages)
svg = """<svg viewBox="0 0 760 250" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="9.5">
<defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7z" fill="#5b6672"/></marker></defs>
<g fill="#eef4fb" stroke="#9db7d6"><rect x="6" y="14" width="120" height="86" rx="6"/><rect x="6" y="122" width="120" height="50" rx="6"/></g>
<g fill="#eef4fb" stroke="#9db7d6"><rect x="160" y="14" width="140" height="158" rx="6"/></g>
<g fill="#fff6e8" stroke="#e0b46a"><rect x="336" y="6" width="134" height="40" rx="6"/><rect x="336" y="54" width="134" height="40" rx="6"/><rect x="336" y="102" width="134" height="40" rx="6"/><rect x="336" y="150" width="134" height="40" rx="6"/></g>
<g fill="#eafaf2" stroke="#7cc7a0"><rect x="336" y="198" width="134" height="40" rx="6"/></g>
<g fill="#eef0ff" stroke="#9aa1e6"><rect x="508" y="30" width="110" height="170" rx="6"/></g>
<g fill="#e6f4ff" stroke="#5aaee8"><rect x="650" y="14" width="104" height="80" rx="6"/><rect x="650" y="110" width="104" height="90" rx="6"/></g>
<g fill="#15171a" font-weight="600"><text x="14" y="32">Raw data (7 xlsx)</text><text x="14" y="140">Waste events</text><text x="168" y="32">Pipeline (src/pipeline.py)</text><text x="344" y="22">Ridge forecast</text><text x="344" y="70">Anomaly episodes</text><text x="344" y="118">Outage Drill</text><text x="344" y="166">Impact + incentive</text><text x="344" y="214">Bin classifier</text><text x="516" y="48">FastAPI</text><text x="658" y="32">Landing page</text><text x="658" y="128">Workspace</text></g>
<g fill="#4a5560" font-size="8.2"><text x="14" y="48">hourly meters</text><text x="14" y="60">daily summary</text><text x="14" y="72">staff logs</text><text x="14" y="84">calendar, buildings</text><text x="14" y="156">train 6,314 / test 1,601</text><text x="168" y="52">dedupe on (time, building)</text><text x="168" y="64">reindex 2,880 h x 8</text><text x="168" y="76">alias map 37 to 8</text><text x="168" y="88">units + plausibility</text><text x="168" y="100">notes to causes (regex)</text><text x="168" y="112">robust-z sensor faults</text><text x="168" y="130">writes data/processed/</text><text x="344" y="34">6 h and 12 h vs naive</text><text x="344" y="82">note, event, regime, rain</text><text x="344" y="130">hide, impute, reconnect</text><text x="344" y="178">kWh, Rs, CO2, kg, litres</text><text x="344" y="226">RF, 5 sensors, 6 classes</text><text x="516" y="66">/api/brief /forecast</text><text x="516" y="80">/impact /classifier</text><text x="516" y="94">/drill /timeseries</text><text x="516" y="108">/buildings /health</text><text x="516" y="130">one process,</text><text x="516" y="142">cache warm-up,</text><text x="516" y="154">gzip, static host</text><text x="658" y="52">hero, live stats,</text><text x="658" y="64">wired grid, API panel</text><text x="658" y="150">overview, drawer,</text><text x="658" y="162">forecast explorer,</text><text x="658" y="174">brief, drill, impact</text></g>
<g stroke="#5b6672" stroke-width="1.3" fill="none" marker-end="url(#a)"><path d="M126 57 H158"/><path d="M300 90 H334"/><path d="M300 60 L334 28"/><path d="M300 120 L334 70"/><path d="M300 140 L334 122"/><path d="M300 160 L334 170"/><path d="M126 147 L334 218"/><path d="M470 26 L506 80"/><path d="M470 74 L506 96"/><path d="M470 122 L506 118"/><path d="M470 170 L506 140"/><path d="M470 218 L506 160"/><path d="M618 90 L648 56"/><path d="M618 120 L648 150"/></g></svg>"""
tech = f"""
<h1>CircuGrid Brief — Technical Report</h1><p class="sub">Predictive Circular-Resource Grid for a Multi-Building Campus · Srujana 2026 “Prompt to Product” · <span class="meta">github.com/HARDIKSINGH150206/p2p</span></p>
<p>CircuGrid Brief fuses four noisy, asynchronous sources from eight campus buildings (hourly meters, daily summaries, staff logs, calendar) plus a smart-bin sensor stream into one grid. It forecasts demand, attributes anomalies to a probable cause with evidence, rehearses a building going offline, classifies waste at the edge, and computes the sustainability impact. Every figure below is produced by the code in the repository on the supplied (synthetic) dataset.</p>
<h2>1. System architecture</h2>{svg}
<table><tr><th style="width:21%">Component</th><th>Responsibility</th><th style="width:26%">File</th></tr>
<tr><td>Pipeline</td><td>Clean and fuse the sources; keep offline buildings visible; persist processed tables and integrity statistics.</td><td><code>src/pipeline.py</code></td></tr>
<tr><td>Forecast</td><td>One ridge regressor per building and horizon (6 h, 12 h) on hour-of-day, day type, weather, current load and footfall, same hour last week and yesterday. Time-ordered split.</td><td><code>src/forecast.py</code></td></tr>
<tr><td>Attribution</td><td>Anomaly episodes against the median of days in the same regime, attributed in a fixed order to a staff note, calendar event, regime shift or rain; ranked action cards with evidence lines.</td><td><code>src/insights.py</code></td></tr>
<tr><td>Outage Drill</td><td>Hide real hours, estimate from visible hours and a train-only day-type profile, reconnect, measure error vs baselines.</td><td><code>src/drill.py</code></td></tr>
<tr><td>Classifier</td><td>Median imputation + 100-tree random forest on five bin sensors, six classes; compost-or-flag routing.</td><td><code>src/classifier.py</code></td></tr>
<tr><td>API + UI</td><td>FastAPI serves JSON and the static frontend (no build step): landing page, workspace with overview, forecast explorer, per-building drawer.</td><td><code>src/api.py</code>, <code>web/</code></td></tr></table>
<p class="meta"><b>Stack:</b> Python 3.12, pandas 3.1, scikit-learn 1.9, FastAPI/uvicorn, vanilla HTML/CSS/JS. Runs CPU-only; no external API or key is required at runtime. Containerised (<code>Dockerfile</code>).</p>
<div class="pb"></div>
<h2>2. Data handling</h2>
<p>Seven raw files in <code>data/</code> are never modified; cleaned tables are rebuilt into <code>data/processed/</code> on every run (git-ignored).</p>
<table><tr><th>Source</th><th>Shape</th><th>Role</th><th>Issues found</th></tr>
<tr><td>hourly_streams</td><td>23,192 × 7</td><td>Meters, solar, footfall with arrival time</td><td>{st["hourly_duplicates_removed"]:.0f} duplicate rows; arrivals up to {st["late_arrival_max_h"]} h late; {st["hourly_gap_rows"]:.0f} missing hours</td></tr>
<tr><td>daily_summary</td><td>960 × 14</td><td>Utilities and waste per building-day</td><td>nulls: occupancy 5, electricity 11, water 11, wet organic 9 (kept as missing)</td></tr>
<tr><td>manual_logs</td><td>415 × 8</td><td>Staff readings and free-text notes</td><td>{st["manual_distinct_spellings"]:.0f} spellings for 8 buildings; units kWh/units, L/kL, kg/bags; {st["manual_values_rejected"]:.0f} implausible values</td></tr>
<tr><td>calendar</td><td>120 × 7</td><td>Day type, events, weather</td><td>clean</td></tr>
<tr><td>waste_events train / test</td><td>6,314 / 1,601</td><td>Labelled / unlabelled bin events</td><td>~2% nulls per sensor</td></tr>
<tr><td>buildings</td><td>8 × 10</td><td>Type, solar, composter flag</td><td>clean</td></tr></table>
<h3>Cleaning and fusion rules</h3><ul>
<li><b>Deduplication and ordering.</b> Rows are keyed on (timestamp, building) and the latest arrival wins, so retransmissions never double-count; late rows are placed by their capture time, not their arrival time.</li>
<li><b>Intermittent connectivity.</b> The hourly feed is reindexed to the full 2,880 h × 8 grid, so a building that goes silent stays on the grid as an explicit gap, is flagged <code>missing</code>, and short gaps are bridged only for modelling. The Outage Drill rehearses this on recorded data (the data holds no live buffering hardware).</li>
<li><b>Conflicting entries.</b> A hand-curated alias dictionary resolves all {st["manual_distinct_spellings"]:.0f} spellings (0 unresolved); a conversion table normalises units; per-stream plausibility ceilings reject unit errors (e.g. a 959,417 value). Manual electricity readings agree with the meter (median ratio 0.99, n = 152).</li>
<li><b>Notes become evidence.</b> An ordered regex table converts {st["manual_notes_parsed"]:.0f} free-text notes into causes (leak, composter, inverter, calibration, meter fault, AC left on, event).</li>
<li><b>Sensor faults are not waste.</b> A robust z-score flags the B04 reading of 6,234 kWh on 27 Aug; it is linked to the same-day “power analyzer being calibrated” note and excluded from savings.</li></ul>
<h3>Data flow</h3>
<table><tr><th>Stage</th><th>Input</th><th>Transformation</th><th>Output</th></tr>
<tr><td>Ingest + clean</td><td>raw xlsx</td><td>dedupe, reindex, alias, units, outliers</td><td><code>hourly_clean</code>, <code>daily_clean</code>, <code>manual_clean</code></td></tr>
<tr><td>Fuse</td><td>cleaned tables + calendar</td><td>join on building and time, regime labels</td><td>model features and baselines</td></tr>
<tr><td>Model</td><td>fused features</td><td>forecast, episodes, drill, classifier</td><td>JSON results (cached at start-up)</td></tr>
<tr><td>Serve</td><td>results</td><td>FastAPI, gzip, health check</td><td>landing page and workspace</td></tr></table>
<p class="note"><b>Privacy:</b> only aggregates are used (occupancy and footfall per building, no individuals). Incentives compare a building with its own baseline so large buildings are not penalised.</p>
<div class="pb"></div>
<h2>3. Models, evaluation and trade-offs</h2>
<div class="kpi"><div><b>{acc}</b><span>bin classifier hold-out accuracy (target &gt;85%), n = {sum(v["support"] for v in cl["per_class"].values())}</span></div><div><b>{cl["latency_ms"]["p50"]} ms</b><span>per event, p50, laptop CPU</span></div><div><b>{n_ridge}/8</b><span>buildings where ridge is best at 6 h</span></div><div><b>{br["attribution_counts"]["attributed"]}/{br["n_episodes"]}</b><span>anomaly episodes attributed</span></div></div>
<table><tr><th>Component</th><th>Method and evaluation</th><th>Result</th></tr>
<tr><td>Forecast</td><td>Train on target times before 18 Sep; score on later days against “same hour last week” and “same hour yesterday”. MAE and WAPE per building, horizon and window.</td><td>Best of three in {n_ridge} of 8 buildings at 6 h; last-week naive wins {", ".join(k for k, v in best.items() if v != "ridge")}. On the B07 alumni-meet day the yesterday baseline (WAPE {al["naive_same_hour_yesterday"]}) beat ridge ({al["ridge"]}).</td></tr>
<tr><td>Outage Drill</td><td>B04, 6 h window at 10:00, averaged over {dr["benchmark"]["n_windows"]} test days. The headline imputer never sees the hidden hours.</td><td>MAE {m["profile_scaled_visible"]["mae"]} kWh ({m["profile_scaled_visible"]["mape"]*100:.1f}%) vs {m["same_hours_last_week"]["mae"]} (last week), {m["unscaled_profile"]["mae"]} (unscaled profile), {m["flat_visible_mean"]["mae"]} (flat mean).</td></tr>
<tr><td>Classifier</td><td>Stratified 80/20 split of the labelled file. 5-fold CV on the training split: ≈84.6%; random forest, extra trees and boosting all land near 84.5%, so we did not tune on the hold-out.</td><td>{acc} accuracy; per-class recall 0.70 (glass) to 0.90 (metal). Predictions for the 1,601 unlabelled events are in <code>waste_events_test_predictions.csv</code>; no accuracy is claimed on them.</td></tr>
<tr><td>Attribution</td><td>Ordered rules: note ±1 day → calendar event → regime shift → rain → unexplained. Solar skips events (only weather plausibly explains it).</td><td>{br["attribution_counts"]["attributed"]} of {br["n_episodes"]} episodes attributed, each with an evidence line and action.</td></tr></table>
<h3>Accuracy–compute trade-off (edge)</h3>
<p>A ridge model per building fits in about 0.01–0.05 s and predicts in microseconds; a gradient-boosting model was timed at roughly 0.14 s per fit on an idle laptop (fit times in the API: ridge {fc["fit_time_s"]["ridge"]} s, boosting {fc["fit_time_s"]["hgb"]} s on this run). Because the forecast is close to persistence at 6 h and ridge already matches or beats the naive baselines in most buildings, the cheaper model is the right edge choice; boosting would cost more without a demonstrated gain.</p>
<h2>4. Scale, cost, failure modes</h2>
<div class="cols"><div><h3>From 8 to 30+ buildings</h3><ul><li><b>Alias table</b> filled at onboarding; unmatched names go to a review queue.</li><li><b>One small model per building;</b> cold start uses the day-type profile for about two weeks.</li><li><b>Late-arrival replay</b> bounded per building (here ≤ 12 h).</li><li><b>Central roll-up</b> of Brief rows only; raw streams stay on the edge box.</li></ul>
<p class="meta">Per-building hardware: ≈ Rs 12,000 (ESP32 + meter 3,500; two-bin sensor kit 3,000; Pi-class box 5,000; misc 500) — a planning assumption, not a quote.</p></div>
<div><h3>Failure modes and mitigations</h3><ul><li><b>Sensor drift or fault.</b> Robust outlier flag cross-checked against notes; flagged readings excluded from forecasts and savings (demonstrated on B04, 27 Aug).</li><li><b>Gaming the incentive.</b> Savings computed from meters, not logs; per-building baseline.</li><li><b>Model degradation over a semester.</b> Rolling baseline reset after exam or break regimes; error tracked against the naive baseline.</li></ul></div></div>
<p class="note"><b>Known limitations:</b> synthetic data; classifier is {acc}, just under 85%; latency measured on a laptop, not edge hardware; manual numeric readings are cleaned but not yet fused; the incentive loop is a baseline ranking with no behaviour change measured; scale claims are a design argument, not load-tested.</p>
"""
n = pdf(page("CircuGrid Brief — Technical Report", tech), "Technical_Report.pdf")
if n != 3:
    print("!! technical report must be exactly 3 pages, got", n); sys.exit(1)

# ---------------------------------------------------------------- 3. UI screenshots package
SEC = [
 ("A. Telemetry dashboard", [("10_overview_kpis", "Live KPIs with sparklines: grid electricity, carbon, solar share, composted, landfill, anomalies explained."), ("11_overview_series_and_alerts", "Daily telemetry stacked by building with staff-note and calendar-event pins, beside the ranked “Needs attention” alerts."), ("12_overview_heatmap", "Building-by-day anomaly heatmap, normalised by day type, so faults stand out from term/break shifts."), ("13_overview_building_cards", "Eight building cards: share of grid electricity, solar and composter badges, flag counts."), ("15_building_drawer", "Per-building drawer: KPIs, electricity with notes pinned, live 6 h forecast, flags and notes.")]),
 ("B. Circular waste allocations", [("14_overview_waste_classifier_forecast", "Composted vs recycled vs landfill per building, the edge classifier accuracy ring, and the B07 forecast."), ("25_bin_classifier_waste_routing", "Bin classifier: hold-out accuracy, latency, confusion matrix, and routing of food waste to composter buildings."), ("24_impact", "Impact view: kWh, carbon, rupees, composted and landfill mass, attributed events, assumptions, incentive baseline.")]),
 ("C. Facility alerts", [("21_brief_facility_alerts", "The Brief: each alert has a cause, an evidence line from the staff log or calendar, a confidence and a ranked action.")]),
 ("D. Forecasting and resilience", [("22_forecast_explorer", "Forecast explorer: any building, 6 h or 12 h, any window; ridge vs two naive baselines."), ("23_outage_drill", "Outage Drill after reconnect: estimated vs replayed hours and the measured error against baselines."), ("20_grid_wired", "Wired grid: five sources fuse into one hub and six outputs come alive.")]),
 ("E. Landing page", [("01_landing_hero", "Landing page hero with a live dashboard preview."), ("02_landing_stats_and_steps", "Live statistics strip and the three-step explanation."), ("03_landing_wired_grid", "Interactive wired graph on the landing page."), ("04_landing_campus_map", "Campus map sized by electricity share, scale argument and hardware budget assumption."), ("05_landing_constraints", "Status of each problem-statement constraint: built, partly, design only.")]),
]
html, k = "", 0
cover = "<h1>UI Screenshots Package</h1><p class='sub'>CircuGrid Brief · all figures are live values from the running application</p><table><tr><th>Section</th><th>Screens</th></tr>" + "".join(f"<tr><td>{t}</td><td>{len(s)}</td></tr>" for t, s in SEC) + "</table><p class='meta'>Screens are captured from the running app with a Chrome DevTools script (tools/shoot.mjs). Dashboard, waste-allocation and alert views are grouped as requested.</p><div class='pb'></div>"
html += cover
for t, shots in SEC:
    head = f"<h2 style='break-after:avoid'>{t}</h2>"
    for name, cap in shots:
        im_ = Image.open(SHOTS / f"{name}.png"); w, h = im_.size; step = int(w * 1.28); parts = []
        y = 0
        while y < h:
            parts.append(im_.crop((0, y, w, min(h, y + step)))); y += step
        for i, part in enumerate(parts):
            f_ = TMP / f"{name}_{i}.png"; part.save(f_)
            wpct = 100 if w >= 800 else 50
            html += f"<div style='break-inside:avoid;margin:8px 0 14px'>{head}<img src='file://{f_}' style='width:{wpct}%;display:block;margin:0 auto;border-radius:6px;border:1px solid #ccd'><p class='meta'><b>Fig. {k + 1}{'' if len(parts) == 1 else '.' + str(i + 1)}</b> — {cap}{' (continued)' if i else ''}</p></div>"
            head = ""
        k += 1
pdf(page("UI Screenshots Package", html), "UI_Screenshots_Package.pdf")

# ---------------------------------------------------------------- 4. Project overview
feat = [("Fusion and cleaning", "Built", "Dedupe, full-grid reindex, alias map, units, note parsing, sensor-fault flag"), ("Forecast 6 h / 12 h", "Built", f"Ridge per building vs two naive baselines; best in {n_ridge}/8 at 6 h"), ("Root-cause Brief", "Built", f'{br["attribution_counts"]["attributed"]}/{br["n_episodes"]} episodes attributed with evidence'), ("Outage Drill", "Built", f'B04 6 h error {m["profile_scaled_visible"]["mae"]} kWh vs {m["same_hours_last_week"]["mae"]} naive'), ("Edge bin classifier + routing", "Partly", f"{acc} (target 85%); not run on edge hardware"), ("Impact and incentive baseline", "Partly", "Impact computed from data; incentive is a baseline ranking, no behaviour change measured"), ("Web app: landing + workspace", "Built", "Overview, drawer, forecast explorer, brief filters, wired grid"), ("Deployment", "Partly", "Dockerfile, Procfile, render.yaml; verified from a clean clone; hosted deploy done by the team")]
ov = f"""
<h1>CircuGrid Brief — Project Overview</h1><p class="sub">Srujana 2026 “Prompt to Product: Prompt for the Planet” · problem: Predictive Circular-Resource Grid for a Multi-Building Campus</p>
<h2>1. The initial idea</h2>
<p>Campus facilities teams audit buildings by hand, so faults and surges are noticed days late and nobody can say why they happened. The problem statement asked for a grid that fuses noisy sources, forecasts 6–12 hours ahead, classifies waste at the edge, survives connectivity gaps, explains anomalies, and nudges occupants. Our first concept (A) was a single control room covering all of that. We did not pick it by taste: we ran it through a generator–critic loop (below), and the winning framing became <b>CircuGrid Brief</b>: <i>forecast the surge, name the cause, fix it first</i>.</p>
<p>Data findings that shaped it ({bl["days"]} days, 8 buildings): {bl["electricity_kwh"]:,} kWh ≈ {bl["co2_t"]} t CO₂; the two hostels and the food court use ~65% of electricity and ~95% of wet organic waste; rooftop solar covers {bl["solar_share_pct"]}%; and free-text staff notes reveal faults the meters never flagged (a leak, a burnt-out composter motor, a solar inverter fault, a meter calibration).</p>
<h2>2. Development process</h2>
<table><tr><th style="width:22%">Stage</th><th>What we did</th></tr>
<tr><td>Rules first</td><td>A project constitution (<code>CLAUDE.md</code>) fixed the deadline, rubric, “every number computed from data” and “update the workbook after every task” before any code.</td></tr>
<tr><td>Data audit</td><td>Profiled all seven files; found duplicates, late arrivals, 37 building spellings, mixed units and the faults hidden in notes.</td></tr>
<tr><td>Idea selection</td><td>Separate ideator and evaluator agents with fresh context, three rounds, scores <b>7.2 → 8.0 → 8.3</b>. The judge caught a demo hook that contradicted the data and a leaky evaluation; we built from the best version and did not claim it passed its 8.5 gate.</td></tr>
<tr><td>Parallel plan</td><td>Function contracts (<code>docs/CONTRACTS.md</code>), phase branches and a PR workflow so two people could build concurrently; later the team built directly on <code>main</code>.</td></tr>
<tr><td>Build</td><td>Backend and ML first (pipeline, forecast, attribution, drill, classifier, impact, API), then a rough UI, then the final frontend adapted from a previous project’s design system and a reference landing template.</td></tr>
<tr><td>Verification</td><td>A DevTools-protocol harness clicked every control and recorded console errors; it found a real bug (duplicate element ids that wiped two landing sections). Clean-clone install and endpoint smoke test before deployment.</td></tr></table>
<h2>3. Tools used</h2>
<ul><li><b>Claude Code</b> (Claude Sonnet 5.5) as the coding agent; fresh Claude subagents as independent ideator and evaluator.</li><li><b>Python, pandas, scikit-learn, FastAPI/uvicorn</b>; vanilla HTML/CSS/JS; headless Chrome for testing and PDF generation; Git/GitHub; Docker.</li><li>No runtime LLM: all intelligence in the product is classical ML and statistics; there is no API key dependency. Prompts and iterations are logged in the Prompt Workbook.</li></ul>
<h2>4. Implemented features</h2>
<table><tr><th>Feature</th><th style="width:9%">Status</th><th>Detail</th></tr>{"".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in feat)}</table>
<h2>5. Final outcome</h2>
<div class="kpi"><div><b>{acc}</b><span>bin classifier hold-out accuracy</span></div><div><b>{n_ridge}/8</b><span>buildings where ridge is best (6 h)</span></div><div><b>{m["profile_scaled_visible"]["mae"]} kWh</b><span>Outage Drill error, B04</span></div><div><b>{br["attribution_counts"]["attributed"]}/{br["n_episodes"]}</b><span>anomalies attributed</span></div></div>
<p>The result is a working, demonstrable product: a landing page and a workspace served by one FastAPI process, running on the supplied dataset, with every number computed from it. In a live walkthrough, an operator can connect the five sources, see the B04 inverter fault, the B05 composter outage and the B07 alumni-meet surge named with their evidence, rehearse an outage, and read the impact with its assumptions.</p>
<p class="note"><b>Honest gaps.</b> The classifier is {acc}, just under the 85% target. The forecast is close to persistence and loses to a naive baseline in three buildings. Manual numeric readings are cleaned but not fused. Latency is measured on a laptop, not edge hardware. The incentive loop is a baseline ranking. The optional LLM text feature in the original plan was not built. The dataset is synthetic, so results show feasibility, not field performance.</p>
<p class="meta">Repository: github.com/HARDIKSINGH150206/p2p · Team: Hardik Singh (product, ML, backend, frontend); data-cleaning exploration by NYN-05.</p>
"""
pdf(page("CircuGrid Brief — Project Overview", ov), "Project_Overview.pdf")

# ---------------------------------------------------------------- 1. Prompt workbook
md = (ROOT / "docs" / "PROMPT_WORKBOOK.md").read_text(encoding="utf-8")
body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
wcss = "body{font-size:8.9pt}h1{font-size:19pt}h2{font-size:12pt;break-after:avoid}h3{break-after:avoid}table{font-size:7.9pt}th,td{padding:2px 5px}hr{border:0;border-top:1px solid #d6d9de;margin:10px 0}blockquote p{margin:3px 0}a{color:#0066cc;text-decoration:none}"
pdf(page("Prompt Workbook — CircuGrid Brief", body, wcss), "Prompt_Workbook.pdf")

# ---------------------------------------------------------------- 5. predictions CSV
src = ROOT / "data" / "processed" / "waste_events_test_predictions.csv"
shutil.copy(src, OUT / "waste_events_test_predictions.csv")
rows = (OUT / "waste_events_test_predictions.csv").read_text().splitlines()
assert rows[0] == "event_id,predicted_class" and len(rows) == 1602, "predictions CSV malformed"
print("csv rows:", len(rows) - 1)
