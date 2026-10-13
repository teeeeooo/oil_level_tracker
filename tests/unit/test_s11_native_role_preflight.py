"""G0 integrity/precision controls; synthetic pixels never become scene truth."""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image
import pytest

from tests.diagnostics import s11_native_role_preflight as g
from tests.unit.test_s11_contextual_role_preflight import fixture_review


def test_point_membership_is_lossless_and_censors_missing_path_mask_and_crop():
    visible = np.ones((30, 30), bool)
    visible[8, 10] = False
    columns = [(10, 10), (11, 1)]
    got = g.membership(visible, columns, [-2, -3], requested_columns=3)
    assert got == dict(requested=6, observed=1, censored_crop=2, censored_mask=1,
                       missing_path=2, status='PARTIAL_OR_UNAVAILABLE')
    with pytest.raises(ValueError, match='ambiguous path'):
        g.membership(visible, [(10, 10), (10, 11)], [-2])


def test_all_junction_arms_survive_without_pairing_or_physical_orientation():
    edge = np.zeros((35, 35), bool)
    edge[17, 2:33] = True
    edge[2:33, 17] = True
    visible = np.ones_like(edge)
    rows, graph = g.edge_bindings(edge, visible, 17, True)
    assert len(rows) == 31
    row = next(r for r in rows if r['row'] == 17)
    assert row['degree'] == 4 and len(row['incident_fragments']) == 4
    assert all(p['junction_incident'] and not p['candidate_positive'] for p in row['incident_fragments'])
    assert graph['vertices'] == np.count_nonzero(edge)
    assert all(r['physical_role'] == 'UNREVIEWED' for r in rows)


def test_curved_partial_path_keeps_actual_columns_and_missing_support():
    edge = np.zeros((40, 40), bool)
    for x in range(12, 23):
        edge[10 + x - 12, x] = True
    visible = np.ones_like(edge)
    rows, _ = g.edge_bindings(edge, visible, 17, False)
    path = rows[0]['incident_fragments'][0]
    assert path['orientation'] == 'X_MONOTONE_PARTIAL_PATH'
    assert path['fixed_column_rows'] == [15]
    assert len(path['support_columns_xy']) == 11
    assert path['side_support']['lower']['missing_path'] == 14 * 11
    assert rows[0]['rgb_status'] == 'UNAVAILABLE_SAVED_RGB'
    assert rows[0]['decision'] == 'NOT_EVALUATED'


def test_faces_keep_shared_owner_views_and_zero_mask_crop_distinctions():
    labels = np.zeros((10, 10), np.uint16)
    labels[:4] = 1
    labels[4:7] = 2
    visible = np.ones_like(labels, bool)
    result = g.center_faces(labels, visible, 5)
    shared = [f for f in result['faces'] if f['raster_y'] == 3.5]
    assert len(shared) == 2
    assert {f['inside_label'] for f in shared} == {1, 2}
    assert {f['status'] for f in result['faces']} == {'CROP', 'VISIBLE_OTHER_LABEL', 'VISIBLE_ZERO'}
    visible[4, 5] = False
    assert 'MASKED_NEIGHBOUR' in {f['status'] for f in g.center_faces(labels, visible, 5)['faces']}
    assert g.center_faces(None, visible, 5)['status'] == 'UNAVAILABLE_SAVED_LABELS'


@pytest.mark.parametrize('ys', [[], [13], [12, 13, 14]])
def test_interval_hit_cardinality_never_creates_candidate_positive(ys):
    plan = {'evaluation_only': {'qualified_intervals': [dict(id='upper', case_id='x', interval=[11.5, 14.5])], 'guides': []}}
    cases = {'x': {'rows': [dict(row=y, source_xy=[7, y]) for y in ys], 'component_faces': {'faces': []}}}
    result = g.weak_constraints(plan, cases)[0]
    assert result['compatible_edge_rows'] == ys
    assert result['candidate_positive_ids'] == result['candidate_negative_ids'] == []
    assert result['correspondence'] == 'NOT_QUALIFIED'


