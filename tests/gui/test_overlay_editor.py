from __future__ import annotations

from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtWidgets import QApplication, QGraphicsLineItem, QGraphicsRectItem, QGraphicsScene

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.widgets.video_overlay_canvas import (
    DraggableZeroLine,
    VideoOverlayCanvas,
    resized_rect,
    scene_rect_in_frame,
)


class _PointerEvent:
    def __init__(self, x: float, y: float, button: Qt.MouseButton) -> None:
        self._position = QPointF(x, y)
        self._button = button
        self.accepted = False

    def position(self) -> QPointF:
        return self._position

    def button(self) -> Qt.MouseButton:
        return self._button

    def accept(self) -> None:
        self.accepted = True


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


def test_detection_status_update_does_not_rebuild_editable_geometry(qtbot):
    canvas = VideoOverlayCanvas()
    qtbot.addWidget(canvas)
    glass = InspectionRecipe.default_glass(640, 480)
    canvas.set_frame(np.zeros((480, 640, 3), dtype=np.uint8))
    canvas.set_glasses([glass], glass.id)
    editable = canvas._editable_ellipse_item
    detection = SimpleNamespace(
        glass_id=glass.id,
        fill_state=FillState.PARTIAL_VISIBLE,
        overall_confidence=0.8,
        candidates=[],
    )
    canvas.set_detection(detection)
    assert canvas._editable_ellipse_item is editable
    assert editable.scene() is canvas.scene()


def test_fit_zoom_frame_refresh_and_resize_have_distinct_view_lifetimes(qtbot):
    canvas = VideoOverlayCanvas()
    qtbot.addWidget(canvas)
    canvas.resize(720, 480)
    canvas.show()
    QApplication.processEvents()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    canvas.set_frame(frame, reset_view=True)
    fit_scale = canvas.transform().m11()
    assert canvas.fit_mode is True
    assert fit_scale > 0

    canvas.zoom_in()
    manual_scale = canvas.transform().m11()
    assert canvas.fit_mode is False
    assert manual_scale > fit_scale

    canvas.set_frame(np.ones_like(frame))
    assert abs(canvas.transform().m11() - manual_scale) < 1e-9
    canvas.resize(780, 520)
    QApplication.processEvents()
    assert abs(canvas.transform().m11() - manual_scale) < 1e-9

    canvas.fit_to_view()
    assert canvas.fit_mode is True
    resized_fit_scale = canvas.transform().m11()
    canvas.resize(680, 460)
    QApplication.processEvents()
    assert canvas.fit_mode is True
    assert abs(canvas.transform().m11() - resized_fit_scale) > 1e-6

    canvas.actual_size()
    assert canvas.fit_mode is False
    assert abs(canvas.transform().m11() - 1.0) < 1e-9


def test_manual_pan_and_scene_coordinates_remain_view_only(qtbot):
    canvas = VideoOverlayCanvas()
    qtbot.addWidget(canvas)
    canvas.resize(700, 460)
    canvas.show()
    QApplication.processEvents()
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    glass = InspectionRecipe.default_glass(1920, 1080)
    recipe = InspectionRecipe.empty(1920, 1080)
    recipe.glasses = [glass]
    recipe_before = recipe.to_dict()

    canvas.set_frame(frame, reset_view=True)
    canvas.set_glasses([glass], glass.id)
    canvas.actual_size()
    hbar = canvas.horizontalScrollBar()
    vbar = canvas.verticalScrollBar()
    assert hbar.maximum() > 0
    assert vbar.maximum() > 0
    hbar.setValue(hbar.maximum() // 2)
    vbar.setValue(vbar.maximum() // 2)
    before = (hbar.value(), vbar.value())

    press = _PointerEvent(350, 230, Qt.MouseButton.MiddleButton)
    move = _PointerEvent(310, 190, Qt.MouseButton.NoButton)
    release = _PointerEvent(310, 190, Qt.MouseButton.MiddleButton)
    canvas.mousePressEvent(press)
    canvas.mouseMoveEvent(move)
    canvas.mouseReleaseEvent(release)

    assert press.accepted and move.accepted and release.accepted
    assert hbar.value() == before[0] + 40
    assert vbar.value() == before[1] + 40
    assert canvas.fit_mode is False
    assert recipe.to_dict() == recipe_before

    source_point = QPointF(713.25, 421.75)
    view_point = canvas.mapFromScene(source_point)
    restored = canvas.mapToScene(view_point)
    assert abs(restored.x() - source_point.x()) <= 1.0
    assert abs(restored.y() - source_point.y()) <= 1.0


def test_context_reset_returns_manual_view_to_fit(qtbot):
    canvas = VideoOverlayCanvas()
    qtbot.addWidget(canvas)
    canvas.resize(720, 480)
    canvas.show()
    QApplication.processEvents()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    canvas.set_frame(frame, reset_view=True)
    canvas.zoom_in()
    assert canvas.fit_mode is False

    canvas.set_frame(frame, reset_view=True)

    assert canvas.fit_mode is True


def test_video_preview_shared_canvas_resets_on_open_and_preserves_frame_zoom(qtbot, monkeypatch):
    import oil_tracker.ui.widgets.video_preview_widget as preview_module

    class Reader:
        def __init__(self, path):
            self.metadata = VideoMetadata(str(path), 640, 480, 30.0, 10.0, 300, "fake")

        def read_at(self, timestamp):
            return np.zeros((480, 640, 3), dtype=np.uint8), int(timestamp * 30), float(timestamp)

        def close(self):
            pass

    monkeypatch.setattr(preview_module, "OpenCvVideoReader", Reader)
    preview = preview_module.VideoPreviewWidget()
    qtbot.addWidget(preview)
    preview.resize(760, 520)
    preview.show()
    QApplication.processEvents()

    preview.open_video("first.mp4")
    assert preview.canvas.fit_mode is True
    preview.canvas.zoom_in()
    manual_scale = preview.canvas.transform().m11()
    preview.load_frame(1.0)
    assert preview.canvas.fit_mode is False
    assert abs(preview.canvas.transform().m11() - manual_scale) < 1e-9

    preview.open_video("second.mp4")
    assert preview.canvas.fit_mode is True
