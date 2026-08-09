from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest
from PySide6.QtCore import QCoreApplication, QObject, Signal
from PySide6.QtWidgets import QApplication, QWidget

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow


class _Preview(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def invalidate(self):
        pass

    def request(self, *_args):
        pass


class _Analysis(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()

    def start(self, *_args):
        pass

    def cancel(self):
        pass


class _Renderer:
    def export(self, *_args):
        return []


def _workbench() -> WorkbenchController:
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
        reader_factory=lambda _path: None,
    )


def test_qapp_is_the_single_qapplication_owner(qapp):
    assert isinstance(qapp, QApplication)
    assert QApplication.instance() is qapp
    assert QCoreApplication.instance() is qapp


def test_qtbot_reuses_the_session_qapplication(qapp, qtbot):
    assert QApplication.instance() is qapp
    widget = QWidget()
    qtbot.addWidget(widget)
    assert QApplication.instance() is qapp


def test_injected_qt_platform_is_restored_after_application_creation(qapp):
    if qapp.property("oil_tracker_test_qpa_injected"):
        assert "QT_QPA_PLATFORM" not in os.environ
        assert QApplication.platformName() == "offscreen"


def test_registered_dirty_main_window_teardown_is_noninteractive(qtbot):
    workbench = _workbench()
    window = MainWindow(workbench, _Preview(), _Analysis(), _Renderer())
    qtbot.addWidget(window)
    workbench.add_glass()

    assert workbench.profile_has_unsaved_changes is True
    assert window._confirm_unsaved_profile_close.__func__ is MainWindow._confirm_unsaved_profile_close


def test_qt_state_verifier_rejects_visible_top_level_widgets(
    qapp, qtbot, qt_state_verifier
):
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.show()
    qapp.processEvents()
    with pytest.raises(AssertionError, match="visible top-level widgets leaked"):
        qt_state_verifier(qapp)
    widget.close()
    qapp.processEvents()
    qt_state_verifier(qapp)


def test_qt_core_and_value_imports_do_not_create_an_application(
    headless_subprocess_env,
):
    code = (
        "from PySide6.QtCore import QCoreApplication, QObject; "
        "from oil_tracker.adapters.presentation.qt_frame_image_converter "
        "import QtFrameImageConverter; "
        "assert QObject is not None; "
        "assert QtFrameImageConverter is not None; "
        "assert QCoreApplication.instance() is None"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        env=headless_subprocess_env,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
