// Recipe list and Recipe screen (DESIGN.md §4–§5, Product SSOT §3 and §5).
// Every rule check runs in Python through /api/recipes/check; this file only edits and draws.
import * as api from "./api.js";

const $ = (id) => document.getElementById(id);
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const MODES = {
  RECOVERY: "기준점 회복",
  HOLD_BELOW_ZERO: "기준점 아래 유지",
  HOLD_ABOVE_ZERO: "기준점 위 유지",
};
const MODE_FIELDS = {
  RECOVERY: [["recovery_limit_sec", "회복 제한 시간", "s"], ["stable_hold_sec", "안정 유지 시간", "s"]],
  HOLD_BELOW_ZERO: [["allowed_sec", "허용 시간", "s"], ["allowed_px", "허용 높이", "px"]],
  HOLD_ABOVE_ZERO: [["allowed_sec", "허용 시간", "s"], ["allowed_px", "허용 높이", "px"]],
};
const HANDLE = 8;        // px, drawn handle size
const HIT = 6;           // px, handle hit tolerance
const ZERO_HIT = 7;      // px, half of the 14 px zero-line hit band
const MIN_RADIUS = 8;    // source px, as domain/geometry.py
const MAX_ZOOM = 16;
const CHECK_DELAY_MS = 250;
const NOTICE_MS = 8000;
const SPEED_MIN = 0.1;
const SPEED_MAX = 16;
const SPEED_PRESETS = [0.5, 1, 2, 3, 4];

let defaultRule = null;
const state = {
  recipe: null,          // the Recipe being edited, in the API's detail shape
  dirty: false,
  selected: null,        // Glass id
  video: null,           // the open sample video
  shownIndex: 0,         // frame index on screen
  shownTime: 0,
  wantIndex: 0,          // frame index asked for
  loading: false,
  image: null,           // ImageBitmap on screen
  zoom: 1, panX: 0, panY: 0,
  problems: [],          // from the last check
  badInputs: new Map(),  // input key -> text that is not a number
  playing: false,
  speed: 1,
  drag: null,
};

// ---- formatting ----------------------------------------------------------------------

function clock(seconds) {
  if (!Number.isFinite(seconds)) return "--:--.-";
  const tenths = Math.round(seconds * 10);
  const minutes = Math.floor(tenths / 600);
  const rest = (tenths % 600) / 10;
  return `${String(minutes).padStart(2, "0")}:${rest.toFixed(1).padStart(4, "0")}`;
}

/** "2", "2x", "×2" and "*2" all read as 2, clamped to the allowed range; null when it is not a number. */
function parseSpeed(text) {
  const bare = text.trim().replace(/^[x×*]\s*/i, "").replace(/\s*[x×]$/i, "");
  const number = Number(bare);
  if (bare === "" || !Number.isFinite(number)) return null;
  return Math.round(Math.min(SPEED_MAX, Math.max(SPEED_MIN, number)) * 100) / 100;
}

function localDate(iso) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

function fileNameFor(name) {
  // display only; adapters/storage/recipe_files.py owns the real rule
  let stem = name.trim().replace(/[<>:"/\\|?*\x00-\x1f]/g, "_").replace(/[. ]+$/, "") || "_";
  if (/^(con|prn|aux|nul|com[0-9¹²³]|lpt[0-9¹²³])(\..*)?$/i.test(stem)) stem = "_" + stem;
  return stem + ".recipe.json";
}

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (value !== undefined && value !== null) node.setAttribute(key, value);
  }
  for (const child of children) if (child !== null && child !== undefined) node.append(child);
  return node;
}

function notify(id, message, kind = "info") {
  const node = $(id);
  node.textContent = message;
  node.className = `notice ${kind}`;
  clearTimeout(node.timer);
  node.timer = setTimeout(() => { node.textContent = ""; }, NOTICE_MS);
}

function showView(name) {
  $("listView").hidden = name !== "list";
  $("editView").hidden = name !== "edit";
}

