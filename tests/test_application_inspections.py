from dataclasses import replace
from itertools import count
from pathlib import Path

import pytest

from oil_tracker.application.inspections import (
    GlassPosition,
    InspectionLocked,
    InspectionSetup,
    Inspections,
    InvalidSetup,
)
from oil_tracker.application.ports import (
    AnalysisCancelled,
    GlassImages,
    ImageLayout,
    InspectionEntry,
    InspectionListing,
    InspectionNotFound,
    RecipeListing,
    RecipeNotFound,
    StoredAnalysis,
    VideoAnalysis,
    VideoInfo,
    VideoUnreadable,
)
from oil_tracker.application.videos import VideoSessions
from oil_tracker.domain.enums import InspectionState, JudgmentMode, SampleOrigin
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import AnalysisSettings, GlassDraft
from oil_tracker.domain.line import Line
from oil_tracker.domain.recipe import Glass, JudgmentRule, Recipe, ReferenceFrame

RECIPE = Recipe(
    "r1", "2호기", ReferenceFrame(1280, 720, "SPL4.mp4", 0.0, b"jpeg"),
    (Glass("g1", "BASE", Ellipse(640, 360, 80, 200), 380),), "c", "u",
)
HD_RECIPE = Recipe(
    "r2", "HD", ReferenceFrame(1920, 1080, "hd.mp4", 0.0, b"jpeg"),
    (Glass("g9", "MAIN", Ellipse(900, 500, 80, 200), 520, JudgmentRule(JudgmentMode.HOLD_BELOW_ZERO)),), "c", "u",
)
SETTINGS = AnalysisSettings(0.0, 9.0, 1.0)


class FakeInspectionStore:
    location = Path("/inspections")

    def __init__(self):
        self.saved, self.analyses, self.cleared = {}, {}, []

    def create(self, inspection):
        self.saved[inspection.id] = inspection
        return f"folder-{inspection.id}"

    def list_inspections(self):
        return InspectionListing(tuple(InspectionEntry(f"folder-{i.id}", i) for i in self.saved.values()), ())

    def load(self, inspection_id):
        if inspection_id not in self.saved:
            raise InspectionNotFound(inspection_id)
        return self.saved[inspection_id]

    def save(self, inspection):
        assert inspection.id in self.saved
        self.saved[inspection.id] = inspection

    def save_analysis(self, inspection_id, analysis, images):
        self.analyses[inspection_id] = (analysis, tuple(images))

    def load_analysis(self, inspection_id):
        if inspection_id not in self.analyses:
            return None
        analysis, images = self.analyses[inspection_id]
        return StoredAnalysis(analysis, tuple(ImageLayout(i.glass_id, i.y0, i.rows, len(i.context_png)) for i in images))

    def clear_analysis(self, inspection_id):
        self.cleared.append(inspection_id)
        self.analyses.pop(inspection_id, None)

    def image_piece(self, inspection_id, glass_id, kind, index):
        return f"{inspection_id}/{glass_id}/{kind}-{index}".encode()


class FakeRecipeStore:
    location = Path("/recipes")

    def __init__(self, *recipes):
        self.saved = {r.id: r for r in recipes}

    def list_recipes(self):
        return RecipeListing(tuple(self.saved.values()), (("broken.recipe.json", "JSON 형식이 아닙니다."),))

    def load(self, recipe_id):
        if recipe_id not in self.saved:
            raise RecipeNotFound(recipe_id)
        return self.saved[recipe_id]

    def save(self, recipe):
        self.saved[recipe.id] = recipe


class FakeVideo:
    def __init__(self, path):
        width, height = (1920, 1080) if "hd" in path.name else (1280, 720)
        self.info = VideoInfo(path.name, width, height, 10.0, 100, 5_000)

    def frame_at(self, time_sec, *, max_size=None):
        raise AssertionError("the inspection use cases decode no frame")

    def close(self):
        pass


class FakeAnalyser:
    def __init__(self):
        self.outcome = "ok"
        self.calls = []

    def analyse(self, path, glasses, settings, progress, cancelled):
        self.calls.append((path, glasses, settings))
        progress(5, 10)
        if self.outcome == "cancel":
            raise AnalysisCancelled()
        if self.outcome == "fail":
            raise VideoUnreadable("영상을 열 수 없습니다: SPL4.mp4")
        oil = Line((400.0, None), (SampleOrigin.DRAFT,) * 2)
        return VideoAnalysis(
            (0.0, 0.5),
            tuple(GlassDraft(g.id, oil) for g in glasses),
            tuple(GlassImages(g.id, 160, 400, (b"png",), (b"bg",)) for g in glasses),
        )


class FakeDesktop:
    def __init__(self):
        self.opened = []

    def pick_video(self):
        return None

    def open_folder(self, folder):
        self.opened.append(folder)


