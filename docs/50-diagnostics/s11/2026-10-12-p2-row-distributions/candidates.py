"""Saved-candidate diagnostic for the unchanged regional row-mean comparison.

Reuse the frozen measurement and CDF verifier. The only inventory adaptation is
all proposals from the seven already pinned captures, plus the four old controls.
No decoder, detector, new reference, physical selector or source label is added.
"""
from pathlib import Path
import argparse
import importlib.util
import math
import time
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('row_population_capture', HERE / 'run.py')
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)


def inventory(source):
    known = {q['id']: q for q in source['queries']}
    queries, captures = [], []
    for frame, files in sorted(source['images'].items(), key=lambda item: int(item[0])):
        if 'capture' not in files:
            continue
        candidates = owner.read(owner.ROOT / files['capture'])['current']['candidates']
        captures.append(dict(frame=int(frame), path=files['capture'], count=len(candidates)))
        for index, candidate in enumerate(candidates):
            query_id = f's4-f{frame}-idx{index}'
            query = known.get(query_id, dict(
                id=query_id, frame=int(frame), source_xy=[595, candidate['y']],
                candidate_index=index, source=candidate['source'], label='UNREVIEWED',
                subtype_status='UNASSESSED', initial_reference=int(frame) == 1275))
            assert query['source_xy'] == [595, candidate['y']]
            assert query['source'] == candidate['source']
            queries.append(query)
    queries.extend(q for q in source['queries'] if 'candidate_index' not in q)
    assert len(queries) == len({q['id'] for q in queries})
    return queries, captures


def adapted_inputs(manifest):
    # Frozen owner's verifier already checks every pixel, cost, mask and pin.
    # Adapt only its required inventory from the 14 old queries to the frozen
    # complete candidate roster, rebuilt independently from saved capture JSON.
    pre, source, pins, loader, images, references = original_inputs(manifest)
    queries, captures = inventory(source)
    assert queries == pre['queries'] and captures == pre['captures']
    return pre, dict(source, queries=queries), pins, loader, images, references


original_inputs = owner.inputs


def frame_summary(results, captures):
    summaries = []
    for capture in captures:
        rows = [r for r in results if r['query']['frame'] == capture['frame']]
        accepted = [r for r in rows if r['summary']['row_mean']['preference'] == 'interface']
        summaries.append(dict(
            frame=capture['frame'], candidate_count=len(rows),
            measured=sum(r['summary']['row_mean']['measured'] for r in rows),
            preferences={label: sum(r['summary']['row_mean']['preference'] == value for r in rows)
                         for label, value in [('interface', 'interface'), ('structure', 'structure'),
                                              ('texture', 'texture'), ('unresolved', None)]},
            interface_queries=[r['query'] for r in accepted],
            distinct_interface_source_y=sorted({r['query']['source_xy'][1] for r in accepted}),
            physical_identity='UNASSESSED except unchanged original candidate reviews'))
    return summaries


