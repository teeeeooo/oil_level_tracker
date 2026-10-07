from dataclasses import asdict, replace, FrozenInstanceError
import json

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_pipeline_diagnostics import (
    OilMeasurementLineage, project_measurement_lineage,
)
from oil_tracker.adapters.vision.oil_shadow_observations import (
    _narrow_summary, build_bounded_proposals,
)
from oil_tracker.adapters.vision.oil_shadow_types import OilShadowBounds
from oil_tracker.adapters.vision.oil_supplemental_path import (
    _phase_transition_profile, phase_transition_support,
)
from tests.test_oil_shadow_observations import _raw
from tests.test_oil_detector_integration import glass, oil_frame
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector


def test_disjoint_x_pooling_reports_false_contrast_without_inventing_paired_support():
    image = np.tile(np.tile([0, 0, 0, 0, 192, 192, 192, 192], 5), (100, 1)).astype(np.uint8)
    visible = np.zeros_like(image, bool)
    for x in range(0, 40, 8):
        visible[:50, x:x+4] = True
        visible[51:, x+4:x+8] = True
    before = image.copy(), visible.copy()
    response, coverage, consistency, _ = _phase_transition_profile(image, visible)
    support = phase_transition_support(image, visible, local_y=50, crop_origin=(13, 700))
    assert response[50] == coverage[50] == consistency[50] == 1
    assert len(support) == 15
    for s in support:
        assert s['pooled_delta'] == 192
        assert s['pooled_available']
        assert s['common_x_count'] == s['paired_x_count'] == 0
        assert not s['paired_available'] and s['paired_mean_delta'] is None
        assert s['paired_reason'] == 'no_complete_common_columns'
        assert s['upper_mean_source_x'] < s['lower_mean_source_x']
    assert np.array_equal(image, before[0]) and np.array_equal(visible, before[1])


def test_matched_step_support_and_exact_x_runs_are_retained():
    image = np.full((100, 40), 170, np.uint8); image[51:] = 70
    valid = np.ones_like(image, bool); valid[:, 3:5] = False
    rows = phase_transition_support(image, valid, local_y=50, crop_origin=(10, 20))
    assert rows[0]['paired_x_runs'] == ((10,13), (15,18))
    for row in rows:
        assert row['pooled_delta'] == row['paired_mean_delta'] == row['paired_median_delta'] == -100
    assert rows[0]['upper_source_y_range'] == (67,70)
    assert rows[0]['lower_source_y_range'] == (71,74)


@pytest.mark.parametrize('shape,y', [((0,0),0),((2,3),0),((8,3),-1),((8,3),99)])
def test_small_empty_and_outside_crops_do_not_wrap_or_invent_values(shape,y):
    image = np.ones(shape, np.uint8)
    records = phase_transition_support(image, image, local_y=y)
    assert len(records) == 15
    assert all(r['pooled_delta'] is None and r['paired_mean_delta'] is None for r in records)
    json.dumps(records, allow_nan=False)


@pytest.mark.parametrize('value', [True, np.bool_(False), 1.5, float('nan')])
def test_support_sampling_indices_reject_bool_and_nonintegral_values(value):
    with pytest.raises(ValueError, match='integer'):
        phase_transition_support(np.ones((20,20)),np.ones((20,20)),local_y=value)


@pytest.mark.parametrize('sign,relation', [(-0.7,'same'),(0.7,'opposite'),(0.,'zero'),(None,'unknown')])
def test_legacy_pair_retains_signed_validity_without_changing_strength(sign,relation):
    bounds=OilShadowBounds();proposal=build_bounded_proposals((_raw(40),),bounds)[0]
    context={k:np.zeros(80) for k in ['energy','coverage','signed','valid','glare','exclusion','border','static']}
    context['valid'][:]=1;context['energy'][40]=.8;context['energy'][44]=.9
    context['signed'][40]=-.8;context['signed'][44]=0 if sign is None else sign
    if sign is None:context['valid'][44]=0
    baseline=_narrow_summary(proposal,context,bounds);sink={}
    assert _narrow_summary(proposal,context,bounds,diagnostic_sink=sink)==baseline
    pair=sink['narrow_pair']
    assert pair['center_local_y']==40 and pair['partner_local_y']==44
    assert pair['legacy_pair_strength']==.8
    assert pair['sign_relation']==relation
    assert pair['partner_valid']==(sign is not None)


