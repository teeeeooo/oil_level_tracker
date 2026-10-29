import cv2
import numpy as np
import pytest

from oil_tracker.adapters.video.frames import open_video
from oil_tracker.application.ports import VideoUnreadable

FPS = 10.0
COUNT = 30
WIDTH, HEIGHT = 160, 120


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    """Frame i is a flat grey of level 8 * i, so a decoded frame names its index."""
    path = tmp_path_factory.mktemp("video") / "sample.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (WIDTH, HEIGHT))
    assert writer.isOpened()
    for index in range(COUNT):
        writer.write(np.full((HEIGHT, WIDTH, 3), 8 * index, np.uint8))
    writer.release()
    return path


def index_of(jpeg: bytes) -> int:
    image = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_GRAYSCALE)
    return round(float(image.mean()) / 8)


def test_info(video):
    opened = open_video(video)
    try:
        assert (opened.info.name, opened.info.width, opened.info.height) == ("sample.avi", WIDTH, HEIGHT)
        assert opened.info.fps == pytest.approx(FPS)
        assert opened.info.frame_count == COUNT
        assert opened.info.duration_sec == pytest.approx(3.0)
    finally:
        opened.close()


def test_frames_are_exact_in_any_order(video):
    opened = open_video(video)
    try:
        for time_sec in (1.2, 1.3, 1.4, 0.0, 2.9, 0.5, 0.6, 1.24):
            frame = opened.frame_at(time_sec)
            assert frame.index == round(time_sec * FPS)
            assert frame.time_sec == pytest.approx(frame.index / FPS)
            assert index_of(frame.jpeg) == frame.index
    finally:
        opened.close()


def test_times_outside_the_video_are_clamped(video):
    opened = open_video(video)
    try:
        assert opened.frame_at(-5).index == 0
        last = opened.frame_at(999)
        assert last.index == COUNT - 1
        assert index_of(last.jpeg) == COUNT - 1
        with pytest.raises(ValueError):
            opened.frame_at(float("nan"))
    finally:
        opened.close()


def test_max_size_limits_the_longer_side(video):
    opened = open_video(video)
    try:
        jpeg = opened.frame_at(0, max_size=80).jpeg
        image = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
        assert image.shape[:2] == (60, 80)
        full = cv2.imdecode(np.frombuffer(opened.frame_at(0, max_size=1280).jpeg, np.uint8), cv2.IMREAD_COLOR)
        assert full.shape[:2] == (HEIGHT, WIDTH)
    finally:
        opened.close()


def test_a_file_that_is_not_a_video_is_refused(tmp_path):
    path = tmp_path / "not-a-video.mp4"
    path.write_bytes(b"hello")
    with pytest.raises(VideoUnreadable):
        open_video(path)
