// Editing operations on dense samples (Product SSOT §6). A line is { ys: [source y or null],
// origins: ["DRAFT" | "EDITED" | "DRAWN"] }, as the API sends it. The operations change a line in
// place; the undo history keeps what each change replaced. editor.js owns the state.
import { lowerBound } from "./render.js";

export const SNAP_REACH = 8;      // source px (user, 2026-10-29)
export const SNAP_MIN_STEP = 6;   // luma step below which there is no edge to settle on
export const UNDO_DEPTH = 200;    // the spike's depth; the undo depth is the agent's choice
export const GRAB_WIDTHS = [2, 5, 10, 20, 30, 60, 120, 300, 600];  // seconds, stepped with [ and ]

/** The sample nearest to t. */
export function nearestIndex(times, t) {
  const i = lowerBound(times, t);
  if (i <= 0) return 0;
  if (i >= times.length) return times.length - 1;
  return t - times[i - 1] <= times[i] - t ? i - 1 : i;
}

/** The samples whose times lie in [t0, t1], as [first, end). */
export function indexRange(times, t0, t1) {
  return [lowerBound(times, Math.min(t0, t1)), lowerBound(times, Math.max(t0, t1) + 1e-9)];
}

/** How far a sample follows the grabbed one: 1 there, 0 at the grab width. Smooth bends without
 * overshoot (a raised cosine); pointed bends straight to a corner at the grabbed sample. */
export function falloff(distance, width, shape) {
  const x = Math.abs(distance) / width;
  if (x >= 1) return 0;
  return shape === "pointed" ? 1 - x : 0.5 * (1 + Math.cos(Math.PI * x));
}

export function copyLine(line) {
  return { ys: line.ys.slice(), origins: line.origins.slice() };
}

/** The stretch of non-empty samples around `index` that a grab moves. */
export function pieceAround(ys, index) {
  let first = index, end = index + 1;
  while (first > 0 && ys[first - 1] !== null) first--;
  while (end < ys.length && ys[end] !== null) end++;
  return [first, end];
}

/** Grab-and-drag: move the grabbed sample of `base` to `y`; its piece follows within `width`
 * seconds. Writes into `line`; returns the samples changed as [first, end). */
export function grab(line, base, times, index, y, width, shape) {
  const [pieceFirst, pieceEnd] = pieceAround(base.ys, index);
  const [first, end] = indexRange(times, times[index] - width, times[index] + width);
  const lo = Math.max(first, pieceFirst), hi = Math.min(end, pieceEnd);
  const shift = y - base.ys[index];
  for (let i = lo; i < hi; i++) {
    const weight = falloff(times[i] - times[index], width, shape);
    line.ys[i] = base.ys[i] + shift * weight;
    if (weight > 0 && shift !== 0) line.origins[i] = base.origins[i] === "DRAWN" ? "DRAWN" : "EDITED";
    else line.origins[i] = base.origins[i];
  }
  return [lo, hi];
}

/** The pencil: draw from (t0, y0) to (t1, y1), straight in between; returns [first, end). A press,
 * or a stroke between two samples, draws the sample nearest to it. */
export function pencil(line, times, t0, y0, t1, y1, settle = (i, y) => y) {
  let [first, end] = indexRange(times, t0, t1);
  if (first === end) {
    first = nearestIndex(times, (t0 + t1) / 2);
    end = first + 1;
  }
  for (let i = first; i < end; i++) {
    const share = t1 === t0 ? 1 : (times[i] - t0) / (t1 - t0);
    line.ys[i] = settle(i, y0 + (y1 - y0) * share);
    line.origins[i] = "DRAWN";
  }
  return [first, end];
}

/** Empty the samples in [first, end): no line there until it is drawn (Product SSOT §4). */
export function erase(line, first, end) {
  for (let i = first; i < end; i++) {
    line.ys[i] = null;
    line.origins[i] = "EDITED";
  }
}

