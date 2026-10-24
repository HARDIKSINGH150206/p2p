/* Workspace views. Needs common.js */
window.navTo = (k) => show(k);
/* ---------- nav / views ---------- */
const VIEWS = [['grid', 'Grid', 'seal'], ['brief', 'Brief', 'list'], ['forecast', 'Forecast', 'clock'], ['drill', 'Outage Drill', 'bolt'], ['impact', 'Impact', 'layers'], ['bin', 'Bin classifier', 'cpu']];
VIEWS.forEach(([k, t, i]) => { const b = document.createElement('button'); b.id = 'n_' + k; b.innerHTML = icon(i, 18) + t; b.onclick = () => show(k); $('nav').append(b); });
function show(k) { VIEWS.forEach(([x]) => { $('v-' + x).classList.toggle('on', x === k); $('n_' + x).classList.toggle('on', x === k); }); if (k === 'grid') measure(); history.replaceState(null, '', '#' + k); }

/* ---------- views ---------- */
function renderBrief(r) {
  if (r.error) return ($('briefBody').textContent = r.error);
  const conf = { high: 'ws-chip-ok', medium: 'ws-chip-warn', low: 'ws-chip-bad', none: 'ws-chip-bad' };
  $('briefBody').innerHTML = `<div class="row">${chip('ws-chip-ok', r.attribution_counts.attributed + ' attributed')}${chip('', r.attribution_counts.unexplained + ' unexplained')}${chip('', r.n_episodes + ' episodes')}</div>` +
    r.cards.map((c) => `<div class="card"><h3>${c.title}</h3><div class="row" style="margin:6px 0">${chip(conf[c.confidence], c.confidence + ' confidence')}${chip('', c.cause.replace(/_/g, ' '))}<span class="meta">${c.date_range[0]} → ${c.date_range[1]}</span></div>
      <div class="ev">Evidence: ${c.evidence}</div><div class="act"><b>Action:</b> ${c.action}</div>
      <p class="meta">${c.kwh != null ? f(c.kwh) + ' kWh · Rs ' + f(c.rs) + ' · ' + f(c.co2_kg) + ' kg CO2 ' : ''}${c.kg != null ? f(c.kg) + ' kg ' : ''}${c.litres != null ? f(c.litres) + ' L' : ''}</p>
      ${c.forecast_check ? `<p class="meta">forecast check (6 h, that day): ${Object.entries(c.forecast_check).map(([m, v]) => m.replace('naive_same_hour_', 'naive ') + ' WAPE ' + v.wape).join(' · ')}</p>` : ''}</div>`).join('');
}
function renderForecast(r) {
  if (r.error) return ($('fcBody').textContent = r.error);
  const m = r.metrics, s = r.b07_19sep, rows = {};
  m.filter((x) => x.window === 'all_test').forEach((x) => ((rows[x.building_id + '|' + x.horizon_h] ??= {})[x.model] = x.wape));
  const al = m.filter((x) => x.window === 'alumni_19sep' && x.building_id === 'B07' && x.horizon_h === 6);
  $('fcBody').innerHTML = `<div class="note">Honest read: on the B07 alumni-meet day the yesterday baseline beat ridge. The model picks up the ramp, and the residual names the surge; it does not predict a one-off event. Fit time: ridge ${r.fit_time_s.ridge}s vs gradient boosting ${r.fit_time_s.hgb}s.</div>
    <h3 style="font-weight:500">B07 Food Court · Alumni meet, Sat 19 Sep (6 h ahead)</h3><canvas class="chart" id="fcC" width="960" height="280"></canvas>
    <div class="legend">${legend([['#f2efe9', 'actual'], ['#34d399', 'ridge'], ['#f87171', 'naive last week'], ['#0099ff', 'naive yesterday']])}</div>
    <p class="meta">${al.map((x) => x.model.replace('naive_same_hour_', 'naive ') + ' WAPE ' + x.wape).join(' · ')}</p>
    <h3 style="font-weight:500;margin-top:24px">WAPE per building, all test days (lower is better; best in green)</h3>
    <table><tr><th>building · horizon</th><th>ridge</th><th>last week</th><th>yesterday</th></tr>${Object.entries(rows).map(([k, v]) => { const best = Math.min(v.ridge, v.naive_same_hour_last_week, v.naive_same_hour_yesterday); const c = (x) => (x === best ? ' style="color:var(--ok)"' : ''); return `<tr><td>${k.replace('|', ' · ')} h</td><td${c(v.ridge)}>${v.ridge}</td><td${c(v.naive_same_hour_last_week)}>${v.naive_same_hour_last_week}</td><td${c(v.naive_same_hour_yesterday)}>${v.naive_same_hour_yesterday}</td></tr>`; }).join('')}</table>`;
  line($('fcC'), [s.actual, s.forecast, s.naive_week, s.naive_day], ['#f2efe9', '#34d399', '#f87171', '#0099ff']);
}
let lastDrill;
['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08'].forEach((b) => { const o = document.createElement('option'); o.value = o.textContent = b; if (b === 'B04') o.selected = true; $('dB').append(o); });
$('dGo').onclick = async () => {
  $('dBody').textContent = 'Running…'; const r = await J('/api/drill', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ building_id: $('dB').value, start: $('dS').value, hours: +$('dH').value }) });
  if (r.detail) { $('dBody').textContent = r.detail; return; } lastDrill = r;
  line($('dC'), [r.hidden.map((h) => h.estimate)], ['#fbbf24']); $('dLeg').innerHTML = legend([['#fbbf24', 'OFFLINE: estimated']]); $('dBody').innerHTML = `<div class="note">${chip('ws-chip-warn', 'offline')} ${r.building_id} stays on the grid with estimates for ${r.hidden.length} hidden hours.</div>`; $('dRe').disabled = false;
};
$('dRe').onclick = () => {
  const r = lastDrill, e = r.errors, b = r.benchmark.mean_errors;
  line($('dC'), [r.hidden.map((h) => h.actual), r.hidden.map((h) => h.estimate)], ['#f2efe9', '#fbbf24']); $('dLeg').innerHTML = legend([['#f2efe9', 'actual (replayed)'], ['#fbbf24', 'estimate']]);
  const nm = { profile_scaled_visible: 'Headline: profile scaled to visible hours', flat_visible_mean: 'Flat visible-hours mean', same_hours_last_week: 'Same hours last week', unscaled_profile: 'Unscaled day-type profile', best_case_daily_total: 'Best case once daily summary arrives' };
  $('dBody').innerHTML = `<table><tr><th>method</th><th>MAE kWh (this window)</th><th>MAPE</th><th>MAE avg over ${r.benchmark.n_windows} test days</th></tr>${Object.keys(nm).map((k) => `<tr${k === 'profile_scaled_visible' ? ' class="best"' : ''}><td>${nm[k]}</td><td>${e[k].mae}</td><td>${(e[k].mape * 100).toFixed(1)}%</td><td>${b[k].mae}</td></tr>`).join('')}</table>
  <p class="meta" style="margin-top:8px">${r.notes.profile_source}. The last row uses the hidden-hour daily total, so it is labelled best case, not a fair headline.</p>`;
};
function renderImpact(r, inc) {
  if (r.error) return ($('imBody').textContent = r.error); const b = r.baseline;
  $('imBody').innerHTML = `<div class="kpis"><div class="kpi"><b>${f(b.electricity_kwh)}</b><span>kWh in ${b.days} days</span></div><div class="kpi"><b>${f(b.co2_t, 1)} t</b><span>CO2 at 0.70 kg/kWh</span></div><div class="kpi"><b>Rs ${f(b.cost_rs)}</b><span>at Rs 8/kWh</span></div><div class="kpi"><b>${b.solar_share_pct}%</b><span>solar share (${f(b.solar_kwh)} kWh)</span></div><div class="kpi"><b>${f(b.composted_kg)} kg</b><span>composted</span></div><div class="kpi"><b>${f(b.landfill_kg)} kg</b><span>landfill</span></div></div>
  <p class="meta">${b.note}</p><h3 style="font-weight:500;margin-top:20px">Attributed events (avoidable if caught)</h3>` +
    r.events.map((e) => `<div class="card"><h3>${e.title}</h3><div class="ev">${e.evidence}</div><p class="meta">${e.kwh != null ? f(e.kwh) + ' kWh · Rs ' + f(e.rs) + ' · ' + f(e.co2_kg) + ' kg CO2 ' : ''}${e.kg != null ? f(e.kg) + ' kg' : ''}${e.litres != null ? ' · ' + f(e.litres) + ' L' : ''}</p></div>`).join('') +
    `<div class="note">Scenario, not a measured outcome. Constants from the data guide: ${r.assumptions.co2_kg_per_kwh} kg CO2/kWh, Rs ${r.assumptions.rs_per_kwh}/kWh, ${r.assumptions.kwh_per_1000l} kWh per 1000 L. ${r.excluded}</div>
    <h3 style="font-weight:500;margin-top:20px">Incentive baseline</h3><div class="note">No behaviour change measured: saved kWh versus each building's own baseline, per occupant. Negative means above its own baseline.</div>
    <table><tr><th>building</th><th>saved kWh</th><th>avg occupancy</th><th>per occupant</th></tr>${(inc || []).map((x) => `<tr><td>${x.building_id}</td><td>${f(x.saved_kwh_vs_own_baseline, 1)}</td><td>${x.avg_occupancy}</td><td>${x.saved_per_occupant}</td></tr>`).join('')}</table>`;
}
function renderBin(r) {
  if (r.error) return ($('binBody').textContent = r.error);
  const L = r.confusion.labels, mx = Math.max(...r.confusion.matrix.flat());
  $('binBody').innerHTML = `<div class="kpis"><div class="kpi"><b>${(r.accuracy * 100).toFixed(2)}%</b><span>hold-out accuracy (target 85%)</span></div><div class="kpi"><b>${r.latency_ms.p50} ms</b><span>per event, p50</span></div><div class="kpi"><b>${r.latency_ms.p95} ms</b><span>p95</span></div><div class="kpi"><b>${r.fit_time_s}s</b><span>training time</span></div></div>
  <p class="meta">${r.evaluated_on}</p>
  <table style="margin-top:12px"><tr><th>class</th><th>precision</th><th>recall</th><th>n</th></tr>${Object.entries(r.per_class).map(([k, v]) => `<tr><td>${k}</td><td>${v.precision}</td><td>${v.recall}</td><td>${v.support}</td></tr>`).join('')}</table>
  <h3 style="font-weight:500;margin-top:24px">Confusion matrix (rows actual, columns predicted)</h3>
  <table><tr><th></th>${L.map((l) => `<th>${l.replace('_', ' ')}</th>`).join('')}</tr>${r.confusion.matrix.map((row, i) => `<tr><td>${L[i]}</td>${row.map((v) => `<td style="background:rgba(0,153,255,${(v / mx) * 0.55})">${v}</td>`).join('')}</tr>`).join('')}</table>
  <h3 style="font-weight:500;margin-top:24px">Routing of ${f(r.n_test_predicted)} unlabelled test events</h3>
  <p>${Object.entries(r.routing.test_counts).map(([k, v]) => `${k.replace('_', ' ')}: <b>${v}</b>`).join(' · ')}</p>
  <p>Food-organic in composter buildings (${r.routing.compost_eligible_buildings.join(', ')}): <b>${r.routing.food_organic_events_in_composter_buildings}</b> → compost. Without a composter: <b>${r.routing.food_organic_events_without_composter}</b> → flag for diversion. No accuracy is claimed on the unlabelled file.</p>`;
}

/* ---------- boot ---------- */
buildGraph(); measure();
show((location.hash || '#grid').slice(1).replace(/^$/, 'grid') in Object.fromEntries(VIEWS.map((v) => [v[0], 1])) ? location.hash.slice(1) : 'grid');
const touch = () => { update(); };
J('/api/stats').then((s) => { D.stats = s; $('statChip').textContent = `${f(s.hourly_duplicates_removed)} duplicates removed · ${f(s.hourly_gap_rows)} gaps filled`; $('statChip').classList.add('ws-chip-ok'); touch(); });
J('/api/brief').then((r) => { D.brief = r; renderBrief(r); touch(); });
J('/api/forecast').then((r) => { D.forecast = r; renderForecast(r); touch(); });
J('/api/impact').then(async (r) => { D.impact = r; renderImpact(r, await J('/api/incentive')); touch(); });
J('/api/classifier').then((r) => { D.classifier = r; renderBin(r); touch(); });
J('/api/drill', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' }).then((r) => { D.drillB = r; touch(); });
if (location.search.includes('demo')) setTimeout(() => $('gAll').click(), 400);

