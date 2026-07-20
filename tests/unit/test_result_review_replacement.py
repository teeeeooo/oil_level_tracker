from __future__ import annotations

import numpy as np
import pytest

from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController


class _Reader:
    def __init__(self, path, events, *, fail_read=False):
        self.path = str(path)
        self.events = events
        self.fail_read = fail_read
        self.closed = False
        self.metadata = VideoMetadata(self.path, 320, 240, 10.0, 5.0, 50, "fake")
        events.append(("open", self.path))

    def read_at(self, timestamp):
        self.events.append(("read", self.path, float(timestamp)))
        if self.fail_read:
            raise OSError("decode failed")
        actual = float(timestamp) + 0.01
        return np.zeros((240, 320, 3), dtype=np.uint8), int(actual * 10), actual

    def close(self):
        self.closed = True
        self.events.append(("close", self.path))


def test_candidate_factory_failure_preserves_active_reader_frame_and_timestamp():
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
    with pytest.raises(OSError):
        controller.open_video("bad.mp4", 2.0)
    assert controller.reader is active
    assert active.closed is False
    assert controller.current_time == before_time
    assert controller.current_frame_index == before_frame


def test_candidate_decode_failure_closes_candidate_only_and_preserves_active_reader():
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


def test_successful_candidate_decodes_before_previous_reader_is_closed():
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
