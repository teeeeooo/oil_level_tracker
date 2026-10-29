"""Browser smoke check of the inspection screens on macOS Chrome (no Windows claim).

Skipped when Playwright or Chrome is missing. Set OLT_SMOKE_SHOTS to a folder to keep
screenshots.
"""

import json
import os
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
        page.locator("#resultView").wait_for()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        assert page.locator("#resultTitle").inner_text() == "level.avi"
        assert page.locator("#graph path").count() >= 1
        assert page.locator("#resultGlass option").all_inner_texts() == ["BASE"]
        page.locator("#resultView .toggle").click()
        assert page.locator("#backgroundToggle").is_checked()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        shot(page, "i4-result")

        folder = next((data / "Inspections").iterdir())
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
        shot(page, "i5-list")
        listed.get_by_role("button", name="열기").click()
        page.wait_for_function("document.querySelectorAll('#context image').length === 1")
        assert errors == []
    finally:
        running.close()
