import importlib.util
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.adapters.storage.recipe_files import recipe_to_json
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.recipe import Glass, Recipe, ReferenceFrame

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("time_analysis", ROOT / "scripts" / "time_analysis.py")
script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(script)


def test_timing_lines(tmp_path, capsys):
    video = tmp_path / "level.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (160, 120))
    for index in range(30):
        frame = np.full((120, 160, 3), 50, np.uint8)
        frame[20 + 2 * index:] = 210
        writer.write(frame)
    writer.release()
    recipe = Recipe(
        "r1", "test", ReferenceFrame(160, 120, "level.avi", 0.0, b"jpeg"),
        (Glass("g1", "BASE", Ellipse(50, 60, 30, 50), 60), Glass("g2", "ACCUM", Ellipse(115, 60, 25, 40), 60)),
        "c", "u",
    )
    recipe_path = tmp_path / "test.recipe.json"
    recipe_path.write_text(recipe_to_json(recipe), encoding="utf-8")

    assert script.main(["--video", str(video), "--recipe", str(recipe_path)]) == 0
    lines = [line for line in capsys.readouterr().out.splitlines() if not line.startswith("  progress")]
    assert lines[0].startswith('video name="level.avi" bytes=')
    assert lines[0].endswith("columns=6 frames_decoded=26")
    assert lines[1].startswith("pass glasses=2 hardware_requested=False hardware_used=False grab=")
    assert lines[2].startswith('glass name="BASE" context=6x100 mean=')
    assert lines[3].startswith('glass name="ACCUM" context=6x80 mean=')
    assert lines[4].startswith("sha256 seconds=")
    assert lines[5].startswith("analysis total=") and lines[5].endswith("limit=180s")
