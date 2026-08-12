from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication

from oil_tracker.domain.review import (
    ReviewGraphEventMarker,
    ReviewGraphHighlight,
    ReviewGraphModel,
    ReviewGraphPoint,
    ReviewGraphSeries,
)
from oil_tracker.ui.widgets.result_review_graph import ResultReviewGraph


def _model(cursor=1.0, *, glass_name="Glass A", foam=True):
    oil = ReviewGraphSeries("유면", (
        ReviewGraphPoint(0.0, 1.0, True, 0.9),
        ReviewGraphPoint(1.0, None, False, 0.2),
        ReviewGraphPoint(2.0, 3.0, True, 0.8),
    ))
    foam_points = (
        ReviewGraphPoint(0.0, None, True, 0.9),
        ReviewGraphPoint(1.0, 4.0 if foam else None, True, 0.8),
    )
    return ReviewGraphModel(
        glass_id="glass-a",
        glass_name=glass_name,
        unit="px",
        y_axis_label="기준선 대비 높이 (px)",
        oil_air=oil,
        foam_front=ReviewGraphSeries("거품 경계", foam_points),
        event_markers=(ReviewGraphEventMarker(1.5, "FOAM_START"),),
        highlights=(ReviewGraphHighlight(0.8, 1.2, (), ("검토",)),),
        analysis_start_sec=0.0,
        analysis_end_sec=2.0,
        compressor_start_sec=0.5,
        cursor_timestamp_sec=cursor,
        axis_lower=-10.0,
        axis_upper=12.0,
        analysis_top_boundary_value=10.0,
        analysis_bottom_boundary_value=-8.0,
        range_source="analysis_geometry",
    )


def test_graph_renders_selected_glass_unit_boundaries_and_optional_foam(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.set_model(_model())
    assert graph.axes.get_title() == "Glass A 유면 추적"
    assert graph.axes.get_ylabel() == "기준선 대비 높이 (px)"
    assert tuple(round(value, 6) for value in graph.axes.get_ylim()) == (-10.0, 12.0)
    labels = graph.axes.get_legend_handles_labels()[1]
    assert "유면" in labels
    assert "거품 경계" in labels
    assert "기준선" in labels
    assert "분석 영역 위쪽 경계" in labels
    assert "분석 영역 아래쪽 경계" in labels
    bridge = next(line for line in graph.axes.lines if line.get_label() == "관측 공백 연결")
    assert tuple(bridge.get_xdata()) == (0.0, 2.0)
    assert tuple(bridge.get_ydata()) == (1.0, 3.0)
    oil_anchors = next(collection for collection in graph.axes.collections if collection.get_label() == "유면")
    assert tuple(tuple(value) for value in oil_anchors.get_offsets()) == ((0.0, 1.0), (2.0, 3.0))
    graph.set_model(_model(glass_name="Glass B", foam=False))
    assert "Glass B" in graph.axes.get_title()
    assert "거품 경계" not in graph.axes.get_legend_handles_labels()[1]


def test_cursor_update_does_not_rebuild_series(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.set_model(_model())
    count = graph.series_rebuild_count
    graph.set_cursor(1.75)
    assert graph.series_rebuild_count == count
    assert list(graph.cursor_artist.get_xdata()) == [1.75, 1.75]


def test_graph_renders_confirmed_initial_state_hold_as_disclosed_band(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    model = replace(
        _model(foam=False),
        oil_air=ReviewGraphSeries(
            "유면",
            (
                ReviewGraphPoint(0.0, None, False, 0.2),
                ReviewGraphPoint(2.0, None, False, 0.2),
            ),
        ),
        assumed_initial_state="FULL_NO_INTERFACE",
        assumed_state_start_sec=0.0,
        assumed_state_end_sec=2.0,
    )

    graph.set_model(model)

    labels = graph.axes.get_legend_handles_labels()[1]
    assert "확정 초기 상태 유지 가정 (FULL)" in labels
    assert "유면" not in labels


def test_sustained_cursor_updates_keep_minimum_height_layout_stable_and_allow_model_replace(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.resize(790, graph.minimumHeight())
    graph.show()
    graph.set_model(_model())
    graph.canvas.draw()
    QApplication.processEvents()

    initial_rebuild_count = graph.series_rebuild_count
    initial_axes_count = len(graph.figure.axes)
    initial_line_count = len(graph.axes.lines)
    initial_callback_ids = graph._callback_ids
    initial_bounds = tuple(float(value) for value in graph.axes.get_window_extent().bounds)
    assert initial_bounds[3] >= 90.0

    final_timestamp = 0.0
    for index in range(80):
        final_timestamp = 1.0 + (index % 4) * 0.25
        graph.set_cursor(final_timestamp)
        graph.canvas.draw()

    final_bounds = tuple(float(value) for value in graph.axes.get_window_extent().bounds)
    assert graph.series_rebuild_count == initial_rebuild_count
    assert len(graph.figure.axes) == initial_axes_count
    assert len(graph.axes.lines) == initial_line_count
    assert graph._callback_ids == initial_callback_ids
    assert max(abs(after - before) for before, after in zip(initial_bounds, final_bounds)) <= 0.5
    assert list(graph.cursor_artist.get_xdata()) == [final_timestamp, final_timestamp]

    graph.set_model(_model(cursor=0.5, glass_name="Glass B", foam=False))
    graph.canvas.draw()
    replacement_bounds = tuple(float(value) for value in graph.axes.get_window_extent().bounds)
    assert graph.series_rebuild_count == initial_rebuild_count + 1
    assert graph.axes.get_title() == "Glass B 유면 추적"
    assert tuple(round(value, 6) for value in graph.axes.get_ylim()) == (-10.0, 12.0)
    assert max(abs(after - before) for before, after in zip(initial_bounds, replacement_bounds)) <= 0.5


def test_valid_axes_click_emits_timestamp_and_drag_is_ignored(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.set_model(_model())
    received = []
    graph.timestampClicked.connect(received.append)
    press = SimpleNamespace(inaxes=graph.axes, xdata=1.25, ydata=0.0, button=1, x=100.0, y=50.0)
    release = SimpleNamespace(inaxes=graph.axes, xdata=1.25, ydata=0.0, button=1, x=102.0, y=51.0)
    graph._on_press(press)
    graph._on_release(release)
    assert received == [1.25]
    graph._on_press(press)
    graph._on_release(SimpleNamespace(**{**release.__dict__, "x": 120.0}))
    assert received == [1.25]


def test_outside_none_and_nan_clicks_are_ignored(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.set_model(_model())
    received = []
    graph.timestampClicked.connect(received.append)
    graph._on_press(SimpleNamespace(inaxes=None, xdata=1.0, ydata=0.0, button=1, x=0.0, y=0.0))
    graph._on_release(SimpleNamespace(inaxes=None, xdata=1.0, button=1, x=0.0, y=0.0))
    graph._on_press(SimpleNamespace(inaxes=graph.axes, xdata=None, ydata=0.0, button=1, x=0.0, y=0.0))
    graph._on_press(SimpleNamespace(inaxes=graph.axes, xdata=float("nan"), ydata=0.0, button=1, x=0.0, y=0.0))
    assert received == []


def test_graph_close_disconnects_callbacks(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.set_model(_model())
    graph.close()
    assert graph._callback_ids == ()
