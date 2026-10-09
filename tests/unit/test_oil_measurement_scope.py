from dataclasses import asdict, replace, FrozenInstanceError
import json

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_measurement_scope import OilMeasurementScope, band_selection, band_record
from oil_tracker.adapters.vision.oil_material_path import _sector_profile, generate_material_path_candidates
from oil_tracker.adapters.vision.oil_supplemental_path import _phase_transition_profile, phase_transition_support
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.geometry import Rect
from oil_tracker.domain.recipe import DetectorSettings
from tests.test_oil_detector_integration import glass, oil_frame


def scope(g, rects=(Rect(146, 126, 8, 8),)):
    return OilMeasurementScope.bind(g, frame_size=(320, 240), reference_sha256='a'*64, rectangles=rects)


def test_half_open_union_clipping_and_same_x_other_y():
    s = scope(glass(), (Rect(90, 126, 18, 8), Rect(100, 128, 18, 8), Rect(-100, -100, 1, 1)))
    mask = s.rasterize((20, 40), (80, 120))
    expected = np.zeros((20, 40), bool)
    expected[6:14, 10:28] = True
    expected[8:16, 20:38] = True
    assert np.array_equal(mask, expected)
    assert not mask[16:, 10:28].any() and not mask.flags.writeable
    with pytest.raises(FrozenInstanceError):
        s.glass_id = 'mutated'
    with pytest.raises(ValueError):
        s.rasterize((2049, 2), (0, 0))


@pytest.mark.parametrize('rect', [Rect(0,0,0,2),Rect(0,0,-1,2),Rect(.1,0,1,2),Rect(float('nan'),0,1,2),Rect(True,0,1,2)])
def test_invalid_rectangles_fail_before_rasterization(rect):
    with pytest.raises(ValueError): scope(glass(), (rect,))


def test_bounds_bindings_duplicates_and_context_change_fail_before_state():
    g=glass(); s=scope(g)
    with pytest.raises(ValueError): scope(g, (Rect(1,1,1,1),)*17)
    with pytest.raises(ValueError): OpenCvPhaseDetector(oil_measurement_scopes=(s,s))
    for changes in ({'reference_sha256':'x'}, {'frame_size':(True,240)}, {'rectangles':[]}):
        with pytest.raises(ValueError): replace(s, **changes)
    d=OpenCvPhaseDetector(oil_measurement_scopes=(s,))
    g.detector_settings.minimum_final_confidence=.7
    with pytest.raises(ValueError, match='binding mismatch'): d.detect(oil_frame(),g,1,0)
    assert not d._trackers
    assert d.version != OpenCvPhaseDetector.version


@pytest.mark.parametrize('rects', [(),(Rect(0,0,2,2),), (Rect(-20,-20,1,1),)])
def test_empty_or_no_eligible_intersection_complete_legacy_output(rects):
    g=glass();frame=oil_frame()
    a,aa=OpenCvPhaseDetector().detect(frame,g,1,0,debug=True)
    d=OpenCvPhaseDetector(oil_measurement_scopes=(scope(g,rects),))
    b,bb=d.detect(frame,g,1,0,debug=True)
    assert asdict(a)==asdict(b)
    assert aa.state==bb.state
    if not rects: assert d.version==OpenCvPhaseDetector.version


def test_other_glass_isolation_and_reset_keeps_explicit_policy():
    g=glass();d=OpenCvPhaseDetector(oil_measurement_scopes=(scope(g),));other=glass(glass_id='other')
    a,_=d.detect(oil_frame(),other,1,0)
    b,_=OpenCvPhaseDetector().detect(oil_frame(),other,1,0)
    assert asdict(a)==asdict(b)
    version=d.version; d.reset()
    assert d.version==version and len(d.measurement_scope_manifest)==1


