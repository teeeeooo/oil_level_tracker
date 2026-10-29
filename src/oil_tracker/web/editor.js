// The editor (DESIGN.md §5 "Editor window"; Product SSOT §4 and §6). It holds the edits, turns the
// pointer and keys into line operations (lines.js) and draws through render.js. What follows from
// the lines (FULL/EMPTY, the empty stretches, the coverage) comes from the API after each change.
import * as api from "./api.js";
import * as lines from "./lines.js";
import * as nav from "./nav.js";
import * as player from "./player.js";
import * as render from "./render.js";
import { $, MODES, clock, el, localDate, notify, parseClock, typing } from "./ui.js";

const TOOL_KEYS = { KeyG: "grab", KeyP: "pencil", KeyR: "range", KeyH: "pan" };
const HIT_PX = 8;          // how near a line a press grabs it
const EDGE_PX = 5;         // how near a selection edge a press moves it
const DRAG_PX = 3;         // the movement that makes a press a drag
const MIN_SPAN_SEC = 2;    // the narrowest time view
const MIN_SPAN_PX = 8;     // the lowest height view, in source px
const SOURCE_POLL_MS = 300;

const state = {
  detail: null,            // the inspection
  analysis: null,          // its stored analysis: times and the picture layout
  edits: null,             // the edit document, as the API sends it; changed in place
  savedAt: null,
  dirty: false,
  derived: new Map(),      // glass id -> what follows from its lines (API)
  glassId: null,
  tool: "grab",
  kind: "oil",             // the line the pencil draws
  width: 30,               // the grab width, seconds
  shape: "smooth",
  snap: true,
  background: false,
  view: null,
  selection: null,         // { t0, t1 }
  playhead: 0,
  drag: null,
  hot: null,               // the line kind under the pointer
  history: new lines.History(),
  images: new Map(),       // "glass/kind" -> [{ url, width }]
  luma: new Map(),         // glass id -> the context image's luma
  redraws: [],             // ms per lines redraw while dragging, for the A5 measurement
};
let backToList = () => {};
let toSetup = () => {};
let pending = { back: false, lines: false, marks: false };
let frameRequested = false;
let deriving = null;       // the states request in flight
let deriveAgain = false;

// ---- opening and leaving -----------------------------------------------------------------------

export async function open(inspectionId) {
  release();
  nav.show("editorView");
  const id = encodeURIComponent(inspectionId);
  try {
    state.detail = await api.getJson(`/api/inspections/${id}`);
    state.analysis = await api.getJson(`/api/inspections/${id}/analysis`);
    const opened = await api.getJson(`/api/inspections/${id}/edits`);
    state.edits = opened.edits;
    state.savedAt = opened.saved_at;
    setDirty(opened.unsaved);
    takeDerived(opened.glasses);
  } catch (error) {
    notify("editorNotice", error.message, "error");
    return;
  }
  state.glassId = state.analysis.glasses[0]?.glass_id ?? null;
  state.playhead = state.analysis.times[0] ?? 0;
  checkSource().catch(() => {});
  renderHeader();
  renderTools();
  try {
    await player.open(inspectionId, { time: onPlayerTime, overlay, repeat: () => state.selection });
  } catch (error) {
    notify("editorNotice", `영상을 열 수 없습니다: ${error.message}`, "error");
  }
  await showGlass(true);
}

function release() {
  player.close();
  for (const pieces of state.images.values()) for (const piece of pieces) URL.revokeObjectURL(piece.url);
  state.images.clear();
  state.luma.clear();
  state.derived.clear();
  state.history.clear();
  Object.assign(state, { detail: null, analysis: null, edits: null, selection: null, drag: null, hot: null });
  setDirty(false);
  for (const id of ["graph", "context"]) for (const layer of $(id).children) layer.replaceChildren();
  $("axis").replaceChildren();
  $("sourceWarning").hidden = true;
}

function leave() {
  if (state.dirty && !confirm("저장하지 않은 편집이 있습니다. 저장하지 않고 나갈까요?")) return;
  release();
  backToList();
}

/** "범위 바꿔 다시 분석…": the setup of this inspection. The re-analysis merges the saved edits, so
 * unsaved ones are saved first. */
async function reanalyse() {
  if (!state.detail) return;
  if (state.dirty && !confirm("다시 분석하기 전에 편집을 저장합니다. 저장하고 분석 설정으로 갈까요?")) return;
  if (state.dirty && !(await save())) return;
  const id = state.detail.id;
  release();
  toSetup(id);
}

