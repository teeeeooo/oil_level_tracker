"""Ports: what the use cases need from outside. Adapters implement them."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from oil_tracker.domain.recipe import Recipe


class RecipeNotFound(LookupError):
    pass


class RecipeNameTaken(ValueError):
    pass


@dataclass(frozen=True)
class RecipeListing:
    recipes: tuple[Recipe, ...]
    unreadable: tuple[tuple[str, str], ...]  # (file name, reason)


class RecipeStore(Protocol):
    def list_recipes(self) -> RecipeListing: ...

    def load(self, recipe_id: str) -> Recipe: ...

    def save(self, recipe: Recipe) -> None:
        """Create or replace the Recipe with this id. Renaming moves its file."""
        ...


class VideoUnreadable(ValueError):
    pass


@dataclass(frozen=True)
class VideoInfo:
    name: str
    width: int
    height: int
    fps: float
    frame_count: int

    @property
    def duration_sec(self) -> float:
        return self.frame_count / self.fps


@dataclass(frozen=True)
class Frame:
    """One decoded source frame. The image is opaque to the use cases."""

    index: int
    time_sec: float
    jpeg: bytes


class OpenVideo(Protocol):
    info: VideoInfo

    def frame_at(self, time_sec: float, *, max_size: int | None = None) -> Frame:
        """The frame shown at time_sec, clamped to the video. max_size limits the longer side."""
        ...

    def close(self) -> None: ...


class VideoOpener(Protocol):
    def __call__(self, path: Path) -> OpenVideo:
        """Raise VideoUnreadable when the file cannot be decoded."""
        ...
