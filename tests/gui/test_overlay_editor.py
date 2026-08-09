from __future__ import annotations

from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
)

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.geometry import ExclusionZone, Rect
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.widgets.video_overlay_canvas import (
    DraggableZeroLine,
    EditableEllipseItem,
    ResizeHandleItem,
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


def test_video_preview_shared_canvas_resets_on_open_and_preserves_frame_zoom(qtbot):
    import oil_tracker.ui.widgets.video_preview_widget as preview_module

    class Reader:
        instances = []

        def __init__(self, path):
            self.metadata = VideoMetadata(str(path), 640, 480, 30.0, 10.0, 300, "fake")
            self.closed = False
            self.instances.append(self)

        def read_at(self, timestamp):
            return np.zeros((480, 640, 3), dtype=np.uint8), int(timestamp * 30), float(timestamp)

        def close(self):
            self.closed = True

    preview = preview_module.VideoPreviewWidget(reader_factory=Reader)
    qtbot.addWidget(preview)
    preview.resize(760, 520)
    preview.show()
    QApplication.processEvents()

    preview.open_video("first.mp4")
    first = Reader.instances[-1]
    assert preview.canvas.fit_mode is True
    preview.canvas.zoom_in()
    manual_scale = preview.canvas.transform().m11()
    preview.load_frame(1.0)
    assert preview.canvas.fit_mode is False
    assert abs(preview.canvas.transform().m11() - manual_scale) < 1e-9

    preview.open_video("second.mp4")
    second = Reader.instances[-1]
    assert preview.canvas.fit_mode is True
    assert first.closed is True
    assert second.closed is False

    preview.close_video()
    assert second.closed is True


def test_resize_handles_keep_eight_direction_hit_targets_with_restrained_markers(qtbot):
    glass = InspectionRecipe.default_glass(640, 480)
    e = glass.geometry.ellipse
    item = EditableEllipseItem(
        glass.id,
        QRectF(e.bounds.x, e.bounds.y, e.bounds.width, e.bounds.height),
        QRectF(0, 0, 640, 480),
        lambda *_args: None,
    )
    scene = QGraphicsScene()
    scene.addItem(item)
    item.setSelected(True)

    assert tuple(item._handles) == EditableEllipseItem.HANDLE_ROLES
    assert len(item._handles) == 8
    for handle in item._handles.values():
        assert handle.rect().width() == ResizeHandleItem.HIT_SIZE == 18.0
        assert handle.rect().height() == ResizeHandleItem.HIT_SIZE
        assert ResizeHandleItem.VISUAL_SIZE == 6.0
        assert handle.flags() & QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations

    item.begin_resize("br", item.rect().bottomRight())
    assert item._handles["br"]._resize_active is True
    item.end_resize(item.rect().bottomRight())
    assert item._handles["br"]._resize_active is False


def _drag_view(canvas, start_scene: QPointF, end_scene: QPointF) -> None:
    start = canvas.mapFromScene(start_scene)
    end = canvas.mapFromScene(end_scene)
    QTest.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=start)
    QApplication.processEvents()
    QTest.mouseMove(canvas.viewport(), end, delay=10)
    QApplication.processEvents()
    QTest.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=end)
    QApplication.processEvents()


def test_exclusion_drag_and_resize_do_not_move_selected_ellipse(qtbot):
    canvas = VideoOverlayCanvas()
    qtbot.addWidget(canvas)
    canvas.resize(720, 520)
    canvas.show()
    glass = InspectionRecipe.default_glass(640, 480)
    glass.geometry.exclusions = [
        ExclusionZone("zone-a", Rect(280, 150, 80, 50), "Zone A"),
        ExclusionZone("zone-b", Rect(180, 300, 70, 45), "Zone B"),
    ]
    canvas.set_frame(np.zeros((480, 640, 3), dtype=np.uint8), reset_view=True)
    canvas.set_glasses([glass], glass.id)
    QApplication.processEvents()

    ellipse = canvas._editable_ellipse_item
    first = canvas._exclusion_items["zone-a"]
    second = canvas._exclusion_items["zone-b"]
    ellipse_before = QRectF(ellipse.rect())
    second_before = QRectF(second.rect())
    geometry_changes = QSignalSpy(canvas.geometryChanged)
    exclusion_changes = QSignalSpy(canvas.exclusionChanged)

    _drag_view(canvas, QPointF(300, 170), QPointF(335, 190))

    assert ellipse.rect() == ellipse_before
    assert ellipse.pos() == QPointF(0, 0)
    assert geometry_changes.count() == 0
    assert first.rect() != QRectF(280, 150, 80, 50)
    assert second.rect() == second_before
    assert exclusion_changes.count() == 1
    assert exclusion_changes.at(0)[1] == "zone-a"
    assert canvas._active_target == "exclusion"
    assert canvas._active_zone_id == "zone-a"
    assert ellipse.isSelected() is True

    first_before_resize = QRectF(first.rect())
    resize_start = first_before_resize.bottomRight() - QPointF(2, 2)
    _drag_view(canvas, resize_start, resize_start + QPointF(30, 25))

    assert ellipse.rect() == ellipse_before
    assert ellipse.pos() == QPointF(0, 0)
    assert geometry_changes.count() == 0
    assert first.rect().width() > first_before_resize.width()
    assert first.rect().height() > first_before_resize.height()
    assert second.rect() == second_before
    assert exclusion_changes.count() == 2
    assert exclusion_changes.at(1)[1] == "zone-a"
    assert ellipse.isSelected() is True


