"""Bounded cross-source context diagnostic using the unchanged CR1 encoder/bank.

Only geometry/support adapt to a differently sized saved ROI. Every interval
anchor is unlabelled; containment truth is not per-anchor or candidate truth.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / 'docs/50-diagnostics/s11/2026-10-12-cr1-context-comparison'


def legacy():
    spec = importlib.util.spec_from_file_location('cr1_unchanged_transfer_backend', LEGACY / 'probe.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.np = np
    return module


def padded(rgb, visible):
    height, width = visible.shape
    assert rgb.shape == (height, width, 3) and height > 0 and width > 0
    edge = max(height, width)
    top, left = (edge - height) // 2, (edge - width) // 2
    image = np.zeros((edge, edge, 3), dtype=rgb.dtype)
    mask = np.zeros((edge, edge), dtype=bool)
    image[top:top + height, left:left + width] = rgb
    mask[top:top + height, left:left + width] = visible
    return image, mask, (left, top)


def common_columns(contexts):
    offsets = list(range(-12, -1)) + list(range(2, 13))
    for mask, (x, y) in contexts:
        height, width = mask.shape
        if x - 12 < 0 or y - 12 < 0 or x + 12 >= width or y + 12 >= height:
            return []
    columns = [dx for dx in range(-12, 13)
               if all(all(mask[y + dy, x + dx] for dy in offsets) for mask, (x, y) in contexts)]
    return columns if len(columns) >= 8 else []


def weights(xy, columns, rows, edge):
    if not columns:
        return None
    assert edge > 0
    result = np.zeros(256, dtype=np.float64)
    for dy in rows:
        for dx in columns:
            gx, gy = [min(15., max(0., (p + 0.5) * (224 / edge) / 14 - 0.5))
                      for p in (xy[0] + dx, xy[1] + dy)]
            ix, iy = math.floor(gx), math.floor(gy)
            ax, ay = gx - ix, gy - iy
            for xx, wx in [(ix, 1 - ax), (min(ix + 1, 15), ax)]:
                for yy, wy in [(iy, 1 - ay), (min(iy + 1, 15), ay)]:
                    result[yy * 16 + xx] += wx * wy / (len(rows) * len(columns))
    return result


def strips(xy, columns, edge):
    return weights(xy, columns, range(-12, -1), edge), weights(xy, columns, range(2, 13), edge)


def weight_record(xy, columns, edge):
    upper, lower = strips(xy, columns, edge)
    if upper is None:
        return {'status': 'UNAVAILABLE'}
    return {'upper': [[int(i), float(upper[i])] for i in np.flatnonzero(upper)],
            'lower': [[int(i), float(lower[i])] for i in np.flatnonzero(lower)],
            'overlap_mass': float(np.minimum(upper, lower).sum()),
            'shared_token_count': int(np.count_nonzero((upper > 0) & (lower > 0)))}


def interval_anchors(intervals, source_x):
    result = []
    for interval in intervals:
        low, high = interval['source_y_cell_bounds']
        assert math.isfinite(low) and math.isfinite(high) and low < high
        assert interval['role'] in ('Oil upper', 'Foam upper')
        for y in range(math.floor(low), math.ceil(high) + 1):
            result.append({'range_id': interval['id'], 'contained_boundary_role': interval['role'],
                           'source_xy': [source_x, y], 'anchor_label': 'UNREVIEWED_ANCHOR',
                           'meaning': 'floor/ceil cover of a boundary-containment interval, not point truth'})
    return result


def pixel_controls(base, encoder):
    # New rectangular native geometry; only remote pixels differ in the pair.
    rgb = np.full((210, 228, 3), 60, dtype=np.uint8)
    rgb[:105] = [160, 180, 140]
    altered = rgb.copy()
    altered[:, :48] = [220, 30, 100]
    visible = np.ones(rgb.shape[:2], dtype=bool)
    a, mask, offset = padded(rgb, visible)
    b, _, _ = padded(altered, visible)
    xy = (114, 105 + offset[1])
    local_a = encoder.encode(a, mask, xy, 'local')
    local_b = encoder.encode(b, mask, xy, 'local')
    full_a = encoder.encode(a, mask, xy, 'full')
    full_b = encoder.encode(b, mask, xy, 'full')
    w = strips(xy, list(range(-12, 13)), a.shape[0])
    available = all(base.descriptor(t, *w) is not None for t in (local_a, local_b, full_a, full_b))
    result = {'local_tokens_equal': bool(np.array_equal(local_a, local_b)),
              'full_tokens_differ': bool(not np.array_equal(full_a, full_b)),
              'descriptor_available': available, 'forwards': 4,
              'native_shape': [210, 228], 'square_shape': [228, 228], 'offset_xy': list(offset)}
    result['status'] = 'PASS' if all(result[k] for k in
        ('local_tokens_equal', 'full_tokens_differ', 'descriptor_available')) else 'FAIL'
    return result


def run(manifest_path, output):
    base = legacy()
    plan = base.read(manifest_path)
    assert plan['schema'] == 's11-cr1-public-transfer-preflight-v1'
    assert not output.exists()
    for path, digest in plan['pins'].items():
        assert base.sha(ROOT / path) == digest, path
    ready = base.read(LEGACY / 'readiness.json')
    backend_pins = {p: h for p, h in ready['frozen_files'].items() if '/models/' in p}
    for path, digest in backend_pins.items():
        assert base.sha(ROOT / path) == digest, path
    from importlib.metadata import version
    assert {p: version(p) for p in plan['packages']} == plan['packages']
    pre = base.read(LEGACY / 'preflight.json')
    prepared_path = ROOT / plan['prepared']
    prepared = base.read(prepared_path)
    assert base.sha(prepared_path.parent / prepared['masks_file']) == prepared['mask_sha256']
    position = base.read(ROOT / plan['position_review'])
    assert position['status'] == 'CLOSED_USER_CONFIRMED_BOTH_RANGES'
    assert position['frame_index'] == plan['frame_index'] and position['timestamp_sec'] == plan['timestamp_sec']
    assert position['source_x'] == plan['source_x']
    queries = interval_anchors(position['proposed_ranges'], position['source_x'])
    assert queries == plan['queries'] and len(queries) <= plan['max_queries']
    denied = base.sandbox()
    started = time.monotonic()
    from PIL import Image
    with np.load(ROOT / plan['native_images'], allow_pickle=False) as archive:
        rgb = archive['original_roi'][:, :, ::-1].copy()
        visible = (archive['effective_mask'] != 0) & (archive['glare_mask'] == 0)
        capture = base.read(ROOT / plan['native_capture_readout'])
        native = next(c for c in capture['cases'] if c['variant']['id'] == 'native')
        for name in ('original_roi', 'effective_mask', 'glare_mask'):
            assert hashlib.sha256(archive[name].tobytes()).hexdigest() == native['images'][name]['array_sha256']
    assert list(rgb.shape) == plan['geometry']['native_shape']
    assert native['crop_origin'] == plan['geometry']['source_origin_xy']
    source_rgb = np.array(Image.open(ROOT / plan['source_frame']).convert('RGB'))
    ox, oy = native['crop_origin']
    assert np.array_equal(source_rgb[oy:oy + rgb.shape[0], ox:ox + rgb.shape[1]], rgb)
    image, mask, offset = padded(rgb, visible)
    assert list(offset) == plan['geometry']['pad_offset_xy'] and image.shape[0] == plan['geometry']['square_edge']
    refs = pre['references']
    bank_owner = base.read(ROOT / plan['bank_input_owner'])
    for ref in refs.values():
        path = prepared['images'][str(ref['frame'])]
        assert path == bank_owner['images'][str(ref['frame'])]['original_roi']
        assert base.sha(ROOT / path) == bank_owner['inputs'][path]
    images = {r['frame']: np.array(Image.open(ROOT / prepared['images'][str(r['frame'])]).convert('RGB'))
              for r in refs.values()}
    with np.load(prepared_path.parent / prepared['masks_file'], allow_pickle=False) as archive:
        masks = {str(r['frame']): archive[str(r['frame'])].copy() for r in refs.values()}
    query_frame = plan['source_id'] + ':' + str(plan['frame_index'])
    images[query_frame], masks[query_frame] = image, mask
    ref_xy = {k: base.local_xy(r['source_xy']) for k, r in refs.items()}
    decode_seconds = time.monotonic() - started
    encoder = base.Encoder(plan['resources'])
    controls = pixel_controls(base, encoder)
    rows = []
    for query in queries:
        row = {'query': query, 'status': 'NOT_RUN', 'modes': {}}
        rows.append(row)
        if controls['status'] != 'PASS':
            continue
        if time.monotonic() - started > plan['resources']['full_seconds_limit']:
            row['reason'] = 'time_budget_exceeded'
            continue
        sx, sy = query['source_xy']
        ox, oy = plan['geometry']['source_origin_xy']
        xy = (sx - ox + offset[0], sy - oy + offset[1])
        assert [xy[0] + ox - offset[0], xy[1] + oy - offset[1]] == query['source_xy']
        columns = common_columns([(mask, xy)] + [(masks[str(r['frame'])], ref_xy[k]) for k, r in refs.items()])
        row.update(padded_xy=list(xy), common_columns=columns, status='UNAVAILABLE_COMMON_SUPPORT_OR_CROP')
        if not columns:
            continue
        row['token_weights'] = {'query': weight_record(xy, columns, image.shape[0]),
            'references': {k: base.weight_record(ref_xy[k], columns) for k in refs}}
        row['status'] = 'MEASURED'
        for mode in ('full', 'local'):
            q = base.descriptor(encoder.saved(images, masks, query_frame, xy, mode), *strips(xy, columns, image.shape[0]))
            bank = {k: base.descriptor(encoder.saved(images, masks, r['frame'], ref_xy[k], mode, reference=True),
                                       *base.strips(ref_xy[k], columns)) for k, r in refs.items()}
            row['modes'][mode] = base.rank(q, bank, required=3)
    summaries = {}
    for interval in position['proposed_ranges']:
        group = [r for r in rows if r['query']['range_id'] == interval['id']]
        summaries[interval['id']] = {'contained_boundary_role': interval['role'], 'anchors': len(group),
            'statuses': dict(Counter(r['status'] for r in group)),
            'preferences': {m: dict(Counter(r['modes'].get(m, {}).get('preference') or 'UNAVAILABLE_OR_TIE'
                                           for r in group)) for m in ('full', 'local')}}
    result = {'schema': 's11-cr1-public-transfer-readout-v1', 'preflight_sha256': base.sha(manifest_path),
        'status': 'COMPLETE_DIAGNOSTIC_ONLY' if all(r['status'] != 'NOT_RUN' for r in rows) else 'INCOMPLETE',
        'source_id': plan['source_id'], 'frame_index': plan['frame_index'], 'timestamp_sec': plan['timestamp_sec'],
        'pixel_controls': controls, 'geometry': plan['geometry'], 'results': rows, 'range_summaries': summaries,
        'physical_accuracy': 'NOT_EVALUATED', 'candidate_selection': 'NOT_EVALUATED', 'tau_support': None,
        'partition': 'EXPOSED_CROSS_SOURCE_DEVELOPMENT', 'untouched_holdout_recordings': 0,
        'foam_upper_prototype': 'ABSENT', 'production_changed': False, 'video_decode': False,
        'resources': {'elapsed_sec': time.monotonic() - started, 'saved_raster_decode_seconds': decode_seconds,
            'encoder_load_seconds': encoder.load_seconds, 'forward_count': len(encoder.times),
            'forward_seconds': encoder.times, 'peak_rss_bytes': base.rss(),
            'workspace_allocated_bytes': base.allocated(base.WORKSPACE), 'retained_token_maps': 0},
        'runtime_guard': {'denied_events': denied, 'scope': 'Python audit events; not OS-level confinement'},
        'backend_pin_count': len(backend_pins), 'packages': {p: version(p) for p in plan['packages']}}
    for path, digest in {**plan['pins'], **backend_pins}.items():
        assert base.sha(ROOT / path) == digest, path
    assert result['resources']['workspace_allocated_bytes'] + plan['external_allocated_reservation_bytes'] < 3_000_000_000
    base.write(output, result)
    assert output.stat().st_size <= plan['resources']['run_output_bytes_limit']
    print(json.dumps({'status': result['status'], 'pixel_controls': controls, 'ranges': summaries,
                      'forward_count': len(encoder.times), 'elapsed_sec': result['resources']['elapsed_sec']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    run(args.manifest.resolve(), args.output.resolve())
