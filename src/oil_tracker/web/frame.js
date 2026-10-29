// The frame view shared by the Recipe screen and the analysis setup (DESIGN.md §4 "Frame view", §5):
// an exact source frame, the Glasses over it, edited as in v1, and the transport under it.
// There is one frame view in the page; attach() moves it into the screen on show, with that
// screen's hooks. The screen owns the Glasses and the open video's lifetime.
import * as api from "./api.js";
import { $, clock, css, el, notify } from "./ui.js";

const HANDLE = 8;        // px, drawn handle size
const HIT = 6;           // px, handle hit tolerance
const ZERO_HIT = 7;      // px, half of the 14 px zero-line hit band
const MIN_RADIUS = 8;    // source px, as domain/geometry.py
const MAX_ZOOM = 16;
const SPEED_MIN = 0.1;
const SPEED_MAX = 16;
const SPEED_PRESETS = [0.5, 1, 2, 3, 4];

const NO_HOOKS = {
  glasses: () => [],          // each {id, name, ellipse, zero_line_y}
  selected: () => null,       // the selected Glass id
  select: () => {},           // a click picked another Glass
  moving: () => {},           // a drag is moving a Glass
  moved: () => {},            // a drag or an arrow key changed a Glass
  marks: () => [],            // scrub marks: {time, label, kind}
  range: () => null,          // a [start, end] band on the scrub
  size: () => ({ W: 1280, H: 720 }),  // the frame size with no video open
  noticeId: "",
};

let hooks = NO_HOOKS;
const state = {
  video: null,           // the open video, in the API's shape
  shownIndex: 0,         // frame index on screen
  shownTime: 0,
  wantIndex: 0,          // frame index asked for
  loading: false,
  image: null,           // ImageBitmap on screen
  zoom: 1, panX: 0, panY: 0,
  playing: false,
  speed: 1,
  drag: null,
};

// ---- attaching ----------------------------------------------------------------------------

/** Move the frame view into `host` (after its header) and drive it with `screenHooks`. */
export function attach(host, screenHooks) {
  hooks = { ...NO_HOOKS, ...screenHooks };
  host.append($("frameBox"), $("transport"));
  state.image = null;
  resetView();
  refresh();
}

export function video() {
  return state.video;
}

/** The time of the frame on screen. */
export function shownTime() {
  return state.shownTime;
}

export function showImage(bitmap) {
  state.image = bitmap;
  draw();
}

export function resetView() {
  state.zoom = 1; state.panX = 0; state.panY = 0;
}

// ---- video and frames -----------------------------------------------------------------------

/** Ask for a video file and open it; null when cancelled or refused (the notice says why). */
export async function chooseVideo(noticeId, recipeId = null) {
  const picked = await api.call("POST", "/api/videos/pick", {});
  let path = null;
  if (picked.status === 501) path = prompt("영상 파일 경로");  // development without a window
  else if (picked.ok) path = picked.data.path;
  else notify(noticeId, picked.data.error ?? "파일을 고르지 못했습니다.", "error");
  if (!path) return null;
  const opened = await api.call("POST", "/api/videos", { path, recipe_id: recipeId });
  if (!opened.ok) {
    notify(noticeId, opened.data.error ?? "영상을 열지 못했습니다.", "error");
    return null;
  }
  return opened.data;
}

export function setVideo(video, time) {
  state.video = video;
  state.shownIndex = -1;
  resetView();
  refresh();
  seekIndex(Math.round(time * video.fps));
}

export async function closeVideo() {
  stopPlayback();
  if (!state.video) return;
  const id = state.video.id;
  state.video = null;
  refresh();
  await api.call("DELETE", `/api/videos/${encodeURIComponent(id)}`);
}

export function seekTime(time) {
  if (state.video) seekIndex(Math.round(time * state.video.fps));
}

function seekIndex(index) {
  if (!state.video) return;
  state.wantIndex = Math.max(0, Math.min(state.video.frame_count - 1, index));
  renderTransport();
  loadFrame();
}

async function loadFrame() {
  if (state.loading || !state.video) return;
  const video = state.video;
  const index = state.wantIndex;
  state.loading = true;
  try {
    // the frame's own start: the server rounds to the nearest frame, and a half-way time could round
    // either way (Python rounds a half to even)
    const time = index / video.fps;
    const { bitmap, headers } = await api.getImage(`/api/videos/${encodeURIComponent(video.id)}/frame?t=${time}`);
    if (state.video === video) {
      state.image = bitmap;
      state.shownIndex = Number(headers.get("X-Frame-Index"));
      state.shownTime = Number(headers.get("X-Frame-Time"));
      renderTransport();
      draw();
    }
  } catch (error) {
    stopPlayback();
    notify(hooks.noticeId, error.message, "error");
  } finally {
    state.loading = false;
  }
  if (state.video === video && state.wantIndex !== index) loadFrame();  // a newer frame was asked for meanwhile
}

