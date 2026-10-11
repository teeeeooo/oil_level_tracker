"""Independently reconstruct saved P2 costs directly from native pixel samples."""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import itertools
import json
import subprocess

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('frozen_p2_input_loader',HERE/'run.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


def same(a,b):
    if not np.isclose(a,b,rtol=0,atol=1e-13):
        raise AssertionError((a,b))


def check(readout_path,output):
    pre=loader.read(HERE/'preflight.json'); readout=loader.read(readout_path)
    assert readout['preflight_sha256']==loader.sha(HERE/'preflight.json')
    for path,digest in {**pre['inputs'],**pre['production_sources']}.items():
        assert loader.sha(ROOT/path)==digest,path
    images=loader.load_images(pre)

    def crop(frame,xy):
        x,y=map(int,xy); x-=543; y-=798
        return tuple(a[y-12:y+13,x-12:x+13] for a in images[frame])

    refs={role:crop(r['frame'],r['source_xy']) for role,r in pre['references'].items()}
    costs_checked=0; measured=0; unavailable=0; sample_values=0
    assert len(readout['results'])==len(pre['queries'])
    for row,q in zip(readout['results'],pre['queries'],strict=True):
        assert row['query']==q
        centers=sorted({int(np.floor(q['source_xy'][1])),int(np.ceil(q['source_xy'][1]))})
        assert [v['source_center_xy'] for v in row['variants']]==[[595,y] for y in centers]
        for variant in row['variants']:
            image,visible,edge=crop(q['frame'],variant['source_center_xy'])
            ys,xs=np.where(edge[10:15,5:20]); all_points=np.column_stack([xs+5,ys+10])
            for mode,result in variant['modes'].items():
                points=all_points if mode=='joint' else all_points[(all_points[:,0]>=10)&(all_points[:,0]<15)]
                full=all(np.any((points[:,0]>=lo)&(points[:,0]<hi)) for lo,hi in pre['parts_x'])
                reason=('missing_current_part' if mode=='joint' and not full else
                        'no_current_edge_support' if not len(points) else None)
                if reason:
                    assert result['status']=='UNAVAILABLE' and result['reason']==reason
                    assert result['appearance_preference'] is None
                    unavailable+=1; continue
                points=np.unique(points,axis=0)
                xy=sorted({(int(x),int(y)+dy) for x,y in points for dy in range(-2,3)})
                xy=np.array(xy); x,y=xy.T; px,py=points.T
                assert visible[y,x].all()
                shifts=[]
                for dx,dy in itertools.product(range(-2,3),repeat=2):
                    xx,yy=x+dx,y+dy
                    if xx.min()<0 or yy.min()<0 or xx.max()>=25 or yy.max()>=25:
                        continue
                    if all(mask[yy,xx].all() for _,mask,_ in refs.values()):
                        shifts.append([dx,dy])
                assert shifts==result['common_shifts_xy']
                assert xy.tolist()==result['sample_xy']
                assert points.tolist()==result['edge_points_xy']
                assert result['appearance_denominator']==3*len(xy)**2*255**2
                role_minima={}
                for role,(reference,_,ref_edges) in refs.items():
                    recorded=result['roles'][role]; costs=[]
                    assert len(recorded['costs'])==len(shifts)
                    for i,(dx,dy) in enumerate(shifts):
                        diff=image[y,x].astype(float)-reference[y+dy,x+dx].astype(float)
                        residual=diff-diff.mean(axis=0)
                        appearance=float(np.mean(residual*residual)/255**2)
                        geometry=1-float(np.count_nonzero(ref_edges[py+dy,px+dx])/len(points))
                        cost=(3*appearance+geometry)/4
                        same(appearance,recorded['appearance_costs'][i]);same(geometry,recorded['geometry_costs'][i])
                        same(cost,recorded['costs'][i]);costs.append(cost)
                        costs_checked+=1;sample_values+=diff.size
                    minimum=min(costs);same(minimum,recorded['best_cost'])
                    assert [s for s,c in zip(shifts,costs,strict=True) if abs(c-minimum)<=1e-12]==recorded['best_shifts_xy']
                    role_minima[role]=minimum
                ranks=sorted((v,k) for k,v in role_minima.items());margin=ranks[1][0]-ranks[0][0]
                preference=ranks[0][1] if ranks[0][0]<=.05 and margin>=.01 else None
                assert result['appearance_preference']==preference
                same(margin,result['best_role_margin'])
                assert result['physical_identity']=='UNRESOLVED' and result['selected_front'] is None
                measured+=1
        for mode in ['joint','center_only']:
            values=[v['modes'][mode] for v in row['variants']]
            preferences={v['appearance_preference'] for v in values}
            assert row['summary'][mode]==dict(measured=all(v['status']=='MEASURED' for v in values),
                                              preference=next(iter(preferences)) if len(preferences)==1 else None,
                                              fractional_agreement=len(preferences)==1)
    for mode in ['joint','center_only']:
        noninitial=[r for r in readout['results'] if not r['query']['initial_reference']]
        pos=[r for r in noninitial if r['query']['label']=='confirmed_target']
        neg=[r for r in noninitial if r['query']['label']=='rejected_target']
        assert len(pos)==6 and len(neg)==3
        assert sum(r['summary'][mode]['preference']=='interface' for r in pos)==0
        assert sum(r['summary'][mode]['measured'] and r['summary'][mode]['preference'] in ['structure','texture'] for r in neg)==0
        assert readout['counts'][mode]['measured_queries']==sum(r['summary'][mode]['measured'] for r in readout['results'])
    # A falsification witness, not a threshold sweep or adjusted operating point:
    # accepting this positive with max-cost/min-margin cannot reject the negative.
    rows={r['query']['id']:r for r in readout['results']}
    positive=rows['s4-f1320-idx9']['variants'][0]['modes']['joint']
    negative=rows['s4-f1260-idx15']['variants'][0]['modes']['joint']
    for value in [positive,negative]:
        assert min(value['roles'],key=lambda k:value['roles'][k]['best_cost'])=='interface'
    assert negative['roles']['interface']['best_cost']<positive['roles']['interface']['best_cost']
    assert negative['best_role_margin']>positive['best_role_margin']
    assert not readout['progression_passed'] and readout['disposition']=='CLOSED_WITHOUT_PROMOTION'
    # Existing helper bodies and constants are unchanged by the additive API.
    owner='tests/diagnostics/s11_boundary_temporal_probe.py'
    before=subprocess.check_output(['git','show',pre['starting_head']+':'+owner],cwd=ROOT,text=True)
    after=(ROOT/owner).read_text(encoding='utf-8')
    old=[ast.dump(n,include_attributes=False) for n in ast.parse(before).body]
    new=[ast.dump(n,include_attributes=False) for n in ast.parse(after).body]
    cursor=iter(new)
    for node in old:
        assert any(candidate==node for candidate in cursor)
    defs=[n.name for n in ast.parse(after).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
    assert len(defs)==len(set(defs))
    result=dict(status='PASS',readout_sha256=loader.sha(readout_path),
                preflight_sha256=loader.sha(HERE/'preflight.json'),
                verifier_sha256=loader.sha(Path(__file__)),
                execution_head=readout['execution_head'],
                input_pins_checked=len(pre['inputs']),production_sources_unchanged=len(pre['production_sources']),
                measured_variant_modes=measured,unavailable_variant_modes=unavailable,
                role_shift_costs_reconstructed=costs_checked,bgr_value_comparisons=sample_values,
                existing_helper_ast_preserved=True,all_ten_candidate_controls_retained=True,
                public_unavailable_groups_retained=len(pre['retained_unavailable']),
                cutoff_margin_dominance_witness=dict(
                    positive='s4-f1320-idx9',negative='s4-f1260-idx15',
                    positive_cost=positive['roles']['interface']['best_cost'],negative_cost=negative['roles']['interface']['best_cost'],
                    positive_margin=positive['best_role_margin'],negative_margin=negative['best_role_margin']),
                focused_tests=dict(passed=80,failures=0,command='.venv/bin/python -m pytest -q -p no:cacheprovider tests/unit/test_s11_shared_support_roles.py tests/unit/test_s11_reference_constellation.py tests/unit/test_s11_current_boundary_reference.py tests/unit/test_s11_boundary_temporal_probe.py tests/unit/test_s11_ordered_patch_correspondence.py',
                                   scope='pre-run test execution; frozen implementation has not changed'),
                physical_identity='NOT_EVALUATED',runtime_behavior_change=False)
    if output.exists():
        raise FileExistsError(output)
    loader.write(output,result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--readout',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();check(args.readout,args.out)
