from __future__ import annotations

from pathlib import Path

from oil_tracker.application.services.review_query import ReviewQueryModel
from oil_tracker.domain.enums import EventType, FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewBundle, ReviewEvent, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession


def _model(samples, events=(), *, start=1.0, end=5.0, sampling_fps=2.0):
    recipe = InspectionRecipe.empty(320, 240, "review")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.geometry.zero_line_y = 140.0
    glass.detector_settings.minimum_final_confidence = 0.5
    recipe.glasses.append(glass)
    bundle = ReviewBundle(
        root=Path("/bundle"),
        run_id="run",
        recipe=recipe,
        session=AnalysisSession(analysis_start_sec=start, analysis_end_sec=end, sampling_fps=sampling_fps),
        manifest={},
        source_video_path="",
        source_video_candidates=(),
        source_metadata=None,
        analysis_start_sec=start,
        analysis_end_sec=end,
        compressor_start_sec=None,
        glasses=(ReviewGlass(glass.id, glass.name),),
        samples=tuple(samples),
        events=tuple(events),
    )
    return ReviewQueryModel(bundle), glass


def _sample(glass_id, timestamp, frame, *, confidence=0.8, valid=True, flags=(), oil_px=10.0, raw_oil=115.0, foam_px=None, raw_foam=None, order=0):
    return ReviewTrackingSample(
        "run",
        glass_id,
        frame,
        timestamp,
        FillState.PARTIAL_VISIBLE,
        raw_oil_air_level_y=raw_oil,
        smoothed_oil_air_level_px_from_zero=oil_px,
        raw_foam_front_y=raw_foam,
        smoothed_foam_front_px_from_zero=foam_px,
        overall_confidence=confidence,
        is_valid=valid,
        flags=tuple(flags),
        input_order=order,
    )


def test_sample_query_exact_between_and_analysis_range():
    recipe = InspectionRecipe.empty(320, 240)
    glass = InspectionRecipe.default_glass(320, 240, 1)
    samples = [_sample(glass.id, 1.0, 10), _sample(glass.id, 2.0, 20), _sample(glass.id, 4.0, 40)]
    model, actual_glass = _model([sample.__class__(**{**sample.__dict__, "glass_id": glass.id}) for sample in samples])
    # replace generated model glass id so the query data and snapshot agree
    model.bundle.recipe.glasses[0].id = glass.id
    model.bundle.glasses = (ReviewGlass(glass.id, actual_glass.name),)
    assert model.sample_at(glass.id, 2.0).frame_index == 20
    assert model.sample_at(glass.id, 2.9).frame_index == 20
    assert model.sample_at(glass.id, 0.9) is None
    assert model.sample_at(glass.id, 5.1) is None


def test_duplicate_timestamp_is_deterministic_by_frame_and_input_order():
    base = InspectionRecipe.default_glass(320, 240, 1)
    samples = [
        _sample(base.id, 2.0, 20, order=1),
        _sample(base.id, 2.0, 21, order=0),
        _sample(base.id, 2.0, 21, order=3),
    ]
    model, glass = _model([])
    glass.id = base.id
    model = ReviewQueryModel(ReviewBundle(
        root=Path("/bundle"), run_id="run", recipe=model.bundle.recipe,
        session=model.bundle.session, manifest={}, source_video_path="", source_video_candidates=(), source_metadata=None,
        analysis_start_sec=1.0, analysis_end_sec=5.0, compressor_start_sec=None,
        glasses=(ReviewGlass(base.id, glass.name),), samples=tuple(samples), events=()
    ))
    assert model.sample_at(base.id, 2.0).input_order == 3


def test_overlay_restores_oil_and_foam_y_and_uses_raw_fallback():
    model, glass = _model([])
    sample = _sample(glass.id, 2.0, 20, oil_px=12.0, raw_oil=99.0, foam_px=8.0, raw_foam=101.0)
    model = _replace_samples(model, [sample])
    overlay = model.overlay_at(glass.id, 2.0)
    assert overlay.oil_boundary_y == 128.0
    assert overlay.foam_front_y == 132.0
    fallback = _sample(glass.id, 3.0, 30, oil_px=None, raw_oil=119.0, foam_px=None, raw_foam=121.0)
    model = _replace_samples(model, [fallback])
    overlay = model.overlay_at(glass.id, 3.0)
    assert overlay.oil_boundary_y == 119.0
    assert overlay.foam_front_y == 121.0


def test_boundary_outside_ellipse_is_suppressed():
    model, glass = _model([])
    sample = _sample(glass.id, 2.0, 20, oil_px=500.0)
    overlay = _replace_samples(model, [sample]).overlay_at(glass.id, 2.0)
    assert overlay.oil_boundary_y is None
    assert "타원 밖" in overlay.boundary_status


def test_event_previous_next_and_active_duration():
    model, glass = _model([])
    events = [
        ReviewEvent("run", glass.id, EventType.FOAM_START, 2.0, 2.5),
        ReviewEvent("run", glass.id, EventType.FOAM_END, 4.0),
    ]
    model = _replace_events(model, events)
    assert model.previous_event(glass.id, 3.0).event_type == EventType.FOAM_START
    assert model.next_event(glass.id, 3.0).event_type == EventType.FOAM_END
    assert model.active_events(glass.id, 2.25)[0].event_type == EventType.FOAM_START


def test_low_confidence_intervals_group_and_pick_lowest_earliest_representative():
    model, glass = _model([])
    samples = [
        _sample(glass.id, 1.0, 10),
        _sample(glass.id, 2.0, 20, confidence=0.3, valid=False, flags=("DETECTION_LOST",)),
        _sample(glass.id, 2.5, 25, confidence=0.2, flags=("FOGGED_OR_GLARE",)),
        _sample(glass.id, 3.0, 30, confidence=0.2, flags=("REVIEW_REQUIRED",)),
        _sample(glass.id, 4.5, 45, confidence=0.1, flags=("LOW_CONFIDENCE",)),
    ]
    intervals = _replace_samples(model, samples).low_confidence_intervals(glass.id)
    assert len(intervals) == 2
    assert intervals[0].representative_time_sec == 2.5
    assert intervals[0].minimum_confidence == 0.2
    assert "DETECTION_LOST" in intervals[0].reasons
    assert intervals[1].representative_time_sec == 4.5


def test_threshold_invalid_and_foam_flags_are_review_reasons():
    model, glass = _model([])
    samples = [
        _sample(glass.id, 2.0, 20, confidence=0.49),
        _sample(glass.id, 2.5, 25, confidence=0.9, valid=False),
        _sample(glass.id, 3.0, 30, confidence=0.9, flags=("FOAM_REVIEW",)),
    ]
    intervals = _replace_samples(model, samples).low_confidence_intervals(glass.id)
    reasons = {reason for interval in intervals for reason in interval.reasons}
    assert "신뢰도 기준 미달" in reasons
    assert "유효하지 않은 검출" in reasons
    assert "FOAM_REVIEW" in reasons


def _replace_samples(model, samples):
    bundle = model.bundle
    return ReviewQueryModel(ReviewBundle(**{**bundle.__dict__, "samples": tuple(samples)}))


def _replace_events(model, events):
    bundle = model.bundle
    return ReviewQueryModel(ReviewBundle(**{**bundle.__dict__, "events": tuple(events)}))
