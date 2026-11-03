"""Make the P-1 introduction video, draft 3 (docs/40-operations/intro-video.md). Not part of the app.

Stages:
1. assets, into design/intro/assets/ (ignored by Git): the app itself, run from this folder's code on
   a temporary data folder and driven in Chrome as an inspector would use it. Each action is a clip:
   one screenshot per video frame, with where the pointer is (the page draws the pointer). The
   Recipe is drawn on the example video, the inspection analysed, the draft corrected with the
   pencil along the context image's milk edge, the Glass checked, the version submitted; then
   stills of the editor, the judgment, the report and frames of the video;
2. the frames: design/intro/intro.html in Chrome, seek(t) and a screenshot every 1/30 s;
3. the sound: the music, edited to the video (MUSIC_EDIT), with the page's cues synthesised here on top;
4. both muxed by imageio-ffmpeg's ffmpeg into an H.264 + AAC MP4.

Usage: python scripts/render_intro.py [--video sample/sample7.mp4] [--music TRACK.mp3]
           [--out ~/Movies/OilLevelTracker/intro.mp4] [--skip-assets] [--stills 3.5,20]
"""

from __future__ import annotations

import argparse
import json
import math
import mimetypes
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))  # this folder's code, even where another copy is installed
sys.path.insert(0, str(ROOT / "scripts"))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from measure_editor import Server  # noqa: E402

PAGE = ROOT / "design" / "intro"
ASSETS = PAGE / "assets"
ORIGIN = "http://intro.local/"
RATE = 48_000
FPS = 30
APP = {"width": 1600, "height": 900}  # the app's window in the clips, captured at twice the pixels

# the Glass on sample7 (user, 2026-11-03: not the cup's upper part, where the draft caught the
# top): from the thick base up to just above the final level, inside the walls
GLASS = {"center_x": 1125.0, "center_y": 675.0, "radius_x": 250.0, "radius_y": 175.0}
ZERO_Y, LIMIT_SEC = 700.0, 30.0
WHITE = 195  # the milk in the context image: every channel above this
NAME, HEADER = "예시 검사", {"compressor_model": "예시 모델", "test_type": "예시 시험"}
RECIPE = "예시 유리컵"
EDGE_SEC = 31.5  # the pencil follows the milk's edge up to here; the draft is right after it


# ---- 1. assets ----

def smooth(p: float) -> float:
    return p * p * (3 - 2 * p)


