// Drawing shared by the editor and the report (architecture.md, "One drawing module"). It draws only
// what it receives, as SVG text: no screen state and no API, so the report can inline it.
// Ported in part from spike/webui:spikes/webui/static/render.js (scales, niceTicks, the panel
// layering). v2 lines are dense samples (Product SSOT §4), drawn with a gap where a sample is empty.
//
// A panel is one Glass:
//   { times: [s], oil: [h or null], top: h, bottom: h, compressor: s or null,
//     image: { top: h, rows, pieces: [{ href, first, count }] } or null }
// where h is a height in source px above the zero line (the Glass top has the largest h).

export const INSET = { left: 52, right: 16, top: 14, bottom: 10 };  // DESIGN.md §7: no line clipped at the edge

const TEXT = "font-size:12px;font-family:var(--font);font-variant-numeric:tabular-nums";

/** The whole panel: every time column and the Glass from bottom to top. */
export function fitView(panel) {
  const { times } = panel;
  const dt = step(times);
  return { t0: times[0] - dt / 2, t1: times[times.length - 1] + dt / 2, h0: panel.bottom, h1: panel.top };
}

function step(times) {
  return times.length > 1 ? (times[times.length - 1] - times[0]) / (times.length - 1) : 1;
}

export function scales(view, width, height) {
  const pw = Math.max(1, width - INSET.left - INSET.right);
  const ph = Math.max(1, height - INSET.top - INSET.bottom);
  const sx = (t) => INSET.left + ((t - view.t0) / (view.t1 - view.t0)) * pw;
  const sy = (h) => INSET.top + ((view.h1 - h) / (view.h1 - view.h0)) * ph;
  return { sx, sy, pw, ph };
}

export function niceTicks(a, b, count) {
  const span = Math.abs(b - a);
  if (!(span > 0)) return [a];
  const raw = span / count;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const tick = [1, 2, 5, 10].map((f) => f * mag).find((s) => s >= raw) || 10 * mag;
  const out = [];
  for (let v = Math.ceil(Math.min(a, b) / tick) * tick; v <= Math.max(a, b) + 1e-9; v += tick) out.push(+v.toFixed(6));
  return out;
}

/** An SVG path through the samples, broken where a sample is empty; a lone sample is a dot. */
export function linePath(times, values, sx, sy) {
  let d = "";
  let run = 0;
  for (let i = 0; i <= times.length; i++) {
    const v = i < times.length ? values[i] : null;
    if (v === null || v === undefined) {
      if (run === 1) d += "l0,0";
      run = 0;
      continue;
    }
    d += `${run ? "L" : "M"}${sx(times[i]).toFixed(1)},${sy(v).toFixed(1)}`;
    run += 1;
  }
  return d;
}

function clip(id, width, height) {
  return `<defs><clipPath id="${id}"><rect x="${INSET.left}" y="0" width="${width - INSET.left - INSET.right}" height="${height}"/></clipPath></defs>`;
}

function hline(y, x0, x1, style) {
  return `<line x1="${x0}" x2="${x1}" y1="${y}" y2="${y}" style="${style}"/>`;
}

function compressorLine(panel, s, height, label) {
  if (panel.compressor === null || panel.compressor === undefined) return "";
  const x = s.sx(panel.compressor);
  let out = `<line x1="${x}" x2="${x}" y1="${INSET.top}" y2="${height - INSET.bottom}" style="stroke:var(--compressor);stroke-width:1.5;stroke-dasharray:4 3"/>`;
  if (label) out += `<text x="${x + 4}" y="${INSET.top + 12}" style="${TEXT};fill:var(--compressor);font-weight:600">기동</text>`;
  return out;
}

function oilLine(panel, s, halo) {
  const d = linePath(panel.times, panel.oil, s.sx, s.sy);
  const shape = "fill:none;stroke-linejoin:round;stroke-linecap:round";
  const under = halo ? `<path d="${d}" style="stroke:var(--line-halo);stroke-width:5;${shape}"/>` : "";
  return `${under}<path d="${d}" style="stroke:var(--oil);stroke-width:2;${shape}"/>`;
}

/** The graph: the Oil line against height from the zero line, with the Glass top and bottom. */
export function graphSvg(panel, view, width, height, id) {
  const s = scales(view, width, height);
  const right = width - INSET.right;
  const parts = [clip(`${id}-clip`, width, height)];
  for (const t of niceTicks(view.t0, view.t1, Math.max(2, Math.floor(width / 90)))) {
    parts.push(`<line x1="${s.sx(t)}" x2="${s.sx(t)}" y1="${INSET.top}" y2="${height - INSET.bottom}" style="stroke:var(--stroke-3)"/>`);
  }
  for (const h of niceTicks(view.h0, view.h1, Math.max(2, Math.floor(height / 40)))) {
    parts.push(hline(s.sy(h), INSET.left, right, "stroke:var(--stroke-2)"));
    parts.push(`<text x="${INSET.left - 8}" y="${s.sy(h) + 4}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">${Math.round(h)}</text>`);
  }
  parts.push(hline(s.sy(panel.top), INSET.left, right, "stroke:var(--stroke-1)"));
  parts.push(`<text x="${right - 4}" y="${s.sy(panel.top) - 3}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">Glass 위</text>`);
  parts.push(hline(s.sy(panel.bottom), INSET.left, right, "stroke:var(--stroke-1)"));
  parts.push(hline(s.sy(0), INSET.left, right, "stroke:var(--reference);stroke-width:1.5;stroke-dasharray:6 4"));
  parts.push(`<text x="${right - 4}" y="${s.sy(0) - 4}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">0선</text>`);
  parts.push(`<g clip-path="url(#${id}-clip)">${compressorLine(panel, s, height, true)}${oilLine(panel, s, false)}</g>`);
  return parts.join("");
}

/** The context image (or the background view) with the Oil line over it. */
export function contextSvg(panel, view, width, height, id) {
  const s = scales(view, width, height);
  const parts = [clip(`${id}-clip`, width, height), `<g clip-path="url(#${id}-clip)">`];
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
  parts.push(compressorLine(panel, s, height, false), oilLine(panel, s, true), "</g>");
  parts.push(`<text x="${INSET.left - 8}" y="${s.sy(panel.top) + 10}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">위</text>`);
  parts.push(`<text x="${INSET.left - 8}" y="${s.sy(panel.bottom)}" text-anchor="end" style="${TEXT};fill:var(--fg-3)">아래</text>`);
  return parts.join("");
}

/** The shared time axis, in seconds. */
export function axisSvg(view, width) {
  const s = scales(view, width, 32);
  const parts = [];
  for (const t of niceTicks(view.t0, view.t1, Math.max(2, Math.floor(width / 90)))) {
    const x = s.sx(t);
    parts.push(`<line x1="${x}" x2="${x}" y1="0" y2="5" style="stroke:var(--stroke-1)"/>`);
    parts.push(`<text x="${x}" y="20" text-anchor="middle" style="${TEXT};fill:var(--fg-3)">${t}</text>`);
  }
  parts.push(`<text x="${INSET.left - 30}" y="20" text-anchor="middle" style="${TEXT};fill:var(--fg-3)">s</text>`);
  return parts.join("");
}
