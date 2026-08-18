from __future__ import annotations

from pathlib import Path

from oil_tracker.application.services.review_graph import build_review_graph_model
from oil_tracker.application.services.review_query import ReviewQueryModel
from oil_tracker.domain.enums import EventType, FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import (
    ReviewBundle,
    ReviewEvent,
    ReviewFilter,
    ReviewGlass,
    ReviewTrackingSample,
)
from oil_tracker.domain.session import AnalysisSession
from oil_tracker.domain.retrospective import (
    RetrospectiveInterpretation,
    RetrospectiveStatus,
)


def _sample(glass_id, timestamp, frame, **values):
    defaults = dict(
        run_id="run",
        glass_id=glass_id,
        frame_index=frame,
        timestamp_sec=timestamp,
        fill_state=FillState.PARTIAL_VISIBLE,
        overall_confidence=0.8,
        is_valid=True,
    )
    defaults.update(values)
    return ReviewTrackingSample(**defaults)


def _bundle(samples, events=(), *, mm_per_pixel=None):
    recipe = InspectionRecipe.empty(320, 240, "graph")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.mm_per_pixel = mm_per_pixel
    glass.detector_settings.minimum_final_confidence = 0.5
    recipe.glasses.append(glass)
    bundle = ReviewBundle(
        root=Path("/bundle"),
        run_id="run",
        recipe=recipe,
        session=AnalysisSession(analysis_start_sec=1.0, analysis_end_sec=4.0, sampling_fps=2.0),
        manifest={},
        source_video_path="",
        source_video_candidates=(),
        source_metadata=None,
        analysis_start_sec=1.0,
        analysis_end_sec=4.0,
        compressor_start_sec=1.5,
        glasses=(ReviewGlass(glass.id, glass.name),),
        samples=tuple(samples),
        events=tuple(events),
    )
    return bundle, glass


def test_px_graph_prefers_smoothed_then_raw_and_keeps_gap():
    bundle, glass = _bundle([])
    bundle.samples = (
        _sample(glass.id, 1.0, 10, smoothed_oil_air_level_px_from_zero=3.0, raw_oil_air_level_px_from_zero=8.0),
        _sample(glass.id, 2.0, 20, raw_oil_air_level_px_from_zero=5.0),
        _sample(glass.id, 3.0, 30),
    )
    model = build_review_graph_model(bundle, glass.id)
    assert model.unit == "px"
    assert model.y_axis_label == "기준선 대비 높이 (px)"
    assert [point.value for point in model.oil_air.points] == [3.0, 5.0, None]
    assert model.axis_lower is not None and model.axis_upper is not None
    assert model.axis_lower < 0 < model.axis_upper
    assert model.analysis_top_boundary_value is not None
    assert model.analysis_bottom_boundary_value is not None


def test_mm_graph_is_used_only_when_usable_mm_value_exists():
    bundle, glass = _bundle([], mm_per_pixel=0.1)
    bundle.samples = (
        _sample(glass.id, 1.0, 10, smoothed_oil_air_level_mm_from_zero=1.2, raw_oil_air_level_mm_from_zero=2.0),
    )
    model = build_review_graph_model(bundle, glass.id)
    assert model.unit == "mm"
    assert model.oil_air.points[0].value == 1.2


def test_mm_calibration_without_mm_values_falls_back_to_px():
    bundle, glass = _bundle([], mm_per_pixel=0.1)
    bundle.samples = (_sample(glass.id, 1.0, 10, raw_oil_air_level_px_from_zero=4.0),)
    assert build_review_graph_model(bundle, glass.id).unit == "px"


def test_foam_series_presence_is_data_driven():
    bundle, glass = _bundle([])
    bundle.samples = (_sample(glass.id, 1.0, 10),)
    assert not build_review_graph_model(bundle, glass.id).foam_front.has_values
    bundle.samples = (_sample(glass.id, 1.0, 10, raw_foam_front_px_from_zero=7.0),)
    assert build_review_graph_model(bundle, glass.id).foam_front.has_values


