"""CAF-1 clean-anchor fill qualification diagnostic. Not a promoted production policy.

An observation may grant anchor-based fill authority only when its own current
row is material-clean. See docs/50-diagnostics/s11/2026-10-20-clean-anchor-fill.md.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import replace
import gzip
import json
from pathlib import Path
import subprocess
import time
from unittest.mock import patch

from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
from oil_tracker.adapters.vision.oil_phase_lifecycle import OilMaterialPhaseLifecycleOwner as Owner
from tests.diagnostics import s11_history_phase_amplification as hpa
from tests.diagnostics import s11_role_consumer_intervention as rci
from tests.diagnostics import s11_single_observation_influence as soi
from tests.diagnostics import s11_single_observation_verify as verify

PROTOCOL = Path('docs/50-diagnostics/s11/2026-10-20-clean-anchor-fill.md')
SOI_PARENT = Path('sample/output/s11-single-observation-20261016-001/evidence')
EXTREMA = ('MAXIMUM_OIL_LEVEL', 'MINIMUM_OIL_LEVEL')


def clean_chain(chain):
    """Copy of the chain in which contradicted rows do not count as anchors."""
    return replace(chain, observations=tuple(
        replace(item, independent_anchor=item.independent_anchor and not item.material_veto)
        for item in chain.observations))


@contextmanager
def clean_anchor():
    """Patch the fill profile; yield the de-duplicated list of changed decisions."""
    original = Owner._fill_confirmation_profile
    operations = []
    seen = set()

    def profile(self, chain):
        ordinary = original(self, chain)
        cleaned = clean_chain(chain)
        if cleaned == chain:
            return ordinary
        result = original(self, cleaned)
        if result is not ordinary:
            key = (chain.owner, chain.last.frame, ordinary.value, result.value)
            if key not in seen:
                seen.add(key)
                operations.append(dict(
                    owner=chain.owner, owners=list(chain.owners), terminal_frame=chain.last.frame,
                    ordinary=ordinary.value, trial=result.value,
                    contradicted_anchor_frames=[o.frame for o in chain.observations
                                                if o.independent_anchor and o.material_veto],
                    clean_anchor_frames=[o.frame for o in chain.observations
                                         if o.independent_anchor and not o.material_veto]))
        return result

    with patch.object(Owner, '_fill_confirmation_profile', profile):
        yield operations
    rci.require(Owner._fill_confirmation_profile is original, 'clean-anchor patch leak')


def execute(raw, recipe, case):
    with clean_anchor() as operations:
        result = soi.execute(raw, recipe, case)
    return (*result, operations)


def extrema(record):
    return sorted((l['event_type'], l['timestamp_sec'], (l['sample'] or {}).get('raw_oil_air_level_y'))
                  for l in record['presentation']['landmarks'] if l['event_type'] in EXTREMA)


def control_outcomes(record, controls):
    rows = {r['frame_index']: r for r in record['rows']}
    out = []
    for control in controls:
        row = rows[control['frame']]
        out.append(dict(id=control['id'], frame=control['frame'], label=control['review_label'],
                        control_y=control['y'], oil_y=row['oil_y'],
                        selected=row['oil_y'] is not None and row['oil_y'] == control['y']))
    return out


def run(root, output):
    rci.require(output.is_dir() and not any(output.iterdir()), 'empty managed work required')
    parent = root / SOI_PARENT
    prior = json.loads((parent / 'comparison.json').read_text(encoding='utf-8'))
    raw = json.loads((root / rci.SAVED / 'raw.json').read_text(encoding='utf-8'))
    recipe = rci.JsonRecipeRepository().load(root / rci.BUNDLE / 'recipe_snapshot.oilrecipe')
    controls = prior['preflight']['controls']
    saved = []
    with gzip.open(parent / 'population.jsonl.gz', 'rt', encoding='utf-8') as stream:
        for line in stream:
            saved.append(json.loads(line))
    rci.require(len(saved) == 246, 'original denominator mismatch')
    source_paths = list((root / 'src').rglob('*.py')) + [
        Path(__file__), Path(soi.__file__), Path(rci.__file__), Path(hpa.__file__), Path(verify.__file__)]
    sources = {str(p.relative_to(root)): rci.digest(p) for p in source_paths}
    inputs = {**prior['preflight']['inputs'],
              str(SOI_PARENT / 'population.jsonl.gz'): rci.digest(parent / 'population.jsonl.gz'),
              str(PROTOCOL): rci.digest(root / PROTOCOL)}
    rci.require(all(rci.digest(root / p) == v for p, v in inputs.items()), 'input drift')
    pre = dict(head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True,
                                            encoding='utf-8', stdin=subprocess.DEVNULL).strip(),
               sources=sources, inputs=inputs, cases=[r['case'] for r in saved], controls=controls,
               scope='CAF-1 diagnostic wrapper; not production adoption')
    rci.write_json(output / 'preflight.json', pre)
    summaries = []
    checks = event_checks = 0
    ordinary_baseline = None
    began = time.perf_counter()
    with gzip.open(output / 'population.jsonl.gz', 'xt', encoding='utf-8') as stream:
        for ordinal, original in enumerate(saved):
            ordinary, _, _, _ = soi.execute(raw, recipe, original['case'])
            rci.require(ordinary['rows'] == original['rows'] and ordinary['events'] == original['events'],
                        'ordinary policy does not reproduce saved SOI rows/events')
            trial, _, _, _, operations = execute(raw, recipe, original['case'])
            if ordinal == 0:
                ordinary_baseline = ordinary
            for record in (ordinary, trial):
                for row, source in zip(record['rows'], raw, strict=True):
                    verify.check_row(row, source)
                    checks += 1
                samples = {r['frame_index']: r['sample'] for r in record['rows']}
                for event in record['events']:
                    verify.check_event_levels(event, samples[event['representative_frame_index']])
                    event_checks += 1
            summary = soi.summarize(trial, ordinary_baseline)
            paired = soi.summarize(trial, ordinary)
            summary.update(
                operations=len(operations),
                paired_oil_changed_frames=paired['oil_changed_frames'],
                paired_foam_changed_frames=paired['foam_changed_frames'],
                paired_public_equal=hpa.public_signature(trial) == hpa.public_signature(ordinary),
                ordinary_oil_numeric=sum(r['oil_y'] is not None for r in ordinary['rows']),
                ordinary_report_extrema=extrema(ordinary), trial_report_extrema=extrema(trial),
                ordinary_foam_landmarks=soi.summarize(ordinary, ordinary)['foam_landmarks'],
                ordinary_controls=control_outcomes(ordinary, controls),
                trial_controls=control_outcomes(trial, controls))
            summaries.append(summary)
            stream.write(json.dumps(dict(ordinary=ordinary, trial=trial, operations=operations),
                                    ensure_ascii=False, allow_nan=False) + '\n')
            if ordinal % 20 == 0 or ordinal == 245:
                print(ordinal, len(operations), summary['ordinary_oil_numeric'], summary['oil_numeric'],
                      f'{time.perf_counter() - began:.1f}s', flush=True)
    changed = [s['id'] for s in summaries if not s['paired_public_equal']]
    with gzip.open(output / 'population.jsonl.gz', 'rt', encoding='utf-8') as stream:
        targets = {}
        for line in stream:
            payload = json.loads(line)
            if payload['trial']['id'] in changed:
                targets[payload['trial']['id']] = payload
    for name in changed:
        expected = targets[name]
        for policy in ('ordinary', 'trial'):
            if policy == 'ordinary':
                record, _, public, presentation = soi.execute(raw, recipe, expected['ordinary']['case'])
            else:
                record, _, public, presentation, operations = execute(raw, recipe, expected['trial']['case'])
                rci.require(operations == expected['operations'], 'activation replay drift')
            rci.require(record == expected[policy], 'publication replay drift')
            directory = output / 'paired' / name / policy
            directory.mkdir(parents=True)
            rci.CsvExporter().export(public, directory / 'tracking.csv', directory / 'events.csv')
            GraphRenderer().render(public, directory / 'graphs', recipe, presentation=presentation)
    rci.require(all(rci.digest(root / p) == v for p, v in {**sources, **inputs}.items()),
                'source/input mutation')
    result = dict(schema='s11-clean-anchor-fill-v1', preflight=pre, cases=summaries, changed_cases=changed,
                  population_cases=len(saved), population_rows=checks, events_verified=event_checks,
                  activated_cases=sum(bool(s['operations']) for s in summaries),
                  production_unchanged=True, physical_accuracy='NOT_EVALUATED',
                  report_comprehension='NOT_HUMAN_EVALUATED', seconds=time.perf_counter() - began)
    rci.write_json(output / 'comparison.json', result)
    print('COMPLETE', len(saved), checks, result['activated_cases'], len(changed), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=hpa.ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.output.resolve())


if __name__ == '__main__':
    main()