class Clip:
    """One action in the app as a clip: a screenshot per video frame and the pointer in each.

    The pointer is Playwright's mouse; a frame whose screen cannot have changed reuses the last
    screenshot. marks name frames the page times its scene to."""

    def __init__(self, page, name: str, at: tuple[float, float]) -> None:
        self.page, self.name = page, name
        self.folder = ASSETS / "clips" / name
        self.folder.mkdir(parents=True)
        self.frames: list[list] = []  # [screenshot, x, y, pressed, pointer kind]
        self.shots = 0
        self.marks: dict[str, int] = {}
        self.x, self.y = at
        self.down, self.kind = False, "arrow"
        page.mouse.move(self.x, self.y)

    def settle(self, ms: int = 0) -> None:
        if ms:
            self.page.wait_for_timeout(ms)
        self.page.evaluate("() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)))")

    def frame(self, fresh: bool = True) -> None:
        if fresh or not self.shots:
            self.settle()
            self.page.screenshot(path=str(self.folder / f"{self.shots:04d}.jpg"), type="jpeg", quality=88)
            self.shots += 1
        self.frames.append([self.shots - 1, round(self.x, 1), round(self.y, 1), self.down, self.kind])

    def hold(self, frames: int, wait_ms: int = 0) -> None:
        self.settle(wait_ms)
        self.frame()
        for _ in range(frames - 1):
            self.frame(fresh=False)

    def mark(self, name: str) -> None:
        self.marks[name] = len(self.frames)

    def move(self, x: float, y: float, frames: int, arc: float = 0.12) -> None:
        """To (x, y) in a slight curve, easing in and out, as a hand moves a mouse."""
        x0, y0 = self.x, self.y
        nx, ny = -(y - y0), x - x0  # the curve bows to one side of the straight path
        for k in range(1, frames + 1):
            p = smooth(k / frames)
            bow = arc * math.sin(math.pi * p)
            self.x, self.y = x0 + (x - x0) * p + nx * bow, y0 + (y - y0) * p + ny * bow
            self.page.mouse.move(self.x, self.y)
            self.frame()

    def path(self, points: list[tuple[float, float]], frames: int) -> None:
        """Along points (the pencil), at an even pace along their length."""
        lengths = np.r_[0, np.cumsum(np.hypot(*np.diff(np.array(points), axis=0).T))]
        for k in range(1, frames + 1):
            at = smooth(k / frames) * lengths[-1]
            i = min(len(points) - 2, int(np.searchsorted(lengths, at, side="right")) - 1)
            f = (at - lengths[i]) / max(1e-9, lengths[i + 1] - lengths[i])
            self.x = points[i][0] + (points[i + 1][0] - points[i][0]) * f
            self.y = points[i][1] + (points[i + 1][1] - points[i][1]) * f
            self.page.mouse.move(self.x, self.y)
            self.frame()

    def press(self) -> None:
        self.page.mouse.down()
        self.down = True
        self.frame()
        self.frame()

    def release(self, wait_ms: int = 0) -> None:
        self.page.mouse.up()
        self.down = False
        self.settle(wait_ms)
        self.frame()

    def click(self, x: float, y: float, frames: int, wait_ms: int = 150) -> None:
        self.move(x, y, frames)
        self.press()
        self.release(wait_ms)

    def drag(self, x: float, y: float, frames: int, wait_ms: int = 0) -> None:
        self.press()
        self.move(x, y, frames, arc=0.04)
        self.release(wait_ms)

    def save(self) -> None:
        facts = {"fps": FPS, "size": [APP["width"], APP["height"]], "frames": self.frames, "marks": self.marks}
        (ASSETS / "clips" / f"{self.name}.json").write_text(json.dumps(facts))
        print(f"  clip {self.name}: {len(self.frames)} frames, {self.shots} screenshots", flush=True)


def centre(locator) -> tuple[float, float]:
    box = locator.bounding_box()
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def relative(box: dict, origin: dict) -> dict:
    return {"x": box["x"] - origin["x"], "y": box["y"] - origin["y"], "width": box["width"], "height": box["height"]}


def field(scope, label: str):
    return scope.locator(".field", has=scope.page.locator(".label", has_text=label)).locator("input")


def frame_point(page, sx: float, sy: float) -> tuple[float, float]:
    """A source-frame point on the Recipe screen's frame, in page pixels (frame.js layout(), zoom 1)."""
    box = page.evaluate("""() => { const c = document.getElementById('frame').getBoundingClientRect();
        const b = document.getElementById('frameBox'); return [c.left, c.top, b.clientWidth, b.clientHeight]; }""")
    left, top, w, h = box
    s = min(w / 1920, h / 1080)
    return left + (w - 1920 * s) / 2 + sx * s, top + (h - 1080 * s) / 2 + sy * s