// ---- list ------------------------------------------------------------------------------

async function showList() {
  stopPlayback();
  await closeVideo();
  state.recipe = null;
  showView("list");
  let listing;
  try {
    listing = await api.getJson("/api/recipes");
  } catch (error) {
    notify("listNotice", error.message, "error");
    return;
  }
  const rows = $("recipeRows");
  rows.replaceChildren();
  if (listing.recipes.length === 0) {
    rows.append(el("tr", { class: "empty-row" }, el("td", { colspan: "5" }, "Recipe가 없습니다. \"새 Recipe\"로 만드세요.")));
  }
  for (const recipe of listing.recipes) {
    const open = () => openRecipe(recipe.id);
    rows.append(el("tr", { "data-id": recipe.id, ondblclick: open, onclick: (e) => selectRow(e.currentTarget) },
      el("td", {}, recipe.name),
      el("td", {}, recipe.glass_names.join(", ")),
      el("td", { class: "num" }, `${recipe.width} × ${recipe.height}`),
      el("td", {}, localDate(recipe.updated_at)),
      el("td", {}, el("button", { class: "btn small", onclick: open }, "열기"))));
  }
  const unreadable = listing.unreadable;
  const box = $("unreadable");
  box.replaceChildren();
  if (unreadable.length) {
    box.append(`읽을 수 없는 파일 ${unreadable.length}개`);
    for (const item of unreadable) box.append(el("div", {}, el("b", {}, item.file), `: ${item.reason}`));
  }
  $("folderPath").textContent = listing.folder;
}

function selectRow(row) {
  for (const other of $("recipeRows").children) other.classList.toggle("sel", other === row);
}

async function openRecipe(recipeId) {
  let recipe;
  try {
    recipe = await api.getJson(`/api/recipes/${encodeURIComponent(recipeId)}`);
  } catch (error) {
    notify("listNotice", error.message, "error");
    return;
  }
  enterEdit(recipe);
  try {
    const { bitmap } = await api.getImage(`/api/recipes/${encodeURIComponent(recipe.id)}/reference.jpg`);
    state.image = bitmap;
  } catch (error) {
    notify("editNotice", `기준 프레임을 불러오지 못했습니다: ${error.message}`, "error");
  }
  draw();
}

async function newRecipe() {
  const video = await chooseVideo(null, "listNotice");
  if (!video) return;
  enterEdit({ id: null, name: "", glasses: [], reference_frame: null, updated_at: null });
  setVideo(video, 0);
}

// ---- edit: state ------------------------------------------------------------------------

function enterEdit(recipe) {
  state.recipe = recipe;
  state.selected = recipe.glasses[0]?.id ?? null;
  state.dirty = false;
  state.image = null;
  state.zoom = 1; state.panX = 0; state.panY = 0;
  state.problems = [];
  state.badInputs.clear();
  $("editNotice").textContent = "";
  showView("edit");
  $("recipeName").value = recipe.name;
  renderAll();
  scheduleCheck();
  $("frame").focus();
}

function selectedGlass() {
  return state.recipe?.glasses.find((g) => g.id === state.selected) ?? null;
}

function frameSize() {
  if (state.video) return { W: state.video.width, H: state.video.height };
  const f = state.recipe?.reference_frame;
  return f ? { W: f.width, H: f.height } : { W: 1280, H: 720 };
}

function changed({ panel = false } = {}) {
  state.dirty = true;
  renderTitle();
  if (panel) renderPanel();
  renderProblems();
  draw();
  scheduleCheck();
}

function draft() {
  const r = state.recipe;
  return {
    id: r.id,
    name: r.name,
    glasses: r.glasses,
    reference: state.video ? { video_id: state.video.id, time_sec: state.shownTime } : null,
  };
}

let checkTimer = 0;
let checkSerial = 0;
function scheduleCheck() {
  clearTimeout(checkTimer);
  checkTimer = setTimeout(runCheck, CHECK_DELAY_MS);
}

