"""Ordered-gap observation is invariant to identity and never selects a front."""
import copy
import json

import numpy as np
import pytest

from tests.diagnostics.s11_foam_front_alternatives import measure


def gap_scene():
    gray = np.full((40, 15), 160, np.uint8)
    gray[14:18] = 40
    labels = np.zeros(gray.shape, np.uint16)
    labels[18:30, 3:12] = 2
    return gray, labels, np.ones(gray.shape, bool), np.zeros(gray.shape, bool)


def view(result, radius=8):
    return next(v for v in result['components'][0]['columns'][4]['views']
                if v['radius_px'] == radius)


def test_ordered_gap_keeps_both_plateaus_and_all_equal_trough_samples():
    arrays = gap_scene()
    original = [a.copy() for a in arrays]
    result = measure(*arrays, origin=(100, 200), include_gap_brackets=True)
    pairs = view(result)['gap_brackets']
    assert len(pairs) == 1
    assert pairs[0]['upper_edge_source_y_range'] == [213, 215]
    assert pairs[0]['lower_edge_source_y_range'] == [217, 219]
    assert pairs[0]['minimum_source_y_values'] == [214, 215, 216, 217]
    assert pairs[0]['raw_gray_above_minimum_below'] == [160, 40, 160]
    assert pairs[0]['physical_gap_identity'] == 'UNRESOLVED'
    assert pairs[0]['selected_foam_front'] is None
    assert result['components'][0]['foam_front'] is None
    for a, b in zip(arrays, original):
        np.testing.assert_array_equal(a, b)
    json.dumps(result, allow_nan=False)


def test_opt_in_is_additive_and_default_output_is_unchanged():
    arrays = gap_scene()
    before = measure(*arrays)
    result = copy.deepcopy(measure(*arrays, include_gap_brackets=True))
    result.pop('gap_bracket_schema')
    result.pop('gap_bracket_limits')
    for c in result['components']:
        for col in c['columns']:
            for v in col['views']:
                v.pop('gap_brackets')
    assert result == before == measure(*arrays, include_gap_brackets=False)


def test_bright_ribbon_and_single_step_are_not_dark_gap_pairs():
    gray, labels, effective, glare = gap_scene()
    gray[:] = 40
    gray[14:18] = 160
    assert view(measure(gray, labels, effective, glare, include_gap_brackets=True))['gap_brackets'] == []
    gray[:18] = 40
    gray[18:] = 160
    assert view(measure(gray, labels, effective, glare, include_gap_brackets=True))['gap_brackets'] == []


@pytest.mark.parametrize('mask', ['effective', 'glare'])
def test_gap_cannot_bridge_an_unavailable_stencil(mask):
    gray, labels, effective, glare = gap_scene()
    if mask == 'effective':
        effective[16, 7] = False
    else:
        glare[16, 7] = True
    v = view(measure(gray, labels, effective, glare, include_gap_brackets=True))
    assert v['appearance_state'] == 'censored'
    assert v['gap_brackets'] == []


def test_inspection_window_boundary_cannot_be_used_as_missing_upper_edge():
    result = measure(*gap_scene(), include_gap_brackets=True)
    assert view(result, 4)['gap_brackets'] == []
    assert len(view(result, 8)['gap_brackets']) == 1


def test_multiple_gaps_are_all_retained_without_amplitude_ranking():
    gray, labels, effective, glare = gap_scene()
    gray[:] = 160
    gray[12:14] = 100
    gray[17:19] = 40
    labels[:] = 0
    labels[17:30, 3:12] = 2
    pairs = view(measure(gray, labels, effective, glare, include_gap_brackets=True))['gap_brackets']
    assert len(pairs) == 2
    assert [p['raw_gray_above_minimum_below'][1] for p in pairs] == [100, 40]
    assert all(p['selected_foam_front'] is None for p in pairs)


def test_reflection_and_internal_texture_with_same_pixels_cannot_be_classified_as_air():
    arrays = gap_scene()
    result = measure(*arrays, include_gap_brackets=True)
    for _identity in ('air_above_foam', 'glass_pattern', 'internal_foam_texture'):
        assert measure(*(a.copy() for a in arrays), include_gap_brackets=True) == result
    assert view(result)['gap_brackets'][0]['physical_gap_identity'] == 'UNRESOLVED'


@pytest.mark.parametrize('width', [1, 2])
def test_narrow_trough_keeps_opposite_signs_even_when_absolute_peak_merges(width):
    gray, labels, effective, glare = gap_scene()
    gray[:] = 160
    gray[14:14+width] = 40
    v = view(measure(gray, labels, effective, glare, include_gap_brackets=True))
    assert len(v['gap_brackets']) == 1
    assert v['gap_brackets'][0]['minimum_source_y_values'] == list(range(14,14+width))
    if width == 2:
        assert len(v['peaks']) == 1  # Absolute slope alone merged opposite signs.


def test_non_boolean_option_is_rejected():
    with pytest.raises(ValueError, match='boolean'):
        measure(*gap_scene(), include_gap_brackets=1)
