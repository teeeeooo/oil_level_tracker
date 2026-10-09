"""Independent saved-pixel oracle; reads all frozen CBR-1 outcomes without rerunning it."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
pre, result = read(OUT/'preflight.json'), read(OUT/'readout.json')
assert sha(OUT/'preflight.json') == result['preflight_sha256']
for path, expected in {**pre['inputs'], **pre['production_source_pins']}.items():
    assert sha(ROOT/path) == expected, path
assert sha(ROOT/'tests/diagnostics/s11_boundary_temporal_probe.py') == pre['helper_sha256']
assert sha(ROOT/'tests/diagnostics/s11_contour_contact_probe.py') == pre['geometry_owner_sha256']
assert sha(OUT/'run.py') == pre['runner_sha256']
graphs = read(ROOT/'sample/output/s11-seed-observed-edges-20261009-001/readout.json')
supports = read(ROOT/'sample/output/s11-reference-current-perimeters-20261009-001/readout.json')
gp = {r['frame']: r['graph_path'] for p in graphs['results'] for r in p['rows']}
sp = {r['frame']: r['support_path'] for p in supports['results'] for r in p['rows']}
ox, oy = pre['origin']; cx = pre['center_x']; offset = pre['operation']['side_offset']
cache = {}
def arrays(f):
    if f not in cache:
        with np.load(ROOT/sp[f], allow_pickle=False) as s, np.load(ROOT/gp[f], allow_pickle=False) as g:
            assert np.array_equal(s['visible'], g['visible'])
            assert np.array_equal(g['vertices_xy'], np.argwhere((g['canny']>0)&g['visible'])[:, ::-1]+[ox,oy])
            cache[f] = (s['crop'].copy(), s['visible'].copy(), g['vertices_xy'].copy(),
                        g['fragment_offsets'].copy(), g['fragment_vertices'].copy())
    return cache[f]

totals = Counter(); plans = []
for plan, group in zip(pre['plans'], result['results'], strict=True):
    assert [r['frame'] for r in group['rows']] == plan['frames']
    ref = {x:y for x,y in set(map(tuple, plan['points_source_xy']))}
    assert len(ref) == len(set(map(tuple, plan['points_source_xy'])))
    anchor, av, *_ = arrays(plan['start'])
    counters = Counter(); winner_pairs = Counter(); center_pairs = Counter(); grid = []
    witnesses = []
    for summary in group['rows']:
        f = summary['frame']; first = f == plan['start']
        assert summary['initialized'] == first and summary['analysis_grid'] == (f%15 == 0)
        path = OUT/summary['detail']
        assert sha(path) == summary['detail_sha256'] == result['details'][path.name]
        detail = json.loads(gzip.decompress(path.read_bytes()))
        assert detail['frame'] == f and detail['reference_frame'] == plan['start']
        assert detail['physical_decision'] == 'NOT_EVALUATED' and detail['selected_front'] is None
        image, visible, vertices, offsets, ids = arrays(f)
        assert len(detail['candidates']) == len(offsets)-1 == summary['geometry_candidates']
        qualified = []; states = Counter(); with_ref = with_pairs = preferred = 0
        for i, row in enumerate(detail['candidates']):
            totals['candidates'] += 1
            xy = sorted(set(map(tuple, vertices[ids[offsets[i]:offsets[i+1]]].tolist())))
            center = sorted(y for x,y in xy if x==cx)
            common = sorted({x for x,y in xy} & ref.keys())
            assert row['candidate_id'] == i and row['center_crossings'] == center
            assert row['requested_columns'] == common
            with_ref += bool(common)
            if not first and center:
                counters['center_fragments'] += 1
                counters['center_fragments_with_reference_columns'] += bool(common)
            ambiguous = any(sum(px==x for px,py in xy)>1 for x in common)
            expected_samples = []; missing = []
            if not ambiguous:
                for x in common:
                    y = next(py for px,py in xy if px==x); ry = ref[x]
                    px, py, rpy = x-ox,y-oy,ry-oy
                    if not (offset <= rpy < av.shape[0]-offset and av[rpy,px] and av[rpy-offset,px] and av[rpy+offset,px]):
                        missing.append(dict(source_x=x, reason='reference_side_unavailable'))
                    elif not (offset <= py < visible.shape[0]-offset and visible[py-offset,px] and visible[py+offset,px]):
                        missing.append(dict(source_x=x, reason='current_side_unavailable'))
                    else:
                        expected_samples.append(dict(current_xy=[x,y], reference_xy=[x,ry],
                            current_a=image[py-offset,px].tolist(), current_b=image[py+offset,px].tolist(),
                            reference_a=anchor[rpy-offset,px].tolist(), reference_b=anchor[rpy+offset,px].tolist()))
            assert row['samples'] == expected_samples and row['missing'] == missing
            assert row['structure_status'] == 'NOT_MEASURED' and row['structure_loss'] is None
            totals['sample_pairs'] += len(expected_samples)
            assert row['structure_reason'] == 'not_supplied'
            costs = None; appearance = 'UNAVAILABLE'
            if ambiguous:
                reason = 'ambiguous_current_column'
            elif not expected_samples:
                reason = 'no_common_visible_pairs'
            else:
                with_pairs += 1
                costs = {}
                for name, choices in {'AB':('a','b'), 'BA':('b','a'), 'AA':('a','a'), 'BB':('b','b')}.items():
                    costs[name] = sum(abs(sample['current_'+side][ch]-sample['reference_'+target][ch])
                                      for sample in expected_samples for side,target in zip(('a','b'),choices) for ch in range(3))
                totals['losses'] += 4
                appearance = 'PROVISIONAL_AB' if costs['AB'] < min(costs[k] for k in ('BA','AA','BB')) else 'UNRESOLVED'
                reason = None if appearance == 'PROVISIONAL_AB' else 'ordered_sides_not_strictly_preferred'
                assert row['denominator'] == 6*len(expected_samples)
            assert row['losses'] == costs and row['appearance'] == appearance and row['reason'] == reason
            if costs is None: assert row['denominator'] is None
            states[reason or 'provisional'] += 1
            if appearance == 'PROVISIONAL_AB':
                preferred += 1
                if center:
                    qualified.append(row)
                    if not first:
                        center_pairs[len(expected_samples)] += 1
            if not first and center:
                counters['center_fragments_with_visible_pairs'] += bool(expected_samples)
        center_ys = [y for row in qualified for y in row['center_crossings']]
        expected_y = qualified[0]['center_crossings'][0] if len(qualified)==1 and len(center_ys)==1 else None
        reason = 'unique_provisional_center' if expected_y is not None else ('ambiguous_provisional_center' if qualified else 'no_provisional_center')
        assert detail['provisional_y'] == summary['provisional_y'] == expected_y
        assert detail['reason'] == summary['reason'] == reason and detail['status'] == summary['status'] == 'MEASURED'
        assert dict(states) == summary['candidate_reasons']
        assert with_ref == summary['candidates_with_reference_columns'] and with_pairs == summary['candidates_with_visible_pairs']
        assert preferred == summary['provisional_role_candidates'] and len(qualified) == summary['provisional_center_candidates']
        assert center_ys == summary['all_provisional_center_y']
        if not first:
            counters[reason] += 1
            if expected_y is not None: winner_pairs[len(qualified[0]['samples'])] += 1
            if summary['analysis_grid']: grid.append(dict(frame=f, reason=reason, provisional_y=expected_y))
        if f in pre['review_frames'][plan['id']]:
            witnesses.append(dict(frame=f, candidates=[dict(candidate_id=r['candidate_id'], center_crossings=r['center_crossings'],
                pairs=len(r['samples']), losses=r['losses'], current_xy=[s['current_xy'] for s in r['samples']]) for r in qualified]))
        totals['queries'] += 1
    assert dict(Counter(r['reason'] for r in group['rows'][1:])) == group['summary']['states']
    assert [[r['frame'],r['provisional_y']] for r in group['rows'][1:] if r['provisional_y'] is not None] == group['summary']['outputs']
    for present, key in ((True,'longest_unique_native_frame_run'),(False,'longest_missing_native_frame_run')):
        lengths = ''.join('1' if (r['provisional_y'] is not None)==present else '0' for r in group['rows'][1:]).split('0')
        assert max(map(len,lengths)) == group['summary'][key]
    assert sum(r['provisional_y'] is not None for r in grid) == group['summary']['analysis_grid_unique_provisional']
    plans.append(dict(plan=plan['id'], reference_includes_center_x=cx in ref,
        continuation_counters=dict(counters), unique_winner_support_pairs=dict(winner_pairs),
        all_provisional_center_support_pairs=dict(center_pairs), analysis_grid=grid, reviewed_witnesses=witnesses))
assert totals['queries'] == result['query_count'] == 198 and len(cache) == result['unique_rasters'] == 167
receipt = dict(schema='s11-cbr1-independent-verification-v1', status='PASS', totals=dict(totals), unique_rasters=len(cache),
    preflight_sha256=sha(OUT/'preflight.json'), readout_sha256=sha(OUT/'readout.json'), verifier_sha256=sha(Path(__file__)),
    input_pins=len(pre['inputs']), production_source_pins=len(pre['production_source_pins']), plans=plans,
    scope='All saved query/candidate mappings, visible BGR pairs, four exact losses, missingness, center decisions and summaries independently reconstructed from original NPZ arrays. No comparator import; no runtime or video decode.',
    physical_efficacy='NOT_EVALUATED')
with (OUT/'verification.json').open('x') as f: f.write(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
