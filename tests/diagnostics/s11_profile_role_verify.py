"""Independent pixel, fit and publication checks for PWC-1 (not physical truth)."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import math
import cv2
import numpy as np
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from tests.diagnostics.s11_role_consumer_verify import check, verify_event_sample

MODEL_NAMES = ('affine', 'corner', 'jump', 'separate_slopes')


def load_gzip(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def preferred(errors, arm):
    target = 'jump' if arm == 'H1' else 'separate_slopes'
    better = lambda a, b: all(errors[a][f] + 1e-12 < errors[b][f] for f in (0, 1))
    if better(target, 'affine') and better(target, 'corner'): return 'JUMP_PREFERRED'
    if better('corner', 'affine') and better('corner', target): return 'CORNER_PREFERRED'
    return 'UNKNOWN'


def verify_measurement(row, gray, visible):
    ox, oy = row['origin']; h, w = gray.shape
    band = max(3, min(12, int(round(h * .01)))); length = 3 * band + 1
    check(row['band'] == band and row['length'] == length, 'measurement window drift')
    check(row['shape'] == [h, w] and row['native_path_created'] is False, 'raster/native claim')
    y = row['y']; lo = math.floor(y-oy)-length; hi = math.ceil(y-oy)+length
    ys = [i for i in range(lo, hi+1) if abs(i+oy-y) >= 2]
    sectors, errors, cells = [], {m: [] for m in MODEL_NAMES}, 0
    if min(ys) < 0 or max(ys) >= h:
        check(row['status'] == 'UNAVAILABLE_CROP' and not row['sectors'], 'crop censoring')
    else:
        for sector in range(5):
            x0, x1 = w*sector//5, w*(sector+1)//5
            xs = [x for x in range(x0, x1) if all(bool(visible[j, x]) for j in ys)]
            if len(xs) < 2 or len(xs)/(x1-x0) < .5: continue
            sectors.append(sector)
            saved = next(s for s in row['sectors'] if s['sector'] == sector)
            check(saved['columns'] == xs and saved['rows'] == [j+oy for j in ys], 'support/fold drift')
            values = np.array([sum(int(gray[j, x]) for x in xs)/(255*len(xs)) for j in ys])
            check(np.allclose(values, saved['values'], atol=1e-14, rtol=0), 'direct pixel means')
            cells += len(xs)*len(ys)
            z = np.array([(j+oy-y)/length for j in ys])
            sector_errors = {}
            for model in MODEL_NAMES:
                cols = [np.ones(len(ys)), z]
                if model in ('corner', 'separate_slopes'): cols.append(np.abs(z))
                if model in ('jump', 'separate_slopes'): cols.append(np.sign(z))
                matrix = np.column_stack(cols); predicted = []
                for parity in (0, 1):
                    train = np.array([(j+oy)%2 == parity for j in ys]); test = ~train
                    a, b = matrix[train], values[train]
                    beta = np.linalg.solve(a.T @ a, a.T @ b)
                    mse = float(np.mean((values[test] - matrix[test] @ beta)**2))
                    check(np.allclose(beta, saved['coefficients'][model][parity], atol=1e-9, rtol=0), 'independent coefficients')
                    check(abs(mse-saved['errors'][model][parity]) < 1e-10, 'independent fold MSE')
                    predicted.append(mse)
                sector_errors[model] = predicted
            for model in MODEL_NAMES: errors[model].append(sector_errors[model])
        check([s['sector'] for s in row['sectors']] == sectors, 'usable sector denominator')
        check(row['status'] == ('MEASURED' if sectors else 'UNAVAILABLE_SUPPORT'), 'availability claim')
    if sectors:
        aggregated = {m: np.mean(errors[m], axis=0).tolist() for m in MODEL_NAMES}
        for model in MODEL_NAMES:
            check(np.allclose(aggregated[model], row['errors'][model], atol=1e-10, rtol=0), 'sector balance')
        check(row['preferences'] == {a: preferred(aggregated, a) for a in ('H1', 'H2')}, 'independent preference')
    else:
        check(row['errors'] is None and all(v == 'UNKNOWN' for v in row['preferences'].values()), 'absence mislabel')
    return {'profile_count': len(sectors), 'pixel_references': cells}


def verify(root, directory):
    comparison = json.loads((directory/'comparison.json').read_text())
    measurements = load_gzip(directory/'measurements.json.gz')
    trace = load_gzip(directory/'readout.json.gz'); pre = comparison['preflight']
    check(pre == measurements['preflight'] == trace['preflight'], 'preflight binding')
    for rel, sha in {**pre['inputs'], **pre['source_hashes']}.items():
        check(hashlib.sha256((root/rel).read_bytes()).hexdigest() == sha, 'input/source mutation: '+rel)
    raw = json.loads((root/next(p for p in pre['inputs'] if p.endswith('/raw.json'))).read_text())
    original = {d['frame_index']: d for d in raw}
    recipe_path = next(p for p in pre['inputs'] if p.endswith('recipe_snapshot.oilrecipe'))
    glass = JsonRecipeRepository().load(root/recipe_path).glasses[0]
    frames = {}
    with OpenCvVideoReader(root/'sample/sample4.mp4') as reader:
        for d in raw:
            frame, index, time = reader.read_at(d['time_sec'])
            check(index == d['frame_index'] and abs(time-d['time_sec']) < 1e-6, 'source frame/time')
            masks = build_mask_bundle(frame, glass)
            processed = preprocess(masks.crop, masks.effective_mask, glass.detector_settings)
            visible = (masks.effective_mask > 0) & (processed.glare_mask == 0)
            frames[index] = (processed.gray, visible)
            saved = pre['source_binding']['frames'][f'sample4-f{index}']
            check(saved['origin'] == list(masks.crop_origin), 'frame origin')
            check(hashlib.sha256(processed.gray.tobytes()).hexdigest() == saved['gray_sha256'], 'frame pixels')
            check(hashlib.sha256(visible.tobytes()).hexdigest() == saved['visible_sha256'], 'frame visibility')
    expected_keys = [(d['frame_index'], i) for d in raw for i,c in enumerate(d['candidates']) if c['kind']=='oil_air']
    table = {(m['frame'],m['index']):m for m in measurements['sample4']}
    check(list(table) == expected_keys and len(table) == len(measurements['sample4']), 'complete pixel population')
    totals = Counter()
    for key, row in table.items():
        c = original[key[0]]['candidates'][key[1]]
        check((c['source'],c['y']) == (row['source'],row['y']), 'pixel candidate binding')
        totals.update(verify_measurement(row, *frames[key[0]]))
    prepared_path = next(p for p in pre['inputs'] if p.endswith('/prepared.json'))
    spec = json.loads((root/prepared_path).read_text())['frames']['public-f1499']
    with np.load(root/spec['rgb']['path'], allow_pickle=False) as archive:
        public_gray = cv2.cvtColor(archive['original_roi'], cv2.COLOR_BGR2GRAY)
        public_visible = (archive['effective_mask'] > 0) & (archive['glare_mask'] == 0)
    roster_path = next(p for p in pre['inputs'] if 'raster-partition' in p)
    roster = load_gzip(root/roster_path)
    original_units = {u['id']: u for u in roster['units'] if 'raster_witness' in u}
    check(len(measurements['screened']) == len(original_units) == 175, 'screen denominator')
    for unit in measurements['screened']:
        old = original_units[unit['id']]; row = unit['measurement']; q = old['query']
        for field in ('review_label', 'label_basis', 'group', 'raw_frame_id'):
            check(unit[field] == old[field], 'review changed')
        check((row['frame'],row['index'],row['source'],row['y']) ==
              (q['frame'],q['candidate_index'],q['source'],q['source_xy'][1]), 'screen identity')
        if unit['group'] == 'sample4': check(row == table[(row['frame'],row['index'])], 'screen/replay mismatch')
        else: totals.update(verify_measurement(row, public_gray, public_visible))
    true_controls = {(c['frame'],c['index']): c for c in pre['controls']}
    for key,c in true_controls.items():
        units = [u for u in original_units.values() if u['group']=='sample4' and
                 (u['query']['frame'],u['query']['candidate_index']) == key]
        check(len(units)==1, 'review identity missing'); u=units[0]
        check(c['review_label']==u['review_label'] and c['label_basis']==u['label_basis'], 'review precision')
        physical = isinstance(u['label_basis'],dict) and u['label_basis'].get('physical')=='TARGET_CORRESPONDENCE'
        check(c['physical_positive']==physical, 'practical promoted to truth')
    def status(row):
        chosen = row['selected']
        if chosen is None: return 'NO_NUMERIC_OIL'
        c = true_controls.get((row['frame_index'],chosen['candidate_offset']))
        if c is None: return 'UNASSESSED_SELECTION'
        if c['review_label']=='OPPOSED': return 'REVIEWED_OPPOSED'
        return 'PHYSICAL_CORRESPONDENCE' if c['physical_positive'] else 'PRACTICALLY_ACCEPTED'
    check(len(trace['variants']) == len(comparison['variants']) == 7, 'condition denominator')
    report = {}; baseline = trace['variants'][0]['rows']
    for run, summary in zip(trace['variants'],comparison['variants'],strict=True):
        name = run['variant']; rows=run['rows']; check(name==summary['variant'], 'condition binding')
        arm, mode = (None, 'baseline') if name=='baseline' else name.split('_',1)
        with (directory/name/'tracking.csv').open(encoding='utf-8-sig',newline='') as f:
            csv_rows=list(csv.DictReader(f))
        check(len(rows)==len(csv_rows)==len(raw)==113, 'full-window denominator')
        counts=Counter(); joined=0; foam_changed=[]
        for i,(row,source,csv_row) in enumerate(zip(rows,raw,csv_rows,strict=True)):
            check(row['frame_index']==source['frame_index']==int(csv_row['frame_index']), 'CSV frame')
            check(row['time_sec']==source['time_sec']==float(csv_row['timestamp_sec']), 'CSV timestamp')
            for trace_key,csv_key in [('oil_y','raw_oil_air_level_y'),('foam_y','raw_foam_front_y')]:
                y=None if csv_row[csv_key]=='' else float(csv_row[csv_key])
                check(row[trace_key]==y, 'CSV coordinate')
            for key in ('oil_is_valid','foam_is_valid'):
                check(row[key]==(csv_row[key]=='True'), 'per-series validity')
            selected=row['selected']
            if selected is not None:
                c=source['candidates'][selected['candidate_offset']]
                check((c['source'],c['y'])==(selected['source'],selected['y']) and
                      c['y']==row['oil_y'] and c['kind']=='oil_air', 'same-frame numeric provenance')
                joined+=1
            else: check(row['oil_y'] is None, 'fabricated numeric Oil')
            check(row['review_status']==status(row), 'pixel preference leaked into truth')
            counts[row['review_status']]+=1
            if row['foam_fields']!=baseline[i]['foam_fields'] or row['foam_is_valid']!=baseline[i]['foam_is_valid']:
                foam_changed.append(row['frame_index'])
        check(dict(counts)==summary['review_status_counts'] and joined==summary['numeric_oil'], 'summary counts')
        check(foam_changed==summary['foam_changed_frames'], 'Foam changes')
        check([(c['frame'],c['index']) for c in run['authority_calls']]==expected_keys, 'authority denominator/order')
        promotions=0
        for call in run['authority_calls']:
            key=(call['frame'],call['index']); before=call['before']; after=call['after']
            positive = arm is not None and table[key]['preferences'][arm]=='JUMP_PREFERRED'
            should_promote = positive and mode in ('positive_authority_only','negative_veto_positive_authority') and before['tier'] in (1,2)
            expected=dict(before)
            if should_promote:
                expected['tier']=3
                expected['failed_gates']=[*before['failed_gates'],'DIAGNOSTIC_PIXEL_PROFILE_AUTHORITY_PROMOTION']
                promotions+=1
            check(expected==after, 'unqualified or omitted authority intervention')
        expected_vetoes = []
        if mode in ('negative_member_veto','negative_veto_positive_authority'):
            expected_vetoes=[key for key in expected_keys if table[key]['preferences'][arm]=='CORNER_PREFERRED']
        check([(e['frame'],e['index']) for e in run['input_edits']]==expected_vetoes, 'pixel member veto scope')
        for edit in run['input_edits']:
            c=original[edit['frame']]['candidates'][edit['index']]
            check(edit['before']==c['features'].get('sequence_eligible') and edit['after']==0.0, 'veto mutation')
        check(promotions==len(summary['authority_changes']), 'promotion count')
        with (directory/name/'events.csv').open(encoding='utf-8-sig',newline='') as f:
            events=list(csv.DictReader(f))
        extrema=0
        for event in events:
            verify_event_sample(event, {c['frame_index']:c for c in csv_rows})
            if event['event_type'] not in ('MAXIMUM_OIL_LEVEL','MINIMUM_OIL_LEVEL'): continue
            item=next(x for x in summary['extrema'] if x['event']==event['event_type'])
            row=next(r for r in rows if r['frame_index']==int(event['representative_frame_index']))
            check(item['frame_index']==row['frame_index'] and item['y']==row['oil_y'] and
                  item['review_status']==status(row), 'extrema provenance/role')
            extrema+=1
        report[name]={'rows':len(rows),'numeric_source_joins':joined,'authority_calls':len(expected_keys),
                      'promotions':promotions,'member_vetoes':len(expected_vetoes),
                      'events':len(events),'extrema':extrema}
    return {'schema':'s11-profile-witness-verification-v1','status':'PASS','mismatches':0,
            'sampled_source_frames':len(frames),'sample4_candidates':len(table),
            'screened_candidates':len(original_units),'pixel_arithmetic':dict(totals),'variants':report,
            'claim':'Original-pixel arithmetic, row-held-out fit, intervention scope and publication provenance; not physical accuracy or human comprehension.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd())
    parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=verify(args.root.resolve(),args.directory.resolve())
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2); f.write('\n')
    print(json.dumps(result,indent=2))
