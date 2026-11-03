"""Make the P-2 user manual's screenshots and clips (docs/40-operations/user-manual.md). Not part of the app.

The app itself, run from this folder's code on a temporary data folder, is driven in Chrome through one
inspection of the example video, as an inspector would use it: a Recipe drawn, the inspection set up and
analysed, the draft corrected, the judgment checked, the version submitted. Along the way it saves, into
src/oil_tracker/web/manual/:
- img/<name>.webp: screenshots. Where a figure names a screen's parts, numbered badges are drawn in the
  page before the screenshot;
- clips/<name>.mp4: H.264 clips of one action each, a screenshot per frame (render_intro.Clip) with the
  pointer and the keys pressed drawn in the page.

Usage: python scripts/render_manual.py [--video sample/sample7.mp4] [--stop STAGE]
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import cv2  # noqa: E402
import imageio_ffmpeg  # noqa: E402
import numpy as np  # noqa: E402

from measure_editor import Server  # noqa: E402
from render_intro import (  # noqa: E402
    HEADER, LIMIT_SEC, NAME, PENCIL_SEC, POINT_SECS, RECIPE, WRONG_SEC, ZERO_Y, Clip, centre, context_point,
    edge, edge_at, field, frame_point)

OUT = ROOT / "src" / "oil_tracker" / "web" / "manual"
IMG, CLIPS = OUT / "img", OUT / "clips"
VIEW = {"width": 1280, "height": 800}  # the app's smallest window, captured at twice the pixels
WHOLE = {"x": 0, "y": 0, **VIEW}
SCALE = 1.5  # stills and clips keep 1.5 pixels per CSS pixel: sharp at the manual's width
# the data folder as a Windows PC shows it, in place of the temporary one
FOLDER = "C:\\Users\\사용자\\Documents\\OilLevelTracker"
FPS = 30
KEY_FRAMES = 40  # a key's chip shows this long
VIDEO_NAME = "예시_유리컵.mp4"  # the example video's name in the screens

# Drawn in the app's page, above everything (a popover is in the top layer, re-shown above an open
# dialog): the pointer, a ring while pressed, the key just pressed, and numbered badges and boxes.
OVERLAY = r"""
(() => {
  const NS = "http://www.w3.org/2000/svg";
  let layer = null, svg = null, at = null, marks = { badges: [], boxes: [] };
  const ARROW = "M0 0 L0 18 L4.6 13.6 L7.6 20.6 L10.4 19.4 L7.4 12.6 L13.6 12.6 Z";
  const DOUBLE = "M-10 0 L-5 -5 L-5 -2 L5 -2 L5 -5 L10 0 L5 5 L5 2 L-5 2 L-5 5 Z";
  const ROTATION = { "ew-resize": 0, "col-resize": 0, "ns-resize": 90, "row-resize": 90, "nwse-resize": 45, "nesw-resize": -45 };

  function node(name, attrs, parent) {
    const el = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    parent.appendChild(el);
    return el;
  }
  function ensure() {
    if (!layer || !layer.isConnected) {
      layer = document.createElement("div");
      layer.setAttribute("popover", "manual");
      layer.style.cssText = "position:fixed;inset:0;width:100vw;height:100vh;margin:0;border:0;padding:0;" +
        "background:transparent;overflow:visible;pointer-events:none";
      svg = document.createElementNS(NS, "svg");
      svg.setAttribute("width", "100%");
      svg.setAttribute("height", "100%");
      layer.appendChild(svg);
      document.body.appendChild(layer);
    }
    if (document.querySelector("dialog[open]") || !layer.matches(":popover-open")) {
      if (layer.matches(":popover-open")) layer.hidePopover();
      layer.showPopover();
    }
  }
  function kindAt(x, y) {
    const el = document.elementFromPoint(x, y);
    const cursor = el ? getComputedStyle(el).cursor : "default";
    if (cursor === "crosshair") return "cross";
    if (cursor in ROTATION) return cursor;
    if (cursor === "move") return "move";
    return "arrow";
  }
  function draw() {
    ensure();
    svg.replaceChildren();
    for (const b of marks.boxes) {
      node("rect", { x: b.x, y: b.y, width: b.width, height: b.height, rx: 4, fill: "none",
        stroke: "#FFFFFF", "stroke-width": 5 }, svg);
      node("rect", { x: b.x, y: b.y, width: b.width, height: b.height, rx: 4, fill: "none",
        stroke: "var(--brand)", "stroke-width": 2.5 }, svg);
    }
    for (const b of marks.badges) {
      node("circle", { cx: b.x, cy: b.y, r: 13, fill: "var(--brand)", stroke: "#FFFFFF", "stroke-width": 2.5 }, svg);
      const t = node("text", { x: b.x, y: b.y + 5, "text-anchor": "middle", fill: "#FFFFFF",
        style: "font: 600 14px var(--font)" }, svg);
      t.textContent = String(b.n);
    }
    if (!at) return;
    const { x, y } = at;
    if (at.down) node("circle", { cx: x, cy: y, r: 15, fill: "rgba(15,108,189,0.22)", stroke: "var(--brand)",
      "stroke-width": 2 }, svg);
    const kind = kindAt(x, y);
    const g = node("g", { transform: `translate(${x} ${y})` }, svg);
    if (kind === "arrow") {
      node("path", { d: ARROW, transform: "scale(1.15)", fill: "#FFFFFF", stroke: "#000000", "stroke-width": 1.3,
        "stroke-linejoin": "round" }, g);
    } else if (kind === "cross") {
      for (const [w, c] of [[4, "#FFFFFF"], [1.6, "#000000"]])
        node("path", { d: "M-11 0 H11 M0 -11 V11", stroke: c, "stroke-width": w, "stroke-linecap": "round" }, g);
    } else if (kind === "move") {
      for (const angle of [0, 90])
        node("path", { d: DOUBLE, transform: `rotate(${angle}) scale(1.15)`, fill: "#FFFFFF", stroke: "#000000",
          "stroke-width": 1.1, "stroke-linejoin": "round" }, g);
    } else {
      node("path", { d: DOUBLE, transform: `rotate(${ROTATION[kind]}) scale(1.2)`, fill: "#FFFFFF",
        stroke: "#000000", "stroke-width": 1.1, "stroke-linejoin": "round" }, g);
    }
    if (at.key) {
      const above = y > innerHeight - 70;
      const k = node("g", { transform: `translate(${x + 22} ${above ? y - 44 : y + 26})` }, svg);
      const text = node("text", { x: 10, y: 19, fill: "#FFFFFF", style: "font: 600 14px var(--font)" }, k);
      text.textContent = at.key;
      const width = text.getComputedTextLength() + 20;
      const box = node("rect", { width, height: 28, rx: 6, fill: "var(--fg-1)", opacity: 0.92 }, k);
      k.insertBefore(box, text);
    }
  }
  window.manual = {
    pointer(p) { at = p; draw(); },
    marks(m) { marks = m; draw(); },
  };
})();
"""


# ---- helpers ----

class ManualClip(Clip):
    """A Clip whose frames carry the pointer and the last key, drawn in the page; saved as an MP4."""

    def __init__(self, page, name: str, at: tuple[float, float], region: dict, work: Path) -> None:
        super().__init__(page, name, at, root=work, region=region)
        self.key_label, self.since_key = None, KEY_FRAMES

    def frame(self, fresh: bool = True) -> None:
        if fresh or not self.shots:
            key = self.key_label if self.since_key < KEY_FRAMES else None
            self.page.evaluate("p => window.manual.pointer(p)",
                               {"x": self.x, "y": self.y, "down": self.down, "key": key})
        super().frame(fresh)
        self.since_key += 1

    def key(self, key: str, label: str, wait_ms: int = 150) -> None:
        self.key_label, self.since_key = label, 0
        super().key(key, label, wait_ms)

    def wheel(self, dy: float, label: str, wait_ms: int = 250) -> None:
        if self.key_label != label or self.since_key >= KEY_FRAMES:
            self.key_label = label
        self.since_key = 0
        self.page.mouse.wheel(0, dy)
        self.settle(wait_ms)
        self.frame()

    def save(self) -> None:
        width = even(min(self.region["width"] * 2, 1920))  # the screenshots' own pixels, or 1920 wide
        height = even(self.region["height"] * width / self.region["width"])
        out = CLIPS / f"{self.name}.mp4"
        writer = imageio_ffmpeg.write_frames(
            str(out), (width, height), fps=FPS, codec="libx264", quality=None, macro_block_size=2,
            pix_fmt_in="rgb24", pix_fmt_out="yuv420p",
            output_params=["-crf", "24", "-preset", "slow", "-tune", "animation", "-movflags", "+faststart"])
        writer.send(None)
        loaded: dict[int, bytes] = {}
        for shot, *_ in self.frames:
            if shot not in loaded:
                image = cv2.imread(str(self.folder / f"{shot:04d}.jpg"))
                image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
                loaded[shot] = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).tobytes()
            writer.send(loaded[shot])
        writer.close()
        self.page.evaluate("() => window.manual.pointer(null)")
        print(f"  clip {self.name}: {len(self.frames) / FPS:.1f} s, {width}x{height}, "
              f"{out.stat().st_size / 1e6:.2f} MB", flush=True)


def even(value: float) -> int:
    return int(round(value / 2)) * 2


def settle(page, ms: int = 0) -> None:
    if ms:
        page.wait_for_timeout(ms)
    page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")


def box(target, pad: float = 0) -> dict:
    """A locator's box, or a box, grown by pad on every side."""
    b = target if isinstance(target, dict) else target.bounding_box()
    return {"x": b["x"] - pad, "y": b["y"] - pad, "width": b["width"] + 2 * pad, "height": b["height"] + 2 * pad}


