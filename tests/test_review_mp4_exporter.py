from __future__ import annotations

from types import SimpleNamespace

import cv2
import numpy as np
import pytest

from oil_tracker.adapters.storage.review_mp4_exporter import (
    ReviewMp4DestinationError,
    ReviewMp4EncodingError,
    ReviewMp4ExportCancelled,
    ReviewMp4Exporter,
)
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import SimpleCancellationToken
from oil_tracker.application.services.review_query import ReviewQueryModel
from oil_tracker.domain.enums import FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewBundle, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


def _write_source(path, *, width=160, height=120, fps=10.0, frames=20):
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    assert writer.isOpened()
    try:
        for index in range(frames):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :, 0] = index * 5
            writer.write(frame)
    finally:
        writer.release()


def _bundle(tmp_path, source, *, start=0.2, end=0.8, debug=False):
    recipe = InspectionRecipe.empty(160, 120, "snapshot")
    glass = InspectionRecipe.default_glass(160, 120, 1)
    glass.geometry.zero_line_y = 70.0
    recipe.glasses.append(glass)
    metadata = VideoMetadata(str(source), 160, 120, 10.0, 2.0, 20, "mp4v")
    session = AnalysisSession(
        input_video_path=str(source),
        video_metadata=metadata,
        analysis_start_sec=start,
        analysis_end_sec=end,
        sampling_fps=2.0,
    )
    samples = (
        ReviewTrackingSample(
            "run",
            glass.id,
            2,
            0.2,
            FillState.PARTIAL_VISIBLE,
            smoothed_oil_air_level_px_from_zero=10.0,
            overall_confidence=0.9,
            is_valid=True,
        ),
        ReviewTrackingSample(
            "run",
            glass.id,
            5,
            0.5,
            FillState.UNKNOWN_REVIEW,
            overall_confidence=0.2,
            is_valid=False,
            flags=("REVIEW_REQUIRED",),
        ),
    )
    bundle = ReviewBundle(
        root=tmp_path / "bundle",
        run_id="run",
        recipe=recipe,
        session=session,
        manifest={},
        source_video_path=str(source),
        source_video_candidates=(str(source),),
        source_metadata=metadata,
        analysis_start_sec=start,
        analysis_end_sec=end,
        compressor_start_sec=None,
        glasses=(ReviewGlass(glass.id, glass.name, ResultState.REVIEW_REQUIRED),),
        samples=samples,
        events=(),
        debug_trace_level="basic" if debug else "none",
        debug_record_count=1 if debug else 0,
    )
    bundle.root.mkdir()
    return bundle, glass


def test_general_export_is_reopenable_preserves_geometry_interval_and_overlay(tmp_path):
    source = tmp_path / "source.mp4"
    _write_source(source)
    bundle, glass = _bundle(tmp_path, source)
    result = ReviewMp4Exporter().export(
        bundle=bundle,
        query=ReviewQueryModel(bundle),
        source_video_path=source,
        glass_id=glass.id,
        destination=tmp_path / "annotated.mp4",
    )
    assert result.path.is_file()
    assert (result.width, result.height) == (160, 120)
    assert result.frame_count == 7
    assert result.duration_sec == pytest.approx(0.7)
    capture = cv2.VideoCapture(str(result.path))
    try:
        assert capture.isOpened()
        assert int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) == 160
        assert int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) == 120
        assert int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) == result.frame_count
        ok, frame = capture.read()
        assert ok and frame is not None
        assert np.count_nonzero(frame) > 0
        assert np.count_nonzero(frame[60, 45:115]) > 0
    finally:
        capture.release()
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []


class _RecordingQuery:
    def __init__(self, delegate):
        self.delegate = delegate
        self.timestamps = []
        self.overlays = []

    def overlay_at(self, glass_id, timestamp_sec):
        self.timestamps.append(float(timestamp_sec))
        overlay = self.delegate.overlay_at(glass_id, timestamp_sec)
        self.overlays.append(overlay)
        return overlay


class _FakeReader:
    instances = []

    def __init__(self, path, sequence=None):
        self.path = str(path)
        self.sequence = list(sequence or [(2, 0.25), (3, 0.35), (4, 0.45), (5, 0.55)])
        self.position = 0
        self.closed = False
        self.metadata = VideoMetadata(self.path, 160, 120, 10.0, 1.0, 10, "fake")
        self.__class__.instances.append(self)

    def read_at(self, _timestamp):
        self.position = 0
        return self._value()

    def read_next(self):
        self.position += 1
        if self.position >= len(self.sequence):
            raise EOFError
        return self._value()

    def _value(self):
        frame_index, timestamp = self.sequence[self.position]
        return np.zeros((120, 160, 3), dtype=np.uint8), frame_index, timestamp

    def close(self):
        self.closed = True


class _KnownLastFrameReader(_FakeReader):
    def __init__(self, path):
        super().__init__(path, sequence=[(2, 0.25), (3, 0.35), (4, 0.45)])
        self.metadata = VideoMetadata(self.path, 160, 120, 10.0, 0.5, 5, "fake")


