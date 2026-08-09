from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QApplication

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.enums import ValidationSeverity
from oil_tracker.domain.validation import ValidationIssue, ValidationResult
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow


class DummyPreviewController(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def invalidate(self):
        pass

    def request(self, *_args):
        pass


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


@pytest.fixture
def workbench_window(qtbot):
    workbench = _controller()
    window = MainWindow(workbench, DummyPreviewController(), DummyAnalysisController(), DummyRenderer())
    qtbot.addWidget(window)
    window.resize(1280, 760)
    window.show()
    QApplication.processEvents()
    yield window, workbench


def _add_glass(window, workbench):
    glass = workbench.add_glass()
    window._refresh_panels()
    QApplication.processEvents()
    return glass


def test_field_context_highlights_geometry_zero_and_margin(workbench_window):
    window, workbench = workbench_window
    glass = _add_glass(window, workbench)

    window.settings.cx.setFocus()
    QApplication.processEvents()
    assert window._interaction_target == "geometry"
    assert window.canvas._active_target == "geometry"
    assert window.canvas._editable_ellipse_item._interaction_active is True

    window.settings.zero.setFocus()
    QApplication.processEvents()
    assert window._interaction_target == "zero_line"
    assert window.canvas._zero_line_item._interaction_active is True
    assert window.canvas._editable_ellipse_item.isSelected() is True

    window.settings.focus_field("margin")
    QApplication.processEvents()
    assert window.settings.advanced_container.isVisible() is True
    assert window._interaction_target == "margin"
    assert window.canvas._margin_item.pen().width() == 4
    assert window._interaction_glass_id == glass.id


def test_exclusion_selection_tracks_exact_zone_and_refresh_clears_stale(workbench_window):
    window, workbench = workbench_window
    glass = _add_glass(window, workbench)
    first = workbench.add_exclusion(glass.id)
    second = workbench.add_exclusion(glass.id)
    window._refresh_panels()

    window.settings.exclusions.setCurrentRow(1)
    QApplication.processEvents()
    assert window._interaction_target == "exclusion"
    assert window._interaction_zone_id == second.id
    assert window.canvas._active_zone_id == second.id
    assert window.canvas._exclusion_items[second.id]._interaction_active is True
    assert window.canvas._exclusion_items[first.id]._interaction_active is False

    window._refresh_panels()
    assert window._interaction_zone_id == second.id
    assert window.settings.exclusions.currentItem().data(Qt.ItemDataRole.UserRole) == second.id

    workbench.delete_exclusion(glass.id, second.id)
    window._refresh_panels()
    assert window._interaction_target is None
    assert window._interaction_zone_id is None
    assert window.canvas._active_target is None


def test_overlay_requests_reveal_matching_panel_target(workbench_window):
    window, workbench = workbench_window
    glass = _add_glass(window, workbench)
    zone = workbench.add_exclusion(glass.id)
    window._refresh_panels()

    window.canvas.interactionTargetRequested.emit(glass.id, "geometry", None)
    QApplication.processEvents()
    assert window._interaction_target == "geometry"
    assert window.settings.advanced_container.isVisible() is True
    assert window.settings.geometry_group.property("interactionTarget") is True

    window.canvas.interactionTargetRequested.emit(glass.id, "zero_line", None)
    QApplication.processEvents()
    assert window._interaction_target == "zero_line"
    assert window.settings.zero.property("interactionTarget") is True

    window.canvas.interactionTargetRequested.emit(glass.id, "exclusion", zone.id)
    QApplication.processEvents()
    current = window.settings.exclusions.currentItem()
    assert window._interaction_zone_id == zone.id
    assert current.data(Qt.ItemDataRole.UserRole) == zone.id
    assert window.settings.exclusion_group.property("interactionTarget") is True


def test_highlight_only_state_does_not_mutate_recipe_session_dirty_or_undo(workbench_window):
    window, workbench = workbench_window
    glass = _add_glass(window, workbench)
    zone = workbench.add_exclusion(glass.id)
    window._refresh_panels()
    recipe_before = workbench.recipe.to_dict()
    session_before = workbench.session.to_dict()
    state_before = workbench.state
    dirty_before = workbench.profile_has_unsaved_changes
    undo_before = window.undo_stack.count()

    window._set_interaction_target(glass.id, "geometry")
    window._set_interaction_target(glass.id, "zero_line")
    window._set_interaction_target(glass.id, "margin")
    window._set_interaction_target(glass.id, "exclusion", zone.id)

    assert workbench.recipe.to_dict() == recipe_before
    assert workbench.session.to_dict() == session_before
    assert workbench.state == state_before
    assert workbench.profile_has_unsaved_changes == dirty_before
    assert window.undo_stack.count() == undo_before


def test_validation_state_and_active_target_coexist(workbench_window):
    window, workbench = workbench_window
    glass = _add_glass(window, workbench)
    issue = ValidationIssue(
        ValidationSeverity.ERROR,
        "READY_ZERO",
        "zero line error",
        glass.id,
        "zero_line_y",
    )
    window.settings.set_validation_issues([issue], glass.id)
    window._set_interaction_target(glass.id, "zero_line")

    assert window.settings.zero.property("validationState") == "error"
    assert window.settings.zero.property("interactionTarget") is True
    window.settings.focus_field("zero_line_y")
    assert window.settings._last_focused_field == "zero_line_y"
    assert window.canvas._active_target == "zero_line"


def test_first_issue_navigation_still_selects_glass_and_routes_active_target(workbench_window):
    window, workbench = workbench_window
    first = _add_glass(window, workbench)
    second = workbench.add_glass()
    workbench.set_selected(first.id)
    issue = ValidationIssue(
        ValidationSeverity.ERROR,
        "STRUCT_ELLIPSE",
        "geometry",
        second.id,
        "geometry",
    )
    window._apply_validation_result(ValidationResult([issue]))

    window._navigate_next_issue()

    assert workbench.selected_glass_id == second.id
    assert window.canvas._selected_id == second.id
    assert window.settings._last_focused_field == "geometry"
    assert window._interaction_target == "geometry"
    assert window.canvas._active_target == "geometry"


def test_glass_context_change_clears_active_target(workbench_window):
    window, workbench = workbench_window
    first = _add_glass(window, workbench)
    second = workbench.add_glass()
    workbench.set_selected(first.id)
    window._refresh_panels()
    window._set_interaction_target(first.id, "geometry")

    window.select_glass(second.id)

    assert workbench.selected_glass_id == second.id
    assert window._interaction_target is None
    assert window.canvas._active_target is None


def test_highlight_refresh_preserves_s9b_manual_transform(workbench_window):
    window, workbench = workbench_window
    glass = _add_glass(window, workbench)
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    window.canvas.set_frame(frame, reset_view=True)
    window.canvas.zoom_in()
    before = window.canvas.transform()
    assert window.canvas.fit_mode is False

    window._set_interaction_target(glass.id, "geometry")
    window._refresh_panels()

    after = window.canvas.transform()
    assert window.canvas.fit_mode is False
    assert abs(after.m11() - before.m11()) < 1e-9
    assert abs(after.m22() - before.m22()) < 1e-9
    assert abs(after.dx() - before.dx()) < 1e-9
    assert abs(after.dy() - before.dy()) < 1e-9
