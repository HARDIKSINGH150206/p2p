/* Overview dashboard: live KPIs, stacked series with real event pins, anomaly heatmap, building cards, waste flow. */
(function () {
  const COL = ['#0099ff', '#34d399', '#f0b24a', '#ef7a45', '#e8578f', '#9b87f5', '#22d3ee', '#a3e635'];
  const METRICS = [['electricity_kwh', 'Electricity', 'kWh', 1], ['water_litres', 'Water', 'kL', 1000], ['solar_generation_kwh', 'Solar', 'kWh', 1], ['landfill_kg', 'Landfill', 'kg', 1], ['composted_kg', 'Composted', 'kg', 1]];
  const CAUSE_COL = { sensor_calibration: '#a78bfa', composter_down: '#f87171', composter_fixed: '#34d399', water_leak: '#f87171', solar_inverter_fault: '#f87171', solar_inverter_fixed: '#34d399', event_surge: '#fbbf24', energy_left_on: '#fbbf24', meter_issue: '#fbbf24' };
  const S = { ts: null, bl: null, metric: 'electricity_kwh', off: new Set(), mounted: false };
  const el = $('v-overview');
  el.innerHTML = `
  <div class="ov-head reveal"><div><h1 class="ov-title">Campus overview</h1><p class="ov-sub"><span class="live-dot"></span><span id="ovWin">Loading the grid…</span></p></div>
    <div class="row" style="margin:0"><button class="lp-btn lp-btn-outline lp-btn-sm" onclick="navTo('grid')">Wire the grid</button><button class="lp-btn lp-btn-light lp-btn-sm" onclick="navTo('brief')">Open the Brief <span class="lp-arrow">→</span></button></div></div>
  <div class="ov-kpis" id="ovK">${'<div class="okpi"><div class="sk" style="height:84px"></div></div>'.repeat(6)}</div>
  <div class="ov-grid">
    <div class="panel2 reveal" style="animation-delay:.1s"><div class="p-head"><div><h3 id="chT">Daily electricity, stacked by building</h3><p class="hint" id="chH"></p></div><div class="seg" id="chM"></div></div>
      <div class="chips" id="chC"></div><div class="chart-box" id="chBox"><div class="sk" style="height:340px"></div><div class="tip" id="chTip"></div></div></div>
    <div class="panel2 reveal" style="animation-delay:.18s"><div class="p-head"><div><h3>Needs attention</h3><p class="hint">Ranked by confidence, each with its evidence</p></div></div><div class="attn" id="ovAtt"><div class="sk" style="height:300px"></div></div></div>
  </div>
  <div class="panel2 reveal" style="margin-top:14px;animation-delay:.24s"><div class="p-head"><div><h3>Anomaly heatmap</h3><p class="hint" id="hmH">Each cell is a building-day against that building’s median for the same kind of day (term, exam, weekend, break). Hover for the date and any logged event.</p></div></div>
    <div class="hm-wrap" id="hmBox"><canvas id="hmC"></canvas><div class="tip" id="hmTip"></div></div><div class="hm-leg">below median<i></i>above median</div></div>
  <div class="bgrid" id="ovB">${'<div class="bcard"><div class="sk" style="height:150px"></div></div>'.repeat(8)}</div>
  <div class="ov3">
    <div class="panel2 reveal"><div class="p-head"><div><h3>Where the waste goes</h3><p class="hint">Composted, recycled and landfill per building, 120 days</p></div><div class="legend" style="margin:0">${legend([['#34d399', 'composted'], ['#0099ff', 'recycled'], ['#f0b24a', 'landfill']])}</div></div><div class="wf" id="ovW"><div class="sk" style="height:220px"></div></div></div>
    <div class="panel2 reveal"><h3>Edge bin classifier</h3><p class="hint">Hold-out accuracy, 6 classes</p><div class="ring" id="ovR"><div class="sk" style="height:150px;width:150px;border-radius:50%"></div></div><p class="hint" id="ovRt" style="text-align:center"></p></div>
    <div class="panel2 reveal"><h3>B07 alumni meet, 6 h ahead</h3><p class="hint">Actual vs ridge and naive baselines</p><canvas id="ovF" class="chart" width="480" height="250" style="height:210px;margin-top:8px;box-shadow:none;background:transparent"></canvas></div>
  </div>`;

  const sum = (a) => a.reduce((x, y) => x + (y || 0), 0);
  const med = (a) => { const b = a.filter((v) => v != null).sort((x, y) => x - y); return b.length ? b[Math.floor(b.length / 2)] : 0; };
  const nice = (v) => (v >= 1e6 ? (v / 1e6).toFixed(2) + 'M' : v >= 1e4 ? (v / 1e3).toFixed(1) + 'k' : f(v));
  const val = (b, m, i) => { const s = S.ts.buildings[b]; let v = s[m][i]; if (m === 'electricity_kwh' && s.outlier[i]) v = med(s[m]); return v == null ? 0 : v; };
  const mInfo = () => METRICS.find((m) => m[0] === S.metric);

  function countUp(node, to, dec, pre = '', suf = '') { const t0 = performance.now(), d = 900; const step = (t) => { const p = Math.min(1, (t - t0) / d), e = 1 - Math.pow(1 - p, 3); node.innerHTML = pre + f(to * e, dec) + '<span class="u">' + suf + '</span>'; if (p < 1) requestAnimationFrame(step); }; matchMedia('(prefers-reduced-motion: reduce)').matches ? (node.innerHTML = pre + f(to, dec) + '<span class="u">' + suf + '</span>') : requestAnimationFrame(step); }
  function spark(vals, color) { const w = 120, h = 30, mx = Math.max(...vals, 1), mn = Math.min(...vals), pts = vals.map((v, i) => `${(i / (vals.length - 1)) * w},${h - 3 - ((v - mn) / (mx - mn || 1)) * (h - 6)}`).join(' '); const id = 'g' + Math.random().toString(36).slice(2, 7); return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".35"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs><polygon points="0,${h} ${pts} ${w},${h}" fill="url(#${id})"/><polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.6" stroke-linejoin="round"/></svg>`; }
  const daily = (m) => S.ts.dates.map((_, i) => sum(Object.keys(S.ts.buildings).map((b) => val(b, m, i))));

  function kpis() {
    const im = D.impact && D.impact.baseline, br = D.brief; if (!im) return;
    const k = [
      ['Grid electricity', im.electricity_kwh, 0, '', ' kWh', 'over 120 days', '#0099ff', daily('electricity_kwh')],
      ['Carbon', im.co2_t, 1, '', ' t', 'CO2 at 0.70 kg per kWh', '#a78bfa', daily('electricity_kwh')],
      ['Solar share', im.solar_share_pct, 1, '', '%', f(im.solar_kwh) + ' kWh generated', '#fbbf24', daily('solar_generation_kwh')],
      ['Composted', im.composted_kg / 1000, 1, '', ' t', '≈ ' + f(im.compost_produced_kg / 1000, 1) + ' t compost at 4:1', '#34d399', daily('composted_kg')],
      ['Landfill', im.landfill_kg / 1000, 1, '', ' t', 'residual, 120 days', '#f0b24a', daily('landfill_kg')],
      ['Anomalies explained', br ? br.attribution_counts.attributed : 0, 0, '', br ? ' of ' + br.n_episodes : '', 'each with an evidence line', '#34d399', null],
    ];
    $('ovK').innerHTML = k.map((x, i) => `<div class="okpi reveal" style="--glow:${x[6]}29;animation-delay:${i * 60}ms"><span class="l">${x[0]}</span><b data-i="${i}">0</b><small>${x[5]}</small>${x[7] ? spark(x[7], x[6]) : '<div style="height:36px"></div>'}</div>`).join('');
    k.forEach((x, i) => { const n = $('ovK').querySelector(`b[data-i="${i}"]`); countUp(n, x[1], x[2], x[3], x[4]); });
  }

  function stack() {
    const T = S.ts, ids = Object.keys(T.buildings), live = ids.filter((b) => !S.off.has(b)), [m, label, unit, div] = mInfo(), n = T.dates.length;
    const box = $('chBox'), W = Math.max(320, box.clientWidth || 700), H = 340, L = 46, R = 10, Tp = 12, B = 34, pw = W - L - R, ph = H - Tp - B;
    const tot = T.dates.map((_, i) => sum(live.map((b) => val(b, m, i)))), mx = Math.max(...tot, 1) * 1.08, X = (i) => L + (i / (n - 1)) * pw, Y = (v) => Tp + ph * (1 - v / mx);
    let paths = '', base = new Array(n).fill(0);
    live.forEach((b) => { const top = base.map((c, i) => c + val(b, m, i)); const up = top.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`), dn = base.map((v, i) => `${X(i).toFixed(1)},${Y(v).toFixed(1)}`).reverse(); const col = COL[ids.indexOf(b)]; paths += `<path d="M${up.join('L')}L${dn.join('L')}Z" fill="${col}" fill-opacity=".55" stroke="${col}" stroke-width="1"/>`; base = top; });
    let grid = ''; for (let i = 0; i <= 4; i++) { const v = (mx / 4) * i, y = Y(v); grid += `<line x1="${L}" x2="${W - R}" y1="${y}" y2="${y}" stroke="rgba(255,255,255,.07)"/><text x="${L - 8}" y="${y + 4}" text-anchor="end" fill="rgba(242,239,233,.45)" font-size="10.5" font-family="ui-monospace,monospace">${nice(v / div)}</text>`; }
    let xt = ''; T.dates.forEach((d, i) => { if (d.slice(8) === '01' || i === 0) xt += `<text x="${X(i)}" y="${H - 14}" fill="rgba(242,239,233,.45)" font-size="10.5" font-family="ui-monospace,monospace">${new Date(d).toLocaleString('en', { month: 'short', day: 'numeric' })}</text>`; });
    // event pins
    let pins = '', di = Object.fromEntries(T.dates.map((d, i) => [d, i]));
    T.events.forEach((e) => { if (e.kind === 'note' && !live.includes(e.building_id)) return; const i = di[e.date]; if (i == null) return; const c = e.kind === 'calendar' ? 'rgba(242,239,233,.28)' : CAUSE_COL[e.cause] || '#fbbf24'; pins += e.kind === 'calendar' ? `<rect x="${X(i) - 2}" y="${H - B + 2}" width="4" height="4" fill="${c}" transform="rotate(45 ${X(i)} ${H - B + 4})"/>` : `<line x1="${X(i)}" x2="${X(i)}" y1="${Tp}" y2="${H - B}" stroke="${c}" stroke-dasharray="2 4" stroke-opacity=".7"/><circle cx="${X(i)}" cy="${H - B + 4}" r="4.5" fill="${c}" stroke="#131313" stroke-width="2"/>`; });
    box.querySelector('.sk') && box.querySelector('.sk').remove();
    let svg = box.querySelector('svg'); if (!svg) { svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); box.prepend(svg); }
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('height', H);
    svg.innerHTML = `${grid}${xt}${paths}${pins}<line id="chX" y1="${Tp}" y2="${H - B}" stroke="rgba(255,255,255,.4)" opacity="0"/>`;
    $('chT').textContent = `Daily ${label.toLowerCase()}, stacked by building`; $('chH').textContent = `${unit} per day · dots mark staff notes and logged events (diamonds are calendar events)` + (m === 'electricity_kwh' ? ' · B04’s 6,234 kWh reading on 27 Aug is a sensor fault and is shown at its median' : '');
    const tip = $('chTip');
    svg.onpointermove = (ev) => { const r = svg.getBoundingClientRect(), px = ((ev.clientX - r.left) / r.width) * W, i = Math.max(0, Math.min(n - 1, Math.round(((px - L) / pw) * (n - 1)))), d = T.dates[i], dt = T.days[i] || {};
      const rows = live.map((b) => [b, val(b, m, i)]).sort((a, b) => b[1] - a[1]), evs = T.events.filter((e) => e.date === d && (e.kind === 'calendar' || live.includes(e.building_id)));
      tip.innerHTML = `<b>${new Date(d).toLocaleDateString('en', { weekday: 'short', day: 'numeric', month: 'short' })}</b> <span style="color:var(--paper-4)">· ${esc((dt.day_type || '').replace('_', ' '))}${dt.rain > 5 ? ' · rain ' + dt.rain + ' mm' : ''}</span>` + rows.map(([b, v]) => `<div class="r"><span><i style="background:${COL[ids.indexOf(b)]}"></i>${b}</span><span>${f(v / div, div > 1 ? 1 : 0)} ${unit}</span></div>`).join('') + `<div class="r" style="border-top:1px solid var(--line-2);margin-top:4px;padding-top:4px"><span>Total</span><b>${f(sum(rows.map((x) => x[1])) / div, div > 1 ? 1 : 0)} ${unit}</b></div>` + evs.map((e) => `<div class="evl">${e.kind === 'note' ? '<b>' + e.building_id + '</b> · ' : ''}${esc(e.label)}</div>`).join('');
      const bx = box.getBoundingClientRect(); tip.style.left = Math.min(bx.width - 230, Math.max(0, ev.clientX - bx.left + 14)) + 'px'; tip.style.top = '10px'; tip.classList.add('on'); const x = $('chX'); x.setAttribute('x1', X(i)); x.setAttribute('x2', X(i)); x.setAttribute('opacity', 1); };
    svg.onpointerleave = () => { tip.classList.remove('on'); $('chX').setAttribute('opacity', 0); };
  }
  function chartControls() {
    $('chM').innerHTML = METRICS.map(([k, l]) => `<button data-m="${k}" class="${k === S.metric ? 'on' : ''}">${l}</button>`).join('');
    $('chM').onclick = (e) => { const b = e.target.closest('button'); if (!b) return; S.metric = b.dataset.m; chartControls(); stack(); heat(); };
    const ids = Object.keys(S.ts.buildings);
    $('chC').innerHTML = ids.map((b, i) => `<button class="bchip ${S.off.has(b) ? 'off' : ''}" data-b="${b}"><i style="background:${COL[i]}"></i>${b}</button>`).join('');
    $('chC').onclick = (e) => { const b = e.target.closest('button'); if (!b) return; const id = b.dataset.b; S.off.has(id) ? S.off.delete(id) : S.off.add(id); if (S.off.size === ids.length) S.off.clear(); chartControls(); stack(); };
  }

  const RG = { working: 'w', exam: 'e', weekend: 'k', holiday: 'k', semester_break: 'b' };
  const rcache = {};
  function rmed(b, m, i) { const key = b + m; if (!rcache[key]) { const T = S.ts, g = {}; T.dates.forEach((d, k) => { const r = RG[(T.days[k] || {}).day_type] || 'w', v = T.buildings[b][m][k]; if (v != null && !(m === 'electricity_kwh' && T.buildings[b].outlier[k])) (g[r] = g[r] || []).push(v); }); rcache[key] = Object.fromEntries(Object.entries(g).map(([r, a]) => [r, med(a)])); } return rcache[key][RG[(S.ts.days[i] || {}).day_type] || 'w'] || 0; }
  function heat() {
    const T = S.ts, ids = Object.keys(T.buildings), m = S.metric, c = $('hmC'), box = $('hmBox'), W = Math.max(320, box.clientWidth), rowH = 26, L = 38, Tp = 18, H = Tp + ids.length * rowH + 4, dpr = devicePixelRatio || 1, n = T.dates.length, cw = (W - L) / n;
    c.width = W * dpr; c.height = H * dpr; c.style.height = H + 'px'; const x = c.getContext('2d'); x.scale(dpr, dpr); x.clearRect(0, 0, W, H); x.font = '10.5px ui-monospace,monospace'; x.fillStyle = 'rgba(242,239,233,.55)';
    const ramp = (r) => { if (r == null) return '#141414'; const t = Math.log2(Math.max(0.25, Math.min(4, r))) / 2; if (t < 0) { const a = Math.min(1, -t); return `rgb(${30 - a * 18},${34 + a * 28},${44 + a * 90})`; } if (t < 0.25) { const a = t / 0.25; return `rgb(${30 + a * 40},${34 + a * 14},${44 - a * 22})`; } const a = (t - 0.25) / 0.75; return `rgb(${58 + a * 181},${42 + a * 97 - a * a * 70},${14 + a * 50 - a * 40})`; };
    ids.forEach((b, r) => { x.fillStyle = 'rgba(242,239,233,.6)'; x.fillText(b, 2, Tp + r * rowH + 17); T.dates.forEach((d, i) => { const v = T.buildings[b][m][i], md = rmed(b, m, i), ok = v != null && md > 0; x.fillStyle = ramp(ok ? val(b, m, i) / md : null); x.beginPath(); x.roundRect ? x.roundRect(L + i * cw + 0.5, Tp + r * rowH + 2, Math.max(1, cw - 1.5), rowH - 4, 2) : x.rect(L + i * cw, Tp + r * rowH + 2, cw - 1, rowH - 4); x.fill(); }); });
    x.fillStyle = 'rgba(242,239,233,.45)'; T.dates.forEach((d, i) => { if (d.slice(8) === '01') x.fillText(new Date(d).toLocaleString('en', { month: 'short' }), L + i * cw, 11); });
    const tip = $('hmTip'); c.onpointermove = (ev) => { const r = c.getBoundingClientRect(), px = ev.clientX - r.left, py = ev.clientY - r.top, i = Math.floor((px - L) / cw), row = Math.floor((py - Tp) / rowH); if (i < 0 || i >= n || row < 0 || row >= ids.length) { tip.classList.remove('on'); return; } const b = ids[row], d = T.dates[i], raw = T.buildings[b][m][i], md = rmed(b, m, i), evs = T.events.filter((e) => e.date === d && (e.kind === 'calendar' || e.building_id === b)), [, , unit, div] = mInfo();
      tip.innerHTML = `<b>${b}</b> · ${new Date(d).toLocaleDateString('en', { day: 'numeric', month: 'short' })}<div class="r"><span>${mInfo()[1]}</span><span>${raw == null ? 'missing' : f(raw / div, div > 1 ? 1 : 0) + ' ' + unit}</span></div><div class="r"><span>vs same kind of day</span><span>${md > 0 && raw != null ? (raw / md).toFixed(2) + '×' : '–'}</span></div>${T.buildings[b].outlier[i] && m === 'electricity_kwh' ? '<div class="evl" style="color:#a78bfa">flagged sensor fault</div>' : ''}${evs.map((e) => `<div class="evl">${esc(e.label)}</div>`).join('')}`;
      tip.style.left = Math.min(W - 230, px + 12) + 'px'; tip.style.top = Math.max(0, py - 90) + 'px'; tip.classList.add('on'); }; c.onpointerleave = () => tip.classList.remove('on');
  }

  function attention() {
    const br = D.brief; if (!br || br.error) { if (br && br.error) errBox('ovAtt', br.error); return; }
    const col = { high: '#34d399', medium: '#fbbf24', low: '#f87171', none: '#f87171' };
    $('ovAtt').innerHTML = br.cards.slice(0, 5).map((c) => `<div class="att" tabindex="0" role="button" onclick="navTo('brief')"><span class="bar" style="background:${col[c.confidence]}"></span><div><h4>${esc(c.title)}</h4><p>${esc(c.evidence.length > 96 ? c.evidence.slice(0, 96) + '…' : c.evidence)}</p></div></div>`).join('');
  }

  function cards() {
    const bl = S.bl, T = S.ts, br = D.brief, cnt = {}; if (br && br.cards) br.cards.forEach((c) => (cnt[c.building_id] = (cnt[c.building_id] || 0) + 1));
    $('ovB').innerHTML = bl.map((b, i) => { const series = T.dates.map((_, k) => val(b.building_id, 'electricity_kwh', k)); return `<div class="bcard reveal" style="animation-delay:${i * 50}ms" tabindex="0" role="button" onclick="navTo('forecast')"><div class="top"><span class="id">${b.building_id} · ${esc(b.building_type)}</span><span class="tinyc blue">${b.electricity_share_pct}%</span></div><h4>${esc(b.building_name.replace('Engineering Labs & Innovation Centre', 'Eng. Labs & Innovation'))}</h4><div class="big">${nice(b.electricity_kwh)} <small style="font-size:12px;color:var(--paper-4)">kWh</small></div>${spark(series, COL[i])}<div class="row2">${b.has_solar ? '<span class="tinyc warn">☼ solar ' + nice(b.solar_kwh) + '</span>' : ''}${b.has_composter ? '<span class="tinyc ok">composter</span>' : ''}${cnt[b.building_id] ? `<span class="tinyc warn">${cnt[b.building_id]} flagged</span>` : '<span class="tinyc">no flags</span>'}</div></div>`; }).join('');
  }
  function waste() {
    const bl = S.bl, mx = Math.max(...bl.map((b) => b.composted_kg + b.recycled_kg + b.landfill_kg));
    $('ovW').innerHTML = bl.map((b) => { const t = b.composted_kg + b.recycled_kg + b.landfill_kg, w = (t / mx) * 100; return `<div class="r"><span class="lp-mono">${b.building_id}</span><div class="bar" style="width:${Math.max(4, w)}%" title="${esc(b.building_name)}"><i style="background:#34d399;width:${(b.composted_kg / t) * 100}%"></i><i style="background:#0099ff;width:${(b.recycled_kg / t) * 100}%"></i><i style="background:#f0b24a;width:${(b.landfill_kg / t) * 100}%"></i></div><span style="text-align:right">${nice(t)} kg</span></div>`; }).join('');
  }
  function ring() {
    const c = D.classifier; if (!c || c.error) return; const a = c.accuracy, R = 62, C = 2 * Math.PI * R;
    $('ovR').innerHTML = `<svg width="170" height="170" viewBox="0 0 170 170"><circle cx="85" cy="85" r="${R}" fill="none" stroke="rgba(255,255,255,.07)" stroke-width="12"/><circle cx="85" cy="85" r="${R}" fill="none" stroke="#0099ff" stroke-width="12" stroke-linecap="round" stroke-dasharray="${C * a} ${C}" transform="rotate(-90 85 85)" style="filter:drop-shadow(0 0 8px rgba(0,153,255,.6))"/><circle cx="85" cy="85" r="${R}" fill="none" stroke="rgba(242,239,233,.5)" stroke-width="2" stroke-dasharray="2 ${C - 2}" transform="rotate(${-90 + 0.85 * 360} 85 85)"/><text x="85" y="88" text-anchor="middle" fill="#f2efe9" font-size="25" font-weight="500" font-family="Inter,system-ui">${(a * 100).toFixed(2)}%</text><text x="85" y="108" text-anchor="middle" fill="rgba(242,239,233,.45)" font-size="11">hold-out accuracy</text></svg>`;
    $('ovRt').textContent = `${c.latency_ms.p50} ms per event · target 85% marked on the ring`;
  }
  function fcast() { const r = D.forecast; if (!r || r.error) return; const s = r.b07_19sep; line($('ovF'), [s.actual, s.forecast, s.naive_week, s.naive_day], ['#f2efe9', '#34d399', '#f87171', '#0099ff']); }

  window.drawOverview = function () {
    if (!S.ts) return; chartControls(); stack(); heat(); kpis(); attention(); cards(); waste(); ring(); fcast();
    const T = S.ts; $('ovWin').textContent = `${new Date(T.dates[0]).toLocaleDateString('en', { day: 'numeric', month: 'short' })} to ${new Date(T.dates.at(-1)).toLocaleDateString('en', { day: 'numeric', month: 'short', year: 'numeric' })} · 8 buildings · every figure computed from the dataset`;
  };
  let rz; addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(() => el.classList.contains('on') && S.ts && (stack(), heat()), 120); });
  window.ovRefresh = () => el.classList.contains('on') && window.drawOverview();
  Promise.all([J('/api/timeseries'), J('/api/buildings')]).then(([ts, bl]) => { if (ts.error || !Array.isArray(bl)) { ['ovK', 'chBox', 'hmBox', 'ovB', 'ovW'].forEach((id) => errBox(id, ts.error || 'buildings unavailable')); return; } S.ts = ts; S.bl = bl; if (el.classList.contains('on')) window.drawOverview(); });
})();
