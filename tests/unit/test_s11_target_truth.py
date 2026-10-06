"""Constructed truth-binding controls, not real-image identity validation."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_target_truth as target
from tests.unit.test_interface_shadow_evaluation import _dataset, _predictions, _frozen


def _inputs(tmp_path):
    physical, _ = _dataset(tmp_path)
    physical['schema_version'] = o2.LABEL_SCHEMA
    physical['review_history'] = [{'note': 'Original human/group attribution stays here.'}]
    for case in physical['cases']:
        for a in case['candidates']:
            old = a.pop('label')
            a.update(identity='interface' if old in o2.POSITIVES else 'non_interface',
                     artifact_tags=['reflection'] if old == 'reflection' else [], artifact_note='', path_reviews=[],
                     identity_review={'reviewer': 'fixture', 'basis': 'synthetic_construction', 'note': old})
    physical['cases'][1].update(visibility='not_visible', contour=[])
    o2.write_new(tmp_path/'labels.json', physical)
    groups = [dict(role='target', candidate_indices=[0], expected_count=1, review_basis='individual', note='Upper surface.'),
              dict(role='internal_interface', candidate_indices=[1], expected_count=1, review_basis='group', note='Real lower interface.'),
              dict(role='other_non_target', source_identity='non_interface', expected_count=1, review_basis='group', note='Human negative group.')]
    mapping = dict(schema_version=target.MAPPING_SCHEMA, target_spec_id=target.SPEC,
                   source_labels_sha256=o2.fingerprint_json(physical), attribution='Explicit synthetic target instruction.',
                   cases=[dict(case_id='a', frame_index=1, glass_id='g', candidate_count=3,
                               target_visibility='visible', note='Target visible.', groups=groups),
                          dict(case_id='empty', frame_index=2, glass_id='g', candidate_count=0,
                               target_visibility='not_visible', note='Full scene; no target.', groups=[])])
    o2.write_new(tmp_path/'mapping.json', mapping)
    return physical, mapping


def _bind(tmp_path):
    return target.bind(tmp_path/'labels.json', tmp_path/'mapping.json', tmp_path/'snapshot.json')


def test_projection_preserves_history_and_counts_internal_boundary_as_target_negative(tmp_path):
    physical, _ = _inputs(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    result = _bind(tmp_path)
    assert result['target_role_counts'] == dict(target=1, internal_interface=1, other_non_target=1)
    assert result['preserved_input_count'] == 3
    assert all((tmp_path/name).read_bytes() == value for name, value in before.items())
    stored = o2.read_json(tmp_path/'snapshot.json')
    assert stored['payload']['physical_labels'] == physical
    frozen, packets = o2.load_frozen(tmp_path/'snapshot.json')
    case = frozen['content']['cases'][0]
    assert [a['identity'] for a in case['candidates']] == ['interface', 'non_interface', 'non_interface']
    assert case['contour'] == []
    assert all(a['path_reviews'] == [] and a['entity_id'] is None and a['artifact_tags'] == [] for a in case['candidates'])
    assert frozen['content']['cases'][1]['visibility'] == 'not_visible'
    report = o2.evaluate(frozen, packets, _predictions(frozen, ('INTERFACE_SUPPORTED',)*3))
    assert report['schema_version'] == 's11-o2-target-shadow-report-v1'
    assert report['partitions']['regression']['wrong_non_interface_support_count'] == 2
    assert report['partitions']['regression']['verified_identity_precision'] == pytest.approx(1/3)
    assert report['target_truth']['physical_identity_counts'] == dict(interface=2, non_interface=1)
    # Old physical-label predictions cannot be silently reinterpreted against new truth.
    with pytest.raises(ValueError, match='different labels'):
        o2.evaluate(frozen, packets, _predictions(_frozen(physical)))
    assert o2.evaluate(frozen, packets)['status'] == 'NOT_EVALUATED'


@pytest.mark.parametrize('fault', ['hash', 'frame', 'glass', 'missing_case', 'missing_candidate', 'duplicate',
                                  'unknown', 'boolean', 'role_conflict', 'count', 'selector', 'extra_field', 'visibility'])
def test_bad_mappings_fail_without_output_or_source_changes(tmp_path, fault):
    _, mapping = _inputs(tmp_path)
    case = mapping['cases'][0]
    if fault == 'hash': mapping['source_labels_sha256'] = '0'*64
    if fault == 'frame': case['frame_index'] = 999
    if fault == 'glass': case['glass_id'] = 'different'
    if fault == 'missing_case': mapping['cases'].pop()
    if fault == 'missing_candidate': case['groups'].pop(1)
    if fault == 'duplicate': case['groups'][1]['candidate_indices'] = [0]
    if fault == 'unknown': case['groups'][1]['candidate_indices'] = [99]
    if fault == 'boolean': case['groups'][0]['candidate_indices'] = [False]
    if fault == 'role_conflict': case['groups'][0]['role'] = 'other_non_target'
    if fault == 'count': case['groups'][0]['expected_count'] = 2
    if fault == 'selector': case['groups'][2]['source_identity'] = 'interface'
    if fault == 'extra_field': case['groups'][0]['threshold'] = 10
    if fault == 'visibility': case['target_visibility'] = 'not_visible'
    (tmp_path/'mapping.json').write_text(json.dumps(mapping), encoding='utf-8')
    before = (tmp_path/'labels.json').read_bytes()
    with pytest.raises((ValueError, KeyError)):
        _bind(tmp_path)
    assert not (tmp_path/'snapshot.json').exists()
    assert (tmp_path/'labels.json').read_bytes() == before


def test_three_interfaces_unknown_names_and_unavailable_target_do_not_infer_a_winner(tmp_path):
    physical, mapping = _inputs(tmp_path)
    a = physical['cases'][0]['candidates'][2]
    a.update(identity='interface', artifact_tags=[])
    # Explicitly reviewed three-boundary target; no material names required.
    mapping['cases'][0]['groups'] = [dict(role='target', candidate_indices=[2], expected_count=1,
        review_basis='group', note='Uppermost actual boundary; material names unknown.'),
        dict(role='internal_interface', candidate_indices=[0, 1], expected_count=2, review_basis='group', note='Internal.')]
    mapping['source_labels_sha256'] = o2.fingerprint_json(physical)
    packets = o2.load_packets(physical, tmp_path)
    content, _ = target.project(physical, packets, mapping)
    assert [a['identity'] for a in content['cases'][0]['candidates']] == ['non_interface', 'non_interface', 'interface']
    # No target visible: all three can explicitly remain internal, no minimum-Y fallback.
    mapping['cases'][0]['target_visibility'] = 'uncertain'
    mapping['cases'][0]['groups'] = [dict(role='internal_interface', candidate_indices=[0,1,2], expected_count=3,
                                        review_basis='group', note='Upper target occluded; these are internal.')]
    content, _ = target.project(physical, packets, mapping)
    assert not any(a['identity'] == 'interface' for a in content['cases'][0]['candidates'])
    # A real interface may have unresolved target membership; don't force a negative.
    mapping['cases'][0]['groups'][0]['role'] = 'uncertain'
    content, _ = target.project(physical, packets, mapping)
    assert all(a['identity'] == 'uncertain' for a in content['cases'][0]['candidates'])


def test_tampered_projection_even_with_rehashed_envelope_rejected(tmp_path):
    _inputs(tmp_path); _bind(tmp_path)
    snapshot = o2.read_json(tmp_path/'snapshot.json')
    snapshot['payload']['evaluation_content']['cases'][0]['candidates'][1]['identity'] = 'interface'
    snapshot['artifact_sha256'] = o2.fingerprint_json(snapshot['payload'])
    snapshot['content_sha256'] = o2.fingerprint_json(snapshot['payload']['evaluation_content'])
    (tmp_path/'snapshot.json').write_text(json.dumps(snapshot), encoding='utf-8')
    with pytest.raises(ValueError, match='projection mismatch'):
        o2.load_frozen(tmp_path/'snapshot.json')


def test_cli_foreign_cwd_unicode_relocation_and_no_overwrite(tmp_path):
    data = tmp_path/'자료'; data.mkdir(); _inputs(data)
    runner = Path(o2.__file__).resolve()
    args = [sys.executable, str(runner), 'bind-target', '--labels', str(data/'labels.json'),
            '--mapping', str(data/'mapping.json'), '--output', str(data/'snapshot.json')]
    def run(argv):
        return subprocess.run(argv, cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8')
    first = run(args); assert first.returncode == 0, first.stderr
    second = run(args); assert second.returncode == 2 and 'exists' in second.stderr
    moved = tmp_path/'이동 자료'; shutil.move(str(data), moved)
    result = run([sys.executable, str(runner), 'evaluate', '--frozen', str(moved/'snapshot.json'), '--output', str(moved/'report.json')])
    assert result.returncode == 0, result.stderr
    report = o2.read_json(moved/'report.json')
    assert report['status'] == 'NOT_EVALUATED' and not report['auto_acceptance']
    assert report['target_truth']['local_scalar_entity_truth'] == 'NOT_TRANSFERRED'


def test_packet_drift_and_partition_leakage_still_rejected(tmp_path):
    physical, mapping = _inputs(tmp_path)
    physical['cases'][1].update(partition='holdout', previously_reviewed=False)
    mapping['source_labels_sha256'] = o2.fingerprint_json(physical)
    with pytest.raises(ValueError, match='leakage'):
        target.project(physical, o2.load_packets(physical, tmp_path), mapping)
    _bind(tmp_path)
    packet = o2.read_json(tmp_path/'packet.json'); packet['frames'][0]['frame_index'] = 33
    (tmp_path/'packet.json').write_text(json.dumps(packet), encoding='utf-8')
    with pytest.raises(ValueError, match='packet hash'):
        o2.load_frozen(tmp_path/'snapshot.json')


def test_source_change_during_binding_does_not_emit_snapshot(tmp_path, monkeypatch):
    _inputs(tmp_path)
    original = target.project
    def drift(*args):
        result = original(*args)
        with (tmp_path/'labels.json').open('a', encoding='utf-8') as handle:
            handle.write(' ')
        return result
    monkeypatch.setattr(target, 'project', drift)
    with pytest.raises(ValueError, match='source changed'):
        _bind(tmp_path)
    assert not (tmp_path/'snapshot.json').exists()


def test_v2_target_report_does_not_promote_physical_path_truth(tmp_path):
    physical, mapping = _inputs(tmp_path)
    packets = o2.load_packets(physical, tmp_path)
    candidate = next(iter(packets.values()))['a']['witness']['candidates'][0]
    physical['cases'][0]['candidates'][0]['path_reviews'] = [
        {**g, 'judgment': 'near_interface', 'review': dict(reviewer='fixture', note='Physical path.', basis='synthetic')}
        for g in o2.review_geometry(candidate)]
    mapping['source_labels_sha256'] = o2.fingerprint_json(physical)
    (tmp_path/'labels.json').write_text(json.dumps(physical), encoding='utf-8')
    (tmp_path/'mapping.json').write_text(json.dumps(mapping), encoding='utf-8')
    _bind(tmp_path)
    frozen, packets = o2.load_frozen(tmp_path/'snapshot.json')
    prediction = _predictions(frozen)
    prediction.update(schema_version=o2.TARGET_PREDICTION_SCHEMA, target_spec_id=o2.TARGET_SPEC,
                      operating_point_id='synthetic', fit_partitions=[], evaluation_regime='EXPLORATORY_UNCALIBRATED')
    for row in prediction['predictions']:
        c = next(iter(packets.values()))['a']['witness']['candidates'][row['candidate_input_index']]
        row.update(local_support=[{**g, 'decision':'NEAR_INTERFACE', 'availability':'available', 'reason':'scripted'}
                                  for g in o2.review_geometry(c)],
                   scalar=dict(decision='NOT_EVALUATED', availability='not_evaluated', reason='No scalar prediction.',
                               source_y=c['canonical_y'], policy_id='original_candidate_y_v1'))
    report = o2.evaluate(frozen, packets, prediction, allow_exploratory=True)
    assert report['schema_version'] == 's11-o2-target-shadow-report-v1'
    assert report['status'] == 'EXPLORATORY_UNCALIBRATED'
    assert report['target_truth']['local_scalar_entity_truth'] == 'NOT_TRANSFERRED'
    assert all(a['path_reviews'] == [] for a in frozen['content']['cases'][0]['candidates'])
    assert o2.read_json(tmp_path/'snapshot.json')['payload']['physical_labels']['cases'][0]['candidates'][0]['path_reviews']
