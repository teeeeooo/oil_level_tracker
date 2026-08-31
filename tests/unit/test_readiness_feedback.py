from __future__ import annotations

from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState, ValidationSeverity, WorkbenchState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, VideoMetadata
from oil_tracker.domain.validation import ValidationIssue, ValidationResult
from oil_tracker.ui.readiness import (
    GlassReadinessState,
    PreviewQuality,
    ProgressStepState,
    build_detection_summary,
    build_workbench_progress,
    first_actionable_issue,
    glass_readiness,
)


def _glass():
    return InspectionRecipe.default_glass(640, 480)


def test_glass_readiness_states_and_global_issue_isolation():
    glass = _glass()
    glass.enabled = False
    result = ValidationResult([ValidationIssue(ValidationSeverity.ERROR, "READY_VIDEO", "missing")])
    assert glass_readiness(glass, result).state == GlassReadinessState.EXCLUDED

    glass.enabled = True
    error = ValidationIssue(ValidationSeverity.ERROR, "READY_ZERO", "missing", glass.id, "zero_line_y")
    assert glass_readiness(glass, ValidationResult([error])).state == GlassReadinessState.ERROR
    warning = ValidationIssue(ValidationSeverity.WARNING, "WARN_SCALE", "scale", glass.id, "mm_per_pixel")
    assert glass_readiness(glass, ValidationResult([warning])).state == GlassReadinessState.REVIEW
    assert glass_readiness(glass, result).state == GlassReadinessState.COMPLETE
    assert glass_readiness(glass, ValidationResult([])).state == GlassReadinessState.COMPLETE


def test_glass_reason_priority_prefers_geometry_then_zero_then_scale():
    glass = _glass()
    issues = [
        ValidationIssue(ValidationSeverity.ERROR, "STRUCT_SCALE", "scale", glass.id, "mm_per_pixel"),
        ValidationIssue(ValidationSeverity.ERROR, "READY_ZERO", "zero", glass.id, "zero_line_y"),
        ValidationIssue(ValidationSeverity.ERROR, "STRUCT_ELLIPSE", "ellipse", glass.id, "geometry"),
    ]
    summary = glass_readiness(glass, ValidationResult(issues))
    assert summary.issue.code == "STRUCT_ELLIPSE"
    assert summary.reason == "분석 영역 수정 필요"


def test_first_actionable_issue_prefers_error_glass_before_warning_glass():
    recipe = InspectionRecipe.empty(640, 480)
    first = InspectionRecipe.default_glass(640, 480, 1)
    second = InspectionRecipe.default_glass(640, 480, 2)
    recipe.glasses = [first, second]
    warning = ValidationIssue(ValidationSeverity.WARNING, "WARN_SCALE", "scale", first.id, "mm_per_pixel")
    error = ValidationIssue(ValidationSeverity.ERROR, "READY_ZERO", "zero", second.id, "zero_line_y")
    assert first_actionable_issue(recipe.glasses, ValidationResult([warning, error])) == error


def test_detection_summary_normal_review_failure_and_position_units():
    glass = _glass()
    glass.mm_per_pixel = 0.2
    normal = PhaseDetection(
        glass.id,
        5,
        1.5,
        FillState.PARTIAL_VISIBLE,
        oil_air_level_y=250.0,
        oil_air_level_px_from_zero=-12.4,
        overall_confidence=0.87,
    )
    summary = build_detection_summary(normal, glass)
    assert summary.quality == PreviewQuality.NORMAL
    assert summary.confidence == "87%"
    assert "12.4 px 아래" in summary.reference_position
    assert "2.48 mm" in summary.reference_position
    assert summary.recommendation == "추가 조치가 필요하지 않습니다."
    assert summary.action_key is None

    review = PhaseDetection(glass.id, 5, 1.5, FillState.UNKNOWN_REVIEW, overall_confidence=0.8)
    assert build_detection_summary(review, glass).quality == PreviewQuality.REVIEW
    low = PhaseDetection(glass.id, 5, 1.5, FillState.PARTIAL_VISIBLE, oil_air_level_y=250, overall_confidence=0.1)
    assert build_detection_summary(low, glass).quality == PreviewQuality.REVIEW
    failed = PhaseDetection(glass.id, 5, 1.5, FillState.PARTIAL_VISIBLE, overall_confidence=0.9)
    assert build_detection_summary(failed, glass).quality == PreviewQuality.FAILURE


