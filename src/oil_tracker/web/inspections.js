// Inspection list, the new-inspection flow, the analysis setup and its progress (DESIGN.md §5,
// Product SSOT §3). Every setup check runs in Python through /api/inspections/check; this file only
// edits and shows. Nothing is written until "분석 시작".
import * as api from "./api.js";
import * as frame from "./frame.js";
import * as nav from "./nav.js";
import { positionFields, renderPositionInputs, showFieldProblems } from "./recipe.js";
import { $, MODES, clock, el, localDate, notify, parseClock, typing } from "./ui.js";

const STATES = { ANALYSED: "분석 완료", NOT_ANALYSED: "분석 안 됨", FAILED: "분석 실패" };
const SETTINGS = ["start_sec", "end_sec", "compressor_start_sec"];
const CHECK_DELAY_MS = 250;
const POLL_MS = 500;

let links = { openRecipes: () => {}, newRecipeWith: () => {}, openResult: () => {} };

const setup = {
  inspection: null,      // the existing inspection, or null until the analysis first starts
  recipe: null,          // the inspection's Recipe copy; Glass positions change in place
  original: null,        // the stored Recipe the copy came from, or null when it is gone
  needsCompressor: false,
  settings: null,        // { start_sec, end_sec, compressor_start_sec }
  selected: null,        // Glass id
  problems: [],          // from the last check
  badInputs: new Map(),  // input key -> text that is not a number or a time
  dirty: false,
};

const setupHooks = {
  glasses: () => setup.recipe?.glasses ?? [],
  selected: () => setup.selected,
  select: (id) => { setup.selected = id; renderGlasses(); },
  moving: () => renderPositionInputs(selectedGlass(), setup.badInputs),
  moved: () => changed(),
  marks: () => {
    const s = setup.settings;
    if (!s) return [];
    const marks = [{ time: s.start_sec, label: "시작", kind: "in" }, { time: s.end_sec, label: "끝", kind: "out" }];
    if (s.compressor_start_sec !== null) marks.push({ time: s.compressor_start_sec, label: "기동", kind: "comp" });
    return marks;
  },
  range: () => (setup.settings ? [setup.settings.start_sec, setup.settings.end_sec] : null),
  size: () => {
    const f = setup.recipe?.reference_frame;
    return f ? { W: f.width, H: f.height } : { W: 1280, H: 720 };
  },
  noticeId: "setupNotice",
};

// ---- list ------------------------------------------------------------------------------

export async function showList() {
  await frame.closeVideo();
  setup.recipe = null;
  nav.show("inspectionsView");
  let listing;
  try {
    listing = await api.getJson("/api/inspections");
  } catch (error) {
    notify("inspectionsNotice", error.message, "error");
    return;
  }
  const rows = $("inspectionRows");
  rows.replaceChildren();
  if (listing.inspections.length === 0) {
    rows.append(el("tr", { class: "empty-row" }, el("td", { colspan: "5" }, "검사가 없습니다. \"새 검사\"로 시작하세요.")));
  }
  for (const item of listing.inspections) {
    const open = () => openInspection(item);
    const reason = item.failure ? el("span", { class: "err" }, ` ${item.failure}`) : null;
    rows.append(el("tr", { "data-id": item.id, ondblclick: open, onclick: (e) => selectRow(e.currentTarget) },
      el("td", {}, item.video_name, el("span", { class: "sub mono" }, item.folder)),
      el("td", {}, item.recipe_name),
      el("td", {}, localDate(item.created_at)),
      el("td", {}, el("span", { class: "badge pending" }, STATES[item.state] ?? item.state), reason),
      el("td", {}, el("button", { class: "btn small", onclick: open }, "열기"))));
  }
  const box = $("inspectionsUnreadable");
  box.replaceChildren();
  if (listing.unreadable.length) {
    box.append(`읽을 수 없는 폴더 ${listing.unreadable.length}개`);
    for (const item of listing.unreadable) box.append(el("div", {}, el("b", {}, item.folder), `: ${item.reason}`));
  }
  $("inspectionsFolder").textContent = listing.folder;
  if (listing.job && !$("progressDialog").open) resumeProgress(listing.job);
}

