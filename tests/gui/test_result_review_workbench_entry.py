from __future__ import annotations

from oil_tracker.bootstrap import build_main_window


def test_workbench_exposes_result_review_action_and_owns_coordinator(qtbot):
    window = build_main_window()
    qtbot.addWidget(window)
    assert "result" in window.actions
    assert "review" in window.actions
    assert window.actions["result"].text() == "결과 보고서"
    assert window.actions["review"].text() == "결과 검토"
    assert window.result_review_coordinator.viewer is None
    window.close()
