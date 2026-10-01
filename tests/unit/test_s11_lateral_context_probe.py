"""Information retention and remaining collisions of ordered side columns."""
import copy
import json

import numpy as np
import pytest

from tests.diagnostics.s11_spatial_context_probe import measure_lateral_context
from tests.unit.test_oil_interface_witness import measure
from tests.unit.test_s11_spatial_context_probe import point


def lateral(gray, *, points=None, mask=None, glare=None, origin=(0, 0), width=9):
    return measure_lateral_context(
        gray, np.ones_like(gray) if mask is None else mask,
        np.zeros_like(gray) if glare is None else glare,
        [point()] if points is None else points, origin=origin, band_width=width)


def mirrored_sectors():
    image = np.full((200, 200), 128, np.uint8)
    for sector in range(5):
        for column in range(8, 32):
            image[90+column//2:, sector*40+column] = 0
    mirrored = np.hstack([image[:, s*40:(s+1)*40][:, ::-1] for s in range(5)])
    points = [point(s, x=(s*40, (s+1)*40)) for s in range(5)]
    return image, mirrored, points


@pytest.mark.parametrize('invert', [False, True])
def test_column_order_distinguishes_complete_o1_and_full_height_row_collision(invert):
    a, b, points = mirrored_sectors()
    if invert:
        a, b = 255-a, 255-b
    originals = (a.copy(), b.copy(), copy.deepcopy(points))
    # Actual full O1 witness equality, with all auxiliary channels held fixed.
    assert measure(a) == measure(b)
    left, right = [lateral(g, points=points) for g in (a, b)]
    assert left['row_context'] == right['row_context']
    for x, y in zip(left['points'], right['points'], strict=True):
        assert x['signed_delta'] != y['signed_delta']
        assert x['signed_delta'] == y['signed_delta'][::-1]
    assert left['decision'] == right['decision'] == 'NOT_EVALUATED'
    assert np.array_equal(a, originals[0]) and np.array_equal(b, originals[1])
    assert points == originals[2]
    json.dumps(left, allow_nan=False)


@pytest.mark.parametrize('occlusion', ['mask', 'glare'])
def test_hidden_horizontal_difference_stays_indistinguishable(occlusion):
    a, b, points = mirrored_sectors()
    mask, glare = np.ones_like(a), np.zeros_like(a)
    if occlusion == 'mask':
        mask[a != b] = 0
    else:
        glare[a != b] = 255
    left, right = [lateral(g, points=points, mask=mask, glare=glare) for g in (a, b)]
    assert left == right
    assert left['decision'] == 'NOT_EVALUATED'
    assert any(n < 9 for p in left['points'] for band in p['bands'].values()
               for n in band['visible_count'])


def test_nonzero_origin_fractional_center_and_basis_are_preserved():
    gray = np.arange(200, dtype=np.uint8)[:, None].repeat(30, axis=1)
    points = [point(2, x=(40, 70), y=160.5, basis='native_path'),
              point(3, x=(40, 70), y=165, basis='candidate_center')]
    result = lateral(gray, points=points, origin=(40, 60))
    a, b = result['points']
    assert a['source_y'] == 160.5 and a['sampling_center_local_y'] == 101
    assert a['geometry_basis'] == 'native_path' and b['geometry_basis'] == 'candidate_center'
    assert a['bands']['near_above']['local_y_range'] == [91, 100]
    assert a['bands']['near_above']['source_y_range'] == [151, 160]
    assert a['source_x_columns'] == list(range(40, 70))
    assert a['bands']['near_above']['gray_mean'] == [95.0]*30
    assert a['bands']['near_below']['gray_mean'] == [107.0]*30
    assert a['signed_delta'] == [12.0]*30
    reverse = lateral(gray, points=points[::-1], origin=(40, 60))
    assert reverse['points'] == result['points'][::-1]


def test_zero_sparse_and_missing_columns_do_not_become_sufficient_support():
    gray = np.zeros((200, 200), np.uint8)
    mask = np.ones_like(gray)
    mask[:, 0] = 0
    mask[98, 0] = 1  # only one observed black pixel in the above band
    glare = np.zeros_like(gray)
    glare[:, 1] = 255
    result = lateral(gray, mask=mask, glare=glare)['points'][0]
    above, below = result['bands'].values()
    assert above['visible_count'][:3] == [1, 0, 9]
    assert above['gray_mean'][:3] == [0.0, None, 0.0]
    assert above['column_state'][:3] == ['observed', 'glare_excluded', 'observed']
    assert below['column_state'][0] == 'outside_effective_mask'
    assert result['signed_delta'][:3] == [None, None, 0.0]
    assert 'available' not in above  # no O1 or classifier availability assertion


@pytest.mark.parametrize('center', [0, 3, 19.75])
def test_crop_edges_are_explicit_and_never_wrap(center):
    gray = np.zeros((20, 10), np.uint8)
    gray[-1] = 200
    result = lateral(gray, points=[point(x=(0, 10), y=center)])['points'][0]
    for band in result['bands'].values():
        start, stop = band['clipped_local_y_range']
        assert 0 <= start <= stop <= 20
        assert band['in_crop_pixels_per_column'] == stop-start
        if start == stop:
            assert band['gray_mean'] == [None]*10
            assert band['column_state'] == ['outside_crop']*10
        else:
            assert band['gray_mean'] == pytest.approx(gray[start:stop].mean(axis=0))
    assert not all(b['crop_complete'] for b in result['bands'].values())


def test_vertical_rearrangement_inside_side_bands_remains_a_lateral_collision():
    a = np.zeros((200, 200), np.uint8)
    a[90:94] = 180
    b = np.zeros_like(a)
    b[95:99] = 180
    left, right = lateral(a), lateral(b)
    assert left['points'] == right['points']  # averaging Y loses within-band order
    assert left['row_context'] != right['row_context']
    # Side means are not full 2-D pixels or connected-region segmentation.
    assert left['decision'] == right['decision'] == 'NOT_EVALUATED'


def test_identical_raster_can_have_no_machine_known_physical_identity():
    image, _, points = mirrored_sectors()
    image[160:] = 128  # return could be Oil plus reflection or another appearance
    result = lateral(image, points=points)
    assert result == lateral(image.copy(), points=copy.deepcopy(points))
    assert result['decision'] == 'NOT_EVALUATED'
    assert result['spec']['threshold'] is None


def test_row_and_column_marginals_together_still_lose_two_dimensional_arrangement():
    a = np.zeros((200, 200), np.uint8)
    a[90:94, :100] = 180
    a[94:98, 100:] = 180
    b = np.zeros_like(a)
    b[90:94, 100:] = 180
    b[94:98, :100] = 180
    assert not np.array_equal(a, b)
    # Both axis means/counts are identical despite different pixel arrangement.
    assert lateral(a) == lateral(b)


@pytest.mark.parametrize('width', [0, -1, True, 1.5, 129])
def test_invalid_band_width_is_rejected(width):
    with pytest.raises(ValueError):
        lateral(np.zeros((200, 200), np.uint8), width=width)


def test_column_inventory_bound_and_invalid_geometry_are_rejected():
    with pytest.raises(ValueError, match='columns exceed'):
        lateral(np.zeros((10, 2000), np.uint8),
                points=[point(i, x=(0, 2000), y=5) for i in range(33)])
    with pytest.raises(ValueError):
        lateral(np.zeros((20, 20), np.uint8), points=[point(x=(-1, 20), y=10)])


def test_empty_inventory_creates_no_lateral_candidates():
    result = lateral(np.zeros((10, 10), np.uint8), points=[])
    assert result['points'] == [] and result['row_context']['points'] == []
    assert result['decision'] == 'NOT_EVALUATED'
