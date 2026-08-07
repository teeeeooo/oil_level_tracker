from __future__ import annotations

import math

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from oil_tracker.application.services.graph_series import continuous_observed_polyline
from oil_tracker.domain.review import ReviewGraphModel
from oil_tracker.visualization.matplotlib_font import (
    apply_font_to_axes,
    configure_matplotlib_korean_font,
)


class ResultReviewGraph(QWidget):
    timestampClicked = Signal(float)
    truthMarkerClicked = Signal(str, float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("resultReviewGraph")
        self.setMinimumHeight(190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._font_selection = configure_matplotlib_korean_font()
        self.figure = Figure(figsize=(8.0, 2.8), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.model: ReviewGraphModel | None = None
        self.cursor_artist = None
        self.series_rebuild_count = 0
        self._press = None
        self._callback_ids = (
            self.canvas.mpl_connect("button_press_event", self._on_press),
            self.canvas.mpl_connect("button_release_event", self._on_release),
        )
        self.clear_model()

    def set_model(self, model: ReviewGraphModel) -> None:
        self.model = model
        self.series_rebuild_count += 1
        self.axes.clear()
        self.axes.set_title(f"{model.glass_name} 유면 추적")
        self.axes.set_xlabel("시간 (초)")
        self.axes.set_ylabel(model.y_axis_label)
        self.axes.set_xlim(model.analysis_start_sec, model.analysis_end_sec)
        if model.axis_lower is not None and model.axis_upper is not None:
            self.axes.set_ylim(model.axis_lower, model.axis_upper)
        self.axes.axhline(0.0, linestyle=":", linewidth=1.2, label="기준선")
        if model.analysis_top_boundary_value is not None:
            self.axes.axhline(
                model.analysis_top_boundary_value,
                linestyle="--",
                linewidth=0.9,
                alpha=0.65,
                label="분석 영역 위쪽 경계",
            )
        if model.analysis_bottom_boundary_value is not None:
            self.axes.axhline(
                model.analysis_bottom_boundary_value,
                linestyle="--",
                linewidth=0.9,
                alpha=0.65,
                label="분석 영역 아래쪽 경계",
            )
        self.axes.axvline(model.analysis_start_sec, linewidth=0.8, alpha=0.45, label="분석 범위")
        self.axes.axvline(model.analysis_end_sec, linewidth=0.8, alpha=0.45)
        if model.compressor_start_sec is not None:
            self.axes.axvline(model.compressor_start_sec, linestyle="--", linewidth=1.0, label="압축기 기동")
        for highlight in model.highlights:
            end = max(highlight.start_time_sec, highlight.end_time_sec)
            self.axes.axvspan(highlight.start_time_sec, end, alpha=0.12, hatch="//")
        for marker in model.event_markers:
            self.axes.axvline(marker.timestamp_sec, linewidth=0.6, alpha=0.18)
        for index, marker in enumerate(model.debug_markers):
            artist = self.axes.axvline(
                marker.timestamp_sec,
                linestyle="-.",
                linewidth=2.2 if marker.selected else 0.9,
                alpha=0.95 if marker.selected else 0.35,
                label="선택 디버그 장면" if marker.selected else "디버그 기록" if index == 0 else None,
            )
            artist.set_gid("debug:" + "|".join(marker.reasons))
        for index, marker in enumerate(model.truth_markers):
            artist = self.axes.axvline(
                marker.timestamp_sec,
                linestyle=(0, (1.0, 1.4)),
                linewidth=2.8 if marker.selected else 1.1,
                alpha=1.0 if marker.selected else 0.55,
                label=(
                    "선택 사용자 정답"
                    if marker.selected
                    else "사용자 정답"
                    if index == 0
                    else None
                ),
            )
            artist.set_gid(
                "truth:"
                + marker.annotation_id
                + ":"
                + marker.disposition
                + ":"
                + "|".join(marker.error_types)
            )
        self._plot_series(
            model.oil_air.points,
            model.oil_air.name,
            "-",
            connect_observed_anchors=True,
        )
        if model.foam_front.has_values:
            self._plot_series(model.foam_front.points, model.foam_front.name, "--")
        self.cursor_artist = self.axes.axvline(
            model.cursor_timestamp_sec,
            linewidth=1.4,
            label="현재 영상 시각",
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
                # Keep the legend shorter than the minimum-height plotting area.
                # A tall single-column legend makes tight_layout progressively
                # squeeze the axes during cursor-only playback redraws.
                ncols=3,
            )
        apply_font_to_axes(self.axes, self._font_selection)
        self.canvas.draw_idle()

    def _plot_series(
        self,
        points,
        label: str,
        linestyle: str,
        *,
        connect_observed_anchors: bool = False,
    ) -> None:
        times = [point.timestamp_sec for point in points]
        values = [float("nan") if point.value is None else point.value for point in points]
        if connect_observed_anchors:
            times, values = continuous_observed_polyline(times, values)
        if times:
            self.axes.plot(times, values, linestyle=linestyle, linewidth=1.6, label=label)

    def set_cursor(self, timestamp_sec: float) -> None:
        if self.model is None or self.cursor_artist is None:
            return
        value = min(self.model.analysis_end_sec, max(self.model.analysis_start_sec, float(timestamp_sec)))
        self.cursor_artist.set_xdata([value, value])
        self.canvas.draw_idle()

    def clear_model(self) -> None:
        self.model = None
        self.cursor_artist = None
        self.axes.clear()
        self.axes.set_title("유면 추적 graph")
        self.axes.text(0.5, 0.5, "결과 bundle을 열어 주세요.", ha="center", va="center", transform=self.axes.transAxes)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        apply_font_to_axes(self.axes, self._font_selection)
        self.canvas.draw_idle()

    def _on_press(self, event) -> None:
        if event.inaxes is not self.axes or event.xdata is None or event.ydata is None:
            self._press = None
            return
        if event.button != 1 or not math.isfinite(float(event.xdata)):
            self._press = None
            return
        toolbar = getattr(getattr(self.canvas, "manager", None), "toolbar", None)
        if toolbar is not None and getattr(toolbar, "mode", ""):
            self._press = None
            return
        self._press = (float(event.x), float(event.y), float(event.xdata))

    def _on_release(self, event) -> None:
        press, self._press = self._press, None
        if press is None or self.model is None:
            return
        if event.inaxes is not self.axes or event.xdata is None or event.button != 1:
            return
        value = float(event.xdata)
        if not math.isfinite(value):
            return
        if math.hypot(float(event.x) - press[0], float(event.y) - press[1]) > 4.0:
            return
        marker = self._truth_marker_at_pixel(float(event.x))
        if marker is not None:
            self.truthMarkerClicked.emit(marker.annotation_id, marker.timestamp_sec)
            return
        self.timestampClicked.emit(
            min(self.model.analysis_end_sec, max(self.model.analysis_start_sec, value))
        )

    def _truth_marker_at_pixel(self, x_pixel: float):
        if self.model is None or not self.model.truth_markers:
            return None
        candidates = []
        for marker in self.model.truth_markers:
            marker_x = float(self.axes.transData.transform((marker.timestamp_sec, 0.0))[0])
            candidates.append((abs(marker_x - x_pixel), marker.timestamp_sec, marker.annotation_id, marker))
        distance, _timestamp, _annotation_id, marker = min(candidates)
        return marker if distance <= 7.0 else None

    def closeEvent(self, event) -> None:
        for callback_id in self._callback_ids:
            self.canvas.mpl_disconnect(callback_id)
        self._callback_ids = ()
        self._press = None
        self.clear_model()
        self.figure.clear()
        super().closeEvent(event)
