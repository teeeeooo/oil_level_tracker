"""Shape-hypothesis controls, explicitly not evidence of physical oil identity."""
import copy
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from tests.diagnostics import s11_shadow_experiment as experiment
from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.unit.test_s11_shadow_experiment import inputs, candidate, ablation_case
from tests.unit.test_oil_interface_witness import measure


def profile(values=(.2,.2,.8,.8)):
    ranges=((70,78),(90,98),(103,111),(123,131))
    return {'band_width_px':8,'bands':[{'name':n,'gray_mean':v,'available':True,
            'clipped_local_y_range':list(r),'valid_fraction':1.0,'reason':''}
            for n,v,r in zip(experiment.PROFILE_BANDS,values,ranges)]}


def enrich(c, values=(.2,.2,.8,.8)):
    means={b['name']:b for b in profile(values)['bands']}
    for sector in c['sectors']:
        for center in sector['centers']:
            for scale in center['scales']:
                for b in scale['bands']: b.update(means[b['name']])
    return c


def test_persistent_step_beats_isolated_stripes_and_ramp_with_same_parameters():
    step=experiment.profile_scale(profile())
    stripe=experiment.profile_scale(profile((.2,.2,.8,.2)))
    ridge=experiment.profile_scale(profile((.2,.8,.8,.2)))
    ramp=profile()
    for b in ramp['bands']:
        b['gray_mean']=.2+.005*sum(b['clipped_local_y_range'])/2
    linear=experiment.profile_scale(ramp)
    assert step['score'] > 0
    assert step['residuals']['step'] == pytest.approx(0)
    assert stripe['score'] < 0 and ridge['score'] < 0 and linear['score'] < 0
    assert stripe['residuals']['near_below_excursion'] == pytest.approx(0)
    assert linear['residuals']['ramp'] == pytest.approx(0)
    # Competing models use the same two nuisance parameters, no label fitting.
    assert step['centered_energy'] == pytest.approx(.36)


def test_structural_step_is_intentionally_indistinguishable_not_certified_oil():
    c=enrich(candidate(equal=True)); d=copy.deepcopy(c);d['candidate_input_index']=10
    scored=[experiment.score_candidate(v) for v in (c,d)]
    report=experiment.evaluate_identity_profile(ablation_case(scored,('interface','non_interface')),[c,d],scored)
    for name in ('common_support','profile_supported'):
        e=report[name]['evaluation']
        assert e['identity_ordering']['counts'][experiment.PROFILE_METHOD] == {'tie':1}
        assert e['path_ordering'] == {}
        assert len(e['candidate_ranking'][experiment.PROFILE_METHOD]['top_ranked']) == 2
    assert 'decision' not in report


def test_flat_zero_polarity_offset_and_coordinate_translation():
    assert experiment.profile_scale(profile((.4,)*4))['score'] == 0
    base=profile(); flipped=profile(tuple(1-b['gray_mean'] for b in base['bands']))
    offset=profile(tuple(.05+b['gray_mean'] for b in base['bands']))
    moved=copy.deepcopy(base)
    for b in moved['bands']: b['clipped_local_y_range']=[v+123 for v in b['clipped_local_y_range']]
    score=experiment.profile_scale(base)['score']
    assert experiment.profile_scale(flipped)['score'] == pytest.approx(score)
    assert experiment.profile_scale(offset)['score'] == pytest.approx(score)
    assert experiment.profile_scale(moved)['score'] == pytest.approx(score)
    assert experiment.profile_scale(profile((.499,.499,.501,.501)))['score'] > 0


def test_identity_ranking_uses_signed_profile_preference_without_path_truth():
    a = enrich(candidate(equal=True))
    b = enrich(candidate(equal=True), (.2, .2, .8, .2))
    b['candidate_input_index'] = 10
    scored = [experiment.score_candidate(c) for c in (a, b)]
    case = ablation_case(scored, ('interface', 'non_interface'))
    result = experiment.evaluate_identity_profile(case, [a, b], scored)
    for view in ('common_support', 'profile_supported'):
        scores = result[view]['scores']
        assert scores[0]['matched_scores'][experiment.PROFILE_METHOD] > 0
        assert scores[1]['matched_scores'][experiment.PROFILE_METHOD] < 0
        evaluation = result[view]['evaluation']
        assert evaluation['identity_ordering']['counts'][experiment.PROFILE_METHOD] == {'correct': 1}
        assert evaluation['path_ordering'] == {}


@pytest.mark.parametrize('state',['missing','null','unavailable','range_missing','range_null','empty_range'])
def test_missing_band_evidence_stays_null_with_reason(state):
    s=profile(); b=s['bands'][0]
    if state=='missing': del b['gray_mean']
    if state=='null': b['gray_mean']=None
    if state=='unavailable': b['available']=False
    if state=='range_missing': del b['clipped_local_y_range']
    if state=='range_null': b['clipped_local_y_range']=None
    if state=='empty_range': b['clipped_local_y_range']=[0,0]
    r=experiment.profile_scale(s)
    assert r['score'] is None and r['residuals'] is None and r['unavailable_reasons']
    if state in ('missing','null'): assert r['observations'][0]['gray_mean_status']==state


@pytest.mark.parametrize('fault',['bool','nan','outside','reversed_range','duplicate','order'])
def test_invalid_profiles_fail(fault):
    s=profile();b=s['bands'][0]
    if fault=='bool':b['gray_mean']=True
    if fault=='nan':b['gray_mean']=float('nan')
    if fault=='outside':b['gray_mean']=1.1
    if fault=='reversed_range':b['clipped_local_y_range']=[3,2]
    if fault=='duplicate':s['bands'].append(copy.deepcopy(b))
    if fault=='order':b['clipped_local_y_range']=[300,310]
    with pytest.raises(ValueError):experiment.profile_scale(s)


