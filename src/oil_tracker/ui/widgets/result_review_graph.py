from __future__ import annotations

import math

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QToolButton, QVBoxLayout, QWidget

from oil_tracker.application.services.graph_series import observed_trajectory
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
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._font_selection = configure_matplotlib_korean_font()
        self.figure = Figure(figsize=(8.0, 2.8), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.oil_toggle = self._toggle("유면", True)
        self.foam_toggle = self._toggle("거품", True)
        self.event_toggle = self._toggle("이벤트", True)
        self.review_toggle = self._toggle("검토 구간", False)
        self.state_note = QLabel()
        self.state_note.setObjectName("reviewGraphStateNote")
        self.state_note.setVisible(False)
        controls = QHBoxLayout()
        controls.setContentsMargins(2, 0, 2, 0)
        controls.setSpacing(4)
        controls.addWidget(QLabel("표시"))
        for toggle in (self.oil_toggle, self.foam_toggle, self.event_toggle, self.review_toggle):
            controls.addWidget(toggle)
            toggle.toggled.connect(self._redraw_current_model)
        controls.addStretch(1)
        controls.addWidget(self.state_note)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addLayout(controls)
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
        self.foam_toggle.setVisible(model.foam_front.has_values)
        self._set_state_note(model.assumed_initial_state)
        self.axes.clear()
        self.axes.set_title(f"{model.glass_name} 유면 추적")
        self.axes.set_xlabel("시간 (초)")
        self.axes.set_ylabel(model.y_axis_label)
        self.axes.set_xlim(model.analysis_start_sec, model.analysis_end_sec)
        if model.axis_lower is not None and model.axis_upper is not None:
            self.axes.set_ylim(model.axis_lower, model.axis_upper)
        self.axes.axhline(0.0, linestyle=":", linewidth=1.2, alpha=0.7)
        if model.analysis_top_boundary_value is not None:
            self.axes.axhline(
                model.analysis_top_boundary_value,
                linestyle="--",
                linewidth=0.9,
                alpha=0.35,
            )
        if model.analysis_bottom_boundary_value is not None:
            self.axes.axhline(
                model.analysis_bottom_boundary_value,
                linestyle="--",
                linewidth=0.9,
                alpha=0.35,
            )
        if (
            model.assumed_initial_state
            and model.assumed_state_start_sec is not None
            and model.assumed_state_end_sec is not None
        ):
            full = model.assumed_initial_state in {
                "FULL_NO_INTERFACE",
                "FULL_WITH_FOAM",
            }
            self.axes.axvspan(
                model.assumed_state_start_sec,
                model.assumed_state_end_sec,
                alpha=0.09,
                color="#3b82f6" if full else "#f59e0b",
            )
        if model.compressor_start_sec is not None:
            self.axes.scatter(
                [model.compressor_start_sec],
                [0.02],
                transform=self.axes.get_xaxis_transform(),
                marker="^",
                s=24,
                color="#f97316",
                zorder=5,
            )
        if self.review_toggle.isChecked():
            for highlight in model.highlights:
                end = max(highlight.start_time_sec, highlight.end_time_sec)
                self.axes.axvspan(highlight.start_time_sec, end, alpha=0.1, color="#dc2626")
        if self.event_toggle.isChecked() and model.event_markers:
            self.axes.scatter(
                [marker.timestamp_sec for marker in model.event_markers],
                [0.025] * len(model.event_markers),
                transform=self.axes.get_xaxis_transform(),
                marker="|",
                s=70,
                linewidths=1.1,
                color="#7c3aed",
                zorder=5,
            )
        if model.selected_event_timestamp_sec is not None:
            self.axes.axvline(
                model.selected_event_timestamp_sec,
                linewidth=1.5,
                color="#7c3aed",
                alpha=0.9,
            )
        if model.debug_markers:
            self.axes.scatter(
                [marker.timestamp_sec for marker in model.debug_markers],
                [0.075] * len(model.debug_markers),
                transform=self.axes.get_xaxis_transform(),
                marker="s",
                s=[36 if marker.selected else 14 for marker in model.debug_markers],
                facecolors=["#0891b2" if marker.selected else "none" for marker in model.debug_markers],
                edgecolors="#0891b2",
                zorder=6,
            )
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
        if self.oil_toggle.isChecked():
            self._plot_series(
                model.oil_air.points,
                model.oil_air.name,
                "-",
                connect_observed_anchors=True,
            )
        if self.foam_toggle.isChecked() and model.foam_front.has_values:
            self._plot_series(model.foam_front.points, model.foam_front.name, "--")
        self.cursor_artist = self.axes.axvline(
            model.cursor_timestamp_sec,
            linewidth=1.4,
            color="#111827",
        )
        self.axes.grid(True, alpha=0.2)
        apply_font_to_axes(self.axes, self._font_selection)
        self.canvas.draw_idle()

    @staticmethod
    def _toggle(text: str, checked: bool) -> QToolButton:
        button = QToolButton()
        button.setText(text)
        button.setCheckable(True)
        button.setChecked(checked)
        button.setAutoRaise(True)
        return button

    def _redraw_current_model(self, _checked: bool = False) -> None:
        if self.model is not None:
            self.set_model(self.model)

    def _set_state_note(self, state: str) -> None:
        labels = {
            "FULL_NO_INTERFACE": "초기 상태: 오일이 가득 참으로 확인됨",
            "FULL_WITH_FOAM": "초기 상태: 거품이 있는 가득 찬 상태로 확인됨",
            "EMPTY_NO_INTERFACE": "초기 상태: 오일이 비어 있음으로 확인됨",
        }
        self.state_note.setText(labels.get(state, ""))
        self.state_note.setVisible(state in labels)

    def _plot_series(
        self,
        points,
        label: str,
        linestyle: str,
        *,
        connect_observed_anchors: bool = False,
    ) -> None:
        times = [point.timestamp_sec for point in points]
        values = [
            float("nan")
            if point.value is None or not point.is_valid
            else point.value
            for point in points
        ]
        if connect_observed_anchors:
            trajectory = observed_trajectory(times, values)
            anchors = trajectory.anchors
            if not anchors:
                return
            labelled = False
            for run in trajectory.observed_runs:
                if len(run.timestamps) < 2:
                    continue
                self.axes.plot(
                    run.timestamps,
                    run.values,
                    linestyle="-",
                    linewidth=1.7,
                    color="#2563eb",
                    label=label if not labelled else None,
                )
                labelled = True
            for index, bridge in enumerate(trajectory.gap_bridges):
                self.axes.plot(
                    bridge.timestamps,
                    bridge.values,
                    linestyle=(0, (4, 3)),
                    linewidth=1.45,
                    color="#2563eb",
                    alpha=0.7,
                    label="관측 공백 연결" if index == 0 else None,
                )
            anchor_times, anchor_values = zip(*anchors)
            self.axes.scatter(
                anchor_times,
                anchor_values,
                s=10,
                color="#2563eb",
                alpha=0.7,
                label=label if not labelled else None,
            )
            return
        if times:
            self.axes.plot(
                times,
                values,
                linestyle=linestyle,
                linewidth=1.6,
                color="#f97316" if label == "거품 경계" else None,
                marker="o" if label == "거품 경계" else None,
                markersize=4 if label == "거품 경계" else None,
                label=label,
            )

    def set_cursor(self, timestamp_sec: float) -> None:
        if self.model is None or self.cursor_artist is None:
            return
        value = min(self.model.analysis_end_sec, max(self.model.analysis_start_sec, float(timestamp_sec)))
        self.cursor_artist.set_xdata([value, value])
        self.canvas.draw_idle()

    def clear_model(self) -> None:
        self.model = None
        self.cursor_artist = None
        self.state_note.setVisible(False)
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
