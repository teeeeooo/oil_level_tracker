from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.debug_renderer import DebugRenderer
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession
from oil_tracker.ui.analysis_completion_coordinator import AnalysisCompletionCoordinator
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow
from oil_tracker.ui.preflight_coordinator import PreflightCoordinator
from oil_tracker.ui.result_actions import ResultActionService
from oil_tracker.ui.result_review_coordinator import ResultReviewCoordinator
from oil_tracker.ui.same_profile_analysis_coordinator import SameProfileAnalysisCoordinator


class _Preview(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)
    def invalidate(self): pass
    def request(self, *_args): pass


class _Analysis(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()
    def start(self, *_args): pass
    def cancel(self): pass


class _Reader:
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True


class _ClosableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.closed = False

    def closeEvent(self, event):
        self.closed = True
        super().closeEvent(event)


class _PreparedResource:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class _PreflightController(QObject):
    started = Signal()
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self.invalidations = 0

    def start(self, *_args): pass
    def cancel(self): pass
    def invalidate(self):
        self.invalidations += 1


def _controller(save_repository=None, load_repository=None):
    save_repository = save_repository or JsonRecipeRepository()
    load_repository = load_repository or save_repository
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(save_repository, validator),
        LoadRecipeUseCase(load_repository),
        ValidateWorkbenchUseCase(validator),
    )


def _window(controller):
    return MainWindow(controller, _Preview(), _Analysis(), DebugRenderer())


def _attach_close_lifecycles(window):
    preflight_controller = _PreflightController()
    preflight = PreflightCoordinator(window, preflight_controller)
    preflight._running = True
    same_profile = SameProfileAnalysisCoordinator(window)
    prepared = _PreparedResource()
    same_profile._prepared = prepared
    review = ResultReviewCoordinator(window)
    review_widget = _ClosableWidget(window)
    review.viewer = review_widget
    completion = AnalysisCompletionCoordinator(
        window, review, same_profile, ResultActionService()
    )
    completion_widget = _ClosableWidget(window)
    completion.dialog = completion_widget
    return (
        preflight_controller, preflight, same_profile, prepared,
        review, review_widget, completion, completion_widget,
    )


def _assert_lifecycles_preserved(lifecycle) -> None:
    controller, preflight, same_profile, prepared, review, review_widget, completion, completion_widget = lifecycle
    assert controller.invalidations == 0
    assert preflight._running is True
    assert same_profile._prepared is prepared
    assert prepared.closed is False
    assert review.viewer is review_widget
    assert review_widget.closed is False
    assert completion.dialog is completion_widget
    assert completion_widget.closed is False


def _assert_lifecycles_closed(lifecycle) -> None:
    controller, preflight, same_profile, prepared, review, review_widget, completion, completion_widget = lifecycle
    assert controller.invalidations == 1
    assert preflight._running is False
    assert same_profile._prepared is None
    assert prepared.closed is True
    assert review.viewer is None
    assert review_widget.closed is True
    assert completion.dialog is None
    assert completion_widget.closed is True


def _saved_controller(tmp_path: Path):
    controller = _controller()
    controller.new_document(640, 480, "Profile")
    controller.add_glass()
    controller.save(tmp_path / "profile.oilrecipe")
    return controller


def test_clean_close_has_no_unsaved_profile_prompt(qtbot, tmp_path, monkeypatch):
    controller = _saved_controller(tmp_path)
    reader = _Reader()
    controller.video_reader = reader
    window = _window(controller)
    lifecycle = _attach_close_lifecycles(window)
    prompts = []
    monkeypatch.setattr(window, "_confirm_unsaved_profile_close", lambda: prompts.append(True))

    assert window.close() is True

    assert prompts == []
    assert reader.closed is True
    _assert_lifecycles_closed(lifecycle)


def test_dirty_close_cancel_preserves_workbench_and_reader(qtbot, tmp_path, monkeypatch):
    controller = _saved_controller(tmp_path)
    reader = _Reader()
    controller.video_reader = reader
    controller.session = AnalysisSession(run_name="Run 1", analysis_start_sec=1.0)
    controller.recipe.name = "Changed Profile"
    before_recipe = controller.recipe.to_dict()
    before_session = controller.session.to_dict()
    window = _window(controller)
    lifecycle = _attach_close_lifecycles(window)
    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Cancel,
    )

    assert window.close() is False

    assert reader.closed is False
    assert controller.recipe.to_dict() == before_recipe
    assert controller.session.to_dict() == before_session
    assert controller.profile_has_unsaved_changes is True
    _assert_lifecycles_preserved(lifecycle)

    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Discard,
    )
    assert window.close() is True
    _assert_lifecycles_closed(lifecycle)


def test_dirty_close_discard_does_not_write_profile(qtbot, tmp_path, monkeypatch):
    controller = _saved_controller(tmp_path)
    path = controller.recipe_path
    before = path.read_bytes()
    controller.recipe.name = "Discard Me"
    reader = _Reader()
    controller.video_reader = reader
    window = _window(controller)
    lifecycle = _attach_close_lifecycles(window)
    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Discard,
    )

    assert window.close() is True

    assert reader.closed is True
    assert path.read_bytes() == before
    assert controller.profile_has_unsaved_changes is True
    _assert_lifecycles_closed(lifecycle)