/** Compare the source video with the analysed one (A9) and warn while it differs, is missing or
 * cannot be read. Hashing a long video takes seconds; the check runs on the server meanwhile. */
async function checkSource() {
  const id = state.detail.id;
  const path = `/api/inspections/${encodeURIComponent(id)}/source-check`;
  $("sourceRecheck").disabled = true;
  if (!$("sourceWarning").hidden) $("sourceWarningText").textContent = "원본 영상을 확인하는 중입니다…";
  let result = await api.call("POST", path);
  while (result.ok && result.data.state === "CHECKING") {
    await new Promise((resolve) => setTimeout(resolve, SOURCE_POLL_MS));
    if (state.detail?.id !== id) return;
    result = await api.call("GET", path);
  }
  if (state.detail?.id !== id) return;
  const check = result.ok ? result.data : { state: "UNREADABLE", message: result.data.error ?? `HTTP ${result.status}` };
  $("sourceRecheck").disabled = false;
  $("sourceWarningText").textContent = check.message ?? "";
  $("sourceWarning").hidden = check.state === "SAME";
}

async function showGlass(fit) {
  const glass = recipeGlass();
  const top = glass.zero_line_y - (glass.ellipse.center_y - glass.ellipse.radius_y);
  const bottom = glass.zero_line_y - (glass.ellipse.center_y + glass.ellipse.radius_y);
  const whole = render.fitView({ times: state.analysis.times, top, bottom });
  state.view = fit || !state.view ? whole : { ...state.view, h0: bottom, h1: top };
  player.frameGlass(glass);
  player.seek(state.playhead);
  renderGlassPanel();
  requestDraw({ back: true, lines: true, marks: true });
  try {
    await loadImages(state.glassId, state.background ? "background" : "context");
    await loadImages(state.glassId, "context");
  } catch (error) {
    notify("editorNotice", `그림을 불러오지 못했습니다: ${error.message}`, "error");
  }
  requestDraw({ back: true });
}

async function loadImages(glassId, kind) {
  const key = `${glassId}/${kind}`;
  if (!state.images.has(key)) {
    const layout = layoutOf(glassId);
    const base = `/api/inspections/${encodeURIComponent(state.detail.id)}/images/${encodeURIComponent(glassId)}`;
    const pieces = [];
    for (let index = 0; index < layout.pieces; index++) pieces.push(await api.getImageUrl(`${base}/${kind}-${index}.png`));
    state.images.set(key, pieces);
  }
  if (kind === "context" && !state.luma.has(glassId)) {
    state.luma.set(glassId, null);  // being read
    state.luma.set(glassId, await lines.lumaOf(state.images.get(key).map((p) => p.url)));
  }
}

// ---- the data the drawing needs ------------------------------------------------------------------

function recipeGlass(glassId = state.glassId) {
  return state.detail.recipe.glasses.find((g) => g.id === glassId);
}

function layoutOf(glassId = state.glassId) {
  return state.analysis.glasses.find((g) => g.glass_id === glassId);
}

function editsOf(glassId = state.glassId) {
  return state.edits.glasses.find((g) => g.glass_id === glassId);
}

function lineOf(glassId, kind) {
  return editsOf(glassId)[kind];
}

function zero() {
  return recipeGlass().zero_line_y;
}

function panel() {
  const glass = recipeGlass(), layout = layoutOf(), edits = editsOf();
  const z = glass.zero_line_y, e = glass.ellipse;
  const derived = state.derived.get(state.glassId);
  const loaded = state.images.get(`${state.glassId}/${state.background ? "background" : "context"}`);
  let first = 0;
  const pieces = (loaded ?? []).map((piece) => {
    const placed = { href: piece.url, first, count: piece.width };
    first += piece.width;
    return placed;
  });
  const heights = (line) => line.ys.map((y) => (y === null ? null : z - y));
  return {
    times: state.edits.times,
    top: z - (e.center_y - e.radius_y),
    bottom: z - (e.center_y + e.radius_y),
    compressor: state.edits.compressor_start_sec,
    lines: { oil: heights(edits.oil), foam: heights(edits.foam), reference: heights(edits.reference) },
    levels: derived?.levels ?? [],
    empty: derived?.empty ?? [],
    cannot: edits.cannot_judge,
    image: { top: z - layout.y0, rows: layout.rows, pieces },
  };
}

