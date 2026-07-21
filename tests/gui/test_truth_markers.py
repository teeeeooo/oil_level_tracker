from __future__ import annotations

from types import SimpleNamespace

from oil_tracker.domain.review import (
    ReviewGraphModel,
    ReviewGraphPoint,
    ReviewGraphSeries,
    ReviewGraphTruthMarker,
)
from oil_tracker.ui.widgets.result_review_graph import ResultReviewGraph
from oil_tracker.ui.widgets.transport_bar import MarkerSlider


def _model(*, selected: bool = False) -> ReviewGraphModel:
    points = (
        ReviewGraphPoint(1.0, 0.0, True, 0.9),
        ReviewGraphPoint(2.0, 1.0, True, 0.8),
        ReviewGraphPoint(3.0, 2.0, True, 0.7),
    )
    return ReviewGraphModel(
        glass_id="glass-1",
        glass_name="관찰창 1",
        unit="px",
        y_axis_label="유면 (px)",
        oil_air=ReviewGraphSeries("공식 유면", points),
        foam_front=ReviewGraphSeries("공식 foam", ()),
        event_markers=(),
        highlights=(),
        analysis_start_sec=1.0,
        analysis_end_sec=3.0,
        compressor_start_sec=1.5,
        cursor_timestamp_sec=1.0,
        truth_markers=(
            ReviewGraphTruthMarker(
                timestamp_sec=2.0,
                annotation_id="truth-1",
                disposition="corrected",
                error_types=("wrong_candidate",),
                selected=selected,
            ),
        ),
    )


def test_graph_truth_marker_is_separate_from_official_series_and_labeled(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    model = _model(selected=True)
    original_points = model.oil_air.points
    graph.set_model(model)
    assert graph.model.oil_air.points is original_points
    truth_artists = [artist for artist in graph.axes.lines if str(artist.get_gid()).startswith("truth:")]
    assert len(truth_artists) == 1
    assert truth_artists[0].get_gid() == "truth:truth-1:corrected:wrong_candidate"
    labels = [artist.get_label() for artist in graph.axes.lines]
    assert "선택 사용자 정답" in labels


def test_clicking_truth_marker_emits_annotation_identity_instead_of_generic_seek(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.set_model(_model())
    graph.canvas.draw()
    clicked = []
    generic = []
    graph.truthMarkerClicked.connect(lambda annotation_id, timestamp: clicked.append((annotation_id, timestamp)))
    graph.timestampClicked.connect(generic.append)
    x_pixel, y_pixel = graph.axes.transData.transform((2.0, 1.0))
    event = SimpleNamespace(
        inaxes=graph.axes,
        xdata=2.0,
        ydata=1.0,
        x=x_pixel,
        y=y_pixel,
        button=1,
    )
    graph._on_press(event)
    graph._on_release(event)
    assert clicked == [("truth-1", 2.0)]
    assert generic == []


def test_click_away_from_truth_marker_keeps_existing_timestamp_navigation(qtbot):
    graph = ResultReviewGraph()
    qtbot.addWidget(graph)
    graph.set_model(_model())
    graph.canvas.draw()
    clicked = []
    graph.timestampClicked.connect(clicked.append)
    x_pixel, y_pixel = graph.axes.transData.transform((2.5, 1.0))
    event = SimpleNamespace(
        inaxes=graph.axes,
        xdata=2.5,
        ydata=1.0,
        x=x_pixel,
        y=y_pixel,
        button=1,
    )
    graph._on_press(event)
    graph._on_release(event)
    assert clicked == [2.5]


def test_timeline_truth_markers_have_disposition_and_selection_without_changing_review_markers(qtbot):
    slider = MarkerSlider()
    qtbot.addWidget(slider)
    slider.set_review_markers(8.0, (1.5,), ((2.0, 2.5),))
    review_points = list(slider._review_points)
    review_intervals = list(slider._review_intervals)
    slider.set_truth_markers(8.0, _model(selected=True).truth_markers)
    assert slider._truth_points == [(2.0, "corrected", True)]
    assert slider._review_points == review_points
    assert slider._review_intervals == review_intervals
    assert "사용자 정답" in slider.toolTip()
    slider.clear_review_markers()
    assert slider._truth_points == []
