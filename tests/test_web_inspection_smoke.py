"""Browser smoke check of the inspection screens on macOS Chrome (no Windows claim).

Skipped when Playwright or Chrome is missing. Set OLT_SMOKE_SHOTS to a folder to keep
screenshots.
"""

import json
import os
import shutil
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

from oil_tracker import bootstrap
from oil_tracker.adapters.storage.recipe_files import recipe_to_json
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.recipe import Glass, Recipe, ReferenceFrame

playwright_api = pytest.importorskip("playwright.sync_api")

W, H, FPS, COUNT = 320, 240, 10.0, 40
GLASS = Glass("g-base", "BASE", Ellipse(160, 120, 40, 100), 130)


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    path = tmp_path_factory.mktemp("video") / "level.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (W, H))
    for index in range(COUNT):
        frame = np.full((H, W, 3), 60, np.uint8)
        frame[150 - index:, 120:200] = 200  # a level that rises 1 px per frame inside the Glass
        writer.write(frame)
    writer.release()
    return path


def write_recipes(folder: Path) -> None:
    folder.mkdir(parents=True)
    fits = Recipe("r-fit", "스모크", ReferenceFrame(W, H, "level.avi", 0.0, b"jpeg"), (GLASS,), "c", "2026-10-29T01:00:00+00:00")
    other = Recipe("r-hd", "HD 카메라", ReferenceFrame(1920, 1080, "hd.mp4", 0.0, b"jpeg"),
                   (Glass("g-hd", "MAIN", Ellipse(900, 500, 80, 200), 520),), "c", "2026-10-29T02:00:00+00:00")
    for recipe in (fits, other):
        (folder / f"{recipe.name}.recipe.json").write_text(recipe_to_json(recipe), encoding="utf-8")


@pytest.fixture
def browser_page():
    with playwright_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception as error:  # noqa: BLE001
            pytest.skip(f"Chrome is not available: {error}")
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        errors: list[str] = []
        page.on("console", lambda message: errors.append(message.text)
                if message.type == "error" and not message.text.startswith("Failed to load resource") else None)
        page.on("pageerror", lambda error: errors.append(str(error)))
        yield page, errors
        browser.close()


def shot(page, name):
    folder = os.environ.get("OLT_SMOKE_SHOTS")
    if folder:
        page.screenshot(path=str(Path(folder) / f"{name}.png"))


def field(page, label):
    return page.locator("#setupView .field", has=page.locator(".label", has_text=label)).locator("input")


