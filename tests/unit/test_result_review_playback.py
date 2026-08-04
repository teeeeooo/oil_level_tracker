from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QImage

from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController
from review_raster_fixtures import solid_image


class _Reader:
    def __init__(self, path, *, duration=2.0, fps=10.0):
        self.path = str(path)
        self.metadata = VideoMetadata(self.path, 32, 24, fps, duration, int(duration * fps), "fake")
        self.closed = False
        self.requests = []
        self._source_image = QImage()

    @property
    def source_image(self):
        return QImage(self._source_image).copy()

    def read_at(self, timestamp):
        self.requests.append(timestamp)
        actual = min(max(0.0, float(timestamp)) + 0.01, max(0.0, self.metadata.duration_sec - 0.01))
        self._source_image = solid_image(32, 24, (10, 20, 30))
        return QImage(self._source_image).copy(), int(actual * self.metadata.fps), actual

    def render_general(self, _glass, _overlay):
        return QImage(self._source_image).copy()

    def render_debug(self, _glass, _record, _timestamp, _highlight=None):
        return QImage(self._source_image).copy()

    def close(self):
        self.closed = True
        self._source_image = QImage()


def test_open_seek_step_speed_and_actual_timestamp(qtbot):
    readers = []

    def factory(path):
        reader = _Reader(path)
        readers.append(reader)
        return reader

    controller = ResultReviewController(factory)
    received = []
    controller.frameReady.connect(
        lambda frame, index, timestamp: received.append((QImage(frame).copy(), index, timestamp))
    )
    controller.open_video("source.mp4", 0.5)
    assert isinstance(received[-1][0], QImage) and not received[-1][0].isNull()
    assert received[-1][2] == 0.51
    controller.seek(1.0)
    assert received[-1][2] == 1.01
    before = controller.current_time
    controller.step(1)
    assert controller.current_time > before
    controller.set_speed(4.0)
    assert controller.speed == 4.0
    controller.close()
    assert readers[0].closed is True


def test_opening_replacement_closes_previous_reader(qapp):
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


def test_play_pause_tick_and_end_of_video_auto_stop(qapp):
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


def test_close_stops_timer_and_releases_reader(qapp):
    reader = _Reader("source.mp4")
    controller = ResultReviewController(lambda _path: reader)
    controller.open_video("source.mp4")
    controller.play()
    controller.close()
    assert not controller.timer.isActive()
    assert reader.closed is True
    assert controller.reader is None


def test_qtimer_playback_advances_through_repository_event_loop(qtbot):
    controller = ResultReviewController(
        lambda path: _Reader(path, duration=1.0, fps=20.0)
    )
    controller.open_video("source.mp4", 0.0)
    before = controller.current_time
    try:
        controller.play()
        qtbot.waitUntil(lambda: controller.current_time > before, timeout=1000)
        assert controller.is_playing is True
    finally:
        controller.close()
