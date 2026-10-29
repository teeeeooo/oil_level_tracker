from dataclasses import replace
from itertools import count
from pathlib import Path

import pytest

from oil_tracker.application.ports import Frame, RecipeListing, RecipeNameTaken, RecipeNotFound, VideoInfo
from oil_tracker.application.recipes import RecipeDraft, Recipes, ReferenceChoice, VideoDoesNotFit
from oil_tracker.application.videos import UnknownVideo, VideoSessions
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.recipe import Glass


class FakeStore:
    location = Path("/recipes")

    def __init__(self):
        self.saved = {}
        self.taken_names = set()

    def list_recipes(self):
        return RecipeListing(tuple(self.saved.values()), ())

    def load(self, recipe_id):
        if recipe_id not in self.saved:
            raise RecipeNotFound(recipe_id)
        return self.saved[recipe_id]

    def save(self, recipe):
        if recipe.name in self.taken_names:
            raise RecipeNameTaken("taken")
        self.saved[recipe.id] = recipe


class FakeVideo:
    def __init__(self, name, width, height):
        self.info = VideoInfo(name, width, height, 10.0, 100)
        self.closed = False
        self.requests = []

    def frame_at(self, time_sec, *, max_size=None):
        self.requests.append((time_sec, max_size))
        index = round(time_sec * 10)
        return Frame(index, index / 10, f"jpeg-{index}".encode())

    def close(self):
        self.closed = True


class FakeDesktop:
    def __init__(self):
        self.opened = []

    def pick_video(self):
        return Path("/videos/picked.mp4")

    def open_folder(self, folder):
        self.opened.append(folder)


@pytest.fixture
def world():
    ids = count(1)
    store, desktop, opened = FakeStore(), FakeDesktop(), {}

    def opener(path):
        width, height = (1920, 1080) if "hd" in path.name else (1280, 720)
        opened[path.name] = FakeVideo(path.name, width, height)
        return opened[path.name]

    new_id = lambda: f"id{next(ids)}"  # noqa: E731
    videos = VideoSessions(opener, new_id)
    times = iter(["t1", "t2", "t3", "t4"])
    recipes = Recipes(store, videos, desktop, lambda: next(times), new_id)
    return recipes, store, opened, desktop


GLASS = Glass("g1", " BASE ", Ellipse(640, 360, 80, 200), 380)


def draft(**changes):
    return replace(RecipeDraft(id=None, name=" 2호기 ", glasses=(GLASS,), reference=None), **changes)


def test_new_recipe_takes_the_frame_on_screen_as_reference(world):
    recipes, store, opened, _ = world
    video = recipes.open_sample_video(Path("/videos/SPL4.mp4"))
    result = recipes.save(draft(reference=ReferenceChoice(video.id, 12.46)))
    assert result.problems == ()
    recipe = result.recipe
    assert store.saved[recipe.id] == recipe
    assert (recipe.name, recipe.glasses[0].name) == ("2호기", "BASE")
    assert (recipe.created_at, recipe.updated_at) == ("t1", "t1")
    frame = recipe.reference_frame
    assert (frame.width, frame.height, frame.source_name) == (1280, 720, "SPL4.mp4")
    assert (frame.time_sec, frame.jpeg) == (12.5, b"jpeg-125")
    assert opened["SPL4.mp4"].requests[-1] == (12.46, 1280)


def test_saving_without_a_video_keeps_the_stored_reference(world):
    recipes, _, _, _ = world
    video = recipes.open_sample_video(Path("/videos/SPL4.mp4"))
    first = recipes.save(draft(reference=ReferenceChoice(video.id, 1.0))).recipe
    again = recipes.save(draft(id=first.id, name="3호기", reference=None)).recipe
    assert again.id == first.id
    assert again.reference_frame == first.reference_frame
    assert (again.created_at, again.updated_at) == ("t1", "t2")


def test_a_new_recipe_needs_a_video(world):
    recipes, store, _, _ = world
    result = recipes.save(draft())
    assert [p.field for p in result.problems] == ["reference_frame"]
    assert store.saved == {}


def test_domain_problems_block_saving(world):
    recipes, store, _, _ = world
    video = recipes.open_sample_video(Path("/videos/SPL4.mp4"))
    bad = replace(GLASS, zero_line_y=999)
    result = recipes.save(draft(glasses=(bad,), reference=ReferenceChoice(video.id, 0)))
    assert [(p.field, p.glass_id) for p in result.problems] == [("zero_line_y", "g1")]
    assert store.saved == {}


def test_a_taken_name_is_a_name_problem(world):
    recipes, store, _, _ = world
    store.taken_names.add("2호기")
    video = recipes.open_sample_video(Path("/videos/SPL4.mp4"))
    result = recipes.save(draft(reference=ReferenceChoice(video.id, 0)))
    assert [p.field for p in result.problems] == ["name"]


def test_an_existing_recipe_refuses_a_video_of_another_size(world):
    recipes, _, opened, _ = world
    video = recipes.open_sample_video(Path("/videos/SPL4.mp4"))
    recipe = recipes.save(draft(reference=ReferenceChoice(video.id, 0))).recipe
    with pytest.raises(VideoDoesNotFit):
        recipes.open_sample_video(Path("/videos/hd.mp4"), recipe.id)
    assert opened["hd.mp4"].closed
    # a video opened without the Recipe id is still refused at save
    hd = recipes.open_sample_video(Path("/videos/hd.mp4"))
    result = recipes.save(draft(id=recipe.id, reference=ReferenceChoice(hd.id, 0)))
    assert [p.field for p in result.problems] == ["reference_frame"]


def test_unknown_ids(world):
    recipes, _, _, _ = world
    with pytest.raises(RecipeNotFound):
        recipes.save(draft(id="missing"))
    with pytest.raises(UnknownVideo):
        recipes.save(draft(reference=ReferenceChoice("nope", 0)))


def test_desktop_actions_go_through_the_port(world):
    recipes, _, _, desktop = world
    assert recipes.pick_sample_video() == Path("/videos/picked.mp4")
    recipes.open_folder()
    assert desktop.opened == [Path("/recipes")]


def test_closing_videos(world):
    recipes, _, opened, _ = world
    first = recipes.open_sample_video(Path("/videos/a.mp4"))
    recipes.open_sample_video(Path("/videos/b.mp4"))
    recipes.videos.close(first.id)
    assert opened["a.mp4"].closed and not opened["b.mp4"].closed
    recipes.videos.close_all()
    assert opened["b.mp4"].closed


def test_check_reports_problems_without_decoding_or_writing(world):
    recipes, store, opened, _ = world
    video = recipes.open_sample_video(Path("/videos/SPL4.mp4"))
    bad = replace(GLASS, zero_line_y=999)
    problems = recipes.check(draft(glasses=(bad,), reference=ReferenceChoice(video.id, 3.0)))
    assert [p.field for p in problems] == ["zero_line_y"]
    assert recipes.check(draft(reference=ReferenceChoice(video.id, 3.0))) == ()
    assert recipes.check(draft()) and store.saved == {}
    assert opened["SPL4.mp4"].requests == []