def union(*targets, pad: float = 0) -> dict:
    boxes = [box(target) for target in targets]
    x0 = min(b["x"] for b in boxes) - pad
    y0 = min(b["y"] for b in boxes) - pad
    x1 = max(b["x"] + b["width"] for b in boxes) + pad
    y1 = max(b["y"] + b["height"] for b in boxes) + pad
    return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}


def callout(n: int, target, side: str = "bottom", nudge: tuple[float, float] = (0, 0)) -> dict:
    """A numbered badge beside a target: a locator or a box, outlined, or an (x, y) point. The badge sits
    to its "left", "right", "top" or "bottom", or "in" its top-left corner, moved by nudge."""
    point = isinstance(target, tuple)
    b = {"x": target[0], "y": target[1], "width": 0, "height": 0} if point else box(target)
    r = 21 if point else 19
    cx, cy = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
    x, y = {"left": (b["x"] - r, cy), "right": (b["x"] + b["width"] + r, cy), "top": (cx, b["y"] - r),
            "bottom": (cx, b["y"] + b["height"] + r), "in": (b["x"] + 18, b["y"] + 18)}[side]
    return {"badge": {"n": n, "x": x + nudge[0], "y": y + nudge[1]},
            "box": None if point or side == "in" else box(b, 3)}


