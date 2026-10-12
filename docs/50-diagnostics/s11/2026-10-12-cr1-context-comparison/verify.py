"""Independent saved-result checks; no encoder import or inference."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    return json.loads(path.read_text())


def verify(readout):
    data, pre, ready = read(readout), read(HERE / 'preflight.json'), read(HERE / 'readiness.json')
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert data['preflight_sha256'] == sha(HERE / 'preflight.json')
    assert data['readiness_sha256'] == sha(HERE / 'readiness.json')
    roster = read(HERE.parent / '2026-10-12-p2-row-distributions/candidates-preflight.json')['queries']
    assert [r['query'] for r in data['results']] == roster
    assert len(roster) == 164 and len({q['id'] for q in roster}) == 164
    assert Counter(r['status'] for r in data['results']) == {'COMPARED': 2, 'NOT_RUN': 162}
    primary = [r for r in data['results'] if r['status'] == 'COMPARED']
    assert {r['query']['id'] for r in primary} == set(pre['primary_queries'])
    comparisons = 0
    weight_sets = 0
    for record in primary:
        query = record['query']
        expected_y = sorted({math.floor(query['source_xy'][1]), math.ceil(query['source_xy'][1])})
        assert [v['source_center_xy'] for v in record['variants']] == [[595, y] for y in expected_y]
        assert all(not lo <= query['frame'] <= hi for lo, hi in
                   (r['episode_exclusion_frames'] for r in pre['references'].values()))
        for v in record['variants']:
            assert v['common_columns'] == list(range(-8, 13))
            for w in [v['token_weights']['query'], *v['token_weights']['references'].values()]:
                upper, lower = dict(w['upper']), dict(w['lower'])
                for weights in (upper, lower):
                    assert all(0 <= i < 256 and x > 0 for i, x in weights.items())
                    assert abs(sum(weights.values()) - 1) < 1e-12
                shared = upper.keys() & lower.keys()
                assert w['shared_token_count'] == len(shared)
                assert abs(w['overlap_mass'] - sum(min(upper[i], lower[i]) for i in shared)) < 1e-12
                weight_sets += 1
            for mode, result in v['modes'].items():
                scores = result['scores']
                assert set(scores) == {'interface', 'structure', 'texture'}
                assert all(math.isfinite(x) and -1-1e-12 <= x <= 1+1e-12 for x in scores.values())
                order = sorted(scores, key=scores.get, reverse=True)
                assert result['preference'] == order[0]
                assert scores[order[0]] - scores[order[1]] > 1e-6
                assert abs(result['top_margin'] - (scores[order[0]] - scores[order[1]])) < 1e-12
                assert record['regional_context_preference'][mode] == order[0]
                comparisons += 1
    assert data['stages']['stage1']['status'] == 'PASS'
    assert data['stages']['stage2']['status'] == 'FAIL'
    assert data['stages']['stage2']['full_pair_pass'] and data['stages']['stage2']['local_pair_pass']
    assert data['stages']['stage3']['status'] == 'NOT_RUN'
    assert data['disposition'] == 'CLOSED_WITHOUT_PROMOTION'
    assert data['physical_acceptance'] == 'NOT_EVALUATED' and not data['production_changed']
    assert data['runtime_guard']['denied_events'] == ['socket.getaddrinfo', 'open']
    assert data['resources']['forward_count'] == 19
    assert len(data['resources']['forward_seconds']) == 19
    assert max(data['resources']['forward_seconds']) < pre['resources']['forward_seconds_limit']
    assert data['resources']['peak_rss_bytes'] < pre['resources']['peak_rss_bytes_limit']
    pins = {**pre['inputs'], **pre['original_capture_pins'], **pre['production_source_pins']}
    for rel, digest in pins.items():
        assert sha(ROOT / rel) == digest, rel
    for name in ('preflight.json', 'prepare.py', 'probe.py'):
        path = HERE / name
        assert sha(path) == ready['frozen_files'][str(path.relative_to(ROOT))]
    result = dict(status='PASS', roster_rows=164, untouched_not_run=162, compared_candidates=2,
                  score_rank_checks=comparisons, weight_mass_overlap_checks=weight_sets,
                  preserved_input_source_pins=len(pins), production_source_pins=221,
                  precision='saved-result consistency, not independent model replication')
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--readout', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify(args.readout)
    if args.output:
        with args.output.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
