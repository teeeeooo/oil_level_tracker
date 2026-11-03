// The full-size video window (Product SSOT §6; DESIGN.md §5 "Video window"): the whole source frame,
// fitted or at 100 %, with the editor's chosen Glass and lines drawn over it. It follows the editor
// through the server's relay (videolink.js is the other side): the editor's state moves it, and its
// transport sends commands for the editor to carry out. A paused frame is the exact frame.
import * as api from "./api.js";
import { SPEED_PRESETS, parseSpeed } from "./frame.js";
import * as render from "./render.js";
import { $, clock, el } from "./ui.js";
import { catchUp } from "./videolink.js";

const ME = "window";
const SEEK_SEND_MS = 100;   // scrubbing sends at most this often
const RETRY_MS = 1000;

const params = new URLSearchParams(location.search);
const inspectionId = params.get("inspection") ?? "";
const channel = `video-${inspectionId}`;
const page = Math.random().toString(36).slice(2);  // this page load, so a late "bye" names its sender

const state = {
  info: null,          // the video: { id, width, height, fps, frame_count, duration_sec }
  editor: null,        // the editor's last state: { time, playing, speed, at, glass, range }
  lines: null,         // { glass_id, times, ys }
  time: 0,             // the time shown
  zoom: "fit",
  pan: null,           // the frame's top-left at 100 %, in window px
  fallback: false,     // the <video> cannot play this file: exact frames instead
  frameUrl: null,
  inFlight: false,
  pending: null,
  seq: -1,
  linked: false,
};
let lastSeek = 0;

async function start() {
  wire();
  try {
    const opened = await api.call("POST", `/api/inspections/${encodeURIComponent(inspectionId)}/video`);
    if (!opened.ok) throw new Error(opened.data.error ?? `영상을 열 수 없습니다 (HTTP ${opened.status}).`);
    state.info = opened.data;
  } catch (error) {
    $("vwCaption").textContent = error.message;  // the server says what failed
    return;
  }
  const video = $("vwVideo");
  video.src = api.mediaUrl(`/media/inspections/${encodeURIComponent(inspectionId)}/source`);
  $("vwCaption").textContent = `편집기에서 고른 Glass의 선을 겹쳐 그림 · ${state.info.width} × ${state.info.height}`;
  layout();
  const joined = await api.call("GET", `/api/relay/${encodeURIComponent(channel)}?after=-1`);
  state.seq = joined.ok ? joined.data.seq : 0;
  post({ type: "hello", page });
  listen();
}

// ---- following the editor --------------------------------------------------------------------------

async function listen() {
  for (;;) {
    let result;
    try {
      result = await api.call("GET", `/api/relay/${encodeURIComponent(channel)}?after=${state.seq}`);
    } catch {
      result = null;
    }
    if (!result?.ok) {
      setLinked(false);
      await new Promise((resolve) => setTimeout(resolve, RETRY_MS));
      continue;
    }
    state.seq = result.data.seq;
    if (result.data.missed) post({ type: "hello", page });  // fell behind: ask for the whole state again
    for (const { from, message } of result.data.messages) {
      if (from === ME || !message) continue;
      if (message.type === "state") follow(message);
      else if (message.type === "lines") {
        state.lines = message;
        drawOverlay();
      } else if (message.type === "bye") {  // the editor closed or opened another inspection
        window.close();
        setLinked(false);
      }
    }
  }
}

function follow(message) {
  state.editor = message;
  setLinked(true);
  $("vwGlass").textContent = message.glass?.name ?? "—";
  if (document.activeElement !== $("vwSpeed")) $("vwSpeed").value = String(message.speed);
  renderPlay();
  if (state.zoom === "actual" && state.pan === null) layout();  // the Glass is known now
  const video = $("vwVideo");
  if (message.playing) {
    const expected = expectedTime();
    if (state.fallback) {
      requestAnimationFrame(tick);
      return;
    }
    video.playbackRate = message.speed;
    if (video.paused) {
      video.currentTime = expected;
      video.play().then(() => {
        if (!state.editor?.playing) video.pause();
        else $("vwImage").hidden = true;
      }).catch(() => {
        state.fallback = true;  // the codec, most likely
        requestAnimationFrame(tick);
      });
    } else {
      const { jump, rate } = catchUp(video.currentTime - expected, message.speed);
      if (jump) video.currentTime = expected;
      video.playbackRate = rate;
    }
    requestAnimationFrame(tick);
  } else {
    video.pause();
    show(message.time);
    requestFrame(message.time);
  }
}

