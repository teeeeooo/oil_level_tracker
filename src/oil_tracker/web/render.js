// Drawing shared by the editor and the report (architecture.md, "One drawing module"). It draws only
// what it receives, as SVG text: no screen state and no API, so the report can inline it.
// Ported in part from spike/webui:spikes/webui/static/render.js (scales, niceTicks, the panel
// layering). v2 lines are dense samples (Product SSOT §4), drawn with a gap where a sample is empty.
//
// A panel is one Glass:
//   { times: [s], top: h, bottom: h, compressor: s or null,
//     lines: { oil: [h or null], foam: [...], reference: [...] },
//     levels: [{ state, first, end }], empty: [{ first, end }], cannot: [{ start_sec, end_sec }],
//     image: { top: h, rows, pieces: [{ href, first, count }] } or null }
// where h is a height in source px above the zero line (the Glass top has the largest h), and
// first/end are sample indices [first, end). Every field but times, top and bottom may be absent.
//
// The editor draws three layers per plot, so a drag redraws only the lines (architecture.md):
// back (grid, bands, picture), lines, and marks ({ playhead, selection, grab, compressor, memos,
// point }); the compressor start moves to the marks while it is dragged. Memos are
// [{ n, t, h or null }]. The point line in progress is { kind, points: [{ t, h }], path, preview,
// guides: [[{ t, h }, { t, h }]] }, where path and preview are { times, hs } or null.

export const INSET = { left: 52, right: 16, top: 14, bottom: 10 };  // DESIGN.md §7: no line clipped at the edge
export const KINDS = ["reference", "foam", "oil"];                  // drawing order: Oil on top

const TEXT = "font-size:12px;font-family:var(--font);font-variant-numeric:tabular-nums";
const SHAPE = "fill:none;stroke-linejoin:round;stroke-linecap:round";
const STROKES = {
  oil: "stroke:var(--oil)",
  foam: "stroke:var(--foam)",
  reference: "stroke:var(--reference);stroke-dasharray:6 4",
};
const PIN_R = 10;       // a memo pin's radius (DESIGN.md §2.3 --memo)
const PIN_RISE = 22;    // how far above its point a memo pin stands
const TIME_STEPS = [0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200];

/** The whole panel: every time column and the Glass from bottom to top. */
export function fitView(panel) {
  const { times } = panel;
  const dt = step(times);
  return { t0: times[0] - dt / 2, t1: times[times.length - 1] + dt / 2, h0: panel.bottom, h1: panel.top };
}

export function step(times) {
  return times.length > 1 ? (times[times.length - 1] - times[0]) / (times.length - 1) : 1;
}

/** Plot scales and their inverses. */
export function scales(view, width, height) {
  const pw = Math.max(1, width - INSET.left - INSET.right);
  const ph = Math.max(1, height - INSET.top - INSET.bottom);
  const sx = (t) => INSET.left + ((t - view.t0) / (view.t1 - view.t0)) * pw;
  const sy = (h) => INSET.top + ((view.h1 - h) / (view.h1 - view.h0)) * ph;
  const tx = (x) => view.t0 + ((x - INSET.left) / pw) * (view.t1 - view.t0);
  const hy = (y) => view.h1 - ((y - INSET.top) / ph) * (view.h1 - view.h0);
  return { sx, sy, tx, hy, pw, ph };
}

export function niceTicks(a, b, count) {
  const span = Math.abs(b - a);
  if (!(span > 0)) return [a];
  const raw = span / count;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const tick = [1, 2, 5, 10].map((f) => f * mag).find((s) => s >= raw) || 10 * mag;
  return ticksOf(a, b, tick);
}

function ticksOf(a, b, tick) {
  const out = [];
  for (let v = Math.ceil(Math.min(a, b) / tick) * tick; v <= Math.max(a, b) + 1e-9; v += tick) out.push(+v.toFixed(6));
  return out;
}

/** Ticks on minutes and seconds rather than on powers of ten. */
export function timeTicks(t0, t1, count) {
  const raw = (t1 - t0) / Math.max(1, count);
  return ticksOf(t0, t1, TIME_STEPS.find((s) => s >= raw) ?? TIME_STEPS[TIME_STEPS.length - 1]);
}

/** m:ss, or m:ss.s below a second's steps. */
export function tickLabel(t) {
  const sign = t < 0 ? "-" : "";
  const a = Math.abs(t);
  const minutes = Math.floor(a / 60);
  const seconds = a - minutes * 60;
  const text = Number.isInteger(Math.round(seconds * 10) / 10) ? String(Math.round(seconds)) : seconds.toFixed(1);
  return `${sign}${minutes}:${text.padStart(Number.isInteger(+text) ? 2 : 4, "0")}`;
}