class _FakeWriter:
    instances = []

    def __init__(self, path, _fps, _frame_size, *, fail_at=None):
        self.path = path
        self.path.write_bytes(b"temporary")
        self.frames = []
        self.closed = False
        self.fail_at = fail_at
        self.__class__.instances.append(self)

    def write(self, frame):
        if self.fail_at is not None and len(self.frames) == self.fail_at:
            raise RuntimeError("writer failed")
        self.frames.append(frame.copy())

    def close(self):
        self.closed = True


def _fake_exporter(*, reader_factory=_FakeReader, writer_factory=_FakeWriter, **kwargs):
    return ReviewMp4Exporter(
        reader_factory=reader_factory,
        writer_factory=writer_factory,
        encoded_validator=lambda _path, _width, _height: None,
        **kwargs,
    )


def test_export_queries_official_tracking_with_actual_decoded_timestamps_and_preserves_gaps(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.6)
    query = _RecordingQuery(ReviewQueryModel(bundle))
    result = _fake_exporter().export(
        bundle=bundle,
        query=query,
        source_video_path=source,
        glass_id=glass.id,
        destination=tmp_path / "sync.mp4",
    )
    assert query.timestamps == [0.25, 0.35, 0.45, 0.55]
    assert query.overlays[0].oil_boundary_y == pytest.approx(60.0)
    assert query.overlays[-1].sample.timestamp_sec == pytest.approx(0.5)
    assert query.overlays[-1].oil_boundary_y is None
    assert query.overlays[-1].foam_front_y is None
    assert result.frame_count == 4
    assert _FakeReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


def test_short_real_source_cannot_publish_incomplete_analysis_interval(tmp_path):
    source = tmp_path / "short.mp4"
    _write_source(source, fps=10.0, frames=6)
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.8)
    destination = tmp_path / "incomplete.mp4"
    with pytest.raises(ReviewMp4EncodingError, match="분석 종료"):
        ReviewMp4Exporter().export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
        )
    assert not destination.exists()
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []


def test_premature_eof_cannot_publish_and_releases_resources(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.8)
    destination = tmp_path / "eof.mp4"
    with pytest.raises(ReviewMp4EncodingError, match="분석 종료"):
        _fake_exporter().export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
        )
    assert not destination.exists()
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []
    assert _FakeReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


def test_known_source_last_frame_before_required_coverage_cannot_publish(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.8)
    destination = tmp_path / "last-frame.mp4"
    with pytest.raises(ReviewMp4EncodingError, match="분석 종료"):
        _fake_exporter(reader_factory=_KnownLastFrameReader).export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
        )
    assert not destination.exists()
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []
    assert _KnownLastFrameReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


def test_sparse_after_end_timestamp_cannot_claim_interval_coverage(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.8)
    destination = tmp_path / "sparse-boundary.mp4"

    def reader_factory(path):
        return _FakeReader(path, sequence=[(2, 0.25), (20, 2.00)])

    with pytest.raises(ReviewMp4EncodingError, match="decoded timeline"):
        _fake_exporter(reader_factory=reader_factory).export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
        )
    assert not destination.exists()
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []
    assert _FakeReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


def test_normal_adjacent_after_end_bracket_is_complete(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.8)

    def reader_factory(path):
        return _FakeReader(
            path,
            sequence=[(2, 0.25), (3, 0.35), (4, 0.45), (5, 0.55), (6, 0.65), (7, 0.75), (8, 0.85)],
        )

    result = _fake_exporter(reader_factory=reader_factory).export(
        bundle=bundle,
        query=ReviewQueryModel(bundle),
        source_video_path=source,
        glass_id=glass.id,
        destination=tmp_path / "adjacent-boundary.mp4",
    )
    assert result.frame_count == 6
    assert result.path.is_file()
    assert _FakeReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


def test_bounded_realistic_decoded_timestamp_jitter_is_accepted(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.8)

    def reader_factory(path):
        return _FakeReader(
            path,
            sequence=[(2, 0.248), (3, 0.352), (4, 0.449), (5, 0.556), (6, 0.651), (7, 0.748), (8, 0.853)],
        )

    result = _fake_exporter(reader_factory=reader_factory).export(
        bundle=bundle,
        query=ReviewQueryModel(bundle),
        source_video_path=source,
        glass_id=glass.id,
        destination=tmp_path / "jitter.mp4",
    )
    assert result.frame_count == 6
    assert result.path.is_file()


def test_materially_sparse_internal_decoded_gap_cannot_publish(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.8)
    destination = tmp_path / "sparse-internal.mp4"

    def reader_factory(path):
        return _FakeReader(path, sequence=[(2, 0.25), (3, 0.35), (6, 0.65), (7, 0.75), (8, 0.85)])

    with pytest.raises(ReviewMp4EncodingError, match="decoded timeline"):
        _fake_exporter(reader_factory=reader_factory).export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
        )
    assert not destination.exists()
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []
    assert _FakeReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


