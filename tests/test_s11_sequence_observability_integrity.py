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


def test_sample3_r16_sequence_preserves_owner_barrier_and_drain_reentry(
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
        run_name="S11 R16 owner lifecycle observability integrity",
        resolution_confirmed=True,
    )
    result = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector(),
        _LocalSequenceValidator(),
    ).run(recipe, session)
    rows = result.glass_results[0].samples

    assert len(rows) == 151
    onset = [sample for sample in rows if sample.timestamp_sec < 32.0]
    foreign_branch = [
        sample
        for sample in rows
        if 34.0 <= sample.timestamp_sec < 39.0
    ]
    completed_fill = [
        sample
        for sample in rows
        if 39.0 <= sample.timestamp_sec < 50.0
    ]
    full_gap = [
        sample
        for sample in rows
        if 50.0 <= sample.timestamp_sec < 64.0
    ]
    assert len(onset) == 4
    assert all(sample.raw_oil_air_level_y is not None for sample in onset)
    assert all(
        abs(float(sample.raw_oil_air_level_y) - 316.0) <= 26.0
        for sample in onset
    )
    # R14's aggregate count and Y243 minimum implicitly accepted a reconciled
    # foreign branch. R16 instead preserves the explicit fill owner and
    # abstains while only opposite-direction/high-conflict rows are available.
    assert foreign_branch
    assert not any(_numeric(sample) for sample in foreign_branch)
    # Direct review shows the free interface rising into the upper entrance and
    # disappearing. The later high-cap texture is internal full/turbulent
    # material, so R14 must not reacquire it as a numeric interface.
    assert not any(_numeric(sample) for sample in completed_fill)
    assert not any(_numeric(sample) for sample in full_gap)
    assert all(
        sample.fill_state is FillState.UNKNOWN_REVIEW for sample in full_gap
    )
    barrier = [
        sample
        for sample in rows
        if 37.0 <= sample.timestamp_sec < 64.0
    ]
    assert barrier
    assert all("R16_MATERIAL_PHASE_BARRIER" in sample.flags for sample in barrier)
    early_foam = [
        sample
        for sample in rows
        if sample.timestamp_sec < 39.0 and sample.raw_foam_front_y is not None
    ]
    # Strong onset confirmation removes isolated positives while retaining a
    # multi-frame dynamic Foam observation during inflow.
    assert len(early_foam) >= 2
    assert min(sample.timestamp_sec for sample in early_foam) <= 30.60
    assert not any(
        sample.raw_foam_front_y is not None
        for sample in rows
        if sample.timestamp_sec >= 85.0
    )

    safe_drain_points = (
        (95.0283, 345.0),
        (96.0293, 359.0),
        (96.5298, 359.0),
        (97.0303, 368.0),
        (97.5308, 368.5),
        (100.0333, 368.0),
        (102.5358, 335.0),
    )
    for timestamp, expected_y in safe_drain_points:
        representative = min(
            rows,
            key=lambda sample: abs(sample.timestamp_sec - timestamp),
        )
        assert abs(representative.timestamp_sec - timestamp) <= 0.26
        assert representative.raw_oil_air_level_y is not None
        assert (
            abs(float(representative.raw_oil_air_level_y) - expected_y)
            <= 0.6
        )
        assert "SEQUENCE_SAME_FRAME_CANDIDATE" in representative.flags

    owner_absence = [
        sample
        for sample in rows
        if 90.0 <= sample.timestamp_sec < 95.0
    ]
    material_conflict = [
        sample
        for sample in rows
        if 98.0 <= sample.timestamp_sec < 100.0
        or 100.5 <= sample.timestamp_sec < 102.5
    ]
    assert owner_absence and material_conflict
    assert not any(_numeric(sample) for sample in owner_absence)
    assert not any(_numeric(sample) for sample in material_conflict)
    lost_owner = min(
        rows,
        key=lambda sample: abs(sample.timestamp_sec - 95.5288),
    )
    assert abs(lost_owner.timestamp_sec - 95.5288) <= 0.26
    assert not _numeric(lost_owner)

    numeric = [sample for sample in rows if _numeric(sample)]
    assert all(
        "SEQUENCE_SAME_FRAME_CANDIDATE" in sample.flags
        for sample in numeric
    )

    for timestamp in (40.04, 45.045, 50.05, 55.055):
        representative = min(
            rows,
            key=lambda sample: abs(sample.timestamp_sec - timestamp),
        )
        assert not _numeric(representative)