/** The first index whose time is not before t. */
export function lowerBound(times, t) {
  let lo = 0, hi = times.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (times[mid] < t) lo = mid + 1; else hi = mid;
  }
  return lo;
}

/** An SVG path through the samples in view, broken where a sample is empty; a lone sample is a dot.
 * Where samples are denser than the pixels, each pixel column keeps its lowest and highest sample. */
export function linePath(times, values, sx, sy, view) {
  let first = 0, end = times.length;
  if (view) {
    first = Math.max(0, lowerBound(times, view.t0) - 1);
    end = Math.min(times.length, lowerBound(times, view.t1) + 1);
  }
  if (end <= first) return "";
  const dense = end - first > 2 * Math.abs(sx(times[end - 1]) - sx(times[first]));
  let d = "", run = 0;
  const point = (x, y) => {
    d += `${run ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`;
    run += 1;
  };
  const brk = () => {
    if (run === 1) d += "l0,0";
    run = 0;
  };
  if (!dense) {
    for (let i = first; i < end; i++) {
      const v = values[i];
      if (v === null || v === undefined) brk(); else point(sx(times[i]), sy(v));
    }
    brk();
    return d;
  }
  let column = null, low = 0, high = 0, lowFirst = true;
  const flush = () => {
    if (column === null) return;
    const a = sy(lowFirst ? low : high), b = sy(lowFirst ? high : low);
    point(column, a);
    if (Math.abs(a - b) >= 0.5) point(column, b);
    column = null;
  };
  for (let i = first; i < end; i++) {
    const v = values[i];
    if (v === null || v === undefined) {
      flush();
      brk();
      continue;
    }
    const x = Math.round(sx(times[i]));
    if (x !== column) {
      flush();
      column = x;
      low = high = v;
      lowFirst = true;
    } else if (v < low) {
      low = v;
      lowFirst = false;
    } else if (v > high) {
      high = v;
    }
  }
  flush();
  brk();
  return d;
}

function clip(id, width, height) {
  return `<defs><clipPath id="${id}-clip"><rect x="${INSET.left}" y="0" width="${width - INSET.left - INSET.right}" height="${height}"/></clipPath>`
    + `<pattern id="${id}-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">`
    + `<rect width="6" height="6" style="fill:rgba(138,138,138,0.12)"/><line x1="0" y1="0" x2="0" y2="6" style="stroke:var(--cannot-judge);stroke-width:1"/></pattern></defs>`;
}

function hline(y, x0, x1, style) {
  return `<line x1="${x0}" x2="${x1}" y1="${y}" y2="${y}" style="${style}"/>`;
}

function vband(s, t0, t1, height, style) {
  const x0 = s.sx(t0), x1 = s.sx(t1);
  return `<rect x="${Math.min(x0, x1)}" y="${INSET.top}" width="${Math.abs(x1 - x0)}" height="${height - INSET.top - INSET.bottom}" style="${style}"/>`;
}

function sampleSpan(times, first, end) {
  const half = step(times) / 2;
  return [times[first] - half, times[end - 1] + half];
}

function compressorLine(panel, s, height, label) {
  if (panel.compressor === null || panel.compressor === undefined) return "";
  const x = s.sx(panel.compressor);
  let out = `<line x1="${x}" x2="${x}" y1="${INSET.top}" y2="${height - INSET.bottom}" style="stroke:var(--compressor);stroke-width:1.5;stroke-dasharray:4 3"/>`;
  if (label) out += `<text x="${x + 4}" y="${INSET.top + 12}" style="${TEXT};fill:var(--compressor);font-weight:600">기동</text>`;
  return out;
}

function levelBands(panel, s, height) {
  const parts = [];
  for (const run of panel.levels ?? []) {
    const [t0, t1] = sampleSpan(panel.times, run.first, run.end);
    const full = run.state === "FULL_NO_INTERFACE";
    parts.push(vband(s, t0, t1, height, `fill:var(${full ? "--full-band" : "--empty-band"})`));
    parts.push(`<text x="${s.sx(t0) + 4}" y="${height - INSET.bottom - 4}" style="${TEXT};font-weight:600;fill:var(${full ? "--oil" : "--fg-3"})">${full ? "FULL" : "EMPTY"}</text>`);
  }
  return parts.join("");
}

function cannotJudge(panel, s, height, id) {
  return (panel.cannot ?? []).map((c) => vband(s, c.start_sec, c.end_sec, height, `fill:url(#${id}-hatch)`)).join("");
}

