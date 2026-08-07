from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QMessageBox, QWidget

from oil_tracker.application.services.redetection_apply import (
    DetectorSettingsApplyScope,
    check_workbench_compatibility,
)
from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.domain.recipe import DetectorSettings, InspectionRecipe
from oil_tracker.ui.redetection_comparison_coordinator import (
    RedetectionComparisonCoordinator,
)
from oil_tracker.ui.redetection_comparison_window import RedetectionComparisonWindow
from oil_tracker.ui.undo import RecipeSnapshotCommand
from redetection_fixtures import make_bundle


def _recipe_with_glasses(snapshot: InspectionRecipe, *glass_ids: str) -> InspectionRecipe:
    recipe = InspectionRecipe.from_dict(snapshot.to_dict())
    recipe.glasses = []
    for index, glass_id in enumerate(glass_ids, start=1):
        glass = InspectionRecipe.default_glass(
            recipe.reference_frame_width,
            recipe.reference_frame_height,
            index,
        )
        glass.id = glass_id
        glass.name = f"Glass {index}"
        recipe.glasses.append(glass)
    return recipe


def _compatibility(
    workbench_recipe: InspectionRecipe,
    snapshot: InspectionRecipe,
    scope: DetectorSettingsApplyScope,
    *,
    state: WorkbenchState = WorkbenchState.DRAFT,
):
    return check_workbench_compatibility(
        workbench_recipe,
        state,
        snapshot,
        "glass-1",
        scope,
    )


def test_compatibility_same_glass_allows_selected_and_all(tmp_path):
    snapshot = make_bundle(tmp_path).recipe
    workbench = _recipe_with_glasses(snapshot, "glass-1", "glass-2")

    assert _compatibility(
        workbench,
        snapshot,
        DetectorSettingsApplyScope.SELECTED,
    ).compatible
    assert _compatibility(
        workbench,
        snapshot,
        DetectorSettingsApplyScope.ALL,
    ).compatible


def test_compatibility_missing_selected_glass_only_blocks_selected(tmp_path):
    snapshot = make_bundle(tmp_path).recipe
    workbench = _recipe_with_glasses(snapshot, "glass-2")

    selected = _compatibility(
        workbench,
        snapshot,
        DetectorSettingsApplyScope.SELECTED,
    )
    all_glasses = _compatibility(
        workbench,
        snapshot,
        DetectorSettingsApplyScope.ALL,
    )

    assert not selected.compatible
    assert any("동일한 관찰창 ID" in reason for reason in selected.reasons)
    assert all_glasses.compatible


def test_compatibility_empty_workbench_blocks_both_scopes(tmp_path):
    snapshot = make_bundle(tmp_path).recipe
    workbench = _recipe_with_glasses(snapshot)

    assert not _compatibility(
        workbench,
        snapshot,
        DetectorSettingsApplyScope.SELECTED,
    ).compatible
    assert not _compatibility(
        workbench,
        snapshot,
        DetectorSettingsApplyScope.ALL,
    ).compatible


def test_compatibility_recipe_mismatch_blocks_both_scopes(tmp_path):
    snapshot = make_bundle(tmp_path).recipe
    workbench = _recipe_with_glasses(snapshot, "glass-1", "glass-2")
    workbench.recipe_id = "different-recipe"

    for scope in DetectorSettingsApplyScope:
        result = _compatibility(workbench, snapshot, scope)
        assert not result.compatible
        assert any("recipe ID" in reason for reason in result.reasons)


def test_compatibility_reference_frame_mismatch_blocks_both_scopes(tmp_path):
    snapshot = make_bundle(tmp_path).recipe
    workbench = _recipe_with_glasses(snapshot, "glass-1", "glass-2")
    workbench.reference_frame_width += 1

    for scope in DetectorSettingsApplyScope:
        result = _compatibility(workbench, snapshot, scope)
        assert not result.compatible
        assert any("기준 해상도" in reason for reason in result.reasons)


