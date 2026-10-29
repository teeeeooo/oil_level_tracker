"""Editor use cases: the edits, what follows from them, the point line and the source check.

Product SSOT §4, §6 and A9; DESIGN.md §5 ("Editor window"). The judgment comes with V2-4.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from oil_tracker.domain.edits import (
    Coverage,
    Edits,
    GlassEdits,
    Run,
    coverage,
    edits_from_analysis,
    empty_samples,
    level_states,
    merge_reanalysis,
    runs,
)
from oil_tracker.domain.enums import InspectionState, LevelState
from oil_tracker.domain.inspection import Analysis, Inspection
from oil_tracker.domain.recipe import Glass

from .ports import Desktop, EdgeTracer, InspectionStore, SourceHasher, StoredAnalysis


class NotAnalysed(LookupError):
    """The editor opens only on an analysed inspection."""


class InvalidEdits(ValueError):
    """The edits or points do not fit the inspection's analysis: a client error."""


@dataclass(frozen=True)
class OpenedEdits:
    edits: Edits
    saved_at: str | None  # None until the first "저장": the drafts as found
    unsaved: bool = False  # the saved edits were fitted to a newer analysis just now


@dataclass(frozen=True)
class GlassState:
    """What follows from one Glass's lines: the bands and the Glass panel (architecture.md)."""

    glass_id: str
    levels: tuple[Run[LevelState], ...]  # FULL and EMPTY, by sample index
    empty: tuple[Run[bool], ...]         # Oil samples still to be drawn
    coverage: Coverage


@dataclass(frozen=True)
class DrawnPiece:
    first: int              # the sample index of the first point
    ys: tuple[float, ...]   # a source-frame y per sample, to the last point


class SourceState(StrEnum):
    CHECKING = "CHECKING"
    SAME = "SAME"
    DIFFERENT = "DIFFERENT"      # A9: the video changed since the analysis
    MISSING = "MISSING"
    UNREADABLE = "UNREADABLE"


@dataclass(frozen=True)
class SourceCheck:
    state: SourceState
    message: str | None = None


