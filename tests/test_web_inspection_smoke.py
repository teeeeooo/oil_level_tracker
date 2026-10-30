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
        field(page, "압축기 모델").fill(" GB-2 R410A ")  # the report header goes with the start
        assert field(page, "시험 종류").get_attribute("maxlength") == "60"
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
        assert page.locator("#editorGlass option").all_inner_texts() == ["BASE · 확인 전"]
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
        assert inspection["report_header"] == {"compressor_model": "GB-2 R410A", "test_type": None}

        # the editor's 검사 정보 saves at once, apart from the edits; leaving sends what was typed
        header = page.locator("#editorHeader")
        assert header.get_by_label("압축기 모델").input_value() == "GB-2 R410A"
        header.get_by_label("시험 종류").fill("냉각 on/off")
        page.get_by_role("button", name="검사 목록").click()
        listed = page.locator("#inspectionRows tr", has_text="level.avi")
        listed.wait_for()
        inspection = json.loads((folder / "inspection.json").read_text(encoding="utf-8"))
        assert inspection["report_header"] == {"compressor_model": "GB-2 R410A", "test_type": "냉각 on/off"}
        assert not (folder / "edits.json").exists()
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
        assert row.locator(".sub.mono").count() == 0  # the folder is named as the inspection: not repeated
        row.get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        assert page.locator("#editorState").inner_text().startswith("초안 그대로")

        # the view keeps to the analysed range: panned past the start and narrowed by the end number,
        # the axis shows no time before the start. "전체 보기" brings the whole range back.
        whole = page.locator("#axisTo").input_value()
        box = page.locator("#graph").bounding_box()
        page.keyboard.down("Shift")
        drag(page, (box["x"] + box["width"] * 0.3, box["y"] + 60), (box["x"] + box["width"] * 0.8, box["y"] + 60))
        page.keyboard.up("Shift")
        page.locator("#axisTo").fill("2")
        page.locator("#axisTo").press("Enter")
        page.wait_for_function("document.getElementById('axisTo').value === '00:02.0'")
        labels = page.evaluate("[...document.querySelectorAll('#axis text')].map((t) => t.textContent)")
        assert labels and not any("-" in label for label in labels)
        page.get_by_role("button", name="전체 보기").click()
        page.wait_for_function("v => document.getElementById('axisTo').value === v", arg=whole)

        # grab-and-drag moves the Oil line; undo puts it back, redo again
        before = oil_path(page)
        start = point_on_oil(page, 0.5)
        drag(page, start, (start[0], start[1] + 40))
        page.get_by_text("저장 안 함").wait_for()
        wait_until(lambda: closing == [False, True])  # the page first says it holds nothing
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
        selbox, clear = page.locator("#selectionBox").bounding_box(), page.locator("#clearSelection").bounding_box()
        assert clear["x"] + clear["width"] <= selbox["x"] + selbox["width"]  # wrapped, not out of the panel
        page.locator("#lineKind button[data-kind=foam]").click()
        assert page.locator("#eraseKind").inner_text() == "Foam"  # "Foam 선 지우기"
        page.keyboard.press("Delete")  # empties the Foam line, not the Oil line
        page.locator("#lineKind button[data-kind=oil]").click()
        page.keyboard.press("g")
        page.locator("#selectionBox").wait_for(state="hidden")
        assert page.locator("#selectionText").inner_text() == "없음"
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
        wait_until(lambda: closing == [False, True, False])
        folder = data / "Inspections" / "편집"
        saved = json.loads((folder / "edits.json").read_text(encoding="utf-8"))
        assert None in saved["glasses"][0]["oil"]["ys"] and "EDITED" in saved["glasses"][0]["oil"]["origins"]
        assert len(saved["glasses"][0]["cannot_judge"]) == 1
        foam = saved["glasses"][0]["foam"]
        assert "EDITED" in foam["origins"] and all(foam["ys"][k] is None for k, o in enumerate(foam["origins"]) if o == "EDITED")

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
        wait_until(lambda: closing == [False, True, False, True, False])
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
        page.locator("#editorHeader").get_by_label("시험 종류").fill("편집기에서")  # sent before the setup reads it
        asked = []
        page.once("dialog", lambda dialog: (asked.append(dialog.message), dialog.accept()))
        page.get_by_role("button", name="범위 바꿔 다시 분석…").click()
        page.locator("#setupView").wait_for()
        assert "저장" in asked[0]
        assert field(page, "시험 종류").input_value() == "편집기에서"
        assert (data / "Inspections" / "다시" / "edits.json").exists()
        assert page.locator("#setupBack").inner_text() == "편집기"
        assert page.locator("#startAnalysis").inner_text() == "다시 분석"

        # once the folder exists the setup saves the report header at once; "← 편집기" goes back
        # without analysing, and the header is there
        field(page, "시험 종류").fill("재분석")
        page.locator("#setupBack").click()
        page.get_by_text("저장함").wait_for()
        assert page.locator("#editorHeader").get_by_label("시험 종류").input_value() == "재분석"
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
        stored = json.loads((data / "Inspections" / "다시" / "inspection.json").read_text(encoding="utf-8"))
        assert stored["report_header"]["test_type"] == "재분석"  # the re-analysis keeps it
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