function marks() {
  const drag = state.drag;
  const grab = drag?.type === "grab"
    ? { t0: state.edits.times[drag.index] - state.width, t1: state.edits.times[drag.index] + state.width, kind: drag.kind }
    : null;
  return { playhead: state.playhead, selection: state.selection, grab };
}

// ---- drawing ------------------------------------------------------------------------------------

function requestDraw(parts) {
  pending = { back: pending.back || !!parts.back, lines: pending.lines || !!parts.lines, marks: pending.marks || !!parts.marks };
  if (frameRequested) return;
  frameRequested = true;
  requestAnimationFrame(draw);
}

function draw() {
  frameRequested = false;
  const parts = pending;
  pending = { back: false, lines: false, marks: false };
  if ($("editorView").hidden || !state.edits || !state.glassId) return;
  const began = performance.now();
  const data = panel();
  const view = state.view;
  const plots = [["graph", "graphBox", false], ["context", "contextBox", true]];
  for (const [id, box, halo] of plots) {
    const width = $(box).clientWidth, height = $(box).clientHeight;
    const svg = $(id);
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    const [back, line, mark] = svg.children;
    if (parts.back) back.innerHTML = id === "graph" ? render.graphBack(data, view, width, height, id) : render.contextBack(data, view, width, height, id);
    if (parts.back || parts.lines) line.innerHTML = render.linesSvg(data, view, width, height, id, { halo, hot: state.hot });
    if (parts.back || parts.marks) mark.innerHTML = render.marksSvg(marks(), view, width, height, id);
  }
  if (parts.back || parts.marks) {
    const width = $("axisBox").clientWidth;
    $("axis").setAttribute("viewBox", `0 0 ${width} 32`);
    $("axis").innerHTML = render.axisSvg(view, width, { times: state.edits.times, empty: data.empty, playhead: state.playhead });
    renderRangeNumbers();
  }
  if (parts.lines || parts.back) player.drawOverlay();
  if (state.drag && parts.lines && !parts.back) {
    state.redraws.push(performance.now() - began);
    if (state.redraws.length > 2000) state.redraws.shift();
  }
}

/** What the video shows over the picture: the Glass and each line's height at that time. */
function overlay(t) {
  if (!state.edits || !state.glassId) return "";
  const glass = recipeGlass(), e = glass.ellipse;
  const times = state.edits.times;
  const i = lines.nearestIndex(times, t);
  const near = Math.abs(times[i] - t) <= render.step(times);
  const parts = [
    `<ellipse cx="${e.center_x}" cy="${e.center_y}" rx="${e.radius_x}" ry="${e.radius_y}" style="fill:none;stroke:var(--glass-outline);stroke-width:1;stroke-dasharray:4 3" vector-effect="non-scaling-stroke"/>`,
  ];
  const chord = (y, style) => `<line x1="${e.center_x - e.radius_x - 12}" x2="${e.center_x + e.radius_x + 12}" y1="${y}" y2="${y}" style="${style}" vector-effect="non-scaling-stroke"/>`;
  parts.push(chord(glass.zero_line_y, "stroke:var(--glass-outline);stroke-width:1;stroke-dasharray:6 4"));
  const styles = { reference: "stroke:var(--reference);stroke-width:2;stroke-dasharray:6 4", foam: "stroke:var(--foam);stroke-width:2.5", oil: "stroke:var(--oil);stroke-width:2.5" };
  for (const kind of render.KINDS) {
    const y = near ? lineOf(state.glassId, kind).ys[i] : null;
    if (y !== null) parts.push(chord(y, "stroke:var(--line-halo);stroke-width:5"), chord(y, styles[kind]));
  }
  return parts.join("");
}

// ---- pointer --------------------------------------------------------------------------------------

function pointer(svg, event) {
  const box = svg.getBoundingClientRect();
  const s = render.scales(state.view, box.width, box.height);
  const x = event.clientX - box.left, y = event.clientY - box.top;
  return { x, y, t: s.tx(x), h: s.hy(y), s };
}

/** The line drawn within HIT_PX of the pointer, nearest first: { kind, index }, where index is the
 * sample of the grabbed piece nearest the pointer's time. */
