// Exercise an unchanged retained report using isolated local Chrome, not a user profile.
import { spawn } from 'node:child_process';
import { mkdtempSync, writeFileSync, existsSync, rmSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [reportArg, outputArg] = process.argv.slice(2);
if (!reportArg || !outputArg) throw new Error('Usage: node script.mjs REPORT WORK_DIRECTORY');
const report = resolve(reportArg), output = resolve(outputArg);
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const reportBefore = digest(readFileSync(report));
for (const name of ['browser.json', 'report-browser.png']) {
  if (existsSync(join(output, name))) throw new Error(`Refusing overwrite: ${name}`);
}
const profile = mkdtempSync(join(output, 'chrome-profile-'));
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
  '--headless=new', '--no-first-run', '--no-default-browser-check',
  '--disable-background-networking', '--disable-component-update',
  '--disable-default-apps', '--disable-extensions', '--metrics-recording-only',
  '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0',
  `--user-data-dir=${profile}`, 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });
let ws, session, nextId = 0;
const pending = new Map(), errors = [], networkFailures = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));
function request(method, params = {}, sessionId = undefined) {
  return new Promise((resolve, reject) => {
    const id = ++nextId;
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`timeout: ${method}`)); }, 15000);
    pending.set(id, { resolve, reject, timer });
    ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
  });
}
async function evaluate(expression) {
  const response = await request('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }, session);
  if (response.exceptionDetails) throw new Error(JSON.stringify(response.exceptionDetails));
  return response.result.value;
}
async function canvasState(cardIndex) {
  return evaluate(`(async () => {
    const card=document.querySelectorAll('.source-sequence')[${cardIndex}];
    const canvas=card.querySelector('canvas'); canvas.scrollIntoView({block:'center',behavior:'instant'});
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    const box=canvas.getBoundingClientRect();
    const data=JSON.parse(card.querySelector('.sequence-data').textContent);
    const index=Number(card.querySelector('input[type="range"]').value);
    return {card_index:${cardIndex}, index, frame:data.frames[index], tile_size:data.tile_size,
      width:canvas.width, height:canvas.height,
      clip:{x:box.left+scrollX,y:box.top+scrollY,width:box.width,height:box.height,scale:1}};
  })()`);
}
async function drawReference(state) {
  await evaluate(`(async () => {
    const s=${JSON.stringify(state)}, image=new Image(); image.src=s.frame.page_path;
    await image.decode();
    const canvas=document.querySelectorAll('.source-sequence')[s.card_index].querySelector('canvas');
    const backup=document.createElement('canvas'); backup.width=s.width; backup.height=s.height;
    backup.getContext('2d').drawImage(canvas,0,0);
    window.__s11CanvasCheckBackup={canvas,backup};
    const ctx=canvas.getContext('2d'); ctx.save(); ctx.setTransform(1,0,0,1,0,0);
    ctx.globalAlpha=1; ctx.globalCompositeOperation='copy';
    ctx.drawImage(image,s.frame.tile_xy[0],s.frame.tile_xy[1],
      s.tile_size,s.tile_size,0,0,s.width,s.height);
    ctx.restore();
  })()`);
}
async function checkCanvas(cardIndex) {
  const state = await canvasState(cardIndex);
  if (state.frame.status !== 'AVAILABLE') throw new Error('Expected available source frame');
  // file:// taints canvas readback. CDP screenshots keep normal browser security intact.
  const screenshot = () => request('Page.captureScreenshot',
    {format:'png',clip:state.clip,captureBeyondViewport:true}, session);
  const actual = await screenshot();
  let expected;
  try {
    await drawReference(state);
    expected = await screenshot();
  } finally {
    await evaluate(`(() => { const saved=window.__s11CanvasCheckBackup; if (!saved) return;
      const ctx=saved.canvas.getContext('2d'); ctx.save(); ctx.setTransform(1,0,0,1,0,0);
      ctx.globalAlpha=1; ctx.globalCompositeOperation='copy'; ctx.drawImage(saved.backup,0,0);
      ctx.restore(); delete window.__s11CanvasCheckBackup; })()`);
  }
  const observedHash = digest(Buffer.from(actual.data, 'base64'));
  const expectedHash = digest(Buffer.from(expected.data, 'base64'));
  const restored = await screenshot();
  const restoredHash = digest(Buffer.from(restored.data, 'base64'));
  if (restoredHash !== observedHash) throw new Error('Canvas restoration mismatch');
  if (observedHash !== expectedHash) {
    throw new Error(`Canvas pixel mismatch: card=${cardIndex}, index=${state.index}, frame=${state.frame.frame_index}`);
  }
  return {card_index:cardIndex,index:state.index,frame_index:state.frame.frame_index,
    actual_time_sec:state.frame.actual_time_sec,page_path:state.frame.page_path,
    tile_xy:state.frame.tile_xy,observed_png_sha256:observedHash,
    reference_png_sha256:expectedHash,restored_png_sha256:restoredHash,equal:true,pixels_restored:true};
}
try {
  const address = await new Promise((resolve, reject) => {
    let stderr = '';
    const timer = setTimeout(() => reject(new Error('Chrome startup timeout')), 15000);
    chrome.on('error', reject);
    chrome.on('exit', code => { clearTimeout(timer); reject(new Error(`Chrome exited ${code}`)); });
    chrome.stderr.on('data', bytes => {
      stderr += bytes.toString();
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) { clearTimeout(timer); resolve(match[1]); }
    });
  });
  ws = new WebSocket(address);
  await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
  ws.onmessage = event => {
    const data = JSON.parse(event.data);
    if (data.id) {
      const entry = pending.get(data.id);
      if (!entry) return;
      pending.delete(data.id); clearTimeout(entry.timer);
      if (data.error) entry.reject(new Error(JSON.stringify(data.error))); else entry.resolve(data.result);
    } else if (data.method === 'Runtime.exceptionThrown') errors.push(data.params);
    else if (data.method === 'Network.loadingFailed') networkFailures.push(data.params);
  };
  const version = await request('Browser.getVersion');
  const target = await request('Target.createTarget', { url: 'about:blank' });
  session = (await request('Target.attachToTarget', { targetId: target.targetId, flatten: true })).sessionId;
  for (const method of ['Page.enable', 'Runtime.enable', 'Network.enable']) await request(method, {}, session);
  await request('Emulation.setDeviceMetricsOverride', { width: 1280, height: 1050, deviceScaleFactor: 1, mobile: false }, session);
  await request('Page.navigate', { url: pathToFileURL(report).href }, session);
  for (let n = 0; n < 60; n++) {
    if (await evaluate('document.readyState === "complete" && document.querySelectorAll(".source-sequence").length === 3')) break;
    await sleep(100);
  }
  await sleep(250);
  const initial = await evaluate(`Array.from(document.querySelectorAll('.source-sequence'), card => ({
    status: card.querySelector('.sequence-time').textContent,
    canvas_visible: !card.querySelector('canvas').hidden,
    controls_visible: !card.querySelector('.sequence-controls').hidden,
    first_disabled: card.querySelector('[data-step="-1"]').disabled,
    last_disabled: card.querySelector('[data-step="1"]').disabled,
    slider_max: Number(card.querySelector('input[type="range"]').max)
  }))`);
  if (initial.length !== 3 || initial.some(s => !s.canvas_visible || !s.controls_visible || !s.first_disabled)) {
    throw new Error('Initial report controls failed');
  }
  const canvasChecks = [];
  for (let cardIndex = 0; cardIndex < initial.length; cardIndex++) {
    canvasChecks.push(await checkCanvas(cardIndex));
  }
  const checks = [];
  for (const index of [75, 120, 180, 0]) {
    await evaluate(`(() => { const card=document.querySelectorAll('.source-sequence')[1];
      const slider=card.querySelector('input[type="range"]'); slider.value='${index}';
      slider.dispatchEvent(new Event('input', {bubbles:true})); })()`);
    await sleep(180);
    const state = await evaluate(`(() => { const card=document.querySelectorAll('.source-sequence')[1];
      return { index:Number(card.querySelector('input[type="range"]').value),
        status:card.querySelector('.sequence-time').textContent,
        first_disabled:card.querySelector('[data-step="-1"]').disabled,
        last_disabled:card.querySelector('[data-step="1"]').disabled }; })()`);
    const frame = 1200 + index;
    if (!state.status.endsWith(`f${frame}`) || state.first_disabled !== (index === 0) || state.last_disabled !== (index === 180)) {
      throw new Error(`Slider mismatch ${JSON.stringify(state)}`);
    }
    checks.push({ ...state, expected_frame: frame });
    canvasChecks.push(await checkCanvas(1));
  }
  await evaluate(`document.querySelectorAll('.source-sequence')[1].querySelector('[data-step="1"]').click()`);
  await sleep(150);
  const step = await evaluate(`document.querySelectorAll('.source-sequence')[1].querySelector('.sequence-time').textContent`);
  if (!step.endsWith('f1201')) throw new Error('Step button failed');
  canvasChecks.push(await checkCanvas(1));
  const imageLoads = await evaluate(`Promise.all([...new Set([
    ...Array.from(document.images, image => image.getAttribute('src')),
    ...Array.from(document.querySelectorAll('.sequence-data'), s => JSON.parse(s.textContent).frames)
      .flat().filter(f => f.status==='AVAILABLE').map(f => f.page_path)
  ])].filter(Boolean).map(path => new Promise(resolve => {
    const image=new Image(); image.onload=()=>resolve({path,loaded:true,width:image.naturalWidth,height:image.naturalHeight});
    image.onerror=()=>resolve({path,loaded:false}); image.src=path;
  })))`);
  if (imageLoads.some(image => !image.loaded) || errors.length || networkFailures.length) throw new Error('Report asset/runtime failure');
  await evaluate(`(() => { const card=document.querySelectorAll('.source-sequence')[1];
    const slider=card.querySelector('input[type="range"]'); slider.value='120';
    slider.dispatchEvent(new Event('input')); card.scrollIntoView({block:'start'}); })()`);
  await sleep(200);
  const shot = await request('Page.captureScreenshot', { format:'png' }, session);
  writeFileSync(join(output, 'report-browser.png'), Buffer.from(shot.data, 'base64'), { flag: 'wx' });
  if (digest(readFileSync(report)) !== reportBefore) throw new Error('Report bytes changed during check');
  const result = { schema:'s11-round3-browser-smoke-v3', report, report_sha256:reportBefore, browser:version,
    access_mode:'file://; no special file-access flags', initial_controls:initial,
    canvas_verification:'CDP PNG equality before/after same-canvas source-tile reference repaint; original pixels restored and rechecked; CSS layout unchanged',
    canvas_checks:canvasChecks,
    slider_checks:checks, next_step_check:step, images:imageLoads,
    page_errors:errors, network_failures:networkFailures,
    original_report_changed:false, human_comprehension:'NOT_EVALUATED' };
  writeFileSync(join(output, 'browser.json'), JSON.stringify(result,null,2)+'\n', { flag:'wx' });
  console.log(JSON.stringify({controls:initial.length,slider_checks:checks.length,images:imageLoads.length,page_errors:errors.length}));
} finally {
  if (ws?.readyState === WebSocket.OPEN) {
    try { await request('Browser.close'); } catch (_) { /* Chrome may close transport first. */ }
    ws.close();
  }
  if (chrome.exitCode === null) { chrome.kill('SIGTERM'); await sleep(700); }
  if (chrome.exitCode === null) { chrome.kill('SIGKILL'); await sleep(300); }
  for (const entry of pending.values()) { clearTimeout(entry.timer); entry.reject(new Error('Browser closed')); }
  if (chrome.exitCode !== null || chrome.signalCode !== null) rmSync(profile, { recursive:true, force:true });
}
