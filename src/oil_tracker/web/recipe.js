// Recipe list and Recipe screen (DESIGN.md §4–§5, Product SSOT §3 and §5).
// Every rule check runs in Python through /api/recipes/check; this file only edits and draws.
import * as api from "./api.js";
import * as frame from "./frame.js";
import * as nav from "./nav.js";
import { $, MODES, clock, el, localDate, notify, typing } from "./ui.js";

const MODE_FIELDS = {
  RECOVERY: [["recovery_limit_sec", "회복 제한 시간", "s"], ["stable_hold_sec", "안정 유지 시간", "s"]],
  HOLD_BELOW_ZERO: [["allowed_sec", "허용 시간", "s"], ["allowed_px", "허용 높이", "px"]],
  HOLD_ABOVE_ZERO: [["allowed_sec", "허용 시간", "s"], ["allowed_px", "허용 높이", "px"]],
};
const CHECK_DELAY_MS = 250;

let defaultRule = null;
let toInspections = () => {};
const state = {
  recipe: null,          // the Recipe being edited, in the API's detail shape
  dirty: false,
  selected: null,        // Glass id
  problems: [],          // from the last check
  badInputs: new Map(),  // input key -> text that is not a number
};

const frameHooks = {
  glasses: () => state.recipe?.glasses ?? [],
  selected: () => state.selected,
  select: (id) => { state.selected = id; renderGlassRows(); renderPanel(); },
  moving: () => renderPositionInputs(),
  moved: () => changed(),
  marks: () => {
    const reference = state.recipe?.reference_frame;
    const video = frame.video();
    return reference && video && reference.source_name === video.name
      ? [{ time: reference.time_sec, label: "기준", kind: "ref" }] : [];
  },
  size: () => {
    const f = state.recipe?.reference_frame;
    return f ? { W: f.width, H: f.height } : { W: 1280, H: 720 };
  },
  noticeId: "editNotice",
};