// ---- playback and speed ---------------------------------------------------------------------

let playStart = 0;
let playFrom = 0;
function playTime() {
  return playFrom + (performance.now() - playStart) / 1000 * state.speed;
}

export function togglePlayback() {
  if (state.playing) stopPlayback();
  else startPlayback();
}

function startPlayback() {
  if (!state.video) return;
  if (state.wantIndex >= state.video.frame_count - 1) seekIndex(0);
  state.playing = true;
  playStart = performance.now();
  playFrom = state.wantIndex / state.video.fps;
  $("playIcon").setAttribute("d", "M5 4h3v12H5zM12 4h3v12h-3z");
  requestAnimationFrame(playTick);
}

function playTick() {
  if (!state.playing || !state.video) return;
  const index = Math.floor(playTime() * state.video.fps);
  if (index >= state.video.frame_count - 1) {
    seekIndex(state.video.frame_count - 1);
    stopPlayback();
    return;
  }
  if (index !== state.wantIndex) seekIndex(index);
  requestAnimationFrame(playTick);
}

export function stopPlayback() {
  state.playing = false;
  $("playIcon").setAttribute("d", "M6 4l10 6-10 6z");
}

/** "2", "2x", "×2" and "*2" all read as 2, clamped to the allowed range; null when it is not a number. */
function parseSpeed(text) {
  const bare = text.trim().replace(/^[x×*]\s*/i, "").replace(/\s*[x×]$/i, "");
  const number = Number(bare);
  if (bare === "" || !Number.isFinite(number)) return null;
  return Math.round(Math.min(SPEED_MAX, Math.max(SPEED_MIN, number)) * 100) / 100;
}

function setSpeed(speed) {
  if (state.playing) {  // carry on from where playback is now
    playFrom = playTime();
    playStart = performance.now();
  }
  state.speed = speed;
  $("speed").value = String(speed);
}

function commitSpeed() {
  const speed = parseSpeed($("speed").value);
  if (speed === null) $("speed").value = String(state.speed);  // not a number: keep the current speed
  else setSpeed(speed);
}

export function toggleSpeedMenu(open) {
  const menu = $("speedMenu");
  menu.hidden = !open;
  if (!open) return;
  menu.replaceChildren(...SPEED_PRESETS.map((speed) => el("button", {
    class: speed === state.speed ? "on" : "", role: "option", "aria-selected": String(speed === state.speed),
    onclick: () => { setSpeed(speed); toggleSpeedMenu(false); $("frame").focus(); },
  }, `${speed}×`)));
}

function scrubTo(clientX) {
  if (!state.video) return;
  const box = $("scrub").getBoundingClientRect();
  const fraction = Math.max(0, Math.min(1, (clientX - box.left) / box.width));
  stopPlayback();
  seekIndex(Math.round(fraction * (state.video.frame_count - 1)));
}

// ---- geometry -------------------------------------------------------------------------------

function frameSize() {
  return state.video ? { W: state.video.width, H: state.video.height } : hooks.size();
}

function layout() {
  const box = $("frameBox");
  const w = box.clientWidth, h = box.clientHeight;
  const { W, H } = frameSize();
  const s = Math.min(w / W, h / H) * state.zoom;
  return { w, h, W, H, s, ox: (w - W * s) / 2 + state.panX, oy: (h - H * s) / 2 + state.panY };
}

function chord(glass, y) {
  const e = glass.ellipse;
  const u = (y - e.center_y) / e.radius_y;
  if (!(Math.abs(u) <= 1)) return null;
  const half = e.radius_x * Math.sqrt(1 - u * u);
  return [e.center_x - half, e.center_x + half];
}

function bounds(glass) {
  const e = glass.ellipse;
  return { l: e.center_x - e.radius_x, r: e.center_x + e.radius_x, t: e.center_y - e.radius_y, b: e.center_y + e.radius_y };
}

function handlePoints(glass, L) {
  const { l, r, t, b } = bounds(glass);
  const cx = glass.ellipse.center_x, cy = glass.ellipse.center_y;
  const at = (x, y) => [L.ox + x * L.s, L.oy + y * L.s];
  return { tl: at(l, t), t: at(cx, t), tr: at(r, t), r: at(r, cy), br: at(r, b), b: at(cx, b), bl: at(l, b), l: at(l, cy) };
}