@pytest.fixture
def world():
    ids = count(1)
    new_id = lambda: f"id{next(ids)}"  # noqa: E731
    opened = []

    def opener(path):
        opened.append(path)
        return FakeVideo(path)

    times = iter(f"t{n}" for n in count(1))
    store, recipes, analyser, desktop = FakeInspectionStore(), FakeRecipeStore(RECIPE, HD_RECIPE), FakeAnalyser(), FakeDesktop()
    hashed = []

    def hasher(path):
        hashed.append(path)
        if path.name == "unreadable.mp4":
            raise OSError("읽기 실패")
        return "abc123"

    inspections = Inspections(
        store, recipes, VideoSessions(opener, new_id), analyser, hasher, desktop, lambda: next(times), new_id
    )
    return inspections, store, recipes, analyser, desktop, opened, hashed


def setup_for(video_id=None, inspection_id=None, recipe=RECIPE, settings=SETTINGS, **moved):
    positions = tuple(
        GlassPosition(g.id, moved.get(g.id, g.ellipse), g.zero_line_y) for g in recipe.glasses
    )
    return InspectionSetup(inspection_id, video_id, recipe.id, positions, settings)


def new_inspection(inspections, name="SPL4.mp4", **changes):
    video = inspections.videos.open(Path("/videos") / name)
    return inspections.prepare(setup_for(video.id, **changes)).inspection


def test_recipe_choices_grey_out_other_frame_sizes(world):
    inspections = world[0]
    video = inspections.videos.open(Path("/videos/SPL4.mp4"))
    result = inspections.recipe_choices(video.id)
    assert [(c.recipe.id, c.problem is None) for c in result.choices] == [("r1", True), ("r2", False)]
    assert "1920×1080" in result.choices[1].problem
    assert result.unreadable == (("broken.recipe.json", "JSON 형식이 아닙니다."),)


def test_check_reports_problems_and_writes_nothing(world):
    inspections, store = world[0], world[1]
    video = inspections.videos.open(Path("/videos/SPL4.mp4"))
    problems = inspections.check(setup_for(video.id, settings=AnalysisSettings(0.0, 9.0)))
    assert [p.field for p in problems] == ["compressor_start_sec"]
    assert inspections.check(setup_for(video.id)) == ()
    assert store.saved == {}


def test_starting_writes_the_inspection_with_its_own_recipe_copy(world):
    inspections, store, recipes = world[0], world[1], world[2]
    moved = Ellipse(650, 362, 80, 200)
    inspection = new_inspection(inspections, g1=moved)
    assert store.saved[inspection.id] == inspection
    assert (inspection.created_at, inspection.state, inspection.settings) == ("t1", InspectionState.NOT_ANALYSED, SETTINGS)
    video = inspection.video
    assert (video.path, video.name, video.size_bytes, video.width, video.height) == (
        str(Path("/videos/SPL4.mp4")), "SPL4.mp4", 5_000, 1280, 720,
    )
    assert video.sha256 is None
    glass = inspection.recipe.glasses[0]
    assert (glass.id, glass.name, glass.ellipse, glass.judgment_rule) == ("g1", "BASE", moved, RECIPE.glasses[0].judgment_rule)
    assert recipes.saved["r1"] == RECIPE  # the Recipe itself is untouched


def test_problems_write_nothing(world):
    inspections, store = world[0], world[1]
    video = inspections.videos.open(Path("/videos/hd.mp4"))
    result = inspections.prepare(setup_for(video.id))
    assert result.inspection is None and [p.field for p in result.problems] == ["recipe"]
    assert store.saved == {}


def test_the_setup_must_fit_its_recipe(world):
    inspections = world[0]
    video = inspections.videos.open(Path("/videos/SPL4.mp4"))
    good = setup_for(video.id)
    with pytest.raises(InvalidSetup):
        inspections.check(replace(good, positions=()))
    with pytest.raises(InvalidSetup):
        inspections.check(replace(good, positions=good.positions * 2))
    with pytest.raises(InvalidSetup):
        inspections.check(replace(good, video_id=None))
    with pytest.raises(RecipeNotFound):
        inspections.check(replace(good, recipe_id="gone"))


def test_the_analysis_stores_its_result_and_the_source_sha256(world):
    inspections, store, _, analyser, _, _, hashed = world
    inspection = new_inspection(inspections)
    calls = []
    analysed = inspections.analyse(inspection.id, lambda d, t: calls.append((d, t)), lambda: False)
    assert analysed.state is InspectionState.ANALYSED and analysed.failure is None
    assert analysed.video.sha256 == "abc123" and store.saved[inspection.id] == analysed
    assert hashed == [Path("/videos/SPL4.mp4")]
    assert analyser.calls == [(Path("/videos/SPL4.mp4"), inspection.recipe.glasses, SETTINGS)]
    assert calls == [(5, 10)]
    analysis, images = store.analyses[inspection.id]
    assert analysis.times == (0.0, 0.5) and analysis.finished_at == "t2"
    assert [d.glass_id for d in analysis.drafts] == ["g1"] and [i.glass_id for i in images] == ["g1"]
    stored = inspections.result(inspection.id)
    assert stored.images == (ImageLayout("g1", 160, 400, 1),)
    assert inspections.image_piece(inspection.id, "g1", "context", 0) == f"{inspection.id}/g1/context-0".encode()
    assert store.cleared == [inspection.id]  # a stale cache goes first