async function runCheck() {
  if (!state.recipe) return;
  const serial = ++checkSerial;
  const result = await api.call("POST", "/api/recipes/check", draft());
  if (serial !== checkSerial || !state.recipe) return;
  if (!result.ok) {
    notify("editNotice", result.data.error ?? "검사하지 못했습니다.", "error");
    return;
  }
  state.problems = result.data.problems;
  renderProblems();
}

async function save() {
  if (state.badInputs.size) {
    notify("editNotice", "숫자가 아닌 입력을 먼저 고치세요.", "error");
    return;
  }
  stopPlayback();
  const result = await api.call("POST", "/api/recipes", draft());
  if (result.status === 422) {
    state.problems = result.data.problems;
    renderProblems();
    notify("editNotice", "문제를 고친 뒤 저장하세요.", "error");
    return;
  }
  if (!result.ok) {
    notify("editNotice", result.data.error ?? "저장하지 못했습니다.", "error");
    return;
  }
  state.recipe = result.data;
  state.dirty = false;
  state.problems = [];
  $("recipeName").value = state.recipe.name;
  renderAll();
  notify("editNotice", "저장했습니다.");
}

async function back() {
  if (state.dirty && !confirm("저장하지 않은 변경이 있습니다. 버리고 목록으로 갈까요?")) return;
  await showList();
}

// ---- edit: video and frames -------------------------------------------------------------

async function chooseVideo(recipeId, noticeId) {
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

async function openVideoForRecipe() {
  stopPlayback();
  const video = await chooseVideo(state.recipe.id, "editNotice");
  if (!video) return;
  await closeVideo();
  const reference = state.recipe.reference_frame;
  const start = reference && reference.source_name === video.name ? reference.time_sec : 0;
  setVideo(video, start);
  scheduleCheck();
}

function setVideo(video, time) {
  state.video = video;
  state.shownIndex = -1;
  state.zoom = 1; state.panX = 0; state.panY = 0;
  renderFrameInfo();
  seekIndex(Math.round(time * video.fps));
}

async function closeVideo() {
  if (!state.video) return;
  const id = state.video.id;
  state.video = null;
  await api.call("DELETE", `/api/videos/${encodeURIComponent(id)}`);
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
    const time = (index + 0.5) / video.fps;  // the middle of the frame, so rounding lands on it
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
    notify("editNotice", error.message, "error");
  } finally {
    state.loading = false;
  }
  if (state.video === video && state.wantIndex !== state.shownIndex) loadFrame();
}

let playStart = 0;
let playFrom = 0;
function playTime() {
  return playFrom + (performance.now() - playStart) / 1000 * state.speed;
}