def test_new_inspection_from_video_to_result(tmp_path, video, browser_page):
    page, errors = browser_page
    data = tmp_path / "data"
    write_recipes(data / "Recipes")
    running = bootstrap.start(data_folder=data)
    try:
        page.on("dialog", lambda dialog: dialog.accept(str(video)))  # no window: the path prompt
        page.goto(running.url)
        page.get_by_text("검사가 없습니다").wait_for()
        page.keyboard.press("F1")
        assert page.locator("#helpTitle").inner_text() == "도움말 · 검사 목록"
        page.keyboard.press("Escape")
        shot(page, "i1-empty-list")

        # the video first, then a Recipe; one of another frame size is greyed with its reason
        page.get_by_role("button", name="새 검사").click()
        picker = page.locator("#pickDialog")
        picker.get_by_text("스모크").wait_for()
        assert "level.avi" in picker.locator("#pickVideo").inner_text()
        greyed = picker.locator("tr.off")
        assert "HD 카메라" in greyed.inner_text() and "1920×1080" in greyed.inner_text()
        assert picker.locator("tr.sel").inner_text().startswith("스모크")
        shot(page, "i2-picker")
        picker.get_by_role("button", name="다음").click()

        # the setup: RECOVERY needs the compressor start
        page.locator("#setupView").wait_for()
        page.wait_for_function("document.getElementById('time').textContent.startsWith('00:00.0')")
        assert page.locator("#setupTitle").inner_text() == "새 검사 · level.avi"
        page.get_by_text("기준점 회복 Glass가 있어 압축기 기동 시각이 필요합니다.").wait_for()
        assert page.locator("#setupProblemCount").inner_text() == "문제 1개"
        assert field(page, "끝").input_value() == "00:04.0"
        assert "샘플 8개" in page.locator("#rangeCaption").inner_text()  # up to the last frame, 3.9 s
        assert not (data / "Inspections").exists()  # nothing is written before the analysis starts

        # "[" puts the time on screen into the range start; text that is not a time is not applied
        page.locator("#frame").focus()
        for _ in range(5):
            page.keyboard.press(".")
        page.wait_for_function("document.getElementById('time').textContent.startsWith('00:00.5')")
        page.wait_for_timeout(300)
        page.keyboard.press("[")
        assert field(page, "시작").input_value() == "00:00.5"
        band = page.locator("#scrubRange").evaluate("node => getComputedStyle(node).backgroundColor")
        assert band == "rgb(255, 224, 122)"  # --range-fill, apart from the blue played part
        field(page, "시작").fill("abc")
        page.get_by_text("시각을 mm:ss.s로 입력하세요.").wait_for()
        field(page, "시작").fill("0")
        field(page, "기동 시각").fill("1")  # seconds, shown as mm:ss.s once entered
        field(page, "기동 시각").press("Enter")
        assert field(page, "기동 시각").input_value() == "00:01.0"
        page.wait_for_function("document.getElementById('setupProblemCount').textContent === ''")

        # the inspection name: it names the folder; too long a name is a problem
        name = page.get_by_label("검사 이름")
        name.fill("가" * 61)
        page.get_by_text("검사 이름은 60자 이하여야 합니다.").wait_for()
        name.fill("스모크: 1차")
        page.wait_for_function("document.getElementById('setupProblemCount').textContent === ''")
        shot(page, "i3-name")

        # a Glass correction goes into this inspection's copy only, and can be undone
        page.locator("#frame").focus()
        page.keyboard.press("ArrowRight")
        row = page.locator("#setupGlassRows .glass-row", has_text="BASE")
        row.get_by_text("Recipe와 다름").wait_for()
        page.get_by_role("button", name="Recipe 위치로 되돌리기").click()
        assert row.get_by_text("Recipe와 다름").count() == 0
        page.locator("#frame").focus()
        page.keyboard.press("Shift+ArrowRight")
        assert field(page, "중심 X").input_value() == "170"
        shot(page, "i3-setup")

        page.get_by_role("button", name="분석 시작").click()
        page.locator("#editorView").wait_for()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        assert page.locator("#editorTitle").inner_text() == "스모크: 1차"
        assert page.locator("#graph path[data-kind=oil]").count() == 1
        assert page.locator("#editorGlass option").all_inner_texts() == ["BASE"]
        page.get_by_text("배경 제거 보기", exact=True).click()
        assert page.locator("#backgroundToggle").is_checked()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        shot(page, "i4-editor")

        folder = next((data / "Inspections").iterdir())
        assert folder.name == "스모크_ 1차"  # made safe for Windows
        copy = json.loads((folder / "recipe.json").read_text(encoding="utf-8"))
        assert copy["glasses"][0]["ellipse"]["center_x"] == 170.0
        stored = json.loads((data / "Recipes" / "스모크.recipe.json").read_text(encoding="utf-8"))
        assert stored["glasses"][0]["ellipse"]["center_x"] == 160.0
        inspection = json.loads((folder / "inspection.json").read_text(encoding="utf-8"))
        assert inspection["state"] == "ANALYSED"
        assert inspection["settings"] == {"start_sec": 0.0, "end_sec": 4.0, "compressor_start_sec": 1.0}

        page.get_by_role("button", name="검사 목록").click()
        listed = page.locator("#inspectionRows tr", has_text="level.avi")
        listed.wait_for()
        assert "분석 완료" in listed.inner_text() and folder.name in listed.inner_text()
        assert listed.inner_text().startswith("스모크: 1차")
        shot(page, "i5-list")
        listed.get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        assert errors == []
    finally:
        running.close()


