/* Landing page. Needs common.js (graph, helpers). All figures come from the API. */
window.navTo = (k) => { location.href = '/app#' + k; };
const DEV = { buildings: null };
const touch = () => { update(); renderHero(); renderFeat(); renderCmp(); renderData(); renderStrip(); renderFaq(); };
buildGraph(); measure();
if (location.search.includes('demo')) setTimeout(() => $('gAll').click(), 600);

/* ---- tilt hero ---- */
const tilt = $('tilt');
const flatten = () => { const r = tilt.getBoundingClientRect(); tilt.classList.toggle('flat', r.top < innerHeight * 0.8); };
addEventListener('scroll', flatten, { passive: true }); setTimeout(flatten, 900);
if (location.search.includes('flat')) tilt.classList.add('flat');

function renderHero() {
  const b = D.impact && D.impact.baseline, br = D.brief, fc = D.forecast; if (!b || !br || !fc) return;
  const s = fc.b07_19sep;
  $('heroDash').innerHTML = `<div class="kpis"><div class="kpi"><b>${f(b.electricity_kwh)}</b><span>kWh · 120 days</span></div><div class="kpi"><b>${f(b.co2_t, 1)} t</b><span>CO2 at 0.70 kg/kWh</span></div><div class="kpi"><b>${b.solar_share_pct}%</b><span>solar share</span></div><div class="kpi"><b>${br.attribution_counts.attributed}/${br.n_episodes}</b><span>anomalies attributed</span></div></div>
  <canvas class="chart" id="heroC" width="900" height="200" style="height:170px;margin-bottom:12px"></canvas>
  <div class="mini-cards">${br.cards.slice(1, 4).map((c) => `<div class="mini"><h4>${c.title}</h4><span class="ws-chip ws-chip-ok">${c.confidence}</span><p class="meta" style="margin:6px 0 0">${c.evidence.slice(0, 74)}…</p></div>`).join('')}</div>`;
  line($('heroC'), [s.actual, s.forecast, s.naive_week, s.naive_day], ['#f2efe9', '#34d399', '#f87171', '#0099ff']);
}

