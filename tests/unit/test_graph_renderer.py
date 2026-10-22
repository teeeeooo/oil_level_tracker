from __future__ import annotations

import math

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer, _state_band_runs
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
    calls: dict[str, tuple[tuple[float, ...], tuple[float, ...], str]] = {}
    scatter_calls: dict[str, tuple[tuple[float, ...], tuple[float, ...]]] = {}
    original_plot = Axes.plot
    original_scatter = Axes.scatter

    def recording_plot(self, x_values, y_values, *args, **kwargs):
        label = kwargs.get("label")
        if label in {"관측 공백 연결", "거품 경계"}:
            calls[label] = (
                tuple(x_values),
                tuple(y_values),
                kwargs.get("marker", ""),
            )
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
    assert calls["관측 공백 연결"][:2] == ((0.0, 2.0), (1.0, 3.0))
    foam_times, foam_values, foam_marker = calls["거품 경계"]
    assert foam_times == (0.0, 1.0, 2.0)
    assert math.isnan(foam_values[0])
    assert foam_values[1] == 4.0
    assert math.isnan(foam_values[2])
    assert foam_marker == "o"

    calls.clear()
    scatter_calls.clear()
    result.samples[-1].timestamp_sec = 10.0
    GraphRenderer()._render_glass(result, glass, tmp_path / "long-gap.png")
    assert scatter_calls["관측 유면"] == ((0.0, 10.0), (1.0, 3.0))
    assert "관측 공백 연결" not in calls

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
    hatches: dict[str | None, str | None] = {}
    original = Axes.axvspan

    def recording_span(self, xmin, xmax, *args, **kwargs):
        spans.append(kwargs.get("label"))
        hatches[kwargs.get("label")] = kwargs.get("hatch")
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
    assert hatches["확정 초기 상태 유지 가정 (FULL)"] == ".."


def test_foam_long_timestamp_gap_breaks_in_combined_and_detail(tmp_path, monkeypatch):
    from types import SimpleNamespace
    calls = []
    original = Axes.plot
    def record(self, x, y, *args, **kwargs):
        if "거품 경계" in (kwargs.get("label") or ""):
            calls.append((list(x), list(y)))
        return original(self, x, y, *args, **kwargs)
    monkeypatch.setattr(Axes, "plot", record)
    config = InspectionRecipe.default_glass(320, 240, 1)
    glass = GlassAnalysisResult(config.id, config.name, ResultState.REVIEW_REQUIRED,
        samples=[_sample(config.id, 0, None, 4), _sample(config.id, 3, None, 5)])
    renderer = GraphRenderer()
    renderer._render_glass(glass, config, tmp_path / "foam-detail.png")
    result = SimpleNamespace(glass_results=[glass], overall_state=ResultState.REVIEW_REQUIRED)
    renderer._render_combined(result, None, tmp_path / "foam-combined.png")
    assert len(calls) == 2
    for times, values in calls:
        assert times == [0, 3, 3]
        assert values[0] == 4 and values[-1] == 5
        assert math.isnan(values[1])
    assert [s.raw_foam_front_px_from_zero for s in glass.samples] == [4, 5]


def test_detail_graph_labels_detector_and_reconstructed_state_bands(tmp_path, monkeypatch) -> None:
    spans = _record_spans(monkeypatch)
    config = InspectionRecipe.default_glass(320, 240, 1)
    result = _reconstructed_then_top_exit_full(config)

    GraphRenderer()._render_glass(result, config, tmp_path / "bands.png")

    styles = {span["label"]: span for span in spans if span["label"]}
    assert styles["초기 상태 재구성 (FULL)"]["face_alpha"] == 0.09
    assert styles["초기 상태 재구성 (FULL)"]["hatch"] == "///"
    assert styles["FULL 판정"]["face_alpha"] == 0.09
    assert styles["FULL 판정"]["hatch"] is None
    assert "확정 초기 상태 유지 가정 (FULL)" not in styles


def test_combined_graph_adds_one_state_row_per_glass_under_the_lines(tmp_path, monkeypatch) -> None:
    spans = _record_spans(monkeypatch)
    base = InspectionRecipe.default_glass(320, 240, 1)
    accum = InspectionRecipe.default_glass(320, 240, 2)
    first = _reconstructed_then_top_exit_full(base)
    second = GlassAnalysisResult(
        glass_id=accum.id,
        glass_name="Accum",
        result_state=ResultState.REVIEW_REQUIRED,
        samples=[_sample(accum.id, 0.0, None, 4.0), _sample(accum.id, 1.0, None, 5.0)],
    )
    from types import SimpleNamespace
    result = SimpleNamespace(glass_results=[first, second], overall_state=ResultState.REVIEW_REQUIRED)

    GraphRenderer()._render_combined(result, None, tmp_path / "combined.png")

    strip = spans[0]["axes"]
    lines = next(axes for axes in strip.figure.axes if axes is not strip)
    assert all(span["axes"] is strip for span in spans)
    assert not lines.patches
    assert [label.get_text() for label in strip.get_yticklabels()] == [first.glass_name, "Accum"]
    rows = {(span["label"], span["hatch"], span["ymin"] >= 0.5) for span in spans}
    assert rows == {
        ("초기 상태 재구성 (FULL)", "///", True),
        ("FULL 판정", None, True),
        ("직접 유면 확인 어려움", None, False),
    }
    # The strip draws the detail-graph runs, only filled more strongly.
    assert {span["face_alpha"] for span in spans if span["label"] == "FULL 판정"} == {0.27}