/** Write drawn samples (the point line) from `first`. */
export function place(line, first, ys) {
  for (let k = 0; k < ys.length; k++) {
    line.ys[first + k] = ys[k];
    line.origins[first + k] = "DRAWN";
  }
  return [first, first + ys.length];
}

/** The snap (user, 2026-10-29): the row within SNAP_REACH of `y` where the luma steps most, in
 * one column of the context image; `y` itself when no step there is an edge. */
export function snap(luma, column, y, y0) {
  if (!luma || column < 0 || column >= luma.width) return y;
  const row = Math.round(y - y0);
  let best = null, strongest = SNAP_MIN_STEP;
  for (let r = Math.max(1, row - SNAP_REACH); r <= Math.min(luma.height - 2, row + SNAP_REACH); r++) {
    const step = Math.abs(luma.data[(r + 1) * luma.width + column] - luma.data[(r - 1) * luma.width + column]);
    if (step > strongest || (step === strongest && best !== null && Math.abs(r - row) < Math.abs(best - row))) {
      strongest = step;
      best = r;
    }
  }
  return best === null ? y : y0 + best;
}

/** The context image's luma, for the snap: { data: Uint8ClampedArray, width, height }. */
export async function lumaOf(urls) {
  const bitmaps = await Promise.all(urls.map(async (url) => createImageBitmap(await (await fetch(url)).blob())));
  const width = bitmaps.reduce((sum, b) => sum + b.width, 0);
  const height = bitmaps[0]?.height ?? 0;
  const data = new Uint8ClampedArray(width * height);
  let left = 0;
  for (const bitmap of bitmaps) {
    const canvas = new OffscreenCanvas(bitmap.width, height);
    const g = canvas.getContext("2d", { willReadFrequently: true });
    g.drawImage(bitmap, 0, 0);
    const rgba = g.getImageData(0, 0, bitmap.width, height).data;
    for (let r = 0; r < height; r++) {
      for (let c = 0; c < bitmap.width; c++) {
        const i = 4 * (r * bitmap.width + c);
        data[r * width + left + c] = 0.299 * rgba[i] + 0.587 * rgba[i + 1] + 0.114 * rgba[i + 2];
      }
    }
    left += bitmap.width;
    bitmap.close();
  }
  return { data, width, height };
}

/** Undo and redo. An entry changes samples of one line: { glassId, kind, first, before, after },
 * where before and after are { ys, origins } for [first, first + length). */
export class History {
  constructor() {
    this.done = [];
    this.undone = [];
  }

  /** Record what changed in `line` since `base`, a copy taken before the change. False when nothing did. */
  record(glassId, kind, base, line) {
    const differs = (i) => base.ys[i] !== line.ys[i] || base.origins[i] !== line.origins[i];
    let first = 0, end = line.ys.length;
    while (first < end && !differs(first)) first++;
    while (end > first && !differs(end - 1)) end--;
    if (first === end) return false;
    const slice = (l) => ({ ys: l.ys.slice(first, end), origins: l.origins.slice(first, end) });
    this.done.push({ glassId, kind, first, before: slice(base), after: slice(line) });
    if (this.done.length > UNDO_DEPTH) this.done.shift();
    this.undone = [];
    return true;
  }

  /** Undo the last change through `lineOf(glassId, kind)`; returns its entry, or null. */
  undo(lineOf) {
    const entry = this.done.pop();
    if (!entry) return null;
    apply(lineOf(entry.glassId, entry.kind), entry.first, entry.before);
    this.undone.push(entry);
    return entry;
  }

  redo(lineOf) {
    const entry = this.undone.pop();
    if (!entry) return null;
    apply(lineOf(entry.glassId, entry.kind), entry.first, entry.after);
    this.done.push(entry);
    return entry;
  }

  clear() {
    this.done = [];
    this.undone = [];
  }
}

function apply(line, first, part) {
  for (let k = 0; k < part.ys.length; k++) {
    line.ys[first + k] = part.ys[k];
    line.origins[first + k] = part.origins[k];
  }
}