def test_memos(tmp_path, video, browser_page):
    page, errors = browser_page
    data = tmp_path / "data"
    write_recipes(data / "Recipes")
    running = bootstrap.start(data_folder=data)
    try:
        analysed_inspection(running, video, "메모")
        page.goto(running.url)
        page.locator("#inspectionRows tr", has_text="메모").get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        page.keyboard.press("m")
        assert page.locator("#editorView button[data-tool=memo]").get_attribute("aria-pressed") == "true"
        box = page.locator("#graph").bounding_box()
        dialog = page.locator("#memoDialog")
        items = page.locator("#memoItems button.memo")

        # a click on the graph opens a new memo; "확인" waits for some text
        page.mouse.click(box["x"] + box["width"] * 0.6, box["y"] + 120)
        assert dialog.locator("#memoTitle").inner_text().startswith("새 메모 · ")
        assert dialog.get_by_role("button", name="확인").is_disabled()
        page.keyboard.type("거품 발생")
        dialog.get_by_role("button", name="확인").click()
        page.locator('#graph [data-memo="1"]').wait_for()
        page.get_by_text("저장 안 함").wait_for()

        # an earlier memo takes number 1 (Ctrl+Enter confirms); Esc adds nothing
        page.mouse.click(box["x"] + box["width"] * 0.3, box["y"] + 150)
        page.keyboard.type("FULL 도달 확인")
        page.keyboard.press("Control+Enter")
        page.locator('#graph [data-memo="2"]').wait_for()
        assert items.all_inner_texts()[0].endswith("FULL 도달 확인")
        page.mouse.click(box["x"] + box["width"] * 0.8, box["y"] + 150)
        page.keyboard.type("버림")
        page.keyboard.press("Escape")
        assert items.count() == 2

        # a click on pin 2 opens it; the change can be undone and redone
        pin = page.locator('#graph [data-memo="2"] circle')
        x = box["x"] + float(pin.get_attribute("cx"))
        y = box["y"] + float(pin.get_attribute("cy"))
        page.mouse.click(x, y)
        assert dialog.locator("#memoTitle").inner_text().startswith("메모 2 · ")
        assert dialog.locator("#memoText").input_value() == "거품 발생"
        dialog.locator("#memoText").fill("거품 발생, 유면 식별 어려움")
        dialog.get_by_role("button", name="확인").click()
        items.nth(1).get_by_text("유면 식별 어려움").wait_for()
        page.locator("#memoItems").scroll_into_view_if_needed()
        shot(page, "m1-memos")
        page.keyboard.press("Control+z")
        items.nth(1).get_by_text("거품 발생", exact=True).wait_for()
        page.keyboard.press("Control+Shift+z")
        items.nth(1).get_by_text("유면 식별 어려움").wait_for()

        # the list opens a memo too; "삭제" removes it
        items.first.click()
        assert dialog.locator("#memoTitle").inner_text().startswith("메모 1 · ")
        dialog.get_by_role("button", name="삭제").click()
        page.locator('#graph [data-memo="2"]').wait_for(state="detached")
        assert items.all_inner_texts()[0].endswith("거품 발생, 유면 식별 어려움")

        page.keyboard.press("Control+s")
        page.get_by_text("저장함").wait_for()
        saved = json.loads((data / "Inspections" / "메모" / "edits.json").read_text(encoding="utf-8"))
        (memo,) = saved["glasses"][0]["memos"]
        assert memo["text"] == "거품 발생, 유면 식별 어려움" and memo["y"] is not None
        assert round(memo["time_sec"] * 10) == memo["time_sec"] * 10

        # a change made while a save is on its way is not in it, so it stays unsaved
        held = []
        page.route("**/api/inspections/*/edits",
                   lambda route: held.append(route) if route.request.method == "POST" else route.continue_())
        page.keyboard.press("Control+s")
        for _ in range(250):
            if held:
                break
            page.wait_for_timeout(20)
        page.mouse.click(box["x"] + box["width"] * 0.5, box["y"] + 150)
        page.keyboard.type("저장 중에 남긴 메모")
        page.keyboard.press("Control+Enter")
        page.evaluate("document.getElementById('editorNotice').textContent = ''")  # the last save's notice
        held[0].continue_()
        page.get_by_text("저장했습니다.").wait_for()  # this save's response handled
        assert page.locator("#editorState").inner_text().startswith("저장 안 함")
        assert errors == []
    finally:
        running.close()