function selectRow(row) {
  for (const other of $("inspectionRows").children) other.classList.toggle("sel", other === row);
}

function openInspection(item) {
  if (item.state === "ANALYSED") links.openResult(item.id);
  else openSetup(item.id);
}

async function resumeProgress(job) {
  let detail;
  try {
    detail = await api.getJson(`/api/inspections/${encodeURIComponent(job.inspection_id)}`);
  } catch {
    return;
  }
  const status = await watchProgress(job, detail);
  if (status.state === "finished") links.openResult(detail.id);
  else await showList();
}

// ---- a new inspection: video, then Recipe ---------------------------------------------------

async function newInspection() {
  const video = await frame.chooseVideo("inspectionsNotice");
  if (!video) return;
  const choice = await pickRecipe(video, { allowNew: true, noticeId: "inspectionsNotice" });
  if (choice === "new") {
    links.newRecipeWith(video);
    return;
  }
  const recipe = choice ? await loadRecipe(choice.id, "inspectionsNotice") : null;
  if (!recipe) {
    await api.call("DELETE", `/api/videos/${encodeURIComponent(video.id)}`);
    return;
  }
  enterSetup({
    inspection: null, video, recipe, original: structuredClone(recipe),
    needsCompressor: choice.needs_compressor_start,
    settings: { start_sec: 0, end_sec: video.duration_sec, compressor_start_sec: null },
  });
}

async function loadRecipe(recipeId, noticeId) {
  try {
    return await api.getJson(`/api/recipes/${encodeURIComponent(recipeId)}`);
  } catch (error) {
    notify(noticeId, error.message, "error");
    return null;
  }
}

/** The Recipe picker (DESIGN.md §5): a choice, "new" for a new Recipe on this video, or null. */
async function pickRecipe(video, { allowNew, current = null, noticeId }) {
  let listing;
  try {
    listing = await api.getJson(`/api/inspections/recipe-choices?video_id=${encodeURIComponent(video.id)}`);
  } catch (error) {
    notify(noticeId, error.message, "error");
    return null;
  }
  const dialog = $("pickDialog");
  $("pickVideo").textContent = video.name;
  $("pickVideoFacts").textContent = `${video.width} × ${video.height} · ${clock(video.duration_sec)}`;
  $("pickNewRecipe").hidden = !allowNew;
  const rows = $("pickRows");
  rows.replaceChildren();
  let picked = null;
  const choose = (recipe, row) => {
    picked = recipe;
    for (const other of rows.children) other.classList.toggle("sel", other === row);
    $("pickNext").disabled = false;
  };
  $("pickNext").disabled = true;
  return new Promise((resolve) => {
    const stop = new AbortController();
    const finish = (value) => {
      stop.abort();
      dialog.close();
      resolve(value);
    };
    if (listing.recipes.length === 0) {
      rows.append(el("tr", { class: "empty-row" }, el("td", { colspan: "4" }, "Recipe가 없습니다. 이 영상으로 새 Recipe를 만드세요.")));
    }
    for (const recipe of listing.recipes) {
      const usable = recipe.problem === null;
      const row = el("tr", { class: usable ? "" : "off", "data-id": recipe.id },
        el("td", {}, recipe.name, recipe.problem ? el("span", { class: "sub" }, recipe.problem) : null),
        el("td", {}, recipe.glass_names.join(", ")),
        el("td", { class: "num" }, `${recipe.width} × ${recipe.height}`),
        el("td", {}, localDate(recipe.updated_at)));
      rows.append(row);
      if (usable) {
        row.addEventListener("click", () => choose(recipe, row));
        row.addEventListener("dblclick", () => finish(recipe));
        if (!picked || recipe.id === current) choose(recipe, row);
      }
    }
    const box = $("pickUnreadable");
    box.replaceChildren(...listing.unreadable.map((item) => el("div", {}, el("b", {}, item.file), `: ${item.reason}`)));
    const signal = stop.signal;
    $("pickNext").addEventListener("click", () => finish(picked), { signal });
    $("pickCancel").addEventListener("click", () => finish(null), { signal });
    $("pickNewRecipe").addEventListener("click", () => finish("new"), { signal });
    dialog.addEventListener("cancel", (event) => { event.preventDefault(); finish(null); }, { signal });
    dialog.showModal();
  });
}

