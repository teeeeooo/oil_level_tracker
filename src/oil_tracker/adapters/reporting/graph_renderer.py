from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from oil_tracker.application.ports.progress import AnalysisCancelled
from oil_tracker.application.services.graph_axis import (
    combined_graph_axis_range,
    graph_axis_range_for_glass,
)
from oil_tracker.application.services.graph_series import continuous_observed_polyline
from oil_tracker.domain.enums import FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult
from oil_tracker.visualization.matplotlib_font import (
    apply_font_to_axes,
    configure_matplotlib_korean_font,
)


class GraphRenderer:
    def __init__(self) -> None:
        self.font_selection = configure_matplotlib_korean_font()

    def render(
        self,
        result: AnalysisResult,
        directory: Path,
        recipe: InspectionRecipe | None = None,
        *,
        progress=None,
        cancellation=None,
    ) -> dict[str, str]:
        directory.mkdir(parents=True, exist_ok=True)
        paths: dict[str, str] = {}
        total = 1 + len(result.glass_results)
        _check_cancelled(cancellation)
        combined = directory / "combined_levels.png"
        self._render_combined(result, recipe, combined)
        paths["combined"] = f"graphs/{combined.name}"
        if progress is not None:
            progress(1, total)
        for index, glass in enumerate(result.glass_results, start=2):
            _check_cancelled(cancellation)
            filename = f"{_safe_name(glass.glass_name)}_detail.png"
            path = directory / filename
            config = _glass_config(recipe, glass.glass_id)
            self._render_glass(glass, config, path)
            paths[glass.glass_id] = f"graphs/{filename}"
            if progress is not None:
                progress(index, total)
        return paths

    def _render_combined(
        self,
        result: AnalysisResult,
        recipe: InspectionRecipe | None,
        path: Path,
    ) -> None:
        fig, ax = plt.subplots(figsize=(12, 5.5))
        observed: list[float | None] = []
        for glass in result.glass_results:
            times = [sample.timestamp_sec for sample in glass.samples]
            oil = [_value(sample.smoothed_oil_air_level_px_from_zero, sample.raw_oil_air_level_px_from_zero) for sample in glass.samples]
            foam = [_value(sample.smoothed_foam_front_px_from_zero, sample.raw_foam_front_px_from_zero) for sample in glass.samples]
            observed.extend(oil)
            observed.extend(foam)
            oil_times, oil_values = continuous_observed_polyline(times, oil)
            if oil_times:
                ax.plot(oil_times, oil_values, label=f"{glass.glass_name} 유면")
            if any(value is not None for value in foam):
                ax.plot(
                    times,
                    _gaps(foam),
                    linestyle="--",
                    label=f"{glass.glass_name} 거품 경계",
                )
        ranges = []
        if recipe is not None:
            for glass_result in result.glass_results:
                config = _glass_config(recipe, glass_result.glass_id)
                if config is not None:
                    ranges.append(graph_axis_range_for_glass(config, unit="px", observed_values=observed))
        axis_range = combined_graph_axis_range(ranges, unit="px") if ranges else None
        ax.axhline(0.0, linestyle=":", linewidth=1.5, label="기준선")
        if axis_range is not None and axis_range.available:
            ax.set_ylim(axis_range.lower, axis_range.upper)
            if axis_range.analysis_top_boundary is not None:
                ax.axhline(axis_range.analysis_top_boundary, linestyle="--", linewidth=0.9, alpha=0.65, label="전체 분석 영역 위쪽 경계")
            if axis_range.analysis_bottom_boundary is not None:
                ax.axhline(axis_range.analysis_bottom_boundary, linestyle="--", linewidth=0.9, alpha=0.65, label="전체 분석 영역 아래쪽 경계")
        ax.set_xlabel("시간 (초)")
        ax.set_ylabel("기준선 대비 높이 (px)")
        ax.set_title(f"전체 Glass 유면 추적 — {_result_state_label(result.overall_state)}")
        ax.grid(True, alpha=0.25)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            unique = dict(zip(labels, handles))
            ax.legend(unique.values(), unique.keys(), loc="best", prop=self.font_selection.properties)
        apply_font_to_axes(ax, self.font_selection)
        fig.tight_layout()
        fig.savefig(path, dpi=140)
        plt.close(fig)

    def _render_glass(self, glass: GlassAnalysisResult, config, path: Path) -> None:
        fig, ax = plt.subplots(figsize=(12, 5.5))
        times = [sample.timestamp_sec for sample in glass.samples]
        use_mm = bool(config is not None and config.mm_per_pixel and config.mm_per_pixel > 0) and any(
            _value(sample.smoothed_oil_air_level_mm_from_zero, sample.raw_oil_air_level_mm_from_zero) is not None
            or _value(sample.smoothed_foam_front_mm_from_zero, sample.raw_foam_front_mm_from_zero) is not None
            for sample in glass.samples
        )
        unit = "mm" if use_mm else "px"
        if unit == "mm":
            oil = [_value(sample.smoothed_oil_air_level_mm_from_zero, sample.raw_oil_air_level_mm_from_zero) for sample in glass.samples]
            foam = [_value(sample.smoothed_foam_front_mm_from_zero, sample.raw_foam_front_mm_from_zero) for sample in glass.samples]
        else:
            oil = [_value(sample.smoothed_oil_air_level_px_from_zero, sample.raw_oil_air_level_px_from_zero) for sample in glass.samples]
            foam = [_value(sample.smoothed_foam_front_px_from_zero, sample.raw_foam_front_px_from_zero) for sample in glass.samples]
        oil_times, oil_values = continuous_observed_polyline(times, oil)
        if oil_times:
            ax.plot(oil_times, oil_values, label="유면", linewidth=2)
        if any(value is not None for value in foam):
            ax.plot(
                times,
                _gaps(foam),
                linestyle="--",
                label="거품 경계",
                linewidth=2,
            )
        ax.axhline(0.0, linestyle=":", linewidth=1.5, label="기준선")
        if config is not None:
            axis_range = graph_axis_range_for_glass(config, unit=unit, observed_values=(*oil, *foam))
            if axis_range.available:
                ax.set_ylim(axis_range.lower, axis_range.upper)
            if axis_range.analysis_top_boundary is not None:
                ax.axhline(axis_range.analysis_top_boundary, linestyle="--", linewidth=0.9, alpha=0.65, label="분석 영역 위쪽 경계")
            if axis_range.analysis_bottom_boundary is not None:
                ax.axhline(axis_range.analysis_bottom_boundary, linestyle="--", linewidth=0.9, alpha=0.65, label="분석 영역 아래쪽 경계")
        self._state_bands(ax, glass)
        for event in glass.events:
            ax.axvline(event.start_time_sec, alpha=0.12, linewidth=0.8)
        ax.set_xlabel("시간 (초)")
        ax.set_ylabel(f"기준선 대비 높이 ({unit})")
        ax.set_title(
            f"{glass.glass_name} 유면 추적 — {_result_state_label(glass.result_state)} — 유효 데이터 {glass.valid_coverage_ratio:.1%}"
        )
        ax.grid(True, alpha=0.25)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            unique = dict(zip(labels, handles))
            ax.legend(unique.values(), unique.keys(), loc="best", prop=self.font_selection.properties)
        apply_font_to_axes(ax, self.font_selection)
        fig.tight_layout()
        fig.savefig(path, dpi=140)
        plt.close(fig)

    def _state_bands(self, ax, glass: GlassAnalysisResult) -> None:
        if not glass.samples:
            return
        groups = []
        start = glass.samples[0]
        previous = start
        for current in glass.samples[1:]:
            if current.fill_state != start.fill_state:
                groups.append((start, previous))
                start = current
            previous = current
        groups.append((start, previous))
        for begin, end in groups:
            if begin.fill_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}:
                ax.axvspan(begin.timestamp_sec, end.timestamp_sec, alpha=0.07)
            elif begin.fill_state == FillState.EMPTY_NO_INTERFACE:
                ax.axvspan(begin.timestamp_sec, end.timestamp_sec, alpha=0.05)
            elif begin.fill_state == FillState.UNKNOWN_REVIEW:
                ax.axvspan(begin.timestamp_sec, end.timestamp_sec, alpha=0.12, hatch="//")
        for sample in glass.samples:
            if sample.overall_confidence < 0.35:
                ax.axvline(sample.timestamp_sec, alpha=0.04)


def _check_cancelled(cancellation) -> None:
    if cancellation is not None and cancellation.cancelled:
        raise AnalysisCancelled("Analysis was cancelled while rendering graphs.")


def _glass_config(recipe: InspectionRecipe | None, glass_id: str):
    if recipe is None:
        return None
    return next((glass for glass in recipe.glasses if glass.id == glass_id), None)


def _value(preferred, fallback):
    return preferred if preferred is not None else fallback


def _gaps(values):
    return [math.nan if value is None else float(value) for value in values]


def _result_state_label(state: ResultState) -> str:
    return {
        ResultState.PASS: "통과",
        ResultState.FAIL: "실패",
        ResultState.REVIEW_REQUIRED: "확인 필요",
        ResultState.NOT_APPLICABLE: "판정 없음",
    }.get(state, state.value)


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in "-_" else "_" for character in value)
