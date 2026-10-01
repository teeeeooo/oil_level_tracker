"""Recorded context provenance and real entry controls; no classifier efficacy."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_shadow_experiment as experiment
from tests.diagnostics import s11_shadow_target_audit as audit
from tests.unit.test_interface_shadow_evaluation import prepared_o2_review


@pytest.fixture
def source():
    candidates = [dict(candidate_input_index=i, source='synthetic', kind='oil_air',
                       canonical_y=100+i, local_y=100+i, rejected=False) for i in (7, 2)]
    frame = dict(record_id='r', glass_id='g', frame_index=1, witness={'candidates': copy.deepcopy(candidates)})
    candidates[0]['features'] = {'artifact_likelihood': 0, 'glare_conflict': None}
    candidates[0]['penalties'] = {'artifact_likelihood': .3}
    candidates[1]['features'] = None
    recipe = {'glasses': [{'id': 'g', 'geometry': {'artifact_templates': []}}]}
    return frame, {'candidates': list(reversed(candidates))}, recipe


def test_exact_original_index_and_distinct_missing_null_zero(source):
    before = copy.deepcopy(source)
    result = audit.recorded_structure_context(*source)
    a, b = result['candidates']
    assert a['candidate_input_index'] == 7  # raw list is score-sorted differently
    assert a['features']['fields']['artifact_likelihood'] == {'state': 'present', 'value': 0}
    assert a['penalties']['fields']['artifact_likelihood']['value'] == .3
    assert a['features']['fields']['glare_conflict']['state'] == 'null'
    assert a['features']['fields']['static_prior_contribution']['state'] == 'missing'
    assert b['features']['state'] == 'null' and b['penalties']['state'] == 'missing'
    assert result['artifact_templates'] == {'state': 'present', 'value': [], 'count': 0}
    assert source == before


@pytest.mark.parametrize('fault', ['duplicate', 'missing', 'source', 'y', 'bool_index', 'rejected', 'glass', 'duplicate_glass'])
def test_reject_wrong_provenance(source, fault):
    frame, payload, recipe = source
    if fault == 'duplicate': payload['candidates'].append(copy.deepcopy(payload['candidates'][0]))
    if fault == 'missing': payload['candidates'].pop()
    if fault == 'source': payload['candidates'][0]['source'] = 'other'
    if fault == 'y': payload['candidates'][0]['canonical_y'] += 1
    if fault == 'bool_index': payload['candidates'][0]['candidate_input_index'] = False
    if fault == 'rejected': payload['candidates'][0]['rejected'] = 0
    if fault == 'glass': recipe['glasses'][0]['id'] = 'other'
    if fault == 'duplicate_glass': recipe['glasses'] *= 2
    with pytest.raises(ValueError): audit.recorded_structure_context(frame, payload, recipe)


@pytest.mark.parametrize('value', [False, True, float('nan'), float('inf'), '0.2'])
def test_invalid_numeric_evidence_is_not_defaulted(source, value):
    source[1]['candidates'][1]['features']['artifact_likelihood'] = value
    with pytest.raises(ValueError): audit.recorded_structure_context(*source)


@pytest.mark.parametrize('state', ['missing', 'null', 'registered', 'duplicate'])
def test_raw_recipe_template_inventory(source, state):
    geometry = source[2]['glasses'][0]['geometry']
    template = {'id': 't', 'kind': 'line', 'center_x': .5, 'center_y': .7,
                'width': .2, 'height': .01, 'angle_deg': 0, 'note': 'historical registration'}
    if state == 'missing': del geometry['artifact_templates']
    if state == 'null': geometry['artifact_templates'] = None
    if state in ('registered', 'duplicate'): geometry['artifact_templates'] = [template] * (2 if state == 'duplicate' else 1)
    if state == 'duplicate':
        with pytest.raises(ValueError): audit.recorded_structure_context(*source)
    else:
        inventory = audit.recorded_structure_context(*source)['artifact_templates']
        assert inventory['state'] == ('present' if state == 'registered' else state)
        assert inventory['count'] == (1 if state == 'registered' else None)
        if state == 'registered': assert inventory['value'] == [template]


@pytest.mark.parametrize('target,bundle', [(False, None), (True, None), (False, 'unused')])
def test_flag_requires_target_audit_and_original_bundle(tmp_path, target, bundle):
    with pytest.raises(ValueError, match='requires'):
        experiment.run([], tmp_path/'out', target_audit=target, structure_context=True,
                       bundle=bundle, reference='unused' if target else None)
    assert not (tmp_path/'out').exists()


def ready_reference(prepared, tmp_path):
    bundle, _, labels, _ = prepared
    labels.update(label_owner='fixture', split_owner='fixture', split_rationale='regression control')
    labels['cases'][0].update(visibility='not_visible', reviewer='fixture', review_note='synthetic control')
    path = tmp_path/'review'/'ready.json'; o2.write_new(path, labels)
    reference = tmp_path/'reference'; baseline = experiment.run([path], reference)
    return bundle, path, reference/'experiment.json', baseline


def test_real_cli_bundle_projection_parity_receipts_and_preservation(prepared_o2_review, tmp_path):
    bundle, path, ref, baseline = ready_reference(prepared_o2_review, tmp_path)
    before = {p: p.read_bytes() for root in (bundle, path.parent, ref.parent) for p in root.rglob('*') if p.is_file()}
    out = tmp_path/'구조 문맥'; cwd = tmp_path/'외부'; cwd.mkdir()
    cmd = [sys.executable, str(Path(experiment.__file__).resolve()), '--labels', str(path),
           '--target-audit', '--structure-context', '--bundle', str(bundle), '--reference', str(ref), '--output', str(out)]
    run = subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8')
    assert run.returncode == 0, run.stderr
    report = o2.read_json(out/'experiment.json')
    assert report['schema_version'] == audit.STRUCTURE_SCHEMA
    assert report['reference']['inputs_scores_evaluation_equal']
    for key in ('inputs', 'scores', 'evaluation'): assert report[key] == baseline[key]
    raw = json.loads((bundle/'debug'/'debug_trace.jsonl').read_text(encoding='utf-8'))
    context = report['target_audit'][0]['recorded_funnel']['structure_context']
    raw_by_index = {c['candidate_input_index']: c for c in raw['candidates']}
    assert context['candidates']
    for c in context['candidates']:
        for key in ('features', 'penalties'):
            for name, field in c[key]['fields'].items():
                if field['state'] == 'present': assert field['value'] == raw_by_index[c['candidate_input_index']][key][name]
    assert context['artifact_templates']['count'] == 0
    receipt = o2.read_json(out/'complete.json')
    assert receipt['schema_version'] == audit.STRUCTURE_SCHEMA and receipt['status'] == 'COMPLETE'
    assert all(o2.sha256_file(out/n) == h for n, h in receipt['outputs'].items())
    assert all(p.read_bytes() == b for p, b in before.items())
    assert all(r['before_sha256'] == r['after_sha256'] for r in report['input_preservation'])
    assert len(report['input_preservation']) == 8
    assert 'no new predictions' in (out/'summary.md').read_text(encoding='utf-8')
    assert report['field_disposition'] == 'FIELD FAIL' and not report['auto_acceptance']
    with pytest.raises(ValueError, match='already exists'):
        experiment.run([path], out, target_audit=True, structure_context=True, reference=ref, bundle=bundle)


def test_structure_projection_input_mutation_has_no_success_receipt(prepared_o2_review, tmp_path, monkeypatch):
    bundle, path, ref, _ = ready_reference(prepared_o2_review, tmp_path)
    original = audit.recorded_structure_context
    def mutate(*args):
        path.write_bytes(path.read_bytes()+b' ')
        return original(*args)
    monkeypatch.setattr(audit, 'recorded_structure_context', mutate)
    out = tmp_path/'failed'
    with pytest.raises(ValueError, match='input changed'):
        experiment.run([path], out, target_audit=True, structure_context=True, reference=ref, bundle=bundle)
    assert not (out/'complete.json').exists()
