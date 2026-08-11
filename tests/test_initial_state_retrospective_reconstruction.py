from __future__ import annotations

from copy import deepcopy

import pytest

from oil_tracker.application.services.initial_state_reconstruction import (
    annotate_judgment_provenance,
    effective_state_aware_coverage,
    enforce_conflict_review,
    merge_state_aware_events,
    observed_coverage,
    project_state_aware_samples,
    reconstruct_initial_state,
    samples_for_judgment,
)
from oil_tracker.domain.enums import EventType, FillState, InitialObservationState, JudgmentMode, ResultState
from oil_tracker.domain.events import detect_events_for_glass
from oil_tracker.domain.judgment import JudgmentOutcome
from oil_tracker.domain.retrospective import RetrospectiveInterpretation, RetrospectiveStatus
from oil_tracker.domain.results import TrackingSample
from oil_tracker.domain.session import InitialStateConfirmation
from tests.fixtures.synthetic import glass_config


def _confirmation(state: InitialObservationState) -> InitialStateConfirmation:
    return InitialStateConfirmation(state, "video.mp4", 0.0)


def _sample(
    index: int,
    state: FillState = FillState.UNKNOWN_REVIEW,
    *,
    y: float | None = None,
    valid: bool = False,
    flags=(),
) -> TrackingSample:
    return TrackingSample(
        run_id="run",
        glass_id="glass",
        frame_index=index,
        timestamp_sec=float(index),
        fill_state=state,
        raw_oil_air_level_y=y,
        raw_oil_air_level_px_from_zero=None,
        smoothed_oil_air_level_px_from_zero=None,
        overall_confidence=0.9 if valid else 0.2,
        is_valid=valid,
        flags=list(flags),
    )


def _accepted_sequence(prior: InitialObservationState):
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    bottom = glass.geometry.ellipse.center_y + glass.geometry.ellipse.radius_y
    if prior is InitialObservationState.FULL_NO_INTERFACE:
        first, second = top + 10, top + 20
        visible = FillState.DRAINING_VISIBLE
    else:
        first, second = bottom - 10, bottom - 20
        visible = FillState.FILLING_VISIBLE
    samples = [
        _sample(0),
        _sample(1),
        _sample(2, visible, y=first, valid=True),
        _sample(3, visible, y=second, valid=True),
    ]
    return glass, samples


@pytest.mark.parametrize(
    ("prior", "expected"),
    [
        (InitialObservationState.FULL_NO_INTERFACE, FillState.FULL_NO_INTERFACE),
        (InitialObservationState.EMPTY_NO_INTERFACE, FillState.EMPTY_NO_INTERFACE),
    ],
)
def test_full_and_empty_reconstruction_are_symmetric(prior, expected):
    glass, samples = _accepted_sequence(prior)
    result = reconstruct_initial_state(glass, samples, _confirmation(prior))

    assert result.status is RetrospectiveStatus.ACCEPTED
    assert result.interpreted_state is expected
    assert (result.start_frame_index, result.end_frame_index) == (0, 1)
    assert result.evidence_frame_indices == (2, 3)


@pytest.mark.parametrize(
    ("prior", "visible", "expected"),
    [
        (
            InitialObservationState.FULL_NO_INTERFACE,
            FillState.DRAINING_VISIBLE,
            FillState.FULL_NO_INTERFACE,
        ),
        (
            InitialObservationState.EMPTY_NO_INTERFACE,
            FillState.FILLING_VISIBLE,
            FillState.EMPTY_NO_INTERFACE,
        ),
    ],
)
def test_r7_anchor_trajectory_reconstructs_leading_initial_state(
    prior,
    visible,
    expected,
):
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    bottom = glass.geometry.ellipse.center_y + glass.geometry.ellipse.radius_y
    first, second = (
        (top + 10.0, top + 22.0)
        if prior is InitialObservationState.FULL_NO_INTERFACE
        else (bottom - 10.0, bottom - 22.0)
    )
    samples = [
        _sample(0, flags=("R7_OBSERVATION_UNAVAILABLE",)),
        _sample(1, flags=("R7_FOAM_UNCONFIRMED",)),
        _sample(
            2,
            visible,
            y=first,
            valid=True,
            flags=("R7_RESOLVED_OIL", "R7_OIL_ANCHOR"),
        ),
        _sample(
            3,
            visible,
            y=second,
            valid=True,
            flags=("R7_RESOLVED_OIL", "R7_OIL_ANCHOR"),
        ),
    ]

    result = reconstruct_initial_state(glass, samples, _confirmation(prior))

    assert result.status is RetrospectiveStatus.ACCEPTED
    assert result.interpreted_state is expected
    assert result.evidence_frame_indices == (2, 3)


