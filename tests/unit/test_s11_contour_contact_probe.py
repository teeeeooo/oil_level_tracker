"""Opposing topology/visibility controls for the saved-edge measurement."""
import numpy as np
import pytest

from tests.diagnostics.s11_contour_contact_probe import measure_edge_contacts, query_reference


def fixture(kind):
    edge = np.zeros((25, 25), dtype=bool)
    edge[12, 4:21] = True
    if kind in ('upper', 'cross'):
        edge[4:13, 12] = True
    if kind in ('lower', 'cross'):
        edge[12:21, 12] = True
    return edge


def center(edge, visible=None):
    if visible is None:
        visible = np.ones_like(edge)
    result, _ = measure_edge_contacts(edge, visible, radii=[6])
    return next(n for n in result['nodes'] if (n['source_x'], n['source_y']) == (12, 12))


@pytest.mark.parametrize('kind,expected', [
    ('upper', 'upper_contact_shape'), ('lower', 'lower_contact_shape'),
    ('cross', 'crossing_shape'), ('line', 'two_arm_shape')])
def test_oriented_arms_distinguish_contact_crossing_and_plain_boundary(kind, expected):
    assert center(fixture(kind))['pattern'] == expected


def test_identical_structural_contact_is_not_physical_identity():
    fluid, structural = fixture('upper'), fixture('upper')
    a, _ = measure_edge_contacts(fluid, np.ones_like(fluid), radii=[6])
    b, _ = measure_edge_contacts(structural, np.ones_like(structural), radii=[6])
    assert a == b
    assert a['decision'] == 'NOT_EVALUATED' and a['physical_identity'] == 'UNRESOLVED'


def test_masked_crossing_cannot_become_upper_contact():
    edge = fixture('cross')
    visible = np.ones_like(edge)
    visible[14:, 12] = False
    row = center(edge, visible)
    assert row['status'] == 'unavailable' and row['pattern'] is None


def test_outside_crop_is_unavailable():
    edge = fixture('upper')
    result, _ = measure_edge_contacts(edge, np.ones_like(edge), radii=[6])
    row = next(n for n in result['nodes'] if (n['source_x'], n['source_y']) == (12, 4))
    assert row['reason'] == 'outside_crop' and row['pattern'] is None


def test_disconnected_upper_stroke_is_not_attached_to_center():
    edge = fixture('upper')
    edge[10:12, 12] = False
    assert center(edge)['pattern'] == 'two_arm_shape'


def test_gap_is_not_morphologically_closed():
    edge = fixture('upper')
    edge[12, 14:16] = False
    assert center(edge)['pattern'] != 'upper_contact_shape'


def test_reconnected_arms_are_not_separate_branches():
    edge = fixture('upper')
    edge[6, 6:13] = True
    edge[6:13, 6] = True
    assert center(edge)['pattern'] == 'complex_or_short'


def test_hidden_pixels_do_not_influence_readout():
    edge = fixture('upper')
    visible = np.ones_like(edge)
    visible[:5] = False
    a, _ = measure_edge_contacts(edge, visible, radii=[6])
    edge[~visible] = ~edge[~visible]
    b, _ = measure_edge_contacts(edge, visible, radii=[6])
    assert a == b


def test_queries_keep_coordinates_scales_missingness_and_input_bytes():
    edge = fixture('upper'); visible = np.ones_like(edge)
    old = edge.copy(), visible.copy()
    result, available = measure_edge_contacts(edge, visible, radii=[6, 8], origin=(100, 200))
    reference = query_reference(result, available, x_range=(109, 116), source_y=212.5, half_width=3)
    assert reference['reference_source_y'] == 212.5
    assert reference['requested_centers'] == 42
    assert all(n['radius'] == 6 for n in reference['nodes'])
    assert reference['pattern_counts']['upper_contact_shape'] >= 1
    assert reference['decision'] == 'NOT_EVALUATED'
    assert np.array_equal(edge, old[0]) and np.array_equal(visible, old[1])


def test_empty_edges_are_measured_without_creating_negative_identity():
    edge = np.zeros((25, 25), bool)
    result, available = measure_edge_contacts(edge, np.ones_like(edge), radii=[6])
    reference = query_reference(result, available, x_range=(10, 15), source_y=12, half_width=3)
    assert reference['edge_center_count'] == 0 and reference['fully_observed_centers'] == 35
    assert reference['decision'] == 'NOT_EVALUATED'


@pytest.mark.parametrize('radii', [[2], [True], [6, 6], [33], []])
def test_invalid_radii_fail_before_processing(radii):
    edge = fixture('upper')
    with pytest.raises(ValueError):
        measure_edge_contacts(edge, np.ones_like(edge), radii=radii)


def test_excessive_dense_patch_work_is_bounded():
    edge = np.ones((200, 200), bool)
    with pytest.raises(ValueError, match='resource bound'):
        measure_edge_contacts(edge, edge, radii=[32])
