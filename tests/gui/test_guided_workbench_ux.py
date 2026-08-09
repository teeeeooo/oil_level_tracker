from __future__ import annotations

import numpy as np

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.enums import ValidationSeverity
from oil_tracker.domain.geometry import EllipseGeometry
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.validation import ValidationIssue, ValidationResult
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.undo import RecipeSnapshotCommand
from oil_tracker.ui.widgets.bottom_action_bar import BottomActionBar
from oil_tracker.ui.widgets.glass_settings_panel import GlassSettingsPanel
from oil_tracker.ui.widgets.roi_editor_dialog import RoiEditorDialog


def controller() -> WorkbenchController:
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )


def test_advanced_settings_are_hidden_until_requested(qtbot):
    panel = GlassSettingsPanel()
    qtbot.addWidget(panel)
    assert panel.advanced_container.isHidden()
    panel.set_advanced_visible(True)
    assert not panel.advanced_container.isHidden()
    assert panel.advanced_toggle.text() == "고급 설정 숨기기"


def test_inline_validation_marks_related_field(qtbot):
    panel = GlassSettingsPanel()
    qtbot.addWidget(panel)
    glass = InspectionRecipe.default_glass(640, 480)
    panel.set_glass(glass)
    issue = ValidationIssue(
        ValidationSeverity.ERROR,
        "READY_ZERO",
        "Zero line is required.",
        glass.id,
        "zero_line_y",
    )
    panel.set_validation_issues([issue], glass.id)
    assert panel.zero.property("validationState") == "error"
    assert "기준점" in panel._validation_messages["zero_line_y"].text()


def test_bottom_action_bar_enables_analysis_only_when_ready(qtbot):
    bar = BottomActionBar()
    qtbot.addWidget(bar)
    bar.set_validation_result(
        ValidationResult([ValidationIssue(ValidationSeverity.ERROR, "READY_VIDEO", "missing")])
    )
    assert not bar.analyze_button.isEnabled()
    bar.set_validation_result(ValidationResult([]))
    assert bar.analyze_button.isEnabled()
    assert "준비 완료" in bar.status.text()


def test_roi_editor_uses_private_copy_until_applied(qtbot):
    glass = InspectionRecipe.default_glass(640, 480)
    original = glass.geometry.ellipse
    dialog = RoiEditorDialog(np.zeros((480, 640, 3), dtype=np.uint8), glass, 640, 480)
    qtbot.addWidget(dialog)
    edited = EllipseGeometry(
        original.center_x + 25,
        original.center_y,
        original.radius_x,
        original.radius_y,
    )
    dialog._ellipse_changed(glass.id, edited)
    assert glass.geometry.ellipse.center_x == original.center_x
    assert dialog.edited_glass().geometry.ellipse.center_x == original.center_x + 25


def test_recipe_snapshot_command_restores_before_and_after(qtbot):
    from PySide6.QtGui import QUndoStack

    workbench = controller()
    glass = workbench.add_glass()
    before = workbench.recipe.to_dict()
    selected = workbench.selected_glass_id
    glass.name = "변경된 이름"
    after = workbench.recipe.to_dict()
    restored = []
    stack = QUndoStack()
    command = RecipeSnapshotCommand(
        workbench,
        before,
        after,
        selected,
        selected,
        "이름 변경",
        lambda: restored.append(True),
        already_applied=True,
    )
    stack.push(command)
    stack.undo()
    assert workbench.selected_glass().name != "변경된 이름"
    stack.redo()
    assert workbench.selected_glass().name == "변경된 이름"
    assert len(restored) == 2
