"""SOI-1: exhaustive single-frame eligibility loss, not a detector repair."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import gzip
import json
from pathlib import Path
import subprocess
import time
from tests.diagnostics import s11_role_consumer_intervention as rci

MODES = ('selected_oil', 'all_oil', 'all_foam')
ROOT = Path(__file__).resolve().parents[2]


def enumerate_cases(raw, baseline):
    cases = []
    for row, out in zip(raw, baseline, strict=True):
        frame = row['frame_index']
        selected = out['debug_metrics']['sequence_decision_witness']['selection']['selected_candidate']
        if selected is not None:
            cases.append(dict(mode='selected_oil', frame=frame, index=selected['candidate_offset']))
        if any(c['kind'] == 'oil_air' for c in row['candidates']):
            cases.append(dict(mode='all_oil', frame=frame, index=None))
        if any(c['kind'] == 'foam_front' and c['features'].get('sequence_foam_eligible', 0) >= .5 for c in row['candidates']):
            cases.append(dict(mode='all_foam', frame=frame, index=None))
    return sorted(cases, key=lambda c: (MODES.index(c['mode']), c['frame']))


def intervene(raw, case):
    if case is None:
        return raw, []
    rci.require(case['mode'] in MODES, 'unknown loss mode')
    matches = [i for i, row in enumerate(raw) if row['frame_index'] == case['frame']]
    rci.require(len(matches) == 1, 'missing or duplicate intervention frame')
    copied = list(raw)
    offset = matches[0]
    copied[offset] = deepcopy(raw[offset])
    kind = 'foam_front' if case['mode'] == 'all_foam' else 'oil_air'
    field = 'sequence_foam_eligible' if kind == 'foam_front' else 'sequence_eligible'
    edits = []
    for i, candidate in enumerate(copied[offset]['candidates']):
        if candidate['kind'] != kind or (case['mode'] == 'selected_oil' and i != case['index']):
            continue
        edits.append(dict(frame=case['frame'], index=i, source=candidate['source'],
                          y=candidate['y'], field=field,
                          before=candidate['features'].get(field), before_present=field in candidate['features']))
        candidate['features'][field] = 0.0
    rci.require(bool(edits), 'empty intervention')
    return copied, edits


def case_id(case):
    return 'baseline' if case is None else f"{case['mode']}-f{case['frame']:06d}"


def execute(raw, recipe, case):
    prepared, edits = intervene(raw, case)
    glass = recipe.glasses[0]
    result = rci.ObservationSequenceResolver().resolve(tuple(rci.decode(d) for d in prepared), glass, glass.initial_state)
    samples = [rci.tracking_sample_from_detection('DIAGNOSTIC_SOI', glass, d) for d in result.detections]
    events = rci.detect_events_for_glass('DIAGNOSTIC_SOI', glass.id, samples)
    gr = rci.GlassAnalysisResult(glass.id, glass.name, rci.ResultState.REVIEW_REQUIRED, samples, events,
        judgment_note='Single-observation eligibility-loss diagnostic; not physical accuracy.')
    public = rci.AnalysisResult('DIAGNOSTIC_SOI', rci.ResultState.REVIEW_REQUIRED, [gr], 'DIAGNOSTIC', 'DIAGNOSTIC')
    presentation = rci.build_report_presentation(public, recipe)
    rows = []
    for original, detection, sample in zip(raw, result.detections, samples, strict=True):
        rci.require((original['frame_index'], original['time_sec']) == (detection.frame_index, detection.time_sec), 'timing drift')
        witness = detection.debug_metrics['sequence_decision_witness']
        selected = witness['selection']['selected_candidate']
        if selected is None:
            rci.require(sample.raw_oil_air_level_y is None, 'unbound Oil output')
        else:
            c = original['candidates'][selected['candidate_offset']]
            rci.require((c['kind'], c['source'], c['y']) == ('oil_air', selected['source'], sample.raw_oil_air_level_y), 'Oil provenance')
        if sample.raw_foam_front_y is not None:
            rci.require(any(c['kind'] == 'foam_front' and c['y'] == sample.raw_foam_front_y for c in original['candidates']), 'Foam provenance')
        rows.append(dict(frame_index=detection.frame_index, time_sec=detection.time_sec,
            oil_y=sample.raw_oil_air_level_y, foam_y=sample.raw_foam_front_y,
            selected=selected, phase=witness['phase'], sample=asdict(sample)))
    pg = rci.normalize(asdict(presentation))['glasses'][0]
    return dict(id=case_id(case), case=case, edits=edits, rows=rci.normalize(rows),
        events=rci.normalize([asdict(e) for e in events]), presentation=pg), result, public, presentation


def summarize(record, baseline):
    case = record['case']; frame = None if case is None else case['frame']
    out = dict(id=record['id'], case=case, rows=len(record['rows']))
    for series in ('oil', 'foam'):
        key = series + '_y'
        changed = [b['frame_index'] for a, b in zip(baseline['rows'], record['rows'], strict=True) if a[key] != b[key]]
        out[series + '_changed_frames'] = changed
        out[series + '_changed_elsewhere'] = sum(f != frame for f in changed)
        out[series + '_changed_before'] = sum(f < frame for f in changed) if frame is not None else 0
        out[series + '_numeric'] = sum(r[key] is not None for r in record['rows'])
        out[series + '_valid'] = sum(r['sample'][series + '_is_valid'] for r in record['rows'])
        out[series + '_missing_runs'] = rci.sampled_runs(record['rows'], lambda r: r[key] is None)
        out[series + '_numeric_runs'] = rci.sampled_runs(record['rows'], lambda r: r[key] is not None)
    out['oil_identity_changed_frames'] = [b['frame_index'] for a, b in zip(baseline['rows'], record['rows'], strict=True)
        if (None if a['selected'] is None else (a['selected']['candidate_offset'], a['selected']['source'], a['selected']['y'])) !=
           (None if b['selected'] is None else (b['selected']['candidate_offset'], b['selected']['source'], b['selected']['y']))]
    out['extrema'] = [e for e in record['events'] if e['event_type'] in ('MAXIMUM_OIL_LEVEL', 'MINIMUM_OIL_LEVEL')]
    out['foam_landmarks'] = [{k: l[k] for k in ('event_type', 'timestamp_sec', 'end_time_sec')}
        for l in record['presentation']['landmarks'] if l['emphasis'] == 'foam']
    out['movement_summary'] = record['presentation']['movement_summary']
    return out


def representatives(summaries):
    return [max((s for s in summaries if s['case'] and s['case']['mode'] == mode),
        key=lambda s: (s[('foam' if mode == 'all_foam' else 'oil') + '_changed_elsewhere'], -s['case']['frame']))['id']
        for mode in MODES]


def run(root, output):
    rci.require(output.is_dir() and not any(output.iterdir()), 'use empty managed work directory')
    inputs = {str(p): rci.digest(root/p) for p in [rci.SAVED/'raw.json', rci.SAVED/'completed.json',
        rci.BUNDLE/'recipe_snapshot.oilrecipe', rci.BUNDLE/'session.json', rci.ROSTER]}
    rci.require(all(inputs[k] == h for k, h in rci.PINS.items()), 'frozen input drift')
    sources = {str(p.relative_to(root)): rci.digest(p) for p in (root/'src').rglob('*.py')}
    raw = json.loads((root/rci.SAVED/'raw.json').read_text())
    expected = json.loads((root/rci.SAVED/'completed.json').read_text())
    recipe = rci.JsonRecipeRepository().load(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    roster = json.loads(gzip.decompress((root/rci.ROSTER).read_bytes()))
    controls = rci.bind_controls(raw, roster['units'])
    cases = enumerate_cases(raw, expected)
    preflight = dict(head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=root, text=True).strip(),
        inputs=inputs, source_hashes=sources, harness_sha256=rci.digest(Path(__file__)),
        cases=cases, controls=controls, options='ALL_OFF', initial_state=recipe.glasses[0].initial_state.value)
    rci.write_json(output/'preflight.json', preflight)
    baseline, complete, public, presentation = execute(raw, recipe, None)
    rci.require(rci.normalize([asdict(d) for d in complete.detections]) == expected, 'baseline inequality')
    records = {baseline['id']: baseline}; summaries = [summarize(baseline, baseline)]
    started = time.perf_counter()
    with gzip.open(output/'population.jsonl.gz', 'xt', encoding='utf-8') as stream:
        stream.write(json.dumps(baseline, ensure_ascii=False, allow_nan=False)+'\n')
        for ordinal, case in enumerate(cases, 1):
            record, _, _, _ = execute(raw, recipe, case)
            summaries.append(summarize(record, baseline))
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False)+'\n')
            if ordinal % 10 == 0 or ordinal == len(cases):
                print(f'{ordinal}/{len(cases)} elapsed={time.perf_counter()-started:.1f}s {record["id"]}', flush=True)
    selected_ids = ['baseline', *representatives(summaries)]
    with gzip.open(output/'population.jsonl.gz', 'rt', encoding='utf-8') as stream:
        for line in stream:
            record = json.loads(line)
            if record['id'] in selected_ids:
                records[record['id']] = record
    from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
    renderer = GraphRenderer()
    for name in selected_ids:
        expected_record = records[name]
        record, complete, public, presentation = execute(raw, recipe, expected_record['case'])
        rci.require(record == expected_record, 'representative non-determinism')
        directory = output/name; directory.mkdir()
        rci.CsvExporter().export(public, directory/'tracking.csv', directory/'events.csv')
        renderer.render(public, directory/'graphs', recipe, presentation=presentation)
        witnesses = [dict(frame=d.frame_index, witness=d.debug_metrics['sequence_decision_witness'],
            debug=d.debug_metrics) for d in complete.detections]
        (directory/'witnesses.json.gz').write_bytes(gzip.compress(json.dumps(rci.normalize(witnesses),
            ensure_ascii=False, sort_keys=True, allow_nan=False).encode(), mtime=0))
    rci.require(all(rci.digest(root/p) == h for p,h in {**inputs, **sources}.items()), 'source/input mutation')
    comparison = dict(schema='s11-single-observation-influence-v1', preflight=preflight,
        baseline_complete_equal=True, cases=summaries, representatives=selected_ids,
        population_cases=len(cases)+1, population_rows=(len(cases)+1)*len(raw),
        source_unchanged=True, physical_accuracy='NOT_EVALUATED', report_comprehension='NOT_HUMAN_EVALUATED',
        runtime_sec=time.perf_counter()-started)
    rci.write_json(output/'comparison.json', comparison)
    import html
    body = ''.join(f'<h2>{html.escape(n)}</h2><p>{html.escape(records[n]["presentation"]["movement_summary"])}</p>'
        f'<img src="{next((output/n/"graphs").glob("*_detail.png")).relative_to(output).as_posix()}" alt="Actual diagnostic graph">'
        for n in selected_ids)
    (output/'review.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8">'
        '<title>SOI-1 sensitivity, not accuracy</title><style>body{font:16px sans-serif;max-width:1280px;margin:auto}img{width:100%}</style>'
        '<h1>SOI-1: 단일 표본 누락의 영향 — 정확도/제품 후보 아님</h1>'
        '<p>후보 검출 결과 한 시점의 eligibility만 제거한 진단입니다. 원래 수치도 정답이 아니며, 새 선택은 별도 검토되지 않았습니다.</p>'
        + body + '</html>', encoding='utf-8')
    print(json.dumps(dict(cases=len(cases), representatives=selected_ids, seconds=comparison['runtime_sec'])), flush=True)
    return comparison


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.output.resolve())


if __name__ == '__main__':
    main()
