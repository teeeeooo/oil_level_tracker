"""Recipe use cases: list, load, open a sample video, save (Product SSOT §3, §5)."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from oil_tracker.domain.recipe import Glass, Recipe, RecipeProblem, ReferenceFrame, recipe_problems

from .ports import Desktop, RecipeListing, RecipeNameTaken, RecipeStore
from .videos import OpenedVideo, VideoSessions

REFERENCE_MAX_SIZE = 1280


class VideoDoesNotFit(ValueError):
    pass


@dataclass(frozen=True)
class ReferenceChoice:
    """The open video and time on screen when the user saved."""

    video_id: str
    time_sec: float


@dataclass(frozen=True)
class RecipeDraft:
    id: str | None  # None for a new Recipe
    name: str
    glasses: tuple[Glass, ...]  # the editor gives every Glass its id
    reference: ReferenceChoice | None  # None keeps the stored reference frame


@dataclass(frozen=True)
class SaveResult:
    recipe: Recipe | None
    problems: tuple[RecipeProblem, ...] = ()


class Recipes:
    def __init__(
        self,
        store: RecipeStore,
        videos: VideoSessions,
        desktop: Desktop,
        now: Callable[[], str],
        new_id: Callable[[], str],
    ) -> None:
        self.store = store
        self.videos = videos
        self.desktop = desktop
        self._now = now
        self._new_id = new_id
        self._save_lock = threading.Lock()

    def list(self) -> RecipeListing:
        return self.store.list_recipes()

    def load(self, recipe_id: str) -> Recipe:
        return self.store.load(recipe_id)

    def pick_sample_video(self) -> Path | None:
        return self.desktop.pick_video()

    def open_folder(self) -> None:
        self.desktop.open_folder(self.store.location)

    def open_sample_video(self, path: Path, recipe_id: str | None = None) -> OpenedVideo:
        """Open a video to draw on. An existing Recipe accepts only its own frame size."""
        opened = self.videos.open(path)
        if recipe_id is not None:
            recipe = self.store.load(recipe_id)
            if not recipe.matches_frame_size(opened.info.width, opened.info.height):
                self.videos.close(opened.id)
                raise VideoDoesNotFit(_size_message(opened.info.width, opened.info.height, recipe))
        return opened

    def save(self, draft: RecipeDraft) -> SaveResult:
        with self._save_lock:
            existing = self.store.load(draft.id) if draft.id is not None else None
            if draft.reference is not None:
                info = self.videos.info(draft.reference.video_id)
                if existing is not None and not existing.matches_frame_size(info.width, info.height):
                    return _problem("reference_frame", _size_message(info.width, info.height, existing))
                frame = self.videos.frame(
                    draft.reference.video_id, draft.reference.time_sec, max_size=REFERENCE_MAX_SIZE
                )
                reference = ReferenceFrame(info.width, info.height, info.name, frame.time_sec, frame.jpeg)
            elif existing is not None:
                reference = existing.reference_frame
            else:
                return _problem("reference_frame", "영상을 열어 기준 프레임을 정하세요.")

            now = self._now()
            recipe = Recipe(
                id=existing.id if existing is not None else self._new_id(),
                name=draft.name.strip(),
                reference_frame=reference,
                glasses=tuple(
                    Glass(g.id, g.name.strip(), g.ellipse, g.zero_line_y, g.judgment_rule) for g in draft.glasses
                ),
                created_at=existing.created_at if existing is not None else now,
                updated_at=now,
            )
            problems = recipe_problems(recipe)
            if problems:
                return SaveResult(None, tuple(problems))
            try:
                self.store.save(recipe)
            except RecipeNameTaken as error:
                return _problem("name", str(error))
            return SaveResult(recipe)


def _problem(field: str, message: str) -> SaveResult:
    return SaveResult(None, (RecipeProblem(field, message),))


def _size_message(width: int, height: int, recipe: Recipe) -> str:
    frame = recipe.reference_frame
    return f"영상 해상도 {width}×{height}가 이 Recipe의 {frame.width}×{frame.height}와 다릅니다."