function togglePlayback() {
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

function stopPlayback() {
  state.playing = false;
  $("playIcon").setAttribute("d", "M6 4l10 6-10 6z");
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

function toggleSpeedMenu(open) {
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

// ---- edit: geometry ---------------------------------------------------------------------

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

function glassesSelectedFirst() {
  const all = state.recipe?.glasses ?? [];
  return [...all.filter((g) => g.id === state.selected), ...all.filter((g) => g.id !== state.selected)];
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
  if (!state.recipe || event.button !== 0) return;
  const canvas = $("frame");
  canvas.focus();
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left, y = event.clientY - rect.top;
  if (event.shiftKey) {
    state.drag = { kind: "pan", x0: event.clientX, y0: event.clientY, panX: state.panX, panY: state.panY };
  } else {
    const hit = hitTest(x, y);
    if (!hit) return;  // a plain drag on empty space does nothing (DESIGN.md §7)
    if (hit.glass.id !== state.selected) {
      state.selected = hit.glass.id;
      renderGlassRows();
      renderPanel();
    }
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
    const hit = state.recipe ? hitTest(x, y) : null;
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
  renderPositionInputs();
}

function onPointerUp() {
  const drag = state.drag;
  state.drag = null;
  if (drag?.moved) changed();
}

function onWheel(event) {
  if (!state.recipe) return;
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

function onKey(event) {
  if ($("help").open) return;  // the dialog closes itself on Esc
  const tag = document.activeElement?.tagName;
  const typing = tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA";
  if (event.key === "F1" || (event.key === "?" && !typing)) {
    event.preventDefault();
    openHelp();
    return;
  }
  if (event.key === "Escape" && !$("speedMenu").hidden) {
    toggleSpeedMenu(false);
    return;
  }
  if (!state.recipe || $("editView").hidden || typing) return;
  if (tag === "BUTTON" && (event.key === " " || event.key === "Enter")) return;
  const step = event.shiftKey ? 10 : 1;
  const arrows = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] };
  if (arrows[event.key]) {
    const glass = selectedGlass();
    if (!glass) return;
    event.preventDefault();
    moveGlass(glass, { ...glass.ellipse }, glass.zero_line_y, ...arrows[event.key]);
    renderPositionInputs();
    changed();
  } else if (event.key === " ") {
    event.preventDefault();
    togglePlayback();
  } else if (event.key === ",") {
    stopPlayback();
    seekIndex(state.wantIndex - 1);
  } else if (event.key === ".") {
    stopPlayback();
    seekIndex(state.wantIndex + 1);
  }
}

// ---- edit: glasses ----------------------------------------------------------------------

function addGlass() {
  const { W, H } = frameSize();
  const glasses = state.recipe.glasses;
  let number = glasses.length + 1;
  const names = new Set(glasses.map((g) => g.name.trim().toLowerCase()));
  while (names.has(`glass ${number}`)) number += 1;
  // v1 InspectionRecipe.default_glass, shifted so a new Glass does not hide an old one
  const rx = Math.round(W * 0.12), ry = Math.round(H * 0.27);
  const shift = Math.round(W * 0.05) * (glasses.length % 4);
  const cx = Math.min(W - rx, Math.round(W * 0.5) + shift), cy = Math.round(H * 0.5);
  glasses.push({
    id: crypto.randomUUID(),
    name: `Glass ${number}`,
    ellipse: { center_x: cx, center_y: cy, radius_x: rx, radius_y: ry },
    zero_line_y: Math.round(H * 0.55),
    judgment_rule: { ...defaultRule },
  });
  state.selected = glasses.at(-1).id;
  changed({ panel: true });
}

function deleteGlass(id) {
  const glasses = state.recipe.glasses;
  const index = glasses.findIndex((g) => g.id === id);
  if (index < 0) return;
  glasses.splice(index, 1);
  for (const key of [...state.badInputs.keys()]) if (key.startsWith(`${id}.`)) state.badInputs.delete(key);
  state.selected = glasses[Math.min(index, glasses.length - 1)]?.id ?? null;
  changed({ panel: true });
}

// ---- rendering ----------------------------------------------------------------------------

function renderAll() {
  renderTitle();
  renderFrameInfo();
  renderTransport();
  renderGlassRows();
  renderPanel();
  renderProblems();
  draw();
}

function renderTitle() {
  const r = state.recipe;
  $("recipeTitle").textContent = r.name.trim() || "새 Recipe";
  $("saveState").textContent = state.dirty ? "저장되지 않은 변경 있음"
    : r.updated_at ? `저장됨 · ${localDate(r.updated_at)}` : "아직 저장하지 않음";
  $("fileName").textContent = r.name.trim() ? `파일: ${fileNameFor(r.name)}` : "";
}

function renderFrameInfo() {
  const reference = state.recipe.reference_frame;
  const parts = [];
  if (state.video) parts.push(state.video.name);
  else if (reference) parts.push(`${reference.source_name} (저장된 기준 프레임)`);
  if (reference) parts.push(`저장된 기준 ${clock(reference.time_sec)}`);
  $("frameSource").textContent = parts.join(" · ");
  $("frameHint").textContent = state.video ? "저장하면 지금 보이는 프레임이 기준이 됩니다"
    : "영상을 열면 프레임을 넘겨 볼 수 있습니다";
  const off = !state.video;
  for (const id of ["prevFrame", "play", "nextFrame", "speed", "speedMenuBtn"]) $(id).disabled = off;
  $("scrub").classList.toggle("off", off);
  $("speedBox").classList.toggle("off", off);
  if (off) toggleSpeedMenu(false);
}

function renderTransport() {
  const video = state.video;
  const ref = $("scrubRef");
  if (!video) {
    $("time").textContent = "--:--.- / --:--.-";
    ref.hidden = true;
    return;
  }
  const last = Math.max(1, video.frame_count - 1);
  const fraction = state.wantIndex / last;
  $("scrubDone").style.width = `${fraction * 100}%`;
  $("scrubThumb").style.left = `${fraction * 100}%`;
  $("time").textContent = `${clock(state.wantIndex / video.fps)} / ${clock(video.duration_sec)}`;
  const reference = state.recipe.reference_frame;
  ref.hidden = !(reference && reference.source_name === video.name);
  if (!ref.hidden) ref.style.left = `${Math.min(100, (reference.time_sec * video.fps / last) * 100)}%`;
}

function problemsFor(glassId, field) {
  return state.problems.filter((p) => p.glass_id === glassId && (field === undefined || p.field === field));
}

function renderGlassRows() {
  const box = $("glassRows");
  box.replaceChildren();
  const glasses = state.recipe.glasses;
  if (glasses.length === 0) box.append(el("div", { class: "glass-empty" }, "\"+ 추가\"로 Glass를 놓으세요."));
  for (const glass of glasses) {
    const bad = [...state.badInputs.keys()].some((k) => k.startsWith(`${glass.id}.`));
    const first = bad ? "숫자가 아닌 입력" : problemsFor(glass.id)[0]?.message ?? "";
    box.append(el("div", {
      class: `glass-row${glass.id === state.selected ? " sel" : ""}`,
      onclick: () => { state.selected = glass.id; renderGlassRows(); renderPanel(); draw(); },
    },
    el("b", {}, glass.name.trim() || "(이름 없음)"),
    el("span", { class: "mode" }, MODES[glass.judgment_rule.mode]),
    el("span", { class: "err", title: first }, first),
    el("button", {
      class: "btn icon-btn del", title: "Glass 삭제",
      onclick: (e) => { e.stopPropagation(); deleteGlass(glass.id); },
    }, trashIcon())));
  }
}

function trashIcon() {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 20 20");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "1.5");
  const path = document.createElementNS(ns, "path");
  path.setAttribute("d", "M4 6h12M8 6V4h4v2M6 6l1 10h6l1-10");
  svg.append(path);
  return svg;
}

function numberField(key, label, unit, value, apply) {
  const input = el("input", { inputmode: "decimal", "data-key": key });
  input.value = state.badInputs.get(key) ?? String(value);
  const box = el("div", { class: "input num" }, input, el("span", { class: "unit" }, unit));
  const err = el("span", { class: "err", "data-err": key });
  input.addEventListener("input", () => {
    const text = input.value.trim();
    const number = Number(text);
    if (text === "" || !Number.isFinite(number)) {
      state.badInputs.set(key, input.value);  // not applied; the drawing keeps the last value
    } else {
      state.badInputs.delete(key);
      apply(number);
    }
    changed();
  });
  return el("div", { class: "field" }, el("span", { class: "label" }, label), box, err);
}

function renderPanel() {
  const body = $("selBody");
  body.replaceChildren();
  const glass = selectedGlass();
  $("selHead").textContent = glass ? `선택한 Glass · ${glass.name.trim() || "(이름 없음)"}` : "선택한 Glass";
  if (!glass) {
    body.append(el("span", { class: "caption" }, "Glass를 선택하거나 추가하세요."));
    return;
  }
  const k = (field) => `${glass.id}.${field}`;
  const nameInput = el("input", { maxlength: "100" });
  nameInput.value = glass.name;
  nameInput.addEventListener("input", () => {
    glass.name = nameInput.value;
    $("selHead").textContent = `선택한 Glass · ${glass.name.trim() || "(이름 없음)"}`;
    changed();
  });
  body.append(el("div", { class: "field" }, el("span", { class: "label" }, "이름"),
    el("div", { class: "input", "data-box": k("name") }, nameInput), el("span", { class: "err", "data-err": k("name") })));

  const e = glass.ellipse;
  const setE = (field) => (v) => { glass.ellipse = { ...glass.ellipse, [field]: v }; };
  body.append(el("span", { class: "label" }, "위치 (원본 프레임 px)"),
    el("div", { class: "grid2" },
      numberField(k("ellipse.center_x"), "중심 X", "px", e.center_x, setE("center_x")),
      numberField(k("ellipse.center_y"), "중심 Y", "px", e.center_y, setE("center_y")),
      numberField(k("ellipse.radius_x"), "반지름 X", "px", e.radius_x, setE("radius_x")),
      numberField(k("ellipse.radius_y"), "반지름 Y", "px", e.radius_y, setE("radius_y"))),
    el("span", { class: "err", "data-err": k("ellipse") }),
    numberField(k("zero_line_y"), "0선 Y", "px", glass.zero_line_y, (v) => { glass.zero_line_y = v; }),
    el("hr"));

  const rule = glass.judgment_rule;
  const select = el("select", { "aria-label": "판정 방식" });
  for (const [mode, label] of Object.entries(MODES)) {
    const option = el("option", { value: mode }, label);
    option.selected = mode === rule.mode;
    select.append(option);
  }
  select.addEventListener("change", () => { rule.mode = select.value; changed({ panel: true }); });
  body.append(el("div", { class: "field" }, el("span", { class: "label" }, "판정 방식"), select));

  const setR = (field, scale = 1) => (v) => { rule[field] = v / scale; };
  const [first, second] = MODE_FIELDS[rule.mode];
  body.append(
    el("div", { class: "grid2" },
      numberField(k(`judgment_rule.${first[0]}`), first[1], first[2], rule[first[0]], setR(first[0])),
      numberField(k(`judgment_rule.${second[0]}`), second[1], second[2], rule[second[0]], setR(second[0]))),
    numberField(k("judgment_rule.minimum_valid_coverage_ratio"), "최소 유효 비율", "%",
      Math.round(rule.minimum_valid_coverage_ratio * 1000) / 10, setR("minimum_valid_coverage_ratio", 100)),
    el("div", { class: "rule-text", id: "ruleText" }, ruleText(rule)),
    el("span", { class: "err", "data-err": k("other") }));
  renderProblems();
}

function ruleText(rule) {
  if (rule.mode === "RECOVERY") {
    return `압축기 기동 후 Oil 선이 0선 이상으로 올라와 ${rule.stable_hold_sec} s 동안 머물러야 합니다. `
      + `그 시작은 기동 후 ${rule.recovery_limit_sec} s 안이어야 합니다.`;
  }
  const side = rule.mode === "HOLD_BELOW_ZERO" ? "위" : "아래";
  return `Oil 선이 0선 ${side}로 ${rule.allowed_px} px 넘게 벗어난 상태가 한 번에 ${rule.allowed_sec} s보다 길게 이어지면 FAIL입니다. `
    + "Foam은 판정에 쓰지 않습니다.";
}

function renderPositionInputs() {
  const glass = selectedGlass();
  if (!glass) return;
  const values = {
    "ellipse.center_x": glass.ellipse.center_x, "ellipse.center_y": glass.ellipse.center_y,
    "ellipse.radius_x": glass.ellipse.radius_x, "ellipse.radius_y": glass.ellipse.radius_y,
    zero_line_y: glass.zero_line_y,
  };
  for (const [field, value] of Object.entries(values)) {
    const key = `${glass.id}.${field}`;
    const input = document.querySelector(`input[data-key="${CSS.escape(key)}"]`);
    if (input && document.activeElement !== input) {
      input.value = String(value);
      state.badInputs.delete(key);
    }
  }
}

function renderProblems() {
  if (!state.recipe) return;
  const count = state.problems.length + state.badInputs.size;
  $("problemCount").textContent = count ? `문제 ${count}개` : "";
  const recipeLevel = (field) => state.problems.filter((p) => p.glass_id === null && p.field === field).map((p) => p.message).join(" ");
  $("recipeNameErr").textContent = recipeLevel("name");
  $("recipeNameBox").classList.toggle("bad", Boolean(recipeLevel("name")));
  $("frameErr").textContent = recipeLevel("reference_frame");
  $("glassesErr").textContent = recipeLevel("glasses");

  const glass = selectedGlass();
  const ruleBox = $("ruleText");
  if (glass && ruleBox) ruleBox.textContent = ruleText(glass.judgment_rule);
  if (!glass) return;
  const shown = new Set();
  for (const node of document.querySelectorAll("#selBody [data-err]")) {
    const key = node.dataset.err;
    const field = key.slice(glass.id.length + 1);
    let message = "";
    if (state.badInputs.has(key)) message = "숫자를 입력하세요.";
    else if (field !== "other") {
      const found = problemsFor(glass.id, field);
      found.forEach((p) => shown.add(p));
      message = found.map((p) => p.message).join(" ");
    }
    if (field === "other") {
      message = problemsFor(glass.id).filter((p) => !shown.has(p)).map((p) => p.message).join(" ");
    }
    node.textContent = message;
    const box = node.previousElementSibling;
    if (box?.classList.contains("input")) box.classList.toggle("bad", Boolean(message));
  }
  renderGlassRows();
}

// ---- drawing ------------------------------------------------------------------------------

function draw() {
  const canvas = $("frame");
  if (!state.recipe || $("editView").hidden) return;
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
  const glasses = glassesSelectedFirst().reverse();  // the selected Glass on top
  for (const glass of glasses) drawGlass(g, glass, L, glass.id === state.selected);
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

// ---- help ---------------------------------------------------------------------------------

function openHelp() {
  const view = $("editView").hidden ? "list" : "edit";
  for (const section of document.querySelectorAll("#help [data-help]")) section.hidden = section.dataset.help !== view;
  $("helpTitle").textContent = view === "edit" ? "도움말 · Recipe 화면" : "도움말 · Recipe 목록";
  stopPlayback();
  toggleSpeedMenu(false);
  $("help").showModal();
}

// ---- start --------------------------------------------------------------------------------

function wire() {
  $("newRecipe").addEventListener("click", newRecipe);
  $("openFolder").addEventListener("click", async () => {
    const result = await api.call("POST", "/api/recipes/open-folder", {});
    if (!result.ok) notify("listNotice", result.data.error ?? "폴더를 열지 못했습니다.", "error");
  });
  $("back").addEventListener("click", back);
  $("save").addEventListener("click", save);
  $("openVideo").addEventListener("click", openVideoForRecipe);
  $("addGlass").addEventListener("click", addGlass);
  $("recipeName").addEventListener("input", () => { state.recipe.name = $("recipeName").value; changed(); });
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
  for (const button of document.querySelectorAll(".help-open")) button.addEventListener("click", openHelp);
  const help = $("help");
  $("helpClose").addEventListener("click", () => help.close());
  help.addEventListener("click", (event) => {  // a click on the backdrop lands on the dialog itself
    const box = help.getBoundingClientRect();
    const inside = event.clientX >= box.left && event.clientX <= box.right && event.clientY >= box.top && event.clientY <= box.bottom;
    if (!inside) help.close();
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
  document.addEventListener("keydown", onKey);
  new ResizeObserver(draw).observe($("frameBox"));
}

async function start() {
  wire();
  try {
    defaultRule = (await api.getJson("/api/defaults")).judgment_rule;
  } catch (error) {
    showView("list");
    notify("listNotice", error.message, "error");
    return;
  }
  await showList();
}

start();