@pytest.mark.parametrize(
    ("prior", "visible", "expected", "direction"),
    [
        (
            InitialObservationState.FULL_NO_INTERFACE,
            FillState.DRAINING_VISIBLE,
            FillState.FULL_NO_INTERFACE,
            1.0,
        ),
        (
            InitialObservationState.EMPTY_NO_INTERFACE,
            FillState.FILLING_VISIBLE,
            FillState.EMPTY_NO_INTERFACE,
            -1.0,
        ),
    ],
)
def test_r7_mid_glass_first_catch_still_reconstructs_confirmed_prefix(
    prior,
    visible,
    expected,
    direction,
):
    glass = glass_config()
    center = glass.geometry.ellipse.center_y
    samples = [
        _sample(0, flags=("R7_OBSERVATION_UNAVAILABLE",)),
        _sample(1, flags=("R7_FOAM_UNCONFIRMED",)),
        _sample(
            2,
            visible,
            y=center - direction * 8.0,
            valid=True,
            flags=("R7_RESOLVED_OIL", "R7_OIL_ANCHOR"),
        ),
        _sample(
            3,
            visible,
            y=center + direction * 8.0,
            valid=True,
            flags=("R7_RESOLVED_OIL", "R7_OIL_ANCHOR"),
        ),
    ]

    result = reconstruct_initial_state(glass, samples, _confirmation(prior))

    assert result.status is RetrospectiveStatus.ACCEPTED
    assert result.interpreted_state is expected
    assert result.evidence_frame_indices == (2, 3)
    assert all(0.32 < value < 0.68 for value in result.evidence_relative_positions)


def test_r7_continuation_only_cannot_confirm_initial_state() -> None:
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    samples = [
        _sample(0, flags=("R7_OBSERVATION_UNAVAILABLE",)),
        _sample(
            1,
            FillState.DRAINING_VISIBLE,
            y=top + 10.0,
            valid=True,
            flags=("R7_RESOLVED_OIL", "R7_OIL_CONTINUATION"),
        ),
        _sample(
            2,
            FillState.DRAINING_VISIBLE,
            y=top + 20.0,
            valid=True,
            flags=("R7_RESOLVED_OIL", "R7_OIL_CONTINUATION"),
        ),
    ]

    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )

    assert result.status is RetrospectiveStatus.UNRESOLVED
    assert not result.evidence_frame_indices


def test_r7_missing_or_rejected_foam_frames_do_not_block_later_anchors() -> None:
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    samples = [
        _sample(
            0,
            flags=("R7_OBSERVATION_UNAVAILABLE", "FOGGED_OR_GLARE"),
        ),
        _sample(1, flags=("R7_FOAM_STATIC_ARTIFACT_REJECTED",)),
        _sample(
            2,
            FillState.DRAINING_VISIBLE,
            y=top + 10.0,
            valid=True,
            flags=("R7_RESOLVED_OIL", "R7_OIL_ANCHOR"),
        ),
        _sample(
            3,
            FillState.DRAINING_VISIBLE,
            y=top + 20.0,
            valid=True,
            flags=("R7_RESOLVED_OIL", "R7_OIL_ANCHOR"),
        ),
    ]

    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )

    assert result.status is RetrospectiveStatus.ACCEPTED


def test_projection_is_separate_and_does_not_fabricate_numeric_oil():
    glass, samples = _accepted_sequence(InitialObservationState.FULL_NO_INTERFACE)
    original = deepcopy(samples)
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    projected = project_state_aware_samples(samples, result)

    assert samples == original
    assert projected[0] is not samples[0]
    assert projected[0].fill_state is FillState.FULL_NO_INTERFACE
    assert projected[0].is_valid is True
    assert projected[0].raw_oil_air_level_y is None
    assert projected[0].smoothed_oil_air_level_px_from_zero is None
    assert "RETROSPECTIVE_INITIAL_STATE" in projected[0].flags
    assert projected[2] is samples[2]
    assert observed_coverage(samples) == pytest.approx(0.5)
    assert effective_state_aware_coverage(samples, result) == pytest.approx(1.0)


