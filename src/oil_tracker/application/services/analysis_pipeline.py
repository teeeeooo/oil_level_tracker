from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import time
from typing import Callable
from uuid import uuid4

from oil_tracker.application.ports.phase_detector import AnalysisDetector
from oil_tracker.application.ports.progress import (
    AnalysisCancelled,
    AnalysisStage,
    CancellationToken,
    ProgressSink,
    build_progress_update,
)
from oil_tracker.application.services.analysis_outcome import (
    StateAwareOutcomeAssembler,
    StateAwareOutcomeMode,
)
from oil_tracker.application.services.debug_capture_policy import DebugCapturePolicy
from oil_tracker.application.services.detection_processing import (
    effective_observation_height,
    tracking_sample_from_detection,
)
from oil_tracker.application.services.detection_run import (
    DetectionRunCoordinator,
    DetectionRunPolicy,
    DetectionTarget,
    SequenceResolutionMode,
)
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.enums import ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult, TrackingSample
from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel


@dataclass
class SimpleCancellationToken:
    _cancelled: bool = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        self._cancelled = True


class AnalysisPipeline:
    def __init__(
        self,
        video_reader_factory: Callable[[str], object],
        detector: AnalysisDetector,
        validator: RecipeValidationService,
        debug_trace_sink_factory=None,
        capture_policy: DebugCapturePolicy | None = None,
        outcome_assembler: StateAwareOutcomeAssembler | None = None,
    ) -> None:
        self.video_reader_factory = video_reader_factory
        self.detector = detector
        self.validator = validator
        self.debug_trace_sink_factory = debug_trace_sink_factory
        self.capture_policy = capture_policy or DebugCapturePolicy()
        self.outcome_assembler = outcome_assembler or StateAwareOutcomeAssembler()

    def run(
        self,
        recipe: InspectionRecipe,
        session: AnalysisSession,
        progress: ProgressSink | None = None,
        cancellation: CancellationToken | None = None,
    ) -> AnalysisResult:
        validation = self.validator.validate(
            recipe,
            session,
            require_run_confirmation=True,
        )
        if not validation.is_ready:
            messages = "; ".join(i.message for i in validation.errors)
            raise ValueError(f"Workbench is not ready: {messages}")

        run_id = str(uuid4())
        started = datetime.now(timezone.utc)
        enabled = [g for g in recipe.glasses if g.enabled]
        schedules = timestamp_schedule(
            session.analysis_start_sec,
            session.effective_end_sec() or 0.0,
            session.sampling_fps,
        )
        if not schedules:
            raise ValueError("Timestamp schedule is empty.")
        detections_by_glass = {g.id: [] for g in enabled}
        by_glass: dict[str, list[TrackingSample]] = {g.id: [] for g in enabled}
        previous_detections = {}
        compressor_index = None
        if session.compressor_start_sec is not None:
            compressor_index = min(
                range(len(schedules)),
                key=lambda index: abs(schedules[index] - session.compressor_start_sec),
            )
        debug_enabled = (
            session.debug_trace_level is not DebugTraceLevel.NONE
            and self.debug_trace_sink_factory is not None
        )
        sink = (
            self.debug_trace_sink_factory.create(run_id, recipe, session)
            if debug_enabled
            else None
        )
        completion = None
        _emit(
            progress,
            AnalysisStage.VIDEO_ANALYSIS,
            0.0,
            message="영상과 분석 영역을 준비하고 있습니다.",
            total=len(schedules) * len(enabled),
        )

        try:
            detection_began = [0.0]

            def static_ready() -> None:
                _emit(
                    progress,
                    AnalysisStage.VIDEO_ANALYSIS,
                    0.02,
                    message="고정 artifact 준비를 마쳤습니다.",
                    total=len(schedules) * len(enabled),
                )
                detection_began[0] = time.perf_counter()

            def observed(observation) -> None:
                if not observation.succeeded or observation.detection is None:
                    return
                detection = observation.detection
                glass = observation.glass
                detections_by_glass[glass.id].append(detection)
                current_frame_sample = tracking_sample_from_detection(
                    run_id,
                    glass,
                    detection,
                )
                if sink is not None:
                    index = len(detections_by_glass[glass.id]) - 1
                    decision = self.capture_policy.decide(
                        session.debug_trace_level,
                        detection,
                        is_valid=current_frame_sample.is_valid,
                        minimum_confidence=(
                            glass.detector_settings.minimum_final_confidence
                        ),
                        effective_height=effective_observation_height(glass),
                        first_sample=index == 0,
                        last_sample=index == len(schedules) - 1,
                        compressor_nearest=index == compressor_index,
                        previous_detection=previous_detections.get(glass.id),
                    )
                    if decision.capture:
                        sink.write(
                            glass,
                            detection,
                            observation.artifacts,
                            decision,
                        )
                previous_detections[glass.id] = detection

            def detection_progress(observation, completed, total) -> None:
                if not observation.succeeded:
                    return
                elapsed = max(1e-6, time.perf_counter() - detection_began[0])
                frame_number = (completed - 1) // max(1, len(enabled)) + 1
                frame_fraction = completed / max(1, total)
                _emit(
                    progress,
                    AnalysisStage.VIDEO_ANALYSIS,
                    0.02 + 0.98 * frame_fraction,
                    message=f"{observation.glass.name} 검출 중",
                    completed=completed,
                    total=total,
                    timestamp_sec=observation.actual_timestamp_sec,
                    glass_name=observation.glass.name,
                    rate_fps=frame_number / elapsed,
                )

            def annotate_sequence(glass, resolved) -> None:
                annotate = getattr(sink, "annotate_sequence", None)
                if callable(annotate):
                    annotate(glass, resolved)

            confirmed_initial_states = {}
            for glass in enabled:
                confirmation = session.initial_state_confirmations.get(glass.id)
                confirmed_initial_states[glass.id] = (
                    confirmation.state
                    if confirmation is not None
                    and confirmation.matches(glass.initial_state, session)
                    else None
                )

            detection_run = DetectionRunCoordinator(
                self.video_reader_factory,
                self.detector,
                self.detector,
            ).run(
                source_video_path=session.input_video_path,
                glasses=enabled,
                targets=tuple(DetectionTarget(value) for value in schedules),
                static_schedule=schedules,
                policy=DetectionRunPolicy(
                    resolution_mode=SequenceResolutionMode.COMPLETED_WINDOW,
                    debug=debug_enabled,
                    reuse_static_decodes=False,
                ),
                confirmed_initial_states=confirmed_initial_states,
                check_cancelled=lambda: _check_cancelled(cancellation),
                on_static_ready=static_ready,
                on_observation=observed,
                on_sequence=annotate_sequence,
                on_progress=detection_progress,
            )

            for glass in enabled:
                resolved = tuple(
                    observation.resolved_detection
                    for observation in detection_run.observations_by_glass[glass.id]
                    if observation.resolved_detection is not None
                )
                by_glass[glass.id] = [
                    tracking_sample_from_detection(run_id, glass, detection)
                    for detection in resolved
                ]

            _check_cancelled(cancellation)
            _emit(
                progress,
                AnalysisStage.VIDEO_ANALYSIS,
                1.0,
                message="영상 분석을 마쳤습니다.",
                completed=len(schedules) * len(enabled),
                total=len(schedules) * len(enabled),
            )
            _emit(
                progress,
                AnalysisStage.EVENTS_AND_JUDGMENT,
                0.0,
                message="Glass별 이벤트와 판정을 계산하고 있습니다.",
                total=len(enabled),
            )

            glass_results: list[GlassAnalysisResult] = []
            for glass_index, glass in enumerate(enabled):
                _check_cancelled(cancellation)
                samples = by_glass[glass.id]
                confirmation = session.initial_state_confirmations.get(glass.id)
                assembly = self.outcome_assembler.assemble(
                    run_id=run_id,
                    glass=glass,
                    samples=samples,
                    confirmation=confirmation,
                    compressor_start_sec=session.compressor_start_sec,
                    mode=StateAwareOutcomeMode.OFFICIAL_ANALYSIS,
                )
                outcome = assembly.judgment
                assert outcome is not None
                glass_results.append(
                    GlassAnalysisResult(
                        glass_id=glass.id,
                        glass_name=glass.name,
                        result_state=outcome.state,
                        samples=samples,
                        events=sorted(
                            assembly.events,
                            key=lambda event: (
                                event.start_time_sec,
                                event.event_type.value,
                            ),
                        ),
                        valid_coverage_ratio=assembly.observed_coverage_ratio or 0.0,
                        effective_state_aware_coverage_ratio=(
                            assembly.effective_coverage_ratio or 0.0
                        ),
                        judgment_note=outcome.note,
                        retrospective=assembly.retrospective,
                    )
                )
                _emit(
                    progress,
                    AnalysisStage.EVENTS_AND_JUDGMENT,
                    (glass_index + 1) / max(1, len(enabled)),
                    message=f"{glass.name} 이벤트와 판정 계산 완료",
                    completed=glass_index + 1,
                    total=len(enabled),
                    glass_name=glass.name,
                )

            _check_cancelled(cancellation)
            overall = _overall_result([result.result_state for result in glass_results])
            completed = datetime.now(timezone.utc)
            if sink is not None:
                completion = sink.finalize()
            _emit(
                progress,
                AnalysisStage.EVENTS_AND_JUDGMENT,
                1.0,
                message="이벤트와 판정 계산을 마쳤습니다.",
                completed=len(enabled),
                total=len(enabled),
            )
            return AnalysisResult(
                run_id=run_id,
                overall_state=overall,
                glass_results=glass_results,
                started_at=started.isoformat(),
                completed_at=completed.isoformat(),
                warnings=[issue.message for issue in validation.warnings],
                manifest={
                    "run_id": run_id,
                    "recipe_id": recipe.recipe_id,
                    "recipe_schema_version": recipe.schema_version,
                    "recipe_snapshot_hash": hashlib.sha256(
                        _stable_recipe_bytes(recipe)
                    ).hexdigest(),
                    "source_video_path": session.input_video_path,
                    "source_metadata": session.video_metadata.to_dict()
                    if session.video_metadata
                    else None,
                    "sampling_fps": session.sampling_fps,
                    "analysis_range": [
                        session.analysis_start_sec,
                        session.effective_end_sec(),
                    ],
                    "run_started_at": started.isoformat(),
                    "run_completed_at": completed.isoformat(),
                    "result_status": overall.value,
                    "debug_trace_level": session.debug_trace_level.value,
                    "debug_record_count": completion.record_count
                    if completion is not None
                    else 0,
                    "sequence_resolver_enabled": (
                        detection_run.sequence_resolver_enabled
                    ),
                    "sequence_resolver": dict(
                        detection_run.sequence_diagnostics
                    ),
                },
                debug_trace_completion=completion,
            )
        except Exception:
            if sink is not None and completion is None:
                sink.abort()
            raise