def test_ellipse_drag_and_resize_still_work_after_exclusion_interaction(qtbot):
    canvas = VideoOverlayCanvas()
    qtbot.addWidget(canvas)
    canvas.resize(720, 520)
    canvas.show()
    glass = InspectionRecipe.default_glass(640, 480)
    glass.geometry.exclusions = [ExclusionZone("zone-a", Rect(280, 150, 80, 50), "Zone A")]
    canvas.set_frame(np.zeros((480, 640, 3), dtype=np.uint8), reset_view=True)
    canvas.set_glasses([glass], glass.id)
    QApplication.processEvents()
    geometry_changes = QSignalSpy(canvas.geometryChanged)

    _drag_view(canvas, QPointF(300, 170), QPointF(325, 185))
    e = glass.geometry.ellipse
    _drag_view(canvas, QPointF(e.center_x, e.center_y + 70), QPointF(e.center_x + 20, e.center_y + 80))
    assert geometry_changes.count() == 1

    ellipse = canvas._editable_ellipse_item
    top_handle = canvas.mapFromScene(QPointF(ellipse.rect().center().x(), ellipse.rect().top()))
    resize_end = canvas.mapFromScene(QPointF(ellipse.rect().center().x(), ellipse.rect().top() - 20))
    QTest.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=top_handle)
    QTest.mouseMove(canvas.viewport(), resize_end, delay=10)
    QTest.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=resize_end)
    QApplication.processEvents()
    assert geometry_changes.count() == 2


def test_overlay_mouse_press_requests_exact_targets(qtbot):
    canvas = VideoOverlayCanvas()
    qtbot.addWidget(canvas)
    canvas.resize(720, 520)
    canvas.show()
    glass = InspectionRecipe.default_glass(640, 480)
    zone = glass.geometry.exclusions
    if not zone:
        glass.geometry.exclusions.append(ExclusionZone("zone-a", Rect(280, 210, 80, 60), "Zone A"))
    canvas.set_frame(np.zeros((480, 640, 3), dtype=np.uint8), reset_view=True)
    canvas.set_glasses([glass], glass.id)
    QApplication.processEvents()
    spy = QSignalSpy(canvas.interactionTargetRequested)
    geometry_changes = QSignalSpy(canvas.geometryChanged)
    zero_changes = QSignalSpy(canvas.zeroLineChanged)
    exclusion_changes = QSignalSpy(canvas.exclusionChanged)

    zero_pos = canvas.mapFromScene(QPointF(glass.geometry.ellipse.center_x, glass.geometry.zero_line_y))
    qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=zero_pos)
    qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=zero_pos)
    assert spy.count() >= 1
    zero_signal = spy.at(spy.count() - 1)
    assert zero_signal[0] == glass.id
    assert zero_signal[1] == "zero_line"
    assert zero_changes.count() == 0

    exact = glass.geometry.exclusions[0]
    zone_pos = canvas.mapFromScene(QPointF(exact.rect.x + exact.rect.width / 2, exact.rect.y + exact.rect.height / 2))
    qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=zone_pos)
    qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=zone_pos)
    exclusion_signal = spy.at(spy.count() - 1)
    assert exclusion_signal[1] == "exclusion"
    assert exclusion_signal[2] == exact.id
    assert exclusion_changes.count() == 0
    assert canvas._editable_ellipse_item.isSelected() is True

    e = glass.geometry.ellipse
    handle_pos = canvas.mapFromScene(QPointF(e.center_x, e.center_y - e.radius_y))
    qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=handle_pos)
    qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=handle_pos)
    geometry_signal = spy.at(spy.count() - 1)
    assert geometry_signal[1] == "geometry"
    assert geometry_changes.count() == 0
