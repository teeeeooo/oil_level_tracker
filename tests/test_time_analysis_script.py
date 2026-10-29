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

    out = tmp_path / "result.md"
    assert script.main(["--video", str(video), "--recipe", str(recipe_path), "--runs", "software", "--out", str(out)]) == 0
    printed = capsys.readouterr().out
    assert "[1/3] PC와 소프트웨어 확인" in printed and "[3/3] 분석: software 디코딩" in printed
    text = out.read_text(encoding="utf-8")
    assert text in printed
    rows = [line for line in text.splitlines() if line.startswith("| software |")]
    assert rows[0].startswith("| software | False | ")
    assert rows[1].startswith("| software | BASE | 6x100 | ")
    assert rows[2].startswith("| software | ACCUM | 6x80 | ")
    assert "`level.avi`, " in text and ", 160x120, 10.000 fps, 30 frames" in text
    assert text.rstrip().endswith("오류: 없음")


def test_the_source_digest_covers_the_code_that_runs():
    digest, files = script.source_digest()
    assert len(digest) == 12 and int(digest, 16) >= 0
    assert files > 20
