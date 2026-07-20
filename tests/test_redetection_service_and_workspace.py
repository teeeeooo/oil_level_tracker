from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from oil_tracker.adapters.storage.redetection_workspace import (
    RedetectionWorkspace,
    RedetectionWorkspaceError,
)
from oil_tracker.application.services.detection_processing import (
    learn_static_artifacts,
    static_artifact_sample_timestamps,
    tracking_sample_from_detection,
)
from oil_tracker.application.services.redetection_request import build_redetection_request
from oil_tracker.application.services.redetection_service import (
    PartialRedetectionService,
    RedetectionCancelled,
    RedetectionError,
)
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, ResultState
from oil_tracker.domain.recipe import DetectorSettings, InspectionRecipe
from oil_tracker.domain.redetection import RedetectionMode, RedetectionPolicy
from oil_tracker.domain.review import ReviewBundle, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


class FakeReader:
    instances = []

    def __init__(self, path: str, *, fail_times=()) -> None:
        self.path = path
        self.metadata = VideoMetadata(path, 320, 240, 30.0, 6.0, 180)
        self.fail_times = set(fail_times)
        self.reads = []
        self.closed = False
        type(self).instances.append(self)

    def read_at(self, timestamp: float):
        self.reads.append(float(timestamp))
        if round(float(timestamp), 6) in self.fail_times:
            raise OSError("decode failed")
        frame_index = int(round(float(timestamp) * 30))
        return np.full((240, 320, 3), frame_index % 255, dtype=np.uint8), frame_index, float(timestamp) + 0.001

    def close(self):
        self.closed = True


class FakeDetector:
    instances = []

    def __init__(self, *, fail_calls=()) -> None:
        self.fail_calls = set(fail_calls)
        self.reset_count = 0
        self.detect_count = 0
        self.learned = []
        self.last_y = None
        type(self).instances.append(self)

    def reset(self, glass_id=None):
        self.reset_count += 1
        self.last_y = None

    def learn_static_artifact(self, frames, glass):
        self.learned.append((len(frames), glass.id))

    def detect(self, frame, glass, frame_index, time_sec, debug=False):
        self.detect_count += 1
        if self.detect_count in self.fail_calls:
            raise RuntimeError("detector failed")
        raw_y = 120.0 - self.detect_count
        smooth_y = raw_y if self.last_y is None else (raw_y + self.last_y) / 2.0
        self.last_y = smooth_y
        zero = glass.geometry.zero_line_y
        candidate = BoundaryCandidate(
            source="hough",
            kind=BoundaryKind.OIL_AIR,
            y=raw_y,
            features={"edge_strength": 0.8},
            penalties={"glare": 0.1},
            feature_score=0.8,
            penalty=0.1,
            final_score=0.7,
            selected=True,
        )
        detection = PhaseDetection(
            glass_id=glass.id,
            frame_index=frame_index,
            time_sec=time_sec,
            fill_state=FillState.VISIBLE_INTERFACE,
            oil_air_level_y=smooth_y,
            oil_air_level_px_from_zero=zero - smooth_y,
            oil_air_level_mm_from_zero=(zero - smooth_y) * (glass.mm_per_pixel or 1.0),
            foam_front_y=smooth_y - 10.0,
            foam_front_px_from_zero=zero - (smooth_y - 10.0),
            foam_front_mm_from_zero=(zero - (smooth_y - 10.0)) * (glass.mm_per_pixel or 1.0),
            oil_air_confidence=0.8,
            foam_confidence=0.6,
            visibility_confidence=0.9,
            overall_confidence=0.8,
            raw_oil_air_level_y=raw_y,
            raw_foam_front_y=raw_y - 10.0,
            smoothed_oil_air_level_y=smooth_y,
            smoothed_foam_front_y=smooth_y - 10.0,
            candidates=[candidate],
            flags=[],
            debug_metrics={"history": self.detect_count},
        )
        artifacts = SimpleNamespace(
            images={
                "overlay": frame,
                "original_roi": frame[60:180, 80:240],
            },
            state={"detect_count": self.detect_count},
        )
        assert debug is True
        return detection, artifacts


