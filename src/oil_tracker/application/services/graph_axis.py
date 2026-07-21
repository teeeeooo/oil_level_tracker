from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from oil_tracker.domain.recipe import GlassInspectionConfig


@dataclass(frozen=True)
class GraphAxisRange:
    unit: str
    lower: float | None
    upper: float | None
    analysis_top_boundary: float | None
    analysis_bottom_boundary: float | None
    source: str
    reason: str = ""

    @property
    def available(self) -> bool:
        return (
            self.lower is not None
            and self.upper is not None
            and math.isfinite(self.lower)
            and math.isfinite(self.upper)
            and self.lower < self.upper
        )


def graph_axis_range_for_glass(
    glass: GlassInspectionConfig,
    *,
    unit: str = "px",
    observed_values: Iterable[float | None] = (),
    padding_ratio: float = 0.05,
) -> GraphAxisRange:
    if unit not in {"px", "mm"}:
        raise ValueError(f"Unsupported graph axis unit: {unit}")
    reason = _geometry_unavailable_reason(glass, unit)
    if reason:
        return _fallback_range(unit, observed_values, reason, padding_ratio)

    geometry = glass.geometry
    ellipse = geometry.ellipse
    effective_radius_y = ellipse.radius_y * (1.0 - geometry.margin_ratio)
    analysis_top_y = ellipse.center_y - effective_radius_y
    analysis_bottom_y = ellipse.center_y + effective_radius_y
    top_value = float(geometry.zero_line_y) - analysis_top_y
    bottom_value = float(geometry.zero_line_y) - analysis_bottom_y
    scale = float(glass.mm_per_pixel) if unit == "mm" else 1.0
    top_value *= scale
    bottom_value *= scale
    lower = min(top_value, bottom_value, 0.0)
    upper = max(top_value, bottom_value, 0.0)
    lower, upper = _with_padding(lower, upper, unit, scale, padding_ratio)
    return GraphAxisRange(
        unit=unit,
        lower=lower,
        upper=upper,
        analysis_top_boundary=top_value,
        analysis_bottom_boundary=bottom_value,
        source="analysis_geometry",
    )


def combined_graph_axis_range(
    ranges: Iterable[GraphAxisRange],
    *,
    unit: str = "px",
    padding_ratio: float = 0.05,
) -> GraphAxisRange:
    available = [item for item in ranges if item.available and item.unit == unit]
    if not available:
        reasons = tuple(item.reason for item in ranges if item.reason)
        return GraphAxisRange(
            unit=unit,
            lower=None,
            upper=None,
            analysis_top_boundary=None,
            analysis_bottom_boundary=None,
            source="unavailable",
            reason="; ".join(dict.fromkeys(reasons)) or "No compatible Glass axis range is available.",
        )
    top_values = [item.analysis_top_boundary for item in available if item.analysis_top_boundary is not None]
    bottom_values = [
        item.analysis_bottom_boundary
        for item in available
        if item.analysis_bottom_boundary is not None
    ]
    raw_lower = min(
        [0.0]
        + top_values
        + bottom_values
    )
    raw_upper = max(
        [0.0]
        + top_values
        + bottom_values
    )
    lower, upper = _with_padding(raw_lower, raw_upper, unit, 1.0, padding_ratio)
    return GraphAxisRange(
        unit=unit,
        lower=lower,
        upper=upper,
        analysis_top_boundary=max(top_values) if top_values else None,
        analysis_bottom_boundary=min(bottom_values) if bottom_values else None,
        source="combined_analysis_geometry",
    )


def _geometry_unavailable_reason(glass: GlassInspectionConfig, unit: str) -> str:
    geometry = glass.geometry
    ellipse = geometry.ellipse
    values = (
        ellipse.center_y,
        ellipse.radius_y,
        geometry.margin_ratio,
    )
    if not all(math.isfinite(float(value)) for value in values):
        return "Glass analysis geometry contains a non-finite value."
    if ellipse.radius_y <= 0:
        return "Glass ellipse radius_y must be positive."
    if geometry.margin_ratio < 0 or geometry.margin_ratio >= 1:
        return "Glass margin_ratio must be in the range [0, 1)."
    if geometry.zero_line_y is None or not math.isfinite(float(geometry.zero_line_y)):
        return "Glass zero line is unavailable."
    if unit == "mm":
        if glass.mm_per_pixel is None or not math.isfinite(float(glass.mm_per_pixel)):
            return "Glass mm_per_pixel is unavailable."
        if glass.mm_per_pixel <= 0:
            return "Glass mm_per_pixel must be positive."
    return ""


def _fallback_range(
    unit: str,
    observed_values: Iterable[float | None],
    reason: str,
    padding_ratio: float,
) -> GraphAxisRange:
    finite = sorted(
        float(value)
        for value in observed_values
        if value is not None and math.isfinite(float(value))
    )
    if not finite:
        return GraphAxisRange(
            unit=unit,
            lower=None,
            upper=None,
            analysis_top_boundary=None,
            analysis_bottom_boundary=None,
            source="unavailable",
            reason=reason,
        )
    lower, upper = _with_padding(min(finite[0], 0.0), max(finite[-1], 0.0), unit, 1.0, padding_ratio)
    return GraphAxisRange(
        unit=unit,
        lower=lower,
        upper=upper,
        analysis_top_boundary=None,
        analysis_bottom_boundary=None,
        source="observed_fallback",
        reason=reason,
    )


def _with_padding(
    lower: float,
    upper: float,
    unit: str,
    scale: float,
    padding_ratio: float,
) -> tuple[float, float]:
    span = upper - lower
    minimum_padding = 1.0 if unit == "px" else max(abs(scale), 0.1)
    padding = max(span * max(0.0, padding_ratio), minimum_padding)
    padded_lower = lower - padding
    padded_upper = upper + padding
    if not padded_lower < padded_upper:
        padded_lower, padded_upper = -minimum_padding, minimum_padding
    return padded_lower, padded_upper
