"""Reconstruct every saved side from direct pixel indices, without the helper."""
from pathlib import Path
import argparse
import hashlib
import json

import cv2
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output.resolve()
    if out.exists():
        raise FileExistsError(out)
    here = Path(__file__).resolve().parent
    pins = {}

    def pin(path, expected=None):
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        assert expected is None or actual == expected, path
        pins[path.relative_to(root).as_posix()] = actual
        return path

    pre = json.loads(pin(here/'preflight.json').read_text())
    result = json.loads(pin(here/'readout.json').read_text())
    assert result['preflight_sha256'] == pins[(here/'preflight.json').relative_to(root).as_posix()]
    for name, expected in pre['inputs'].items():
        pin(root/name, expected)
    graph_record = json.loads((root/'docs/50-diagnostics/s11/2026-10-09-observed-edge-fragments.json').read_text())
    graphs = {g['case_id']:g for g in graph_record['readout']['results']}
    source = json.loads((here.parent/'2026-10-11-p5-default-linkage/preflight.json').read_text())['source_files']
    for name, expected in source.items():
        pin(root/name, expected)
    assert [c['id'] for c in result['cases']] == [c['id'] for c in pre['cases']]
    rows_verified = side_centers = prior_graphs = 0
    for case, saved in zip(pre['cases'], result['cases'], strict=True):
        if case['kind'] == 'default_images':
            images = {k:cv2.imread(str(root/p), cv2.IMREAD_UNCHANGED) for k,p in case['images'].items()}
            gray, edge = images['grayscale'], images['canny'] > 0
            visible = (images['effective_mask'] > 0) & (images['glare_mask'] == 0)
            if case['id'] in graphs:
                g = graphs[case['id']]
                with np.load(pin(root/g['arrays_path'], g['arrays_sha256']), allow_pickle=False) as data:
                    assert np.array_equal(edge, data['edges']) and np.array_equal(visible, data['visible'])
                name = next(n for n in graph_record['preflight']['inputs'] if f"f{case['frame']:09d}_" in n and '/original_roi_' in n)
                old = cv2.imread(str(pin(root/name, graph_record['preflight']['inputs'][name])))
                assert np.array_equal(gray, cv2.cvtColor(old, cv2.COLOR_BGR2GRAY))
                prior_graphs += 1
        elif case['kind'] == 'public_graph':
            with np.load(root/case['raster'], allow_pickle=False) as data:
                gray = cv2.cvtColor(data['crop'], cv2.COLOR_BGR2GRAY)
            with np.load(root/case['graph'], allow_pickle=False) as data:
                edge, visible = data['edges'], data['visible']
            prior_graphs += 1
        else:
            with np.load(root/case['stage'], allow_pickle=False) as data:
                gray, edge = data['gray'], data['canny'] > 0
            with np.load(root/case['raster'], allow_pickle=False) as data:
                visible = data['visible']
        h, w = gray.shape
        actual_rows = np.flatnonzero(edge[:,case['column']] & visible[:,case['column']]).tolist()
        assert actual_rows == [r['row'] for r in saved['measurement']['rows']]
        for row in saved['measurement']['rows']:
            ratios = {'joint':[], 'ablated':[]}
            available = True
            for name in ('upper','lower'):
                side = row[name]
                # Independently derive the request; do not trust saved bounds.
                b = min(32,max(4,round(min(h,w)*.06)))
                y0 = row['row']-2-b if name=='upper' else row['row']+3
                y1 = y0+b
                x0, x1 = case['column']-b, case['column']+b+1
                centers = [(y,x) for y in range(y0,y1) for x in range(x0,x1)
                           if 3 <= y < h-3 and 3 <= x < w-3]
                vector = []
                for y,x in centers:
                    pixels = [(y,x+3),(y,x+1),(y,x-3),(y,x-1),(y+3,x),(y+1,x),(y-3,x),(y-1,x)]
                    if all(visible[p] for p in pixels):
                        vector.append([int(gray[pixels[i]])-int(gray[pixels[i+1]]) for i in range(0,8,2)])
                assert len(vector) == side['available_centers']
                assert side['requested_centers'] == b*(2*b+1)
                side_centers += len(vector)
                if len(vector)<16:
                    assert side['status']=='UNAVAILABLE'
                    available = False
                    continue
                v = np.asarray(vector, dtype=np.int32)
                radial = np.maximum(0,np.maximum(v.min(axis=1),-v.max(axis=1)))
                axis = [np.maximum(0,np.maximum(v[:,a:a+2].min(axis=1),-v[:,a:a+2].max(axis=1))) for a in (0,2)]
                denominator = int(np.maximum(*axis).sum())
                a, b = int(radial.sum()), int((axis[0]+axis[1]).sum())
                assert [a,denominator,b] == [side['joint_sum'],side['axis_sum'],side['ablated_sum_twice']]
                ratios['joint'].append(a/denominator if denominator else 0.)
                ratios['ablated'].append(b/(2*denominator) if denominator else 0.)
            for variant in ('joint','ablated'):
                if not available:
                    assert row[variant]['preference']=='UNAVAILABLE'
                    continue
                cost = {key:sum((v-t)**2 for v,t in zip(ratios[variant],target,strict=True))/2
                        for key,target in pre['models'].items()}
                for key,value in cost.items():
                    assert abs(value-row[variant]['costs'][key]) < 1e-12
                ordered = sorted(cost,key=cost.get)
                margin = cost[ordered[1]]-cost[ordered[0]]
                decision = ordered[0] if cost[ordered[0]]<=pre['max_cost'] and margin>=pre['min_margin'] else 'AMBIGUOUS'
                assert decision == row[variant]['preference']
            assert row['physical_role']=='UNRESOLVED' and not row['scalar_eligible']
            rows_verified += 1
    assert prior_graphs == 25 and rows_verified == result['verification']['query_count']
    pin(Path(__file__).resolve())
    proof = dict(schema='s11-p5-spatial-conjunction-verification-v1',passed=True,
        method='Direct query-centered integer pixel enumeration, without importing the measurement helper.',
        rasters=len(pre['cases']), rows=rows_verified, available_side_centers=side_centers,
        prior_graph_inputs_equal=prior_graphs, production_hashes_unchanged=len(source),
        all_side_sums_costs_and_decisions_equal=True, physical_scalar_count=0, inputs=pins)
    with out.open('x', encoding='utf-8') as stream:
        json.dump(proof,stream,indent=2,ensure_ascii=False)
        stream.write('\n')
    print(json.dumps({k:v for k,v in proof.items() if k!='inputs'}))


if __name__=='__main__':
    main()
