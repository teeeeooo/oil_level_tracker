from __future__ import annotations

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import (
    RecipeValidationService,
)
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.session import AnalysisSession
from tests.s11_local_corpus import require_s11_local_corpus


class _LocalSequenceValidator:
    def __init__(self) -> None:
        self.inner = RecipeValidationService()

    def validate(self, recipe, session, **_kwargs):
        return self.inner.validate(
            recipe,
            session,
            require_run_confirmation=False,
        )


def _numeric(sample) -> bool:
    return bool(
        sample.raw_oil_air_level_y is not None
        or sample.smoothed_oil_air_level_px_from_zero is not None
    )


def test_sample3_sequence_retains_rise_and_censors_full_like_caps_and_false_foam(
    tmp_path,
) -> None:
    root = require_s11_local_corpus()
    video_path = root / "sample" / "sample3.mp4"
    recipe = JsonRecipeRepository().load(root / "sample" / "sample3.oilrecipe")
    reader = OpenCvVideoReader(video_path)
    try:
        metadata = reader.metadata
    finally:
        reader.close()
    session = AnalysisSession(
        input_video_path=str(video_path),
        video_metadata=metadata,
        analysis_start_sec=30.03,
        analysis_end_sec=105.0,
        compressor_start_sec=30.03,
        sampling_fps=2.0,
        output_directory=str(tmp_path),
        run_name="S11 R4 sequence observability integrity",
        resolution_confirmed=True,
    )
    result = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector(),
        _LocalSequenceValidator(),
    ).run(recipe, session)
    rows = result.glass_results[0].samples

    assert len(rows) == 151
    rising = [sample for sample in rows if sample.timestamp_sec < 39.0]
    full_like = [
        sample
        for sample in rows
        if 39.0 <= sample.timestamp_sec < 66.0
    ]
    rising_y = [
        float(sample.raw_oil_air_level_y)
        for sample in rising
        if sample.raw_oil_air_level_y is not None
    ]

    assert sum(_numeric(sample) for sample in rising) >= 5
    assert min(abs(y - 316.0) for y in rising_y) <= 2.0
    assert min(abs(y - 243.0) for y in rising_y) <= 3.0
    # Direct source review retains the real upper meniscus through 38.04 s.
    # The cap-only/full interval begins after that observation and must not
    # regain a numeric coordinate from the dark Glass rim.
    assert not any(_numeric(sample) for sample in full_like)
    assert not any(
        sample.fill_state is FillState.DRAINING_VISIBLE
        for sample in full_like
        if sample.timestamp_sec >= 42.0
    )
    early_foam = [
        sample
        for sample in rows
        if sample.timestamp_sec < 39.0 and sample.raw_foam_front_y is not None
    ]
    # Strong onset confirmation deliberately removes isolated positives, but
    # the true inflow Foam must remain observable near both ends of the episode.
    assert len(early_foam) >= 4
    assert min(sample.timestamp_sec for sample in early_foam) <= 30.60
    assert max(sample.timestamp_sec for sample in early_foam) >= 37.50
    assert not any(
        sample.raw_foam_front_y is not None
        for sample in rows
        if sample.timestamp_sec >= 85.0
    )

    for timestamp in (40.04, 45.045, 50.05, 55.055):
        representative = min(
            rows,
            key=lambda sample: abs(sample.timestamp_sec - timestamp),
        )
        assert not _numeric(representative)
