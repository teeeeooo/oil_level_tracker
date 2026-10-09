"""Exact geometry, ambiguous topology and censoring; no material truth proxy."""
from collections import Counter

import numpy as np
import pytest

from tests.diagnostics.s11_contour_contact_probe import FRAGMENT_SPEC, measure_edge_fragments


def verify(edge, visible=None, origin=(0, 0)):
    visible = np.ones_like(edge) if visible is None else visible
    before = edge.copy(), visible.copy()
    r = measure_edge_fragments(edge, visible, origin=origin)
    xy = [tuple(p) for p in r['vertices_xy'].tolist()]
    expected = {(int(x)+origin[0], int(y)+origin[1]) for y, x in np.argwhere(edge & visible)}
    assert set(xy) == expected and len(xy) == len(expected)
    index = {p: i for i, p in enumerate(xy)}
    # Independent coordinate-set oracle, not the vectorized implementation.
    links = {(i, index[q]) for i, (x, y) in enumerate(xy)
             for dx in (-1, 0, 1) for dy in (-1, 0, 1)
             if (q := (x+dx, y+dy)) in index and i < index[q]}
    assert {tuple(e) for e in r['links'].tolist()} == links
    seen = Counter(); vertices = set()
    for chain, kind in zip(r['fragments'], r['fragment_kinds'], strict=True):
        vertices.update(chain)
        for a, b in zip(chain, chain[1:]):
            seen[tuple(sorted((a, b)))] += 1
        if kind == 'isolated':
            assert len(chain) == 1 and r['degree'][chain[0]] == 0
        else:
            assert all(r['degree'][v] == 2 for v in chain[1:-1])
            if kind == 'cycle':
                assert chain[0] == chain[-1] and r['degree'][chain[0]] == 2
            else:
                assert r['degree'][chain[0]] != 2 and r['degree'][chain[-1]] != 2
    assert set(seen) == links and all(n == 1 for n in seen.values())
    assert vertices == set(range(len(xy)))
    assert np.array_equal(edge, before[0]) and np.array_equal(visible, before[1])
    assert r['physical_identity'] == 'UNRESOLVED' and r['selected_front'] is None
    return r


def test_curved_steep_and_vertical_parts_keep_every_pixel_without_global_y_band():
    e = np.zeros((125, 85), bool)
    e[15:101, 20] = True
    for x in range(20, 75):
        e[100-(x-20), x] = True
    r = verify(e, origin=(700, 200))
    assert np.ptp(r['vertices_xy'][:, 1]) == 85
    assert any(len(f) > 48 for f in r['fragments'])


def test_all_junction_choices_and_diagonal_raster_links_are_preserved():
    e = np.zeros((17, 17), bool); e[8, 2:15] = True; e[2:15, 8] = True
    r = verify(e)
    assert np.count_nonzero(r['degree'] > 2) > 0
    assert len(r['fragments']) > 4  # 8-neighbour corner links are not thinned away.
    assert r['decision'] == 'NOT_EVALUATED'


def test_closed_diamond_and_isolated_point_are_not_lost():
    e = np.zeros((17, 17), bool); e[1, 1] = True
    for k in range(5):
        for y, x in ((4+k, 8+k), (8+k, 12-k), (12-k, 8-k), (8-k, 4+k)):
            e[y, x] = True
    r = verify(e)
    assert Counter(r['fragment_kinds']) == {'cycle': 1, 'isolated': 1}


def test_observed_gap_and_masked_gap_are_not_bridged():
    e = np.zeros((9, 17), bool); e[4, 2:15] = True
    hidden = np.ones_like(e); hidden[4, 8] = False
    r = verify(e, hidden)
    assert len(r['fragments']) == 2
    xy = r['vertices_xy'].tolist()
    assert all(r['unavailable_adjacent'][xy.index([x, 4])] for x in (7, 9))
    e[4, 8] = False
    observed = verify(e)
    assert not observed['unavailable_adjacent'].any()
    assert len(observed['fragments']) == 2


def test_crop_censoring_does_not_invent_an_endpoint_identity():
    e = np.zeros((9, 17), bool); e[4, :] = True
    r = verify(e)
    assert r['crop_adjacent'].sum() == 2 and not r['unavailable_adjacent'].any()


def test_hidden_edges_have_no_effect_and_origin_changes_coordinates_only():
    e = np.zeros((9, 17), bool); e[4, :] = True
    v = np.ones_like(e); v[:, 6:9] = False
    a = verify(e, v); e[~v] = ~e[~v]; b = verify(e, v, origin=(105, -25))
    assert np.array_equal(a['vertices_xy']+[105, -25], b['vertices_xy'])
    for key in ('links', 'degree', 'crop_adjacent', 'unavailable_adjacent'):
        assert np.array_equal(a[key], b[key])
    assert a['fragments'] == b['fragments'] and a['fragment_kinds'] == b['fragment_kinds']


def test_same_geometry_of_fluid_and_glass_remains_physically_unresolved():
    e = np.eye(25, dtype=bool)
    a, b = verify(e), verify(e.copy())
    assert a['fragments'] == b['fragments']
    assert a['decision'] == b['decision'] == 'NOT_EVALUATED'


@pytest.mark.parametrize('shape', [(1, 1), (1, 7), (7, 1), (2, 2), (6, 7)])
def test_dense_narrow_rasters_and_empty_visibility(shape):
    e = np.ones(shape, bool)
    verify(e)
    empty = verify(np.zeros(shape, bool))
    assert empty['status'] == 'MEASURED' and len(empty['vertices_xy']) == 0
    hidden = verify(e, np.zeros(shape, bool))
    assert hidden['status'] == 'UNAVAILABLE' and hidden['reason'] == 'no_visible_pixels'


def test_random_graphs_match_independent_pixel_adjacency_and_edge_partition():
    rng = np.random.default_rng(20261009)
    for _ in range(50):
        e = rng.random((11, 13)) < .3; v = rng.random(e.shape) < .9
        a = verify(e, v); b = verify(e, v)
        assert a['fragments'] == b['fragments']


@pytest.mark.parametrize('bad', ['dtype', 'shape', 'empty', 'mask', 'origin', 'huge_origin'])
def test_invalid_inputs(bad):
    e = np.zeros((4, 5), bool); v = np.ones_like(e); origin = (0, 0)
    if bad == 'dtype': e = e.astype(np.uint8)
    if bad == 'shape': e = e[None]
    if bad == 'empty': e = e[:0]
    if bad == 'mask': v = v.astype(np.uint8)
    if bad == 'origin': origin = (True, 0)
    if bad == 'huge_origin': origin = (2**63, 0)
    with pytest.raises(ValueError): measure_edge_fragments(e, v, origin=origin)


def test_vertex_limit_precedes_lookup_and_traversal_allocation(monkeypatch):
    e = np.ones((4, 5), bool)
    monkeypatch.setitem(FRAGMENT_SPEC, 'max_vertices', 2)
    monkeypatch.setattr(np, 'argwhere', lambda _: pytest.fail('allocated before bound'))
    with pytest.raises(ValueError, match='resource bound'):
        measure_edge_fragments(e, e)
