from __future__ import annotations

from oil_tracker.application.services.event_presentation import event_type_label
from oil_tracker.application.services.graph_axis import graph_axis_range_for_glass
from oil_tracker.application.services.review_query import ReviewQueryModel
from oil_tracker.domain.review import (
    ReviewBundle,
    ReviewFilter,
    ReviewGraphDebugMarker,
    ReviewGraphEventMarker,
    ReviewGraphHighlight,
    ReviewGraphModel,
    ReviewGraphPoint,
    ReviewGraphSeries,
    ReviewTrackingSample,
)


def build_review_graph_model(
    bundle: ReviewBundle,
    glass_id: str,
    review_filter: ReviewFilter = ReviewFilter.ALL,
    cursor_timestamp_sec: float = 0.0,
    query: ReviewQueryModel | None = None,
    debug_summaries=(),
    selected_debug_record_id: str = "",
) -> ReviewGraphModel:
    query = query or ReviewQueryModel(bundle)
    glass = bundle.glass_config(glass_id)
    if glass is None:
        raise KeyError(glass_id)
    samples = tuple(
        sample
        for sample in query.samples_for_glass(glass_id)
        if bundle.analysis_start_sec <= sample.timestamp_sec <= bundle.analysis_end_sec
    )
    use_mm = bool(glass.mm_per_pixel and glass.mm_per_pixel > 0) and any(
        _oil_value(sample, "mm") is not None or _foam_value(sample, "mm") is not None
        for sample in samples
    )
    unit = "mm" if use_mm else "px"
    oil_points = tuple(
        ReviewGraphPoint(
            timestamp_sec=sample.timestamp_sec,
            value=_oil_value(sample, unit),
            is_valid=sample.is_valid,
            confidence=sample.overall_confidence,
        )
        for sample in samples
    )
    foam_points = tuple(
        ReviewGraphPoint(
            timestamp_sec=sample.timestamp_sec,
            value=_foam_value(sample, unit),
            is_valid=sample.is_valid,
            confidence=sample.overall_confidence,
        )
        for sample in samples
    )
    axis_range = graph_axis_range_for_glass(
        glass,
        unit=unit,
        observed_values=(
            *(point.value for point in oil_points),
            *(point.value for point in foam_points),
        ),
    )
    events = tuple(
        ReviewGraphEventMarker(
            timestamp_sec=event.start_time_sec,
            end_time_sec=event.end_time_sec,
            label=event_type_label(event.event_type),
        )
        for event in query.events_for_glass(glass_id)
        if bundle.analysis_start_sec <= event.start_time_sec <= bundle.analysis_end_sec
    )
    highlights = tuple(
        ReviewGraphHighlight(
            start_time_sec=interval.start_time_sec,
            end_time_sec=interval.end_time_sec,
            categories=interval.categories,
            reasons=interval.reasons,
        )
        for interval in query.filtered_intervals(glass_id, review_filter)
    )
    debug_markers = tuple(
        ReviewGraphDebugMarker(
            timestamp_sec=summary.timestamp_sec,
            reasons=tuple(summary.capture_reasons),
            selected=summary.record_id == selected_debug_record_id,
        )
        for summary in debug_summaries
        if summary.glass_id == glass_id and bundle.analysis_start_sec <= summary.timestamp_sec <= bundle.analysis_end_sec
    )
    retrospective = bundle.retrospective_for_glass(glass_id)
    initial_hold = bool(
        retrospective is not None
        and retrospective.accepted
        and retrospective.provenance == "confirmed_initial_state_hold_v1"
    )
    return ReviewGraphModel(
        glass_id=glass_id,
        glass_name=glass.name,
        unit=unit,
        y_axis_label=f"기준선 대비 높이 ({unit})",
        oil_air=ReviewGraphSeries("유면", oil_points),
        foam_front=ReviewGraphSeries("거품 경계", foam_points),
        event_markers=events,
        highlights=highlights,
        analysis_start_sec=bundle.analysis_start_sec,
        analysis_end_sec=bundle.analysis_end_sec,
        compressor_start_sec=bundle.compressor_start_sec,
        cursor_timestamp_sec=_clamp(cursor_timestamp_sec, bundle.analysis_start_sec, bundle.analysis_end_sec),
        debug_markers=debug_markers,
        axis_lower=axis_range.lower,
        axis_upper=axis_range.upper,
        analysis_top_boundary_value=axis_range.analysis_top_boundary,
        analysis_bottom_boundary_value=axis_range.analysis_bottom_boundary,
        range_source=axis_range.source,
        range_reason=axis_range.reason,
        assumed_initial_state=(
            retrospective.interpreted_state.value
            if initial_hold and retrospective.interpreted_state is not None
            else ""
        ),
        assumed_state_start_sec=(
            retrospective.start_time_sec if initial_hold else None
        ),
        assumed_state_end_sec=(
            retrospective.end_time_sec if initial_hold else None
        ),
    )


def _oil_value(sample: ReviewTrackingSample, unit: str) -> float | None:
    if unit == "mm":
        return _first(sample.smoothed_oil_air_level_mm_from_zero, sample.raw_oil_air_level_mm_from_zero)
    return _first(sample.smoothed_oil_air_level_px_from_zero, sample.raw_oil_air_level_px_from_zero)


def _foam_value(sample: ReviewTrackingSample, unit: str) -> float | None:
    if unit == "mm":
        return _first(sample.smoothed_foam_front_mm_from_zero, sample.raw_foam_front_mm_from_zero)
    return _first(sample.smoothed_foam_front_px_from_zero, sample.raw_foam_front_px_from_zero)


def _first(preferred: float | None, fallback: float | None) -> float | None:
    return preferred if preferred is not None else fallback


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, float(value)))
