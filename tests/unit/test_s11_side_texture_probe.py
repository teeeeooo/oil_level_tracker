from copy import deepcopy

import numpy as np
import pytest

from tests.diagnostics.s11_side_texture_probe import (
    SPEC, decide_candidate, js_distance, measure_sector, texture_maps,
)


def measure(frame, y=48, mask=None):
    valid = np.ones(frame.shape[:2], dtype=bool) if mask is None else mask
    maps, valid = texture_maps(frame, valid)
    return measure_sector(maps, valid, x_range=(16, 80), current_y=y)


def scene(kind):
    gray = np.full((96, 96), 80, np.uint8)
    if kind == "step":
        gray[48:] = 180
    elif kind == "ribbon":
        gray[46:51] = 180
    elif kind == "textured":
        rng = np.random.default_rng(713)
        gray[:48] = rng.integers(60, 200, (48, 96), dtype=np.uint8)
    return np.repeat(gray[..., None], 3, axis=2)


@pytest.mark.parametrize("kind", ["flat", "step", "ribbon"])
def test_brightness_edge_without_persistent_texture_is_not_support(kind):
    result = measure(scene(kind))
    assert result["status"] == "AVAILABLE"
    assert result["margin"] <= 0


def test_texture_arrangement_changes_without_being_physical_identity():
    # The same pixels could be bubbly fluid or a stationary textured optical object.
    result = measure(scene("textured"))
    assert result["margin"] > 0
    assert SPEC["physical_identity_sufficient"] is False
    assert "Static textured" in SPEC["collision"]


def test_histograms_are_normalized_and_inputs_immutable():
    image = scene("textured"); before = image.copy()
    result = measure(image)
    assert np.array_equal(image, before)
    for histogram in result["histograms"].values():
        assert len(histogram) == 20 and sum(histogram) == pytest.approx(1)


def test_uniform_exposure_change_preserves_patterns():
    original = np.full((96, 96, 3), 40, np.uint8)
    original[48:] = 80
    a = measure(original); b = measure(original*2 + 10)
    assert a["histograms"] == b["histograms"]
    assert a["margin"] == b["margin"]


def test_missing_support_is_not_zero_or_clean():
    result = measure(scene("textured"), mask=np.zeros((96, 96), dtype=bool))
    assert result["status"] == "UNAVAILABLE" and "margin" not in result


def test_image_edge_insufficient_far_band_abstains():
    result = measure(scene("textured"), y=3)
    assert result["status"] == "UNAVAILABLE"


def test_candidate_majority_is_unique_sector_not_repeated_votes():
    positive = {"status": "AVAILABLE", "margin": .1}
    assert decide_candidate([{"sector": 1, "measurement": positive}]*10)[0] == "UNRESOLVED"
    assert decide_candidate([{"sector": i, "measurement": positive} for i in range(3)])[0] == "INTERFACE_SUPPORTED"


def test_js_distance_symmetric_bounded_and_zero_for_identity():
    a, b = np.array([1., 0.]), np.array([0., 1.])
    assert js_distance(a, a) == 0
    assert js_distance(a, b) == js_distance(b, a) == pytest.approx(np.sqrt(np.log(2)))


@pytest.mark.parametrize("x_range,y", [((-1, 10), 20), ((20, 10), 20), ((0, 97), 20), ((0, 30), float("nan"))])
def test_invalid_geometry_unavailable(x_range, y):
    maps, valid = texture_maps(scene("flat"), np.ones((96, 96), dtype=bool))
    assert measure_sector(maps, valid, x_range=x_range, current_y=y)["status"] == "UNAVAILABLE"