def _emit(progress: ProgressSink | None, stage: AnalysisStage, fraction: float, **kwargs) -> None:
    if progress is not None:
        progress(build_progress_update(stage, fraction, **kwargs))


def _check_cancelled(cancellation: CancellationToken | None) -> None:
    if cancellation is not None and cancellation.cancelled:
        raise AnalysisCancelled("Analysis was cancelled.")


def timestamp_schedule(start_sec: float, end_sec: float, sampling_fps: float) -> list[float]:
    if sampling_fps <= 0 or end_sec <= start_sec:
        return []
    interval = 1.0 / sampling_fps
    count = int((end_sec - start_sec) / interval) + 1
    values = [start_sec + index * interval for index in range(count)]
    if values and values[-1] < end_sec - interval * 0.25:
        values.append(end_sec)
    return [min(end_sec, round(value, 9)) for value in values]


def _overall_result(states: list[ResultState]) -> ResultState:
    if not states:
        return ResultState.NOT_APPLICABLE
    if ResultState.FAIL in states:
        return ResultState.FAIL
    if ResultState.REVIEW_REQUIRED in states:
        return ResultState.REVIEW_REQUIRED
    if all(state == ResultState.PASS for state in states):
        return ResultState.PASS
    return ResultState.NOT_APPLICABLE


def _stable_recipe_bytes(recipe: InspectionRecipe) -> bytes:
    import json

    return json.dumps(
        recipe.to_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
