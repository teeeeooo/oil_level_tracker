import time
from dataclasses import replace
from itertools import count
from pathlib import Path

import pytest

from oil_tracker.application.editing import (
    DrawnPiece,
    Editing,
    InvalidEdits,
    NotAnalysed,
    SourceState,
)
from oil_tracker.application.ports import ImageLayout, InspectionNotFound, StoredAnalysis, StoredEdits
from oil_tracker.domain.edits import Coverage, Run, Stretch, edits_from_analysis
from oil_tracker.domain.enums import InspectionState, LevelState, SampleOrigin
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import Analysis, AnalysisSettings, GlassDraft, Inspection, SourceVideo
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass, Recipe, ReferenceFrame

D = SampleOrigin.DRAFT
GLASS = Glass("g1", "BASE", Ellipse(640, 300, 80, 200), 380)  # top y 100, bottom y 500
RECIPE = Recipe("r1", "2호기", ReferenceFrame(1280, 720, "SPL4.mp4", 0.0, b"jpeg"), (GLASS,), "c", "u")
VIDEO = SourceVideo("/videos/SPL4.mp4", "SPL4.mp4", 5_000, 1280, 720, 10.0, 100, sha256="abc123")
INSPECTION = Inspection("i1", "t0", VIDEO, RECIPE, AnalysisSettings(0.0, 2.5, 1.0), InspectionState.ANALYSED)
TIMES = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5)
DRAFT = Line((100.0, 100.5, None, 300.0, 499.5, None), (D,) * 6)
ANALYSIS = Analysis(TIMES, (GlassDraft("g1", DRAFT),), "t1")


class FakeStore:
    def __init__(self):
        self.inspections = {"i1": INSPECTION}
        self.analyses = {"i1": StoredAnalysis(ANALYSIS, (ImageLayout("g1", 90, 420, 3),))}
        self.edits = {}
        self.pieces = []

    def load(self, inspection_id):
        if inspection_id not in self.inspections:
            raise InspectionNotFound(inspection_id)
        return self.inspections[inspection_id]

    def load_analysis(self, inspection_id):
        return self.analyses.get(inspection_id)

    def load_edits(self, inspection_id):
        return self.edits.get(inspection_id)

    def save_edits(self, inspection_id, edits, saved_at):
        self.edits[inspection_id] = StoredEdits(edits, saved_at)

    def image_piece(self, inspection_id, glass_id, kind, index):
        self.pieces.append((inspection_id, glass_id, kind, index))
        return b"png"


class FakeTracer:
    def __init__(self):
        self.calls = []

    def trace(self, key, piece, pieces, points):
        self.calls.append((key, piece(0), pieces, list(points)))
        first, last = points[0][0], points[-1][0]
        return tuple(points[0][1] + k for k in range(last - first + 1))


@pytest.fixture
def world():
    store, tracer, hashes = FakeStore(), FakeTracer(), {"/videos/SPL4.mp4": "abc123"}

    def hasher(path):
        found = hashes[str(path)]
        if isinstance(found, Exception):
            raise found
        return found

    times = iter(f"s{n}" for n in count(1))
    return Editing(store, tracer, hasher, lambda: next(times)), store, tracer, hashes


def test_the_first_edits_are_the_drafts_with_what_follows_from_them(world):
    editing = world[0]
    opened = editing.open("i1")
    assert (opened.saved_at, opened.unsaved) == (None, False)
    assert opened.edits == edits_from_analysis(ANALYSIS, 1.0)
    (state,) = editing.states("i1", opened.edits)
    assert state.levels == (Run(LevelState.FULL, 0, 2), Run(LevelState.EMPTY, 4, 5))
    assert state.empty == (Run(True, 2, 3), Run(True, 5, 6))
    assert state.coverage == Coverage(total=6, empty=2, cannot_judge=0)


def test_cannot_judge_is_not_counted_as_empty(world):
    editing = world[0]
    edits = editing.open("i1").edits
    marked = replace(edits, glasses=(replace(edits.glasses[0], cannot_judge=(Stretch(0.9, 1.6),)),))
    (state,) = editing.states("i1", marked)
    assert state.empty == (Run(True, 5, 6),)
    assert state.coverage == Coverage(total=6, empty=1, cannot_judge=2)