// ---- setup ----------------------------------------------------------------------------------

async function openSetup(inspectionId) {
  const id = encodeURIComponent(inspectionId);
  let detail;
  try {
    detail = await api.getJson(`/api/inspections/${id}`);
  } catch (error) {
    notify("inspectionsNotice", error.message, "error");
    return;
  }
  const opened = await api.call("POST", `/api/inspections/${id}/video`, {});
  const original = await api.call("GET", `/api/recipes/${encodeURIComponent(detail.recipe.id)}`);
  enterSetup({
    inspection: detail,
    video: opened.ok ? opened.data : null,
    recipe: structuredClone(detail.recipe),
    original: original.ok ? original.data : null,
    needsCompressor: detail.needs_compressor_start,
    settings: {
      start_sec: detail.settings.start_sec,
      end_sec: detail.settings.end_sec,
      compressor_start_sec: detail.settings.compressor_start_sec,
    },
  });
  if (!opened.ok) $("setupVideoErr").textContent = `영상을 열 수 없습니다: ${opened.data.error ?? ""}`;
}

function enterSetup({ inspection, video, recipe, original, needsCompressor, settings }) {
  Object.assign(setup, { inspection, recipe, original, needsCompressor, settings });
  setup.selected = recipe.glasses[0]?.id ?? null;
  setup.problems = [];
  setup.badInputs.clear();
  setup.dirty = false;
  $("setupNotice").textContent = "";
  $("setupVideoErr").textContent = "";
  nav.show("setupView");
  frame.attach($("setupLeft"), setupHooks);
  if (video) frame.setVideo(video, settings.start_sec);
  renderSetup();
  scheduleCheck();
  $("frame").focus();
}

function selectedGlass() {
  return setup.recipe?.glasses.find((g) => g.id === setup.selected) ?? null;
}

function originalGlass(glass) {
  return setup.original?.glasses.find((g) => g.id === glass.id) ?? null;
}

function differsFromRecipe(glass) {
  const recipe = originalGlass(glass);
  if (!recipe) return false;
  const keys = ["center_x", "center_y", "radius_x", "radius_y"];
  return recipe.zero_line_y !== glass.zero_line_y || keys.some((k) => recipe.ellipse[k] !== glass.ellipse[k]);
}

function changed() {
  setup.dirty = true;
  renderCaptions();
  renderGlassRows();
  renderProblems();
  frame.renderTransport();
  frame.draw();
  scheduleCheck();
}

function body() {
  const video = frame.video();
  return {
    inspection_id: setup.inspection?.id ?? null,
    video_id: setup.inspection ? null : video?.id ?? null,
    recipe_id: setup.recipe.id,
    glasses: setup.recipe.glasses.map((g) => ({ id: g.id, ellipse: g.ellipse, zero_line_y: g.zero_line_y })),
    settings: setup.settings,
  };
}

let checkTimer = 0;
let checkSerial = 0;
function scheduleCheck() {
  clearTimeout(checkTimer);
  checkTimer = setTimeout(runCheck, CHECK_DELAY_MS);
}

async function runCheck() {
  if (!setup.recipe) return;
  const serial = ++checkSerial;
  const result = await api.call("POST", "/api/inspections/check", body());
  if (serial !== checkSerial || !setup.recipe) return;
  if (!result.ok) {
    notify("setupNotice", result.data.error ?? "설정을 확인하지 못했습니다.", "error");
    return;
  }
  setup.problems = result.data.problems;
  renderProblems();
}

/** Put the time on screen into a setting ("지금", or the [ and ] keys). */
function takeNow(key) {
  if (!frame.video()) return;
  setup.settings[key] = frame.shownTime();
  setup.badInputs.delete(key);
  renderTimeFields();
  changed();
}

