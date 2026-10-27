"""Co-located fill owners (E4, opt-in, frozen 2026-10-27).

A ``FILL_OWNER_AMBIGUOUS`` frame whose dynamic fill owners are all observed
within one association step publishes from the owners' rows instead of
failing closed. Only the frame's allowed set, reason and ambiguity flag
change; lifecycle state evolves as without the option.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from oil_tracker.adapters.vision.oil_phase_lifecycle import (
    OilMaterialPhase,
    OilMaterialPhaseLifecycleOwner,
)
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from tests.unit.test_oil_fill_owner_contest import EMPTY, STATE_KEYS, _frame, _rise

STEP = 32.0  # maximum_jump_px of the shared test policy


def _run(layers, *, enabled: bool, contest: bool = False):
    from tests.unit.test_oil_phase_lifecycle import _policy

    policy = replace(_policy(confirmed_initial_state=EMPTY), fill_owner_colocation_enabled=enabled,
                     fill_owner_contest_enabled=contest)
    return OilMaterialPhaseLifecycleOwner(policy).resolve(layers)


def _pair(layers, *, contest: bool = False):
    off = _run(layers, enabled=False, contest=contest)
    on = _run(layers, enabled=True, contest=contest)
    assert on.phases == off.phases
    assert on.fill_confirmation_profiles == off.fill_confirmation_profiles
    assert on.owner_chains == off.owner_chains
    for before, after in zip(off.diagnostics, on.diagnostics, strict=True):
        assert {key: after[key] for key in STATE_KEYS} == {key: before[key] for key in STATE_KEYS}
    return off, on


def _two_owner_layers(gap: float):
    """Owners a and b rise together for two frames with a fixed gap; a then continues alone."""
    return (
        _frame(0, _rise(0, "a", 180.0), _rise(0, "b", 180.0 + gap, candidate_offset=1)),
        _frame(1, _rise(1, "a", 172.0), _rise(1, "b", 172.0 + gap, candidate_offset=1)),
        _frame(2, _rise(2, "a", 164.0)),
        _frame(3, _rise(3, "a", 156.0)),
        _frame(4, _rise(4, "a", 148.0)),
        _frame(5, _rise(5, "a", 140.0)),
    )


def _colocated(result) -> list[int]:
    return [frame for frame, reason in enumerate(result.reasons) if reason == "FILL_OWNER_COLOCATED"]


@pytest.mark.parametrize("gap", [10.0, STEP])
def test_owners_within_one_step_publish_from_both_owners(gap) -> None:
    off, on = _pair(_two_owner_layers(gap))

    assert off.reasons[:2] == ("FILL_OWNER_AMBIGUOUS",) * 2
    assert {0, 1} <= off.ambiguous_frames
    assert _colocated(on) == [0, 1]
    for frame in (0, 1):
        assert on.allowed_tracklet_ids[frame] == frozenset({"a", "b"})
        assert on.phases[frame] is OilMaterialPhase.FILLING
        assert frame not in on.ambiguous_frames
    # Every later frame decides exactly as without the option.
    assert on.reasons[2:] == off.reasons[2:]
    assert on.allowed_tracklet_ids[2:] == off.allowed_tracklet_ids[2:]
    assert on.ambiguous_frames - {0, 1} == off.ambiguous_frames - {0, 1}


def test_owners_beyond_one_step_stay_ambiguous() -> None:
    off, on = _pair(_two_owner_layers(STEP + 0.5))

    assert off.reasons[:2] == ("FILL_OWNER_AMBIGUOUS",) * 2
    assert on.reasons == off.reasons
    assert on.allowed_tracklet_ids == off.allowed_tracklet_ids
    assert on.ambiguous_frames == off.ambiguous_frames


def test_owner_without_a_row_keeps_the_frame_ambiguous() -> None:
    layers = (
        _frame(0, _rise(0, "a", 180.0), _rise(0, "b", 190.0, candidate_offset=1)),
        _frame(1, _rise(1, "a", 172.0), _rise(1, "b", 186.0, candidate_offset=1)),
        # b is still a live dynamic owner but has no row in this frame.
        _frame(2, _rise(2, "a", 164.0)),
        _frame(3, _rise(3, "a", 156.0)),
    )

    off, on = _pair(layers)

    assert off.reasons[2] == "FILL_OWNER_AMBIGUOUS"
    assert on.reasons[2] == "FILL_OWNER_AMBIGUOUS"
    assert on.allowed_tracklet_ids[2] == frozenset()
    assert 2 in on.ambiguous_frames
    assert _colocated(on) == [0, 1]


def test_colocated_frames_add_no_contest_mark() -> None:
    off, on = _pair(_two_owner_layers(10.0), contest=True)

    # Without co-location the first shared frame already marks a and b.
    assert off.diagnostics[0]["fill_owner_contest"]["contested_tracklet_ids"] == ["a", "b"]
    assert _colocated(on) == [0, 1]
    for frame in (0, 1):
        assert on.diagnostics[frame]["fill_owner_contest"] == {"contested_tracklet_ids": [], "gated": False}
    # Frames 2-4 still have b as a live owner without a row: ambiguous, so they mark as before.
    assert on.reasons[2:5] == ("FILL_OWNER_AMBIGUOUS",) * 3
    assert on.diagnostics[2]["fill_owner_contest"]["contested_tracklet_ids"] == ["a", "b"]
    assert on.reasons[5] == off.reasons[5] == "FILL_OWNER_CONTESTED"


def test_option_off_is_the_default_and_leaves_the_lifecycle_unchanged() -> None:
    from tests.unit.test_oil_phase_lifecycle import _policy

    assert _policy(confirmed_initial_state=EMPTY).fill_owner_colocation_enabled is False
    layers = _two_owner_layers(10.0)
    default = OilMaterialPhaseLifecycleOwner(_policy(confirmed_initial_state=EMPTY)).resolve(layers)
    off = _run(layers, enabled=False)
    assert default.reasons == off.reasons
    assert default.allowed_tracklet_ids == off.allowed_tracklet_ids
    assert default.ambiguous_frames == off.ambiguous_frames
    assert default.diagnostics == off.diagnostics


@pytest.mark.parametrize("other", [
    {"cost_first_assignment": True},
    {"candidate_rgb": True},
])
def test_rejected_mechanisms_cannot_be_stacked_with_colocation(other) -> None:
    with pytest.raises(ValueError, match="Compare the fill-owner co-location"):
        OpenCvPhaseDetector(fill_owner_colocation=True, **other)


def test_colocation_combines_with_the_integrated_candidate_and_the_contest_gate() -> None:
    detector = OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True, fill_owner_contest=True,
                                   fill_owner_colocation=True)
    resolver = detector._observation_sequence_resolver
    assert resolver._oil.config.fill_owner_colocation_enabled is True
    for version in (detector.version, resolver.version, resolver._oil.version):
        assert version.endswith(
            "+initial-full-observation-v2+top-exit-full-v3+fill-owner-contest-v1+fill-owner-colocation-v1")
