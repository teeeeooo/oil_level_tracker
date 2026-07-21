from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Protocol


class AnalysisStage(str, Enum):
    VIDEO_ANALYSIS = "video_analysis"
    EVENTS_AND_JUDGMENT = "events_and_judgment"
    RESULT_IMAGES = "result_images"
    CSV_AND_SNAPSHOTS = "csv_and_snapshots"
    GRAPHS_AND_REPORT = "graphs_and_report"
    BUNDLE_FINALIZATION = "bundle_finalization"


@dataclass(frozen=True)
class AnalysisStageSpec:
    key: AnalysisStage
    label: str
    index: int
    weight_percent: int
    start_fraction: float
    end_fraction: float

    @property
    def weight(self) -> float:
        return self.end_fraction - self.start_fraction


_STAGE_DEFINITIONS = (
    (AnalysisStage.VIDEO_ANALYSIS, "영상 분석", 60),
    (AnalysisStage.EVENTS_AND_JUDGMENT, "이벤트와 판정 계산", 12),
    (AnalysisStage.RESULT_IMAGES, "결과 이미지 생성", 8),
    (AnalysisStage.CSV_AND_SNAPSHOTS, "CSV와 snapshot 저장", 8),
    (AnalysisStage.GRAPHS_AND_REPORT, "graph와 보고서 생성", 9),
    (AnalysisStage.BUNDLE_FINALIZATION, "bundle 마무리", 3),
)


def _build_stage_specs() -> tuple[AnalysisStageSpec, ...]:
    if sum(weight for _key, _label, weight in _STAGE_DEFINITIONS) != 100:
        raise RuntimeError("Analysis stage weights must total exactly 100 percent.")
    specs: list[AnalysisStageSpec] = []
    accumulated = 0
    for index, (key, label, weight) in enumerate(_STAGE_DEFINITIONS, start=1):
        start = accumulated / 100.0
        accumulated += weight
        end = 1.0 if index == len(_STAGE_DEFINITIONS) else accumulated / 100.0
        specs.append(AnalysisStageSpec(key, label, index, weight, start, end))
    return tuple(specs)


ANALYSIS_STAGE_SPECS = _build_stage_specs()
_STAGE_BY_KEY = {spec.key: spec for spec in ANALYSIS_STAGE_SPECS}
ANALYSIS_STAGE_COUNT = len(ANALYSIS_STAGE_SPECS)


def analysis_stage_spec(stage: AnalysisStage | str) -> AnalysisStageSpec:
    return _STAGE_BY_KEY[AnalysisStage(stage)]


@dataclass(frozen=True)
class ProgressUpdate:
    """Immutable progress for the complete analysis-to-atomic-bundle lifecycle.

    The first five fields keep the original frame-progress construction contract
    compatible. Non-video stages explicitly use ``None`` for frame-only values.
    """

    completed: int = 0
    total: int = 0
    timestamp_sec: float | None = None
    glass_name: str | None = None
    rate_fps: float | None = None
    stage_key: AnalysisStage = AnalysisStage.VIDEO_ANALYSIS
    stage_label: str = "영상 분석"
    stage_index: int = 1
    stage_count: int = ANALYSIS_STAGE_COUNT
    stage_fraction: float = 0.0
    overall_fraction: float = 0.0
    message: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.stage_fraction <= 1.0:
            raise ValueError("stage_fraction must be between 0 and 1.")
        if not 0.0 <= self.overall_fraction <= 1.0:
            raise ValueError("overall_fraction must be between 0 and 1.")
        spec = analysis_stage_spec(self.stage_key)
        if self.stage_label != spec.label or self.stage_index != spec.index:
            raise ValueError("Progress stage metadata does not match the shared policy.")
        if self.stage_count != ANALYSIS_STAGE_COUNT:
            raise ValueError("Progress stage_count does not match the shared policy.")
        if self.completed < 0 or self.total < 0:
            raise ValueError("Progress counts must be non-negative.")


AnalysisProgressUpdate = ProgressUpdate


def build_progress_update(
    stage: AnalysisStage | str,
    stage_fraction: float,
    *,
    message: str = "",
    completed: int = 0,
    total: int = 0,
    timestamp_sec: float | None = None,
    glass_name: str | None = None,
    rate_fps: float | None = None,
    finalization_committed: bool = False,
) -> ProgressUpdate:
    spec = analysis_stage_spec(stage)
    fraction = min(1.0, max(0.0, float(stage_fraction)))
    overall = spec.start_fraction + spec.weight * fraction
    if spec.key is AnalysisStage.BUNDLE_FINALIZATION and fraction >= 1.0:
        overall = 1.0 if finalization_committed else math.nextafter(1.0, 0.0)
    return ProgressUpdate(
        completed=int(completed),
        total=int(total),
        timestamp_sec=timestamp_sec,
        glass_name=glass_name,
        rate_fps=rate_fps,
        stage_key=spec.key,
        stage_label=spec.label,
        stage_index=spec.index,
        stage_count=ANALYSIS_STAGE_COUNT,
        stage_fraction=fraction,
        overall_fraction=min(1.0, max(0.0, overall)),
        message=message,
    )


class AnalysisCancelled(RuntimeError):
    pass


class ProgressSink(Protocol):
    def __call__(self, update: ProgressUpdate) -> None: ...


class CancellationToken(Protocol):
    @property
    def cancelled(self) -> bool: ...


class MonotonicProgressSink:
    """Validates producer ordering and suppresses stale/regressive updates."""

    def __init__(self, sink: ProgressSink | None) -> None:
        self._sink = sink
        self._last_stage_index = 0
        self._last_stage_fraction = 0.0
        self._last_overall_fraction = 0.0
        self._last_update: ProgressUpdate | None = None
        self._finalized = False

    @property
    def last_update(self) -> ProgressUpdate | None:
        return self._last_update

    def __call__(self, update: ProgressUpdate) -> None:
        if self._finalized:
            return
        if update.stage_index < self._last_stage_index:
            return
        if update.stage_index == self._last_stage_index and update.stage_fraction < self._last_stage_fraction:
            return
        if update.overall_fraction < self._last_overall_fraction:
            return
        if update.overall_fraction >= 1.0:
            if not (
                update.stage_key is AnalysisStage.BUNDLE_FINALIZATION
                and update.stage_fraction == 1.0
            ):
                raise ValueError("Overall completion is only valid after bundle finalization.")
            self._finalized = True
        self._last_stage_index = update.stage_index
        self._last_stage_fraction = update.stage_fraction
        self._last_overall_fraction = update.overall_fraction
        self._last_update = update
        if self._sink is not None:
            self._sink(update)