def test_compatibility_analyzing_blocks_both_scopes(tmp_path):
    snapshot = make_bundle(tmp_path).recipe
    workbench = _recipe_with_glasses(snapshot, "glass-1", "glass-2")

    for scope in DetectorSettingsApplyScope:
        result = _compatibility(
            workbench,
            snapshot,
            scope,
            state=WorkbenchState.ANALYZING,
        )
        assert not result.compatible
        assert any("분석이 진행 중" in reason for reason in result.reasons)


def test_window_enables_apply_buttons_independently(qtbot):
    window = RedetectionComparisonWindow(DetectorSettings())
    qtbot.addWidget(window)

    window.set_apply_compatibility(
        False,
        ("현재 Workbench에 동일한 관찰창 ID가 없습니다.",),
        True,
        (),
    )

    assert not window.apply_current.isEnabled()
    assert window.apply_all.isEnabled()
    assert window.save_selected.isEnabled()
    assert window.save_all.isEnabled()
    assert "현재 관찰창 적용:" in window.compatibility_label.text()
    assert "모든 관찰창 적용:\n• 적용 가능" in window.compatibility_label.text()


def test_window_enables_both_apply_buttons_when_both_scopes_are_compatible(qtbot):
    window = RedetectionComparisonWindow(DetectorSettings())
    qtbot.addWidget(window)

    window.set_apply_compatibility(True, (), True, ())

    assert window.apply_current.isEnabled()
    assert window.apply_all.isEnabled()


def test_window_disables_both_apply_buttons_and_displays_each_reason(qtbot):
    window = RedetectionComparisonWindow(DetectorSettings())
    qtbot.addWidget(window)

    window.set_apply_compatibility(
        False,
        ("선택 범위 사유",),
        False,
        ("전체 범위 사유",),
    )

    assert not window.apply_current.isEnabled()
    assert not window.apply_all.isEnabled()
    assert "현재 관찰창 적용:\n• 선택 범위 사유" in window.compatibility_label.text()
    assert "모든 관찰창 적용:\n• 전체 범위 사유" in window.compatibility_label.text()


def test_window_invalid_settings_disable_apply_and_save_even_when_compatible(qtbot):
    window = RedetectionComparisonWindow(DetectorSettings())
    qtbot.addWidget(window)
    window.set_apply_compatibility(True, (), True, ())

    window._settings_changed(None, False, 0)

    assert not window.apply_current.isEnabled()
    assert not window.apply_all.isEnabled()
    assert not window.save_selected.isEnabled()
    assert not window.save_all.isEnabled()


class _Viewer(QWidget):
    redetectionRequested = Signal()
    bundleAboutToChange = Signal()
    bundleChanged = Signal(object)
    sourceVideoChanged = Signal(object)
    selectedGlassChanged = Signal(str)
    viewerClosing = Signal()

    def __init__(self, bundle) -> None:
        super().__init__()
        self.bundle = bundle
        self.selected_glass_id = "glass-1"
        self.current_time = 3.0
        self.active_video_path = bundle.source_video_path
        self.debug_repository = None
        self.jumps = []

    def _jump_to(self, timestamp: float) -> None:
        self.jumps.append(timestamp)


class _Controller(QObject):
    started = Signal(int, str)
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(int, str)
    cancelled = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.generation = 0
        self.service = SimpleNamespace(policy=SimpleNamespace())
        self.current_workspace = None
        self.invalidated = []
        self.closed = False

    def cancel(self) -> None:
        pass

    def invalidate(self, generation: int) -> None:
        self.invalidated.append(generation)

    def close(self) -> None:
        self.closed = True


class _Workbench:
    def __init__(self, recipe: InspectionRecipe) -> None:
        self.recipe = recipe
        self.state = WorkbenchState.VALIDATED
        self.selected_glass_id = "glass-2"

    def mark_dirty(self) -> None:
        self.state = (
            WorkbenchState.DRAFT_DIRTY
            if self.state in {WorkbenchState.VALIDATED, WorkbenchState.ANALYZED}
            else WorkbenchState.DRAFT
        )

    def invalidate_initial_state_confirmations_for_recipe_transition(
        self,
        _before: dict,
        _after: dict,
    ) -> None:
        pass


