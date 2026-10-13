"""Geometry controls for the fixed-bank transfer; no ML runtime is imported."""
from __future__ import annotations

import numpy as np
import pytest

from tests.diagnostics import s11_contextual_role_transfer as transfer


def test_rectangular_padding_preserves_pixels_mask_and_source_coordinate_roundtrip():
    rgb = np.arange(210 * 228 * 3, dtype=np.uint8).reshape(210, 228, 3)
    visible = np.ones((210, 228), dtype=bool)
    visible[100, 114] = False
    image, mask, (left, top) = transfer.padded(rgb, visible)
    assert image.shape == (228, 228, 3) and (left, top) == (0, 9)
    assert np.array_equal(image[9:219], rgb) and np.array_equal(mask[9:219], visible)
    assert not mask[:9].any() and not mask[219:].any()
    source, origin = (578, 428), (464, 254)
    padded_xy = (source[0] - origin[0] + left, source[1] - origin[1] + top)
    assert padded_xy == (114, 183)
    assert (padded_xy[0] + origin[0] - left, padded_xy[1] + origin[1] - top) == source
    assert np.array_equal(image[padded_xy[1], padded_xy[0]], rgb[174, 114])


@pytest.mark.parametrize('xy', [(52, 37), (18, 63), (52, 35)])
@pytest.mark.parametrize('columns', [list(range(-12, 13)), list(range(0, 8))])
def test_reference_geometry_is_bitwise_identical_to_frozen_cr1(xy, columns):
    old = transfer.legacy()
    for offsets in (range(-12, -1), range(2, 13)):
        assert np.array_equal(transfer.weights(xy, columns, offsets, 104), old.weights(xy, columns, offsets))
    assert transfer.weight_record(xy, columns, 104) == old.weight_record(xy, columns)


def test_common_support_matches_legacy_and_preserves_rectangular_boundaries():
    old = transfer.legacy()
    reference = np.ones((104, 104), dtype=bool)
    reference[25:50, 40:48] = False
    contexts = [(reference, (52, 37)), (np.ones((104, 104), dtype=bool), (18, 63))]
    assert transfer.common_columns(contexts) == old.common_columns(contexts)
    public = np.ones((228, 228), dtype=bool)
    assert transfer.common_columns([(public, (114, 183)), *contexts]) == old.common_columns(contexts)
    assert transfer.common_columns([(public, (114, 220)), *contexts]) == []
    public[171:196, 110:126] = False
    assert transfer.common_columns([(public, (114, 183)), *contexts]) == []


def test_native_sampling_uses_actual_square_extent_and_conserves_mass():
    weights = transfer.weights((113.5, 113.5), [0], [0], 228)
    expected = np.zeros(256)
    expected[[7 * 16 + 7, 7 * 16 + 8, 8 * 16 + 7, 8 * 16 + 8]] = 0.25
    assert np.array_equal(weights, expected)
    upper, lower = transfer.strips((114, 183), list(range(-12, 13)), 228)
    assert upper.sum() == pytest.approx(1) and lower.sum() == pytest.approx(1)
    assert np.all(upper >= 0) and np.all(lower >= 0)
    assert not np.array_equal(upper, lower)
    assert not np.array_equal(upper, transfer.weights((114, 183), list(range(-12, 13)), range(-12, -1), 104))
    assert transfer.weight_record((114, 183), [], 228) == {'status': 'UNAVAILABLE'}


def test_complete_floor_ceil_cover_does_not_create_point_truth():
    intervals = [{'id': 'A', 'role': 'Foam upper', 'source_y_cell_bounds': [322.5, 338.5]},
                 {'id': 'B', 'role': 'Oil upper', 'source_y_cell_bounds': [420.5, 435.5]}]
    anchors = transfer.interval_anchors(intervals, 578)
    assert len(anchors) == 35
    assert [a['source_xy'][1] for a in anchors if a['range_id'] == 'A'] == list(range(322, 340))
    assert [a['source_xy'][1] for a in anchors if a['range_id'] == 'B'] == list(range(420, 437))
    assert all(a['source_xy'][0] == 578 and a['anchor_label'] == 'UNREVIEWED_ANCHOR' for a in anchors)
    assert all('candidate_index' not in a for a in anchors)


@pytest.mark.parametrize('bounds', [[4, 4], [7, 3], [float('nan'), 5]])
def test_invalid_containment_is_not_a_scored_interval(bounds):
    with pytest.raises(AssertionError):
        transfer.interval_anchors([{'id': 'x', 'role': 'Oil upper', 'source_y_cell_bounds': bounds}], 10)
