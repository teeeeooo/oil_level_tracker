from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from enum import Enum

import numpy as np

from oil_tracker.adapters.vision.oil_shadow_pipeline import OilShadowPipeline
from oil_tracker.adapters.vision.oil_shadow_temporal import OilShadowTemporalTracker
from oil_tracker.adapters.vision.oil_shadow_types import (
    OilShadowBounds,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceObservation,
    ShadowObservationKind,
    ShadowTemporalStatus,
    ShadowUnavailableObservation,
    stable_digest,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _pipeline_result(image):
    mask = np.full(image.shape[:2], 255, dtype=np.uint8)
    return OilShadowPipeline().run(
        glass_id="seed",
        pre=preprocess(image, mask, DetectorSettings()),
        effective_mask=mask,
        ellipse_mask=mask,
        exclusion_mask=np.zeros_like(mask),
        static_artifact_map=None,
        crop_origin_y=0.0,
    )


def _seeds():
    step = np.full((80, 100), 180, dtype=np.uint8)
    step[40:] = 60
    step[39:42] = 230
    boundary_result = _pipeline_result(step)
    hypothesis = boundary_result.hypotheses[0]
    dark_result = _pipeline_result(np.full((80, 100), 75, dtype=np.uint8))
    no_interface = dark_result.current_observation.evidence
    return hypothesis, no_interface


def _boundary(y: float):
    hypothesis, no_interface = _seeds()
    identity = stable_digest("temporal-boundary", (("y", y),))
    local = y
    hypothesis = replace(
        hypothesis,
        identity=identity,
        representative_local_y=local,
        representative_source_y=y,
        minimum_local_y=local - 1.0,
        maximum_local_y=local + 1.0,
        boundary_likelihood=0.90,
        artifact_likelihood=0.08,
        ambiguity_likelihood=0.12,
    )
    return ShadowBoundaryObservation(
        ShadowObservationKind.BOUNDARY,
        hypothesis,
        no_interface,
    )


def _no_interface():
    _hypothesis, evidence = _seeds()
    return ShadowNoInterfaceObservation(ShadowObservationKind.NO_INTERFACE, evidence)


def _ambiguous(y=40.0):
    return ShadowAmbiguousObservation(
        ShadowObservationKind.AMBIGUOUS,
        (stable_digest("ambiguous", (("y", y),)),),
        0.45,
        0.42,
        0.80,
        0.25,
        0.90,
        y,
        "competing evidence",
    )


def _unavailable():
    return ShadowUnavailableObservation(
        ShadowObservationKind.UNAVAILABLE,
        0.10,
        "insufficient support",
    )


def _assert_no_raster(value):
    if isinstance(value, np.ndarray):
        raise AssertionError("temporal state retained a raster")
    if isinstance(value, (str, int, float, bool, type(None), Enum)):
        return
    if isinstance(value, (tuple, list)):
        for item in value:
            _assert_no_raster(item)
        return
    if isinstance(value, dict):
        for item in value.values():
            _assert_no_raster(item)
        return
    if is_dataclass(value):
        for field in fields(value):
            _assert_no_raster(getattr(value, field.name))
        return
    raise AssertionError(type(value))


def test_typed_transitions_dropout_and_stable_clear_instruction():
    tracker = OilShadowTemporalTracker()
    accepted = tracker.evaluate("g", _boundary(20.0))
    ambiguous = tracker.evaluate("g", _ambiguous())
    unavailable = tracker.evaluate("g", _unavailable())
    first_no_interface = tracker.evaluate("g", _no_interface())
    stable_no_interface = tracker.evaluate("g", _no_interface())
    assert accepted.status is ShadowTemporalStatus.BOUNDARY_ACCEPTED
    assert ambiguous.status is ShadowTemporalStatus.AMBIGUOUS
    assert unavailable.status is ShadowTemporalStatus.UNAVAILABLE
    assert first_no_interface.status is ShadowTemporalStatus.NO_INTERFACE_ACCEPTED
    assert not first_no_interface.clear_smoothing
    assert stable_no_interface.clear_smoothing


def test_rapid_motion_and_bounded_large_jump_reacquisition():
    tracker = OilShadowTemporalTracker()
    rapid = [tracker.evaluate("rapid", _boundary(y)) for y in (20.0, 40.0, 60.0)]
    assert all(item.status is ShadowTemporalStatus.BOUNDARY_ACCEPTED for item in rapid)

    tracker = OilShadowTemporalTracker()
    tracker.evaluate("jump", _boundary(20.0))
    pending = tracker.evaluate("jump", _boundary(80.0))
    reacquired = tracker.evaluate("jump", _boundary(82.0))
    assert pending.status is ShadowTemporalStatus.REACQUISITION_PENDING
    assert pending.reacquisition_count == 1
    assert reacquired.status is ShadowTemporalStatus.BOUNDARY_ACCEPTED
    assert reacquired.clear_smoothing
    assert reacquired.projected_source_y == 82.0


def test_unavailable_stale_clear_is_bounded():
    bounds = OilShadowBounds(unavailable_clear_frames=3)
    tracker = OilShadowTemporalTracker(bounds)
    tracker.evaluate("g", _boundary(20.0))
    decisions = [tracker.evaluate("g", _unavailable()) for _ in range(3)]
    assert not decisions[0].clear_smoothing
    assert decisions[-1].clear_smoothing


def test_beam_history_scalar_counts_and_no_raster_retention_are_bounded():
    bounds = OilShadowBounds(temporal_beam_width=3, temporal_history_window=4)
    tracker = OilShadowTemporalTracker(bounds)
    sequence = (_boundary(20.0), _ambiguous(22.0), _boundary(24.0), _unavailable(), _no_interface())
    for index in range(30):
        decision = tracker.evaluate("g", sequence[index % len(sequence)])
        assert decision.beam_count <= bounds.temporal_beam_width
        assert decision.history_length <= bounds.temporal_history_window
        assert decision.retained_scalar_count <= tracker.retained_scalar_limit
    _assert_no_raster(tracker._states)


def test_glass_isolation_reset_one_reset_all_and_repeated_determinism():
    first = OilShadowTemporalTracker()
    second = OilShadowTemporalTracker()
    sequence = (_boundary(20.0), _boundary(40.0), _ambiguous(), _boundary(42.0), _no_interface())
    decisions_a = [first.evaluate("a", item) for item in sequence]
    decisions_b = [second.evaluate("a", item) for item in sequence]
    assert decisions_a == decisions_b

    first.evaluate("b", _boundary(90.0))
    assert first.state_count == 2
    first.reset("a")
    assert first.state_count == 1
    assert "b" in first._states
    first.reset()
    assert first.state_count == 0
