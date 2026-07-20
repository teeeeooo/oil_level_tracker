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
    )


def test_main_window_creation(qtbot):
    window = MainWindow(controller(), FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    assert "분석 프로필 설정" in window.windowTitle()
    assert window.glass_list is not None
    assert window.settings.minimumWidth() >= 440
    assert window.settings.scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    assert window.settings.scroll.verticalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    assert window.debug_dock.minimumWidth() >= 760


def test_add_delete_glass_binding(qtbot):
    c = controller()
    window = MainWindow(c, FakePreview(), FakeAnalysis(), DebugRenderer())
    qtbot.addWidget(window)
    qtbot.mouseClick(window.glass_list.add_button, Qt.MouseButton.LeftButton)
    assert len(c.recipe.glasses) == 1
    assert window.settings.name.text() == "유면 관찰창 1"
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
    wizard = NewRecipeWizard()
    qtbot.addWidget(wizard)
    assert len(wizard.pageIds()) == 3
    assert wizard.preview.canvas is not None
    assert wizard.set_start.text() == "현재 위치"
    assert wizard.set_end.text() == "현재 위치"
    assert wizard.set_compressor.text() == "현재 위치"
    assert wizard.preview.transport.minimumSizeHint().height() < 80
    wizard._skip()
    assert wizard.skipped


def test_preview_request_routing(qtbot):
    c = controller()
    c.add_glass()
    preview = FakePreview()
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
