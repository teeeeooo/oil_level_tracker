"""Verify the frozen pipeline captures and join the reviewed native anchor.

Saved data only: no detector, decoder or production imports. The older sample4
linkage verifier binds historical receipts; this adapter reads the new archive.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
import zipfile

import cv2
import numpy as np


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    here = Path(__file__).resolve().parent
    pre_path = here / 'pipeline-preflight.json'
    pre = json.loads(pre_path.read_text())
    production = json.loads((root / pre['production_manifest']).read_text())['source_files']
    for path, expected in {**production, **pre['inputs']}.items():
        assert sha((root / path).read_bytes()) == expected, path
    assert sha((here / 'replay_pipeline.py').read_bytes()) == pre['runner_sha256']
    storage = json.loads((here / 'pipeline-linkage/storage.json').read_text())
    archive_path = here / 'pipeline-linkage/captures.zip'
    assert sha(archive_path.read_bytes()) == storage['archive_sha256']
    with zipfile.ZipFile(archive_path) as archive:
        blobs = {}
        assert len(archive.namelist()) == len(set(archive.namelist()))
        assert set(archive.namelist()) == {v['member'] for v in storage['files'].values()}
        for name, entry in storage['files'].items():
            data = archive.read(entry['member'])
            assert sha(data) == entry['sha256'] and len(data) == entry['bytes'], name
            blobs[name] = data
    read = lambda name: json.loads(blobs[name])
    summaries = {mode: read(f'{mode}/summary.json') for mode in pre['runs']}
    for mode, summary in summaries.items():
        assert summary['preflight_sha256'] == sha(pre_path.read_bytes())
        assert summary['runner_sha256'] == pre['runner_sha256']
        assert summary['rows'] == 3 and summary['decodes'] == 6
        assert summary['resources']['within_bounds'] and summary['pins_preserved']
        assert summary['production_files_unchanged'] == len(production)
        for name, expected in summary['outputs'].items():
            assert sha(blobs[f'{mode}/{name}']) == expected, (mode, name)
    assert summaries['NONE']['runtime'] == summaries['FULL']['runtime']
    assert summaries['NONE']['execution_head'] == summaries['FULL']['execution_head']
    equality = {}
    for name in ('raw', 'completed', 'tracking', 'report', 'decodes', 'recipe'):
        assert read(f'NONE/{name}.json') == read(f'FULL/{name}.json'), name
        equality[name] = True
    csv_rows = {}
    for name in ('tracking', 'events'):
        rows = []
        for mode in pre['runs']:
            stream = io.StringIO(blobs[f'{mode}/{name}.csv'].decode('utf-8-sig'))
            rows.append([{k: v for k, v in row.items() if k != 'run_id'}
                         for row in csv.DictReader(stream)])
        assert rows[0] == rows[1], name
        csv_rows[name] = rows[0]
        equality[f'{name}_csv_excluding_run_id'] = True
    decodes = read('FULL/decodes.json')
    assert len(decodes) == 6
    for actual, expected in zip(decodes, pre['window']['expected_decodes'] * 2):
        assert all(actual[k] == v for k, v in expected.items())
    raw, done, tracking = [read(f'FULL/{n}.json') for n in ('raw', 'completed', 'tracking')]
    assert [r['frame_index'] for r in raw] == [f['frame_index'] for f in pre['window']['expected_decodes']]
    names = [n for n in blobs if n.startswith('FULL/') and n.endswith('/debug_trace.jsonl')]
    assert len(names) == 1
    trace_name = names[0]
    traces = [json.loads(line) for line in blobs[trace_name].splitlines()]
    assert len(raw) == len(done) == len(tracking) == len(traces) == len(csv_rows['tracking']) == 3
    candidate_count = 0
    rows = []
    fields = [('raw_oil_y', 'raw_oil_air_level_y'), ('raw_foam_y', 'raw_foam_front_y'),
              ('smoothed_oil_y', 'smoothed_oil_air_level_y'), ('smoothed_foam_y', 'smoothed_foam_front_y')]
    for r, d, t, rec, public in zip(raw, done, tracking, traces, csv_rows['tracking']):
        assert rec['frame_index'] == r['frame_index'] == d['frame_index'] == t['frame_index'] == int(public['frame_index'])
        assert rec['timestamp_sec'] == r['time_sec'] == d['time_sec'] == t['timestamp_sec']
        assert sorted(c['candidate_input_index'] for c in rec['candidates']) == list(range(len(r['candidates'])))
        for c in rec['candidates']:
            source = r['candidates'][c['candidate_input_index']]
            assert c['canonical_y'] == source['y']
            for key in ('kind', 'source', 'features', 'penalties', 'selected', 'rejected', 'reject_reason'):
                assert c[key] == source[key], (r['frame_index'], key)
        # Sequence trace is a compact projection without original offsets.
        # The source/kind/Y tuples are unique in this saved capture; assert this
        # before joining instead of assuming trace order or inventing an index.
        completed_by_key = {(c['kind'], c['source'], c['y']): c for c in d['candidates']}
        compact = rec['sequence']['candidates']
        compact_keys = [(c['kind'], c['source'], c['canonical_y']) for c in compact]
        assert len(completed_by_key) == len(d['candidates']) == len(compact_keys) == len(set(compact_keys))
        assert set(compact_keys) == set(completed_by_key)
        for c, key in zip(compact, compact_keys):
            source = completed_by_key[key]
            assert c['selected'] == source['selected']
            for field in ('authority_reason', 'authority_failed_gates', 'phase_identity', 'tracklet_id'):
                assert c[field] == source['features'].get(f'sequence_{field}')
        candidate_count += len(r['candidates'])
        for field, key in fields:
            assert rec['positions'][field] == r[key]
            assert rec['sequence']['positions'][field] == d[key]
        for key in ('raw_oil_air_level_y', 'raw_foam_front_y'):
            assert d[key] == t[key]
            assert public[key] == ('' if t[key] is None else str(t[key]))
        for key, value in public.items():
            expected = ';'.join(t[key]) if key == 'flags' else ('' if t[key] is None else str(t[key]))
            assert value == expected, (r['frame_index'], key)
        rows.append({'frame_index': r['frame_index'], 'timestamp_sec': r['time_sec'],
                     'current_positions': rec['positions'], 'completed_positions': rec['sequence']['positions'],
                     'tracking': t, 'csv': public,
                     'oil_witness': rec['sequence']['state']['sequence_decision_witness'],
                     'foam_witness': rec['sequence']['state']['sequence_foam_decision_witness']})
    anchor = pre['truth_scope']
    index = [r['frame_index'] for r in raw].index(anchor['frame_index'])
    rec, r, d = traces[index], raw[index], done[index]
    diagnostic = rec['state']['foam_component_diagnostics']
    ox, oy = diagnostic['crop_origin']
    image_data = {}
    for key in ('original_roi', 'canny', 'effective_mask', 'glare_mask'):
        name = str(Path(trace_name).parent / rec['images'][key])
        image_data[key] = cv2.imdecode(np.frombuffer(blobs[name], dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        assert image_data[key] is not None
    baseline = json.loads((here / 'current-frame/current-frame-readout.json').read_text())['cases'][0]
    assert sha(image_data['original_roi'].tobytes()) == baseline['images']['original_roi']['array_sha256']
    x = anchor['source_x'] - ox
    visible = (image_data['effective_mask'] > 0) & (image_data['glare_mask'] == 0)
    edges = (np.flatnonzero((image_data['canny'][:, x] > 0) & visible[:, x]) + oy).tolist()
    distance = lambda y, interval: None if y is None else max(interval[0] - y, y - interval[1], 0.0)
    candidates = []
    for i, (a, b) in enumerate(zip(r['candidates'], d['candidates'])):
        assert a['y'] == b['y'] and a['source'] == b['source']
        interval = anchor['oil_cell_bounds'] if a['kind'] == 'oil_air' else anchor['foam_cell_bounds']
        candidates.append({'input_index': i, 'kind': a['kind'], 'source': a['source'], 'y': a['y'],
            'distance_to_reviewed_interval_px': distance(a['y'], interval),
            'current_selected': a['selected'], 'current_reject_reason': a['reject_reason'],
            'completed_selected': b['selected'], 'completed_reject_reason': b['reject_reason'],
            'sequence_features': {k: v for k, v in b['features'].items() if k.startswith('sequence_')}})
    selected = rows[index]['oil_witness']['selection']['selected_candidate']
    assert selected['y'] == d['raw_oil_air_level_y'] == d['candidates'][selected['candidate_offset']]['y']
    assert d['candidates'][selected['candidate_offset']]['selected']
    result = {'schema': 's11-public-source-pipeline-linkage-v1',
        'preflight_sha256': sha(pre_path.read_bytes()), 'verifier_sha256': sha(Path(__file__).read_bytes()),
        'storage_sha256': sha((here / 'pipeline-linkage/storage.json').read_bytes()),
        'run_summaries': summaries, 'equality': equality,
        'verification': {'passed': True, 'rows': len(rows), 'candidate_joins_current_and_completed': candidate_count,
                         'logical_output_count': len(blobs), 'unique_payload_count': len(set(v['member'] for v in storage['files'].values())),
                         'production_files_unchanged': len(production), 'anchor_native_crop_equal': True,
                         'csv_all_tracking_cells_match': True, 'source_decodes_equal': True},
        'rows': rows, 'anchor': {**anchor, 'current_positions': rec['positions'],
            'completed_positions': rec['sequence']['positions'], 'visible_center_edges': edges,
            'compatible_foam_edges': [y for y in edges if anchor['foam_cell_bounds'][0] <= y <= anchor['foam_cell_bounds'][1]],
            'compatible_oil_edges': [y for y in edges if anchor['oil_cell_bounds'][0] <= y <= anchor['oil_cell_bounds'][1]],
            'current_oil_distance_px': distance(r['raw_oil_air_level_y'], anchor['oil_cell_bounds']),
            'completed_oil_distance_px': distance(d['raw_oil_air_level_y'], anchor['oil_cell_bounds']),
            'current_foam_distance_px': distance(r['raw_foam_front_y'], anchor['foam_cell_bounds']),
            'all_candidates': candidates, 'component_diagnostics': diagnostic},
        'limits': [pre['fixture_scope'], pre['initial_state_authority'], anchor['limits'],
                   'No decoder/detector rerun during verification; no HTML/UI or Windows qualification.'],
        'production_changed': False, 'field_disposition': 'FIELD FAIL'}
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps(result['verification']))


if __name__ == '__main__':
    main()
