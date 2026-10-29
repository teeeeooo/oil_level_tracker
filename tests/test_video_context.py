import warnings

import cv2
import numpy as np
import pytest

from oil_tracker.adapters.video import context
from oil_tracker.adapters.video.context import _Band, background_view, build_contexts
from oil_tracker.adapters.video.draft import OilDraft, draft_line, oil_draft
from oil_tracker.application.ports import AnalysisCancelled, VideoUnreadable
from oil_tracker.domain.enums import SampleOrigin
from oil_tracker.domain.geometry import Ellipse

FPS = 10.0
COUNT = 30
WIDTH, HEIGHT = 160, 120
GLASSES = (Ellipse(50, 60, 30, 50), Ellipse(115, 60, 25, 40))


def level(index: int) -> int:
    """Rows from here down are bright in frame `index`: a level that sinks 2 px per frame."""
    return 20 + 2 * index


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    path = tmp_path_factory.mktemp("video") / "level.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), FPS, (WIDTH, HEIGHT))
    assert writer.isOpened()
    for index in range(COUNT):
        frame = np.full((HEIGHT, WIDTH, 3), 50, np.uint8)
        frame[level(index):] = 210
        writer.write(frame)
    writer.release()
    return path


def boundary(column: np.ndarray, y0: int) -> int:
    """The first source row whose luma is past halfway between the two levels."""
    return y0 + int(np.argmax(column.mean(axis=1) > 130))


def test_band_median_matches_numpy_nanmedian():
    frame = np.random.default_rng(3).integers(0, 256, (100, 120, 3), dtype=np.uint8)
    band = _Band(Ellipse(60, 50, 30, 40), 120, 100)
    column = band.median(frame)
    crop = frame[band.y0:band.y1, band.x0:band.x1].astype(np.float64)
    crop[band.outside] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        expected = np.floor(np.nan_to_num(np.nanmedian(crop, axis=1), nan=0.0))
    assert np.array_equal(column, expected[:, ::-1].astype(np.uint8))


def test_one_pass_samples_every_glass_from_the_same_frames(video):
    calls = []
    result = build_contexts(video, GLASSES, start_sec=0, end_sec=999, rate=2,
                            on_progress=lambda done, total: calls.append((done, total)))
    assert result.frame_indices == (0, 5, 10, 15, 20, 25)
    assert result.times == pytest.approx((0, 0.5, 1.0, 1.5, 2.0, 2.5))
    assert result.frames_decoded == 26
    assert calls[-1] == (26, 26)
    for image, ellipse in zip(result.images, GLASSES):
        assert image.y0 == ellipse.center_y - ellipse.radius_y
        assert image.rgb.shape == (2 * ellipse.radius_y, 6, 3)
        for column, index in enumerate(result.frame_indices):
            assert abs(boundary(image.rgb[:, column], image.y0) - level(index)) <= 2


@pytest.mark.parametrize("workers", [1, 3])
def test_worker_threads_give_the_same_images(video, workers):
    inline = build_contexts(video, GLASSES, start_sec=0, end_sec=999, rate=2, workers=0)
    threaded = build_contexts(video, GLASSES, start_sec=0, end_sec=999, rate=2, workers=workers)
    assert threaded.frame_indices == inline.frame_indices
    for a, b in zip(threaded.images, inline.images):
        assert np.array_equal(a.rgb, b.rgb) and a.y0 == b.y0
    assert set(threaded.seconds) == {"grab", "retrieve", "reduce", "wait"}


def test_the_pass_stops_when_cancelled(video, monkeypatch):
    monkeypatch.setattr(context, "PROGRESS_EVERY", 5)
    asked = []

    def cancelled():
        asked.append(True)
        return len(asked) == 2

    with pytest.raises(AnalysisCancelled):
        build_contexts(video, GLASSES, start_sec=0, end_sec=999, rate=2, cancelled=cancelled)
    assert len(asked) == 2


def test_a_range_seeks_to_its_first_frame(video):
    result = build_contexts(video, GLASSES[:1], start_sec=1.0, end_sec=2.0, rate=2)
    assert result.frame_indices == (10, 15, 20)
    image = result.images[0]
    for column, index in enumerate(result.frame_indices):
        assert abs(boundary(image.rgb[:, column], image.y0) - level(index)) <= 2


def test_an_unreadable_video_is_refused(tmp_path):
    with pytest.raises(VideoUnreadable):
        build_contexts(tmp_path / "missing.mp4", GLASSES, start_sec=0, end_sec=1, rate=2)


def test_background_view_keeps_only_what_changes():
    rgb = np.full((20, 40, 3), 90, np.uint8)
    rgb[5, :] = 200       # a band that never moves
    rgb[12, 30] = 250     # one changing pixel
    view = background_view(rgb)
    assert view[5].max() == 0
    assert view[12, 30] == 255
    assert view[12, :30].max() == 0


def test_the_draft_follows_a_moving_edge():
    rows = np.arange(100)[:, None]
    edge = 30 + np.arange(60) // 2
    rgb = np.repeat(np.where(rows >= edge, 200, 40)[:, :, None], 3, axis=2).astype(np.uint8)
    draft = oil_draft(rgb)
    # the 5-column blur and the jump cost make a moving edge a staircase that trails by up to 2 rows
    assert np.abs(draft.rows - edge).max() <= 2
    assert not draft.empty.any()


def test_the_draft_does_not_jump_to_a_strong_edge_for_one_column():
    rgb = np.full((100, 60, 3), 100, np.uint8)
    rgb[40:] = 160          # a steady edge at row 40
    rgb[80:, 30] = 255      # a much stronger edge at row 80, in one column only
    draft = oil_draft(rgb)
    assert abs(int(draft.rows[30]) - 40) <= 1


def test_weak_stretches_are_left_empty():
    rgb = np.full((100, 60, 3), 100, np.uint8)
    rgb[50:, :30] = 200     # an edge in the first half only
    draft = oil_draft(rgb)
    assert not draft.empty[:20].any()
    assert draft.empty[40:].all()


def test_the_draft_becomes_source_frame_samples():
    draft = OilDraft(np.array([5, 6, 7]), np.array([False, True, False]))
    line = draft_line(draft, y0=400)
    assert line.ys == (405.0, None, 407.0)
    assert line.origins == (SampleOrigin.DRAFT,) * 3