function hitLine(at) {
  const times = state.edits.times;
  const [first, end] = lines.indexRange(times, at.s.tx(at.x - HIT_PX), at.s.tx(at.x + HIT_PX));
  const z = zero();
  const point = (ys, i) => [at.s.sx(times[i]), at.s.sy(z - ys[i])];
  let best = null;
  for (const kind of ["oil", "foam", "reference"]) {
    const ys = lineOf(state.glassId, kind).ys;
    for (let i = Math.max(0, first - 1); i < Math.min(times.length, end + 1); i++) {
      if (ys[i] === null) continue;
      const [x0, y0] = point(ys, i);
      let distance = Math.hypot(at.x - x0, at.y - y0);
      let index = i;
      if (i + 1 < times.length && ys[i + 1] !== null) {  // the segment to the next sample
        const [x1, y1] = point(ys, i + 1);
        const share = Math.min(1, Math.max(0, ((at.x - x0) * (x1 - x0) + (at.y - y0) * (y1 - y0)) / ((x1 - x0) ** 2 + (y1 - y0) ** 2 || 1)));
        const along = Math.hypot(at.x - (x0 + share * (x1 - x0)), at.y - (y0 + share * (y1 - y0)));
        if (along < distance) {
          distance = along;
          index = share < 0.5 ? i : i + 1;
        }
      }
      if (distance <= HIT_PX && (!best || distance < best.distance)) best = { kind, index, distance };
    }
  }
  return best;
}

function selectionEdge(at) {
  if (!state.selection) return null;
  for (const edge of ["t0", "t1"]) if (Math.abs(at.s.sx(state.selection[edge]) - at.x) <= EDGE_PX) return edge;
  return null;
}

/** The source y the pointer points at, settled on a nearby edge when the snap is on. */
function settle(index, y) {
  if (!state.snap) return y;
  return lines.snap(state.luma.get(state.glassId), index, y, layoutOf().y0);
}

function onPointerDown(event) {
  if (!state.edits || (event.button !== 0 && event.button !== 1)) return;
  const svg = event.currentTarget;
  const at = pointer(svg, event);
  svg.setPointerCapture(event.pointerId);
  const start = { svg, x: event.clientX, y: event.clientY, at, moved: false };
  if (event.button === 1 || event.shiftKey || state.tool === "pan") {
    state.drag = { ...start, type: "pan", view: { ...state.view } };
    return;
  }
  if (state.tool === "range") {
    const edge = selectionEdge(at);
    state.drag = edge ? { ...start, type: "edge", edge } : { ...start, type: "select" };
    return;
  }
  if (state.tool === "grab") {
    const hit = hitLine(at);
    if (!hit) {
      state.drag = { ...start, type: "click" };
      return;
    }
    const line = lineOf(state.glassId, hit.kind);
    state.drag = { ...start, type: "grab", kind: hit.kind, index: hit.index, base: lines.copyLine(line), y0: zero() - at.h };
    state.hot = hit.kind;
    setPlayhead(state.edits.times[hit.index]);
    requestDraw({ lines: true, marks: true });
    return;
  }
  if (state.tool === "pencil") {
    const line = lineOf(state.glassId, state.kind);
    const y = zero() - at.h;
    state.drag = { ...start, type: "pencil", kind: state.kind, base: lines.copyLine(line), last: { t: at.t, y } };
    lines.pencil(line, state.edits.times, at.t, y, at.t, y, settle);
    requestDraw({ lines: true });
  }
}

function onPointerMove(event) {
  const drag = state.drag;
  if (!drag) {
    hover(event);
    return;
  }
  const at = pointer(drag.svg, event);
  if (!drag.moved && Math.abs(event.clientX - drag.x) + Math.abs(event.clientY - drag.y) > DRAG_PX) drag.moved = true;
  if (drag.type === "pan" && drag.moved) {
    const dt = at.s.tx(0) - at.s.tx(event.clientX - drag.x);
    const dh = at.s.hy(0) - at.s.hy(event.clientY - drag.y);
    const v = drag.view;
    state.view = { t0: v.t0 + dt, t1: v.t1 + dt, h0: v.h0 + dh, h1: v.h1 + dh };
    requestDraw({ back: true });
  } else if (drag.type === "select" && drag.moved) {
    state.selection = { t0: Math.min(drag.at.t, at.t), t1: Math.max(drag.at.t, at.t) };
    renderSelection();
    requestDraw({ marks: true });
  } else if (drag.type === "edge") {
    state.selection = { ...state.selection, [drag.edge]: at.t };
    renderSelection();
    requestDraw({ marks: true });
  } else if (drag.type === "grab" && drag.moved) {
    const line = lineOf(state.glassId, drag.kind);
    const target = settle(drag.index, drag.base.ys[drag.index] + (zero() - at.h) - drag.y0);
    lines.grab(line, drag.base, state.edits.times, drag.index, target, state.width, event.altKey ? "pointed" : state.shape);
    requestDraw({ lines: true });
  } else if (drag.type === "pencil") {
    const line = lineOf(state.glassId, drag.kind);
    const y = zero() - at.h;
    lines.pencil(line, state.edits.times, drag.last.t, drag.last.y, at.t, y, settle);
    drag.last = { t: at.t, y };
    setPlayhead(Math.min(state.edits.times.at(-1), Math.max(state.edits.times[0], at.t)), true);
    requestDraw({ lines: true });
  }
}