async function changeRecipe() {
  const video = frame.video();
  if (!video) return;
  frame.stopPlayback();
  const choice = await pickRecipe(video, { allowNew: false, current: setup.recipe.id, noticeId: "setupNotice" });
  if (!choice || choice === "new") return;
  const recipe = await loadRecipe(choice.id, "setupNotice");
  if (!recipe) return;
  setup.recipe = recipe;
  setup.original = structuredClone(recipe);
  setup.needsCompressor = choice.needs_compressor_start;
  setup.selected = recipe.glasses[0]?.id ?? null;
  for (const key of [...setup.badInputs.keys()]) if (!SETTINGS.includes(key)) setup.badInputs.delete(key);
  renderSetup();
  changed();
}

function revertGlass(glass) {
  const recipe = originalGlass(glass);
  if (!recipe) return;
  glass.ellipse = { ...recipe.ellipse };
  glass.zero_line_y = recipe.zero_line_y;
  for (const key of [...setup.badInputs.keys()]) if (key.startsWith(`${glass.id}.`)) setup.badInputs.delete(key);
  renderGlasses();
  changed();
}

async function back() {
  if (setup.dirty && !confirm("분석을 시작하지 않으면 바꾼 설정은 저장되지 않습니다. 검사 목록으로 갈까요?")) return;
  await showList();
}

function onKey(event) {
  if (!setup.recipe || typing()) return;
  const tag = document.activeElement?.tagName;
  if (tag === "BUTTON" && (event.key === " " || event.key === "Enter")) return;
  if (event.code === "BracketLeft" || event.code === "BracketRight") {  // the same keys in Korean input mode
    event.preventDefault();
    takeNow(event.code === "BracketLeft" ? "start_sec" : "end_sec");
    return;
  }
  frame.handleKey(event);
}

// ---- analysis and progress ------------------------------------------------------------------

async function startAnalysis() {
  if (setup.badInputs.size) {
    notify("setupNotice", "숫자나 시각이 아닌 입력을 먼저 고치세요.", "error");
    return;
  }
  frame.stopPlayback();
  $("startAnalysis").disabled = true;
  const result = await api.call("POST", "/api/inspections/start", body());
  $("startAnalysis").disabled = false;
  if (result.status === 422) {
    setup.problems = result.data.problems;
    renderProblems();
    notify("setupNotice", "문제를 고친 뒤 분석을 시작하세요.", "error");
    return;
  }
  if (!result.ok) {
    notify("setupNotice", result.data.error ?? "분석을 시작하지 못했습니다.", "error");
    return;
  }
  setup.inspection = result.data.inspection;  // the folder exists from here on
  setup.dirty = false;
  renderTitle();
  const status = await watchProgress(result.data.job, result.data.inspection);
  if (status.state === "finished") {
    await frame.closeVideo();
    links.openResult(setup.inspection.id);
    return;
  }
  const detail = await api.call("GET", `/api/inspections/${encodeURIComponent(setup.inspection.id)}`);
  if (detail.ok) setup.inspection = detail.data;
  renderTitle();
  if (status.state === "cancelled") notify("setupNotice", "분석을 취소했습니다. 설정은 남아 있습니다.");
  else notify("setupNotice", `분석하지 못했습니다: ${status.message ?? ""}`, "error");
}

function timeLeft(seconds) {
  if (seconds === null || seconds === undefined) return "남은 시간 계산 중";
  const total = Math.max(1, Math.round(seconds));
  const minutes = Math.floor(total / 60), rest = total % 60;
  return minutes ? `남은 시간 약 ${minutes}분 ${rest}초` : `남은 시간 약 ${rest}초`;
}

/** Show the progress dialog until the job ends; the job's last status. */
async function watchProgress(job, inspection) {
  const dialog = $("progressDialog");
  const s = inspection.settings;
  $("progressVideo").textContent = inspection.video.name;
  $("progressFacts").textContent = `Glass ${inspection.recipe.glasses.length}개 · ${clock(s.start_sec)}–${clock(s.end_sec)}`;
  const cancel = $("progressCancel");
  cancel.disabled = false;
  cancel.textContent = "취소";
  const stop = new AbortController();
  cancel.addEventListener("click", async () => {
    cancel.disabled = true;
    cancel.textContent = "취소하는 중…";
    await api.call("POST", `/api/jobs/${encodeURIComponent(job.id)}/cancel`, {});
  }, { signal: stop.signal });
  dialog.addEventListener("cancel", (event) => event.preventDefault(), { signal: stop.signal });  // Esc does not hide it
  dialog.showModal();
  let status = job;
  while (status.state === "running") {
    const percent = Math.floor(status.fraction * 100);
    $("progressBar").style.width = `${percent}%`;
    $("progressPercent").textContent = `${percent}%`;
    dialog.querySelector(".progress").setAttribute("aria-valuenow", String(percent));
    $("progressLeft").textContent = status.cancel_requested ? "취소하는 중" : timeLeft(status.time_left_sec);
    await new Promise((resolve) => setTimeout(resolve, POLL_MS));
    const result = await api.call("GET", `/api/jobs/${encodeURIComponent(job.id)}`);
    if (!result.ok) {
      status = { state: "failed", message: result.data.error ?? "진행 상황을 읽지 못했습니다." };
      break;
    }
    status = result.data;
  }
  stop.abort();
  dialog.close();
  return status;
}

