/* CircuGrid Brief frontend. Wired-card graph ported from DigiVault-BFB custody-graph.tsx (vanilla JS). */
const $ = (id) => document.getElementById(id);
const f = (n, d = 0) => (n == null || isNaN(n) ? '–' : Number(n).toLocaleString(undefined, { maximumFractionDigits: d }));
const J = (u, o) => fetch(u, o).then((r) => r.json());
const D = {}; // api data
const BRAND = '#0099ff';

/* ---------- icons ---------- */
const P = {
  bolt: ['M13 3l0 7l6 0l-8 11l0 -7l-6 0l8 -11'], file: ['M14 3v4a1 1 0 0 0 1 1h4', 'M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z', 'M9 13h6', 'M9 17h4'],
  list: ['M3.5 5.5l1.5 1.5l2.5 -2.5', 'M3.5 11.5l1.5 1.5l2.5 -2.5', 'M3.5 17.5l1.5 1.5l2.5 -2.5', 'M11 6l9 0', 'M11 12l9 0', 'M11 18l9 0'],
  calendar: ['M4 7a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12z', 'M16 3v4', 'M8 3v4', 'M4 11h16'],
  cpu: ['M5 5m0 1a1 1 0 0 1 1 -1h12a1 1 0 0 1 1 1v12a1 1 0 0 1 -1 1h-12a1 1 0 0 1 -1 -1z', 'M9 9h6v6h-6z', 'M3 10h2', 'M3 14h2', 'M10 3v2', 'M14 3v2', 'M21 10h-2', 'M21 14h-2', 'M14 21v-2', 'M10 21v-2'],
  seal: ['M12 3l8 4.5l0 9l-8 4.5l-8 -4.5l0 -9l8 -4.5', 'M12 12l8 -4.5', 'M12 12l0 9', 'M12 12l-8 -4.5'],
  grip: ['M9 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0', 'M9 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0', 'M9 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0', 'M15 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0', 'M15 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0', 'M15 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0'],
  check: ['M5 12l5 5l10 -10'], target: ['M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0', 'M12 12m-5 0a5 5 0 1 0 10 0a5 5 0 1 0 -10 0', 'M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0'],
  layers: ['M12 4l-8 4l8 4l8 -4l-8 -4', 'M4 12l8 4l8 -4', 'M4 16l8 4l8 -4'], eye: ['M10 12a2 2 0 1 0 4 0a2 2 0 0 0 -4 0', 'M21 12c-2.4 4 -5.4 6 -9 6c-3.6 0 -6.6 -2 -9 -6c2.4 -4 5.4 -6 9 -6c3.6 0 6.6 2 9 6'],
  database: ['M12 6m-8 0a8 3 0 1 0 16 0a8 3 0 1 0 -16 0', 'M4 6v6a8 3 0 0 0 16 0v-6', 'M4 12v6a8 3 0 0 0 16 0v-6'], scale: ['M7 20l10 0', 'M6 6l6 -1l6 1', 'M12 3l0 17', 'M9 12l-3 -6l-3 6a3 3 0 0 0 6 0', 'M21 12l-3 -6l-3 6a3 3 0 0 0 6 0'],
  shield: ['M12 3a12 12 0 0 0 8.5 3a12 12 0 0 1 -8.5 15a12 12 0 0 1 -8.5 -15a12 12 0 0 0 8.5 -3', 'M9 12l2 2l4 -4'], chain: ['M9 15l6 -6', 'M11 6l.463 -.536a5 5 0 0 1 7.071 7.072l-.534 .464', 'M13 18l-.397 .534a5.068 5.068 0 0 1 -7.127 0a4.972 4.972 0 0 1 0 -7.071l.524 -.463'],
  clock: ['M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0', 'M12 7v5l3 3'], home: ['M5 12l-2 0l9 -9l9 9l-2 0', 'M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-7', 'M9 21v-6a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v6'],
};
const icon = (n, s = 16, w = 1.75, c = '') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" class="${c}" aria-hidden="true">${P[n].map((d) => `<path d="${d}"/>`).join('')}</svg>`;

