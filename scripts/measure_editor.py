"""Measure the editor on one PC, for A5 and A6 (Product SSOT §2). A person runs it in a terminal.

Stages:
1. the PC and its software;
2. the source check;
3. the analysis of the whole video through the app's own server, timed from "분석 시작" to the end;
4. the editor in a browser driven by Playwright. On Windows that is Microsoft Edge, WebView2's
   engine, so the PC needs no pywebview:
   - A5: three pencil strokes over the whole view, then grab-and-drag over the whole view and
     zoomed in. The page times each lines redraw during a drag (the spike's measure); the frame
     intervals during the drags are recorded beside it.
   - A6: exact frames at random times (paused), then 1x playback. For reference, the <video>'s own
     seeks too.
It writes the result file (Markdown) and a data folder for the inspection, and prints the text.

Usage: python scripts/measure_editor.py --video VIDEO --recipe RECIPE.recipe.json
           [--browser msedge] [--size 1920x1040] [--drags 8] [--seeks 40] [--play-sec 60] [--out RESULT.md]
"""

from __future__ import annotations

import argparse
import http.client
import json
import math
import platform
import random
import shutil
import statistics
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))  # this folder's code, even where another copy is installed

import cv2  # noqa: E402

from oil_tracker import bootstrap  # noqa: E402
from oil_tracker.adapters.storage.recipe_files import recipe_from_json  # noqa: E402
from oil_tracker.domain.inspection import needs_compressor_start  # noqa: E402
from time_analysis import package_version, pc_inventory, source_digest, video_facts  # noqa: E402

NAME = "A5A6 측정"
PAUSE_MS = 8  # between mouse moves: a 125 Hz mouse
CODECS = {"h264": 'video/mp4; codecs="avc1.640028"', "hevc": 'video/mp4; codecs="hvc1.1.6.L120.90"'}


class Server:
    def __init__(self, data: Path) -> None:
        self.running = bootstrap.start(data_folder=data)

    def call(self, method: str, path: str, body: object = None) -> dict:
        connection = http.client.HTTPConnection("127.0.0.1", self.running.server.server_address[1], timeout=60)
        headers = {"X-OLT-Token": self.running.token, "Content-Type": "application/json"}
        connection.request(method, path, None if body is None else json.dumps(body).encode(), headers)
        response = connection.getresponse()
        data = json.loads(response.read() or b"{}")
        connection.close()
        if response.status >= 400:
            raise RuntimeError(f"{method} {path}: HTTP {response.status} {data}")
        return data

    def close(self) -> None:
        self.running.close()


def fourcc(path: Path) -> str:
    capture = cv2.VideoCapture(str(path))
    try:
        code = int(capture.get(cv2.CAP_PROP_FOURCC))
        return "".join(chr((code >> 8 * i) & 0xFF) for i in range(4)).strip() or "?"
    finally:
        capture.release()


def analyse(server: Server, video: Path, recipe) -> tuple[str, float]:
    """Make the inspection and analyse the whole video, as "분석 시작" does; return its id and seconds."""
    opened = server.call("POST", "/api/videos", {"path": str(video)})
    duration = opened["frame_count"] / opened["fps"]
    compressor = min(485.0, duration / 2) if needs_compressor_start(recipe) else None
    setup = {
        "inspection_id": None, "video_id": opened["id"], "recipe_id": recipe.id, "name": NAME,
        "glasses": [
            {"id": g.id, "zero_line_y": g.zero_line_y, "ellipse": {
                "center_x": g.ellipse.center_x, "center_y": g.ellipse.center_y,
                "radius_x": g.ellipse.radius_x, "radius_y": g.ellipse.radius_y}}
            for g in recipe.glasses
        ],
        "settings": {"start_sec": 0.0, "end_sec": duration, "compressor_start_sec": compressor},
    }
    began = time.perf_counter()
    started = server.call("POST", "/api/inspections/start", setup)
    reported = began
    while True:
        job = server.call("GET", f"/api/jobs/{started['job']['id']}")
        if job["state"] != "running":
            break
        if time.perf_counter() - reported >= 30:
            print(f"  progress {100 * job['fraction']:.0f}% at {time.perf_counter() - began:.0f}s", flush=True)
            reported = time.perf_counter()
        time.sleep(0.2)
    if job["state"] != "finished":
        raise RuntimeError(f"분석이 끝나지 않았습니다: {job['state']} {job['message']}")
    server.call("DELETE", f"/api/videos/{opened['id']}")
    return started["inspection"]["id"], time.perf_counter() - began


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"n": 0, "median": math.nan, "p95": math.nan, "max": math.nan}
    ordered = sorted(values)
    return {"n": len(values), "median": statistics.median(ordered),
            "p95": ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)], "max": ordered[-1]}