def test_profile_support_is_separate_from_alignment_availability():
    a=enrich(candidate(equal=True));b=copy.deepcopy(a);b['candidate_input_index']=10
    b['sectors'][0]['centers'][0]['scales'][0]['bands'][0]['normal_alignment']=None
    scored=[experiment.score_candidate(v) for v in (a,b)]
    r=experiment.evaluate_identity_profile(ablation_case(scored,('interface','non_interface')),[a,b],scored)
    assert r['common_support']['evaluation']['identity_ordering']['counts'][experiment.PROFILE_METHOD] == {'unscorable':1}
    assert r['profile_supported']['evaluation']['identity_ordering']['counts'][experiment.PROFILE_METHOD] == {'tie':1}
    assert r['support_transition']['identity']['newly_scorable_outcomes'] == {'tie':1}
    assert r['common_support']['scores'][1]['matched_scores'][experiment.PROFILE_METHOD] is None


def test_missing_profile_can_remove_v1_support_without_baseline_fallback():
    c=enrich(candidate())
    c['sectors'][0]['centers'][0]['scales'][0]['bands'][0]['gray_mean']=None
    scored=experiment.score_candidate(c)
    assert scored['matched_scores']['combined'] is not None
    views=experiment.identity_profile_views([c],[scored])
    for name in views:
        assert views[name][0]['identity_geometry_basis']=='native_path'
        assert views[name][0]['matched_scores'][experiment.PROFILE_METHOD] is None
        assert views[name][0]['points'][1]['matched_scores'][experiment.PROFILE_METHOD] is not None


def test_true_o1_raster_step_stripe_and_polarity_controls():
    step=np.full((200,200),180,dtype=np.uint8);step[100:]=80
    stripe=np.full_like(step,180);stripe[100:106]=80
    results=[]
    for raster in (step,stripe,255-step):
        witness=measure(raster)
        scale=asdict(witness.candidates[0].sectors[2].centers[0].scales[0])
        results.append(experiment.profile_scale(scale))
        assert witness.candidates[0].decision=='NOT_EVALUATED'
    assert results[0]['score'] > 0 > results[1]['score']
    assert results[2]['score'] == pytest.approx(results[0]['score'])


def test_real_packet_cli_reference_preservation_and_identity_only(inputs,tmp_path):
    old=tmp_path/'old'; prior=experiment.run([inputs],old)
    reference=old/'experiment.json'
    before={p:p.read_bytes() for root in (inputs.parent,old) for p in root.iterdir() if p.is_file()}
    out=tmp_path/'새 프로필 실험';cwd=tmp_path/'외부 cwd';cwd.mkdir()
    result=subprocess.run([sys.executable,str(Path(experiment.__file__).resolve()),'--labels',str(inputs),
        '--output',str(out),'--identity-profile','--reference',str(reference)],cwd=cwd,
        stdin=subprocess.DEVNULL,capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stderr
    r=o2.read_json(out/'experiment.json')
    assert r['schema_version']==experiment.PROFILE_SCHEMA
    assert r['scores']==prior['scores'] and r['evaluation']==prior['evaluation']
    assert r['reference']['inputs_scores_evaluation_equal']
    assert not r['production_decisions_emitted'] and not r['auto_acceptance']
    for c in r['identity_profile']:
        for view in ('common_support','profile_supported'):
            assert c[view]['evaluation']['path_ordering']=={}
    receipt=o2.read_json(out/'complete.json')
    assert receipt['schema_version']==experiment.PROFILE_SCHEMA
    assert all(o2.sha256_file(out/n)==h for n,h in receipt['outputs'].items())
    assert all(p.read_bytes()==data for p,data in before.items())
    text=(out/'summary.md').read_text(encoding='utf-8')
    assert 'Candidate identity only' in text and 'View: profile_supported' in text
    assert 'A structural step may be indistinguishable' in text
    with pytest.raises(ValueError,match='already exists'):
        experiment.run([inputs],out,identity_profile=True,reference=reference)


def test_profile_scores_do_not_depend_on_identity_metadata_or_annotations():
    c=enrich(candidate(equal=True));scored=experiment.score_candidate(c)
    first=experiment.identity_profile_views([c],[scored])
    c.update(source='different',rejected=True,canonical_y=987,selected=True)
    # Exact geometry/measurement remains the same; no metadata is a predictor input.
    after=experiment.identity_profile_views([c],[experiment.score_candidate(c)])
    for name in first:
        assert first[name][0]['matched_scores']==after[name][0]['matched_scores']
    a=ablation_case([scored],('interface',));b=ablation_case([scored],('non_interface',))
    ra=experiment.evaluate_identity_profile(a,[c],[scored])
    rb=experiment.evaluate_identity_profile(b,[c],[scored])
    for name in first:assert ra[name]['scores']==rb[name]['scores']


def test_modes_reference_and_input_drift_rejected(inputs,tmp_path):
    with pytest.raises(ValueError,match='mutually exclusive'):
        experiment.run([inputs],tmp_path/'out',identity_profile=True,locality_ablation=True)
    with pytest.raises(ValueError,match='supplied together'):
        experiment.run([inputs],tmp_path/'out',identity_profile=True)
    old=tmp_path/'old';experiment.run([inputs],old)
    labels=o2.read_json(inputs);labels['cases'][0]['review_note']='changed after reference'
    inputs.write_text(json.dumps(labels),encoding='utf-8')
    with pytest.raises(ValueError,match='reference inputs differs'):
        experiment.run([inputs],tmp_path/'out',identity_profile=True,reference=old/'experiment.json')
    assert not (tmp_path/'out').exists()