/* ---------- nav / views ---------- */
const VIEWS = [['grid', 'Grid', 'seal'], ['brief', 'Brief', 'list'], ['forecast', 'Forecast', 'clock'], ['drill', 'Outage Drill', 'bolt'], ['impact', 'Impact', 'layers'], ['bin', 'Bin classifier', 'cpu']];
VIEWS.forEach(([k, t, i]) => { const b = document.createElement('button'); b.id = 'n_' + k; b.innerHTML = icon(i, 18) + t; b.onclick = () => show(k); $('nav').append(b); });
function show(k) { VIEWS.forEach(([x]) => { $('v-' + x).classList.toggle('on', x === k); $('n_' + x).classList.toggle('on', x === k); }); if (k === 'grid') measure(); history.replaceState(null, '', '#' + k); }

/* ---------- graph ---------- */
const CW = 1520, CH = 560, CARD_W = 232, CARD_H = 144, HUB_W = 256, ROW_Y0 = 84, ROW_H = 56, PORT_Y = 114, HUB_H = 402;
const g = (id) => ({ stats: D.stats || {}, fc: D.forecast, brief: D.brief, imp: D.impact, bin: D.classifier, drill: D.drillB }[id]);
const INPUTS = [
  { id: 'hourly', row: 0, title: 'Hourly meters', icon: 'bolt', port: 'stream', color: '#f0b24a', hubLabel: 'Dedupe + gap grid',
    lines: () => { const s = D.stats || {}; return [`${f(s.hourly_rows_raw)} rows → ${f(s.hourly_grid_rows)} grid`, `${f(s.hourly_duplicates_removed)} duplicates removed`]; } },
  { id: 'daily', row: 1, title: 'Daily summary', icon: 'file', port: 'daily', color: '#ef7a45', hubLabel: 'Daily fusion', lines: () => ['960 building-days', 'waste · water · solar · electricity'] },
  { id: 'manual', row: 2, title: 'Manual logs', icon: 'list', port: 'notes', color: '#e8578f', hubLabel: 'Alias + note causes',
    chips: () => { const s = D.stats || {}; return [`${f(s.manual_distinct_spellings)} spellings → 8`, `${f(s.manual_notes_parsed)} notes parsed`, 'units fixed']; } },
  { id: 'calendar', row: 3, title: 'Calendar', icon: 'calendar', port: 'context', color: '#9b87f5', hubLabel: 'Events + weather', note: () => '47 events, 5 day types, temperature and rain per day.' },
  { id: 'bins', row: 4, title: 'Bin sensors', icon: 'cpu', port: 'events', color: '#34d399', hubLabel: 'Edge classifier input', lines: () => ['6,314 labelled · 1,601 live', 'weight · moisture · metal · optics · sound'] },
];
const OUTPUTS = [
  { id: 'forecast', hubRow: 0, title: 'Forecast', icon: 'clock', view: 'forecast', wait: 'Waiting for fusion', live: () => 'Ridge vs naive, per building',
    lines: () => { const b = D.forecast && D.forecast.best_model_6h_all_test; if (!b) return ['6 h and 12 h ahead', 'time-ordered split']; const n = Object.values(b).filter((m) => m === 'ridge').length; return ['6 h and 12 h ahead', `Ridge best in ${n}/8 buildings (6 h)`]; } },
  { id: 'brief', hubRow: 1, title: 'Root-cause Brief', icon: 'list', view: 'brief', wait: 'Waiting for fusion', live: () => 'Evidence on every card',
    lines: () => { const c = D.brief && D.brief.attribution_counts; return c ? [`${c.attributed} episodes attributed`, `${c.unexplained} unexplained`] : ['Anomaly → probable cause', 'note · event · weather']; } },
  { id: 'drill', hubRow: 2, title: 'Outage Drill', icon: 'bolt', view: 'drill', wait: 'Waiting for fusion', live: () => 'Offline stays on the grid',
    lines: () => { const b = D.drillB && D.drillB.benchmark && D.drillB.benchmark.mean_errors; return b ? [`B04 6 h hidden: MAE ${b.profile_scaled_visible.mae} kWh`, `vs ${b.same_hours_last_week.mae} last-week naive`] : ['Hide hours, estimate, replay', 'error vs naive baselines']; } },
  { id: 'impact', hubRow: 3, title: 'Impact', icon: 'layers', view: 'impact', wait: 'Waiting for fusion', live: () => 'Computed from the data',
    lines: () => { const b = D.impact && D.impact.baseline; return b ? [`${f(b.co2_t, 1)} t CO2 · Rs ${f(b.cost_rs / 1e6, 1)}M baseline`, `solar share ${b.solar_share_pct}%`] : ['kWh · Rs · CO2 · landfill', 'assumptions shown']; } },
  { id: 'bin', hubRow: 4, title: 'Bin classifier', icon: 'cpu', view: 'bin', wait: 'Waiting for fusion', live: () => 'Edge inference',
    lines: () => { const b = D.classifier; return b && b.accuracy ? [`${(b.accuracy * 100).toFixed(2)}% hold-out accuracy`, `${b.latency_ms.p50} ms per event`] : ['6 classes, 5 sensors', 'accuracy on a hold-out']; } },
  { id: 'action', title: 'Action brief', icon: 'scale', view: 'brief', wait: 'Waiting for forecast and brief', live: () => 'Ranked, explainable',
    lines: () => ['Ranked actions + evidence', 'kWh · Rs · kg CO2'] },
];
const START = { hourly: [300, 32], daily: [40, 208], manual: [340, 208], calendar: [340, 384], bins: [40, 384], hub: [632, 110],
  forecast: [988, 32], brief: [948, 208], drill: [968, 384], impact: [1248, 384], bin: [1248, 208], action: [1248, 32] };