def analysed_inspection(running, video, name):
    """An inspection of the smoke video, analysed through the API; the API call it used."""
    import http.client

    def call(method, path, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", running.server.server_address[1], timeout=30)
        headers = {"X-OLT-Token": running.token, "Content-Type": "application/json"}
        connection.request(method, path, None if body is None else json.dumps(body).encode(), headers)
        data = json.loads(connection.getresponse().read())
        connection.close()
        return data

    opened = call("POST", "/api/videos", {"path": str(video)})
    e = GLASS.ellipse
    setup = {
        "inspection_id": None, "video_id": opened["id"], "recipe_id": "r-fit", "name": name,
        "glasses": [{"id": GLASS.id, "zero_line_y": GLASS.zero_line_y, "ellipse": {
            "center_x": e.center_x, "center_y": e.center_y, "radius_x": e.radius_x, "radius_y": e.radius_y}}],
        "settings": {"start_sec": 0, "end_sec": 3.9, "compressor_start_sec": 1.0},
    }
    job = call("POST", "/api/inspections/start", setup)["job"]
    for _ in range(500):
        if call("GET", f"/api/jobs/{job['id']}")["state"] != "running":
            break
        time.sleep(0.02)
    return call


def oil_path(page):
    return page.locator("#graph path[data-kind=oil]").get_attribute("d")


def wait_for_oil(page, d):
    page.wait_for_function("d => document.querySelector('#graph path[data-kind=oil]').getAttribute('d') === d", arg=d)


def point_on_oil(page, share):
    x, y = page.evaluate(
        """share => { const p = document.querySelector('#graph path[data-kind=oil]');
        const at = p.getPointAtLength(p.getTotalLength() * share); return [at.x, at.y]; }""",
        share,
    )
    box = page.locator("#graph").bounding_box()
    return box["x"] + x, box["y"] + y


def drag(page, start, end, steps=8):
    page.mouse.move(*start)
    page.mouse.down()
    for k in range(1, steps + 1):
        page.mouse.move(start[0] + (end[0] - start[0]) * k / steps, start[1] + (end[1] - start[1]) * k / steps)
    page.mouse.up()


def wait_until(check):
    for _ in range(250):
        if check():
            return
        time.sleep(0.02)
    raise AssertionError("timed out")


def test_editing_saving_and_leaving(tmp_path, video, browser_page):
    page, errors = browser_page
    data = tmp_path / "data"
    write_recipes(data / "Recipes")
    closing = []  # what the window would be told: ask before closing or not
    source = tmp_path / "source.avi"
    shutil.copyfile(video, source)
    running = bootstrap.start(data_folder=data, ask_before_closing=closing.append)
    try:
        analysed_inspection(running, source, "편집")
        page.goto(running.url)
        row = page.locator("#inspectionRows tr", has_text="편집")
        row.get_by_text("분석 완료").wait_for()
        row.get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        assert page.locator("#editorState").inner_text().startswith("초안 그대로")

        # grab-and-drag moves the Oil line; undo puts it back, redo again
        before = oil_path(page)
        start = point_on_oil(page, 0.5)
        drag(page, start, (start[0], start[1] + 40))
        page.get_by_text("저장 안 함").wait_for()
        wait_until(lambda: closing == [True])
        moved = oil_path(page)
        assert moved != before
        shot(page, "e1-grab")
        page.keyboard.press("Control+z")
        wait_for_oil(page, before)  # lines redraw on the next frame
        page.keyboard.press("Control+Shift+z")
        wait_for_oil(page, moved)

        # the range tool: Delete empties the Oil line there, which counts as an empty stretch.
        # A switch just clicked keeps the shortcut keys working.
        page.get_by_text("배경 제거 보기", exact=True).click()
        page.keyboard.press("r")
        assert page.locator("#editorView button[data-tool=range]").get_attribute("aria-pressed") == "true"
        box = page.locator("#graph").bounding_box()
        drag(page, (box["x"] + box["width"] * 0.3, box["y"] + 60), (box["x"] + box["width"] * 0.55, box["y"] + 60))
        assert page.locator("#selectionText").inner_text() != "없음"
        page.keyboard.press("Delete")
        page.locator("#glassFacts").get_by_text("1곳").wait_for()
        page.locator("#axis rect").wait_for()  # the empty stretch's bar on the time axis, next frame
        assert page.locator("#axis rect").count() == 1
        shot(page, "e2-erased")

        # U marks the range "cannot judge": hatched, and no longer an empty stretch. Undo takes it
        # back, redo again; "판단 불가 풀기" clears it, and U marks it once more for the save below.
        hatch = page.locator("#graph rect[style*=hatch]")
        assert page.locator("#clearSelection").is_disabled()
        page.keyboard.press("u")
        hatch.wait_for()
        page.locator("#glassFacts").get_by_text("빈 구간").locator("..").get_by_text("없음").wait_for()
        page.locator("#axis rect").wait_for(state="detached")  # the axis redraws on the next frame
        shot(page, "e2-cannot-judge")
        page.keyboard.press("Control+z")
        hatch.wait_for(state="detached")
        page.keyboard.press("Control+Shift+z")
        hatch.wait_for()
        page.locator("#clearSelection").click()
        hatch.wait_for(state="detached")
        page.locator("#axis rect").wait_for()
        page.keyboard.press("u")
        hatch.wait_for()
        joined, split = page.evaluate("""async () => {
            const l = await import("/web/lines.js");
            const s = (a, b) => ({ start_sec: a, end_sec: b });
            return [l.markStretch([s(0, 1), s(2, 3), s(5, 6)], 1, 2.5), l.clearStretch([s(0, 3), s(5, 6)], 1, 2)];
        }""")
        assert joined == [{"start_sec": 0, "end_sec": 3}, {"start_sec": 5, "end_sec": 6}]  # touching ones join
        assert split == [{"start_sec": 0, "end_sec": 1}, {"start_sec": 2, "end_sec": 3}, {"start_sec": 5, "end_sec": 6}]

        # the video: this AVI cannot play in a <video>, so it plays as exact frames
        before_time = page.locator("#videoTime").inner_text()
        page.keyboard.press("Space")
        page.wait_for_timeout(800)
        page.keyboard.press("Space")
        page.wait_for_function(f"document.getElementById('videoTime').textContent !== {json.dumps(before_time)}")
        page.wait_for_function("!document.getElementById('videoFrame').hidden")

        page.keyboard.press("Control+s")
        page.get_by_text("저장함").wait_for()
        wait_until(lambda: closing == [True, False])
        folder = data / "Inspections" / "편집"
        saved = json.loads((folder / "edits.json").read_text(encoding="utf-8"))
        assert None in saved["glasses"][0]["oil"]["ys"] and "EDITED" in saved["glasses"][0]["oil"]["origins"]
        assert len(saved["glasses"][0]["cannot_judge"]) == 1

        # leaving with unsaved changes asks first
        page.keyboard.press("p")
        drag(page, (box["x"] + box["width"] * 0.3, box["y"] + 100), (box["x"] + box["width"] * 0.5, box["y"] + 120))
        page.get_by_text("저장 안 함").wait_for()
        asked = []
        page.once("dialog", lambda dialog: (asked.append(dialog.message), dialog.dismiss()))
        page.get_by_role("button", name="검사 목록").click()
        assert asked and page.locator("#editorView").is_visible()
        page.once("dialog", lambda dialog: dialog.accept())
        page.get_by_role("button", name="검사 목록").click()
        page.locator("#inspectionsView").wait_for()
        wait_until(lambda: closing == [True, False, True, False])
        assert page.locator("#sourceWarning").is_hidden()

        # reopening warns when the source video changed (A9); "다시 확인" clears it once it is back
        original = source.read_bytes()
        source.write_bytes(original + b"\0")
        row.get_by_role("button", name="열기", exact=True).click()
        page.locator("#sourceWarning").get_by_text("원본 영상이 분석할 때와 다릅니다").wait_for()
        shot(page, "e3-source-warning")
        source.write_bytes(original)
        page.locator("#sourceWarning").get_by_role("button", name="다시 확인").click()
        page.locator("#sourceWarning").wait_for(state="hidden")
        assert errors == []
    finally:
        running.close()


def test_reanalysis_from_the_editor(tmp_path, video, browser_page):
    page, errors = browser_page
    data = tmp_path / "data"
    write_recipes(data / "Recipes")
    running = bootstrap.start(data_folder=data)
    try:
        analysed_inspection(running, video, "다시")
        page.goto(running.url)
        row = page.locator("#inspectionRows tr", has_text="다시")
        row.get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")

        # an unsaved pencil stroke near the end; going to the setup saves it first
        page.keyboard.press("p")
        box = page.locator("#graph").bounding_box()
        drag(page, (box["x"] + box["width"] * 0.8, box["y"] + 100), (box["x"] + box["width"] * 0.95, box["y"] + 110))
        page.get_by_text("저장 안 함").wait_for()
        asked = []
        page.once("dialog", lambda dialog: (asked.append(dialog.message), dialog.accept()))
        page.get_by_role("button", name="범위 바꿔 다시 분석…").click()
        page.locator("#setupView").wait_for()
        assert "저장" in asked[0]
        assert (data / "Inspections" / "다시" / "edits.json").exists()
        assert page.locator("#setupBack").inner_text() == "편집기"
        assert page.locator("#startAnalysis").inner_text() == "다시 분석"

        # "← 편집기" goes back without analysing
        page.locator("#setupBack").click()
        page.get_by_text("저장함").wait_for()
        page.get_by_role("button", name="범위 바꿔 다시 분석…").click()
        page.locator("#setupView").wait_for()

        # a shorter range drops the stroke; the setup says so, and asks before it starts
        end = field(page, "끝")
        end.fill("00:02.0")
        end.press("Enter")
        dropped = page.locator("#droppedCaption")
        dropped.get_by_text("Oil 샘플").wait_for()
        shot(page, "r1-reanalysis-setup")
        asked.clear()
        page.once("dialog", lambda dialog: (asked.append(dialog.message), dialog.accept()))
        page.get_by_role("button", name="다시 분석").click()
        page.locator("#editorView").wait_for()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        assert "Oil 샘플" in asked[0]
        assert "00:00.0 – 00:02.0" in page.locator("#editorFacts").inner_text()
        assert "5개" in page.locator("#editorFacts").inner_text()  # 0 to 2 s, two a second
        saved = json.loads((data / "Inspections" / "다시" / "edits.json").read_text(encoding="utf-8"))
        assert len(saved["times"]) == 5
        assert errors == []
    finally:
        running.close()


def test_the_compressor_marker_moves(tmp_path, video, browser_page):
    page, errors = browser_page
    data = tmp_path / "data"
    write_recipes(data / "Recipes")
    running = bootstrap.start(data_folder=data)
    try:
        analysed_inspection(running, video, "기동")  # the compressor start at 1.0 s
        page.goto(running.url)
        page.locator("#inspectionRows tr", has_text="기동").get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        facts = page.locator("#editorFacts tr", has_text="압축기 기동")
        assert facts.locator("td").inner_text() == "00:01.0"

        # the grab tool drags the marker where no line is under the pointer
        box = page.locator("#graph").bounding_box()
        x = box["x"] + float(page.locator("#graph line[style*=compressor]").get_attribute("x1"))
        y = box["y"] + 30
        page.mouse.move(x + 2, y)
        assert page.evaluate("document.getElementById('graph').style.cursor") == "ew-resize"
        page.mouse.down()
        page.mouse.move(x + box["width"] * 0.12, y)
        page.mouse.move(x + box["width"] * 0.25, y)
        # while dragged, the marker is drawn with the marks; the back layer is not redrawn per move
        page.wait_for_function("""() => {
            const [back, , marks] = document.getElementById('graph').children;
            return !back.querySelector('line[style*=compressor]') && marks.querySelector('line[style*=compressor]');
        }""")
        shot(page, "c1-compressor-drag")
        page.mouse.up()
        facts.get_by_text("(설정 00:01.0에서 옮김)").wait_for()
        page.wait_for_function(  # back in the back layer on the next frame
            "document.getElementById('graph').children[0].querySelector('line[style*=compressor]')")
        moved = facts.locator("td").inner_text()
        page.get_by_text("저장 안 함").wait_for()
        page.keyboard.press("Control+z")
        facts.get_by_text("00:01.0", exact=True).wait_for()
        page.keyboard.press("Control+Shift+z")
        facts.get_by_text("(설정 00:01.0에서 옮김)").wait_for()
        page.keyboard.press("Control+s")
        page.get_by_text("저장함").wait_for()
        saved = json.loads((data / "Inspections" / "기동" / "edits.json").read_text(encoding="utf-8"))
        time_sec = saved["compressor_start_sec"]
        assert 1.5 < time_sec < 3.9 and round(time_sec * 10) == time_sec * 10  # 0.1 s steps
        assert moved.startswith(f"00:0{time_sec:.1f}")

        # a re-analysis starts from the moved time
        page.get_by_role("button", name="범위 바꿔 다시 분석…").click()
        page.locator("#setupView").wait_for()
        assert field(page, "기동 시각").input_value() == f"00:0{time_sec:.1f}"
        assert errors == []
    finally:
        running.close()
