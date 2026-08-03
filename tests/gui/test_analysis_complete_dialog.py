from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox

from oil_tracker.domain.enums import ResultState
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult
from oil_tracker.ui.analysis_completion_summary import build_final_run_summary
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
    assert "사용자 확인 필요" in dialog.title_label.text()
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


def test_dialog_distinguishes_finalized_run_profile_and_source_video(qtbot, tmp_path):
    output = tmp_path / "bundle"
    bundle = SimpleNamespace(
        run_name="반복 시험 03",
        recipe=SimpleNamespace(name="회수 시험 Profile"),
        source_video_path=r"C:\시험 영상\기동 03.mp4",
    )
    summary = build_final_run_summary(_result(), output, bundle)
    dialog = AnalysisCompleteDialog(_result(), output, summary=summary)
    qtbot.addWidget(dialog)

    assert dialog.run_name_label.text() == "반복 시험 03"
    assert dialog.profile_name_label.text() == "회수 시험 Profile"
    assert dialog.source_video_label.text() == "기동 03.mp4"
    assert dialog.source_video_label.toolTip() == r"C:\시험 영상\기동 03.mp4"
    assert dialog.path_label.text() == str(output)
    assert dialog.metadata_status_label.text() == ""


def test_empty_run_name_is_explicit_and_does_not_borrow_other_identity(qtbot, tmp_path):
    bundle = SimpleNamespace(
        run_name="",
        recipe=SimpleNamespace(name="Profile A"),
        source_video_path="source-a.mp4",
    )
    summary = build_final_run_summary(_result(), tmp_path / "bundle", bundle)
    dialog = AnalysisCompleteDialog(_result(), tmp_path / "bundle", summary=summary)
    qtbot.addWidget(dialog)

    assert dialog.run_name_label.text() == "이름 없음 (현재 시험 이름 미지정)"
    assert "Profile A" not in dialog.run_name_label.text()
    assert "source-a.mp4" not in dialog.run_name_label.text()
