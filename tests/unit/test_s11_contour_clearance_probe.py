"""Ordered-gap information, censoring and same-observable optical opposition."""
import numpy as np
import pytest

from tests.diagnostics.s11_contour_contact_probe import measure_edge_clearance


def raster(above=16, below=40):
    edge = np.zeros((50, 20), dtype=bool)
    edge[[above, 20, below], :] = True
    return edge


def measure(edge, visible=None, **kwargs):
    args = dict(x_range=[5, 15], source_y=20, half_width=3)
    args.update(kwargs)
    return measure_edge_clearance(edge, np.ones_like(edge) if visible is None else visible, **args)


def test_empty_run_order_and_original_reference_are_explicit():
    row = measure(raster())['columns'][0]
    assert row['band_edge_source_y'] == [20]
    assert row['above']['stop_source_y'] == 16 and row['below']['stop_source_y'] == 40
    assert row['above']['clear_pixel_count'] == 0
    assert row['below']['clear_pixel_count'] == 16
    assert row['below_minus_above_edge_distance'] == 16


def test_same_edge_count_different_order_remains_distinct():
    a, b = raster(), raster(above=1, below=24)
    assert a.sum() == b.sum()
    assert measure(a)['columns'][0]['below_minus_above_edge_distance'] == 16
    assert measure(b)['columns'][0]['below_minus_above_edge_distance'] == -15


def test_texture_continuing_on_both_sides_can_have_equal_clearance():
    assert measure(raster(15, 25))['columns'][0]['below_minus_above_edge_distance'] == 0


def test_plain_real_or_optical_boundary_with_no_other_edges_is_not_negative():
    edge = np.zeros((50,20), bool); edge[20] = True
    result = measure(edge); row = result['columns'][0]
    assert row['above']['status'] == row['below']['status'] == 'censored'
    assert row['above']['reason'] == row['below']['reason'] == 'outside_crop'
    assert row['below_minus_above_edge_distance'] is None
    assert result['decision'] == 'NOT_EVALUATED' and result['physical_identity'] == 'UNRESOLVED'


def test_mask_before_edge_censors_and_hidden_values_never_change_result():
    edge = raster(); visible = np.ones_like(edge); visible[32:] = False
    a = measure(edge, visible); row = a['columns'][0]
    assert row['below'] == {'status':'censored', 'reason':'masked','stop_source_y':32,
                           'clear_pixel_count':8,'edge_distance_from_reference':None}
    edge[~visible] = ~edge[~visible]
    assert measure(edge, visible) == a


def test_invalid_reference_band_does_not_measure_through_mask():
    edge = raster(); visible = np.ones_like(edge); visible[21,5] = False
    rows = measure(edge, visible)['columns']
    assert rows[0]['status'] == 'reference_unavailable' and rows[0]['above'] is None
    assert rows[1]['status'] == 'measured'


def test_crop_clipped_band_is_unavailable():
    row = measure(raster(), source_y=1)['columns'][0]
    assert row['status'] == 'reference_unavailable' and row['reason'] == 'outside_crop'


def test_mask_stop_is_not_crossed_to_a_later_visible_edge():
    edge = raster(); visible = np.ones_like(edge); visible[26] = False
    row = measure(edge, visible)['columns'][0]
    assert row['below']['stop_source_y'] == 26 and row['below']['status'] == 'censored'


def test_no_edge_in_band_does_not_snap_y_to_a_nearby_edge():
    edge = raster(); edge[20] = False
    result = measure(edge)
    assert result['reference_source_y'] == 20
    assert result['columns'][0]['band_edge_source_y'] == []
    assert result['decision'] == 'NOT_EVALUATED'


def test_fractional_source_geometry_is_preserved_without_rounding():
    result = measure(raster(), x_range=[105,115], source_y=220.5, origin=(100,200))
    assert result['reference_source_y'] == 220.5
    assert result['reference_band_source_y'] == [218,223]
    row = result['columns'][0]
    assert row['source_x'] == 105 and row['band_edge_source_y'] == [220]
    assert row['above']['edge_distance_from_reference'] == 4.5
    assert row['below']['edge_distance_from_reference'] == 19.5


def test_structural_copy_is_indistinguishable_and_inputs_stay_unchanged():
    fluid = raster(); optical = fluid.copy(); visible = np.ones_like(fluid)
    a, b = measure(fluid, visible), measure(optical, visible)
    assert a == b and np.array_equal(fluid, optical) and visible.all()
    assert a['physical_identity'] == 'UNRESOLVED'


@pytest.mark.parametrize('kwargs', [{'source_y':float('nan')},{'source_y':True},{'source_y':'20'},
                                   {'half_width':0},{'half_width':33},{'x_range':[0,21]}])
def test_invalid_geometry_fails_before_scanning(kwargs):
    with pytest.raises(ValueError): measure(raster(), **kwargs)


def test_raster_resource_limit():
    with pytest.raises(ValueError): measure(np.zeros((513,513),bool))
