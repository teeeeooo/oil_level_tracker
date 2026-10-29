import cv2
import numpy as np
import pytest

from oil_tracker.adapters.video.analysis import OpenCvAnalyser, png_pieces, run_analysis
from oil_tracker.adapters.video.draft import draft_line, oil_draft
from oil_tracker.application.ports import AnalysisCancelled
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import AnalysisSettings
from oil_tracker.domain.recipe import Glass

GLASSES = (Glass("g1", "BASE", Ellipse(50, 60, 30, 50), 60), Glass("g2", "ACCUM", Ellipse(115, 60, 25, 40), 60))


@pytest.fixture(scope="module")
def video(tmp_path_factory):
    path = tmp_path_factory.mktemp("video") / "level.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (160, 120))
    for index in range(30):
        frame = np.full((120, 160, 3), 50, np.uint8)
        frame[20 + 2 * index:] = 210
        writer.write(frame)
    writer.release()
    return path


def joined(pieces):
    return np.concatenate([cv2.imdecode(np.frombuffer(p, np.uint8), cv2.IMREAD_UNCHANGED) for p in pieces], axis=1)


def test_png_pieces_split_by_columns_and_keep_the_pixels():
    rgb = np.random.default_rng(1).integers(0, 256, (6, 10, 3), dtype=np.uint8)
    pieces = png_pieces(rgb, columns=4)
    assert [cv2.imdecode(np.frombuffer(p, np.uint8), cv2.IMREAD_UNCHANGED).shape[1] for p in pieces] == [4, 4, 2]
    assert np.array_equal(joined(pieces)[:, :, ::-1], rgb)  # PNG holds BGR; the image is RGB
    grey = rgb[:, :, 0]
    assert np.array_equal(joined(png_pieces(grey, columns=4)), grey)


def test_the_analysis_gives_every_glass_its_draft_and_pictures(video):
    calls = []
    result = OpenCvAnalyser().analyse(
        video, GLASSES, AnalysisSettings(0.0, 2.5), lambda done, total: calls.append((done, total)), lambda: False
    )
    assert result.times == pytest.approx((0, 0.5, 1.0, 1.5, 2.0, 2.5))
    assert [d.glass_id for d in result.drafts] == ["g1", "g2"]
    assert all(len(d.oil.ys) == 6 for d in result.drafts)
    for images, glass in zip(result.images, GLASSES):
        assert images.glass_id == glass.id
        assert images.y0 == glass.ellipse.top and images.rows == 2 * glass.ellipse.radius_y
        assert joined(images.context_png).shape == (images.rows, 6, 3)
        assert joined(images.background_png).shape == (images.rows, 6)
        context = joined(images.context_png)[:, :, ::-1]
        assert result.drafts[GLASSES.index(glass)].oil == draft_line(oil_draft(context), images.y0)
    dones = [done for done, _ in calls]
    assert dones == sorted(dones) and calls[-1][0] == calls[-1][1]


def test_the_analysis_reports_its_timings(video):
    _, timings = run_analysis(video, GLASSES[:1], AnalysisSettings(0.0, 2.5), lambda d, t: None, lambda: False)
    assert timings.frames_decoded == 26 and timings.hardware_used is False
    assert set(timings.pass_seconds) == {"grab", "retrieve", "reduce", "wait", "total"}
    assert set(timings.glass_seconds[0]) == {"draft", "background", "png"}


def test_a_cancelled_analysis_raises(video):
    with pytest.raises(AnalysisCancelled):
        OpenCvAnalyser().analyse(video, GLASSES, AnalysisSettings(0.0, 2.5), lambda d, t: None, lambda: True)