def test_foam_detection_summary_separates_interpretation_recommendation_and_action():
    glass = _glass()
    foam = PhaseDetection(
        glass.id,
        1,
        0.0,
        FillState.FOAMING_VISIBLE,
        oil_air_level_y=200.0,
        overall_confidence=0.8,
    )
    summary = build_detection_summary(foam, glass)
    assert summary.quality == PreviewQuality.REVIEW
    assert summary.interpretation == "거품 가능성이 감지됨"
    assert summary.recommendation == "분석 시작 장면의 거품이라면 시작 상태를 ‘거품이 보임’으로 설정하고 확인하세요."
    assert summary.action_key == "initial_state"


def test_detection_summary_reports_above_and_missing_reference():
    glass = _glass()
    detection = PhaseDetection(
        glass.id,
        1,
        0.0,
        FillState.PARTIAL_VISIBLE,
        oil_air_level_y=200.0,
        oil_air_level_px_from_zero=10.0,
        overall_confidence=0.9,
    )
    assert "10.0 px 위" in build_detection_summary(detection, glass).reference_position
    glass.geometry.zero_line_y = None
    assert build_detection_summary(detection, glass).reference_position == "기준점 미설정"


def test_progress_states_cover_unselected_invalid_validated_and_dirty():
    recipe = InspectionRecipe.empty(640, 480)
    session = AnalysisSession()
    empty = build_workbench_progress(
        recipe,
        session,
        WorkbenchState.EMPTY,
        ValidationResult([ValidationIssue(ValidationSeverity.ERROR, "READY_VIDEO", "missing", field="input_video_path")]),
    )
    assert empty[0].state == ProgressStepState.CURRENT
    assert empty[-1].state == ProgressStepState.WAITING

    glass = InspectionRecipe.default_glass(640, 480)
    recipe.glasses = [glass]
    session.input_video_path = "video.mp4"
    session.video_metadata = VideoMetadata("video.mp4", 640, 480, 30.0, 10.0, 300)
    session.analysis_end_sec = 10.0
    session.compressor_start_sec = 1.0
    ready = build_workbench_progress(recipe, session, WorkbenchState.VALIDATED, ValidationResult([]))
    assert all(step.state == ProgressStepState.COMPLETE for step in ready[:4])
    assert ready[4].state == ProgressStepState.CURRENT
    assert ready[2].label == "Glass 설정"
    dirty = build_workbench_progress(recipe, session, WorkbenchState.DRAFT_DIRTY, ValidationResult([]))
    assert dirty[3].state == ProgressStepState.CURRENT
    assert "재점검" in dirty[3].detail


def test_progress_assigns_time_and_reference_errors_to_their_own_steps():
    recipe = InspectionRecipe.empty(640, 480)
    glass = InspectionRecipe.default_glass(640, 480)
    recipe.glasses = [glass]
    session = AnalysisSession(
        input_video_path="video.mp4",
        video_metadata=VideoMetadata("video.mp4", 640, 480, 30.0, 10.0, 300),
        analysis_end_sec=10.0,
        compressor_start_sec=1.0,
    )
    reference_issue = ValidationIssue(
        ValidationSeverity.ERROR,
        "READY_REFERENCE",
        "reference",
        glass.id,
        "reference_frame",
    )
    reference_steps = build_workbench_progress(
        recipe,
        session,
        WorkbenchState.DRAFT,
        ValidationResult([reference_issue]),
    )
    assert reference_steps[0].state == ProgressStepState.COMPLETE
    assert reference_steps[2].state == ProgressStepState.ERROR

    time_issue = ValidationIssue(
        ValidationSeverity.ERROR,
        "READY_RANGE",
        "range",
        field="analysis_range",
    )
    time_steps = build_workbench_progress(
        recipe,
        session,
        WorkbenchState.DRAFT,
        ValidationResult([time_issue]),
    )
    assert time_steps[0].state == ProgressStepState.COMPLETE
    assert time_steps[1].state == ProgressStepState.ERROR
