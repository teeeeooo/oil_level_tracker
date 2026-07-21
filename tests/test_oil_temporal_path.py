from __future__ import annotations

from oil_tracker.adapters.vision.oil_no_interface import NoInterfaceEvidence
from oil_tracker.adapters.vision.oil_temporal_path import OilDecisionStatus, OilTemporalPath
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings


def candidate(y: float, score: float = 0.86, support: int = 3, polarity: float = 1.0):
    value = BoundaryCandidate(
        "oil_consensus",
        BoundaryKind.OIL_AIR,
        y,
        {
            "observation_score": score,
            "unique_generator_support_count": float(support),
            "polarity_score": abs(polarity) * 0.8,
            "polarity_sign": polarity,
            "polarity_available": 1.0,
        },
    )
    value.final_score = score
    return value


def no_interface(score: float = 0.05, *, available: bool = True):
    return NoInterfaceEvidence(
        score=score,
        boundary_score=0.0,
        uniformity_score=0.9,
        weak_boundary_score=0.9,
        visibility_score=1.0,
        glare_conflict=0.0,
        prior_score=0.0,
        mean_intensity=80.0,
        texture=2.0,
        reason="uniform_region_with_weak_boundary",
        available=available,
    )


def settings(**values):
    base = DetectorSettings(
        minimum_final_confidence=0.42,
        oil_tracker_update_confidence=0.55,
        oil_path_min_margin=0.08,
        oil_path_window=4,
        oil_path_beam_width=4,
        candidate_top_k=8,
        oil_reacquire_frames=2,
        temporal_max_jump_px=12.0,
    )
    for name, value in values.items():
        setattr(base, name, value)
    return base


def test_confident_boundary_updates_prior_and_is_deterministic():
    first = OilTemporalPath()
    second = OilTemporalPath()
    decisions_a = [first.evaluate([candidate(y)], no_interface(), settings()) for y in (20.0, 22.0, 24.0)]
    decisions_b = [second.evaluate([candidate(y)], no_interface(), settings()) for y in (20.0, 22.0, 24.0)]
    assert [item.status for item in decisions_a] == [item.status for item in decisions_b]
    assert all(item.status is OilDecisionStatus.ACCEPTED_BOUNDARY for item in decisions_a)
    assert first.accepted_y == 24.0
    assert decisions_a[-1].tracker_update_accepted


def test_low_confidence_and_rejected_candidates_do_not_update_prior():
    path = OilTemporalPath()
    accepted = path.evaluate([candidate(20.0)], no_interface(), settings())
    assert accepted.status is OilDecisionStatus.ACCEPTED_BOUNDARY
    low = path.evaluate([candidate(35.0, score=0.30)], no_interface(score=0.25), settings())
    assert low.status is not OilDecisionStatus.ACCEPTED_BOUNDARY
    assert not low.tracker_update_accepted
    assert path.accepted_y == 20.0
    rejected = candidate(40.0)
    rejected.rejected = True
    rejected.reject_reason = "test"
    missing = path.evaluate([rejected], no_interface(score=0.20, available=False), settings())
    assert missing.raw_y is None
    assert path.accepted_y == 20.0


def test_low_margin_is_ambiguous_and_does_not_update():
    path = OilTemporalPath()
    decision = path.evaluate(
        [candidate(20.0, 0.80), candidate(24.0, 0.78)],
        no_interface(0.05),
        settings(oil_path_min_margin=0.10),
    )
    assert decision.status is OilDecisionStatus.LOW_MARGIN
    assert decision.raw_y is None
    assert path.accepted_y is None
    assert "OIL_PATH_LOW_MARGIN" in decision.flags


def test_transient_large_false_line_does_not_contaminate_prior():
    path = OilTemporalPath()
    assert path.evaluate([candidate(20.0)], no_interface(), settings()).tracker_update_accepted
    transient = path.evaluate([candidate(70.0, 0.82)], no_interface(0.20), settings())
    assert transient.status in {
        OilDecisionStatus.REACQUISITION_PENDING,
        OilDecisionStatus.PATH_PENDING,
        OilDecisionStatus.LOW_MARGIN,
    }
    assert transient.raw_y is None
    assert path.accepted_y == 20.0
    recovered = path.evaluate([candidate(22.0)], no_interface(), settings())
    assert recovered.status is OilDecisionStatus.ACCEPTED_BOUNDARY
    assert path.accepted_y == 22.0


def test_large_consistent_new_path_reacquires_and_requests_smoothing_clear():
    path = OilTemporalPath()
    path.evaluate([candidate(20.0)], no_interface(), settings())
    pending = path.evaluate([candidate(70.0)], no_interface(0.10), settings())
    assert pending.status is OilDecisionStatus.REACQUISITION_PENDING
    accepted = path.evaluate([candidate(72.0)], no_interface(0.10), settings())
    assert accepted.status is OilDecisionStatus.ACCEPTED_BOUNDARY
    assert accepted.clear_smoothing
    assert "OIL_REACQUIRED" in accepted.flags
    assert path.accepted_y == 72.0


def test_rapid_continuous_motion_is_not_hard_rejected():
    path = OilTemporalPath()
    outputs = [
        path.evaluate([candidate(y, 0.90)], no_interface(), settings(temporal_max_jump_px=10.0))
        for y in (20.0, 31.0, 42.0, 53.0)
    ]
    assert all(item.status is OilDecisionStatus.ACCEPTED_BOUNDARY for item in outputs)
    assert path.accepted_y == 53.0


def test_no_interface_is_explicit_and_stably_invalidates_numeric_prior():
    path = OilTemporalPath()
    path.evaluate([candidate(20.0)], no_interface(), settings())
    first = path.evaluate([], no_interface(0.90), settings())
    second = path.evaluate([], no_interface(0.90), settings())
    assert first.status is OilDecisionStatus.NO_INTERFACE_SELECTED
    assert first.raw_y is None
    assert second.status is OilDecisionStatus.NO_INTERFACE_SELECTED
    assert second.clear_smoothing
    assert path.accepted_y is None


def test_dropout_history_and_beam_are_bounded_and_resettable():
    path = OilTemporalPath()
    config = settings(oil_path_window=3, oil_path_beam_width=2)
    for index in range(12):
        values = [] if index in {4, 5} else [candidate(20.0 + index)]
        path.evaluate(values, no_interface(0.05, available=bool(values)), config)
        assert path.beam_count <= 2
        assert path.retained_scalar_observation_count <= 3 * 2
    path.reset()
    assert path.beam_count == 0
    assert path.retained_scalar_observation_count == 0
    assert path.accepted_y is None