def test_combined_graph_without_state_bands_keeps_lines_only(tmp_path, monkeypatch) -> None:
    spans = _record_spans(monkeypatch)
    config = InspectionRecipe.default_glass(320, 240, 1)
    glass = GlassAnalysisResult(
        glass_id=config.id,
        glass_name=config.name,
        result_state=ResultState.PASS,
        samples=[_sample(config.id, 0.0, 1.0, None), _sample(config.id, 1.0, 2.0, None)],
    )
    from types import SimpleNamespace
    figures = []
    original = Figure.savefig

    def recording_savefig(self, *args, **kwargs):
        figures.append(len(self.axes))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Figure, "savefig", recording_savefig)
    result = SimpleNamespace(glass_results=[glass], overall_state=ResultState.PASS)

    GraphRenderer()._render_combined(result, None, tmp_path / "combined.png")

    assert figures == [1]
    assert spans == []


def test_state_band_runs_give_each_sample_its_own_cell() -> None:
    config = InspectionRecipe.default_glass(320, 240, 1)
    glass = _glass_with_states(config, [
        (0.0, FillState.UNKNOWN_REVIEW),
        (0.5, FillState.EMPTY_NO_INTERFACE),
        (1.0, FillState.UNKNOWN_REVIEW),
        (1.5, FillState.PARTIAL_VISIBLE),
        (2.0, FillState.UNKNOWN_REVIEW),
    ])

    # Neighbouring runs meet halfway, the numeric sample keeps its own cell
    # blank, and no band reaches past the first or last sample.
    assert _state_band_runs(glass) == [
        (0.0, 0.25, "UNKNOWN", "detector"),
        (0.25, 0.75, "EMPTY", "detector"),
        (0.75, 1.25, "UNKNOWN", "detector"),
        (1.75, 2.0, "UNKNOWN", "detector"),
    ]


def test_state_band_runs_leave_long_gaps_blank() -> None:
    config = InspectionRecipe.default_glass(320, 240, 1)
    unknown = FillState.UNKNOWN_REVIEW
    glass = _glass_with_states(config, [(0.0, unknown), (0.5, unknown), (4.0, unknown), (4.5, unknown)])

    # Over the 2 s line-connection limit each side reaches 1 s and the run splits.
    assert _state_band_runs(glass) == [
        (0.0, 1.5, "UNKNOWN", "detector"),
        (3.0, 4.5, "UNKNOWN", "detector"),
    ]
    assert _state_band_runs(_glass_with_states(config, [(0.0, unknown)])) == []


def test_one_sample_state_is_drawn_where_the_legend_lists_it(tmp_path, monkeypatch) -> None:
    spans = _record_spans(monkeypatch)
    config = InspectionRecipe.default_glass(320, 240, 1)
    glass = _glass_with_states(config, [
        (24.0, FillState.UNKNOWN_REVIEW),
        (24.5, FillState.EMPTY_NO_INTERFACE),
        (25.0, FillState.UNKNOWN_REVIEW),
    ])
    from types import SimpleNamespace
    renderer = GraphRenderer()

    renderer._render_glass(glass, config, tmp_path / "detail.png")
    renderer._render_combined(
        SimpleNamespace(glass_results=[glass], overall_state=ResultState.REVIEW_REQUIRED),
        None,
        tmp_path / "combined.png",
    )

    empty = [(span["xmin"], span["xmax"]) for span in spans if span["label"] == "EMPTY 판정"]
    assert empty == [(24.25, 24.75), (24.25, 24.75)]
    assert all(span["xmax"] > span["xmin"] for span in spans)


def _glass_with_states(config, timed_states) -> GlassAnalysisResult:
    return GlassAnalysisResult(
        glass_id=config.id,
        glass_name=config.name,
        result_state=ResultState.REVIEW_REQUIRED,
        samples=[
            TrackingSample(run_id="run", glass_id=config.id, frame_index=index,
                           timestamp_sec=timestamp, fill_state=state)
            for index, (timestamp, state) in enumerate(timed_states)
        ],
    )


def _record_spans(monkeypatch) -> list[dict]:
    spans: list[dict] = []
    original = Axes.axvspan

    def recording_span(self, xmin, xmax, *args, **kwargs):
        patch = original(self, xmin, xmax, *args, **kwargs)
        spans.append({
            "axes": self,
            "xmin": xmin,
            "xmax": xmax,
            "label": kwargs.get("label"),
            "face_alpha": round(patch.get_facecolor()[3], 6),
            "hatch": patch.get_hatch(),
            "ymin": kwargs.get("ymin", 0.0),
        })
        return patch

    monkeypatch.setattr(Axes, "axvspan", recording_span)
    return spans


def _reconstructed_then_top_exit_full(config) -> GlassAnalysisResult:
    full = [TrackingSample(run_id="run", glass_id=config.id, frame_index=40 + i, timestamp_sec=4.0 + i,
                           fill_state=FillState.FULL_NO_INTERFACE, is_valid=True,
                           flags=["OIL_TOP_EXIT_FULL"]) for i in range(3)]
    return GlassAnalysisResult(
        glass_id=config.id,
        glass_name=config.name,
        result_state=ResultState.PASS,
        samples=[
            _sample(config.id, 0.0, None, None),
            _sample(config.id, 1.0, None, None),
            _sample(config.id, 2.0, 10.0, None),
            _sample(config.id, 3.0, 12.0, None),
            *full,
        ],
        retrospective=RetrospectiveInterpretation(
            glass_id=config.id,
            status=RetrospectiveStatus.ACCEPTED,
            confirmed_prior=InitialObservationState.FULL_NO_INTERFACE,
            interpreted_state=FillState.FULL_NO_INTERFACE,
            start_time_sec=0.0,
            end_time_sec=1.0,
            provenance="initial_state_retrospective_v2",
        ),
    )
