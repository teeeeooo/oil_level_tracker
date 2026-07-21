from __future__ import annotations

import math

from oil_tracker.application.services.graph_axis import (
    combined_graph_axis_range,
    graph_axis_range_for_glass,
)
from oil_tracker.domain.geometry import EllipseGeometry, ExclusionZone, GlassGeometry, Rect
from oil_tracker.domain.recipe import GlassInspectionConfig


def _glass(*, margin: float = 0.0, zero: float | None = 100.0, scale: float | None = None):
    return GlassInspectionConfig(
        id="glass-1",
        name="Glass 1",
        geometry=GlassGeometry(
            ellipse=EllipseGeometry(80.0, 100.0, 40.0, 50.0),
            zero_line_y=zero,
            margin_ratio=margin,
            exclusions=[ExclusionZone("x", Rect(0, 70, 200, 20))],
        ),
        mm_per_pixel=scale,
    )


def test_full_inner_ellipse_range_margin_zero_and_zero_inclusion() -> None:
    axis = graph_axis_range_for_glass(_glass(), unit="px")
    assert axis.source == "analysis_geometry"
    assert axis.analysis_top_boundary == 50.0
    assert axis.analysis_bottom_boundary == -50.0
    assert axis.lower < -50.0
    assert axis.upper > 50.0
    assert axis.lower < 0 < axis.upper


def test_margin_and_mm_scale_use_same_canonical_geometry() -> None:
    axis = graph_axis_range_for_glass(_glass(margin=0.2, scale=0.5), unit="mm")
    assert math.isclose(axis.analysis_top_boundary, 20.0)
    assert math.isclose(axis.analysis_bottom_boundary, -20.0)
    assert axis.lower < -20.0
    assert axis.upper > 20.0


def test_exclusion_does_not_shrink_vertical_analysis_range() -> None:
    without = _glass()
    without.geometry.exclusions.clear()
    left = graph_axis_range_for_glass(without)
    right = graph_axis_range_for_glass(_glass())
    assert left.analysis_top_boundary == right.analysis_top_boundary
    assert left.analysis_bottom_boundary == right.analysis_bottom_boundary


def test_missing_zero_uses_explicit_observed_fallback_without_fabricating_values() -> None:
    fallback = graph_axis_range_for_glass(
        _glass(zero=None),
        observed_values=(None, -3.0, 7.0),
    )
    unavailable = graph_axis_range_for_glass(_glass(zero=None), observed_values=(None,))
    assert fallback.source == "observed_fallback"
    assert fallback.reason
    assert fallback.lower < -3.0
    assert fallback.upper > 7.0
    assert unavailable.source == "unavailable"
    assert unavailable.lower is None
    assert unavailable.upper is None


def test_combined_range_is_union_of_all_glass_boundaries() -> None:
    first = graph_axis_range_for_glass(_glass())
    second_glass = _glass(zero=130.0)
    second = graph_axis_range_for_glass(second_glass)
    combined = combined_graph_axis_range((first, second))
    assert combined.source == "combined_analysis_geometry"
    assert combined.analysis_top_boundary == 80.0
    assert combined.analysis_bottom_boundary == -50.0
    assert combined.lower < -50.0
    assert combined.upper > 80.0
