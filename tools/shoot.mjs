// Element screenshots through the Chrome DevTools protocol (no Playwright needed).
// usage: node tools/shoot.mjs <base-url> <out-dir> <width> <height>
import { spawn } from 'node:child_process';
import fs from 'node:fs';
const [base, out, W = '1500', H = '1000'] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const port = 9800 + Math.floor(Math.random() * 300);
const ch = spawn('google-chrome', ['--headless=new', '--no-sandbox', '--disable-gpu', `--remote-debugging-port=${port}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let t; for (let i = 0; i < 40; i++) { try { t = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (t.length) break; } catch {} await sleep(250); }
const ws = new WebSocket(t.find((x) => x.type === 'page').webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
let id = 0; const pend = {}; ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) { pend[d.id](d.result || d.error); delete pend[d.id]; } };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expr) => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.value;
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: +W, height: +H, deviceScaleFactor: 1.5, mobile: false });
async function go(url, wait = 5000) { await send('Page.navigate', { url }); await sleep(wait); }
async function shot(name, selJs, pre) {
  if (pre) await ev(`(async()=>{${pre}})()`);
  const r = await ev(`(()=>{const e=(${selJs});e.scrollIntoView({block:'start'});const b=e.getBoundingClientRect();return {x:b.left+scrollX,y:b.top+scrollY,w:b.width,h:b.height}})()`);
  const s = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: r.x, y: r.y, width: r.w, height: r.h, scale: 1 } });
  fs.writeFileSync(`${out}/${name}.png`, Buffer.from(s.data, 'base64')); console.log('shot', name, Math.round(r.w), Math.round(r.h));
}
const nav = (v) => `document.getElementById('n_${v}').click(); await new Promise(r=>setTimeout(r,1400));`;
// landing
await go(base + '/?flat', 6500);
await shot('01_landing_hero', `document.querySelector('header.hero')`);
await shot('02_landing_stats_and_steps', `document.getElementById('how')`);
await shot('03_landing_wired_grid', `document.getElementById('workflow')`, `document.getElementById('gAll').click(); await new Promise(r=>setTimeout(r,2600));`);
await shot('04_landing_campus_map', `document.getElementById('scale')`);
await shot('05_landing_constraints', `document.getElementById('constraints')`);
// workspace
await go(base + '/app#overview', 7000);
await ev(`document.querySelector('.ws-header').style.position='static'`); // sticky header would overlap element captures
await shot('10_overview_kpis', `document.getElementById('ovK')`);
await shot('11_overview_series_and_alerts', `document.querySelector('.ov-grid')`);
await shot('12_overview_heatmap', `document.getElementById('hmBox').closest('.panel2')`);
await shot('13_overview_building_cards', `document.getElementById('ovB')`);
await shot('14_overview_waste_classifier_forecast', `document.querySelector('.ov3')`);
await shot('15_building_drawer', `document.querySelector('.drw-p')`, `openBuilding('B05'); await new Promise(r=>setTimeout(r,2200));`);
await ev(`document.querySelector('.drw .x').click()`);
await shot('20_grid_wired', `document.getElementById('v-grid')`, nav('grid') + `document.getElementById('gAll').click(); await new Promise(r=>setTimeout(r,2600));`);
await shot('21_brief_facility_alerts', `document.getElementById('v-brief')`, nav('brief'));
await shot('22_forecast_explorer', `document.getElementById('v-forecast')`, nav('forecast') + `const s=document.getElementById('fxB'); s.value='B03'; s.dispatchEvent(new Event('change')); await new Promise(r=>setTimeout(r,1800));`);
await shot('23_outage_drill', `document.getElementById('v-drill')`, nav('drill') + `document.getElementById('dGo').click(); await new Promise(r=>setTimeout(r,3800)); document.getElementById('dRe').click(); await new Promise(r=>setTimeout(r,600));`);
await shot('24_impact', `document.getElementById('v-impact')`, nav('impact'));
await shot('25_bin_classifier_waste_routing', `document.getElementById('v-bin')`, nav('bin'));
ch.kill(); process.exit(0);
