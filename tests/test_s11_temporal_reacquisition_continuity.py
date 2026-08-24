from __future__ import annotations

"""Corpus-level continuity contract for the current observation resolver.

The removed test asserted private counters from the retired current-frame
temporal tracker. Continuity is owned by the completed-window observation
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


def test_sample3_r17_onset_owner_continuity_without_coordinate_carry(
    tmp_path,
) -> None:
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
        run_name="S11 R17 onset owner continuity regression",
        resolution_confirmed=True,
    )
    result = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector(),
        _DetectorRegressionValidator(),
    ).run(recipe, session)
    rows = result.glass_results[0].samples
    numeric = [row for row in rows if row.raw_oil_air_level_y is not None]
    onset = [row for row in rows if row.timestamp_sec < 32.0]
    checked_truth_handoff = min(
        rows,
        key=lambda row: abs(row.timestamp_sec - 34.5345),
    )
    post_truth_gap = [
        row for row in rows if 35.0 <= row.timestamp_sec < 37.0
    ]

    assert len(rows) >= 20
    assert len(onset) == 4
    assert all(row.raw_oil_air_level_y is not None for row in onset)
    assert all(
        abs(float(row.raw_oil_air_level_y) - 316.0) <= 26.0
        for row in onset
    )
    # The checked Y243 annotation is product truth. A strong current anchor may
    # own that frame despite stale track direction, but it must not mutate the
    # fill phase or carry coordinates into the following gap.
    assert checked_truth_handoff.raw_oil_air_level_y is not None
    assert abs(float(checked_truth_handoff.raw_oil_air_level_y) - 243.0) <= 2.0
    assert all(row.raw_oil_air_level_y is None for row in post_truth_gap)
    assert all(
        row.smoothed_oil_air_level_px_from_zero is None
        for row in post_truth_gap
    )
    assert all("SEQUENCE_SAME_FRAME_CANDIDATE" in row.flags for row in numeric)
    assert all(
        row.smoothed_oil_air_level_px_from_zero is None
        for row in rows
        if row.raw_oil_air_level_y is None
    )
