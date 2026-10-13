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
