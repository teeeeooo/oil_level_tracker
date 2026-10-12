"""Frozen regional population comparison; reuses the S1 raster/crop owner.

Only saved sample4 rasters are read. No video, detector or runtime consumer.
The verify command integrates empirical CDFs independently of rank subtraction.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import resource
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from tests.diagnostics.s11_boundary_temporal_probe import ROW_DISTRIBUTION_SPEC, compare_row_distribution_roles
from tests.diagnostics.s11_corpus_access import require_corpus_access


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def inputs(manifest):
    pre = read(manifest)
    source = read(ROOT / pre['source_manifest'])
    pins = {**source['production_sources'], **pre['inputs']}
    for path, digest in pins.items():
        assert sha(ROOT / path) == digest, path
    assert pre['operation'] == ROW_DISTRIBUTION_SPEC
    spec = importlib.util.spec_from_file_location('s11_s1_raster_loader', ROOT / pre['raster_adapter'])
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    require_corpus_access(('sample4',))
    images = loader.load_images(source)
    references = {role: loader.region(images[r['frame']], r['source_xy'])
                  for role, r in source['references'].items()}
    return pre, source, pins, loader, images, references


def run(manifest, output):
    if output.exists():
        raise FileExistsError(output)
    started = time.monotonic()
    pre, source, pins, loader, images, references = inputs(manifest)
    results = []

    def measure(query):
        variants = []
        for y in sorted({math.floor(query['source_xy'][1]), math.ceil(query['source_xy'][1])}):
            center = [int(query['source_xy'][0]), int(y)]
            patch = loader.region(images[query['frame']], center)
            result = (dict(status='UNAVAILABLE', reason='query_crop_outside', modes={}) if patch is None
                      else compare_row_distribution_roles(patch[0], patch[1], references))
            variants.append(dict(source_center_xy=center, measurement=result))
        summary = {}
        for mode in ('distribution', 'row_mean'):
            values = [v['measurement'] for v in variants]
            preferences = {v['modes'].get(mode, {}).get('appearance_preference') for v in values}
            summary[mode] = dict(measured=all(v['status'] == 'MEASURED' for v in values),
                                 preference=next(iter(preferences)) if len(preferences) == 1 else None)
        record = dict(query=query, variants=variants, summary=summary)
        results.append(record)
        return record

    queries = {q['id']: q for q in source['queries']}
    primary = [measure(queries[q]) for q in pre['primary_queries']]
    passed = {}
    for mode in ('distribution', 'row_mean'):
        passed[mode] = (primary[0]['summary'][mode]['preference'] == 'interface'
                        and primary[1]['summary'][mode]['preference'] in ('structure', 'texture'))
    progressed = passed['distribution'] and not passed['row_mean']
    if progressed:
        for query in source['queries']:
            if query['id'] not in pre['primary_queries']:
                measure(query)
    not_run = [q['id'] for q in source['queries'] if q['id'] not in {r['query']['id'] for r in results}]
    for path, digest in pins.items():
        assert sha(ROOT / path) == digest, path
    elapsed = time.monotonic() - started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == 'darwin' else rss*1024
    result = dict(schema='s11-p2-row-distributions-v1', preflight_sha256=sha(manifest),
        execution_head=subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        results=results, primary_passed=passed, progression_passed=progressed, not_run=not_run,
        retained_unavailable=pre['retained_unavailable'],
        disposition='BOUNDED_APPEARANCE_ONLY' if progressed else 'CLOSED_WITHOUT_PROMOTION',
        physical_identity='UNRESOLVED', production_changed=False,
        resources=dict(elapsed_sec=elapsed, peak_rss_bytes=rss_bytes,
                       within_bounds=elapsed <= 60 and rss_bytes <= 1073741824),
        production_files_unchanged=len(source['production_sources']), inputs_preserved=True)
    save(output, result)
    assert result['resources']['within_bounds']
    print(json.dumps({k: result[k] for k in ('primary_passed', 'progression_passed', 'not_run', 'resources')}))


def verify(manifest, readout, output):
    pre, source, pins, loader, images, references = inputs(manifest)
    data = read(readout)
    assert data['preflight_sha256'] == sha(manifest)
    integral_count = 0
    for record in data['results']:
        for variant in record['variants']:
            patch = loader.region(images[record['query']['frame']], variant['source_center_xy'])
            result = variant['measurement']
            if patch is None:
                assert result['reason'] == 'query_crop_outside'
                continue
            common = patch[1].copy()
            for _, mask, _ in references.values():
                common &= mask
            columns = [np.flatnonzero(common[y]) for y in pre['operation']['rows']]
            assert [x.tolist() for x in columns] == result['common_columns_by_row']
            if any(len(x) < 8 for x in columns):
                assert result['reason'] == 'insufficient_common_row_support'
                continue
            assert result['status'] == 'MEASURED'
            raw = {'current': patch[0], **{k: v[0] for k, v in references.items()}}
            centers = {name: np.mean([im[y, xs].mean(axis=0) for y, xs in
                       zip(pre['operation']['rows'], columns, strict=True)], axis=0) for name, im in raw.items()}
            for name in raw:
                np.testing.assert_allclose(centers[name], result['centering_bgr'][name], atol=1e-12, rtol=0)
            for role in references:
                distribution, means = [], []
                for y, xs in zip(pre['operation']['rows'], columns, strict=True):
                    channel_costs, mean_costs = [], []
                    for c in range(3):
                        q = raw['current'][y, xs, c].astype(float)-centers['current'][c]
                        r = raw[role][y, xs, c].astype(float)-centers[role][c]
                        points = np.unique(np.concatenate([q, r]))
                        dq = np.mean(q[:, None] <= points[None, :-1], axis=0)
                        dr = np.mean(r[:, None] <= points[None, :-1], axis=0)
                        channel_costs.append(float(np.sum(abs(dq-dr)*np.diff(points))/510))
                        mean_costs.append(float(abs(q.mean()-r.mean())/510))
                        integral_count += 1
                    distribution.append(float(np.mean(channel_costs)))
                    means.append(float(np.mean(mean_costs)))
                for mode, values in (('distribution', distribution), ('row_mean', means)):
                    expected = result['modes'][mode]['roles'][role]
                    np.testing.assert_allclose(values, expected['row_costs'], atol=1e-12, rtol=0)
                    assert abs(float(np.mean(values))-expected['cost']) < 1e-12
            for mode in ('distribution', 'row_mean'):
                m = result['modes'][mode]
                ordered = sorted((v['cost'], k) for k, v in m['roles'].items())
                margin = ordered[1][0]-ordered[0][0]
                assert abs(margin-m['margin']) < 1e-12
                preference = ordered[0][1] if ordered[0][0] <= .05 and margin >= .01 else None
                assert preference == m['appearance_preference']
    assert set(data['not_run']).isdisjoint(r['query']['id'] for r in data['results'])
    assert set(data['not_run']) | {r['query']['id'] for r in data['results']} == {q['id'] for q in source['queries']}
    for path, digest in pins.items():
        assert sha(ROOT / path) == digest, path
    receipt = dict(passed=True, cdf_integrals=integral_count, queries=len(data['results']),
        input_count=len(pins), production_files_unchanged=len(source['production_sources']),
        readout_sha256=sha(readout), verifier_sha256=sha(Path(__file__)),
        no_decoder_or_detector=True, method='empirical CDF integral, equal-row normalization and direct visibility intersection')
    save(output, receipt)
    print(json.dumps(receipt))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', 'verify'))
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--readout', type=Path)
    args = parser.parse_args()
    if args.action == 'run':
        run(args.manifest.resolve(), args.output.resolve())
    else:
        if args.readout is None:
            parser.error('verify requires --readout')
        verify(args.manifest.resolve(), args.readout.resolve(), args.output.resolve())
