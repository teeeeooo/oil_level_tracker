// Panel drawing shared by the editor and the report. No DOM state lives here.
(function () {
  "use strict";

  const COLORS = { oil: "#1d4ed8", foam: "#d97706", ref: "#6b7280" };
  const KIND_LABELS = { oil: "Oil", foam: "Foam", ref: "참고선" };
  const SEGMENT_STYLE = {
    FULL: { fill: "rgba(22,163,74,0.18)", label: "FULL" },
    EMPTY: { fill: "rgba(220,38,38,0.16)", label: "EMPTY" },
    UNKNOWN: { fill: "rgba(107,114,128,0.22)", label: "판독 불가" },
  };
  const MARGIN = { left: 52, right: 10, top: 8, bottom: 22 };

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // ---- geometry -------------------------------------------------------------------
  function contextGeometry(meta) {
    const times = meta.context.times;
    const dt = times.length > 1 ? (times[times.length - 1] - times[0]) / (times.length - 1) : 1;
    const top = meta.glass.zero_y - meta.context.y0 + 0.5; // height of the image's top edge
    return { times, dt, top, bottom: top - meta.context.rows, t0: times[0] - dt / 2, t1: times[times.length - 1] + dt / 2 };
  }

  function fitView(meta) {
    const g = contextGeometry(meta);
    return { t0: g.t0, t1: g.t1, h0: g.bottom, h1: g.top };
  }

  function scales(view, width, height) {
    const pw = Math.max(1, width - MARGIN.left - MARGIN.right);
    const ph = Math.max(1, height - MARGIN.top - MARGIN.bottom);
    const sx = (t) => MARGIN.left + ((t - view.t0) / (view.t1 - view.t0)) * pw;
    const sy = (h) => MARGIN.top + ((view.h1 - h) / (view.h1 - view.h0)) * ph;
    const tx = (x) => view.t0 + ((x - MARGIN.left) / pw) * (view.t1 - view.t0);
    const hy = (y) => view.h1 - ((y - MARGIN.top) / ph) * (view.h1 - view.h0);
    return { sx, sy, tx, hy, pw, ph };
  }

  // ---- curve: monotone cubic through the points, corners break the tangent ----------
  function tangents(points) {
    const n = points.length;
    const d = [];
    for (let k = 0; k < n - 1; k++) {
      const dt = points[k + 1].t - points[k].t;
      d.push(dt > 0 ? (points[k + 1].h - points[k].h) / dt : 0);
    }
    const mL = new Array(n).fill(0);
    const mR = new Array(n).fill(0);
    for (let k = 0; k < n; k++) {
      if (k === 0) { mL[k] = mR[k] = d[0] || 0; continue; }
      if (k === n - 1) { mL[k] = mR[k] = d[k - 1]; continue; }
      if (points[k].corner) { mL[k] = d[k - 1]; mR[k] = d[k]; continue; }
      const d0 = d[k - 1], d1 = d[k];
      if (d0 * d1 <= 0) { mL[k] = mR[k] = 0; continue; }
      const h0 = points[k].t - points[k - 1].t, h1 = points[k + 1].t - points[k].t;
      // Fritsch-Butland weighted harmonic mean: monotone, no overshoot.
      const m = (3 * (h0 + h1)) / ((2 * h1 + h0) / d0 + (h1 + 2 * h0) / d1);
      mL[k] = mR[k] = m;
    }
    return { mL, mR };
  }

  function curvePath(points, sx, sy) {
    if (points.length === 0) return "";
    const { mL, mR } = tangents(points);
    let d = `M${sx(points[0].t).toFixed(1)},${sy(points[0].h).toFixed(1)}`;
    for (let k = 0; k < points.length - 1; k++) {
      const p = points[k], q = points[k + 1];
      const dt = (q.t - p.t) / 3;
      d += `C${sx(p.t + dt).toFixed(1)},${sy(p.h + mR[k] * dt).toFixed(1)} ` +
        `${sx(q.t - dt).toFixed(1)},${sy(q.h - mL[k + 1] * dt).toFixed(1)} ` +
        `${sx(q.t).toFixed(1)},${sy(q.h).toFixed(1)}`;
    }
    return d;
  }

  function sampleAt(points, t) {
    const n = points.length;
    if (n === 0 || t < points[0].t || t > points[n - 1].t) return null;
    if (n === 1) return points[0].h;
    let k = 0;
    while (k < n - 2 && points[k + 1].t < t) k++;
    const p = points[k], q = points[k + 1];
    const span = q.t - p.t;
    if (span <= 0) return p.h;
    const { mL, mR } = tangents(points);
    const s = (t - p.t) / span, s2 = s * s, s3 = s2 * s;
    return (2 * s3 - 3 * s2 + 1) * p.h + (s3 - 2 * s2 + s) * span * mR[k] +
      (-2 * s3 + 3 * s2) * q.h + (s3 - s2) * span * mL[k + 1];
  }

  function niceTicks(a, b, count) {
    const span = Math.abs(b - a);
    if (!(span > 0)) return [a];
    const raw = span / count;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 5, 10].map((f) => f * mag).find((s) => s >= raw) || 10 * mag;
    const out = [];
    for (let v = Math.ceil(Math.min(a, b) / step) * step; v <= Math.max(a, b) + 1e-9; v += step) out.push(+v.toFixed(6));
    return out;
  }

  // ---- panel ------------------------------------------------------------------------
  // opts: {doc, meta, view, width, height, image, editable, selection, frameTime, id}
  function drawPanel(svg, opts) {
    const { doc, view, width, height } = opts;
    const { sx, sy } = scales(view, width, height);
    const clip = `clip-${opts.id}`;
    const parts = [];
    parts.push(`<defs><clipPath id="${clip}"><rect x="${MARGIN.left}" y="${MARGIN.top}" ` +
      `width="${width - MARGIN.left - MARGIN.right}" height="${height - MARGIN.top - MARGIN.bottom}"/></clipPath></defs>`);
    parts.push(`<rect class="plot-bg" x="${MARGIN.left}" y="${MARGIN.top}" width="${width - MARGIN.left - MARGIN.right}" ` +
      `height="${height - MARGIN.top - MARGIN.bottom}"/>`);
    parts.push(`<g clip-path="url(#${clip})">`);

    if (opts.image) {
      const g = contextGeometry(opts.meta);
      const x0 = sx(g.t0), x1 = sx(g.t1), y0 = sy(g.top), y1 = sy(g.bottom);
      parts.push(`<image href="${opts.image}" x="${x0}" y="${y0}" width="${x1 - x0}" height="${y1 - y0}" ` +
        `preserveAspectRatio="none" class="context-image"/>`);
    }

    // grid
    for (const t of niceTicks(view.t0, view.t1, Math.max(2, Math.floor(width / 90)))) {
      parts.push(`<line class="grid" x1="${sx(t)}" x2="${sx(t)}" y1="${MARGIN.top}" y2="${height - MARGIN.bottom}"/>`);
    }
    for (const h of niceTicks(view.h0, view.h1, Math.max(2, Math.floor(height / 50)))) {
      parts.push(`<line class="grid" x1="${MARGIN.left}" x2="${width - MARGIN.right}" y1="${sy(h)}" y2="${sy(h)}"/>`);
    }

    // segments
    (doc.segments || []).forEach((seg, i) => {
      const style = SEGMENT_STYLE[seg.state] || SEGMENT_STYLE.UNKNOWN;
      const a = sx(Math.min(seg.t0, seg.t1)), b = sx(Math.max(seg.t0, seg.t1));
      const selected = opts.selection && opts.selection.type === "segment" && opts.selection.idx === i;
      parts.push(`<rect data-kind="segment" data-idx="${i}" class="segment${selected ? " selected" : ""}" x="${a}" ` +
        `y="${MARGIN.top}" width="${Math.max(1, b - a)}" height="${height - MARGIN.top - MARGIN.bottom}" fill="${style.fill}"/>`);
      parts.push(`<text class="segment-label" x="${a + 4}" y="${MARGIN.top + 13}">${style.label}</text>`);
      if (opts.editable) {
        for (const edge of ["t0", "t1"]) {
          parts.push(`<rect data-kind="segedge" data-idx="${i}" data-edge="${edge}" class="segedge" ` +
            `x="${sx(seg[edge]) - 4}" y="${MARGIN.top}" width="8" height="${height - MARGIN.top - MARGIN.bottom}"/>`);
        }
      }
    });

    // zero line
    parts.push(`<line class="zero-line" x1="${MARGIN.left}" x2="${width - MARGIN.right}" y1="${sy(0)}" y2="${sy(0)}"/>`);

    // lines
    (doc.lines || []).forEach((line, li) => {
      const color = COLORS[line.kind] || COLORS.ref;
      const active = opts.activeLine === line.id;
      if (line.points.length > 1) {
        parts.push(`<path class="curve curve-${line.kind}${active ? " active" : ""}" d="${curvePath(line.points, sx, sy)}" ` +
          `stroke="${color}"/>`);
      }
      if (!opts.editable && line.points.length !== 1) return;
      line.points.forEach((p, pi) => {
        const x = sx(p.t), y = sy(p.h);
        if (x < MARGIN.left - 8 || x > width - MARGIN.right + 8) return;
        const sel = opts.selection && opts.selection.type === "point" && opts.selection.line === li && opts.selection.idx === pi;
        const r = sel ? 6 : 4;
        const attrs = `data-kind="point" data-line="${li}" data-idx="${pi}" class="point${sel ? " selected" : ""}" ` +
          `stroke="${color}"`;
        parts.push(p.corner
          ? `<rect ${attrs} x="${x - r}" y="${y - r}" width="${2 * r}" height="${2 * r}"/>`
          : `<circle ${attrs} cx="${x}" cy="${y}" r="${r}"/>`);
      });
    });

    // memos
    (doc.memos || []).forEach((memo, i) => {
      const sel = opts.selection && opts.selection.type === "memo" && opts.selection.idx === i;
      parts.push(`<g data-kind="memo" data-idx="${i}" class="memo${sel ? " selected" : ""}">` +
        `<circle cx="${sx(memo.t)}" cy="${sy(memo.h)}" r="9"/>` +
        `<text x="${sx(memo.t)}" y="${sy(memo.h) + 4}">${i + 1}</text></g>`);
    });

    if (opts.frameTime != null) {
      parts.push(`<line class="frame-cursor" x1="${sx(opts.frameTime)}" x2="${sx(opts.frameTime)}" ` +
        `y1="${MARGIN.top}" y2="${height - MARGIN.bottom}"/>`);
    }
    parts.push(`</g>`);

    // axes labels
    for (const t of niceTicks(view.t0, view.t1, Math.max(2, Math.floor(width / 90)))) {
      parts.push(`<text class="tick" x="${sx(t)}" y="${height - 6}" text-anchor="middle">${t}</text>`);
    }
    for (const h of niceTicks(view.h0, view.h1, Math.max(2, Math.floor(height / 50)))) {
      parts.push(`<text class="tick" x="${MARGIN.left - 6}" y="${sy(h) + 4}" text-anchor="end">${h}</text>`);
    }
    parts.push(`<rect class="plot-frame" x="${MARGIN.left}" y="${MARGIN.top}" width="${width - MARGIN.left - MARGIN.right}" ` +
      `height="${height - MARGIN.top - MARGIN.bottom}"/>`);

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.innerHTML = parts.join("");
  }

  // ---- report -------------------------------------------------------------------------
  function renderReport(root, data) {
    const meta = data.meta, doc = data.doc;
    const memos = (doc.memos || []).map((m, i) =>
      `<li>${m.t.toFixed(1)} s · ${Math.round(m.h)} px — ${escapeHtml(m.text || "")}</li>`).join("");
    root.innerHTML = `
      <header class="report-head">
        <h1>유면 보고서 <small>(spike, v${String(data.version).padStart(3, "0")})</small></h1>
        <button class="no-print" onclick="window.print()">인쇄 / PDF 저장</button>
      </header>
      <table class="meta-table">
        <tr><th>영상</th><td>${escapeHtml(meta.video.name)}</td><th>Glass</th><td>${escapeHtml(meta.glass.name)}</td></tr>
        <tr><th>작성</th><td>${escapeHtml(data.created_at)}</td><th>판정</th><td>spike 범위 밖 (계산 안 함)</td></tr>
      </table>
      <h2>그래프 <span class="legend">${legend()}</span></h2>
      <svg id="r-graph" class="report-panel"></svg>
      <h2>맥락 이미지 (편집된 선 겹침)</h2>
      <svg id="r-context" class="report-panel"></svg>
      <h2>메모</h2>
      <ol class="memo-report">${memos || "<li>없음</li>"}</ol>`;
    const view = fitView(meta);
    drawPanel(root.querySelector("#r-graph"), { id: "r-graph", doc, meta, view, width: 1000, height: 240 });
    drawPanel(root.querySelector("#r-context"), { id: "r-context", doc, meta, view, width: 1000, height: 260, image: data.context_png });
  }

  function legend() {
    return Object.entries(KIND_LABELS).map(([kind, label]) =>
      `<span class="legend-item"><i style="background:${COLORS[kind]}"></i>${label}</span>`).join("") +
      Object.values(SEGMENT_STYLE).map((s) =>
        `<span class="legend-item"><i style="background:${s.fill}"></i>${s.label}</span>`).join("");
  }

  window.Render = { COLORS, KIND_LABELS, SEGMENT_STYLE, MARGIN, contextGeometry, fitView, scales, tangents, curvePath,
    sampleAt, niceTicks, drawPanel, renderReport, escapeHtml, legend };
})();