/* ---- features ---- */
const FEATS = ['Forecast', 'Root cause', 'Outage Drill', 'Impact', 'Bin classifier'];
let feat = 0;
$('featTabs').innerHTML = FEATS.map((t, i) => `<button role="tab" data-i="${i}">${t}</button>`).join('');
$('featTabs').onclick = (e) => { const b = e.target.closest('button'); if (b) { feat = +b.dataset.i; renderFeat(); } };
function renderFeat() {
  [...$('featTabs').children].forEach((b, i) => b.classList.toggle('on', i === feat));
  const fc = D.forecast, br = D.brief, im = D.impact, cl = D.classifier, dr = D.drillB; let t = '', p = '<p class="empty">Loading…</p>';
  if (feat === 0) {
    t = ['Forecast 6 to 12 hours ahead', 'A small ridge model per building predicts the next hours of electricity from the hour, day type, weather, current load and footfall. It is scored on days it never saw, against two naive baselines.', 'On the Alumni-meet Saturday the baseline “same hour yesterday” beat the model. We report that, because the real value is that the residual flags and names the surge.'];
    if (fc) { const best = fc.best_model_6h_all_test, n = Object.values(best).filter((m) => m === 'ridge').length, row = fc.metrics.filter((x) => x.building_id === 'B07' && x.window === 'all_test' && x.horizon_h === 6);
      p = `<div class="kpis"><div class="kpi"><b>${n}/8</b><span>buildings where ridge is best (6 h)</span></div><div class="kpi"><b>${fc.fit_time_s.ridge}s</b><span>ridge fit time</span></div></div><table><tr><th>B07 · 6 h · all test days</th><th>MAE kWh</th><th>WAPE</th></tr>${row.map((x) => `<tr><td>${x.model.replace('naive_same_hour_', 'naive ')}</td><td>${x.mae}</td><td>${x.wape}</td></tr>`).join('')}</table>`; }
  } else if (feat === 1) {
    t = ['Causes, not just charts', 'A flagged day is matched to a staff note, then a calendar event, then a regime shift or weather. Every card carries its evidence line and a ranked action.', 'A 6,234 kWh reading at B04 is traced to a “power analyzer being calibrated” note and labelled a sensor fault, so it is never counted as waste.'];
    if (br) p = `<div class="kpis"><div class="kpi"><b>${br.attribution_counts.attributed}</b><span>attributed</span></div><div class="kpi"><b>${br.attribution_counts.unexplained}</b><span>unexplained</span></div></div>` + br.cards.slice(0, 2).map((c) => `<div class="mini" style="margin-bottom:10px"><h4>${c.title}</h4><div class="ev">${c.evidence}</div></div>`).join('');
  } else if (feat === 2) {
    t = ['Offline buildings stay on the grid', 'Hide a window of real hours, estimate them from the visible hours of that day and a profile learned on training days only, then reconnect and measure the error.', 'The headline method never sees the hidden hours. The variant that uses the daily total is shown separately as a best case.'];
    const m = dr && dr.benchmark && dr.benchmark.mean_errors;
    if (m) p = `<div class="kpis"><div class="kpi"><b>${m.profile_scaled_visible.mae} kWh</b><span>MAE, B04, ${dr.benchmark.n_windows} test days</span></div><div class="kpi"><b>${m.same_hours_last_week.mae} kWh</b><span>last-week naive</span></div></div><table><tr><th>method (6 h hidden)</th><th>MAE</th><th>MAPE</th></tr>${Object.entries(m).map(([k, v]) => `<tr><td>${k.replace(/_/g, ' ')}</td><td>${v.mae}</td><td>${(v.mape * 100).toFixed(1)}%</td></tr>`).join('')}</table>`;
  } else if (feat === 3) {
    t = ['Impact you can trace', 'Energy, carbon, cost, water and landfill are computed from the daily records using the data guide’s constants. Events show what was lost or avoidable, labelled as scenarios.', 'No behaviour change is claimed: the incentive view compares each building with its own baseline only.'];
    if (im) { const b = im.baseline; p = `<div class="kpis"><div class="kpi"><b>${f(b.co2_t, 1)} t</b><span>CO2 baseline</span></div><div class="kpi"><b>Rs ${f(b.cost_rs / 1e6, 1)}M</b><span>electricity cost</span></div><div class="kpi"><b>${f(b.composted_kg / 1000, 1)} t</b><span>composted</span></div><div class="kpi"><b>${f(b.landfill_kg / 1000, 1)} t</b><span>landfill</span></div></div>${im.events.slice(0, 3).map((e) => `<div class="mini" style="margin-bottom:8px"><h4>${e.title}</h4></div>`).join('')}`; }
  } else {
    t = ['Edge-sized waste classifier', 'Five bin sensors in, six waste classes out, from a small random forest that runs on CPU in milliseconds. Evaluated on a stratified hold-out of the labelled file.', 'Predicted food waste is routed to a composter where the building has one, and flagged where it does not.'];
    if (cl && cl.accuracy) p = `<div class="kpis"><div class="kpi"><b>${(cl.accuracy * 100).toFixed(2)}%</b><span>hold-out accuracy (target 85%)</span></div><div class="kpi"><b>${cl.latency_ms.p50} ms</b><span>per event, p50</span></div></div><table><tr><th>class</th><th>precision</th><th>recall</th></tr>${Object.entries(cl.per_class).map(([k, v]) => `<tr><td>${k}</td><td>${v.precision}</td><td>${v.recall}</td></tr>`).join('')}</table>`;
  }
  $('featBody').innerHTML = `<div class="txt"><h3>${t[0]}</h3><p>${t[1]}</p><p>${t[2]}</p></div><div class="panel">${p}</div>`;
}

