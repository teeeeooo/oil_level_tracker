from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import time
from typing import Callable
from uuid import uuid4

from oil_tracker.application.ports.phase_detector import PhaseDetector
from oil_tracker.application.ports.progress import CancellationToken, ProgressSink, ProgressUpdate
from oil_tracker.application.services.debug_capture_policy import DebugCapturePolicy
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.events import detect_events_for_glass
from oil_tracker.domain.judgment import judge_samples
from oil_tracker.domain.recipe import GlassInspectionConfig, InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, EventMarker, GlassAnalysisResult, TrackingSample
from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel


class AnalysisCancelled(RuntimeError):
    pass


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
        validation = self.validator.validate(recipe, session)
        if not validation.is_ready:
            messages = "; ".join(i.message for i in validation.errors)
            raise ValueError(f"Workbench is not ready: {messages}")

        run_id = str(uuid4())
        started = datetime.now(timezone.utc)
        enabled = [g for g in recipe.glasses if g.enabled]
        schedules = timestamp_schedule(session.analysis_start_sec, session.effective_end_sec() or 0.0, session.sampling_fps)
        if not schedules:
            raise ValueError("Timestamp schedule is empty.")
        by_glass: dict[str, list[TrackingSample]] = {g.id: [] for g in enabled}
        previous_detections = {}
        compressor_index = None
        if session.compressor_start_sec is not None:
            compressor_index = min(range(len(schedules)), key=lambda index: abs(schedules[index] - session.compressor_start_sec))
        debug_enabled = session.debug_trace_level is not DebugTraceLevel.NONE and self.debug_trace_sink_factory is not None
        sink = self.debug_trace_sink_factory.create(run_id, recipe, session) if debug_enabled else None
        completion = None
        self.detector.reset()

        try:
            reader = self.video_reader_factory(session.input_video_path)
            try:
                self._learn_static_artifacts(reader, enabled, schedules)
                began = time.perf_counter()
                for index, target_time in enumerate(schedules):
                    if cancellation and cancellation.cancelled:
                        raise AnalysisCancelled("Analysis was cancelled.")
                    frame, frame_index, actual_time = reader.read_at(target_time)
                    for glass in enabled:
                        detection, artifacts = self.detector.detect(
                            frame,
                            glass,
                            frame_index,
                            actual_time,
                            debug=debug_enabled,
                        )
                        sample = _to_tracking_sample(run_id, glass, detection)
                        by_glass[glass.id].append(sample)
                        if sink is not None:
                            decision = self.capture_policy.decide(
                                session.debug_trace_level,
                                detection,
                                is_valid=sample.is_valid,
                                minimum_confidence=glass.detector_settings.minimum_final_confidence,
                                effective_height=_effective_observation_height(glass),
                                first_sample=index == 0,
                                last_sample=index == len(schedules) - 1,
                                compressor_nearest=index == compressor_index,
                                previous_detection=previous_detections.get(glass.id),
                            )
                            if decision.capture:
                                sink.write(glass, detection, artifacts, decision)
                        previous_detections[glass.id] = detection
                        artifacts = None
                        if progress:
                            elapsed = max(1e-6, time.perf_counter() - began)
                            progress(ProgressUpdate(index + 1, len(schedules), actual_time, glass.name, (index + 1) / elapsed))
            finally:
                reader.close()

            glass_results: list[GlassAnalysisResult] = []
            for glass in enabled:
                samples = by_glass[glass.id]
                events = detect_events_for_glass(run_id, glass.id, samples)
                if session.compressor_start_sec is not None:
                    closest = min(samples, key=lambda s: abs(s.timestamp_sec - session.compressor_start_sec))
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
                outcome = judge_samples(samples, glass.judgment_rule, session.compressor_start_sec)
                events.append(
                    EventMarker(
                        run_id,
                        glass.id,
                        EventType.JUDGMENT_PASS if outcome.state == ResultState.PASS else EventType.JUDGMENT_FAIL if outcome.state == ResultState.FAIL else EventType.REVIEW_REQUIRED,
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
                        events=sorted(events, key=lambda e: (e.start_time_sec, e.event_type.value)),
                        valid_coverage_ratio=outcome.valid_coverage_ratio,
                        judgment_note=outcome.note,
                    )
                )

            overall = _overall_result([x.result_state for x in glass_results])
            completed = datetime.now(timezone.utc)
            if sink is not None:
                completion = sink.finalize()
            result = AnalysisResult(
                run_id=run_id,
                overall_state=overall,
                glass_results=glass_results,
                started_at=started.isoformat(),
                completed_at=completed.isoformat(),
                warnings=[i.message for i in validation.warnings],
                manifest={
                    "run_id": run_id,
                    "recipe_id": recipe.recipe_id,
                    "recipe_schema_version": recipe.schema_version,
                    "recipe_snapshot_hash": hashlib.sha256(_stable_recipe_bytes(recipe)).hexdigest(),
                    "source_video_path": session.input_video_path,
                    "source_metadata": session.video_metadata.to_dict() if session.video_metadata else None,
                    "sampling_fps": session.sampling_fps,
                    "analysis_range": [session.analysis_start_sec, session.effective_end_sec()],
                    "run_started_at": started.isoformat(),
                    "run_completed_at": completed.isoformat(),
                    "result_status": overall.value,
                    "debug_trace_level": session.debug_trace_level.value,
                    "debug_record_count": completion.record_count if completion is not None else 0,
                },
                debug_trace_completion=completion,
            )
            return result
        except Exception:
            if sink is not None and completion is None:
                sink.abort()
            raise

    def _learn_static_artifacts(self, reader, glasses: list[GlassInspectionConfig], schedules: list[float]) -> None:
        learn = getattr(self.detector, "learn_static_artifact", None)
        if learn is None or len(schedules) < 2:
            return
        indices = sorted(set([0, len(schedules) // 2, len(schedules) - 1]))
        frames = []
        for idx in indices:
            try:
                frame, _, _ = reader.read_at(schedules[idx])
                frames.append(frame)
            except Exception:
                continue
        for glass in glasses:
            learn(frames, glass)


def timestamp_schedule(start_sec: float, end_sec: float, sampling_fps: float) -> list[float]:
    if sampling_fps <= 0 or end_sec <= start_sec:
        return []
    interval = 1.0 / sampling_fps
    count = int((end_sec - start_sec) / interval) + 1
    values = [start_sec + i * interval for i in range(count)]
    if values and values[-1] < end_sec - interval * 0.25:
        values.append(end_sec)
    return [min(end_sec, round(value, 9)) for value in values]


def _to_tracking_sample(run_id: str, glass: GlassInspectionConfig, detection) -> TrackingSample:
    zero = glass.geometry.zero_line_y
    mm = glass.mm_per_pixel
    raw_oil_px = None if detection.raw_oil_air_level_y is None or zero is None else zero - detection.raw_oil_air_level_y
    raw_foam_px = None if detection.raw_foam_front_y is None or zero is None else zero - detection.raw_foam_front_y
    oil_px = detection.oil_air_level_px_from_zero
    foam_px = detection.foam_front_px_from_zero
    explicit_state = detection.fill_state in {FillState.FULL_NO_INTERFACE, FillState.EMPTY_NO_INTERFACE}
    visible_valid = detection.fill_state not in {FillState.UNKNOWN_REVIEW} and (oil_px is not None or detection.fill_state == FillState.FULL_WITH_FOAM)
    valid = detection.overall_confidence >= glass.detector_settings.minimum_final_confidence and (explicit_state or visible_valid)
    return TrackingSample(
        run_id=run_id,
        glass_id=glass.id,
        frame_index=detection.frame_index,
        timestamp_sec=detection.time_sec,
        fill_state=detection.fill_state,
        raw_oil_air_level_y=detection.raw_oil_air_level_y,
        raw_oil_air_level_px_from_zero=raw_oil_px,
        raw_oil_air_level_mm_from_zero=None if raw_oil_px is None or mm is None else raw_oil_px * mm,
        smoothed_oil_air_level_px_from_zero=oil_px,
        smoothed_oil_air_level_mm_from_zero=detection.oil_air_level_mm_from_zero,
        oil_air_confidence=detection.oil_air_confidence,
        raw_foam_front_y=detection.raw_foam_front_y,
        raw_foam_front_px_from_zero=raw_foam_px,
        raw_foam_front_mm_from_zero=None if raw_foam_px is None or mm is None else raw_foam_px * mm,
        smoothed_foam_front_px_from_zero=foam_px,
        smoothed_foam_front_mm_from_zero=detection.foam_front_mm_from_zero,
        foam_confidence=detection.foam_confidence,
        visibility_confidence=detection.visibility_confidence,
        overall_confidence=detection.overall_confidence,
        is_valid=valid,
        flags=detection.flags,
    )


def _effective_observation_height(glass: GlassInspectionConfig) -> float:
    full_height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
    return max(1.0, full_height * max(0.05, 1.0 - float(glass.geometry.margin_ratio) * 2.0))


def _overall_result(states: list[ResultState]) -> ResultState:
    if not states:
        return ResultState.NOT_APPLICABLE
    if ResultState.FAIL in states:
        return ResultState.FAIL
    if ResultState.REVIEW_REQUIRED in states:
        return ResultState.REVIEW_REQUIRED
    if all(x == ResultState.PASS for x in states):
        return ResultState.PASS
    return ResultState.NOT_APPLICABLE


def _stable_recipe_bytes(recipe: InspectionRecipe) -> bytes:
    import json

    return json.dumps(recipe.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
