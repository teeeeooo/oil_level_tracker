"""Human reply precision, exact binding and full-dependency controls."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image
import pytest

from tests.diagnostics import s11_native_role_qualification as q


def fixture_reply(tmp_path):
    root = tmp_path / "원본 space"
    root.mkdir()

    def pin(name):
        return dict(path=name, sha256=q.o2.sha256_file(root / name))

    def write(name, value):
        q.o2.write_new(root / name, value)
        return pin(name)

    rgb = np.arange(64*64*3, dtype=np.uint8).reshape(64, 64, 3)
    visible = np.ones((64, 64), bool)
    edges = np.zeros_like(visible)
    edges[20, 10:35] = True
    edges[30, 20:27] = True
    np.savez(root / "native.npz", original_roi=rgb[:, :, ::-1], effective_mask=visible.astype('uint8')*255,
             glare_mask=np.zeros((64, 64), 'uint8'), canny=edges.astype('uint8')*255)
    Image.fromarray(rgb).save(root / "RGB.png")
    (root / "display.bin").write_bytes(b"a frozen human display")
    geometry = dict(origin=[100, 200], shape=[64, 64], scale_xy=[1, 1], column=23)
    case = dict(id="native", frame=7, kind="public_compressor", raster="native.npz", rows=[20, 30], **geometry)
    plan = dict(cases=[case], pins={"native.npz": pin("native.npz")["sha256"]})
    manifest = dict(inputs=dict(foam_preflight=write("plan.json", plan)))
    rows, _ = q.g0.edge_bindings(edges, visible, 23, True)
    for row in rows:
        row['source_xy'] = [123., float(row['row']+200)]
    context = dict(id='native', frame=7, time_sec=0.23, time_kind='NOMINAL_ONLY', geometry=geometry,
                   geometry_sha256=q.o2.fingerprint_json(geometry), rows=rows,
                   original_case_ref=dict(index=0), source_recording=dict(path='recording', sha256='f'*64))
    baseline = dict(schema=q.g0.SCHEMA, manifest_sha256=q.o2.fingerprint_json(manifest),
                    contexts=[context], counts=dict(contexts=1, edges=2, new_physical_labels=0))
    subjects = []
    for sid, row, xs in zip(['N1', 'N2'], rows, [range(10, 35), range(20, 27)]):
        fragment = row['incident_fragments'][0]
        subjects.append(dict(id=sid, case_id='native', frame=7, view_id='original',
                             fixed_column_xy=row['source_xy'], native_fragment_id=fragment['fragment_id'],
                             source_path_xy=[[x+100, row['row']+200] for x in xs],
                             raster_path_sha256=fragment['path_sha256'], readout_subject_sha256=q.o2.fingerprint_json(fragment),
                             vertex_count=fragment['vertex_count'], junction_incident=fragment['junction_incident']))
    proposal = dict(schema='s11-native-fragment-role-review-proposal-v1',
                    g0_manifest=write('manifest.json', manifest), g0_readout=write('baseline.json', baseline),
                    subjects=subjects, views=[dict(id='original', source=pin('RGB.png'),
                                                   image_origin_xy=[100, 200], display_xyxy=[100, 200, 164, 264])])
    statements = ['N1 : 두 표면 해석 허용', 'N2 : Foam 내부 변화']
    role_sets = [['EXTERNAL_FOAM_UPPER', 'OSCILLATING_LIQUID_UPPER'], ['INTERNAL_FOAM_CHANGE']]
    reply = dict(schema=q.SCHEMA, proposal=write('proposal.json', proposal), display=pin('display.bin'),
                 response_ko='\n'.join(statements), answers=[dict(id=s['id'], subject_sha256=q.o2.fingerprint_json(s),
                 statement_ko=t, allowed_interpretations=roles, scope='DISPLAYED_FRAGMENT_ROLE_ONLY')
                 for s, t, roles in zip(subjects, statements, role_sets)])
    return root, reply, proposal


def test_exact_roles_are_sets_not_dense_labels_or_independent_observations(tmp_path):
    root, reply, _ = fixture_reply(tmp_path)
    original = copy.deepcopy(reply)
    result = q.qualify(root, reply)
    first, second = result['subjects']
    assert first['allowed_interpretations'] == ['EXTERNAL_FOAM_UPPER', 'OSCILLATING_LIQUID_UPPER']
    assert first['capability_target'] == 'EXTERNAL_SURFACE'
    assert second['capability_target'] == 'INTERNAL_FOAM_CHANGE'
    assert result['same_frame_dependency'][0]['shared_dependency_pixels'] > 0
    assert not result['same_frame_dependency'][0]['independent_split_allowed']
    assert result['baseline_counts']['new_physical_labels'] == 0  # historical count unchanged
    assert result['qualified_units'] == 2 and result['untouched_holdout_recordings'] == 0
    assert all(not r['dense_labels'] and r['side_material_labels'] is None and r['coordinate_tolerance'] is None
               and r['decision'] == 'NOT_EVALUATED' for r in result['subjects'])
    assert not result['training_executed'] and not result['production_changed']
    assert reply == original


@pytest.mark.parametrize('change,match', [
    ('stale_rgb', 'hash mismatch'), ('display', 'hash mismatch'), ('subject_hash', 'subject changed'),
    ('missing', 'each displayed'), ('duplicate', 'duplicate answer'), ('scope', 'precision'),
    ('role', 'role'), ('mixed_target', 'ambiguous surface'), ('statement', 'absent from response'),
    ('frame', 'frame mismatch'), ('path', 'geometry changed'), ('crop', 'outside displayed'),
])
def test_invalid_review_cannot_silently_change_scope(tmp_path, change, match):
    root, reply, proposal = fixture_reply(tmp_path)
    if change in ('stale_rgb', 'display'):
        (root / ('RGB.png' if change == 'stale_rgb' else 'display.bin')).write_bytes(b'changed')
    elif change == 'subject_hash':
        reply['answers'][0]['subject_sha256'] = '0'*64
    elif change == 'missing':
        reply['answers'].pop()
    elif change == 'duplicate':
        reply['answers'].append(copy.deepcopy(reply['answers'][0]))
    elif change == 'scope':
        reply['answers'][0]['scope'] = 'WHOLE_FRAME'
    elif change == 'role':
        reply['answers'][0]['allowed_interpretations'] = ['PURE_GAS']
    elif change == 'mixed_target':
        reply['answers'][0]['allowed_interpretations'].append('INTERNAL_FOAM_CHANGE')
    elif change == 'statement':
        reply['answers'][0]['statement_ko'] = 'not actually said'
    else:
        if change == 'frame': proposal['subjects'][0]['frame'] += 1
        if change == 'path': proposal['subjects'][0]['source_path_xy'][0][1] += 1
        if change == 'crop': proposal['views'][0]['display_xyxy'][0] = 120
        (root / 'proposal.json').write_text(json.dumps(proposal), encoding='utf-8')
        reply['proposal']['sha256'] = q.o2.sha256_file(root / 'proposal.json')
        reply['answers'][0]['subject_sha256'] = q.o2.fingerprint_json(proposal['subjects'][0])
    with pytest.raises(ValueError, match=match):
        q.qualify(root, reply)


def test_dependency_mask_is_checked_outside_center_and_crop_is_not_padded():
    visible = np.ones((25, 25), bool)
    # The upper center is visible; one corner of its actual 7x7 input is not.
    visible[4, 7] = False
    support, _ = q.context_support(visible, [(10, 12), (1, 12)], [(10, 12), (1, 12)])
    assert support['sides']['upper']['censored_mask_patches'] == 1
    assert support['sides']['upper']['censored_crop_patches'] == 1
    assert support['sides']['upper']['complete_patches'] == 0
    assert support['status'] == 'UNAVAILABLE_SIDE_CONTEXT'


def facet_reply(tmp_path):
    root, reply, _ = fixture_reply(tmp_path)
    reply['schema'] = q.FACET_SCHEMA
    first, second = reply['answers']
    first.update(allowed_interpretations=['INTERNAL_FOAM_CHANGE'],
                 statement_ko='N1 : 내부 변화; 원형 무늬 영향인 듯',
                 context_facets=[dict(kind='GLASS_CIRCULAR_PATTERN_PATH_INFLUENCE',
                                      certainty='USER_SUSPECTED', statement_ko='원형 무늬 영향인 듯')])
    second.update(allowed_interpretations=['STRUCTURE_BOUNDARY'], statement_ko='N2 : 구조물 (원형 rim)',
                  context_facets=[dict(kind='CIRCULAR_RIM', certainty='USER_CONFIRMED_CONTEXT',
                                       statement_ko='원형 rim')])
    reply['response_ko'] = '\n'.join(a['statement_ko'] for a in reply['answers'])
    return root, reply


def test_context_facet_does_not_replace_internal_role_or_prove_cause(tmp_path):
    root, reply = facet_reply(tmp_path)
    result = q.qualify(root, reply)
    internal, structure = result['subjects']
    assert result['schema'].endswith('-v2')
    assert internal['capability_target'] == 'INTERNAL_FOAM_CHANGE'
    assert internal['context_facets'][0]['certainty'] == 'USER_SUSPECTED'
    assert structure['capability_target'] == 'STRUCTURE_BOUNDARY'
    assert not any(s['causal_mechanism_verified'] for s in result['subjects'])
    assert all(s['side_material_labels'] is None for s in result['subjects'])


@pytest.mark.parametrize('change,match', [('certainty', 'certainty'), ('statement', 'absent'),
                                         ('duplicate', 'duplicate facet')])
def test_facets_cannot_upgrade_uncertainty_or_borrow_another_subject_statement(tmp_path, change, match):
    root, reply = facet_reply(tmp_path)
    facet = reply['answers'][0]['context_facets'][0]
    if change == 'certainty': facet['certainty'] = 'USER_CONFIRMED_CONTEXT'
    if change == 'statement': facet['statement_ko'] = '원형 rim'
    if change == 'duplicate': reply['answers'][0]['context_facets'].append(copy.deepcopy(facet))
    with pytest.raises(ValueError, match=match):
        q.qualify(root, reply)


def test_context_crossings_and_unknown_columns_do_not_become_pure_side_truth():
    path = [(10, 16), (11, 15), (12, 14), (13, 13), (14, 12), (15, 11), (16, 10)]
    result, pixels = q.context_support(np.ones((30, 30), bool), [(13, 13), (14, 12)], path)
    upper = result['sides']['upper']
    assert upper['crossing_or_touching_path_pixels'] > 0
    assert upper['outside_reviewed_path_columns'] > 0
    assert upper['reused_pixel_uses'] > 0
    assert not result['pure_material_truth'] and pixels


def test_real_cli_from_other_cwd_with_unicode_space_paths_and_no_overwrite(tmp_path):
    root, reply, _ = fixture_reply(tmp_path)
    q.o2.write_new(root / 'reply.json', reply)
    output = root / '결과 result.json'
    args = [sys.executable, '-B', str(Path(q.__file__).resolve()), '--root', str(root),
            '--reply', str(root / 'reply.json'), '--output', str(output)]
    env = os.environ.copy(); env.pop('PYTHONPATH', None)
    kwargs = dict(cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8')
    done = subprocess.run(args, **kwargs)
    assert done.returncode == 0, done.stderr
    assert json.loads(output.read_text(encoding='utf-8'))['qualified_units'] == 2
    again = subprocess.run(args, **kwargs)
    assert again.returncode != 0 and 'refuse overwrite' in again.stderr


def explicit_reply(tmp_path):
    root, reply, proposal = fixture_reply(tmp_path)
    proposal['display'] = reply['display']
    (root / 'proposal.json').write_text(json.dumps(proposal), encoding='utf-8')
    reply['proposal']['sha256'] = q.o2.sha256_file(root / 'proposal.json')
    reply['schema'] = q.REVIEW_SCHEMA
    for answer in reply['answers']:
        answer.update(review_status='QUALIFIED_ROLE', context_facets=[])
    return root, reply, proposal


def test_inspection_checks_geometry_without_inventing_human_answers(tmp_path):
    root, reply, _ = explicit_reply(tmp_path)
    request = dict(schema=q.INSPECTION_SCHEMA, proposal=reply['proposal'], display=reply['display'])
    result = q.qualify(root, request)
    assert result['status'] == 'PROPOSAL_VERIFIED_PENDING_REVIEW'
    assert result['qualified_units'] == result['new_training_labels'] == 0
    assert result['accounted_units'] == 2
    assert result['review_status_counts'] == {'PENDING_REVIEW': 2}
    assert all(s['capability_target'] is None and s['allowed_interpretations'] == []
               for s in result['subjects'])
    assert 'reply_sha256' not in result and result['request_sha256']
    assert result['same_frame_dependency'][0]['shared_dependency_pixels'] > 0
    assert not result['same_frame_dependency'][0]['independent_split_allowed']


def test_ambiguous_and_unassessable_are_preserved_without_positive_or_negative_targets(tmp_path):
    root, reply, _ = explicit_reply(tmp_path)
    first, second = reply['answers']
    first.update(review_status='AMBIGUOUS_ROLE',
                 allowed_interpretations=['EXTERNAL_FOAM_UPPER', 'INTERNAL_FOAM_CHANGE'],
                 statement_ko='N1은 상단인지 내부 변화인지 애매함')
    second.update(review_status='UNASSESSABLE', allowed_interpretations=[],
                  statement_ko='N2는 판독 불가')
    reply['response_ko'] = '\n'.join(a['statement_ko'] for a in reply['answers'])
    original = copy.deepcopy(reply)
    result = q.qualify(root, reply)
    assert result['schema'].endswith('-v3')
    assert result['qualified_units'] == 0 and result['accounted_units'] == 2
    assert result['review_status_counts'] == {'AMBIGUOUS_ROLE': 1, 'UNASSESSABLE': 1}
    assert result['subjects'][0]['allowed_interpretations'] == first['allowed_interpretations']
    assert all(s['capability_target'] is None and s['decision'] == 'NOT_EVALUATED'
               for s in result['subjects'])
    assert reply == original


def test_explicit_qualified_alternatives_keep_common_target_but_no_pixel_labels(tmp_path):
    root, reply, _ = explicit_reply(tmp_path)
    result = q.qualify(root, reply)
    assert result['qualified_units'] == result['accounted_units'] == 2
    assert result['subjects'][0]['capability_target'] == 'EXTERNAL_SURFACE'
    assert result['subjects'][0]['side_material_labels'] is None
    assert result['subjects'][0]['coordinate_tolerance'] is None


@pytest.mark.parametrize('status,roles,match', [
    ('QUALIFIED_ROLE', [], 'must have an interpretation'),
    ('QUALIFIED_ROLE', ['EXTERNAL_FOAM_UPPER', 'INTERNAL_FOAM_CHANGE'], 'ambiguous surface'),
    ('AMBIGUOUS_ROLE', ['STRUCTURE_BOUNDARY'], 'explicit alternatives'),
    ('UNASSESSABLE', ['STRUCTURE_BOUNDARY'], 'cannot assert a role'),
    ('PENDING_REVIEW', [], 'unsupported review status'),
    ('REJECTED', [], 'unsupported review status'),
])
def test_reply_status_cannot_hide_missing_or_incompatible_judgment(tmp_path, status, roles, match):
    root, reply, _ = explicit_reply(tmp_path)
    reply['answers'][0].update(review_status=status, allowed_interpretations=roles)
    with pytest.raises(ValueError, match=match):
        q.qualify(root, reply)


@pytest.mark.parametrize('inspection', [False, True])
def test_v3_and_inspection_bind_display_to_proposal(tmp_path, inspection):
    root, reply, _ = explicit_reply(tmp_path)
    (root / 'another-display.bin').write_bytes(b'valid pin for a different display')
    reply['display'] = dict(path='another-display.bin', sha256=q.o2.sha256_file(root / 'another-display.bin'))
    if inspection:
        reply = {k: reply[k] for k in ['proposal', 'display']}
        reply['schema'] = q.INSPECTION_SCHEMA
    with pytest.raises(ValueError, match='display differs'):
        q.qualify(root, reply)


def test_alias_of_one_native_subject_does_not_multiply_review_units(tmp_path):
    root, reply, proposal = explicit_reply(tmp_path)
    alias = copy.deepcopy(proposal['subjects'][0])
    alias['id'] = 'another-name-for-N1'
    proposal['subjects'].append(alias)
    (root / 'proposal.json').write_text(json.dumps(proposal), encoding='utf-8')
    request = dict(schema=q.INSPECTION_SCHEMA,
                   proposal=dict(path='proposal.json', sha256=q.o2.sha256_file(root / 'proposal.json')),
                   display=reply['display'])
    with pytest.raises(ValueError, match='duplicate native subject'):
        q.qualify(root, request)


def test_inspection_real_cli_outside_repo_preserves_pending_status_and_write_once(tmp_path):
    root, _, _ = explicit_reply(tmp_path)
    output = root / '검토 전.json'
    args = [sys.executable, '-B', str(Path(q.__file__).resolve()), '--root', str(root),
            '--inspect-proposal', str(root / 'proposal.json'), '--output', str(output)]
    env = os.environ.copy(); env.pop('PYTHONPATH', None)
    kwargs = dict(cwd=tmp_path, env=env, stdin=subprocess.DEVNULL,
                  capture_output=True, text=True, encoding='utf-8')
    done = subprocess.run(args, **kwargs)
    assert done.returncode == 0, done.stderr
    result = json.loads(output.read_text(encoding='utf-8'))
    assert result['qualified_units'] == 0 and result['review_status_counts'] == {'PENDING_REVIEW': 2}
    again = subprocess.run(args, **kwargs)
    assert again.returncode != 0 and 'refuse overwrite' in again.stderr


def preparation_fixture(tmp_path):
    root, reply, proposal = explicit_reply(tmp_path)
    baseline = q.o2.read_json(root / 'baseline.json')
    context = baseline['contexts'][0]
    fragments = []
    for subject, row in zip(proposal['subjects'], context['rows']):
        fragment = row['incident_fragments'][0]
        fragments.append(dict(id=f"native/fragment-{fragment['fragment_id']}",
                              fragment_id=fragment['fragment_id'],
                              source_path_xy=subject['source_path_xy'],
                              fixed_column_source_ys=[row['source_xy'][1]],
                              g0_fragment_sha256=q.o2.fingerprint_json(fragment)))
    packet = dict(case_id='native', **{k: context[k] for k in ['frame', 'geometry', 'source_recording']},
                  fragments=fragments, intervals=[
                      dict(original=dict(id='upper', interval=[220, 220]), compatible_fragments=[fragments[0]['id']]),
                      dict(original=dict(id='lower', interval=[230, 230]), compatible_fragments=[fragments[1]['id']]),
                  ])
    manifest = dict(inputs={k: proposal[k] for k in ['g0_manifest', 'g0_readout']})
    reused = dict(manifest_sha256=q.o2.fingerprint_json(manifest), native_review_packets=[packet])
    q.o2.write_new(root / 'reuse-manifest.json', manifest)
    q.o2.write_new(root / 'reuse-readout.json', reused)
    plan = dict(schema=q.PREPARATION_SCHEMA,
                reuse_manifest=dict(path='reuse-manifest.json', sha256=q.o2.sha256_file(root / 'reuse-manifest.json')),
                reuse_readout=dict(path='reuse-readout.json', sha256=q.o2.sha256_file(root / 'reuse-readout.json')),
                case_id='native', interval_id='upper', view=proposal['views'][0], display=reply['display'],
                question='Displayed fragment role?')
    return root, plan, reused


def test_preparation_keeps_other_interval_unreviewed_and_can_be_independently_inspected(tmp_path):
    root, plan, reused = preparation_fixture(tmp_path)
    original = copy.deepcopy(reused)
    proposal = q.prepare_proposal(root, plan)
    assert proposal['qualified_units'] == 0 and len(proposal['subjects']) == 1
    assert proposal['complete_saved_fragment_count'] == 2
    assert proposal['preserved_intervals'] == reused['native_review_packets'][0]['intervals'][1:]
    q.o2.write_new(root / 'prepared.json', proposal)
    result = q.qualify(root, dict(schema=q.INSPECTION_SCHEMA, display=proposal['display'],
                      proposal=dict(path='prepared.json', sha256=q.o2.sha256_file(root / 'prepared.json'))))
    assert result['qualified_units'] == 0 and result['accounted_units'] == 1
    assert reused == original


@pytest.mark.parametrize('change,match', [
    ('interval', 'drops or adds'), ('path', 'saved native path changed'),
    ('geometry', 'geometry changed'), ('source', 'source_recording changed'),
    ('alias', 'duplicate fragment selection'),
])
def test_preparation_cannot_rehash_away_population_or_source_corruption(tmp_path, change, match):
    root, plan, reused = preparation_fixture(tmp_path)
    packet = reused['native_review_packets'][0]
    if change == 'interval': packet['intervals'][0]['original']['interval'][1] = 230
    if change == 'path': packet['fragments'][0]['source_path_xy'][0][1] += 1
    if change == 'geometry': packet['geometry']['origin'][0] += 1
    if change == 'source': packet['source_recording']['sha256'] = '0'*64
    if change == 'alias': packet['intervals'][0]['compatible_fragments'] *= 2
    (root / 'reuse-readout.json').write_text(json.dumps(reused), encoding='utf-8')
    plan['reuse_readout']['sha256'] = q.o2.sha256_file(root / 'reuse-readout.json')
    with pytest.raises(ValueError, match=match):
        q.prepare_proposal(root, plan)


def test_preparation_real_cli_then_inspection_with_no_human_answer(tmp_path):
    root, plan, _ = preparation_fixture(tmp_path)
    q.o2.write_new(root / '준비 plan.json', plan)
    command = [sys.executable, '-B', str(Path(q.__file__).resolve()), '--root', str(root)]
    env = os.environ.copy(); env.pop('PYTHONPATH', None)
    kwargs = dict(cwd=tmp_path, env=env, stdin=subprocess.DEVNULL,
                  capture_output=True, text=True, encoding='utf-8')
    proposal = root / '새 proposal.json'
    done = subprocess.run(command + ['--prepare-plan', str(root / '준비 plan.json'), '--output', str(proposal)], **kwargs)
    assert done.returncode == 0, done.stderr
    output = root / 'inspection.json'
    checked = subprocess.run(command + ['--inspect-proposal', str(proposal), '--output', str(output)], **kwargs)
    assert checked.returncode == 0, checked.stderr
    assert json.loads(output.read_text(encoding='utf-8'))['qualified_units'] == 0
