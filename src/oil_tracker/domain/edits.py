"""The edit document: what the user makes of an analysis (Product SSOT §4 and §6).

Each Glass has one Oil, one Foam and one reference line, as dense samples on the analysis times; a
line's pieces are the stretches between its empty samples. "Cannot judge" stretches and memos are
stored. FULL and EMPTY are not: they follow from where the Oil line sits in its Glass.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .enums import LevelState, SampleOrigin
from .inspection import ANALYSIS_RATE, Analysis
from .line import Line
from .recipe import Glass

LEVEL_TOLERANCE_PX = 1.0     # an Oil sample this close to the Glass top or bottom is FULL or EMPTY
TIME_TOLERANCE_SEC = 0.5 / ANALYSIS_RATE  # two analyses' samples within half a step are the same time
MAXIMUM_MEMO_LENGTH = 500


@dataclass(frozen=True)
class Stretch:
    """The samples whose times lie in [start_sec, end_sec)."""

    start_sec: float
    end_sec: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.start_sec) and math.isfinite(self.end_sec)) or self.start_sec >= self.end_sec:
            raise ValueError("A stretch needs a finite start before its end.")

    def holds(self, time_sec: float) -> bool:
        return self.start_sec <= time_sec < self.end_sec


@dataclass(frozen=True)
class Memo:
    id: str
    time_sec: float
    y: float | None  # the source-frame y it points at; None pins it to the time alone
    text: str

    def __post_init__(self) -> None:
        if not math.isfinite(self.time_sec) or (self.y is not None and not math.isfinite(self.y)):
            raise ValueError("A memo needs a finite time and height.")
        if len(self.text) > MAXIMUM_MEMO_LENGTH:
            raise ValueError(f"A memo has at most {MAXIMUM_MEMO_LENGTH} characters.")


@dataclass(frozen=True)
class GlassEdits:
    glass_id: str
    oil: Line
    foam: Line
    reference: Line
    cannot_judge: tuple[Stretch, ...] = ()
    memos: tuple[Memo, ...] = ()


@dataclass(frozen=True)
class Edits:
    times: tuple[float, ...]
    glasses: tuple[GlassEdits, ...]
    compressor_start_sec: float | None  # the setup's, until the user drags the marker

    def __post_init__(self) -> None:
        count = len(self.times)
        for glass in self.glasses:
            if any(len(line.ys) != count for line in (glass.oil, glass.foam, glass.reference)):
                raise ValueError("Every line needs one sample per analysis time.")
        if len({glass.glass_id for glass in self.glasses}) != len(self.glasses):
            raise ValueError("A Glass appears twice in the edits.")
        if self.compressor_start_sec is not None and not math.isfinite(self.compressor_start_sec):
            raise ValueError("The compressor start must be finite.")

    def glass(self, glass_id: str) -> GlassEdits:
        return next(g for g in self.glasses if g.glass_id == glass_id)


def empty_line(count: int) -> Line:
    return Line((None,) * count, (SampleOrigin.DRAFT,) * count)


def edits_from_analysis(analysis: Analysis, compressor_start_sec: float | None) -> Edits:
    """The first edit document: each Oil draft as found, with no Foam, reference, stretch or memo."""
    count = len(analysis.times)
    return Edits(
        analysis.times,
        tuple(GlassEdits(draft.glass_id, draft.oil, empty_line(count), empty_line(count)) for draft in analysis.drafts),
        compressor_start_sec,
    )


# ---- what follows from the lines ------------------------------------------------------------------


def level_states(oil: Line, glass: Glass) -> tuple[LevelState | None, ...]:
    """FULL at the Glass top, EMPTY at its bottom (Product SSOT §4); None elsewhere and where empty."""
    top = glass.ellipse.center_y - glass.ellipse.radius_y
    bottom = glass.ellipse.center_y + glass.ellipse.radius_y

    def state(y: float | None) -> LevelState | None:
        if y is None:
            return None
        if y <= top + LEVEL_TOLERANCE_PX:
            return LevelState.FULL
        if y >= bottom - LEVEL_TOLERANCE_PX:
            return LevelState.EMPTY
        return None

    return tuple(state(y) for y in oil.ys)


@dataclass(frozen=True)
class Run[T]:
    value: T
    first: int  # sample indices [first, end)
    end: int


def runs[T](values: tuple[T | None, ...]) -> tuple[Run[T], ...]:
    """The stretches of equal values, leaving out None."""
    found: list[Run[T]] = []
    for index, value in enumerate(values):
        if value is None:
            continue
        if found and found[-1].value == value and found[-1].end == index:
            found[-1] = replace(found[-1], end=index + 1)
        else:
            found.append(Run(value, index, index + 1))
    return tuple(found)


@dataclass(frozen=True)
class Coverage:
    """Product SSOT §4: empty and "cannot judge" samples are both invalid."""

    total: int
    empty: int         # no Oil sample, outside a "cannot judge" stretch
    cannot_judge: int

    @property
    def valid(self) -> int:
        return self.total - self.empty - self.cannot_judge

    @property
    def valid_ratio(self) -> float:
        return self.valid / self.total if self.total else 0.0


def cannot_judge_flags(times: tuple[float, ...], stretches: tuple[Stretch, ...]) -> tuple[bool, ...]:
    return tuple(any(stretch.holds(t) for stretch in stretches) for t in times)


def coverage(times: tuple[float, ...], glass: GlassEdits) -> Coverage:
    flags = cannot_judge_flags(times, glass.cannot_judge)
    empty = sum(1 for y, flagged in zip(glass.oil.ys, flags) if y is None and not flagged)
    return Coverage(len(times), empty, sum(flags))


# ---- re-analysis ----------------------------------------------------------------------------------


@dataclass(frozen=True)
class Dropped:
    """What re-analysis loses: the edits outside the new range (Product SSOT §6)."""

    oil_samples: int = 0        # edited or drawn Oil samples
    foam_samples: int = 0
    reference_samples: int = 0
    stretches: int = 0
    memos: int = 0
    glasses: tuple[str, ...] = ()  # Glasses the new analysis no longer has

    @property
    def anything(self) -> bool:
        return bool(self.oil_samples or self.foam_samples or self.reference_samples
                    or self.stretches or self.memos or self.glasses)


def merge_reanalysis(old: Edits, analysis: Analysis, compressor_start_sec: float | None) -> tuple[Edits, Dropped]:
    """The edits on a new analysis: every old sample is kept where the new range still has its time,
    and only the new times take the new draft (user, 2026-10-29)."""
    times = analysis.times
    matches = _match_times(old.times, times)
    kept = {i for i in matches if i is not None}
    outside = [i for i in range(len(old.times)) if i not in kept]
    first, end = (times[0], times[-1] + TIME_TOLERANCE_SEC) if times else (0.0, 0.0)

    dropped = Dropped(glasses=tuple(g.glass_id for g in old.glasses
                                    if g.glass_id not in {d.glass_id for d in analysis.drafts}))
    glasses: list[GlassEdits] = []
    for draft in analysis.drafts:
        previous = next((g for g in old.glasses if g.glass_id == draft.glass_id), None)
        if previous is None:
            glasses.append(GlassEdits(draft.glass_id, draft.oil, empty_line(len(times)), empty_line(len(times))))
            continue
        stretches = tuple(_clip(s, first, end) for s in previous.cannot_judge if s.end_sec > first and s.start_sec < end)
        memos = tuple(m for m in previous.memos if first - TIME_TOLERANCE_SEC <= m.time_sec < end)
        glasses.append(GlassEdits(
            draft.glass_id,
            _carry(previous.oil, matches, draft.oil),
            _carry(previous.foam, matches, empty_line(len(times))),
            _carry(previous.reference, matches, empty_line(len(times))),
            stretches,
            memos,
        ))
        dropped = replace(
            dropped,
            oil_samples=dropped.oil_samples + sum(previous.oil.origins[i] is not SampleOrigin.DRAFT for i in outside),
            foam_samples=dropped.foam_samples + sum(previous.foam.ys[i] is not None for i in outside),
            reference_samples=dropped.reference_samples + sum(previous.reference.ys[i] is not None for i in outside),
            stretches=dropped.stretches + len(previous.cannot_judge) - len(stretches),
            memos=dropped.memos + len(previous.memos) - len(memos),
        )
    return Edits(times, tuple(glasses), compressor_start_sec), dropped


def _match_times(old: tuple[float, ...], new: tuple[float, ...]) -> list[int | None]:
    """For each new time, the old sample at the same time (within half a step), or None."""
    matches: list[int | None] = []
    j = 0
    for t in new:
        while j + 1 < len(old) and abs(old[j + 1] - t) <= abs(old[j] - t):
            j += 1
        matches.append(j if old and abs(old[j] - t) <= TIME_TOLERANCE_SEC else None)
    return matches


def _carry(previous: Line, matches: list[int | None], fresh: Line) -> Line:
    ys = tuple(previous.ys[i] if i is not None else fresh.ys[k] for k, i in enumerate(matches))
    origins = tuple(previous.origins[i] if i is not None else fresh.origins[k] for k, i in enumerate(matches))
    return Line(ys, origins)


def _clip(stretch: Stretch, first: float, end: float) -> Stretch:
    return Stretch(max(stretch.start_sec, first), min(stretch.end_sec, end))