// ---- rendering ----------------------------------------------------------------------------

function renderSetup() {
  renderTitle();
  const video = frame.video();
  const facts = video ?? setup.inspection?.video;
  $("setupVideo").textContent = facts ? `${facts.name} · ${facts.width} × ${facts.height} · ${clock(facts.duration_sec)}` : "";
  $("changeRecipe").disabled = !video;
  $("setupRecipeName").textContent = setup.recipe.name;
  $("setupRecipeGlasses").replaceChildren(...setup.recipe.glasses.flatMap((g) => [
    el("b", {}, g.name), el("span", {}, MODES[g.judgment_rule.mode])]));
  renderTimeFields();
  renderGlasses();
  frame.refresh();
}

function renderTitle() {
  const name = (frame.video() ?? setup.inspection?.video)?.name ?? "";
  $("setupTitle").textContent = `${setup.inspection ? "검사" : "새 검사"} · ${name}`;
  const state = setup.inspection ? STATES[setup.inspection.state] : "분석 전";
  const failure = setup.inspection?.failure ? ` (${setup.inspection.failure})` : "";
  $("setupState").textContent = `${state}${failure} · Recipe ${setup.recipe.name}`;
}

function timeField(key, label, title, optional) {
  const value = setup.settings[key];
  const input = el("input", { inputmode: "decimal", "data-key": key, "aria-label": label, placeholder: "mm:ss.s" });
  input.value = setup.badInputs.get(key) ?? (value === null ? "" : clock(value));
  input.addEventListener("input", () => {
    const text = input.value.trim();
    const time = optional && text === "" ? null : parseClock(text);
    if (time === null && !(optional && text === "")) {
      setup.badInputs.set(key, input.value);  // not applied; the marks keep the last value
    } else {
      setup.badInputs.delete(key);
      setup.settings[key] = time;
    }
    changed();
  });
  input.addEventListener("change", () => {  // once entered, it reads as mm:ss.s (DESIGN.md §4 "Time field")
    if (!setup.badInputs.has(key)) input.value = setup.settings[key] === null ? "" : clock(setup.settings[key]);
  });
  input.addEventListener("keydown", (event) => { if (event.key === "Enter") input.blur(); });
  return el("div", { class: "field" }, el("span", { class: "label" }, label),
    el("div", { class: "timefield" }, el("div", { class: "input num" }, input),
      el("button", { class: "btn small", title, onclick: () => takeNow(key) }, "지금")),
    el("span", { class: "err", "data-err": key }));
}

function renderTimeFields() {
  $("rangeFields").replaceChildren(
    timeField("start_sec", "시작", "지금 시각으로 ([)", false),
    timeField("end_sec", "끝", "지금 시각으로 (])", false));
  $("compressorField").replaceChildren(timeField("compressor_start_sec", "기동 시각", "지금 시각으로", true));
  renderCaptions();
}

