from __future__ import annotations

from oil_tracker.application.ports.progress import AnalysisStage, build_progress_update
from oil_tracker.ui.widgets.analysis_progress_dialog import AnalysisProgressDialog


def test_dialog_uses_overall_progress_and_keeps_frame_completion_below_100(qtbot) -> None:
    dialog = AnalysisProgressDialog()
    qtbot.addWidget(dialog)
    dialog.update_progress(build_progress_update(AnalysisStage.VIDEO_ANALYSIS, 1.0))
    assert dialog.progress.maximum() == 1000
    assert dialog.progress.value() == 600
    assert dialog.stage.text() == "1/6 · 영상 분석"


def test_dialog_hides_frame_details_after_video_stage(qtbot) -> None:
    dialog = AnalysisProgressDialog()
    qtbot.addWidget(dialog)
    dialog.update_progress(
        build_progress_update(
            AnalysisStage.VIDEO_ANALYSIS,
            0.5,
            completed=2,
            total=4,
            timestamp_sec=1.25,
            glass_name="Glass 1",
            rate_fps=3.0,
        )
    )
    assert not dialog.frame_detail.isHidden()
    assert "1.250초" in dialog.frame_detail.text()
    dialog.update_progress(
        build_progress_update(
            AnalysisStage.RESULT_IMAGES,
            0.5,
            message="결과 이미지 생성 중",
        )
    )
    assert dialog.frame_detail.isHidden()
    assert dialog.rate.isHidden()


def test_dialog_never_rounds_prefinalization_to_100(qtbot) -> None:
    dialog = AnalysisProgressDialog()
    qtbot.addWidget(dialog)
    dialog.update_progress(
        build_progress_update(
            AnalysisStage.BUNDLE_FINALIZATION,
            1.0,
            finalization_committed=False,
        )
    )
    assert dialog.progress.value() == 999
    dialog.update_progress(
        build_progress_update(
            AnalysisStage.BUNDLE_FINALIZATION,
            1.0,
            finalization_committed=True,
        )
    )
    assert dialog.progress.value() == 1000