def point_in(page, plot, share, rise):
    """Page coordinates `rise` px above the Oil line at `share` of its length, in plot `plot`."""
    x, y = page.evaluate(
        """([plot, share]) => { const p = document.querySelector(`#${plot} path[data-kind=oil]`);
        const at = p.getPointAtLength(p.getTotalLength() * share); return [at.x, at.y]; }""",
        [plot, share],
    )
    box = page.locator(f"#{plot}").bounding_box()
    return box["x"] + x, box["y"] + y - rise


def test_the_point_line(tmp_path, video, browser_page):
    page, errors = browser_page
    data = tmp_path / "data"
    write_recipes(data / "Recipes")
    running = bootstrap.start(data_folder=data)
    try:
        analysed_inspection(running, video, "점 잇기")
        page.goto(running.url)
        page.locator("#inspectionRows tr", has_text="점 잇기").get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        before = oil_path(page)
        points = page.locator("#graph circle[data-point]")
        text = page.locator("#pointText")
        asked = []
        page.on("request", lambda request: asked.append(request.url) if request.url.endswith("/point-line") else None)

        page.keyboard.press("s")  # the snap off: the points stay where they are clicked, joined straight
        page.keyboard.press("l")
        assert page.locator("#editorView button[data-tool=point]").get_attribute("aria-pressed") == "true"
        assert page.locator("#pointBox").is_visible() and text.inner_text() == "점 0개 · Oil"

        # a point on the context image, then the pointer over the graph: the preview joins them
        page.mouse.click(*point_in(page, "context", 0.15, 12))
        assert text.inner_text() == "점 1개 · Oil"
        page.mouse.move(*point_in(page, "graph", 0.6, 20))
        page.wait_for_function("document.querySelector('#graph path[style*=\"2 3\"]')")  # the preview, dotted
        # a point on the graph: the path between the two, dashed on both plots, straight
        page.mouse.click(*point_in(page, "graph", 0.85, 20))
        assert text.inner_text() == "점 2개 · Oil"
        page.wait_for_function("document.querySelector('#context path[style*=\"5 3\"]')")
        assert points.count() == 2 and page.locator("#context circle[data-point]").count() == 2
        assert asked == []  # the snap is off: no edges to follow
        shot(page, "p1-point-line")
        # the snap on joins the same points along the edges, from the API; off again, straight
        page.keyboard.press("s")
        wait_until(lambda: len(asked) >= 1)
        page.wait_for_function("document.querySelector('#context path[style*=\"5 3\"]')")
        page.keyboard.press("s")

        # Backspace takes the last point off; a click puts it back. The line is untouched so far.
        page.keyboard.press("Backspace")
        assert text.inner_text() == "점 1개 · Oil"
        page.mouse.click(*point_in(page, "graph", 0.85, 20))
        assert oil_path(page) == before and page.locator("#editorState").inner_text().startswith("초안 그대로")

        # Enter: the path becomes the Oil line from the first point to the last, as one change
        page.mouse.move(*point_in(page, "graph", 0.5, 0))
        page.keyboard.press("Enter")
        page.get_by_text("저장 안 함").wait_for()
        page.wait_for_function("d => document.querySelector('#graph path[data-kind=oil]').getAttribute('d') !== d", arg=before)
        drawn = oil_path(page)
        assert points.count() == 0 and text.inner_text() == "점 0개 · Oil"
        page.keyboard.press("Control+z")
        wait_for_oil(page, before)
        page.keyboard.press("Control+Shift+z")
        wait_for_oil(page, drawn)
        page.keyboard.press("Control+s")
        page.get_by_text("저장함").wait_for()
        oil = json.loads((data / "Inspections" / "점 잇기" / "edits.json").read_text(encoding="utf-8"))["glasses"][0]["oil"]
        drawn_at = [k for k, origin in enumerate(oil["origins"]) if origin == "DRAWN"]
        assert len(drawn_at) >= 2 and drawn_at == list(range(drawn_at[0], drawn_at[-1] + 1))  # one stretch
        ys = [oil["ys"][k] for k in drawn_at]  # straight: the samples are evenly spaced in time
        assert all(abs(ys[k + 1] - 2 * ys[k] + ys[k - 1]) < 1e-6 for k in range(1, len(ys) - 1))

        # Esc cancels points not yet joined; changing the tool does too
        page.mouse.click(*point_in(page, "graph", 0.3, 10))
        page.wait_for_function("document.querySelectorAll('#graph circle[data-point]').length === 1")  # next frame
        page.keyboard.press("Escape")
        page.wait_for_function("document.querySelectorAll('#graph circle[data-point]').length === 0")
        page.mouse.click(*point_in(page, "graph", 0.3, 10))
        page.keyboard.press("g")
        page.wait_for_function("document.querySelectorAll('#graph circle[data-point]').length === 0")
        assert page.locator("#pointBox").is_hidden()
        assert oil_path(page) == drawn
        assert errors == []
    finally:
        running.close()


