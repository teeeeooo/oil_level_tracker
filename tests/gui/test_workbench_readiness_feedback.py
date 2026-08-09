from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import (
    FillState,
    InitialObservationState,
    ValidationSeverity,
    WorkbenchState,
)
from oil_tracker.domain.session import InitialStateConfirmation, VideoMetadata
from oil_tracker.domain.validation import ValidationIssue, ValidationResult
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow
from oil_tracker.ui.widgets.detection_summary_card import DetectionSummaryCard
from oil_tracker.ui.widgets.glass_list_panel import GlassListPanel
from oil_tracker.ui.widgets.workbench_progress import WorkbenchProgressWidget


class DummyPreviewController(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def __init__(self):
        super().__init__()
        self.invalidations = 0
        self.requests = []

    def invalidate(self):
        self.invalidations += 1

    def request(self, frame, glass, frame_index, time_sec):
        self.requests.append((glass.id, frame_index, time_sec))


class DummyAnalysisController(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()

    def start(self, *_args):
        pass

    def cancel(self):
        pass


class DummyRenderer:
    def export(self, *_args):
        return []


def _controller() -> WorkbenchController:
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )


def _window(qtbot):
    workbench = _controller()
    preview = DummyPreviewController()
    window = MainWindow(workbench, preview, DummyAnalysisController(), DummyRenderer())
    qtbot.addWidget(window)
    window.show()
    return window, workbench, preview


def test_glass_list_shows_text_status_and_activates_issue(qtbot):
    panel = GlassListPanel()
    qtbot.addWidget(panel)
    from oil_tracker.domain.recipe import InspectionRecipe
    from oil_tracker.ui.readiness import glass_readiness_by_id

    glass = InspectionRecipe.default_glass(640, 480)
    issue = ValidationIssue(ValidationSeverity.ERROR, "READY_ZERO", "zero", glass.id, "zero_line_y")
    result = ValidationResult([issue])
    panel.set_glasses([glass], glass.id, glass_readiness_by_id([glass], result))
    item = panel.list.item(0)
    assert "수정 필요" in item.text()
    assert "기준점 설정 필요" in item.text()
    with qtbot.waitSignal(panel.issueActivated) as blocker:
        panel._activated(item)
    assert blocker.args == [issue]


def test_progress_widget_emits_clicked_step(qtbot):
    widget = WorkbenchProgressWidget()
    qtbot.addWidget(widget)
    with qtbot.waitSignal(widget.stepActivated) as blocker:
        widget._buttons["glasses"].click()
    assert blocker.args == ["glasses"]


def test_detection_card_loading_failure_and_result(qtbot):
    from oil_tracker.domain.recipe import InspectionRecipe

    card = DetectionSummaryCard()
    qtbot.addWidget(card)
    glass = InspectionRecipe.default_glass(640, 480)
    card.set_loading()
    assert card.values["status"].text() == "분석 중"
    card.set_failure("후보 없음")
    assert card.values["judgment"].text() == "후보 없음"
    detection = PhaseDetection(
        glass.id,
        1,
        0.1,
        FillState.PARTIAL_VISIBLE,
        oil_air_level_y=200,
        oil_air_level_px_from_zero=10,
        overall_confidence=0.9,
    )
    card.set_detection(detection, glass)
    assert card.property("quality") == "normal"
    assert "위" in card.values["reference"].text()


def test_navigation_selects_first_error_glass_focuses_field_and_canvas(qtbot):
    window, workbench, _preview = _window(qtbot)
    first = workbench.add_glass()
    second = workbench.add_glass()
    workbench.set_selected(first.id)
    issue = ValidationIssue(ValidationSeverity.ERROR, "STRUCT_ELLIPSE", "geometry", second.id, "geometry")
    window._apply_validation_result(ValidationResult([issue]))
    window._navigate_next_issue()
    assert workbench.selected_glass_id == second.id
    assert window.canvas._selected_id == second.id
    assert window.settings._last_focused_field == "geometry"
    assert "분석 영역 타원" in validation_issue_text(window)


def test_navigation_falls_back_to_warning_when_no_error(qtbot):
    window, workbench, _preview = _window(qtbot)
    first = workbench.add_glass()
    second = workbench.add_glass()
    warning = ValidationIssue(ValidationSeverity.WARNING, "WARN_ZERO_EDGE", "zero", second.id, "zero_line_y")
    window._apply_validation_result(ValidationResult([warning]))
    window._navigate_next_issue()
    assert workbench.selected_glass_id == second.id
    assert window.settings._last_focused_field == "zero_line_y"


def test_preview_rejects_stale_glass_and_frame_results(qtbot):
    window, workbench, preview = _window(qtbot)
    glass = workbench.add_glass()
    workbench.session.input_video_path = "video.mp4"
    workbench.session.video_metadata = VideoMetadata("video.mp4", 1280, 720, 30.0, 10.0, 300)
    window.current_frame_index = 10
    window.current_time = 1.0
    window._preview_context = (glass.id, 10, 1.0)
    stale = PhaseDetection(glass.id, 9, 0.9, FillState.PARTIAL_VISIBLE, oil_air_level_y=200, overall_confidence=0.9)
    window._preview_ready(stale, object())
    assert window.canvas._detection is None
    current = PhaseDetection(glass.id, 10, 1.0, FillState.PARTIAL_VISIBLE, oil_air_level_y=200, overall_confidence=0.9)
    window._preview_ready(current, None)
    assert window.canvas._detection is current

    other = workbench.add_glass()
    window._preview_context = (other.id, 10, 1.0)
    window.canvas.set_detection(None)
    window._preview_ready(current, None)
    assert window.canvas._detection is None

    window.schedule_preview()
    assert window.canvas._detection is None
    assert preview.invalidations > 0


def test_inline_validation_does_not_validate_until_explicit_check(qtbot):
    window, workbench, _preview = _window(qtbot)
    glass = workbench.add_glass()
    glass.initial_state = InitialObservationState.EMPTY_NO_INTERFACE
    workbench.session.input_video_path = "video.mp4"
    workbench.session.video_metadata = VideoMetadata("video.mp4", 1280, 720, 30.0, 10.0, 300)
    workbench.session.analysis_end_sec = 10.0
    workbench.session.compressor_start_sec = 1.0
    workbench.session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
        glass.initial_state,
        workbench.session.input_video_path,
        workbench.session.analysis_start_sec,
    )
    workbench.state = WorkbenchState.DRAFT
    result = window._refresh_inline_validation()
    assert result.is_ready
    assert workbench.state == WorkbenchState.DRAFT
    assert not window.action_bar.analyze_button.isEnabled()
    window.validate_workbench()
    assert workbench.state == WorkbenchState.VALIDATED
    assert window.action_bar.analyze_button.isEnabled()
    workbench.mark_dirty()
    window._refresh_inline_validation()
    assert workbench.state == WorkbenchState.DRAFT_DIRTY
    assert not window.action_bar.analyze_button.isEnabled()


def validation_issue_text(window) -> str:
    return window.statusBar().currentMessage()
