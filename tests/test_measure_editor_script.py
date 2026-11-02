"""The A5/A6 measuring script, run end to end on macOS Chrome with short settings (no Windows claim).

Skipped when Playwright or Chrome is missing.
"""

import importlib.util
import re
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

from oil_tracker.adapters.storage.recipe_files import recipe_to_json
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.recipe import Glass, Recipe, ReferenceFrame

pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))  # the script imports its neighbour, time_analysis
SPEC = importlib.util.spec_from_file_location("measure_editor", ROOT / "scripts" / "measure_editor.py")
script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(script)


def test_the_result_file_has_every_measure(tmp_path, capsys):
    video = tmp_path / "level.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (320, 240))
    for index in range(60):
        frame = np.full((240, 320, 3), 60, np.uint8)
        frame[150 - index:, 120:200] = 200
        writer.write(frame)
    writer.release()
    glass = Glass("g1", "BASE", Ellipse(160, 120, 40, 100), 130)
    recipe_path = tmp_path / "smoke.recipe.json"
    recipe_path.write_text(recipe_to_json(Recipe("r1", "스모크", ReferenceFrame(320, 240, "level.avi", 0.0, b"jpeg"),
                                                 (glass,), "c", "u")), encoding="utf-8")

    out = tmp_path / "result.md"
    argv = ["--video", str(video), "--recipe", str(recipe_path), "--browser", "chrome", "--size", "1280x800",
            "--drags", "1", "--seeks", "3", "--play-sec", "1", "--out", str(out)]
    try:
        code = script.main(argv)
    except Exception as error:  # noqa: BLE001
        pytest.skip(f"Chrome is not available: {error}")
    text = out.read_text(encoding="utf-8")
    if "Executable doesn't exist" in text or "is not found" in text:
        pytest.skip("Chrome is not available")
    assert code == 0, text
    printed = capsys.readouterr().out
    assert "[4/5] 편집기 측정: chrome" in printed and "[5/5] 중앙값 비교 (A4)" in printed
    assert "샘플 12개" in text and "코덱 `MJPG`" in text
    assert "- 키프레임: 60개, 간격 최소 1 / 중앙값 1 / 최대 1 프레임" in text  # MJPG: every frame is a key frame
    rows = [line for line in text.splitlines() if line.startswith("| ")]
    assert any(row.startswith("| 연필, 전체 보기") for row in rows)
    assert any(row.startswith("| **전체** |") for row in rows)
    assert any(row.startswith("| 정확한 프레임 (서버) | 3 |") for row in rows)
    assert any(row.startswith("| frames (대체) |") for row in rows)  # an AVI does not play in a <video>
    assert any(row.startswith("| `uint8` 부분 정렬 (지금) | 기준 |") for row in rows)
    assert "**다름**" not in text
    assert text.rstrip().endswith("오류: 없음")
    assert (out.parent / next(p.name for p in out.parent.iterdir() if p.name.startswith("a5a6-data-"))).is_dir()


FAKE_APP = '''
import os, signal, subprocess, sys, tempfile, time
sys.path.insert(0, sys.argv[1])
from oil_tracker import bootstrap
chrome, data = sys.argv[2], sys.argv[4]
running = bootstrap.start(data_folder=__import__("pathlib").Path(data))
port = os.environ["OLT_WEBVIEW_DEBUG_PORT"]
profile = tempfile.mkdtemp()
window = subprocess.Popen([chrome, "--headless=new", f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
                           "--no-first-run", "--window-size=1440,900", running.url],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
signal.signal(signal.SIGTERM, lambda *_: (window.terminate(), window.wait(), running.close(), sys.exit(0)))
while True:
    time.sleep(1)
'''


def test_the_built_app_is_measured_in_its_own_window(tmp_path, capsys):
    # The app mode (V2-5) on macOS: a stand-in for OilLevelTracker.exe serves this folder's code and
    # opens Chrome with the debugging port the script asks the app for.
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            chrome = p.chromium.launch(channel="chrome")
        except Exception as error:  # noqa: BLE001
            pytest.skip(f"Chrome is not available: {error}")
        chrome.close()
    candidates = [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                  Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")]
    binary = next((c for c in candidates if c.exists()), None)
    if binary is None:
        pytest.skip("no Chrome binary to stand in for WebView2")
    video = tmp_path / "level.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (320, 240))
    for index in range(60):
        frame = np.full((240, 320, 3), 60, np.uint8)
        frame[150 - index:, 120:200] = 200
        writer.write(frame)
    writer.release()
    glass = Glass("g1", "BASE", Ellipse(160, 120, 40, 100), 130)
    recipe_path = tmp_path / "smoke.recipe.json"
    recipe_path.write_text(recipe_to_json(Recipe("r1", "스모크", ReferenceFrame(320, 240, "level.avi", 0.0, b"jpeg"),
                                                 (glass,), "c", "u")), encoding="utf-8")
    fake = tmp_path / "fake_app.py"
    fake.write_text(FAKE_APP, encoding="utf-8")
    out = tmp_path / "result.md"

    found = script.measure_with(
        type("Args", (), {"video": video, "drags": 1, "seeks": 3, "play_sec": 1})(),
        [sys.executable, str(fake), str(ROOT / "src"), str(binary)],
        _data_folder(tmp_path, recipe_path), recipe_from(recipe_path), (1280, 800),
        facts := {"browser": "WebView2 (앱 창)"}, errors := [],
    )
    assert errors == []
    assert facts["window_sec"] > 0 and facts["analysis_sec"] > 0
    assert re.fullmatch(r"\d+x\d+", facts["size"])  # the window's page, as the app opened it
    assert found["samples"] == 12 and found["seeks"]["n"] == 3 and found["a5_all"]["n"] > 0
    printed = capsys.readouterr().out
    assert "[3/5] 분석 (빌드한 앱으로" in printed and "[4/5] 편집기 측정: WebView2 (앱 창)" in printed


def _data_folder(tmp_path, recipe_path):
    data = tmp_path / "data"
    (data / "Recipes").mkdir(parents=True)
    (data / "Recipes" / recipe_path.name).write_bytes(recipe_path.read_bytes())
    return data


def recipe_from(path):
    from oil_tracker.adapters.storage.recipe_files import recipe_from_json

    return recipe_from_json(path.read_text(encoding="utf-8"))