function onPointerUp() {
  const drag = state.drag;
  state.drag = null;
  if (!drag) return;
  if ((drag.type === "click" || drag.type === "pan" || drag.type === "select") && !drag.moved) {
    setPlayhead(drag.at.t);
  } else if (drag.type === "edge" && state.selection) {
    const { t0, t1 } = state.selection;
    state.selection = { t0: Math.min(t0, t1), t1: Math.max(t0, t1) };
    renderSelection();
  } else if (drag.type === "grab" || drag.type === "pencil") {
    if (state.history.record(state.glassId, drag.kind, drag.base, lineOf(state.glassId, drag.kind))) changed();
  }
  requestDraw({ lines: true, marks: true });
}

function hover(event) {
  if (state.tool !== "grab" || !state.edits) return;
  const hit = hitLine(pointer(event.currentTarget, event));
  const hot = hit?.kind ?? null;
  event.currentTarget.style.cursor = hot ? "ns-resize" : "";
  if (hot !== state.hot) {
    state.hot = hot;
    requestDraw({ lines: true });
  }
}

function onWheel(event) {
  if (!state.edits) return;
  event.preventDefault();
  const at = pointer(event.currentTarget, event);
  const factor = Math.exp(event.deltaY * 0.0015);
  const v = state.view;
  const whole = render.fitView(panel());
  if (event.shiftKey) {
    const span = Math.min((whole.h1 - whole.h0) * 2, Math.max(MIN_SPAN_PX, (v.h1 - v.h0) * factor));
    const ratio = (at.h - v.h0) / (v.h1 - v.h0);
    state.view = { ...v, h0: at.h - ratio * span, h1: at.h - ratio * span + span };
  } else {
    const span = Math.min((whole.t1 - whole.t0) * 1.5, Math.max(MIN_SPAN_SEC, (v.t1 - v.t0) * factor));
    const ratio = (at.t - v.t0) / (v.t1 - v.t0);
    state.view = { ...v, t0: at.t - ratio * span, t1: at.t - ratio * span + span };
  }
  requestDraw({ back: true });
}

// ---- changes --------------------------------------------------------------------------------------

/** Unsaved edits: leaving the editor or closing the window asks first (Product SSOT §6). */
function setDirty(dirty) {
  if (state.dirty === dirty) return;
  state.dirty = dirty;
  api.call("POST", "/api/editor/unsaved", { unsaved: dirty }).catch(() => {});
}

function changed() {
  setDirty(true);
  renderHeader();
  derive();
}

/** Ask what follows from the lines now; one request at a time, the last change last. */
async function derive() {
  if (!state.edits) return;
  if (deriving) {
    deriveAgain = true;
    return;
  }
  const id = encodeURIComponent(state.detail.id);
  deriving = api.call("POST", `/api/inspections/${id}/edits/states`, { edits: state.edits });
  const result = await deriving;
  deriving = null;
  if (result.ok && state.edits) {
    takeDerived(result.data.glasses);
    renderGlassPanel();
    requestDraw({ back: true });
  } else if (!result.ok) {
    notify("editorNotice", result.data.error ?? `HTTP ${result.status}`, "error");
  }
  if (deriveAgain) {
    deriveAgain = false;
    if (state.edits) derive();
  }
}

function takeDerived(glasses) {
  for (const glass of glasses) state.derived.set(glass.glass_id, glass);
}

function undo(redo = false) {
  const entry = redo ? state.history.redo(lineOf) : state.history.undo(lineOf);
  if (!entry) return;
  if (entry.glassId !== state.glassId) {
    state.glassId = entry.glassId;
    $("editorGlass").value = entry.glassId;
    showGlass(false);
  }
  changed();
  requestDraw({ lines: true });
}