def test_the_pencil_lock(tmp_path, video, browser_page):
    # "수평·수직" (user, 2026-10-30): a stroke mostly across draws level at the pressed height;
    # mostly up or down, it joins the pressed height to the pointer's between two neighbouring samples
    page, errors = browser_page
    data = tmp_path / "data"
    write_recipes(data / "Recipes")
    running = bootstrap.start(data_folder=data)
    try:
        analysed_inspection(running, video, "직선")
        page.goto(running.url)
        page.locator("#inspectionRows tr", has_text="직선").get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        page.keyboard.press("s")  # the snap off: the pressed height stays
        page.get_by_text("수평·수직", exact=True).click()
        page.keyboard.press("p")
        box = page.locator("#graph").bounding_box()
        left, top = box["x"] + box["width"] * 0.2, box["y"] + box["height"] * 0.4

        def drawn():
            page.keyboard.press("Control+s")
            page.get_by_text("저장함").wait_for()
            oil = json.loads((data / "Inspections" / "직선" / "edits.json").read_text(encoding="utf-8"))["glasses"][0]["oil"]
            return [y for y, origin in zip(oil["ys"], oil["origins"]) if origin == "DRAWN"]

        drag(page, (left, top), (left + box["width"] * 0.5, top + 40))  # across, wandering down
        level = drawn()
        assert len(level) > 3 and len(set(level)) == 1
        page.keyboard.press("Control+z")
        drag(page, (left, top), (left + 12, top + 60))  # up or down, a little slanted
        upright = drawn()
        assert len(upright) == 2 and upright[0] == level[0]  # from the pressed height
        assert upright[1] > upright[0]  # to the pointer's, lower on the screen: a larger source y
        assert errors == []
    finally:
        running.close()


