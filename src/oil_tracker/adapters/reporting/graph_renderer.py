from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

from oil_tracker.application.ports.progress import AnalysisCancelled
from oil_tracker.application.services.graph_axis import (
    combined_graph_axis_range,
    graph_axis_range_for_glass,
)
from oil_tracker.application.services.graph_series import (
    REPORT_MAX_CONTEXT_GAP_SEC,
    observed_trajectory,
)
from oil_tracker.application.services.initial_state_reconstruction import (
    project_state_aware_samples,
)
from oil_tracker.application.services.report_presentation import (
    ReportGlassPresentation,
    ReportPresentation,
    build_report_presentation,
)
from oil_tracker.domain.enums import EventType, FillState, ResultState
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
        presentation: ReportPresentation | None = None,
    ) -> dict[str, str]:
        directory.mkdir(parents=True, exist_ok=True)
        paths: dict[str, str] = {}
        presentation = presentation or (
            build_report_presentation(result, recipe) if recipe is not None else None
        )
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
            report_glass = (
                presentation.for_glass(glass.glass_id)
                if presentation is not None
                else None
            )
            self._render_glass(glass, config, path, report_glass)
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
        rows = [(glass.glass_name, _state_band_runs(glass)) for glass in result.glass_results]
        strip = None
        if any(runs for _, runs in rows):
            # One state row per Glass under the lines; the line plot stays lines only.
            strip_height = _STRIP_ROW_HEIGHT_IN * len(rows)
            fig = plt.figure(figsize=(12, 5.5 + strip_height + 0.8), layout="constrained")
            grid = fig.add_gridspec(2, 1, height_ratios=(5.5, strip_height))
            ax = fig.add_subplot(grid[0])
            strip = fig.add_subplot(grid[1], sharex=ax)
        else:
            fig, ax = plt.subplots(figsize=(12, 5.5))
        observed: list[float | None] = []
        for glass_index, glass in enumerate(result.glass_results):
            times = [sample.timestamp_sec for sample in glass.samples]
            oil = [_value(sample.smoothed_oil_air_level_px_from_zero, sample.raw_oil_air_level_px_from_zero) for sample in glass.samples]
            foam = [_value(sample.smoothed_foam_front_px_from_zero, sample.raw_foam_front_px_from_zero) for sample in glass.samples]
            observed.extend(oil)
            observed.extend(foam)
            _plot_oil_trajectory(
                ax,
                times,
                oil,
                label=f"{glass.glass_name} 유면",
                color=f"C{glass_index % 10}",
                show_bridge_label=False,
            )
            if any(value is not None for value in foam):
                ax.plot(
                    *_foam_plot_points(times, foam),
                    linestyle="--",
                    marker="o",
                    markersize=3.5,
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
        if strip is None:
            ax.set_xlabel("시간 (초)")
        else:
            ax.tick_params(labelbottom=False)
        ax.set_ylabel("기준선 대비 높이 (px)")
        ax.set_title(f"전체 Glass 유면 추적 — {_result_state_label(result.overall_state)}")
        ax.grid(True, alpha=0.25)
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            unique = dict(zip(labels, handles))
            ax.legend(unique.values(), unique.keys(), loc="best", prop=self.font_selection.properties)
        apply_font_to_axes(ax, self.font_selection)
        if strip is None:
            fig.tight_layout()
        else:
            self._state_strip(fig, strip, rows)
        fig.savefig(path, dpi=140)
        plt.close(fig)

    def _state_strip(self, fig, strip, rows) -> None:
        """Draw each Glass's detail-graph bands on its own row, top to bottom."""
        count = len(rows)
        for index, (_, runs) in enumerate(rows):
            top = count - index
            for begin, end, state, source in runs:
                label, style = _band_style(state, source, emphasis=_STRIP_EMPHASIS)
                strip.axvspan(
                    begin,
                    end,
                    ymin=(top - 1 + _STRIP_ROW_PAD) / count,
                    ymax=(top - _STRIP_ROW_PAD) / count,
                    label=label,
                    **style,
                )
        strip.set_ylim(0, count)
        strip.set_yticks([count - index - 0.5 for index in range(count)])
        strip.set_yticklabels([name for name, _ in rows])
        strip.tick_params(axis="y", length=0)
        strip.set_xlabel("시간 (초)")
        strip.grid(True, axis="x", alpha=0.25)
        handles, labels = strip.get_legend_handles_labels()
        unique = dict(zip(labels, handles))
        fig.legend(
            unique.values(),
            unique.keys(),
            loc="outside lower center",
            ncol=min(4, len(unique)),
            frameon=False,
            prop=self.font_selection.properties,
        )
        apply_font_to_axes(strip, self.font_selection)

    def _render_glass(
        self,
        glass: GlassAnalysisResult,
        config,
        path: Path,
        report_glass: ReportGlassPresentation | None = None,
    ) -> None:
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
        _plot_oil_trajectory(
            ax,
            times,
            oil,
            label="관측 유면",
            color="#2563eb",
            linewidth=2.2,
            show_bridge_label=True,
        )
        if any(value is not None for value in foam):
            ax.plot(
                *_foam_plot_points(times, foam),
                linestyle=(0, (5, 3)),
                marker="o",
                markersize=4,
                label="거품 경계",
                linewidth=2,
                color="#f97316",
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
        if report_glass is not None:
            _plot_landmarks(ax, report_glass, unit)
        ax.set_xlabel("시간 (초)")
        ax.set_ylabel(f"기준선 대비 높이 ({unit})")
        ax.set_title(
            f"{glass.glass_name} 유면 관찰 — {_result_state_label(glass.result_state)}"
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
        labeled: set[str] = set()
        for begin, end, state, source in _state_band_runs(glass):
            label, style = _band_style(state, source, emphasis=1.0)
            ax.axvspan(
                begin,
                end,
                label=None if label in labeled else label,
                **style,
            )
            labeled.add(label)


# Every FULL/EMPTY band names where its state came from and draws it in that
# source's pattern: solid for the detector itself (including top-exit FULL),
# diagonal hatching for an accepted initial-state reconstruction and dots for
# the all-missing confirmed-state hold. Colour follows the state.
_STATE_BAND_SOURCES = {
    "detector": ("{state} 판정", None),
    "retrospective": ("초기 상태 재구성 ({state})", "///"),
    "hold": ("확정 초기 상태 유지 가정 ({state})", ".."),
}
_STATE_BAND_COLORS = {"FULL": "#3b82f6", "EMPTY": "#f59e0b", "UNKNOWN": "#64748b"}
_UNKNOWN_BAND_LABEL = "직접 유면 확인 어려움"
# The combined graph's state strip has no line over it, so it fills more strongly.
_STRIP_EMPHASIS = 3.0
_STRIP_ROW_HEIGHT_IN = 0.42
_STRIP_ROW_PAD = 0.12


def _state_band_runs(glass: GlassAnalysisResult) -> list[tuple[float, float, str, str]]:
    """Contiguous (start, end, state, source) runs shared by both graphs."""
    if not glass.samples:
        return []
    samples = project_state_aware_samples(
        glass.samples,
        glass.retrospective,
    )
    groups = []
    start = samples[0]
    previous = start
    for current in samples[1:]:
        if _band_key(current) != _band_key(start):
            groups.append((start, previous))
            start = current
        previous = current
    groups.append((start, previous))
    return [
        (begin.timestamp_sec, end.timestamp_sec, *_band_key(begin))
        for begin, end in groups
        if _band_key(begin)[0] is not None
    ]


def _band_style(state: str, source: str, *, emphasis: float) -> tuple[str, dict]:
    """Legend label and patch style; emphasis 1.0 keeps the detail-graph alphas."""
    color = _STATE_BAND_COLORS[state]
    if state == "UNKNOWN":
        return _UNKNOWN_BAND_LABEL, {
            "facecolor": to_rgba(color, 0.065 * emphasis),
            "linewidth": 0.0,
        }
    template, hatch = _STATE_BAND_SOURCES[source]
    style = {"facecolor": to_rgba(color, 0.09 * emphasis), "linewidth": 0.0}
    if hatch is not None:
        # The hatch takes the edge colour; linewidth 0 leaves no outline.
        style.update(hatch=hatch, edgecolor=to_rgba(color, min(1.0, 0.5 * emphasis)))
    return template.format(state=state), style


def _band_key(sample) -> tuple[str | None, str]:
    if sample.fill_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}:
        state = "FULL"
    elif sample.fill_state == FillState.EMPTY_NO_INTERFACE:
        state = "EMPTY"
    elif sample.fill_state == FillState.UNKNOWN_REVIEW:
        state = "UNKNOWN"
    else:
        state = None
    flags = set(sample.flags)
    source = (
        "hold" if "R8_CONFIRMED_INITIAL_STATE_HOLD" in flags
        else "retrospective" if "RETROSPECTIVE_INITIAL_STATE" in flags
        else "detector"
    )
    return state, source


def _plot_oil_trajectory(
    ax,
    timestamps,
    values,
    *,
    label: str,
    color: str | None = None,
    linewidth: float = 1.8,
    show_bridge_label: bool,
) -> None:
    trajectory = observed_trajectory(timestamps, values, max_gap_sec=REPORT_MAX_CONTEXT_GAP_SEC)
    anchors = trajectory.anchors
    if not anchors:
        return
    color = color or "#2563eb"
    labelled = False
    for run in trajectory.observed_runs:
        if len(run.timestamps) < 2:
            continue
        ax.plot(
            run.timestamps,
            run.values,
            color=color,
            linewidth=linewidth,
            solid_capstyle="round",
            label=label if not labelled else None,
        )
        labelled = True
    bridge_labelled = False
    for bridge in trajectory.gap_bridges:
        ax.plot(
            bridge.timestamps,
            bridge.values,
            color=color,
            linewidth=max(1.2, linewidth * 0.85),
            linestyle=(0, (4, 3)),
            alpha=0.7,
            label=(
                "관측 공백 연결"
                if show_bridge_label and not bridge_labelled
                else None
            ),
        )
        bridge_labelled = True
    anchor_times, anchor_values = zip(*anchors)
    ax.scatter(
        anchor_times,
        anchor_values,
        color=color,
        s=12,
        alpha=0.7,
        zorder=3,
        label=label if not labelled else None,
    )


def _plot_landmarks(
    ax,
    report: ReportGlassPresentation,
    unit: str,
) -> None:
    top_row = 0
    for landmark in report.landmarks:
        oil_value = (
            landmark.oil_level_mm if unit == "mm" else landmark.oil_level_px
        )
        foam_value = (
            landmark.foam_front_mm if unit == "mm" else landmark.foam_front_px
        )
        if landmark.event_type in {
            EventType.MAXIMUM_OIL_LEVEL,
            EventType.MINIMUM_OIL_LEVEL,
        } and oil_value is not None:
            color = (
                "#7c3aed"
                if landmark.event_type is EventType.MAXIMUM_OIL_LEVEL
                else "#dc2626"
            )
            ax.scatter(
                [landmark.timestamp_sec],
                [oil_value],
                marker="D",
                s=42,
                color=color,
                edgecolor="white",
                linewidth=0.8,
                zorder=6,
                label=landmark.label,
            )
            ax.annotate(
                f"{landmark.label}\n{landmark.timestamp_sec:.1f}초",
                xy=(landmark.timestamp_sec, oil_value),
                xytext=(8, 14 if landmark.event_type is EventType.MAXIMUM_OIL_LEVEL else -34),
                textcoords="offset points",
                fontsize=8,
                color=color,
                arrowprops={"arrowstyle": "-", "color": color, "alpha": 0.7},
                zorder=7,
            )
            continue

        if landmark.event_type in {EventType.FOAM_START, EventType.FOAM_END}:
            color = "#ea580c"
            ax.axvline(
                landmark.timestamp_sec,
                color=color,
                linewidth=0.9,
                linestyle=(0, (2, 3)),
                alpha=0.45,
            )
            if foam_value is not None:
                ax.scatter(
                    [landmark.timestamp_sec],
                    [foam_value],
                    marker="^",
                    s=32,
                    color=color,
                    zorder=5,
                )
        elif landmark.event_type is EventType.COMPRESSOR_START:
            color = "#475569"
            ax.axvline(
                landmark.timestamp_sec,
                color=color,
                linewidth=1.1,
                linestyle="--",
                alpha=0.6,
            )
        elif oil_value is not None:
            color = "#0f766e"
            ax.scatter(
                [landmark.timestamp_sec],
                [oil_value],
                marker="o",
                s=28,
                color=color,
                zorder=5,
            )
        else:
            continue

        ax.text(
            landmark.timestamp_sec,
            0.985 - 0.055 * (top_row % 3),
            landmark.label,
            transform=ax.get_xaxis_transform(),
            rotation=90,
            rotation_mode="anchor",
            va="top",
            ha="right",
            fontsize=7,
            color=color,
            alpha=0.9,
        )
        top_row += 1


def _check_cancelled(cancellation) -> None:
    if cancellation is not None and cancellation.cancelled:
        raise AnalysisCancelled("Analysis was cancelled while rendering graphs.")


def _glass_config(recipe: InspectionRecipe | None, glass_id: str):
    if recipe is None:
        return None
    return next((glass for glass in recipe.glasses if glass.id == glass_id), None)


def _value(preferred, fallback):
    return preferred if preferred is not None else fallback


def _foam_plot_points(timestamps, values):
    """Keep stored Foam markers without connecting unsupported time spans."""
    if len(timestamps) != len(values):
        raise ValueError("Foam timestamps and values must have the same length.")
    times, points = [], []
    previous_time = None
    for timestamp, value in zip(timestamps, values):
        finite = value is not None and math.isfinite(float(value))
        if (finite and previous_time is not None
                and not 0 < float(timestamp) - previous_time <= REPORT_MAX_CONTEXT_GAP_SEC):
            times.append(float(timestamp))
            points.append(math.nan)
        times.append(float(timestamp))
        points.append(float(value) if finite else math.nan)
        previous_time = float(timestamp) if finite else None
    return times, points


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