def test_a_cancelled_analysis_keeps_the_setup(world):
    inspections, store, _, analyser, _, _, _ = world
    inspection = new_inspection(inspections)
    analyser.outcome = "cancel"
    with pytest.raises(AnalysisCancelled):
        inspections.analyse(inspection.id, lambda d, t: None, lambda: True)
    kept = store.saved[inspection.id]
    assert (kept.state, kept.failure, kept.settings) == (InspectionState.NOT_ANALYSED, None, SETTINGS)
    assert store.analyses == {} and inspections.result(inspection.id) is None


def test_a_failed_analysis_records_its_reason(world):
    inspections, store, _, analyser, _, _, _ = world
    inspection = new_inspection(inspections)
    analyser.outcome = "fail"
    with pytest.raises(VideoUnreadable):
        inspections.analyse(inspection.id, lambda d, t: None, lambda: False)
    failed = store.saved[inspection.id]
    assert failed.state is InspectionState.FAILED
    assert failed.failure == "영상을 열 수 없습니다: SPL4.mp4"
    assert store.analyses == {}


def test_an_unreadable_source_for_the_sha256_fails_the_analysis(world):
    inspections, store = world[0], world[1]
    inspection = new_inspection(inspections, name="unreadable.mp4")
    with pytest.raises(OSError):
        inspections.analyse(inspection.id, lambda d, t: None, lambda: False)
    failed = store.saved[inspection.id]
    assert failed.state is InspectionState.FAILED and failed.failure.startswith("파일을 읽거나 쓸 수 없습니다")
    assert store.analyses == {}


def test_a_failed_inspection_can_be_set_up_again(world):
    inspections, store, recipes, analyser, _, _, _ = world
    inspection = new_inspection(inspections)
    analyser.outcome = "fail"
    with pytest.raises(VideoUnreadable):
        inspections.analyse(inspection.id, lambda d, t: None, lambda: False)
    recipes.save(replace(RECIPE, name="renamed later"))
    other = inspections.videos.open(Path("/videos/hd.mp4"))
    again = inspections.prepare(
        setup_for(other.id, inspection.id, settings=AnalysisSettings(1.0, 8.0, 2.0), g1=Ellipse(630, 360, 80, 200))
    ).inspection
    assert (again.state, again.failure, again.settings) == (InspectionState.NOT_ANALYSED, None, AnalysisSettings(1.0, 8.0, 2.0))
    assert again.video == inspection.video  # an existing inspection keeps its video
    assert again.recipe.name == "2호기"  # its own copy, not the Recipe as edited since
    assert again.recipe.glasses[0].ellipse.center_x == 630
    assert again.created_at == inspection.created_at


def test_another_recipe_replaces_the_copy(world):
    inspections = world[0]
    inspection = new_inspection(inspections)
    hd = replace(HD_RECIPE, reference_frame=replace(HD_RECIPE.reference_frame, width=1280, height=720),
                 glasses=(replace(HD_RECIPE.glasses[0], ellipse=Ellipse(600, 360, 80, 200), zero_line_y=380),))
    world[2].save(hd)
    again = inspections.prepare(setup_for(None, inspection.id, recipe=hd)).inspection
    assert again.recipe.id == "r2" and [g.id for g in again.recipe.glasses] == ["g9"]


def test_an_analysed_inspection_is_locked(world):
    inspections = world[0]
    inspection = new_inspection(inspections)
    inspections.analyse(inspection.id, lambda d, t: None, lambda: False)
    with pytest.raises(InspectionLocked):
        inspections.check(setup_for(None, inspection.id))
    with pytest.raises(InspectionLocked):
        inspections.prepare(setup_for(None, inspection.id))
    with pytest.raises(InspectionLocked):
        inspections.analyse(inspection.id, lambda d, t: None, lambda: False)


def test_listing_opening_and_the_folder(world):
    inspections, _, _, _, desktop, opened, _ = world
    inspection = new_inspection(inspections)
    assert [e.inspection.id for e in inspections.list().inspections] == [inspection.id]
    assert inspections.load(inspection.id) == inspection
    video = inspections.open_video(inspection.id)
    assert opened[-1] == Path("/videos/SPL4.mp4") and video.info.name == "SPL4.mp4"
    inspections.open_folder()
    assert desktop.opened == [Path("/inspections")]
    with pytest.raises(InspectionNotFound):
        inspections.load("missing")
