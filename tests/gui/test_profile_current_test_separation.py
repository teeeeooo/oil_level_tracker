from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.debug_renderer import DebugRenderer
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow
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
    def __init__(self, path):
        self.metadata = VideoMetadata(str(path), 640, 480, 30.0, 12.0, 360, "fake")
    def read_at(self, _timestamp):
        return np.zeros((480, 640, 3), dtype=np.uint8), 0, 0.0
    def close(self): pass


def _controller():
    repo = JsonRecipeRepository()
    validator = RecipeValidationService()
    controller = WorkbenchController(
        SaveRecipeUseCase(repo, validator),
        LoadRecipeUseCase(repo),
        ValidateWorkbenchUseCase(validator),
    )
    controller.reader_factory = _Reader
    return controller


def _window(qtbot):
    controller = _controller()
    window = MainWindow(controller, _Preview(), _Analysis(), DebugRenderer())
    qtbot.addWidget(window)
    return window, controller


def test_workbench_visibly_separates_profile_and_current_test_ownership(qtbot):
    window, controller = _window(qtbot)
    assert "Profile — 재사용 설정" in window.profile_context.title()
    assert "Profile에는 저장되지 않음" in window.session_bar.title()
    assert "Profile 설정" in window.glass_list.ownership_label.text()
    assert "Profile 설정" in window.settings.ownership_label.text()
    assert "Profile" in window.glass_list.ownership_hint.text()
    assert "현재 시험" in window.session_bar.title()
    assert window.profile_name_label.text() == controller.recipe.name
    assert window.profile_path_label.text() == "아직 저장되지 않음"


def test_profile_identity_refreshes_after_save_and_load(qtbot, tmp_path, monkeypatch):
    window, controller = _window(qtbot)
    controller.recipe.name = "Profile A"
    save_target = tmp_path / "profile-a"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_a, **_k: (str(save_target), ""))
    window.save_recipe()
    saved = save_target.with_suffix(".oilrecipe")
    assert controller.recipe_path == saved
    assert window.profile_name_label.text() == "Profile A"
    assert window.profile_path_label.text() == str(saved)

    other = InspectionRecipe.empty(640, 480, "Profile B")
    JsonRecipeRepository().save(tmp_path / "profile-b.oilrecipe", other)
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_a, **_k: (str(tmp_path / "profile-b.oilrecipe"), ""),
    )
    window.load_recipe()
    assert controller.recipe.name == "Profile B"
    assert window.profile_name_label.text() == "Profile B"
    assert window.profile_path_label.text() == str(tmp_path / "profile-b.oilrecipe")


def test_current_test_area_tracks_session_without_changing_profile(qtbot, monkeypatch):
    window, controller = _window(qtbot)
    controller.recipe.name = "Reusable Profile"
    controller.session.analysis_start_sec = 1.5
    controller.session.analysis_end_sec = 8.0
    controller.session.compressor_start_sec = 2.25
    controller.session.sampling_fps = 3.0
    profile_before = controller.recipe.to_dict()
    window._refresh_all()
    assert window.start_spin.value() == 1.5
    assert window.end_spin.value() == 8.0
    assert window.compressor_spin.value() == 2.25
    assert window.sampling_spin.value() == 3.0
    window.run_name_edit.setText("Run 03")
    window.run_name_edit.editingFinished.emit()
    assert controller.session.run_name == "Run 03"
    assert window.run_name_edit.text() == "Run 03"
    assert window.profile_name_label.text() == "Reusable Profile"
    assert controller.recipe.to_dict() == profile_before

    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_a, **_k: ("next.mp4", ""))
    window.open_video()
    assert controller.session.input_video_path == "next.mp4"
    assert window.video_path_label.text() == "next.mp4"
    assert controller.session.run_name == ""
    assert window.run_name_edit.text() == ""
    assert window.profile_name_label.text() == "Reusable Profile"
    assert controller.recipe.to_dict() == profile_before


def test_same_profile_replacement_shows_snapshot_profile_and_fresh_current_test(qtbot, monkeypatch):
    window, controller = _window(qtbot)
    snapshot = InspectionRecipe.empty(640, 480, "Snapshot Profile")
    controller.recipe.name = "Old Profile"
    controller.session.run_name = "Old Run"
    window._refresh_all()
    bundle = SimpleNamespace(
        recipe=snapshot,
        session=SimpleNamespace(sampling_fps=2.0),
        source_video_path="old.mp4",
        root=Path("."),
    )
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_a, **_k: ("next.mp4", ""))
    monkeypatch.setattr(QMessageBox, "question", lambda *_a, **_k: QMessageBox.StandardButton.Yes)
    coordinator = SameProfileAnalysisCoordinator(window)

    assert coordinator.start(bundle) is True
    assert controller.recipe.name == "Snapshot Profile"
    assert controller.recipe_path is None
    assert controller.session.input_video_path == "next.mp4"
    assert controller.session.run_name == ""
    assert window.profile_name_label.text() == "Snapshot Profile"
    assert window.profile_path_label.text() == "아직 저장되지 않음"
    assert window.video_path_label.text() == "next.mp4"
    assert window.run_name_edit.text() == ""


def test_new_profile_refreshes_profile_identity_from_recipe_owner(qtbot):
    window, controller = _window(qtbot)
    controller.recipe.name = "Old Profile"
    window._refresh_all()
    controller.new_document(800, 600, "New Reusable Profile")
    window._refresh_all()
    assert window.profile_name_label.text() == "New Reusable Profile"
    assert window.profile_path_label.text() == "아직 저장되지 않음"
    assert controller.recipe_path is None
