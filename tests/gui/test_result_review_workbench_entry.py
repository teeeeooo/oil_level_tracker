from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QLabel, QMessageBox

from oil_tracker.bootstrap import build_main_window
from oil_tracker.domain.session import DebugTraceLevel
from oil_tracker.ui.redetection_result_review_window import RedetectionResultReviewWindow


def test_real_startup_installs_one_debug_trace_selector(qtbot, monkeypatch):
    window = build_main_window()
    qtbot.addWidget(window)
    window.show()
    selectors = window.findChildren(QComboBox, "debugTraceLevelCombo")
    labels = [
        label for label in window.session_bar.findChildren(QLabel)
        if label.text() == "분석 기록 옵션"
    ]
    assert len(selectors) == len(labels) == 1
    selector = selectors[0]
    assert selector is window.debug_trace_selector
    assert selector.isVisible()
    messages = []
    monkeypatch.setattr(QMessageBox, "information", lambda *_args: messages.append(_args))
    selector.setCurrentIndex(selector.findData(DebugTraceLevel.FULL.value))
    assert window.workbench.session.debug_trace_level is DebugTraceLevel.FULL
    assert len(messages) == 1
    window._refresh_all()
    assert selector.currentData() == DebugTraceLevel.FULL.value
    assert len(window.findChildren(QComboBox, "debugTraceLevelCombo")) == 1
    window.close()


def test_workbench_exposes_result_review_action_and_owns_coordinator(qtbot):
    window = build_main_window()
    qtbot.addWidget(window)
    assert "result" in window.actions
    assert "review" in window.actions
    assert window.actions["result"].text() == "결과 보고서"
    assert window.actions["review"].text() == "결과 검토"
    assert window.result_review_coordinator.viewer is None
    assert window.result_review_coordinator.viewer_factory is not None

    viewer = window.result_review_coordinator.viewer_factory(window)
    qtbot.addWidget(viewer)
    assert isinstance(viewer, RedetectionResultReviewWindow)
    assert viewer.playback.reader_factory is not None
    assert viewer.png_exporter is not None
    assert viewer.debug_artifact_presenter is not None
    assert not hasattr(viewer.canvas, "save_png")
    viewer.close()
    window.close()
