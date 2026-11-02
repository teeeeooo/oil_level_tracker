// The editor's side of the full-size video window (Product SSOT §6; DESIGN.md §5 "Video window").
// "크게 보기" asks the server to open it, a second OS window; without an app window (a browser), the
// page opens it itself. The two pages share no browser channel, so they talk through the server's
// relay. The editor stays the master: the window sends commands (play, step, seek, speed), the
// editor carries them out and sends its state; while playing it sends its time twice a second.
// catchUp() is the rule by which the window keeps to that time.
import * as api from "./api.js";

const ME = "editor";
const TICK_MS = 500;       // the time while playing, for the window to correct drift
const LINES_DELAY_MS = 300;
const JUMP_SEC = 1.0;      // wall-clock seconds of drift past which the window jumps
const STEADY_SEC = 0.04;   // wall-clock seconds of drift the window lets be
const CATCH_SEC = 2.0;     // the window makes up a drift over about this long
const RATE_BAND = 0.1;     // ...playing at most 10 % faster or slower than the editor

let link = null;           // { id, channel, seq, hooks, popup, alive, pages }
let tick = 0;
let linesTimer = 0;

/** How the window's playing <video> keeps to the editor: drift is its time less the editor's, in
 * video seconds. A seek decodes from a key frame, so a jump at every small drift stalls the picture,
 * worst at a high speed (V2-4b Windows run): a small drift is made up by playing a little faster or
 * slower, and only a drift of over JUMP_SEC of wall time jumps. */
export function catchUp(drift, speed) {
  const wall = drift / speed;
  if (Math.abs(wall) > JUMP_SEC) return { jump: true, rate: speed };
  if (Math.abs(wall) <= STEADY_SEC) return { jump: false, rate: speed };
  const change = Math.max(-RATE_BAND, Math.min(RATE_BAND, -wall / CATCH_SEC));
  return { jump: false, rate: speed * (1 + change) };
}

/** Open the window for this inspection, or bring it forward. hooks: { state(), lines(), command(message) },
 * where state() is { time, playing, speed, glass, range } and lines() { glass_id, times, ys }. */
export async function show(inspectionId, hooks) {
  if (link?.id !== inspectionId) {  // listen before the window opens, so its first "hello" is heard
    stop();
    const own = { id: inspectionId, channel: `video-${inspectionId}`, seq: -1, hooks, popup: null, alive: true, pages: new Set() };
    const joined = await api.call("GET", `/api/relay/${encodeURIComponent(own.channel)}?after=-1`);
    own.seq = joined.data.seq;
    link = own;
    listen(own);
  }
  const result = await api.call("POST", `/api/inspections/${encodeURIComponent(inspectionId)}/video-window`);
  if (!result.ok) {
    stop();
    throw new Error(result.data.error ?? `HTTP ${result.status}`);
  }
  if (!link) return;  // closed meanwhile
  if (!result.data.opened) {  // no app window: a browser opens it as a popup
    if (link.popup && !link.popup.closed) link.popup.focus();
    else link.popup = window.open(result.data.path, "oltVideoWindow", "popup,width=1280,height=800");
  }
  sendState();
  sendLines();
}

/** The editor closes or opens another inspection: the window closes too. */
export function close() {
  if (!link) return;
  post({ type: "bye" });
  api.call("POST", "/api/video-window/close").catch(() => {});
  if (link.popup && !link.popup.closed) link.popup.close();
  stop();
}

export function isOpen() {
  return link !== null;
}

/** The player played, stopped, moved or changed speed, or the Glass changed. */
export function stateChanged() {
  if (!link) return;
  sendState();
  clearInterval(tick);
  tick = link.hooks.state().playing ? setInterval(sendState, TICK_MS) : 0;
}

/** The chosen Glass's lines changed (sent shortly after, once). */
export function linesChanged() {
  if (!link) return;
  clearTimeout(linesTimer);
  linesTimer = setTimeout(sendLines, LINES_DELAY_MS);
}

function stop() {
  clearInterval(tick);
  clearTimeout(linesTimer);
  if (link) link.alive = false;
  link = null;
}

function sendState() {
  if (link) post({ type: "state", at: Date.now(), ...link.hooks.state() });
}

function sendLines() {
  if (link) post({ type: "lines", ...link.hooks.lines() });
}

function post(message) {
  if (!link) return;
  api.call("POST", `/api/relay/${encodeURIComponent(link.channel)}`, { from: ME, message }).catch(() => {});
}

async function listen(own) {
  while (own.alive) {
    let result;
    try {
      result = await api.call("GET", `/api/relay/${encodeURIComponent(own.channel)}?after=${own.seq}`);
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 1000));  // the server is closing
      continue;
    }
    if (!own.alive) return;
    if (!result.ok) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      continue;
    }
    own.seq = result.data.seq;
    for (const { from, message } of result.data.messages) {
      if (from === ME || !message) continue;
      if (message.type === "hello") {
        own.pages.add(message.page);
        sendState();
        sendLines();
      } else if (message.type === "command") {
        own.hooks.command(message);
      } else if (message.type === "bye" && own.pages.delete(message.page) && own.pages.size === 0) {
        stop();  // the user closed the window
        return;
      }
    }
  }
}