class Editor:
    """The editor page, driven like a person would: mouse, wheel and keys."""

    def __init__(self, page) -> None:
        self.page = page
        page.evaluate("""() => { window.__frames = [];
            const tick = (t) => { window.__frames.push(t); requestAnimationFrame(tick); };
            requestAnimationFrame(tick); }""")
        self.windows: list[tuple[float, float]] = []

    def measurements(self) -> dict:
        return self.page.evaluate("async () => (await import('/web/editor.js')).measurements()")

    def now(self) -> float:
        return self.page.evaluate("performance.now()")

    def graph(self) -> dict:
        return self.page.locator("#graph").bounding_box()

    def point_on(self, kind: str, share: float) -> tuple[float, float] | None:
        found = self.page.evaluate(
            """([kind, share]) => { const p = document.querySelector(`#graph path[data-kind=${kind}]`);
            if (!p) return null; const at = p.getPointAtLength(p.getTotalLength() * share); return [at.x, at.y]; }""",
            [kind, share],
        )
        if found is None:
            return None
        box = self.graph()
        return box["x"] + found[0], box["y"] + found[1]

    def stroke(self, points: list[tuple[float, float]]) -> None:
        began = self.now()
        self.page.mouse.move(*points[0])
        self.page.mouse.down()
        for point in points[1:]:
            self.page.mouse.move(*point)
            self.page.wait_for_timeout(PAUSE_MS)
        self.page.mouse.up()
        self.windows.append((began, self.now()))
        self.page.wait_for_timeout(400)  # the bands come back from the API

    def pencil(self, kind_label: str, height: float, moves: int = 60) -> None:
        self.page.keyboard.press("p")
        self.page.locator("#lineKind button", has_text=kind_label).click()
        box = self.graph()
        left, right = box["x"] + 60, box["x"] + box["width"] - 20
        y = box["y"] + box["height"] * height
        self.stroke([(left + (right - left) * k / moves, y + 6 * math.sin(k / 3)) for k in range(moves + 1)])

    def grabs(self, shares: list[float], amplitude: float = 50, moves: int = 30) -> None:
        self.page.keyboard.press("g")
        for share in shares:
            start = self.point_on("oil", share)
            if start is None:
                continue
            x, y = start
            self.stroke([(x, y + amplitude * math.sin(2 * math.pi * k / moves)) for k in range(moves + 1)])

    def zoom(self, factor: float) -> None:
        box = self.graph()
        self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        for _ in range(5):
            self.page.mouse.wheel(0, math.log(factor) / 0.0015 / 5)
            self.page.wait_for_timeout(100)
        self.page.wait_for_timeout(500)

    def frame_intervals(self) -> list[float]:
        frames = self.page.evaluate("window.__frames")
        intervals = []
        for began, ended in self.windows:
            inside = [t for t in frames if began <= t <= ended]
            intervals += [b - a for a, b in zip(inside, inside[1:])]
        self.windows = []
        return intervals

    def click_axis(self, share: float) -> None:
        """Click the time axis between its two range numbers, which are inputs of their own."""
        box = self.page.locator("#axis").bounding_box()
        left, right = box["x"] + 100, box["x"] + box["width"] - 90
        self.page.mouse.click(left + (right - left) * share, box["y"] + box["height"] / 2)


