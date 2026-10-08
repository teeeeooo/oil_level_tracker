from dataclasses import replace
from types import SimpleNamespace

from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox
import pytest

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.artifact_reference import OpenCvArtifactReferenceReviewer
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.ui.widgets.artifact_support_dialog import ArtifactSupportDialog
from oil_tracker.ui.widgets.roi_editor_dialog import RoiEditorDialog
from tests.fixtures.artifact_reference import reference_fixture
from tests.gui.test_main_window_collaborator_ownership import _window


def test_real_drag_preview_modes_resize_and_explicit_confirmation(qtbot):
    _, glass, template, _, _ = reference_fixture()
    dialog = ArtifactSupportDialog(template, glass, 160, 120, reference_reviewer=OpenCvArtifactReferenceReviewer())
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    canvas = dialog.canvas
    start, end = canvas.mapFromScene(QPointF(15, 24)), canvas.mapFromScene(QPointF(70, 28))
    qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=start)
    qtbot.mouseMove(canvas.viewport(), pos=end)
    qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=end)
    rect = canvas.review_rect
    assert rect is not None
    assert not dialog.confirm_edges.isChecked()
    assert canvas._review_item.scene() is canvas.scene()
    dialog.mode.setCurrentIndex(1)
    dialog.resize(720, 530)
    dialog.mode.setCurrentIndex(0)
    assert canvas.review_rect == rect
    assert canvas._review_item.scene() is canvas.scene()
    assert dialog.confirm_edges.isEnabled()
    dialog.confirm_edges.setChecked(True)
    qtbot.mouseClick(dialog.buttons.button(QDialogButtonBox.StandardButton.Ok), Qt.MouseButton.LeftButton)
    assert dialog.result() == QDialog.DialogCode.Accepted
    saved = dialog.reviewed_reference()
    assert saved.review_state == "reviewed_support" and saved.review_rect == rect
    reopened = ArtifactSupportDialog(replace(template, support_reference=saved), glass, 160, 120,
                                     reference_reviewer=OpenCvArtifactReferenceReviewer())
    qtbot.addWidget(reopened)
    assert reopened.confirm_edges.isChecked()
    reopened.canvas.set_review_rect((20, 20, 5, 5))
    assert not reopened.confirm_edges.isChecked()
    reopened.reject()
    assert reopened.reviewed_reference() == saved


def test_roi_editor_nested_cancel_apply_save_and_reopen(qtbot, monkeypatch, tmp_path):
    frame, glass, template, _, _ = reference_fixture()
    proposer = SimpleNamespace(propose=lambda _frame, _glass: [template])
    editor = RoiEditorDialog(frame, glass, 160, 120, artifact_proposer=proposer,
                             source_frame_index=42, source_time_sec=1.4,
                             reference_reviewer=OpenCvArtifactReferenceReviewer())
    qtbot.addWidget(editor)
    editor.scan_artifacts_button.click()
    editor.artifact_proposal_list.setCurrentRow(0)
    outcome = [False]
    def review(dialog):
        qtbot.addWidget(dialog)
        dialog.canvas.set_review_rect((15, 24, 55, 4))
        # No checkbox: even a rectangle containing edges remains uncertain.
        dialog.accept() if outcome[0] else dialog.reject()
        return dialog.result()
    monkeypatch.setattr(ArtifactSupportDialog, "exec", review)
    editor.review_proposal_button.click()
    assert editor._artifact_proposals[0].support_reference.review_rect is None
    outcome[0] = True
    editor.review_proposal_button.click()
    editor.accept_artifact_button.click()
    assert glass.geometry.artifact_templates == []
    edited = editor.edited_glass()
    saved = edited.geometry.artifact_templates[0].support_reference
    assert saved.review_state == "mixed_or_uncertain"
    assert saved.snapshot()["frame_index"] == 42 and saved.snapshot()["time_sec"] == 1.4
    assert edited.geometry.artifact_templates[0].to_dict(include_reference=False) == template.to_dict(include_reference=False)
    editor.accept()
    recipe = InspectionRecipe.empty(160, 120)
    recipe.glasses = [edited]
    path = tmp_path / "review.oilrecipe"
    JsonRecipeRepository().save(path, recipe)
    loaded = JsonRecipeRepository().load(path).glasses[0]
    reopened = RoiEditorDialog(None, loaded, 160, 120, reference_reviewer=OpenCvArtifactReferenceReviewer())
    qtbot.addWidget(reopened)
    reopened.artifact_template_list.setCurrentRow(0)
    outcome[0] = False
    reopened.review_template_button.click()
    assert reopened.edited_glass() == loaded


