"""Inspection use cases: the list, a new inspection's Recipe, the setup, the analysis and its result.

Product SSOT §3, §6 (re-analysis) and §8; the screens are in DESIGN.md §5. The analysis itself runs
as a job in adapters/http, which calls analyse() on its own thread.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

from oil_tracker.domain.edits import Dropped, dropped_by_reanalysis, merge_reanalysis
from oil_tracker.domain.enums import InspectionState
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import (
    Analysis,
    AnalysisSettings,
    Inspection,
    ReportHeader,
    SourceVideo,
    analysis_times,
    inspection_name,
    setup_problems,
)
from oil_tracker.domain.problems import Problem
from oil_tracker.domain.recipe import Recipe

from .editing import Locked, is_locked
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
    name: str | None = None                # a new inspection's name as typed; an existing one keeps its own
    header: ReportHeader = ReportHeader()  # a new inspection's; an existing one's is saved by set_header


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
        existing, video, recipe = self._resolve(setup)
        return tuple(setup_problems(video, recipe, setup.settings, _name(setup, existing)))

    def dropped(self, setup: InspectionSetup) -> Dropped:
        """What re-analysing with this setup drops from the saved edits, to say before it starts (§6)."""
        existing, video, recipe = self._resolve(setup)
        saved = None if existing is None else self.store.load_edits(existing.id)
        if saved is None:
            return Dropped()
        try:
            times = analysis_times(video, setup.settings)
        except ValueError:  # an empty range, which the check reports as a problem
            return Dropped()
        return dropped_by_reanalysis(saved.edits, times, tuple(glass.id for glass in recipe.glasses))

    def prepare(self, setup: InspectionSetup) -> SetupResult:
        """The inspection with its Recipe copy, ready to analyse: the folder is made here.

        An analysed inspection is not written: a re-analysis keeps the stored setup and analysis until
        the new one is done, so a cancel or a failure leaves it as it was.
        """
        existing, video, recipe = self._resolve(setup)
        name = _name(setup, existing)
        problems = setup_problems(video, recipe, setup.settings, name)
        if problems:
            return SetupResult(None, tuple(problems))
        if existing is not None and is_locked(self.store, existing.id):
            raise Locked("제출한 버전은 다시 분석할 수 없습니다. \"고쳐서 다시 제출\"로 새 버전을 시작하세요.")
        if existing is None:
            inspection = Inspection(
                self._new_id(), self._now(), video, recipe, setup.settings, name=name, header=setup.header
            )
            self.store.create(inspection)
        else:
            inspection = replace(
                existing, recipe=recipe, settings=setup.settings, state=InspectionState.NOT_ANALYSED, failure=None
            )
            if existing.state is not InspectionState.ANALYSED:
                self.store.save(inspection)
        return SetupResult(inspection)

    def set_header(self, inspection_id: str, header: ReportHeader) -> Inspection:
        """Save the report header at once, apart from the edits (DESIGN.md §5, 검사 정보). A submitted
        version keeps its own copy; the header is locked until "고쳐서 다시 제출"."""
        if is_locked(self.store, inspection_id):
            raise Locked("제출한 버전의 검사 정보는 고칠 수 없습니다.")
        changed = replace(self.store.load(inspection_id), header=header)
        self.store.save(changed)
        return changed

    def analyse(
        self,
        inspection: Inspection,
        progress: Callable[[int, int], None],
        cancelled: Callable[[], bool],
    ) -> Inspection:
        """Analyse an inspection from prepare(); it ends ANALYSED, FAILED, or NOT_ANALYSED when cancelled.

        The source SHA-256 runs on a second thread meanwhile. A first analysis records a cancel or a
        failure, clears the cache and raises again; a re-analysis only raises, leaving the previous
        analysis in place. Saved edits are fitted to the new analysis (Product SSOT §6).
        """
        again = self.store.load(inspection.id).state is InspectionState.ANALYSED
        if not again:
            self.store.clear_analysis(inspection.id)
        path = Path(inspection.video.path)
        hashing = _Background(lambda: self._hasher(path))
        try:
            found = self.analyser.analyse(path, inspection.recipe.glasses, inspection.settings, progress, cancelled)
            sha256 = hashing.result()
            analysis = Analysis(found.times, found.drafts, self._now())
            self.store.save_analysis(inspection.id, analysis, found.images)
        except AnalysisCancelled:
            if not again:
                self.store.clear_analysis(inspection.id)
                self.store.save(replace(inspection, state=InspectionState.NOT_ANALYSED, failure=None))
            raise
        except Exception as failure:
            if not again:
                self.store.clear_analysis(inspection.id)
                self.store.save(replace(inspection, state=InspectionState.FAILED, failure=failure_reason(failure)))
            raise
        saved = self.store.load_edits(inspection.id)
        if saved is not None:
            merged, _ = merge_reanalysis(saved.edits, analysis, inspection.settings.compressor_start_sec)
            self.store.save_edits(inspection.id, merged, self._now())
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


def _name(setup: InspectionSetup, existing: Inspection | None) -> str | None:
    """The name is set when the folder is made, and stays."""
    return existing.name if existing is not None else inspection_name(setup.name)


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
