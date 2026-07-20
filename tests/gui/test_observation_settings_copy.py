from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog, QMessageBox

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.observation_settings_copy import (
    GlassSettingsCopyOptions,
    GlassSettingsCopyRequest,
)
from oil_tracker.application.preflight import preflight_context_key
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.enums import JudgmentMode, WorkbenchState
from oil_tracker.domain.geometry import EllipseGeometry
from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow
from oil_tracker.ui.observation_settings_copy_coordinator import ObservationSettingsCopyCoordinator
from oil_tracker.ui.preflight_coordinator import PreflightCoordinator
from oil_tracker.ui.widgets.glass_list_panel import GlassListPanel
from oil_tracker.ui.widgets.glass_settings_copy_dialog import GlassSettingsCopyDialog


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


class DummyPreflightController(QObject):
    started = Signal()
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self.invalidations = 0

    def start(self, *_args):
        self.started.emit()

    def cancel(self):
        self.cancelled.emit()

    def invalidate(self):
        self.invalidations += 1


class DummyRenderer:
    def export(self, *_args):
        return []


class FakeDialog:
    def __init__(self, request, result=QDialog.DialogCode.Accepted):
        self.request = request
        self.result = result

    def exec(self):
        return self.result

    def copy_request(self):
        return self.request


def _controller() -> WorkbenchController:
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
    )


def _window(qtbot):
    workbench = _controller()
    preview = DummyPreviewController()
    window = MainWindow(workbench, preview, DummyAnalysisController(), DummyRenderer())
    qtbot.addWidget(window)
    window.show()
    workbench.new_document(640, 480)
    source = workbench.add_glass()
    first = workbench.add_glass()
    second = workbench.add_glass()
    metadata = VideoMetadata("video.mp4", 640, 480, 10.0, 10.0, 100)
    workbench.session.input_video_path = metadata.path
    workbench.session.video_metadata = metadata
    workbench.session.analysis_start_sec = 0.0
    workbench.session.analysis_end_sec = 10.0
    workbench.session.compressor_start_sec = 2.0
    workbench.session.sampling_fps = 2.0
    workbench.set_selected(source.id)
    window._refresh_all()
    window._refresh_inline_validation()
    return window, workbench, preview, source.id, first.id, second.id


def _glass(workbench, glass_id):
    return next(glass for glass in workbench.recipe.glasses if glass.id == glass_id)


def _request(source_id, targets, options):
    return GlassSettingsCopyRequest(source_id, tuple(targets), options)


def test_copy_button_requires_selected_source_and_another_glass(qtbot):
    panel = GlassListPanel()
    qtbot.addWidget(panel)
    from oil_tracker.domain.recipe import InspectionRecipe

    first = InspectionRecipe.default_glass(640, 480, 1)
    second = InspectionRecipe.default_glass(640, 480, 2)
    panel.set_glasses([first], first.id)
    assert not panel.copy_button.isEnabled()
    panel.set_glasses([first, second], None)
    assert not panel.copy_button.isEnabled()
    panel.set_glasses([first, second], first.id)
    assert panel.copy_button.isEnabled()
    with qtbot.waitSignal(panel.copyRequested):
        panel.copy_button.click()