def test_analysis_end_between_adjacent_source_frames_is_complete(tmp_path):
    source = tmp_path / "source.mp4"
    _write_source(source, fps=10.0, frames=20)
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.85)
    result = ReviewMp4Exporter().export(
        bundle=bundle,
        query=ReviewQueryModel(bundle),
        source_video_path=source,
        glass_id=glass.id,
        destination=tmp_path / "between-frames.mp4",
    )
    assert result.path.is_file()
    assert result.frame_count == 7
    assert result.analysis_end_sec == pytest.approx(0.85)
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []


def test_incomplete_overwrite_preserves_existing_final_file(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.8)
    destination = tmp_path / "existing.mp4"
    destination.write_bytes(b"old-final")
    with pytest.raises(ReviewMp4EncodingError, match="분석 종료"):
        _fake_exporter().export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
            overwrite=True,
        )
    assert destination.read_bytes() == b"old-final"
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []
    assert _FakeReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


class _DebugRepository:
    instances = []

    def __init__(self, _bundle):
        self.closed = False
        self.record = SimpleNamespace(timestamp_sec=0.35, candidates=())
        self.summary = SimpleNamespace(record_id="debug-1", frame_index=3, timestamp_sec=0.35)
        self.__class__.instances.append(self)

    def summaries(self, glass_id):
        return (self.summary,)

    def load_record(self, record_id):
        assert record_id == "debug-1"
        return self.record

    def close(self):
        self.closed = True


class _DebugRenderer:
    def __init__(self):
        self.records = []

    def render_export(self, frame, _glass, record, _timestamp):
        self.records.append(record)
        return frame.copy()


def test_debug_export_uses_only_exact_stored_trace_frames(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.6, debug=True)
    debug_renderer = _DebugRenderer()
    result = _fake_exporter(
        debug_repository_factory=_DebugRepository,
        debug_renderer=debug_renderer,
    ).export(
        bundle=bundle,
        query=ReviewQueryModel(bundle),
        source_video_path=source,
        glass_id=glass.id,
        destination=tmp_path / "debug.mp4",
        include_debug=True,
    )
    assert [record is not None for record in debug_renderer.records] == [False, True, False, False]
    assert result.debug_frames == 1
    assert _DebugRepository.instances[-1].closed


def test_general_export_never_opens_or_renders_debug_trace(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.6, debug=True)
    debug_renderer = _DebugRenderer()
    before = len(_DebugRepository.instances)
    _fake_exporter(
        debug_repository_factory=_DebugRepository,
        debug_renderer=debug_renderer,
    ).export(
        bundle=bundle,
        query=ReviewQueryModel(bundle),
        source_video_path=source,
        glass_id=glass.id,
        destination=tmp_path / "general.mp4",
        include_debug=False,
    )
    assert len(_DebugRepository.instances) == before
    assert debug_renderer.records == []


def test_writer_failure_cleans_temp_and_releases_handles(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.6)

    def writer_factory(path, fps, frame_size):
        return _FakeWriter(path, fps, frame_size, fail_at=1)

    destination = tmp_path / "failed.mp4"
    with pytest.raises(RuntimeError, match="writer failed"):
        _fake_exporter(writer_factory=writer_factory).export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
        )
    assert not destination.exists()
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []
    assert _FakeReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


def test_cancellation_after_progress_does_not_publish_and_releases_handles(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.6)
    cancellation = SimpleCancellationToken()
    destination = tmp_path / "cancelled.mp4"

    def cancel_after_first(update):
        if update.processed_frames == 1:
            cancellation.cancel()

    with pytest.raises(ReviewMp4ExportCancelled):
        _fake_exporter().export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
            cancellation=cancellation,
            progress=cancel_after_first,
        )
    assert not destination.exists()
    assert list(tmp_path.glob(".*.tmp-*.mp4")) == []
    assert _FakeReader.instances[-1].closed
    assert _FakeWriter.instances[-1].closed


def test_existing_destination_requires_explicit_overwrite_and_source_cannot_be_replaced(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.6)
    destination = tmp_path / "existing.mp4"
    destination.write_bytes(b"existing")
    exporter = _fake_exporter()
    with pytest.raises(ReviewMp4DestinationError, match="덮어쓸 수 없습니다"):
        exporter.export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=destination,
        )
    assert destination.read_bytes() == b"existing"
    with pytest.raises(ReviewMp4DestinationError, match="원본 source MP4"):
        exporter.export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=source,
            overwrite=True,
        )
    assert source.read_bytes() == b"source"


def test_official_bundle_destination_is_rejected_without_mutation(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source")
    bundle, glass = _bundle(tmp_path, source, start=0.2, end=0.6)
    sentinel = bundle.root / "analysis_manifest.json"
    sentinel.write_text("official", encoding="utf-8")
    nested = bundle.root / "derivatives"
    with pytest.raises(ReviewMp4DestinationError, match="공식 결과 bundle 내부"):
        _fake_exporter().export(
            bundle=bundle,
            query=ReviewQueryModel(bundle),
            source_video_path=source,
            glass_id=glass.id,
            destination=nested / "annotated.mp4",
        )
    assert sentinel.read_text(encoding="utf-8") == "official"
    assert not nested.exists()
