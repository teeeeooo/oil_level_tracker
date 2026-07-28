from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from enum import Enum

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_temporal import (
    OilShadowTemporalTracker,
    TemporalCommitError,
    TemporalCommitPayload,
)
from oil_tracker.adapters.vision.oil_shadow_types import (
    AbsenceStabilityMode,
    AcceptedBoundaryOutcome,
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
    return ShadowUnavailableObservation(
        visibility=0.10,
        reason="insufficient support",
    )


def _commit(tracker, glass_id, observation, token):
    snapshot = tracker.snapshot(glass_id)
    provisional = tracker.evaluate(snapshot, observation)
    tracker.commit(TemporalCommitPayload(snapshot, provisional.next_state, token))
    return provisional


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


def test_snapshot_and_evaluation_do_not_create_or_mutate_live_state():
    tracker = OilShadowTemporalTracker()
    snapshot = tracker.snapshot("g")
    before = snapshot.state
    first = tracker.evaluate(snapshot, _boundary(20.0))
    second = tracker.evaluate(snapshot, _boundary(20.0))
    assert tracker.state_count == 0
    assert tracker.snapshot("g").state == before
    assert first == second
    assert first.next_state is not before
    assert isinstance(first.decision, BoundaryAcceptedDecision)
    assert first.decision.acceptance_mode is BoundaryAcceptanceMode.INITIAL


def test_committed_transitions_preserve_successful_semantics_and_actions():
    tracker = OilShadowTemporalTracker()
    initial = _commit(tracker, "g", _boundary(20.0), "initial-token")
    continuous = _commit(tracker, "g", _boundary(40.0), "continuous-token")
    pending = _commit(tracker, "g", _boundary(100.0), "pending-token")
    reacquired = _commit(tracker, "g", _boundary(102.0), "reacquired-token")
    assert isinstance(initial.decision, BoundaryAcceptedDecision)
    assert isinstance(continuous.decision, BoundaryAcceptedDecision)
    assert isinstance(pending.decision, ReacquisitionPendingDecision)
    assert isinstance(reacquired.decision, BoundaryAcceptedDecision)
    assert reacquired.decision.acceptance_mode is BoundaryAcceptanceMode.REACQUIRED
    assert reacquired.decision.smoothing_action is SmoothingAction.CLEAR_BEFORE_ACCEPT
    assert reacquired.decision.accepted_source_y == 102.0


def test_successful_unavailable_advances_only_proposed_or_committed_state():
    bounds = OilShadowBounds(unavailable_clear_frames=3)
    tracker = OilShadowTemporalTracker(bounds)
    _commit(tracker, "g", _boundary(20.0), "accepted")
    snapshot = tracker.snapshot("g")
    proposed = tracker.evaluate(snapshot, _unavailable())
    assert isinstance(proposed.decision, EvidenceUnavailableDecision)
    assert proposed.decision.stability_mode is AbsenceStabilityMode.PENDING
    assert tracker.snapshot("g") == snapshot
    first = _commit(tracker, "g", _unavailable(), "unavailable-1")
    second = _commit(tracker, "g", _unavailable(), "unavailable-2")
    third = _commit(tracker, "g", _unavailable(), "unavailable-3")
    assert first.decision.stability_mode is AbsenceStabilityMode.PENDING
    assert second.decision.stability_mode is AbsenceStabilityMode.PENDING
    assert third.decision.stability_mode is AbsenceStabilityMode.STABLE
    assert third.decision.smoothing_action is SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE
    assert tracker.snapshot("g").state.unavailable_count == 3


def test_no_interface_counter_is_bounded_and_stable_clear_is_derived():
    bounds = OilShadowBounds(no_interface_clear_frames=2)
    tracker = OilShadowTemporalTracker(bounds)
    _commit(tracker, "g", _boundary(20.0), "accepted")
    first = _commit(tracker, "g", _no_interface(), "absence-1")
    stable = _commit(tracker, "g", _no_interface(), "absence-2")
    for index in range(10):
        stable = _commit(tracker, "g", _no_interface(), f"absence-extra-{index}")
    assert first.decision.stability_mode is AbsenceStabilityMode.PENDING
    assert stable.decision.stability_mode is AbsenceStabilityMode.STABLE
    assert tracker.snapshot("g").state.no_interface_count == 2


def test_stale_and_replay_commit_cannot_overwrite_newer_state():
    tracker = OilShadowTemporalTracker()
    snapshot = tracker.snapshot("g")
    provisional = tracker.evaluate(snapshot, _boundary(20.0))
    payload = TemporalCommitPayload(snapshot, provisional.next_state, "one")
    committed = tracker.commit(payload)
    with pytest.raises(TemporalCommitError, match="Stale|replay"):
        tracker.commit(payload)
    stale = tracker.evaluate(snapshot, _boundary(80.0))
    with pytest.raises(TemporalCommitError, match="Stale"):
        tracker.commit(TemporalCommitPayload(snapshot, stale.next_state, "stale"))
    assert tracker.snapshot("g").state == committed


@pytest.mark.parametrize("global_reset", (False, True))
def test_reset_invalidates_every_pre_reset_snapshot(global_reset):
    tracker = OilShadowTemporalTracker()
    snapshot = tracker.snapshot("g")
    proposal = tracker.evaluate(snapshot, _boundary(20.0))
    if global_reset:
        tracker.reset()
    else:
        tracker.reset("g")
    reset_snapshot = tracker.snapshot("g")
    assert reset_snapshot.version == snapshot.version + 1
    assert tracker.state_count == 0
    with pytest.raises(TemporalCommitError, match="Stale"):
        tracker.commit(TemporalCommitPayload(snapshot, proposal.next_state, "pre-reset"))
    fresh = tracker.evaluate(reset_snapshot, _boundary(22.0))
    tracker.commit(TemporalCommitPayload(reset_snapshot, fresh.next_state, "post-reset"))
    assert tracker.snapshot("g").version == reset_snapshot.version + 1


def test_commit_hook_failure_leaves_complete_prior_state_unchanged():
    def fail(_snapshot, _state):
        raise RuntimeError("injected commit failure")

    tracker = OilShadowTemporalTracker(commit_hook=fail)
    snapshot = tracker.snapshot("g")
    proposal = tracker.evaluate(snapshot, _boundary(20.0))
    with pytest.raises(RuntimeError, match="injected"):
        tracker.commit(TemporalCommitPayload(snapshot, proposal.next_state, "fail"))
    assert tracker.state_count == 0
    assert tracker.snapshot("g") == snapshot


def test_beam_history_scalar_counts_no_raster_and_reset_are_bounded():
    bounds = OilShadowBounds(temporal_beam_width=3, temporal_history_window=4)
    tracker = OilShadowTemporalTracker(bounds)
    sequence = (_boundary(20.0), _ambiguous(22.0), _boundary(24.0), _unavailable(), _no_interface())
    for index in range(30):
        provisional = _commit(tracker, "g", sequence[index % len(sequence)], f"token-{index}")
        assert provisional.resources.beam_count <= bounds.temporal_beam_width
        assert provisional.resources.history_length <= bounds.temporal_history_window
        assert provisional.resources.retained_scalar_count <= tracker.retained_scalar_limit
    _assert_no_raster(tracker._states)
    tracker.reset("g")
    assert tracker.state_count == 0
    tracker.reset()
    assert tracker.state_count == 0
