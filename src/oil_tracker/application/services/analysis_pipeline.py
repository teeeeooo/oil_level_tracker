from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
import hashlib
import time
from typing import Callable
from uuid import uuid4

from oil_tracker.application.ports.phase_detector import PhaseDetector
from oil_tracker.application.ports.progress import (
    AnalysisCancelled,
    AnalysisStage,
    CancellationToken,
    ProgressSink,
    build_progress_update,
)
from oil_tracker.application.services.debug_capture_policy import DebugCapturePolicy
from oil_tracker.application.services.detection_processing import (
    effective_observation_height,
    learn_static_artifacts,
    tracking_sample_from_detection,
)
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
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.enums import EventType, ResultState
from oil_tracker.domain.events import detect_events_for_glass
from oil_tracker.domain.judgment import judge_samples
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, EventMarker, GlassAnalysisResult, TrackingSample
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
        detector: PhaseDetector,
        validator: RecipeValidationService,
        debug_trace_sink_factory=None,
        capture_policy: DebugCapturePolicy | None = None,
    ) -> None:
        self.video_reader_factory = video_reader_factory
        self.detector = detector
        self.validator = validator
        self.debug_trace_sink_factory = debug_trace_sink_factory
        self.capture_policy = capture_policy or DebugCapturePolicy()

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
        sequence_diagnostics: dict[str, object] = {}
        sequence_resolver_enabled = False
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
        self.detector.reset()
        _emit(
            progress,
            AnalysisStage.VIDEO_ANALYSIS,
            0.0,
            message="영상과 분석 영역을 준비하고 있습니다.",
            total=len(schedules) * len(enabled),
        )

        try:
            reader = self.video_reader_factory(session.input_video_path)
            try:
                _check_cancelled(cancellation)
                learn_static_artifacts(reader, self.detector, enabled, schedules)
                _check_cancelled(cancellation)
                _emit(
                    progress,
                    AnalysisStage.VIDEO_ANALYSIS,
                    0.02,
                    message="고정 artifact 준비를 마쳤습니다.",
                    total=len(schedules) * len(enabled),
                )
                began = time.perf_counter()
                total_detections = len(schedules) * len(enabled)
                for index, target_time in enumerate(schedules):
                    _check_cancelled(cancellation)
                    frame, frame_index, actual_time = reader.read_at(target_time)
                    for glass_index, glass in enumerate(enabled):
                        _check_cancelled(cancellation)
                        detection, artifacts = self.detector.detect(
                            frame,
                            glass,
                            frame_index,
                            actual_time,
                            debug=debug_enabled,
                        )
                        detections_by_glass[glass.id].append(detection)
                        current_frame_sample = tracking_sample_from_detection(
                            run_id,
                            glass,
                            detection,
                        )
                        if sink is not None:
                            decision = self.capture_policy.decide(
                                session.debug_trace_level,
                                detection,
                                is_valid=current_frame_sample.is_valid,
                                minimum_confidence=glass.detector_settings.minimum_final_confidence,
                                effective_height=effective_observation_height(glass),
                                first_sample=index == 0,
                                last_sample=index == len(schedules) - 1,
                                compressor_nearest=index == compressor_index,
                                previous_detection=previous_detections.get(glass.id),
                            )
                            if decision.capture:
                                sink.write(glass, detection, artifacts, decision)
                        previous_detections[glass.id] = detection
                        artifacts = None
                        completed_detections = index * len(enabled) + glass_index + 1
                        elapsed = max(1e-6, time.perf_counter() - began)
                        frame_fraction = completed_detections / max(1, total_detections)
                        _emit(
                            progress,
                            AnalysisStage.VIDEO_ANALYSIS,
                            0.02 + 0.98 * frame_fraction,
                            message=f"{glass.name} 검출 중",
                            completed=completed_detections,
                            total=total_detections,
                            timestamp_sec=actual_time,
                            glass_name=glass.name,
                            rate_fps=(index + 1) / elapsed,
                        )
            finally:
                reader.close()

            for glass in enabled:
                _check_cancelled(cancellation)
                confirmation = session.initial_state_confirmations.get(glass.id)
                confirmed_state = (
                    confirmation.state
                    if confirmation is not None
                    and confirmation.matches(glass.initial_state, session)
                    else None
                )
                resolved, diagnostics = _resolve_detection_sequence(
                    self.detector,
                    detections_by_glass[glass.id],
                    glass,
                    confirmed_state,
                )
                sequence_resolver_enabled = sequence_resolver_enabled or diagnostics is not None
                if diagnostics is not None:
                    sequence_diagnostics[glass.id] = diagnostics
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
                retrospective = reconstruct_initial_state(glass, samples, confirmation)
                effective_samples = project_state_aware_samples(samples, retrospective)
                observed_events = detect_events_for_glass(run_id, glass.id, samples)
                projected_events = detect_events_for_glass(run_id, glass.id, effective_samples)
                events = merge_state_aware_events(
                    observed_events,
                    projected_events,
                    retrospective,
                )
                if session.compressor_start_sec is not None:
                    closest = min(
                        samples,
                        key=lambda sample: abs(
                            sample.timestamp_sec - session.compressor_start_sec
                        ),
                    )
                    events.append(
                        EventMarker(
                            run_id,
                            glass.id,
                            EventType.COMPRESSOR_START,
                            session.compressor_start_sec,
                            representative_frame_index=closest.frame_index,
                            confidence=1.0,
                        )
                    )
                judgment_samples = samples_for_judgment(
                    samples,
                    retrospective,
                    glass.judgment_rule.mode,
                )
                outcome = judge_samples(
                    judgment_samples,
                    glass.judgment_rule,
                    session.compressor_start_sec,
                )
                outcome = annotate_judgment_provenance(
                    outcome,
                    retrospective,
                    glass.judgment_rule.mode,
                )
                outcome = enforce_conflict_review(outcome, retrospective)
                events.append(
                    EventMarker(
                        run_id,
                        glass.id,
                        EventType.JUDGMENT_PASS
                        if outcome.state == ResultState.PASS
                        else EventType.JUDGMENT_FAIL
                        if outcome.state == ResultState.FAIL
                        else EventType.REVIEW_REQUIRED,
                        samples[-1].timestamp_sec,
                        representative_frame_index=samples[-1].frame_index,
                        confidence=outcome.valid_coverage_ratio,
                        note=outcome.note,
                    )
                )
                glass_results.append(
                    GlassAnalysisResult(
                        glass_id=glass.id,
                        glass_name=glass.name,
                        result_state=outcome.state,
                        samples=samples,
                        events=sorted(
                            events,
                            key=lambda event: (
                                event.start_time_sec,
                                event.event_type.value,
                            ),
                        ),
                        valid_coverage_ratio=observed_coverage(samples),
                        effective_state_aware_coverage_ratio=effective_state_aware_coverage(
                            samples,
                            retrospective,
                        ),
                        judgment_note=outcome.note,
                        retrospective=retrospective,
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
                    "sequence_resolver_enabled": sequence_resolver_enabled,
                    "sequence_resolver": sequence_diagnostics,
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


def _resolve_detection_sequence(
    detector,
    detections,
    glass,
    confirmed_initial_state,
):
    resolver = getattr(detector, "resolve_sequence", None)
    if not callable(resolver):
        return tuple(detections), None
    result = resolver(
        tuple(detections),
        glass,
        confirmed_initial_state,
    )
    resolved = tuple(getattr(result, "detections", result))
    if len(resolved) != len(detections):
        raise ValueError(
            "Sequence resolver must return exactly one detection per input frame."
        )
    for source, projected in zip(detections, resolved, strict=True):
        if (
            source.glass_id != projected.glass_id
            or source.frame_index != projected.frame_index
            or abs(float(source.time_sec) - float(projected.time_sec)) > 1e-9
        ):
            raise ValueError(
                "Sequence resolver changed Glass, frame or timestamp identity."
            )
    diagnostics = getattr(result, "diagnostics", None)
    if diagnostics is None:
        return resolved, {"version": str(getattr(detector, "version", "unknown"))}
    if is_dataclass(diagnostics):
        return resolved, asdict(diagnostics)
    if isinstance(diagnostics, dict):
        return resolved, dict(diagnostics)
    return resolved, {"summary": str(diagnostics)}