@pytest.mark.parametrize('step', [0,40,-40])
def test_affected_asymmetric_horizontal_ramp_retains_only_real_vertical_step(step):
    values=np.tile(np.arange(100,dtype=np.float32)*2,(100,1)); values[51:]+=step
    visible=np.ones(values.shape,bool);excluded=np.zeros_like(visible)
    for x in range(0,100,20): excluded[40:50,x+12:x+20]=True
    base=_phase_transition_profile(values,visible)
    new=_phase_transition_profile(values,visible,measurement_exclusion=excluded)
    support=phase_transition_support(values,visible,local_y=50,measurement_exclusion=excluded)
    for row in support:
        assert row['pooled_delta']==pytest.approx(step)
        assert row['sampling']['rule']=='complete_common_x'
        assert row['sampling']['original_counts']==[row['radius']*20]*2
        assert row['sampling']['used_counts']==[row['radius']*12]*2
    for a,b in zip(base,new): assert np.array_equal(a[65:],b[65:])
    assert new[0][50]==pytest.approx(min(1,abs(step)/48))


def test_unaffected_disjoint_visibility_retains_legacy_but_affected_has_no_common_support():
    uv=np.zeros((3,10),bool);lv=uv.copy();uv[:,:5]=True;lv[:,5:]=True
    zero=np.zeros_like(uv)
    u,l,changed,reason=band_selection(uv,lv,zero,zero,minimum=2)
    assert not changed and reason=='legacy_pool' and u is uv and l is lv
    ex=zero.copy();ex[0,0]=True
    u,l,changed,reason=band_selection(uv,lv,ex,zero,minimum=2)
    assert changed and reason=='insufficient_common_support' and not u.any() and not l.any()


def test_native_original_normalization_and_untouched_primitives_are_exact():
    rng=np.random.default_rng(72)
    image=rng.integers(20,190,size=(120,100)).astype(np.float32)
    visible=np.ones(image.shape,bool);excluded=np.zeros_like(visible);excluded[43:48,3:8]=True
    args=dict(material_evidence_map=None,capture_diagnostics=True)
    a=_sector_profile(image,visible,0,20,**args)
    b=_sector_profile(image,visible,0,20,measurement_exclusion=excluded,**args)
    for key in ('score','signed','support','contrast_channel','contrast_scale'):
        aa,bb=getattr(a,key),getattr(b,key)
        assert np.array_equal(aa[:30],bb[:30]) and np.array_equal(aa[60:],bb[60:])
    assert np.array_equal(image,rng.__class__(np.random.PCG64(72)).integers(20,190,size=(120,100)).astype(np.float32))


def test_native_partial_withdrawal_preserves_line_else_all_masked_unavailable():
    frame=np.full((120,120,3),175,np.uint8); frame[60:]=70
    mask=np.full((120,120),255,np.uint8);pre=preprocess(frame,mask,DetectorSettings())
    excluded=np.zeros(mask.shape,bool);excluded[52:68,:24]=True
    candidates=generate_material_path_candidates(pre,mask,None,crop_origin_y=0,measurement_exclusion=excluded)
    assert candidates and abs(candidates[0].y-60)<=3
    assert candidates[0].features['material_path_sector_fraction']==pytest.approx(.8)
    assert not generate_material_path_candidates(pre,mask,None,crop_origin_y=0,measurement_exclusion=np.ones_like(excluded))


def test_real_entry_debug_neutral_foam_unchanged_and_actual_native_lineage():
    g=glass();frame=oil_frame();before=frame.copy();s=scope(g)
    d=OpenCvPhaseDetector(oil_measurement_scopes=(s,))
    a,_=d.detect(frame,g,1,0,debug=False)
    b,art=OpenCvPhaseDetector(oil_measurement_scopes=(s,)).detect(frame,g,1,0,debug=True)
    baseline,base_art=OpenCvPhaseDetector().detect(frame,g,1,0,debug=True)
    assert asdict(a)==asdict(b) and np.array_equal(frame,before)
    assert art.state['foam_component_diagnostics']==base_art.state['foam_component_diagnostics']
    unchanged={'distributed_sobel_path','calibrated_high_recall'}
    assert [asdict(c) for c in a.candidates if c.source in unchanged or c.source.startswith('oil_hypothesis:')]==[asdict(c) for c in baseline.candidates if c.source in unchanged or c.source.startswith('oil_hypothesis:')]
    records=art.state['oil_measurement_lineage']['candidates']
    native=[r for r in records if r.get('native_sampling')]
    assert native
    for r in native:
        assert r['sampling_scope']['sha256']==s.sha256
        for op in r['native_sampling']:
            assert op['available'] and all(u<=o for u,o in zip(op['used_counts'],op['original_counts']))
    assert len(json.dumps(records))<1_048_576
    # Physical labels and candidate authority never appear in the scope.
    assert 'target_role' not in json.dumps(s.manifest)


