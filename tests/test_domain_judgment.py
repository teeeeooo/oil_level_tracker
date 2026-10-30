"""Fixed cases for the judgment rule (Product SSOT §5, acceptance A3)."""

import pytest

from oil_tracker.domain.edits import GlassEdits, Stretch, empty_line
from oil_tracker.domain.enums import JudgmentMode, SampleOrigin
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.judgment import Verdict, judge
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass, JudgmentRule

ZERO = 100.0  # the zero line's source y; a height h is the sample at y = ZERO - h


def case(heights, mode=JudgmentMode.RECOVERY, compressor=0.0, cannot=(), **rule):
    """Judge Oil heights sampled every 0.5 s from t = 0; None is an empty sample."""
    times = tuple(0.5 * i for i in range(len(heights)))
    ys = tuple(None if h is None else ZERO - h for h in heights)
    oil = Line(ys, (SampleOrigin.DRAFT,) * len(ys))
    edits = GlassEdits("g1", oil, empty_line(len(ys)), empty_line(len(ys)), tuple(Stretch(*s) for s in cannot))
    glass = Glass("g1", "BASE", Ellipse(50, 100, 40, 90), ZERO, JudgmentRule(mode=mode, **rule))
    return judge(times, edits, glass, compressor)


def secs(seconds, height):
    return [height] * round(seconds * 2)


# ---- RECOVERY: after the compressor start, at or above zero for stable_hold_sec, starting within
# recovery_limit_sec (defaults 120 s and 5 s) ----


def test_recovery_within_the_limit_passes():
    found = case(secs(30, -10) + secs(20, 5), compressor=10.0)
    assert found.verdict is Verdict.PASS
    assert found.recovery.first == 60 and found.recovery.after_sec == pytest.approx(20.0)
    assert "20초" in found.reason


def test_recovery_exactly_at_the_limit_passes_and_after_it_fails():
    assert case(secs(130, -10) + secs(10, 0), compressor=10.0).verdict is Verdict.PASS  # zero counts: 120.0 s
    late = case(secs(130.5, -10) + secs(10, 0), compressor=10.0)
    assert late.verdict is Verdict.FAIL and late.recovery.after_sec == pytest.approx(120.5)
    assert "한도 120초를 넘었습니다" in late.reason


def test_a_dip_inside_the_hold_restarts_it():
    heights = secs(10, -10) + secs(3, 5) + [-1] + secs(10, 5)
    found = case(heights, compressor=0.0)
    assert found.verdict is Verdict.PASS and found.recovery.first == 27  # after the dip at 13 s


def test_no_recovery_fails():
    found = case(secs(60, -10) + secs(4, 5), compressor=0.0)  # 4 s above zero at the end: not held
    assert found.verdict is Verdict.FAIL and found.recovery is None
    assert "5초를 유지한 구간이 없습니다" in found.reason


def test_the_hold_must_fit_in_the_analysis():
    found = case(secs(10, -10) + [5] * 10, compressor=0.0)  # 5 samples less than the 11 a 5 s hold spans
    assert found.recovery is None
    assert case(secs(10, -10) + [5] * 11, compressor=0.0).recovery.first == 20


def test_before_the_compressor_start_does_not_count():
    found = case(secs(20, 5) + secs(20, -10) + secs(10, 5), compressor=20.0)
    assert found.recovery.first == 80 and found.recovery.after_sec == pytest.approx(20.0)


def test_already_above_zero_at_the_start_recovers_at_once():
    assert case(secs(30, 5), compressor=5.0).recovery.after_sec == 0.0


def test_invalid_samples_inside_the_hold_are_passed_over():
    heights = secs(10, -10) + secs(2, 5) + [None, None] + secs(5, 5)
    assert case(heights, compressor=0.0).recovery.first == 20
    cannot = case(secs(10, -10) + secs(2, 5) + [-30, -30] + secs(5, 5), compressor=0.0, cannot=[(12.0, 13.0)])
    assert cannot.recovery.first == 20  # the dip lies in a "cannot judge" stretch


def test_recovery_needs_a_compressor_start():
    found = case(secs(30, 5), compressor=None)
    assert found.verdict is Verdict.REVIEW and "압축기 기동" in found.reason


# ---- coverage: empty and "cannot judge" samples are invalid; below the minimum is "검토 필요" ----


def test_too_few_valid_samples_need_review_but_keep_the_measures():
    heights = secs(10, 5) + [None] * 21  # 20 of 41 valid
    found = case(heights, compressor=0.0)
    assert found.verdict is Verdict.REVIEW and found.recovery.first == 0
    assert found.coverage.valid == 20 and "49%" in found.reason