function eraseSelection() {
  if (!state.selection) return;
  const line = lineOf(state.glassId, "oil");
  const base = lines.copyLine(line);
  const [first, end] = lines.indexRange(state.edits.times, state.selection.t0, state.selection.t1);
  lines.erase(line, first, end);
  if (state.history.record(state.glassId, "oil", base, line)) changed();
  requestDraw({ lines: true });
}

/** Save the edits; whether they were saved. */
async function save() {
  if (!state.edits) return false;
  const id = encodeURIComponent(state.detail.id);
  const result = await api.call("POST", `/api/inspections/${id}/edits`, { edits: state.edits });
  if (!result.ok) {
    notify("editorNotice", result.data.error ?? `HTTP ${result.status}`, "error");
    return false;
  }
  state.savedAt = result.data.saved_at;
  setDirty(false);
  renderHeader();
  notify("editorNotice", "저장했습니다.");
  return true;
}

// ---- the playhead and the view --------------------------------------------------------------------

function setPlayhead(t, quiet = false) {
  state.playhead = t;
  if (!quiet || !player.isPlaying()) player.seek(t);
  requestDraw({ marks: true });
}

function onPlayerTime(t) {
  state.playhead = t;
  if (player.isPlaying() && (t < state.view.t0 || t > state.view.t1)) {  // keep the playhead in view
    const span = state.view.t1 - state.view.t0;
    state.view = { ...state.view, t0: t - span * 0.1, t1: t + span * 0.9 };
    requestDraw({ back: true });
  }
  requestDraw({ marks: true });
}

/** Move to the next (or previous) empty stretch of the Oil line. */
function jumpToEmpty(direction) {
  const runs = state.derived.get(state.glassId)?.empty ?? [];
  const times = state.edits.times;
  const now = state.playhead;
  const run = direction > 0
    ? runs.find((r) => times[r.first] > now + 1e-6)
    : [...runs].reverse().find((r) => times[r.first] < now - 1e-6);
  if (!run) {
    notify("editorNotice", direction > 0 ? "뒤에 빈 구간이 없습니다." : "앞에 빈 구간이 없습니다.");
    return;
  }
  const t0 = times[run.first], t1 = times[run.end - 1];
  const span = Math.max(state.view.t1 - state.view.t0, (t1 - t0) * 1.5);
  const middle = (t0 + t1) / 2;
  state.view = { ...state.view, t0: middle - span / 2, t1: middle + span / 2 };
  setPlayhead(t0);
  requestDraw({ back: true });
}

function renderRangeNumbers() {
  for (const [id, edge] of [["axisFrom", "t0"], ["axisTo", "t1"]]) {
    const input = $(id);
    if (document.activeElement !== input) input.value = clock(Math.max(0, state.view[edge]));
  }
}

function applyRangeNumber(input, edge) {
  const t = parseClock(input.value);
  const other = edge === "t0" ? state.view.t1 : state.view.t0;
  if (t !== null && (edge === "t0" ? other - t : t - other) >= MIN_SPAN_SEC) {
    state.view = { ...state.view, [edge]: t };
    requestDraw({ back: true });
  }
  renderRangeNumbers();
}

// ---- panels -----------------------------------------------------------------------------------------

function renderHeader() {
  const d = state.detail;
  if (!d) return;
  $("editorTitle").textContent = d.name ?? d.video.name;
  const saved = state.dirty ? "저장 안 함" : state.savedAt ? `저장함 ${localDate(state.savedAt).slice(11)}` : "초안 그대로";
  $("editorState").replaceChildren(el("span", { class: state.dirty ? "dirty" : "" }, saved), ` · ${d.video.name}`);
  const glasses = $("editorGlass");
  if ([...glasses.options].map((o) => o.value).join("\n") !== d.recipe.glasses.map((g) => g.id).join("\n")) {
    glasses.replaceChildren(...d.recipe.glasses.map((g) => el("option", { value: g.id }, g.name)));
  }
  glasses.value = state.glassId ?? "";
  const s = d.settings;
  const rows = [
    ["분석 범위", `${clock(s.start_sec)} – ${clock(s.end_sec)}`],
    ["압축기 기동", state.edits?.compressor_start_sec === null ? "없음" : clock(state.edits?.compressor_start_sec)],
    ["Recipe", `${d.recipe.name} (이 검사의 사본)`],
    ["샘플", `${state.analysis.times.length.toLocaleString()}개 (초당 2개)`],
    ["분석한 시각", localDate(state.analysis.finished_at)],
    ["원본 SHA-256", d.video.sha256 ?? "-"],
  ];
  $("editorFacts").replaceChildren(...rows.map(([k, v]) => el("tr", {}, el("th", {}, k), el("td", { class: k.includes("SHA") ? "mono" : "" }, v))));
}

