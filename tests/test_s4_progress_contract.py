from __future__ import annotations

import math

from oil_tracker.application.ports.progress import (
    ANALYSIS_STAGE_SPECS,
    AnalysisStage,
    MonotonicProgressSink,
    build_progress_update,
)


def test_official_analysis_stage_order_labels_and_weights() -> None:
    assert [spec.key for spec in ANALYSIS_STAGE_SPECS] == [
        AnalysisStage.VIDEO_ANALYSIS,
        AnalysisStage.EVENTS_AND_JUDGMENT,
        AnalysisStage.RESULT_IMAGES,
        AnalysisStage.CSV_AND_SNAPSHOTS,
        AnalysisStage.GRAPHS_AND_REPORT,
        AnalysisStage.BUNDLE_FINALIZATION,
    ]
    assert [spec.label for spec in ANALYSIS_STAGE_SPECS] == [
        "영상 분석",
        "이벤트와 판정 계산",
        "결과 이미지 생성",
        "CSV와 snapshot 저장",
        "graph와 보고서 생성",
        "bundle 마무리",
    ]
    assert sum(spec.weight_percent for spec in ANALYSIS_STAGE_SPECS) == 100
    assert ANALYSIS_STAGE_SPECS[0].weight_percent == max(
        spec.weight_percent for spec in ANALYSIS_STAGE_SPECS
    )


def test_frame_stage_completion_is_not_overall_completion() -> None:
    update = build_progress_update(AnalysisStage.VIDEO_ANALYSIS, 1.0)
    assert update.stage_fraction == 1.0
    assert update.overall_fraction == 0.60
    assert update.overall_fraction < 1.0


def test_atomic_commit_is_required_for_exact_overall_completion() -> None:
    before_replace = build_progress_update(
        AnalysisStage.BUNDLE_FINALIZATION,
        1.0,
        finalization_committed=False,
    )
    after_replace = build_progress_update(
        AnalysisStage.BUNDLE_FINALIZATION,
        1.0,
        finalization_committed=True,
    )
    assert before_replace.overall_fraction < 1.0
    assert after_replace.overall_fraction == 1.0


def test_monotonic_sink_suppresses_stage_and_fraction_regression() -> None:
    received = []
    sink = MonotonicProgressSink(received.append)
    sink(build_progress_update(AnalysisStage.VIDEO_ANALYSIS, 0.5))
    sink(build_progress_update(AnalysisStage.VIDEO_ANALYSIS, 0.25))
    sink(build_progress_update(AnalysisStage.EVENTS_AND_JUDGMENT, 0.2))
    sink(build_progress_update(AnalysisStage.VIDEO_ANALYSIS, 1.0))
    sink(
        build_progress_update(
            AnalysisStage.BUNDLE_FINALIZATION,
            1.0,
            finalization_committed=True,
        )
    )
    assert [update.stage_key for update in received] == [
        AnalysisStage.VIDEO_ANALYSIS,
        AnalysisStage.EVENTS_AND_JUDGMENT,
        AnalysisStage.BUNDLE_FINALIZATION,
    ]
    assert all(
        left.overall_fraction <= right.overall_fraction
        for left, right in zip(received, received[1:])
    )
    assert math.isclose(received[-1].overall_fraction, 1.0)
