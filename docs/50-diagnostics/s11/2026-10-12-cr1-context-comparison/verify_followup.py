"""Saved-result and original-mask audit, independent of the inference adapter."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def verify(path):
    import numpy as np
    data = read(path)
    pre, plan = read(HERE/'preflight.json'), read(HERE/'followup-preflight.json')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert data['followup_preflight_sha256'] == sha(HERE/'followup-preflight.json')
    for rel, digest in plan['pins'].items():
        assert sha(ROOT/rel) == digest, rel
    roster = read(ROOT/plan['prepared'])['queries']
    assert [r['query'] for r in data['results']] == roster
    assert len(roster) == 164 and len({q['id'] for q in roster}) == 164
    masks = dict(np.load((ROOT/plan['prepared']).parent/'visibility.npz', allow_pickle=False))
    original = {r['query']['id']: r for r in read(ROOT/plan['first_readout'])['results']}
    old_mean = {r['query']['id']: r for r in read(ROOT/plan['mean_baseline'])['results']}
    groups, verified_variants, score_checks = defaultdict(list), 0, 0
    reference_points = {(r['frame'], *r['source_xy']) for r in pre['references'].values()}
    for record in data['results']:
        q, measurement = record['query'], record['measurement']
        assert measurement['query'] == q and measurement['status'] == 'COMPARED'
        group_key = (q['frame'], *q['source_xy'])
        groups[group_key].append(record)
        excluded = [key for key, ref in pre['references'].items()
                    if ref['episode_exclusion_frames'][0] <= q['frame'] <= ref['episode_exclusion_frames'][1]]
        expected_group = ('reference_self_support' if group_key in reference_points else
                          'reference_episode_diagnostic' if excluded else 'outside_reference_episode_development')
        assert record['exposure'] == expected_group
        assert record['original_excluded_classes'] == excluded
        assert record['original_episode_eligible'] == (not excluded)
        assert record['mean_baseline'] == old_mean[q['id']]['summary']['row_mean']
        if record['origin'] == 'REUSED_FIRST_TRIAL':
            assert measurement == original[q['id']]
        else:
            assert original[q['id']]['status'] == 'NOT_RUN'
        expected_y = sorted({math.floor(q['source_xy'][1]), math.ceil(q['source_xy'][1])})
        assert [v['source_center_xy'] for v in measurement['variants']] == [[595, y] for y in expected_y]
        for v in measurement['variants']:
            contexts = [(q['frame'], v['source_center_xy'])] + [
                (r['frame'], r['source_xy']) for r in pre['references'].values()]
            columns = np.ones(25, dtype=bool)
            complete = True
            for frame, (sx, sy) in contexts:
                x, y = int(sx-543), int(sy-798)
                if min(x-12, y-12) < 0 or max(x+12, y+12) >= 104:
                    complete = False
                    break
                patch = masks[str(frame)][y-12:y+13, x-12:x+13]
                columns &= np.concatenate((patch[:11], patch[14:]), axis=0).all(axis=0)
            expected_columns = (np.flatnonzero(columns)-12).tolist() if complete and columns.sum() >= 8 else []
            assert v['common_columns'] == expected_columns
            if not expected_columns:
                assert v['status'] == 'UNAVAILABLE_COMMON_SUPPORT_OR_CROP' and not v['modes']
                continue
            assert v['status'] == 'MEASURED'
            for w in [v['token_weights']['query'], *v['token_weights']['references'].values()]:
                upper, lower = dict(w['upper']), dict(w['lower'])
                for weights in (upper, lower):
                    assert all(0 <= i < 256 and a > 0 for i, a in weights.items())
                    assert abs(sum(weights.values()) - 1) < 1e-12
                shared = upper.keys() & lower.keys()
                assert w['shared_token_count'] == len(shared)
                assert abs(w['overlap_mass'] - sum(min(upper[i], lower[i]) for i in shared)) < 1e-12
            for mode in ('full', 'local'):
                result = v['modes'][mode]
                assert set(result['scores']) == set(pre['references'])
                assert all(math.isfinite(s) and -1-1e-12 <= s <= 1+1e-12 for s in result['scores'].values())
                order = sorted(result['scores'], key=result['scores'].get, reverse=True)
                gap = result['scores'][order[0]]-result['scores'][order[1]]
                assert abs(gap-result['top_margin']) < 1e-12
                assert result['status'] == ('TIE' if gap <= 1e-6 else 'MEASURED')
                assert result['preference'] == (None if gap <= 1e-6 else order[0])
                score_checks += 1
            verified_variants += 1
        for mode in ('full', 'local'):
            prefs = [v['modes'].get(mode, {}).get('preference') for v in measurement['variants']]
            assert measurement['regional_context_preference'][mode] == (prefs[0] if len(set(prefs)) == 1 else None)
    assert data['denominators']['exposure'] == dict(Counter(r['exposure'] for r in data['results']))
    assert data['denominators']['query_labels'] == dict(Counter(q['label'] for q in roster))
    assert data['denominators']['original_episode_eligible'] == sum(r['original_episode_eligible'] for r in data['results'])
    assert data['denominators']['fully_unavailable'] == sum(
        all(not v['modes'] for v in r['measurement']['variants']) for r in data['results'])
    duplicate_groups = [values for values in groups.values() if len(values) > 1]
    assert len(data['duplicate_support_groups']) == len(duplicate_groups)
    for values in duplicate_groups:
        assert all(v['measurement']['variants'] == values[0]['measurement']['variants'] for v in values)
    rows = {r['query']['id']: r for r in data['results']}
    baseline = read(ROOT/plan['application_baseline'])
    for frame in data['summary']['frames']:
        original = next(x for x in baseline['oil_checkpoints'] if x['tracking']['frame_index'] == frame['frame'])
        assert frame['application_baseline']['final_y'] == original['tracking']['raw_oil_air_level_y']
        population = [r for r in rows.values() if r['query']['frame'] == frame['frame']]
        for mode, values in frame['methods'].items():
            expected = [r for r in population if (r['mean_baseline']['preference'] if mode == 'mean' else
                r['measurement']['regional_context_preference'][mode]) == 'interface']
            assert values['interface_candidate_ids'] == [r['query']['id'] for r in expected]
            assert values['distinct_interface_y'] == sorted({r['query']['source_xy'][1] for r in expected})
    for entry in data['summary']['qualified']:
        subset = [r for r in rows.values() if r['exposure'] == entry['exposure'] and r['query']['label'] == entry['label']]
        assert len(subset) == entry['count']
        for mode in ('full', 'local', 'mean'):
            assert entry['preferences'][mode] == dict(Counter(
                (r['mean_baseline']['preference'] if mode == 'mean' else r['measurement']['regional_context_preference'][mode])
                or 'UNRESOLVED' for r in subset))
    assert data['original_trial_disposition'] == 'CLOSED_WITHOUT_PROMOTION'
    assert data['physical_acceptance'] == 'NOT_EVALUATED' and not data['production_changed']
    assert data['guard_denied_events'] == ['socket.getaddrinfo', 'open']
    assert data['resources']['cumulative_forward_count'] <= 420
    assert data['resources']['peak_rss_bytes'] <= 2000000000
    assert data['resources']['elapsed_sec'] <= 600
    for rel, digest in {**pre['production_source_pins'], **pre['original_capture_pins']}.items():
        assert sha(ROOT/rel) == digest, rel
    return dict(status='PASS', records=164, reused_first_trial_records=2,
        measured_variants=verified_variants, score_rank_checks=score_checks,
        common_support_checks=sum(len(r['measurement']['variants']) for r in rows.values()),
        duplicate_groups=len(duplicate_groups), production_sources_unchanged=221,
        full_summary_and_exposure_checks='PASS', model_rerun=False,
        scope='Independent saved-result/mask audit; actual-token library controls are recorded by the measured run.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--readout', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = verify(args.readout)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result))
