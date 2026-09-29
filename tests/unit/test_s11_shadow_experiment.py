"""Synthetic contracts for an exploratory ranking tool, not classifier accuracy."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_review_records as records
from tests.diagnostics import s11_shadow_experiment as experiment
from tests.unit.test_interface_shadow_evaluation import _dataset


def scale(delta=.2, norm=2, align=.8, far=.01, width=8):
    return {"band_width_px": width, "signed_delta": delta, "normalized_delta": norm,
            "bands": [{"name": n, "available": True, "gray_mean": g, "normal_alignment": align}
                      for n, g in (("near_above", .2), ("near_below", .4), ("far_above", .2), ("far_below", .2+far))]}


def candidate(native=True, equal=False):
    y = 10 if equal else 12
    centers = [{"role": "native_path", "source_y": 10, "scales": [scale()]}] if native else []
    if not equal or not native:
        centers.append({"role": "candidate_center", "source_y": y, "scales": [scale(align=.2)]})
    return {"candidate_input_index": 9, "source": "synthetic", "rejected": False,
            "sectors": [{"sector": 0, "source_x_range": [0, 20], "path_source_y": 10 if native else None,
                         "candidate_source_y": y, "centers": centers}]}


@pytest.fixture
def inputs(tmp_path):
    root = tmp_path / '원본 reviews'
    root.mkdir()
    labels, _ = _dataset(root)
    old = root / 'labels.json'
    o2.write_new(old, labels)
    new = root / 'labels-v2.json'
    records.migrate(old, new, o2.fingerprint_json(labels), 'synthetic-reviewer', 'No physical judgment inferred.')
    return new


def test_fixed_hypothesis_penalizes_broad_context_without_polarity_rule():
    sharp = experiment.scale_scores(scale())
    broad = experiment.scale_scores(scale(far=.7))
    flipped = experiment.scale_scores(scale(delta=-.2, norm=-2))
    assert sharp['scores'] == flipped['scores']
    assert sharp['scores']['contrast_only'] == broad['scores']['contrast_only']
    assert sharp['scores']['combined'] > broad['scores']['combined']
    assert sharp['scores']['combined'] == pytest.approx((2/3*.8*(.2/(.2+.01+1/255)))**(1/3))


@pytest.mark.parametrize('state', ['missing', 'null', 'zero', 'unavailable'])
def test_measurement_states_are_not_silently_zero(state):
    s = scale()
    if state == 'missing': del s['normalized_delta']
    if state == 'null': s['normalized_delta'] = None
    if state == 'zero': s['normalized_delta'] = 0
    if state == 'unavailable': s['bands'][0]['available'] = False
    r = experiment.scale_scores(s)
    assert r['scores']['contrast_only'] == (0 if state == 'zero' else None)
    if state in ('missing', 'null'):
        assert r['field_status']['normalized_delta'] == state
    if state == 'zero': assert r['scores']['combined'] == 0


@pytest.mark.parametrize('v', [True, float('nan'), float('inf'), '0.2'])
def test_invalid_numbers_fail_closed(v):
    s = scale(); s['normalized_delta'] = v
    with pytest.raises(ValueError, match='invalid measurement'):
        experiment.scale_scores(s)


def test_alias_is_measurement_reuse_not_label_inheritance():
    c = candidate(equal=True)
    result = experiment.score_candidate(c)
    assert len(result['points']) == 2
    assert result['points'][1]['exact_center_alias']
    a = {'candidate_input_index': 9, 'identity': 'interface', 'path_reviews': [
        {'geometry_basis': 'native_path', 'source_x_range': [0,20], 'source_y': 10, 'judgment': 'near_interface'}]}
    r = experiment.evaluate_case({'case_id':'c','partition':'regression','visibility':'visible','candidates':[a]}, [result])
    assert r['path_ordering']['candidate_center']['identity_judgment_counts'] == {'interface/unreviewed': 1}


def test_geometry_join_is_exact_and_native_missing_does_not_fall_back():
    c = candidate()
    c['sectors'][0]['centers'][0]['scales'][0]['bands'][2]['available'] = False
    r = experiment.score_candidate(c)
    assert r['scores']['combined'] is None
    assert r['points'][1]['scores']['combined'] is not None
    assert r['identity_geometry_basis'] == 'native_path'
    assert r['matched_scores'] == {m:None for m in experiment.METHODS}
    assert r['scores']['contrast_only'] is not None  # available baseline retained
    c['sectors'][0]['centers'][0]['source_y'] += 1
    with pytest.raises(ValueError, match='Y mismatch'):
        experiment.score_candidate(c)


def test_center_only_and_metadata_blind_scoring():
    c = candidate(native=False)
    a = experiment.score_candidate(c)
    c.update(source='another-family', rejected=True, candidate_input_index=88, canonical_y=555,
             glass_id='unseen', rank=100, selected=True)
    b = experiment.score_candidate(c)
    assert a['scores'] == b['scores']
    assert b['identity_geometry_basis'] == 'candidate_center'


def test_ablation_uses_identical_scales_not_extra_baseline_support():
    c = candidate(equal=True)
    bad = scale(norm=1000, width=16)
    bad['bands'][2]['available'] = False
    c['sectors'][0]['centers'][0]['scales'].append(bad)
    r = experiment.score_candidate(c)
    assert r['scores']['contrast_only'] > r['matched_scores']['contrast_only']
    assert r['points'][0]['common_scale_count'] == 1
    assert r['matched_scores']['contrast_only'] == pytest.approx(2/3)


def test_duplicate_geometry_and_scale_are_rejected():
    c = candidate(); c['sectors'] *= 2
    with pytest.raises(ValueError, match='duplicate sector'):
        experiment.score_candidate(c)
    c = candidate(); c['sectors'][0]['centers'][0]['scales'] *= 2
    with pytest.raises(ValueError, match='duplicate scale'):
        experiment.score_candidate(c)


def test_pairs_ties_missing_improvements_and_regressions():
    pos = [{'key': 1, 'scores': dict(zip(experiment.METHODS, (.1,.8,.7)))}]
    neg = [{'key': 2, 'scores': dict(zip(experiment.METHODS, (.9,.7,.6)))},
           {'key': 3, 'scores': dict(zip(experiment.METHODS, (.1,.7,.8)))},
           {'key': 4, 'scores': dict(zip(experiment.METHODS, (.2,.8,None)))}]
    r = experiment.pair_results(pos,neg)
    assert r['pair_count'] == 3 and r['common_scorable_pair_count'] == 2
    assert r['counts']['combined'] == {'correct':1,'reversed':1,'unscorable':1}
    assert r['combined_vs_baseline_on_common_pairs']['contrast_only'] == {'improved':1,'regressed':0}
    assert r['combined_vs_baseline_on_common_pairs']['alignment_only'] == {'improved':0,'regressed':1}


def test_negative_identity_is_not_interface_location_control():
    cs = [experiment.score_candidate(candidate(equal=True))]
    b = copy.deepcopy(cs[0]); b['candidate_input_index'] = 10
    labels = [{'candidate_input_index':i, 'identity':identity, 'path_reviews':[
        {'geometry_basis':'native_path','source_x_range':[0,20],'source_y':10,'judgment':judgment}]}
        for i,identity,judgment in [(9,'interface','near_interface'),(10,'non_interface','off_interface')]]
    r = experiment.evaluate_case({'case_id':'c','partition':'regression','visibility':'visible','candidates':labels}, cs+[b])
    assert r['path_ordering']['native_path']['interface_location']['pair_count'] == 0
    assert r['path_ordering']['native_path']['identity_negative_control_same_x']['pair_count'] == 1
    assert len(r['candidate_ranking']['combined']['top_ranked']) == 2  # do not break ties by index


def test_real_packet_entry_point_preservation_receipt_and_no_overwrite(inputs,tmp_path):
    before = {p:p.read_bytes() for p in inputs.parent.iterdir() if p.is_file()}
    out = tmp_path/'results'
    r = experiment.run([inputs],out)
    assert r['status'] == 'EXPLORATORY_UNCALIBRATED'
    assert not r['production_decisions_emitted'] and not r['auto_acceptance']
    assert r['artifact']['spec']['fitted'] is False
    assert r['evaluation'][0]['identity_ordering']['pair_count'] == 2
    assert r['evaluation'][1]['identity_ordering']['pair_count'] == 0
    receipt = o2.read_json(out/'complete.json')
    assert all(o2.sha256_file(out/n)==h for n,h in receipt['outputs'].items())
    assert all(p.read_bytes()==data for p,data in before.items())
    with pytest.raises(ValueError,match='already exists'):
        experiment.run([inputs],out)
    with pytest.raises(ValueError,match='unique'):
        experiment.run([inputs,inputs],tmp_path/'other')


def test_cli_from_non_repo_cwd_and_nonascii_paths(inputs,tmp_path):
    cwd=tmp_path/'별도 cwd';cwd.mkdir()
    out=tmp_path/'결과 파일'
    proc=subprocess.run([sys.executable,str(Path(experiment.__file__).resolve()),'--labels',str(inputs),'--output',str(out)],
                        cwd=cwd,stdin=subprocess.DEVNULL,capture_output=True,text=True,encoding='utf-8')
    assert proc.returncode==0, proc.stderr
    assert (out/'complete.json').exists()


def test_labels_never_change_scores(inputs,tmp_path):
    first=experiment.run([inputs],tmp_path/'first')
    labels=o2.read_json(inputs)
    for c in labels['cases']:
        for a in c['candidates']: a['identity']='unreviewed'
    inputs.write_text(json.dumps(labels),encoding='utf-8')
    second=experiment.run([inputs],tmp_path/'second')
    assert first['scores']==second['scores']
    assert second['evaluation'][0]['identity_ordering']['pair_count']==0
    assert first['artifact']['sha256']==second['artifact']['sha256']


def test_holdout_and_corrupt_inputs_rejected(inputs,tmp_path):
    labels=o2.read_json(inputs)
    for c in labels['cases']:
        c['previously_reviewed']=False;c['partition']='holdout'
    inputs.write_text(json.dumps(labels),encoding='utf-8')
    with pytest.raises(ValueError,match='only regression'):
        experiment.run([inputs],tmp_path/'out')
    assert not (tmp_path/'out').exists()
    labels['cases'][0]['candidates'][0]['witness_sha256']='0'*64
    inputs.write_text(json.dumps(labels),encoding='utf-8')
    with pytest.raises(ValueError,match='candidate hash'):
        experiment.run([inputs],tmp_path/'out')


def test_mutation_during_scoring_does_not_publish_success(inputs,tmp_path,monkeypatch):
    original=experiment.score_candidate
    def changed(c):
        inputs.write_bytes(inputs.read_bytes()+b' ')
        return original(c)
    monkeypatch.setattr(experiment,'score_candidate',changed)
    with pytest.raises(ValueError,match='input changed'):
        experiment.run([inputs],tmp_path/'out')
    assert not (tmp_path/'out').exists()


def test_all_negative_and_unreviewed_top_are_visible_not_success():
    cs = [experiment.score_candidate(candidate())]
    for identity in ('non_interface', 'unreviewed'):
        case = {'case_id':'negative','partition':'regression','visibility':'not_visible',
                'candidates':[{'candidate_input_index':9,'identity':identity,'path_reviews':[]}]}
        r = experiment.evaluate_case(case,cs)
        assert r['identity_ordering']['pair_count']==0
        assert r['candidate_ranking']['combined']['top_ranked'][0]['identity']==identity
        assert r['path_ordering']['native_path']['interface_location']['pair_count']==0


def test_same_x_comparison_does_not_pair_different_intervals():
    p={'key':1,'source_x_range':[0,20],'scores':{m:.9 for m in experiment.METHODS}}
    n={'key':2,'source_x_range':[20,40],'scores':{m:.1 for m in experiment.METHODS}}
    assert experiment.pair_results([p],[n])['pair_count']==1
    assert experiment.pair_results([p],[n],same_x=True)['pair_count']==0


def test_identical_inputs_have_deterministic_scores_and_reports(inputs,tmp_path):
    assert experiment.run([inputs],tmp_path/'one') == experiment.run([inputs],tmp_path/'two')


def test_duplicate_frames_across_distinct_label_files_rejected(inputs,tmp_path):
    second=inputs.parent/'duplicate.json'
    second.write_bytes(inputs.read_bytes())
    with pytest.raises(ValueError,match='duplicate'):
        experiment.run([inputs,second],tmp_path/'out')
    assert not (tmp_path/'out').exists()


def test_multi_review_real_loader_runs_without_combine_or_data_mutation(inputs,tmp_path):
    root=tmp_path/'second review';root.mkdir()
    old,_=_dataset(root)
    packet=o2.read_json(root/'packet.json')
    for f in packet['frames']:
        f['case_id']='second-'+f['case_id']
        f['run_id']='second-run'
    (root/'packet.json').write_text(json.dumps(packet),encoding='utf-8')
    sha=o2.fingerprint_json(packet)
    for c in old['cases']:
        c['case_id']='second-'+c['case_id'];c['physical_case_id']=c['case_id'];c['packet_sha256']=sha
    old['packets'][0]['sha256']=sha
    source=root/'labels.json';o2.write_new(source,old)
    dest=root/'labels-v2.json'
    records.migrate(source,dest,o2.fingerprint_json(old),'reviewer','format only')
    report=experiment.run([inputs,dest],tmp_path/'out')
    assert len(report['inputs'])==2 and len(report['scores'])==4
    assert set(c['case_id'] for c in report['evaluation'])=={'a','empty','second-a','second-empty'}


def test_native_packet_cli_evaluates_explicit_paths_without_center_label_inheritance(inputs,tmp_path):
    labels=o2.read_json(inputs)
    packet_path=inputs.parent/labels['packets'][0]['path']
    packet=o2.read_json(packet_path)
    frame=packet['frames'][0]
    a=labels['cases'][0]['candidates'][0]
    c=frame['witness']['candidates'][0]
    for sec in c['sectors']:
        sec['path_source_y']=sec['candidate_source_y']
        sec['centers'][0]['role']='native_path'
    c['contour']['geometry_source']='native_generator_path'
    a['witness_sha256']=o2.fingerprint_json(c)
    a['path_reviews']=[{'geometry_basis':'native_path','source_x_range':s['source_x_range'],
                       'source_y':s['path_source_y'],'judgment':'near_interface',
                       'review':{'reviewer':'synthetic','basis':'direct_human_review',
                                 'note':'Synthetic test label only.', 'at':None}}
                      for s in c['sectors']]
    packet_path.write_text(json.dumps(packet),encoding='utf-8')
    sha=o2.fingerprint_json(packet)
    labels['packets'][0]['sha256']=sha
    for case in labels['cases']: case['packet_sha256']=sha
    inputs.write_text(json.dumps(labels),encoding='utf-8')
    out=tmp_path/'native output'
    proc=subprocess.run([sys.executable,str(Path(experiment.__file__).resolve()),'--labels',str(inputs),'--output',str(out)],
                        cwd=tmp_path,stdin=subprocess.DEVNULL,capture_output=True,text=True,encoding='utf-8')
    assert proc.returncode==0,proc.stderr
    r=o2.read_json(out/'experiment.json')['evaluation'][0]['path_ordering']
    assert r['native_path']['identity_judgment_counts']['interface/near_interface']==len(c['sectors'])
    assert not any('near_interface' in k for k in r['candidate_center']['identity_judgment_counts'])


def test_existing_label_writer_lock_is_respected(inputs,tmp_path):
    inputs.with_name(inputs.name+'.lock').write_text('writer',encoding='utf-8')
    with pytest.raises(ValueError,match='writer lock'):
        experiment.run([inputs],tmp_path/'out')
    assert not (tmp_path/'out').exists()


def ablation_case(scored, identities=('interface', 'interface')):
    return {'case_id':'synthetic', 'partition':'regression', 'visibility':'visible',
            'candidates':[{'candidate_input_index': c['candidate_input_index'], 'identity': identity,
                           'path_reviews':[{'geometry_basis':'native_path', 'source_x_range':[0,20],
                                            'source_y':10, 'judgment': 'near_interface' if i == 0 else 'off_interface'}]}
                          for i,(c,identity) in enumerate(zip(scored,identities))]}


def scored_terms(index, contrasts, localities):
    """Controlled scorer outputs; independent median oracle for aggregation tests."""
    from statistics import median
    c = experiment.score_candidate(candidate(equal=True))
    c['candidate_input_index'] = index
    for p in c['points']:
        p['scales'] = [{'band_width_px': i+1, 'scores':dict(zip(experiment.METHODS, (v, 1, (v*l)**(1/3))))}
                       for i,(v,l) in enumerate(zip(contrasts,localities))]
        p['matched_scores'] = {m:median(s['scores'][m] for s in p['scales']) for m in experiment.METHODS}
        p['common_scale_count'] = len(contrasts)
    c['matched_scores'] = c['points'][0]['matched_scores'].copy()
    return c


def test_locality_control_holds_exponent_and_median_not_scale_majority():
    near = scored_terms(1, [.8,.5,.2], [.9,.01,.9])
    off = scored_terms(2, [.7,.4,.1], [.7,.7,.7])
    original = copy.deepcopy([near,off])
    r = experiment.evaluate_locality_ablation(ablation_case(original), original)
    task = r['common_support']['evaluation']['path_ordering']['native_path']['interface_location_same_x']
    assert task['counts']['combined'] == {'reversed':1}
    assert task['counts']['without_locality'] == {'correct':1}
    assert task['without_locality_vs_baseline_on_common_pairs']['combined'] == {'improved':1,'regressed':0}
    p = r['common_support']['scores'][0]['points'][0]
    assert p['matched_scores']['without_locality'] == pytest.approx(.5**(1/3))
    assert p['matched_scores']['without_locality'] != pytest.approx(.5**.5)
    assert original == [near,off]
    assert r['support_transition']['native_path/interface_location']['counts'] == {'retained_same_order':1}


def test_locality_removal_can_regress_and_is_reported():
    near = scored_terms(1, [.3], [.9])
    off = scored_terms(2, [.9], [.1])
    r = experiment.evaluate_locality_ablation(ablation_case([near,off]), [near,off])
    task = r['common_support']['evaluation']['path_ordering']['native_path']['interface_location']
    assert task['without_locality_vs_baseline_on_common_pairs']['combined'] == {'improved':0,'regressed':1}


def test_missing_far_band_expands_coverage_without_common_support_success():
    a = candidate(equal=True)
    b = copy.deepcopy(a); b['candidate_input_index'] = 10
    b['sectors'][0]['centers'][0]['scales'][0]['bands'][2]['gray_mean'] = None
    scored = [experiment.score_candidate(c) for c in (a,b)]
    r = experiment.evaluate_locality_ablation(ablation_case(scored), scored)
    common = r['common_support']['scores'][1]
    expanded = r['ca_supported']['scores'][1]
    assert common['matched_scores']['without_locality'] is None
    assert common['points'][0]['common_scale_count'] == 0
    assert expanded['points'][0]['common_scale_count'] == 1
    assert expanded['matched_scores']['without_locality'] is not None
    task = r['common_support']['evaluation']['path_ordering']['native_path']['interface_location']
    assert task['without_locality_vs_baseline_on_common_pairs']['combined'] == {'improved':0,'regressed':0}
    change = r['support_transition']['native_path/interface_location']
    assert change['counts'] == {'newly_scorable':1}
    assert change['newly_scorable_outcomes'] == {'tie':1}  # new coverage is not a win
    assert 'combined' not in r['ca_supported']['evaluation']['candidate_ranking']


def test_ca_support_still_needs_both_near_features_and_preserves_zero():
    for state in ('missing_alignment', 'zero_contrast'):
        c = candidate(equal=True)
        s = c['sectors'][0]['centers'][0]['scales'][0]
        if state == 'missing_alignment': s['bands'][1]['normal_alignment'] = None
        else: s['normalized_delta'] = 0
        scored = experiment.score_candidate(c)
        r = experiment.ablation_scores([scored],common_support=False)[0]
        assert r['matched_scores']['without_locality'] == (None if state == 'missing_alignment' else 0)
        assert r['points'][0]['common_scale_count'] == (0 if state == 'missing_alignment' else 1)


def test_extra_scales_can_change_retained_pair_order_without_new_pair():
    a = candidate(equal=True)
    good = a['sectors'][0]['centers'][0]['scales'][0]
    good['normalized_delta'] = 20
    for width in (16,24):
        extra = scale(norm=.01,width=width)
        extra['bands'][2]['available'] = False
        a['sectors'][0]['centers'][0]['scales'].append(extra)
    b = candidate(equal=True);b['candidate_input_index'] = 10
    scored = [experiment.score_candidate(c) for c in (a,b)]
    r = experiment.evaluate_locality_ablation(ablation_case(scored),scored)
    change = r['support_transition']['native_path/interface_location']
    assert change['counts'] == {'retained_changed_order':1}
    assert change['pairs'][0]['common_outcome'] == 'correct'
    assert change['pairs'][0]['ca_supported_outcome'] == 'reversed'
    assert change['newly_scorable_outcomes'] == {}


def test_ablation_alias_and_identity_control_remain_separate():
    a,b = scored_terms(1,[.8],[.9]), scored_terms(2,[.2],[.9])
    r = experiment.evaluate_locality_ablation(ablation_case([a,b],('interface','non_interface')),[a,b])
    for view in ('common_support','ca_supported'):
        paths = r[view]['evaluation']['path_ordering']
        assert paths['native_path']['interface_location']['pair_count'] == 0
        assert paths['native_path']['identity_negative_control_same_x']['pair_count'] == 1
        assert paths['candidate_center']['identity_judgment_counts'] == {'interface/unreviewed':1,'non_interface/unreviewed':1}


def test_ablation_real_cli_reference_match_receipt_and_immutable_inputs(inputs,tmp_path):
    old = tmp_path/'v1 preserved'
    prior = experiment.run([inputs],old)
    reference = old/'experiment.json'
    before = {p:p.read_bytes() for root in (inputs.parent,old) for p in root.iterdir() if p.is_file()}
    output = tmp_path/'새 대조 결과'
    cwd = tmp_path/'다른 cwd';cwd.mkdir()
    cmd = [sys.executable,str(Path(experiment.__file__).resolve()),'--labels',str(inputs),
           '--output',str(output),'--locality-ablation','--reference',str(reference)]
    proc = subprocess.run(cmd,cwd=cwd,stdin=subprocess.DEVNULL,capture_output=True,text=True,encoding='utf-8')
    assert proc.returncode == 0, proc.stderr
    r = o2.read_json(output/'experiment.json')
    assert r['schema_version'] == experiment.ABLATION_SCHEMA
    assert r['scores'] == prior['scores'] and r['evaluation'] == prior['evaluation']
    assert r['reference']['inputs_scores_evaluation_equal']
    assert r['artifact']['sha256'] != prior['artifact']['sha256']
    assert len(r['input_preservation']) == len(prior['input_preservation'])+1
    receipt = o2.read_json(output/'complete.json')
    assert receipt['schema_version'] == experiment.ABLATION_SCHEMA
    assert all(o2.sha256_file(output/n) == h for n,h in receipt['outputs'].items())
    assert all(p.read_bytes() == data for p,data in before.items())
    summary = (output/'summary.md').read_text(encoding='utf-8')
    assert 'View: common_support' in summary and 'View: ca_supported' in summary
    assert 'without_locality' in summary and 'newly scorable' in summary
    with pytest.raises(ValueError,match='already exists'):
        experiment.run([inputs],output,locality_ablation=True,reference=reference)


@pytest.mark.parametrize('field',['scores','evaluation','inputs','artifact'])
def test_ablation_rejects_reference_drift_before_creating_output(inputs,tmp_path,field):
    old = tmp_path/'old';experiment.run([inputs],old)
    reference = old/'experiment.json';data=o2.read_json(reference)
    if field == 'artifact': data[field]['sha256']='0'*64
    else: data[field]=[]
    reference.write_text(json.dumps(data),encoding='utf-8')
    out = tmp_path/'new'
    with pytest.raises(ValueError,match='reference'):
        experiment.run([inputs],out,locality_ablation=True,reference=reference)
    assert not out.exists()


def test_ablation_requires_reference_and_keeps_mode_explicit(inputs,tmp_path):
    with pytest.raises(ValueError,match='supplied together'):
        experiment.run([inputs],tmp_path/'out',locality_ablation=True)
    with pytest.raises(ValueError,match='supplied together'):
        experiment.run([inputs],tmp_path/'out',reference=tmp_path/'fake')


def test_ablation_partial_native_never_falls_back_and_zero_pairs_are_not_success():
    c = candidate()
    c['sectors'][0]['centers'][0]['scales'][0]['bands'][0]['normal_alignment'] = None
    scored = experiment.score_candidate(c)
    result = experiment.evaluate_locality_ablation(ablation_case([scored],('non_interface',)),[scored])
    for name in ('common_support','ca_supported'):
        s = result[name]['scores'][0]
        assert s['identity_geometry_basis'] == 'native_path'
        assert s['matched_scores']['without_locality'] is None
        assert s['points'][1]['matched_scores']['without_locality'] is not None
        assert result[name]['evaluation']['identity_ordering']['pair_count'] == 0


def test_ca_support_expands_preferred_points_and_changes_candidate_median():
    c = candidate(equal=True)
    extra = copy.deepcopy(c['sectors'][0])
    extra['sector'] = 1; extra['source_x_range'] = [20,40]
    extra['centers'][0]['scales'][0]['normalized_delta'] = .01
    extra['centers'][0]['scales'][0]['bands'][2]['available'] = False
    c['sectors'].append(extra)
    original = experiment.score_candidate(c)
    common = experiment.ablation_scores([original],common_support=True)[0]
    expanded = experiment.ablation_scores([original],common_support=False)[0]
    assert common['point_count'] == expanded['point_count'] == 2
    assert common['common_point_count'] == 1 and expanded['common_point_count'] == 2
    a=(2/3*.8)**(1/3);b=(.01/1.01*.8)**(1/3)
    assert common['matched_scores']['without_locality'] == pytest.approx(a)
    assert expanded['matched_scores']['without_locality'] == pytest.approx((a+b)/2)