def record_recipe(page) -> dict:
    """The Recipe screen: add a Glass, move it onto the cup, size it to where the milk moves, set the
    zero line, save. The rule's time limit is typed after the clip and saved again."""
    page.locator("#toRecipes").click()
    page.locator("#newRecipe").click()  # the path prompt answers with the video
    page.locator("#editView").wait_for()
    page.locator("#recipeName").fill(RECIPE)
    scrub = page.locator("#scrub").bounding_box()
    page.mouse.click(scrub["x"] + scrub["width"] * 40 / 44.4, scrub["y"] + scrub["height"] / 2)  # milk in the cup
    page.mouse.move(1400, 600)
    page.wait_for_timeout(1200)

    clip = Clip(page, "recipe", (1430, 560))
    clip.hold(6)
    clip.click(*centre(page.locator("#addGlass")), 20)  # the default Glass: centre (960, 540), 230 x 292, zero 594
    clip.mark("added")
    clip.hold(4)
    clip.move(*frame_point(page, 960, 520), 16)
    clip.kind = "move"
    clip.mark("move")
    clip.drag(*frame_point(page, 1125, 655), 26)  # centre (1125, 675): box 895-1355 x 383-967, zero 729
    clip.kind = "arrow"
    clip.hold(3)
    clip.move(*frame_point(page, 895, 383), 12)
    clip.kind = "resize"
    clip.mark("resize")
    clip.drag(*frame_point(page, 875, 500), 20)
    clip.kind = "arrow"
    clip.move(*frame_point(page, 1355, 967), 14)
    clip.kind = "resize"
    clip.drag(*frame_point(page, 1375, 850), 20)
    clip.kind = "arrow"
    clip.hold(3)
    zero = page.locator("#selBody").locator(".field", has=page.locator(".label", has_text="0선 Y")).locator("input")
    zero_y = float(zero.input_value())
    clip.move(*frame_point(page, 1210, zero_y), 12)
    clip.kind = "zero"
    clip.mark("zero")
    clip.drag(*frame_point(page, 1210, ZERO_Y), 18)
    clip.kind = "arrow"
    clip.hold(4)
    clip.mark("save")
    clip.click(*centre(page.locator("#save")), 18, wait_ms=500)
    clip.hold(16)
    clip.save()

    body = page.locator("#selBody")
    glass = {key: float(field(body, label).input_value()) for key, label in (
        ("center_x", "중심 X"), ("center_y", "중심 Y"), ("radius_x", "반지름 X"), ("radius_y", "반지름 Y"))}
    zero_line = float(field(body, "0선 Y").input_value())
    limit = field(body, "회복 제한 시간")
    limit.fill(f"{LIMIT_SEC:g}")
    limit.press("Enter")
    page.wait_for_timeout(400)
    page.locator("#save").click()
    page.wait_for_function("document.getElementById('editNotice').textContent.includes('저장했습니다')")
    return {"ellipse": glass, "zero": zero_line}


def record_setup(page, server) -> str:
    """The analysis setup, filled in; the clip clicks "분석 시작". The id of the analysed inspection."""
    page.locator("#back").click()
    page.locator("#recipesView").wait_for()
    page.goto(server.url)
    page.get_by_role("button", name="새 검사").click()
    page.locator("#pickRows tr", has_text=RECIPE).click()
    page.locator("#pickNext").click()
    setup = page.locator("#setupView")
    setup.wait_for()
    setup.get_by_label("검사 이름").fill(NAME)
    for label, value in (("기동 시각", "5"), ("압축기 모델", HEADER["compressor_model"]), ("시험 종류", HEADER["test_type"])):
        box = field(setup, label)
        box.fill(value)
        box.press("Enter")
    page.wait_for_function("document.getElementById('setupProblemCount').textContent === ''")
    page.locator("#frame").focus()
    page.mouse.move(900, 500)
    page.wait_for_timeout(800)

    clip = Clip(page, "setup", (980, 520))
    clip.hold(4)
    clip.click(*centre(page.locator("#startAnalysis")), 22)
    clip.hold(2)
    clip.save()
    for _ in range(600):
        listed = server.call("GET", "/api/inspections")["inspections"]
        if listed and listed[0]["state"] == "ANALYSED":
            return listed[0]["id"]
        time.sleep(0.2)
    raise RuntimeError("분석이 끝나지 않았습니다")


def edge(context: np.ndarray, top: float, bottom: float) -> list[float]:
    """The top of the milk per sample (source-frame y), the Glass bottom where there is none."""
    white = context.min(axis=2)
    scale = (bottom - top) / context.shape[0]
    ys = []
    for column in white.T:
        rows = np.flatnonzero(np.convolve(column > WHITE, np.ones(6), "valid") == 6)
        ys.append(top + rows[0] * scale if rows.size else bottom)
    return [float(np.median(ys[max(0, i - 2):i + 3])) for i in range(len(ys))]


def context_point(page, t: float, y: float, facts: dict) -> tuple[float, float]:
    """A time and source-frame y on the editor's context image, in page pixels."""
    box = page.locator("#context image").bounding_box()
    t0, t1 = facts["view"]
    return (box["x"] + (t - t0) / (t1 - t0) * box["width"],
            box["y"] + (y - facts["top"]) / (facts["bottom"] - facts["top"]) * box["height"])


