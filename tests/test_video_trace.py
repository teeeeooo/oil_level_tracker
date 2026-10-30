import numpy as np
import pytest
from numpy.lib.stride_tricks import sliding_window_view

from oil_tracker.adapters.video.analysis import png_pieces
from oil_tracker.adapters.video.draft import JUMP_WEIGHT, MAX_JUMP, strongest_path
from oil_tracker.adapters.video.trace import REACH, ContextEdgeTracer, corridor_path


def two_edges(columns=80):
    """A bright band from row 30 to row 60 in a dark Glass: an edge at each end of it."""
    rgb = np.full((100, columns, 3), 40, np.uint8)
    rgb[30:60] = 200
    return rgb


def reader(rgb, columns):
    pieces = png_pieces(rgb, columns)
    calls = []

    def piece(index):
        calls.append(index)
        return pieces[index]

    return piece, len(pieces), calls


def reference_path(s, start=None, end=None):
    """The search as first written: every pair of rows within the jump limit, per column."""
    height, columns = s.shape
    jump = max(1, int(MAX_JUMP * height))
    penalty = JUMP_WEIGHT * np.abs(np.arange(-jump, jump + 1)) / height
    rows = np.arange(height)
    score = s[:, 0].astype(np.float64)
    if start is not None:
        score = np.where(rows == start, score, -np.inf)
    back = np.zeros((height, columns), dtype=np.int32)
    for t in range(1, columns):
        total = sliding_window_view(np.pad(score, jump, constant_values=-np.inf), 2 * jump + 1) - penalty
        best = total.argmax(axis=1)
        back[:, t] = rows + best - jump
        score = total[rows, best] + s[:, t]
    if end is not None and not np.isfinite(score[end]):
        return np.rint(np.linspace(start, end, columns)).astype(np.int32)
    path = np.zeros(columns, dtype=np.int32)
    path[-1] = int(score.argmax()) if end is None else end
    for t in range(columns - 1, 0, -1):
        path[t - 1] = back[path[t], t]
    return path


def path_value(s, path):
    return s[path, np.arange(len(path))].sum() - JUMP_WEIGHT * np.abs(np.diff(path)).sum() / s.shape[0]


@pytest.mark.parametrize("height, columns, seed", [(7, 40, 1), (100, 300, 2), (728, 400, 3), (61, 200, 4)])
def test_the_search_finds_the_same_path_as_every_pair_of_rows(height, columns, seed):
    rng = np.random.default_rng(seed)
    s = rng.random((height, columns))
    pinned = (1, height - 2)
    assert np.array_equal(strongest_path(s), reference_path(s))
    assert np.array_equal(strongest_path(s, *pinned), reference_path(s, *pinned))
    # with exact ties the paths may part where they score the same: the rounding differs
    s[:, ::7] = np.round(s[:, ::7], 1)
    for pins in ((None, None), pinned):
        assert path_value(s, strongest_path(s, *pins)) == pytest.approx(path_value(s, reference_path(s, *pins)), abs=1e-9)


def test_the_path_is_pinned_to_its_ends():
    s = np.zeros((50, 10))
    s[20] = 1.0
    assert strongest_path(s).tolist() == [20] * 10
    pinned = strongest_path(s, 5, 30)
    assert (pinned[0], pinned[-1]) == (5, 30)
    assert (pinned[2:-2] == 20).all()  # it leaves the pins for the edge between them


def test_pins_out_of_reach_are_joined_straight():
    s = np.zeros((100, 3))
    assert strongest_path(s, 0, 99).tolist() == [0, 50, 99]  # 25 rows per column at most


def test_points_on_one_edge_follow_it_across_pieces():
    piece, pieces, calls = reader(two_edges(), columns=32)
    tracer = ContextEdgeTracer()
    rows = tracer.trace("i1/g1/t1", piece, pieces, [(5, 59), (70, 60)])
    assert len(rows) == 66 and (rows[0], rows[-1]) == (59, 60)
    assert all(abs(r - 60) <= 1 for r in rows)  # the lower edge, not the upper one
    upper = tracer.trace("i1/g1/t1", piece, pieces, [(5, 30), (40, 29), (70, 30)])
    assert len(upper) == 66 and upper[35] == 29 and all(abs(r - 30) <= 1 for r in upper)
    assert calls == [0, 1, 2]  # decoded once for both


def test_the_tracer_keeps_the_latest_images():
    piece, pieces, calls = reader(two_edges(), columns=80)
    tracer = ContextEdgeTracer(keep=2)
    for key in ("a", "b", "a", "c", "a", "b"):
        tracer.trace(key, piece, pieces, [(0, 30), (5, 30)])
    assert len(calls) == 4  # a, b, c, then b again after c pushed it out


def test_the_path_keeps_near_the_straight_line_between_the_points():
    # user, 2026-10-30: free to follow the strongest edges, the path ran to the image's top or bottom
    s = np.zeros((200, 60))
    s[0] = s[199] = 1.0  # the strongest steps, far from the points
    s[100, 10:50] = 0.8  # an edge 6 rows from the line
    rows = corridor_path(s, 0, 94, 59, 94)
    assert (rows[0], rows[-1]) == (94, 94)
    assert all(abs(r - 94) <= REACH for r in rows)
    assert (rows[12:48] == 100).all()  # it follows the edge within reach


def test_without_an_edge_near_the_line_the_path_is_straight():
    s = np.zeros((200, 41))
    s[0] = s[199] = 1.0
    s[120:130] = 0.2  # steps below the snap's minimum are no edge
    rows = corridor_path(s, 0, 100, 40, 140)
    assert rows.tolist() == [100 + k for k in range(41)]


def test_the_band_is_cut_at_the_image_edges():
    s = np.zeros((20, 10))
    s[0] = 1.0
    rows = corridor_path(s, 0, 2, 9, 2)
    assert rows.min() >= 0 and (rows[2:-2] == 0).all()  # the top row's edge, never above it