def test_prior_seeded_visible_labels_are_not_positive_proof():
    glass = glass_config()
    samples = [
        _sample(0, FillState.DRAINING_VISIBLE),
        _sample(1, FillState.DRAINING_VISIBLE),
    ]
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    assert result.status is RetrospectiveStatus.UNRESOLVED
    assert not result.evidence_frame_indices


@pytest.mark.parametrize(
    "barrier_sample",
    [
        _sample(1, flags=("FOGGED_OR_GLARE",)),
        _sample(1, flags=("DETECTION_LOST",)),
        _sample(1, flags=("NO_INTERFACE_EVIDENCE_UNAVAILABLE",)),
        _sample(1, flags=("OIL_PIPELINE_FAILURE",)),
        _sample(1, FillState.FOAMING_VISIBLE),
    ],
)
def test_barriers_stop_leading_inference(barrier_sample):
    glass, samples = _accepted_sequence(InitialObservationState.FULL_NO_INTERFACE)
    samples[1] = barrier_sample
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    assert result.status is RetrospectiveStatus.UNRESOLVED
    assert result.barriers


def test_authoritative_foam_with_independent_numeric_oil_remains_direction_evidence():
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    samples = [
        _sample(0),
        _sample(1),
        _sample(
            2,
            FillState.FOAMING_VISIBLE,
            y=top + 10,
            valid=True,
            flags=("FOAM_STRONG_EVIDENCE",),
        ),
        _sample(
            3,
            FillState.FOAMING_VISIBLE,
            y=top + 20,
            valid=True,
            flags=("FOAM_STRONG_EVIDENCE",),
        ),
    ]

    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    projected = project_state_aware_samples(samples, result)

    assert result.status is RetrospectiveStatus.ACCEPTED
    assert result.evidence_frame_indices == (2, 3)
    assert projected[0].fill_state is FillState.FULL_NO_INTERFACE
    assert projected[2] is samples[2]
    assert projected[2].fill_state is FillState.FOAMING_VISIBLE


def test_sequence_resolved_leading_state_is_not_reconstructed_twice():
    glass = glass_config()
    samples = [
        _sample(
            0,
            FillState.FULL_NO_INTERFACE,
            valid=True,
            flags=("SEQUENCE_RESOLVED_STATE", "SEQUENCE_INITIAL_STATE_PRIOR"),
        ),
        _sample(
            1,
            FillState.FULL_NO_INTERFACE,
            valid=True,
            flags=("SEQUENCE_RESOLVED_STATE", "SEQUENCE_INITIAL_STATE_PRIOR"),
        ),
    ]

    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )

    assert result.status is RetrospectiveStatus.NOT_APPLICABLE
    assert "sequence resolver" in result.reason


def test_hard_unavailable_barrier_still_wins_over_malformed_numeric_foam_sample():
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    samples = [
        _sample(0),
        _sample(
            1,
            FillState.FOAMING_VISIBLE,
            y=top + 10,
            valid=True,
            flags=("FOAM_STRONG_EVIDENCE", "FOGGED_OR_GLARE"),
        ),
        _sample(2, FillState.DRAINING_VISIBLE, y=top + 20, valid=True),
    ]

    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )

    assert result.status is RetrospectiveStatus.UNRESOLVED
    assert result.barriers == ("FOGGED_OR_GLARE",)


def test_contradictory_direct_topology_is_conflict_without_interval():
    glass = glass_config()
    bottom = glass.geometry.ellipse.center_y + glass.geometry.ellipse.radius_y
    samples = [
        _sample(0),
        _sample(1, FillState.FILLING_VISIBLE, y=bottom - 10, valid=True),
        _sample(2, FillState.FILLING_VISIBLE, y=bottom - 20, valid=True),
    ]
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    assert result.status is RetrospectiveStatus.CONFLICT
    assert result.start_time_sec is None
    assert result.end_time_sec is None