function selectedGlass() {
  return hooks.glasses().find((g) => g.id === hooks.selected()) ?? null;
}

function glassesSelectedFirst() {
  const all = hooks.glasses();
  const selected = hooks.selected();
  return [...all.filter((g) => g.id === selected), ...all.filter((g) => g.id !== selected)];
}

function hitTest(x, y) {
  const L = layout();
  const selected = selectedGlass();
  if (selected) {
    for (const [role, [hx, hy]] of Object.entries(handlePoints(selected, L))) {
      if (Math.abs(x - hx) <= HIT && Math.abs(y - hy) <= HIT) return { kind: "resize", glass: selected, role };
    }
  }
  const ordered = glassesSelectedFirst();
  for (const glass of ordered) {  // the zero line sits above the ellipse
    const zy = L.oy + glass.zero_line_y * L.s;
    const span = chord(glass, glass.zero_line_y);
    if (!span || Math.abs(y - zy) > ZERO_HIT) continue;
    if (x >= L.ox + span[0] * L.s - HIT && x <= L.ox + span[1] * L.s + HIT) return { kind: "zero", glass };
  }
  const sx = (x - L.ox) / L.s, sy = (y - L.oy) / L.s;
  for (const glass of ordered) {
    const e = glass.ellipse;
    const dx = (sx - e.center_x) / e.radius_x, dy = (sy - e.center_y) / e.radius_y;
    if (dx * dx + dy * dy <= 1) return { kind: "move", glass };
  }
  return null;
}

const CURSORS = { tl: "nwse-resize", br: "nwse-resize", tr: "nesw-resize", bl: "nesw-resize", t: "ns-resize", b: "ns-resize", l: "ew-resize", r: "ew-resize" };

function setEllipseFromBox(glass, l, t, r, b) {
  glass.ellipse = { center_x: (l + r) / 2, center_y: (t + b) / 2, radius_x: (r - l) / 2, radius_y: (b - t) / 2 };
  glass.zero_line_y = Math.min(b, Math.max(t, glass.zero_line_y));  // as v1: resizing pulls the zero line inside
}

function resizeGlass(glass, start, role, sx, sy) {
  const { W, H } = frameSize();
  const min = 2 * MIN_RADIUS;
  let { l, r, t, b } = start;
  if (role.includes("l")) l = Math.max(0, Math.min(Math.round(sx), r - min));
  if (role.includes("r")) r = Math.min(W, Math.max(Math.round(sx), l + min));
  if (role.includes("t")) t = Math.max(0, Math.min(Math.round(sy), b - min));
  if (role.includes("b")) b = Math.min(H, Math.max(Math.round(sy), t + min));
  setEllipseFromBox(glass, l, t, r, b);
}

function moveGlass(glass, startEllipse, startZero, dx, dy) {
  const { W, H } = frameSize();
  const e = startEllipse;
  const cx = Math.min(W - e.radius_x, Math.max(e.radius_x, Math.round(e.center_x + dx)));
  const cy = Math.min(H - e.radius_y, Math.max(e.radius_y, Math.round(e.center_y + dy)));
  glass.ellipse = { ...e, center_x: cx, center_y: cy };
  glass.zero_line_y = startZero + (cy - e.center_y);
}

function moveZero(glass, sy) {
  const { t, b } = bounds(glass);
  glass.zero_line_y = Math.min(b, Math.max(t, Math.round(sy)));
}

function onPointerDown(event) {
  if (event.button !== 0) return;
  const canvas = $("frame");
  canvas.focus();
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left, y = event.clientY - rect.top;
  if (event.shiftKey) {
    state.drag = { kind: "pan", x0: event.clientX, y0: event.clientY, panX: state.panX, panY: state.panY };
  } else {
    const hit = hitTest(x, y);
    if (!hit) return;  // a plain drag on empty space does nothing (DESIGN.md §7)
    if (hit.glass.id !== hooks.selected()) hooks.select(hit.glass.id);
    const L = layout();
    state.drag = {
      ...hit,
      sx0: (x - L.ox) / L.s, sy0: (y - L.oy) / L.s,
      box: bounds(hit.glass), ellipse: { ...hit.glass.ellipse }, zero: hit.glass.zero_line_y, moved: false,
    };
  }
  canvas.setPointerCapture(event.pointerId);
  draw();
}

