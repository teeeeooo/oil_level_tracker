"""Frozen CBR-1 current-geometry comparison; no video decode or runtime writes."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT/'src')]
os.environ.setdefault('MPLCONFIGDIR', '/tmp/s11-cbr1-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tests.diagnostics.s11_boundary_temporal_probe import compare_current_boundary_reference, CURRENT_BOUNDARY_SPEC

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())

def write(name, data):
    p = OUT/name
    with p.open('x') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')

def longest(rows, predicate):
    run = best = 0
    for row in rows:
        run = run+1 if predicate(row) else 0
        best = max(best, run)
    return best

prior = ROOT/'sample/output/s11-material-reference-20261009-001/preflight.json'
edge_record = ROOT/'sample/output/s11-seed-observed-edges-20261009-001/readout.json'
support_record = ROOT/'sample/output/s11-reference-current-perimeters-20261009-001/readout.json'
old = read(prior); graphs = read(edge_record); supports = read(support_record)
origin = old['origin']; plans = old['plans']
review_frames = {'oil-positive': [1275, 1281, 1320, 1335, 1348, 1350],
                 'foam-positive': [420, 438, 450, 480, 495, 510],
                 'rim-opposition': [450, 465, 480]}
gp = {r['frame']: (r['graph_path'], r['graph_sha256']) for p in graphs['results'] for r in p['rows']}
sp = {r['frame']: (r['support_path'], r['support_sha256']) for p in supports['results'] for r in p['rows']}
inputs = {str(p.relative_to(ROOT)): sha(p) for p in (prior, edge_record, support_record, ROOT/'sample/sample4.oilrecipe')}
for f in sorted({f for p in plans for f in p['frames']}):
    for path, expected in (gp[f], sp[f]):
        assert sha(ROOT/path) == expected, path
        inputs[path] = expected
for plan in plans:
    binding = ROOT/plan['input_binding']; inputs[str(binding.relative_to(ROOT))] = sha(binding)
source_pins = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'src').rglob('*.py'))}
for p, expected in old['source_pins'].items(): assert source_pins[p] == expected, p
recipe = read(ROOT/'sample/sample4.oilrecipe')
center = int(np.floor(recipe['glasses'][0]['geometry']['ellipse']['center_x']+.5))
pre = {'schema': 's11-cbr1-frozen-preflight-v1', 'base_head': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
       'operation': CURRENT_BOUNDARY_SPEC, 'plans': plans, 'origin': origin, 'center_x': center,
       'geometry_input': 'Unchanged saved Canny/visibility and complete observed-edge fragment graphs. No support labels, LK coordinates or H0 arrays enter the comparator.',
       'structure_opposition': 'Original Structure role plan retained. No co-located structure reference exists on the full positive-role sample domain; NOT_MEASURED, never a favorable vote. Constructed equal-domain opposition is tested separately.',
       'reference_mapping': 'same source X; current per-fragment unique Y; +/-2 native rows; complete visible paired pixels; no interpolation or reference update',
       'common_support': 'AB,BA,AA,BB exact integer L1 on identical paired samples; expose missing reference/current columns and no-reference mappings',
       'partition': 'all exposed development/regression; no independent holdout',
       'progression': 'Sustained non-initial target-vicinity support on prior reviewed Oil 42.5-44s and Foam 14-16s without new long wrong-region runs across complete plans. Otherwise close fixed variant; no grouping/stencil/column/threshold tuning. Undecidable physical interpretations stop for user judgment.',
       'physical_truth': 'Existing regional replies only; no exact center labels or new physical annotations. Provisional appearance counts are not recall or accuracy.',
       'cadence': {'native_fps': 30, 'analysis_subset': 'absolute frame index divisible by 15; existing 0.5s grid, initialization excluded', 'temporal_dependency': 'none; no intermediate-frame input'},
       'ablation': None, 'review_frames': review_frames, 'inputs': inputs, 'production_source_pins': source_pins,
       'helper_sha256': sha(ROOT/'tests/diagnostics/s11_boundary_temporal_probe.py'), 'geometry_owner_sha256': sha(ROOT/'tests/diagnostics/s11_contour_contact_probe.py'),
       'runner_sha256': sha(Path(__file__)), 'scope': 'offline saved-array comparison only; no detector, video decode, Recipe/truth/report change or Windows work'}
write('preflight.json', pre)
print('PREFLIGHT', sha(OUT/'preflight.json'), flush=True)
cache = {}
def frame(f):
    if f not in cache:
        with np.load(ROOT/sp[f][0], allow_pickle=False) as a:
            image, visible = a['crop'].copy(), a['visible'].copy()
        with np.load(ROOT/gp[f][0], allow_pickle=False) as g:
            assert np.array_equal(visible, g['visible'])
            offsets, ids = g['fragment_offsets'], g['fragment_vertices']
            geometry = dict(spec_id='observed-edge-fragments-v1', origin=origin, shape=list(visible.shape),
                            vertices_xy=g['vertices_xy'].copy(), fragments=[ids[offsets[i]:offsets[i+1]].tolist() for i in range(len(offsets)-1)])
            assert np.array_equal(geometry['vertices_xy'], np.argwhere((g['canny']>0)&visible)[:, ::-1]+origin)
        cache[f] = image, visible, geometry
    return cache[f]

results = []; artifacts = {}; elapsed = 0
for plan in plans:
    initial, iv, _ = frame(plan['start']); points = np.asarray(plan['points_source_xy'], np.int64)
    rows = []
    for i, f in enumerate(plan['frames']):
        image, visible, geometry = frame(f)
        start = time.perf_counter()
        result = compare_current_boundary_reference(initial, image, iv, visible, points, geometry, origin=origin, center_x=center)
        duration = time.perf_counter()-start; elapsed += duration
        result.update(frame=f, role=plan['role'], reference_frame=plan['start'], reference_binding=plan['input_binding'])
        name = f'{plan["id"]}-f{f}.json.gz'; path = OUT/name
        with path.open('xb') as stream:
            stream.write(gzip.compress(json.dumps(result, separators=(',', ':'), allow_nan=False).encode(), mtime=0))
        artifacts[name] = sha(path)
        cs = result['candidates']; preferred = [c for c in cs if c['appearance']=='PROVISIONAL_AB']
        rows.append({'frame': f, 'time_s': f/30, 'initialized': i==0, 'analysis_grid': f%15==0,
                     'status': result['status'], 'reason': result['reason'], 'geometry_candidates': len(geometry['fragments']),
                     'candidates_with_reference_columns': sum(bool(c['requested_columns']) for c in cs),
                     'candidates_with_visible_pairs': sum(bool(c['samples']) for c in cs),
                     'provisional_role_candidates': len(preferred),
                     'provisional_center_candidates': sum(bool(c['center_crossings']) for c in preferred),
                     'all_provisional_center_y': [y for c in preferred for y in c['center_crossings']],
                     'provisional_y': result['provisional_y'], 'physical_decision': result['physical_decision'],
                     'provisional_support_pairs': [len(c['samples']) for c in preferred],
                     'candidate_reasons': dict(Counter(c['reason'] or 'provisional' for c in cs)),
                     'elapsed_s': duration, 'detail': name, 'detail_sha256': artifacts[name]})
    later = rows[1:]; grid = [r for r in later if r['analysis_grid']]
    s = {'plan': plan['id'], 'role': plan['role'], 'continuation_frames': len(later),
         'states': dict(Counter(r['reason'] for r in later)), 'unique_provisional': sum(r['provisional_y'] is not None for r in later),
         'longest_unique_native_frame_run': longest(later, lambda r: r['provisional_y'] is not None),
         'longest_missing_native_frame_run': longest(later, lambda r: r['provisional_y'] is None),
         'analysis_grid_continuation_frames': len(grid), 'analysis_grid_unique_provisional': sum(r['provisional_y'] is not None for r in grid),
         'outputs': [[r['frame'], r['provisional_y']] for r in later if r['provisional_y'] is not None]}
    results.append({'summary': s, 'rows': rows}); print(json.dumps(s), flush=True)
    picks = review_frames[plan['id']]
    fig, axs = plt.subplots(2, len(picks), figsize=(2.7*len(picks), 5.5), squeeze=False, layout='constrained')
    for j, f in enumerate(picks):
        image, _, _ = frame(f); row = next(r for r in rows if r['frame']==f)
        for k in (0, 1):
            axs[k,j].imshow(image[:,:,::-1], extent=(origin[0]-.5, origin[0]+103.5, origin[1]+103.5, origin[1]-.5), interpolation='nearest')
            axs[k,j].set_axis_off()
        axs[0,j].set_title(f'f{f} / {f/30:g}s original', fontsize=9)
        for y in row['all_provisional_center_y']:axs[1,j].plot([center-3,center+3],[y,y],color='#ff9900',linewidth=1.5)
        axs[1,j].set_title(f'appearance center Y={row["provisional_y"]}\n{row["reason"]}',fontsize=8)
    fig.suptitle(f'{plan["id"]}: orange=current appearance alternatives, not physical Oil/Foam truth',fontsize=10)
    fig.savefig(OUT/f'{plan["id"]}-review.png',dpi=130);plt.close(fig)
for name, expected in {**inputs, **source_pins}.items(): assert sha(ROOT/name)==expected, name
write('readout.json', {'schema':'s11-cbr1-readout-v1','preflight_sha256':sha(OUT/'preflight.json'),
                       'results':results,'unique_rasters':len(cache),'query_count':sum(len(r['rows']) for r in results),
                       'elapsed_comparison_s':elapsed,'details':artifacts,'inputs_and_production_unchanged':True,
                       'physical_efficacy':'NOT_EVALUATED','source_decode':False,'production_changed':False})
print('COMPLETE', str(OUT), flush=True)
