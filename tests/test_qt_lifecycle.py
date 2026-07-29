from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QWidget


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
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