def test_insufficient_or_canonical_ambiguous_evidence_stays_unresolved():
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    samples = [
        _sample(0),
        _sample(1),
        _sample(2, FillState.PARTIAL_VISIBLE, y=top + 10, valid=True),
    ]
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    assert result.status is RetrospectiveStatus.UNRESOLVED


def test_only_leading_prefix_is_projected_not_middle_run_unknowns():
    glass, samples = _accepted_sequence(InitialObservationState.FULL_NO_INTERFACE)
    samples.append(_sample(4))
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    projected = project_state_aware_samples(samples, result)
    assert projected[0].fill_state is FillState.FULL_NO_INTERFACE
    assert projected[4].fill_state is FillState.UNKNOWN_REVIEW
    assert projected[4].is_valid is False


def test_unknown_and_auto_confirmations_do_not_grant_reconstruction_authority():
    glass, samples = _accepted_sequence(InitialObservationState.FULL_NO_INTERFACE)
    for state in (InitialObservationState.UNKNOWN_REVIEW, InitialObservationState.AUTO):
        result = reconstruct_initial_state(glass, samples, _confirmation(state))
        assert result.status is RetrospectiveStatus.NOT_APPLICABLE
        assert result.interpreted_state is None


def test_recovery_judgment_path_never_receives_projected_samples():
    glass, samples = _accepted_sequence(InitialObservationState.FULL_NO_INTERFACE)
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    recovery = samples_for_judgment(samples, result, JudgmentMode.RECOVERY)
    hold = samples_for_judgment(samples, result, JudgmentMode.HOLD_BELOW_ZERO)
    assert recovery[0].fill_state is FillState.UNKNOWN_REVIEW
    assert hold[0].fill_state is FillState.FULL_NO_INTERFACE


def test_direct_opposite_no_interface_evidence_is_conflict():
    glass, samples = _accepted_sequence(InitialObservationState.FULL_NO_INTERFACE)
    samples[0] = _sample(0, FillState.EMPTY_NO_INTERFACE, valid=True)
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    assert result.status is RetrospectiveStatus.CONFLICT
    assert result.start_time_sec is None
    assert "contradicts" in result.reason


def test_state_aware_event_merge_keeps_observed_review_evidence_and_marks_added_state_event():
    glass, samples = _accepted_sequence(InitialObservationState.FULL_NO_INTERFACE)
    result = reconstruct_initial_state(
        glass,
        samples,
        _confirmation(InitialObservationState.FULL_NO_INTERFACE),
    )
    observed = detect_events_for_glass("run", glass.id, samples)
    projected = detect_events_for_glass(
        "run",
        glass.id,
        project_state_aware_samples(samples, result),
    )
    merged = merge_state_aware_events(observed, projected, result)

    assert any(event.event_type is EventType.REVIEW_REQUIRED for event in merged)
    state_events = [
        event for event in merged
        if event.event_type is EventType.FULL_NO_INTERFACE_START
    ]
    assert state_events
    assert any("provenance=retrospective_initial_state" in event.note for event in state_events)


def test_conflict_forces_review_and_hold_judgment_keeps_retrospective_provenance():
    conflict = RetrospectiveInterpretation(
        glass_id="glass",
        status=RetrospectiveStatus.CONFLICT,
        confirmed_prior=InitialObservationState.FULL_NO_INTERFACE,
        reason="contradiction",
    )
    accepted = RetrospectiveInterpretation(
        glass_id="glass",
        status=RetrospectiveStatus.ACCEPTED,
        confirmed_prior=InitialObservationState.FULL_NO_INTERFACE,
        interpreted_state=FillState.FULL_NO_INTERFACE,
        start_time_sec=0.0,
        end_time_sec=1.0,
        start_frame_index=0,
        end_frame_index=1,
    )
    base = JudgmentOutcome(ResultState.PASS, 1.0, "base")

    conflicted = enforce_conflict_review(base, conflict)
    assert conflicted.state is ResultState.REVIEW_REQUIRED
    assert "conflict" in conflicted.note.lower()

    hold = annotate_judgment_provenance(base, accepted, JudgmentMode.HOLD_BELOW_ZERO)
    recovery = annotate_judgment_provenance(base, accepted, JudgmentMode.RECOVERY)
    assert "provenance=retrospective_initial_state" in hold.note
    assert recovery.note == "base"