def test_real_entry_sidecar_is_lossless_and_has_no_mutable_raster_aliases(monkeypatch):
    from oil_tracker.adapters.vision import phase_candidate_assembler as assembly
    config=glass();frame=oil_frame()
    no_debug,_=OpenCvPhaseDetector().detect(frame,config,1,0.,debug=False)
    observed,artifacts=OpenCvPhaseDetector().detect(frame,config,1,0.,debug=True)
    assert asdict(no_debug)==asdict(observed)
    namespace=artifacts.state['oil_measurement_lineage']
    assert namespace['decision']=='NOT_EVALUATED'
    semantic=[r for r in namespace['candidates'] if r['source'].startswith('oil_hypothesis:')]
    assert semantic and all(r['status']=='measured' for r in semantic)
    for row in semantic:
        for member in row['hypothesis']['members']:
            pair=member['narrow_pair']
            assert pair['center_source_y']==pair['center_local_y']+namespace['crop_origin'][1]
            assert member['score_nodes']['boundary']>=0
            assert len(member['broad_samples'])==3
    assert 'oil_measurement_lineage' not in observed.debug_metrics
    saved=json.dumps(namespace,sort_keys=True,allow_nan=False)
    frame[:]=0
    assert json.dumps(namespace,sort_keys=True,allow_nan=False)==saved
    def forbidden(*args,**kwargs):raise AssertionError('capture with debug NONE')
    monkeypatch.setattr(assembly,'capture_measurement_lineage',forbidden)
    OpenCvPhaseDetector().detect(oil_frame(),config,2,.5,debug=False)


def test_duplicate_candidate_identity_is_by_index_and_rejects_wrong_binding():
    from oil_tracker.domain.detection import BoundaryCandidate
    from oil_tracker.domain.enums import BoundaryKind
    c=BoundaryCandidate('same',BoundaryKind.OIL_AIR,33.5)
    a=OilMeasurementLineage(0,c.source,c.y,'{"status":"unavailable"}')
    b=replace(a,candidate_input_index=1)
    kwargs=dict(frame_index=1,glass_id='유리',crop_origin=(2,3))
    output=project_measurement_lineage((a,b),(c,c),**kwargs)
    assert [r['candidate_input_index'] for r in output['candidates']]==[0,1]
    with pytest.raises(FrozenInstanceError):a.source_y=22
    for invalid in [replace(a,candidate_input_index=True),replace(a,candidate_input_index=.5),replace(a,source='wrong'),replace(a,source_y=34)]:
        with pytest.raises(ValueError):project_measurement_lineage((invalid,),(c,),**kwargs)
    with pytest.raises(ValueError):project_measurement_lineage((a,a),(c,c),**kwargs)


def test_saved_real_pair_preserves_distinct_proposal_measurement_and_scalar_coordinates():
    from pathlib import Path
    from oil_tracker.adapters.vision.oil_shadow_types import BoundedYProposal
    data=json.loads((Path(__file__).parents[1]/'fixtures/s11_measurement_lineage_real_case.json').read_text())
    payload=data['proposal'];payload['member_ids']=tuple(payload['member_ids'])
    proposal=BoundedYProposal(**payload)
    context={k:np.asarray(v,dtype=data['context_dtypes'][k]) for k,v in data['context'].items()}
    sink={};value=_narrow_summary(proposal,context,OilShadowBounds(),diagnostic_sink=sink)
    assert json.loads(json.dumps(asdict(value)))==data['expected']
    member=data['candidate']['hypothesis']['members'][0];pair=sink['narrow_pair']
    origin=data['crop_origin'][1]
    assert pair['center_local_y']+origin==member['narrow_pair']['center_source_y']==853
    assert pair['partner_local_y']+origin==member['narrow_pair']['partner_source_y']==851
    assert pair['sign_relation']=='same'
    assert member['scalar_source_y']==854
    assert pair['legacy_pair_strength']==pytest.approx(.7475433913485435)
    assert member['score_nodes']['pulse_artifact']>0
    assert 'pulse_artifact' in project_measurement_lineage((),(),frame_index=420,glass_id='x',crop_origin=(0,0))['score_dependencies']['boundary']
