from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable

from oil_tracker.application.detection_quality import DetectionQuality, assess_detection_quality
from oil_tracker.application.preflight import (
    DEFAULT_PREFLIGHT_POLICY,
    PreflightCancelled,
    PreflightDetectionResult,
    PreflightPolicy,
    PreflightProgress,
    PreflightResult,
    PreflightSamplePoint,
    PreflightStatus,
    apply_position_jump_warnings,
    build_preflight_schedule,
    preflight_context_key,
    summarize_preflight,
)
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession


logger = logging.getLogger(__name__)


@dataclass
class PreflightCancellationToken:
    _cancelled: bool = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        self._cancelled = True


class PreflightCheckUseCase:
    def __init__(
        self,
        video_reader_factory: Callable[[str], object],
        detector_factory: Callable[[], object],
        validator: RecipeValidationService,
        policy: PreflightPolicy = DEFAULT_PREFLIGHT_POLICY,
    ) -> None:
        self.video_reader_factory = video_reader_factory
        self.detector_factory = detector_factory
        self.validator = validator
        self.policy = policy

    def execute(
        self,
        recipe: InspectionRecipe,
        session: AnalysisSession,
        progress: Callable[[PreflightProgress], None] | None = None,
        cancellation: object | None = None,
    ) -> PreflightResult:
        validation = self.validator.validate(recipe, session)
        if not validation.is_ready:
            codes = ", ".join(issue.code for issue in validation.errors[:3])
            raise ValueError(f"사전 점검 전에 설정 오류를 수정해 주세요. ({codes})")

        enabled = [glass for glass in recipe.glasses if glass.enabled]
        context_key = preflight_context_key(recipe, session)
        try:
            reader = self.video_reader_factory(session.input_video_path)
        except Exception as exc:
            raise ValueError(f"시험 영상을 열 수 없습니다: {exc}") from exc

        decoded: list[tuple[object, object, int, float]] = []
        decode_failures: dict[object, str] = {}
        try:
            end_sec = session.effective_end_sec()
            if end_sec is None:
                raise ValueError("분석 종료 시각이 없습니다.")
            schedule = build_preflight_schedule(
                session.analysis_start_sec,
                end_sec,
                reader.metadata,
                session.compressor_start_sec,
                self.policy,
            )
            if not schedule:
                raise ValueError("사전 점검 대표 시점을 만들 수 없습니다.")

            for request in schedule:
                self._raise_if_cancelled(cancellation)
                try:
                    frame, frame_index, actual_timestamp = reader.read_at(request.normalized_timestamp)
                    decoded.append((request, frame, frame_index, actual_timestamp))
                except Exception as exc:
                    logger.exception("Preflight frame decode failed at %.6fs", request.normalized_timestamp)
                    decode_failures[request] = str(exc)

            results: list[PreflightDetectionResult] = []
            total = len(schedule) * len(enabled)
            completed = 0
            decoded_by_request = {request: (frame, frame_index, actual) for request, frame, frame_index, actual in decoded}
            static_frames = [frame for _, frame, _, _ in decoded]

            for request in schedule:
                for glass in enabled:
                    self._raise_if_cancelled(cancellation)
                    decoded_item = decoded_by_request.get(request)
                    if decoded_item is None:
                        sample_point = PreflightSamplePoint(
                            labels=request.labels,
                            requested_timestamps=request.requested_timestamps,
                            requested_timestamp=request.requested_timestamp,
                            actual_timestamp=request.normalized_timestamp,
                            frame_index=request.frame_key,
                        )
                        results.append(
                            PreflightDetectionResult(
                                glass_id=glass.id,
                                glass_name=glass.name,
                                sample_point=sample_point,
                                fill_state=None,
                                confidence=None,
                                oil_level_y=None,
                                oil_level_px_from_zero=None,
                                oil_level_mm_from_zero=None,
                                foam_detected=False,
                                flags=("FRAME_DECODE_FAILED",),
                                status=PreflightStatus.FAILURE,
                                reason=f"영상 장면을 읽지 못했습니다: {decode_failures[request]}",
                            )
                        )
                    else:
                        frame, frame_index, actual_timestamp = decoded_item
                        sample_point = PreflightSamplePoint(
                            labels=request.labels,
                            requested_timestamps=request.requested_timestamps,
                            requested_timestamp=request.requested_timestamp,
                            actual_timestamp=float(actual_timestamp),
                            frame_index=int(frame_index),
                        )
                        results.append(self._detect_sample(static_frames, frame, frame_index, actual_timestamp, glass, sample_point))

                    completed += 1
                    if progress is not None:
                        progress(PreflightProgress(completed, total, request.label, glass.name))

            results = apply_position_jump_warnings(results, {glass.id: glass for glass in enabled}, self.policy)
            summaries, overall = summarize_preflight(results, enabled)
            return PreflightResult(
                overall_status=overall,
                samples=tuple(results),
                glass_summaries=summaries,
                video_path=session.input_video_path,
                context_key=context_key,
                analysis_start_sec=session.analysis_start_sec,
                analysis_end_sec=end_sec,
                compressor_start_sec=session.compressor_start_sec,
            )
        finally:
            reader.close()

    def _detect_sample(self, static_frames, frame, frame_index, actual_timestamp, glass, sample_point):
        detector = self.detector_factory()
        learn = getattr(detector, "learn_static_artifact", None)
        if callable(learn) and static_frames:
            try:
                learn(static_frames, glass)
            except Exception:
                logger.exception("Optional preflight static-artifact learning failed for glass %s", glass.id)
        try:
            detection, _ = detector.detect(frame, glass, frame_index, actual_timestamp, debug=False)
        except Exception as exc:
            logger.exception(
                "Preflight detector failed for glass %s at %.6fs",
                glass.id,
                actual_timestamp,
            )
            return PreflightDetectionResult(
                glass_id=glass.id,
                glass_name=glass.name,
                sample_point=sample_point,
                fill_state=None,
                confidence=None,
                oil_level_y=None,
                oil_level_px_from_zero=None,
                oil_level_mm_from_zero=None,
                foam_detected=False,
                flags=("DETECTOR_EXCEPTION",),
                status=PreflightStatus.FAILURE,
                reason=f"관찰창 검출 중 오류가 발생했습니다: {exc}",
            )

        assessment = assess_detection_quality(detection, glass.detector_settings.minimum_final_confidence)
        status = PreflightStatus(assessment.quality.value)
        flags = tuple(sorted({str(flag).upper() for flag in detection.flags}))
        foam_detected = (
            detection.foam_front_y is not None
            or detection.fill_state in {FillState.FULL_WITH_FOAM, FillState.FOAMING_VISIBLE}
            or any("FOAM" in flag for flag in flags)
        )
        return PreflightDetectionResult(
            glass_id=glass.id,
            glass_name=glass.name,
            sample_point=sample_point,
            fill_state=detection.fill_state,
            confidence=float(detection.overall_confidence),
            oil_level_y=detection.oil_air_level_y,
            oil_level_px_from_zero=detection.oil_air_level_px_from_zero,
            oil_level_mm_from_zero=detection.oil_air_level_mm_from_zero,
            foam_detected=foam_detected,
            flags=flags,
            status=status,
            reason=assessment.reason,
        )

    @staticmethod
    def _raise_if_cancelled(cancellation: object | None) -> None:
        if cancellation is not None and bool(getattr(cancellation, "cancelled", False)):
            raise PreflightCancelled("사전 점검이 취소되었습니다.")
