from copy import deepcopy
import json
from types import SimpleNamespace as NS

import cv2
import numpy as np
import pytest

from oil_tracker.adapters.reporting.source_sequence_renderer import (
    MAX_SEQUENCE_FRAMES, TILE_SIZE, SourceSequenceRenderer, sequence_times, source_tile,
)
from oil_tracker.application.ports.progress import AnalysisCancelled
from oil_tracker.application.services.report_review_windows import (
    MAX_REVIEW_WINDOWS, SourceReviewWindow, plan_source_review_windows,
)
from oil_tracker.domain.enums import EventType
from tests.unit.test_source_context_renderer import Reader, geometry, inputs


def view(*, extrema=(), scenes=(), missing=(), oil=True, foam=None):
    landmarks = [NS(event_type=kind, timestamp_sec=t, end_time_sec=None) for kind, t in extrema]
    if foam is not None:
        landmarks.append(NS(event_type=EventType.FOAM_START, timestamp_sec=foam[0], end_time_sec=foam[1]))
    return NS(scene_captures=tuple(NS(timestamp_sec=t) for t in scenes), has_oil=oil,
              unavailable_intervals=missing, landmarks=landmarks)


def test_broad_gap_does_not_swallow_native_extrema_zoom_and_foam_is_independent():
    presentation = view(extrema=[(EventType.MAXIMUM_OIL_LEVEL, 40), (EventType.MINIMUM_OIL_LEVEL, 42)],
                        scenes=(10, 30, 50), foam=(20, 35))
    before = deepcopy(presentation)
    windows = plan_source_review_windows(presentation, 0, 60)
    assert len(windows) == 3
    assert [(w.start_sec, w.end_sec) for w in windows] == [(10, 50), (18, 37), (38, 44)]
    assert len(windows[-1].reasons) == 2
    assert presentation == before


def test_all_missing_oil_keeps_whole_scene_and_independent_foam():
    windows = plan_source_review_windows(view(oil=False, foam=(4, 6)), 0, 20)
    assert len(windows) == 2
    assert windows[0].start_sec == 0 and windows[0].end_sec == 20
    assert windows[1].reasons == ("주요 Foam 관측 구간",)


def test_request_bounds_clip_and_preserve_separate_extrema():
    windows = plan_source_review_windows(view(extrema=[(EventType.MAXIMUM_OIL_LEVEL, 0),
                (EventType.MINIMUM_OIL_LEVEL, 100)], scenes=(10, 30, 50), foam=(60, 70)), 0, 100)
    assert len(windows) == MAX_REVIEW_WINDOWS
    assert windows[0].start_sec == 0 and windows[-1].end_sec == 100


@pytest.mark.parametrize("start,end", [(-1, 2), (2, 1), (0, float("nan"))])
def test_invalid_window_rejected(start, end):
    with pytest.raises(ValueError):
        plan_source_review_windows(view(), start, end)


@pytest.mark.parametrize("start,end,fps", [(0, 2, 30), (0, 3600, 30), (1, 1, 30), (0, .01, 10)])
def test_source_time_budget_is_native_or_slower(start, end, fps):
    times = sequence_times(start, end, fps)
    assert 1 <= len(times) <= MAX_SEQUENCE_FRAMES
    assert times[0] == start
    if len(times) > 1:
        assert times[-1] == end
        assert np.all(np.diff(times) >= 1/fps - 1e-9)


def test_native_crop_keeps_pixels_and_artifact_corners_without_mutation():
    frame = np.arange(40*40*3, dtype=np.uint8).reshape(40, 40, 3)
    before = frame.copy()
    tile, meta = source_tile(frame, geometry())
    x, y, w, h = meta["tile_content_xywh"]
    assert np.array_equal(tile[y:y+h, x:x+w], frame[2:38, 2:38])
    assert meta["resize_method"] == "none"
    assert np.array_equal(frame, before)


