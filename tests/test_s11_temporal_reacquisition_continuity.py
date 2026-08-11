from __future__ import annotations

"""Corpus-level continuity contract for the R6 observation resolver.

The removed test asserted private counters from the retired current-frame
temporal tracker.  R6 continuity is owned by the completed-window observation
path, while every published coordinate must still exist in its source frame.
"""

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.session import AnalysisSession
from tests.s11_local_corpus import require_s11_local_corpus


class _DetectorRegressionValidator:
    def __init__(self) -> None:
        self.inner = RecipeValidationService()

    def validate(self, recipe, session, **_kwargs):
        return self.inner.validate(recipe, session, require_run_confirmation=False)


def test_sample3_observation_path_recovers_rise_without_coordinate_carry(tmp_path) -> None:
    root = require_s11_local_corpus()
    video_path = root / "sample" / "sample3.mp4"
    recipe = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe")
    reader = OpenCvVideoReader(str(video_path))
    try:
        metadata = reader.metadata
    finally:
        reader.close()

    session = AnalysisSession(
        input_video_path=str(video_path),
        video_metadata=metadata,
        analysis_start_sec=30.03,
        analysis_end_sec=40.1,
        compressor_start_sec=30.03,
        sampling_fps=2.0,
        output_directory=str(tmp_path),
        run_name="S11 R6 observation continuity regression",
        resolution_confirmed=True,
    )
    result = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector(),
        _DetectorRegressionValidator(),
    ).run(recipe, session)
    rows = result.glass_results[0].samples
    numeric = [row for row in rows if row.raw_oil_air_level_y is not None]

    assert len(rows) >= 20
    assert len(numeric) >= 15
    assert float(numeric[0].raw_oil_air_level_y) >= 300.0
    assert min(float(row.raw_oil_air_level_y) for row in numeric) <= 245.0
    assert all("SEQUENCE_SAME_FRAME_CANDIDATE" in row.flags for row in numeric)
    assert all(
        row.smoothed_oil_air_level_px_from_zero is None
        for row in rows
        if row.raw_oil_air_level_y is None
    )
