import pytest

from tests.diagnostics import s11_fast_fill_cadence as fff

ESTIMATES = [{"t": 10.0, "y": 800.0}, {"t": 14.0, "y": 600.0}]


def _candidate(y, admitted, reason=None):
    return {"y": y, "sequence_tracklet_admitted": admitted, "sequence_tracklet_failure_reason": reason}


def _frame(candidates, published=None, reason="FILL_MOTION_OWNER"):
    return {"oil_candidates": candidates, "published_oil_y": published, "reason": reason}


def test_surface_interpolates_inside_and_is_none_outside():
    assert fff.surface_at(ESTIMATES, 12.0) == pytest.approx(700.0)
    assert fff.surface_at(ESTIMATES, 9.5) is None
    assert fff.surface_at(ESTIMATES, 14.5) is None


def test_readings_count_admitted_level_and_net_progress_frames():
    readout = [
        _frame([_candidate(805.0, True)], published=805.0),                      # 10 s: admitted near the level
        _frame([_candidate(752.0, False, "INSUFFICIENT_NET_PROGRESS")]),         # 11 s: level 750, unadmitted
        _frame([_candidate(702.0, False, "INSUFFICIENT_AUTHORITY"),
                _candidate(780.0, True)], reason="FILL_OWNER_AMBIGUOUS"),        # 12 s: admitted row is 80 px off
        _frame([_candidate(640.0, False, "INSUFFICIENT_NET_PROGRESS")]),         # 13 s: level 650
        _frame([_candidate(600.0, True)]),                                      # 15 s: outside the estimates
    ]
    out = fff.readings(readout, [10.0, 11.0, 12.0, 13.0, 15.0], ESTIMATES, (10.0, 16.0))
    assert out["frames"] == 4
    assert out["level_admitted_frames"] == 1
    assert out["near_level_unadmitted_only_frames"] == 3
    assert out["net_progress_frames"] == 2
    assert out["unadmitted_reasons"] == {"INSUFFICIENT_NET_PROGRESS": 2, "INSUFFICIENT_AUTHORITY": 1}
    assert out["m3_holds"] is True
    assert out["fill_owner_ambiguous_frames"] == 1
    assert out["published_offsets_px"] == [5.0]


def test_m3_needs_net_progress_as_the_commonest_reason():
    readout = [_frame([_candidate(800.0, False, "INSUFFICIENT_AUTHORITY")]),
               _frame([_candidate(750.0, False, "INSUFFICIENT_AUTHORITY")])]
    out = fff.readings(readout, [10.0, 11.0], ESTIMATES, (10.0, 14.0))
    assert out["m3_holds"] is False and out["net_progress_frames"] == 0


def test_association_cap_narrows_only_the_tracklet_jump_and_restores_it():
    from oil_tracker.adapters.vision import oil_observation_resolver as resolver

    original = resolver._tracklet_policy
    calls = []

    def fake(*args, **kwargs):
        calls.append(args)
        from oil_tracker.adapters.vision.oil_interface_tracklets import DirectedTrackletPolicy
        return DirectedTrackletPolicy(
            geometry_top_y=0.0, geometry_height=500.0, maximum_jump_px=32.0, row_hypothesis_tolerance_px=12.0,
            maximum_lost_frames=2, confirmation_window_frames=6, confirmation_min_observations=3,
            confirmation_min_anchor_frames=3, confirmation_min_progress_px=25.0,
            confirmation_min_directional_agreement=0.6, confirmation_min_motion_support=0.2,
            confirmation_min_motion_coverage=0.2, continuation_grace_frames=2,
            continuation_min_motion_energy=0.1, continuation_min_motion_coverage=0.1)

    resolver._tracklet_policy = fake
    try:
        with fff.association_cap(9.0):
            policy = resolver._tracklet_policy("refs", "glass", "config")
        assert policy.maximum_jump_px == 9.0
        assert policy.row_hypothesis_tolerance_px == 12.0  # the row tolerance keeps the Recipe-derived value
        assert resolver._tracklet_policy is fake
        with fff.association_cap(None):
            assert resolver._tracklet_policy is fake
    finally:
        resolver._tracklet_policy = original
