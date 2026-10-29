import numpy as np

from oil_tracker.adapters.video.analysis import png_pieces
from oil_tracker.adapters.video.draft import strongest_path
from oil_tracker.adapters.video.trace import ContextEdgeTracer


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
