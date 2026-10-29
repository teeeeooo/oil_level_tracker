"""Browser smoke check of the Recipe screens on macOS Chrome (no Windows claim).

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

playwright_api = pytest.importorskip("playwright.sync_api")

W, H, FPS = 320, 240, 10.0


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    path = tmp_path_factory.mktemp("video") / "smoke.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (W, H))
    for index in range(30):
        frame = np.full((H, W, 3), 40 + 5 * index, np.uint8)
        cv2.ellipse(frame, (160, 120), (38, 65), 0, 0, 360, (200, 210, 200), -1)
        writer.write(frame)
    writer.release()
    return path


@pytest.fixture
def browser_page():
    with playwright_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception as error:  # noqa: BLE001
            pytest.skip(f"Chrome is not available: {error}")
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        errors: list[str] = []
        # Chrome also logs every non-2xx response; the 501 (no window) and 422 (refused save) are expected
        page.on("console", lambda message: errors.append(message.text)
                if message.type == "error" and not message.text.startswith("Failed to load resource") else None)
        page.on("pageerror", lambda error: errors.append(str(error)))
        yield page, errors
        browser.close()


def shot(page, name):
    folder = os.environ.get("OLT_SMOKE_SHOTS")
    if folder:
        page.screenshot(path=str(Path(folder) / f"{name}.png"))


def frame_point(page, x, y):
    """Page coordinates of a source-frame point, at zoom 1 (as recipe.js layout())."""
    box = page.locator("#frameBox").bounding_box()
    s = min(box["width"] / W, box["height"] / H)
    ox = box["x"] + (box["width"] - W * s) / 2
    oy = box["y"] + (box["height"] - H * s) / 2
    return ox + x * s, oy + y * s


def drag(page, start, end):
    page.mouse.move(*start)
    page.mouse.down()
    page.mouse.move((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    page.mouse.move(*end)
    page.mouse.up()


def field(page, label):
    return page.locator(".field", has=page.locator(".label", has_text=label)).locator("input")


def open_recipe_list(page, running):
    """The app opens on the inspection list; the Recipe list is one click away."""
    page.goto(running.url)
    page.get_by_text("검사가 없습니다").wait_for()
    page.get_by_role("button", name="Recipe", exact=True).click()
    page.get_by_text("Recipe가 없습니다").wait_for()


def test_create_edit_save_and_reopen_a_recipe(tmp_path, video, browser_page):
    page, errors = browser_page
    running = bootstrap.start(data_folder=tmp_path / "data")
    try:
        page.on("dialog", lambda dialog: dialog.accept(str(video)))  # no window: the path prompt
        open_recipe_list(page, running)
        shot(page, "1-empty-list")

        page.get_by_role("button", name="새 Recipe").click()
        page.locator("#editView").wait_for()
        page.wait_for_function("document.getElementById('time').textContent.startsWith('00:00.0')")
        assert "smoke.avi" in page.locator("#frameSource").inner_text()

        page.get_by_role("button", name="+ 추가").click()
        assert page.locator(".glass-row b").inner_text() == "Glass 1"
        assert field(page, "0선 Y").input_value() == "132"  # v1 default_glass: 0.55 * H
        page.locator("#recipeName").fill("스모크 Recipe")

        # the zero line is dragged by the line itself (v1)
        drag(page, frame_point(page, 160, 132), frame_point(page, 160, 150))
        assert field(page, "0선 Y").input_value() == "150"
        # a drag stops at the ellipse bottom (120 + 65)
        drag(page, frame_point(page, 160, 150), frame_point(page, 160, 230))
        assert field(page, "0선 Y").input_value() == "185"
        field(page, "0선 Y").fill("150")  # at the very bottom the chord is a point under the handle
        # dragging inside the ellipse moves the Glass with its zero line
        drag(page, frame_point(page, 160, 90), frame_point(page, 180, 90))
        assert field(page, "중심 X").input_value() == "180"
        assert field(page, "0선 Y").input_value() == "150"
        # a corner handle resizes; arrow keys nudge 1 px
        drag(page, frame_point(page, 180 + 38, 120 + 65), frame_point(page, 180 + 48, 120 + 75))
        assert (field(page, "반지름 X").input_value(), field(page, "반지름 Y").input_value()) == ("43", "70")
        page.locator("#frame").focus()
        page.keyboard.press("ArrowRight")
        assert field(page, "중심 X").input_value() == "186"

        # text that is not a number is not applied and blocks saving
        field(page, "반지름 X").fill("abc")
        page.get_by_text("숫자를 입력하세요.").wait_for()
        assert page.locator("#problemCount").inner_text() == "문제 1개"
        field(page, "반지름 X").fill("43")

        # the mode shows its own fields; Python checks the values
        page.get_by_label("판정 방식").select_option("HOLD_ABOVE_ZERO")
        assert field(page, "허용 시간").input_value() == "5"
        field(page, "허용 시간").fill("-1")
        page.locator("#selBody .err", has_text="허용 시간: 0 이상이어야 합니다.").wait_for()
        assert page.locator(".glass-row .err").inner_text() == "허용 시간: 0 이상이어야 합니다."
        shot(page, "2-edit-with-problem")
        page.get_by_role("button", name="저장").click()
        page.get_by_text("문제를 고친 뒤 저장하세요.").wait_for()
        assert not (tmp_path / "data" / "Recipes").exists()
        field(page, "허용 시간").fill("3")
        page.wait_for_function("document.getElementById('problemCount').textContent === ''")

        # the frame on screen at save becomes the reference
        page.get_by_title("다음 프레임 (.)").click()
        page.get_by_title("다음 프레임 (.)").click()
        page.wait_for_function("document.getElementById('time').textContent.startsWith('00:00.2')")
        page.wait_for_timeout(300)  # let the frame arrive
        page.get_by_role("button", name="저장").click()
        page.get_by_text("저장했습니다.").wait_for()
        shot(page, "3-saved")

        saved = json.loads((tmp_path / "data" / "Recipes" / "스모크 Recipe.recipe.json").read_text(encoding="utf-8"))
        glass = saved["glasses"][0]
        assert glass["ellipse"] == {"center_x": 186.0, "center_y": 125.0, "radius_x": 43.0, "radius_y": 70.0}
        assert glass["zero_line_y"] == 150.0
        assert glass["judgment_rule"]["mode"] == "HOLD_ABOVE_ZERO"
        assert glass["judgment_rule"]["allowed_sec"] == 3.0
        assert saved["reference_frame"]["time_sec"] == pytest.approx(0.2)
        assert saved["reference_frame"]["source_name"] == "smoke.avi"

        page.get_by_role("button", name="목록").click()
        row = page.locator("#recipeRows tr", has_text="스모크 Recipe")
        row.wait_for()
        assert "Glass 1" in row.inner_text() and "320 × 240" in row.inner_text()
        shot(page, "4-list")

        row.get_by_role("button", name="열기").click()
        page.locator("#editView").wait_for()
        page.wait_for_function("document.getElementById('frameSource').textContent.includes('저장된 기준 프레임')")
        assert "00:00.2" in page.locator("#frameSource").inner_text()
        assert page.locator("#play").is_disabled()
        page.wait_for_timeout(300)
        shot(page, "5-reopened")
        assert errors == []
    finally:
        running.close()


def test_speed_field_and_help(tmp_path, video, browser_page):
    page, errors = browser_page
    running = bootstrap.start(data_folder=tmp_path / "data")
    try:
        page.on("dialog", lambda dialog: dialog.accept(str(video)))
        open_recipe_list(page, running)

        # F1 opens the help for the screen on show; Esc closes it
        page.keyboard.press("F1")
        help_box = page.locator("#help")
        help_box.get_by_text("Recipe 파일이 있는 폴더를").wait_for()
        assert help_box.locator("#helpTitle").inner_text() == "도움말 · Recipe 목록"
        assert not help_box.get_by_text("타원 안쪽 끌기").is_visible()
        page.keyboard.press("Escape")
        assert not help_box.is_visible()

        page.get_by_role("button", name="새 Recipe").click()
        page.wait_for_function("document.getElementById('time').textContent.startsWith('00:00.0')")
        speed = page.get_by_label("재생 배속")
        assert speed.input_value() == "1"

        # typed speeds: "*3" reads as 3, text that is not a number keeps it, a large value is clamped
        for typed, shown in (("*3", "3"), ("abc", "3"), ("2x", "2"), ("100", "16"), ("0", "0.1")):
            speed.fill(typed)
            speed.press("Enter")
            assert speed.input_value() == shown, typed
        page.get_by_role("button", name="배속 선택").click()
        page.get_by_role("option", name="4×").click()
        assert speed.input_value() == "4"
        assert page.locator("#speedMenu").is_hidden()

        # 4×: 0.5 s of playback covers about 2 s of the 3 s video
        page.keyboard.press("Space")
        page.wait_for_timeout(500)
        page.keyboard.press("Space")
        minutes, seconds = page.locator("#time").inner_text().split(" / ")[0].split(":")
        assert float(seconds) >= 1.2
        shot(page, "6-speed")

        # the button opens the Recipe screen help; keys do not reach the screen while it is open
        page.get_by_role("button", name="+ 추가").click()
        before = field(page, "중심 X").input_value()
        page.get_by_role("button", name="도움말").click()
        help_box.get_by_text("타원 안쪽 끌기").wait_for()
        assert help_box.locator("#helpTitle").inner_text() == "도움말 · Recipe 화면"
        page.keyboard.press("ArrowRight")
        shot(page, "7-help")
        page.mouse.click(5, 5)  # outside the dialog
        assert not help_box.is_visible()
        assert field(page, "중심 X").input_value() == before
        page.locator("#frame").focus()
        page.keyboard.press("?")
        help_box.get_by_text("타원 안쪽 끌기").wait_for()
        help_box.get_by_role("button", name="닫기").click()
        assert not help_box.is_visible()
        assert errors == []
    finally:
        running.close()