def test_large_non_square_crop_preserves_aspect_and_downscale_only():
    frame = np.full((400, 800, 3), 120, np.uint8)
    g = NS(ellipse=NS(center_x=400, center_y=200, radius_x=300, radius_y=100))
    tile, meta = source_tile(frame, g)
    assert tile.shape == (TILE_SIZE, TILE_SIZE, 3)
    assert meta["tile_content_xywh"][2:] == [192, 64]
    assert meta["resize_method"] == "INTER_AREA"


def test_render_records_provenance_and_no_numeric_repair(tmp_path):
    result, recipe, session = inputs()
    before = deepcopy((result, recipe, session.input_video_path))
    reader = Reader("source")
    presentation = NS(for_glass=lambda _: view(oil=False))
    output = SourceSequenceRenderer(lambda _: reader).render(result, recipe, session, tmp_path,
                                                            presentation=presentation)
    info = output["glass"][0]
    assert info["available_count"] == info["frame_count"] == 21
    assert not info["numeric_measurement"] and not info["subsampled"]
    assert [f["frame_index"] for f in info["frames"]] == list(range(21))
    assert reader.closed and (result, recipe, session.input_video_path) == before
    meta = json.loads((tmp_path / "source_sequence_01_01.json").read_text(encoding="utf-8"))
    assert meta == json.loads(json.dumps(info))
    first = info["frames"][0]
    page = cv2.imread(str(tmp_path / _basename(first["page_path"])))
    expected, _ = source_tile(reader.read_at(0)[0], recipe.glasses[0].geometry)
    assert np.array_equal(page[:TILE_SIZE, :TILE_SIZE], expected)


def _basename(path):
    return path.rsplit("/", 1)[-1]


@pytest.mark.parametrize("failure", ["decode", "duplicate", "timestamp", "geometry", "nonmonotonic"])
def test_bad_frame_is_unavailable_without_sprite_reference(tmp_path, failure):
    reader = Reader("source")
    original = reader.read_at
    def read(time):
        frame, index, actual = original(time)
        if .99 < time < 1.01:
            if failure == "decode":
                raise EOFError("missing")
            if failure == "duplicate":
                index = 9
            elif failure == "timestamp":
                actual = 50
            elif failure == "nonmonotonic":
                actual = .9
            else:
                frame = np.zeros((80, 80, 3), np.uint8)
        return frame, index, actual
    reader.read_at = read
    payload = SourceSequenceRenderer()._collect(reader, inputs()[1].glasses[0],
        SourceReviewWindow(0, 2, ("test",)), tmp_path, "test")
    assert payload["status"] == "PARTIAL"
    assert payload["frames"][10]["status"] == "UNAVAILABLE"
    assert "page_path" not in payload["frames"][10]
    assert payload["frames"][11]["status"] == "AVAILABLE"


@pytest.mark.parametrize("fps", [0, -1, float("inf"), float("nan")])
def test_unknown_native_cadence_has_no_frames(tmp_path, fps):
    reader = Reader("source")
    reader.metadata = NS(fps=fps)
    payload = SourceSequenceRenderer()._collect(reader, inputs()[1].glasses[0],
        SourceReviewWindow(0, 2, ("test",)), tmp_path, "test")
    assert payload["status"] == "UNAVAILABLE" and reader.calls == []


def test_source_open_failure_is_disclosed_and_nonfatal(tmp_path):
    def missing(_):
        raise OSError("offline source")
    output = SourceSequenceRenderer(missing).render(*inputs(), tmp_path,
              presentation=NS(for_glass=lambda _: view(oil=False)))
    info = output["glass"][0]
    assert info["status"] == "UNAVAILABLE" and info["frame_count"] == 0
    assert info["source_error"] == "OSError"


