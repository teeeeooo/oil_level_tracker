#!/usr/bin/env python3
"""Read-only audit of the frozen S2 operating geometry; no detector or tuning."""
import argparse, collections, hashlib, json, math
from pathlib import Path
P = Path('docs/50-diagnostics/s11/2026-10-11-p5-spatial-conjunction')
def audit(root):
    data = json.loads((root/P/'readout.json').read_text())
    mf = root/P/'preflight.json'
    assert hashlib.sha256(mf.read_bytes()).hexdigest() == data['preflight_sha256']
    counts = collections.Counter(); prefs = {k:collections.Counter() for k in ['joint','ablated']}
    ranges = []; qualified = []
    for case in data['cases']:
        counts['rasters'] += 1
        for row in case['measurement']['rows']:
            counts['queries'] += 1
            for v in prefs: prefs[v][row[v]['preference']] += 1
            for side in [row['upper'],row['lower']]:
                if side['status'] != 'AVAILABLE':
                    counts['unavailable_sides'] += 1; continue
                counts['available_sides'] += 1
                p, z = side['axis_sum'], side['ablated_sum_twice']
                if p:
                    assert p <= z <= 2*p
                    assert math.isclose(side['ablated_ratio'], z/(2*p), abs_tol=1e-12)
                    ranges.append(side['ablated_ratio']); counts['contrast_positive_sides'] += 1
                else:
                    assert side['ablated_ratio'] == 0
                    counts['zero_contrast_sides'] += 1
            for v, key in [('joint','joint_ratio'),('ablated','ablated_ratio')]:
                a,b = row['upper'].get(key),row['lower'].get(key)
                if a is None or b is None: continue
                c=row[v]['costs']; expected={'upper_cellular':(a*a+(b-1)**2)/2,
                    'internal_cellular':((a-1)**2+(b-1)**2)/2,'noncellular':(a*a+b*b)/2}
                for name,val in expected.items():
                    assert math.isclose(c[name],val,rel_tol=1e-11,abs_tol=1e-12)
                assert math.isclose(c['upper_cellular']-c['noncellular'],0.5-b,abs_tol=1e-12)
                assert math.isclose(c['upper_cellular']-c['internal_cellular'],a-0.5,abs_tol=1e-12)
                counts['verified_variant_cost_triples'] += 1
    for item in data['qualified_intervals']:
        rows=[]
        for r in item['observed_rows']:
            a,b=r['upper']['joint_ratio'],r['lower']['joint_ratio']
            rows.append({'source_y':r['source_y'],'upper_joint_ratio':a,'lower_joint_ratio':b,
                'upper_ablated_ratio':r['upper']['ablated_ratio'],'lower_ablated_ratio':r['lower']['ablated_ratio'],
                'CU_minus_CN':0.5-b,'CU_minus_CI':a-0.5,'joint_preference':r['joint']['preference'],
                'ablated_preference':r['ablated']['preference']})
        qualified.append({'case_id':item['case_id'],'role':item['role'],'interval':item['interval'],'rows':rows})
    return {'schema':'s11-direction-s2-decision-geometry-audit-v1',
        'inputs':{str(P/'readout.json'):hashlib.sha256((root/P/'readout.json').read_bytes()).hexdigest(),
                  str(P/'preflight.json'):hashlib.sha256(mf.read_bytes()).hexdigest()},
        'counts':dict(counts),'preferences':{k:dict(v) for k,v in prefs.items()},
        'ablated_nonzero_contrast_range':[min(ranges),max(ranges)],'qualified_intervals':qualified,
        'equations':{'CU_minus_CN':'0.5-b','CU_minus_CI':'a-0.5','upper_unique':'a<0.5 and b>0.5',
            'upper_margin_005':'a<=0.45 and b>=0.55 plus cost gate','ablated_range':'0.5<=r0<=1 for sum(P)>0'},
        'new_classifier':False,'thresholds_changed':False,'production_changed':False,
        'physical_acceptance':'NOT_EVALUATED'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True); p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists(): p.error('Refusing to overwrite output')
    result=audit(a.root.resolve()); a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f: json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
    print(json.dumps({'status':'VERIFIED','counts':result['counts'],'preferences':result['preferences']}))