/** The editor's time now, from its last word. */
function expectedTime() {
  const m = state.editor;
  return m.playing ? m.time + ((Date.now() - m.at) / 1000) * m.speed : m.time;
}

function tick() {
  if (!state.editor?.playing) return;
  if (state.fallback) {
    show(expectedTime());
    if (!state.inFlight) requestFrame(state.time);
  } else {
    show($("vwVideo").currentTime);
  }
  requestAnimationFrame(tick);
}

function show(t) {
  state.time = t;
  drawOverlay();
  renderTime();
}

function requestFrame(t) {
  if (!state.info) return;
  if (state.inFlight) {
    state.pending = t;
    return;
  }
  state.inFlight = true;
  api.getBlobUrl(`/api/videos/${encodeURIComponent(state.info.id)}/frame?t=${t.toFixed(4)}`)
    .then(async ({ url }) => {
      const shown = new Image();
      shown.src = url;
      await shown.decode();
      if (state.editor?.playing && !state.fallback) {  // playing again meanwhile
        URL.revokeObjectURL(url);
        return;
      }
      $("vwImage").src = url;
      $("vwImage").hidden = false;
      if (state.frameUrl) URL.revokeObjectURL(state.frameUrl);
      state.frameUrl = url;
    })
    .catch(() => {})  // a closed session or a frame past the end: the last picture stays
    .finally(() => {
      state.inFlight = false;
      if (state.pending !== null) {
        const next = state.pending;
        state.pending = null;
        requestFrame(next);
      }
    });
}

function setLinked(linked) {
  state.linked = linked;
  $("vwSync").classList.toggle("on", linked);
  $("vwSyncText").textContent = linked ? "편집기와 같은 위치" : "편집기와 연결되지 않음";
}

// ---- drawing ---------------------------------------------------------------------------------------

function layout() {
  if (!state.info) return;
  const stage = $("vwStage");
  const sw = stage.clientWidth, sh = stage.clientHeight, w = state.info.width, h = state.info.height;
  let k, x, y;
  if (state.zoom === "fit") {
    k = Math.min(1, sw / w, sh / h);
    x = (sw - w * k) / 2;
    y = (sh - h * k) / 2;
  } else {
    k = 1;
    const e = state.editor?.glass?.ellipse;  // start where the chosen Glass shows
    const wanted = state.pan ?? (e ? { x: sw / 2 - e.center_x, y: sh / 2 - e.center_y } : null);
    const pan = clampPan(wanted ?? { x: 0, y: 0 }, sw, sh);
    if (wanted) state.pan = pan;
    ({ x, y } = pan);
  }
  const frame = $("vwFrame");
  frame.style.width = `${w}px`;
  frame.style.height = `${h}px`;
  frame.style.transform = `translate(${x}px, ${y}px) scale(${k})`;
  $("vwOverlay").setAttribute("viewBox", `0 0 ${w} ${h}`);
  $("vwZoomText").textContent = `${Math.round(k * 100)} %`;
  for (const button of $("vwZoom").children) button.classList.toggle("on", button.dataset.zoom === state.zoom);
  stage.classList.toggle("pan", state.zoom === "actual");
  drawOverlay();
}

/** At 100 %, the frame covers the window where it is larger, and is centred where it is smaller. */
function clampPan(pan, sw, sh) {
  const w = state.info.width, h = state.info.height;
  const x = w <= sw ? (sw - w) / 2 : Math.min(0, Math.max(sw - w, pan.x));
  const y = h <= sh ? (sh - h) / 2 : Math.min(0, Math.max(sh - h, pan.y));
  return { x, y };
}

function drawOverlay() {
  const m = state.editor, lines = state.lines;
  const shown = $("vwLines").checked && m?.glass;
  $("vwOverlay").innerHTML = shown
    ? render.videoOverlay(m.glass, lines?.times ?? [], lines?.ys ?? {}, state.time)
    : "";
}

function renderTime() {
  const range = state.editor?.range;
  $("vwTime").textContent = `${clock(state.time)} / ${clock(state.info?.duration_sec ?? NaN)}`;
  const share = range && range.t1 > range.t0 ? Math.min(1, Math.max(0, (state.time - range.t0) / (range.t1 - range.t0))) : 0;
  $("vwDone").style.width = `${share * 100}%`;
  $("vwThumb").style.left = `${share * 100}%`;
}

function renderPlay() {
  $("vwPlayIcon").setAttribute("d", state.editor?.playing ? "M5 4h3v12H5zM12 4h3v12h-3z" : "M6 4l10 6-10 6z");
}

// ---- the transport: commands for the editor --------------------------------------------------------