def record_edit(page, facts: dict) -> None:
    """The editor: the draft as it came, then the pencil along the milk's edge where the draft
    missed it, a click that shows that moment in the video, the Glass checked."""
    page.wait_for_function("document.querySelectorAll('#context image').length === 1")
    page.mouse.move(800, 450)
    page.wait_for_timeout(1500)
    page.screenshot(path=str(ASSETS / "editor-draft.jpg"), type="jpeg", quality=92)
    hide = page.add_style_tag(content="#graph [data-kind=oil], #context [data-kind=oil] { visibility: hidden }")
    page.wait_for_timeout(200)
    page.screenshot(path=str(ASSETS / "editor-noline.jpg"), type="jpeg", quality=92)
    hide.evaluate("node => node.remove()")
    facts["boxes"] = {name: page.locator(selector).first.bounding_box() for name, selector in (
        ("graph", "#graphBox"), ("context", "#contextBox"), ("contextImage", "#context image"),
        ("video", "#videoBox"), ("judgment", "#judgmentSection"), ("toolbar", "#editorView header.toolbar"),
        ("pencil", "#editorView button[data-tool=pencil]"), ("submit", "#editorSubmit"))}

    points = [context_point(page, t, y, facts) for t, y in zip(facts["times"], facts["edge"]) if t <= EDGE_SEC]
    points.insert(0, context_point(page, 0.0, facts["bottom"] - 2, facts))  # from the Glass bottom: EMPTY

    clip = Clip(page, "edit", (900, 420))
    clip.hold(4)
    clip.click(*centre(page.locator("#editorView button[data-tool=pencil]")), 20)
    clip.hold(3)
    clip.move(*points[0], 20)
    clip.kind = "pencil"
    clip.mark("stroke")
    clip.press()
    clip.path(points, 78)
    clip.release(wait_ms=700)
    clip.mark("stroked")
    clip.hold(14, wait_ms=300)
    clip.kind = "arrow"
    clip.click(*centre(page.locator("#editorView button[data-tool=select]")), 18)
    clip.mark("look")
    clip.click(*context_point(page, 20.0, 760.0, facts), 22, wait_ms=900)
    clip.hold(30, wait_ms=300)
    clip.mark("check")
    clip.click(*centre(page.locator("#checkGlass")), 24, wait_ms=700)
    clip.hold(12)
    clip.save()

    page.mouse.move(800, 300)
    page.wait_for_timeout(500)
    page.screenshot(path=str(ASSETS / "editor-final.jpg"), type="jpeg", quality=92)
    # the judgment, alone, and where its verdict and rows are in it
    section = page.locator("#judgmentSection")
    origin = section.bounding_box()
    facts["judgmentRows"] = [
        {"label": row.locator("th, td").first.inner_text(), "box": relative(row.bounding_box(), origin)}
        for row in page.locator("#judgmentFacts tr").all()]
    facts["verdict"] = relative(page.locator("#verdictBadge").bounding_box(), origin)
    section.screenshot(path=str(ASSETS / "judgment.png"))
    page.evaluate("for (const node of document.querySelectorAll('*')) if (node.scrollTop) node.scrollTop = 0")


def record_submit(page) -> None:
    clip = Clip(page, "submit", (1000, 300))
    clip.hold(4)
    clip.click(*centre(page.locator("#editorSubmit")), 22, wait_ms=500)
    clip.mark("dialog")
    clip.hold(10)
    clip.click(*centre(page.locator("#submitConfirm")), 22, wait_ms=1200)
    clip.mark("submitted")
    clip.hold(24)
    clip.save()


