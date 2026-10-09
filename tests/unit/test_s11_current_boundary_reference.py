"""Current geometry and exact side measurements, without physical authority."""
import numpy as np
import pytest

from tests.diagnostics import s11_boundary_temporal_probe as probe
from tests.diagnostics.s11_contour_contact_probe import measure_edge_fragments


def scene(height=17, width=21, row=8):
    image = np.full((height, width, 3), (20, 40, 60), np.uint8)
    image[row+1:] = (160, 180, 200)
    visible = np.ones((height, width), bool)
    edges = np.zeros_like(visible)
    edges[row, 4:17] = True
    points = np.array([[x, row] for x in (5, 8, 10, 12, 15)], np.int64)
    return image, visible, edges, points


def compare(anchor, current, av, cv, points, edges, *, origin=(0, 0), center_x=10, **kwargs):
    geometry = measure_edge_fragments(edges, cv, origin=origin)
    return probe.compare_current_boundary_reference(
        anchor, current, av, cv, points, geometry, origin=origin, center_x=center_x, **kwargs)


def test_current_observed_geometry_moves_without_transporting_initial_points():
    a, v, _, p = scene(row=6)
    b, _, e, _ = scene(row=10)
    r = compare(a, b, v, v, p, e)
    assert r['provisional_y'] == 10
    assert r['physical_decision'] == 'NOT_EVALUATED' and r['selected_front'] is None
    row, = r['candidates']
    assert row['center_crossings'] == [10]
    assert row['losses']['AB'] == 0 and row['denominator'] == 30
    assert all(s['current_xy'][1] == 10 and s['reference_xy'][1] == 6 for s in row['samples'])
    assert row['structure_status'] == 'NOT_MEASURED'


def test_exact_losses_equal_separate_direct_integer_oracle():
    a, v, e, p = scene()
    b = a.copy()
    b[6, 5:16] += np.array((7, 2, 1), np.uint8)
    b[10, 5:16] -= np.array((3, 5, 9), np.uint8)
    r = compare(a, b, v, v, p, e)
    for row in r['candidates']:
        expected = {k: 0 for k in ('AB', 'BA', 'AA', 'BB')}
        for s in row['samples']:
            x, y = s['current_xy']; rx, ry = s['reference_xy']
            for key, (u, d) in {'AB': (-2, 2), 'BA': (2, -2), 'AA': (-2, -2), 'BB': (2, 2)}.items():
                expected[key] += sum(abs(int(b[y+dy, x, c])-int(a[ry+refdy, rx, c]))
                                     for dy, refdy in ((-2, u), (2, d)) for c in range(3))
        assert row['losses'] == expected


def test_stationary_inclined_boundary_and_source_coordinate_translation():
    a, v, e, p = scene()
    e[:] = False
    for x in range(4, 17):
        y = 5 + x//4
        a[:y+1, x] = (20, 40, 60); a[y+1:, x] = (160, 180, 200); e[y, x] = True
    p[:, 1] = 5+p[:, 0]//4
    r = compare(a, a, v, v, p, e)
    shifted = compare(a, a, v, v, p+[100, 200], e, origin=(100, 200), center_x=110)
    assert r['provisional_y'] == 7 and shifted['provisional_y'] == 207
    assert [c['losses'] for c in r['candidates']] == [c['losses'] for c in shifted['candidates']]


def test_center_missing_does_not_use_side_height_or_fill_gap():
    a, v, e, p = scene(); e[:, 10] = False
    r = compare(a, a, v, v, p, e)
    assert r['provisional_y'] is None
    assert all(not c['center_crossings'] for c in r['candidates'])


def test_masked_support_is_recorded_and_poisoned_pixels_have_no_vote():
    a, v, e, p = scene(); cv = v.copy(); cv[6, 5] = False
    b = a.copy(); b[~cv] = 255
    r = compare(a, a, v, cv, p, e); s = compare(a, b, v, cv, p, e)
    assert r == s
    assert r['candidates'][0]['missing'] == [{'source_x': 5, 'reason': 'current_side_unavailable'}]
    assert r['candidates'][0]['denominator'] == 24


def test_absent_masked_and_ambiguous_references_are_unavailable():
    a, v, e, p = scene()
    assert compare(a, a, v, v, p[:0], e)['reason'] == 'no_reference'
    assert compare(a, a, ~v, v, p, e)['reason'] == 'no_visible_reference_pairs'
    assert compare(a, a, v, v, np.vstack([p, [5, 9]]), e)['reason'] == 'ambiguous_reference_column'