def run(manifest, output):
    if output.exists():
        raise FileExistsError(output)
    started = time.monotonic()
    pre, source, pins, loader, images, references = adapted_inputs(manifest)
    previous = owner.read(HERE / 'followup-readout.json')
    old = {r['query']['id']: r for r in previous['results']}
    results = []
    for query in pre['queries']:
        if query['id'] in old:
            assert query == old[query['id']]['query']
            results.append(old[query['id']])
            continue
        variants = []
        for y in sorted({math.floor(query['source_xy'][1]), math.ceil(query['source_xy'][1])}):
            center = [int(query['source_xy'][0]), int(y)]
            region = loader.region(images[query['frame']], center)
            result = (dict(status='UNAVAILABLE', reason='query_crop_outside', modes={}) if region is None
                      else owner.compare_row_distribution_roles(region[0], region[1], references))
            variants.append(dict(source_center_xy=center, measurement=result))
        summary = {}
        for mode in ('distribution', 'row_mean'):
            values = [v['measurement'] for v in variants]
            prefs = {v['modes'].get(mode, {}).get('appearance_preference') for v in values}
            summary[mode] = dict(measured=all(v['status'] == 'MEASURED' for v in values),
                                 preference=next(iter(prefs)) if len(prefs) == 1 else None)
        results.append(dict(query=query, variants=variants, summary=summary))
    for path, digest in pins.items():
        assert owner.sha(owner.ROOT / path) == digest, path
    elapsed = time.monotonic() - started
    rss = owner.resource.getrusage(owner.resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if owner.sys.platform == 'darwin' else rss * 1024
    data = dict(schema='s11-unchanged-mean-all-candidates-v1', preflight_sha256=owner.sha(manifest),
                execution_head=owner.subprocess.check_output(
                    ['git', '-C', str(owner.ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                results=results, not_run=[], reused_query_ids=sorted(old),
                frames=frame_summary(results, pre['captures']),
                retained_unavailable=pre['retained_unavailable'],
                disposition='DIAGNOSTIC_ONLY_NO_PROMOTION', physical_identity='NOT_EVALUATED',
                parent_distribution_disposition='CLOSED_WITHOUT_PROMOTION',
                resources=dict(elapsed_sec=elapsed, peak_rss_bytes=rss_bytes,
                               within_bounds=elapsed <= 60 and rss_bytes <= 1073741824),
                production_files_unchanged=len(source['production_sources']), production_changed=False)
    # One compact record per query avoids a multi-megabyte indentation expansion.
    with output.open('x', encoding='utf-8') as stream:
        stream.write(owner.json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n')
    assert data['resources']['within_bounds']
    print(owner.json.dumps([dict(frame=f['frame'], count=f['candidate_count'],
        preferences=f['preferences'], interface_y=f['distinct_interface_source_y']) for f in data['frames']]))


def verify(manifest, readout, output):
    pre, source, _, _, _, _ = adapted_inputs(manifest)
    data = owner.read(readout)
    assert [r['query'] for r in data['results']] == pre['queries']
    old = {r['query']['id']: r for r in owner.read(HERE / 'followup-readout.json')['results']}
    current = {r['query']['id']: r for r in data['results']}
    assert all(current[key] == value for key, value in old.items())
    assert data['reused_query_ids'] == sorted(old)
    for record in data['results']:
        query = record['query']
        assert [v['source_center_xy'] for v in record['variants']] == [
            [595, y] for y in sorted({math.floor(query['source_xy'][1]), math.ceil(query['source_xy'][1])})]
        for mode in ('distribution', 'row_mean'):
            values = [v['measurement'] for v in record['variants']]
            preferences = {v.get('modes', {}).get(mode, {}).get('appearance_preference') for v in values}
            expected = next(iter(preferences)) if len(preferences) == 1 else None
            assert record['summary'][mode] == dict(
                measured=all(v['status'] == 'MEASURED' for v in values), preference=expected)
    assert data['frames'] == frame_summary(data['results'], pre['captures'])
    assert sum(f['candidate_count'] for f in data['frames']) == sum(c['count'] for c in pre['captures'])
    assert data['retained_unavailable'] == pre['retained_unavailable']
    assert data['not_run'] == [] and data['disposition'] == 'DIAGNOSTIC_ONLY_NO_PROMOTION'
    assert not data['production_changed'] and data['physical_identity'] == 'NOT_EVALUATED'
    assert data['resources']['elapsed_sec'] <= 60 and data['resources']['peak_rss_bytes'] <= 1073741824
    with patch.object(owner, 'inputs', side_effect=adapted_inputs):
        owner.verify(manifest, readout, output)
    print(owner.json.dumps(dict(candidate_inventory='complete', original_controls='byte-equivalent data',
                              query_count=len(source['queries']), binding_and_summary_checks='PASS')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('run', 'verify'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--readout', type=Path)
    args = parser.parse_args()
    manifest = HERE / 'candidates-preflight.json'
    if args.action == 'run':
        run(manifest, args.output.resolve())
    else:
        if args.readout is None:
            parser.error('verify requires --readout')
        verify(manifest, args.readout.resolve(), args.output.resolve())
