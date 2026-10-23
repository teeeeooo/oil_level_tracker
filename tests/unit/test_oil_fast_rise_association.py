from __future__ import annotations

from dataclasses import replace

import pytest

from oil_tracker.adapters.vision.oil_candidate_authority import OilCandidateAuthority
from oil_tracker.adapters.vision.oil_interface_tracklets import DirectedInterfaceTrackletBuilder
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from tests.unit.test_oil_interface_tracklets import _policy, _ref

ANCHOR = OilCandidateAuthority.ANCHOR_ELIGIBLE


def _row(frame, y, *, witness=True, ordered_lower=False, offset=0):
    return _ref(frame, offset, y, authority=ANCHOR if witness else OilCandidateAuthority.CONTINUATION_ELIGIBLE,
                source="phase", motion=0.8, coverage=0.8, ordered_lower=ordered_lower)


def _resolve(frames, *, enabled=True, **policy):
    builder = DirectedInterfaceTrackletBuilder(replace(_policy(), fast_rise_association_enabled=enabled, **policy))
    return builder.resolve(tuple(tuple(rows) for rows in frames))


def _ids(result):
    return [[ref.tracklet_id for ref in refs] for refs in result.refs_by_frame]


def _rising(step, count=5, start=900.0):
    return [[_row(frame, start - step * frame)] for frame in range(count)]


def test_witnessed_fast_rise_seeds_one_tracklet_and_continues_beyond_the_cap():
    result = _resolve(_rising(70.0, count=6))
    ids = {ref.tracklet_id for refs in result.refs_by_frame for ref in refs}
    assert len(ids) == 1
    assert result.fast_rise_seed_frames == (2,)
    assert all(ref.tracklet_admitted for refs in result.refs_by_frame for ref in refs)


def test_option_off_keeps_one_row_tracklets_that_never_admit():
    result = _resolve(_rising(70.0, count=6), enabled=False)
    assert len({ref.tracklet_id for refs in result.refs_by_frame for ref in refs}) == 6
    assert result.fast_rise_seed_frames == ()
    assert not any(ref.tracklet_admitted for refs in result.refs_by_frame for ref in refs)


def test_motion_within_the_cap_is_identical_with_the_option():
    frames = _rising(20.0, count=6)
    assert _resolve(frames) == _resolve(frames, enabled=False)


@pytest.mark.parametrize("frames", [
    pytest.param([[_row(f, 600.0 + 70.0 * f)] for f in range(4)], id="downward"),
    pytest.param(_rising(100.0, count=4), id="above-three-caps"),
    pytest.param([[_row(0, 900.0)], [_row(1, 830.0)], [_row(2, 750.0)]], id="velocity-change"),
    pytest.param([[_row(0, 900.0)], [_row(1, 830.0, witness=False)], [_row(2, 760.0)]], id="unwitnessed-row"),
    pytest.param([[_row(0, 900.0)], [_row(1, 830.0, ordered_lower=True)], [_row(2, 760.0)]], id="mixed-representation"),
    pytest.param([[_row(0, 900.0)], [_row(1, 830.0)], [_row(2, 756.0), _row(2, 764.0, offset=1)]], id="ambiguous"),
])
def test_no_seed_outside_the_frozen_conditions(frames):
    assert _resolve(frames).fast_rise_seed_frames == ()


def test_the_mark_clears_when_the_rise_slows_and_a_stopped_row_is_lost():
    frames = _rising(70.0, count=4)  # 900, 830, 760, 690
    frames += [[_row(4, 680.0)], [_row(5, 675.0)]]  # the level stops at the top
    result = _resolve(frames)
    ids = _ids(result)
    assert result.fast_rise_seed_frames == (2,)
    assert ids[0] == ids[1] == ids[2] == ids[3]
    assert ids[4] != ids[3]  # 10 px against a 70 px/sample prediction fails the prediction gate


@pytest.mark.parametrize("other", [{"cost_first_assignment": True}, {"candidate_rgb": True}])
def test_rejected_mechanisms_cannot_be_stacked_with_fast_rise(other):
    with pytest.raises(ValueError, match="Compare the fast-rise association"):
        OpenCvPhaseDetector(fast_rise_association=True, **other)


def test_fast_rise_combines_with_the_integrated_candidate():
    detector = OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True, fast_rise_association=True)
    resolver = detector._observation_sequence_resolver
    assert resolver._oil.config.fast_rise_association_enabled is True
    for version in (detector.version, resolver.version, resolver._oil.version):
        assert version.endswith("+initial-full-observation-v2+top-exit-full-v3+fast-rise-association-v1")
