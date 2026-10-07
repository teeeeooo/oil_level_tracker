from copy import deepcopy
import json
from types import SimpleNamespace as NS

import cv2
import numpy as np
import pytest

from oil_tracker.adapters.reporting.source_context_renderer import (
    MAX_CONTEXT_COLUMNS, MAX_CONTEXT_HEIGHT, SourceContextRenderer,
    context_times, source_column,
)
from oil_tracker.application.ports.progress import AnalysisCancelled


def geometry(size=40):
    return NS(ellipse=NS(center_x=size/2, center_y=size/2,
                         radius_x=size/2-2, radius_y=size/2-2), zero_line_y=size/2)


def inputs():
    config = NS(id="glass", geometry=geometry())
    recipe = NS(glasses=[config])
    result = NS(glass_results=[NS(glass_id="glass")])
    session = NS(input_video_path="source", analysis_start_sec=0,
                 sampling_fps=2, effective_end_sec=lambda: 2)
    return result, recipe, session


class Reader:
    metadata = NS(fps=10, duration_sec=10)
    def __init__(self, path):
        self.closed = False
        self.calls = []

    def read_at(self, time):
        self.calls.append(time)
        frame = np.zeros((40, 40, 3), np.uint8)
        frame[:int(18 + time*2)] = 200
        return frame, int(round(time*10)), time

    def close(self):
        self.closed = True


@pytest.mark.parametrize("edge", [12, 18, 25])
@pytest.mark.parametrize("inverted", [False, True])
def test_column_preserves_band_position_polarity_and_input(edge, inverted):
    frame = np.zeros((40, 40, 3), np.uint8)
    frame[:edge] = 255
    if inverted:
        frame = 255-frame
    before = frame.copy()
    column, meta = source_column(frame, geometry())
    assert meta["y_range"] == [2, 38]
    assert meta["x_range"] == [12, 28]
    assert column[edge-3, 0] == float(not inverted)
    assert column[edge-2, 0] == float(inverted)
    assert np.array_equal(frame, before)
    assert column.shape == (36, 4)


def test_rgb_channel_order_and_height_bound():
    frame = np.zeros((1000, 1000, 3), np.uint8)
    frame[:, :, 2] = 255
    column, meta = source_column(frame, geometry(1000))
    assert column.shape == (MAX_CONTEXT_HEIGHT, 4)
    assert np.all(column[column[:, 3] > 0, 0] == 1)
    assert np.all(column[:, 2] == 0)
    assert meta["height_bin_edges_source_y"][0] == 2
    assert meta["height_bin_edges_source_y"][-1] == 998


@pytest.mark.parametrize("args", [(0, 10, 2), (30, 105, 2), (0, 10000, 30), (2, 2, 1)])
def test_time_grid_is_bounded_and_not_faster_than_requested(args):
    times = context_times(*args)
    assert 1 <= len(times) <= MAX_CONTEXT_COLUMNS
    assert times[0] == args[0]
    if len(times) > 1:
        assert times[-1] == args[1]
        assert np.all(np.diff(times) >= 1/args[2] - 1e-12)


@pytest.mark.parametrize("args", [(-1, 2, 1), (2, 1, 1), (0, 1, 0), (0, np.inf, 1)])
def test_invalid_time_grid_rejected(args):
    with pytest.raises(ValueError):
        context_times(*args)


def test_real_png_and_provenance_without_result_mutation(tmp_path):
    result, recipe, session = inputs()
    before = deepcopy((result, recipe))
    reader = Reader("source")
    paths = SourceContextRenderer(lambda path: reader).render(result, recipe, session, tmp_path)
    info = paths["glass"]
    assert info["status"] == "AVAILABLE"
    assert info["available_count"] == info["column_count"] == 5
    assert (tmp_path / "source_context_01.png").read_bytes().startswith(b"\x89PNG")
    meta = json.loads((tmp_path / "source_context_01.json").read_text(encoding="utf-8"))
    assert [c["frame_index"] for c in meta["columns"]] == [0, 5, 10, 15, 20]
    assert not meta["numeric_measurement"]
    assert "oil" not in meta and "foam" not in meta
    assert reader.closed and (result, recipe) == before


@pytest.mark.parametrize("failure", ["decode", "timestamp", "duplicate"])
def test_missing_source_column_is_blank_not_carried(failure):
    reader = Reader("source")
    original = reader.read_at
    def read(time):
        frame, index, actual = original(time)
        if time == 1:
            if failure == "decode":
                raise EOFError("test gap")
            return frame, 5 if failure == "duplicate" else index, 8 if failure == "timestamp" else actual
        return frame, index, actual
    reader.read_at = read
    result, recipe, session = inputs()
    payload = SourceContextRenderer()._collect(reader, recipe.glasses[0], session)
    assert payload["status"] == "PARTIAL"
    assert payload["columns"][2]["status"] == "UNAVAILABLE"
    assert np.all(payload["raster"][:, 2, 3] == 0)
    assert np.any(payload["raster"][:, 1, 3] == 1)
    assert np.any(payload["raster"][:, 3, 3] == 1)


@pytest.mark.parametrize("error_type", [ValueError, OSError, cv2.error])
def test_unavailable_video_is_disclosed_and_nonfatal(tmp_path, error_type):
    def missing(path):
        raise error_type("unavailable source")
    paths = SourceContextRenderer(missing).render(*inputs(), tmp_path)
    assert paths["glass"]["status"] == "UNAVAILABLE"
    assert not paths["glass"]["image_path"]
    assert (tmp_path / "source_context_01.json").is_file()


def test_mid_collection_cancel_closes_source_reader(tmp_path):
    token = NS(cancelled=False)
    reader = Reader("source")
    original = reader.read_at
    def read(time):
        token.cancelled = True
        return original(time)
    reader.read_at = read
    with pytest.raises(AnalysisCancelled):
        SourceContextRenderer(lambda path: reader).render(*inputs(), tmp_path, cancellation=token)
    assert reader.closed


@pytest.mark.parametrize("fps", [0, -1, float("nan"), float("inf")])
def test_unknown_native_cadence_is_not_claimed_available(fps):
    reader = Reader("source")
    reader.metadata = NS(fps=fps, duration_sec=10)
    result, recipe, session = inputs()
    payload = SourceContextRenderer()._collect(reader, recipe.glasses[0], session)
    assert payload["status"] == "UNAVAILABLE"
    assert not reader.calls


def test_static_optical_line_is_preserved_not_classified():
    frame = np.full((40, 40, 3), 30, np.uint8)
    frame[15:18] = 220
    column, meta = source_column(frame, geometry())
    assert column[13, 0] == pytest.approx(220/255)
    assert column[12, 0] == pytest.approx(30/255)
    assert "oil_y" not in meta and "foam_y" not in meta


def test_capped_long_grid_has_explicit_coarse_sampling():
    times = context_times(0, 3600, 2)
    assert len(times) == MAX_CONTEXT_COLUMNS
    assert np.min(np.diff(times)) > 10