const INITIAL = [true, false, false, false, false];
const st = { connected: [...INITIAL], pos: Object.fromEntries(Object.entries(START).map(([k, v]) => [k, { x: v[0], y: v[1] }])), live: 0, drag: null, scale: 1, flash: null };
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const cardEls = {}, portEls = {};
let wires, hubEl, hubList, hubStatus, hubVerify, flashEl;

const outPort = (id) => ({ x: st.pos[id].x + CARD_W, y: st.pos[id].y + PORT_Y });
const inPort = (id) => ({ x: st.pos[id].x, y: st.pos[id].y + PORT_Y });
const hubIn = (r) => ({ x: st.pos.hub.x, y: st.pos.hub.y + ROW_Y0 + ROW_H * r });
const hubOut = (r) => ({ x: st.pos.hub.x + HUB_W, y: st.pos.hub.y + ROW_Y0 + ROW_H * r });
const wirePath = (a, b, sag) => { const k = Math.max(60, (b.x - a.x) / 2), n = (v) => v.toFixed(1); return `M ${n(a.x)} ${n(a.y)} C ${n(a.x + k)} ${n(a.y + sag)}, ${n(b.x - k)} ${n(b.y + sag)}, ${n(b.x)} ${n(b.y)}`; };
const liveWire = (a, b, color) => { const d = wirePath(a, b, 0.12 * Math.hypot(b.x - a.x, b.y - a.y)); return `<g><path d="${d}" stroke="${color}" stroke-width="7" opacity=".45" fill="none" filter="url(#glow)" pathLength="1" class="lp-g-draw"/><path d="${d}" stroke="${color}" stroke-width="2.5" stroke-linecap="round" fill="none" pathLength="1" class="lp-g-draw"/>${reduced ? '' : `<path d="${d}" stroke="white" stroke-opacity=".75" stroke-width="2" stroke-linecap="round" stroke-dasharray="1 14" fill="none" class="lp-g-flow"/>`}</g>`; };
const idleWire = (a, b) => `<path d="${wirePath(a, b, 0)}" stroke="white" stroke-opacity=".12" stroke-width="1.5" stroke-dasharray="3 6" stroke-linecap="round" fill="none"/>`;
const sealed = () => st.connected.every(Boolean);
const count = () => st.connected.filter(Boolean).length;
const outLive = (i) => st.live > i;
const courtLive = () => st.live >= OUTPUTS.length;