def test_missing_guide_does_not_snap_to_nearby_edge_or_label_neighbor():
    plan = {'evaluation_only': {'qualified_intervals': [], 'guides': [dict(frame=10, source_xy=[7, 14])]}}
    case = {'rows': [dict(row=13, source_xy=[7, 13]), dict(row=15, source_xy=[7, 15])]}
    result = g.weak_constraints(plan, {'s4-f10': case})[0]
    assert result['correspondence'] == 'NO_EXACT_EDGE'
    assert result['exact_edge_rows'] == [] and not result['nearest_edge_used']


def fixture_native(tmp_path):
    root, oil, _, review = fixture_review(tmp_path)

    def pin(name):
        return {'path': name, 'sha256': g.o2.sha256_file(root / name)}

    def write(name, value):
        (root / name).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        return pin(name)

    rgb = np.arange(64 * 64 * 3, dtype=np.uint8).reshape(64, 64, 3)
    visible = np.ones((64, 64), np.uint8) * 255
    edge = np.zeros((64, 64), np.uint8); edge[32, 5:59] = 255
    labels = np.zeros((64, 64), np.uint16); labels[34:50, 5:59] = 1
    np.savez(root / 'native.npz', original_roi=rgb[:, :, ::-1], effective_mask=visible,
             glare_mask=np.zeros_like(visible), canny=edge, foam_component_labels=labels)
    Image.fromarray(rgb).save(root / 'RGB.png')
    case = dict(id='s4-f10', kind='public_compressor', raster='native.npz', origin=[0, 0],
                scale_xy=[1, 1], shape=[64, 64], column=32, frame=10, rows=[32], exposure='EXPOSED_DEVELOPMENT')
    refs = []
    pins = {n: pin(n)['sha256'] for n in ['native.npz', 'RGB.png']}
    for name, y in [('R', 3), ('L', 37)]:
        rect = [10, y, 35, y + 25]
        reply = dict(judgment=dict(reference_use='APPROVED_AT_DISPLAYED_FOOTPRINT', appearance=name),
                     subject=dict(id=name, source_rectangle_xyxy_half_open=rect,
                                  rgb_array_sha256=hashlib.sha256(rgb[y:y+25, 10:35].tobytes()).hexdigest()))
        rpin = write(f'{name}.json', reply); pins[rpin['path']] = rpin['sha256']
        refs.append(dict(id=name, appearance=name, reply=rpin['path'], case_id=case['id'],
                         source_image='RGB.png', source_sha256=pins['RGB.png'], source_rectangle=rect))
    plan = dict(schema='s11-foam-material-sides-preflight-v1', pins=pins, references=refs,
                cases=[case], resources={'max_queries_per_raster': 400},
                evaluation_only={'qualified_intervals': [dict(id='interval', case_id=case['id'], interval=[31.5, 32.5])], 'guides': []})
    identity = dict(frame_index=10, timestamp_sec=0.333, glass_id='synthetic')
    inputs = dict(foam_preflight=write('foam.json', plan), oil_manifest=write('oil.json', oil),
                  oil_review_manifest=write('review.json', review), identity=write('identity.json', identity))
    source = pin('original.bin')
    binding = dict(id=case['id'], case_sha256=g.o2.fingerprint_json(case), labels=None,
                   identity=dict(input='identity', keys=[], sha256=g.o2.fingerprint_json(identity)),
                   frame_key='frame_index', time_key='timestamp_sec', time_kind='RECORDED',
                   source_recording=source, glass_recipe={'status': 'SYNTHETIC'})
    manifest = dict(schema=g.SCHEMA, inputs=inputs, artifacts=[source], bindings=[binding],
                    dependencies=copy.deepcopy(g.DEPENDENCIES), side_offsets=copy.deepcopy(g.SIDE_OFFSETS),
                    resources=dict(max_cases=1, max_edges=1, max_output_bytes=100000))
    return root, manifest


def test_real_audit_preserves_review_precision_and_no_ml_import(tmp_path):
    root, manifest = fixture_native(tmp_path)
    result = g.audit(root, manifest)
    assert result['counts']['edges'] == 1 and result['counts']['oil_records'] == 3
    assert result['weak_constraints'][0]['compatible_edge_rows'] == [32]
    assert result['weak_constraints'][0]['candidate_positive_ids'] == []
    a, b, unreviewed = result['oil_rows']
    assert a['physical_qualification'] == b['physical_qualification'] == 'NOT_QUALIFIED'
    assert b['practical_acceptance'] == 'ACCEPTED_APPROXIMATION'
    assert unreviewed['physical_qualification'] == 'HISTORICAL_ONLY'
    assert all(not r['training_label_created'] for r in result['oil_rows'])
    assert result['readiness'][3]['status'] == 'NOT_READY'
    assert result['reference_units'][0]['independent_units'] == 1
    assert not result['reference_units'][0]['dense_pixel_labels']
    assert 'torch' not in sys.modules


