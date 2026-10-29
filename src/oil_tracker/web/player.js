// The editor's source video (Product SSOT §6 "Video"; A6): cropped to the Glass, with the lines drawn
// over it. Playing uses a <video> served with HTTP Range. A paused frame is the exact frame OpenCV
// reads, as the analysis did, so a line can be matched to it. A video the <video> cannot decode
// plays as exact frames instead.
import * as api from "./api.js";
import { SPEED_PRESETS, parseSpeed } from "./frame.js";
import { $, clock, el } from "./ui.js";

const NO_HOOKS = {
  time: () => {},           // the shown time changed
  overlay: () => "",        // SVG in source-frame coordinates, drawn over the picture
  repeat: () => null,       // { t0, t1 } to repeat, or null
};

const state = {
  inspectionId: null,
  videoId: null,            // the frame session
  info: null,               // { fps, frame_count, width, height, duration_sec }
  crop: null,               // the source region to show: { x, y, w, h }
  shown: null,              // the source region the box shows, which exact frames are cut to
  time: 0,
  playing: false,
  speed: 1,
  repeat: false,
  fallback: false,          // the <video> cannot play this file
  frameUrl: null,
  inFlight: false,
  pending: null,
  seeks: [],                // ms per exact frame, for the A6 measurement
};
let hooks = NO_HOOKS;
let playStart = 0;
let playFrom = 0;

export async function open(inspectionId, screenHooks) {
  close();
  hooks = { ...NO_HOOKS, ...screenHooks };
  state.inspectionId = inspectionId;
  const opened = (await api.call("POST", `/api/inspections/${encodeURIComponent(inspectionId)}/video`)).data;
  if (opened.error) throw new Error(opened.error);
  state.videoId = opened.id;
  state.info = opened;
  state.fallback = false;
  const video = $("video");
  video.src = api.mediaUrl(`/media/inspections/${encodeURIComponent(inspectionId)}/source`);
  video.load();
  renderTransport();
}

export function close() {
  state.playing = false;  // no last frame for a session about to close
  const video = $("video");
  video.pause();
  video.removeAttribute("src");
  video.load();
  if (state.videoId) api.call("DELETE", `/api/videos/${encodeURIComponent(state.videoId)}`);
  if (state.frameUrl) URL.revokeObjectURL(state.frameUrl);
  $("videoFrame").removeAttribute("src");
  Object.assign(state, { inspectionId: null, videoId: null, info: null, frameUrl: null, pending: null, seeks: [] });
  hooks = NO_HOOKS;
}

/** Show the region around a Glass: its ellipse with room for the lines to either side. */
export function frameGlass(glass) {
  if (!state.info) return;
  const e = glass.ellipse;
  const halfW = Math.max(2 * e.radius_x, 120), halfH = Math.max(1.15 * e.radius_y, 120);
  const x = Math.max(0, e.center_x - halfW), y = Math.max(0, e.center_y - halfH);
  state.crop = { x, y, w: Math.min(state.info.width, e.center_x + halfW) - x, h: Math.min(state.info.height, e.center_y + halfH) - y };
  layout();
}

export function layout() {
  const box = $("videoBox");
  if (!state.crop || !state.info) return;
  const bw = box.clientWidth, bh = box.clientHeight;
  if (!bw || !bh) return;  // hidden
  const { x, y, w, h } = state.crop;
  const k = Math.min(bw / w, bh / h);
  const vw = bw / k, vh = bh / k, vx = x + w / 2 - vw / 2, vy = y + h / 2 - vh / 2;
  const left = Math.max(0, Math.floor(vx)), top = Math.max(0, Math.floor(vy));
  state.shown = {
    x: left, y: top,
    w: Math.min(state.info.width, Math.ceil(vx + vw)) - left, h: Math.min(state.info.height, Math.ceil(vy + vh)) - top,
  };
  const stage = $("videoStage");
  stage.style.width = `${state.info.width}px`;
  stage.style.height = `${state.info.height}px`;
  stage.style.transform = `translate(${-vx * k}px, ${-vy * k}px) scale(${k})`;
  $("videoOverlay").setAttribute("viewBox", `${vx} ${vy} ${vw} ${vh}`);
  drawOverlay();
}

export function drawOverlay() {
  $("videoOverlay").innerHTML = hooks.overlay(state.time);
}

export function time() {
  return state.time;
}

export function isPlaying() {
  return state.playing;
}

export function seekStats() {
  return state.seeks.slice();
}

/** How the video plays: in the <video>, or as exact frames when the <video> cannot decode it. */
export function playbackInfo() {
  return { fallback: state.fallback, playing: state.playing, time: state.time };
}

/** Show the exact frame at t (paused). */
export function seek(t) {
  if (!state.info) return;
  if (state.playing) stop();
  state.time = clamp(t);
  renderTime();
  drawOverlay();
  requestFrame(state.time);
}

function clamp(t) {
  const last = (state.info.frame_count - 1) / state.info.fps;
  return Math.min(last, Math.max(0, t));
}

