"""Population exchange, independent CDF arithmetic and role ambiguity controls."""
import numpy as np
import pytest

from tests.diagnostics.s11_boundary_temporal_probe import (
    ROW_DISTRIBUTION_SPEC as SPEC,
    compare_row_distribution_roles as compare,
)


def population_fixture():
    visible = np.ones((25, 25), dtype=bool)
    references = {}
    for role, spread in (('interface', 80), ('structure', 0), ('texture', 40)):
        image = np.empty((25, 25, 3), dtype=np.uint8)
        population = np.array([100-spread]*12 + [100] + [100+spread]*12)
        for y in range(25):
            offset = 20 if y >= 12 else 0
            image[y] = (population[:, None] + offset + [0, 5, 10]).astype(np.uint8)
        references[role] = (image, visible.copy(), np.zeros_like(visible))
    query = references['interface'][0].copy()
    rng = np.random.default_rng(1210)
    for y in range(25):
        query[y] = query[y, rng.permutation(25)] + np.array([2, 3, 4], np.uint8)
    return query, visible, references


def test_positive_region_is_reachable_after_grain_exchange_and_exposure_offset():
    q, v, refs = population_fixture()
    result = compare(q, v, refs)
    full, ablation = (result['modes'][m] for m in ('distribution', 'row_mean'))
    assert full['appearance_preference'] == 'interface'
    assert full['roles']['interface']['cost'] == pytest.approx(0, abs=1e-14)
    assert full['roles']['texture']['cost'] == pytest.approx((24/25)*40/510)
    assert full['roles']['structure']['cost'] == pytest.approx((24/25)*80/510)
    assert ablation['appearance_preference'] is None
    assert all(r['cost'] == pytest.approx(0, abs=1e-14) for r in ablation['roles'].values())
    assert result['physical_identity'] == 'UNRESOLVED' and result['selected_front'] is None


def test_sorted_distance_matches_independent_empirical_cdf_integral():
    rng = np.random.default_rng(219)
    q = rng.integers(0, 256, (25, 25, 3), dtype=np.uint8)
    v = np.ones((25, 25), bool)
    v[:4, :3] = False  # unequal row lengths, still equal row weighting
    refs = {role: (rng.integers(0, 256, q.shape, dtype=np.uint8), v.copy(), ~v)
            for role in SPEC['roles']}
    r = compare(q, v, refs)
    for role in SPEC['roles']:
        per_row = []
        for y, xs in zip(r['row_indices'], r['common_columns_by_row'], strict=True):
            channels = []
            for c in range(3):
                a = q[y, xs, c].astype(float)-r['centering_bgr']['current'][c]
                b = refs[role][0][y, xs, c].astype(float)-r['centering_bgr'][role][c]
                nodes = np.unique(np.concatenate([a, b]))
                cdf_a = np.mean(a[:, None] <= nodes[None, :-1], axis=0)
                cdf_b = np.mean(b[:, None] <= nodes[None, :-1], axis=0)
                channels.append(float(np.sum(np.diff(nodes)*abs(cdf_a-cdf_b))/510))
            per_row.append(float(np.mean(channels)))
        assert per_row == pytest.approx(r['modes']['distribution']['roles'][role]['row_costs'], abs=1e-14)
        assert 0 <= r['modes']['distribution']['roles'][role]['cost'] <= 1


def test_common_mask_hides_values_without_changing_any_role_domain():
    q, v, refs = population_fixture()
    refs['texture'][1][:, :5] = False
    before = compare(q, v, refs)
    q[:, :5] = 255
    for image, _, _ in refs.values():
        image[:, :5] = 0
    assert compare(q, v, refs) == before
    assert all(xs == list(range(5, 25)) for xs in before['common_columns_by_row'])


@pytest.mark.parametrize('role', ['structure', 'texture'])
def test_copied_or_coherently_deformed_opponent_is_ambiguous(role):
    q, v, refs = population_fixture()
    # A common optical row warp can be identical for two physical hypotheses.
    refs[role] = refs['interface']
    r = compare(q, v, refs)
    assert r['modes']['distribution']['appearance_preference'] is None


def test_row_and_side_order_are_not_discarded():
    q, v, refs = population_fixture()
    original = compare(q, v, refs)
    reversed_sides = compare(q[::-1].copy(), v, refs)
    assert original['modes']['distribution']['roles']['interface']['cost'] == pytest.approx(0)
    assert reversed_sides['modes']['distribution']['roles']['interface']['cost'] > 0


def test_inputs_are_not_modified():
    q, v, refs = population_fixture()
    arrays = [q, v] + [a for ref in refs.values() for a in ref]
    copies = [a.copy() for a in arrays]
    compare(q, v, refs)
    assert all(np.array_equal(a, b) for a, b in zip(arrays, copies, strict=True))


@pytest.mark.parametrize('role', SPEC['roles'])
def test_missing_role_cannot_become_a_win(role):
    q, v, refs = population_fixture()
    refs[role] = None
    r = compare(q, v, refs)
    assert r['status'] == 'UNAVAILABLE' and r['reason'] == f'missing_{role}_reference'


def test_one_sparse_row_stops_measurement_without_dropping_it():
    q, v, refs = population_fixture()
    v[0, 7:] = False
    r = compare(q, v, refs)
    assert r['reason'] == 'insufficient_common_row_support'
    assert len(r['common_columns_by_row']) == 22


@pytest.mark.parametrize('bad', [np.zeros((26, 25, 3), np.uint8), np.zeros((25, 25, 3), float)])
def test_fixed_support_and_input_type_are_enforced(bad):
    _, v, refs = population_fixture()
    with pytest.raises(ValueError, match='25x25 uint8'):
        compare(bad, v, refs)
