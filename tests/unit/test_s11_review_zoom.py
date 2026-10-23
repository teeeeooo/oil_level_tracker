import json
from types import SimpleNamespace

import cv2
import numpy as np

from tests.diagnostics import s11_review_zoom as zoom


def _ellipse(cx=100.0, cy=120.0, rx=40.0, ry=50.0):
    return SimpleNamespace(center_x=cx, center_y=cy, radius_x=rx, radius_y=ry)


def test_box_scale_and_ruler_follow_the_ellipse():
    box = zoom.zoom_box(_ellipse(), (400, 300, 3))
    assert box == (52, 62, 148, 178)
    assert zoom.zoom_box(_ellipse(cx=10, cy=10), (400, 300, 3))[:2] == (0, 0)
    assert zoom.auto_scale(box) == 5  # 116 px tall -> about 600 px
    assert zoom.auto_scale((0, 0, 10, 20)) == 8 and zoom.auto_scale((0, 0, 10, 600)) == 2
    assert zoom.ruler_steps(5) == (5, 10) and zoom.ruler_steps(3) == (10, 20)


def test_sheet_pixel_maps_back_to_the_source_row_and_column():
    image = np.zeros((300, 300, 3), np.uint8)
    box, scale = (52, 62, 148, 178), 5
    panels = [zoom.panel(image, box, scale, f"p{index}") for index in range(4)]
    sheet = zoom.sheet(panels, "header")
    height, width = panels[0].shape[:2]
    assert sheet.shape[:2] == (zoom.HEADER + 2 * height, zoom.COLUMNS * width)
    # Centre of source pixel (x=70, y=100) in the fourth panel (row 1, column 0).
    column = zoom.LEFT + (70 - box[0]) * scale + scale // 2
    row = zoom.HEADER + height + zoom.TOP + (100 - box[1]) * scale + scale // 2
    number, x, y = zoom.source_point(column, row, list(box), scale, [width, height])
    assert number == 3
    assert abs(x - 70.4) < 1e-9 and abs(y - 99.9) < 1e-9


def test_read_marks_returns_only_red_marks_per_frame(tmp_path):
    image = np.full((300, 300, 3), 90, np.uint8)
    box, scale = (52, 62, 148, 178), 5
    panels = [zoom.panel(image, box, scale, f"p{index}") for index in range(2)]
    clean = zoom.sheet(panels, "header")
    height, width = panels[0].shape[:2]
    cv2.imwrite(str(tmp_path / "review-zoom.png"), clean)
    manifest = {"review_id": "review-x", "zoom_source_xyxy": list(box), "scale": scale,
                "panel_size": [width, height],
                "frames": [{"frame_index": 10, "decoded_time_sec": 1.0},
                           {"frame_index": 20, "decoded_time_sec": 2.0}],
                "image": {"path": "review-zoom.png", "sha256": "x"}}
    (tmp_path / "review-zoom.json").write_text(json.dumps(manifest), encoding="utf-8")
    marked = clean.copy()
    centre = (width + zoom.LEFT + (100 - box[0]) * scale, zoom.HEADER + zoom.TOP + (130 - box[1]) * scale)
    cv2.circle(marked, centre, 6, (40, 40, 240), -1)  # red dot in the second panel
    cv2.circle(marked, (zoom.LEFT + 50, zoom.HEADER + zoom.TOP + 50), 6, (240, 240, 240), -1)  # not red
    cv2.imwrite(str(tmp_path / "marked.png"), marked)

    result = zoom.read_marks(tmp_path / "review-zoom.json", tmp_path / "marked.png")

    assert result["frames"][0]["marks"] == []
    (x, y), = result["frames"][1]["marks"]
    assert abs(x - 100) <= 0.3 and abs(y - 129.5) <= 0.3
    assert result["changed_not_red_px"] > 0


def test_read_marks_stops_on_a_rescaled_image(tmp_path):
    clean = np.full((100, 120, 3), 90, np.uint8)
    cv2.imwrite(str(tmp_path / "review-zoom.png"), clean)
    (tmp_path / "review-zoom.json").write_text(json.dumps(
        {"review_id": "r", "zoom_source_xyxy": [0, 0, 1, 1], "scale": 5, "panel_size": [120, 66],
         "frames": [], "image": {"path": "review-zoom.png", "sha256": "x"}}), encoding="utf-8")
    cv2.imwrite(str(tmp_path / "marked.png"), cv2.resize(clean, (118, 98)))
    try:
        zoom.read_marks(tmp_path / "review-zoom.json", tmp_path / "marked.png")
    except SystemExit as stop:
        assert "STOP" in str(stop)
    else:
        raise AssertionError("a rescaled image must stop")