def measure(page, url: str, drags: int, seeks: int, play_sec: float) -> dict:
    page.goto(url)
    row = page.locator("#inspectionRows tr", has_text=NAME)
    row.get_by_role("button", name="열기", exact=True).click()
    page.wait_for_function("document.querySelectorAll('#context image').length >= 1", timeout=120_000)
    editor = Editor(page)
    for _ in range(600):
        if editor.measurements()["lumaReady"]:
            break
        page.wait_for_timeout(100)
    found: dict = {"samples": editor.measurements()["samples"]}
    found["can_play"] = page.evaluate("codecs => Object.fromEntries(Object.entries(codecs).map(([k, v]) => "
                                      "[k, document.createElement('video').canPlayType(v) || 'no']))", CODECS)

    print("  A5: 연필 (전체 보기)", flush=True)
    for label, height in (("Oil", 0.55), ("Foam", 0.4), ("참조", 0.7)):
        editor.pencil(label, height)
    redraws = editor.measurements()["redraws"]
    scenarios = [("연필, 전체 보기 (선 3개를 끝까지)", redraws, editor.frame_intervals())]

    print("  A5: 잡아끌기 (전체 보기)", flush=True)
    editor.grabs([0.1 + 0.8 * k / max(1, drags - 1) for k in range(drags)])
    after = editor.measurements()["redraws"]
    scenarios.append(("잡아끌기, 전체 보기", after[len(redraws):], editor.frame_intervals()))

    print("  A5: 잡아끌기 (10배 확대)", flush=True)
    editor.zoom(0.1)
    editor.grabs([0.15 + 0.7 * k / max(1, drags - 1) for k in range(drags)])
    last = editor.measurements()["redraws"]
    scenarios.append(("잡아끌기, 10배 확대", last[len(after):], editor.frame_intervals()))
    found["a5"] = [(name, stats(r), stats(f)) for name, r, f in scenarios]
    found["a5_all"] = stats(last)
    page.keyboard.press("Escape")

    print(f"  A6: 정확한 프레임 {seeks}번", flush=True)
    before = len(editor.measurements()["seeks"])
    chance = random.Random(29)
    for _ in range(seeks):
        editor.click_axis(chance.random())
        page.wait_for_timeout(500)
    found["seeks"] = stats(editor.measurements()["seeks"][before:])

    print(f"  A6: 1배 재생 {play_sec:g}초", flush=True)
    editor.click_axis(0.4)
    page.wait_for_timeout(800)
    page.evaluate("""() => { const v = document.getElementById('video'); window.__waiting = 0; window.__playing = false;
        v.addEventListener('playing', () => { window.__playing = true; });
        for (const name of ['waiting', 'stalled']) v.addEventListener(name, () => { if (window.__playing) window.__waiting += 1; }); }""")
    start = page.evaluate("""() => { const v = document.getElementById('video');
        const q = v.getVideoPlaybackQuality ? v.getVideoPlaybackQuality() : null;
        return { t: performance.now(), dropped: q ? q.droppedVideoFrames : 0, total: q ? q.totalVideoFrames : 0 }; }""")
    began_time = editor.measurements()["video"]["time"]
    page.keyboard.press("Space")
    page.wait_for_timeout(play_sec * 1000)
    end = page.evaluate("""() => { const v = document.getElementById('video');
        const q = v.getVideoPlaybackQuality ? v.getVideoPlaybackQuality() : null;
        return { t: performance.now(), dropped: q ? q.droppedVideoFrames : 0, total: q ? q.totalVideoFrames : 0,
                 waiting: window.__waiting }; }""")
    video = editor.measurements()["video"]
    page.keyboard.press("Space")
    page.wait_for_timeout(500)
    found["video_seeks"] = stats([] if video["fallback"] else page.evaluate("""async (count) => {
        const v = document.getElementById('video'); const times = []; let seed = 7;
        const next = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
        for (let k = 0; k < count; k++) {
          const began = performance.now();
          const done = new Promise((resolve) => v.addEventListener('seeked', resolve, { once: true }));
          v.currentTime = next() * v.duration;
          await done;
          times.push(performance.now() - began);
        }
        return times; }""", min(20, seeks)))
    found["play"] = {
        "element": "frames (대체)" if video["fallback"] else "<video>",
        "wall": (end["t"] - start["t"]) / 1000,
        "advanced": video["time"] - began_time,
        "waiting": end["waiting"],
        "dropped": end["dropped"] - start["dropped"],
        "total": end["total"] - start["total"],
    }
    return found


