import numpy as np
import pytest

from tests.diagnostics.s11_boundary_temporal_probe import (
    _side_costs, _test_side, compare_split_sides, SPLIT_SIDE_SPEC,
)


def fixture(shifts=((3,2),(3,2))):
    rng=np.random.default_rng(417)
    a=rng.integers(20,180,(35,43,3),dtype=np.uint8)
    b=rng.integers(20,180,a.shape,dtype=np.uint8)
    depth=4;x0,x1=12,21;y0,y1=12,14
    for (s0,s1),(dx,dy) in zip([(y0-depth,y0),(y1,y1+depth)],shifts,strict=True):
        b[s0+dy:s1+dy,x0+dx:x1+dx]=a[s0:s1,x0:x1]+7
    mask=np.ones(a.shape[:2],bool)
    return a,b,mask,dict(x_range=(x0,x1),y_range=(y0,y1),depth=depth)


def test_common_translation_and_exposure_are_not_two_materials():
    a,b,m,kw=fixture()
    before=[x.copy() for x in (a,b,m)]
    r=compare_split_sides(a,b,m,m,**kw)
    assert r['transport_pattern']=='SHARED_MATCH'
    for f in r['folds']:
        assert f['matches']=={k:[3,2] for k in ['upper_shift','lower_shift','common_shift']}
        assert f['common_test_error']==f['split_test_error']==0
    assert r['physical_identity']=='UNRESOLVED' and r['selected_front'] is None
    for x,y in zip(before,(a,b,m),strict=True):assert np.array_equal(x,y)


def test_distinct_ordered_side_transport_survives_heldout_columns():
    a,b,m,kw=fixture(shifts=((3,-2),(-3,5)))
    r=compare_split_sides(a,b,m,m,**kw)
    assert r['transport_pattern']=='SPLIT_BETTER'
    for f in r['folds']:
        assert f['matches']['upper_shift']==[3,-2]
        assert f['matches']['lower_shift']==[-3,5]
        assert f['split_test_error']==0 < f['common_test_error']


def test_piecewise_warp_of_fixed_pattern_is_a_non_material_counterexample():
    # The same two transported texture bands can be two regions of one optical
    # pattern. Differential transport must never be promoted to Foam identity.
    a,b,m,kw=fixture(shifts=((-4,0),(4,0)))
    r=compare_split_sides(a,b,m,m,**kw)
    assert r['transport_pattern']=='SPLIT_BETTER'
    assert r['physical_identity']=='UNRESOLVED'
    assert r['selected_front'] is None


def test_flat_or_repeating_patch_does_not_pick_first_minimum():
    a=np.full((20,24,3),100,np.uint8);m=np.ones(a.shape[:2],bool)
    r=compare_split_sides(a,a,m,m,x_range=(4,11),y_range=(8,9),depth=3)
    assert r['transport_pattern']=='AMBIGUOUS_FIT'
    assert all(f['matches'] is None and min(f['minimizer_counts'])>1 for f in r['folds'])


def test_masked_anchor_and_current_gap_are_unavailable():
    a,b,m,kw=fixture()
    hidden=m.copy();hidden[12,15]=False  # The excluded plateau still needs visibility.
    assert compare_split_sides(a,b,hidden,m,**kw)['reason']=='anchor_masked'
    assert compare_split_sides(a,b,m,np.zeros_like(m),**kw)['reason']=='no_visible_current_placement'


def test_search_does_not_accept_poisoned_best_rectangle():
    a,b,m,kw=fixture();hidden=m.copy()
    hidden[14,18]=False  # Within translated plateau (source x15,y12 + shift3,2).
    r=compare_split_sides(a,b,m,hidden,**kw)
    for f in r['folds']:
        if f['matches'] is not None:
            assert f['matches']['common_shift'] != [3,2]


def test_integer_fit_matches_brute_force_mean_centering():
    rng=np.random.default_rng(451)
    t=rng.integers(0,256,(3,7,3),dtype=np.uint8)
    w=rng.integers(0,256,(6,3,7,3),dtype=np.uint8)
    columns=np.arange(7)%2==0
    cost,sums,n=_side_costs(t,w,columns)
    for i in range(len(w)):
        d=t[:,columns].astype(float)-w[i][:,columns].astype(float)
        expected=np.square(d-d.mean(axis=(0,1))).sum()
        assert cost[i]/n==pytest.approx(expected)
        assert np.array_equal(sums[i],d.sum(axis=(0,1)))


def test_crop_boundary_is_unavailable_not_zero_error():
    a,b,m,kw=fixture();kw['y_range']=(1,2)
    r=compare_split_sides(a,b,m,m,**kw)
    assert r['status']=='UNAVAILABLE' and r['reason']=='anchor_outside_crop' and r['folds']==[]


def test_large_heldout_residual_keeps_exact_arithmetic_beyond_int64():
    t=np.full((300,201,3),255,np.uint8);w=np.zeros_like(t)
    train=np.arange(201)%2==0;test=~train
    n=300*int(train.sum())
    # Training and test differences oppose each other, maximizing residuals.
    numerator,denominator=_test_side(t,w,test,np.full(3,-255*n,np.int64),n)
    expected=int(t[:,test].size)*(510*n)**2
    assert expected > np.iinfo(np.int64).max
    assert numerator==expected and denominator==int(t[:,test].size)*n**2


@pytest.mark.parametrize('change', ['dtype','shape','mask','geometry','depth'])
def test_invalid_inputs(change):
    a,b,m,kw=fixture()
    if change=='dtype':a=a.astype(float)
    if change=='shape':b=b[:-1]
    if change=='mask':m=m.astype(np.uint8)
    if change=='geometry':kw['x_range']=(5,6)
    if change=='depth':kw['depth']=True
    with pytest.raises(ValueError):compare_split_sides(a,b,m,m,**kw)


def test_work_bound_checked_before_search_allocation(monkeypatch):
    a,b,m,kw=fixture()
    monkeypatch.setitem(SPLIT_SIDE_SPEC,'max_compared_samples',1)
    with pytest.raises(ValueError,match='resource bound'):
        compare_split_sides(a,b,m,m,**kw)