/** The graph's back layer: grid, Glass top and bottom, zero line, bands and the compressor start. */
export function graphBack(panel, view, width, height, id) {
  const s = scales(view, width, height);
  const right = width - INSET.right;
  const parts = [clip(id, width, height)];
  for (const t of timeTicks(view.t0, view.t1, Math.max(2, Math.floor(width / 90)))) {
    parts.push(`<line x1="${s.sx(t)}" x2="${s.sx(t)}" y1="${INSET.top}" y2="${height - INSET.bottom}" style="stroke:var(--stroke-3)"/>`);
  }
  for (const h of niceTicks(view.h0, view.h1, Math.max(2, Math.floor(height / 40)))) {
    parts.push(hline(s.sy(h), INSET.left, right, "stroke:var(--stroke-2)"));
    parts.push(`<text x="${INSET.left - 8}" y="${s.sy(h) + 4}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">${Math.round(h)}</text>`);
  }
  parts.push(`<g clip-path="url(#${id}-clip)">${levelBands(panel, s, height)}${cannotJudge(panel, s, height, id)}</g>`);
  parts.push(hline(s.sy(panel.top), INSET.left, right, "stroke:var(--stroke-1)"));
  parts.push(`<text x="${right - 4}" y="${s.sy(panel.top) - 3}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">Glass 위</text>`);
  parts.push(hline(s.sy(panel.bottom), INSET.left, right, "stroke:var(--stroke-1)"));
  parts.push(hline(s.sy(0), INSET.left, right, "stroke:var(--reference);stroke-width:1.5;stroke-dasharray:6 4"));
  parts.push(`<text x="${right - 4}" y="${s.sy(0) - 4}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">0선</text>`);
  parts.push(`<g clip-path="url(#${id}-clip)">${compressorLine(panel, s, height, true)}</g>`);
  return parts.join("");
}

/** The context image's back layer: the picture (or the background view) and the stretch marks. */
export function contextBack(panel, view, width, height, id) {
  const s = scales(view, width, height);
  const parts = [clip(id, width, height), `<g clip-path="url(#${id}-clip)">`];
  const image = panel.image;
  if (image) {
    const dt = step(panel.times);
    const y0 = s.sy(image.top + 0.5), y1 = s.sy(image.top + 0.5 - image.rows);
    for (const piece of image.pieces) {
      if (!piece.href) continue;
      const x0 = s.sx(panel.times[piece.first] - dt / 2);
      const x1 = s.sx(panel.times[piece.first + piece.count - 1] + dt / 2);
      parts.push(`<image href="${piece.href}" x="${x0}" y="${y0}" width="${x1 - x0}" height="${y1 - y0}" preserveAspectRatio="none"/>`);
    }
  }
  parts.push(cannotJudge(panel, s, height, id), compressorLine(panel, s, height, false), "</g>");
  parts.push(`<text x="${INSET.left - 8}" y="${s.sy(panel.top) + 10}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">위</text>`);
  parts.push(`<text x="${INSET.left - 8}" y="${s.sy(panel.bottom)}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">아래</text>`);
  return parts.join("");
}

/** The lines layer. `halo` sets them off a picture; `hot` (a kind) draws that line 3 px wide. */
export function linesSvg(panel, view, width, height, id, { halo = false, hot = null } = {}) {
  const s = scales(view, width, height);
  const parts = [`<g clip-path="url(#${id}-clip)">`];
  for (const kind of KINDS) {
    const values = panel.lines?.[kind];
    if (!values) continue;
    const d = linePath(panel.times, values, s.sx, s.sy, view);
    if (!d) continue;
    const wide = kind === hot ? 3 : kind === "reference" ? 1.5 : 2;
    if (halo) parts.push(`<path d="${d}" style="stroke:var(--line-halo);stroke-width:${wide + 3};${SHAPE}"/>`);
    parts.push(`<path data-kind="${kind}" d="${d}" style="${STROKES[kind]};stroke-width:${wide};${SHAPE}"/>`);
  }
  parts.push("</g>");
  return parts.join("");
}

/** The marks layer: the selected range, the grab-width preview, the point line in progress and the
 * playhead. */
export function marksSvg(marks, view, width, height, id) {
  const s = scales(view, width, height);
  const parts = [`<g clip-path="url(#${id}-clip)">`];
  if (marks.grab) {
    parts.push(vband(s, marks.grab.t0, marks.grab.t1, height, `fill:var(--${marks.grab.kind});fill-opacity:0.15`));
  }
  if (marks.selection) {
    const { t0, t1 } = marks.selection;
    parts.push(vband(s, t0, t1, height, "fill:var(--selection-band)"));
    for (const t of [t0, t1]) {
      parts.push(`<line x1="${s.sx(t)}" x2="${s.sx(t)}" y1="0" y2="${height}" style="stroke:var(--brand);stroke-width:1"/>`);
    }
  }
  if (marks.compressor !== null && marks.compressor !== undefined) {
    parts.push(compressorLine(marks, s, height, id === "graph"));
  }
  for (const memo of marks.memos ?? []) parts.push(memoPin(memo, s));
  if (marks.point) parts.push(pointLine(marks.point, s, view));
  if (marks.playhead !== null && marks.playhead !== undefined) {
    const x = s.sx(marks.playhead);
    parts.push(`<line x1="${x}" x2="${x}" y1="0" y2="${height}" style="stroke:var(--playhead);stroke-width:1"/>`);
  }
  parts.push("</g>");
  return parts.join("");
}