class Cancellation:
    def __init__(self, cancelled=False):
        self.cancelled = cancelled


def _bundle(tmp_path: Path, *, fps: float = 2.0) -> ReviewBundle:
    recipe = InspectionRecipe.empty(320, 240, "fixture")
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "glass-1"
    glass.mm_per_pixel = 0.25
    recipe.glasses = [glass]
    source = tmp_path / "영상.mp4"
    source.touch()
    metadata = VideoMetadata(str(source), 320, 240, 30.0, 6.0, 180)
    session = AnalysisSession(
        input_video_path=str(source),
        video_metadata=metadata,
        analysis_start_sec=1.0,
        analysis_end_sec=5.0,
        compressor_start_sec=1.5,
        sampling_fps=fps,
    )
    samples = []
    index = 0
    timestamp = 1.0
    while timestamp <= 5.0 + 1e-9:
        samples.append(
            ReviewTrackingSample(
                run_id="official",
                glass_id="glass-1",
                frame_index=index,
                timestamp_sec=round(timestamp, 9),
                fill_state=FillState.VISIBLE_INTERFACE,
                raw_oil_air_level_y=119.0,
                raw_oil_air_level_px_from_zero=13.0,
                raw_oil_air_level_mm_from_zero=3.25,
                smoothed_oil_air_level_px_from_zero=13.0,
                smoothed_oil_air_level_mm_from_zero=3.25,
                oil_air_confidence=0.8,
                raw_foam_front_y=109.0,
                raw_foam_front_px_from_zero=23.0,
                raw_foam_front_mm_from_zero=5.75,
                smoothed_foam_front_px_from_zero=23.0,
                smoothed_foam_front_mm_from_zero=5.75,
                foam_confidence=0.6,
                visibility_confidence=0.9,
                overall_confidence=0.8,
                is_valid=True,
                flags=(),
                input_order=index,
            )
        )
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
        analysis_start_sec=1.0,
        analysis_end_sec=5.0,
        compressor_start_sec=1.5,
        glasses=(ReviewGlass("glass-1", "Glass 1", ResultState.PASS),),
        samples=tuple(samples),
        events=(),
    )


def _request(bundle, mode, generation=1, **kwargs):
    return build_redetection_request(
        bundle,
        bundle.source_video_path,
        "glass-1",
        3.0,
        mode,
        bundle.recipe.glasses[0].detector_settings,
        generation,
        **kwargs,
    )


def _service(detector_factory=FakeDetector, reader_factory=FakeReader, policy=None):
    return PartialRedetectionService(
        reader_factory,
        detector_factory,
        RedetectionWorkspace.create,
        policy=policy,
    )


def test_static_artifact_policy_is_start_middle_end_and_available_only():
    assert static_artifact_sample_timestamps([1, 2, 3, 4, 5]) == (1.0, 3.0, 5.0)
    reader = FakeReader("x", fail_times={3.0})
    detector = FakeDetector()
    recipe = InspectionRecipe.empty(320, 240)
    glass = InspectionRecipe.default_glass(320, 240)
    decoded = learn_static_artifacts(reader, detector, [glass], [1, 2, 3, 4, 5])
    assert decoded == (1.0, 5.0)
    assert detector.learned == [(2, glass.id)]


def test_tracking_conversion_matches_official_raw_smoothed_mm_and_validity():
    recipe = InspectionRecipe.empty(320, 240)
    glass = InspectionRecipe.default_glass(320, 240)
    glass.mm_per_pixel = 0.25
    detector = FakeDetector()
    detector.reset()
    detection, _ = detector.detect(np.zeros((240, 320, 3), np.uint8), glass, 3, 1.0, debug=True)
    sample = tracking_sample_from_detection("run", glass, detection)
    assert sample.raw_oil_air_level_px_from_zero == pytest.approx(glass.geometry.zero_line_y - detection.raw_oil_air_level_y)
    assert sample.raw_oil_air_level_mm_from_zero == pytest.approx(sample.raw_oil_air_level_px_from_zero * 0.25)
    assert sample.smoothed_oil_air_level_px_from_zero == detection.oil_air_level_px_from_zero
    assert sample.is_valid


