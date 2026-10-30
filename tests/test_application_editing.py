import time
from dataclasses import replace
from itertools import count
from pathlib import Path

import pytest

from oil_tracker.application.editing import (
    DrawnPiece,
    Editing,
    InvalidEdits,
    Locked,
    NotAnalysed,
    SourceState,
    VersionOutOfDate,
)
from oil_tracker.application.ports import ImageLayout, InspectionNotFound, StoredAnalysis, StoredEdits
from oil_tracker.domain.edits import Coverage, Decision, Run, Stretch, edits_from_analysis
from oil_tracker.domain.enums import InspectionState, LevelState, SampleOrigin, Verdict
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import Analysis, AnalysisSettings, GlassDraft, Inspection, SourceVideo
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass, Recipe, ReferenceFrame

D = SampleOrigin.DRAFT
GLASS = Glass("g1", "BASE", Ellipse(640, 300, 80, 200), 380)  # top y 100, bottom y 500
RECIPE = Recipe("r1", "2호기", ReferenceFrame(1280, 720, "SPL4.mp4", 0.0, b"jpeg"), (GLASS,), "c", "u")
VIDEO = SourceVideo("/videos/SPL4.mp4", "SPL4.mp4", 5_000, 1280, 720, 10.0, 100, sha256="abc123")
SOURCE = Path(VIDEO.path)  # compared as a path: str() spells it with "\\" on Windows
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
        self.submitted = {}
        self.copies = {}
        self.reports = {}

    def report_path(self, inspection_id, number):
        return Path(f"/reports/{inspection_id}/{number}.html")

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

    def has_edits(self, inspection_id):
        return inspection_id in self.edits

    def versions(self, inspection_id):
        return tuple(version for version, _ in self.submitted.get(inspection_id, []))

    def load_version_edits(self, inspection_id, number):
        for version, edits in self.submitted.get(inspection_id, []):
            if version.number == number:
                return StoredEdits(edits, version.submitted_at)
        raise InspectionNotFound(number)

    def load_version_inspection(self, inspection_id, number):
        self.load_version_edits(inspection_id, number)
        return self.copies[(inspection_id, number)]

    def submit(self, inspection, edits, version, report_html):
        self.reports[(inspection.id, version.number)] = report_html
        self.copies[(inspection.id, version.number)] = inspection
        self.submitted.setdefault(inspection.id, []).append((version, edits))
        self.edits.pop(inspection.id, None)

    def image_piece(self, inspection_id, glass_id, kind, index):
        self.pieces.append((inspection_id, glass_id, kind, index))
        return b"png"


class FakeReports:
    def write(self, report):
        piece = report.context_piece(report.layouts[0].glass_id, 0)
        return f"report v{report.version.number} {report.inspection.id} {len(report.edits.times)} {piece.decode()}"


class FakeTracer:
    def __init__(self):
        self.calls = []

    def trace(self, key, piece, pieces, points):
        self.calls.append((key, piece(0), pieces, list(points)))
        first, last = points[0][0], points[-1][0]
        return tuple(points[0][1] + k for k in range(last - first + 1))


class FakeDesktop:
    def __init__(self):
        self.asked = []
        self.opened = []

    def open_file(self, path):
        self.opened.append(path)

    def pick_video(self):
        return None

    def open_folder(self, folder):
        pass

    def ask_before_closing(self, ask):
        self.asked.append(ask)


@pytest.fixture
def desktop():
    return FakeDesktop()


@pytest.fixture
def world(desktop):
    store, tracer, hashes = FakeStore(), FakeTracer(), {SOURCE: "abc123"}

    def hasher(path):
        found = hashes[Path(path)]
        if isinstance(found, Exception):
            raise found
        return found

    times = iter(f"s{n}" for n in count(1))
    return Editing(store, tracer, hasher, desktop, lambda: next(times), FakeReports()), store, tracer, hashes


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
    hashes[SOURCE] = "changed"
    assert settled(editing, "i1").state is SourceState.SAME  # a finished check stands until asked again
    editing.check_source("i1")
    different = settled(editing, "i1")
    assert different.state is SourceState.DIFFERENT and different.message
    hashes[SOURCE] = FileNotFoundError(2, "No such file")
    editing.check_source("i1")
    assert settled(editing, "i1").state is SourceState.MISSING
    hashes[SOURCE] = PermissionError(13, "Permission denied")
    editing.check_source("i1")
    assert settled(editing, "i1").state is SourceState.UNREADABLE
    assert editing.source_file("i1") == SOURCE


def test_unsaved_edits_make_the_window_ask_before_closing(world, desktop):
    editing = world[0]
    editing.mark_unsaved(True)
    editing.mark_unsaved(False)
    assert desktop.asked == [True, False]


# ---- submitting and versions (Product SSOT §3, A9) ----


def checked(edits, override=None, reason=""):
    decision = Decision(override, reason, "c1")
    return replace(edits, glasses=tuple(replace(g, decision=decision) for g in edits.glasses))


def test_submitting_needs_every_glass_checked_and_locks_the_version(world, desktop):
    editing, store = world[0], world[1]
    edits = editing.open("i1").edits
    with pytest.raises(InvalidEdits, match="남은 Glass: BASE"):
        editing.submit("i1", edits)
    store.save_edits("i1", edits, "s0")
    version = editing.submit("i1", checked(edits, Verdict.PASS, "영상으로 확인"))  # unsaved edits go with it
    (glass,) = version.glasses
    assert (version.number, glass.verdict, glass.override, glass.reason, glass.checked_at) == (1, Verdict.PASS, Verdict.PASS, "영상으로 확인", "c1")
    assert glass.computed is editing.states("i1", edits)[0].judgment.verdict
    assert not store.has_edits("i1")  # the working edits went into the version
    assert store.reports[("i1", 1)] == "report v1 i1 6 png"  # with its report, from the context pieces
    editing.open_report("i1", 1)
    assert desktop.opened == [Path("/reports/i1/1.html")]

    opened = editing.open("i1")  # the latest version, read-only
    assert opened.version == 1 and opened.edits.glasses[0].decision.reason == "영상으로 확인"
    for change in (lambda: editing.save("i1", opened.edits), lambda: editing.submit("i1", opened.edits)):
        with pytest.raises(Locked):
            change()


def test_revising_starts_the_next_version_from_the_latest(world):
    editing, store = world[0], world[1]
    with pytest.raises(Locked):
        editing.revise("i1")  # nothing submitted
    first = checked(editing.open("i1").edits)
    editing.submit("i1", first)
    editing.revise("i1")
    opened = editing.open("i1")
    assert opened.version is None and opened.edits == first  # with the checks; a change takes one off
    with pytest.raises(Locked):
        editing.revise("i1")
    editing.save("i1", first)
    assert editing.submit("i1", first).number == 2
    assert [v.number for v in editing.versions("i1")] == [1, 2]
    assert editing.open("i1", 1).version == 1


def test_an_older_version_after_a_reanalysis_opens_only_as_its_report(world):
    editing, store = world[0], world[1]
    editing.submit("i1", checked(editing.open("i1").edits))
    editing.revise("i1")
    shorter = Analysis(TIMES[:4], (GlassDraft("g1", Line(DRAFT.ys[:4], (D,) * 4)),), "t2")
    store.analyses["i1"] = StoredAnalysis(shorter, store.analyses["i1"].images)
    with pytest.raises(VersionOutOfDate):
        editing.open("i1", 1)
    with pytest.raises(InspectionNotFound):
        editing.open("i1", 7)
