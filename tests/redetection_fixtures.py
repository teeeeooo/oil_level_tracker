from __future__ import annotations

from pathlib import Path

from oil_tracker.domain.enums import FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import TrackingSample
from oil_tracker.domain.review import ReviewBundle, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


def make_bundle(tmp_path: Path, *, fps: float = 2.0, duration: float = 6.0) -> ReviewBundle:
    recipe = InspectionRecipe.empty(320, 240, "fixture")
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "glass-1"
    glass.name = "Glass 1"
    glass.mm_per_pixel = 0.25
    recipe.glasses = [glass]
    source = tmp_path / "영상.mp4"
    source.touch(exist_ok=True)
    metadata = VideoMetadata(str(source), 320, 240, 30.0, duration, int(duration * 30))
    session = AnalysisSession(
        input_video_path=str(source),
        video_metadata=metadata,
        analysis_start_sec=1.0,
        analysis_end_sec=duration - 1.0,
        compressor_start_sec=1.5,
        sampling_fps=fps,
    )
    samples = []
    index = 0
    timestamp = session.analysis_start_sec
    while timestamp <= session.analysis_end_sec + 1e-9:
        samples.append(make_official_sample(index, round(timestamp, 9)))
        index += 1
        timestamp += 1.0 / fps
    return ReviewBundle(
        root=tmp_path / "bundle",
        run_id="official",
        recipe=recipe,
        session=session,
        manifest={},
        source_video_path=str(source),
        source_video_candidates=(),
        source_metadata=metadata,
        analysis_start_sec=session.analysis_start_sec,
        analysis_end_sec=session.analysis_end_sec,
        compressor_start_sec=session.compressor_start_sec,
        glasses=(ReviewGlass("glass-1", "Glass 1", ResultState.PASS),),
        samples=tuple(samples),
        events=(),
    )


def make_official_sample(index: int, timestamp: float, **overrides) -> ReviewTrackingSample:
    values = dict(
        run_id="official",
        glass_id="glass-1",
        frame_index=index,
        timestamp_sec=timestamp,
        fill_state=FillState.PARTIAL_VISIBLE,
        raw_oil_air_level_y=120.0,
        raw_oil_air_level_px_from_zero=12.0,
        raw_oil_air_level_mm_from_zero=3.0,
        smoothed_oil_air_level_px_from_zero=13.0,
        smoothed_oil_air_level_mm_from_zero=3.25,
        oil_air_confidence=0.8,
        raw_foam_front_y=110.0,
        raw_foam_front_px_from_zero=22.0,
        raw_foam_front_mm_from_zero=5.5,
        smoothed_foam_front_px_from_zero=23.0,
        smoothed_foam_front_mm_from_zero=5.75,
        foam_confidence=0.6,
        visibility_confidence=0.9,
        overall_confidence=0.8,
        is_valid=True,
        flags=(),
        input_order=index,
    )
    values.update(overrides)
    return ReviewTrackingSample(**values)


def make_tracking(index: int, timestamp: float, **overrides) -> TrackingSample:
    values = dict(
        run_id="rerun",
        glass_id="glass-1",
        frame_index=index,
        timestamp_sec=timestamp,
        fill_state=FillState.PARTIAL_VISIBLE,
        raw_oil_air_level_y=118.0,
        raw_oil_air_level_px_from_zero=14.0,
        raw_oil_air_level_mm_from_zero=3.5,
        smoothed_oil_air_level_px_from_zero=15.0,
        smoothed_oil_air_level_mm_from_zero=3.75,
        oil_air_confidence=0.85,
        raw_foam_front_y=108.0,
        raw_foam_front_px_from_zero=24.0,
        raw_foam_front_mm_from_zero=6.0,
        smoothed_foam_front_px_from_zero=25.0,
        smoothed_foam_front_mm_from_zero=6.25,
        foam_confidence=0.65,
        visibility_confidence=0.9,
        overall_confidence=0.9,
        is_valid=True,
        flags=[],
    )
    values.update(overrides)
    return TrackingSample(**values)