function onPointerMove(event) {
  const canvas = $("frame");
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left, y = event.clientY - rect.top;
  const drag = state.drag;
  if (!drag) {
    const hit = hitTest(x, y);
    canvas.style.cursor = !hit ? "default" : hit.kind === "resize" ? CURSORS[hit.role] : hit.kind === "zero" ? "ns-resize" : "move";
    return;
  }
  if (drag.kind === "pan") {
    state.panX = drag.panX + event.clientX - drag.x0;
    state.panY = drag.panY + event.clientY - drag.y0;
    draw();
    return;
  }
  const L = layout();
  const sx = (x - L.ox) / L.s, sy = (y - L.oy) / L.s;
  if (drag.kind === "resize") resizeGlass(drag.glass, drag.box, drag.role, sx, sy);
  else if (drag.kind === "move") moveGlass(drag.glass, drag.ellipse, drag.zero, sx - drag.sx0, sy - drag.sy0);
  else moveZero(drag.glass, sy);
  drag.moved = true;
  draw();
  hooks.moving();
}

function onPointerUp() {
  const drag = state.drag;
  state.drag = null;
  if (drag?.moved) hooks.moved();
}

function onWheel(event) {
  event.preventDefault();
  const rect = $("frame").getBoundingClientRect();
  const cx = event.clientX - rect.left, cy = event.clientY - rect.top;
  const before = layout();
  const px = (cx - before.ox) / before.s, py = (cy - before.oy) / before.s;
  state.zoom = Math.max(1, Math.min(MAX_ZOOM, state.zoom * Math.exp(-event.deltaY * 0.0015)));
  if (state.zoom === 1) {
    state.panX = 0; state.panY = 0;
  } else {
    const after = layout();
    state.panX += cx - (after.ox + px * after.s);
    state.panY += cy - (after.oy + py * after.s);
  }
  draw();
}

/** The frame view's keys: Space, "," and ".", and the arrows for the selected Glass. True when used. */
export function handleKey(event) {
  const step = event.shiftKey ? 10 : 1;
  const arrows = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] };
  if (arrows[event.key]) {
    const glass = selectedGlass();
    if (!glass) return false;
    event.preventDefault();
    moveGlass(glass, { ...glass.ellipse }, glass.zero_line_y, ...arrows[event.key]);
    draw();
    hooks.moving();
    hooks.moved();
  } else if (event.key === " ") {
    event.preventDefault();
    togglePlayback();
  } else if (event.key === ",") {
    stopPlayback();
    seekIndex(state.wantIndex - 1);
  } else if (event.key === ".") {
    stopPlayback();
    seekIndex(state.wantIndex + 1);
  } else {
    return false;
  }
  return true;
}

// ---- rendering -------------------------------------------------------------------------------

/** Enable the transport when a video is open, and redraw. */
export function refresh() {
  const off = !state.video;
  for (const id of ["prevFrame", "play", "nextFrame", "speed", "speedMenuBtn"]) $(id).disabled = off;
  $("scrub").classList.toggle("off", off);
  $("speedBox").classList.toggle("off", off);
  if (off) toggleSpeedMenu(false);
  renderTransport();
  draw();
}

export function renderTransport() {
  const video = state.video;
  const marks = $("scrubMarks");
  const band = $("scrubRange");
  if (!video) {
    $("time").textContent = "--:--.- / --:--.-";
    marks.replaceChildren();
    band.hidden = true;
    return;
  }
  const last = Math.max(1, video.frame_count - 1);
  const at = (time) => `${Math.max(0, Math.min(100, (time * video.fps / last) * 100))}%`;
  const fraction = state.wantIndex / last;
  $("scrubDone").style.width = `${fraction * 100}%`;
  $("scrubThumb").style.left = `${fraction * 100}%`;
  $("time").textContent = `${clock(state.wantIndex / video.fps)} / ${clock(video.duration_sec)}`;
  marks.replaceChildren(...hooks.marks().map((mark) => el("span", { class: `mark ${mark.kind}`, style: `left:${at(mark.time)}` }, mark.label)));
  const range = hooks.range();
  band.hidden = !range;
  if (range) {
    band.style.left = at(range[0]);
    band.style.width = `calc(${at(range[1])} - ${at(range[0])})`;
  }
}

