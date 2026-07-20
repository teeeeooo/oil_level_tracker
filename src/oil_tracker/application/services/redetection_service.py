from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any, Callable

from oil_tracker.application.services.detection_processing import (
    learn_static_artifacts,
    tracking_sample_from_detection,
)
from oil_tracker.application.services.detector_settings import (
    compare_detector_settings,
    detector_settings_from_json,
    validate_detector_settings,
)
from oil_tracker.application.services.redetection_comparison import (
    align_redetection_samples,
    compare_events,
    summarize_comparison,
)
from oil_tracker.application.services.redetection_request import (
    full_static_artifact_schedule,
    redetection_schedule,
)
from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.events import detect_events_for_glass
from oil_tracker.domain.judgment import judge_samples
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.redetection import (
    RedetectionCandidate,
    RedetectionMode,
    RedetectionPolicy,
    RedetectionProgress,
    RedetectionResult,
    RedetectionSample,
)
from oil_tracker.domain.results import EventMarker, TrackingSample
from oil_tracker.domain.session import AnalysisSession


LOGGER = logging.getLogger(__name__)


class RedetectionError(RuntimeError):
    pass


class RedetectionCancelled(RedetectionError):
    pass


@dataclass(frozen=True)
class RedetectionRunOutput:
    result: RedetectionResult
    workspace: Any


