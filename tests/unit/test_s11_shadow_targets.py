"""W3 target semantics and real Windows-style entry paths, not model efficacy."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_shadow_experiment as experiment
from tests.diagnostics import s11_shadow_target_audit as audit
from tests.unit.test_s11_shadow_experiment import inputs
from tests.unit.test_interface_shadow_evaluation import prepared_o2_review


@pytest.fixture
def targets(inputs, tmp_path):
    frozen = o2.freeze(inputs, tmp_path/'frozen.json')
    packets = o2.load_packets(frozen, tmp_path)
    rows = []
    for case in frozen['content']['cases']:
        frame = packets[case['packet_sha256']][case['case_id']]
        for a, c in zip(case['candidates'], frame['witness']['candidates'], strict=True):
            rows.append({'case_id': case['case_id'], 'candidate_input_index': a['candidate_input_index'],
                         'witness_sha256': a['witness_sha256'], 'decision': 'UNRESOLVED', 'reason': 'scripted control',
                         'local_support': [{**g, 'decision': 'UNRESOLVED', 'availability': 'available',
                                            'reason': 'scripted control'} for g in o2.review_geometry(c)],
                         'scalar': {'decision': 'UNRESOLVED', 'availability': 'available', 'source_y': c['canonical_y'],
                                    'policy_id': 'original_candidate_y_v1', 'reason': 'scripted control'}})
    predictions = {'schema_version': o2.TARGET_PREDICTION_SCHEMA,
                   'target_spec_id': o2.TARGET_SPEC, 'operating_point_id': 'synthetic-scripted-v1',
                   'frozen_labels_sha256': frozen['content_sha256'], 'classifier_id': 'scripted-not-a-classifier',
                   'artifact_sha256': 'a'*64, 'fit_partitions': [], 'evaluation_regime': 'EXPLORATORY_UNCALIBRATED',
                   'operating_point_description': 'Synthetic decisions, no fit or calibrated operating point.',
                   'predictions': rows}
    return frozen, packets, predictions


def test_separate_targets_keep_missing_unknown_and_no_candidate_frames(targets):
    frozen, packets, predictions = targets
    first, second, third = predictions['predictions']
    first['decision'] = 'INTERFACE_SUPPORTED'
    first['scalar']['decision'] = 'USABLE'
    first['local_support'][0]['decision'] = 'OFF_INTERFACE'
    second['decision'] = 'NOT_EVALUATED'
    second['local_support'] = []
    del predictions['predictions'][2]
    result = o2.evaluate(frozen, packets, predictions, allow_exploratory=True)
    assert result['schema_version'] == 's11-o2-shadow-report-v3'
    assert result['prediction_identity']['operating_point_id'] == 'synthetic-scripted-v1'
    assert result['status'] == 'EXPLORATORY_UNCALIBRATED' and not result['auto_acceptance']
    metrics = result['targets']['regression']
    assert metrics['candidate_identity_confusion']['non_interface'] == {'MISSING_PREDICTION': 1}
    assert metrics['candidate_identity_confusion']['interface'] == {'INTERFACE_SUPPORTED': 1, 'NOT_EVALUATED': 1}
    assert metrics['visible_frame_count'] == 2  # includes the empty visible frame
    assert metrics['visible_frame_verified_identity_coverage'] == .5
    assert metrics['visible_frame_verified_scalar_coverage'] is None
    assert metrics['scalar']['unverified_usable_count'] == 1 and metrics['scalar']['mean_error_px'] is None
    assert metrics['scalar_rows'][0]['prediction_reason'] == 'scripted control'
    assert metrics['local_rows'][0]['prediction_availability'] == 'available'
    assert metrics['local_support']['candidate_center']['missing_prediction_count'] == 10
    assert metrics['local_support']['candidate_center']['unverified_decisive_count'] == 1
    assert result['partitions']['regression']['wrong_non_interface_support_count'] == 0


def test_local_confusion_is_exact_geometry_and_not_inherited_from_identity(targets):
    frozen, packets, p = targets
    row = p['predictions'][0]
    c = frozen['content']['cases'][0]['candidates'][0]
    c['path_reviews'] = [{k: row['local_support'][0][k] for k in ('geometry_basis','source_x_range','source_y')} |
                         {'judgment': 'near_interface', 'review': {'reviewer':'fixture','note':'constructed','basis':'synthetic'}}]
    frozen['content_sha256'] = o2.fingerprint_json(frozen['content'])
    p['frozen_labels_sha256'] = frozen['content_sha256']
    row['local_support'][0]['decision'] = 'OFF_INTERFACE'
    stats = o2.evaluate(frozen, packets, p, allow_exploratory=True)['targets']['regression']['local_support']['candidate_center']
    assert stats['confusion']['near_interface'] == {'OFF_INTERFACE': 1}
    assert stats['conditional_accuracy'] == 0 and stats['point_count'] == 15


@pytest.mark.parametrize('fault', ['opt_in', 'fit', 'partition', 'regime', 'v1_flag', 'v1_targets',
                                  'geometry', 'basis', 'duplicate', 'witness', 'scalar_y', 'scalar_bool',
                                  'policy', 'usable_without_identity', 'availability', 'interval', 'target_spec', 'operating_point'])
def test_reject_ambiguous_or_illegal_target_imports(targets, fault):
    frozen, packets, p = targets
    row = p['predictions'][0]
    opt_in = True
    if fault == 'target_spec': p['target_spec_id'] = 'unknown'
    if fault == 'operating_point': p['operating_point_id'] = ''
    if fault == 'opt_in': opt_in = False
    if fault == 'fit': p['fit_partitions'] = ['regression']
    if fault == 'partition': frozen['content']['cases'][0]['partition'] = 'holdout'
    if fault == 'regime': del p['evaluation_regime']
    if fault == 'v1_flag': p['schema_version'] = o2.PREDICTION_SCHEMA; p['fit_partitions'] = ['development']
    if fault == 'v1_targets':
        p['schema_version'] = o2.PREDICTION_SCHEMA; p['fit_partitions'] = ['development']; opt_in = False
    if fault == 'geometry': row['local_support'][0]['source_y'] += 1
    if fault == 'basis': row['local_support'][0]['geometry_basis'] = 'native_path'
    if fault == 'duplicate': row['local_support'].append(copy.deepcopy(row['local_support'][0]))
    if fault == 'witness': row['witness_sha256'] = '0'*64
    if fault == 'scalar_y': row['scalar']['source_y'] += 1
    if fault == 'scalar_bool': row['scalar']['source_y'] = True
    if fault == 'policy': row['scalar']['policy_id'] = 'median-path-y'
    if fault == 'usable_without_identity': row['scalar']['decision'] = 'USABLE'
    if fault == 'availability': row['local_support'][0]['availability'] = 'unavailable'
    if fault == 'interval': row['local_support'][0]['source_y_interval'] = [2, 1]
    with pytest.raises((ValueError, KeyError)):
        o2.evaluate(frozen, packets, p, allow_exploratory=opt_in)


def test_v1_compatibility_and_calibrated_v2_guard(targets):
    frozen, packets, p = targets
    p['evaluation_regime'] = 'CALIBRATED'
    with pytest.raises(ValueError, match='operating point'):
        o2.evaluate(frozen, packets, p)
    p['fit_partitions'] = ['development']
    result = o2.evaluate(frozen, packets, p)
    assert result['status'] == 'EVALUATED_NOT_QUALIFIED'
    old = copy.deepcopy(p); old['schema_version'] = o2.PREDICTION_SCHEMA
    for row in old['predictions']:
        del row['local_support']; del row['scalar']
    baseline = o2.evaluate(frozen, packets, old)
    assert baseline['schema_version'] == 's11-o2-shadow-report-v2'
    assert baseline['partitions'] == result['partitions']
    assert 'targets' not in baseline


def test_all_abstain_is_zero_coverage_not_success(targets):
    frozen, packets, p = targets
    result = o2.evaluate(frozen, packets, p, allow_exploratory=True)
    assert result['partitions']['regression']['abstention_count'] == 3
    assert result['targets']['regression']['visible_frame_verified_identity_coverage'] == 0
    assert result['targets']['regression']['scalar']['decision_counts'] == {'UNRESOLVED': 3}


def test_unobservable_is_distinct_from_missing_and_not_evaluated(targets):
    frozen, packets, p = targets
    p['predictions'][0]['decision'] = 'UNOBSERVABLE'
    point = p['predictions'][0]['local_support'][0]
    point.update(decision='UNOBSERVABLE', availability='unavailable')
    p['predictions'][0]['scalar'].update(decision='UNOBSERVABLE', availability='unavailable')
    p['predictions'][1]['local_support'] = []
    p['predictions'][1]['scalar'].update(decision='NOT_EVALUATED', availability='not_evaluated')
    del p['predictions'][2]
    result = o2.evaluate(frozen, packets, p, allow_exploratory=True)['targets']['regression']
    assert result['scalar']['decision_counts'] == {'UNOBSERVABLE': 1, 'NOT_EVALUATED': 1, 'MISSING_PREDICTION': 1}
    assert result['local_support']['candidate_center']['confusion']['unreviewed']['UNOBSERVABLE'] == 1
    assert result['visible_frame_verified_identity_coverage'] == 0


def test_context_missing_null_zero_and_availability_are_distinct(targets):
    frozen, packets, _ = targets
    case = frozen['content']['cases'][0]
    frame = packets[case['packet_sha256']][case['case_id']]
    band = frame['witness']['candidates'][0]['sectors'][0]['centers'][0]['scales'][0]['bands'][0]
    band['static_overlap'] = 0; band['static_available'] = True
    band['material_mean'] = None
    del band['glare_fraction']
    before = copy.deepcopy(frame)
    row = audit.context_rows(case, frame)[0]
    assert row['fields']['static_overlap'] == {'state': 'present', 'value': 0}
    assert row['fields']['material_mean']['state'] == 'null'
    assert row['fields']['glare_fraction']['state'] == 'missing'
    assert frame == before


def test_occlusion_context_remains_measurable_when_gray_band_is_unavailable(targets):
    frozen, packets, _ = targets
    case = frozen['content']['cases'][0]
    frame = packets[case['packet_sha256']][case['case_id']]
    rows = audit.context_rows(case, frame)[:1]
    rows[0]['availability']['available']['value'] = False
    rows[0]['fields']['glare_fraction'] = {'state': 'present', 'value': 1}
    summary = audit.context_summary(rows)[0]['fields']
    assert summary['glare_fraction']['usable_count'] == 1 and summary['glare_fraction']['median'] == 1
    assert summary['gray_mean']['usable_count'] == 0


def sequence_for(frame):
    raw = frame['witness']['candidates'][0]
    member = {'candidate_offset': raw['candidate_input_index'], 'source': raw['source'], 'y': raw['canonical_y'],
              'authority': 'ANCHOR_ELIGIBLE', 'tracklet_admitted': True, 'selected': True}
    return {'state': {'sequence_decision_witness': {
        'schema_version': 'r21-decision-witness-v1',
        'identity': {'layer': 'sequence', 'glass_id': frame['glass_id'], 'frame_index': frame['frame_index'],
                     'time_sec': frame['timestamp_sec']},
        'rows': [{'row_hypothesis_id': 'r', 'tracklet_id': 't', 'phase_admitted': True,
                  'publishable': True, 'members': [member]}],
        'phase': {'value':'OPEN'}, 'routes': {},
        'selection': {'selected_candidate': {k:member[k] for k in ('candidate_offset','source','y')}}}},
        'positions': {'raw_oil_y': raw['canonical_y']}}


@pytest.mark.parametrize('fault', ['frame','member_y','offset','duplicate','selection'])
def test_funnel_rejects_wrong_or_ambiguous_identity(targets, fault):
    frozen, packets, _ = targets
    case = frozen['content']['cases'][0]; frame = packets[case['packet_sha256']][case['case_id']]
    seq = sequence_for(frame); w = seq['state']['sequence_decision_witness']
    if fault == 'frame': w['identity']['frame_index'] += 1
    if fault == 'member_y': w['rows'][0]['members'][0]['y'] += 1
    if fault == 'offset': w['rows'][0]['members'][0]['candidate_offset'] = 999
    if fault == 'duplicate': w['rows'] *= 2
    if fault == 'selection': w['selection']['selected_candidate']['candidate_offset'] = 1
    with pytest.raises(ValueError): audit.recorded_funnel(frame, seq)


def test_funnel_reports_recorded_losses_without_guessing_earlier_gates(targets):
    frozen, packets, _ = targets
    case = frozen['content']['cases'][0]; frame = packets[case['packet_sha256']][case['case_id']]
    seq = sequence_for(frame)
    result = audit.recorded_funnel(frame, seq)
    assert result['candidates'][0]['first_known_loss'] is None
    assert result['candidates'][1]['first_known_loss'] == 'UNKNOWN_BEFORE_RETAINED_REFS'
    row = seq['state']['sequence_decision_witness']['rows'][0]
    row['phase_admitted'] = False; row['members'][0]['selected'] = False
    seq['state']['sequence_decision_witness']['selection']['selected_candidate'] = None
    assert audit.recorded_funnel(frame, seq)['candidates'][0]['first_known_loss'] == 'phase_not_admitted'
    assert audit.recorded_funnel(frame, None)['status'] == 'UNAVAILABLE'


def test_target_audit_cli_no_predictions_reference_and_receipts(inputs, tmp_path):
    old = tmp_path/'reference'; baseline = experiment.run([inputs], old)
    before = {p:p.read_bytes() for root in (inputs.parent, old) for p in root.iterdir() if p.is_file()}
    out = tmp_path/'새 감사 결과'; cwd = tmp_path/'외부 cwd'; cwd.mkdir()
    cmd = [sys.executable, str(Path(experiment.__file__).resolve()), '--labels', str(inputs),
           '--output', str(out), '--target-audit', '--reference', str(old/'experiment.json')]
    run = subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8')
    assert run.returncode == 0, run.stderr
    report = o2.read_json(out/'experiment.json')
    assert report['reference']['inputs_scores_evaluation_equal']
    assert report['scores'] == baseline['scores'] and report['evaluation'] == baseline['evaluation']
    assert not report['production_decisions_emitted']
    assert report['target_audit'][0]['target_accounting']['scalar']['decision_counts'] == {'MISSING_PREDICTION': 3}
    assert report['target_audit'][0]['recorded_funnel']['status'] == 'NOT_REQUESTED'
    receipt = o2.read_json(out/'complete.json')
    assert receipt['schema_version'] == audit.SCHEMA
    assert all(o2.sha256_file(out/n) == h for n,h in receipt['outputs'].items())
    assert all(p.read_bytes() == b for p,b in before.items())
    with pytest.raises(ValueError, match='already exists'):
        experiment.run([inputs], out, target_audit=True, reference=old/'experiment.json')


def test_real_bundle_audit_joins_exact_packet_and_preserves_inputs(prepared_o2_review, tmp_path):
    bundle, _, labels, _ = prepared_o2_review
    labels.update(label_owner='fixture', split_owner='fixture', split_rationale='regression control')
    labels['cases'][0].update(visibility='not_visible', reviewer='fixture', review_note='No physical classifier claim')
    path = tmp_path/'review'/'ready.json'; o2.write_new(path, labels)
    reference = tmp_path/'old'; experiment.run([path], reference)
    before = {p:p.read_bytes() for p in bundle.rglob('*') if p.is_file()}
    report = experiment.run([path], tmp_path/'audit', target_audit=True, reference=reference/'experiment.json', bundle=bundle)
    assert report['target_audit'][0]['recorded_funnel']['status'] == 'UNAVAILABLE'
    assert all(p.read_bytes() == b for p,b in before.items())
    assert len(report['input_preservation']) == 8  # labels, packet, reference, five bundle files


def test_real_indexed_record_includes_top_level_sequence(prepared_o2_review, tmp_path):
    bundle, _, labels, _ = prepared_o2_review
    packet = o2.read_json(tmp_path/'review'/'packet.json')
    frame = packet['frames'][0]
    trace = bundle/'debug'/'debug_trace.jsonl'
    index = bundle/'debug'/'debug_index.json'
    # Construct the serialized sequence fixture; never execute resolver predicates.
    payload = json.loads(trace.read_bytes())
    payload['sequence'] = sequence_for(frame)
    encoded = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    trace.write_bytes(encoded+b'\n')
    idx = o2.read_json(index)
    idx['records'][0].update(byte_offset=0, byte_length=len(encoded))
    index.write_text(json.dumps(idx), encoding='utf-8')
    snapshots = {}
    results = audit.load_recorded_sequences(bundle, [tmp_path/'review'/'labels.json'], snapshots)
    assert results[frame['case_id']]['status'] == 'RECORDED'
    assert results[frame['case_id']]['candidates'][0]['member']['selected']
    assert all(o2.sha256_file(p) == h for p,h in snapshots.items())


def test_target_audit_mutation_does_not_publish_receipt(inputs, tmp_path, monkeypatch):
    old = tmp_path/'old'; experiment.run([inputs], old)
    original = audit.audit_case
    def mutate(*args, **kwargs):
        inputs.write_bytes(inputs.read_bytes()+b' ')
        return original(*args, **kwargs)
    monkeypatch.setattr(audit, 'audit_case', mutate)
    with pytest.raises(ValueError, match='input changed'):
        experiment.run([inputs], tmp_path/'out', target_audit=True, reference=old/'experiment.json')
    assert not (tmp_path/'out'/'complete.json').exists()


def test_prediction_v2_cli_explicit_exploratory(targets, tmp_path):
    _, _, p = targets
    pred = tmp_path/'predictions.json'; o2.write_new(pred, p)
    out = tmp_path/'report.json'; cwd = tmp_path/'different cwd'; cwd.mkdir()
    result = subprocess.run([sys.executable, str(Path(o2.__file__).resolve()), 'evaluate',
        '--frozen', str(tmp_path/'frozen.json'), '--predictions', str(pred), '--exploratory', '--output', str(out)],
        cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert o2.read_json(out)['status'] == 'EXPLORATORY_UNCALIBRATED'
