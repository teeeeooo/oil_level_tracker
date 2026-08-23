from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from oil_tracker.application.services.initial_state_reconstruction import (
    annotate_judgment_provenance,
    effective_state_aware_coverage,
    enforce_conflict_review,
    merge_state_aware_events,
    observed_coverage,
    project_state_aware_samples,
    reconstruct_initial_state,
    samples_for_judgment,
)
from oil_tracker.domain.enums import EventType, ResultState
from oil_tracker.domain.events import detect_events_for_glass
from oil_tracker.domain.judgment import JudgmentOutcome, judge_samples
from oil_tracker.domain.recipe import GlassInspectionConfig
from oil_tracker.domain.results import EventMarker, TrackingSample
from oil_tracker.domain.retrospective import RetrospectiveInterpretation


class StateAwareOutcomeMode(str, Enum):
    OFFICIAL_ANALYSIS = "official_analysis"
    FULL_REDETECTION = "full_redetection"
    INTERVAL_REDETECTION = "interval_redetection"


@dataclass(frozen=True)
class StateAwareOutcome:
    retrospective: RetrospectiveInterpretation | None
    events: tuple[EventMarker, ...]
    judgment: JudgmentOutcome | None
    observed_coverage_ratio: float | None
    effective_coverage_ratio: float | None


class StateAwareOutcomeAssembler:
    """Build events and judgment from one completed observed sample stream."""

    def assemble(
        self,
        *,
        run_id: str,
        glass: GlassInspectionConfig,
        samples: Sequence[TrackingSample],
        confirmation,
        compressor_start_sec: float | None,
        mode: StateAwareOutcomeMode,
    ) -> StateAwareOutcome:
        observed_samples = list(samples)
        retrospective = self._retrospective(
            glass,
            observed_samples,
            confirmation,
            mode,
        )
        effective_samples = project_state_aware_samples(
            observed_samples,
            retrospective,
        )
        observed_events = detect_events_for_glass(
            run_id,
            glass.id,
            observed_samples,
        )
        projected_events = detect_events_for_glass(
            run_id,
            glass.id,
            effective_samples,
        )
        events = merge_state_aware_events(
            observed_events,
            projected_events,
            retrospective,
        )

        judgment = None
        observed_ratio = None
        effective_ratio = None
        if mode is not StateAwareOutcomeMode.INTERVAL_REDETECTION:
            if compressor_start_sec is not None:
                closest = min(
                    observed_samples,
                    key=lambda sample: abs(
                        sample.timestamp_sec - compressor_start_sec
                    ),
                )
                representative = closest.frame_index
                if (
                    mode is StateAwareOutcomeMode.FULL_REDETECTION
                    and representative < 0
                ):
                    representative = None
                events.append(
                    EventMarker(
                        run_id,
                        glass.id,
                        EventType.COMPRESSOR_START,
                        compressor_start_sec,
                        representative_frame_index=representative,
                        confidence=1.0,
                    )
                )
            judgment_samples = samples_for_judgment(
                observed_samples,
                retrospective,
                glass.judgment_rule.mode,
            )
            judgment = judge_samples(
                judgment_samples,
                glass.judgment_rule,
                compressor_start_sec,
            )
            judgment = annotate_judgment_provenance(
                judgment,
                retrospective,
                glass.judgment_rule.mode,
            )
            judgment = enforce_conflict_review(judgment, retrospective)
            last_frame_index = observed_samples[-1].frame_index
            if (
                mode is StateAwareOutcomeMode.FULL_REDETECTION
                and last_frame_index < 0
            ):
                last_frame_index = None
            events.append(
                EventMarker(
                    run_id,
                    glass.id,
                    EventType.JUDGMENT_PASS
                    if judgment.state is ResultState.PASS
                    else EventType.JUDGMENT_FAIL
                    if judgment.state is ResultState.FAIL
                    else EventType.REVIEW_REQUIRED,
                    observed_samples[-1].timestamp_sec,
                    representative_frame_index=last_frame_index,
                    confidence=judgment.valid_coverage_ratio,
                    note=judgment.note,
                )
            )
            observed_ratio = observed_coverage(observed_samples)
            effective_ratio = effective_state_aware_coverage(
                observed_samples,
                retrospective,
            )

        return StateAwareOutcome(
            retrospective=retrospective,
            events=tuple(events),
            judgment=judgment,
            observed_coverage_ratio=observed_ratio,
            effective_coverage_ratio=effective_ratio,
        )

    @staticmethod
    def _retrospective(
        glass: GlassInspectionConfig,
        samples: list[TrackingSample],
        confirmation,
        mode: StateAwareOutcomeMode,
    ) -> RetrospectiveInterpretation | None:
        if mode is StateAwareOutcomeMode.INTERVAL_REDETECTION:
            return None
        if (
            mode is StateAwareOutcomeMode.FULL_REDETECTION
            and confirmation is None
        ):
            return None
        return reconstruct_initial_state(glass, samples, confirmation)