function requestFrame(t) {
  if (state.inFlight) {
    state.pending = t;
    return;
  }
  state.inFlight = true;
  const began = performance.now();
  const cut = state.shown ? `&crop=${state.shown.x},${state.shown.y},${state.shown.w},${state.shown.h}` : "";
  api.getBlobUrl(`/api/videos/${encodeURIComponent(state.videoId)}/frame?t=${t.toFixed(4)}${cut}`)
    .then(async ({ url, headers }) => {
      const img = $("videoFrame");
      const shown = new Image();
      shown.src = url;
      await shown.decode();
      const [x, y, w, h] = (headers.get("X-Frame-Region") ?? `0,0,${state.info.width},${state.info.height}`).split(",").map(Number);
      Object.assign(img.style, { left: `${x}px`, top: `${y}px`, width: `${w}px`, height: `${h}px` });
      img.src = url;
      img.hidden = false;
      if (state.frameUrl) URL.revokeObjectURL(state.frameUrl);
      state.frameUrl = url;
      state.seeks.push(performance.now() - began);
      if (state.seeks.length > 500) state.seeks.shift();
    })
    .catch(() => {})  // a closed session or a frame past the end: the last picture stays
    .finally(() => {
      state.inFlight = false;
      if (state.pending !== null && state.info) {
        const next = state.pending;
        state.pending = null;
        requestFrame(next);
      } else if (state.playing && state.fallback) {
        requestAnimationFrame(fallbackTick);
      }
    });
}

export function toggle() {
  if (state.playing) stop();
  else play();
}

async function play() {
  if (!state.info) return;
  state.playing = true;
  renderTransport();
  const range = state.repeat ? hooks.repeat() : null;
  if (range && (state.time < range.t0 || state.time >= range.t1)) state.time = range.t0;
  if (!state.fallback) {
    const video = $("video");
    try {
      video.playbackRate = state.speed;
      video.currentTime = state.time;
      await video.play();
      if (!state.playing) {  // stopped while starting
        video.pause();
        return;
      }
      $("videoFrame").hidden = true;
      requestAnimationFrame(videoTick);
      return;
    } catch {
      state.fallback = true;  // the codec, most likely: play exact frames instead
    }
  }
  playStart = performance.now();
  playFrom = state.time;
  fallbackTick();
}

function videoTick() {
  if (!state.playing || state.fallback) return;
  const video = $("video");
  advance(video.currentTime, (t) => { video.currentTime = t; });
  if (video.ended) stop();
  else requestAnimationFrame(videoTick);
}

function fallbackTick() {
  if (!state.playing || !state.fallback) return;
  const t = playFrom + ((performance.now() - playStart) / 1000) * state.speed;
  advance(t, (start) => {
    playFrom = start;
    playStart = performance.now();
  });
  if (state.time >= (state.info.frame_count - 1) / state.info.fps) {
    stop();
    return;
  }
  if (!state.inFlight) requestFrame(state.time);
}

function advance(t, jump) {
  const range = state.repeat ? hooks.repeat() : null;
  if (range && t >= range.t1) {
    jump(range.t0);
    t = range.t0;
  }
  state.time = clamp(t);
  renderTime();
  drawOverlay();
  hooks.time(state.time);
}

export function stop() {
  if (!state.playing) return;
  state.playing = false;
  const video = $("video");
  if (!state.fallback) {
    video.pause();
    state.time = clamp(video.currentTime);
    hooks.time(state.time);
  }
  renderTransport();
  requestFrame(state.time);
}

/** One frame back or forward, paused. */
export function step(direction) {
  if (!state.info) return;
  const index = Math.round(state.time * state.info.fps) + direction;
  seek(index / state.info.fps);
  hooks.time(state.time);
}

function setSpeed(speed) {
  if (state.playing && state.fallback) {
    playFrom = state.time;
    playStart = performance.now();
  }
  state.speed = speed;
  $("videoSpeed").value = String(speed);
  if (state.playing && !state.fallback) $("video").playbackRate = speed;
}

function commitSpeed() {
  const speed = parseSpeed($("videoSpeed").value);
  if (speed === null) $("videoSpeed").value = String(state.speed);
  else setSpeed(speed);
}

export function toggleSpeedMenu(open) {
  const menu = $("videoSpeedMenu");
  menu.hidden = !(open ?? menu.hidden);
  if (menu.hidden) return;
  menu.replaceChildren(...SPEED_PRESETS.map((speed) => el("button", {
    class: speed === state.speed ? "on" : "", role: "option", "aria-selected": String(speed === state.speed),
    onclick: () => { setSpeed(speed); toggleSpeedMenu(false); },
  }, `${speed}×`)));
}

function renderTime() {
  const end = state.info ? state.info.duration_sec : NaN;
  $("videoTime").textContent = `${clock(state.time)} / ${clock(end)}`;
}

function renderTransport() {
  $("videoPlayIcon").setAttribute("d", state.playing ? "M5 4h3v12H5zM12 4h3v12h-3z" : "M6 4l10 6-10 6z");
  $("videoRepeat").classList.toggle("on", state.repeat);
  $("videoRepeat").setAttribute("aria-pressed", String(state.repeat));
  renderTime();
}

export function wire() {
  $("videoPrev").addEventListener("click", () => step(-1));
  $("videoNext").addEventListener("click", () => step(1));
  $("videoPlay").addEventListener("click", toggle);
  $("videoRepeat").addEventListener("click", () => {
    state.repeat = !state.repeat;
    renderTransport();
  });
  const speed = $("videoSpeed");
  speed.addEventListener("change", commitSpeed);
  speed.addEventListener("keydown", (event) => {
    if (event.key === "Enter") speed.blur();
    if (event.key === "Escape") {
      speed.value = String(state.speed);
      speed.blur();
    }
    event.stopPropagation();
  });
  $("videoSpeedBtn").addEventListener("click", () => toggleSpeedMenu());
  $("video").addEventListener("error", () => {
    if (state.inspectionId) state.fallback = true;
  });
  new ResizeObserver(layout).observe($("videoBox"));
}
