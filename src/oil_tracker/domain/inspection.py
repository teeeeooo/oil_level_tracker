"""An inspection: one video, a copy of its Recipe and the analysis (Product SSOT §3, §8)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .enums import InspectionState, JudgmentMode
from .line import Line
from .problems import Problem
from .recipe import Recipe, recipe_problems

ANALYSIS_RATE = 2.0        # samples per second, fixed in the first version (Product SSOT §3)
MINIMUM_RANGE_SEC = 1.0
MAXIMUM_NAME_LENGTH = 60   # an inspection name; it names the folder, which must stay inside Windows' path limit


@dataclass(frozen=True)
class SourceVideo:
    """The video is referenced by path and SHA-256, not copied (Product SSOT §8)."""

    path: str
    name: str
    size_bytes: int
    width: int
    height: int
    fps: float
    frame_count: int
    sha256: str | None = None  # set by the analysis

    @property
    def duration_sec(self) -> float:
        return self.frame_count / self.fps


@dataclass(frozen=True)
class AnalysisSettings:
    start_sec: float
    end_sec: float
    compressor_start_sec: float | None = None

    @property
    def sample_count(self) -> int:
        return math.floor((self.end_sec - self.start_sec) * ANALYSIS_RATE + 1e-9) + 1


@dataclass(frozen=True)
class GlassDraft:
    glass_id: str
    oil: Line


@dataclass(frozen=True)
class Analysis:
    """What the analysis found; the context images themselves belong to the adapters."""

    times: tuple[float, ...]
    drafts: tuple[GlassDraft, ...]
    finished_at: str

    def __post_init__(self) -> None:
        if any(len(draft.oil.ys) != len(self.times) for draft in self.drafts):
            raise ValueError("Every draft needs one sample per analysis time.")


@dataclass(frozen=True)
class Inspection:
    id: str
    created_at: str
    video: SourceVideo
    recipe: Recipe  # the inspection's copy; Glass corrections are made here only (§3)
    settings: AnalysisSettings
    state: InspectionState = InspectionState.NOT_ANALYSED
    failure: str | None = None
    name: str | None = None  # the user's name for it, which names its folder; None names it by time and video (§8)


def inspection_name(text: str | None) -> str | None:
    """The name the user typed, without surrounding spaces; None when it is blank."""
    name = (text or "").strip()
    return name or None


def needs_compressor_start(recipe: Recipe) -> bool:
    return any(glass.judgment_rule.mode is JudgmentMode.RECOVERY for glass in recipe.glasses)


def setup_problems(
    video: SourceVideo, recipe: Recipe, settings: AnalysisSettings, name: str | None = None
) -> list[Problem]:
    """What blocks "분석 시작" (Product SSOT §3, analysis setup)."""
    problems = recipe_problems(recipe)  # the copy, with any Glass correction
    if name is not None and len(name) > MAXIMUM_NAME_LENGTH:
        problems.append(Problem("inspection_name", f"검사 이름은 {MAXIMUM_NAME_LENGTH}자 이하여야 합니다."))
    message = recipe.frame_size_message(video.width, video.height)
    if message is not None:
        problems.append(Problem("recipe", message))

    start, end = settings.start_sec, settings.end_sec
    duration = video.duration_sec
    range_ok = True
    if not math.isfinite(start) or not 0 <= start < duration:
        problems.append(Problem("start_sec", "시작 시각은 영상 안이어야 합니다."))
        range_ok = False
    if not math.isfinite(end) or not 0 < end <= duration:
        problems.append(Problem("end_sec", "끝 시각은 영상 안이어야 합니다."))
        range_ok = False
    if range_ok and end - start < MINIMUM_RANGE_SEC:
        problems.append(Problem("end_sec", f"분석 범위는 {MINIMUM_RANGE_SEC:g}초 이상이어야 합니다."))
        range_ok = False

    compressor = settings.compressor_start_sec
    if compressor is None:
        if needs_compressor_start(recipe):
            problems.append(Problem("compressor_start_sec", "기준점 회복 Glass가 있어 압축기 기동 시각이 필요합니다."))
    elif not math.isfinite(compressor) or (range_ok and not start <= compressor <= end):
        problems.append(Problem("compressor_start_sec", "압축기 기동 시각이 분석 범위 밖입니다."))
    return problems