def test_dialog_shows_source_excludes_it_from_targets_and_uses_safe_defaults(qtbot):
    from oil_tracker.domain.recipe import InspectionRecipe

    recipe = InspectionRecipe.empty(640, 480)
    source = InspectionRecipe.default_glass(640, 480, 1)
    target = InspectionRecipe.default_glass(640, 480, 2)
    excluded = InspectionRecipe.default_glass(640, 480, 3)
    excluded.enabled = False
    source.mm_per_pixel = None
    recipe.glasses = [source, target, excluded]
    dialog = GlassSettingsCopyDialog(recipe, source.id)
    qtbot.addWidget(dialog)

    assert source.name in dialog.source_label.text()
    assert source.id not in dialog.target_checks
    assert set(dialog.target_checks) == {target.id, excluded.id}
    assert "분석 제외" in dialog.target_checks[excluded.id].text()
    assert not dialog.apply_button.isEnabled()
    assert [dialog.option_checks[key].isChecked() for key in (
        "judgment_rule", "detector_settings", "margin_ratio", "initial_state"
    )] == [True, True, True, True]
    assert not dialog.option_checks["mm_per_pixel"].isChecked()
    assert not dialog.option_checks["ellipse_size"].isChecked()
    assert "None 복사" in dialog.option_checks["mm_per_pixel"].text()
    assert "중심 위치와 기준점" in dialog.option_checks["ellipse_size"].toolTip()

    dialog.select_all_button.click()
    assert all(check.isChecked() for check in dialog.target_checks.values())
    assert dialog.apply_button.isEnabled()
    assert source.name in dialog.summary_label.text()
    dialog.clear_all_button.click()
    assert not any(check.isChecked() for check in dialog.target_checks.values())
    assert not dialog.apply_button.isEnabled()


def test_dialog_apply_requires_at_least_one_option(qtbot):
    from oil_tracker.domain.recipe import InspectionRecipe

    recipe = InspectionRecipe.empty(640, 480)
    source = InspectionRecipe.default_glass(640, 480, 1)
    target = InspectionRecipe.default_glass(640, 480, 2)
    recipe.glasses = [source, target]
    dialog = GlassSettingsCopyDialog(recipe, source.id)
    qtbot.addWidget(dialog)
    dialog.target_checks[target.id].setChecked(True)
    assert dialog.apply_button.isEnabled()
    for check in dialog.option_checks.values():
        check.setChecked(False)
    assert not dialog.apply_button.isEnabled()
    assert "설정 항목" in dialog.summary_label.text()


def test_cancel_leaves_recipe_undo_preview_and_state_unchanged(qtbot):
    window, workbench, preview, source_id, first_id, _second_id = _window(qtbot)
    coordinator = ObservationSettingsCopyCoordinator(window)
    before = workbench.recipe.to_dict()
    before_state = workbench.state
    request = _request(source_id, (first_id,), GlassSettingsCopyOptions())
    coordinator._create_dialog = lambda *_args: FakeDialog(request, QDialog.DialogCode.Rejected)

    coordinator.open_dialog()

    assert workbench.recipe.to_dict() == before
    assert workbench.state == before_state
    assert window.undo_stack.count() == 0
    assert preview.invalidations == 0


def test_apply_updates_multiple_targets_keeps_source_selected_and_undoes_as_one_command(qtbot):
    window, workbench, preview, source_id, first_id, second_id = _window(qtbot)
    source = _glass(workbench, source_id)
    source.judgment_rule.mode = JudgmentMode.HOLD_BELOW_ZERO
    source.judgment_rule.recovery_limit_sec = 88.0
    source.detector_settings.canny_low = 91
    source.geometry.margin_ratio = 0.16
    first_before = deepcopy(_glass(workbench, first_id))
    second_before = deepcopy(_glass(workbench, second_id))
    window.validate_workbench()
    assert workbench.state == WorkbenchState.VALIDATED

    options = GlassSettingsCopyOptions(True, True, True, True, False, False)
    request = _request(source_id, (first_id, second_id), options)
    coordinator = ObservationSettingsCopyCoordinator(window)
    coordinator._create_dialog = lambda *_args: FakeDialog(request)
    coordinator.open_dialog()

    assert window.undo_stack.count() == 1
    assert workbench.selected_glass_id == source_id
    assert window.canvas._selected_id == source_id
    assert _glass(workbench, first_id).judgment_rule == _glass(workbench, source_id).judgment_rule
    assert _glass(workbench, second_id).detector_settings == _glass(workbench, source_id).detector_settings
    assert _glass(workbench, first_id).geometry.ellipse == first_before.geometry.ellipse
    assert _glass(workbench, second_id).geometry.zero_line_y == second_before.geometry.zero_line_y
    assert workbench.state == WorkbenchState.DRAFT_DIRTY
    assert not window.action_bar.analyze_button.isEnabled()
    assert window._last_validation is not None
    assert preview.invalidations > 0

    window.undo_stack.undo()
    assert _glass(workbench, first_id).judgment_rule == first_before.judgment_rule
    assert _glass(workbench, second_id).detector_settings == second_before.detector_settings
    assert workbench.selected_glass_id == source_id

    window.undo_stack.redo()
    assert _glass(workbench, first_id).judgment_rule == _glass(workbench, source_id).judgment_rule
    assert _glass(workbench, second_id).detector_settings == _glass(workbench, source_id).detector_settings
    assert workbench.selected_glass_id == source_id


