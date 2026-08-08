from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline, SimpleCancellationToken
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, InitialStateConfirmation
from tests.fixtures.synthetic import glass_config, partial_frame


def make_video(path: Path, frames: int = 20, fps: float = 10.0) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, (320, 240))
    assert writer.isOpened()
    for index in range(frames):
        writer.write(partial_frame(170 - min(index, 15) * 4))
    writer.release()


def _confirm_observed_only(recipe: InspectionRecipe, session: AnalysisSession) -> None:
    for glass in recipe.glasses:
        glass.initial_state = InitialObservationState.UNKNOWN_REVIEW
        session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
            InitialObservationState.UNKNOWN_REVIEW,
            session.input_video_path,
            session.analysis_start_sec,
        )


def test_recipe_video_to_analysis_and_bundle(tmp_path):
    video = tmp_path / "sample.avi"
    make_video(video)
    reader = OpenCvVideoReader(video)
    metadata = reader.metadata
    reader.close()
    recipe = InspectionRecipe.empty(320, 240, "Integration")
    glass = glass_config()
    glass.judgment_rule.stable_hold_sec = .2
    glass.judgment_rule.recovery_limit_sec = 3
    recipe.glasses.append(glass)
    session = AnalysisSession(
        str(video),
        metadata,
        0,
        metadata.duration_sec,
        0,
        5,
        str(tmp_path),
        resolution_confirmed=True,
    )
    _confirm_observed_only(recipe, session)
    pipeline = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector(),
        RecipeValidationService(),
    )
    result = pipeline.run(recipe, session)
    assert result.glass_results[0].samples
    bundle = OutputBundleStore().write_bundle(result, recipe, session, tmp_path)
    for expected in (
        "report.html",
        "tracking_data.csv",
        "events.csv",
        "recipe_snapshot.oilrecipe",
        "session.json",
        "analysis_manifest.json",
    ):
        assert (bundle / expected).is_file()
    report_bytes = (bundle / "report.html").read_bytes()
    assert report_bytes.startswith(b"\xef\xbb\xbf")
    html = report_bytes.decode("utf-8-sig")
    assert "유면 관찰 보고서" in html
    assert "분석 프로필" in html
    assert "영상에서 확인할 주요 순간" in html
    assert "관측 최고 유면" in html
    assert "관측 최저 유면" in html
    assert "LOW_CONFIDENCE_START" not in html
    assert "Valid sample coverage" not in html
    assert "판정 안내" in html
    assert '<img class="capture"' in html
    assert list((bundle / "captures").glob("*.png"))


def test_multi_glass_decodes_each_timestamp_once(tmp_path):
    class Reader:
        def __init__(self):
            self.count = 0

        def read_at(self, timestamp):
            self.count += 1
            return partial_frame(130), self.count, timestamp

        def close(self):
            pass

    shared = Reader()
    recipe = InspectionRecipe.empty(320, 240)
    recipe.glasses.extend([glass_config(), glass_config()])
    recipe.glasses[1].name = "Glass B"
    from oil_tracker.domain.session import VideoMetadata

    session = AnalysisSession(
        "fake.avi",
        VideoMetadata("fake.avi", 320, 240, 10, 1, 10),
        0,
        1,
        0,
        2,
        resolution_confirmed=True,
    )
    _confirm_observed_only(recipe, session)
    pipeline = AnalysisPipeline(
        lambda _path: shared,
        OpenCvPhaseDetector(),
        RecipeValidationService(),
    )
    result = pipeline.run(recipe, session)
    assert len(result.glass_results) == 2
    # 3 schedule decodes + 3 optional static-learning decodes, independent of glass count.
    assert shared.count <= 6


def test_cancellation_stops_before_decode():
    recipe = InspectionRecipe.empty(320, 240)
    recipe.glasses.append(glass_config())
    from oil_tracker.domain.session import VideoMetadata

    session = AnalysisSession(
        "fake.avi",
        VideoMetadata("fake.avi", 320, 240, 10, 1, 10),
        0,
        1,
        0,
        2,
        resolution_confirmed=True,
    )
    _confirm_observed_only(recipe, session)

    class Reader:
        def read_at(self, _timestamp):
            return partial_frame(), 0, 0

        def close(self):
            pass

    token = SimpleCancellationToken(True)
    import pytest

    from oil_tracker.application.services.analysis_pipeline import AnalysisCancelled

    with pytest.raises(AnalysisCancelled):
        AnalysisPipeline(
            lambda _path: Reader(),
            OpenCvPhaseDetector(),
            RecipeValidationService(),
        ).run(recipe, session, cancellation=token)


class _RetrospectiveSequenceDetector:
    def __init__(self) -> None:
        self.calls = 0

    def reset(self) -> None:
        self.calls = 0

    def detect(self, _frame, glass, frame_index, time_sec, debug=False):
        del debug
        call = self.calls
        self.calls += 1
        if call < 2:
            detection = PhaseDetection(
                glass.id,
                frame_index,
                time_sec,
                FillState.UNKNOWN_REVIEW,
                overall_confidence=0.2,
            )
            return detection, None
        boundary_y = 35.0 + (call - 2) * 10.0
        zero = glass.geometry.zero_line_y
        oil_px = None if zero is None else zero - boundary_y
        detection = PhaseDetection(
            glass.id,
            frame_index,
            time_sec,
            FillState.DRAINING_VISIBLE,
            oil_air_level_y=boundary_y,
            oil_air_level_px_from_zero=oil_px,
            oil_air_confidence=0.95,
            visibility_confidence=0.95,
            overall_confidence=0.95,
            raw_oil_air_level_y=boundary_y,
            smoothed_oil_air_level_y=boundary_y,
        )
        return detection, None


def test_pipeline_bundle_reader_preserves_retrospective_provenance_separately(tmp_path):
    video = tmp_path / "retrospective.avi"
    make_video(video, frames=25, fps=10.0)
    metadata_reader = OpenCvVideoReader(video)
    metadata = metadata_reader.metadata
    metadata_reader.close()

    recipe = InspectionRecipe.empty(320, 240, "Retrospective integration")
    glass = glass_config()
    glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    recipe.glasses.append(glass)
    session = AnalysisSession(
        input_video_path=str(video),
        video_metadata=metadata,
        analysis_start_sec=0.0,
        analysis_end_sec=2.0,
        compressor_start_sec=0.0,
        sampling_fps=2.0,
        output_directory=str(tmp_path),
        resolution_confirmed=True,
    )
    session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
        glass.initial_state,
        session.input_video_path,
        session.analysis_start_sec,
    )

    result = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        _RetrospectiveSequenceDetector(),
        RecipeValidationService(),
    ).run(recipe, session)
    glass_result = result.glass_results[0]
    assert glass_result.retrospective is not None
    assert glass_result.retrospective.accepted is True
    assert glass_result.samples[0].fill_state is FillState.UNKNOWN_REVIEW
    assert glass_result.samples[0].raw_oil_air_level_y is None
    assert glass_result.effective_state_aware_coverage_ratio > glass_result.valid_coverage_ratio

    output = OutputBundleStore().write_bundle(result, recipe, session, tmp_path)
    bundle = ResultBundleReader().read(output)
    interpretation = bundle.retrospective_for_glass(glass.id)
    assert bundle.result_semantics_version == 2
    assert interpretation is not None and interpretation.accepted
    assert bundle.samples[0].fill_state is FillState.UNKNOWN_REVIEW
    assert bundle.samples[0].raw_oil_air_level_y is None
