import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.domain.geometry import Ellipse

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("compare_medians", ROOT / "scripts" / "compare_medians.py")
script = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(script)


def test_every_way_gives_the_apps_medians(tmp_path):
    video = tmp_path / "noise.avi"
    rng = np.random.default_rng(5)
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (160, 120))
    for _ in range(40):
        frame = rng.integers(0, 256, (120, 160, 3), dtype=np.uint8)
        frame[:, :40] = rng.choice([0, 255], (120, 40, 3)).astype(np.uint8)  # ties with the fill values
        writer.write(frame)
    writer.release()
    # odd and even band widths, and an ellipse cut by the frame's edges
    ellipses = [Ellipse(60, 60, 30, 50), Ellipse(100, 55, 31.5, 40), Ellipse(10, 110, 25, 45)]
    found = script.compare(video, ellipses, frames=6, repeats=1, pass_sec=2.0, rounds=1, threads=2)
    assert [w["name"] for w in found["ways"]] == list(script.WAYS)
    assert all(w["same"] for w in found["ways"])
    assert len(found["passes"]) == 3 and all(p["same"] for p in found["passes"])
    assert found["passes"][0]["name"] == script.APP
    text = "\n".join(script.markdown(found))
    assert "| `uint8` 부분 정렬 (지금) | 기준 |" in text and "**다름**" not in text
    assert "| 2회 |" in text and "| — |" in text  # one round only


def test_a_different_way_is_marked(tmp_path, monkeypatch):
    video = tmp_path / "flat.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (64, 64))
    for index in range(20):
        writer.write(np.full((64, 64, 3), 10 * index, np.uint8))
    writer.release()
    monkeypatch.setitem(script.WAYS, "틀린 방식", lambda band: lambda frame: np.zeros((band.rows.size, 3), np.uint8))
    found = script.compare(video, [Ellipse(32, 32, 20, 25)], frames=4, repeats=1, pass_sec=1.0, rounds=1, threads=1)
    assert {w["name"]: w["same"] for w in found["ways"]}["틀린 방식"] is False
    assert "틀린 방식" not in [p["name"] for p in found["passes"]]  # only identical ways are timed in the pass
    assert "| 틀린 방식 | **다름** |" in "\n".join(script.markdown(found))
