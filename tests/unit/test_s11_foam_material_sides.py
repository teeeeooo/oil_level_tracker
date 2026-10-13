"""No ML import: qualify side semantics, unavailable data and native geometry."""
import numpy as np
import pytest

from tests.diagnostics import s11_foam_material_sides as sides


def test_distinct_foam_appearances_cannot_be_collapsed_into_absence():
    fine, coarse = np.array([1., 0.]), np.array([0., 1.])
    for u, l in [(fine, fine), (coarse, coarse), (fine, coarse), (coarse, fine)]:
        by_ref = {k: sides.affinities(u, l, p) for k, p in [('R', fine), ('L', coarse)]}
        assert all(r['status'] == 'MEASURED' for r in by_ref.values())
        assert all('class' not in r and 'foam_absent' not in r for r in by_ref.values())
        if not np.array_equal(u, l):
            assert by_ref['R']['ordered_contrast'] == -by_ref['L']['ordered_contrast']
            assert abs(by_ref['R']['ordered_contrast']) == 1
    # Low affinity to both stays only an affinity, even for another Foam appearance.
    assert sides.affinities(-fine-coarse, -fine-coarse, fine)['lower_affinity'] < 0


def test_side_exchange_reverses_ordered_term_and_keeps_unordered_control():
    u, l, p = np.array([1., 2.]), np.array([-3., 1.]), np.array([2., 7.])
    normal, swap = sides.affinities(u, l, p), sides.affinities(l, u, p)
    assert normal['ordered_contrast'] == -swap['ordered_contrast']
    assert normal['unordered_control'] == swap['unordered_control']
    assert normal['upper_affinity'] == swap['lower_affinity']


@pytest.mark.parametrize('bad', [None, np.zeros(2), np.array([np.nan, 1]), np.array([np.inf, 2])])
def test_unavailable_reference_or_side_is_never_a_negative(bad):
    good = np.ones(2)
    assert sides.affinities(good, good, bad)['status'].startswith('UNAVAILABLE')
    assert sides.affinities(good, bad, good)['status'].startswith('UNAVAILABLE')
    assert 'ordered_contrast' not in sides.affinities(good, bad, good)


def test_one_masked_required_pixel_or_crop_loss_cannot_silently_change_footprint():
    mask = np.ones((104, 104), dtype=bool)
    assert sides.side_support(mask, (52, 52))['status'] == 'AVAILABLE'
    mask[40, 40] = False
    r = sides.side_support(mask, (52, 52))
    assert r['status'] == 'UNAVAILABLE_REQUIRED_SUPPORT'
    assert r['visible_pixels'] == {'upper': 274, 'lower': 275}
    assert sides.side_support(mask, (5, 52))['status'] == 'UNAVAILABLE_REQUIRED_SUPPORT'


def test_side_sampling_retains_actual_extent_and_token_overlap():
    tokens = np.arange(256*4, dtype=float).reshape(256, 4)+1
    xy = (415, 247)
    upper, lower = sides.vectors(tokens, xy, 830)
    wu, wl = sides.geometry.strips(xy, list(range(-12, 13)), 830)
    assert np.allclose(upper, (wu@tokens)/np.linalg.norm(wu@tokens))
    assert np.allclose(lower, (wl@tokens)/np.linalg.norm(wl@tokens))
    assert np.minimum(wu, wl).sum() > 0  # not independent spatial measurements
    assert not np.array_equal(wu, wl)


def test_load_case_rejects_changed_native_edge_inventory(tmp_path):
    from PIL import Image
    images = {'canny': np.zeros((30, 30), np.uint8),
              'effective_mask': np.full((30, 30), 255, np.uint8),
              'glare_mask': np.zeros((30, 30), np.uint8)}
    images['canny'][15, 15] = 255
    paths = {}
    for key, value in images.items():
        name = f'{key}.png'; Image.fromarray(value).save(tmp_path/name); paths[key] = name
    case = {'id': 'fixture', 'kind': 'default_images', 'images': paths,
            'rgb': None, 'shape': [30, 30], 'column': 15, 'rows': [15]}
    rgb, visible, rows = sides.load_case(tmp_path, case)
    assert rgb is None and visible.all() and rows == [15]
    case['rows'] = [14]
    with pytest.raises(AssertionError, match='changed edge roster'):
        sides.load_case(tmp_path, case)
