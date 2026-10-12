"""Fixed-operation usefulness continuation; first-trial sources stay frozen.

The only admission change is explicit development-only scoring of the original
reference-neighbor groups. Their original exclusion is retained beside each row.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cr1_frozen_measurement', HERE / 'probe.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ROOT = base.ROOT


def exposure(query, pre):
    if any(query['frame'] == r['frame'] and query['source_xy'] == r['source_xy']
           for r in pre['references'].values()):
        return 'reference_self_support'
    if base.exclusion(query, pre):
        return 'reference_episode_diagnostic'
    return 'outside_reference_episode_development'


def preference(record, mode):
    return record['measurement'].get('regional_context_preference', {}).get(mode)


def summarize(rows, baseline):
    qualified = []
    for group in sorted({r['exposure'] for r in rows}):
        for label in sorted({r['query']['label'] for r in rows}):
            selected = [r for r in rows if r['exposure'] == group and r['query']['label'] == label]
            if not selected:
                continue
            qualified.append(dict(exposure=group, label=label, count=len(selected),
                preferences={mode: dict(Counter(
                    (r['mean_baseline']['preference'] if mode == 'mean' else preference(r, mode)) or 'UNRESOLVED'
                    for r in selected)) for mode in ('full', 'local', 'mean')}))
    frames = []
    for frame in sorted({r['query']['frame'] for r in rows if 'candidate_index' in r['query']}):
        population = [r for r in rows if r['query']['frame'] == frame]
        saved = next(x for x in baseline['oil_checkpoints'] if x['tracking']['frame_index'] == frame)
        source_y = saved['tracking']['raw_oil_air_level_y']
        matches = [r['query']['id'] for r in population if r['query']['source_xy'][1] == source_y]
        values = dict(frame=frame, time_sec=saved['tracking']['timestamp_sec'], count=len(population),
            application_baseline=dict(raw_y=saved['raw'], final_y=source_y, candidate_y_matches=matches,
                join_precision='same saved frame and Y; original index labels retained, no inferred lineage or new label',
                flags=saved['tracking']['flags']), methods={})
        for mode in ('full', 'local', 'mean'):
            preferred = [r for r in population if
                (r['mean_baseline']['preference'] if mode == 'mean' else preference(r, mode)) == 'interface']
            values['methods'][mode] = dict(interface_candidate_ids=[r['query']['id'] for r in preferred],
                distinct_interface_y=sorted({r['query']['source_xy'][1] for r in preferred}),
                unreviewed_interface_ids=[r['query']['id'] for r in preferred if r['query']['label'] == 'UNREVIEWED'],
                target_interface_ids=[r['query']['id'] for r in preferred if r['query']['label'] == 'confirmed_target'],
                wrong_interface_ids=[r['query']['id'] for r in preferred if r['query']['label'] == 'rejected_target'])
        frames.append(values)
    return dict(qualified=qualified, frames=frames,
        reviewed_rows=[dict(id=r['query']['id'], frame=r['query']['frame'], y=r['query']['source_xy'][1],
            label=r['query']['label'], exposure=r['exposure'], full=preference(r, 'full'),
            local=preference(r, 'local'), mean=r['mean_baseline']['preference'])
            for r in rows if r['query']['label'] != 'UNREVIEWED'])


def actual_token_controls(encoder, images, masks):
    import numpy as np
    torch = encoder.torch
    xy, columns = (52, 43), list(range(-8, 13))
    tokens = encoder.saved(images, masks, 1200, xy, 'full')
    upper, lower = base.strips(xy, columns)
    query = base.descriptor(tokens, upper, lower)
    assert base.rank(query, {'a': query, 'b': query})['status'] == 'TIE'
    assert base.rank(query, {'a': query, 'b': query}, required=3)['status'] == 'UNAVAILABLE'
    translated = base.local_xy((1595, 1841), (1543, 1798))
    assert translated == xy
    assert np.array_equal(query, base.descriptor(tokens, *base.strips(translated, columns)))
    # Independent library interpolation on measured tokens checks the native-to-
    # token support, including the same canvas scale and border convention.
    field = torch.from_numpy(tokens.reshape(16, 16, 384).transpose(2, 0, 1).copy()).double()[None]
    errors = []
    for offsets, weights in [(range(-12, -1), upper), (range(2, 13), lower)]:
        points = [[((xy[0]+dx+.5)*224/104/14-.5)*2/15-1,
                   ((xy[1]+dy+.5)*224/104/14-.5)*2/15-1]
                  for dy in offsets for dx in columns]
        grid = torch.tensor(points, dtype=torch.float64)[None, None]
        pooled = torch.nn.functional.grid_sample(field, grid, align_corners=True,
            mode='bilinear', padding_mode='border')[0, :, 0].mean(dim=1).numpy()
        error = float(np.max(np.abs(pooled - weights @ tokens)))
        assert error < 1e-12
        errors.append(error)
    return dict(status='PASS', actual_token_copied_tie=True, missing_class_unavailable=True,
        source_origin_translation_equal=True, equal_scale_library_interpolation_max_errors=errors,
        caveat='Coordinate bookkeeping controls; no claim of rotation/scale robustness on unseen physical scenes.')


def run(manifest, out):
    pre = base.read(HERE / 'preflight.json')
    plan = base.read(manifest)
    for rel, digest in plan['pins'].items():
        assert base.sha(ROOT / rel) == digest, rel
    ready = base.read(HERE / 'readiness.json')
    for rel, digest in ready['frozen_files'].items():
        retained_rel = plan['readiness_relocations'].get(rel, rel)
        assert base.sha(ROOT / retained_rel) == digest, rel
    prepared = base.read(ROOT / plan['prepared'])
    first = base.read(ROOT / plan['first_readout'])
    assert first['stages']['stage1']['status'] == 'PASS'
    assert first['stages']['stage2']['status'] == 'FAIL'
    reused = {r['query']['id']: r for r in first['results'] if r['status'] == 'COMPARED'}
    assert set(reused) == set(pre['primary_queries'])
    mean = base.read(ROOT / plan['mean_baseline'])
    assert [r['query'] for r in mean['results']] == prepared['queries']
    mean = {r['query']['id']: r for r in mean['results']}
    baseline = base.read(ROOT / plan['application_baseline'])
    denied = base.sandbox()
    import numpy as np
    from PIL import Image
    base.np = np
    started = time.monotonic()
    encoder = base.Encoder(pre['resources'])
    decode_start = time.monotonic()
    images = {int(f): np.array(Image.open(ROOT / p).convert('RGB')) for f, p in prepared['images'].items()}
    masks = dict(np.load((ROOT / plan['prepared']).parent / prepared['masks_file'], allow_pickle=False))
    decode_seconds = time.monotonic() - decode_start
    rows = []
    for query in prepared['queries']:
        qid = query['id']
        original_exclusions = base.exclusion(query, pre)
        if qid in reused:
            measurement = reused[qid]
        else:
            # This changes admission to the diagnostic only, not the measurement.
            # Original exposure and ineligibility stay explicit on every record.
            with patch.object(base, 'exclusion', return_value=[]):
                measurement = base.compare(query, pre, encoder, images, masks)
        assert measurement['status'] == 'COMPARED'
        rows.append(dict(query=query, exposure=exposure(query, pre),
            original_excluded_classes=original_exclusions,
            original_episode_eligible=not original_exclusions,
            origin='REUSED_FIRST_TRIAL' if qid in reused else 'NEW_DIAGNOSTIC',
            measurement=measurement, mean_baseline=mean[qid]['summary']['row_mean']))
        if time.monotonic() - started > pre['resources']['stage_seconds_limit']:
            raise RuntimeError('complete diagnostic time budget exceeded')
        if len(encoder.times) + first['resources']['forward_count'] > pre['resources']['max_forward_calls']:
            raise RuntimeError('cumulative forward budget exceeded')
    controls = actual_token_controls(encoder, images, masks)
    groups = defaultdict(list)
    for row in rows:
        query = row['query']
        groups[(query['frame'], *query['source_xy'])].append(row)
    duplicates = []
    for key, values in groups.items():
        if len(values) > 1:
            assert all(v['measurement']['variants'] == values[0]['measurement']['variants'] for v in values)
            duplicates.append(dict(frame=key[0], xy=list(key[1:]), ids=[v['query']['id'] for v in values]))
    data = dict(schema='s11-cr1-usefulness-followup-v1', followup_preflight_sha256=base.sha(manifest),
        original_trial_disposition=first['disposition'], reused_ids=sorted(reused),
        results=rows, summary=summarize(rows, baseline), controls=controls,
        duplicate_support_groups=duplicates, independent_recordings=1, untouched_holdout_recordings=0,
        denominators=dict(total=len(rows), candidates=160, context_controls=4,
            exposure=dict(Counter(r['exposure'] for r in rows)),
            original_episode_eligible=sum(r['original_episode_eligible'] for r in rows),
            query_labels=dict(Counter(r['query']['label'] for r in rows)),
            fully_unavailable=sum(all(v['status'] != 'MEASURED' for v in r['measurement']['variants']) for r in rows),
            partly_unavailable=sum(any(v['status'] != 'MEASURED' for v in r['measurement']['variants']) and
                                  any(v['status'] == 'MEASURED' for v in r['measurement']['variants']) for r in rows)),
        resources=dict(elapsed_sec=time.monotonic()-started, model_load_sec=encoder.load_seconds,
            saved_png_mask_decode_sec=decode_seconds, native_video_decode='NOT_RUN_SAVED_INPUT_DIAGNOSTIC',
            forward_seconds=encoder.times, new_forward_count=len(encoder.times),
            cumulative_forward_count=len(encoder.times)+first['resources']['forward_count'],
            peak_rss_bytes=base.rss(), workspace_allocated_bytes=base.allocated(base.WORKSPACE),
            tracked_diagnostic_allocated_bytes=base.allocated(HERE), retained_token_maps=0),
        guard_denied_events=denied, retained_unassessed=pre['retained_unassessed'],
        production_changed=False, physical_acceptance='NOT_EVALUATED',
        disposition='COMPLETE_DIAGNOSTIC_REQUIRES_USEFULNESS_INTERPRETATION')
    for rel, digest in {**plan['pins'], **pre['production_source_pins'], **pre['original_capture_pins']}.items():
        assert base.sha(ROOT / rel) == digest, rel
    assert data['resources']['workspace_allocated_bytes'] + base.allocated(HERE) < 3_000_000_000
    assert denied == ['socket.getaddrinfo', 'open']
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode() + b'\n'
    with (out / 'followup-readout.json.gz').open('xb') as stream:
        stream.write(gzip.compress(payload, mtime=0))
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) < pre['resources']['run_output_bytes_limit']
    print(json.dumps(dict(denominators=data['denominators'], reviewed=data['summary']['reviewed_rows'],
        controls=controls, resources={k:v for k,v in data['resources'].items() if k != 'forward_seconds'})))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.preflight, args.out)
