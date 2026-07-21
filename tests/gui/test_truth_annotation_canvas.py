from __future__ import annotations

import numpy as np
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage

from oil_tracker.application.services.user_truth import UserTruthService
from oil_tracker.ui.widgets.truth_annotation_canvas import TruthAnnotationCanvas
from user_truth_fixtures import make_truth_bundle


def _canvas(qtbot, tmp_path):
    bundle = make_truth_bundle(tmp_path)
    glass = bundle.recipe.glasses[0]
    official = UserTruthService().official_reference(bundle, glass, 2.0)
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    canvas = TruthAnnotationCanvas()
    qtbot.addWidget(canvas)
    canvas.set_frame(frame)
    canvas.set_context(
        glass,
        official_reference=official,
        truth_oil_y=128.0,
        truth_foam_y=118.0,
        status_text="frame 60",
    )
    canvas.actual_size()
    canvas.show()
    return canvas, glass, official


def test_canvas_keeps_separate_official_and_truth_layers_with_labels(qtbot, tmp_path):
    canvas, _glass, official = _canvas(qtbot, tmp_path)
    assert canvas._official is official
    assert canvas.oil_y == 128.0
    assert canvas.foam_y == 118.0
    assert canvas.edit_target == "oil"
    image = QImage(canvas.size(), QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    canvas.render(image)
    assert not image.isNull()
    assert canvas._show_official


def test_oil_click_and_drag_emit_source_frame_canonical_y(qtbot, tmp_path):
    canvas, glass, _official = _canvas(qtbot, tmp_path)
    received = []
    canvas.oilLineChanged.connect(received.append)
    target_y = int(round(glass.geometry.ellipse.center_y + 4))
    center_x = int(round(glass.geometry.ellipse.center_x))
    qtbot.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(center_x, target_y))
    assert received[-1] == target_y
    assert canvas.oil_y == target_y
    drag_y = target_y + 6
    qtbot.mousePress(canvas, Qt.MouseButton.LeftButton, pos=QPoint(center_x, target_y))
    qtbot.mouseMove(canvas, QPoint(center_x, drag_y))
    qtbot.mouseRelease(canvas, Qt.MouseButton.LeftButton, pos=QPoint(center_x, drag_y))
    assert canvas.oil_y == drag_y


def test_foam_edit_target_is_independent_from_oil(qtbot, tmp_path):
    canvas, glass, _official = _canvas(qtbot, tmp_path)
    original_oil = canvas.oil_y
    received = []
    canvas.foamLineChanged.connect(received.append)
    canvas.set_edit_target("foam")
    target_y = int(round(glass.geometry.ellipse.center_y - 8))
    qtbot.mouseClick(
        canvas,
        Qt.MouseButton.LeftButton,
        pos=QPoint(int(glass.geometry.ellipse.center_x), target_y),
    )
    assert canvas.foam_y == target_y
    assert received[-1] == target_y
    assert canvas.oil_y == original_oil


def test_keyboard_moves_active_line_by_one_and_shift_five_pixels(qtbot, tmp_path):
    canvas, _glass, _official = _canvas(qtbot, tmp_path)
    canvas.set_edit_target("oil")
    canvas.setFocus()
    start = canvas.oil_y
    qtbot.keyClick(canvas, Qt.Key.Key_Down)
    assert canvas.oil_y == start + 1
    qtbot.keyClick(canvas, Qt.Key.Key_Up, modifier=Qt.KeyboardModifier.ShiftModifier)
    assert canvas.oil_y == start - 4


def test_numeric_out_of_range_is_visible_error_without_hidden_clamp(qtbot, tmp_path):
    canvas, glass, _official = _canvas(qtbot, tmp_path)
    errors = []
    canvas.validationError.connect(errors.append)
    original = canvas.oil_y
    value = glass.geometry.ellipse.bounds.bottom + 1.0
    assert not canvas.set_truth_y("oil", value, emit=True)
    assert canvas.oil_y == original
    assert errors and "타원 밖" in errors[-1]


def test_zoom_and_fit_do_not_change_canonical_coordinates(qtbot, tmp_path):
    canvas, _glass, _official = _canvas(qtbot, tmp_path)
    original = (canvas.oil_y, canvas.foam_y)
    canvas.zoom_in()
    canvas.zoom_in()
    canvas.zoom_out()
    canvas.fit_to(500, 350)
    canvas.actual_size()
    assert (canvas.oil_y, canvas.foam_y) == original
    assert canvas.scale_factor == 1.0


def test_remove_lines_and_official_toggle_are_independent(qtbot, tmp_path):
    canvas, _glass, _official = _canvas(qtbot, tmp_path)
    canvas.remove_line("oil")
    assert canvas.oil_y is None
    assert canvas.foam_y == 118.0
    canvas.set_official_visible(False)
    assert not canvas._show_official
    canvas.remove_line("foam")
    assert canvas.foam_y is None
