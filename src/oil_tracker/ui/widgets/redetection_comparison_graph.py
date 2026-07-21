from __future__ import annotations

import math

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from oil_tracker.application.services.graph_axis import graph_axis_range_for_glass
from oil_tracker.visualization.matplotlib_font import (
    apply_font_to_axes,
    configure_matplotlib_korean_font,
)


class RedetectionComparisonGraph(QWidget):
    comparisonSelected = Signal(int, float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._font_selection = configure_matplotlib_korean_font()
        self.figure = Figure(figsize=(8.0, 3.2), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self._points = ()
        self._target_timestamp = 0.0
        self._selection_artist = None
        self._callback = self.canvas.mpl_connect("button_release_event", self._clicked)
        self.clear("재검출 결과가 없습니다.")

    def set_result(self, result, glass) -> None:
        self._update_adjacent_table_headers()
        self._points = tuple(result.comparisons)
        self._target_timestamp = result.request.target_timestamp_sec
        use_mm = bool(glass.mm_per_pixel and glass.mm_per_pixel > 0) and any(
            _oil(point.official_sample, "mm") is not None
            or _oil(_tracking(point), "mm") is not None
            or _foam(point.official_sample, "mm") is not None
            or _foam(_tracking(point), "mm") is not None
            for point in self._points
        )
        unit = "mm" if use_mm else "px"
        official_oil = [_oil(point.official_sample, unit) for point in self._points]
        rerun_oil = [_oil(_tracking(point), unit) for point in self._points]
        official_foam = [_foam(point.official_sample, unit) for point in self._points]
        rerun_foam = [_foam(_tracking(point), unit) for point in self._points]
        axis_range = graph_axis_range_for_glass(
            glass,
            unit=unit,
            observed_values=(*official_oil, *rerun_oil, *official_foam, *rerun_foam),
        )
        self.axes.clear()
        self.axes.set_title(f"{glass.name} 재검출 비교")
        self.axes.set_xlabel("시간 (초)")
        self.axes.set_ylabel(f"기준선 대비 높이 ({unit})")
        if axis_range.available:
            self.axes.set_ylim(axis_range.lower, axis_range.upper)
        self.axes.axhline(0.0, linestyle=":", linewidth=1.2, label="기준선")
        if axis_range.analysis_top_boundary is not None:
            self.axes.axhline(
                axis_range.analysis_top_boundary,
                linestyle="--",
                linewidth=0.9,
                alpha=0.65,
                label="분석 영역 위쪽 경계",
            )
        if axis_range.analysis_bottom_boundary is not None:
            self.axes.axhline(
                axis_range.analysis_bottom_boundary,
                linestyle="--",
                linewidth=0.9,
                alpha=0.65,
                label="분석 영역 아래쪽 경계",
            )
        self.axes.axvline(
            self._target_timestamp,
            linestyle="--",
            linewidth=1.1,
            label="재검출 기준 시각",
        )
        times = [point.nominal_timestamp_sec for point in self._points]
        self._plot(times, official_oil, "공식 유면", "-")
        self._plot(times, rerun_oil, "재검출 유면", "-")
        self._plot(times, official_foam, "공식 거품 경계", "--")
        self._plot(times, rerun_foam, "재검출 거품 경계", "--")
        for event in result.rerun_events:
            self.axes.axvline(event.start_time_sec, linewidth=0.6, alpha=0.2)
        unmatched = [
            point.nominal_timestamp_sec
            for point in self._points
            if point.match_status != "matched"
        ]
        changed = [
            point.nominal_timestamp_sec
            for point in self._points
            if point.fill_state_same is False or point.validity_same is False
        ]
        if unmatched:
            self.axes.scatter(unmatched, [0.0] * len(unmatched), marker="x", label="미일치")
        if changed:
            self.axes.scatter(changed, [0.0] * len(changed), marker="o", facecolors="none", label="상태/유효성 변경")
        self._selection_artist = self.axes.axvline(
            self._target_timestamp,
            linewidth=1.7,
            label="선택 비교",
        )
        self.axes.grid(True, alpha=0.2)
        handles, labels = self.axes.get_legend_handles_labels()
        if handles:
            unique = dict(zip(labels, handles))
            self.axes.legend(
                unique.values(),
                unique.keys(),
                loc="best",
                fontsize="small",
                prop=self._font_selection.properties,
            )
        apply_font_to_axes(self.axes, self._font_selection)
        self.canvas.draw_idle()

    def select_index(self, index: int) -> None:
        if index < 0 or index >= len(self._points) or self._selection_artist is None:
            return
        timestamp = self._points[index].nominal_timestamp_sec
        self._selection_artist.set_xdata([timestamp, timestamp])
        self.canvas.draw_idle()

    def clear(self, message: str) -> None:
        self._points = ()
        self.axes.clear()
        self.axes.set_title("재검출 비교 graph")
        self.axes.text(0.5, 0.5, message, ha="center", va="center", transform=self.axes.transAxes)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        apply_font_to_axes(self.axes, self._font_selection)
        self.canvas.draw_idle()

    def _plot(self, times, values, label: str, linestyle: str) -> None:
        if not any(value is not None for value in values):
            return
        self.axes.plot(
            times,
            [float("nan") if value is None else value for value in values],
            linestyle=linestyle,
            linewidth=1.5,
            label=label,
        )

    def _update_adjacent_table_headers(self) -> None:
        table = getattr(self.window(), "tracking_table", None)
        if table is None:
            return
        table.setHorizontalHeaderLabels(
            (
                "기준 시각",
                "공식 시각",
                "재검출 시각",
                "공식 유면",
                "재검출 유면",
                "유면 Δ",
                "공식 거품 경계",
                "재검출 거품 경계",
                "거품 경계 Δ",
                "신뢰도 Δ",
                "상태",
                "유효성",
                "일치 상태",
            )
        )

    def _clicked(self, event) -> None:
        if event.inaxes is not self.axes or event.xdata is None or not self._points:
            return
        value = float(event.xdata)
        if not math.isfinite(value):
            return
        index = min(
            range(len(self._points)),
            key=lambda item: (
                abs(self._points[item].nominal_timestamp_sec - value),
                item,
            ),
        )
        timestamp = self._points[index].rerun_actual_timestamp_sec
        if timestamp is None:
            timestamp = self._points[index].official_timestamp_sec
        if timestamp is None:
            timestamp = self._points[index].nominal_timestamp_sec
        self.select_index(index)
        self.comparisonSelected.emit(index, float(timestamp))

    def closeEvent(self, event) -> None:
        if self._callback is not None:
            self.canvas.mpl_disconnect(self._callback)
        self._callback = None
        self.figure.clear()
        super().closeEvent(event)


def _tracking(point):
    return point.rerun_sample.tracking_sample if point.rerun_sample is not None else None


def _first(preferred, fallback):
    return preferred if preferred is not None else fallback


def _oil(sample, unit: str):
    if sample is None:
        return None
    if unit == "mm":
        return _first(sample.smoothed_oil_air_level_mm_from_zero, sample.raw_oil_air_level_mm_from_zero)
    return _first(sample.smoothed_oil_air_level_px_from_zero, sample.raw_oil_air_level_px_from_zero)


def _foam(sample, unit: str):
    if sample is None:
        return None
    if unit == "mm":
        return _first(sample.smoothed_foam_front_mm_from_zero, sample.raw_foam_front_mm_from_zero)
    return _first(sample.smoothed_foam_front_px_from_zero, sample.raw_foam_front_px_from_zero)