function renderCaptions() {
  const s = setup.settings;
  const length = s.end_sec - s.start_sec;
  // as the analysis samples: 2 per second, up to the last frame (adapters/video/context.py sample_indices)
  const video = frame.video() ?? setup.inspection?.video;
  const last = video ? (video.frame_count - 1) / video.fps : s.end_sec;
  const sampled = Math.min(s.end_sec, last) - s.start_sec;
  const samples = sampled >= 0 ? Math.floor(sampled * 2 + 1e-9) + 1 : 0;
  $("rangeCaption").textContent = `길이 ${clock(Math.max(0, length))} · 샘플 ${samples.toLocaleString()}개 (초당 2개)`;
  $("compressorCaption").textContent = setup.needsCompressor
    ? "기준점 회복 Glass가 있어 필요합니다. 분석 범위 안이어야 합니다."
    : "기준점 회복 Glass가 없어 넣지 않아도 됩니다. 넣으면 분석 범위 안이어야 합니다.";
}

function renderGlasses() {
  renderGlassRows();
  const box = $("setupGlassBody");
  const glass = selectedGlass();
  if (!glass) {
    box.replaceChildren(el("span", { class: "caption" }, "Glass가 없습니다."));
    return;
  }
  const recipe = originalGlass(glass);
  const revert = el("button", { class: "btn small", onclick: () => revertGlass(glass) }, "Recipe 위치로 되돌리기");
  revert.disabled = !recipe;
  const caption = recipe
    ? `Recipe: 중심 ${recipe.ellipse.center_x}, ${recipe.ellipse.center_y} · 0선 ${recipe.zero_line_y}`
    : "원래 Recipe를 찾을 수 없습니다.";
  box.replaceChildren(...positionFields(setup.badInputs, glass, changed),
    el("div", { class: "row" }, revert, el("span", { class: "caption" }, caption)),
    el("span", { class: "err", "data-err": `${glass.id}.other` }));
  renderProblems();
  frame.draw();
}

function renderGlassRows() {
  const box = $("setupGlassRows");
  box.replaceChildren();
  for (const glass of setup.recipe.glasses) {
    const bad = [...setup.badInputs.keys()].some((k) => k.startsWith(`${glass.id}.`));
    const first = bad ? "숫자가 아닌 입력" : setup.problems.find((p) => p.glass_id === glass.id)?.message ?? "";
    box.append(el("div", {
      class: `glass-row${glass.id === setup.selected ? " sel" : ""}`,
      onclick: () => { setup.selected = glass.id; renderGlasses(); },
    },
    el("b", {}, glass.name),
    el("span", { class: "mode" }, MODES[glass.judgment_rule.mode]),
    differsFromRecipe(glass) ? el("span", { class: "badge pending" }, "Recipe와 다름") : null,
    el("span", { class: "err", title: first }, first)));
  }
}

function renderProblems() {
  if (!setup.recipe) return;
  const count = setup.problems.length + setup.badInputs.size;
  $("setupProblemCount").textContent = count ? `문제 ${count}개` : "";
  for (const key of SETTINGS) {
    const node = document.querySelector(`#setupView [data-err="${key}"]`);
    if (!node) continue;
    const message = setup.badInputs.has(key) ? "시각을 mm:ss.s로 입력하세요."
      : setup.problems.filter((p) => p.glass_id === null && p.field === key).map((p) => p.message).join(" ");
    node.textContent = message;
    node.parentElement.querySelector(".input").classList.toggle("bad", Boolean(message));
  }
  $("setupRecipeErr").textContent = setup.problems
    .filter((p) => p.glass_id === null && !SETTINGS.includes(p.field)).map((p) => p.message).join(" ");
  const glass = selectedGlass();
  if (glass) showFieldProblems($("setupGlassBody"), glass, setup.problems, setup.badInputs);
  renderGlassRows();
}

// ---- start --------------------------------------------------------------------------------

export function init(screenLinks) {
  links = screenLinks;
  nav.register("inspectionsView", { title: "검사 목록" });
  nav.register("setupView", { title: "분석 설정", onKey });
  $("newInspection").addEventListener("click", newInspection);
  $("toRecipes").addEventListener("click", () => links.openRecipes());
  $("openInspectionsFolder").addEventListener("click", async () => {
    const result = await api.call("POST", "/api/inspections/open-folder", {});
    if (!result.ok) notify("inspectionsNotice", result.data.error ?? "폴더를 열지 못했습니다.", "error");
  });
  $("setupBack").addEventListener("click", back);
  $("startAnalysis").addEventListener("click", startAnalysis);
  $("changeRecipe").addEventListener("click", changeRecipe);
}
