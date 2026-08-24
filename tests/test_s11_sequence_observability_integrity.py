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


def test_sample3_r16_sequence_preserves_owner_barrier_and_drain_handoffs(
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
    checked_truth_handoff = min(
        rows,
        key=lambda sample: abs(sample.timestamp_sec - 34.5345),
    )
    post_truth_gap = [
        sample
        for sample in rows
        if 35.0 <= sample.timestamp_sec < 37.0
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
    # Checked-in user truth remains authoritative even when an accumulated
    # track direction disagrees. A bounded current material anchor can own this
    # frame without mutating the fill phase or reopening the later barrier.
    assert checked_truth_handoff.raw_oil_air_level_y is not None
    assert abs(float(checked_truth_handoff.raw_oil_air_level_y) - 243.0) <= 2.0
    assert not any(_numeric(sample) for sample in post_truth_gap)
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
        if 37.0 <= sample.timestamp_sec < 81.0
    ]
    assert barrier
    assert not any(_numeric(sample) for sample in barrier)
    assert all("R17_MATERIAL_PHASE_BARRIER" in sample.flags for sample in barrier)
    early_foam = [
        sample
        for sample in rows
        if sample.timestamp_sec < 39.0 and sample.raw_foam_front_y is not None
    ]
    # Strong onset confirmation removes isolated positives while retaining a
    # multi-frame dynamic Foam observation during inflow.
    assert len(early_foam) >= 2
    assert min(sample.timestamp_sec for sample in early_foam) <= 30.60
    reviewed_second_episode = [
        sample
        for sample in early_foam
        if 37.0 <= sample.timestamp_sec <= 38.1
    ]
    assert len(reviewed_second_episode) >= 2
    assert not any(
        sample.raw_foam_front_y is not None
        for sample in rows
        if sample.timestamp_sec >= 85.0
    )

    # Symmetric split handling keeps the full-cap barrier closed until a clean
    # downward interface becomes observable.  These reviewed witnesses span
    # the release and two physical-ID handoffs; their public coordinates all
    # come from the selected frame, never from a retained owner coordinate.
    reviewed_drain_witnesses = (
        (81.0143, 233.0, "R17_TRACKLET_WITNESS"),
        (83.5168, 239.0, "R17_TRACKLET_CONFIRMED"),
        (85.5188, 253.0, "R17_TRACKLET_CONFIRMED"),
        (91.5248, 320.0, "R17_TRACKLET_WITNESS"),
        (94.0273, 336.0, "R17_TRACKLET_CONFIRMED"),
        (95.0283, 345.0, "R17_TRACKLET_CONTINUING"),
        (96.5298, 342.0, "R17_TRACKLET_CONTINUING"),
    )
    for timestamp, expected_y, lifecycle_flag in reviewed_drain_witnesses:
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
        assert lifecycle_flag in representative.flags
        assert "SEQUENCE_SAME_FRAME_CANDIDATE" in representative.flags

    reviewed_drain = [
        sample
        for sample in rows
        if 81.0 <= sample.timestamp_sec < 97.0 and _numeric(sample)
    ]
    assert reviewed_drain
    assert float(reviewed_drain[-1].raw_oil_air_level_y) - float(
        reviewed_drain[0].raw_oil_air_level_y
    ) >= 105.0
    assert all(
        float(following.raw_oil_air_level_y)
        >= float(prior.raw_oil_air_level_y) - 3.1
        for prior, following in zip(reviewed_drain, reviewed_drain[1:])
    )
    assert max(
        following.timestamp_sec - prior.timestamp_sec
        for prior, following in zip(reviewed_drain, reviewed_drain[1:])
    ) <= 3.51

    # The established phase may transfer to the independently confirmed
    # strong-motion drain row even when its historical texture average is
    # stale.  This is not a coordinate carry: every value remains a selected
    # candidate from that frame and stays on the reviewed descending branch.
    reviewed_successor_witnesses = (
        (97.0303, 344.0, "R17_TRACKLET_WITNESS"),
        (98.0313, 353.0, "R17_TRACKLET_CONFIRMED"),
        (98.5318, 359.0, "R17_TRACKLET_CONTINUING"),
        (100.0333, 368.0, "R17_TRACKLET_CONTINUING"),
        (100.5338, 361.0, "R17_TRACKLET_CONTINUING"),
        (101.5348, 361.0, "R17_TRACKLET_CONTINUING"),
    )
    for timestamp, expected_y, lifecycle_flag in reviewed_successor_witnesses:
        representative = min(
            rows,
            key=lambda sample: abs(sample.timestamp_sec - timestamp),
        )
        assert abs(representative.timestamp_sec - timestamp) <= 0.26
        assert representative.raw_oil_air_level_y is not None
        assert abs(float(representative.raw_oil_air_level_y) - expected_y) <= 0.6
        assert lifecycle_flag in representative.flags
        assert "SEQUENCE_SAME_FRAME_CANDIDATE" in representative.flags

    late_drain = [
        sample
        for sample in rows
        if sample.timestamp_sec >= 90.0 and _numeric(sample)
    ]
    assert len(late_drain) >= 10
    assert all(float(sample.raw_oil_air_level_y) >= 320.0 for sample in late_drain)

    unsafe_reentry_window = [
        sample
        for sample in rows
        if abs(sample.timestamp_sec - 96.0293) <= 0.26
        or sample.timestamp_sec >= 102.0
    ]
    assert unsafe_reentry_window
    assert not any(_numeric(sample) for sample in unsafe_reentry_window)
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