def scrub_marks(page) -> dict:
    """The scrub bar with the marks written above it."""
    b = box(page.locator("#scrub"))
    return {**b, "y": b["y"] - 16, "height": b["height"] + 16}


def windows_paths(page) -> None:
    """The data folder as a Windows PC shows it, in place of the temporary one."""
    page.evaluate(r"""folder => {
        for (const [id, sub] of [["inspectionsFolder", "Inspections"], ["folderPath", "Recipes"]]) {
            const el = document.getElementById(id);
            if (el && el.textContent) el.textContent = folder + "\\" + sub;
        }
    }""", FOLDER)


def still(page, name: str, region: dict | None = None, callouts: list | tuple = (), thumb: bool = False) -> None:
    """A screenshot of the page or a region of it, with callouts, as img/<name>.webp; with thumb, also
    without them as img/<name>-thumb.webp, for the quick start."""
    windows_paths(page)
    page.evaluate("() => window.manual.pointer(null)")
    shots = [(name, callouts, SCALE)] + ([(f"{name}-thumb", (), 0.75)] if thumb else [])
    for file, marks, scale in shots:
        page.evaluate("m => window.manual.marks(m)",
                      {"badges": [c["badge"] for c in marks], "boxes": [c["box"] for c in marks if c["box"]]})
        settle(page, 150)
        data = page.screenshot(clip=region, type="png")
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        width = even((region or VIEW)["width"] * scale)
        height = even(image.shape[0] * width / image.shape[1])
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        path = IMG / f"{file}.webp"
        cv2.imwrite(str(path), image, [cv2.IMWRITE_WEBP_QUALITY, 86])
        print(f"  still {file}: {width}x{height}, {path.stat().st_size / 1e3:.0f} kB", flush=True)
    page.evaluate("() => window.manual.marks({badges: [], boxes: []})")


