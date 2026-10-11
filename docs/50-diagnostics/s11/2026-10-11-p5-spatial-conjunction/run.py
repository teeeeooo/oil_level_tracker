"""Run one frozen offline P5-S2 comparison, without video or detector execution."""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import resource
import subprocess
import sys
import time


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
    from tests.diagnostics.s11_side_texture_probe import measure_spatial_conjunction
    here = Path(__file__).resolve().parent
    pre_path = here/'preflight.json'
    pre = json.loads(pre_path.read_text())

    def sha(path):
        with path.open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()

    def verify():
        for name, expected in pre['inputs'].items():
            if sha(root/name) != expected:
                raise ValueError(f'changed input: {name}')

    def load(name):
        with np.load(root/name, allow_pickle=False) as data:
            return {k: data[k].copy() for k in data.files
                    if k in ('crop', 'gray', 'edges', 'canny', 'visible')}

    verify()
    y, x = np.indices((97, 97))
    cells = np.clip(220-12*((x % 8-4)**2+(y % 8-4)**2), 20, 220)
    native = np.where(y >= 48, cells, 40).astype(np.uint8)
    edge = np.zeros(native.shape, bool)
    edge[48] = True
    valid = np.ones(native.shape, bool)
    inclined = np.where(y >= 48+(x-48)//4, cells, 40).astype(np.uint8)
    warped = np.stack([np.roll(row, round(3*np.sin(i/7))) for i, row in enumerate(native)])
    missing = valid.copy(); missing[:47] = False
    partial = valid.copy(); partial[50:56, 43:53] = False
    synthetic = []
    for name, gray, visible in [('stationary', native, valid), ('inclined', inclined, valid),
                               ('polarity', 255-native, valid), ('printed_copy', native.copy(), valid),
                               ('optical_warp', warped, valid), ('warped_printed_copy', warped.copy(), valid),
                               ('missing_upper', native, missing), ('partial', native, partial),
                               ('uniform', np.full_like(native, 40), valid)]:
        synthetic.append(dict(id=name, measurement=measure_spatial_conjunction(gray, edge, visible, column=48)))
    same = lambda a, b: next(s['measurement'] for s in synthetic if s['id']==a) == next(s['measurement'] for s in synthetic if s['id']==b)
    assert same('stationary', 'printed_copy') and same('stationary', 'polarity')
    assert same('optical_warp', 'warped_printed_copy')

    started = time.perf_counter()
    cases = []
    for case in pre['cases']:
        if case['kind'] == 'public_graph':
            raster, graph = load(case['raster']), load(case['graph'])
            gray = cv2.cvtColor(raster['crop'], cv2.COLOR_BGR2GRAY)
            edges, visible = graph['edges'], graph['visible']
        elif case['kind'] == 'water_stages':
            raster, stage = load(case['raster']), load(case['stage'])
            gray, edges, visible = stage['gray'], stage['canny'] > 0, raster['visible']
            assert np.array_equal(gray, cv2.cvtColor(raster['crop'], cv2.COLOR_BGR2GRAY))
        else:
            images = {k: cv2.imread(str(root/p), cv2.IMREAD_UNCHANGED) for k,p in case['images'].items()}
            assert all(v is not None for v in images.values())
            gray, edges = images['grayscale'], images['canny'] > 0
            visible = (images['effective_mask'] > 0) & (images['glare_mask'] == 0)
        assert list(gray.shape) == case['shape']
        result = measure_spatial_conjunction(gray, edges, visible, column=case['column'])
        assert [r['row'] for r in result['rows']] == np.flatnonzero(edges[:,case['column']] & visible[:,case['column']]).tolist()
        assert len(result['rows']) <= pre['resource']['max_queries_per_raster']
        for row in result['rows']:
            row['source_y'] = case['origin'][1]+(row['row']+.5)*case['scale_xy'][1]-.5
        cases.append(dict(id=case['id'], frame=case['frame'],
            source_x=case['origin'][0]+(case['column']+.5)*case['scale_xy'][0]-.5,
            scale_xy=case['scale_xy'], measurement=result,
            counts={v:dict(Counter(r[v]['preference'] for r in result['rows'])) for v in ('joint','ablated')}))
    elapsed = time.perf_counter()-started
    verify()

    def interval(case_id, low, high):
        case = next(c for c in cases if c['id']==case_id)
        rows = [r for r in case['measurement']['rows'] if low <= r['source_y'] <= high]
        return dict(case_id=case_id, interval=[low,high], observed_rows=rows,
                    status='OBSERVED' if rows else 'NO_OBSERVED_CENTER_EDGE',
                    upper_cellular={v:any(r[v]['preference']=='upper_cellular' for r in rows) for v in ('joint','ablated')})

    ref = pre['evaluation_only']['foam_positive']
    qualified = [dict(role='Foam upper', **interval(f"s4-f{ref['frame_index']}", *ref['source_y_cell_bounds']))]
    for ref in pre['evaluation_only']['abc']:
        qualified.append(dict(role=ref['role'], **interval(f"water-f{ref['frame_index']:06d}", *ref['interval'])))
    guides = []
    for q in pre['evaluation_only']['p2_queries']:
        guides.append(dict(reference=q, **interval(f"s4-f{q['frame']}", q['source_xy'][1], q['source_xy'][1])))
    positive = [q for q in qualified if q['role'].startswith('Foam')]
    water = [q for q in qualified if q['role'].startswith('Water')]
    texture = [q for q in guides if q['reference']['label']=='internal_foam_texture']
    appearance_conditions = dict(
        all_qualified_foam_retained=all(q['upper_cellular']['joint'] for q in positive),
        all_water_measured_and_opposed=all(q['observed_rows'] and all(r['joint']['preference'] in ('internal_cellular','noncellular') for r in q['observed_rows']) for q in water),
        all_texture_measured_and_opposed=all(q['observed_rows'] and all(r['joint']['preference'] in ('internal_cellular','noncellular') for r in q['observed_rows']) for q in texture),
        added_discrimination_without_positive_loss=(all(q['upper_cellular']['joint'] for q in positive)
            and sum(q['upper_cellular']['joint'] for q in water+texture) < sum(q['upper_cellular']['ablated'] for q in water+texture)))
    disposition = 'CLOSED_WITHOUT_PROMOTION' if not all(appearance_conditions.values()) else 'BOUNDED_APPEARANCE_ONLY_REQUIRES_STRUCTURE_EVIDENCE'
    result = dict(schema='s11-p5-spatial-conjunction-readout-v1',
        execution_head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
        preflight_sha256=sha(pre_path), runner_sha256=sha(Path(__file__)),
        synthetic=synthetic, cases=cases, qualified_intervals=qualified, original_query_guides=guides,
        necessary_appearance_conditions=appearance_conditions, disposition=disposition,
        generic_adoption=False, structure_competition='Copied/warped cellular structure remains indistinguishable; noncellular is not a glass certificate.',
        physical_decision='UNRESOLVED', selected_scalar=None,
        verification=dict(inputs_preserved=True, all_center_edges_retained=True, raster_count=len(cases),
            query_count=sum(len(c['measurement']['rows']) for c in cases), same_support_ablation=True,
            printed_copy_equal=True, warped_copy_equal=True, polarity_equal=True),
        runtime=dict(python=sys.version.split()[0], numpy=np.__version__, opencv=cv2.__version__,
            measurement_seconds=elapsed, peak_rss_platform_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            rss_scope='fresh process including preparation, input loading and synthetic measurements'),
        production_changed=False, video_decoded=False, episode_changed=False, field_disposition='FIELD FAIL')
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
    print(json.dumps({k:result[k] for k in ('disposition','necessary_appearance_conditions','verification','runtime')}))


if __name__ == '__main__':
    main()
