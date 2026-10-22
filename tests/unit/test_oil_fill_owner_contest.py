"""Contested fill-owner gate (opt-in, frozen 2026-10-22).

A tracklet that shared a ``FILL_OWNER_AMBIGUOUS`` frame cannot become the
publishing fill owner by outlasting the others. The gate only empties the
frame's allowed set; lifecycle state evolves as without it.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from oil_tracker.adapters.vision.oil_phase_lifecycle import (
    OilMaterialPhase,
    OilMaterialPhaseLifecycleOwner,
)
from oil_tracker.adapters.vision.oil_sequence_types import TrackletConfirmationProfile
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.enums import InitialObservationState
from tests.unit.test_oil_phase_lifecycle import _node, _policy, _unknown

EMPTY = InitialObservationState.EMPTY_NO_INTERFACE
# Lifecycle state that the gate must leave exactly as without it.
STATE_KEYS = (
    "dynamic_fill_owner_ids",
    "established_fill_owner",
    "established_fill_owner_chain",
    "established_fill_last_y",
    "established_fill_last_frame",
    "ownerless_barrier_state",
    "release_stage",
    "release_selected_tracklet_id",
    "recovery_stage",
)


def _rise(frame: int, tracklet: str, y: float, **kwargs):
    """A confirmed upward row with strong motion: a dynamic fill owner."""
    return _node(
        frame,
        tracklet,
        y,
        direction=-1,
        progress=30.0,
        motion_support=0.90,
        motion_coverage=0.85,
        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY,
        **kwargs,
    )


def _frame(frame: int, *nodes):
    return (*nodes, _unknown(frame))


def _run(layers, *, enabled: bool, initial=EMPTY):
    policy = replace(_policy(confirmed_initial_state=initial), fill_owner_contest_enabled=enabled)
    return OilMaterialPhaseLifecycleOwner(policy).resolve(layers)


def _pair(layers, *, initial=EMPTY):
    off, on = _run(layers, enabled=False, initial=initial), _run(layers, enabled=True, initial=initial)
    assert on.phases == off.phases
    for before, after in zip(off.diagnostics, on.diagnostics, strict=True):
        assert "fill_owner_contest" not in before
        assert {key: after[key] for key in STATE_KEYS} == {key: before[key] for key in STATE_KEYS}
    return off, on


def _gated_frames(result) -> list[int]:
    return [frame for frame, reason in enumerate(result.reasons) if reason == "FILL_OWNER_CONTESTED"]


def _assert_gated(result, frame: int) -> None:
    assert result.reasons[frame] == "FILL_OWNER_CONTESTED"
    assert result.allowed_tracklet_ids[frame] == frozenset()
    assert result.owner_chains[frame] == ()
    assert frame in result.ambiguous_frames
    assert result.diagnostics[frame]["fill_owner_contest"]["gated"] is True


def _survivor_layers():
    """Owners a and b share frames 0-1; b ages out and a is left alone at frame 5."""
    return (
        _frame(0, _rise(0, "a", 180.0), _rise(0, "b", 190.0, candidate_offset=1)),
        _frame(1, _rise(1, "a", 172.0), _rise(1, "b", 186.0, candidate_offset=1)),
        _frame(2, _rise(2, "a", 164.0)),
        _frame(3, _rise(3, "a", 156.0)),
        _frame(4, _rise(4, "a", 148.0)),
        _frame(5, _rise(5, "a", 140.0)),
    )


def test_contested_survivor_publishes_unknown_instead_of_winning_by_attrition() -> None:
    off, on = _pair(_survivor_layers())

    assert off.reasons[:5] == ("FILL_OWNER_AMBIGUOUS",) * 5
    assert off.reasons[5] == "FILL_MOTION_OWNER"
    assert off.allowed_tracklet_ids[5] == frozenset({"a"})
    assert on.reasons[:5] == off.reasons[:5]
    _assert_gated(on, 5)
    assert _gated_frames(on) == [5]
    assert on.phases[5] is OilMaterialPhase.FILLING
    assert on.diagnostics[5]["fill_owner_contest"]["contested_tracklet_ids"] == ["a", "b"]
    # The survivor still becomes the established fill, exactly as without the gate.
    assert on.diagnostics[5]["established_fill_owner"] == "a"


def test_never_contested_owner_publishes_as_before() -> None:
    layers = tuple(_frame(frame, _rise(frame, "a", 180.0 - 10.0 * frame)) for frame in range(4))

    off, on = _pair(layers)

    assert on.reasons == off.reasons
    assert on.allowed_tracklet_ids == off.allowed_tracklet_ids
    assert on.owner_chains == off.owner_chains
    assert on.ambiguous_frames == off.ambiguous_frames
    assert on.allowed_tracklet_ids[3] == frozenset({"a"})
    assert all(item["fill_owner_contest"] == {"contested_tracklet_ids": [], "gated": False}
               for item in on.diagnostics)


def test_fresh_uncontested_chain_after_a_contest_publishes_as_before() -> None:
    layers = (
        _frame(0, _rise(0, "a", 180.0), _rise(0, "b", 190.0, candidate_offset=1)),
        _frame(1, _rise(1, "a", 172.0), _rise(1, "b", 186.0, candidate_offset=1)),
        *(_frame(frame) for frame in range(2, 6)),
        _frame(6, _rise(6, "c", 185.0)),
        _frame(7, _rise(7, "c", 175.0)),
    )

    off, on = _pair(layers)

    assert off.reasons[6] == on.reasons[6] == "FILL_MOTION_OWNER"
    assert off.allowed_tracklet_ids[6] == on.allowed_tracklet_ids[6] == frozenset({"c"})
    assert on.allowed_tracklet_ids[7] == frozenset({"c"})
    assert _gated_frames(on) == []


def test_handoff_successor_of_a_contested_chain_is_gated() -> None:
    layers = (
        _frame(0, _rise(0, "a", 180.0), _rise(0, "b", 190.0, candidate_offset=1)),
        _frame(1, _rise(1, "a", 172.0), _rise(1, "b", 186.0, candidate_offset=1)),
        _frame(2, _rise(2, "a", 164.0)),
        _frame(3, _rise(3, "a", 156.0)),
        _frame(4, _rise(4, "a", 148.0)),
        _frame(5, _rise(5, "a2", 142.0)),
        _frame(6, _rise(6, "a2", 134.0)),
    )

    off, on = _pair(layers)

    assert off.reasons[5] == "FILL_MOTION_OWNER"
    assert off.allowed_tracklet_ids[5] == frozenset({"a2"})
    assert off.owner_chains[5] == ("a", "a2")
    _assert_gated(on, 5)
    _assert_gated(on, 6)
    assert "a2" in on.diagnostics[6]["fill_owner_contest"]["contested_tracklet_ids"]


def test_handoff_successor_stays_contested_after_its_chain_restarts() -> None:
    layers = (
        _frame(0, _rise(0, "a", 180.0), _rise(0, "b", 190.0, candidate_offset=1)),
        _frame(1, _rise(1, "a", 172.0), _rise(1, "b", 186.0, candidate_offset=1)),
        _frame(2, _rise(2, "a", 164.0)),
        _frame(3, _rise(3, "a", 156.0)),
        _frame(4, _rise(4, "a", 148.0)),
        _frame(5, _rise(5, "a2", 142.0)),
        *(_frame(frame) for frame in range(6, 9)),
        # The handed-off chain has aged out; a2 starts a new chain of its own.
        _frame(9, _rise(9, "a2", 150.0)),
    )

    off, on = _pair(layers)

    assert off.owner_chains[9] == ("a2",)
    assert off.allowed_tracklet_ids[9] == frozenset({"a2"})
    _assert_gated(on, 9)


def test_fill_phase_reentry_by_a_contested_tracklet_is_gated() -> None:
    layers = (
        _frame(0, _rise(0, "a", 180.0)),
        _frame(1, _rise(1, "a", 160.0)),
        _frame(2, _rise(2, "a", 140.0)),
        _frame(3, _rise(3, "a", 120.0), _rise(3, "b", 190.0, candidate_offset=1)),
        *(_frame(frame) for frame in range(4, 7)),
        # b returns mid-Glass next to the established fill, so it can only re-enter.
        _frame(7, _rise(7, "b", 138.0)),
    )

    off, on = _pair(layers)

    assert off.reasons[3] == "FILL_OWNER_AMBIGUOUS"
    assert off.reasons[7] == "FILL_PHASE_REENTRY"
    assert off.allowed_tracklet_ids[7] == frozenset({"b"})
    _assert_gated(on, 7)
    assert _gated_frames(on) == [7]


def test_current_anchor_handoff_from_a_contested_owner_is_gated() -> None:
    anchor = _node(
        6,
        "current-anchor",
        70.0,
        direction=1,
        progress=18.0,
        material_conflict=1.0,
        tracklet_material_conflict=0.65,
        motion_support=0.9,
        motion_coverage=0.8,
        material_path=True,
        confirmation_profile=TrackletConfirmationProfile.ANCHOR_CORRIDOR,
    )
    layers = (
        _frame(0, _rise(0, "owner", 130.0)),
        _frame(1, _rise(1, "owner", 120.0), _rise(1, "rival", 140.0, candidate_offset=1)),
        _frame(2, _rise(2, "owner", 110.0)),
        _frame(3, _rise(3, "owner", 100.0)),
        _frame(4, _rise(4, "owner", 95.0)),
        _frame(5, _rise(5, "owner", 90.0)),
        _frame(6, anchor),
    )

    off, on = _pair(layers, initial=None)

    assert off.reasons[1] == "FILL_OWNER_AMBIGUOUS"
    assert off.reasons[6] == "FILL_CURRENT_ANCHOR_HANDOFF"
    assert off.allowed_tracklet_ids[6] == frozenset({"current-anchor"})
    _assert_gated(on, 5)
    _assert_gated(on, 6)


def test_fill_span_completion_is_not_gated_and_ends_the_contest() -> None:
    layers = (
        _frame(0, _rise(0, "a", 180.0), _rise(0, "b", 190.0, candidate_offset=1)),
        _frame(1, _rise(1, "a", 150.0), _rise(1, "b", 186.0, candidate_offset=1)),
        _frame(2, _rise(2, "a", 120.0)),
        _frame(3, _rise(3, "a", 90.0)),
        _frame(4, _rise(4, "a", 50.0)),
        _frame(5),
    )

    off, on = _pair(layers)

    assert off.reasons[4] == on.reasons[4] == "FILL_SPAN_CONFIRMED"
    assert off.phases[4] is OilMaterialPhase.FILLED_BARRIER
    assert on.allowed_tracklet_ids[4] == off.allowed_tracklet_ids[4] == frozenset({"a"})
    assert on.diagnostics[4]["fill_owner_contest"]["contested_tracklet_ids"] == ["a", "b"]
    assert on.diagnostics[5]["fill_owner_contest"]["contested_tracklet_ids"] == []
    assert _gated_frames(on) == []


def test_drain_release_is_not_gated_and_ends_the_contest() -> None:
    layers = (
        _frame(0, _rise(0, "fill-a", 180.0)),
        _frame(1, _rise(1, "fill-a", 155.0)),
        _frame(2, _rise(2, "fill-a", 150.0), _rise(2, "fill-b", 190.0, candidate_offset=1)),
        *(_frame(frame) for frame in range(3, 7)),
        _frame(7, _node(7, "reversed", 170.0, direction=1, progress=20.0, motion_support=0.90,
                        motion_coverage=0.85,
                        confirmation_profile=TrackletConfirmationProfile.MOTION_TRAJECTORY)),
        _frame(8),
    )

    off, on = _pair(layers)

    assert off.reasons[2] == "FILL_OWNER_AMBIGUOUS"
    assert off.phases[7] is on.phases[7] is OilMaterialPhase.DRAINING
    assert on.allowed_tracklet_ids[7] == off.allowed_tracklet_ids[7] == frozenset({"reversed"})
    assert on.diagnostics[7]["fill_owner_contest"]["contested_tracklet_ids"] == ["fill-a", "fill-b"]
    assert on.diagnostics[8]["fill_owner_contest"]["contested_tracklet_ids"] == []
    assert _gated_frames(on) == []


@pytest.mark.parametrize("other", [
    {"cost_first_assignment": True},
    {"candidate_rgb": True},
])
def test_rejected_mechanisms_cannot_be_stacked_with_the_contest_gate(other) -> None:
    with pytest.raises(ValueError, match="Compare the fill-owner contest"):
        OpenCvPhaseDetector(fill_owner_contest=True, **other)


def test_contest_gate_combines_with_the_integrated_candidate() -> None:
    detector = OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True, fill_owner_contest=True)
    resolver = detector._observation_sequence_resolver
    assert resolver._oil.config.fill_owner_contest_enabled is True
    for version in (detector.version, resolver.version, resolver._oil.version):
        assert version.endswith("+initial-full-observation-v2+top-exit-full-v3+fill-owner-contest-v1")
