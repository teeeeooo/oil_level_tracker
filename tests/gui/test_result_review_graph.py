from __future__ import annotations

from types import SimpleNamespace

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
        y_axis_label="기준점 대비 높이 (px)",
        oil_air=oil,
        foam_front=ReviewGraphSeries("거품 경계", foam_points),
        event_markers=(ReviewGraphEventMarker(1.5, "FOAM_START"),),
        highlights=(ReviewGraphHighlight(0.8, 1.2, (), ("검토",)),),
        analysis_start_sec=0.0,
        analysis_end_sec=2.0,
        compressor_start_sec=0.5,
        cursor_timestamp_sec=cursor,
    )


def test_graph_renders_selected_glass_unit_and_optional_foam(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.set_model(_model())
    assert "Glass A" in graph.axes.get_title()
    assert graph.axes.get_ylabel() == "기준점 대비 높이 (px)"
    labels = graph.axes.get_legend_handles_labels()[1]
    assert "유면" in labels
    assert "거품 경계" in labels
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
