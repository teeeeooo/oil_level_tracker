from oil_tracker.domain.enums import FillState, JudgmentMode, ResultState
from oil_tracker.domain.judgment import judge_samples
from oil_tracker.domain.recipe import JudgmentRule
from oil_tracker.domain.results import TrackingSample


def sample(t, level, valid=True):
    return TrackingSample("r", "g", int(t*10), t, FillState.PARTIAL_VISIBLE, smoothed_oil_air_level_px_from_zero=level, overall_confidence=.9, is_valid=valid)


def test_recovery_passes_after_stable_hold():
    samples = [sample(0, -5), sample(1, 1), sample(2, 2), sample(3, 2)]
    rule = JudgmentRule(mode=JudgmentMode.RECOVERY, recovery_limit_sec=4, stable_hold_sec=2, minimum_valid_coverage_ratio=.5)
    assert judge_samples(samples, rule, 0).state == ResultState.PASS


def test_low_coverage_requires_review():
    samples = [sample(0, -1, False), sample(1, 2, True), sample(2, 2, False)]
    rule = JudgmentRule(minimum_valid_coverage_ratio=.8)
    assert judge_samples(samples, rule, 0).state == ResultState.REVIEW_REQUIRED


def test_hold_above_fails_on_long_violation():
    samples = [sample(0, 2), sample(1, -3), sample(3, -2)]
    rule = JudgmentRule(mode=JudgmentMode.HOLD_ABOVE_ZERO, allowed_violation_sec=.5)
    assert judge_samples(samples, rule, None).state == ResultState.FAIL
