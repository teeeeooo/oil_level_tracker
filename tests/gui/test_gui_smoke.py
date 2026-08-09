from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Qt, Signal

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.debug_renderer import DebugRenderer
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow
from oil_tracker.ui.wizard.new_recipe_wizard import NewRecipeWizard


class FakePreview(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def __init__(self):
        super().__init__()
        self.requests = 0

    def request(self, *_args):
        self.requests += 1


class FakeAnalysis(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()

    def start(self, *_args):
        pass

    def cancel(self):
        pass


def controller():
    repo = JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repo, validator),
        LoadRecipeUseCase(repo),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )


def test_main_window_creation(qtbot):
    window = MainWindow(controller(), FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    assert "분석 프로필 설정" in window.windowTitle()
    assert window.glass_list is not None
    assert window.settings.minimumWidth() >= 370
    assert window.settings.scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    assert window.settings.scroll.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    assert window.debug_dock.minimumWidth() >= 760


def test_add_delete_glass_binding(qtbot):
    c = controller()
    window = MainWindow(c, FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    qtbot.mouseClick(window.glass_list.add_button, Qt.MouseButton.LeftButton)
    assert len(c.recipe.glasses) == 1
    assert window.settings.name.text() == "Glass 1"
    qtbot.mouseClick(window.glass_list.delete_button, Qt.MouseButton.LeftButton)
    assert len(c.recipe.glasses) == 0


def test_save_load_model_roundtrip(tmp_path):
    c = controller()
    c.add_glass()
    path = tmp_path / "gui.oilrecipe"
    c.save(path)
    c.new_document()
    c.load(path)
    assert len(c.recipe.glasses) == 1
    assert c.selected_glass_id == c.recipe.glasses[0].id


def test_wizard_has_preview_time_pickers_and_skip(qtbot):
    wizard = NewRecipeWizard(reader_factory=lambda _path: None)
    qtbot.addWidget(wizard)
    assert len(wizard.pageIds()) == 3
    assert wizard.preview.canvas is not None
    assert wizard.set_start.text() == "현재 위치"
    assert wizard.set_end.text() == "현재 위치"
    assert wizard.set_compressor.text() == "현재 위치"
    assert wizard.preview.transport.minimumSizeHint().height() < 80
    wizard._skip()
    assert wizard.skipped


def test_wizard_closes_metadata_reader_when_metadata_access_fails(qtbot, monkeypatch):
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    class Reader:
        def __init__(self):
            self.closed = False

        @property
        def metadata(self):
            raise OSError("metadata failed")

        def close(self):
            self.closed = True

    reader = Reader()
    wizard = NewRecipeWizard(reader_factory=lambda _path: reader)
    qtbot.addWidget(wizard)
    warnings = []
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args: ("bad.mp4", ""))
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda _parent, title, message: warnings.append((title, message)),
    )

    wizard._browse()

    assert reader.closed is True
    assert wizard.video_path.text() == ""
    assert warnings == [("영상 열기 실패", "metadata failed")]


