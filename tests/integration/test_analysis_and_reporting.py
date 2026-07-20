from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline, SimpleCancellationToken
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession
from tests.fixtures.synthetic import glass_config, partial_frame


def make_video(path: Path, frames: int = 20, fps: float = 10.0) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, (320, 240))
    assert writer.isOpened()
    for index in range(frames):
        writer.write(partial_frame(170 - min(index, 15) * 4))
    writer.release()


def test_recipe_video_to_analysis_and_bundle(tmp_path):
    video = tmp_path / "sample.avi"; make_video(video)
    reader = OpenCvVideoReader(video); metadata = reader.metadata; reader.close()
    recipe = InspectionRecipe.empty(320, 240, "Integration")
    glass = glass_config(); glass.judgment_rule.stable_hold_sec = .2; glass.judgment_rule.recovery_limit_sec = 3
    recipe.glasses.append(glass)
    session = AnalysisSession(str(video), metadata, 0, metadata.duration_sec, 0, 5, str(tmp_path), resolution_confirmed=True)
    pipeline = AnalysisPipeline(lambda p: OpenCvVideoReader(p), OpenCvPhaseDetector(), RecipeValidationService())
    result = pipeline.run(recipe, session)
    assert result.glass_results[0].samples
    bundle = OutputBundleStore().write_bundle(result, recipe, session, tmp_path)
    for expected in ("report.html", "tracking_data.csv", "events.csv", "recipe_snapshot.oilrecipe", "session.json", "analysis_manifest.json"):
        assert (bundle / expected).is_file()
    html = (bundle / "report.html").read_text(encoding="utf-8")
    assert "Rotary Oil Level Analysis" in html


def test_multi_glass_decodes_each_timestamp_once(tmp_path):
    class Reader:
        def __init__(self): self.count = 0
        def read_at(self, timestamp): self.count += 1; return partial_frame(130), self.count, timestamp
        def close(self): pass
    shared = Reader()
    recipe = InspectionRecipe.empty(320, 240); recipe.glasses.extend([glass_config(), glass_config()]); recipe.glasses[1].name = "Glass B"
    from oil_tracker.domain.session import VideoMetadata
    session = AnalysisSession("fake.avi", VideoMetadata("fake.avi", 320, 240, 10, 1, 10), 0, 1, 0, 2, resolution_confirmed=True)
    pipeline = AnalysisPipeline(lambda _p: shared, OpenCvPhaseDetector(), RecipeValidationService())
    result = pipeline.run(recipe, session)
    assert len(result.glass_results) == 2
    # 3 schedule decodes + 3 optional static-learning decodes, independent of glass count.
    assert shared.count <= 6


def test_cancellation_stops_before_decode():
    recipe = InspectionRecipe.empty(320, 240); recipe.glasses.append(glass_config())
    from oil_tracker.domain.session import VideoMetadata
    session = AnalysisSession("fake.avi", VideoMetadata("fake.avi", 320, 240, 10, 1, 10), 0, 1, 0, 2, resolution_confirmed=True)
    class Reader:
        def read_at(self, _timestamp): return partial_frame(), 0, 0
        def close(self): pass
    token = SimpleCancellationToken(True)
    import pytest
    from oil_tracker.application.services.analysis_pipeline import AnalysisCancelled
    with pytest.raises(AnalysisCancelled):
        AnalysisPipeline(lambda _p: Reader(), OpenCvPhaseDetector(), RecipeValidationService()).run(recipe, session, cancellation=token)
