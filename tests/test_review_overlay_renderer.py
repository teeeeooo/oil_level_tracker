from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.review_overlay_renderer import ReviewOverlayRenderer
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import ExclusionZone, InspectionRecipe
from oil_tracker.domain.geometry import Rect
from oil_tracker.domain.review import ReviewOverlayData, ReviewTrackingSample


def _glass():
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.geometry.zero_line_y = 140.0
    glass.geometry.exclusions.append(ExclusionZone("test", Rect(145, 100, 20, 18)))
    return glass


def _overlay(glass, *, valid=True, within=True, oil_y=130.0, foam_y=120.0):
    sample = ReviewTrackingSample(
        "run",
        glass.id,
        10,
        1.0,
        FillState.PARTIAL_VISIBLE,
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


def test_renderer_draws_roi_exclusion_zero_oil_and_foam_with_ellipse_extent():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    glass = _glass()
    rendered = ReviewOverlayRenderer().render(frame, glass, _overlay(glass))
    assert rendered.shape == frame.shape
    assert np.count_nonzero(rendered) > 0
    assert np.count_nonzero(rendered[130, 0:50]) == 0
    assert np.count_nonzero(rendered[130, 120:200]) > 0
    assert np.count_nonzero(rendered[120, 120:200]) > 0
    assert np.count_nonzero(rendered[100:119, 145:166]) > 0


def test_renderer_suppresses_geometry_outside_analysis_range():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    glass = _glass()
    rendered = ReviewOverlayRenderer().render(frame, glass, _overlay(glass, within=False))
    ellipse_top = int(glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y)
    assert np.count_nonzero(rendered[ellipse_top, 150:170]) == 0
    assert np.count_nonzero(rendered) > 0


def test_invalid_sample_changes_roi_highlight():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    glass = _glass()
    normal = ReviewOverlayRenderer().render(frame, glass, _overlay(glass, valid=True))
    invalid = ReviewOverlayRenderer().render(frame, glass, _overlay(glass, valid=False))
    assert not np.array_equal(normal, invalid)


def test_boundary_outside_ellipse_is_not_drawn():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    glass = _glass()
    rendered = ReviewOverlayRenderer().render(
        frame,
        glass,
        _overlay(glass, oil_y=5.0, foam_y=235.0),
    )
    assert np.count_nonzero(rendered[5, :]) == 0
    assert np.count_nonzero(rendered[235, :]) == 0


def test_renderer_does_not_mutate_input_and_is_deterministic():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[30:40, 30:40] = (1, 2, 3)
    original = frame.copy()
    glass = _glass()
    renderer = ReviewOverlayRenderer()
    first = renderer.render(frame, glass, _overlay(glass))
    second = renderer.render(frame, glass, _overlay(glass))
    assert np.array_equal(frame, original)
    assert np.array_equal(first, second)


def test_grayscale_input_is_rendered_at_original_resolution():
    frame = np.zeros((120, 160), dtype=np.uint8)
    glass = InspectionRecipe.default_glass(160, 120, 1)
    glass.geometry.zero_line_y = 70.0
    rendered = ReviewOverlayRenderer().render(
        frame,
        glass,
        _overlay(glass, oil_y=65.0, foam_y=60.0),
    )
    assert rendered.shape == (120, 160, 3)