def make_assets(video: Path) -> None:
    from playwright.sync_api import sync_playwright

    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    ASSETS.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as temp, sync_playwright() as playwright:
        data = Path(temp) / "data"
        data.mkdir()
        server = Server(data)
        try:
            browser = playwright.chromium.launch(channel="chrome")
            page = browser.new_page(viewport=APP, device_scale_factor=2)
            page.on("dialog", lambda dialog: dialog.accept(str(video)))  # no window: the path prompt
            page.goto(server.url)
            page.wait_for_timeout(600)

            drawn = record_recipe(page)
            print(f"  Glass as drawn: {drawn}", flush=True)
            inspection = record_setup(page, server)

            # the facts the page's scenes are drawn from: the line as drafted and the milk's edge
            context = cv2.imread(str(next((data / "Inspections").glob("*/cache/*/context-000.png"))))
            cv2.imwrite(str(ASSETS / "context.png"), context)
            e = drawn["ellipse"]
            top, bottom = e["center_y"] - e["radius_y"], e["center_y"] + e["radius_y"]
            edits = server.call("GET", f"/api/inspections/{inspection}/edits")["edits"]
            times = edits["times"]
            dt = (times[-1] - times[0]) / (len(times) - 1)
            facts = {"glass": drawn, "top": top, "bottom": bottom, "times": times,
                     "view": [times[0] - dt / 2, times[-1] + dt / 2],
                     "draft": edits["glasses"][0]["oil"]["ys"], "edge": edge(context, top, bottom),
                     "band": [e["center_x"] - 0.4 * e["radius_x"], e["center_x"] + 0.4 * e["radius_x"]]}
            record_edit(page, facts)
            record_submit(page)
            (ASSETS / "facts.json").write_text(json.dumps(facts, ensure_ascii=False))

            report = next((data / "Inspections").glob("*/versions/001/report.html"))
            page.goto(report.as_uri())
            page.wait_for_timeout(1500)
            for i, section in enumerate(page.locator("section.page").all()[:2]):
                section.screenshot(path=str(ASSETS / f"report-{i}.png"))
            browser.close()
        finally:
            server.close()

    # the cup at 24 moments, for the scene that builds the context image
    capture = cv2.VideoCapture(str(video))
    duration = capture.get(cv2.CAP_PROP_FRAME_COUNT) / capture.get(cv2.CAP_PROP_FPS)
    for i in range(24):
        capture.set(cv2.CAP_PROP_POS_MSEC, duration * 1000 * i / 23 * 0.999)
        ok, frame = capture.read()
        crop = frame[300:1000, 760:1490]  # the cup
        cv2.imwrite(str(ASSETS / f"cup-{i:02d}.jpg"), crop, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"assets: {ASSETS}")


# ---- 2. frames ----