/* ---- campus map ---- */
const POS = { B01: [18, 34], B02: [32, 66], B03: [46, 28], B04: [63, 62], B05: [78, 30], B06: [88, 66], B07: [52, 80], B08: [9, 70] };
(function dots() { let h = ''; for (let y = 0; y < 26; y++) for (let x = 0; x < 72; x++) h += `<circle cx="${x * 16 + 8}" cy="${y * 16 + 8}" r="1.3"/>`; $('mapDots').innerHTML = `<svg width="100%" height="100%" viewBox="0 0 1152 416" preserveAspectRatio="xMidYMid slice" fill="rgba(255,255,255,.16)">${h}</svg>`; })();
fetch('/api/buildings').then((r) => r.json()).then((bs) => {
  DEV.buildings = bs; const max = Math.max(...bs.map((b) => b.electricity_kwh)), map = $('map'), tip = $('mapTip');
  bs.forEach((b) => { const sz = 38 + 56 * (b.electricity_kwh / max), n = document.createElement('div'); n.className = 'node' + (b.has_composter ? ' comp' : ''); n.style.cssText = `left:${POS[b.building_id][0]}%;top:${POS[b.building_id][1]}%;width:${sz}px;height:${sz}px`;
    n.innerHTML = `${b.building_id}${b.has_solar ? '<span class="sun">☼</span>' : ''}<small>${b.building_name.replace('Engineering Labs & Innovation Centre', 'Eng. Labs')} · ${b.electricity_share_pct}%</small>`;
    n.onmousemove = (e) => { const r = map.getBoundingClientRect(); tip.style.opacity = 1; tip.style.left = Math.min(e.clientX - r.left + 14, r.width - 210) + 'px'; tip.style.top = Math.max(8, e.clientY - r.top - 90) + 'px';
      tip.innerHTML = `<b>${b.building_name}</b><br>${b.building_type} · ${b.floors} floors · built ${b.year_built}<br>electricity ${f(b.electricity_kwh)} kWh (${b.electricity_share_pct}%)<br>${b.has_solar ? 'solar ' + f(b.solar_kwh) + ' kWh · ' : 'no solar · '}${b.has_composter ? 'composted ' + f(b.composted_kg) + ' kg' : 'no composter'}<br>landfill ${f(b.landfill_kg)} kg`; };
    n.onmouseleave = () => (tip.style.opacity = 0); map.append(n); });
});

/* ---- developers ---- */
const EPS = [['brief', 'GET', '/api/brief'], ['forecast', 'GET', '/api/forecast'], ['impact', 'GET', '/api/impact'], ['classifier', 'GET', '/api/classifier'], ['drill', 'POST', '/api/drill']];
let ep = 0;
$('devTabs').innerHTML = EPS.map(([n], i) => `<button data-i="${i}">${n}</button>`).join('');
$('devTabs').onclick = (e) => { const b = e.target.closest('button'); if (b) { ep = +b.dataset.i; renderDev(); } };
function hl(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"([^"]+)":/g, '<span class="k">"$1"</span>:').replace(/: "([^"]*)"/g, ': <span class="s">"$1"</span>').replace(/: (-?\d+\.?\d*)/g, ': <span class="n">$1</span>'); }
async function renderDev() {
  [...$('devTabs').children].forEach((b, i) => b.classList.toggle('on', i === ep)); const [n, m, u] = EPS[ep];
  $('devReq').innerHTML = m === 'GET' ? `<span class="k">curl</span> http://localhost:8000${u}` : `<span class="k">curl</span> -X POST http://localhost:8000${u} \\\n  -H "content-type: application/json" \\\n  -d '{"building_id":"B04",\n       "start":"2026-10-08 10:00",\n       "hours":6}'`;
  $('devRes').textContent = 'loading…'; $('devStatus').textContent = 'response'; const t0 = performance.now();
  const r = m === 'GET' ? await fetch(u) : await fetch(u, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ building_id: 'B04', start: '2026-10-08 10:00', hours: 6 }) });
  const j = await r.json(), txt = JSON.stringify(j, null, 2).split('\n'); $('devStatus').textContent = `${r.status} · ${Math.round(performance.now() - t0)} ms · ${txt.length} lines (first 32 shown)`;
  $('devRes').innerHTML = hl(txt.slice(0, 32).join('\n')) + (txt.length > 32 ? '\n<span style="color:var(--paper-4)">…</span>' : '');
}
renderDev();