def test_dirty_close_save_uses_existing_authoritative_profile_path(qtbot, tmp_path, monkeypatch):
    controller = _saved_controller(tmp_path)
    path = controller.recipe_path
    controller.recipe.name = "Saved On Close"
    reader = _Reader()
    controller.video_reader = reader
    window = _window(controller)
    lifecycle = _attach_close_lifecycles(window)
    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Save,
    )

    assert window.close() is True

    assert reader.closed is True
    assert controller.profile_has_unsaved_changes is False
    assert controller.recipe_path == path
    assert JsonRecipeRepository().load(path).name == "Saved On Close"
    _assert_lifecycles_closed(lifecycle)


def test_save_as_cancel_during_close_keeps_window_state(qtbot, tmp_path, monkeypatch):
    controller = _controller()
    controller.new_document(640, 480, "Unsaved New Profile")
    reader = _Reader()
    controller.video_reader = reader
    before = controller.recipe.to_dict()
    window = _window(controller)
    lifecycle = _attach_close_lifecycles(window)
    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Save,
    )
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_a, **_k: ("", ""))

    assert window.close() is False

    assert reader.closed is False
    assert controller.recipe_path is None
    assert controller.recipe.to_dict() == before
    assert controller.profile_has_unsaved_changes is True
    _assert_lifecycles_preserved(lifecycle)

    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Discard,
    )
    assert window.close() is True
    _assert_lifecycles_closed(lifecycle)


class _FailingRepository(JsonRecipeRepository):
    def save(self, path, recipe):
        raise OSError("save failed")


def test_save_failure_during_close_keeps_workbench_open(qtbot, tmp_path, monkeypatch):
    source = tmp_path / "profile.oilrecipe"
    JsonRecipeRepository().save(source, InspectionRecipe.empty(640, 480, "Profile"))
    controller = _controller(_FailingRepository(), JsonRecipeRepository())
    controller.load(source)
    controller.recipe.name = "Changed"
    before_recipe = controller.recipe.to_dict()
    before_session = controller.session.to_dict()
    reader = _Reader()
    controller.video_reader = reader
    window = _window(controller)
    lifecycle = _attach_close_lifecycles(window)
    errors = []
    monkeypatch.setattr(window, "_error", lambda title, message: errors.append((title, message)))
    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Save,
    )

    assert window.close() is False

    assert reader.closed is False
    assert errors == [("프로필 저장 실패", "save failed")]
    assert controller.recipe.to_dict() == before_recipe
    assert controller.session.to_dict() == before_session
    assert controller.profile_has_unsaved_changes is True
    assert JsonRecipeRepository().load(source).name == "Profile"
    _assert_lifecycles_preserved(lifecycle)

    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Discard,
    )
    assert window.close() is True
    _assert_lifecycles_closed(lifecycle)


def test_recipe_edit_then_undo_to_saved_content_returns_clean(qtbot, tmp_path):
    controller = _saved_controller(tmp_path)
    window = _window(controller)
    original_name = controller.recipe.glasses[0].name

    window._field_changed("name", "Changed Glass")
    assert controller.profile_has_unsaved_changes is True
    assert window.undo_stack.canUndo()

    window.undo_stack.undo()

    assert controller.recipe.glasses[0].name == original_name
    assert controller.profile_has_unsaved_changes is False


def test_session_only_edit_keeps_profile_clean_and_s8_c2_separation(qtbot, tmp_path):
    controller = _saved_controller(tmp_path)
    window = _window(controller)
    recipe_before = controller.recipe.to_dict()

    window.run_name_edit.setText("Current Run")
    window.start_spin.setValue(1.0)
    window.end_spin.setValue(8.0)
    window.compressor_spin.setValue(2.0)
    window.sampling_spin.setValue(3.0)
    window._session_changed()

    assert controller.recipe.to_dict() == recipe_before
    assert controller.profile_has_unsaved_changes is False
    assert window.profile_name_label.text() == controller.recipe.name
    assert "Profile에는 저장되지 않음" in window.session_bar.title()


def test_save_as_on_close_keeps_extension_normalization(qtbot, tmp_path, monkeypatch):
    controller = _controller()
    controller.new_document(640, 480, "New Profile")
    window = _window(controller)
    requested = tmp_path / "new-profile"
    monkeypatch.setattr(
        window,
        "_confirm_unsaved_profile_close",
        lambda: QMessageBox.StandardButton.Save,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_a, **_k: (str(requested), ""),
    )

    event = QCloseEvent()
    window.closeEvent(event)

    actual = requested.with_suffix(".oilrecipe")
    assert event.isAccepted()
    assert controller.recipe_path == actual
    assert actual.is_file()
    assert controller.profile_has_unsaved_changes is False
