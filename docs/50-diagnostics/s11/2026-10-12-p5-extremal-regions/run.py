"""Execute the frozen P5-S3 stages from saved rasters, without video replay."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_case(root, case):
    """Read the three pinned artifact formats; no live detector or image repair."""
    import cv2
    import numpy as np
    if case['kind'] == 'default_images':
        images = {k: cv2.imread(str(root/p), cv2.IMREAD_UNCHANGED)
                  for k, p in case['images'].items()}
        if any(value is None for value in images.values()):
            raise ValueError('missing saved image')
        return (images['grayscale'], images['canny'] > 0,
                (images['effective_mask'] > 0) & (images['glare_mask'] == 0))
    with np.load(root/case['raster'], allow_pickle=False) as data:
        gray = cv2.cvtColor(data['crop'], cv2.COLOR_BGR2GRAY)
        visible = data['visible'].copy()
    if case['kind'] == 'water_stages':
        with np.load(root/case['stage'], allow_pickle=False) as data:
            assert np.array_equal(gray, data['gray'])
            edges = data['canny'] > 0
    else:
        with np.load(root/case['graph'], allow_pickle=False) as data:
            edges, visible = data['edges'].copy(), data['visible'].copy()
    return gray, edges, visible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    sys.path[:0] = [str(root/'src'), str(root)]
    import cv2
    import numpy as np
    from tests.diagnostics.s11_side_texture_probe import measure_extremal_regions
    from tests.unit.test_s11_extremal_regions import scene

    here = Path(__file__).resolve().parent
    pre = json.loads((here/'preflight.json').read_text())
    inventory = root/pre['inventory']['path']
    snapshot = root/pre['source_snapshot']['path']
    assert sha(inventory) == pre['inventory']['sha256']
    assert sha(snapshot) == pre['source_snapshot']['sha256']
    old = json.loads(inventory.read_text())
    source = json.loads(snapshot.read_text())['source_files']
    pins = {str(p.relative_to(root)): sha(p) for p in (
        here/'preflight.json', here/'run.py', inventory, snapshot,
        root/'tests/diagnostics/s11_side_texture_probe.py',
        root/'tests/unit/test_s11_extremal_regions.py')}
    source_checks = []

    def verify_sources():
        assert all(sha(root/p) == value for p, value in source.items())
        source_checks.append(len(source))

    def pin_case(case):
        paths = list(case.get('images', {}).values())
        paths += [case[k] for k in ('raster', 'stage', 'graph') if k in case]
        for path in paths:
            assert sha(root/path) == old['inputs'][path], path
            pins[path] = old['inputs'][path]

    verify_sources()
    synthetic = []
    for kind in pre['synthetic']['cases']:
        gray, edges, visible = scene(kind)
        column = 0 if kind == 'cropped' else 48
        if kind == 'cropped':
            edges[:] = False
            edges[48, 0] = True
        result = measure_extremal_regions(gray, edges, visible, column=column)
        synthetic.append(dict(id=kind, measurement=result))
    by_id = {s['id']: s['measurement'] for s in synthetic}
    preference = lambda name, variant='integrated': by_id[name]['rows'][0][variant]
    synthetic_conditions = dict(
        positive_reachable=all(preference(k) == 'upper_like'
            for k in ('stationary', 'inclined', 'polarity', 'printed_copy')),
        contrast_duration_adds_opposition=(preference('weak_contrast') == 'low_support'
            and preference('weak_contrast', 'ablated') == 'upper_like'),
        internal_opposition=preference('internal_cells') == 'internal_like',
        plain_opposition=all(preference(k) == 'low_support' for k in ('structural_step', 'uniform')),
        missing_unavailable=all(preference(k) == 'UNAVAILABLE'
            for k in ('missing_upper', 'partial', 'cropped')),
        copy_collision=by_id['stationary'] == by_id['printed_copy'],
        warped_copy_collision=by_id['optical_warp'] == by_id['warped_printed_copy'])

    cases = []
    representative = []
    conditions = {}
    seconds = 0.0
    if all(synthetic_conditions.values()):
        started = time.perf_counter()
        for case_id in pre['representative_case_ids']:
            case = next(c for c in old['cases'] if c['id'] == case_id)
            pin_case(case)
            gray, edges, visible = load_case(root, case)
            assert list(gray.shape) == case['shape']
            measurement = measure_extremal_regions(gray, edges, visible, column=case['column'])
            assert [r['row'] for r in measurement['rows']] == np.flatnonzero(
                edges[:, case['column']] & visible[:, case['column']]).tolist()
            for row in measurement['rows']:
                row['source_y'] = case['origin'][1]+(row['row']+.5)*case['scale_xy'][1]-.5
            cases.append(dict(id=case_id, measurement=measurement))
        seconds = time.perf_counter()-started
        ref = pre['evaluation_only']['foam_positive']
        queries = [dict(id='sample4-upper', case_id='s4-f1620', role='Foam upper',
                        interval=ref['source_y_cell_bounds'])]
        queries += [dict(id=q['label'], case_id=f"water-f{q['frame_index']:06d}",
                         role=q['role'], interval=q['interval'])
                    for q in pre['evaluation_only']['abc']]
        for query in queries:
            saved = next(c for c in cases if c['id'] == query['case_id'])
            rows = [r for r in saved['measurement']['rows']
                    if query['interval'][0] <= r['source_y'] <= query['interval'][1]]
            representative.append(dict(query, rows=rows,
                status='OBSERVED' if rows else 'NO_OBSERVED_CENTER_EDGE'))
        foam = [q for q in representative if q['role'].startswith('Foam')]
        water = [q for q in representative if q['role'].startswith('Water')]
        conditions = dict(
            both_foam_uppers_retained=all(any(r['integrated'] == 'upper_like'
                for r in q['rows']) for q in foam),
            both_water_surfaces_opposed=all(q['rows'] and all(
                r['integrated'] in ('low_support', 'internal_like') for r in q['rows']) for q in water),
            resource_time=seconds <= pre['resource']['representative_seconds_limit'])
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == 'darwin' else rss*1024
    if conditions:
        conditions['resource_memory'] = rss_bytes <= pre['resource']['process_peak_rss_bytes_limit']
    stage_pass = all(synthetic_conditions.values()) and bool(conditions) and all(conditions.values())
    # A successful stage is a checkpoint for the frozen broader comparison.
    # This runner deliberately stops before that separately invoked stage.
    disposition = 'REPRESENTATIVE_PASS_BROADER_STAGE_PENDING' if stage_pass else 'CLOSED_WITHOUT_PROMOTION'
    texture = next(q for q in pre['evaluation_only']['p2_queries'] if q['id'] == 's4-texture-f1620')
    s4 = next((c for c in cases if c['id'] == 's4-f1620'), None)
    texture_rows = [] if s4 is None else [r for r in s4['measurement']['rows'] if r['source_y'] == texture['source_xy'][1]]
    verify_sources()
    assert all(sha(root/p) == value for p, value in pins.items())
    result = dict(schema='s11-p5-extremal-regions-readout-v1',
        execution_head=subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
        inputs=pins, synthetic=synthetic, synthetic_conditions=synthetic_conditions,
        cases=cases, qualified_queries=representative, representative_conditions=conditions,
        internal_guide=dict(reference=texture, rows=texture_rows,
            status='OBSERVED' if texture_rows else 'NO_OBSERVED_CENTER_EDGE'),
        broader_inventory=[dict(id=c['id'], status='REPRESENTATIVE_ONLY' if c['id'] in pre['representative_case_ids'] else 'NOT_RUN') for c in old['cases']],
        disposition=disposition, physical_decision='UNRESOLVED', selected_scalar=None,
        runtime=dict(python=sys.version.split()[0], numpy=np.__version__, opencv=cv2.__version__,
            representative_seconds=seconds, process_peak_rss_bytes=rss_bytes),
        verification=dict(source_files_checked_before_and_after=source_checks, input_hashes_preserved=True,
            observed_queries=sum(len(c['measurement']['rows']) for c in cases)),
        production_changed=False, video_decoded=False, episode_changed=False, field_disposition='FIELD FAIL')
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('disposition', 'synthetic_conditions', 'representative_conditions', 'runtime', 'verification')}))
    for query in representative:
        print(query['id'], [(r['source_y'], r['integrated'], r['ablated'],
            [r[side].get('integrated', r[side].get('reason')) for side in ('upper', 'lower')]) for r in query['rows']])


if __name__ == '__main__':
    main()
