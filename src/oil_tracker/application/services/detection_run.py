from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass, replace
from enum import Enum
from typing import Any

from oil_tracker.application.ports.phase_detector import (
    CompletedWindowResolver,
    PreparedFrameDetector,
)
from oil_tracker.application.services.detection_processing import learn_static_artifacts
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig


class SequenceResolutionMode(str, Enum):
    CURRENT_FRAME_COMPATIBILITY = "current_frame_compatibility"
    COMPLETED_WINDOW = "completed_window"


@dataclass(frozen=True)
class DetectionTarget:
    timestamp_sec: float
    publish: bool = True


@dataclass(frozen=True)
class DetectionRunPolicy:
    resolution_mode: SequenceResolutionMode
    debug: bool = False
    reuse_static_decodes: bool = False
    maximum_consecutive_failures: int = 0
    suppress_reader_close_errors: bool = False

    @property
    def fail_fast(self) -> bool:
        return self.maximum_consecutive_failures <= 0


@dataclass(frozen=True)
class DetectionObservation:
    target: DetectionTarget
    glass: GlassInspectionConfig
    frame_index: int | None
    actual_timestamp_sec: float | None
    detection: PhaseDetection | None
    resolved_detection: PhaseDetection | None
    artifacts: Any | None = None
    error: Exception | None = None

    @property
    def succeeded(self) -> bool:
        return self.detection is not None and self.error is None


@dataclass(frozen=True)
class DetectionRunResult:
    observations_by_glass: Mapping[str, tuple[DetectionObservation, ...]]
    sequence_diagnostics: Mapping[str, dict[str, Any]]

    @property
    def sequence_resolver_enabled(self) -> bool:
        return bool(self.sequence_diagnostics)


class ConsecutiveDetectionFailures(RuntimeError):
    def __init__(
        self,
        target: DetectionTarget,
        count: int,
        cause: Exception,
    ) -> None:
        super().__init__(f"{count} consecutive detection failures at {target.timestamp_sec}")
        self.target = target
        self.count = count
        self.cause = cause


ObservationCallback = Callable[[DetectionObservation], None]
SequenceCallback = Callable[
    [GlassInspectionConfig, tuple[PhaseDetection, ...]],
    None,
]
ProgressCallback = Callable[[DetectionObservation, int, int], None]
ReaderCloseErrorCallback = Callable[[Exception], None]