function fileNameFor(name) {
  // display only; adapters/storage/recipe_files.py owns the real rule
  let stem = name.trim().replace(/[<>:"/\\|?*\x00-\x1f]/g, "_").replace(/[. ]+$/, "") || "_";
  if (/^(con|prn|aux|nul|com[0-9¹²³]|lpt[0-9¹²³])(\..*)?$/i.test(stem)) stem = "_" + stem;
  return stem + ".recipe.json";
}

// ---- list ------------------------------------------------------------------------------

export async function showList() {
  await frame.closeVideo();
  state.recipe = null;
  nav.show("recipesView");
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
    frame.showImage(bitmap);
  } catch (error) {
    notify("editNotice", `기준 프레임을 불러오지 못했습니다: ${error.message}`, "error");
  }
}

async function newRecipe() {
  const video = await frame.chooseVideo("listNotice");
  if (video) newRecipeWith(video);
}

/** A new Recipe drawn on a video that is already open (also from the new-inspection flow). */
export function newRecipeWith(video) {
  enterEdit({ id: null, name: "", glasses: [], reference_frame: null, updated_at: null });
  frame.setVideo(video, 0);
  renderFrameInfo();
}

// ---- edit: state ------------------------------------------------------------------------

function enterEdit(recipe) {
  state.recipe = recipe;
  state.selected = recipe.glasses[0]?.id ?? null;
  state.dirty = false;
  state.problems = [];
  state.badInputs.clear();
  $("editNotice").textContent = "";
  nav.show("editView");
  frame.attach($("editLeft"), frameHooks);
  $("recipeName").value = recipe.name;
  renderAll();
  scheduleCheck();
  $("frame").focus();
}

function selectedGlass() {
  return state.recipe?.glasses.find((g) => g.id === state.selected) ?? null;
}

function changed({ panel = false } = {}) {
  state.dirty = true;
  renderTitle();
  if (panel) renderPanel();
  renderProblems();
  frame.draw();
  scheduleCheck();
}

function draft() {
  const r = state.recipe;
  const video = frame.video();
  return {
    id: r.id,
    name: r.name,
    glasses: r.glasses,
    reference: video ? { video_id: video.id, time_sec: frame.shownTime() } : null,
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
  frame.stopPlayback();
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

async function openVideoForRecipe() {
  frame.stopPlayback();
  const video = await frame.chooseVideo("editNotice", state.recipe.id);
  if (!video) return;
  await frame.closeVideo();
  const reference = state.recipe.reference_frame;
  const start = reference && reference.source_name === video.name ? reference.time_sec : 0;
  frame.setVideo(video, start);
  renderFrameInfo();
  scheduleCheck();
}

function onKey(event) {
  if (!state.recipe || typing()) return;
  const tag = document.activeElement?.tagName;
  if (tag === "BUTTON" && (event.key === " " || event.key === "Enter")) return;
  frame.handleKey(event);
}

// ---- edit: glasses ----------------------------------------------------------------------

function addGlass() {
  const video = frame.video();
  const { W, H } = video ? { W: video.width, H: video.height } : frameHooks.size();
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
  renderGlassRows();
  renderPanel();
  renderProblems();
  frame.draw();
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
  const video = frame.video();
  const parts = [];
  if (video) parts.push(video.name);
  else if (reference) parts.push(`${reference.source_name} (저장된 기준 프레임)`);
  if (reference) parts.push(`저장된 기준 ${clock(reference.time_sec)}`);
  $("frameSource").textContent = parts.join(" · ");
  $("frameHint").textContent = video ? "저장하면 지금 보이는 프레임이 기준이 됩니다"
    : "영상을 열면 프레임을 넘겨 볼 수 있습니다";
  frame.refresh();
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
      onclick: () => { state.selected = glass.id; renderGlassRows(); renderPanel(); frame.draw(); },
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

/** A number input whose text that is not a number is kept aside instead of applied. */
export function numberField(badInputs, key, label, unit, value, apply, onChange) {
  const input = el("input", { inputmode: "decimal", "data-key": key });
  input.value = badInputs.get(key) ?? String(value);
  const box = el("div", { class: "input num" }, input, el("span", { class: "unit" }, unit));
  const err = el("span", { class: "err", "data-err": key });
  input.addEventListener("input", () => {
    const text = input.value.trim();
    const number = Number(text);
    if (text === "" || !Number.isFinite(number)) {
      badInputs.set(key, input.value);  // not applied; the drawing keeps the last value
    } else {
      badInputs.delete(key);
      apply(number);
    }
    onChange();
  });
  return el("div", { class: "field" }, el("span", { class: "label" }, label), box, err);
}

/** The five position fields of a Glass, as on the Recipe screen. */
export function positionFields(badInputs, glass, onChange) {
  const k = (field) => `${glass.id}.${field}`;
  const e = glass.ellipse;
  const setE = (field) => (v) => { glass.ellipse = { ...glass.ellipse, [field]: v }; };
  const field = (...args) => numberField(badInputs, ...args, onChange);
  return [
    el("span", { class: "label" }, "위치 (원본 프레임 px)"),
    el("div", { class: "grid2" },
      field(k("ellipse.center_x"), "중심 X", "px", e.center_x, setE("center_x")),
      field(k("ellipse.center_y"), "중심 Y", "px", e.center_y, setE("center_y")),
      field(k("ellipse.radius_x"), "반지름 X", "px", e.radius_x, setE("radius_x")),
      field(k("ellipse.radius_y"), "반지름 Y", "px", e.radius_y, setE("radius_y"))),
    el("span", { class: "err", "data-err": k("ellipse") }),
    field(k("zero_line_y"), "0선 Y", "px", glass.zero_line_y, (v) => { glass.zero_line_y = v; }),
  ];
}

/** Refresh the position fields after a drag, except the one being typed in. */
export function renderPositionInputs(glass = selectedGlass(), badInputs = state.badInputs) {
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
      badInputs.delete(key);
    }
  }
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
  body.append(...positionFields(state.badInputs, glass, () => changed()), el("hr"));

  const rule = glass.judgment_rule;
  const select = el("select", { "aria-label": "판정 방식" });
  for (const [mode, label] of Object.entries(MODES)) {
    const option = el("option", { value: mode }, label);
    option.selected = mode === rule.mode;
    select.append(option);
  }
  select.addEventListener("change", () => { rule.mode = select.value; changed({ panel: true }); });
  body.append(el("div", { class: "field" }, el("span", { class: "label" }, "판정 방식"), select));

  const field = (...args) => numberField(state.badInputs, ...args, () => changed());
  const setR = (name, scale = 1) => (v) => { rule[name] = v / scale; };
  const [first, second] = MODE_FIELDS[rule.mode];
  body.append(
    el("div", { class: "grid2" },
      field(k(`judgment_rule.${first[0]}`), first[1], first[2], rule[first[0]], setR(first[0])),
      field(k(`judgment_rule.${second[0]}`), second[1], second[2], rule[second[0]], setR(second[0]))),
    field(k("judgment_rule.minimum_valid_coverage_ratio"), "최소 유효 비율", "%",
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

/** Show each Glass problem under its field in `body`; the rest go to the "other" slot if there is one. */
export function showFieldProblems(body, glass, problems, badInputs) {
  const shown = new Set();
  const forField = (field) => problems.filter((p) => p.glass_id === glass.id && p.field === field);
  for (const node of body.querySelectorAll("[data-err]")) {
    const key = node.dataset.err;
    const field = key.slice(glass.id.length + 1);
    let message = "";
    if (badInputs.has(key)) message = "숫자를 입력하세요.";
    else if (field !== "other") {
      const found = forField(field);
      found.forEach((p) => shown.add(p));
      message = found.map((p) => p.message).join(" ");
    }
    if (field === "other") {
      message = problems.filter((p) => p.glass_id === glass.id && !shown.has(p)).map((p) => p.message).join(" ");
    }
    node.textContent = message;
    const box = node.previousElementSibling;
    if (box?.classList.contains("input")) box.classList.toggle("bad", Boolean(message));
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
  if (glass) showFieldProblems($("selBody"), glass, state.problems, state.badInputs);
  renderGlassRows();
}

// ---- start --------------------------------------------------------------------------------

/** Wire the Recipe screens; `backToInspections` opens the inspection list. */
export async function init(backToInspections) {
  toInspections = backToInspections;
  nav.register("recipesView", { title: "Recipe 목록" });
  nav.register("editView", { title: "Recipe 화면", onKey });
  $("toInspections").addEventListener("click", async () => {
    await frame.closeVideo();
    toInspections();
  });
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
  defaultRule = (await api.getJson("/api/defaults")).judgment_rule;
}