function renderGlassPanel() {
  const glass = recipeGlass();
  const derived = state.derived.get(state.glassId);
  $("glassHead").textContent = `Glass · ${glass.name}`;
  $("glassMode").textContent = MODES[glass.judgment_rule.mode];
  if (!derived) return;
  const c = derived.coverage;
  const pct = (n) => `${((100 * n) / Math.max(1, c.total)).toFixed(1)} %`;
  const count = (runs) => (runs.length ? `${runs.length}곳` : "없음");
  const levels = (name) => count(derived.levels.filter((r) => r.state === name));
  const minimum = glass.judgment_rule.minimum_valid_coverage_ratio;
  const stretches = editsOf().cannot_judge.length;
  const rows = [
    ["빈 구간", derived.empty.length ? [el("span", { class: "empty-text" }, `${count(derived.empty)} · ${pct(c.empty)}`), " ", el("span", { class: "caption" }, "그리기 전까지 무효")] : ["없음"]],
    ["판단 불가", [stretches ? `${stretches}곳 · ${pct(c.cannot_judge)}` : "없음"]],
    ["유효 비율", [`${Math.floor(100 * c.valid_ratio)} %`, " ", el("span", { class: "caption" }, `(기준 ${Math.round(100 * minimum)} % 이상)`)]],
    ["FULL / EMPTY", [`FULL ${levels("FULL_NO_INTERFACE")} · EMPTY ${levels("EMPTY_NO_INTERFACE")}`, " ", el("span", { class: "caption" }, "(선 위치로 자동)")]],
  ];
  $("glassFacts").replaceChildren(...rows.map(([k, v]) => el("tr", {}, el("th", {}, k), el("td", {}, ...v))));
}

function renderTools() {
  for (const button of document.querySelectorAll("#editorView button[data-tool]")) {
    button.classList.toggle("on", button.dataset.tool === state.tool);
    button.setAttribute("aria-pressed", String(button.dataset.tool === state.tool));
  }
  for (const button of document.querySelectorAll("#lineKind button")) button.classList.toggle("on", button.dataset.kind === state.kind);
  for (const button of document.querySelectorAll("#grabShape button")) button.classList.toggle("on", button.dataset.shape === state.shape);
  const index = lines.GRAB_WIDTHS.indexOf(state.width);
  $("grabWidth").value = String(index);
  $("grabWidthText").textContent = `${state.width} s`;
  $("snapToggle").checked = state.snap;
  for (const id of ["graph", "context"]) $(id).dataset.mode = state.tool;  // its cursor
  renderSelection();
}

function renderSelection() {
  const box = $("selectionBox");
  box.hidden = state.tool !== "range" && !state.selection;
  const s = state.selection;
  $("selectionText").textContent = s ? `${clock(s.t0)} – ${clock(s.t1)} · ${(s.t1 - s.t0).toFixed(1)} s` : "없음";
  $("eraseSelection").disabled = !s;
}

function setTool(tool) {
  state.tool = tool;
  state.hot = null;
  for (const id of ["graph", "context"]) $(id).style.cursor = "";
  renderTools();
  requestDraw({ lines: true });
}

function stepWidth(direction) {
  const steps = lines.GRAB_WIDTHS;
  state.width = steps[Math.min(steps.length - 1, Math.max(0, steps.indexOf(state.width) + direction))];
  renderTools();
}

// ---- keys -----------------------------------------------------------------------------------------