@pytest.mark.parametrize('change', ['stale_source', 'stale_review', 'wrong_frame', 'wrong_pts', 'geometry', 'duplicate', 'missing_case', 'footprint', 'time_precision', 'source_unpinned'])
def test_inconsistent_bound_inputs_fail_before_observation(tmp_path, change):
    root, manifest = fixture_native(tmp_path)
    if change == 'stale_source':
        (root / 'original.bin').write_bytes(b'changed')
    elif change == 'stale_review':
        (root / '후속 설명.json').write_text('{}', encoding='utf-8')
    elif change in ('wrong_frame', 'wrong_pts'):
        identity = g.o2.read_json(root / 'identity.json')
        identity['frame_index' if change == 'wrong_frame' else 'timestamp_sec'] += 1
        (root / 'identity.json').write_text(json.dumps(identity), encoding='utf-8')
        manifest['inputs']['identity']['sha256'] = g.o2.sha256_file(root / 'identity.json')
        if change == 'wrong_frame':
            manifest['bindings'][0]['identity']['sha256'] = g.o2.fingerprint_json(identity)
    elif change == 'geometry':
        manifest['bindings'][0]['case_sha256'] = '0' * 64
    elif change == 'duplicate':
        manifest['bindings'].append(copy.deepcopy(manifest['bindings'][0]))
    elif change == 'missing_case':
        manifest['bindings'].clear()
    elif change == 'footprint':
        manifest['dependencies']['saved_rgb_point']['footprint'].append([1, 1])
    elif change == 'time_precision':
        manifest['bindings'][0]['time_kind'] = 'NOMINAL_ONLY'
    else:
        manifest['bindings'][0]['source_recording'] = dict(path='other', sha256='0' * 64)
    with pytest.raises((ValueError, AssertionError)):
        g.audit(root, manifest)


def test_cli_from_unicode_foreign_cwd_is_deterministic_and_refuses_overwrite(tmp_path):
    root, manifest = fixture_native(tmp_path)
    entry = root / '준비 명세.json'
    entry.write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
    outside = tmp_path / '다른 작업 폴더'; outside.mkdir()
    output = outside / 'readiness.json.gz'
    command = [sys.executable, '-B', str(Path(g.__file__).resolve()), '--root', str(root),
               '--manifest', str(entry), '--output', str(output)]
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONPATH'}
    run = lambda cmd: subprocess.run(cmd, cwd=outside, env=env, stdin=subprocess.DEVNULL,
                                     capture_output=True, text=True, encoding='utf-8')
    first = run(command)
    assert first.returncode == 0, first.stderr
    raw = output.read_bytes()
    result = json.loads(gzip.decompress(raw))
    assert result['status'] == 'BINDINGS_VERIFIED_ROLE_NOT_READY'
    assert result['contexts'][0]['time_sec'] == 0.333
    retry = run(command)
    assert retry.returncode != 0 and 'refuse overwrite' in retry.stderr and output.read_bytes() == raw
    command[-1] = str(outside / 'again.json.gz')
    assert run(command).returncode == 0
    assert json.loads(gzip.decompress(Path(command[-1]).read_bytes())) == result


def test_alternative_paths_share_actual_pixels_across_sides_without_independent_votes():
    visible = np.ones((40, 40), bool)
    paths = [{"support_columns_xy": [[10, 20]]}, {"support_columns_xy": [[10, 24]]}]
    result = g.shared_support(paths, visible)
    assert result["shared_upper_lower_pixels"] == 1
    assert result["reused_within_side"] == {"upper": 7, "lower": 7}
    assert not result["independent_votes"]
    visible[22, 10] = False
    assert g.shared_support(paths, visible)["shared_upper_lower_pixels"] == 0
