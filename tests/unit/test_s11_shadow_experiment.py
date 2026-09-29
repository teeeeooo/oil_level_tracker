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