class DetectionRunCoordinator:
    """Own one reader/detector lifecycle from static preparation to resolution."""

    def __init__(
        self,
        video_reader_factory: Callable[[str], Any],
        detector: PreparedFrameDetector,
        completed_window_resolver: CompletedWindowResolver | None = None,
    ) -> None:
        self.video_reader_factory = video_reader_factory
        self.detector = detector
        self.completed_window_resolver = completed_window_resolver

    def run(
        self,
        *,
        source_video_path: str,
        glasses: Sequence[GlassInspectionConfig],
        targets: Sequence[DetectionTarget],
        static_schedule: Sequence[float],
        policy: DetectionRunPolicy,
        confirmed_initial_states: Mapping[
            str,
            InitialObservationState | None,
        ]
        | None = None,
        check_cancelled: Callable[[], None] | None = None,
        validate_reader: Callable[[Any], None] | None = None,
        on_static_start: Callable[[], None] | None = None,
        on_static_ready: Callable[[], None] | None = None,
        on_observation: ObservationCallback | None = None,
        on_sequence: SequenceCallback | None = None,
        on_progress: ProgressCallback | None = None,
        on_reader_close_error: ReaderCloseErrorCallback | None = None,
    ) -> DetectionRunResult:
        selected_glasses = tuple(glasses)
        selected_targets = tuple(targets)
        observations: dict[str, list[DetectionObservation]] = {
            glass.id: [] for glass in selected_glasses
        }
        self.detector.reset()
        reader = self.video_reader_factory(source_video_path)
        decoded_cache: dict[float, tuple[Any, int, float]] = {}
        try:
            self._check(check_cancelled)
            if validate_reader is not None:
                validate_reader(reader)
            self._check(check_cancelled)
            if on_static_start is not None:
                on_static_start()
            learn_static_artifacts(
                reader,
                self.detector,
                selected_glasses,
                static_schedule,
                decoded_frame_cache=(
                    decoded_cache if policy.reuse_static_decodes else None
                ),
            )
            self._check(check_cancelled)
            if on_static_ready is not None:
                on_static_ready()

            total = len(selected_targets) * len(selected_glasses)
            completed = 0
            consecutive_failures = 0
            for target in selected_targets:
                self._check(check_cancelled)
                try:
                    decoded = decoded_cache.pop(target.timestamp_sec, None)
                    if decoded is None:
                        decoded = reader.read_at(target.timestamp_sec)
                    frame, frame_index, actual_timestamp = decoded
                except Exception as exc:
                    consecutive_failures += 1
                    for glass in selected_glasses:
                        observation = DetectionObservation(
                            target=target,
                            glass=glass,
                            frame_index=None,
                            actual_timestamp_sec=None,
                            detection=None,
                            resolved_detection=None,
                            error=exc,
                        )
                        observations[glass.id].append(observation)
                        if on_observation is not None:
                            on_observation(observation)
                        completed += 1
                        if on_progress is not None:
                            on_progress(observation, completed, total)
                    self._handle_failure(policy, target, consecutive_failures, exc)
                    continue

                for glass in selected_glasses:
                    self._check(check_cancelled)
                    try:
                        detection, artifacts = self.detector.detect(
                            frame,
                            glass,
                            frame_index,
                            actual_timestamp,
                            debug=policy.debug,
                        )
                    except Exception as exc:
                        consecutive_failures += 1
                        observation = DetectionObservation(
                            target=target,
                            glass=glass,
                            frame_index=frame_index,
                            actual_timestamp_sec=actual_timestamp,
                            detection=None,
                            resolved_detection=None,
                            error=exc,
                        )
                        observations[glass.id].append(observation)
                        if on_observation is not None:
                            on_observation(observation)
                        completed += 1
                        if on_progress is not None:
                            on_progress(observation, completed, total)
                        self._handle_failure(
                            policy,
                            target,
                            consecutive_failures,
                            exc,
                        )
                        continue

                    consecutive_failures = 0
                    observation = DetectionObservation(
                        target=target,
                        glass=glass,
                        frame_index=int(frame_index),
                        actual_timestamp_sec=float(actual_timestamp),
                        detection=detection,
                        resolved_detection=detection,
                        artifacts=artifacts,
                    )
                    if on_observation is not None:
                        on_observation(observation)
                    observations[glass.id].append(
                        replace(observation, artifacts=None)
                    )
                    completed += 1
                    if on_progress is not None:
                        on_progress(observation, completed, total)
        finally:
            decoded_cache.clear()
            try:
                reader.close()
            except Exception as exc:
                if on_reader_close_error is not None:
                    on_reader_close_error(exc)
                if not policy.suppress_reader_close_errors:
                    raise

        diagnostics: dict[str, dict[str, Any]] = {}
        if policy.resolution_mode is SequenceResolutionMode.COMPLETED_WINDOW:
            if self.completed_window_resolver is None:
                raise TypeError(
                    "Completed-window mode requires an explicit sequence resolver."
                )
            for glass in selected_glasses:
                self._check(check_cancelled)
                rows = observations[glass.id]
                if not all(row.succeeded for row in rows):
                    raise ValueError(
                        "Completed-window resolution requires one successful "
                        "detection for every target."
                    )
                source = tuple(
                    row.detection for row in rows if row.detection is not None
                )
                resolved, summary = resolve_completed_window(
                    self.completed_window_resolver,
                    source,
                    glass,
                    None
                    if confirmed_initial_states is None
                    else confirmed_initial_states.get(glass.id),
                )
                observations[glass.id] = [
                    replace(row, resolved_detection=projected)
                    for row, projected in zip(rows, resolved, strict=True)
                ]
                if summary is not None:
                    diagnostics[glass.id] = summary
                if on_sequence is not None:
                    on_sequence(glass, resolved)

        return DetectionRunResult(
            observations_by_glass={
                glass_id: tuple(rows) for glass_id, rows in observations.items()
            },
            sequence_diagnostics=diagnostics,
        )

    @staticmethod
    def _check(check_cancelled: Callable[[], None] | None) -> None:
        if check_cancelled is not None:
            check_cancelled()

    @staticmethod
    def _handle_failure(
        policy: DetectionRunPolicy,
        target: DetectionTarget,
        count: int,
        cause: Exception,
    ) -> None:
        if policy.fail_fast:
            raise cause
        if count >= policy.maximum_consecutive_failures:
            raise ConsecutiveDetectionFailures(target, count, cause) from cause


def resolve_completed_window(
    resolver: CompletedWindowResolver,
    detections: Sequence[PhaseDetection],
    glass: GlassInspectionConfig,
    confirmed_initial_state: InitialObservationState | None,
) -> tuple[tuple[PhaseDetection, ...], dict[str, Any] | None]:
    result = resolver.resolve_sequence(
        tuple(detections),
        glass,
        confirmed_initial_state,
    )
    resolved = tuple(result.detections)
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
    diagnostics = result.diagnostics
    if diagnostics is None:
        return resolved, None
    if is_dataclass(diagnostics):
        return resolved, asdict(diagnostics)
    if isinstance(diagnostics, dict):
        return resolved, dict(diagnostics)
    return resolved, {"summary": str(diagnostics)}