def test_preview_request_routing(qtbot):
    c = controller()
    c.add_glass()
    preview = FakePreview()
    from oil_tracker.domain.session import VideoMetadata

    c.session.input_video_path = "video.mp4"
    c.session.video_metadata = VideoMetadata("video.mp4", 1280, 720, 30.0, 10.0, 300)
    window = MainWindow(c, preview, FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    window.request_preview()
    assert preview.requests == 1


def test_validation_routing_selects_glass(qtbot):
    c = controller()
    a = c.add_glass()
    c.add_glass()
    window = MainWindow(c, FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    from oil_tracker.domain.enums import ValidationSeverity
    from oil_tracker.domain.validation import ValidationIssue

    issue = ValidationIssue(ValidationSeverity.ERROR, "X", "problem", a.id, "zero_line_y")
    window._route_validation_issue(issue)
    assert c.selected_glass_id == a.id


def test_current_test_name_is_session_owned_and_does_not_rename_profile(qtbot):
    c = controller()
    c.recipe.name = "재사용 프로필"
    window = MainWindow(c, FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)

    window.run_name_edit.setText("  반복 시험 03  ")
    window.run_name_edit.editingFinished.emit()

    assert c.session.run_name == "반복 시험 03"
    assert c.recipe.name == "재사용 프로필"
    assert "run_name" not in c.recipe.to_dict()
    assert "프로필에는 저장되지" in window.run_name_edit.toolTip()


def test_normal_open_video_clears_current_test_name_in_ui_without_mutating_profile(qtbot, monkeypatch):
    import numpy as np
    from PySide6.QtWidgets import QFileDialog

    from oil_tracker.domain.enums import WorkbenchState
    from oil_tracker.domain.session import VideoMetadata

    class Reader:
        def __init__(self, path):
            self.metadata = VideoMetadata(str(path), 1280, 720, 30.0, 10.0, 300, "fake")
            self.closed = False

        def read_at(self, _timestamp):
            return np.zeros((720, 1280, 3), dtype=np.uint8), 0, 0.0

        def close(self):
            self.closed = True

    c = controller()
    c.reader_factory = Reader
    c.recipe.name = "재사용 프로필"
    recipe_before = c.recipe.to_dict()
    c.session.run_name = "이전 시험"
    c.state = WorkbenchState.ANALYZED
    window = MainWindow(c, FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    assert window.run_name_edit.text() == "이전 시험"
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args, **_kwargs: ("new.mp4", ""))

    window.open_video()

    assert c.session.run_name == ""
    assert window.run_name_edit.text() == ""
    assert c.recipe.to_dict() == recipe_before
    assert "run_name" not in c.recipe.to_dict()


def test_open_video_dialog_cancel_preserves_current_test_name(qtbot, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    c = controller()
    c.recipe.name = "재사용 프로필"
    recipe_before = c.recipe.to_dict()
    c.session.run_name = "유지할 시험"
    window = MainWindow(c, FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    assert window.run_name_edit.text() == "유지할 시험"
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args, **_kwargs: ("", ""))

    window.open_video()

    assert c.session.run_name == "유지할 시험"
    assert window.run_name_edit.text() == "유지할 시험"
    assert c.recipe.to_dict() == recipe_before


def test_normal_open_video_metadata_failure_preserves_ui_and_reader_ownership(qtbot, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    from oil_tracker.domain.enums import WorkbenchState
    from oil_tracker.domain.session import VideoMetadata

    class ActiveReader:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    class MetadataFailureReader:
        def __init__(self):
            self.closed = False

        @property
        def metadata(self):
            raise OSError("metadata failed")

        def close(self):
            self.closed = True

    old = ActiveReader()
    candidate = MetadataFailureReader()
    c = controller()
    c.reader_factory = lambda _path: candidate
    c.video_reader = old
    c.recipe.name = "재사용 프로필"
    recipe_before = c.recipe.to_dict()
    c.session.input_video_path = "old.mp4"
    c.session.video_metadata = VideoMetadata("old.mp4", 1280, 720, 30.0, 10.0, 300, "fake")
    c.session.run_name = "유지할 시험"
    c.state = WorkbenchState.ANALYZED
    session_before = c.session.to_dict()
    window = MainWindow(c, FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    assert window.run_name_edit.text() == "유지할 시험"
    assert window.video_path_label.text() == "old.mp4"
    errors = []
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args, **_kwargs: ("bad.mp4", ""))
    monkeypatch.setattr(window, "_error", lambda title, message: errors.append((title, message)))

    window.open_video()

    assert errors == [("영상 열기 실패", "metadata failed")]
    assert c.video_reader is old
    assert old.closed is False
    assert candidate.closed is True
    assert c.session.to_dict() == session_before
    assert c.state == WorkbenchState.ANALYZED
    assert window.run_name_edit.text() == "유지할 시험"
    assert window.video_path_label.text() == "old.mp4"
    assert c.recipe.to_dict() == recipe_before