class PartialRedetectionService:
    """Run one selected-glass re-detection without touching official state."""

    def __init__(
        self,
        video_reader_factory: Callable[[str], Any],
        detector_factory: Callable[[], Any],
        workspace_factory: Callable[..., Any],
        *,
        policy: RedetectionPolicy | None = None,
    ) -> None:
        self.video_reader_factory = video_reader_factory
        self.detector_factory = detector_factory
        self.workspace_factory = workspace_factory
        self.policy = policy or RedetectionPolicy()

    def run(
        self,
        request,
        official_bundle,
        *,
        official_candidate_timestamps=(),
        progress: Callable[[RedetectionProgress], None] | None = None,
        cancellation=None,
    ) -> RedetectionRunOutput:
        self._check_cancelled(cancellation)
        recipe = InspectionRecipe.from_dict(json.loads(request.recipe_snapshot_json))
        session = AnalysisSession.from_dict(json.loads(request.session_snapshot_json))
        temporary_settings = detector_settings_from_json(request.detector_settings_json)
        validation_errors = validate_detector_settings(temporary_settings)
        if validation_errors:
            messages = ", ".join(
                f"{field}: {message}" for field, message in validation_errors.items()
            )
            raise RedetectionError(f"검출 설정이 올바르지 않습니다: {messages}")
        glass = next(
            (item for item in recipe.glasses if item.id == request.selected_glass_id),
            None,
        )
        if glass is None:
            raise RedetectionError("선택한 관찰창이 recipe snapshot에 없습니다.")
        baseline_settings = glass.detector_settings
        glass.detector_settings = temporary_settings
        source = Path(request.source_video_path).expanduser()
        if not source.is_file():
            raise RedetectionError(
                "원본 영상이 없습니다. 원본 영상을 다시 지정해 주세요."
            )
        schedule = redetection_schedule(request)
        if not schedule:
            raise RedetectionError("재검출할 timestamp schedule이 비어 있습니다.")
        display_total = sum(not warmup for _timestamp, warmup in schedule)
        if display_total <= 0:
            raise RedetectionError("표시 구간에 재검출 sample이 없습니다.")

        self._emit(
            progress,
            request,
            "source_prepare",
            0,
            display_total,
            None,
            "원본 영상 준비",
        )
        detector = self.detector_factory()
        if detector is None:
            raise RedetectionError("재검출 detector를 만들 수 없습니다.")
        detector.reset()
        workspace = None
        reader = None
        decoded_frame_cache: dict[float, tuple[Any, int, float]] = {}
        try:
            workspace = self.workspace_factory(recipe, policy=self.policy)
            reader = self.video_reader_factory(str(source))
            metadata = getattr(reader, "metadata", None)
            if metadata is None:
                raise RedetectionError("원본 영상 metadata를 읽을 수 없습니다.")
            if (int(metadata.width), int(metadata.height)) != (
                recipe.reference_frame_width,
                recipe.reference_frame_height,
            ):
                raise RedetectionError(
                    "원본 영상 해상도가 결과 snapshot과 일치하지 않습니다. "
                    f"영상 {metadata.width}×{metadata.height}, snapshot "
                    f"{recipe.reference_frame_width}×{recipe.reference_frame_height}"
                )

            self._check_cancelled(cancellation)
            self._emit(
                progress,
                request,
                "static_artifact_learning",
                0,
                display_total,
                None,
                "고정 artifact 학습",
            )
            learn_static_artifacts(
                reader,
                detector,
                [glass],
                full_static_artifact_schedule(request),
                decoded_frame_cache=decoded_frame_cache,
            )

            display_samples: list[RedetectionSample] = []
            processed_display = 0
            consecutive_failures = 0
            for nominal_timestamp, warmup in schedule:
                self._check_cancelled(cancellation)
                detection = None
                artifacts = None
                frame_index = None
                actual_timestamp = None
                detection_error: Exception | None = None
                try:
                    decoded = decoded_frame_cache.pop(nominal_timestamp, None)
                    if decoded is None:
                        decoded = reader.read_at(nominal_timestamp)
                    frame, frame_index, actual_timestamp = decoded
                    detection, artifacts = detector.detect(
                        frame,
                        glass,
                        frame_index,
                        actual_timestamp,
                        debug=True,
                    )
                except Exception as exc:
                    detection_error = exc
                    consecutive_failures += 1
                    LOGGER.exception(
                        "Redetection sample failed at %.9f", nominal_timestamp
                    )
                else:
                    consecutive_failures = 0

                if detection_error is not None:
                    if request.mode is RedetectionMode.CURRENT:
                        raise RedetectionError(
                            "현재 장면 재검출에 실패했습니다: "
                            f"{type(detection_error).__name__}: {detection_error}"
                        ) from detection_error
                    if (
                        consecutive_failures
                        >= self.policy.max_consecutive_sample_failures
                    ):
                        raise RedetectionError(
                            "연속된 frame decode 또는 detector 실패로 재검출을 "
                            "계속할 수 없습니다."
                        ) from detection_error
                    if warmup:
                        continue
                    sample = RedetectionSample(
                        nominal_timestamp_sec=nominal_timestamp,
                        requested_timestamp_sec=nominal_timestamp,
                        actual_timestamp_sec=None,
                        frame_index=None,
                        tracking_sample=None,
                        fill_state=None,
                        confidence=None,
                        is_valid=False,
                        flags=("REDETECTION_SAMPLE_FAILED",),
                        selected_candidate=None,
                        debug_record_id="",
                        error_message=(
                            f"{type(detection_error).__name__}: {detection_error}"
                        ),
                    )
                else:
                    if warmup:
                        continue
                    tracking = tracking_sample_from_detection(
                        workspace.run_id,
                        glass,
                        detection,
                    )
                    record_id = workspace.write_detection(
                        glass,
                        detection,
                        artifacts,
                    )
                    sample = RedetectionSample(
                        nominal_timestamp_sec=nominal_timestamp,
                        requested_timestamp_sec=nominal_timestamp,
                        actual_timestamp_sec=actual_timestamp,
                        frame_index=frame_index,
                        tracking_sample=tracking,
                        fill_state=tracking.fill_state,
                        confidence=tracking.overall_confidence,
                        is_valid=tracking.is_valid,
                        flags=tuple(tracking.flags),
                        selected_candidate=_selected_candidate(detection),
                        debug_record_id=record_id,
                    )
                workspace.append_sample(sample)
                display_samples.append(sample)
                processed_display += 1
                self._emit(
                    progress,
                    request,
                    "redetection",
                    processed_display,
                    display_total,
                    nominal_timestamp,
                    "재검출",
                )

            succeeded = [sample for sample in display_samples if sample.succeeded]
            if not succeeded:
                raise RedetectionError(
                    "표시 구간에서 성공한 재검출 sample이 없습니다."
                )

            self._check_cancelled(cancellation)
            self._emit(
                progress,
                request,
                "comparison",
                display_total,
                display_total,
                None,
                "공식 결과와 비교 계산",
            )
            official_samples = tuple(
                sample
                for sample in official_bundle.samples
                if sample.glass_id == request.selected_glass_id
            )
            comparisons = align_redetection_samples(
                request,
                official_samples,
                tuple(display_samples),
                session.sampling_fps,
                official_candidate_timestamps=official_candidate_timestamps,
                policy=self.policy,
            )

            rerun_events: list[EventMarker] = []
            event_comparisons = ()
            official_state = None
            official_note = ""
            rerun_state = None
            rerun_note = ""
            rerun_coverage = None
            if request.mode is not RedetectionMode.CURRENT:
                self._emit(
                    progress,
                    request,
                    "event_judgment",
                    display_total,
                    display_total,
                    None,
                    "이벤트와 판정 계산",
                )
                tracking_samples = [
                    _tracking_for_event_and_judgment(workspace.run_id, glass.id, sample)
                    for sample in display_samples
                ]
                rerun_events = detect_events_for_glass(
                    workspace.run_id,
                    glass.id,
                    tracking_samples,
                )
                if request.mode is RedetectionMode.FULL:
                    if session.compressor_start_sec is not None:
                        closest = min(
                            tracking_samples,
                            key=lambda item: abs(
                                item.timestamp_sec - session.compressor_start_sec
                            ),
                        )
                        rerun_events.append(
                            EventMarker(
                                workspace.run_id,
                                glass.id,
                                EventType.COMPRESSOR_START,
                                session.compressor_start_sec,
                                representative_frame_index=(
                                    closest.frame_index if closest.frame_index >= 0 else None
                                ),
                                confidence=1.0,
                            )
                        )
                    outcome = judge_samples(
                        tracking_samples,
                        glass.judgment_rule,
                        session.compressor_start_sec,
                    )
                    rerun_state = outcome.state
                    rerun_note = outcome.note
                    rerun_coverage = outcome.valid_coverage_ratio
                    rerun_events.append(
                        EventMarker(
                            workspace.run_id,
                            glass.id,
                            EventType.JUDGMENT_PASS
                            if outcome.state is ResultState.PASS
                            else EventType.JUDGMENT_FAIL
                            if outcome.state is ResultState.FAIL
                            else EventType.REVIEW_REQUIRED,
                            tracking_samples[-1].timestamp_sec,
                            representative_frame_index=(
                                tracking_samples[-1].frame_index
                                if tracking_samples[-1].frame_index >= 0
                                else None
                            ),
                            confidence=outcome.valid_coverage_ratio,
                            note=outcome.note,
                        )
                    )
                    official_summary = official_bundle.glass_summary(glass.id)
                    if official_summary is not None:
                        official_state = official_summary.result_state
                    official_note = _official_judgment_note(
                        official_bundle.events,
                        glass.id,
                    )
                    if not official_note:
                        notes = official_bundle.manifest.get("glass_judgment_notes")
                        if isinstance(notes, dict):
                            official_note = str(notes.get(glass.id, ""))
                else:
                    rerun_note = (
                        "구간 참고 결과입니다. 짧은 구간만으로 전체 시험 "
                        "PASS/FAIL을 확정하지 않습니다."
                    )
                official_events = _official_events_for_request(
                    official_bundle.events,
                    request,
                )
                event_comparisons = compare_events(
                    official_events,
                    rerun_events,
                    session.sampling_fps,
                    policy=self.policy,
                )

            summary = summarize_comparison(
                comparisons,
                event_comparisons,
                official_judgment=official_state,
                rerun_judgment=rerun_state,
            )
            settings_diffs = compare_detector_settings(
                baseline_settings,
                temporary_settings,
            )
            self._emit(
                progress,
                request,
                "workspace_finalize",
                display_total,
                display_total,
                None,
                "workspace 완료",
            )
            workspace.finalize()
            result = RedetectionResult(
                request=request,
                workspace_root=str(workspace.root),
                settings_diffs=settings_diffs,
                samples=tuple(display_samples),
                comparisons=comparisons,
                rerun_events=tuple(
                    sorted(
                        rerun_events,
                        key=lambda event: (
                            event.start_time_sec,
                            event.event_type.value,
                        ),
                    )
                ),
                event_comparisons=event_comparisons,
                summary=summary,
                official_judgment_note=official_note,
                rerun_judgment_note=rerun_note,
                rerun_valid_coverage_ratio=rerun_coverage,
                candidate_baseline_available=bool(
                    official_candidate_timestamps
                ),
                limitation_message=_limitation_message(request.mode),
                warnings=tuple(
                    sample.error_message
                    for sample in display_samples
                    if sample.error_message
                ),
            )
            return RedetectionRunOutput(result=result, workspace=workspace)
        except Exception:
            if workspace is not None:
                workspace.cleanup()
            raise
        finally:
            decoded_frame_cache.clear()
            if reader is not None:
                try:
                    reader.close()
                except Exception:
                    LOGGER.exception("Redetection reader close failed")
            detector = None

    @staticmethod
    def _check_cancelled(cancellation) -> None:
        if cancellation is not None and cancellation.cancelled:
            raise RedetectionCancelled("재검출이 취소되었습니다.")

    @staticmethod
    def _emit(
        progress,
        request,
        stage,
        processed,
        total,
        timestamp,
        message,
    ) -> None:
        if progress is not None:
            progress(
                RedetectionProgress(
                    generation=request.generation,
                    stage=stage,
                    processed_samples=processed,
                    total_samples=total,
                    current_timestamp_sec=timestamp,
                    message=message,
                )
            )


