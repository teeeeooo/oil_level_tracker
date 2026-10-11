import numpy as np
import pytest

from tests.diagnostics.s11_side_texture_probe import measure_spatial_conjunction


def scene():
    y, x = np.indices((97, 97))
    cells = np.clip(220-12*((x % 8-4)**2+(y % 8-4)**2), 20, 220)
    gray = np.where(y >= 48, cells, 40).astype(np.uint8)
    edge = np.zeros(gray.shape, bool)
    edge[48, :] = True
    return gray, edge, np.ones(gray.shape, bool)


def test_direct_pixel_oracle_and_common_ablation_support():
    gray, edges, visible = scene()
    # Exercise visibility holes and an irregular, signed field independently.
    rng = np.random.default_rng(17)
    gray[:] = rng.integers(0, 256, gray.shape, dtype=np.uint8)
    visible[39, 46] = False
    output = measure_spatial_conjunction(gray, edges, visible, column=48)['rows'][0]
    for side in ['upper', 'lower']:
        actual = output[side]
        x0, y0, x1, y1 = actual['bounds_xyxy']
        sums = [0, 0, 0]
        centers = 0
        for y in range(y0, y1):
            for x in range(x0, x1):
                positions = [(y, x+3), (y, x+1), (y, x-3), (y, x-1),
                             (y+3, x), (y+1, x), (y-3, x), (y-1, x)]
                if not all(visible[p] for p in positions):
                    continue
                values = [int(gray[positions[i]])-int(gray[positions[i+1]]) for i in range(0, 8, 2)]
                e, w, s, n = values
                r = max(0, min(values), -max(values))
                a = max(0, min(e, w), -max(e, w))
                b = max(0, min(s, n), -max(s, n))
                sums = [sums[0]+r, sums[1]+max(a, b), sums[2]+a+b]
                centers += 1
        assert centers == actual['available_centers']
        assert sums == [actual['joint_sum'], actual['axis_sum'], actual['ablated_sum_twice']]
        assert actual['joint_ratio'] <= actual['ablated_ratio'] <= 1
    for variant in ['joint', 'ablated']:
        u, d = (output[s][f'{variant}_ratio'] for s in ['upper', 'lower'])
        assert output[variant]['costs'] == dict(upper_cellular=(u*u+(1-d)**2)/2,
            internal_cellular=((1-u)**2+(1-d)**2)/2, noncellular=(u*u+d*d)/2)


def test_polarity_copy_and_stationary_identity_collision():
    gray, edges, visible = scene()
    first = measure_spatial_conjunction(gray, edges, visible, column=48)
    assert first == measure_spatial_conjunction(255-gray, edges, visible, column=48)
    # A physical layer and a printed copy with identical pixels are identical
    # inputs. Never permit the evaluator's semantic role to enter inference.
    assert first == measure_spatial_conjunction(gray.copy(), edges.copy(), visible.copy(), column=48)
    assert first['physical_decision'] == 'UNRESOLVED'
    assert first['selected_scalar'] is None
    assert not any(r['scalar_eligible'] for r in first['rows'])


def test_hidden_pixels_and_input_immutability():
    gray, edges, visible = scene()
    visible[50:56, 43:53] = False
    original = gray.copy()
    first = measure_spatial_conjunction(gray, edges, visible, column=48)
    assert np.array_equal(gray, original)
    gray[~visible] = 255-gray[~visible]
    edges[~visible] = ~edges[~visible]
    assert first == measure_spatial_conjunction(gray, edges, visible, column=48)


def test_missing_support_is_not_noncellular_opposition():
    gray, edges, visible = scene()
    visible[:47] = False
    row = measure_spatial_conjunction(gray, edges, visible, column=48)['rows'][0]
    assert row['joint']['preference'] == row['ablated']['preference'] == 'UNAVAILABLE'
    assert row['joint']['costs'] is None


def test_no_edge_no_synthetic_candidate_and_small_crop():
    gray, edges, visible = scene()
    edges[:] = False
    assert measure_spatial_conjunction(gray, edges, visible, column=48)['rows'] == []
    edges = np.ones((3, 2), bool)
    result = measure_spatial_conjunction(np.zeros((3, 2), np.uint8), edges, edges, column=0)
    assert len(result['rows']) == 3
    assert all(r['joint']['preference'] == 'UNAVAILABLE' for r in result['rows'])


@pytest.mark.parametrize('bad', [None, np.zeros((3, 3), float), np.zeros((4097, 1), np.uint8),
                                np.zeros((2049, 2049), np.uint8)])
def test_resource_and_type_rejection(bad):
    with pytest.raises(ValueError):
        measure_spatial_conjunction(bad, np.zeros((1, 1), bool), np.zeros((1, 1), bool), column=0)


@pytest.mark.parametrize('column', [-1, 97, 48.0, True])
def test_no_column_rounding_or_relocation(column):
    with pytest.raises(ValueError):
        measure_spatial_conjunction(*scene(), column=column)
