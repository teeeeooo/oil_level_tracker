from __future__ import annotations

from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsScene

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.ui.widgets.video_overlay_canvas import (
    DraggableZeroLine,
    VideoOverlayCanvas,
    resized_rect,
    scene_rect_in_frame,
)


def test_scene_rect_conversion_returns_qrectf_without_bounding_rect_call(qtbot):
    scene = QGraphicsScene()
    item = QGraphicsRectItem(QRectF(10, 20, 40, 50))
    scene.addItem(item)
    item.setPos(5, 7)
    result = scene_rect_in_frame(item, item.rect(), QRectF(0, 0, 200, 200))
    assert result == QRectF(15, 27, 40, 50)


def test_diagonal_resize_changes_both_axes_and_keeps_opposite_corner():
    start = QRectF(100, 100, 120, 160)
    result = resized_rect(start, "br", QPointF(300, 340), QRectF(0, 0, 500, 500))
    assert result.topLeft() == start.topLeft()
    assert result.width() == 200
    assert result.height() == 240


def test_side_resize_only_changes_requested_axis():
    start = QRectF(100, 100, 120, 160)
    result = resized_rect(start, "r", QPointF(280, 10), QRectF(0, 0, 500, 500))
    assert result.top() == start.top()
    assert result.height() == start.height()
    assert result.right() == 280


def test_zero_line_moves_independently_and_has_reference_label(qtbot):
    glass = InspectionRecipe.default_glass(640, 480)
    ellipse = glass.geometry.ellipse
    original = (ellipse.center_x, ellipse.center_y, ellipse.radius_x, ellipse.radius_y)
    changes = []
    line = DraggableZeroLine(glass.id, ellipse.center_y, ellipse, lambda _id, y: changes.append(y))
    scene = QGraphicsScene()
    scene.addItem(line)
    line._set_y(ellipse.center_y + 25)
    assert line.line().y1() == ellipse.center_y + 25
    assert line.label.text() == "기준점"
    assert (ellipse.center_x, ellipse.center_y, ellipse.radius_x, ellipse.radius_y) == original


def test_normal_canvas_does_not_draw_detector_candidate_lines(qtbot):
    canvas = VideoOverlayCanvas()
    qtbot.addWidget(canvas)
    glass = InspectionRecipe.default_glass(640, 480)
    canvas.set_frame(np.zeros((480, 640, 3), dtype=np.uint8))
    canvas.set_glasses([glass], glass.id)
    detection = SimpleNamespace(
        glass_id=glass.id,
        fill_state=FillState.PARTIAL_VISIBLE,
        overall_confidence=0.8,
        candidates=[SimpleNamespace(y=100), SimpleNamespace(y=200)],
    )
    canvas.set_detection(detection)
    line_items = [item for item in canvas.scene().items() if isinstance(item, QGraphicsLineItem)]
    assert len(line_items) == 1
    assert isinstance(line_items[0], DraggableZeroLine)