/* ---- data files ---- */
const FILES = [
  ['hourly_streams', '23,192 × 7', 'Hourly electricity, water, solar and footfall per building, with arrival time.', () => { const s = D.stats || {}; return `${f(s.hourly_duplicates_removed)} duplicates removed, reindexed to ${f(s.hourly_grid_rows)} hourly rows, ${f(s.hourly_gap_rows)} gap rows flagged and bridged, arrivals up to ${s.late_arrival_max_h} h late.`; }],
  ['daily_summary', '960 × 14', 'Per building-day: occupancy, utilities, segregated waste, composted, recycled, landfill.', () => 'Baselines per regime and anomaly episodes; impact and incentive figures. Nulls (occupancy 5, electricity 11, water 11, wet organic 9) are left as missing, not guessed.'],
  ['manual_logs', '415 × 8', 'Staff entries in mixed units under many spellings, plus free-text notes.', () => { const s = D.stats || {}; return `${f(s.manual_distinct_spellings)} spellings mapped to 8 buildings, units normalised, ${f(s.manual_values_rejected)} implausible values rejected, ${f(s.manual_notes_parsed)} notes turned into causes.`; }],
  ['calendar', '120 × 7', 'Day type, events, temperature, rainfall, humidity.', () => 'Used as forecast features and as the second attribution step (for example the 19 Sep alumni meet, and rain on 9 Oct that explains a solar dip).'],
  ['waste_events_train', '6,314 × 10', 'Labelled smart-bin events with five sensor readings.', () => 'Trains the classifier; accuracy comes from a stratified 20% hold-out of this file.'],
  ['waste_events_test', '1,601 × 9', 'Unlabelled bin events.', () => 'Classified and routed; predictions written to a CSV. No accuracy is claimed, because there are no labels.'],
  ['buildings', '8 × 10', 'Type, floors, area, solar capacity, composter flag.', () => 'Drives the campus map and the compost-or-flag routing.'],
];
let df = 0;
$('dataTabs').innerHTML = FILES.map(([n], i) => `<button data-i="${i}">${n}</button>`).join('');
$('dataTabs').onclick = (e) => { const b = e.target.closest('button'); if (b) { df = +b.dataset.i; renderData(); } };
function renderData() { [...$('dataTabs').children].forEach((b, i) => b.classList.toggle('on', i === df)); const [n, sh, d, use] = FILES[df]; $('dataBody').innerHTML = `<div class="txt"><h3 class="lp-mono" style="font-size:20px">${n}.xlsx</h3><p>${d}</p></div><div class="panel"><div class="kpis"><div class="kpi"><b style="font-size:22px">${sh}</b><span>rows × columns</span></div></div><p style="color:var(--paper-2);line-height:1.6;margin:0">${use()}</p></div>`; }

