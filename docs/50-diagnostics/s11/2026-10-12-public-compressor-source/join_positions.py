"""Join the closed position ranges to saved captures; no detector or video runs.

This artifact adapter reads the current-frame capture schema. Earlier interval
reproducers are bound to different historical captures, so their inference and
source readers are not copied here. A compatible scalar or pooled sector sample
is never promoted to an observed, physically identified fixed-column contour.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path

import numpy as np


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    base = root / 'docs/50-diagnostics/s11/2026-10-12-public-compressor-source'
    captures = base / 'current-frame'
    pins = {}

    def read(path, expected=None):
        data = path.read_bytes()
        actual = digest(data)
        if expected is not None:
            assert actual == expected, str(path)
        pins[str(path.relative_to(root))] = actual
        return data

    reply = json.loads(read(base / 'position-review/position-review.json'))
    assert reply['status'] == 'CLOSED_USER_CONFIRMED_BOTH_RANGES'
    assert reply['confirmed_range_ids'] == ['A', 'B']
    read(base / 'position-review' / reply['figure']['file'], reply['figure']['sha256'])
    read(base / 'native-at-50.png', reply['source_image_sha256'])
    report = json.loads(read(captures / 'current-frame-readout.json'))
    pre = json.loads(read(base / 'current-frame-preflight.json', report['preflight_sha256']))
    read(base / 'inspect_detector.py', report['runner_sha256'])
    for name, expected in {**pre['inputs'], **pre['source_files']}.items():
        read(root / name, expected)
    storage = json.loads(read(captures / 'capture-storage.json'))
    logical = {}
    for name, expected in report['outputs'].items():
        entry = storage['outputs'][name]
        data = read(captures / entry['stored_path'], entry['stored_sha256'])
        assert len(data) == entry['stored_bytes']
        assert entry['encoding'] in ('identity', 'gzip')
        decoded = gzip.decompress(data) if entry['encoding'] == 'gzip' else data
        assert digest(decoded) == expected == entry['logical_sha256']
        assert len(decoded) == entry['logical_bytes']
        logical[name] = decoded
    for variant in ('native', 'half'):
        assert logical[f'{variant}-none.json'] == logical[f'{variant}-full.json']

    case = next(c for c in report['cases'] if c['variant']['id'] == 'native')
    raw = json.loads(logical['native-none.json'])
    state = json.loads(logical['native-diagnostics.json'])['state']
    assert raw['frame_index'] == reply['frame_index']
    assert raw['time_sec'] == reply['timestamp_sec']
    ox, oy = case['crop_origin']
    x = reply['source_x'] - ox
    assert x == case['center_column']
    assert reply['source_x'] == case['native_source_center_x']
    bands = {r['id']: r['source_y_cell_bounds'] for r in reply['proposed_ranges']}

    def memberships(y):
        return [key for key, (lo, hi) in bands.items() if lo <= y <= hi]

    def gap(y, key):
        lo, hi = bands[key]
        return max(lo - y, 0, y - hi)

    with np.load(io.BytesIO(logical['native-images.npz']), allow_pickle=False) as images:
        for name, item in case['images'].items():
            array = images[name]
            assert digest(array.tobytes()) == item['array_sha256']
        visible = (images['effective_mask'] > 0) & (images['glare_mask'] == 0)
        edges = (np.flatnonzero((images['canny'][:, x] > 0) & visible[:, x]) + oy).tolist()
        assert edges == [r['native_source_y'] for r in case['visible_center_edges']]
        components = state['foam_component_diagnostics']
        selected = next(c for c in components['components'] if c['selected_component'])
        assert selected['label'] == components['selected_label']
        # The retained label raster uses diagnostic_id, not the generator label.
        labels = images['foam_component_labels']
        rows = np.flatnonzero((labels[:, x] == selected['diagnostic_id']) & visible[:, x]) + oy
        runs = []
        for y in map(int, rows):
            if runs and y == runs[-1][1] + 1:
                runs[-1][1] = y
            else:
                runs.append([y, y])
        stage_rows = []
        for band in reply['proposed_ranges']:
            lo, hi = band['source_rows_inclusive']
            for y in range(lo, hi + 1):
                stage_rows.append({
                    'range_id': band['id'], 'source_y': y,
                    'visible': bool(visible[y - oy, x]),
                    'canny': bool(images['canny'][y - oy, x]),
                    'component_diagnostic_id': int(labels[y - oy, x]),
                    **{key: int(images[key][y - oy, x]) for key in (
                        'foam_mask', 'foam_material_support_mask', 'foam_whiteness',
                        'foam_texture_evidence', 'foam_combined_evidence')},
                })

    candidate_rows = []
    interfaces = {c['candidate_input_index']: c for c in state['oil_interface_diagnostics']['candidates']}
    for i, candidate in enumerate(raw['candidates']):
        path = interfaces.get(i, {}).get('path_aligned', {})
        center_sector = [s for s in path.get('sectors', [])
                         if s['source_x_range'][0] <= reply['source_x'] < s['source_x_range'][1]]
        candidate_rows.append({
            'candidate_input_index': i,
            **{key: candidate[key] for key in ('kind', 'source', 'y', 'selected', 'rejected', 'reject_reason')},
            'scalar_range_membership_only': memberships(candidate['y']),
            'native_path_status': path.get('status', 'not_captured_for_this_family'),
            'center_sector_samples': [
                {'source_x_range_half_open': s['source_x_range'],
                 'pooled_path_source_y': s['path_source_y'],
                 'scalar_range_membership_only': memberships(s['path_source_y'])}
                for s in center_sector],
            'certified_fixed_column_physical_contour': False,
        })
    front = selected['source_front_y']
    result = {
        'schema': 's11-public-source-reviewed-position-join-v1',
        'method': 'Exposed saved-data join. Containment is evaluated after immutable capture; no inference, rerun, tuning or physical candidate labels.',
        'frame_index': reply['frame_index'], 'timestamp_sec': reply['timestamp_sec'],
        'source_x': reply['source_x'], 'confirmed_ranges': reply['proposed_ranges'],
        'all_visible_center_canny_rows': edges,
        'range_canny_rows': {key: [y for y in edges if key in memberships(y)] for key in bands},
        'candidates': candidate_rows, 'reviewed_range_stage_pixels': stage_rows,
        'oil_current': {
            'raw_y': raw['raw_oil_air_level_y'], 'public_current_y': raw['oil_air_level_y'],
            'range_membership': memberships(raw['raw_oil_air_level_y']),
            'distance_to_oil_interval_px': gap(raw['raw_oil_air_level_y'], 'B'),
            'decision_reason': state['oil_decision_reason'],
            'selected_hypothesis_id': state['oil_selected_hypothesis_id'],
            'scope': 'Provisional current-frame scalar; not a completed-window result or exact-Y error.',
        },
        'foam_spatial': {
            'generator_label': selected['label'], 'diagnostic_id': selected['diagnostic_id'],
            'status': selected['decision_status'], 'component_front_y': front,
            'distance_to_foam_interval_px': gap(front, 'A'),
            'visible_selected_support_center_runs_inclusive': runs,
            'range_membership': memberships(front),
            'raw_current_y': raw['raw_foam_front_y'], 'public_current_y': raw['foam_front_y'],
            'temporal_pending_count': state['foam_temporal_pending_count'],
            'temporal_required_count': state['foam_temporal_required_count'],
            'scope': 'The component front misses the reviewed interval before temporal publication. Support occupancy is not a physical contour; fresh-frame pending is not an episode failure.',
        },
        'half_resolution': {
            'reviewed_accuracy': 'NOT_EVALUATED',
            'reason': 'Rounded center projects to X578.5, not the reviewed native X578; no truth transfer.',
        },
        'verification': {'logical_capture_hashes': len(logical), 'production_hashes': len(pre['source_files']),
                         'native_candidate_joins': len(candidate_rows), 'native_center_edges': len(edges),
                         'reviewed_range_pixels': len(stage_rows), 'none_full_byte_equal': True},
        'input_sha256': pins, 'reproducer_sha256': digest(Path(__file__).read_bytes()),
    }
    assert all(digest((root / name).read_bytes()) == value for name, value in pins.items())
    with output.open('x') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('range_canny_rows', 'oil_current', 'foam_spatial', 'verification')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