def test_tracking_conversion_allows_explicit_full_state_with_confidence():
    recipe = InspectionRecipe.empty(320, 240)
    glass = InspectionRecipe.default_glass(320, 240)
    detection = PhaseDetection(
        glass.id,
        1,
        1.0,
        FillState.FULL_NO_INTERFACE,
        overall_confidence=0.9,
    )
    assert tracking_sample_from_detection("run", glass, detection).is_valid
    detection.overall_confidence = 0.1
    assert not tracking_sample_from_detection("run", glass, detection).is_valid


def test_current_frame_uses_fresh_detector_one_detection_and_lazy_workspace(tmp_path):
    FakeReader.instances.clear()
    FakeDetector.instances.clear()
    bundle = _bundle(tmp_path)
    service = _service()
    output = service.run(_request(bundle, RedetectionMode.CURRENT), bundle)
    try:
        detector = FakeDetector.instances[-1]
        reader = FakeReader.instances[-1]
        assert detector.reset_count == 1
        assert detector.detect_count == 1
        assert detector.learned == [(3, "glass-1")]
        assert len(output.result.samples) == 1
        assert output.result.samples[0].actual_timestamp_sec == pytest.approx(3.001)
        assert output.result.limitation_message.startswith("현재 장면만 독립적으로")
        assert reader.closed
        repository = output.workspace.repository
        record = repository.load_record(output.result.samples[0].debug_record_id)
        assert record.candidates[0]["selected"] is True
        assert repository.load_image(record, "overlay").shape == (240, 320, 3)
        assert repository.record_cache_size == service.policy.record_cache_size
    finally:
        root = Path(output.result.workspace_root)
        output.workspace.cleanup()
        assert not root.exists()


def test_each_run_gets_new_detector_and_previous_state_does_not_leak(tmp_path):
    FakeDetector.instances.clear()
    bundle = _bundle(tmp_path)
    service = _service()
    first = service.run(_request(bundle, RedetectionMode.CURRENT, 1), bundle)
    first_y = first.result.samples[0].tracking_sample.raw_oil_air_level_y
    first.workspace.cleanup()
    second = service.run(_request(bundle, RedetectionMode.CURRENT, 2), bundle)
    try:
        assert len(FakeDetector.instances) == 2
        assert first_y == second.result.samples[0].tracking_sample.raw_oil_air_level_y
        assert all(instance.reset_count == 1 for instance in FakeDetector.instances)
    finally:
        second.workspace.cleanup()


def test_short_range_warmup_updates_state_but_is_not_returned(tmp_path):
    bundle = _bundle(tmp_path, fps=2.0)
    service = _service()
    output = service.run(
        _request(bundle, RedetectionMode.SHORT, before_sec=0.5, after_sec=0.5),
        bundle,
    )
    try:
        detector = FakeDetector.instances[-1]
        assert detector.detect_count == 6  # 2 sec warm-up + 1 sec visible at 2 fps
        assert len(output.result.samples) == 3
        assert all(not sample.warmup for sample in output.result.samples)
        assert output.result.summary.comparison_sample_count >= 3
        assert "구간 참고 결과" in output.result.rerun_judgment_note
        assert output.result.summary.rerun_judgment is None
    finally:
        output.workspace.cleanup()


def test_full_range_detector_calls_match_schedule_and_recalculates_judgment(tmp_path):
    bundle = _bundle(tmp_path, fps=2.0)
    service = _service()
    output = service.run(_request(bundle, RedetectionMode.FULL), bundle)
    try:
        detector = FakeDetector.instances[-1]
        assert detector.detect_count == 9
        assert len(output.result.samples) == 9
        assert output.result.summary.rerun_judgment is not None
        assert output.result.rerun_valid_coverage_ratio == pytest.approx(1.0)
        assert output.result.rerun_events
    finally:
        output.workspace.cleanup()