export function draw() {
  const canvas = $("frame");
  if ($("frameBox").offsetParent === null) return;  // not on screen
  const L = layout();
  const dpr = window.devicePixelRatio || 1;
  if (canvas.width !== Math.round(L.w * dpr) || canvas.height !== Math.round(L.h * dpr)) {
    canvas.width = Math.round(L.w * dpr);
    canvas.height = Math.round(L.h * dpr);
  }
  const g = canvas.getContext("2d");
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.fillStyle = css("--frame-bg");
  g.fillRect(0, 0, L.w, L.h);
  if (state.image) g.drawImage(state.image, L.ox, L.oy, L.W * L.s, L.H * L.s);
  const selected = hooks.selected();
  for (const glass of glassesSelectedFirst().reverse()) drawGlass(g, glass, L, glass.id === selected);  // the selected one on top
}

function drawGlass(g, glass, L, selected) {
  const X = (x) => L.ox + x * L.s, Y = (y) => L.oy + y * L.s;
  const e = glass.ellipse;
  if (!(e.radius_x > 0 && e.radius_y > 0)) return;
  const span = chord(glass, glass.zero_line_y) ?? [e.center_x - e.radius_x, e.center_x + e.radius_x];
  const width = selected ? 1.5 : 1;
  for (const [stroke, offset] of [[css("--glass-shadow"), 1], [css("--glass-outline"), 0]]) {
    g.save();
    g.strokeStyle = stroke;
    g.lineWidth = width;
    g.setLineDash(selected ? [] : [4, 3]);
    g.beginPath();
    g.ellipse(X(e.center_x), Y(e.center_y) + offset, e.radius_x * L.s, e.radius_y * L.s, 0, 0, Math.PI * 2);
    g.stroke();
    g.beginPath();
    g.moveTo(X(span[0]), Y(glass.zero_line_y) + offset);
    g.lineTo(X(span[1]), Y(glass.zero_line_y) + offset);
    g.stroke();
    g.restore();
  }
  const font = css("--font");
  g.font = `600 12px ${font}`;
  const name = glass.name.trim() || "(이름 없음)";
  const chipW = g.measureText(name).width + 12;
  const top = Y(e.center_y - e.radius_y);
  chip(g, X(e.center_x) - chipW / 2, top - 26, chipW, name);
  g.font = `400 12px ${font}`;
  chip(g, X(span[0]) - 20, Y(glass.zero_line_y) - 10, 16, "0");
  if (selected) {
    g.fillStyle = css("--bg-1");
    g.strokeStyle = css("--brand");
    g.lineWidth = 1;
    for (const [hx, hy] of Object.values(handlePoints(glass, L))) {
      g.fillRect(hx - HANDLE / 2, hy - HANDLE / 2, HANDLE, HANDLE);
      g.strokeRect(hx - HANDLE / 2 + 0.5, hy - HANDLE / 2 + 0.5, HANDLE - 1, HANDLE - 1);
    }
  }
}

function chip(g, x, y, width, text) {
  g.fillStyle = css("--frame-caption-bg");
  g.beginPath();
  g.roundRect(x, y, width, 20, 4);
  g.fill();
  g.fillStyle = css("--bg-1");
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.fillText(text, x + width / 2, y + 10.5);
}

// ---- wiring ------------------------------------------------------------------------------------

export function wire() {
  $("prevFrame").addEventListener("click", () => { stopPlayback(); seekIndex(state.wantIndex - 1); });
  $("nextFrame").addEventListener("click", () => { stopPlayback(); seekIndex(state.wantIndex + 1); });
  $("play").addEventListener("click", togglePlayback);
  const speed = $("speed");
  speed.addEventListener("change", commitSpeed);
  speed.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      commitSpeed();
      $("frame").focus();
    } else if (event.key === "Escape") {
      speed.value = String(state.speed);
      $("frame").focus();
    }
  });
  $("speedMenuBtn").addEventListener("click", () => toggleSpeedMenu($("speedMenu").hidden));
  document.addEventListener("pointerdown", (event) => {
    if (!$("speedMenu").hidden && !$("speedBox").contains(event.target)) toggleSpeedMenu(false);
  });
  const scrub = $("scrub");
  scrub.addEventListener("pointerdown", (event) => {
    if (!state.video) return;
    scrub.setPointerCapture(event.pointerId);
    scrubTo(event.clientX);
  });
  scrub.addEventListener("pointermove", (event) => {
    if (scrub.hasPointerCapture(event.pointerId)) scrubTo(event.clientX);
  });
  const canvas = $("frame");
  canvas.addEventListener("pointerdown", onPointerDown);
  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerup", onPointerUp);
  canvas.addEventListener("pointercancel", onPointerUp);
  canvas.addEventListener("wheel", onWheel, { passive: false });
  new ResizeObserver(draw).observe($("frameBox"));
}