def test_the_judgment_the_users_verdict_and_the_check(tmp_path, video, browser_page):
    # Product SSOT §3 and §5; DESIGN.md §5 (the judgment panel)
    page, errors = browser_page
    data = tmp_path / "data"
    write_recipes(data / "Recipes")
    running = bootstrap.start(data_folder=data)
    try:
        analysed_inspection(running, video, "판정")
        page.goto(running.url)
        page.locator("#inspectionRows tr", has_text="판정").get_by_role("button", name="열기", exact=True).click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        badge, picker = page.locator("#verdictBadge"), page.locator("#editorGlass option")
        page.wait_for_function("document.getElementById('verdictBadge').textContent !== ''")
        computed = badge.inner_text()
        assert computed in ("합격", "불합격", "검토 필요")
        assert page.locator("#verdictNote").inner_text() == "자동 판정"
        assert page.locator("#judgmentReason").inner_text() != ""
        assert page.locator("#editorSubmit").is_disabled()
        assert "남은 Glass: BASE" in page.locator("#editorSubmit").get_attribute("title")

        # the user's own verdict needs a reason before the check
        own = "합격" if computed != "합격" else "불합격"
        page.locator(f"#overrideKind button[data-override={'PASS' if own == '합격' else 'FAIL'}]").click()
        page.locator("#reasonBox").wait_for()
        page.wait_for_function("t => document.getElementById('verdictBadge').textContent === t", arg=own)
        assert page.locator("#verdictNote").inner_text() == f"직접 판정 · 자동 판정은 {computed}"
        page.get_by_role("button", name="이 Glass 확인").click()
        page.get_by_text("직접 판정한 Glass는 이유를 써야 확인할 수 있습니다.").wait_for()
        assert page.locator("#checkedRow").is_hidden()
        page.locator("#overrideReason").fill("거품 아래 유면을 영상으로 확인함")
        page.get_by_role("button", name="이 Glass 확인").click()
        page.locator("#checkedRow").wait_for()
        assert picker.all_inner_texts() == [f"BASE · {own}"]
        assert "제출은 다음 단계" in page.locator("#editorSubmit").get_attribute("title")

        # a Foam stroke keeps the check; an Oil change takes it off, and its undo too
        page.keyboard.press("p")
        page.locator("#lineKind button[data-kind=foam]").click()
        box = page.locator("#graph").bounding_box()
        drag(page, (box["x"] + box["width"] * 0.3, box["y"] + 40), (box["x"] + box["width"] * 0.4, box["y"] + 40))
        page.get_by_text("저장 안 함").wait_for()
        assert page.locator("#checkedRow").is_visible()
        page.locator("#lineKind button[data-kind=oil]").click()
        drag(page, (box["x"] + box["width"] * 0.6, box["y"] + 60), (box["x"] + box["width"] * 0.7, box["y"] + 60))
        page.locator("#checkRow").wait_for()
        assert picker.all_inner_texts() == ["BASE · 확인 전"]
        page.get_by_role("button", name="이 Glass 확인").click()
        page.keyboard.press("Control+z")
        page.locator("#checkRow").wait_for()

        # saved with the edits; the verdict and the reason come back, the check as it was
        page.get_by_role("button", name="이 Glass 확인").click()
        page.keyboard.press("Control+s")
        page.get_by_text("저장함").wait_for()
        decision = json.loads((data / "Inspections" / "판정" / "edits.json").read_text(encoding="utf-8"))["glasses"][0]["decision"]
        assert decision["override"] == {"합격": "PASS", "불합격": "FAIL"}[own]
        assert decision["reason"] == "거품 아래 유면을 영상으로 확인함" and decision["checked_at"]
        page.reload()
        page.locator("#inspectionRows tr", has_text="판정").get_by_role("button", name="열기", exact=True).click()
        page.locator("#checkedRow").wait_for()
        assert page.locator("#overrideReason").input_value() == "거품 아래 유면을 영상으로 확인함"
        page.locator("#overrideKind button[data-override='']").click()  # back to the computed verdict
        page.wait_for_function("t => document.getElementById('verdictBadge').textContent === t", arg=computed)
        assert page.locator("#reasonBox").is_hidden() and page.locator("#checkRow").is_visible()
        shot(page, "j1-judgment")
        page.locator("#editorHeader").scroll_into_view_if_needed()
        shot(page, "j2-inspection-info")
        assert errors == []
    finally:
        running.close()
