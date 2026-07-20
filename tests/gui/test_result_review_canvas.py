from __future__ import annotations

import cv2
import numpy as np

from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewOverlayData, ReviewTrackingSample
from oil_tracker.ui.widgets.result_review_canvas import ResultReviewCanvas


def _glass():
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.geometry.zero_line_y = 140.0
    return glass


def _overlay(glass, *, valid=True, within=True, oil_y=130.0, foam_y=120.0):
    sample = ReviewTrackingSample(
        "run", glass.id, 10, 1.0, FillState.PARTIAL_VISIBLE,
        smoothed_oil_air_level_px_from_zero=10.0,
        smoothed_foam_front_px_from_zero=20.0,
        overall_confidence=0.8 if valid else 0.2,
        is_valid=valid,
        flags=() if valid else ("LOW_CONFIDENCE",),
    )
    return ReviewOverlayData(
        glass.id,
        1.0,
        sample if within else None,
        oil_y if within else None,
        foam_y if within else None,
        within,
        () if valid else ("LOW_CONFIDENCE",),
    )


def test_renderer_draws_roi_zero_oil_and_foam_with_ellipse_extent():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    glass = _glass()
    rendered = ReviewOverlayRenderer().render(frame, glass, _overlay(glass))
    assert rendered.shape == frame.shape
    assert np.count_nonzero(rendered) > 0
    assert np.count_nonzero(rendered[130, 0:50]) == 0
    assert np.count_nonzero(rendered[130, 120:200]) > 0
    assert np.count_nonzero(rendered[120, 120:200]) > 0


def test_renderer_suppresses_geometry_outside_analysis_range():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    glass = _glass()
    rendered = ReviewOverlayRenderer().render(frame, glass, _overlay(glass, within=False))
    ellipse_top = int(glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y)
    assert np.count_nonzero(rendered[ellipse_top, 150:170]) == 0


def test_invalid_sample_changes_roi_highlight():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    glass = _glass()
    normal = ReviewOverlayRenderer().render(frame, glass, _overlay(glass, valid=True))
    invalid = ReviewOverlayRenderer().render(frame, glass, _overlay(glass, valid=False))
    assert not np.array_equal(normal, invalid)


def test_canvas_is_read_only_and_saves_original_resolution_unicode_png(qtbot, tmp_path):
    canvas = ResultReviewCanvas()
    qtbot.addWidget(canvas)
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    glass = _glass()
    canvas.set_review_frame(frame, glass, _overlay(glass))
    assert not hasattr(canvas, "geometryChanged")
    assert not hasattr(canvas, "zeroLineChanged")
    destination = canvas.save_png(tmp_path / "검토 장면.png")
    decoded = cv2.imdecode(np.fromfile(str(destination), dtype=np.uint8), cv2.IMREAD_COLOR)
    assert decoded.shape[:2] == (240, 320)