def hush(page) -> None:
    """The editor's passing notices gone, as they would be a few seconds later."""
    page.evaluate("() => { for (const id of ['editorNotice', 'editNotice']) document.getElementById(id).textContent = ''; }")


def unscroll(page) -> None:
    """Every scrolled panel back at its top."""
    page.evaluate("() => { for (const node of document.querySelectorAll('*')) if (node.scrollTop) node.scrollTop = 0; }")


def rest(page, x: float = 1240, y: float = 780) -> None:
    """The pointer out of the way, where it hovers over nothing."""
    page.mouse.move(x, y)
    settle(page, 300)


# ---- the walk through the app ----

def inspection_list(page) -> None:
    page.locator("#inspectionsView").wait_for()
    rest(page, 640, 500)
    still(page, "list-empty", thumb=True, callouts=[
        callout(1, page.locator("#newInspection")), callout(2, page.locator("#toRecipes")),
        callout(3, page.locator("#inspectionsView .help-open")), callout(4, page.locator("#openInspectionsFolder"), "right")])


def recipe(page, work: Path) -> dict:
    """The Recipe list, a new Recipe on the example video: a Glass placed, sized and its zero line set (a
    clip), the rule's time limit, saved."""
    page.locator("#toRecipes").click()
    page.locator("#recipesView").wait_for()
    page.locator("#newRecipe").click()  # the path prompt answers with the video
    page.locator("#editView").wait_for()
    page.locator("#recipeName").fill(RECIPE)
    scrub = page.locator("#scrub").bounding_box()
    page.mouse.click(scrub["x"] + scrub["width"] * 40 / 44.4, scrub["y"] + scrub["height"] / 2)  # milk in the cup
    rest(page, 640, 760)
    settle(page, 900)
    still(page, "recipe-new", callouts=[
        callout(1, page.locator("#openVideo")), callout(2, scrub_marks(page), "top"),
        callout(3, page.locator("#recipeName"), "left"), callout(4, page.locator("#addGlass"), "left")])

    page.locator("#addGlass").click()  # the default Glass: centre (960, 540), 230 x 292, zero 594
    settle(page, 300)
    x0, y0 = frame_point(page, 560, 230)
    x1, y1 = frame_point(page, 1690, 1050)
    region = {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}
    clip = ManualClip(page, "recipe-glass", frame_point(page, 1500, 330), region, work)
    clip.hold(15)
    clip.move(*frame_point(page, 960, 520), 18)
    clip.drag(*frame_point(page, 1125, 655), 28)  # centre (1125, 675): box 895-1355 x 383-967, zero 729
    clip.hold(10)
    clip.move(*frame_point(page, 895, 383), 16)
    clip.drag(*frame_point(page, 875, 500), 24)
    clip.hold(6)
    clip.move(*frame_point(page, 1355, 967), 18)
    clip.drag(*frame_point(page, 1375, 850), 24)
    clip.hold(10)
    zero = field(page.locator("#selBody"), "0선 Y")
    clip.move(*frame_point(page, 1210, float(zero.input_value())), 16)
    clip.drag(*frame_point(page, 1210, ZERO_Y), 22)
    clip.hold(10)
    clip.move(*frame_point(page, 1500, 330), 18)
    clip.hold(40)
    clip.save()

    body = page.locator("#selBody")
    limit = field(body, "회복 제한 시간")
    limit.fill(f"{LIMIT_SEC:g}")
    limit.press("Enter")
    settle(page, 300)
    page.locator("#save").click()
    page.wait_for_function("document.getElementById('editNotice').textContent.includes('저장했습니다')")
    rest(page, 640, 760)
    drawn = {"ellipse": {key: float(field(body, label).input_value()) for key, label in (
        ("center_x", "중심 X"), ("center_y", "중심 Y"), ("radius_x", "반지름 X"), ("radius_y", "반지름 Y"))},
        "zero": float(field(body, "0선 Y").input_value())}
    e = drawn["ellipse"]
    still(page, "recipe-screen", thumb=True, callouts=[
        callout(1, frame_point(page, e["center_x"] + e["radius_x"], e["center_y"] - e["radius_y"]), "right"),
        callout(2, frame_point(page, e["center_x"] - e["radius_x"] - 30, drawn["zero"]), "left"),
        callout(3, page.locator("#glassRows"), "left"),
        callout(4, page.locator("#selBody select").first, "left"),
        callout(5, page.locator("#save"))])
    still(page, "recipe-rule", region=box(page.locator("#selBody")))

    page.locator("#back").click()
    page.locator("#recipesView").wait_for()
    rest(page, 640, 600)
    still(page, "recipe-list", callouts=[
        callout(1, page.locator("#newRecipe")), callout(2, page.locator("#openFolder"), "right")])
    return drawn