def test_saving_and_opening_again(world):
    editing, store = world[0], world[1]
    edits = editing.open("i1").edits
    edited = replace(edits, compressor_start_sec=1.5)
    assert editing.save("i1", edited) == "s1"
    assert store.edits["i1"] == StoredEdits(edited, "s1")
    opened = editing.open("i1")
    assert (opened.edits, opened.saved_at, opened.unsaved) == (edited, "s1", False)


def test_edits_must_fit_the_analysis(world):
    editing = world[0]
    edits = editing.open("i1").edits
    with pytest.raises(InvalidEdits):
        editing.save("i1", replace(edits, times=tuple(t + 0.1 for t in TIMES)))
    with pytest.raises(InvalidEdits):
        editing.save("i1", replace(edits, glasses=(replace(edits.glasses[0], glass_id="g2"),)))
    with pytest.raises(InvalidEdits):
        editing.states("i1", replace(edits, glasses=(replace(edits.glasses[0], glass_id="g2"),)))


def test_saved_edits_left_behind_by_a_reanalysis_are_fitted_on_opening(world):
    editing, store = world[0], world[1]
    old_times = (0.0, 0.5, 1.0)
    old = edits_from_analysis(Analysis(old_times, (GlassDraft("g1", Line((200.0, 210.0, 220.0), (D,) * 3)),), "t0"), 0.5)
    store.save_edits("i1", old, "s0")
    opened = editing.open("i1")
    assert (opened.saved_at, opened.unsaved) == ("s0", True)
    assert opened.edits.times == TIMES and opened.edits.compressor_start_sec == 0.5
    assert opened.edits.glasses[0].oil.ys == (200.0, 210.0, 220.0, 300.0, 499.5, None)


def test_only_an_analysed_inspection_opens(world):
    editing, store = world[0], world[1]
    store.inspections["i1"] = replace(INSPECTION, state=InspectionState.NOT_ANALYSED)
    with pytest.raises(NotAnalysed):
        editing.open("i1")
    store.inspections["i1"] = INSPECTION
    del store.analyses["i1"]
    with pytest.raises(NotAnalysed):
        editing.save("i1", edits_from_analysis(ANALYSIS, None))
    with pytest.raises(InspectionNotFound):
        editing.open("missing")


def test_the_point_line_goes_through_the_context_image(world):
    editing, store, tracer = world[0], world[1], world[2]
    drawn = editing.point_line("i1", "g1", [(1, 150.4), (4, 600.0)])
    assert drawn == DrawnPiece(1, (150.0, 151.0, 152.0, 153.0))  # rows from y0 90, the last clamped to the image
    key, piece, pieces, points = tracer.calls[0]
    assert (key, piece, pieces, points) == ("i1/g1/t1", b"png", 3, [(1, 60), (4, 419)])
    assert store.pieces == [("i1", "g1", "context", 0)]


@pytest.mark.parametrize("points", [[(1, 150.0)], [(3, 150.0), (1, 150.0)], [(1, 150.0), (1, 160.0)], [(1, 150.0), (6, 150.0)]])
def test_the_point_line_needs_points_in_time_order(world, points):
    with pytest.raises(InvalidEdits):
        world[0].point_line("i1", "g1", points)


def test_the_point_line_needs_a_glass_of_the_analysis(world):
    with pytest.raises(InvalidEdits):
        world[0].point_line("i1", "g9", [(1, 150.0), (2, 150.0)])


def settled(editing, inspection_id):
    for _ in range(200):
        check = editing.source_check(inspection_id)
        if check.state is not SourceState.CHECKING:
            return check
        time.sleep(0.01)
    raise AssertionError("the source check did not end")


def test_the_source_check_compares_the_sha256_with_the_analysis(world):
    editing, _, _, hashes = world
    assert settled(editing, "i1").state is SourceState.SAME
    hashes["/videos/SPL4.mp4"] = "changed"
    assert settled(editing, "i1").state is SourceState.SAME  # a finished check stands until asked again
    editing.check_source("i1")
    different = settled(editing, "i1")
    assert different.state is SourceState.DIFFERENT and different.message
    hashes["/videos/SPL4.mp4"] = FileNotFoundError(2, "No such file")
    editing.check_source("i1")
    assert settled(editing, "i1").state is SourceState.MISSING
    hashes["/videos/SPL4.mp4"] = PermissionError(13, "Permission denied")
    editing.check_source("i1")
    assert settled(editing, "i1").state is SourceState.UNREADABLE
    assert editing.source_file("i1") == Path("/videos/SPL4.mp4")
