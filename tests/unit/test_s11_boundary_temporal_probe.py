import json
import cv2
import numpy as np
import pytest

from oil_tracker.adapters.vision import temporal_raster_evidence as temporal
from tests.diagnostics.s11_boundary_temporal_probe import CHANNELS, measure_pair, sample_queries


def texture():
    rng = np.random.default_rng(52)
    a = rng.integers(40, 170, (104, 104), dtype=np.uint8)
    return cv2.GaussianBlur(a, (3, 3), 0), np.ones(a.shape, bool)


@pytest.mark.parametrize('raw,expected,status', [
    ((0.,0.,.8),(0.,0.,.8),'accepted'),
    ((1.,-1.,1.2),(1.,-1.,1.),'accepted'),
    ((0.,0.,.01),(0.,0.,.01),'low_response'),
    ((10.,0.,.9),(0.,0.,.9),'shift_exceeds_bound'),
    ((float('nan'),0.,.8),(0.,0.,0.),'nonfinite'),
])
def test_optional_registration_reason_preserves_legacy_tuple(monkeypatch, raw, expected, status):
    a,m = texture()
    monkeypatch.setattr(cv2, 'phaseCorrelate', lambda *args: ((raw[0],raw[1]),raw[2]))
    plain = temporal._translation(a,a,m)
    trace = {}
    observed = temporal._translation(a,a,m,diagnostics=trace)
    assert plain == observed == expected
    assert trace['status'] == status
    json.dumps(trace, allow_nan=False)


def test_opencv_error_is_not_observed_zero(monkeypatch):
    def fail(*args): raise cv2.error('failure')
    monkeypatch.setattr(cv2,'phaseCorrelate',fail)
    a,m=texture();meta,arrays=measure_pair(a,a,m)
    assert meta['status']=='registration_unavailable'
    assert meta['registration_current_to_anchor']['status']=='opencv_error'
    assert not arrays['valid'].any()
    assert np.isnan(arrays['registered_exposure']).all()
    assert sample_queries(arrays,[{'source_x':50,'source_y':50}])[0]['mean_absolute_residual']['direct'] is None


def test_identical_textured_scene_is_valid_zero_not_identity():
    a,m=texture();before=a.copy();meta,arrays=measure_pair(a,a.copy(),m)
    assert meta['status']=='measured'
    assert meta['mean_absolute_residual']['registered_exposure']==0
    assert meta['foam_front'] is None and meta['physical_identity']=='UNRESOLVED'
    np.testing.assert_array_equal(a,before)
    json.dumps(meta,allow_nan=False)


def test_constant_scene_does_not_claim_registration():
    a=np.full((104,104),80,np.uint8);meta,arrays=measure_pair(a,a,np.ones(a.shape,bool))
    assert meta['status']=='registration_unavailable'
    assert not arrays['valid'].any()


def test_translation_and_exposure_controls_reduce_same_domain_residual():
    a,m=texture()
    b=cv2.warpAffine(a,np.float32([[1,0,1],[0,1,-1]]),(104,104),borderMode=cv2.BORDER_REFLECT)
    b=(b.astype(np.float32)*1.1+7).astype(np.uint8)
    meta,arrays=measure_pair(a,b,m)
    assert meta['status']=='measured'
    means=meta['mean_absolute_residual']
    assert means['registered_exposure'] < means['direct']*.35
    assert meta['common_pixels'] < a.size  # out-of-crop interpolation is unavailable
    for key in CHANNELS:
        assert np.array_equal(np.isfinite(arrays[key]),arrays['valid'])


def test_local_change_survives_without_assigning_physical_motion():
    a,m=texture();b=a.copy();b[45:55,45:55]+=30
    meta,arrays=measure_pair(a,b,m)
    assert meta['status']=='measured'
    local,remote=sample_queries(arrays,[{'source_x':50,'source_y':50},{'source_x':20,'source_y':20}])
    assert local['mean_absolute_residual']['registered_exposure'] > 20
    assert remote['mean_absolute_residual']['registered_exposure'] < 2
    assert meta['physical_identity']=='UNRESOLVED'


def test_fractional_interpolation_never_rescues_mask_holes(monkeypatch):
    a,m=texture();m[50,50]=False
    calls=iter([((.5,0.),.9),((-.5,0.),.9)])
    monkeypatch.setattr(cv2,'phaseCorrelate',lambda *args:next(calls))
    meta,arrays=measure_pair(a,a,m)
    assert meta['status']=='measured'
    assert not arrays['valid'][50,50] and not arrays['valid'][50,51]
    q=sample_queries(arrays,[{'source_x':150,'source_y':250}],origin=(100,200))[0]
    assert q['valid_pixels'] < q['requested_pixels'] and not q['fully_observed']


def test_high_response_out_of_bound_fallback_remains_unavailable(monkeypatch):
    a,m=texture();monkeypatch.setattr(cv2,'phaseCorrelate',lambda *args:((10.,0.),.95))
    meta,arrays=measure_pair(a,a,m)
    assert meta['status']=='registration_unavailable'
    assert meta['registration_current_to_anchor']['raw_dx']==10
    assert not arrays['valid'].any()


@pytest.mark.parametrize('bad',['dtype','shape','mask','small'])
def test_input_bounds(bad):
    a,m=texture();b=a.copy()
    if bad=='dtype': a=a.astype(float)
    if bad=='shape': b=b[:-1]
    if bad=='mask': m=m.astype(np.uint8)
    if bad=='small':
        m[:]=False;meta,arrays=measure_pair(a,b,m)
        assert meta['status']=='insufficient_geometry'
        return
    with pytest.raises(ValueError): measure_pair(a,b,m)