def _tracking_for_event_and_judgment(
    run_id: str,
    glass_id: str,
    sample: RedetectionSample,
) -> TrackingSample:
    if sample.tracking_sample is not None:
        return sample.tracking_sample
    return TrackingSample(
        run_id=run_id,
        glass_id=glass_id,
        frame_index=-1,
        timestamp_sec=sample.nominal_timestamp_sec,
        fill_state=FillState.UNKNOWN_REVIEW,
        overall_confidence=0.0,
        is_valid=False,
        flags=["DETECTION_LOST", "REDETECTION_SAMPLE_FAILED"],
    )


def _official_judgment_note(events, glass_id: str) -> str:
    judgment_types = {
        EventType.JUDGMENT_PASS,
        EventType.JUDGMENT_FAIL,
        EventType.REVIEW_REQUIRED,
    }
    candidates = [
        event
        for event in events
        if event.glass_id == glass_id
        and event.event_type in judgment_types
        and str(getattr(event, "note", "") or "")
    ]
    if not candidates:
        return ""
    selected = max(
        candidates,
        key=lambda event: (
            event.start_time_sec,
            getattr(event, "input_order", 0),
        ),
    )
    return str(selected.note)


def _selected_candidate(detection) -> RedetectionCandidate | None:
    ordered = sorted(
        detection.candidates,
        key=lambda candidate: (
            -candidate.final_score,
            candidate.y,
            candidate.source,
        ),
    )
    for rank, candidate in enumerate(ordered, 1):
        if candidate.selected:
            return RedetectionCandidate(
                rank=rank,
                kind=candidate.kind.value,
                source=candidate.source,
                canonical_y=candidate.y,
                feature_score=candidate.feature_score,
                total_penalty=candidate.penalty,
                final_score=candidate.final_score,
                selected=True,
                rejected=candidate.rejected,
                reject_reason=candidate.reject_reason,
                features=dict(candidate.features),
                penalties=dict(candidate.penalties),
            )
    return None


def _official_events_for_request(events, request):
    selected = [
        event
        for event in events
        if event.glass_id == request.selected_glass_id
    ]
    if request.mode is RedetectionMode.FULL:
        return tuple(selected)
    start = request.requested_range.display_start_sec
    end = request.requested_range.display_end_sec
    return tuple(
        event
        for event in selected
        if event.start_time_sec <= end
        and (
            event.end_time_sec
            if event.end_time_sec is not None
            else event.start_time_sec
        )
        >= start
    )


def _limitation_message(mode: RedetectionMode) -> str:
    if mode is RedetectionMode.CURRENT:
        return (
            "현재 장면만 독립적으로 검출한 결과입니다. 공식 분석의 temporal "
            "smoothing과 상태 이력은 완전히 재현되지 않을 수 있습니다."
        )
    if mode is RedetectionMode.SHORT:
        return (
            "짧은 구간 이전의 전체 분석 이력은 포함되지 않습니다. 가까운 "
            "temporal context를 사용한 비교 결과입니다. 전체 시험 판정이 아닌 "
            "구간 참고 결과입니다."
        )
    return (
        "분석 snapshot의 전체 timestamp schedule과 판정 규칙을 사용한 선택 "
        "관찰창 재검출 결과입니다."
    )