class Editing:
    def __init__(
        self,
        store: InspectionStore,
        tracer: EdgeTracer,
        hasher: SourceHasher,
        desktop: Desktop,
        now: Callable[[], str],
    ) -> None:
        self.store = store
        self._tracer = tracer
        self._hasher = hasher
        self._desktop = desktop
        self._now = now
        self._checks: dict[str, SourceCheck] = {}
        self._lock = threading.Lock()

    def open(self, inspection_id: str) -> OpenedEdits:
        """The saved edits, or the first ones from the drafts.

        Saved edits that no longer fit the analysis (the app stopped between a re-analysis and its
        merge) are merged now and come back unsaved.
        """
        inspection, stored = self._analysed(inspection_id)
        saved = self.store.load_edits(inspection_id)
        if saved is None:
            return OpenedEdits(edits_from_analysis(stored.analysis, inspection.settings.compressor_start_sec), None)
        if _fits(saved.edits, stored.analysis):
            return OpenedEdits(saved.edits, saved.saved_at)
        merged, _ = merge_reanalysis(saved.edits, stored.analysis, saved.edits.compressor_start_sec)
        return OpenedEdits(merged, saved.saved_at, unsaved=True)

    def states(self, inspection_id: str, edits: Edits) -> tuple[GlassState, ...]:
        """What follows from the lines as they are, saved or not."""
        glasses = {glass.id: glass for glass in self.store.load(inspection_id).recipe.glasses}
        if any(g.glass_id not in glasses for g in edits.glasses):
            raise InvalidEdits("이 검사에 없는 Glass의 편집입니다.")
        return tuple(glass_state(edits.times, g, glasses[g.glass_id]) for g in edits.glasses)

    def save(self, inspection_id: str, edits: Edits) -> str:
        """Replace the saved edits; return the time they were saved."""
        _, stored = self._analysed(inspection_id)
        if not _fits(edits, stored.analysis):
            raise InvalidEdits("편집 내용이 이 검사의 분석과 맞지 않습니다.")
        saved_at = self._now()
        self.store.save_edits(inspection_id, edits, saved_at)
        return saved_at

    def mark_unsaved(self, unsaved: bool) -> None:
        """The editor holds edits it has not saved: closing the window asks first (§6)."""
        self._desktop.ask_before_closing(unsaved)

    def point_line(self, inspection_id: str, glass_id: str, points: Sequence[tuple[int, float]]) -> DrawnPiece:
        """The line through the user's points along the edges between them (§6). Points are
        (sample index, source-frame y), in time order."""
        _, stored = self._analysed(inspection_id)
        layout = next((image for image in stored.images if image.glass_id == glass_id), None)
        if layout is None:
            raise InvalidEdits("이 검사에 없는 Glass입니다.")
        columns = [column for column, _ in points]
        if len(points) < 2 or columns != sorted(set(columns)) or columns[0] < 0 or columns[-1] >= len(stored.analysis.times):
            raise InvalidEdits("점 잇기에는 서로 다른 시각의 점이 시각 순서대로 둘 이상 필요합니다.")
        rows = [min(layout.rows - 1, max(0, round(y - layout.y0))) for _, y in points]
        traced = self._tracer.trace(
            f"{inspection_id}/{glass_id}/{stored.analysis.finished_at}",
            lambda index: self.store.image_piece(inspection_id, glass_id, "context", index),
            layout.pieces,
            list(zip(columns, rows)),
        )
        return DrawnPiece(columns[0], tuple(float(layout.y0 + row) for row in traced))

    def source_file(self, inspection_id: str) -> Path:
        """The source video, for the built-in player."""
        return Path(self.store.load(inspection_id).video.path)

    def check_source(self, inspection_id: str) -> SourceCheck:
        """Start comparing the source's SHA-256 with the analysis's (A9), unless a check is running.

        Hashing SPL#1 takes seconds, so it runs on a thread; source_check() reports it.
        """
        inspection = self.store.load(inspection_id)
        with self._lock:
            current = self._checks.get(inspection_id)
            if current is not None and current.state is SourceState.CHECKING:
                return current
            self._checks[inspection_id] = SourceCheck(SourceState.CHECKING)
        path = Path(inspection.video.path)
        threading.Thread(
            target=self._check, args=(inspection_id, path, inspection.video.sha256), name="source-check", daemon=True
        ).start()
        return SourceCheck(SourceState.CHECKING)

    def source_check(self, inspection_id: str) -> SourceCheck:
        """The latest check, starting one when none has run since the app started."""
        with self._lock:
            current = self._checks.get(inspection_id)
        return current if current is not None else self.check_source(inspection_id)

    def _check(self, inspection_id: str, path: Path, expected: str | None) -> None:
        try:
            same = self._hasher(path) == expected
            result = SourceCheck(SourceState.SAME) if same else SourceCheck(
                SourceState.DIFFERENT, "원본 영상이 분석할 때와 다릅니다. 같은 이름의 다른 파일일 수 있습니다."
            )
        except FileNotFoundError:
            result = SourceCheck(SourceState.MISSING, f"원본 영상을 찾을 수 없습니다: {path}")
        except OSError as failure:
            result = SourceCheck(SourceState.UNREADABLE, f"원본 영상을 읽을 수 없습니다: {failure}")
        with self._lock:
            self._checks[inspection_id] = result

    def _analysed(self, inspection_id: str) -> tuple[Inspection, StoredAnalysis]:
        inspection = self.store.load(inspection_id)
        stored = self.store.load_analysis(inspection_id)
        if inspection.state is not InspectionState.ANALYSED or stored is None:
            raise NotAnalysed("분석이 끝난 검사만 편집할 수 있습니다.")
        return inspection, stored


def glass_state(times: tuple[float, ...], edits: GlassEdits, glass: Glass) -> GlassState:
    empty = tuple(True if flag else None for flag in empty_samples(times, edits))
    return GlassState(edits.glass_id, runs(level_states(edits.oil, glass)), runs(empty), coverage(times, edits))


def _fits(edits: Edits, analysis: Analysis) -> bool:
    return edits.times == analysis.times and [g.glass_id for g in edits.glasses] == [
        d.glass_id for d in analysis.drafts
    ]