def test_diagnostic_exhaustion_is_explicit_and_cannot_change_detection(monkeypatch):
    from oil_tracker.adapters.vision import phase_candidate_assembler as assembler
    g=glass();s=scope(g)
    before,_=OpenCvPhaseDetector(oil_measurement_scopes=(s,)).detect(oil_frame(),g,1,0)
    monkeypatch.setattr(assembler,'MAX_TRACE_BYTES',1)
    after,art=OpenCvPhaseDetector(oil_measurement_scopes=(s,)).detect(oil_frame(),g,1,0,debug=True)
    assert asdict(before)==asdict(after)
    assert all(r['reason']=='sampling_trace_bound_exceeded' for r in art.state['oil_measurement_lineage']['candidates'])


def test_same_reference_cannot_also_veto_and_unrelated_templates_remain_allowed():
    from oil_tracker.domain.artifact_reference import ArtifactSupportReference
    from oil_tracker.domain.geometry import ArtifactTemplate
    g=glass();s=scope(g)
    # Binding is metadata validation; existing reference decoding remains its own owner.
    ref=ArtifactSupportReference('{}','a'*64,'unreviewed',None)
    t=ArtifactTemplate('t','oil_air',.5,.5,.2,.1,support_reference=ref)
    g.geometry.artifact_templates=[t]
    with pytest.raises(ValueError,match='artifact veto'): s.validate(g,oil_frame())
    g.geometry.artifact_templates=[replace(t,support_reference=replace(ref,snapshot_sha256='b'*64))]
    s.validate(g,oil_frame())


def test_phase_trace_reproduces_actual_scoped_profile_and_unavailable_support():
    image=np.full((100,100),90,np.float32);image[51:]=150
    visible=np.ones_like(image,bool);ex=np.zeros_like(visible)
    ex[40:50,:10]=True;ex[51:61,10:20]=True
    a=_phase_transition_profile(image,visible,measurement_exclusion=ex)
    rows=phase_transition_support(image,visible,local_y=50,measurement_exclusion=ex)
    response=[];coverage=[]
    for radius in (3,6,10):
        ops=[r for r in rows if r['radius']==radius]
        first=ops[0]
        assert not first['pooled_available'] and first['sampling']['reason']=='insufficient_common_support'
        assert first['sampling']['used_counts']==[0,0]
        deltas=[abs(r['pooled_delta'])/48 for r in ops if r['pooled_available']]
        response.append(min(1,np.median(deltas)));coverage.append(len(deltas)/5)
    assert a[0][50]==max(response) and a[1][50]==pytest.approx(coverage[np.argmax(response)])


def test_native_trace_does_not_invent_a_new_floor_for_untouched_legacy_band():
    visible=np.ones((20,10),bool);visible[5:8]=False
    ex=np.zeros_like(visible);ex[0]=True
    record=band_record(visible,ex,row=8,radius=3,start=0,stop=10,crop_origin=(0,0),minimum=15,legacy_zero_weight=True)
    assert record['available'] and record['rule']=='legacy_pool'
    assert record['original_counts']==[0,30] and record['used_counts']==[0,30]
    assert record['minimum_per_side']==0 and record['legacy_zero_weight_value']==0
