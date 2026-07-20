from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from oil_tracker.application.detection_quality import (
    DetectionQuality as PreviewQuality,
    assess_detection_quality,
)
from oil_tracker.domain.enums import ValidationSeverity, WorkbenchState
from oil_tracker.ui.presentation_labels import fill_state_label, validation_issue_short_message


class GlassReadinessState(str, Enum):
    COMPLETE = "complete"
    REVIEW = "review"
    ERROR = "error"
    EXCLUDED = "excluded"


class ProgressStepState(str, Enum):
    COMPLETE = "complete"
    CURRENT = "current"
    ERROR = "error"
    WARNING = "warning"
    WAITING = "waiting"


@dataclass(frozen=True)
class GlassReadiness:
    glass_id: str
    state: GlassReadinessState
    label: str
    symbol: str
    reason: str = ""
    issue: object | None = None


@dataclass(frozen=True)
class ProgressStep:
    key: str
    label: str
    state: ProgressStepState
    detail: str


@dataclass(frozen=True)
class PreviewSummary:
    quality: PreviewQuality
    detection_status: str
    fill_state: str
    confidence: str
    reference_position: str
    judgment: str


_SEVERITY_ORDER = {
    ValidationSeverity.ERROR: 0,
    ValidationSeverity.WARNING: 1,
    ValidationSeverity.INFORMATION: 2,
}

_FIELD_ORDER = {
    "geometry": 0,
    "reference_frame": 1,
    "zero_line_y": 10,
    "exclusions": 20,
    "judgment_mode": 30,
    "judgment_rule": 30,
    "compressor_start": 31,
    "margin": 40,
    "mm_per_pixel": 41,
    "minimum_final_confidence": 42,
    "detector_settings": 42,
}

_STATE_LABELS = {
    GlassReadinessState.COMPLETE: ("완료", "✓"),
    GlassReadinessState.REVIEW: ("확인 필요", "⚠"),
    GlassReadinessState.ERROR: ("수정 필요", "●"),
    GlassReadinessState.EXCLUDED: ("분석 제외", "—"),
}


def issue_sort_key(issue) -> tuple[int, int, str]:
    return (
        _SEVERITY_ORDER.get(issue.severity, 99),
        _FIELD_ORDER.get(issue.field or "", 90),
        issue.code,
    )


def prioritize_issues(issues) -> list:
    return sorted(issues, key=issue_sort_key)


def glass_readiness(glass, validation_result) -> GlassReadiness:
    if not glass.enabled:
        label, symbol = _STATE_LABELS[GlassReadinessState.EXCLUDED]
        return GlassReadiness(glass.id, GlassReadinessState.EXCLUDED, label, symbol)

    related = [
        issue
        for issue in validation_result.issues
        if issue.glass_id == glass.id
        and issue.severity in {ValidationSeverity.ERROR, ValidationSeverity.WARNING}
    ]
    ordered = prioritize_issues(related)
    issue = ordered[0] if ordered else None
    if any(item.severity == ValidationSeverity.ERROR for item in related):
        state = GlassReadinessState.ERROR
        issue = prioritize_issues(
            item for item in related if item.severity == ValidationSeverity.ERROR
        )[0]
    elif any(item.severity == ValidationSeverity.WARNING for item in related):
        state = GlassReadinessState.REVIEW
        issue = prioritize_issues(
            item for item in related if item.severity == ValidationSeverity.WARNING
        )[0]
    else:
        state = GlassReadinessState.COMPLETE
    label, symbol = _STATE_LABELS[state]
    reason = validation_issue_short_message(issue) if issue is not None else ""
    return GlassReadiness(glass.id, state, label, symbol, reason, issue)


def glass_readiness_by_id(glasses, validation_result) -> dict[str, GlassReadiness]:
    return {glass.id: glass_readiness(glass, validation_result) for glass in glasses}


def first_actionable_issue(glasses, validation_result):
    summaries = glass_readiness_by_id(glasses, validation_result)
    for target_state in (GlassReadinessState.ERROR, GlassReadinessState.REVIEW):
        for glass in glasses:
            summary = summaries[glass.id]
            if summary.state == target_state:
                return summary.issue
    return None


def first_issue_for_fields(validation_result, fields: set[str], *, errors_only: bool = False):
    issues = [
        issue
        for issue in validation_result.issues
        if issue.field in fields
        and (not errors_only or issue.severity == ValidationSeverity.ERROR)
    ]
    ordered = prioritize_issues(issues)
    return ordered[0] if ordered else None


def first_validation_error(validation_result):
    ordered = prioritize_issues(validation_result.errors)
    return ordered[0] if ordered else None


