import json

import numpy as np
import pytest

from tests.diagnostics.s11_boundary_temporal_probe import match_ordered_patch


def match(a, b, y=20, radius=4):
    return match_ordered_patch(a, b, x_range=(3, 17), anchor_y=y, radius=radius)


def test_rapid_translation_and_exposure_offset_preserve_ordered_pattern():
    rng = np.random.default_rng(7)
    a = rng.integers(20, 180, (100, 20, 3), dtype=np.uint8)
    b = rng.integers(20, 180, a.shape, dtype=np.uint8)
    b[71:80, 3:17] = a[16:25, 3:17]+12
    before = a.copy(), b.copy()
    forward = match(a, b)
    assert forward['best_y'] == [75]  # 55-pixel jump; no small-motion censoring.
    assert forward['best_loss'] < 1e-25
    assert match(b, a, y=75)['best_y'] == [20]
    assert forward['physical_identity'] == 'UNRESOLVED'
    assert forward['decision'] == 'NOT_EVALUATED'
    np.testing.assert_array_equal(a, before[0])
    np.testing.assert_array_equal(b, before[1])
    json.dumps(forward, allow_nan=False)


def test_duplicate_patterns_retain_both_alternatives():
    rng = np.random.default_rng(18)
    a = rng.integers(0, 200, (100, 20, 3), dtype=np.uint8)
    b = a.copy()
    b[66:75, 3:17] = a[16:25, 3:17]
    result = match(a, b)
    assert result['best_y'] == [20, 70]
    assert result['runner_up_margin'] == 0


def test_constant_appearance_is_ambiguous_not_stationary():
    a = np.full((100, 20, 3), 80, dtype=np.uint8)
    result = match(a, a)
    assert result['best_y'] == list(range(4, 96))
    assert result['physical_identity'] == 'UNRESOLVED'


def test_static_structure_can_match_perfectly_without_becoming_oil():
    a = np.zeros((100, 20, 3), dtype=np.uint8)
    a[18:21, :, :] = 200
    result = match(a, a)
    assert result['best_y'] == [20]
    assert result['best_loss'] == 0
    assert result['decision'] == 'NOT_EVALUATED'


def test_order_is_retained_even_when_band_averages_match():
    rng = np.random.default_rng(9)
    a = rng.integers(0, 255, (100, 20, 3), dtype=np.uint8)
    b = a.copy()
    b[16:25, 3:17] = a[16:25, 3:17][:, ::-1]
    result = match(a, b)
    assert result['losses'][result['centers'].index(20)] > 0


def test_cropped_patch_is_unavailable_not_clean():
    a = np.zeros((100, 20, 3), dtype=np.uint8)
    result = match(a, a, y=1)
    assert result['status'] == 'unavailable_patch'
    assert result['best_y'] == [] and result['best_loss'] is None


@pytest.mark.parametrize('fault', ['shape', 'dtype', 'noninteger', 'outside'])
def test_invalid_inputs_fail_closed(fault):
    a = np.zeros((100, 20, 3), dtype=np.uint8)
    b = a.copy()
    if fault == 'shape': b = b[:-1]
    if fault == 'dtype': b = b.astype(float)
    with pytest.raises(ValueError):
        match(a, b, y=20.5 if fault == 'noninteger' else 100 if fault == 'outside' else 20)