def markdown(facts: dict, found: dict, errors: list[tuple[str, str]]) -> str:
    pc, video = facts["pc"], facts["video"]
    lines = [
        "# A5·A6 편집기 측정 결과",
        "",
        f"- 측정: {facts['when']} (이 PC 시각)",
        f"- 소스: `source={facts['source'][0]} files={facts['source'][1]}`",
        f"- 소프트웨어: python {facts['python']}, opencv-python-headless {facts['opencv']}, "
        f"playwright {facts['playwright']}, 브라우저 {facts['browser']} {facts.get('browser_version', '?')}",
        f"- CPU: {pc['cpu']}, cores={pc['cores']}, logical={pc['logical']}, RAM {pc['ram_gb']} GB",
        f"- GPU: {pc['gpu']}; OS: {pc['os']}",
        f"- 영상: `{video['name']}`, {video['bytes']} bytes, {video['width']}x{video['height']}, "
        f"{video['fps']:.3f} fps, {video['frames']} frames, 코덱 `{facts['fourcc']}`",
        f"- Recipe: `{facts['recipe']}`, Glass {facts['glass_count']}개; 창 {facts['size']}",
    ]
    if "analysis_sec" in facts:
        lines.append(f"- 분석(앱 서버로, 창 없이): **{facts['analysis_sec']:.1f}초**, 샘플 {found.get('samples', '?')}개")
    if "can_play" in found:
        lines.append(f"- 브라우저가 재생할 수 있다는 코덱: H.264 `{found['can_play']['h264']}`, HEVC `{found['can_play']['hevc']}`")
    if "a5" in found:
        lines += [
            "",
            "## A5: 끄는 동안 선 다시 그리기 (ms)",
            "",
            "| 장면 | 횟수 | 중앙값 | 95% | 최대 | 프레임 간격 중앙값 | 95% | 최대 |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for name, redraw, frames in found["a5"]:
            lines.append(
                f"| {name} | {redraw['n']} | {redraw['median']:.1f} | {redraw['p95']:.1f} | {redraw['max']:.1f} "
                f"| {frames['median']:.1f} | {frames['p95']:.1f} | {frames['max']:.1f} |"
            )
        a = found["a5_all"]
        lines.append(f"| **전체** | {a['n']} | **{a['median']:.1f}** | {a['p95']:.1f} | **{a['max']:.1f}** | | | |")
    if "seeks" in found:
        s = found["seeks"]
        lines += ["", "## A6: 정확한 프레임 (ms)", "", "| 방식 | 횟수 | 중앙값 | 95% | 최대 |", "|---|---|---|---|---|",
                  f"| 정확한 프레임 (서버) | {s['n']} | **{s['median']:.0f}** | {s['p95']:.0f} | {s['max']:.0f} |"]
        v = found.get("video_seeks")
        if v and v["n"]:
            lines.append(f"| 참고: `<video>` 탐색 | {v['n']} | {v['median']:.0f} | {v['p95']:.0f} | {v['max']:.0f} |")
    if "play" in found:
        p = found["play"]
        lines += ["", "## A6: 1배 재생", "", "| 재생 방식 | 벽시계 (s) | 진행 (s) | waiting·stalled | 버린 프레임 / 전체 |",
                  "|---|---|---|---|---|",
                  f"| {p['element']} | {p['wall']:.1f} | **{p['advanced']:.1f}** | **{p['waiting']}** | {p['dropped']} / {p['total']} |"]
    lines += ["", f"오류: {'없음' if not errors else len(errors)}"]
    for name, text in errors:
        lines += ["", f"## 오류: {name}", "", "```", text.rstrip(), "```"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--browser", default="msedge", help="the Playwright channel: msedge on Windows, chrome on macOS")
    parser.add_argument("--size", default="1920x1040", help="the page size, as a maximised window on a 1080p screen")
    parser.add_argument("--drags", type=int, default=8, help="grab-and-drags per view")
    parser.add_argument("--seeks", type=int, default=40)
    parser.add_argument("--play-sec", type=float, default=60.0)
    parser.add_argument("--out", type=Path, help="the result file (default: a5a6-editor-<time>.md here)")
    args = parser.parse_args(argv)
    width, height = (int(n) for n in args.size.lower().split("x"))
    stamp = f"{datetime.now():%Y%m%d-%H%M}"
    out = args.out or Path(f"a5a6-editor-{stamp}.md")
    data = out.parent / f"a5a6-data-{stamp}"

    print("[1/4] PC와 소프트웨어 확인", flush=True)
    recipe = recipe_from_json(args.recipe.read_text(encoding="utf-8"))
    facts = {
        "when": f"{datetime.now():%Y-%m-%d %H:%M}",
        "python": platform.python_version(),
        "opencv": package_version("opencv-python-headless"),
        "playwright": package_version("playwright"),
        "browser": args.browser,
        "pc": pc_inventory(),
        "video": {"name": args.video.name, "bytes": args.video.stat().st_size, **video_facts(args.video)},
        "fourcc": fourcc(args.video),
        "recipe": recipe.name,
        "glass_count": len(recipe.glasses),
        "size": f"{width}x{height}",
    }
    pc = facts["pc"]
    print(f"  CPU: {pc['cpu']}, cores={pc['cores']}, logical={pc['logical']}, RAM {pc['ram_gb']} GB", flush=True)

    print("[2/4] 소스 확인", flush=True)
    facts["source"] = source_digest(script="measure_editor.py")
    print(f"  source={facts['source'][0]} files={facts['source'][1]}", flush=True)

    found: dict = {}
    errors: list[tuple[str, str]] = []
    (data / "Recipes").mkdir(parents=True)
    shutil.copyfile(args.recipe, data / "Recipes" / args.recipe.name)
    server = Server(data)
    try:
        print("[3/4] 분석 (앱 서버로, 진행 상황은 30초마다 표시)", flush=True)
        try:
            _, facts["analysis_sec"] = analyse(server, args.video, recipe)
            print(f"  끝: {facts['analysis_sec']:.1f}초", flush=True)
        except Exception:
            errors.append(("분석", traceback.format_exc()))
            print(errors[-1][1], flush=True)
        if not errors:
            print(f"[4/4] 편집기 측정: {args.browser}", flush=True)
            try:
                from playwright.sync_api import sync_playwright

                with sync_playwright() as p:
                    browser = p.chromium.launch(channel=args.browser, headless=False)
                    facts["browser_version"] = browser.version
                    page = browser.new_page(viewport={"width": width, "height": height})
                    page.on("pageerror", lambda error: errors.append(("페이지", str(error))))
                    found = measure(page, server.running.url, args.drags, args.seeks, args.play_sec)
                    browser.close()
            except Exception:
                errors.append(("편집기 측정", traceback.format_exc()))
                print(errors[-1][1], flush=True)
    finally:
        server.close()

    text = markdown(facts, found, errors)
    out.write_text(text, encoding="utf-8")
    print("", flush=True)
    print(text, flush=True)
    print(f"결과 파일: {out.resolve()}", flush=True)
    print(f"측정용 데이터 폴더(지워도 됨): {data.resolve()}", flush=True)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
