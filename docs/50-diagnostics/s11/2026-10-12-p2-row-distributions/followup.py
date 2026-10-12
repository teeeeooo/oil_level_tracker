"""Diagnostic-only continuation of the unchanged mean ablation on saved cases.

The failed distribution pilot stays closed. This supplies no runtime decision or
promotion; it asks whether the first pair's mean-only result survives other cases.
"""
from pathlib import Path
import argparse
import importlib.util
import math
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('row_population_capture', HERE / 'run.py')
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    started = time.monotonic()
    manifest = HERE / 'followup-preflight.json'
    pre, source, pins, loader, images, references = owner.inputs(manifest)
    previous = owner.read(HERE / 'readout.json')
    results = list(previous['results'])
    reused = {r['query']['id'] for r in results}
    for query in source['queries']:
        if query['id'] in reused:
            continue
        variants = []
        for y in sorted({math.floor(query['source_xy'][1]), math.ceil(query['source_xy'][1])}):
            center = [int(query['source_xy'][0]), int(y)]
            patch = loader.region(images[query['frame']], center)
            measurement = (dict(status='UNAVAILABLE', reason='query_crop_outside', modes={}) if patch is None
                           else owner.compare_row_distribution_roles(patch[0], patch[1], references))
            variants.append(dict(source_center_xy=center, measurement=measurement))
        summary = {}
        for mode in ('distribution', 'row_mean'):
            values = [v['measurement'] for v in variants]
            prefs = {v['modes'].get(mode, {}).get('appearance_preference') for v in values}
            summary[mode] = dict(measured=all(v['status'] == 'MEASURED' for v in values),
                                 preference=next(iter(prefs)) if len(prefs) == 1 else None)
        results.append(dict(query=query, variants=variants, summary=summary))
    for path, digest in pins.items():
        assert owner.sha(owner.ROOT / path) == digest, path
    counts = {}
    for label in sorted({r['query']['label'] for r in results}):
        rows = [r for r in results if r['query']['label'] == label and not r['query']['initial_reference']]
        counts[label] = {pref: sum(r['summary']['row_mean']['preference'] == value for r in rows)
                        for pref, value in (('interface', 'interface'), ('structure', 'structure'),
                                            ('texture', 'texture'), ('unresolved', None))}
        counts[label]['total_noninitial'] = len(rows)
    assert len(results) == len(source['queries']) == len({r['query']['id'] for r in results})
    elapsed = time.monotonic()-started
    rss = owner.resource.getrusage(owner.resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if owner.sys.platform == 'darwin' else rss*1024
    value = dict(schema='s11-p2-unchanged-mean-diagnostic-v1', preflight_sha256=owner.sha(manifest),
        execution_head=owner.subprocess.check_output(['git', '-C', str(owner.ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        results=results, not_run=[], reused_query_ids=sorted(reused), counts=counts,
        retained_unavailable=pre['retained_unavailable'],
        resources=dict(elapsed_sec=elapsed, peak_rss_bytes=rss_bytes,
                       within_bounds=elapsed <= 60 and rss_bytes <= 1073741824),
        production_files_unchanged=len(source['production_sources']),
        disposition='DIAGNOSTIC_ONLY_NO_PROMOTION', parent_disposition=previous['disposition'],
        exposure='Mean success on the primary pair was seen before this follow-up was frozen.',
        distribution_outputs='Incidental output of the unchanged measurement owner; no rescoring or reopening the failed pilot.',
        physical_identity='UNRESOLVED', production_changed=False)
    owner.save(args.output, value)
    assert value['resources']['within_bounds']
    print(owner.json.dumps(counts))


if __name__ == '__main__':
    main()
