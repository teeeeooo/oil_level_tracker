"""Make the P-1 introduction video (docs/40-operations/intro-video.md). Not part of the app.

Stages:
1. assets, into design/intro/assets/ (ignored by Git): an inspection of the example video analysed
   through this folder's server in a temporary data folder, its Oil line taken from the context image
   where the draft misses, the screens captured in Chrome, and frames of the video;
2. the frames: design/intro/intro.html in Chrome, seek(t) and a screenshot every 1/30 s;
3. the sound: the page's cues, synthesised here (no recorded sound, nothing to license);
4. both muxed by imageio-ffmpeg's ffmpeg into an H.264 + AAC MP4.

Usage: python scripts/render_intro.py [--video sample/sample7.mp4] [--out ~/Movies/OilLevelTracker/intro.mp4]
           [--skip-assets] [--stills 3.5,20]
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import wave
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))  # this folder's code, even where another copy is installed
sys.path.insert(0, str(ROOT / "scripts"))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from measure_editor import Server  # noqa: E402
from oil_tracker import bootstrap  # noqa: E402

PAGE = ROOT / "design" / "intro"
ASSETS = PAGE / "assets"
ORIGIN = "http://intro.local/"
RATE = 48_000

# the Glass on sample7, inside the cup's rim and thick base (a trial on 2026-11-02: with either
# inside the ellipse the draft follows that edge instead)
GLASS = {"center_x": 1125.0, "center_y": 632.0, "radius_x": 260.0, "radius_y": 222.0}
ZERO_Y, COMPRESSOR_SEC = 700.0, 5.0
RULE = {"mode": "RECOVERY", "recovery_limit_sec": 30.0, "stable_hold_sec": 5.0,
        "minimum_valid_coverage_ratio": 0.7, "allowed_sec": 5.0, "allowed_px": 0.0}
WHITE = 195  # the milk in the context image: every channel above this
NAME, HEADER = "예시 검사", {"compressor_model": "예시 모델", "test_type": "예시 시험"}


# ---- 1. assets ----

def write_recipe(data: Path, video: Path) -> None:
    capture = cv2.VideoCapture(str(video))
    capture.set(cv2.CAP_PROP_POS_MSEC, 40_000)
    ok, frame = capture.read()
    if not ok:
        raise RuntimeError(f"영상을 읽지 못했습니다: {video}")
    height, width = frame.shape[:2]
    jpeg = cv2.imencode(".jpg", cv2.resize(frame, (width // 2, height // 2)), [cv2.IMWRITE_JPEG_QUALITY, 80])[1]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    recipe = {
        "format": "oil-level-tracker-recipe", "schema_version": 1, "id": str(uuid.uuid4()),
        "name": "예시 유리컵", "created_at": now, "updated_at": now,
        "reference_frame": {"width": width, "height": height, "source_name": video.name, "time_sec": 40.0,
                            "jpeg_base64": base64.b64encode(jpeg).decode()},
        "glasses": [{"id": str(uuid.uuid4()), "name": "GLASS", "ellipse": GLASS, "zero_line_y": ZERO_Y,
                     "judgment_rule": RULE}],
    }
    folder = data / "Recipes"
    folder.mkdir(parents=True)
    (folder / "예시 유리컵.recipe.json").write_text(json.dumps(recipe, ensure_ascii=False), encoding="utf-8")


def boundary(context: np.ndarray, top: float, bottom: float) -> list[float]:
    """The top of the milk per column (source-frame y), the Glass bottom where there is none."""
    white = context.min(axis=2)
    ys = []
    for column in white.T:
        rows = np.flatnonzero(np.convolve(column[20:] > WHITE, np.ones(6), "valid") == 6)
        ys.append(top + 20 + rows[0] if rows.size else bottom)
    smooth = [float(np.median(ys[max(0, i - 2):i + 3])) if 0 < i < len(ys) - 1 else float(ys[i]) for i in range(len(ys))]
    return smooth


def make_assets(video: Path) -> None:
    from playwright.sync_api import sync_playwright

    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    ASSETS.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as temp, sync_playwright() as playwright:
        data = Path(temp) / "data"
        write_recipe(data, video)
        server = Server(data)
        try:
            browser = playwright.chromium.launch(channel="chrome")
            page = browser.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=2)
            page.on("dialog", lambda dialog: dialog.accept(str(video)))  # no window: the path prompt

            # the analysis setup, as the inspector fills it in
            page.goto(server.url)
            page.get_by_role("button", name="새 검사").click()
            page.locator("#pickDialog").get_by_role("button", name="다음").click()
            page.locator("#setupView").wait_for()
            setup = page.locator("#setupView")
            setup.get_by_label("검사 이름").fill(NAME)
            for label, value in (("기동 시각", "5"), ("압축기 모델", HEADER["compressor_model"]),
                                 ("시험 종류", HEADER["test_type"])):
                box = setup.locator(".field", has=page.locator(".label", has_text=label)).locator("input")
                box.fill(value)
                box.press("Enter")
            page.wait_for_function("document.getElementById('setupProblemCount').textContent === ''")
            page.locator("#frame").focus()
            page.wait_for_timeout(800)
            page.screenshot(path=str(ASSETS / "setup.png"))
            page.get_by_role("button", name="분석 시작").click()
            for _ in range(600):
                listed = server.call("GET", "/api/inspections")["inspections"]
                if listed and listed[0]["state"] == "ANALYSED":
                    break
                time.sleep(0.2)
            else:
                raise RuntimeError("분석이 끝나지 않았습니다")
            inspection = listed[0]["id"]

            # the Oil line from the context image, checked
            context_png = next((data / "Inspections").glob("*/cache/*/context-000.png"))
            context = cv2.imread(str(context_png))
            cv2.imwrite(str(ASSETS / "context.png"), context)
            top, bottom = GLASS["center_y"] - GLASS["radius_y"], GLASS["center_y"] + GLASS["radius_y"]
            edits = server.call("GET", f"/api/inspections/{inspection}/edits")["edits"]
            glass = edits["glasses"][0]
            draft = list(glass["oil"]["ys"])
            ys = boundary(context, top, bottom)
            glass["oil"] = {"ys": ys, "origins": ["DRAWN"] * len(ys)}
            glass["decision"] = {"override": None, "reason": "", "checked_at": datetime.now(timezone.utc).isoformat()}
            server.call("POST", f"/api/inspections/{inspection}/edits", {"edits": edits})
            (ASSETS / "line.json").write_text(json.dumps(
                {"draft": draft, "ys": ys, "top": top, "bottom": bottom, "zero": ZERO_Y, "times": edits["times"]}))

            # the editor, then the submitted report
            page.goto(server.url)
            page.locator("#inspectionRows tr", has_text=NAME).get_by_role("button", name="열기", exact=True).click()
            page.wait_for_function("document.querySelectorAll('#context image').length === 1")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(ASSETS / "editor.png"))
            page.locator("#editorView .editor-left").screenshot(path=str(ASSETS / "graph.png"))
            page.locator("#judgmentSection").screenshot(path=str(ASSETS / "judgment.png"))
            server.call("POST", f"/api/inspections/{inspection}/submit", {"edits": edits})
            report = next((data / "Inspections").glob("*/versions/001/report.html"))
            page.goto(report.as_uri())
            page.wait_for_timeout(1500)
            page.screenshot(path=str(ASSETS / "report-crop.png"), clip={"x": 300, "y": 20, "width": 1400, "height": 990})
            browser.close()
        finally:
            server.close()

    capture = cv2.VideoCapture(str(video))
    duration = capture.get(cv2.CAP_PROP_FRAME_COUNT) / capture.get(cv2.CAP_PROP_FPS)
    for i in range(48):
        capture.set(cv2.CAP_PROP_POS_MSEC, duration * 1000 * i / 47 * 0.999)
        ok, frame = capture.read()
        crop = frame[300:1000, 760:1490]  # the cup
        cv2.imwrite(str(ASSETS / f"frame-{i:02d}.jpg"), crop, [cv2.IMWRITE_JPEG_QUALITY, 88])
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
    if kind == "glide":
        n = secs(4.0)
        x = t(n)
        phase = 2 * np.pi * np.cumsum(330 * 2 ** (x / 4.0)) / RATE
        return np.sin(phase) * np.sin(np.pi * x / 4.0) ** 2 * 0.18
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
    if kind == "boom":
        n = secs(3.5)
        x = t(n)
        body = np.sin(2 * np.pi * 52 * x) + 0.4 * np.sin(2 * np.pi * 104 * x)
        return (body * envelope(n, 0.01, 1.1) + lowpass(rng.standard_normal(n), 400) * envelope(n, 0.005, 0.25)) * 0.6
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


def soundtrack(cues: list, duration: float) -> np.ndarray:
    rng = np.random.default_rng(7)
    mix_ = np.zeros(int((duration + 1) * RATE))
    for at, kind, gain in cues:
        clip = sound(kind, rng) * gain
        start = int(at * RATE)
        end = min(len(mix_), start + len(clip))
        mix_[start:end] += clip[: end - start]
    mix_ = reverb(mix_)[: int(duration * RATE)]
    mix_ *= 0.5 / max(1e-9, np.abs(mix_).max())  # about -6 dBFS at the loudest
    return mix_


def write_wav(path: Path, samples: np.ndarray) -> None:
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())


# ---- 4. the MP4 ----

def render(out: Path) -> None:
    import imageio_ffmpeg
    from playwright.sync_api import sync_playwright

    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp, sync_playwright() as playwright:
        browser, page, meta, errors = open_page(playwright)
        fps, duration = meta["fps"], meta["duration"]
        audio = Path(temp) / "sound.wav"
        write_wav(audio, soundtrack(meta["cues"], duration))
        command = [
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "image2pipe", "-framerate", str(fps), "-i", "-", "-i", str(audio),
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out),
        ]
        encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
        began = time.perf_counter()
        total = int(duration * fps)
        for i in range(total):
            page.evaluate(f"window.intro.seek({i / fps})")
            encoder.stdin.write(page.screenshot(type="png"))
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
    parser.add_argument("--skip-assets", action="store_true", help="use design/intro/assets/ as it is")
    parser.add_argument("--stills", help="only screenshots at these times (comma-separated), beside --out")
    args = parser.parse_args()
    if not args.skip_assets:
        make_assets(args.video.resolve())
    if args.stills:
        stills([float(s) for s in args.stills.split(",")], args.out.parent / "stills")
    else:
        render(args.out.expanduser())


if __name__ == "__main__":
    main()