def test_exactly_the_minimum_is_enough():
    heights = secs(35, 5) + [None] * 30  # 70 of 100 valid
    assert case(heights, compressor=0.0).verdict is Verdict.PASS
    assert case(heights[:-1] + [None, None], compressor=0.0).verdict is Verdict.REVIEW  # 69 of 101


def test_cannot_judge_counts_against_coverage():
    found = case(secs(50, 5), compressor=0.0, cannot=[(0.0, 31.0)])
    assert found.coverage.cannot_judge == 62 and found.verdict is Verdict.REVIEW


# ---- HOLD_BELOW_ZERO and HOLD_ABOVE_ZERO: the longest continuous violation against allowed_sec
# (default 5 s), more than allowed_px (default 0) past zero ----


def test_hold_below_without_a_violation_passes():
    found = case(secs(30, -5) + secs(10, 0), mode=JudgmentMode.HOLD_BELOW_ZERO)
    assert found.verdict is Verdict.PASS and found.violation is None and found.reason == "위반이 없습니다."


def test_the_longest_violation_against_the_allowed_time():
    five = case(secs(10, -5) + secs(5, 3) + secs(10, -5), mode=JudgmentMode.HOLD_BELOW_ZERO)
    assert five.verdict is Verdict.PASS and five.violation.seconds == 5.0
    longer = case(secs(10, -5) + secs(5.5, 3) + secs(10, -5), mode=JudgmentMode.HOLD_BELOW_ZERO)
    assert longer.verdict is Verdict.FAIL and (longer.violation.first, longer.violation.end) == (20, 31)


def test_separate_violations_do_not_add_up():
    # v1 measured from the first violating sample to the last; v2 takes the longest run (§5)
    heights = secs(4, 3) + secs(30, -5) + secs(4, 7)
    found = case(heights, mode=JudgmentMode.HOLD_BELOW_ZERO)
    assert found.verdict is Verdict.PASS and found.violation.first == 0
    assert found.violation.seconds == 4.0 and found.violation.worst_px == 3.0  # the first of equal runs


def test_allowed_px_is_a_margin():
    at = case(secs(10, 2) + secs(10, -5), mode=JudgmentMode.HOLD_BELOW_ZERO, allowed_px=2.0)
    assert at.violation is None
    past = case(secs(10, 2.5) + secs(10, -5), mode=JudgmentMode.HOLD_BELOW_ZERO, allowed_px=2.0)
    assert past.verdict is Verdict.FAIL and past.violation.worst_px == 2.5


def test_an_invalid_sample_ends_a_run():
    heights = secs(3, 4) + [None] + secs(3, 4) + secs(30, -5)
    found = case(heights, mode=JudgmentMode.HOLD_BELOW_ZERO)
    assert found.verdict is Verdict.PASS and found.violation.seconds == 3.0


def test_hold_above_mirrors_hold_below():
    found = case(secs(10, 5) + secs(6, -4) + secs(10, 5), mode=JudgmentMode.HOLD_ABOVE_ZERO)
    assert found.verdict is Verdict.FAIL and found.violation.seconds == 6.0 and found.violation.worst_px == 4.0
    assert "허용 5초를 넘었습니다" in found.reason
    assert case(secs(30, 5), mode=JudgmentMode.HOLD_ABOVE_ZERO).verdict is Verdict.PASS


def test_the_hold_modes_ignore_the_compressor_start():
    heights = secs(10, 3) + secs(30, -5)
    assert case(heights, mode=JudgmentMode.HOLD_BELOW_ZERO, compressor=None).verdict is Verdict.FAIL
    assert case(heights, mode=JudgmentMode.HOLD_BELOW_ZERO, compressor=20.0).verdict is Verdict.FAIL


def test_a_full_glass_violates_hold_below_and_an_empty_one_hold_above():
    full = case(secs(6, 90) + secs(30, -5), mode=JudgmentMode.HOLD_BELOW_ZERO)  # at the Glass top
    empty = case(secs(6, -90) + secs(30, 5), mode=JudgmentMode.HOLD_ABOVE_ZERO)  # at the bottom
    assert full.verdict is Verdict.FAIL and empty.verdict is Verdict.FAIL


def test_foam_never_affects_the_judgment():
    times = tuple(0.5 * i for i in range(60))
    oil = Line(tuple(ZERO + 5 for _ in times), (SampleOrigin.DRAFT,) * 60)
    foam = Line(tuple(ZERO - 50 for _ in times), (SampleOrigin.DRAWN,) * 60)  # far above zero
    glass = Glass("g1", "BASE", Ellipse(50, 100, 40, 90), ZERO, JudgmentRule(mode=JudgmentMode.HOLD_BELOW_ZERO))
    assert judge(times, GlassEdits("g1", oil, foam, empty_line(60)), glass, None).verdict is Verdict.PASS
