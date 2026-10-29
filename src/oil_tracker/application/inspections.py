"""Inspection use cases: the list, a new inspection's Recipe, the setup, the analysis and its result.

Product SSOT §3 and §8; the screens are in DESIGN.md §5. The analysis itself runs as a job in
adapters/http, which calls analyse() on its own thread.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

from oil_tracker.domain.enums import InspectionState
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import Analysis, AnalysisSettings, Inspection, SourceVideo, setup_problems
from oil_tracker.domain.problems import Problem
from oil_tracker.domain.recipe import Recipe

from .ports import (
    AnalysisCancelled,
    Desktop,
    InspectionListing,
    InspectionStore,
    RecipeStore,
    SourceHasher,
    StoredAnalysis,
    VideoAnalyser,
    VideoUnreadable,
)
from .videos import OpenedVideo, VideoSessions


class InspectionLocked(ValueError):
    """An analysed inspection keeps its setup; re-analysis comes with the editor (V2-3)."""


class InvalidSetup(ValueError):
    """The request does not fit its Recipe or video: a client error, not a problem to show."""


@dataclass(frozen=True)
class RecipeChoice:
    recipe: Recipe
    problem: str | None  # why it cannot be used with the video; None when it fits


@dataclass(frozen=True)
class RecipeChoices:
    choices: tuple[RecipeChoice, ...]
    unreadable: tuple[tuple[str, str], ...]  # (file name, reason)


@dataclass(frozen=True)
class GlassPosition:
    glass_id: str
    ellipse: Ellipse
    zero_line_y: float


@dataclass(frozen=True)
class InspectionSetup:
    inspection_id: str | None              # None until the analysis first starts (Product SSOT §3)
    video_id: str | None                   # a new inspection's open video; an existing one keeps its own
    recipe_id: str                         # the Recipe the copy comes from
    positions: tuple[GlassPosition, ...]   # every Glass of that Recipe, corrected for this inspection only
    settings: AnalysisSettings


@dataclass(frozen=True)
class SetupResult:
    inspection: Inspection | None
    problems: tuple[Problem, ...] = ()


class Inspections:
    def __init__(
        self,
        store: InspectionStore,
        recipes: RecipeStore,
        videos: VideoSessions,
        analyser: VideoAnalyser,
        hasher: SourceHasher,
        desktop: Desktop,
        now: Callable[[], str],
        new_id: Callable[[], str],
    ) -> None:
        self.store = store
        self.recipes = recipes
        self.videos = videos
        self.analyser = analyser
        self._hasher = hasher
        self.desktop = desktop
        self._now = now
        self._new_id = new_id

    def list(self) -> InspectionListing:
        return self.store.list_inspections()

    def load(self, inspection_id: str) -> Inspection:
        return self.store.load(inspection_id)

    def open_folder(self) -> None:
        self.desktop.open_folder(self.store.location)

    def recipe_choices(self, video_id: str) -> RecipeChoices:
        """Every Recipe, with the reason one of another frame size cannot be picked."""
        info = self.videos.info(video_id)
        listing = self.recipes.list_recipes()
        return RecipeChoices(
            tuple(RecipeChoice(r, r.frame_size_message(info.width, info.height)) for r in listing.recipes),
            listing.unreadable,
        )

    def open_video(self, inspection_id: str) -> OpenedVideo:
        """Open an existing inspection's own video for its setup screen."""
        return self.videos.open(Path(self.store.load(inspection_id).video.path))

    def check(self, setup: InspectionSetup) -> tuple[Problem, ...]:
        """The problems that block "분석 시작", without writing anything."""
        _, video, recipe = self._resolve(setup)
        return tuple(setup_problems(video, recipe, setup.settings))

    def prepare(self, setup: InspectionSetup) -> SetupResult:
        """Write the inspection with its Recipe copy, ready to analyse: the folder is made here."""
        existing, video, recipe = self._resolve(setup)
        problems = setup_problems(video, recipe, setup.settings)
        if problems:
            return SetupResult(None, tuple(problems))
        if existing is None:
            inspection = Inspection(self._new_id(), self._now(), video, recipe, setup.settings)
            self.store.create(inspection)
        else:
            inspection = replace(
                existing, recipe=recipe, settings=setup.settings, state=InspectionState.NOT_ANALYSED, failure=None
            )
            self.store.save(inspection)
        return SetupResult(inspection)

    def analyse(
        self,
        inspection_id: str,
        progress: Callable[[int, int], None],
        cancelled: Callable[[], bool],
    ) -> Inspection:
        """Analyse a prepared inspection; it ends ANALYSED, FAILED, or NOT_ANALYSED when cancelled.

        The source SHA-256 runs on a second thread meanwhile. A cancel or a failure clears the cache,
        is recorded, then raised again.
        """
        inspection = self.store.load(inspection_id)
        if inspection.state is InspectionState.ANALYSED:
            raise InspectionLocked("이미 분석이 끝난 검사입니다.")
        self.store.clear_analysis(inspection_id)
        path = Path(inspection.video.path)
        hashing = _Background(lambda: self._hasher(path))
        try:
            found = self.analyser.analyse(path, inspection.recipe.glasses, inspection.settings, progress, cancelled)
            sha256 = hashing.result()
            analysis = Analysis(found.times, found.drafts, self._now())
            self.store.save_analysis(inspection_id, analysis, found.images)
        except AnalysisCancelled:
            self.store.clear_analysis(inspection_id)
            self.store.save(replace(inspection, state=InspectionState.NOT_ANALYSED, failure=None))
            raise
        except Exception as failure:
            self.store.clear_analysis(inspection_id)
            self.store.save(replace(inspection, state=InspectionState.FAILED, failure=failure_reason(failure)))
            raise
        analysed = replace(
            inspection,
            video=replace(inspection.video, sha256=sha256),
            state=InspectionState.ANALYSED,
            failure=None,
        )
        self.store.save(analysed)
        return analysed

    def result(self, inspection_id: str) -> StoredAnalysis | None:
        return self.store.load_analysis(inspection_id)

    def image_piece(self, inspection_id: str, glass_id: str, kind: str, index: int) -> bytes:
        return self.store.image_piece(inspection_id, glass_id, kind, index)

    def _resolve(self, setup: InspectionSetup) -> tuple[Inspection | None, SourceVideo, Recipe]:
        """The existing inspection, the video and the Recipe copy with this inspection's positions."""
        existing = None
        if setup.inspection_id is not None:
            existing = self.store.load(setup.inspection_id)
            if existing.state is InspectionState.ANALYSED:
                raise InspectionLocked("분석이 끝난 검사는 설정을 바꿀 수 없습니다.")
            video = existing.video
        elif setup.video_id is not None:
            info = self.videos.info(setup.video_id)
            video = SourceVideo(
                str(self.videos.path(setup.video_id)), info.name, info.size_bytes,
                info.width, info.height, info.fps, info.frame_count,
            )
        else:
            raise InvalidSetup("새 검사에는 영상이 필요합니다.")

        if existing is not None and existing.recipe.id == setup.recipe_id:
            base = existing.recipe
        else:
            base = self.recipes.load(setup.recipe_id)
        positions = {p.glass_id: p for p in setup.positions}
        if len(positions) != len(setup.positions) or set(positions) != {g.id for g in base.glasses}:
            raise InvalidSetup("Glass 위치가 Recipe의 Glass와 맞지 않습니다.")
        glasses = tuple(
            replace(g, ellipse=positions[g.id].ellipse, zero_line_y=positions[g.id].zero_line_y)
            for g in base.glasses
        )
        return existing, video, replace(base, glasses=glasses)


def failure_reason(failure: Exception) -> str:
    """What the inspection list shows after "분석 실패"."""
    if isinstance(failure, VideoUnreadable):
        return str(failure)
    if isinstance(failure, OSError):
        return f"파일을 읽거나 쓸 수 없습니다: {failure}"
    return f"분석 중 오류가 났습니다: {type(failure).__name__}: {failure}"


class _Background[T]:
    """A function on a daemon thread; a cancelled analysis does not wait for it."""

    def __init__(self, function: Callable[[], T]) -> None:
        self._value: T | None = None
        self._error: BaseException | None = None
        self._thread = threading.Thread(target=self._run, args=(function,), name="source-sha256", daemon=True)
        self._thread.start()

    def _run(self, function: Callable[[], T]) -> None:
        try:
            self._value = function()
        except BaseException as error:  # noqa: BLE001 - handed to result()
            self._error = error

    def result(self) -> T:
        self._thread.join()
        if self._error is not None:
            raise self._error
        return self._value  # type: ignore[return-value]
