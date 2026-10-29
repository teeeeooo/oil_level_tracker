// Small helpers shared by every screen: DOM building, notices, time and date text.
export const $ = (id) => document.getElementById(id);
export const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const NOTICE_MS = 8000;

export const MODES = {
  RECOVERY: "기준점 회복",
  HOLD_BELOW_ZERO: "기준점 아래 유지",
  HOLD_ABOVE_ZERO: "기준점 위 유지",
};

/** mm:ss.s, with hours folded into the minutes as the transport shows them. */
export function clock(seconds) {
  if (!Number.isFinite(seconds)) return "--:--.-";
  const tenths = Math.round(seconds * 10);
  const minutes = Math.floor(tenths / 600);
  const rest = (tenths % 600) / 10;
  return `${String(minutes).padStart(2, "0")}:${rest.toFixed(1).padStart(4, "0")}`;
}

/** "mm:ss.s", "h:mm:ss.s" or plain seconds; null when the text is not a time. */
export function parseClock(text) {
  const parts = text.trim().split(":");
  if (parts.length > 3 || parts.some((p) => p.trim() === "")) return null;
  let seconds = 0;
  for (const [index, part] of parts.entries()) {
    const value = Number(part);
    const last = index === parts.length - 1;
    if (!Number.isFinite(value) || value < 0 || (!last && !Number.isInteger(value))) return null;
    seconds = seconds * 60 + value;
  }
  return Math.round(seconds * 1000) / 1000;
}

export function localDate(iso) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (value !== undefined && value !== null) node.setAttribute(key, value);
  }
  for (const child of children) if (child !== null && child !== undefined) node.append(child);
  return node;
}

export function notify(id, message, kind = "info") {
  const node = $(id);
  node.textContent = message;
  node.className = `notice ${kind}`;
  clearTimeout(node.timer);
  node.timer = setTimeout(() => { node.textContent = ""; }, NOTICE_MS);
}

/** Whether keys go to a text field rather than the screen. */
export function typing() {
  const tag = document.activeElement?.tagName;
  return tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA";
}