@pytest.mark.parametrize("case", ["legacy", "corrupt", "resized", "roi_changed"])
def test_unavailable_reference_never_replaced_by_current_frame(qtbot, case):
    _, glass, template, _, _ = reference_fixture()
    w, h = 160, 120
    if case == "legacy":
        template = replace(template, support_reference=None)
    elif case == "corrupt":
        template = replace(template, support_reference=replace(template.support_reference, snapshot_sha256="bad"))
    elif case == "resized":
        w, h = 320, 240
    else:
        glass.geometry.ellipse = replace(glass.geometry.ellipse, center_x=81)
    dialog = ArtifactSupportDialog(template, glass, w, h, reference_reviewer=OpenCvArtifactReferenceReviewer())
    qtbot.addWidget(dialog)
    assert not dialog.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled()
    assert dialog.canvas.read_only
    assert dialog.reviewed_reference() == template.support_reference


@pytest.mark.parametrize("apply", [False, True])
def test_main_window_entry_preserves_real_source_position_and_commit_boundary(qtbot, monkeypatch, apply):
    window, _ = _window(qtbot)
    frame, glass, template, _, _ = reference_fixture()
    recipe = InspectionRecipe.empty(160, 120)
    recipe.glasses = [glass]
    window.workbench.recipe = recipe
    window.workbench.selected_glass_id = glass.id
    window.current_frame = frame
    window.current_frame_index = 17383
    window.current_time = 579.433
    window.artifact_proposer = SimpleNamespace(propose=lambda _frame, _glass: [template])
    window.reference_reviewer = OpenCvArtifactReferenceReviewer()
    def edit(dialog):
        qtbot.addWidget(dialog)
        assert dialog._reference_reviewer is window.reference_reviewer
        dialog.scan_artifacts_button.click()
        dialog.artifact_proposal_list.setCurrentRow(0)
        dialog.accept_artifact_button.click()
        dialog.accept() if apply else dialog.reject()
        return dialog.result()
    monkeypatch.setattr(RoiEditorDialog, "exec", edit)
    window.open_roi_editor()
    templates = window.workbench.selected_glass().geometry.artifact_templates
    assert len(templates) == int(apply)
    if apply:
        snap = templates[0].support_reference.snapshot()
        assert snap["frame_index"] == 17383 and snap["time_sec"] == 579.433
        assert templates[0].support_reference.review_state == "proposal_negative"
    assert glass.geometry.artifact_templates == []


def test_application_bootstrap_supplies_reference_review_service(qtbot, monkeypatch, tmp_path):
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "mpl"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    import oil_tracker.bootstrap as bootstrap
    # Logging's user-data directory is unrelated to the composition under test.
    monkeypatch.setattr(bootstrap, "configure_logging", lambda: None)
    window = bootstrap.build_main_window()
    qtbot.addWidget(window)
    _, _, template, _, _ = reference_fixture()
    snapshot, images = window.reference_reviewer.load(template.support_reference)
    rendered, count = window.reference_reviewer.render(images, (15, 24, 55, 4), "review")
    assert count > 0
    assert rendered.shape[:2] == (snapshot["crop_size"][1], snapshot["crop_size"][0])
    assert window.artifact_proposer is not None
