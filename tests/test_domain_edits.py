import pytest

from oil_tracker.domain.edits import (
    Coverage,
    Dropped,
    Edits,
    GlassEdits,
    Memo,
    Run,
    Stretch,
    coverage,
    edits_from_analysis,
    empty_line,
    level_states,
    merge_reanalysis,
    runs,
)
from oil_tracker.domain.enums import LevelState, SampleOrigin
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import Analysis, GlassDraft
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass

D, E, W = SampleOrigin.DRAFT, SampleOrigin.EDITED, SampleOrigin.DRAWN
GLASS = Glass("g1", "BASE", Ellipse(100, 300, 40, 200), 320)  # top y 100, bottom y 500


def line(*ys, origin=D):
    return Line(tuple(ys), (origin,) * len(ys))


def analysis(times, *drafts):
    return Analysis(tuple(times), tuple(GlassDraft(glass_id, oil) for glass_id, oil in drafts), "t")


def test_the_first_edits_are_the_drafts():
    found = analysis([0.0, 0.5, 1.0], ("g1", line(200.0, None, 210.0)))
    edits = edits_from_analysis(found, 0.5)
    glass = edits.glass("g1")
    assert edits.times == (0.0, 0.5, 1.0) and edits.compressor_start_sec == 0.5
    assert glass.oil == line(200.0, None, 210.0)
    assert glass.foam == glass.reference == empty_line(3)
    assert (glass.cannot_judge, glass.memos) == ((), ())


def test_the_document_keeps_its_shape():
    with pytest.raises(ValueError):
        Edits((0.0, 0.5), (GlassEdits("g1", line(1.0), empty_line(2), empty_line(2)),), None)
    one = GlassEdits("g1", line(1.0), empty_line(1), empty_line(1))
    with pytest.raises(ValueError):
        Edits((0.0,), (one, one), None)
    with pytest.raises(ValueError):
        Stretch(2.0, 2.0)
    with pytest.raises(ValueError):
        Memo("m1", 1.0, None, "가" * 501)


def test_full_and_empty_follow_the_line_at_the_glass_top_and_bottom():
    oil = line(100.0, 100.9, 101.5, 300.0, 499.0, 520.0, None)
    assert level_states(oil, GLASS) == (
        LevelState.FULL, LevelState.FULL, None, None, LevelState.EMPTY, LevelState.EMPTY, None,
    )


def test_runs_join_equal_neighbours_and_skip_none():
    assert runs(("A", "A", None, "A", "B", "B")) == (Run("A", 0, 2), Run("A", 3, 4), Run("B", 4, 6))
    assert runs(()) == ()


def test_coverage_counts_empty_and_cannot_judge_once_each():
    times = (0.0, 0.5, 1.0, 1.5, 2.0)
    glass = GlassEdits("g1", line(200.0, None, None, 210.0, 220.0), empty_line(5), empty_line(5),
                       cannot_judge=(Stretch(1.0, 2.0),))
    found = coverage(times, glass)
    assert found == Coverage(total=5, empty=1, cannot_judge=2)  # the empty sample at 1.0 is "cannot judge"
    assert (found.valid, found.valid_ratio) == (2, 0.4)


def test_reanalysis_keeps_every_sample_the_new_range_still_has():
    # old range 0-2 s, new range 1-3 s, with times shifted by a frame
    old_glass = GlassEdits(
        "g1",
        Line((200.0, 201.0, None, 230.0, 240.0), (D, E, E, W, D)),
        Line((None, 150.0, None, None, 160.0), (D, W, D, D, W)),
        line(None, None, None, None, None),
        cannot_judge=(Stretch(0.2, 1.2), Stretch(0.0, 0.4)),
        memos=(Memo("m1", 0.5, 201.0, "거품"), Memo("m2", 1.5, None, "확인")),
    )
    old = Edits((0.0, 0.5, 1.0, 1.5, 2.0), (old_glass,), 0.5)
    new = analysis([1.02, 1.52, 2.02, 2.52, 3.02], ("g1", line(300.0, 301.0, 302.0, 303.0, 304.0)))

    merged, dropped = merge_reanalysis(old, new, 1.5)
    glass = merged.glass("g1")
    assert merged.times == new.times and merged.compressor_start_sec == 1.5
    assert glass.oil == Line((None, 230.0, 240.0, 303.0, 304.0), (E, W, D, D, D))  # a deleted sample stays empty
    assert glass.foam == Line((None, None, 160.0, None, None), (D, D, W, D, D))
    assert glass.cannot_judge == (Stretch(1.02, 1.2),)
    assert glass.memos == (Memo("m2", 1.5, None, "확인"),)
    assert dropped == Dropped(oil_samples=1, foam_samples=1, stretches=1, memos=1)
    assert dropped.anything


def test_reanalysis_drafts_a_new_glass_and_reports_a_lost_one():
    old = Edits((0.0, 0.5), (GlassEdits("gone", line(1.0, 2.0), empty_line(2), empty_line(2)),), None)
    merged, dropped = merge_reanalysis(old, analysis([0.0, 0.5], ("g2", line(5.0, 6.0))), None)
    assert merged.glass("g2").oil == line(5.0, 6.0)
    assert dropped.glasses == ("gone",)
    same, nothing = merge_reanalysis(merged, analysis([0.0, 0.5], ("g2", line(7.0, 8.0))), None)
    assert same.glass("g2").oil == line(5.0, 6.0) and not nothing.anything
