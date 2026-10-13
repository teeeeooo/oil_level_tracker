"""Frozen offline Foam appearance-side comparison; no detector or decision rule.

Reuse CR1's encoder and the transfer geometry. A new runner is needed because
these references describe material interiors, not CR1's joint role descriptors.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tests.diagnostics import s11_contextual_role_transfer as geometry


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def unit(vector):
    if vector is None or not np.isfinite(vector).all():
        return None
    norm = float(np.linalg.norm(vector))
    return vector / norm if norm > 1e-12 else None


def affinities(upper, lower, reference):
    if reference is None:
        return {'status': 'UNAVAILABLE_REFERENCE'}
    if upper is None or lower is None:
        return {'status': 'UNAVAILABLE_SIDE'}
    u, l, p = (unit(v) for v in (upper, lower, reference))
    if any(v is None for v in (u, l, p)):
        return {'status': 'UNAVAILABLE_VECTOR'}
    a, b = float(u @ p), float(l @ p)
    return {'status': 'MEASURED', 'upper_affinity': a, 'lower_affinity': b,
            'ordered_contrast': b - a, 'unordered_control': (a + b) / 2}


def side_support(mask, xy):
    """Every requested pixel is required; no changing widths after mask loss."""
    x, y = xy
    h, w = mask.shape
    requested = 25 * 11
    counts = {}
    for name, offsets in [('upper', range(-12, -1)), ('lower', range(2, 13))]:
        counts[name] = sum(0 <= y + dy < h and 0 <= x + dx < w
                           and bool(mask[y + dy, x + dx])
                           for dy in offsets for dx in range(-12, 13))
    return {'status': 'AVAILABLE' if all(n == requested for n in counts.values())
            else 'UNAVAILABLE_REQUIRED_SUPPORT', 'requested_per_side': requested,
            'visible_pixels': counts}


def load_case(root, case):
    """Read existing rasters/edges only; never regenerate or snap an edge."""
    if case['kind'] in ('public_graph', 'water_stages'):
        with np.load(root / case['raster'], allow_pickle=False) as archive:
            rgb = archive['crop'][:, :, ::-1].copy()
            visible = archive['visible'].astype(bool) if 'visible' in archive else None
        with np.load(root / case.get('graph', case.get('stage')), allow_pickle=False) as archive:
            edges = archive['edges'].astype(bool) if 'edges' in archive else archive['canny'] > 0
            if 'visible' in archive:
                visible = archive['visible'].astype(bool)
    elif case['kind'] == 'public_compressor':
        with np.load(root / case['raster'], allow_pickle=False) as archive:
            rgb = archive['original_roi'][:, :, ::-1].copy()
            visible = (archive['effective_mask'] > 0) & (archive['glare_mask'] == 0)
            edges = archive['canny'] > 0
    else:
        images = {k: np.array(Image.open(root / p)) for k, p in case['images'].items()}
        edges = images['canny'] > 0
        visible = (images['effective_mask'] > 0) & (images['glare_mask'] == 0)
        rgb = np.array(Image.open(root / case['rgb']).convert('RGB')) if case['rgb'] else None
    assert list(visible.shape) == case['shape'] and edges.shape == visible.shape
    assert rgb is None or rgb.shape == (*visible.shape, 3)
    rows = np.flatnonzero(edges[:, case['column']] & visible[:, case['column']]).tolist()
    assert rows == case['rows'], f"changed edge roster: {case['id']}"
    return rgb, visible, rows


def validate(plan, root):
    assert plan['schema'] == 's11-foam-material-sides-preflight-v1'
    for name, digest in plan['pins'].items():
        assert sha(root / name) == digest, f'changed pin: {name}'
    assert [r['id'] for r in plan['references']] == ['R', 'L']
    cases = {c['id']: c for c in plan['cases']}
    assert len(cases) == len(plan['cases'])
    loaded = {}
    for case in cases.values():
        rgb, visible, rows = load_case(root, case)
        loaded[case['id']] = (rgb, visible, rows)
        assert len(rows) <= plan['resources']['max_queries_per_raster']
    references = {}
    for ref in plan['references']:
        reply = read(root / ref['reply'])
        assert reply['judgment']['reference_use'] == 'APPROVED_AT_DISPLAYED_FOOTPRINT'
        assert reply['judgment']['appearance'] == ref['appearance']
        assert reply['subject']['id'] == ref['id']
        assert reply['subject']['source_rectangle_xyxy_half_open'] == ref['source_rectangle']
        rgb, visible, _ = loaded[ref['case_id']]
        case = cases[ref['case_id']]
        assert case['scale_xy'] == [1, 1] and rgb is not None
        source = np.array(Image.open(root / ref['source_image']).convert('RGB'))
        ox, oy = case['origin']; h, w = visible.shape
        assert np.array_equal(source[oy:oy+h, ox:ox+w], rgb)
        x0, y0, x1, y1 = ref['source_rectangle']
        assert x1-x0 == y1-y0 == 25
        patch = source[y0:y1, x0:x1]
        assert sha(root / ref['source_image']) == ref['source_sha256']
        assert hashlib.sha256(patch.tobytes()).hexdigest() == reply['subject']['rgb_array_sha256']
        x, y = x0+12-ox, y0+12-oy
        assert visible[y-12:y+13, x-12:x+13].shape == (25, 25)
        assert visible[y-12:y+13, x-12:x+13].all()
        references[ref['id']] = (ref, patch, (x, y))
    return loaded, references


def vectors(tokens, xy, edge):
    wu, wl = geometry.strips(xy, list(range(-12, 13)), edge)
    return unit(wu @ tokens), unit(wl @ tokens)


def pixel_controls(base, encoder, refs, bank):
    # The existing remote-pixel intervention exercises the real encoder/masking.
    isolation = geometry.pixel_controls(base, encoder)
    controls = []
    blank = np.full((25, 25, 3), 60, dtype=np.uint8)
    patches = {'R': refs['R'][1], 'L': refs['L'][1], 'blank': blank}
    for a, b in [('R', 'R'), ('L', 'L'), ('R', 'L'), ('L', 'R'), ('blank', 'R'), ('R', 'blank')]:
        rgb = np.full((104, 104, 3), 60, dtype=np.uint8)
        rgb[40:51, 40:65] = patches[a][:11]
        rgb[54:65, 40:65] = patches[b][-11:]
        row = {'upper_patch': a, 'lower_patch': b, 'kind': 'CONSTRUCTED_PIXELS_NOT_SCENE_TRUTH', 'modes': {}}
        for mode in ('full', 'local'):
            tokens = encoder.encode(rgb, np.ones((104, 104), bool), (52, 52), mode)
            upper, lower = vectors(tokens, (52, 52), 104)
            row['modes'][mode] = {}
            for key in ('R', 'L'):
                result = affinities(upper, lower, bank[mode][key])
                swapped = affinities(lower, upper, bank[mode][key])
                assert result['status'] == 'MEASURED'
                assert swapped['ordered_contrast'] == -result['ordered_contrast']
                assert swapped['unordered_control'] == result['unordered_control']
                row['modes'][mode][key] = result
        controls.append(row)
    # Equal pixels cannot distinguish a physical layer from a printed copy.
    return {'status': isolation['status'], 'context_isolation': isolation,
            'side_exchange_algebra': 'PASS', 'appearance_composites': controls,
            'physical_identity': 'NOT_EVALUATED',
            'copy_limit': 'Identical pixels retain identical scores regardless of assigned physical role.'}


def run(plan_path, output):
    assert not output.exists(), 'refuse overwrite'
    plan = read(plan_path)
    loaded, references = validate(plan, ROOT)
    base = geometry.legacy()
    ready = read(geometry.LEGACY / 'readiness.json')
    backend_pins = {p: h for p, h in ready['frozen_files'].items() if '/models/' in p}
    for p, digest in backend_pins.items():
        assert sha(ROOT / p) == digest, p
    from importlib.metadata import version
    assert {p: version(p) for p in plan['packages']} == plan['packages']
    denied = base.sandbox()
    start = time.monotonic()
    encoder = base.Encoder(plan['resources'])
    bank, reference_records = {'full': {}, 'local': {}}, {}
    for key, (ref, patch, xy) in references.items():
        rgb, visible, _ = loaded[ref['case_id']]
        image, mask, (dx, dy) = geometry.padded(rgb, visible)
        xy = (xy[0]+dx, xy[1]+dy)
        weights = geometry.weights(xy, list(range(-12, 13)), range(-12, 13), image.shape[0])
        for mode in bank:
            tokens = encoder.encode(image, mask, xy, mode)
            bank[mode][key] = unit(weights @ tokens)
            assert bank[mode][key] is not None
        reference_records[key] = {'case_id': ref['case_id'], 'appearance': ref['appearance'],
            'padded_xy': list(xy), 'square_edge': image.shape[0],
            'native_pixels_per_token': image.shape[0]/16,
            'token_weights': [[int(i), float(weights[i])] for i in np.flatnonzero(weights)]}
    controls = pixel_controls(base, encoder, references, bank)
    assert controls['status'] == 'PASS', 'encoder-through-pixel control failed'
    cases = []
    for case in plan['cases']:
        rgb, visible, rows = loaded[case['id']]
        result = {'id': case['id'], 'exposure': case['exposure'], 'rows': []}
        cases.append(result)
        full_tokens = None
        if rgb is not None:
            image, mask, offset = geometry.padded(rgb, visible)
            result.update(square_edge=image.shape[0], pad_offset_xy=list(offset),
                          working_pixels_per_token=image.shape[0]/16,
                          scale_xy=case['scale_xy'])
        for y in rows:
            xy = (case['column'], y)
            support = side_support(visible, xy)
            ox, oy = case['origin']; sx, sy = case['scale_xy']
            row = {'row': y, 'source_xy': [ox+(xy[0]+.5)*sx-.5, oy+(y+.5)*sy-.5],
                   'physical_label': 'UNREVIEWED_EDGE', 'support': support, 'modes': {}}
            result['rows'].append(row)
            if rgb is None:
                row['status'] = 'UNAVAILABLE_SAVED_RGB'; continue
            if support['status'] != 'AVAILABLE':
                row['status'] = support['status']; continue
            if time.monotonic()-start > plan['resources']['full_seconds_limit']:
                row['status'] = 'NOT_RUN_TIME_LIMIT'; continue
            qxy = (xy[0]+offset[0], xy[1]+offset[1])
            edge = image.shape[0]
            row['token_weights'] = geometry.weight_record(qxy, list(range(-12, 13)), edge)
            row['status'] = 'MEASURED'
            for mode in ('full', 'local'):
                if mode == 'full' and full_tokens is None:
                    full_tokens = encoder.encode(image, mask, qxy, mode)
                tokens = full_tokens if mode == 'full' else encoder.encode(image, mask, qxy, mode)
                upper, lower = vectors(tokens, qxy, edge)
                row['modes'][mode] = {k: affinities(upper, lower, bank[mode][k]) for k in bank[mode]}
            # Token maps are never serialized; the single full map is replaced each scene.
        result['statuses'] = dict(Counter(r['status'] for r in result['rows']))
        print(json.dumps({'case': case['id'], 'statuses': result['statuses']}), flush=True)
    for p, digest in {**plan['pins'], **backend_pins}.items():
        assert sha(ROOT / p) == digest, p
    elapsed = time.monotonic()-start
    cross = {m: float(bank[m]['R'] @ bank[m]['L']) for m in bank}
    result = {'schema': 's11-foam-material-sides-readout-v1', 'preflight_sha256': sha(plan_path),
        'status': 'COMPLETE_DIAGNOSTIC_ONLY' if all(not r['status'].startswith('NOT_RUN')
                   for c in cases for r in c['rows']) else 'INCOMPLETE',
        'references': reference_records, 'reference_cross_affinity': cross,
        'pixel_controls': controls, 'cases': cases, 'packages': plan['packages'],
        'backend_pin_count': len(backend_pins), 'runtime_guard_denied_events': denied,
        'physical_accuracy': 'NOT_EVALUATED', 'candidate_selection': 'NOT_EVALUATED',
        'foam_absence': 'NOT_EVALUATED', 'untouched_holdout_recordings': 0,
        'production_changed': False, 'video_decode': False, 'threshold': None,
        'resources': {'elapsed_seconds': elapsed, 'encoder_load_seconds': encoder.load_seconds,
            'forward_count': len(encoder.times), 'forward_seconds': encoder.times,
            'peak_rss_bytes': base.rss(), 'workspace_allocated_bytes': base.allocated(base.WORKSPACE),
            'retained_token_maps': 0}}
    assert result['resources']['workspace_allocated_bytes'] + plan['external_allocated_reservation_bytes'] < 3_000_000_000
    payload = json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode()+b'\n'
    compressed = gzip.compress(payload, mtime=0)
    assert len(compressed) <= plan['resources']['run_output_bytes_limit']
    with output.open('xb') as stream:
        stream.write(compressed)
    print(json.dumps({'status': result['status'], 'forwards': len(encoder.times),
                      'seconds': elapsed, 'output_bytes': len(compressed)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    if args.validate_only:
        loaded, refs = validate(read(args.manifest), ROOT)
        print(json.dumps({'status': 'PASS', 'cases': len(loaded),
            'edges': sum(len(v[2]) for v in loaded.values()), 'references': list(refs), 'model_calls': 0}))
    else:
        if args.output is None:
            parser.error('--output required unless --validate-only')
        run(args.manifest, args.output)