def test_interval_sample_failure_continues_and_is_streamed(tmp_path):
    bundle = _bundle(tmp_path, fps=2.0)
    service = _service(lambda: FakeDetector(fail_calls={5}))
    output = service.run(_request(bundle, RedetectionMode.FULL), bundle)
    try:
        failures = [sample for sample in output.result.samples if not sample.succeeded]
        assert len(failures) == 1
        assert "detector failed" in failures[0].error_message
        assert len(output.result.samples) == 9
    finally:
        output.workspace.cleanup()


def test_current_detector_failure_fails_and_cleans_workspace(tmp_path, monkeypatch):
    bundle = _bundle(tmp_path)
    created = []

    def workspace_factory(recipe, policy):
        workspace = RedetectionWorkspace.create(recipe, policy=policy, temporary_parent=tmp_path)
        created.append(workspace)
        return workspace

    service = PartialRedetectionService(FakeReader, lambda: FakeDetector(fail_calls={1}), workspace_factory)
    with pytest.raises(RedetectionError, match="현재 장면"):
        service.run(_request(bundle, RedetectionMode.CURRENT), bundle)
    assert created and not created[0].root.exists()


def test_workspace_write_failure_is_fatal_not_sample_failure(tmp_path):
    bundle = _bundle(tmp_path)

    class BrokenWorkspace:
        run_id = "broken"
        root = tmp_path / "broken"
        repository = None

        def write_detection(self, *args):
            raise RedetectionWorkspaceError("artifact write failed")

        def append_sample(self, sample):
            raise AssertionError("must not append after artifact failure")

        def cleanup(self):
            self.cleaned = True

    workspace = BrokenWorkspace()
    service = PartialRedetectionService(FakeReader, FakeDetector, lambda recipe, policy: workspace)
    with pytest.raises(RedetectionWorkspaceError, match="artifact write failed"):
        service.run(_request(bundle, RedetectionMode.CURRENT), bundle)
    assert workspace.cleaned


def test_cancellation_before_run_creates_no_reader_or_detector(tmp_path):
    bundle = _bundle(tmp_path)
    FakeReader.instances.clear()
    FakeDetector.instances.clear()
    with pytest.raises(RedetectionCancelled):
        _service().run(
            _request(bundle, RedetectionMode.CURRENT),
            bundle,
            cancellation=Cancellation(True),
        )
    assert not FakeReader.instances
    assert not FakeDetector.instances


def test_source_resolution_mismatch_cleans_reader_and_workspace(tmp_path):
    bundle = _bundle(tmp_path)
    created = []

    class WrongReader(FakeReader):
        def __init__(self, path):
            super().__init__(path)
            self.metadata.width = 640

    def workspace_factory(recipe, policy):
        workspace = RedetectionWorkspace.create(recipe, policy=policy, temporary_parent=tmp_path)
        created.append(workspace)
        return workspace

    service = PartialRedetectionService(WrongReader, FakeDetector, workspace_factory)
    with pytest.raises(RedetectionError, match="해상도"):
        service.run(_request(bundle, RedetectionMode.CURRENT), bundle)
    assert WrongReader.instances[-1].closed
    assert not created[0].root.exists()


def test_workspace_unique_streaming_index_and_official_bundle_unchanged(tmp_path):
    bundle = _bundle(tmp_path)
    bundle.root.mkdir()
    sentinel = bundle.root / "tracking_data.csv"
    sentinel.write_text("official", encoding="utf-8")
    service = _service()
    first = service.run(_request(bundle, RedetectionMode.CURRENT, 1), bundle)
    second = service.run(_request(bundle, RedetectionMode.CURRENT, 2), bundle)
    try:
        assert first.workspace.root != second.workspace.root
        assert first.workspace.sample_path.read_text(encoding="utf-8").count("\n") == 1
        assert first.workspace.index_path.is_file()
        assert sentinel.read_text(encoding="utf-8") == "official"
        assert not any(path.name.startswith("redetection") for path in bundle.root.iterdir())
    finally:
        first.workspace.cleanup()
        second.workspace.cleanup()
