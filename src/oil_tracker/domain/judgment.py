"""The computed judgment of one Glass from its edited Oil line (Product SSOT §5).

Heights are source-frame pixels from the zero line, positive upward. Only valid samples count: an
empty Oil sample or one in a "cannot judge" stretch says nothing about the level (§4). The measures
are found even when the valid share is too low, so the editor can show them beside "검토 필요".

Agent's choices where §5 is silent (2026-10-30):
- A recovery holds when every valid sample from its start to `stable_hold_sec` later is at or above
  zero and the analysis reaches that far; invalid samples inside it are passed over (as in v1).
- A violation run is consecutive violating samples; an invalid sample ends it. Its length is its
  sample count times the sample step, so one violating sample lasts 0.5 s.
- The HOLD modes look at the whole analysis range; only RECOVERY uses the compressor start.
"""

from __future__ import annotations

from dataclasses import dataclass

from .edits import Coverage, Decision, GlassEdits, cannot_judge_flags, coverage
from .enums import JudgmentMode, Verdict
from .inspection import ANALYSIS_RATE
from .recipe import Glass

STEP_SEC = 1.0 / ANALYSIS_RATE
EPSILON = 1e-9


@dataclass(frozen=True)
class Recovery:
    """The first stretch after the compressor start at or above zero that holds."""

    first: int          # its first sample
    after_sec: float    # from the compressor start


@dataclass(frozen=True)
class Violation:
    """The longest run of violating samples in a HOLD mode."""

    first: int          # sample indices [first, end)
    end: int
    seconds: float
    worst_px: float     # the furthest past zero on the forbidden side


@dataclass(frozen=True)
class Judgment:
    verdict: Verdict
    reason: str
    coverage: Coverage
    recovery: Recovery | None = None    # RECOVERY only
    violation: Violation | None = None  # the HOLD modes only; None when nothing violates


def judge(times: tuple[float, ...], edits: GlassEdits, glass: Glass, compressor_start_sec: float | None) -> Judgment:
    rule = glass.judgment_rule
    cover = coverage(times, edits)
    flags = cannot_judge_flags(times, edits.cannot_judge)
    heights = tuple(None if y is None or flagged else glass.zero_line_y - y for y, flagged in zip(edits.oil.ys, flags))

    if rule.mode is JudgmentMode.RECOVERY:
        if compressor_start_sec is None:
            return Judgment(Verdict.REVIEW, "기준점 회복 판정에는 압축기 기동 시각이 필요합니다.", cover)
        recovery = find_recovery(times, heights, compressor_start_sec, rule.stable_hold_sec)
        low = _too_few(cover, rule.minimum_valid_coverage_ratio)
        if low:
            return Judgment(Verdict.REVIEW, low, cover, recovery=recovery)
        if recovery is None:
            reason = f"기동 뒤 0선 이상에서 {_s(rule.stable_hold_sec)}초를 유지한 구간이 없습니다."
            return Judgment(Verdict.FAIL, reason, cover)
        if recovery.after_sec <= rule.recovery_limit_sec + EPSILON:
            reason = f"기동 후 {_s(recovery.after_sec)}초에 0선을 회복해 {_s(rule.stable_hold_sec)}초 이상 유지했습니다."
            return Judgment(Verdict.PASS, reason, cover, recovery=recovery)
        reason = f"기동 후 {_s(recovery.after_sec)}초에 회복해 한도 {_s(rule.recovery_limit_sec)}초를 넘었습니다."
        return Judgment(Verdict.FAIL, reason, cover, recovery=recovery)

    sign = 1.0 if rule.mode is JudgmentMode.HOLD_BELOW_ZERO else -1.0  # past zero on the forbidden side
    violation = longest_violation(tuple(None if h is None else sign * h for h in heights), rule.allowed_px)
    low = _too_few(cover, rule.minimum_valid_coverage_ratio)
    if low:
        return Judgment(Verdict.REVIEW, low, cover, violation=violation)
    if violation is None:
        return Judgment(Verdict.PASS, "위반이 없습니다.", cover)
    if violation.seconds <= rule.allowed_sec + EPSILON:
        reason = f"가장 긴 위반 {_s(violation.seconds)}초가 허용 {_s(rule.allowed_sec)}초 이내입니다."
        return Judgment(Verdict.PASS, reason, cover, violation=violation)
    reason = f"가장 긴 위반 {_s(violation.seconds)}초가 허용 {_s(rule.allowed_sec)}초를 넘었습니다."
    return Judgment(Verdict.FAIL, reason, cover, violation=violation)


def final_verdict(judgment: Judgment, decision: Decision) -> Verdict:
    """The user's verdict where they judged the Glass themselves, else the computed one (§3)."""
    return decision.override or judgment.verdict


def find_recovery(
    times: tuple[float, ...], heights: tuple[float | None, ...], start_sec: float, hold_sec: float
) -> Recovery | None:
    """The first valid sample at or after the start, at or above zero, from which every valid sample
    stays at or above zero for hold_sec, within the analysis."""
    last = times[-1] if times else 0.0
    for i, (t, h) in enumerate(zip(times, heights)):
        if t < start_sec - EPSILON or h is None or h < 0:
            continue
        until = t + hold_sec
        if last < until - EPSILON:
            return None  # every later start ends past the analysis too
        j = i
        while j < len(times) and times[j] <= until + EPSILON and (heights[j] is None or heights[j] >= 0):
            j += 1
        if j == len(times) or times[j] > until + EPSILON:
            return Recovery(i, t - start_sec)
    return None


def longest_violation(beyond: tuple[float | None, ...], allowed_px: float) -> Violation | None:
    """The longest run of samples more than allowed_px past zero; the first of equal ones."""
    best: Violation | None = None
    first: int | None = None
    for i, value in enumerate((*beyond, None)):
        if value is not None and value > allowed_px + EPSILON:
            if first is None:
                first = i
            continue
        if first is not None:
            run = Violation(first, i, (i - first) * STEP_SEC, max(beyond[k] for k in range(first, i)))
            if best is None or run.end - run.first > best.end - best.first:
                best = run
            first = None
    return best


def _too_few(cover: Coverage, minimum: float) -> str | None:
    if cover.valid_ratio >= minimum - EPSILON:
        return None
    return f"유효 비율 {cover.valid_ratio:.0%}가 기준 {minimum:.0%}보다 낮습니다."


def _s(seconds: float) -> str:
    return f"{seconds:g}" if seconds == int(seconds) else f"{seconds:.1f}"
