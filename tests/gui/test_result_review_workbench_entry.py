from __future__ import annotations

from oil_tracker.bootstrap import build_main_window
from oil_tracker.ui.redetection_result_review_window import RedetectionResultReviewWindow


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
