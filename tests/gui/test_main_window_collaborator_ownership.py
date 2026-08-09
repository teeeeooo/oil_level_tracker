from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog

import oil_tracker.ui.profile_lifecycle_coordinator as profile_lifecycle_module
from oil_tracker.adapters.presentation.qt_frame_image_converter import blank_bgr_frame
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow


class _Preview(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.invalidations = 0

    def invalidate(self) -> None:
        self.invalidations += 1

    def request(self, *_args) -> None:
        pass


class _Analysis(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()

    def start(self, *_args) -> None:
        pass

    def cancel(self) -> None:
        pass


class _Renderer:
    def export(self, *_args):
        return []


class _Reader:
    def __init__(self) -> None:
        self.metadata = VideoMetadata("video.mp4", 640, 480, 10.0, 2.0, 20)
        self.requests: list[float] = []

    def read_at(self, timestamp: float):
        self.requests.append(timestamp)
        return blank_bgr_frame(640, 480), int(timestamp * 10), timestamp

    def close(self) -> None:
        pass


class _History:
    def entries(self):
        return ()


def _window(qtbot) -> tuple[MainWindow, _Preview]:
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    workbench = WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )
    preview = _Preview()
    window = MainWindow(workbench, preview, _Analysis(), _Renderer())
    qtbot.addWidget(window)
    return window, preview


def test_playback_state_has_one_controller_owner_with_compatibility_accessors(qtbot):
    window, _preview = _window(qtbot)
    owner = window.playback_controller

    assert "current_frame" not in window.__dict__
    assert "current_time" not in window.__dict__
    assert "current_frame_index" not in window.__dict__
    assert "_preview_context" not in window.__dict__
    assert "last_debug_artifacts" not in window.__dict__

    frame = object()
    window.current_frame = frame
    window.current_time = 1.25
    window.current_frame_index = 12
    window._preview_context = ("glass", 12, 1.25)
    window.last_debug_artifacts = "artifacts"

    assert owner.current_frame is frame
    assert owner.current_time == 1.25
    assert owner.current_frame_index == 12
    assert owner.preview_context == ("glass", 12, 1.25)
    assert owner.last_debug_artifacts == "artifacts"
    assert window.play_timer is owner.play_timer
    assert window.preview_timer is owner.preview_timer


def test_playback_controller_owns_decode_timers_and_shutdown(qtbot):
    window, preview = _window(qtbot)
    reader = _Reader()
    window.workbench.video_reader = reader
    window.workbench.session.input_video_path = reader.metadata.path
    window.workbench.session.video_metadata = reader.metadata

    window.transport.seekRequested.emit(0.25)
    window.transport.playToggled.emit(True)

    assert reader.requests == [0.5]
    assert window.playback_controller.current_time == 0.5
    assert window.play_timer.isActive()
    assert window.preview_timer.isActive()

    window.playback_controller.close()

    assert not window.play_timer.isActive()
    assert not window.preview_timer.isActive()
    assert preview.invalidations > 0


def test_profile_lifecycle_owns_navigation_state_and_close_policy(qtbot, monkeypatch):
    window, _preview = _window(qtbot)
    history = _History()
    window.set_recent_profile_history(history)
    pending = Path("pending.oilrecipe")
    window._pending_profile_path = pending

    assert "recent_profile_history" not in window.__dict__
    assert "_pending_profile_path" not in window.__dict__
    assert window.profile_lifecycle.recent_profile_history is history
    assert window.profile_lifecycle.pending_profile_path is pending

    close_requests = []
    monkeypatch.setattr(
        window.profile_lifecycle,
        "accept_close",
        lambda confirm: close_requests.append(confirm) or False,
    )
    event = QCloseEvent()
    window.closeEvent(event)

    assert not event.isAccepted()
    assert len(close_requests) == 1
    assert close_requests[0].__self__ is window


def test_new_profile_action_routes_through_profile_lifecycle_owner(qtbot, monkeypatch):
    window, _preview = _window(qtbot)
    window.workbench.add_glass()

    class _SkippedWizard:
        DialogCode = QDialog.DialogCode

        def __init__(self, **_kwargs) -> None:
            self.skipped = True

        def exec(self):
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(profile_lifecycle_module, "NewRecipeWizard", _SkippedWizard)

    window.actions["new"].trigger()

    assert window.workbench.recipe.glasses == []
    assert window.workbench.selected_glass_id is None
    assert window.workbench.video_reader is None
    assert window.playback_controller.current_frame_index == 0
    assert window.playback_controller.current_time == 0.0
