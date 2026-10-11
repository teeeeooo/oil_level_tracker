from collections import deque

import numpy as np
import pytest

from tests.diagnostics.s11_side_texture_probe import measure_extremal_regions


def scene(kind='stationary'):
    y, x = np.indices((97, 97))
    cells = ((y % 5 == 2) | (y % 5 == 3)) & (x % 4 < 2)
    boundary = 48+(x-48)//4 if kind == 'inclined' else 48
    use = cells & (y >= boundary)
    if kind == 'internal_cells':
        use = cells
    gray = np.where(use, 41 if kind == 'weak_contrast' else 240, 40).astype(np.uint8)
    if kind == 'structural_step':
        gray = np.where(y >= 48, 240, 40).astype(np.uint8)
    elif kind == 'uniform':
        gray[:] = 40
    elif kind == 'polarity':
        gray = 255-gray
    elif kind in ('optical_warp', 'warped_printed_copy'):
        gray = np.stack([np.roll(row, round(3*np.sin(i/7))) for i, row in enumerate(gray)])
    edges = np.zeros(gray.shape, bool)
    edges[48, :] = True
    visible = np.ones(gray.shape, bool)
    if kind == 'missing_upper':
        visible[:47] = False
    elif kind == 'partial':
        visible[52, 48] = False
    return gray, edges, visible


def flood_spectrum(patch):
    """Slow independent pixel flood: no OpenCV or distinct-level shortcut."""
    height, width = patch.shape
    spectrum = []
    for cut in range(1, 256):
        area = 0
        for bright in (False, True):
            remaining = {(y, x) for y in range(height) for x in range(width)
                         if bool(patch[y, x] >= cut) == bright}
            while remaining:
                seed = remaining.pop()
                queue, component = deque([seed]), [seed]
                while queue:
                    y, x = queue.popleft()
                    for neighbor in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
                        if neighbor in remaining:
                            remaining.remove(neighbor)
                            component.append(neighbor)
                            queue.append(neighbor)
                ys, xs = zip(*component, strict=True)
                if (len(component) >= 4 and len(set(ys)) >= 2 and len(set(xs)) >= 2
                        and min(ys) > 0 and max(ys) < height-1
                        and min(xs) > 0 and max(xs) < width-1):
                    area += len(component)
        spectrum.append(area)
    return spectrum


@pytest.mark.parametrize(('kind', 'integrated', 'ablated'), [
    ('stationary', 'upper_like', 'upper_like'),
    ('inclined', 'upper_like', 'upper_like'),
    ('polarity', 'upper_like', 'upper_like'),
    ('printed_copy', 'upper_like', 'upper_like'),
    ('weak_contrast', 'low_support', 'upper_like'),
    ('internal_cells', 'internal_like', 'internal_like'),
    ('structural_step', 'low_support', 'low_support'),
    ('uniform', 'low_support', 'low_support'),
    ('missing_upper', 'UNAVAILABLE', 'UNAVAILABLE'),
    ('partial', 'UNAVAILABLE', 'UNAVAILABLE'),
])
def test_predeclared_measured_reachability(kind, integrated, ablated):
    result = measure_extremal_regions(*scene(kind), column=48)
    row = result['rows'][0]
    assert (row['integrated'], row['ablated']) == (integrated, ablated)
    assert result['physical_decision'] == 'UNRESOLVED'
    assert result['selected_scalar'] is None and not row['scalar_eligible']


def test_independent_flood_arithmetic():
    gray, edges, visible = scene()
    rng = np.random.default_rng(806)
    gray[:] = rng.integers(0, 6, gray.shape, dtype=np.uint8)*50
    result = measure_extremal_regions(gray, edges, visible, column=48)
    for side in ('upper', 'lower'):
        actual = result['rows'][0][side]
        x0, y0, x1, y1 = actual['bounds_xyxy']
        spectrum = flood_spectrum(gray[y0:y1, x0:x1])
        expanded = [area for a, b, area in actual['threshold_area_runs'] for _ in range(a, b)]
        assert expanded == spectrum
        assert actual['integrated_area'] == sum(spectrum)
        assert actual['peak_area'] == max(spectrum)
        assert 0 <= actual['integrated'] <= actual['ablated'] <= 1


def test_copy_warp_polarity_and_input_immutability():
    gray, edges, visible = scene()
    original = gray.copy(), edges.copy(), visible.copy()
    first = measure_extremal_regions(gray, edges, visible, column=48)
    inverted = measure_extremal_regions(255-gray, edges, visible, column=48)
    for side in ('upper', 'lower'):
        a, b = first['rows'][0][side], inverted['rows'][0][side]
        assert a['integrated_area'] == b['integrated_area']
        assert a['peak_area'] == b['peak_area']
        # Polarity reverses the threshold axis, not its integral or decisions.
        sa = [area for lo, hi, area in a['threshold_area_runs'] for _ in range(lo, hi)]
        sb = [area for lo, hi, area in b['threshold_area_runs'] for _ in range(lo, hi)]
        assert sa == sb[::-1]
    assert first == measure_extremal_regions(*scene('printed_copy'), column=48)
    assert measure_extremal_regions(*scene('optical_warp'), column=48) == measure_extremal_regions(
        *scene('warped_printed_copy'), column=48)
    assert all(np.array_equal(a, b) for a, b in zip(original, (gray, edges, visible), strict=True))


def test_hidden_data_and_all_edge_conservation():
    gray, edges, visible = scene('partial')
    edges[1, 48] = edges[94, 48] = True
    first = measure_extremal_regions(gray, edges, visible, column=48)
    gray[~visible] = 255-gray[~visible]
    edges[~visible] = ~edges[~visible]
    assert first == measure_extremal_regions(gray, edges, visible, column=48)
    assert [r['row'] for r in first['rows']] == [1, 48, 94]
    assert all(r['integrated'] == 'UNAVAILABLE' for r in first['rows'])
    edges[:] = False
    assert measure_extremal_regions(gray, edges, visible, column=48)['rows'] == []


@pytest.mark.parametrize('failure', ['dtype', 'shape', 'column', 'dimension', 'queries'])
def test_invalid_and_resource_inputs(failure):
    gray, edges, visible = scene()
    column = 48
    if failure == 'dtype':
        gray = gray.astype(float)
    elif failure == 'shape':
        visible = visible[:-1]
    elif failure == 'column':
        column = True
    elif failure == 'dimension':
        gray = np.zeros((4097, 1), np.uint8)
        edges = visible = np.ones(gray.shape, bool)
        column = 0
    elif failure == 'queries':
        gray = np.zeros((257, 97), np.uint8)
        edges = visible = np.ones(gray.shape, bool)
    with pytest.raises(ValueError):
        measure_extremal_regions(gray, edges, visible, column=column)
