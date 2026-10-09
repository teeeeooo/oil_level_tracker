"""Exact spatial matching contracts; input role does not establish later identity."""
import numpy as np
import pytest

from tests.diagnostics import s11_boundary_temporal_probe as probe


def scene():
    a=np.random.default_rng(918).integers(20,220,(17,21,3),dtype=np.uint8)
    p=np.array([[7,7],[10,8],[13,7]],np.int64)
    return a,p,np.ones(a.shape[:2],bool)


def test_identity_and_exact_costs_against_direct_centered_residuals():
    a,p,v=scene();r=probe.match_reference_constellation(a,a,p,v,v)
    assert r['best_shifts_xy'].tolist()==[[0,0]]
    x,y=r['sample_xy'].T;t=a[y,x].astype(float)
    for shift,num in zip(r['shifts_xy'],r['cost_numerators'],strict=True):
        d=t-a[y+shift[1],x+shift[0]].astype(float)
        loss=np.mean((d-d.mean(axis=0))**2)/255**2
        assert num/r['cost_denominator']==pytest.approx(loss,abs=1e-14)


def test_known_translation_and_channel_offsets():
    a,p,v=scene();b=np.zeros_like(a);b[2:,3:]=a[:-2,:-3]+[4,6,8]
    r=probe.match_reference_constellation(a,b,p,v,v)
    assert r['best_shifts_xy'].tolist()==[[3,2]]
    assert min(r['cost_numerators'])==0
    assert r['selected_front'] is None and r['physical_identity']=='UNRESOLVED'


def test_duplicates_and_order_do_not_change_sampling_weight_or_costs():
    a,p,v=scene();r=probe.match_reference_constellation(a,a,p,v,v)
    s=probe.match_reference_constellation(a,a,np.concatenate([p[::-1],p]),v,v)
    for key in ['sample_xy','shifts_xy','cost_numerators','best_shifts_xy']:
        np.testing.assert_array_equal(r[key],s[key])


def test_only_declared_samples_contribute_and_holes_stay_unmeasured():
    a,p,v=scene();r=probe.match_reference_constellation(a,a,p,v,v)
    sample=np.zeros_like(v);x,y=r['sample_xy'].T;sample[y,x]=True
    poisoned=a.copy();poisoned[~sample]=255
    s=probe.match_reference_constellation(poisoned,a,p,v,v)
    np.testing.assert_array_equal(r['cost_numerators'],s['cost_numerators'])


def test_current_visibility_and_poisoned_hidden_values():
    a,p,v=scene();cv=v.copy();cv[:,10]=False
    r=probe.match_reference_constellation(a,a,p,v,cv)
    b=a.copy();b[~cv]=255;s=probe.match_reference_constellation(a,b,p,v,cv)
    np.testing.assert_array_equal(r['shifts_xy'],s['shifts_xy'])
    np.testing.assert_array_equal(r['cost_numerators'],s['cost_numerators'])
    assert [0,0] not in r['shifts_xy'].tolist()


def test_masked_reference_and_no_current_support_are_explicit():
    a,p,v=scene();av=v.copy();av[7,7]=False
    assert probe.match_reference_constellation(a,a,p,av,v)['reason']=='reference_stencil_masked'
    assert probe.match_reference_constellation(a,a,p,v,~v)['reason']=='no_visible_current_placement'


def test_exact_repeated_pattern_ties_are_not_broken():
    y,x=np.indices((17,21));a=np.repeat(((x%3+y%3)*20+40)[...,None],3,axis=2).astype(np.uint8)
    p=np.array([[7,7],[10,8],[13,7]]);v=np.ones(a.shape[:2],bool)
    r=probe.match_reference_constellation(a,a,p,v,v)
    assert r['minimizer_count']>1 and r['selected_front'] is None


def test_constant_and_crop_censored_reference_are_unavailable():
    a,p,v=scene()
    assert probe.match_reference_constellation(np.full_like(a,42),a,p,v,v)['reason']=='constant_reference'
    assert probe.match_reference_constellation(a,a,np.array([[4,0]]),v,v)['reason']=='reference_stencil_outside_crop'


def test_geometry_translation_preserves_costs_and_inputs_are_owned():
    a,p,v=scene();before=a.copy();r=probe.match_reference_constellation(a,a,p,v,v)
    padded=np.pad(a,((3,3),(4,4),(0,0)));visible=np.pad(v,((3,3),(4,4)))
    s=probe.match_reference_constellation(padded,padded,p+[4,3],visible,visible)
    np.testing.assert_array_equal(r['shifts_xy'],s['shifts_xy'])
    np.testing.assert_array_equal(r['cost_numerators'],s['cost_numerators'])
    s['sample_xy'][:]=0;np.testing.assert_array_equal(a,before)


@pytest.mark.parametrize('bad', [np.empty((0,2),int),np.array([[1.,2.]]),np.array([[-1,2]]),np.array([[21,2]]),np.array([[True,False]])])
def test_bad_points_rejected(bad):
    a,p,v=scene()
    with pytest.raises(ValueError):probe.match_reference_constellation(a,a,bad,v,v)


def test_resource_bound_stops_without_subset_selection(monkeypatch):
    a,p,v=scene();monkeypatch.setitem(probe.CONSTELLATION_SPEC,'max_compared_values',3)
    with pytest.raises(ValueError,match='budget'):probe.match_reference_constellation(a,a,p,v,v)