function post(message) {
  api.call("POST", `/api/relay/${encodeURIComponent(channel)}`, { from: ME, message }).catch(() => {});
}

function command(action, value) {
  post({ type: "command", action, value });
}

function scrubTime(event) {
  const range = state.editor?.range;
  if (!range) return null;
  const box = $("vwScrub").getBoundingClientRect();
  const share = Math.min(1, Math.max(0, (event.clientX - box.left) / box.width));
  return range.t0 + share * (range.t1 - range.t0);
}

function commitSpeed() {
  const speed = parseSpeed($("vwSpeed").value);
  if (speed === null) $("vwSpeed").value = String(state.editor?.speed ?? 1);
  else command("speed", speed);
}

function toggleSpeedMenu(open) {
  const menu = $("vwSpeedMenu");
  menu.hidden = !(open ?? menu.hidden);
  if (menu.hidden) return;
  const current = state.editor?.speed;
  menu.replaceChildren(...SPEED_PRESETS.map((speed) => el("button", {
    class: speed === current ? "on" : "", role: "option", "aria-selected": String(speed === current),
    onclick: () => { command("speed", speed); toggleSpeedMenu(false); },
  }, `${speed}×`)));
}

function wire() {
  $("vwPlay").addEventListener("click", () => command("toggle"));
  $("vwPrev").addEventListener("click", () => command("step", -1));
  $("vwNext").addEventListener("click", () => command("step", 1));
  $("vwLines").addEventListener("change", drawOverlay);
  for (const button of $("vwZoom").children) {
    button.addEventListener("click", () => {
      state.zoom = button.dataset.zoom;
      layout();
    });
  }
  const speed = $("vwSpeed");
  speed.addEventListener("change", commitSpeed);
  speed.addEventListener("keydown", (event) => {
    if (event.key === "Enter") speed.blur();
    if (event.key === "Escape") {
      speed.value = String(state.editor?.speed ?? 1);
      speed.blur();
    }
    event.stopPropagation();
  });
  $("vwSpeedBtn").addEventListener("click", () => toggleSpeedMenu());

  const scrub = $("vwScrub");
  scrub.addEventListener("pointerdown", (event) => {
    const t = scrubTime(event);
    if (t === null) return;
    scrub.setPointerCapture(event.pointerId);
    show(t);
    command("seek", t);
    lastSeek = performance.now();
  });
  scrub.addEventListener("pointermove", (event) => {
    if (!scrub.hasPointerCapture(event.pointerId)) return;
    const t = scrubTime(event);
    show(t);
    if (performance.now() - lastSeek >= SEEK_SEND_MS) {
      command("seek", t);
      lastSeek = performance.now();
    }
  });
  scrub.addEventListener("pointerup", (event) => {
    if (!scrub.hasPointerCapture(event.pointerId)) return;
    command("seek", scrubTime(event));
  });

  const stage = $("vwStage");
  let drag = null;
  stage.addEventListener("pointerdown", (event) => {
    if (state.zoom !== "actual" || !state.pan) return;
    stage.setPointerCapture(event.pointerId);
    stage.classList.add("panning");
    drag = { x: event.clientX, y: event.clientY, pan: { ...state.pan } };
  });
  stage.addEventListener("pointermove", (event) => {
    if (!drag) return;
    state.pan = { x: drag.pan.x + event.clientX - drag.x, y: drag.pan.y + event.clientY - drag.y };
    layout();
  });
  const endDrag = () => {
    drag = null;
    stage.classList.remove("panning");
  };
  stage.addEventListener("pointerup", endDrag);
  stage.addEventListener("pointercancel", endDrag);
  new ResizeObserver(layout).observe(stage);

  document.addEventListener("keydown", (event) => {
    if (event.target instanceof HTMLInputElement && event.target.type !== "checkbox") return;
    if (event.code === "Space") {
      event.preventDefault();
      command("toggle");
    } else if (event.code === "Comma" || event.code === "Period") {
      event.preventDefault();
      command("step", event.code === "Comma" ? -1 : 1);
    } else if (event.key === "Escape") {
      toggleSpeedMenu(false);
    }
  });
  document.addEventListener("pointerdown", (event) => {
    if (!event.target.closest(".speed")) toggleSpeedMenu(false);
  });
  $("vwVideo").addEventListener("error", () => { state.fallback = true; });
  window.addEventListener("pagehide", () => {
    api.beacon("POST", `/api/relay/${encodeURIComponent(channel)}`, { from: ME, message: { type: "bye", page } });
    if (state.info) api.beacon("DELETE", `/api/videos/${encodeURIComponent(state.info.id)}`);
  });
}

start();
