"""Mac/Chromium smoke check of the spike editor (no Windows claim).

Starts app.py with --no-window, drives the page with Playwright and prints one
line per check. Usage:
  python spikes/webui/check_ui.py --video V --recipe R --out DIR [--draft-spacing S] [--channel chrome]
"""
from __future__ import annotations

import argparse
import re
import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}".rstrip(), flush=True)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--recipe", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--draft-spacing", default="2.0")
    parser.add_argument("--rate", default="2.0")
    parser.add_argument("--channel", default=None, help="e.g. chrome; default is Playwright's Chromium")
    args = parser.parse_args()

    port = free_port()
    server = subprocess.Popen([sys.executable, str(HERE / "app.py"), "--video", args.video, "--recipe", args.recipe,
                               "--out", str(args.out), "--port", str(port), "--no-window",
                               "--draft-spacing", args.draft_spacing, "--rate", args.rate],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        for line in server.stdout:
            if line.startswith("SPIKE context "):
                print(line.strip())
            if line.startswith("SPIKE server"):
                break
        else:
            print("server did not start")
            return 2
        return run(f"http://127.0.0.1:{port}/", args)
    finally:
        server.terminate()
        server.wait(timeout=10)


def run(url: str, args) -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=args.channel) if args.channel else p.chromium.launch()
        page = browser.new_page(viewport={"width": 1500, "height": 950})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        opened: list[str] = []
        page.route("**/api/open", lambda route: (opened.append(route.request.post_data or ""),
                                                 route.fulfill(json={"ok": True})))
        page.goto(url)
        page.wait_for_function("document.getElementById('diag').textContent.includes('context:')")
        diag = lambda: page.locator("#diag").text_content()  # noqa: E731
        check("load", True, diag().splitlines()[0])

        graph = page.locator("#graphPanel")
        ctxp = page.locator("#contextPanel")
        gb, cb = graph.bounding_box(), ctxp.bounding_box()
        points_of = lambda line: page.locator(f"#graphPanel [data-kind=point][data-line='{line}']")  # noqa: E731
        draft_count = points_of(0).count()

        # W7 frame: click empty graph area
        page.mouse.click(gb["x"] + gb["width"] * 0.55, gb["y"] + 20)
        page.wait_for_function("document.querySelector('#framePanel image') !== null")
        check("W7 frame on click", True, page.locator("#frameTime").text_content())

        # W5 drag a point (snap off so the move is exact)
        page.uncheck("#snap")
        target = points_of(0).nth(min(10, draft_count - 1))
        box = target.bounding_box()
        before = page.locator("#selectionInfo").text_content()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.down()
        for step in range(1, 11):  # downward: the draft points near the top would leave the panel
            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2 + 2 * step)
        page.mouse.up()
        after = page.locator("#selectionInfo").text_content()
        check("W5 drag point", "px" in after and after != before, after)

        # W5 corner toggle and undo
        sel = page.locator("#graphPanel .point.selected")
        sb = sel.bounding_box()
        page.mouse.dblclick(sb["x"] + sb["width"] / 2, sb["y"] + sb["height"] / 2)
        page.wait_for_timeout(100)
        corner = page.locator("#graphPanel rect.point.selected, #graphPanel rect[data-kind=point]").count() > 0
        check("W5 corner toggle", corner, page.locator("#selectionInfo").text_content())
        page.keyboard.press("Control+z")
        page.wait_for_timeout(100)
        check("W5 undo corner", page.locator("#graphPanel rect[data-kind=point]").count() == 0)
        page.keyboard.press("Control+Shift+z")
        page.wait_for_timeout(100)
        check("W5 redo corner", page.locator("#graphPanel rect[data-kind=point]").count() == 1)

        # W5 new Foam line with four points on the context image
        page.select_option("#newLineKind", "foam")
        page.click("#newLine")
        for fx, fy in ((0.40, 0.35), (0.50, 0.30), (0.60, 0.40), (0.72, 0.33)):
            page.mouse.click(cb["x"] + cb["width"] * fx, cb["y"] + cb["height"] * fy)
        page.wait_for_timeout(100)
        check("W5 Foam line", page.locator("#contextPanel path.curve-foam").count() == 1,
              f"foam points={points_of(1).count()}")

        # W5 segment
        page.keyboard.press("s")
        page.mouse.move(cb["x"] + cb["width"] * 0.08, cb["y"] + cb["height"] * 0.8)
        page.mouse.down()
        page.mouse.move(cb["x"] + cb["width"] * 0.30, cb["y"] + cb["height"] * 0.8, steps=8)
        page.mouse.up()
        check("W5 segment", page.locator("#graphPanel [data-kind=segment]").count() == 1,
              page.locator("#selectionInfo").text_content())

        # W5 memo
        page.keyboard.press("m")
        page.mouse.click(cb["x"] + cb["width"] * 0.8, cb["y"] + cb["height"] * 0.6)
        page.keyboard.type("Foam 경계 확인")
        page.wait_for_timeout(100)
        check("W5 memo", "Foam 경계 확인" in page.locator("#memoList").text_content())
        page.mouse.click(10, 10)  # leave the memo box

        # W5 delete a point
        page.keyboard.press("v")
        foam_before = points_of(1).count()
        fp = points_of(1).nth(1).bounding_box()
        page.mouse.click(fp["x"] + fp["width"] / 2, fp["y"] + fp["height"] / 2)
        page.keyboard.press("Delete")
        page.wait_for_timeout(100)
        check("W5 delete point", points_of(1).count() == foam_before - 1)

        # W5 zoom and pan
        ticks_before = page.locator("#graphPanel text.tick").all_text_contents()
        page.mouse.move(gb["x"] + gb["width"] * 0.5, gb["y"] + gb["height"] * 0.5)
        page.mouse.wheel(0, -600)
        page.wait_for_timeout(100)
        ticks_zoom = page.locator("#graphPanel text.tick").all_text_contents()
        check("W5 wheel zoom", ticks_zoom != ticks_before)
        page.mouse.move(gb["x"] + gb["width"] * 0.6, gb["y"] + 15)
        page.mouse.down()
        page.mouse.move(gb["x"] + gb["width"] * 0.3, gb["y"] + 15, steps=6)
        page.mouse.up()
        check("W5 pan", page.locator("#graphPanel text.tick").all_text_contents() != ticks_zoom)
        page.keyboard.press("f")

        # W6 snap: a dragged point lands on an integer row height
        page.check("#snap")
        page.wait_for_timeout(50)
        target = points_of(0).nth(min(5, draft_count - 1))
        box = target.bounding_box()
        page.mouse.move(box["x"] + 4, box["y"] + 4)
        page.mouse.down()
        page.mouse.move(box["x"] + 4, box["y"] + 4 - 13, steps=5)
        page.mouse.up()
        info = page.locator("#selectionInfo").text_content()
        h = float(re.search(r"(-?[\d.]+) px", info).group(1))
        check("W6 snap to row", abs(h - round(h)) < 1e-6, info)

        # background view toggle
        page.check("#bgView")
        page.wait_for_timeout(100)
        check("bg view", page.locator("#contextPanel image").get_attribute("href").endswith("context_bg.png"))
        page.uncheck("#bgView")

        # W9 drag smoothness: render times while dragging a point
        page.uncheck("#snap")
        target = points_of(0).nth(draft_count // 2)
        box = target.bounding_box()
        page.mouse.move(box["x"] + 4, box["y"] + 4)
        page.mouse.down()
        t0 = time.perf_counter()
        for step in range(60):
            page.mouse.move(box["x"] + 4 + (step % 7), box["y"] + 4 - step)
        page.mouse.up()
        elapsed = time.perf_counter() - t0
        render_line = [l for l in diag().splitlines() if l.startswith("render")][0]
        render_median = float(re.search(r"median: ([\d.]+)", render_line).group(1))
        check("W9 render while dragging", render_median < 16, f"{render_line}; 60 moves in {elapsed:.2f}s; "
              f"points={sum(points_of(i).count() for i in range(2))}")

        # several seeks for W7 timing
        for fx in (0.1, 0.3, 0.5, 0.7, 0.9, 0.2, 0.4, 0.6, 0.8, 0.95):
            page.mouse.click(gb["x"] + gb["width"] * fx, gb["y"] + 15)
            page.wait_for_timeout(250)
        seek_line = [l for l in diag().splitlines() if l.startswith("frame seek")][0]
        check("W7 seek timing", "n=" in seek_line, seek_line)

        # save and report
        page.click("#save")
        page.wait_for_function("document.getElementById('status').textContent.includes('저장됨')")
        check("save", True, page.locator("#status").text_content())
        page.click("#report")
        page.wait_for_function("document.getElementById('status').textContent.includes('보고서 v')")
        status = page.locator("#status").text_content()
        report_path = Path(status.split("작성: ", 1)[1])
        check("report written", report_path.is_file(), f"{report_path.name} {report_path.stat().st_size} bytes")
        check("report open requested", bool(opened))

        # W8 (Chromium part): the report renders offline from file://
        report = browser.new_context(offline=True).new_page()
        report_errors: list[str] = []
        report.on("pageerror", lambda e: report_errors.append(str(e)))
        report.goto(report_path.as_uri())
        report.wait_for_selector("#r-context path.curve")
        check("W8 report renders offline", not report_errors and report.locator("#r-context image").count() == 1
              and "Foam 경계 확인" in report.locator(".memo-report").text_content(),
              f"curves={report.locator('#r-graph path.curve').count()} errors={report_errors}")
        pdf = args.out / "report-check.pdf"
        report.pdf(path=str(pdf), format="A4", landscape=True)
        check("W8 print to PDF (Chromium)", pdf.stat().st_size > 10_000, f"{pdf.stat().st_size} bytes")
        report.screenshot(path=str(args.out / "report-check.png"), full_page=True)
        page.screenshot(path=str(args.out / "editor-check.png"))

        # reload resumes the saved version
        page.goto(url)
        page.wait_for_function("document.getElementById('status').textContent.includes('저장본')")
        check("resume saved version", True, page.locator("#status").text_content())

        check("no page errors", not errors, "; ".join(errors[:3]))
        browser.close()
    failed = [name for name, ok, _ in results if not ok]
    print(f"SUMMARY {len(results) - len(failed)}/{len(results)} PASS" + (f" FAILED={failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
