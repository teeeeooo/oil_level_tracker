"""Verify the existing recorder's two default runs; never execute a detector.

Run with --root <repo> --runs <recording directory> --output <new JSON path>.
The preflight pins input/source/harness bytes. Original run directories are
required, and the output must not exist. Uses direct serialization and raster
arithmetic independently of the diagnostic measurement helpers.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json

import cv2
import numpy as np


def digest(value):
    # Match the original audit's documented asdict serialization.
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, runs, output = args.root.resolve(), args.runs.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    inputs = {}

    def pin(path, expected=None):
        path = path if path.is_absolute() else root / path
        with path.open('rb') as stream:
            value = hashlib.file_digest(stream, 'sha256').hexdigest()
        if expected is not None and value != expected:
            raise ValueError(f'changed input: {path}')
        name = path.relative_to(root).as_posix()
        if name in inputs and inputs[name] != value:
            raise ValueError(f'input changed during verification: {name}')
        inputs[name] = value
        return path

    def read(path):
        return json.loads(pin(path).read_text(encoding='utf-8'))

    here = Path(__file__).resolve().parent
    pre = read(here / 'preflight.json')
    for group in ('source_files', 'inputs', 'harness_files', 'records'):
        for name, expected in pre[group].items():
            pin(Path(name), expected)
    prior = read(root / next(n for n in pre['records'] if n.endswith('sample4-current-default.json')))
    saved = read(root / next(n for n in pre['records'] if n.endswith('foam-upper-position-comparison.json')))
    reply = read(root / next(n for n in pre['records'] if n.endswith('foam-upper-position-reply.json')))
    reference = reply['reviewed_references'][0]
    saved_frames = {r['frame_index']: r for r in saved['sample4_saved_centers']}
    # Preserve the original preflight, including its mistaken f1275-for-f420
    # transcription. Both frames already belong to the complete frozen run.
    # The join retains the union; no trial, measurement or output is retuned.
    foam_frames = sorted(set(pre['foam_frames']) | set(saved_frames))
    count = pre['expected_rows']
    none, full, equality, summaries = {}, {}, {}, {}
    for mode, data in [('none', none), ('full', full)]:
        summaries[mode] = read(runs / mode / 'summary.json')
        for name, expected in summaries[mode]['outputs'].items():
            pin(runs / mode / name, expected)
        for name in ('raw', 'completed', 'tracking', 'report'):
            data[name] = read(runs / mode / f'{name}.json')
        assert all(len(data[n]) == count for n in ('raw', 'completed', 'tracking'))
        assert summaries[mode]['rows'] == count
        assert summaries[mode]['scopes'] == []
        assert summaries[mode]['preflight_sha256'] == inputs[(here/'preflight.json').relative_to(root).as_posix()]
    assert summaries['none']['runtime'] == summaries['full']['runtime'] == prior['runtime']
    for name in none:
        assert none[name] == full[name], name
        equality[name] = dict(equal=True, canonical_sha256=digest(none[name]))
    for name in ('raw', 'completed'):
        assert [digest(v) for v in none[name]] == prior[name]
    bundle = Path(summaries['none']['report_bundle'])
    public = {}
    for name in ('tracking_data.csv', 'events.csv'):
        with pin(bundle / name).open(encoding='utf-8-sig', newline='') as stream:
            public[name] = [{k: v for k, v in row.items() if k != 'run_id'}
                            for row in csv.DictReader(stream)]
        assert public[name] == prior[name], name
    assert len(public['tracking_data.csv']) == count
    assert summaries['none']['fingerprint'] == summaries['full']['fingerprint'] == prior['fingerprint']
    indices = [d['frame_index'] for d in none['raw']]
    assert len(set(indices)) == count
    assert indices == [d['frame_index'] for d in none['completed']] == [r['frame_index'] for r in none['tracking']]
    by_frame = {frame: i for i, frame in enumerate(indices)}
    traces = list((runs / 'full').rglob('debug_trace.jsonl'))
    assert len(traces) == 1
    trace = pin(traces[0])
    selected = {}
    joined_candidates = 0
    rows = 0
    with trace.open() as stream:
        for line in stream:
            rec = json.loads(line)
            raw, done, tracking = (none[n][rows] for n in ('raw', 'completed', 'tracking'))
            assert rec['frame_index'] == raw['frame_index']
            assert rec['glass_id'] == raw['glass_id'] == done['glass_id'] == tracking['glass_id']
            assert rec['timestamp_sec'] == raw['time_sec'] == done['time_sec'] == tracking['timestamp_sec']
            assert len(rec['candidates']) == len(raw['candidates'])
            assert sorted(c['candidate_input_index'] for c in rec['candidates']) == list(range(len(raw['candidates'])))
            for c in rec['candidates']:
                original = raw['candidates'][c['candidate_input_index']]
                assert c['canonical_y'] == original['y']
                for key in ('kind', 'source', 'features', 'penalties', 'selected', 'rejected', 'reject_reason'):
                    assert c[key] == original[key], (rows, key)
                joined_candidates += 1
            for field, key in [('raw_oil_y', 'raw_oil_air_level_y'), ('raw_foam_y', 'raw_foam_front_y'),
                               ('smoothed_oil_y', 'smoothed_oil_air_level_y'), ('smoothed_foam_y', 'smoothed_foam_front_y')]:
                assert rec['positions'][field] == raw[key]
                assert rec['sequence']['positions'][field] == done[key]
            assert done['raw_oil_air_level_y'] == tracking['raw_oil_air_level_y']
            assert done['raw_foam_front_y'] == tracking['raw_foam_front_y']
            if rec['frame_index'] in foam_frames:
                selected[rec['frame_index']] = rec
            rows += 1
    assert rows == count and set(selected) == set(foam_frames)
    foam = []
    for frame in foam_frames:
        rec = selected[frame]
        old = saved_frames.get(frame)
        diagnostic = rec['state']['foam_component_diagnostics']
        if old is not None:
            assert diagnostic == old['all_component_metadata']
        ox, oy = diagnostic['crop_origin']
        x = pre['qualified_x'] - ox
        arrays = {}
        image_pins = {}
        for key in ('original_roi', 'grayscale', 'canny', 'effective_mask', 'glare_mask', 'foam_component_labels'):
            path = pin(trace.parent / rec['images'][key])
            image_pins[key] = dict(path=path.relative_to(root).as_posix(), sha256=inputs[path.relative_to(root).as_posix()])
            arrays[key] = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            assert arrays[key] is not None
        assert np.array_equal(cv2.cvtColor(arrays['original_roi'], cv2.COLOR_BGR2GRAY), arrays['grayscale'])
        visible = (arrays['effective_mask'] > 0) & (arrays['glare_mask'] == 0)
        edge_rows = (np.flatnonzero((arrays['canny'][:, x] > 0) & visible[:, x]) + oy).tolist()
        if old is not None:
            assert edge_rows == old['all_visible_canny_center_rows']
        for p in old['center_pixels'] if old is not None else []:
            y = p['source_y'] - oy
            assert p['gray'] == int(arrays['grayscale'][y, x])
            assert p['visible'] == bool(visible[y, x])
            assert p['diagnostic_label'] == int(arrays['foam_component_labels'][y, x])
        idx = by_frame[frame]
        foam.append(dict(frame_index=frame, timestamp_sec=rec['timestamp_sec'], image_inputs=image_pins,
            crop_origin=[ox, oy], source_x=pre['qualified_x'], visible_center_edge_rows=edge_rows,
            component_diagnostics=diagnostic,
            raw_candidates=[c for c in rec['candidates'] if c['kind'] == 'foam_front'],
            raw_positions=rec['positions'], sequence_positions=rec['sequence']['positions'],
            sequence_witness=rec['sequence']['state'].get('sequence_foam_decision_witness'),
            public_tracking=none['tracking'][idx], public_csv=public['tracking_data.csv'][idx],
            saved_source_join='EQUAL' if old is not None else 'NO_PRIOR_FOAM_SOURCE_JOIN',
            position_truth='QUALIFIED_INTERVAL' if frame == pre['qualified_foam_frame'] else 'UNAVAILABLE',
            frame_role='UNREVIEWED' if frame == 1635 else 'EXISTING_REVIEW_SCOPE'))
    target = next(r for r in foam if r['frame_index'] == pre['qualified_foam_frame'])
    lo, hi = reference['source_y_cell_bounds']
    compatible = [y for y in target['visible_center_edge_rows'] if lo <= y <= hi]
    raw_compatible = [c for c in target['raw_candidates'] if lo <= c['canonical_y'] <= hi]
    assert compatible == [813] and raw_compatible == []
    witness = target['sequence_witness']
    assert witness['candidate']['candidate_offset'] == target['raw_candidates'][0]['candidate_input_index']
    assert witness['candidate']['y'] == target['raw_candidates'][0]['canonical_y'] == 833
    oil = [dict(raw=none['raw'][by_frame[f]]['raw_oil_air_level_y'],
                tracking=none['tracking'][by_frame[f]], csv=public['tracking_data.csv'][by_frame[f]]) for f in pre['oil_frames']]
    pin(Path(__file__).resolve())
    for name, expected in list(inputs.items()):
        pin(Path(name), expected)
    result = dict(schema='s11-p5-default-linkage-readout-v1', base_head=pre['base_head'],
        inputs=inputs, run_summaries=summaries, equality=equality,
        control_reconciliation=dict(original_preflight_frames=pre['foam_frames'],
            actual_saved_source_frames=sorted(saved_frames), joined_union_frames=foam_frames,
            reason='Preflight transcribed f1275 in place of f420; preserve both in the already frozen full run. Initial verifier failed lookup; no replay or output retuning.'),
        verification=dict(passed=True, source_files=len(pre['source_files']), rows=rows,
            exact_current_candidates=joined_candidates, prior_raw_and_completed_hashes_equal=True,
            prior_tracking_and_events_equal=True, source_center_and_component_records_equal=True,
            diagnostic_equality=True, local_xy_off=True, inputs_preserved=True),
        trace_bytes=trace.stat().st_size, foam_frames=foam, oil_checkpoints=oil, events=public['events.csv'],
        qualified_reference=reference, compatible_observed_center_edges=compatible,
        compatible_raw_foam_candidates=raw_compatible,
        first_supported_harmful_stage='component-to-front reduction chooses internal Y833; current raw candidates contain no interval-compatible front',
        limits=['Controlled default UNKNOWN session, not unconfirmed AUTO operator setup.',
                'No role model, production fix, physical acceptance or independent report comprehension.',
                'No labels transferred to other frames; f1635 remains unreviewed.',
                'NONE writes the retained report bundle; FULL report model is compared, but a second HTML bundle is not rendered.',
                'Pipeline elapsed seconds exclude bundle rendering and are not comparable to the prior end-to-end 109-second receipt.'],
        field_disposition='FIELD FAIL', production_changed=False, episode_changed=False)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps(result['verification']))


if __name__ == '__main__':
    main()
