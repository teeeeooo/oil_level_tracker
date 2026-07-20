from __future__ import annotations

from pathlib import Path

import numpy as np

from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController


class _Reader:
    def __init__(self, path, *, duration=2.0, fps=10.0):
        self.path = str(path)
        self.metadata = VideoMetadata(self.path, 32, 24, fps, duration, int(duration * fps), "fake")
        self.closed = False
        self.requests = []

    def read_at(self, timestamp):
        self.requests.append(timestamp)
        actual = min(max(0.0, float(timestamp)) + 0.01, max(0.0, self.metadata.duration_sec - 0.01))
        return np.zeros((24, 32, 3), dtype=np.uint8), int(actual * self.metadata.fps), actual

    def close(self):
        self.closed = True


def test_open_seek_step_speed_and_actual_timestamp(qtbot):
    readers = []

    def factory(path):
        reader = _Reader(path)
        readers.append(reader)
        return reader

    controller = ResultReviewController(factory)
    received = []
    controller.frameReady.connect(lambda _frame, index, timestamp: received.append((index, timestamp)))
    controller.open_video("source.mp4", 0.5)
    assert received[-1][1] == 0.51
    controller.seek(1.0)
    assert received[-1][1] == 1.01
    before = controller.current_time
    controller.step(1)
    assert controller.current_time > before
    controller.set_speed(4.0)
    assert controller.speed == 4.0
    controller.close()
    assert readers[0].closed is True


def test_opening_replacement_closes_previous_reader():
    readers = []

    def factory(path):
        reader = _Reader(path)
        readers.append(reader)
        return reader

    controller = ResultReviewController(factory)
    controller.open_video(Path("first.mp4"))
    controller.open_video(Path("second.mp4"))
    assert readers[0].closed is True
    assert readers[1].closed is False
    controller.close()
    assert readers[1].closed is True


def test_play_pause_tick_and_end_of_video_auto_stop():
    controller = ResultReviewController(lambda path: _Reader(path, duration=1.0, fps=10.0))
    controller.open_video("source.mp4", 0.0)
    controller.play()
    assert controller.is_playing
    controller._tick()
    assert controller.current_time > 0.0
    controller.current_time = 0.95
    controller._tick()
    assert not controller.is_playing
    controller.close()


def test_close_stops_timer_and_releases_reader():
    reader = _Reader("source.mp4")
    controller = ResultReviewController(lambda _path: reader)
    controller.open_video("source.mp4")
    controller.play()
    controller.close()
    assert not controller.timer.isActive()
    assert reader.closed is True
    assert controller.reader is None