/** The point line in progress (Product SSOT §6): the traced path dashed, the preview to the pointer
 * and the straight guides dotted until their paths arrive, and the points. */
function pointLine(point, s, view) {
  const stroke = `stroke:var(--${point.kind})`;
  const parts = [];
  const path = (piece, style, halo) => {
    const d = piece && linePath(piece.times, piece.hs, s.sx, s.sy, view);
    if (!d) return;
    if (halo) parts.push(`<path d="${d}" style="stroke:var(--line-halo);stroke-width:5;${SHAPE}"/>`);
    parts.push(`<path d="${d}" style="${style};${SHAPE}"/>`);
  };
  path(point.path, `${stroke};stroke-width:2;stroke-dasharray:5 3`, true);
  path(point.preview, `${stroke};stroke-width:1;stroke-dasharray:2 3`, false);
  for (const [a, b] of point.guides ?? []) {
    parts.push(`<line x1="${s.sx(a.t)}" y1="${s.sy(a.h)}" x2="${s.sx(b.t)}" y2="${s.sy(b.h)}" style="${stroke};stroke-width:1;stroke-dasharray:2 3"/>`);
  }
  for (const p of point.points) {
    parts.push(`<circle data-point cx="${s.sx(p.t)}" cy="${s.sy(p.h)}" r="5" style="fill:var(--bg-1);${stroke};stroke-width:2"/>`);
  }
  return parts.join("");
}

/** Where a memo's pin stands: above its point, or below it near the top; a memo pinned to a time
 * alone stands at the top. */
export function memoPinAt(memo, s) {
  const x = s.sx(memo.t);
  const base = memo.h === null ? INSET.top : s.sy(memo.h);
  const y = base - PIN_RISE - PIN_R < 0 ? base + PIN_RISE : base - PIN_RISE;
  return { x, y, base, r: PIN_R };
}

function memoPin(memo, s) {
  const { x, y, base, r } = memoPinAt(memo, s);
  return `<g data-memo="${memo.n}"><line x1="${x}" x2="${x}" y1="${base}" y2="${y}" style="stroke:var(--memo);stroke-width:1"/>`
    + `<circle cx="${x}" cy="${y}" r="${r}" style="fill:var(--memo)"/>`
    + `<text x="${x}" y="${y + 4}" text-anchor="middle" style="${TEXT};fill:var(--bg-1);font-weight:600">${memo.n}</text></g>`;
}

/** The graph in one piece: what the report shows. */
export function graphSvg(panel, view, width, height, id) {
  return graphBack(panel, view, width, height, id) + linesSvg(panel, view, width, height, id);
}

/** The context image in one piece, with its lines. */
export function contextSvg(panel, view, width, height, id) {
  return contextBack(panel, view, width, height, id) + linesSvg(panel, view, width, height, id, { halo: true });
}

/** The shared time axis, with the empty stretches as bars along its top edge and the playhead. */
export function axisSvg(view, width, { times = null, empty = [], playhead = null } = {}) {
  const s = scales(view, width, 32);
  const parts = [];
  if (times) {
    for (const run of empty) {
      const [t0, t1] = sampleSpan(times, run.first, run.end);
      const x0 = Math.max(INSET.left, s.sx(t0)), x1 = Math.min(width - INSET.right, s.sx(t1));
      if (x1 > x0) parts.push(`<rect x="${x0}" y="0" width="${Math.max(2, x1 - x0)}" height="4" style="fill:var(--empty-mark)"/>`);
    }
  }
  for (const t of timeTicks(view.t0, view.t1, Math.max(2, Math.floor(width / 90)))) {
    const x = s.sx(t);
    if (x < INSET.left + 40 || x > width - INSET.right - 40) continue;  // the range numbers sit at the ends
    parts.push(`<line x1="${x}" x2="${x}" y1="4" y2="9" style="stroke:var(--stroke-1)"/>`);
    parts.push(`<text x="${x}" y="22" text-anchor="middle" style="${TEXT};fill:var(--fg-3)">${tickLabel(t)}</text>`);
  }
  if (playhead !== null && playhead >= view.t0 && playhead <= view.t1) {
    const x = s.sx(playhead);
    parts.push(`<path d="M${x - 5},0L${x + 5},0L${x},6Z" style="fill:var(--playhead)"/>`);
  }
  return parts.join("");
}