def setup(page, server) -> str:
    """A new inspection: the video, the Recipe, the analysis setup; analysed. The inspection's id."""
    page.goto(server.url)
    page.get_by_role("button", name="새 검사").click()
    page.locator("#pickDialog").wait_for()
    page.locator("#pickRows tr", has_text=RECIPE).click()
    rest(page, 1240, 780)
    still(page, "pick-recipe", region=box(page.locator("#pickDialog"), 8))
    page.locator("#pickNext").click()
    view = page.locator("#setupView")
    view.wait_for()
    view.get_by_label("검사 이름").fill(NAME)
    for label, value in (("기동 시각", "5"), ("압축기 모델", HEADER["compressor_model"]),
                         ("시험 종류", HEADER["test_type"])):
        entry = field(view, label)
        entry.fill(value)
        entry.press("Enter")
    page.wait_for_function("document.getElementById('setupProblemCount').textContent === ''")
    page.locator("#frame").focus()
    rest(page, 640, 400)
    settle(page, 600)
    still(page, "setup", thumb=True, callouts=[
        callout(1, scrub_marks(page), "top"), callout(2, page.locator("#startAnalysis"), "left")])
    still(page, "setup-fields", region=union(page.locator("#rangeFields"), page.locator("#compressorField"), pad=8))

    page.locator("#startAnalysis").click()
    page.locator("#progressDialog[open]").wait_for()
    try:  # under way, with the time left
        page.wait_for_function("!['', '0%'].includes(document.getElementById('progressPercent').textContent)",
                               timeout=3000)
    except Exception:  # noqa: BLE001 - a quick analysis may not show it
        pass
    settle(page, 100)
    still(page, "progress", region=box(page.locator("#progressDialog"), 8))
    for _ in range(600):
        listed = server.call("GET", "/api/inspections")["inspections"]
        if listed and listed[0]["state"] == "ANALYSED":
            return listed[0]["id"]
        time.sleep(0.2)
    raise RuntimeError("분석이 끝나지 않았습니다")


def editor_facts(server, data: Path, inspection: str, drawn: dict) -> dict:
    """Where the draft is and where the milk's edge is, per sample, for the pointer's paths."""
    context = cv2.imread(str(next((data / "Inspections").glob("*/cache/*/context-000.png"))))
    e = drawn["ellipse"]
    top, bottom = e["center_y"] - e["radius_y"], e["center_y"] + e["radius_y"]
    edits = server.call("GET", f"/api/inspections/{inspection}/edits")["edits"]
    times = edits["times"]
    dt = (times[-1] - times[0]) / (len(times) - 1)
    return {"top": top, "bottom": bottom, "times": times, "view": [times[0] - dt / 2, times[-1] + dt / 2],
            "draft": edits["glasses"][0]["oil"]["ys"], "edge": edge(context, top, bottom)}


def plots(page) -> dict:
    """The graph, the context image and the time axis, with their headers: where the editing clips are."""
    return box(page.locator("#editorView section.editor-left"))


