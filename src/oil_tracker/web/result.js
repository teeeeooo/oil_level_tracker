// The analysis result, read-only, in the editor layout (DESIGN.md §5 "Editor window"). The editor
// (V2-3) adds editing to this same screen. Drawing is render.js's; this file only gathers the data.
import * as api from "./api.js";
import * as nav from "./nav.js";
import * as render from "./render.js";
import { $, MODES, clock, el, localDate, notify } from "./ui.js";

const state = {
  detail: null,     // the inspection
  analysis: null,   // its stored analysis
  glassId: null,
  background: false,
  images: new Map(),  // "glass/kind" -> [{ url, width }] in time order
};
let backToList = () => {};

export async function open(inspectionId) {
  release();
  nav.show("resultView");
  const id = encodeURIComponent(inspectionId);
  try {
    state.detail = await api.getJson(`/api/inspections/${id}`);
    state.analysis = await api.getJson(`/api/inspections/${id}/analysis`);
  } catch (error) {
    notify("resultNotice", error.message, "error");
    return;
  }
  state.glassId = state.analysis.glasses[0]?.glass_id ?? null;
  renderHeader();
  await showGlass();
}

function release() {
  for (const pieces of state.images.values()) for (const piece of pieces) URL.revokeObjectURL(piece.url);
  state.images.clear();
  state.detail = null;
  state.analysis = null;
  for (const id of ["graph", "context", "axis"]) $(id).replaceChildren();
}

async function showGlass() {
  renderGlassFacts();
  draw();  // the lines first; the pictures follow
  try {
    await loadImages(state.glassId, state.background ? "background" : "context");
  } catch (error) {
    notify("resultNotice", `그림을 불러오지 못했습니다: ${error.message}`, "error");
  }
  draw();
}

async function loadImages(glassId, kind) {
  const key = `${glassId}/${kind}`;
  if (state.images.has(key)) return;
  const layout = state.analysis.glasses.find((g) => g.glass_id === glassId);
  const base = `/api/inspections/${encodeURIComponent(state.detail.id)}/images/${encodeURIComponent(glassId)}`;
  const pieces = [];
  for (let index = 0; index < layout.pieces; index++) pieces.push(await api.getImageUrl(`${base}/${kind}-${index}.png`));
  state.images.set(key, pieces);
}

function panel() {
  const glass = state.detail.recipe.glasses.find((g) => g.id === state.glassId);
  const layout = state.analysis.glasses.find((g) => g.glass_id === state.glassId);
  const zero = glass.zero_line_y, e = glass.ellipse;
  const loaded = state.images.get(`${state.glassId}/${state.background ? "background" : "context"}`);
  let first = 0;
  const pieces = (loaded ?? []).map((piece) => {
    const placed = { href: piece.url, first, count: piece.width };
    first += piece.width;
    return placed;
  });
  return {
    times: state.analysis.times,
    oil: layout.oil.ys.map((y) => (y === null ? null : zero - y)),
    top: zero - (e.center_y - e.radius_y),
    bottom: zero - (e.center_y + e.radius_y),
    compressor: state.detail.settings.compressor_start_sec,
    image: { top: zero - layout.y0, rows: layout.rows, pieces },
  };
}

function draw() {
  if ($("resultView").hidden || !state.analysis || !state.glassId) return;
  const data = panel();
  const view = render.fitView(data);
  const size = (box) => [$(box).clientWidth, $(box).clientHeight];
  const [gw, gh] = size("graphBox");
  const [cw, ch] = size("contextBox");
  const [aw] = size("axisBox");
  paint("graph", gw, gh, render.graphSvg(data, view, gw, gh, "graph"));
  paint("context", cw, ch, render.contextSvg(data, view, cw, ch, "context"));
  paint("axis", aw, 32, render.axisSvg(view, aw));
}

function paint(id, width, height, svg) {
  const node = $(id);
  node.setAttribute("viewBox", `0 0 ${width} ${height}`);
  node.innerHTML = svg;
}

function renderHeader() {
  const d = state.detail;
  $("resultTitle").textContent = d.video.name;
  $("resultState").textContent = `Recipe ${d.recipe.name} · 분석 완료 · 읽기 전용`;
  const picker = $("resultGlass");
  picker.replaceChildren(...d.recipe.glasses.map((g) => el("option", { value: g.id }, g.name)));
  picker.value = state.glassId;
  const s = d.settings;
  const rows = [
    ["영상", d.video.name],
    ["Recipe", `${d.recipe.name} (이 검사의 사본)`],
    ["분석 범위", `${clock(s.start_sec)} – ${clock(s.end_sec)}`],
    ["압축기 기동", s.compressor_start_sec === null ? "없음" : clock(s.compressor_start_sec)],
    ["샘플", `${state.analysis.times.length.toLocaleString()}개 (초당 2개)`],
    ["분석한 시각", localDate(state.analysis.finished_at)],
    ["원본 SHA-256", d.video.sha256 ?? "-"],
  ];
  $("resultFacts").replaceChildren(...rows.map(([k, v]) => el("tr", {}, el("th", {}, k), el("td", { class: k.includes("SHA") ? "mono" : "" }, v))));
}

function renderGlassFacts() {
  const glass = state.detail.recipe.glasses.find((g) => g.id === state.glassId);
  const layout = state.analysis.glasses.find((g) => g.glass_id === state.glassId);
  const ys = layout.oil.ys;
  const empty = ys.filter((y) => y === null).length;
  $("resultGlassHead").textContent = `Glass · ${glass.name}`;
  const rows = [
    ["판정 방식", MODES[glass.judgment_rule.mode]],
    ["0선 Y", `${glass.zero_line_y} px`],
    ["Oil 초안", `빈 구간 ${Math.round((100 * empty) / Math.max(1, ys.length))}% (그리기 전까지 무효)`],
  ];
  $("resultGlassFacts").replaceChildren(...rows.map(([k, v]) => el("tr", {}, el("th", {}, k), el("td", {}, v))));
}

export function init(toList) {
  backToList = toList;
  nav.register("resultView", { title: "분석 결과" });
  $("resultBack").addEventListener("click", () => {
    release();
    backToList();
  });
  $("resultGlass").addEventListener("change", () => {
    state.glassId = $("resultGlass").value;
    showGlass();
  });
  $("backgroundToggle").addEventListener("change", () => {
    state.background = $("backgroundToggle").checked;
    if (state.analysis) showGlass();
  });
  const observer = new ResizeObserver(draw);
  for (const id of ["graphBox", "contextBox"]) observer.observe($(id));
}
