from __future__ import annotations

from dataclasses import dataclass

from .enums import FillState, JudgmentMode, ResultState
from .recipe import JudgmentRule
from .results import TrackingSample


@dataclass(frozen=True)
class JudgmentOutcome:
    state: ResultState
    valid_coverage_ratio: float
    note: str


def judge_samples(samples: list[TrackingSample], rule: JudgmentRule, compressor_start_sec: float | None) -> JudgmentOutcome:
    if not samples:
        return JudgmentOutcome(ResultState.REVIEW_REQUIRED, 0.0, "No tracking samples were produced.")

    valid = [s for s in samples if s.is_valid]
    coverage = len(valid) / len(samples)
    if coverage < rule.minimum_valid_coverage_ratio:
        return JudgmentOutcome(
            ResultState.REVIEW_REQUIRED,
            coverage,
            f"Valid sample coverage {coverage:.1%} is below {rule.minimum_valid_coverage_ratio:.1%}.",
        )

    if rule.mode == JudgmentMode.RECOVERY:
        if compressor_start_sec is None:
            return JudgmentOutcome(ResultState.REVIEW_REQUIRED, coverage, "Compressor start is required for RECOVERY.")
        deadline = compressor_start_sec + rule.recovery_limit_sec
        eligible = [s for s in valid if s.timestamp_sec >= compressor_start_sec]
        for start_index, sample in enumerate(eligible):
            level = sample.smoothed_oil_air_level_px_from_zero
            if level is None or level < 0:
                continue
            hold_end = sample.timestamp_sec + rule.stable_hold_sec
            held = [x for x in eligible[start_index:] if x.timestamp_sec <= hold_end]
            if held and held[-1].timestamp_sec >= hold_end - 1e-6 and all(
                x.smoothed_oil_air_level_px_from_zero is not None and x.smoothed_oil_air_level_px_from_zero >= 0 for x in held
            ):
                if sample.timestamp_sec <= deadline:
                    return JudgmentOutcome(ResultState.PASS, coverage, f"Recovered above zero at {sample.timestamp_sec:.2f}s and held.")
                return JudgmentOutcome(ResultState.FAIL, coverage, "Recovery occurred after the configured deadline.")
        return JudgmentOutcome(ResultState.FAIL, coverage, "Stable recovery above zero was not detected.")

    if rule.mode == JudgmentMode.HOLD_BELOW_ZERO:
        violating = [
            s for s in valid
            if s.fill_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}
            or (s.smoothed_oil_air_level_px_from_zero is not None and s.smoothed_oil_air_level_px_from_zero > rule.allowed_excursion_height)
        ]
        if not violating:
            return JudgmentOutcome(ResultState.PASS, coverage, "Oil level remained below zero within configured tolerance.")
        duration = _duration(violating)
        state = ResultState.FAIL if duration > rule.allowed_excursion_sec else ResultState.PASS
        return JudgmentOutcome(state, coverage, f"Above-zero excursion duration: {duration:.2f}s.")

    violating = [
        s for s in valid
        if s.fill_state == FillState.EMPTY_NO_INTERFACE
        or (s.smoothed_oil_air_level_px_from_zero is not None and s.smoothed_oil_air_level_px_from_zero < -rule.allowed_violation_depth)
    ]
    if not violating:
        return JudgmentOutcome(ResultState.PASS, coverage, "Oil level remained above zero within configured tolerance.")
    duration = _duration(violating)
    state = ResultState.FAIL if duration > rule.allowed_violation_sec else ResultState.PASS
    return JudgmentOutcome(state, coverage, f"Below-zero violation duration: {duration:.2f}s.")


def _duration(samples: list[TrackingSample]) -> float:
    if len(samples) < 2:
        return 0.0
    return max(0.0, samples[-1].timestamp_sec - samples[0].timestamp_sec)
