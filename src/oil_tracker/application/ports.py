"""Ports: what the use cases need from outside. Adapters implement them."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from oil_tracker.domain.inspection import Analysis, AnalysisSettings, GlassDraft, Inspection
from oil_tracker.domain.recipe import Glass, Recipe


class RecipeNotFound(LookupError):
    pass


class RecipeNameTaken(ValueError):
    pass


@dataclass(frozen=True)
class RecipeListing:
    recipes: tuple[Recipe, ...]
    unreadable: tuple[tuple[str, str], ...]  # (file name, reason)


class RecipeStore(Protocol):
    @property
    def location(self) -> Path:
        """The folder the Recipes live in, for display and "폴더 열기"."""
        ...

    def list_recipes(self) -> RecipeListing: ...

    def load(self, recipe_id: str) -> Recipe: ...

    def save(self, recipe: Recipe) -> None:
        """Create or replace the Recipe with this id. Renaming moves its file."""
        ...


class InspectionNotFound(LookupError):
    pass


class UnreadableAnalysis(ValueError):
    pass


@dataclass(frozen=True)
class InspectionEntry:
    folder_name: str
    inspection: Inspection


@dataclass(frozen=True)
class InspectionListing:
    inspections: tuple[InspectionEntry, ...]  # newest first
    unreadable: tuple[tuple[str, str], ...]   # (folder name, reason)


@dataclass(frozen=True)
class GlassImages:
    """One Glass's analysis pictures as encoded PNG pieces; opaque to the use cases."""

    glass_id: str
    y0: int                            # the source-frame y of the first row
    rows: int
    context_png: tuple[bytes, ...]     # pieces of at most 4,096 columns, in time order
    background_png: tuple[bytes, ...]


@dataclass(frozen=True)
class ImageLayout:
    glass_id: str
    y0: int
    rows: int
    pieces: int


@dataclass(frozen=True)
class StoredAnalysis:
    analysis: Analysis
    images: tuple[ImageLayout, ...]


class InspectionStore(Protocol):
    @property
    def location(self) -> Path:
        """The Inspections folder, for display and "폴더 열기"."""
        ...

    def create(self, inspection: Inspection) -> str:
        """Make the inspection's folder with its Recipe copy; return the folder name."""
        ...

    def list_inspections(self) -> InspectionListing: ...

    def load(self, inspection_id: str) -> Inspection: ...

    def save(self, inspection: Inspection) -> None:
        """Replace the inspection and its Recipe copy."""
        ...

    def save_analysis(self, inspection_id: str, analysis: Analysis, images: Sequence[GlassImages]) -> None:
        """Replace the cached analysis as a whole: a reader never sees half of one."""
        ...

    def load_analysis(self, inspection_id: str) -> StoredAnalysis | None: ...

    def clear_analysis(self, inspection_id: str) -> None: ...

    def image_piece(self, inspection_id: str, glass_id: str, kind: str, index: int) -> bytes:
        """`kind` is "context" or "background"."""
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


class AnalysisCancelled(Exception):
    pass


@dataclass(frozen=True)
class VideoAnalysis:
    """One pass over the range for every Glass, in the order of the Glasses given."""

    times: tuple[float, ...]            # source-video seconds of the sampled frames
    drafts: tuple[GlassDraft, ...]      # one Oil sample per time; None where the draft is empty
    images: tuple[GlassImages, ...]


class VideoAnalyser(Protocol):
    def analyse(
        self,
        path: Path,
        glasses: Sequence[Glass],
        settings: AnalysisSettings,
        progress: Callable[[int, int], None],
        cancelled: Callable[[], bool],
    ) -> VideoAnalysis:
        """Report progress as (done, total) work units and ask `cancelled` between steps.

        Raise AnalysisCancelled when it returns True, VideoUnreadable when the file cannot be decoded.
        """
        ...


class DesktopUnavailable(RuntimeError):
    pass


class Desktop(Protocol):
    def pick_video(self) -> Path | None:
        """Ask for a video file. None when the user cancels. Raise DesktopUnavailable without a window."""
        ...

    def open_folder(self, folder: Path) -> None: ...