def editor_tour(page, work: Path, facts: dict) -> None:
    page.wait_for_function("document.querySelectorAll('#context image').length === 1")
    rest(page, 640, 24)
    settle(page, 1200)
    tools = page.locator("#editorView [data-tool]")
    still(page, "editor", thumb=True, callouts=[
        callout(1, union(tools.first, tools.last)), callout(2, page.locator("#editorGlass")),
        callout(3, union(page.locator("#editorSave"), page.locator("#editorSubmit")), nudge=(-62, 0)),
        callout(4, page.locator("#fitWhole"), nudge=(-40, -4)),
        callout(5, page.locator("label.toggle", has=page.locator("#backgroundToggle")), "left"),
        callout(6, page.locator("#videoWindow"), "left")])

    at = lambda t, y: context_point(page, t, y, facts)  # noqa: E731
    graph = page.locator("#graph").bounding_box()
    clip = ManualClip(page, "view", at(30, facts["top"] + 60), WHOLE, work)
    clip.hold(10)
    clip.click(*at(20.0, facts["top"] + 60), 20, wait_ms=900)  # the video goes to 0:20
    clip.hold(30, wait_ms=300)
    clip.move(graph["x"] + graph["width"] * 0.42, graph["y"] + graph["height"] * 0.5, 18)
    for _ in range(4):
        clip.wheel(-200, "휠  확대")
        clip.hold(5)
    clip.hold(20)
    clip.click(*centre(page.locator("#fitWhole")), 22, wait_ms=500)
    clip.hold(36)
    clip.save()

    toggle = page.locator("label.toggle", has=page.locator("#backgroundToggle"))
    toggle.click()
    rest(page, 640, 24)
    settle(page, 800)
    still(page, "background", region=box(page.locator("#contextBox")))
    toggle.click()
    settle(page, 500)


def correct(page, work: Path, facts: dict) -> None:
    """The draft's wrong stretch selected and deleted, then the milk's edge drawn back with the pencil
    and with joined points; one clip each."""
    at = lambda t, y: context_point(page, t, y, facts)  # noqa: E731
    region = plots(page)
    band_y = facts["top"] + 0.3 * (facts["bottom"] - facts["top"])

    clip = ManualClip(page, "range-delete", at(6, band_y), region, work)
    clip.hold(12)
    clip.move(*at(WRONG_SEC[0], band_y), 18)
    clip.key("KeyR", "R  범위")
    clip.hold(8)
    clip.drag(*at(WRONG_SEC[1], band_y), 28)
    clip.hold(14)
    clip.key("Delete", "Delete", wait_ms=400)
    clip.hold(50)
    clip.save()
    still(page, "selection", region=box(page.locator("#editSection")))

    pencil = [at(0.0, facts["bottom"] - 2)]  # from the Glass bottom: EMPTY
    pencil += [at(t, y) for t, y in zip(facts["times"], facts["edge"]) if t <= PENCIL_SEC]
    clip = ManualClip(page, "pencil", at(WRONG_SEC[1], band_y), region, work)
    clip.hold(10)
    clip.move(*pencil[0], 20)
    clip.key("KeyP", "P  연필")
    clip.hold(6)
    clip.press()
    clip.path(pencil, 50)
    clip.release(wait_ms=300)
    clip.hold(45)
    clip.save()

    joined = [at(t, edge_at(facts, t)) for t in (PENCIL_SEC, *POINT_SECS)]
    end = WRONG_SEC[1]
    joined.append(at(end, facts["draft"][min(range(len(facts["times"])), key=lambda k: abs(facts["times"][k] - end))]))
    clip = ManualClip(page, "points", pencil[-1], region, work)
    clip.hold(10)
    clip.key("KeyL", "L  점 잇기")
    clip.hold(6)
    for x, y in joined:
        clip.click(x, y, 14, wait_ms=350)
        clip.hold(4)
    clip.hold(8, wait_ms=300)
    clip.key("Enter", "Enter", wait_ms=900)
    clip.hold(50, wait_ms=300)
    clip.save()