function head(id, ic, title, extra = '') { return `<div class="lp-g-head ${id === 'hub' ? 'lp-g-head-hub' : ''}" data-drag="${id}">${icon(ic, 16, 1.75, 'lp-g-head-icon')}<p>${title}</p>${extra}<button type="button" class="lp-g-grip" data-key="${id}" aria-label="Move ${title} with arrow keys">${icon('grip', 14, 2)}</button></div>`; }
function buildGraph() {
  const c = $('gCanvas'); c.style.width = CW + 'px'; c.style.height = CH + 'px';
  let h = `<svg width="${CW}" height="${CH}" class="lp-g-wires" id="gWires" aria-hidden="true"><defs><filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter></defs></svg>`;
  INPUTS.forEach((d) => { h += `<div class="lp-g-card" id="c_${d.id}">${head(d.id, d.icon, d.title)}<div class="lp-g-body" id="b_${d.id}"></div><div class="lp-g-foot lp-g-foot-end">${d.port}</div></div>`; });
  h += `<div class="lp-g-hub" id="hub"><div class="lp-g-hub-glow" id="hubGlow" style="display:none"><span class="lp-g-hub-line"></span><span class="lp-g-hub-blob"></span></div><div class="lp-g-hub-inner">${head('hub', 'seal', 'Fused grid', '<span class="lp-g-hub-sub">8 buildings</span>')}<div class="lp-g-hub-list" id="hubList"><ul>${INPUTS.map((d) => `<li id="hr_${d.id}"><span class="lp-g-row-off">${d.hubLabel}</span></li>`).join('')}</ul></div><div class="lp-g-hub-foot"><span class="lp-g-sdot" id="hubDot"></span><span class="lp-g-status" id="hubStatus"></span><a class="lp-g-verify" id="hubVerify" href="#brief" style="display:none">Open brief</a></div></div></div>`;
  OUTPUTS.forEach((o) => { h += `<div class="lp-g-card lp-g-card-dim" id="c_${o.id}">${head(o.id, o.icon, o.title)}<div class="lp-g-body" id="b_${o.id}"></div><div class="lp-g-foot lp-g-foot-start"><span class="lp-g-sdot"></span><span class="ft"></span></div></div>`; });
  c.innerHTML = h;
  wires = $('gWires'); hubEl = $('hub'); hubList = $('hubList'); hubStatus = $('hubStatus'); hubVerify = $('hubVerify');
  [...INPUTS, ...OUTPUTS].forEach((d) => (cardEls[d.id] = $('c_' + d.id)));
  // ports
  const mk = (key, o) => { const el = document.createElement(o.btn ? 'button' : 'span'); el.className = 'lp-g-port' + (o.btn ? ' lp-g-port-btn' + (o.grab ? ' lp-g-port-grab' : '') : ''); if (o.btn) { el.type = 'button'; el.setAttribute('aria-label', o.label || ''); } el.innerHTML = '<span class="lp-g-dot"></span>'; c.append(el); portEls[key] = { el, pt: o.pt, dot: el.firstChild }; return el; };
  OUTPUTS.forEach((o) => mk('in_' + o.id, { pt: () => inPort(o.id) }));
  mk('out_forecast', { pt: () => outPort('forecast') }); mk('out_brief', { pt: () => outPort('brief') });
  for (let r = 0; r < 5; r++) mk('hout_' + r, { pt: () => hubOut(r) });
  INPUTS.forEach((d) => {
    const o = mk('out_' + d.id, { btn: true, grab: true, label: 'Connect ' + d.hubLabel, pt: () => outPort(d.id) });
    o.addEventListener('pointerdown', (e) => startWire(d.row, e));
    o.addEventListener('click', () => { if (dragged) { dragged = false; return; } setRow(d.row, !st.connected[d.row]); });
    const i = mk('hin_' + d.id, { btn: true, label: d.hubLabel + ' input', pt: () => hubIn(d.row) });
    i.addEventListener('click', () => st.connected[d.row] && setRow(d.row, false));
  });
  // card dragging (header) + keyboard
  c.querySelectorAll('[data-drag]').forEach((hd) => hd.addEventListener('pointerdown', (e) => startCard(hd.dataset.drag, e)));
  c.querySelectorAll('[data-key]').forEach((b) => b.addEventListener('keydown', (e) => keyMove(b.dataset.key, e)));
  OUTPUTS.forEach((o) => $('b_' + o.id).addEventListener('click', () => outLiveById(o.id) && show(o.view)));
  hubVerify.onclick = (e) => { e.preventDefault(); show('brief'); };
  update(true);
}
const outLiveById = (id) => { const i = OUTPUTS.findIndex((o) => o.id === id); return id === 'action' ? courtLive() : outLive(i); };
let dragged = false;
const toCanvas = (e) => { const r = $('gCanvas').getBoundingClientRect(); return { x: (e.clientX - r.left) / st.scale, y: (e.clientY - r.top) / st.scale }; };
function startWire(row, e) {
  if (e.button !== 0) return; e.preventDefault(); const el = e.currentTarget; el.setPointerCapture(e.pointerId); const sx = e.clientX, sy = e.clientY; let moved = false; dragged = false;
  const move = (ev) => { if (!moved && Math.hypot(ev.clientX - sx, ev.clientY - sy) < 4) return; moved = true; st.drag = { row, end: toCanvas(ev) }; update(); };
  const up = (ev) => { el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', up); el.removeEventListener('pointercancel', up); st.drag = null; if (moved) { dragged = true; const end = toCanvas(ev), t = hubIn(row); if (Math.hypot(end.x - t.x, end.y - t.y) < 40) setRow(row, true); } update(); };
  el.addEventListener('pointermove', move); el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
}
function startCard(id, e) {
  if (e.button !== 0 || e.target.closest('button,a')) return; const el = e.currentTarget; el.setPointerCapture(e.pointerId); const sx = e.clientX, sy = e.clientY, s0 = { ...st.pos[id] }, w = id === 'hub' ? HUB_W : CARD_W, h = id === 'hub' ? HUB_H : CARD_H;
  const move = (ev) => { st.pos[id] = { x: Math.min(CW - w, Math.max(0, s0.x + (ev.clientX - sx) / st.scale)), y: Math.min(CH - h, Math.max(0, s0.y + (ev.clientY - sy) / st.scale)) }; update(); };
  const up = () => { el.removeEventListener('pointermove', move); el.removeEventListener('pointerup', up); el.removeEventListener('pointercancel', up); };
  el.addEventListener('pointermove', move); el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
}
function keyMove(id, e) { const step = e.shiftKey ? 32 : 8, d = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[e.key]; if (!d) return; e.preventDefault(); const w = id === 'hub' ? HUB_W : CARD_W, h = id === 'hub' ? HUB_H : CARD_H, p = st.pos[id]; st.pos[id] = { x: Math.min(CW - w, Math.max(0, p.x + d[0])), y: Math.min(CH - h, Math.max(0, p.y + d[1])) }; update(); }
let timers = [], liveTimer;
function setRow(row, on) { st.connected[row] = on; if (on) { st.flash = INPUTS[row].color; flashHub(INPUTS[row].color); } syncLive(); update(); }
function flashHub(color) { if (reduced) return; const el = document.createElement('span'); el.className = 'lp-g-flash'; el.style.setProperty('--c', color); hubList.append(el); setTimeout(() => el.remove(), 950); }
function syncLive() { clearInterval(liveTimer); if (!sealed()) { st.live = 0; return; } if (reduced) { st.live = OUTPUTS.length; return; } let n = 0; liveTimer = setInterval(() => { n++; st.live = n; update(); if (n >= OUTPUTS.length) clearInterval(liveTimer); }, 170); }
$('gAll').onclick = () => { timers.forEach(clearTimeout); timers = []; INPUTS.filter((d) => !st.connected[d.row]).forEach((d, i) => timers.push(setTimeout(() => setRow(d.row, true), reduced ? 0 : i * 220))); };
$('gReset').onclick = () => { timers.forEach(clearTimeout); clearInterval(liveTimer); st.connected = [...INITIAL]; st.live = 0; Object.entries(START).forEach(([k, v]) => (st.pos[k] = { x: v[0], y: v[1] })); update(); };

function update(force) {
  const live = outLive, S = sealed(), n = count();
  // cards
  Object.entries(cardEls).forEach(([id, el]) => { el.style.left = st.pos[id].x + 'px'; el.style.top = st.pos[id].y + 'px'; });
  hubEl.style.left = st.pos.hub.x + 'px'; hubEl.style.top = st.pos.hub.y + 'px'; hubEl.classList.toggle('lp-g-hub-sealed', S); $('hubGlow').style.display = S ? '' : 'none';
  INPUTS.forEach((d) => {
    const b = $('b_' + d.id); if (b.dataset.k !== String(Object.keys(D).length)) { b.dataset.k = String(Object.keys(D).length);
      const ln = d.lines && d.lines(); b.innerHTML = (ln ? `<div class="lp-g-lines"><p class="lp-g-l1">${ln[0]}</p><p class="lp-g-l2">${ln[1]}</p></div>` : '') + (d.chips ? `<div class="lp-g-chips">${d.chips().map((c) => `<span>${c}</span>`).join('')}</div>` : '') + (d.note ? `<p class="lp-g-note">${d.note()}</p>` : ''); }
    const li = $('hr_' + d.id), on = st.connected[d.row]; li.innerHTML = `<span class="${on ? 'lp-g-row-on' : 'lp-g-row-off'}">${d.hubLabel}</span>${on ? `<span class="lp-g-check" style="color:${d.color}">${icon('check', 16, 2.5)}</span>` : ''}`;
  });
  OUTPUTS.forEach((o, i) => {
    const on = o.id === 'action' ? courtLive() : live(i), el = cardEls[o.id]; el.classList.toggle('lp-g-card-dim', !on); el.classList.toggle('clickable', on);
    const b = $('b_' + o.id), ln = o.lines(), key = on + '|' + ln.join('|'); if (b.dataset.k !== key) { b.dataset.k = key; b.innerHTML = `<div class="lp-g-lines"><p class="lp-g-l1">${ln[0]}</p><p class="lp-g-l2">${ln[1]}</p></div>`; }
    const dot = el.querySelector('.lp-g-sdot'); dot.style.backgroundColor = on ? BRAND : ''; dot.style.boxShadow = on ? `0 0 6px ${BRAND}` : ''; el.querySelector('.ft').textContent = on ? o.live() : o.wait;
  });
  hubStatus.textContent = S ? (courtLive() ? 'Fused · models live' : 'Fused · starting models') : `Awaiting inputs · ${n}/5`; $('hubDot').style.backgroundColor = S ? BRAND : 'rgba(242,239,233,.3)'; hubVerify.style.display = S ? '' : 'none';
  $('gLive').textContent = `${n} of 5 sources connected.${S ? ' Grid fused.' : ''}`;
  // wires
  let w = wires.querySelector('defs').outerHTML;
  INPUTS.forEach((d) => { if (st.connected[d.row]) w += liveWire(outPort(d.id), hubIn(d.row), d.color); });
  OUTPUTS.forEach((o, i) => { if (o.hubRow === undefined) return; w += live(i) ? liveWire(hubOut(o.hubRow), inPort(o.id), BRAND) : idleWire(hubOut(o.hubRow), inPort(o.id)); });
  ['forecast', 'brief'].forEach((s) => (w += courtLive() ? liveWire(outPort(s), inPort('action'), BRAND) : idleWire(outPort(s), inPort('action'))));
  if (st.drag) w += `<path d="${wirePath(outPort(INPUTS[st.drag.row].id), st.drag.end, 0)}" stroke="${INPUTS[st.drag.row].color}" stroke-width="2.5" stroke-linecap="round" fill="none"/>`;
  wires.innerHTML = w;
  // ports
  Object.entries(portEls).forEach(([k, p]) => { const pt = p.pt(); p.el.style.left = pt.x - 14 + 'px'; p.el.style.top = pt.y - 14 + 'px'; });
  const col = (k, c) => (portEls[k].dot.style.cssText = c ? `background-color:${c};box-shadow:0 0 0 3px var(--ink-2),0 0 12px 1px ${c}` : '');
  OUTPUTS.forEach((o, i) => col('in_' + o.id, (o.id === 'action' ? courtLive() : live(i)) ? BRAND : null));
  col('out_forecast', courtLive() ? BRAND : null); col('out_brief', courtLive() ? BRAND : null);
  for (let r = 0; r < 5; r++) col('hout_' + r, live(r) ? BRAND : null);
  INPUTS.forEach((d) => { col('out_' + d.id, st.connected[d.row] || (st.drag && st.drag.row === d.row) ? d.color : null); col('hin_' + d.id, st.connected[d.row] ? d.color : null); portEls['hin_' + d.id].dot.classList.toggle('lp-g-dot-target', !!st.drag && st.drag.row === d.row); });
  // mobile list
  $('gMobile').innerHTML = INPUTS.map((d) => `<button class="lp-g-mitem" data-r="${d.row}"><span>${icon(d.icon, 20)}</span><span><b>${d.title}</b><br><small style="color:var(--paper-4)">${d.hubLabel}</small></span><span class="lp-g-mstate ${st.connected[d.row] ? 'on' : ''}">${st.connected[d.row] ? 'Connected' : 'Connect'}</span></button>`).join('') + (S ? OUTPUTS.map((o) => `<button class="lp-g-mitem" data-v="${o.view}"><span>${icon(o.icon, 20)}</span><span><b>${o.title}</b><br><small style="color:var(--paper-4)">${o.lines()[1]}</small></span><span class="lp-g-mstate on">Open</span></button>`).join('') : '');
  $('gMobile').querySelectorAll('button').forEach((b) => (b.onclick = () => (b.dataset.v ? show(b.dataset.v) : setRow(+b.dataset.r, !st.connected[+b.dataset.r]))));
}
function measure() { const s = $('gStage'); if (!s) return; st.scale = s.clientWidth / CW; $('gCanvas').style.transform = `scale(${st.scale})`; s.style.height = CH * st.scale + 'px'; $('gGrid').style.cssText = `top:${16 * st.scale}px;height:${528 * st.scale}px`; }
new ResizeObserver(measure).observe(document.body);

/* ---------- charts ---------- */
function line(c, series, colors) {
  const x = c.getContext('2d'), W0 = c.width, H0 = c.height; x.clearRect(0, 0, W0, H0);
  const all = series.flat().filter((v) => v != null), mx = Math.max(...all), mn = Math.min(...all), n = Math.max(...series.map((s) => s.length)), L = 52, T = 14, W = W0 - L - 16, H = H0 - T - 30;
  x.strokeStyle = 'rgba(255,255,255,.08)'; x.fillStyle = 'rgba(242,239,233,.45)'; x.font = '11px ui-monospace,monospace';
  for (let i = 0; i <= 4; i++) { const y = T + (H * i) / 4; x.beginPath(); x.moveTo(L, y); x.lineTo(L + W, y); x.stroke(); x.fillText(f(mx - ((mx - mn) * i) / 4), 6, y + 4); }
  series.forEach((s, i) => { x.strokeStyle = colors[i]; x.lineWidth = i === 0 ? 2.2 : 1.6; x.beginPath(); s.forEach((v, k) => { if (v == null) return; const px = L + (W * k) / (n - 1 || 1), py = T + H * (1 - (v - mn) / (mx - mn || 1)); k ? x.lineTo(px, py) : x.moveTo(px, py); }); x.stroke(); });
}
const legend = (items) => items.map(([c, t]) => `<span><i style="background:${c}"></i>${t}</span>`).join('');
const chip = (c, t) => `<span class="ws-chip ${c}">${t}</span>`;

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
