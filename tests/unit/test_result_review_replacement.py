from __future__ import annotations

import pytest
from PySide6.QtGui import QImage

from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController
from review_raster_fixtures import solid_image


class _Reader:
    def __init__(self, path, events, *, fail_read=False):
        self.path = str(path)
        self.events = events
        self.fail_read = fail_read
        self.closed = False
        self.metadata = VideoMetadata(self.path, 320, 240, 10.0, 5.0, 50, "fake")
        self._source_image = QImage()
        events.append(("open", self.path))

    @property
    def source_image(self):
        return QImage(self._source_image).copy()

    def read_at(self, timestamp):
        self.events.append(("read", self.path, float(timestamp)))
        if self.fail_read:
            raise OSError("decode failed")
        actual = float(timestamp) + 0.01
        self._source_image = solid_image(320, 240, (10, 20, 30))
        return QImage(self._source_image).copy(), int(actual * 10), actual

    def render_general(self, _glass, _overlay):
        return QImage(self._source_image).copy()

    def render_debug(self, _glass, _record, _timestamp, _highlight=None):
        return QImage(self._source_image).copy()

    def close(self):
        self.closed = True
        self._source_image = QImage()
        self.events.append(("close", self.path))


def test_candidate_factory_failure_preserves_active_reader_frame_and_timestamp(qapp):
    events = []
    first = _Reader("first.mp4", events)

    def factory(path):
        if str(path) == "bad.mp4":
            raise OSError("open failed")
        return first

    controller = ResultReviewController(factory)
    controller.open_video("first.mp4", 1.0)
    active = controller.reader
    before_time = controller.current_time
    before_frame = controller.current_frame_index
    before_image = controller.source_image
    with pytest.raises(OSError):
        controller.open_video("bad.mp4", 2.0)
    assert controller.reader is active
    assert active.closed is False
    assert controller.current_time == before_time
    assert controller.current_frame_index == before_frame
    assert controller.source_image == before_image


def test_candidate_decode_failure_closes_candidate_only_and_preserves_active_reader(qapp):
    events = []
    readers = {}

    def factory(path):
        reader = _Reader(path, events, fail_read=str(path) == "bad.mp4")
        readers[str(path)] = reader
        return reader

    controller = ResultReviewController(factory)
    controller.open_video("first.mp4", 1.0)
    active = controller.reader
    with pytest.raises(OSError):
        controller.open_video("bad.mp4", 2.0)
    assert controller.reader is active
    assert active.closed is False
    assert readers["bad.mp4"].closed is True


def test_successful_candidate_decodes_before_previous_reader_is_closed(qapp):
    events = []

    def factory(path):
        return _Reader(path, events)

    controller = ResultReviewController(factory)
    controller.open_video("first.mp4", 1.0)
    first = controller.reader
    controller.open_video("second.mp4", 2.0)
    second = controller.reader
    assert first.closed is True
    assert second.closed is False
    assert events.index(("read", "second.mp4", 2.0)) < events.index(("close", "first.mp4"))
    controller.close()
    assert second.closed is True
