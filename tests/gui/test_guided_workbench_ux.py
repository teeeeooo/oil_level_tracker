from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.artifact_calibration import template_from_candidate
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind, ValidationSeverity
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


def test_roi_editor_accepts_detector_artifact_proposal_on_private_copy(
    qtbot,
    monkeypatch,
):
    candidate = BoundaryCandidate(
        source="test-proposal",
        kind=BoundaryKind.OIL_AIR,
        y=200.0,
        features={
            "artifact_center_x_norm": 0.5,
            "artifact_center_y_norm": 0.4,
            "artifact_width_norm": 0.6,
            "artifact_height_norm": 0.02,
            "artifact_angle_deg": 0.0,
        },
        final_score=0.8,
    )

    monkeypatch.setattr(
        "oil_tracker.ui.widgets.roi_editor_dialog.propose_artifact_templates",
        lambda _frame, _glass: [
            template_from_candidate(candidate, name="경계 후보 1")
        ],
    )
    glass = InspectionRecipe.default_glass(640, 480)
    dialog = RoiEditorDialog(
        np.zeros((480, 640, 3), dtype=np.uint8),
        glass,
        640,
        480,
    )
    qtbot.addWidget(dialog)

    dialog._scan_artifacts()
    dialog.artifact_proposal_list.setCurrentRow(0)
    dialog._accept_artifact()

    assert glass.geometry.artifact_templates == []
    templates = dialog.edited_glass().geometry.artifact_templates
    assert len(templates) == 1
    assert templates[0].kind == "line"
    assert templates[0].center_y == 0.4


def test_roi_editor_bulk_selects_and_highlights_artifact_proposals(
    qtbot,
    monkeypatch,
):
    candidates = [
        BoundaryCandidate(
            source=f"proposal-{index}",
            kind=BoundaryKind.OIL_AIR,
            y=180.0 + index * 40.0,
            features={
                "artifact_center_x_norm": 0.5,
                "artifact_center_y_norm": 0.3 + index * 0.2,
                "artifact_width_norm": 0.6,
                "artifact_height_norm": 0.02,
                "artifact_angle_deg": 0.0,
            },
            final_score=0.8,
        )
        for index in range(2)
    ]
    proposals = [
        template_from_candidate(candidate, name=f"경계 후보 {index + 1}")
        for index, candidate in enumerate(candidates)
    ]
    monkeypatch.setattr(
        "oil_tracker.ui.widgets.roi_editor_dialog.propose_artifact_templates",
        lambda _frame, _glass: proposals,
    )
    glass = InspectionRecipe.default_glass(640, 480)
    dialog = RoiEditorDialog(
        np.zeros((480, 640, 3), dtype=np.uint8),
        glass,
        640,
        480,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.wait(10)

    dialog._scan_artifacts()
    dialog.select_all_artifacts_button.click()
    assert len(dialog.artifact_proposal_list.selectedItems()) == 2
    assert dialog.canvas._highlighted_artifact_proposal_ids == {
        proposal.id for proposal in proposals
    }
    assert all(item.pen().width() == 4 for item in dialog.canvas._artifact_items)

    dialog.accept_artifact_button.click()
    assert len(dialog.edited_glass().geometry.artifact_templates) == 2
    assert dialog.content_splitter.orientation() == Qt.Orientation.Horizontal
    canvas_right = dialog.canvas.mapTo(
        dialog,
        dialog.canvas.rect().bottomRight(),
    ).x()
    artifact_left = dialog.artifact_group.mapTo(
        dialog,
        dialog.artifact_group.rect().topLeft(),
    ).x()
    assert canvas_right < artifact_left


def test_roi_editor_primary_artifact_actions_are_visible_without_scrolling(qtbot):
    glass = InspectionRecipe.default_glass(1920, 1080)
    dialog = RoiEditorDialog(
        np.zeros((1080, 1920, 3), dtype=np.uint8),
        glass,
        1920,
        1080,
    )
    qtbot.addWidget(dialog)
    dialog.resize(980, 700)
    dialog.show()
    qtbot.wait(10)

    for widget in (
        dialog.scan_artifacts_button,
        dialog.select_all_artifacts_button,
        dialog.accept_artifact_button,
    ):
        assert widget.isVisible()
        top_left = widget.mapTo(dialog, widget.rect().topLeft())
        bottom_right = widget.mapTo(dialog, widget.rect().bottomRight())
        assert dialog.rect().contains(top_left)
        assert dialog.rect().contains(bottom_right)

    assert dialog.isSizeGripEnabled()
    assert dialog.windowFlags() & Qt.WindowType.WindowMaximizeButtonHint
    assert dialog.content_splitter.orientation() == Qt.Orientation.Horizontal


def test_roi_editor_bulk_selects_highlights_and_deletes_confirmed_artifacts(
    qtbot,
    monkeypatch,
):
    glass = InspectionRecipe.default_glass(640, 480)
    candidates = [
        BoundaryCandidate(
            source=f"confirmed-{index}",
            kind=BoundaryKind.OIL_AIR,
            y=160.0 + 40.0 * index,
            features={
                "artifact_center_x_norm": 0.5,
                "artifact_center_y_norm": 0.25 + 0.2 * index,
                "artifact_width_norm": 0.6,
                "artifact_height_norm": 0.02,
                "artifact_angle_deg": 0.0,
            },
            final_score=0.8,
        )
        for index in range(3)
    ]
    glass.geometry.artifact_templates = [
        template_from_candidate(candidate, name=f"지정 후보 {index + 1}")
        for index, candidate in enumerate(candidates)
    ]
    original_ids = [template.id for template in glass.geometry.artifact_templates]
    dialog = RoiEditorDialog(
        np.zeros((480, 640, 3), dtype=np.uint8),
        glass,
        640,
        480,
    )
    qtbot.addWidget(dialog)

    first = dialog.artifact_template_list.item(0)
    third = dialog.artifact_template_list.item(2)
    first.setSelected(True)
    third.setSelected(True)
    assert dialog.canvas._highlighted_artifact_template_ids == {
        original_ids[0],
        original_ids[2],
    }
    assert "2개" in dialog.delete_artifact_button.text()

    dialog.delete_artifact_button.click()
    assert [
        template.id for template in dialog.edited_glass().geometry.artifact_templates
    ] == [original_ids[1]]
    assert [template.id for template in glass.geometry.artifact_templates] == original_ids

    dialog.select_all_templates_button.click()
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.Yes,
    )
    dialog.delete_artifact_button.click()
    assert dialog.edited_glass().geometry.artifact_templates == []
    assert all(size > 0 for size in dialog.content_splitter.sizes())


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
