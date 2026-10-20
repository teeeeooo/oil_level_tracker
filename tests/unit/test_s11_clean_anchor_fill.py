from __future__ import annotations

from oil_tracker.adapters.vision.oil_phase_lifecycle import (
    OilFillConfirmationProfile as Profile,
    OilMaterialPhaseLifecycleOwner as Owner,
    _FillChain,
    _FillObservation,
)
from oil_tracker.adapters.vision.oil_sequence_types import TrackletConfirmationProfile
from oil_tracker.domain.enums import InitialObservationState
from tests.diagnostics.s11_clean_anchor_fill import clean_anchor, clean_chain
from tests.unit.test_oil_phase_lifecycle import _policy


def _observation(frame, y, *, anchor=False, veto=False, support=0.0, coverage=0.0):
    return _FillObservation(
        frame=frame,
        y=y,
        material_veto=veto,
        independent_anchor=anchor,
        confirmation_profile=TrackletConfirmationProfile.ANCHOR_CORRIDOR,
        net_progress_px=40.0,
        directional_agreement=1.0,
        motion_support=support,
        motion_coverage=coverage,
    )


def _rising_chain(flags, *, origin_y=190.0):
    # Geometry height 200, top 0: rises from Y190 into the entrance band (< 54).
    ys = (190.0, 150.0, 100.0, 40.0)
    observations = tuple(
        _observation(frame, y, **flag) for frame, (y, flag) in enumerate(zip(ys, flags))
    )
    return _FillChain(owner="t1", owners=("t1",), origin_y=origin_y, observations=observations)


def _profile(chain, **policy):
    return Owner(_policy(**policy))._fill_confirmation_profile(chain)


def test_clean_anchor_still_qualifies_under_trial():
    chain = _rising_chain(({}, {"anchor": True}, {"anchor": True, "veto": True}, {}))
    assert _profile(chain) is Profile.UNKNOWN_FILL_ANCHORED
    with clean_anchor() as operations:
        assert _profile(chain) is Profile.UNKNOWN_FILL_ANCHORED
    assert operations == []


def test_contradicted_only_anchors_do_not_grant_fill_authority():
    chain = _rising_chain(({}, {"anchor": True, "veto": True}, {"anchor": True, "veto": True}, {"veto": True}))
    assert _profile(chain) is Profile.UNKNOWN_FILL_ANCHORED
    with clean_anchor() as operations:
        assert _profile(chain) is Profile.NONE
    assert operations == [{
        "owner": "t1", "owners": ["t1"], "terminal_frame": 3,
        "ordinary": Profile.UNKNOWN_FILL_ANCHORED.value, "trial": Profile.NONE.value,
        "contradicted_anchor_frames": [1, 2], "clean_anchor_frames": [],
    }]


def test_anchor_free_chain_is_unchanged():
    chain = _rising_chain(({}, {"veto": True}, {}, {}))
    assert clean_chain(chain) == chain
    ordinary = _profile(chain)
    with clean_anchor() as operations:
        assert _profile(chain) is ordinary
    assert operations == []


def test_empty_entrance_motion_keeps_motion_path_but_not_contradicted_anchor_path():
    empty = {"confirmed_initial_state": InitialObservationState.EMPTY_NO_INTERFACE}
    motion = _rising_chain(({}, {"support": 0.9, "coverage": 0.9, "veto": True}, {}, {}))
    anchor = _rising_chain(({}, {"anchor": True, "veto": True}, {}, {}))
    # Without any clean anchor the motion path still qualifies an empty entrance.
    with clean_anchor():
        assert _profile(motion, **empty) is Profile.EMPTY_ENTRANCE_MOTION
    # A contradicted anchor without motion support no longer supplies that path.
    assert _profile(anchor, **empty) is Profile.UNKNOWN_FILL_ANCHORED
    with clean_anchor() as operations:
        assert _profile(anchor, **empty) is Profile.NONE
    assert len(operations) == 1


def test_short_or_non_rising_chains_are_unchanged():
    short = _FillChain(owner="t1", owners=("t1",), origin_y=190.0, observations=(
        _observation(0, 190.0, anchor=True, veto=True), _observation(1, 40.0, anchor=True, veto=True)))
    with clean_anchor() as operations:
        assert _profile(short) is Profile.NONE
    assert operations == []


def test_patch_is_removed_after_context():
    original = Owner._fill_confirmation_profile
    with clean_anchor():
        assert Owner._fill_confirmation_profile is not original
    assert Owner._fill_confirmation_profile is original
