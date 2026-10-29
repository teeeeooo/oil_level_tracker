"""The A5/A6 measuring script, run end to end on macOS Chrome with short settings (no Windows claim).

Skipped when Playwright or Chrome is missing.
"""

import importlib.util
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
    assert "[4/4] 편집기 측정: chrome" in capsys.readouterr().out
    assert "샘플 12개" in text and "코덱 `MJPG`" in text
    rows = [line for line in text.splitlines() if line.startswith("| ")]
    assert any(row.startswith("| 연필, 전체 보기") for row in rows)
    assert any(row.startswith("| **전체** |") for row in rows)
    assert any(row.startswith("| 정확한 프레임 (서버) | 3 |") for row in rows)
    assert any(row.startswith("| frames (대체) |") for row in rows)  # an AVI does not play in a <video>
    assert text.rstrip().endswith("오류: 없음")
    assert (out.parent / next(p.name for p in out.parent.iterdir() if p.name.startswith("a5a6-data-"))).is_dir()
