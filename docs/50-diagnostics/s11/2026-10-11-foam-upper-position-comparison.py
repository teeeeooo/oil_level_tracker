"""Join qualified source intervals to immutable saved observations, without inference.

Run with the repository Python, --root <repo> --output <new JSON path>.
No video, preprocessing, detector, proposed selector or episode is executed.
This is an exposed-evidence audit, not a frozen prospective efficacy experiment.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

import cv2
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    directory = 'docs/50-diagnostics/s11/'
    inputs = {}

    def pin(name, expected=None):
        path = root / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if isinstance(expected, dict):
            expected = expected['sha256']
        if expected is not None and actual != expected:
            raise ValueError(f'input changed: {name}')
        if name in inputs and inputs[name] != actual:
            raise ValueError(f'input changed during audit: {name}')
        inputs[name] = actual
        return path

    def document(name):
        return json.loads(pin(directory + name).read_text())

    def archive(name, expected):
        with np.load(pin(name, expected), allow_pickle=False) as saved:
            return {key: saved[key].copy() for key in saved.files}

    reply = document('2026-10-11-foam-upper-position-reply.json')
    question = document('2026-10-11-foam-upper-position-review.json')
    assert reply['status'] == 'CLOSED'
    pin(reply['question_record']['path'], reply['question_record']['sha256'])
    pin(reply['source_figure']['path'], reply['source_figure']['sha256'])
    for name, expected in question['inputs'].items():
        pin(name, expected)
    reference = reply['reviewed_references'][0]
    ox, oy = reference['source']['crop_origin_xy']
    sx = reference['source_x']
    x = sx - ox
    lo, hi = reference['source_y_cell_bounds']

    gap = document('2026-10-09-foam-upper-gap-representation.json')
    graph = document('2026-10-09-observed-edge-fragments.json')
    abc = document('2026-10-10-abc-source-interval-comparison.json')
    water = document('2026-10-10-water-foam-representation.json')
    production = document('2026-10-11-p2-shared-support/preflight.json')['production_sources']
    for name, expected in production.items():
        pin(name, expected)
    for name in [
        '2026-10-10-upper-projection-ac-reply.json',
        '2026-10-10-upper-projection-interval-reply.json',
        '2026-10-10-water-lower-interface-reply.json',
        '2026-10-10-later-water-role-reply.json',
        '2026-10-09-public-beer-layer-reply.json',
        '2026-10-09-public-milk-interface-reply.json',
    ]:
        document(name)
    trace_name = next(n for n in gap['bracket_preflight']['inputs'] if n.endswith('debug_trace.jsonl'))
    trace = pin(trace_name, gap['bracket_preflight']['inputs'][trace_name])
    frames = gap['bracket_preflight']['frames']
    records = {}
    with trace.open() as stream:
        for line in stream:
            record = json.loads(line)
            if record['frame_index'] in frames:
                assert record['frame_index'] not in records
                records[record['frame_index']] = record
    assert set(records) == set(frames)
    brackets_name = next(n for n in gap['artifacts'] if n.endswith('/brackets.json'))
    brackets = json.loads(pin(brackets_name, gap['artifacts'][brackets_name]).read_text())
    verified_peaks = 0
    verified_pairs = 0
    sample4 = []

    for frame in frames:
        record = records[frame]
        arrays = {}
        for key in ['original_roi', 'grayscale', 'canny', 'effective_mask', 'glare_mask', 'foam_component_labels']:
            name = str((trace.parent / record['images'][key]).relative_to(root))
            path = pin(name, gap['bracket_preflight']['inputs'][name])
            arrays[key] = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
            assert arrays[key] is not None
        gray = arrays['grayscale']
        labels = arrays['foam_component_labels']
        assert np.array_equal(cv2.cvtColor(arrays['original_roi'], cv2.COLOR_BGR2GRAY), gray)
        capture_name = f'sample/output/s11-foam-upper-gap-20261009-001/capture-f{frame}.npz'
        capture = archive(capture_name, gap['artifacts'][capture_name])
        assert np.array_equal(labels, capture['labels'])
        visible = (arrays['effective_mask'] > 0) & (arrays['glare_mask'] == 0)
        assert np.array_equal(visible, capture['visible'])
        current_graph = next(r for r in graph['readout']['results'] if r['case_id'] == f's4-f{frame}')
        g = archive(current_graph['arrays_path'], current_graph['arrays_sha256'])
        assert np.array_equal(g['edges'], arrays['canny'] > 0)
        assert np.array_equal(g['visible'], visible)
        edge_rows = (np.flatnonzero((arrays['canny'][:, x] > 0) & visible[:, x]) + oy).tolist()
        graph_rows = sorted((g['vertices_xy'][g['vertices_xy'][:, 0] == x, 1] + oy).tolist())
        assert edge_rows == graph_rows

        # Independent one-column byte arithmetic; no diagnostic helper imports.
        valid = np.zeros(gray.shape[0], dtype=bool)
        valid[1:-1] = (visible[1:-1, x] & visible[:-2, x] & visible[2:, x]
                       & visible[1:-1, x-1] & visible[1:-1, x+1])
        delta = np.zeros(gray.shape[0], dtype=np.int16)
        delta[1:-1] = gray[2:, x].astype(np.int16) - gray[:-2, x].astype(np.int16)

        def plateaus(values, start, stop):
            found = []
            for first in range(start + 1, stop - 1):
                if not valid[first-1:first+1].all() or values[first] <= max(0, values[first-1]):
                    continue
                last = first + 1
                while last < stop and valid[last] and values[last] == values[first]:
                    last += 1
                if last < stop and valid[last] and values[last] < values[first]:
                    found.append((first, last))
            return found

        component_records = record['state']['foam_component_diagnostics']
        assert not component_records['truncated']
        saved = next(c for c in brackets['cases'] if c['frame_index'] == frame)
        center_components = []
        for component in saved['components']:
            rows = np.flatnonzero(labels[:, x] == component['component_id'])
            columns = [c for c in component['columns'] if c['source_x'] == sx]
            assert bool(rows.size) == bool(columns)
            if not rows.size:
                continue
            column = columns[0]
            assert (rows[0] + oy, rows[-1] + oy) == (column['support_top_source_y'], column['support_bottom_source_y'])
            for view in column['views']:
                start, stop = (y - oy for y in view['source_y_range'])
                absolute = plateaus(np.abs(delta), start, stop)
                assert [[a+oy, b+oy] for a, b in absolute] == [p['source_y_range'] for p in view['peaks']]
                for (a, _), peak in zip(absolute, view['peaks']):
                    assert abs(abs(int(delta[a])) / 510 - peak['vertical_magnitude']) < 1e-15
                verified_peaks += len(absolute)
                ordered = sorted([(a, b, -1) for a, b in plateaus(-delta, start, stop)]
                                 + [(a, b, 1) for a, b in plateaus(delta, start, stop)])
                pairs = []
                for (a, b, sign), (c, d, next_sign) in zip(ordered, ordered[1:]):
                    if (sign, next_sign) != (-1, 1) or not valid[a-1:d+1].all():
                        continue
                    trough = gray[b-1:c+1, x]
                    minimum = int(trough.min())
                    above, below = int(gray[a-1, x]), int(gray[d, x])
                    if minimum < min(above, below):
                        pairs.append(dict(upper_edge_source_y_range=[a+oy, b+oy],
                            lower_edge_source_y_range=[c+oy, d+oy],
                            trough_sample_source_y_range=[b-1+oy, c+1+oy],
                            minimum_source_y_values=(np.flatnonzero(trough == minimum)+b-1+oy).tolist(),
                            raw_gray_above_minimum_below=[above, minimum, below],
                            physical_gap_identity='UNRESOLVED', selected_foam_front=None))
                assert pairs == view['gap_brackets']
                verified_pairs += len(pairs)
            center_components.append(dict(diagnostic_id=component['component_id'], **column))
        center_pixels = [dict(source_y=y+oy, gray=int(gray[y, x]),
            raw_white=bool(capture['raw_white'][y, x]), clean_white=bool(capture['clean_white'][y, x]),
            diagnostic_label=int(labels[y, x]), visible=bool(visible[y, x])) for y in range(gray.shape[0])]
        sample4.append(dict(frame_index=frame, source_x=sx, origin=[ox, oy],
            center_pixels=center_pixels, all_visible_canny_center_rows=edge_rows,
            graph_center_rows=graph_rows, all_center_components=center_components,
            all_component_metadata=component_records,
            current_foam_candidates=[c for c in record['candidates'] if c['kind'] == 'foam_front'],
            current_positions=record['positions'], sequence_positions=record['sequence']['positions'],
            sequence_foam_witness=record['sequence']['state'].get('sequence_foam_decision_witness'),
            position_scoring='QUALIFIED' if frame == reference['frame_index'] else 'UNAVAILABLE_NO_INTERVAL_LABEL'))

    target = next(r for r in sample4 if r['frame_index'] == reference['frame_index'])
    selected = next(c for c in target['all_component_metadata']['components'] if c['selected_component'])
    in_band = lambda y: lo <= y <= hi
    target_comparison = dict(reference=reference,
        raw_canny_compatible_rows=[y for y in target['all_visible_canny_center_rows'] if in_band(y)],
        scalar_candidates=[dict(candidate_input_index=c['candidate_input_index'], source_y=c['canonical_y'],
            compatible=in_band(c['canonical_y'])) for c in target['current_foam_candidates']],
        selected_component_global_top=selected['source_bbox_xyxy'][1],
        global_top_compatible=in_band(selected['source_bbox_xyxy'][1]),
        selected_component_global_bottom=selected['source_bbox_xyxy'][3]-1,
        raw_candidate_min_distance_to_interval=max(lo-selected['source_front_y'], selected['source_front_y']-hi, 0),
        compatible_peaks=[dict(diagnostic_id=c['diagnostic_id'], radius_px=v['radius_px'], **p)
            for c in target['all_center_components'] for v in c['views'] for p in v['peaks']
            if any(in_band(y) for y in range(*p['source_y_range']))],
        current_smoothed_value_is_not_a_same_frame_front=True,
        prediction='NOT_EVALUATED', selected_front=None)

    # Recheck A/B/C native interval joins from their unchanged saved arrays.
    water_comparisons = []
    for old in abc['readout']['references']:
        ref = old['reference']
        frame, wx = ref['frame_index'], ref['source_x'] - 740
        low, high = ref['interval']
        base = f'sample/output/s11-water-foam-support-20261010-002/f{frame:06d}.npz'
        stage = f'sample/output/s11-water-foam-support-20261010-002/stages/f{frame:06d}.npz'
        a = archive(base, water['local_artifacts'][base])
        s = archive(stage, water['local_artifacts'][stage])
        rows = (np.flatnonzero(s['canny'][:, wx] > 0)+250).tolist()
        assert rows == old['all_canny_center_rows']
        crossings = [dict(source_y=float(p[1])/2, inside_label=int(a['inside_label'][i]),
            outside_label=int(a['outside_label'][i]), status=int(a['status'][i]))
            for i, (p, q) in enumerate(zip(a['start_xy2'], a['end_xy2']))
            if p[1] == q[1] and min(p[0], q[0]) <= 2*ref['source_x'] < max(p[0], q[0])]
        assert crossings == old['all_appearance_crossings']
        for sample in old['reference_stage_samples']:
            wy = sample['source_y'] - 250
            for key in ['lightness', 'whiteness', 'texture', 'raw_white_support', 'white_clean',
                        'chromatic_support', 'recovered_droplet_support', 'support']:
                actual = s[key][wy, wx].item()
                assert (bool(actual) if type(sample[key]) is bool else actual) == sample[key]
            assert int(s['retained_labels'][wy, wx]) == sample['retained_label']
        water_comparisons.append(old)

    # Retain the complete previous graph control inventory; verify every array pin.
    for result in graph['readout']['results']:
        pin(result['arrays_path'], result['arrays_sha256'])
    script = Path(__file__).resolve()
    script_name = str(script.relative_to(root))
    pin(script_name)
    for name, expected in list(inputs.items()):
        pin(name, expected)
    result = dict(schema='s11-qualified-foam-upper-position-comparison-v1',
        base_head=subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
        operation='Post-qualification join to already exposed saved evidence. No new inference or outcome-conditioned generator.',
        inputs=inputs, runner=dict(path=script_name, sha256=inputs[script_name]),
        sample4_saved_centers=sample4, qualified_sample4_comparison=target_comparison,
        qualified_water_comparisons=water_comparisons,
        preserved_graph_control_inventory=graph['readout']['results'],
        verification=dict(passed=True, sample4_frames=len(sample4), native_water_frames=len(water_comparisons),
            saved_graphs_hash_verified=len(graph['readout']['results']), direct_byte_peaks=verified_peaks,
            direct_byte_gap_pairs=verified_pairs, production_files_hash_verified=len(production),
            all_input_hashes_preserved=True, original_equals_saved_gray=True,
            all_center_graph_vertices_equal_saved_visible_canny=True,
            method='Direct byte differences and plateau/corridor enumeration without importing the probe; native masks, graph centers, stage arrays and all retained face crossings independently rejoined.'),
        limits='Only f1620/X595 is newly position-qualified. Other sample4 rows keep regional/qualitative roles; f1635 is unreviewed. A is Foam-upper; B/C are no-Foam water-upper. Beer and milk retain rear/front projection, cropped-upper and unclear-lower limits. All are exposed development evidence, not independent holdouts. No exact-Y error, physical classifier, full contour or accepted episode is established.',
        production_changed=False, detector_executed=False, video_decoded=False, episode_changed=False,
        legacy_truth_changed=False, selected_front=None, field_disposition='FIELD FAIL')
    with output.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(result['verification']))
    print(json.dumps(target_comparison, ensure_ascii=False))


if __name__ == '__main__':
    main()