def test_oil_and_foam_graph_points_use_independent_validity():
    bundle, glass = _bundle([])
    bundle.samples = (
        _sample(
            glass.id,
            1.0,
            10,
            raw_oil_air_level_px_from_zero=4.0,
            raw_foam_front_px_from_zero=7.0,
            is_valid=False,
            oil_is_valid=False,
            foam_is_valid=True,
        ),
    )

    model = build_review_graph_model(bundle, glass.id)

    assert not model.oil_air.points[0].is_valid
    assert model.foam_front.points[0].is_valid


def test_graph_excludes_samples_outside_analysis_range_and_sorts_deterministically():
    bundle, glass = _bundle([])
    bundle.samples = (
        _sample(glass.id, 4.5, 45, raw_oil_air_level_px_from_zero=9.0),
        _sample(glass.id, 2.0, 21, input_order=2, raw_oil_air_level_px_from_zero=2.0),
        _sample(glass.id, 0.5, 5, raw_oil_air_level_px_from_zero=1.0),
        _sample(glass.id, 2.0, 20, input_order=1, raw_oil_air_level_px_from_zero=3.0),
    )
    model = build_review_graph_model(bundle, glass.id)
    assert [(p.timestamp_sec, p.value) for p in model.oil_air.points] == [(2.0, 3.0), (2.0, 2.0)]


def test_event_compressor_analysis_range_and_cursor_are_present():
    bundle, glass = _bundle([])
    bundle.samples = (_sample(glass.id, 1.0, 10),)
    bundle.events = (ReviewEvent("run", glass.id, EventType.FOAM_START, 2.0, 2.5),)
    model = build_review_graph_model(bundle, glass.id, cursor_timestamp_sec=99.0)
    assert model.analysis_start_sec == 1.0
    assert model.analysis_end_sec == 4.0
    assert model.compressor_start_sec == 1.5
    assert model.cursor_timestamp_sec == 4.0
    assert model.event_markers[0].label == "거품 발생"


def test_filter_controls_graph_highlights_without_hiding_events():
    bundle, glass = _bundle([])
    bundle.samples = (
        _sample(glass.id, 2.0, 20, overall_confidence=0.2, is_valid=False, flags=("FOAM_REVIEW",)),
    )
    bundle.events = (ReviewEvent("run", glass.id, EventType.FOAM_START, 2.0),)
    query = ReviewQueryModel(bundle)
    invalid = build_review_graph_model(bundle, glass.id, ReviewFilter.INVALID, query=query)
    lost = build_review_graph_model(bundle, glass.id, ReviewFilter.DETECTION_LOST, query=query)
    assert len(invalid.highlights) == 1
    assert len(lost.highlights) == 0
    assert len(lost.event_markers) == 1


def test_graph_builder_does_not_mutate_bundle_samples():
    bundle, glass = _bundle([])
    original = (_sample(glass.id, 2.0, 20, raw_oil_air_level_px_from_zero=2.0),)
    bundle.samples = original
    build_review_graph_model(bundle, glass.id)
    assert bundle.samples is original


def test_graph_model_exposes_confirmed_initial_state_hold_without_oil_values():
    bundle, glass = _bundle([])
    bundle.samples = (
        _sample(
            glass.id,
            1.0,
            10,
            fill_state=FillState.UNKNOWN_REVIEW,
            is_valid=False,
        ),
    )
    bundle.retrospective_interpretations = (
        RetrospectiveInterpretation(
            glass_id=glass.id,
            status=RetrospectiveStatus.ACCEPTED,
            confirmed_prior=InitialObservationState.FULL_NO_INTERFACE,
            interpreted_state=FillState.FULL_NO_INTERFACE,
            start_time_sec=1.0,
            end_time_sec=4.0,
            provenance="confirmed_initial_state_hold_v1",
        ),
    )

    model = build_review_graph_model(bundle, glass.id)

    assert not model.oil_air.has_values
    assert model.assumed_initial_state == "FULL_NO_INTERFACE"
    assert model.assumed_state_start_sec == 1.0
    assert model.assumed_state_end_sec == 4.0
