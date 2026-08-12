from __future__ import annotations

import math

from matplotlib.axes import Axes

from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
from oil_tracker.domain.enums import (
    FillState,
    InitialObservationState,
    ResultState,
)
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.retrospective import (
    RetrospectiveInterpretation,
    RetrospectiveStatus,
)
from oil_tracker.domain.results import GlassAnalysisResult, TrackingSample


def test_static_detail_connects_oil_anchors_but_preserves_foam_gaps(
    tmp_path,
    monkeypatch,
) -> None:
    calls: dict[str, tuple[tuple[float, ...], tuple[float, ...]]] = {}
    scatter_calls: dict[str, tuple[tuple[float, ...], tuple[float, ...]]] = {}
    original_plot = Axes.plot
    original_scatter = Axes.scatter

    def recording_plot(self, x_values, y_values, *args, **kwargs):
        label = kwargs.get("label")
        if label in {"관측 공백 연결", "거품 경계"}:
            calls[label] = (tuple(x_values), tuple(y_values))
        return original_plot(self, x_values, y_values, *args, **kwargs)

    def recording_scatter(self, x_values, y_values, *args, **kwargs):
        label = kwargs.get("label")
        if label == "관측 유면":
            scatter_calls[label] = (tuple(x_values), tuple(y_values))
        return original_scatter(self, x_values, y_values, *args, **kwargs)

    monkeypatch.setattr(Axes, "plot", recording_plot)
    monkeypatch.setattr(Axes, "scatter", recording_scatter)
    glass = InspectionRecipe.default_glass(320, 240, 1)
    result = GlassAnalysisResult(
        glass_id=glass.id,
        glass_name=glass.name,
        result_state=ResultState.REVIEW_REQUIRED,
        samples=[
            _sample(glass.id, 0.0, 1.0, None),
            _sample(glass.id, 1.0, None, 4.0),
            _sample(glass.id, 2.0, 3.0, None),
        ],
    )

    output = tmp_path / "detail.png"
    GraphRenderer()._render_glass(result, glass, output)

    assert output.is_file()
    assert scatter_calls["관측 유면"] == ((0.0, 2.0), (1.0, 3.0))
    assert calls["관측 공백 연결"] == ((0.0, 2.0), (1.0, 3.0))
    foam_times, foam_values = calls["거품 경계"]
    assert foam_times == (0.0, 1.0, 2.0)
    assert math.isnan(foam_values[0])
    assert foam_values[1] == 4.0
    assert math.isnan(foam_values[2])

    calls.clear()
    scatter_calls.clear()
    result.samples = [
        _sample(glass.id, 0.0, None, None),
        _sample(glass.id, 1.0, None, 4.0),
    ]
    GraphRenderer()._render_glass(result, glass, tmp_path / "all-missing-oil.png")
    assert "관측 유면" not in scatter_calls


def _sample(
    glass_id: str,
    timestamp: float,
    oil: float | None,
    foam: float | None,
) -> TrackingSample:
    return TrackingSample(
        run_id="run",
        glass_id=glass_id,
        frame_index=int(timestamp * 10),
        timestamp_sec=timestamp,
        fill_state=FillState.UNKNOWN_REVIEW if oil is None else FillState.PARTIAL_VISIBLE,
        raw_oil_air_level_px_from_zero=oil,
        raw_foam_front_px_from_zero=foam,
    )


def test_detail_graph_renders_confirmed_initial_state_hold_without_oil_line(
    tmp_path,
    monkeypatch,
) -> None:
    spans: list[str | None] = []
    original = Axes.axvspan

    def recording_span(self, xmin, xmax, *args, **kwargs):
        spans.append(kwargs.get("label"))
        return original(self, xmin, xmax, *args, **kwargs)

    monkeypatch.setattr(Axes, "axvspan", recording_span)
    config = InspectionRecipe.default_glass(320, 240, 1)
    result = GlassAnalysisResult(
        glass_id=config.id,
        glass_name=config.name,
        result_state=ResultState.REVIEW_REQUIRED,
        samples=[
            _sample(config.id, 0.0, None, None),
            _sample(config.id, 1.0, None, None),
        ],
        retrospective=RetrospectiveInterpretation(
            glass_id=config.id,
            status=RetrospectiveStatus.ACCEPTED,
            confirmed_prior=InitialObservationState.FULL_NO_INTERFACE,
            interpreted_state=FillState.FULL_NO_INTERFACE,
            start_time_sec=0.0,
            end_time_sec=1.0,
            provenance="confirmed_initial_state_hold_v1",
        ),
    )

    GraphRenderer()._render_glass(result, config, tmp_path / "initial-hold.png")

    assert "확정 초기 상태 유지 가정 (FULL)" in spans