class _Preflight:
    def __init__(self) -> None:
        self.reset_count = 0

    def reset(self) -> None:
        self.reset_count += 1


class _MainWindow:
    def __init__(self, workbench: _Workbench) -> None:
        self.workbench = workbench
        self.undo_stack = QUndoStack()
        self.preflight_coordinator = _Preflight()
        self._last_validation = object()
        self.preview_invalidations = []
        self.refresh_count = 0
        self.validation_refresh_count = 0
        self.restore_refresh_count = 0

    def _record_recipe_change(self, text: str, change) -> None:
        before = self.workbench.recipe.to_dict()
        selected_before = self.workbench.selected_glass_id
        change()
        after = self.workbench.recipe.to_dict()
        selected_after = self.workbench.selected_glass_id
        if before == after and selected_before == selected_after:
            return
        self.undo_stack.push(
            RecipeSnapshotCommand(
                self.workbench,
                before,
                after,
                selected_before,
                selected_after,
                text,
                self._after_snapshot_restored,
                already_applied=True,
            )
        )
        self._after_user_change()

    def _after_snapshot_restored(self) -> None:
        self.restore_refresh_count += 1
        self._refresh_all()
        self._refresh_inline_validation()

    def _after_user_change(self) -> None:
        self._refresh_all()
        self._refresh_inline_validation()

    def _invalidate_preview(self, message: str) -> None:
        self.preview_invalidations.append(message)

    def _refresh_all(self) -> None:
        self.refresh_count += 1

    def _refresh_inline_validation(self) -> None:
        self.validation_refresh_count += 1


def test_coordinator_missing_selected_glass_keeps_all_apply_available_and_atomic(
    qtbot,
    tmp_path,
    monkeypatch,
):
    bundle = make_bundle(tmp_path)
    official_recipe_before = deepcopy(bundle.recipe.to_dict())
    official_samples_before = bundle.samples
    workbench_recipe = _recipe_with_glasses(bundle.recipe, "glass-2")
    main_window = _MainWindow(_Workbench(workbench_recipe))
    viewer = _Viewer(bundle)
    controller = _Controller()
    qtbot.addWidget(viewer)
    coordinator = RedetectionComparisonCoordinator(
        main_window,
        viewer,
        controller,
    )

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: QMessageBox.StandardButton.Ok,
    )
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs: QMessageBox.StandardButton.Ok,
    )

    coordinator.open()
    window = coordinator.window
    assert window is not None
    assert not window.apply_current.isEnabled()
    assert window.apply_all.isEnabled()
    assert window.save_selected.isEnabled()
    assert window.save_all.isEnabled()

    window.settings_editor._editors["canny_low"].setValue(12)
    assert window.apply_all.isEnabled()
    window.apply_all.click()

    assert main_window.workbench.recipe.glasses[0].id == "glass-2"
    assert main_window.workbench.recipe.glasses[0].detector_settings.canny_low == 12
    assert main_window.workbench.selected_glass_id == "glass-2"
    assert main_window.workbench.state is WorkbenchState.DRAFT_DIRTY
    assert main_window.undo_stack.count() == 1
    assert main_window.preflight_coordinator.reset_count == 1
    assert main_window._last_validation is None
    assert main_window.preview_invalidations == [
        "검출 설정 변경 · 현재 장면 재분석 필요"
    ]
    assert main_window.refresh_count >= 2
    assert main_window.validation_refresh_count >= 2
    assert "Workbench 적용 완료 · 1개 관찰창" in window.apply_status.text()
    assert not window.apply_current.isEnabled()
    assert window.apply_all.isEnabled()

    main_window.undo_stack.undo()
    assert main_window.workbench.recipe.glasses[0].detector_settings.canny_low == 45
    assert main_window.workbench.selected_glass_id == "glass-2"
    main_window.undo_stack.redo()
    assert main_window.workbench.recipe.glasses[0].detector_settings.canny_low == 12
    assert main_window.workbench.selected_glass_id == "glass-2"
    assert main_window.restore_refresh_count == 2

    assert bundle.recipe.to_dict() == official_recipe_before
    assert bundle.samples == official_samples_before
    coordinator.close()