def more_tools(page, work: Path, facts: dict) -> None:
    """Grab-and-drag (a clip, then undone), a picked line, cannot judge, copy and the repeat paste, and a
    memo."""
    at = lambda t, y: context_point(page, t, y, facts)  # noqa: E731
    region = plots(page)
    t = 24.0
    y = edge_at(facts, t)
    clip = ManualClip(page, "grab", at(t + 4, y + 60), region, work)
    clip.hold(10)
    clip.key("KeyG", "G  잡아끌기")
    clip.hold(8)
    for _ in range(2):  # the width from 30 s to 10 s: a bump, not the whole line
        clip.key("BracketLeft", "[  끌기 폭 줄이기")
        clip.hold(8)
    clip.move(*at(t, y), 16)
    clip.drag(*at(t, y - 50), 26, wait_ms=300)
    clip.hold(40)
    clip.save()
    page.keyboard.press("Control+z")
    for _ in range(2):
        page.keyboard.press("BracketRight")
    settle(page, 400)

    page.keyboard.press("KeyV")
    page.mouse.click(*at(t, y))
    settle(page, 400)
    rest(page, 640, 24)
    still(page, "picked", region=box(page.locator("#editSection")))
    page.keyboard.press("Escape")

    page.keyboard.press("KeyR")
    page.mouse.move(*at(40.0, facts["top"] + 40))
    page.mouse.down()
    page.mouse.move(*at(44.0, facts["top"] + 40), steps=8)
    page.mouse.up()
    page.keyboard.press("KeyU")
    settle(page, 500)
    rest(page, 640, 24)
    still(page, "cannot-judge", region=union(page.locator("#graphBox"), page.locator("#contextBox"),
                                            page.locator("#axisBox")))
    page.keyboard.press("Control+z")
    page.keyboard.press("Escape")
    settle(page, 300)

    page.keyboard.press("KeyR")
    page.mouse.move(*at(34.0, facts["top"] + 40))
    page.mouse.down()
    page.mouse.move(*at(40.0, facts["top"] + 40), steps=8)
    page.mouse.up()
    page.keyboard.press("Control+c")
    settle(page, 400)
    rest(page, 640, 24)
    page.locator("#copyBox").scroll_into_view_if_needed()
    still(page, "copy", region=union(page.locator("#selectionBox"), page.locator("#copyBox"), pad=8))
    page.keyboard.press("Escape")
    page.keyboard.press("Escape")
    unscroll(page)
    settle(page, 300)

    page.keyboard.press("KeyM")
    page.locator("#memoPop").wait_for()
    page.locator("#memoAdd").click()
    page.mouse.click(*at(16.0, edge_at(facts, 16.0)))
    page.locator("#memoDialog[open]").wait_for()
    page.locator("#memoText").fill("우유가 Glass 아래쪽에 닿기 시작")
    rest(page, 1240, 780)
    still(page, "memo-dialog", region=box(page.locator("#memoDialog"), 8))
    page.locator("#memoSave").click()
    settle(page, 300)
    if page.locator("#memoPop").is_hidden():
        page.locator("#editorView button[data-tool=memo]").click()  # the list again, with the new memo
    page.locator("#memoPop").wait_for()
    rest(page, 640, 24)
    still(page, "memo-list", region=union(page.locator("#memoPop"), page.locator("#graphBox"), pad=4))
    page.locator("#memoPopClose").click()
    page.keyboard.press("KeyV")
    settle(page, 300)


def reopen(page) -> None:
    """Saved, and the inspection opened again from the list, as the next day: the copy and the notices
    of the tools' stage are gone."""
    page.keyboard.press("Control+s")
    page.wait_for_function("!document.getElementById('editorState').textContent.includes('저장 안 함')")
    page.reload()
    page.locator("#inspectionRows tr").first.dblclick()
    page.wait_for_function("document.querySelectorAll('#context image').length === 1")
    settle(page, 800)


def judgment(page) -> None:
    reopen(page)
    section = page.locator("#judgmentSection")
    section.evaluate("node => node.scrollIntoView({ block: 'start' })")
    rest(page, 640, 24)
    room = page.add_style_tag(content="#judgmentSection > .body { padding-left: 44px }")  # for the badges
    settle(page, 200)
    still(page, "judgment", region=box(section), callouts=[
        callout(1, page.locator("#verdictBadge"), "left"), callout(2, page.locator("#judgmentFacts"), "left"),
        callout(3, page.locator("#overrideRow"), "left"), callout(4, page.locator("#checkRow"), "left")])
    room.evaluate("node => node.remove()")
    page.locator("#overrideKind button", has_text="불합격").click()
    page.locator("#reasonBox").wait_for()
    settle(page, 300)
    still(page, "override", region=box(section))
    page.locator("#overrideKind button", has_text="자동").click()
    settle(page, 300)
    page.locator("#checkGlass").click()
    settle(page, 500)
    rest(page, 640, 24)
    still(page, "checked", region=box(section))
    unscroll(page)
    still(page, "editor-checked", thumb=True)
    hush(page)
    still(page, "toolbar-checked", region=union(page.locator("#editorGlass"), page.locator("#editorSubmit"), pad=10))
    page.keyboard.press("Control+s")
    page.wait_for_function("!document.getElementById('editorState').textContent.includes('저장 안 함')")
    settle(page, 300)