def test_cancellation_even_after_last_frame_closes_reader(tmp_path):
    reader = Reader("source")
    token = NS(cancelled=False)
    original = reader.read_at
    def read(time):
        if time >= 2:
            token.cancelled = True
        return original(time)
    reader.read_at = read
    with pytest.raises(AnalysisCancelled):
        SourceSequenceRenderer(lambda _: reader).render(*inputs(), tmp_path,
              presentation=NS(for_glass=lambda _: view(oil=False)), cancellation=token)
    assert reader.closed


def test_html_fragments_escape_labels_and_keep_json_inert():
    from oil_tracker.adapters.reporting.html_reporter import HtmlReporter
    reporter = HtmlReporter()
    template = reporter.environment.get_template("source_sequences.html.j2")
    sequence = dict(reasons=["<b>unsafe</b>"], start_sec=0, end_sec=1, available_count=0,
                    frame_count=0, preview_path="", metadata_path="assets/meta.json",
                    frames=[], source_error="</script><script>bad()</script>")
    html = template.render(source_context={"sequences": [sequence]})
    assert "&lt;b&gt;unsafe&lt;/b&gt;" in html
    assert "<b>unsafe</b>" not in html and "<script>bad()" not in html
    assert "noscript" in html and 'type="application/json"' in html


class SequentialReader(Reader):
    def __init__(self, path):
        super().__init__(path)
        self.index = -1
        self.seeks = 0

    def read_at(self, time):
        self.seeks += 1
        self.index = int(round(time*10))
        return super().read_at(self.index/10)

    def read_next(self):
        self.index += 1
        return super().read_at(self.index/10)


def test_native_frame_sequence_seeks_once_and_keeps_every_identity(tmp_path):
    reader = SequentialReader("source")
    payload = SourceSequenceRenderer()._collect(reader, inputs()[1].glasses[0],
        SourceReviewWindow(0, 2, ("test",)), tmp_path, "test")
    assert payload["status"] == "AVAILABLE"
    assert [f["frame_index"] for f in payload["frames"]] == list(range(21))
    assert reader.seeks == 1
    assert payload["decode_strategy"]["sequential_read_count"] == 20


def test_large_source_jump_uses_seek_instead_of_unbounded_decode():
    from oil_tracker.adapters.reporting.source_sequence_renderer import _SequenceSampler
    reader = SequentialReader("source")
    sampler = _SequenceSampler(reader, 10)
    assert sampler.read_at(0)[1] == 0
    assert sampler.read_at(20)[1] == 200
    assert sampler.seek_count == 2 and sampler.sequential_read_count == 0


def test_nonmonotonic_sequential_frame_is_missing_then_recovers(tmp_path):
    reader = SequentialReader("source")
    original = reader.read_next
    broken = False
    def read_next():
        nonlocal broken
        if not broken:
            broken = True
            return Reader.read_at(reader, 0)
        return original()
    reader.read_next = read_next
    payload = SourceSequenceRenderer()._collect(reader, inputs()[1].glasses[0],
        SourceReviewWindow(0, 2, ("test",)), tmp_path, "test")
    assert payload["status"] == "PARTIAL"
    assert payload["frames"][1]["status"] == "UNAVAILABLE"
    assert payload["frames"][2]["status"] == "AVAILABLE"
    assert payload["frames"][2]["frame_index"] == 2


def test_slow_reported_timestamps_cannot_create_unbounded_sequential_loop():
    from oil_tracker.adapters.reporting.source_sequence_renderer import MAX_SEQUENTIAL_ADVANCE, _SequenceSampler
    reader = SequentialReader("source")
    sampler = _SequenceSampler(reader, 10)
    sampler.read_at(0)
    def too_slow():
        reader.index += 1
        frame, _, _ = Reader.read_at(reader, 0)
        return frame, reader.index, reader.index*.0001
    reader.read_next = too_slow
    with pytest.raises(ValueError, match="budget_exceeded"):
        sampler.read_at(1)
    assert sampler.sequential_read_count == MAX_SEQUENTIAL_ADVANCE
    assert sampler.last is None