function onKey(event) {
  if (!state.edits || typing()) return;
  const ctrl = event.ctrlKey || event.metaKey;
  if (ctrl && event.code === "KeyZ") {
    event.preventDefault();
    undo(event.shiftKey);
  } else if (ctrl && event.code === "KeyY") {
    event.preventDefault();
    undo(true);
  } else if (ctrl && event.code === "KeyS") {
    event.preventDefault();
    save();
  } else if (ctrl || event.altKey) {
    return;
  } else if (TOOL_KEYS[event.code]) {
    setTool(TOOL_KEYS[event.code]);
  } else if (event.code === "BracketLeft" || event.code === "BracketRight") {
    stepWidth(event.code === "BracketLeft" ? -1 : 1);
  } else if (event.code === "KeyS") {
    state.snap = !state.snap;
    renderTools();
  } else if (event.code === "KeyN") {
    jumpToEmpty(event.shiftKey ? -1 : 1);
  } else if (event.key === "Delete" || event.key === "Backspace") {
    eraseSelection();
  } else if (event.key === "Escape") {
    if (!$("videoSpeedMenu").hidden) player.toggleSpeedMenu(false);
    else {
      state.selection = null;
      renderSelection();
      requestDraw({ marks: true });
    }
  } else if (event.code === "Space") {
    event.preventDefault();
    player.toggle();
  } else if (event.code === "Comma" || event.code === "Period") {
    player.step(event.code === "Comma" ? -1 : 1);
  } else {
    return;
  }
  event.preventDefault();
}

/** Redraw times while dragging and exact-frame times, for the A5 and A6 measurement
 * (scripts/measure_editor.py). */
export function measurements() {
  return {
    redraws: state.redraws.slice(),
    seeks: player.seekStats(),
    samples: state.edits?.times.length ?? 0,
    lumaReady: !!state.luma.get(state.glassId),
    video: player.playbackInfo(),
  };
}

export function init(toList, openSetup) {
  backToList = toList;
  toSetup = openSetup;
  nav.register("editorView", { title: "편집", onKey });
  player.wire();
  $("editorBack").addEventListener("click", leave);
  $("sourceRecheck").addEventListener("click", () => checkSource().catch(() => {}));
  $("editorSave").addEventListener("click", save);
  $("editorReanalyse").addEventListener("click", reanalyse);
  $("editorUndo").addEventListener("click", () => undo(false));
  $("editorRedo").addEventListener("click", () => undo(true));
  $("editorGlass").addEventListener("change", () => {
    $("editorGlass").blur();  // the editor's keys again
    state.glassId = $("editorGlass").value;
    state.selection = null;
    renderSelection();
    showGlass(false);
  });
  for (const button of document.querySelectorAll("#editorView button[data-tool]")) {
    button.addEventListener("click", () => setTool(button.dataset.tool));
  }
  for (const button of document.querySelectorAll("#lineKind button")) {
    button.addEventListener("click", () => { state.kind = button.dataset.kind; renderTools(); });
  }
  for (const button of document.querySelectorAll("#grabShape button")) {
    button.addEventListener("click", () => { state.shape = button.dataset.shape; renderTools(); });
  }
  $("grabWidth").addEventListener("input", () => {
    state.width = lines.GRAB_WIDTHS[Number($("grabWidth").value)];
    renderTools();
  });
  $("snapToggle").addEventListener("change", () => { state.snap = $("snapToggle").checked; });
  $("backgroundToggle").addEventListener("change", () => {
    state.background = $("backgroundToggle").checked;
    if (state.edits) showGlass(false);
  });
  $("eraseSelection").addEventListener("click", eraseSelection);
  $("prevEmpty").addEventListener("click", () => jumpToEmpty(-1));
  $("nextEmpty").addEventListener("click", () => jumpToEmpty(1));
  for (const [id, edge] of [["axisFrom", "t0"], ["axisTo", "t1"]]) {
    const input = $(id);
    input.addEventListener("change", () => applyRangeNumber(input, edge));
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") input.blur();
      if (event.key === "Escape") {
        renderRangeNumbers();
        input.blur();
      }
    });
    input.addEventListener("blur", renderRangeNumbers);
  }
  for (const id of ["graph", "context"]) {
    const svg = $(id);
    svg.addEventListener("pointerdown", onPointerDown);
    svg.addEventListener("pointermove", onPointerMove);
    svg.addEventListener("pointerup", onPointerUp);
    svg.addEventListener("pointercancel", onPointerUp);
    svg.addEventListener("wheel", onWheel, { passive: false });
  }
  $("axis").addEventListener("pointerdown", (event) => {
    if (state.edits) setPlayhead(pointer($("axis"), event).t);
  });
  const observer = new ResizeObserver(() => requestDraw({ back: true }));
  for (const id of ["graphBox", "contextBox"]) observer.observe($(id));
  window.addEventListener("beforeunload", (event) => {
    if (state.dirty) event.preventDefault();
  });
}