def test_exact_duplicate_reference_points_do_not_reweight():
    a, v, e, p = scene()
    assert compare(a, a, v, v, p, e) == compare(a, a, v, v, np.vstack([p[::-1], p]), e)


def test_identical_reference_sides_are_unresolved_not_a_positive():
    a, v, e, p = scene(); a[:] = 80
    r = compare(a, a, v, v, p, e)
    assert r['provisional_y'] is None
    assert r['candidates'][0]['losses'] == dict(AB=0, BA=0, AA=0, BB=0)


def test_reversed_and_same_side_current_pixels_do_not_win():
    a, v, e, p = scene()
    for b in (255-a, np.full_like(a, (20, 40, 60))):
        assert compare(a, b, v, v, p, e)['provisional_y'] is None


def test_measured_structure_opposition_and_missing_opposition_stay_distinct():
    a, v, e, p = scene()
    opposed = compare(a, a, v, v, p, e, structure_reference=(a, v, p))
    assert opposed['provisional_y'] is None
    assert opposed['candidates'][0]['appearance'] == 'CONTRADICTED'
    partial = compare(a, a, v, v, p, e, structure_reference=(a, v, p[:1]))
    assert partial['candidates'][0]['structure_loss'] is None
    assert partial['candidates'][0]['structure_reason'] == 'incomplete_common_support'
    assert partial['physical_decision'] == 'NOT_EVALUATED'


def test_two_current_appearance_matches_remain_ambiguous():
    a, v, e, p = scene(row=4); b = a.copy(); e[12, 4:17] = True
    b[10, 4:17] = (20, 40, 60); b[14, 4:17] = (160, 180, 200)
    r = compare(a, b, v, v, p, e)
    assert r['reason'] == 'ambiguous_provisional_center' and r['provisional_y'] is None


def test_copied_distractor_is_only_appearance_even_when_unique():
    a, v, _, p = scene(row=4); b, _, e, _ = scene(row=12)
    r = compare(a, b, v, v, p, e)
    assert r['provisional_y'] == 12
    assert r['selected_front'] is None and r['physical_decision'] == 'NOT_EVALUATED'


def test_true_edge_structure_crossing_keeps_all_junction_alternatives():
    a, v, e, p = scene(); e[3:14, 10] = True
    g = measure_edge_fragments(e, v)
    r = compare(a, a, v, v, p, e)
    assert len(r['candidates']) == len(g['fragments'])
    assert r['selected_front'] is None


def test_separate_role_calls_cannot_suppress_each_other():
    a, v, e, p = scene()
    oil = compare(a, a, v, v, p, e)
    foam = compare(a, a, ~v, v, p, e)
    assert foam['status'] == 'UNAVAILABLE'
    assert oil == compare(a, a, v, v, p, e)


@pytest.mark.parametrize('key,value', [('max_fragments', 0), ('max_vertices', 0),
                                      ('max_pair_budget', 1), ('max_fragment_indices', 1)])
def test_resource_exhaustion_never_returns_a_prefix_subset(monkeypatch, key, value):
    a, v, e, p = scene(); monkeypatch.setitem(probe.CURRENT_BOUNDARY_SPEC, key, value)
    r = compare(a, a, v, v, p, e)
    assert r['status'] == 'UNAVAILABLE' and r['reason'].endswith('budget_exceeded')
    assert r['candidates'] == [] and r['provisional_y'] is None


def test_incorrect_geometry_binding_and_unobserved_vertices_reject():
    a, v, e, p = scene(); g = measure_edge_fragments(e, v); g['origin'] = [1, 0]
    with pytest.raises(ValueError, match='binding'):
        probe.compare_current_boundary_reference(a, a, v, v, p, g, center_x=10)
    g = measure_edge_fragments(e, v); hidden = v.copy(); hidden[8, 5] = False
    with pytest.raises(ValueError, match='unobserved'):
        probe.compare_current_boundary_reference(a, a, v, hidden, p, g, center_x=10)


def test_non_integer_points_and_out_of_crop_center_reject():
    a, v, e, p = scene()
    with pytest.raises(ValueError): compare(a, a, v, v, p.astype(float), e)
    with pytest.raises(ValueError): compare(a, a, v, v, p, e, center_x=50)
