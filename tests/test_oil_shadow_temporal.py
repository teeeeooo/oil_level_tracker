from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from enum import Enum

import numpy as np

from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_temporal import (
    GlassTemporalSnapshot,
    GlassTemporalState,
    OilShadowTemporalModel,
)
from oil_tracker.adapters.vision.oil_shadow_types import (
    AbsenceStabilityMode,
    BoundaryAcceptanceMode,
    BoundaryAcceptedDecision,
    EvidenceUnavailableDecision,
    NoInterfaceOutcome,
    OilShadowBounds,
    PipelineFailureOutcome,
    ReacquisitionPendingDecision,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceObservation,
    ShadowUnavailableObservation,
    SmoothingAction,
    stable_digest,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _pipeline_result(image):
    mask = np.full(image.shape[:2], 255, dtype=np.uint8)
    return OilHypothesisPipeline().run(
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
    boundary = _pipeline_result(step)
    dark = _pipeline_result(np.full((80, 100), 75, dtype=np.uint8))
    assert not isinstance(boundary, PipelineFailureOutcome)
    assert boundary.hypotheses
    assert isinstance(dark, NoInterfaceOutcome)
    return boundary.hypotheses[0], dark.evidence


def _boundary(y: float):
    hypothesis, _evidence = _seeds()
    identity = stable_digest("temporal-boundary", (("y", y),))
    hypothesis = replace(
        hypothesis,
        identity=identity,
        representative_local_y=y,
        representative_source_y=y,
        minimum_local_y=y - 1.0,
        maximum_local_y=y + 1.0,
        boundary_likelihood=0.90,
        artifact_likelihood=0.08,
        ambiguity_likelihood=0.12,
    )
    return ShadowBoundaryObservation(hypothesis=hypothesis)


def _no_interface():
    _hypothesis, evidence = _seeds()
    return ShadowNoInterfaceObservation(evidence=evidence)


def _ambiguous(y=40.0):
    return ShadowAmbiguousObservation(
        hypothesis_ids=(stable_digest("ambiguous", (("y", y),)),),
        boundary_likelihood=0.45,
        artifact_likelihood=0.42,
        ambiguity_likelihood=0.80,
        no_interface_likelihood=0.25,
        visibility=0.90,
        projected_source_y=y,
        reason="competing evidence",
    )


def _unavailable():
    return ShadowUnavailableObservation(visibility=0.10, reason="insufficient support")


def _snapshot(state: GlassTemporalState | None = None, generation: int = 0):
    state = state or GlassTemporalState("g")
    return GlassTemporalSnapshot("g", generation, state.version, state)


def _advance(model, snapshot, observation):
    provisional = model.evaluate(snapshot, observation)
    return provisional, _snapshot(provisional.next_state, snapshot.reset_generation)


def _assert_no_raster(value):
    if isinstance(value, np.ndarray):
        raise AssertionError("temporal state retained a raster")
    if isinstance(value, (str, int, float, bool, type(None), Enum)):
        return
    if isinstance(value, tuple):
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


def test_pure_evaluation_is_deterministic_and_has_no_live_state_authority():
    model = OilShadowTemporalModel()
    snapshot = _snapshot()
    first = model.evaluate(snapshot, _boundary(20.0))
    second = model.evaluate(snapshot, _boundary(20.0))
    assert first == second
    assert first.next_state is not snapshot.state
    assert isinstance(first.decision, BoundaryAcceptedDecision)
    assert first.decision.acceptance_mode is BoundaryAcceptanceMode.INITIAL
    assert not hasattr(model, "commit")
    assert not hasattr(model, "reset")
    assert not hasattr(model, "snapshot")


def test_successful_transition_policy_is_preserved_by_pure_model():
    model = OilShadowTemporalModel()
    snapshot = _snapshot()
    initial, snapshot = _advance(model, snapshot, _boundary(20.0))
    continuous, snapshot = _advance(model, snapshot, _boundary(40.0))
    pending, snapshot = _advance(model, snapshot, _boundary(100.0))
    reacquired, snapshot = _advance(model, snapshot, _boundary(102.0))
    assert isinstance(initial.decision, BoundaryAcceptedDecision)
    assert isinstance(continuous.decision, BoundaryAcceptedDecision)
    assert isinstance(pending.decision, ReacquisitionPendingDecision)
    assert isinstance(reacquired.decision, BoundaryAcceptedDecision)
    assert reacquired.decision.acceptance_mode is BoundaryAcceptanceMode.REACQUIRED
    assert reacquired.decision.smoothing_action is SmoothingAction.CLEAR_BEFORE_ACCEPT
    assert reacquired.decision.accepted_source_y == 102.0


def test_unavailable_and_no_interface_counters_remain_bounded():
    bounds = OilShadowBounds(unavailable_clear_frames=3, no_interface_clear_frames=2)
    model = OilShadowTemporalModel(bounds)
    snapshot = _snapshot()
    _accepted, snapshot = _advance(model, snapshot, _boundary(20.0))
    first, snapshot = _advance(model, snapshot, _unavailable())
    second, snapshot = _advance(model, snapshot, _unavailable())
    third, snapshot = _advance(model, snapshot, _unavailable())
    assert isinstance(first.decision, EvidenceUnavailableDecision)
    assert first.decision.stability_mode is AbsenceStabilityMode.PENDING
    assert second.decision.stability_mode is AbsenceStabilityMode.PENDING
    assert third.decision.stability_mode is AbsenceStabilityMode.STABLE
    assert third.decision.smoothing_action is SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE
    for _ in range(10):
        stable, snapshot = _advance(model, snapshot, _no_interface())
    assert stable.decision.stability_mode is AbsenceStabilityMode.STABLE
    assert snapshot.state.no_interface_count == bounds.no_interface_clear_frames


def test_temporal_resources_and_state_retain_no_raster():
    bounds = OilShadowBounds(temporal_beam_width=3, temporal_history_window=4)
    model = OilShadowTemporalModel(bounds)
    snapshot = _snapshot()
    sequence = (_boundary(20.0), _ambiguous(22.0), _boundary(24.0), _unavailable(), _no_interface())
    for index in range(30):
        provisional, snapshot = _advance(model, snapshot, sequence[index % len(sequence)])
        assert provisional.resources.beam_count <= bounds.temporal_beam_width
        assert provisional.resources.history_length <= bounds.temporal_history_window
        assert provisional.resources.retained_scalar_count <= model.retained_scalar_limit
    _assert_no_raster(snapshot.state)
