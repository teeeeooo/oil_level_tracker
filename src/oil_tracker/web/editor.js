// The editor (DESIGN.md §5 "Editor window"; Product SSOT §4 and §6). It holds the edits, turns the
// pointer and keys into line operations (lines.js) and draws through render.js. What follows from
// the lines (FULL/EMPTY, the empty stretches, the coverage) comes from the API after each change.
import * as api from "./api.js";
import * as lines from "./lines.js";
import * as nav from "./nav.js";
import * as player from "./player.js";
import * as render from "./render.js";
import { $, MODES, clock, el, localDate, notify, parseClock, typing } from "./ui.js";

const TOOL_KEYS = { KeyG: "grab", KeyP: "pencil", KeyL: "point", KeyR: "range", KeyM: "memo", KeyH: "pan" };
const KIND_NAMES = { oil: "Oil", foam: "Foam", reference: "참조" };
const VERDICTS = { PASS: ["합격", "pass"], FAIL: ["불합격", "fail"], REVIEW: ["검토 필요", "review"] };  // text, badge
const HIT_PX = 8;          // how near a line a press grabs it
const EDGE_PX = 5;         // how near a selection edge or the compressor marker a press moves it
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
  changes: 0,              // counts the changes, so a save knows whether more came while it ran
  derived: new Map(),      // glass id -> what follows from its lines (API)
  glassId: null,
  tool: "grab",
  kind: "oil",             // the line the pencil and the point line draw
  width: 30,               // the grab width, seconds
  shape: "smooth",
  snap: true,
  lock: false,             // the pencil draws only level or upright strokes (user, 2026-10-30)
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
  memo: null,              // the memo in the dialog: { glassId, id or null for a new one, time, y }; set on open
  point: null,             // the point line in progress (see "the point line" below)
};
let backToList = () => {};
let toSetup = () => {};
let pending = { back: false, lines: false, marks: false };
let frameRequested = false;
let deriving = null;       // the states request in flight
let deriveAgain = false;
let unsavedSent = Promise.resolve();  // the window's flag goes out in order (setDirty)
let previewing = false;    // the point line's preview request in flight
let previewAgain = false;

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
  if ($("memoDialog").open) $("memoDialog").close();
  Object.assign(state, { detail: null, analysis: null, edits: null, selection: null, drag: null, hot: null, memo: null, point: null });
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
  renderMemos();
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
    compressor: state.drag?.type === "compressor" ? null : state.edits.compressor_start_sec,  // in the marks meanwhile
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
  const compressor = drag?.type === "compressor" ? drag.time : null;
  return { playhead: state.playhead, selection: state.selection, grab, compressor, memos: memoMarks(), point: pointMarks() };
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
  state.view = inRange(state.view);
  const data = panel();
  const view = state.view;
  const plots = [["graph", "graphBox", false], ["context", "contextBox", true]];
  const shown = parts.back || parts.marks ? marks() : null;
  for (const [id, box, halo] of plots) {
    const width = $(box).clientWidth, height = $(box).clientHeight;
    const svg = $(id);
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    const [back, line, mark] = svg.children;
    if (parts.back) back.innerHTML = id === "graph" ? render.graphBack(data, view, width, height, id) : render.contextBack(data, view, width, height, id);
    if (parts.back || parts.lines) line.innerHTML = render.linesSvg(data, view, width, height, id, { halo, hot: state.hot });
    if (shown) mark.innerHTML = render.marksSvg(id === "graph" ? shown : { ...shown, memos: [] }, view, width, height, id);  // pins on the graph
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

function nearCompressor(at) {
  const t = state.edits.compressor_start_sec;
  return t !== null && Math.abs(at.s.sx(t) - at.x) <= EDGE_PX;
}

/** A compressor start the pointer can put: in 0.1 s steps, inside the analysis range. */
function compressorAt(t) {
  const s = state.detail.settings;
  return Math.round(Math.min(s.end_sec, Math.max(s.start_sec, t)) * 10) / 10;
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
  if (state.tool === "point") {
    if (event.button === 0) addPoint(at);
    return;
  }
  if (state.tool === "memo") {
    state.drag = { ...start, type: "memo" };
    return;
  }
  if (state.tool === "range") {
    const edge = selectionEdge(at);
    state.drag = edge ? { ...start, type: "edge", edge } : { ...start, type: "select" };
    return;
  }
  if (state.tool === "grab") {
    const hit = hitLine(at);
    if (!hit && nearCompressor(at)) {  // a line under the pointer comes first
      state.drag = { ...start, type: "compressor", time: state.edits.compressor_start_sec };
      requestDraw({ back: true, marks: true });
      return;
    }
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
    const [first] = lines.pencil(line, state.edits.times, at.t, y, at.t, y, settle);
    if (state.lock) Object.assign(state.drag, { anchor: { t: at.t, y: line.ys[first] }, touched: [first, first + 1] });
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
  } else if (drag.type === "compressor" && drag.moved) {
    drag.time = compressorAt(at.t);
    requestDraw({ marks: true });
  } else if (drag.type === "grab" && drag.moved) {
    const line = lineOf(state.glassId, drag.kind);
    const target = settle(drag.index, drag.base.ys[drag.index] + (zero() - at.h) - drag.y0);
    lines.grab(line, drag.base, state.edits.times, drag.index, target, state.width, event.altKey ? "pointed" : state.shape);
    requestDraw({ lines: true });
  } else if (drag.type === "pencil" && drag.anchor) {
    lockedStroke(drag, at, event);
    setPlayhead(Math.min(state.edits.times.at(-1), Math.max(state.edits.times[0], at.t)), true);
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

/** The pencil with "수평·수직" on, like Shift in Paint: from the press, a level stroke at the pressed
 * height when the pointer has moved more across than up or down, else an upright one from the pressed
 * height to the pointer's. Each move redraws the stroke from the line as it was. */
function lockedStroke(drag, at, event) {
  const line = lineOf(state.glassId, drag.kind);
  const [from, to] = drag.touched;
  for (let i = from; i < to; i++) {
    line.ys[i] = drag.base.ys[i];
    line.origins[i] = drag.base.origins[i];
  }
  const { t, y } = drag.anchor;
  const level = Math.abs(event.clientX - drag.x) >= Math.abs(event.clientY - drag.y);
  drag.touched = level
    ? lines.pencil(line, state.edits.times, t, y, at.t, y)
    : lines.upright(line, state.edits.times, t, y, zero() - at.h);
}

function onPointerUp() {
  const drag = state.drag;
  state.drag = null;
  if (!drag) return;
  if (["click", "pan", "select", "compressor", "memo"].includes(drag.type) && !drag.moved) {
    setPlayhead(drag.at.t);
  }
  if (drag.type === "memo" && !drag.moved) {
    const id = drag.svg.id === "graph" ? hitMemo(drag.at) : null;
    openMemo(id, drag.at.t, zero() - drag.at.h);
  }
  if (drag.type === "compressor") {
    if (drag.moved && state.history.recordCompressor(state.edits.compressor_start_sec, drag.time)) {
      state.edits.compressor_start_sec = drag.time;
      changed();
    }
    requestDraw({ back: true });
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
  if (state.tool === "point" && state.edits) {
    previewTo(pointer(event.currentTarget, event));
    return;
  }
  if (state.tool === "memo" && state.edits) {
    const over = event.currentTarget.id === "graph" && hitMemo(pointer(event.currentTarget, event));
    event.currentTarget.style.cursor = over ? "pointer" : "";
    return;
  }
  if (state.tool !== "grab" || !state.edits) return;
  const at = pointer(event.currentTarget, event);
  const hit = hitLine(at);
  const hot = hit?.kind ?? null;
  event.currentTarget.style.cursor = hot ? "ns-resize" : nearCompressor(at) ? "ew-resize" : "";
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
    const span = Math.min(whole.t1 - whole.t0, Math.max(MIN_SPAN_SEC, (v.t1 - v.t0) * factor));
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
  tellWindow(dirty);
}

/** One call at a time: two in flight could arrive swapped and leave the window's flag wrong. */
function tellWindow(unsaved) {
  unsavedSent = unsavedSent.then(() => api.call("POST", "/api/editor/unsaved", { unsaved })).catch(() => {});
}

function changed() {
  state.changes += 1;
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
  const target = {
    lineOf,
    setList: (glassId, kind, list) => { editsOf(glassId)[kind] = list; },
    setCompressor: (time) => { state.edits.compressor_start_sec = time; },
  };
  const entry = redo ? state.history.redo(target) : state.history.undo(target);
  if (!entry) return;
  if (entry.glassId !== null && entry.glassId !== state.glassId) {
    state.glassId = entry.glassId;
    $("editorGlass").value = entry.glassId;
    showGlass(false);
  }
  changed();
  const layer = { cannot_judge: { back: true }, compressor: { back: true }, memos: { marks: true } }[entry.kind];
  requestDraw(layer ?? { lines: true });
  renderSelection();
  renderMemos();
}

/** Delete: empty the line chosen in "그릴 선" over the selected range (user, 2026-10-30; before, the
 * Oil line only). */
function eraseSelection() {
  if (!state.selection) return;
  const line = lineOf(state.glassId, state.kind);
  const base = lines.copyLine(line);
  const [first, end] = lines.indexRange(state.edits.times, state.selection.t0, state.selection.t1);
  lines.erase(line, first, end);
  if (state.history.record(state.glassId, state.kind, base, line)) changed();
  requestDraw({ lines: true });
}

/** U: mark the selected range "cannot judge" (Product SSOT §4); or take the mark off it. The lines
 * stay as they are: those samples count neither as valid nor as empty. */
function judgeSelection(cannot) {
  const s = state.selection;
  if (!s || s.t1 <= s.t0) return;
  const [first, end] = lines.indexRange(state.edits.times, s.t0, s.t1);
  if (cannot && first === end) return;  // no sample in it
  const glass = editsOf();
  const before = glass.cannot_judge;
  const after = cannot ? lines.markStretch(before, s.t0, s.t1) : lines.clearStretch(before, s.t0, s.t1);
  if (!state.history.recordList(state.glassId, "cannot_judge", before, after)) return;
  glass.cannot_judge = after;
  changed();
  requestDraw({ back: true });
  renderSelection();
}

// ---- the point line -------------------------------------------------------------------------------
// Points clicked on the context image or the graph (Product SSOT §6) are joined along the edges
// between them by the API (architecture.md); Enter writes the path into the chosen line. state.point
// while points are placed: { glassId, kind, points: [{ index, y }] in time order, order: [index] in
// the order placed (Backspace), path: { first, ys } or null, tracing: its request, cursor:
// { index, y } or null, preview: { first, ys } or null }, y in source px.

/** The sample and source y the pointer points at, settled on a nearby edge when the snap is on. */
function pointAt(at) {
  const index = lines.nearestIndex(state.edits.times, at.t);
  return { index, y: settle(index, zero() - at.h) };
}

/** The points a point at `index` would join: its neighbours in time, without one at that time. */
function neighbours(points, index) {
  const before = points.filter((p) => p.index < index).at(-1);
  const after = points.find((p) => p.index > index);
  return [before, after].filter(Boolean);
}

function addPoint(at) {
  if (!state.point || state.point.glassId !== state.glassId) {
    state.point = { glassId: state.glassId, kind: state.kind, points: [], order: [], path: null, tracing: null, cursor: null, preview: null };
  }
  const point = state.point;
  const added = pointAt(at);
  point.points = [...point.points.filter((p) => p.index !== added.index), added].sort((a, b) => a.index - b.index);
  point.order = [...point.order.filter((i) => i !== added.index), added.index];
  point.cursor = null;
  point.preview = null;
  tracePoints();
}

function removeLastPoint() {
  const point = state.point;
  const index = point.order.pop();
  point.points = point.points.filter((p) => p.index !== index);
  point.preview = null;
  tracePoints();
}

function cancelPoint() {
  state.point = null;
  renderPointBox();
  requestDraw({ marks: true });
}

/** Ask for the path through the points; an answer to an older request is dropped. */
function tracePoints() {
  const point = state.point;
  point.path = null;
  point.tracing = null;
  if (point.points.length >= 2) {
    const tracing = askPath(point.glassId, point.points).then((path) => {
      if (state.point === point && point.tracing === tracing && path) {
        point.path = path;
        requestDraw({ marks: true });
      }
    });
    point.tracing = tracing;
  }
  renderPointBox();
  requestDraw({ marks: true });
}

/** The path through `points`: { first, ys }, or null after an error (told unless quiet). Along the
 * edges from the API with the snap on; straight with it off (user, 2026-10-30). */
async function askPath(glassId, points, quiet = false) {
  if (!state.snap) return lines.straight(state.edits.times, points);
  const id = encodeURIComponent(state.detail.id);
  const body = { glass_id: glassId, points: points.map((p) => ({ index: p.index, y: p.y })) };
  const result = await api.call("POST", `/api/inspections/${id}/point-line`, body);
  if (result.ok) return result.data;
  if (!quiet) notify("editorNotice", result.data.error ?? `HTTP ${result.status}`, "error");
  return null;
}

/** The preview: the path a click here would add, between the neighbouring points. */
function previewTo(at) {
  const point = state.point;
  if (!point || point.glassId !== state.glassId || !point.points.length) return;
  point.cursor = pointAt(at);
  point.preview = null;
  requestDraw({ marks: true });
  askPreview();
}

/** One preview request at a time, for the pointer's latest place. */
async function askPreview() {
  if (previewing) {
    previewAgain = true;
    return;
  }
  const point = state.point, cursor = point?.cursor;
  if (!cursor) return;
  previewing = true;
  const joined = [...neighbours(point.points, cursor.index), cursor].sort((a, b) => a.index - b.index);
  const path = await askPath(point.glassId, joined, true);
  previewing = false;
  if (path && state.point === point && point.cursor === cursor) {
    point.preview = path;
    requestDraw({ marks: true });
  }
  if (previewAgain) {
    previewAgain = false;
    askPreview();
  }
}

function leavePlot() {
  if (!state.point?.cursor) return;
  state.point.cursor = null;
  state.point.preview = null;
  requestDraw({ marks: true });
}

/** Enter: the path becomes the chosen line from the first point to the last, as one change. */
async function commitPoint() {
  const point = state.point;
  if (point.points.length < 2) {
    notify("editorNotice", "점을 두 개 이상 찍어야 이을 수 있습니다.");
    return;
  }
  while (state.point === point && !point.path && point.tracing) {
    const tracing = point.tracing;
    await tracing;
    if (point.tracing === tracing) break;  // it answered, or failed, and no newer request was made
  }
  if (state.point !== point || !point.path || !state.edits) return;
  const line = lineOf(point.glassId, point.kind);
  const base = lines.copyLine(line);
  lines.place(line, point.path.first, point.path.ys);
  state.point = null;
  if (state.history.record(point.glassId, point.kind, base, line)) changed();
  renderPointBox();
  requestDraw({ lines: true, marks: true });
}

/** What the marks draw of the point line, in the plots' heights. */
function pointMarks() {
  const point = state.point;
  if (!point || point.glassId !== state.glassId) return null;
  const times = state.edits.times, z = zero();
  const at = (p) => ({ t: times[p.index], h: z - p.y });
  const piece = (path) => path && { times: times.slice(path.first, path.first + path.ys.length), hs: path.ys.map((y) => z - y) };
  const guides = [];
  if (!point.path) for (let k = 1; k < point.points.length; k++) guides.push([at(point.points[k - 1]), at(point.points[k])]);
  if (point.cursor && !point.preview) {
    for (const p of neighbours(point.points, point.cursor.index)) guides.push([at(p), at(point.cursor)]);
  }
  return { kind: point.kind, points: point.points.map(at), path: piece(point.path), preview: piece(point.preview), guides };
}

function renderPointBox() {
  $("pointBox").hidden = state.tool !== "point";
  const point = state.point;
  $("pointText").textContent = `점 ${point?.points.length ?? 0}개 · ${KIND_NAMES[point?.kind ?? state.kind]}`;
}

// ---- memos ----------------------------------------------------------------------------------------

/** The Glass's memos in time order: the order of their numbers. */
function memoList() {
  return [...editsOf().memos].sort((a, b) => a.time_sec - b.time_sec);
}

/** The pins to draw: { n, t, h, id }, h in the graph's heights (null for a memo on a time alone). */
function memoMarks() {
  const z = zero();
  return memoList().map((m, k) => ({ n: k + 1, t: m.time_sec, h: m.y === null ? null : z - m.y, id: m.id }));
}

/** The memo whose pin is under the pointer on the graph, or null. */
function hitMemo(at) {
  for (const memo of memoMarks().reverse()) {  // the last drawn lies on top
    const pin = render.memoPinAt(memo, at.s);
    if (Math.hypot(at.x - pin.x, at.y - pin.y) <= pin.r + 2) return memo.id;
  }
  return null;
}

/** The memo dialog, for memo `id` or for a new one at (t, source y). */
function openMemo(id, t = null, y = null) {
  const memos = memoList();
  const k = memos.findIndex((m) => m.id === id);
  const memo = k >= 0 ? memos[k] : null;
  const times = state.edits.times;
  const time = memo ? memo.time_sec : Math.round(Math.min(times.at(-1), Math.max(times[0], t)) * 10) / 10;
  state.memo = { glassId: state.glassId, id: memo?.id ?? null, time, y: memo ? memo.y : Math.round(y * 10) / 10 };
  if (player.isPlaying()) player.stop();
  $("memoTitle").textContent = memo ? `메모 ${k + 1} · ${clock(time)}` : `새 메모 · ${clock(time)}`;
  $("memoText").value = memo?.text ?? "";
  $("memoDelete").hidden = !memo;
  renderMemoDialog();
  $("memoDialog").showModal();
  $("memoText").focus();
}

function renderMemoDialog() {
  const text = $("memoText").value;
  $("memoLength").textContent = `${text.length} / ${$("memoText").maxLength}`;
  $("memoSave").disabled = !text.trim();
}

/** Add, change or delete the memo in the dialog; an undoable change of the Glass's memos. */
function commitMemo(remove) {
  const target = state.memo;
  const text = $("memoText").value.trim();
  state.memo = null;
  $("memoDialog").close();
  if (!target || !state.edits || (!remove && !text)) return;
  const glass = editsOf(target.glassId);
  const before = glass.memos;
  let after;
  if (remove) after = before.filter((m) => m.id !== target.id);
  else if (target.id) after = before.map((m) => (m.id === target.id ? { ...m, text } : m));
  else after = [...before, { id: crypto.randomUUID(), time_sec: target.time, y: target.y, text }];
  if (!state.history.recordList(target.glassId, "memos", before, after)) return;
  glass.memos = after;
  changed();
  renderMemos();
  requestDraw({ marks: true });
}

function renderMemos() {
  if (!state.edits) return;
  const memos = memoList();
  const items = memos.map((m, k) => el("button", {
    class: "memo",
    onclick: () => {
      reveal(m.time_sec);
      setPlayhead(m.time_sec);
      openMemo(m.id);
    },
  }, el("span", { class: "pin" }, String(k + 1)), el("span", {}, el("span", { class: "t" }, clock(m.time_sec)), el("span", { class: "text" }, m.text))));
  $("memoItems").replaceChildren(...(items.length ? items : [el("span", { class: "caption" }, "메모 없음")]));
}

/** The view with its times inside the analysed range: no time before the first sample or after the
 * last (user, 2026-10-30), at most the whole range wide. The heights are left as they are. */
function inRange(view) {
  const whole = render.fitView({ times: state.edits.times });
  const span = Math.min(view.t1 - view.t0, whole.t1 - whole.t0);
  const t0 = Math.min(Math.max(view.t0, whole.t0), whole.t1 - span);
  return { ...view, t0, t1: t0 + span };
}

/** "전체 보기" (user, 2026-10-30): the whole time range and the Glass's height again. */
function fitWhole() {
  if (!state.edits) return;
  state.view = render.fitView(panel());
  requestDraw({ back: true });
}

/** Bring time t into view, keeping the zoom. */
function reveal(t) {
  const v = state.view;
  if (t >= v.t0 && t <= v.t1) return;
  const span = v.t1 - v.t0;
  state.view = { ...v, t0: t - span / 2, t1: t + span / 2 };
  requestDraw({ back: true });
}

/** Save the edits; whether they were saved. */
async function save() {
  if (!state.edits) return false;
  const id = encodeURIComponent(state.detail.id);
  const sent = state.changes;
  const result = await api.call("POST", `/api/inspections/${id}/edits`, { edits: state.edits });
  if (!result.ok) {
    notify("editorNotice", result.data.error ?? `HTTP ${result.status}`, "error");
    return false;
  }
  state.savedAt = result.data.saved_at;
  setDirty(state.changes !== sent);  // a change made while the save ran is not in it
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
  const view = inRange(state.view);  // the other edge as shown
  const other = edge === "t0" ? view.t1 : view.t0;
  if (t !== null && (edge === "t0" ? other - t : t - other) >= MIN_SPAN_SEC) {
    state.view = inRange({ ...view, [edge]: t });
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
    ["압축기 기동", compressorText()],
    ["Recipe", `${d.recipe.name} (이 검사의 사본)`],
    ["샘플", `${state.analysis.times.length.toLocaleString()}개 (초당 2개)`],
    ["분석한 시각", localDate(state.analysis.finished_at)],
    ["원본 SHA-256", d.video.sha256 ?? "-"],
  ];
  $("editorFacts").replaceChildren(...rows.map(([k, v]) => el("tr", {}, el("th", {}, k), el("td", { class: k.includes("SHA") ? "mono" : "" }, v))));
}

function compressorText() {
  const t = state.edits?.compressor_start_sec ?? null, set = state.detail.settings.compressor_start_sec;
  if (t === null) return "없음";
  return t === set ? clock(t) : `${clock(t)} (설정 ${clock(set)}에서 옮김)`;
}

// ---- the judgment (Product SSOT §3 and §5; DESIGN.md §5) -------------------------------------------
// The API computes each Glass's judgment with its states. The user's decision lives in the edits:
// their own verdict with a reason, and the check that submitting needs.

/** A change to what a judgment reads takes the check off: that Glass's Oil line or "cannot judge"
 * stretches, or the compressor start for every Glass (user, 2026-10-30). Foam, reference lines and
 * memos leave it. */
function takeCheckOff(entry) {
  const glasses = entry.kind === "compressor" ? state.edits.glasses
    : ["oil", "cannot_judge"].includes(entry.kind) ? [editsOf(entry.glassId)] : [];
  for (const glass of glasses) glass.decision.checked_at = null;
}

function decide(change) {
  Object.assign(editsOf().decision, change);
  changed();
  renderJudgment();
}

function setOverride(value) {
  const decision = editsOf().decision;
  if ((decision.override ?? "") === value) return;
  decide({ override: value || null, checked_at: null });  // another verdict: check it again
  if (value) $("overrideReason").focus();
}

function checkGlass() {
  const decision = editsOf().decision;
  if (decision.override && !decision.reason.trim()) {
    notify("editorNotice", "직접 판정한 Glass는 이유를 써야 확인할 수 있습니다.", "error");
    $("overrideReason").focus();
    return;
  }
  decide({ checked_at: new Date().toISOString() });
}

function renderJudgment() {
  if (!state.edits) return;
  const glass = recipeGlass(), rule = glass.judgment_rule, decision = editsOf().decision;
  const judgment = state.derived.get(state.glassId)?.judgment;
  $("judgmentHead").textContent = `판정 · ${glass.name}`;
  $("judgmentMode").textContent = MODES[rule.mode];
  for (const button of document.querySelectorAll("#overrideKind button")) {
    button.classList.toggle("on", button.dataset.override === (decision.override ?? ""));
  }
  $("reasonBox").hidden = !decision.override;
  if (document.activeElement !== $("overrideReason")) $("overrideReason").value = decision.reason;
  $("checkRow").hidden = Boolean(decision.checked_at);
  $("checkedRow").hidden = !decision.checked_at;
  $("checkedText").textContent = decision.checked_at ? `✓ 확인함 ${localDate(decision.checked_at).slice(11)}` : "";
  const left = state.edits.glasses.filter((g) => !g.decision.checked_at).map((g) => recipeGlass(g.glass_id).name);
  $("checkLeft").textContent = left.length ? `남은 Glass: ${left.join(", ")}` : "";
  renderGlassPicker();
  if (!judgment) return;
  const [text, tone] = VERDICTS[judgment.verdict];
  $("verdictBadge").textContent = text;
  $("verdictBadge").className = `badge big ${tone}`;
  $("verdictNote").textContent = decision.override ? `직접 판정 · 자동 판정은 ${VERDICTS[judgment.computed][0]}` : "자동 판정";
  $("judgmentReason").textContent = judgment.reason;
  const times = state.edits.times, s = (v) => `${Number(v.toFixed(1))} s`;
  const caption = (t) => el("span", { class: "caption" }, t);
  const cover = state.derived.get(state.glassId).coverage;
  const rows = [["압축기 기동", [compressorText()]]];
  if (rule.mode === "RECOVERY") {
    const r = judgment.recovery;
    rows.push(["0선 회복", r ? [clock(times[r.index]), " ", caption(`기동 후 ${s(r.after_sec)} (한도 ${s(rule.recovery_limit_sec)})`)] : ["없음"]]);
    rows.push(["회복 뒤 유지", [caption(`기준 ${s(rule.stable_hold_sec)} 이상`)]]);
  } else {
    const v = judgment.violation;
    rows.push(["가장 긴 위반", v
      ? [s(v.seconds), " ", caption(`(허용 ${s(rule.allowed_sec)}) ${clock(times[v.first])}–${clock(times[v.end - 1] + 0.5)} · 최대 ${v.worst_px.toFixed(1)} px`)]
      : ["없음"]]);
    rows.push(["허용 높이", [`${rule.allowed_px} px`]]);
  }
  rows.push(["유효 비율", [`${Math.floor(100 * cover.valid_ratio)} %`, " ", caption(`(기준 ${Math.round(100 * rule.minimum_valid_coverage_ratio)} % 이상)`)]]);
  $("judgmentFacts").replaceChildren(...rows.map(([k, v]) => el("tr", {}, el("th", {}, k), el("td", {}, ...v))));
}

/** Each Glass in the picker with its state: "확인 전" until checked, then its final judgment. */
function renderGlassPicker() {
  const picker = $("editorGlass");
  for (const option of picker.options) {
    const decision = state.edits.glasses.find((g) => g.glass_id === option.value)?.decision;
    const verdict = state.derived.get(option.value)?.judgment?.verdict;
    const status = decision?.checked_at && verdict ? VERDICTS[verdict][0] : "확인 전";
    option.textContent = `${recipeGlass(option.value).name} · ${status}`;
  }
  const left = state.edits.glasses.filter((g) => !g.decision.checked_at).map((g) => recipeGlass(g.glass_id).name);
  $("editorSubmit").title = left.length
    ? `모든 Glass를 확인해야 제출할 수 있습니다 (남은 Glass: ${left.join(", ")})`
    : "제출은 다음 단계에서 만듭니다";
}

function renderGlassPanel() {
  renderJudgment();
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
  const origins = editsOf().oil.origins;
  const edited = origins.filter((o) => o === "EDITED").length, drawn = origins.filter((o) => o === "DRAWN").length;
  const rows = [
    ["편집 기록", [`초안 고침 ${edited.toLocaleString()} · 직접 그림 ${drawn.toLocaleString()} 샘플`, " ", el("span", { class: "caption" }, `(전체 ${origins.length.toLocaleString()})`)]],
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
  $("lockToggle").checked = state.lock;
  for (const id of ["graph", "context"]) $(id).dataset.mode = state.tool;  // its cursor
  renderSelection();
  renderPointBox();
}

function renderSelection() {
  const box = $("selectionBox");
  box.hidden = state.tool !== "range" && !state.selection;
  const s = state.selection;
  $("selectionText").textContent = s ? `${clock(s.t0)} – ${clock(s.t1)} · ${(s.t1 - s.t0).toFixed(1)} s` : "없음";
  $("eraseSelection").disabled = !s;
  $("eraseKind").textContent = KIND_NAMES[state.kind];
  $("markSelection").disabled = !s;
  const marked = state.edits ? editsOf()?.cannot_judge ?? [] : [];
  $("clearSelection").disabled = !s || !marked.some((c) => c.end_sec > s.t0 && c.start_sec < s.t1);
}

function setTool(tool) {
  if (tool !== "point" && state.point) cancelPoint();
  if (tool !== "range") state.selection = null;  // another tool lets the range go (user, 2026-10-30)
  state.tool = tool;
  state.hot = null;
  for (const id of ["graph", "context"]) $(id).style.cursor = "";
  renderTools();
  requestDraw({ lines: true, marks: true });
}

/** The snap also decides how the point line joins its points, so a point line in progress is joined
 * again. */
function setSnap(on) {
  state.snap = on;
  if (state.point) {
    state.point.preview = null;
    tracePoints();
  }
  renderTools();
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
    setSnap(!state.snap);
  } else if (event.code === "KeyN") {
    jumpToEmpty(event.shiftKey ? -1 : 1);
  } else if (state.point && event.key === "Enter") {
    commitPoint();
  } else if (state.point && event.key === "Backspace") {
    removeLastPoint();
  } else if (event.key === "Delete" || event.key === "Backspace") {
    eraseSelection();
  } else if (event.code === "KeyU") {
    judgeSelection(true);
  } else if (event.key === "Escape") {
    if (!$("videoSpeedMenu").hidden) player.toggleSpeedMenu(false);
    else if (state.point) cancelPoint();
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
  tellWindow(false);  // a reloaded page holds no edits
  nav.register("editorView", { title: "편집", onKey });
  player.wire();
  $("editorBack").addEventListener("click", leave);
  $("sourceRecheck").addEventListener("click", () => checkSource().catch(() => {}));
  $("editorSave").addEventListener("click", save);
  $("editorReanalyse").addEventListener("click", reanalyse);
  $("markSelection").addEventListener("click", () => judgeSelection(true));
  $("memoText").addEventListener("input", renderMemoDialog);
  $("memoText").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey) && !$("memoSave").disabled) commitMemo(false);
  });
  $("memoSave").addEventListener("click", () => commitMemo(false));
  $("memoDelete").addEventListener("click", () => commitMemo(true));
  // openMemo sets the dialog's memo; nothing clears it on the "close" event, which comes a task
  // later and could clear a memo opened meanwhile
  $("memoCancel").addEventListener("click", () => $("memoDialog").close());
  $("clearSelection").addEventListener("click", () => judgeSelection(false));
  $("editorUndo").addEventListener("click", () => undo(false));
  $("editorRedo").addEventListener("click", () => undo(true));
  $("editorGlass").addEventListener("change", () => {
    $("editorGlass").blur();  // the editor's keys again
    state.glassId = $("editorGlass").value;
    state.selection = null;
    if (state.point) cancelPoint();
    renderSelection();
    showGlass(false);
  });
  for (const button of document.querySelectorAll("#editorView button[data-tool]")) {
    button.addEventListener("click", () => setTool(button.dataset.tool));
  }
  for (const button of document.querySelectorAll("#lineKind button")) {
    button.addEventListener("click", () => {
      state.kind = button.dataset.kind;
      if (state.point) state.point.kind = state.kind;  // the line the points will draw
      renderTools();
      requestDraw({ marks: true });
    });
  }
  for (const button of document.querySelectorAll("#grabShape button")) {
    button.addEventListener("click", () => { state.shape = button.dataset.shape; renderTools(); });
  }
  $("grabWidth").addEventListener("input", () => {
    state.width = lines.GRAB_WIDTHS[Number($("grabWidth").value)];
    renderTools();
  });
  $("snapToggle").addEventListener("change", () => setSnap($("snapToggle").checked));
  $("lockToggle").addEventListener("change", () => { state.lock = $("lockToggle").checked; });
  $("backgroundToggle").addEventListener("change", () => {
    state.background = $("backgroundToggle").checked;
    if (state.edits) showGlass(false);
  });
  $("eraseSelection").addEventListener("click", eraseSelection);
  for (const button of document.querySelectorAll("#overrideKind button")) {
    button.addEventListener("click", () => setOverride(button.dataset.override));
  }
  $("overrideReason").addEventListener("input", () => {
    const reason = $("overrideReason").value, decision = editsOf().decision;
    decide({ reason, checked_at: decision.override && !reason.trim() ? null : decision.checked_at });
  });
  $("checkGlass").addEventListener("click", checkGlass);
  $("uncheckGlass").addEventListener("click", () => decide({ checked_at: null }));
  state.history.listener = takeCheckOff;
  $("fitWhole").addEventListener("click", fitWhole);
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
    svg.addEventListener("pointerleave", leavePlot);
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
