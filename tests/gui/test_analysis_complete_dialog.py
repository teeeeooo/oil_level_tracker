from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox

from oil_tracker.domain.enums import ResultState
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult
from oil_tracker.ui.widgets.analysis_complete_dialog import AnalysisCompleteDialog


def _result():
    return AnalysisResult(
        run_id="run",
        overall_state=ResultState.REVIEW_REQUIRED,
        glass_results=[
            GlassAnalysisResult("g1", "Glass 1", ResultState.PASS),
            GlassAnalysisResult("g2", "Glass 2", ResultState.REVIEW_REQUIRED),
        ],
        started_at="2026-07-21T00:00:00",
        completed_at="2026-07-21T00:01:00",
        warnings=["warning"],
        errors=["error-a", "error-b"],
    )


def test_dialog_displays_result_path_per_glass_counts_and_analyzed_state(qtbot, tmp_path):
    output = tmp_path / "bundle"
    dialog = AnalysisCompleteDialog(_result(), output)
    qtbot.addWidget(dialog)
    assert "검토 필요" in dialog.title_label.text()
    assert dialog.path_label.text() == str(output)
    assert "Glass 1" in dialog.summary_label.text()
    assert "Glass 2" in dialog.summary_label.text()
    assert "경고 1개" in dialog.counts_label.text()
    assert "오류 2개" in dialog.counts_label.text()
    assert "ANALYZED" in dialog.counts_label.text()


def test_dialog_emits_each_action_once_per_click(qtbot, tmp_path):
    dialog = AnalysisCompleteDialog(_result(), tmp_path / "bundle")
    qtbot.addWidget(dialog)
    received = []
    dialog.reviewRequested.connect(lambda: received.append("review"))
    dialog.reportRequested.connect(lambda: received.append("report"))
    dialog.folderRequested.connect(lambda: received.append("folder"))
    dialog.sameProfileRequested.connect(lambda: received.append("same_profile"))
    for button in (
        dialog.review_button,
        dialog.report_button,
        dialog.folder_button,
        dialog.same_profile_button,
    ):
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert received == ["review", "report", "folder", "same_profile"]


def test_dialog_close_does_not_mutate_result(qtbot, tmp_path):
    result = _result()
    dialog = AnalysisCompleteDialog(result, tmp_path / "bundle")
    qtbot.addWidget(dialog)
    close_button = dialog.close_box.button(QDialogButtonBox.StandardButton.Close)
    qtbot.mouseClick(close_button, Qt.MouseButton.LeftButton)
    assert result.overall_state == ResultState.REVIEW_REQUIRED
    assert len(result.errors) == 2