/* ---- constraints ---- */
function renderCmp() {
  const cl = D.classifier, fc = D.forecast, br = D.brief, st = D.stats || {}, n = fc ? Object.values(fc.best_model_6h_all_test).filter((m) => m === 'ridge').length : '…';
  const c = { B: ['ws-chip-ok', 'Built'], P: ['ws-chip-warn', 'Partly'], D: ['', 'Design only'] };
  const rows = [
    ['Multi-source fusion under noise', `Hourly meters, daily summary, staff notes and calendar joined on building and time. ${f(st.hourly_duplicates_removed)} duplicates removed; offline gaps are kept, not dropped. Manual meter readings are cleaned but not yet fused.`, 'P'],
    ['Edge classification, 5+ classes, >85%, <2 s', cl && cl.accuracy ? `6 classes, ${(cl.accuracy * 100).toFixed(2)}% on a hold-out (just under 85%), ${cl.latency_ms.p50} ms per event on a laptop. Not yet run on edge hardware.` : '…', 'P'],
    ['Forecast 6 to 12 h ahead', `Ridge per building at 6 h and 12 h against two naive baselines; best in ${n} of 8 buildings at 6 h. Accuracy and compute trade-off is shown in the Forecast tab.`, 'B'],
    ['Intermittent connectivity and integrity', 'Duplicates dropped by key, late rows ordered by arrival, gaps explicit. The Outage Drill rehearses an offline window on recorded data. No live buffering hardware.', 'P'],
    ['Root-cause attribution with ranked actions', br ? `${br.attribution_counts.attributed} of ${br.n_episodes} episodes attributed, each with an evidence line and an action.` : '…', 'B'],
    ['Behavioural and economic incentive loop', 'A baseline ranking per occupant exists, labelled “no behaviour change measured”. A staggered pilot design is written down but not run.', 'P'],
    ['Cost and scale envelope', 'Rs 12,000 per building (an assumption with line items) and a four-point argument for 30+ buildings. Not load-tested.', 'D'],
    ['Failure-mode awareness', 'Sensor fault (the B04 calibration reading is excluded) and gaming or model drift, each with a mitigation: savings computed from meters not logs, rolling baselines with error tracked against naive.', 'B'],
  ];
  $('cmp').innerHTML = `<tr><th>Constraint</th><th>What we did, and where we stand</th><th>Status</th></tr>` + rows.map(([a, b, s]) => `<tr><td>${a}</td><td>${b}</td><td><span class="ws-chip ${c[s][0]}">${c[s][1]}</span></td></tr>`).join('');
}

J('/api/stats').then((s) => { D.stats = s; touch(); });
J('/api/brief').then((r) => { D.brief = r; touch(); });
J('/api/forecast').then((r) => { D.forecast = r; touch(); });
J('/api/impact').then((r) => { D.impact = r; touch(); });
J('/api/classifier').then((r) => { D.classifier = r; touch(); });
J('/api/drill', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }).then((r) => { D.drillB = r; touch(); });
renderFeat(); renderData(); renderCmp();