def build_workbench_progress(recipe, session, state: WorkbenchState, validation_result) -> list[ProgressStep]:
    errors = validation_result.errors
    warnings = validation_result.warnings
    video_fields = {"input_video_path", "video_metadata"}
    time_fields = {"analysis_range", "sampling_fps", "compressor_start"}

    video_errors = [issue for issue in errors if issue.field in video_fields]
    video_warnings = [issue for issue in warnings if issue.field in video_fields]
    time_errors = [issue for issue in errors if issue.field in time_fields]
    time_warnings = [issue for issue in warnings if issue.field in time_fields]
    glass_errors = [
        issue
        for issue in errors
        if issue.code == "READY_GLASS"
        or (issue.glass_id is not None and issue.field not in time_fields)
    ]
    glass_warnings = [
        issue
        for issue in warnings
        if issue.glass_id is not None and issue.field not in time_fields
    ]

    video_complete = bool(session.input_video_path and session.video_metadata and not video_errors)
    if not session.input_video_path:
        video_step = ProgressStep("video", "영상 선택", ProgressStepState.CURRENT, "시험 영상을 선택해 주세요")
    elif not video_complete:
        video_step = ProgressStep("video", "영상 선택", ProgressStepState.ERROR, "영상 정보 확인 필요")
    elif video_warnings:
        video_step = ProgressStep("video", "영상 선택", ProgressStepState.WARNING, "영상 조건 확인 필요")
    else:
        video_step = ProgressStep("video", "영상 선택", ProgressStepState.COMPLETE, "영상 정보 읽음")

    if not video_complete:
        time_step = ProgressStep("time", "시간 설정", ProgressStepState.WAITING, "영상 선택 후 설정")
    elif time_errors:
        time_step = ProgressStep("time", "시간 설정", ProgressStepState.ERROR, "시간 조건 수정 필요")
    elif time_warnings:
        time_step = ProgressStep("time", "시간 설정", ProgressStepState.WARNING, "시간 조건 확인 필요")
    else:
        time_step = ProgressStep("time", "시간 설정", ProgressStepState.COMPLETE, "분석 시간 설정 완료")

    enabled_count = sum(1 for glass in recipe.glasses if glass.enabled)
    if enabled_count == 0:
        glass_state = ProgressStepState.CURRENT if video_complete else ProgressStepState.WAITING
        glass_step = ProgressStep("glasses", "관찰창 설정", glass_state, "분석할 관찰창이 필요함")
    elif glass_errors:
        glass_step = ProgressStep("glasses", "관찰창 설정", ProgressStepState.ERROR, "관찰창 수정 필요")
    elif glass_warnings:
        glass_step = ProgressStep("glasses", "관찰창 설정", ProgressStepState.WARNING, "관찰창 확인 필요")
    else:
        glass_step = ProgressStep(
            "glasses", "관찰창 설정", ProgressStepState.COMPLETE, f"{enabled_count}개 설정 완료"
        )

    prerequisites_ready = not errors and enabled_count > 0 and video_complete
    validated = state in {WorkbenchState.VALIDATED, WorkbenchState.ANALYZING, WorkbenchState.ANALYZED}
    if validated:
        validation_step = ProgressStep("validation", "설정 점검", ProgressStepState.COMPLETE, "설정 점검 완료")
    elif prerequisites_ready and state == WorkbenchState.DRAFT_DIRTY:
        validation_step = ProgressStep("validation", "설정 점검", ProgressStepState.CURRENT, "변경 후 재점검 필요")
    elif prerequisites_ready:
        validation_step = ProgressStep("validation", "설정 점검", ProgressStepState.CURRENT, "설정 점검을 실행해 주세요")
    else:
        validation_step = ProgressStep("validation", "설정 점검", ProgressStepState.WAITING, "앞 단계 완료 후 실행")

    if state == WorkbenchState.ANALYZING:
        analysis_step = ProgressStep("analysis", "분석 실행", ProgressStepState.CURRENT, "분석 중")
    elif state == WorkbenchState.ANALYZED:
        analysis_step = ProgressStep("analysis", "분석 실행", ProgressStepState.COMPLETE, "분석 완료")
    elif state == WorkbenchState.VALIDATED:
        analysis_step = ProgressStep("analysis", "분석 실행", ProgressStepState.CURRENT, "분석 실행 가능")
    else:
        analysis_step = ProgressStep("analysis", "분석 실행", ProgressStepState.WAITING, "설정 점검 후 실행")

    return [video_step, time_step, glass_step, validation_step, analysis_step]


def build_detection_summary(detection, glass) -> PreviewSummary:
    if detection is None:
        return PreviewSummary(
            PreviewQuality.FAILURE,
            "검출 실패",
            "-",
            "-",
            "-",
            "검출 결과가 없습니다",
        )

    confidence = max(0.0, min(1.0, float(detection.overall_confidence)))
    threshold = float(glass.detector_settings.minimum_final_confidence)
    assessment = assess_detection_quality(detection, threshold)
    quality = assessment.quality
    if quality == PreviewQuality.FAILURE:
        detection_status = "검출 실패"
    elif quality == PreviewQuality.REVIEW:
        detection_status = "확인 필요"
    else:
        detection_status = "유면 확인됨" if detection.oil_air_level_y is not None else "유면 경계 미표시"

    reference_position = _reference_position(detection, glass)
    return PreviewSummary(
        quality=quality,
        detection_status=detection_status,
        fill_state=fill_state_label(detection.fill_state),
        confidence=f"{confidence * 100:.0f}%",
        reference_position=reference_position,
        judgment=assessment.reason,
    )


def _reference_position(detection, glass) -> str:
    if glass.geometry.zero_line_y is None:
        return "기준점 미설정"
    px = detection.oil_air_level_px_from_zero
    if px is None and detection.oil_air_level_y is not None:
        px = glass.geometry.zero_line_y - detection.oil_air_level_y
    if px is None:
        return "유면 경계가 화면에 없음"
    px = float(px)
    if abs(px) < 0.05:
        return "기준점과 같은 위치"
    direction = "위" if px > 0 else "아래"
    text = f"기준점보다 {abs(px):.1f} px {direction}"
    if glass.mm_per_pixel is not None:
        mm = detection.oil_air_level_mm_from_zero
        if mm is None:
            mm = px * glass.mm_per_pixel
        text += f" ({abs(float(mm)):.2f} mm)"
    return text
