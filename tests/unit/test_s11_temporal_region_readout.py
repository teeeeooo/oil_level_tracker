import json

import numpy as np
import pytest

from tests.diagnostics.s11_temporal_region_readout import decide_candidate, measure_pair


def scene(cut, *, h=48, w=24, ribbon=False, reversed_contrast=False):
    y, x = np.mgrid[:h, :w]
    z = np.abs(y-cut) < 3 if ribbon else y >= cut
    level = 140-90*z if reversed_contrast else 35+90*z
    return np.stack([level+x, level+2*x, level+x//2], axis=-1).astype(np.uint8)


def measure(a, b, cut=24, mask=None):
    valid = np.ones(a.shape[:2], bool) if mask is None else mask
    return measure_pair(a, b, valid, valid.copy(), x_range=(0, a.shape[1]), current_y=cut)


@pytest.mark.parametrize('other', [12, 36])
@pytest.mark.parametrize('inverse', [False, True])
def test_joint_moving_partition_control_without_small_jump_or_polarity_rule(other, inverse):
    a, b = scene(24, reversed_contrast=inverse), scene(other, reversed_contrast=inverse)
    before = a.copy(), b.copy()
    result = measure(a, b)
    model = result['models']['moving_step']
    assert model['tied_cuts'] == [other]
    assert model['validation_mse'] < 1e-6
    assert result['supported'], result['reason']
    np.testing.assert_array_equal(a, before[0])
    np.testing.assert_array_equal(b, before[1])
    json.dumps(result, allow_nan=False)


def test_stationary_step_is_an_unresolved_structure_collision():
    a = scene(24)
    result = measure(a, a)
    assert not result['supported']
    assert result['models']['static_step']['validation_mse'] == pytest.approx(
        result['models']['moving_step']['validation_mse'], abs=1e-12)


def test_moving_ribbon_cannot_become_a_moving_region_boundary():
    result = measure(scene(24, ribbon=True), scene(12, ribbon=True))
    assert not result['supported']
    assert result['models']['moving_ribbon_bw']['validation_mse'] < 1e-6


def test_illumination_change_on_fixed_structure_remains_unresolved():
    a = scene(24)
    result = measure(a, a+10)
    assert not result['supported']


def test_common_mask_missingness_is_not_a_zero_residual():
    a = scene(24)
    result = measure(a, a, mask=np.zeros(a.shape[:2], bool))
    assert result['status'] == 'unavailable' and not result['supported']
    assert result['models'] == {}


def test_conditional_fit_matches_full_least_squares():
    a, b = scene(24), scene(12)
    result = measure(a, b)
    h, w = a.shape[:2]
    y, x = np.mgrid[:h, :w]
    blocks=[]
    for time, cut in [(0,24),(1,12)]:
        blocks.append(np.stack([np.ones_like(x),x/(w-1),y/(h-1),
                                np.full_like(x,time),y>=cut],axis=-1))
    design=np.stack(blocks);values=np.stack([a,b]).astype(float)/255
    mask=np.stack([x%4!=0]*2);beta=np.linalg.lstsq(design[mask],values[mask],rcond=1e-10)[0]
    error=np.mean((design[~mask]@beta-values[~mask])**2)
    assert result['models']['moving_step']['validation_mse'] == pytest.approx(error,abs=1e-12)


def test_agreement_does_not_pool_away_a_bad_or_missing_sector():
    yes={'supported':True};no={'supported':False}
    views=[{'sector':i,'pairs':[yes,yes]} for i in range(5)]
    assert decide_candidate(views)[0]=='INTERFACE_SUPPORTED'
    views[2]={'sector':2,'pairs':[yes,no]}
    assert decide_candidate(views)[0]=='UNRESOLVED'
    assert decide_candidate(views[:2])[0]=='UNRESOLVED'
    assert decide_candidate([views[0]]*5)[0]=='UNRESOLVED'


@pytest.mark.parametrize('fault',['shape','float_image','nonfinite','bool_y','outside','bad_mask','string_y'])
def test_invalid_inputs_fail_closed(fault):
    a,b=scene(24),scene(12);v=np.ones(a.shape[:2],bool);cut=24
    if fault=='shape': b=b[:-1]
    if fault=='float_image': b=b.astype(float)
    if fault=='nonfinite':cut=float('nan')
    if fault=='bool_y':cut=True
    if fault=='outside':cut=100
    if fault=='bad_mask':v=v.astype(np.uint8)
    if fault=='string_y':cut='24'
    with pytest.raises(ValueError):
        measure_pair(a,b,v,v,x_range=(0,24),current_y=cut)