def open_page(playwright):
    browser = playwright.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def serve(route):
        path = PAGE / route.request.url.removeprefix(ORIGIN).split("?")[0]
        if path.is_file():
            route.fulfill(path=str(path), content_type=mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        else:
            route.fulfill(status=404, body="")

    page.route(f"{ORIGIN}**", serve)
    page.goto(f"{ORIGIN}intro.html")
    meta = page.evaluate("window.intro.ready")
    return browser, page, meta, errors


# ---- 3. sound ----

def envelope(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / RATE
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def lowpass(x: np.ndarray, cutoff: np.ndarray | float) -> np.ndarray:
    """One-pole low-pass; the cutoff may change per sample."""
    a = np.exp(-2 * np.pi * np.broadcast_to(cutoff, x.shape) / RATE)
    y, out = 0.0, np.empty_like(x)
    for i, (v, k) in enumerate(zip(x, a)):
        y = (1 - k) * v + k * y
        out[i] = y
    return out


def sound(kind: str, rng: np.random.Generator) -> np.ndarray:
    def secs(s: float) -> int:
        return int(s * RATE)

    t = lambda n: np.arange(n) / RATE  # noqa: E731
    if kind == "tick":
        n = secs(0.03)
        return rng.standard_normal(n) * envelope(n, 0.0005, 0.004) * 0.5 + np.sin(2 * np.pi * 3200 * t(n)) * envelope(n, 0.0005, 0.006) * 0.3
    if kind == "click":  # a mouse button
        n = secs(0.04)
        return rng.standard_normal(n) * envelope(n, 0.0003, 0.003) * 0.6 + np.sin(2 * np.pi * 2400 * t(n)) * envelope(n, 0.0003, 0.004) * 0.35
    if kind == "type":
        n = secs(0.05)
        body = np.sin(2 * np.pi * 1800 * t(n)) * envelope(n, 0.0005, 0.01)
        return (body * 0.4 + rng.standard_normal(n) * envelope(n, 0.0003, 0.003) * 0.4)
    if kind == "tok":
        n = secs(0.25)
        return np.sin(2 * np.pi * 620 * t(n) + 2 * np.sin(2 * np.pi * 310 * t(n)) * envelope(n, 0.001, 0.02)) * envelope(n, 0.002, 0.07) * 0.7
    if kind == "whoosh":
        n = secs(0.9)
        x = t(n) / 0.9
        cutoff = 300 + 5000 * np.sin(np.pi * x) ** 2
        noise = lowpass(rng.standard_normal(n), cutoff)
        return noise * np.sin(np.pi * x) ** 2 * 1.6
    if kind == "riser":
        n = secs(2.4)
        x = t(n)
        freq = 70 * (1 + x / 2.4 * 1.6)
        phase = 2 * np.pi * np.cumsum(freq) / RATE
        tone = np.sin(phase) + 0.35 * np.sin(2 * phase) + 0.15 * np.sin(3 * phase)
        return tone * (x / 2.4) ** 1.5 * np.exp(-np.maximum(0, x - 2.1) / 0.1) * 0.45
    if kind == "scribble":
        n = secs(2.3)
        x = t(n)
        strokes = 0.6 + 0.4 * np.sin(2 * np.pi * 7 * x) ** 2
        return lowpass(rng.standard_normal(n), 2500) * strokes * np.sin(np.pi * x / 2.3) ** 0.5 * 0.5
    if kind == "stamp":
        n = secs(0.5)
        x = t(n)
        return (np.sin(2 * np.pi * 90 * x * (1 - x)) * envelope(n, 0.001, 0.09) + lowpass(rng.standard_normal(n), 900) * envelope(n, 0.001, 0.03) * 1.5) * 0.9
    if kind in ("chime", "shimmer"):
        n = secs(2.2)
        x = t(n)
        notes = (880, 1320) if kind == "chime" else (1760, 2637, 3520)
        out = np.zeros(n)
        for j, f in enumerate(notes):
            start = secs(0.09 * j)
            m = n - start
            out[start:] += np.sin(2 * np.pi * f * t(m)) * envelope(m, 0.003, 0.5 if kind == "chime" else 0.8)
        return out * (0.35 if kind == "chime" else 0.12)
    if kind == "flip":  # a card turning over
        n = secs(0.35)
        x = t(n) / 0.35
        return lowpass(rng.standard_normal(n), 1800 + 3000 * x) * np.sin(np.pi * x) ** 3 * 0.9
    raise ValueError(kind)


def reverb(x: np.ndarray) -> np.ndarray:
    """A light room: a few feedback delays."""
    out = x.copy()
    for delay, gain in ((0.031, 0.32), (0.047, 0.27), (0.071, 0.22), (0.113, 0.16)):
        d = int(delay * RATE)
        y = np.zeros_like(x)
        for start in range(0, len(x), d):
            y[start:start + d] = x[start:start + d] + (gain * y[start - d:start][: len(y[start:start + d])] if start >= d else 0)
        out += y * 0.35
    return out


def effects(cues: list, duration: float) -> np.ndarray:
    rng = np.random.default_rng(7)
    mix_ = np.zeros(int((duration + 1) * RATE))
    for at, kind, gain in cues:
        clip = sound(kind, rng) * gain
        start = int(at * RATE)
        end = min(len(mix_), start + len(clip))
        mix_[start:end] += clip[: end - start]
    return reverb(mix_)[: int(duration * RATE)]


def soundtrack(cues: list, duration: float, music: Path | None) -> np.ndarray:
    """Stereo: the music with the effects on top, or the effects alone; about -2 dBFS at the loudest
    (the AAC encoder overshoots a mix at -1 dBFS)."""
    sfx = effects(cues, duration)
    if music is None:
        mix_ = np.repeat(sfx[:, None] / max(1e-9, np.abs(sfx).max()) * 0.5, 2, axis=1)
    else:
        song = music_track(music, duration)
        sfx *= 0.35 * np.abs(song).max() / max(1e-9, np.abs(sfx).max())  # under the music
        mix_ = song + sfx[:, None]
    return mix_ * (0.78 / max(1e-9, np.abs(mix_).max()))


def write_wav(path: Path, samples: np.ndarray) -> None:
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(pcm.tobytes())


# the music (user, 2026-11-02: a Suno track, for the department's own use): 108 BPM, bars of 2.222 s
# from 0.034 s. The video keeps bars 0-33 (intro, build, the second section and the whole main
# section), then jumps to bar 66, the last section, whose final hit (bar 70, the video's bar 38) and
# tail end the video: 88.9 s in all. design/intro/intro.html times its scenes to these bars.
BAR, FIRST_BEAT = 60 / 108 * 4, 0.034
MUSIC_EDIT = ((0.0, FIRST_BEAT + 34 * BAR), (FIRST_BEAT + 66 * BAR, None))
SPLICE_SEC = 0.03


def music_track(path: Path, duration: float) -> np.ndarray:
    """The edited music, stereo at RATE, duration seconds long."""
    import imageio_ffmpeg

    raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-loglevel", "error", "-i", str(path), "-vn",
                          "-ac", "2", "-ar", str(RATE), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, "<f4").reshape(-1, 2).astype(float)
    fade = int(SPLICE_SEC * RATE)
    out = np.zeros((0, 2))
    for start, end in MUSIC_EDIT:
        piece = audio[int(start * RATE): None if end is None else int(end * RATE)].copy()
        if len(out):
            ramp = np.linspace(0, 1, fade)[:, None]
            out[-fade:] = out[-fade:] * (1 - ramp) + piece[:fade] * ramp
            piece = piece[fade:]
        out = np.concatenate([out, piece])
    total = int(duration * RATE)
    out = np.pad(out, ((0, max(0, total - len(out))), (0, 0)))[:total]
    tail = int(0.5 * RATE)
    out[-tail:] *= np.linspace(1, 0, tail)[:, None]
    return out


# ---- 4. the MP4 ----

def render(out: Path, music: Path | None) -> None:
    import imageio_ffmpeg
    from playwright.sync_api import sync_playwright

    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp, sync_playwright() as playwright:
        browser, page, meta, errors = open_page(playwright)
        fps, duration = meta["fps"], meta["duration"]
        audio = Path(temp) / "sound.wav"
        write_wav(audio, soundtrack(meta["cues"], duration, music))
        command = [
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "image2pipe", "-framerate", str(fps), "-i", "-", "-i", str(audio),
            "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out),
        ]
        encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
        began = time.perf_counter()
        total = int(duration * fps)
        for i in range(total):
            page.evaluate(f"window.intro.seek({i / fps})")
            encoder.stdin.write(page.screenshot(type="jpeg", quality=95))
            if i % (fps * 5) == 0:
                print(f"  frame {i}/{total} at {time.perf_counter() - began:.0f}s", flush=True)
        encoder.stdin.close()
        if encoder.wait() != 0:
            raise RuntimeError("ffmpeg가 실패했습니다")
        browser.close()
    if errors:
        print("page errors:", *errors, sep="\n  ")
    print(f"video: {out} ({out.stat().st_size / 1e6:.1f} MB, {time.perf_counter() - began:.0f}s)")


def stills(times: list[float], folder: Path) -> None:
    from playwright.sync_api import sync_playwright

    folder.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser, page, _meta, errors = open_page(playwright)
        for t in times:
            page.evaluate(f"window.intro.seek({t})")
            page.screenshot(path=str(folder / f"t{t:05.1f}.png"))
        browser.close()
    if errors:
        print("page errors:", *errors, sep="\n  ")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--video", type=Path, default=ROOT / "sample" / "sample7.mp4")
    parser.add_argument("--out", type=Path, default=Path.home() / "Movies" / "OilLevelTracker" / "intro.mp4")
    parser.add_argument("--music", type=Path, help="the music track; without it, the effects alone")
    parser.add_argument("--skip-assets", action="store_true", help="use design/intro/assets/ as it is")
    parser.add_argument("--assets-only", action="store_true", help="make the assets and stop")
    parser.add_argument("--stills", help="only screenshots at these times (comma-separated), beside --out")
    args = parser.parse_args()
    if not args.skip_assets:
        make_assets(args.video.resolve())
    if args.assets_only:
        return
    if args.stills:
        stills([float(s) for s in args.stills.split(",")], args.out.expanduser().parent / "stills")
    else:
        render(args.out.expanduser(), args.music)


if __name__ == "__main__":
    main()