def test_detection_related_copy_marks_existing_preflight_result_stale(qtbot):
    window, workbench, _preview, source_id, first_id, _second_id = _window(qtbot)
    source = _glass(workbench, source_id)
    source.detector_settings.canny_low = 97
    preflight = PreflightCoordinator(window, DummyPreflightController())
    preflight.last_result = SimpleNamespace(context_key=preflight_context_key(workbench.recipe, workbench.session))
    preflight.panel.status_label.setText("정상")

    options = GlassSettingsCopyOptions(False, True, False, False, False, False)
    request = _request(source_id, (first_id,), options)
    coordinator = ObservationSettingsCopyCoordinator(window)
    coordinator._create_dialog = lambda *_args: FakeDialog(request)
    coordinator.open_dialog()

    qtbot.waitUntil(lambda: preflight.panel.status_label.text() == "재점검 필요")
    assert workbench.selected_glass_id == source_id
    preflight.last_result = None
    preflight.deleteLater()
    qtbot.wait(20)


def test_no_op_shows_message_without_undo_dirty_preview_or_preflight_change(qtbot, monkeypatch):
    window, workbench, preview, source_id, first_id, _second_id = _window(qtbot)
    source = _glass(workbench, source_id)
    target = _glass(workbench, first_id)
    target.detector_settings = deepcopy(source.detector_settings)
    before_state = workbench.state
    before_context = preflight_context_key(workbench.recipe, workbench.session)
    messages = []
    monkeypatch.setattr(QMessageBox, "information", lambda *_args: messages.append(_args[-1]))

    options = GlassSettingsCopyOptions(False, True, False, False, False, False)
    request = _request(source_id, (first_id,), options)
    coordinator = ObservationSettingsCopyCoordinator(window)
    coordinator._create_dialog = lambda *_args: FakeDialog(request)
    coordinator.open_dialog()

    assert messages == ["복사할 변경 사항이 없습니다."]
    assert window.undo_stack.count() == 0
    assert workbench.state == before_state
    assert preview.invalidations == 0
    assert preflight_context_key(workbench.recipe, workbench.session) == before_context


def test_geometry_error_is_reported_and_multi_target_copy_is_atomic(qtbot, monkeypatch):
    window, workbench, _preview, source_id, first_id, second_id = _window(qtbot)
    source = _glass(workbench, source_id)
    source.geometry.ellipse = EllipseGeometry(320.0, 240.0, 80.0, 90.0)
    invalid = _glass(workbench, second_id)
    invalid.geometry.ellipse = EllipseGeometry(610.0, 240.0, 20.0, 60.0)
    before = workbench.recipe.to_dict()
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: warnings.append(_args[-1]))

    options = GlassSettingsCopyOptions(False, False, False, False, False, True)
    request = _request(source_id, (first_id, second_id), options)
    coordinator = ObservationSettingsCopyCoordinator(window)
    coordinator._create_dialog = lambda *_args: FakeDialog(request)
    coordinator.open_dialog()

    assert len(warnings) == 1
    assert _glass(workbench, second_id).name in warnings[0]
    assert workbench.recipe.to_dict() == before
    assert window.undo_stack.count() == 0