/* ---- live stats strip ---- */
function renderStrip() {
  const st = D.stats, br = D.brief, cl = D.classifier, im = D.impact; if (!st || !br || !cl || !im) return;
  $('strip').innerHTML = [[f(st.hourly_grid_rows), 'hourly readings fused from ' + f(st.hourly_rows_raw) + ' raw rows'], [br.attribution_counts.attributed + ' / ' + br.n_episodes, 'anomalies attributed to a cause'], [(cl.accuracy * 100).toFixed(2) + '%', 'bin classifier hold-out accuracy'], [f(im.baseline.co2_t, 1) + ' t', 'CO2 baseline tracked, 120 days']].map(([a, b]) => `<div class="sti"><b>${a}</b><span>${b}</span></div>`).join('');
}
/* ---- how it works ---- */
$('steps').innerHTML = [
  ['01 · Connect', 'Fuse what you already log', 'Hourly meters, daily summaries, staff notes, the academic calendar and bin sensors join on building and time. Duplicates, late rows and unit mix-ups are fixed on the way in.', ['Offline buildings stay on the grid', 'Alias table for messy building names', 'Raw files are never modified']],
  ['02 · Understand', 'Forecast, then explain', 'A small model per building predicts the next 6 to 12 hours. When a day breaks the pattern, the system looks for a note, an event or the weather that explains it, and shows its evidence.', ['Scored against naive baselines', 'Sensor faults are not counted as waste', 'Every card carries an evidence line']],
  ['03 · Act', 'Rank the fix, count the saving', 'Actions are ranked with kWh, rupees, CO2 and kilograms of waste attached, and labelled as scenarios. Rehearse an outage before it happens.', ['Constants from the data guide', 'Assumptions shown beside every figure', 'No behaviour change is claimed']],
].map(([n, t, p, u]) => `<div class="step"><span class="n">${n}</span><h3>${t}</h3><p>${p}</p><ul>${u.map((x) => `<li>${x}</li>`).join('')}</ul></div>`).join('');
/* ---- plans (hardware = buildings x Rs 12,000 planning assumption) ---- */
const per = 12000, rs = (n) => 'Rs ' + n.toLocaleString('en-IN');
$('planGrid').innerHTML = [
  ['Pilot', 'One block, to prove it', 3, 'warm', ['Fusion and Brief for 3 buildings', 'Forecast 6 h and 12 h', 'Outage Drill on recorded data', 'Edge bin classifier on 2 bins per building'], 'Start a pilot', false],
  ['Campus', 'A whole campus on one grid', 8, 'hot', ['All 8 buildings of this dataset', 'Per-building models and baselines', 'Incentive baseline by occupancy', 'Impact view with assumptions'], 'Open the workspace', true],
  ['Network', 'Many campuses, one view', 30, 'cool', ['30+ buildings per deployment', 'Alias onboarding with a review queue', 'Central roll-up of Brief rows only', 'Raw streams stay on each edge box'], 'Read the scale plan', false],
].map(([n, w, b, , li, cta, hot]) => `<div class="plan ${hot ? 'hot' : ''}"><h3>${n}${hot ? ' <span class="ws-chip ws-chip-blue" style="margin-left:6px">this dataset</span>' : ''}</h3><div class="who">${w}</div><div class="big">${rs(b * per)}<small> hardware, ${b} buildings</small></div><p class="fine">= ${b} × ${rs(per)} planning assumption. Subscription pricing: not set.</p><ul>${li.map((x) => `<li>${x}</li>`).join('')}</ul><a class="lp-btn ${hot ? 'lp-btn-light' : 'lp-btn-outline'}" href="${hot ? '/app' : '#scale'}">${cta} <span class="lp-arrow">→</span></a></div>`).join('');
/* ---- faq ---- */
function renderFaq() {
  const cl = D.classifier, fc = D.forecast, n = fc && fc.best_model_6h_all_test ? Object.values(fc.best_model_6h_all_test).filter((m) => m === 'ridge').length : null, acc = cl && cl.accuracy ? (cl.accuracy * 100).toFixed(2) + '%' : 'its measured value', al = fc && fc.metrics ? fc.metrics.filter((x) => x.building_id === 'B07' && x.window === 'alumni_19sep' && x.horizon_h === 6) : [], rg = al.find((x) => x.model === 'ridge'), yd = al.find((x) => x.model === 'naive_same_hour_yesterday');
  const q = [
  ['Is this real campus data?', 'No. The dataset is a synthetic benchmark supplied for the hackathon: 8 buildings, 120 days, with deliberately injected faults. Everything shown is computed from it, and results show the method works, not how it will perform in the field.'],
  ['How accurate is the waste classifier?', `On a stratified hold-out of the labelled file it reaches ${acc}${cl && cl.accuracy < 0.85 ? ', just under' : ', against'} the 85% target in the problem statement. Several model types land at about the same figure, so we report it as it is. The unlabelled test file has no ground truth, so no accuracy is claimed on it.`],
  ['Does the forecast beat a simple baseline?', `At 6 hours it is the best of the three methods in ${n == null ? '…' : n} of 8 buildings, and not in the other ${n == null ? '…' : 8 - n}. On the alumni-meet day ${rg && yd ? (yd.wape < rg.wape ? 'the “same hour yesterday” baseline won (WAPE ' + yd.wape + ' vs ' + rg.wape + ')' : 'ridge won (WAPE ' + rg.wape + ' vs ' + yd.wape + ')') : 'the result is shown in the Forecast tab'}. The value is a calibrated baseline that makes surges and faults visible and nameable, not a crystal ball.`],
  ['What if a building goes offline?', 'The Outage Drill rehearses it: hide a window of real hours, estimate them from the visible hours and a profile learned on earlier days, then reconnect and measure the error against naive methods. It runs on recorded data; we have no live buffering hardware.'],
  ['Does it need an AI API key?', 'No. Forecasting, attribution, the drill and the classifier run locally with scikit-learn. Any language-model text is optional and has a template fallback.'],
  ['What about privacy?', 'Only aggregates are used: footfall and occupancy counts per building, never individuals. Incentives compare a building with its own baseline so large buildings are not penalised.'],
];
  $('faqList').innerHTML = q.map(([q, a]) => `<details><summary>${q}</summary><p>${a}</p></details>`).join('');
}
renderFaq();
