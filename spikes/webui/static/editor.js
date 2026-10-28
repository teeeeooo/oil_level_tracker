// Editor interaction for the web UI spike. Drawing is in render.js.
(function () {
  "use strict";
  const R = window.Render;
  const $ = (id) => document.getElementById(id);
  const PANELS = ["graphPanel", "contextPanel"];
  const SNAP_RADIUS_ROWS = 8;
  const MIN_POINT_GAP_SEC = 0.01;

  const state = {
    meta: null, doc: null, view: null, savedVersion: 0,
    tool: "select", activeLine: null, selection: null, frameTime: null,
    undo: [], redo: [], drag: null, luma: null, dirty: false,
    images: { context: "/api/context.png", background: "/api/context_bg.png" },
    stats: { seeks: [], decodes: [], renders: [] },
  };

  // ---- startup ----------------------------------------------------------------------
  async function init() {
    state.meta = await (await fetch("/api/meta")).json();
    const saved = state.meta.saved;
    state.doc = saved ? stripSaveFields(saved.doc) : {
      schema: "webui-spike-1", lines: clone(state.meta.draft.lines), segments: [], memos: [],
    };
    state.savedVersion = saved ? saved.version : 0;
    state.activeLine = state.doc.lines.length ? state.doc.lines[0].id : null;
    state.view = R.fitView(state.meta);
    await loadLuma();
    bindUi();
    setTool("select");
    refreshLineSelect();
    render();
    setStatus(saved ? `저장본 v${pad(saved.version)} 불러옴` : "초안 (naive draft) 로드됨");
    postLog({ key: "ui", engine: engineName(), panels_px: PANELS.map((id) => $(id).clientWidth + "x" + $(id).clientHeight).join(",") });
  }

  function stripSaveFields(doc) {
    const copy = clone(doc);
    delete copy.saved_at; delete copy.version;
    return copy;
  }

  async function loadLuma() {
    const img = new Image();
    img.src = state.images.context;
    await img.decode();
    const canvas = document.createElement("canvas");
    canvas.width = img.width; canvas.height = img.height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);
    const rgba = ctx.getImageData(0, 0, img.width, img.height).data;
    const luma = new Float32Array(img.width * img.height);
    for (let i = 0; i < luma.length; i++) luma[i] = 0.299 * rgba[4 * i] + 0.587 * rgba[4 * i + 1] + 0.114 * rgba[4 * i + 2];
    state.luma = { data: luma, width: img.width, height: img.height };
  }

  // ---- helpers ----------------------------------------------------------------------
  const clone = (v) => JSON.parse(JSON.stringify(v));
  const pad = (n) => String(n).padStart(3, "0");
  const lineById = (id) => state.doc.lines.find((l) => l.id === id);
  const median = (xs) => { if (!xs.length) return null; const s = [...xs].sort((a, b) => a - b); return s[Math.floor(s.length / 2)]; };

  function engineName() {
    const ua = navigator.userAgent;
    const edge = ua.match(/Edg\/([\d.]+)/);
    if (edge) return "WebView2 Edg/" + edge[1];
    const chrome = ua.match(/Chrome\/([\d.]+)/);
    if (chrome) return "Chromium " + chrome[1];
    const webkit = ua.match(/AppleWebKit\/([\d.]+)/);
    return webkit ? "WebKit " + webkit[1] : ua;
  }

  function pushUndo() {
    state.undo.push(JSON.stringify(state.doc));
    if (state.undo.length > 200) state.undo.shift();
    state.redo = [];
    state.dirty = true;
  }
  function undo() {
    if (!state.undo.length) return;
    state.redo.push(JSON.stringify(state.doc));
    state.doc = JSON.parse(state.undo.pop());
    afterHistory();
  }
  function redo() {
    if (!state.redo.length) return;
    state.undo.push(JSON.stringify(state.doc));
    state.doc = JSON.parse(state.redo.pop());
    afterHistory();
  }
  function afterHistory() {
    state.selection = null;
    if (!lineById(state.activeLine)) state.activeLine = state.doc.lines.length ? state.doc.lines[0].id : null;
    refreshLineSelect();
    render();
  }

  function setStatus(text) { $("status").textContent = text; }

  function postLog(body) {
    fetch("/api/log", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).catch(() => {});
  }

  function panelGeometry(svg) {
    const box = svg.getBoundingClientRect();
    return { width: Math.max(200, Math.round(box.width)), height: Math.max(100, Math.round(box.height)), box };
  }

  function eventToData(svg, e) {
    const { width, height, box } = panelGeometry(svg);
    const x = ((e.clientX - box.left) / box.width) * width;
    const y = ((e.clientY - box.top) / box.height) * height;
    const s = R.scales(state.view, width, height);
    return { x, y, t: s.tx(x), h: s.hy(y), s, width, height, box };
  }

  function columnOf(t) {
    const times = state.meta.context.times;
    let lo = 0, hi = times.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (times[mid] < t) lo = mid; else hi = mid; }
    return Math.abs(times[lo] - t) <= Math.abs(times[hi] - t) ? lo : hi;
  }

  function snapHeight(t, h) {
    if (!$("snap").checked || !state.luma) return h;
    const { data, width, height } = state.luma;
    const c = columnOf(t);
    const zero = state.meta.glass.zero_y, y0 = state.meta.context.y0;
    const r0 = Math.round(zero - h - y0);
    let best = null, bestValue = -1;
    for (let r = Math.max(1, r0 - SNAP_RADIUS_ROWS); r <= Math.min(height - 2, r0 + SNAP_RADIUS_ROWS); r++) {
      const g = Math.abs(data[(r + 1) * width + c] - data[(r - 1) * width + c]);
      if (g > bestValue) { bestValue = g; best = r; }
    }
    return best == null ? h : zero - (y0 + best);
  }

  // ---- rendering --------------------------------------------------------------------
  let frameRequested = false;
  function render() {
    if (frameRequested) return;
    frameRequested = true;
    requestAnimationFrame(() => {
      frameRequested = false;
      const began = performance.now();
      for (const id of PANELS) {
        const svg = $(id);
        const { width, height } = panelGeometry(svg);
        R.drawPanel(svg, {
          id, doc: state.doc, meta: state.meta, view: state.view, width, height, editable: true,
          selection: state.selection, activeLine: state.activeLine, frameTime: state.frameTime,
          image: id === "contextPanel" ? ($("bgView").checked ? state.images.background : state.images.context) : null,
        });
      }
      const ms = performance.now() - began;
      state.stats.renders.push(ms);
      if (state.stats.renders.length > 500) state.stats.renders.shift();
      drawFrameOverlay();
      refreshSide();
    });
  }

  function refreshSide() {
    const sel = state.selection;
    const memoText = $("memoText");
    let info = "없음";
    let showMemo = false; // set hidden once: toggling it on a focused textarea blurs it
    if (sel && sel.type === "point") {
      const line = state.doc.lines[sel.line];
      const p = line && line.points[sel.idx];
      if (p) info = `${R.KIND_LABELS[line.kind]} 점 ${sel.idx + 1}/${line.points.length} · ${p.t.toFixed(2)} s · ${p.h.toFixed(1)} px` +
        (p.corner ? " · 꼭짓점" : "");
    } else if (sel && sel.type === "segment") {
      const seg = state.doc.segments[sel.idx];
      if (seg) info = `${R.SEGMENT_STYLE[seg.state].label} 구간 · ${Math.min(seg.t0, seg.t1).toFixed(2)}–${Math.max(seg.t0, seg.t1).toFixed(2)} s`;
    } else if (sel && sel.type === "memo") {
      const memo = state.doc.memos[sel.idx];
      if (memo) {
        info = `메모 ${sel.idx + 1} · ${memo.t.toFixed(2)} s`;
        showMemo = true;
        if (document.activeElement !== memoText) memoText.value = memo.text || "";
      }
    }
    if (memoText.hidden === showMemo) memoText.hidden = !showMemo;
    $("selectionInfo").textContent = info;
    $("memoList").innerHTML = state.doc.memos.map((m, i) =>
      `<li data-idx="${i}">${m.t.toFixed(1)} s — ${R.escapeHtml(m.text || "(빈 메모)")}</li>`).join("");
    const points = state.doc.lines.reduce((n, l) => n + l.points.length, 0);
    const seekMedian = median(state.stats.seeks), decodeMedian = median(state.stats.decodes);
    $("diag").textContent = [
      `engine: ${engineName()}`,
      `context: ${state.meta.context.columns} x ${state.meta.context.rows} px, build ${state.meta.context.build_sec} s`,
      `video: ${state.meta.video.name} ${state.meta.video.width}x${state.meta.video.height} @ ${state.meta.video.fps.toFixed(2)} fps`,
      `lines: ${state.doc.lines.length}, points: ${points}, segments: ${state.doc.segments.length}, memos: ${state.doc.memos.length}`,
      `render median: ${(median(state.stats.renders) || 0).toFixed(1)} ms, max: ${Math.max(0, ...state.stats.renders).toFixed(1)} ms`,
      `frame seek median: ${seekMedian == null ? "-" : seekMedian.toFixed(0) + " ms"} (n=${state.stats.seeks.length}), decode median: ${decodeMedian == null ? "-" : decodeMedian.toFixed(0) + " ms"}`,
      `saved version: ${state.savedVersion ? "v" + pad(state.savedVersion) : "-"}${state.dirty ? " (변경 있음)" : ""}`,
    ].join("\n");
  }

  function refreshLineSelect() {
    const counts = {};
    $("lineSelect").innerHTML = state.doc.lines.map((l) => {
      counts[l.kind] = (counts[l.kind] || 0) + 1;
      return `<option value="${l.id}" ${l.id === state.activeLine ? "selected" : ""}>${R.KIND_LABELS[l.kind]} ${counts[l.kind]} (${l.points.length}점)</option>`;
    }).join("");
  }

  // ---- frame view ---------------------------------------------------------------------
  const frame = { url: null, crop: null, inFlight: false, pending: null };

  function seekFrame(t) {
    state.frameTime = t;
    if (frame.inFlight) { frame.pending = t; render(); return; }
    frame.inFlight = true;
    const began = performance.now();
    fetch(`/api/frame?t=${t.toFixed(3)}`).then(async (res) => {
      if (!res.ok) throw new Error((await res.json()).error);
      const crop = res.headers.get("X-Crop").split(",").map(Number);
      const decodeMs = Number(res.headers.get("X-Decode-Ms"));
      const actual = Number(res.headers.get("X-Frame-Time"));
      const blob = await res.blob();
      if (frame.url) URL.revokeObjectURL(frame.url);
      frame.url = URL.createObjectURL(blob);
      frame.crop = crop;
      frame.actual = actual;
      const ms = performance.now() - began;
      state.stats.seeks.push(ms); state.stats.decodes.push(decodeMs);
      if (state.stats.seeks.length % 10 === 0) {
        postLog({ key: "seek", n: state.stats.seeks.length, median_ms: median(state.stats.seeks).toFixed(0),
          decode_median_ms: median(state.stats.decodes).toFixed(0) });
      }
      render();
    }).catch((err) => setStatus("프레임 오류: " + err.message)).finally(() => {
      frame.inFlight = false;
      if (frame.pending != null) { const next = frame.pending; frame.pending = null; seekFrame(next); }
    });
  }

  function drawFrameOverlay() {
    const svg = $("framePanel");
    if (!frame.url) { svg.innerHTML = `<text x="12" y="24" fill="#9ca3af">그래프를 클릭하면 원본 프레임이 표시됩니다</text>`; return; }
    const [x0, y0, w, h] = frame.crop;
    const g = state.meta.glass;
    const t = state.frameTime;
    $("frameTime").textContent = `${frame.actual.toFixed(2)} s`;
    const parts = [`<image href="${frame.url}" x="0" y="0" width="${w}" height="${h}"/>`];
    parts.push(`<ellipse cx="${g.cx - x0}" cy="${g.cy - y0}" rx="${g.rx}" ry="${g.ry}" fill="none" stroke="#fff" stroke-opacity="0.6" stroke-dasharray="4 3"/>`);
    parts.push(`<line x1="0" x2="${w}" y1="${g.zero_y - y0}" y2="${g.zero_y - y0}" stroke="#fff" stroke-dasharray="6 4" stroke-opacity="0.8"/>`);
    for (const line of state.doc.lines) {
      const value = R.sampleAt(line.points, t);
      if (value == null) continue;
      const y = g.zero_y - value - y0;
      parts.push(`<line x1="${g.cx - g.rx - x0 - 12}" x2="${g.cx + g.rx - x0 + 12}" y1="${y}" y2="${y}" ` +
        `stroke="${R.COLORS[line.kind]}" stroke-width="2.5" ${line.kind === "ref" ? 'stroke-dasharray="6 4"' : ""}/>`);
    }
    const seg = state.doc.segments.find((s) => t >= Math.min(s.t0, s.t1) && t <= Math.max(s.t0, s.t1));
    if (seg) parts.push(`<text x="8" y="20" fill="#fff" font-size="16" font-weight="700">${R.SEGMENT_STYLE[seg.state].label}</text>`);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.innerHTML = parts.join("");
  }

  // ---- pointer interaction ----------------------------------------------------------
  function onPointerDown(e) {
    if (e.button !== 0 && e.button !== 1) return;
    const svg = e.currentTarget;
    const at = eventToData(svg, e);
    const hit = e.target.closest("[data-kind]");
    const kind = hit && hit.dataset.kind;
    svg.setPointerCapture(e.pointerId);
    const pan = () => ({ type: "pan", svg, startX: e.clientX, startY: e.clientY, view: { ...state.view }, moved: false, t: at.t });

    if (e.button === 1) { state.drag = pan(); return; }

    if (state.tool === "select") {
      if (kind === "point" && isDoublePress(hit)) {
        toggleCorner(+hit.dataset.line, +hit.dataset.idx);
        return;
      }
      if (kind === "point") {
        pushUndo();
        state.selection = { type: "point", line: +hit.dataset.line, idx: +hit.dataset.idx };
        state.activeLine = state.doc.lines[state.selection.line].id;
        refreshLineSelect();
        state.drag = { type: "point", svg, pressKey: pressKey(hit) };
        seekFrame(state.doc.lines[state.selection.line].points[state.selection.idx].t);
      } else if (kind === "segedge") {
        pushUndo();
        state.selection = { type: "segment", idx: +hit.dataset.idx };
        state.drag = { type: "segedge", svg, idx: +hit.dataset.idx, edge: hit.dataset.edge };
      } else if (kind === "memo") {
        pushUndo();
        state.selection = { type: "memo", idx: +hit.dataset.idx };
        state.drag = { type: "memo", svg, idx: +hit.dataset.idx };
      } else if (kind === "segment") {
        state.selection = { type: "segment", idx: +hit.dataset.idx };
        state.drag = pan();
      } else {
        state.selection = null;
        state.drag = pan();
      }
    } else if (state.tool === "add") {
      pushUndo();
      let line = lineById(state.activeLine);
      if (!line) { line = newLine("oil"); }
      const p = { t: at.t, h: snapHeight(at.t, at.h), corner: false, src: "drawn" };
      let idx = line.points.findIndex((q) => q.t > p.t);
      if (idx < 0) idx = line.points.length;
      if ((idx > 0 && p.t - line.points[idx - 1].t < MIN_POINT_GAP_SEC) ||
        (idx < line.points.length && line.points[idx].t - p.t < MIN_POINT_GAP_SEC)) { state.undo.pop(); return; }
      line.points.splice(idx, 0, p);
      state.selection = { type: "point", line: state.doc.lines.indexOf(line), idx };
      state.drag = { type: "point", svg };
      refreshLineSelect();
      seekFrame(p.t);
    } else if (state.tool === "segment") {
      pushUndo();
      const state_ = $("segmentState").value;
      state.doc.segments.push({ id: uid("seg"), state: state_, t0: at.t, t1: at.t });
      const idx = state.doc.segments.length - 1;
      state.selection = { type: "segment", idx };
      state.drag = { type: "segedge", svg, idx, edge: "t1", creating: true };
    } else if (state.tool === "memo") {
      pushUndo();
      state.doc.memos.push({ id: uid("memo"), t: at.t, h: at.h, text: "" });
      state.selection = { type: "memo", idx: state.doc.memos.length - 1 };
      state.drag = { type: "memo-new", svg };
      render();
      return;
    }
    render();
  }

  function onPointerMove(e) {
    const drag = state.drag;
    if (!drag) return;
    const at = eventToData(drag.svg, e);
    if (drag.type === "pan") {
      const dx = e.clientX - drag.startX, dy = e.clientY - drag.startY;
      if (Math.abs(dx) + Math.abs(dy) > 3) drag.moved = true;
      if (!drag.moved) return;
      const spanT = drag.view.t1 - drag.view.t0, spanH = drag.view.h1 - drag.view.h0;
      const dt = (-dx / at.s.pw) * spanT * (at.width / at.box.width);
      const dh = (dy / at.s.ph) * spanH * (at.height / at.box.height);
      state.view = { t0: drag.view.t0 + dt, t1: drag.view.t1 + dt, h0: drag.view.h0 + dh, h1: drag.view.h1 + dh };
    } else if (drag.type === "point") {
      const sel = state.selection;
      const line = state.doc.lines[sel.line];
      const pts = line.points;
      const lo = sel.idx > 0 ? pts[sel.idx - 1].t + MIN_POINT_GAP_SEC : -Infinity;
      const hi = sel.idx < pts.length - 1 ? pts[sel.idx + 1].t - MIN_POINT_GAP_SEC : Infinity;
      const p = pts[sel.idx];
      p.t = Math.min(hi, Math.max(lo, at.t));
      p.h = snapHeight(p.t, at.h);
      if (p.src === "draft") p.src = "edited";
      throttledSeek(p.t);
    } else if (drag.type === "segedge") {
      state.doc.segments[drag.idx][drag.edge] = at.t;
    } else if (drag.type === "memo") {
      const memo = state.doc.memos[drag.idx];
      memo.t = at.t; memo.h = at.h;
    }
    render();
  }

  function onPointerUp(e) {
    const drag = state.drag;
    state.drag = null;
    if (!drag) return;
    const unchanged = ["point", "segedge", "memo"].includes(drag.type) && !drag.creating &&
      state.undo.length && state.undo[state.undo.length - 1] === JSON.stringify(state.doc);
    if (unchanged) state.undo.pop(); // a click without a change leaves no undo step
    // only a press that moved nothing can be the first half of a double press
    lastPress = unchanged && drag.pressKey ? { key: drag.pressKey, time: performance.now() } : { key: null, time: 0 };
    if (drag.type === "memo-new") {
      // focus on pointerup: a focus set during pointerdown is lost to the mousedown default
      const memoText = $("memoText");
      memoText.hidden = false;
      memoText.value = "";
      memoText.focus();
    }
    if (drag.type === "pan" && !drag.moved) {
      seekFrame(Math.min(state.meta.context.times.at(-1), Math.max(state.meta.context.times[0], drag.t)));
    } else if (drag.type === "segedge") {
      const seg = state.doc.segments[drag.idx];
      if (Math.abs(seg.t1 - seg.t0) < 0.05) {
        if (drag.creating) { state.doc.segments.splice(drag.idx, 1); state.undo.pop(); state.selection = null; }
      } else if (seg.t1 < seg.t0) { [seg.t0, seg.t1] = [seg.t1, seg.t0]; }
    }
    render();
  }

  let lastSeek = 0;
  function throttledSeek(t) {
    const now = performance.now();
    if (now - lastSeek > 120) { lastSeek = now; seekFrame(t); } else { state.frameTime = t; }
  }

  function onWheel(e) {
    e.preventDefault();
    const at = eventToData(e.currentTarget, e);
    const factor = Math.exp(e.deltaY * 0.0015);
    const v = state.view;
    const fit = R.fitView(state.meta);
    if (e.shiftKey) {
      const span = Math.min((fit.h1 - fit.h0) * 2, Math.max(4, (v.h1 - v.h0) * factor));
      const ratio = (at.h - v.h0) / (v.h1 - v.h0);
      state.view = { ...v, h0: at.h - ratio * span, h1: at.h - ratio * span + span };
    } else {
      const span = Math.min((fit.t1 - fit.t0) * 1.5, Math.max(0.5, (v.t1 - v.t0) * factor));
      const ratio = (at.t - v.t0) / (v.t1 - v.t0);
      state.view = { ...v, t0: at.t - ratio * span, t1: at.t - ratio * span + span };
    }
    render();
  }

  // Panels are redrawn on every press, so the browser's dblclick never sees the same
  // element twice; detect a second press on the same point here instead.
  let lastPress = { key: null, time: 0 };
  const pressKey = (hit) => `${hit.dataset.line}:${hit.dataset.idx}`;
  function isDoublePress(hit) {
    const double = lastPress.key === pressKey(hit) && performance.now() - lastPress.time < 400;
    if (double) lastPress = { key: null, time: 0 };
    return double;
  }

  function toggleCorner(li, pi) {
    pushUndo();
    const p = state.doc.lines[li].points[pi];
    p.corner = !p.corner;
    if (p.src === "draft") p.src = "edited";
    state.selection = { type: "point", line: li, idx: pi };
    state.drag = null;
    render();
  }

  // ---- commands ---------------------------------------------------------------------
  let uidCounter = 0;
  function uid(prefix) { uidCounter += 1; return `${prefix}-${Date.now().toString(36)}-${uidCounter}`; }

  function newLine(kind) {
    const line = { id: uid(kind), kind, points: [] };
    state.doc.lines.push(line);
    state.activeLine = line.id;
    refreshLineSelect();
    return line;
  }

  function deleteSelection() {
    const sel = state.selection;
    if (!sel) return;
    pushUndo();
    if (sel.type === "point") {
      const line = state.doc.lines[sel.line];
      line.points.splice(sel.idx, 1);
      if (!line.points.length) {
        state.doc.lines.splice(sel.line, 1);
        if (state.activeLine === line.id) state.activeLine = state.doc.lines.length ? state.doc.lines[0].id : null;
      }
    } else if (sel.type === "segment") {
      state.doc.segments.splice(sel.idx, 1);
    } else if (sel.type === "memo") {
      state.doc.memos.splice(sel.idx, 1);
    }
    state.selection = null;
    refreshLineSelect();
    render();
  }

  function setTool(tool) {
    state.tool = tool;
    document.querySelectorAll("#tools button").forEach((b) => b.classList.toggle("on", b.dataset.tool === tool));
    for (const id of PANELS) $(id).style.cursor = tool === "select" ? "default" : "crosshair";
  }

  async function save() {
    const res = await fetch("/api/save", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ doc: state.doc }) });
    const out = await res.json();
    if (!res.ok) { setStatus("저장 실패: " + out.error); return null; }
    state.savedVersion = out.version;
    state.dirty = false;
    postLog({ key: "render", median_ms: (median(state.stats.renders) || 0).toFixed(1),
      max_ms: Math.max(0, ...state.stats.renders).toFixed(1), points: state.doc.lines.reduce((n, l) => n + l.points.length, 0) });
    setStatus(`저장됨 v${pad(out.version)}`);
    render();
    return out;
  }

  async function makeReport() {
    const res = await fetch("/api/report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ doc: state.doc }) });
    const out = await res.json();
    if (!res.ok) { setStatus("보고서 실패: " + out.error); return; }
    setStatus(`보고서 v${pad(out.version)} 작성: ${out.path}`);
    await fetch("/api/open", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: out.path }) });
  }

  // ---- wiring -----------------------------------------------------------------------
  function bindUi() {
    for (const id of PANELS) {
      const svg = $(id);
      svg.addEventListener("pointerdown", onPointerDown);
      svg.addEventListener("pointermove", onPointerMove);
      svg.addEventListener("pointerup", onPointerUp);
      svg.addEventListener("pointercancel", onPointerUp);
      svg.addEventListener("wheel", onWheel, { passive: false });
    }
    document.querySelectorAll("#tools button").forEach((b) => b.addEventListener("click", () => setTool(b.dataset.tool)));
    $("lineSelect").addEventListener("change", (e) => { state.activeLine = e.target.value; render(); });
    $("newLine").addEventListener("click", () => { pushUndo(); newLine($("newLineKind").value); setTool("add"); render(); });
    $("snap").addEventListener("change", render);
    $("bgView").addEventListener("change", render);
    $("fit").addEventListener("click", () => { state.view = R.fitView(state.meta); render(); });
    $("undo").addEventListener("click", undo);
    $("redo").addEventListener("click", redo);
    $("save").addEventListener("click", save);
    $("report").addEventListener("click", makeReport);
    $("printApp").addEventListener("click", () => window.print());
    $("memoText").addEventListener("focus", () => pushUndo());
    $("memoText").addEventListener("input", (e) => {
      const sel = state.selection;
      if (sel && sel.type === "memo") { state.doc.memos[sel.idx].text = e.target.value; render(); }
    });
    $("memoList").addEventListener("click", (e) => {
      const li = e.target.closest("li[data-idx]");
      if (!li) return;
      state.selection = { type: "memo", idx: +li.dataset.idx };
      seekFrame(state.doc.memos[state.selection.idx].t);
      render();
    });
    window.addEventListener("resize", render);
    document.addEventListener("keydown", (e) => {
      if (e.target.matches("input, textarea, select")) return;
      const mod = e.ctrlKey || e.metaKey;
      if (mod && e.key.toLowerCase() === "z") { e.preventDefault(); e.shiftKey ? redo() : undo(); return; }
      if (mod && e.key.toLowerCase() === "y") { e.preventDefault(); redo(); return; }
      if (mod) return;
      if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); deleteSelection(); return; }
      const tools = { v: "select", a: "add", s: "segment", m: "memo" };
      if (tools[e.key.toLowerCase()]) setTool(tools[e.key.toLowerCase()]);
      if (e.key.toLowerCase() === "f") { state.view = R.fitView(state.meta); render(); }
    });
    window.addEventListener("beforeunload", (e) => { if (state.dirty) { e.preventDefault(); e.returnValue = ""; } });
  }

  init().catch((err) => { setStatus("초기화 실패: " + err.message); console.error(err); });
})();