def submit(page, data: Path) -> None:
    page.locator("#editorSubmit").click()
    page.locator("#submitDialog[open]").wait_for()
    settle(page, 400)
    rest(page, 1240, 780)
    still(page, "submit-dialog", region=box(page.locator("#submitDialog"), 8))
    page.locator("#submitConfirm").click()
    page.locator("#versionBar").wait_for()
    settle(page, 1200)
    unscroll(page)
    rest(page, 640, 400)
    hush(page)
    still(page, "submitted", callouts=[
        callout(1, page.locator("#versionPicker"), "bottom"), callout(2, page.locator("#editorReport"), "left"),
        callout(3, page.locator("#reviseButton"), "bottom")])

    report = next((data / "Inspections").glob("*/versions/001/report.html"))
    page.goto(report.as_uri())
    settle(page, 1500)
    first = page.locator("section.page").first
    still(page, "report", region=box(first))


def listed(page, server) -> None:
    page.goto(server.url)
    page.locator("#inspectionRows tr").first.wait_for()
    rest(page, 640, 500)
    still(page, "list")


def warning(page, source: Path) -> None:
    """The editor's warning when the source video is not where the analysis found it."""
    moved = source.with_name("옮김_" + source.name)
    source.rename(moved)
    try:
        page.locator("#inspectionRows tr").first.dblclick()
        page.locator("#sourceWarning").wait_for()
        settle(page, 800)
        rest(page, 640, 400)
        page.evaluate("""([folder, shown]) => {
            const text = document.getElementById('sourceWarningText');
            text.textContent = text.textContent.replace(folder, shown);
        }""", [str(source.parent) + "/", "C:\\Users\\사용자\\Videos\\"])
        bar = box(page.locator("#sourceWarning"))
        end = box(page.locator("#sourceRecheck"))
        still(page, "source-warning", region={**bar, "width": end["x"] + end["width"] + 12 - bar["x"]})
    finally:
        moved.rename(source)


STAGES = ["list", "recipe", "setup", "editor", "correct", "tools", "judgment", "submit", "faq"]


def walk(video: Path, stop: str | None) -> None:
    from playwright.sync_api import sync_playwright

    for folder in (IMG, CLIPS):
        folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp, sync_playwright() as playwright:
        work = Path(temp)
        data = work / "data"
        data.mkdir()
        source = work / "videos" / VIDEO_NAME
        source.parent.mkdir()
        shutil.copyfile(video, source)
        server = Server(data)
        try:
            browser = playwright.chromium.launch(channel="chrome")
            page = browser.new_page(viewport=VIEW, device_scale_factor=2)
            page.add_init_script(OVERLAY)
            page.on("dialog", lambda dialog: dialog.accept(str(source)))  # no window: the path prompt
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(server.url)
            settle(page, 600)

            def stage(name: str) -> bool:
                print(f"{name}:", flush=True)
                return stop is not None and STAGES.index(name) > STAGES.index(stop)

            for name in STAGES:
                if stage(name):
                    break
                if name == "list":
                    inspection_list(page)
                elif name == "recipe":
                    drawn = recipe(page, work)
                elif name == "setup":
                    inspection = setup(page, server)
                    facts = editor_facts(server, data, inspection, drawn)
                elif name == "editor":
                    editor_tour(page, work, facts)
                elif name == "correct":
                    correct(page, work, facts)
                elif name == "tools":
                    more_tools(page, work, facts)
                elif name == "judgment":
                    judgment(page)
                elif name == "submit":
                    submit(page, data)
                    listed(page, server)
                elif name == "faq":
                    warning(page, source)
            if errors:
                print("page errors:", *errors, sep="\n  ")
            browser.close()
        finally:
            server.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--video", type=Path, default=ROOT / "sample" / "sample7.mp4")
    parser.add_argument("--stop", choices=STAGES, help="stop after this stage")
    args = parser.parse_args()
    began = time.perf_counter()
    walk(args.video, args.stop)
    print(f"done in {time.perf_counter() - began:.0f} s: {OUT}")


if __name__ == "__main__":
    main()
