"""Frozen diagnostic role interventions, never a deployable detector/classifier.

Human-reviewed exact candidates are injected only to locate consumer bottlenecks.
No role propagates to adjacent frames, coordinates, families, members or tracks.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, replace
from enum import Enum
import gzip
import hashlib
import html
import json
import math
from pathlib import Path
import subprocess
import time
from unittest.mock import patch

from oil_tracker.adapters.reporting.csv_exporter import CsvExporter
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision import oil_observation_resolver as oil_module
from oil_tracker.adapters.vision.oil_candidate_authority import (
    AuthorityDecision, OilCandidateAuthority as Tier,
)
from oil_tracker.adapters.vision.observation_sequence_resolver import ObservationSequenceResolver
from oil_tracker.application.services.detection_processing import tracking_sample_from_detection
from oil_tracker.application.services.report_presentation import build_report_presentation
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, ResultState
from oil_tracker.domain.events import detect_events_for_glass
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult

ROOT = Path(__file__).resolve().parents[2]
SAVED = Path('sample/output/s11-p5-default-linkage-20261011-001/none')
BUNDLE = SAVED / 'oil_level_analysis_Local_XY_fixed_comparison_sample4_20261011_224401'
ROSTER = Path('sample/output/s11-raster-partition-20261016-001/evidence/readout.json.gz')
PINS = {
    str(SAVED/'raw.json'): '399ca8a5d19c2fa26f01c4f24fd72870acd84f22747201d8006616265cc5936f',
    str(SAVED/'completed.json'): 'f5b403ce9a061fca3bd4933a44bfdbcf83df0c95811222981a7105aa259870ca',
    str(ROSTER): '5458e62d198a821056996fabe736b9510d4b699571cd5497f88006c67a4723fc',
}
VARIANTS = ('baseline', 'negative_anchor_demotion', 'negative_member_veto',
            'positive_authority_only', 'negative_veto_positive_authority')
DYNAMIC_KEYS = {'foam_material_identity', 'composition_lower_reserve'}
FOAM_FIELDS = ('foam_front_y', 'foam_front_px_from_zero', 'foam_front_mm_from_zero',
               'raw_foam_front_y', 'smoothed_foam_front_y', 'foam_confidence')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalize(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(normalize(v) for v in value)
    if isinstance(value, (tuple, list)):
        return [normalize(v) for v in value]
    return value


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(normalize(value), stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def decode(raw):
    copied = deepcopy(raw)
    copied['fill_state'] = FillState(copied['fill_state'])
    copied['candidates'] = [BoundaryCandidate(**{**c, 'kind': BoundaryKind(c['kind'])})
                            for c in copied['candidates']]
    return PhaseDetection(**copied)


def bind_controls(raw, units):
    """Keep candidate-offset provenance and practical versus physical scope."""
    frames = {d['frame_index']: d for d in raw}
    require(len(frames) == len(raw), 'duplicate source frame')
    controls, seen = [], set()
    for unit in units:
        if unit['group'] != 'sample4' or unit['review_label'] not in {'ACCEPTED', 'OPPOSED'}:
            continue
        q = unit['query']
        key = (q['frame'], q['candidate_index'])
        require(key not in seen, 'duplicate reviewed candidate identity')
        seen.add(key)
        require(key[0] in frames, 'review frame absent')
        candidates = frames[key[0]]['candidates']
        require(0 <= key[1] < len(candidates), 'candidate index outside raw frame')
        c = candidates[key[1]]
        require(c['kind'] == 'oil_air', 'non-Oil role binding')
        require((c['source'], c['y']) == (q['source'], q['source_xy'][1]),
                'reviewed source/index/Y binding mismatch')
        basis = unit['label_basis']
        physical = isinstance(basis, dict) and basis.get('physical') == 'TARGET_CORRESPONDENCE'
        controls.append({'id': unit['id'], 'frame': key[0], 'index': key[1],
                         'source': c['source'], 'y': c['y'],
                         'review_label': unit['review_label'], 'label_basis': basis,
                         'physical_positive': physical,
                         'practical_only': unit['review_label'] == 'ACCEPTED' and not physical})
    return controls


def intervene_authority(decision, *, variant, opposed, physical_positive):
    """Change just the returned tier; existing phase/material evidence is untouched."""
    require(variant in VARIANTS, 'unknown diagnostic variant')
    if variant == 'negative_anchor_demotion' and opposed and decision.tier is Tier.ANCHOR_ELIGIBLE:
        return replace(decision, tier=Tier.CONTINUATION_ELIGIBLE,
                       failed_gates=(*decision.failed_gates, 'DIAGNOSTIC_ORACLE_ANCHOR_DEMOTION'))
    if (variant in {'positive_authority_only', 'negative_veto_positive_authority'}
            and physical_positive and Tier.HARD_INVALID < decision.tier < Tier.ANCHOR_ELIGIBLE):
        return replace(decision, tier=Tier.ANCHOR_ELIGIBLE,
                       failed_gates=(*decision.failed_gates, 'DIAGNOSTIC_ORACLE_AUTHORITY_PROMOTION'))
    return decision


def prepare_input(raw, controls, variant):
    require(variant in VARIANTS, 'unknown diagnostic variant')
    copied = deepcopy(raw)
    opposed = {(c['frame'], c['index']) for c in controls if c['review_label'] == 'OPPOSED'}
    edits = []
    if variant in {'negative_member_veto', 'negative_veto_positive_authority'}:
        for d in copied:
            for i, c in enumerate(d['candidates']):
                if (d['frame_index'], i) in opposed:
                    require(c['kind'] == 'oil_air', 'veto on non-Oil candidate')
                    edits.append({'frame': d['frame_index'], 'index': i,
                                  'before': c['features'].get('sequence_eligible'), 'after': 0.0})
                    c['features']['sequence_eligible'] = 0.0
    return copied, edits


def sampled_runs(rows, predicate):
    """Record sampled spans, not continuous physical durations or interpolated coverage."""
    runs, active = [], []
    for row in rows:
        if predicate(row):
            active.append(row)
        elif active:
            runs.append(active)
            active = []
    if active:
        runs.append(active)
    return [{'start_sec': r[0]['time_sec'], 'last_sample_sec': r[-1]['time_sec'],
             'sample_count': len(r), 'sampled_span_sec': r[-1]['time_sec']-r[0]['time_sec']}
            for r in runs]


def control_status(row, controls):
    selected = row['selected']
    if selected is None:
        return 'NO_NUMERIC_OIL'
    match = next((c for c in controls if (c['frame'], c['index']) ==
                  (row['frame_index'], selected['candidate_offset'])), None)
    if match is None:
        return 'UNASSESSED_SELECTION'
    require((match['source'], match['y']) == (selected['source'], selected['y']),
            'selected control provenance mismatch')
    if match['review_label'] == 'OPPOSED':
        return 'REVIEWED_OPPOSED'
    return 'PRACTICALLY_ACCEPTED' if match['practical_only'] else 'PHYSICAL_CORRESPONDENCE'


def replay(raw, controls, glass, variant):
    prepared, edits = prepare_input(raw, controls, variant)
    detections = tuple(decode(d) for d in prepared)
    ordered = [(d.frame_index, i, c) for d in detections for i, c in enumerate(d.candidates)
               if c.kind is BoundaryKind.OIL_AIR and math.isfinite(c.y)]
    by_key = {(c['frame'], c['index']): c for c in controls}
    calls = []
    original = oil_module.evaluate_candidate_authority

    def observe(candidate, config, context, evidence=None):
        require(len(calls) < len(ordered), 'unexpected authority call')
        frame, index, expected = ordered[len(calls)]
        actual_dict, expected_dict = asdict(candidate), asdict(expected)
        actual_dict['features'] = {k: v for k, v in actual_dict['features'].items() if k not in DYNAMIC_KEYS}
        expected_dict['features'] = {k: v for k, v in expected_dict['features'].items() if k not in DYNAMIC_KEYS}
        require(actual_dict == expected_dict, 'authority call/input identity drift')
        before = original(candidate, config, context, evidence=evidence)
        control = by_key.get((frame, index), {})
        after = intervene_authority(before, variant=variant,
            opposed=control.get('review_label') == 'OPPOSED',
            physical_positive=control.get('physical_positive', False))
        calls.append({'frame': frame, 'index': index, 'source': candidate.source, 'y': candidate.y,
                      'before': normalize(asdict(before)), 'after': normalize(asdict(after)),
                      'phase_identity': context.phase_identity.identity.value,
                      'material_texture_conflict': evidence.material_texture_conflict,
                      'representation_support': context.representation_support})
        return after

    started = time.perf_counter()
    with patch.object(oil_module, 'evaluate_candidate_authority', observe):
        result = ObservationSequenceResolver().resolve(detections, glass, glass.initial_state)
    require(oil_module.evaluate_candidate_authority is original, 'runtime patch not restored')
    require(len(calls) == len(ordered), 'authority call denominator mismatch')
    complete = normalize([asdict(d) for d in result.detections])
    rows = []
    for original_row, out in zip(raw, complete, strict=True):
        require((original_row['frame_index'], original_row['time_sec']) ==
                (out['frame_index'], out['time_sec']), 'source frame/time drift')
        witness = out['debug_metrics']['sequence_decision_witness']
        selected = witness['selection']['selected_candidate']
        if selected is None:
            require(out['raw_oil_air_level_y'] is None, 'numeric Oil without selected candidate')
        else:
            c = original_row['candidates'][selected['candidate_offset']]
            require(c['source'] == selected['source'] and c['y'] == selected['y'] == out['raw_oil_air_level_y'],
                    'same-frame selected Y provenance violation')
        row = {'frame_index': out['frame_index'], 'time_sec': out['time_sec'],
               'oil_y': out['raw_oil_air_level_y'], 'foam_y': out['raw_foam_front_y'],
               'selected': selected, 'fill_state': out['fill_state'], 'flags': out['flags'],
               'phase': witness['phase'], 'candidate_rows': witness['rows'],
               'foam_fields': {k: out[k] for k in FOAM_FIELDS}}
        row['review_status'] = control_status(row, controls)
        rows.append(row)
    samples = [tracking_sample_from_detection('DIAGNOSTIC_ROLE_ORACLE', glass, d) for d in result.detections]
    for row, sample in zip(rows, samples, strict=True):
        row['oil_is_valid'], row['foam_is_valid'] = sample.oil_is_valid, sample.foam_is_valid
    # REVIEW_REQUIRED is a diagnostic wrapper status, not a rerun of Recipe judgment.
    glass_result = GlassAnalysisResult(glass.id, glass.name, ResultState.REVIEW_REQUIRED, samples,
        detect_events_for_glass('DIAGNOSTIC_ROLE_ORACLE', glass.id, samples),
        judgment_note='Diagnostic intervention; no detector or physical acceptance.')
    public_result = AnalysisResult('DIAGNOSTIC_ROLE_ORACLE', ResultState.REVIEW_REQUIRED,
        [glass_result], 'DIAGNOSTIC', 'DIAGNOSTIC')
    return {'variant': variant, 'rows': rows, 'authority_calls': calls,
            'input_edits': edits, 'runtime_sec': time.perf_counter()-started,
            'diagnostics': normalize(asdict(result.diagnostics))}, complete, public_result


def summarize(readout, baseline, controls, events, presentation):
    rows = readout['rows']
    ext = []
    for event in events:
        if event.event_type.value not in {'MAXIMUM_OIL_LEVEL', 'MINIMUM_OIL_LEVEL'}:
            continue
        row = next(r for r in rows if r['frame_index'] == event.representative_frame_index)
        ext.append({'event': event.event_type.value, 'frame_index': row['frame_index'],
                    'time_sec': row['time_sec'], 'y': row['oil_y'],
                    'review_status': row['review_status'], 'selected': row['selected']})
    changed = []
    for a, b in zip(baseline['rows'], rows, strict=True):
        # Track IDs are also retained separately, but physical binding is source/index/Y.
        identity = lambda r: None if r['selected'] is None else (
            r['selected']['candidate_offset'], r['selected']['source'], r['selected']['y'])
        if identity(a) != identity(b):
            changed.append({'frame_index': b['frame_index'], 'time_sec': b['time_sec'],
                            'baseline_y': a['oil_y'], 'variant_y': b['oil_y'],
                            'baseline_selected': a['selected'], 'variant_selected': b['selected'],
                            'review_status': b['review_status']})
    foam_changes = [b['frame_index'] for a, b in zip(baseline['rows'], rows, strict=True)
                    if a['foam_fields'] != b['foam_fields'] or a['foam_is_valid'] != b['foam_is_valid']]
    protection = []
    for c in controls:
        a = next(r for r in baseline['rows'] if r['frame_index'] == c['frame'])
        b = next(r for r in rows if r['frame_index'] == c['frame'])
        def chosen(row):
            s = row['selected']
            return s is not None and (s['candidate_offset'], s['source'], s['y']) == (c['index'], c['source'], c['y'])
        member_rows = [{**member, 'row_publishable': rr['publishable'],
                        'row_phase_admitted': rr['phase_admitted'],
                        'allowed_ids': b['phase']['allowed_tracklet_ids']}
                       for rr in b['candidate_rows'] for member in rr['members']
                       if member['candidate_offset'] == c['index']]
        protection.append({**c, 'baseline_selected': chosen(a), 'variant_selected': chosen(b),
                           'executed_member_rows': member_rows})
    return {'variant': readout['variant'], 'rows': len(rows),
            'numeric_oil': sum(r['oil_y'] is not None for r in rows),
            'numeric_foam': sum(r['foam_y'] is not None for r in rows),
            'review_status_counts': dict(Counter(r['review_status'] for r in rows)),
            'extrema': ext, 'changed_selections': changed,
            'phase_changed_frames': [b['frame_index'] for a, b in zip(baseline['rows'], rows, strict=True)
                                     if a['phase'] != b['phase']],
            'foam_changed_frames': foam_changes, 'controls': protection,
            'numeric_oil_runs': sampled_runs(rows, lambda r: r['oil_y'] is not None),
            'missing_oil_runs': sampled_runs(rows, lambda r: r['oil_y'] is None),
            'numeric_foam_runs': sampled_runs(rows, lambda r: r['foam_y'] is not None),
            'authority_changes': [c for c in readout['authority_calls'] if c['before'] != c['after']],
            'authority_calls': len(readout['authority_calls']),
            'report_presentation': normalize(asdict(presentation)),
            'runtime_sec': readout['runtime_sec']}


def run(root, output):
    require(not any(output.iterdir()), 'output must be an empty managed work directory')
    for relative, expected in PINS.items():
        require(digest(root/relative) == expected, 'frozen input hash mismatch: '+relative)
    sources = {str(p.relative_to(root)): digest(p) for p in (root/'src').rglob('*.py')}
    additional = [BUNDLE/'recipe_snapshot.oilrecipe', BUNDLE/'session.json', SAVED/'summary.json']
    inputs = {**PINS, **{str(p): digest(root/p) for p in additional}}
    raw = json.loads((root/SAVED/'raw.json').read_text())
    expected = json.loads((root/SAVED/'completed.json').read_text())
    roster = json.loads(gzip.decompress((root/ROSTER).read_bytes()))
    controls = bind_controls(raw, roster['units'])
    require(len(raw) == 113 and len(controls) == 13, 'frozen population mismatch')
    require(sum(c['physical_positive'] for c in controls) == 6, 'physical role count drift')
    require(sum(c['practical_only'] for c in controls) == 1, 'practical role count drift')
    require(sum(c['review_label'] == 'OPPOSED' for c in controls) == 6, 'opposition count drift')
    recipe = JsonRecipeRepository().load(root/BUNDLE/'recipe_snapshot.oilrecipe')
    recipe_before = recipe.to_dict()
    glass = recipe.glasses[0]
    preflight = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                 'inputs': inputs, 'source_hashes': sources, 'controls': controls,
                 'harness_sha256': digest(Path(__file__)),
                 'variants': list(VARIANTS), 'initial_state': glass.initial_state.value,
                 'recipe_geometry': normalize(asdict(glass.geometry)),
                 'scope': 'DIAGNOSTIC_REVIEWED_ROLE_INTERVENTION_NOT_PHYSICAL_CLASSIFIER',
                 'all_comparison_options': 'OFF', 'windows_execution': False,
                 'roster_other_units_not_replayed': sum(u['group'] != 'sample4' for u in roster['units'])}
    write_json(output/'preflight.json', preflight)
    results, summaries = [], []
    from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
    renderer = GraphRenderer()
    for variant in VARIANTS:
        readout, complete, public_result = replay(raw, controls, glass, variant)
        if variant == 'baseline':
            require(complete == expected, 'baseline complete-output mismatch; diagnose before proceeding')
        directory = output/variant
        directory.mkdir()
        CsvExporter().export(public_result, directory/'tracking.csv', directory/'events.csv')
        presentation = build_report_presentation(public_result, recipe)
        renderer.render(public_result, directory/'graphs', recipe, presentation=presentation)
        results.append(readout)
        summaries.append(summarize(readout, results[0], controls, public_result.glass_results[0].events, presentation))
        print(json.dumps({k: summaries[-1][k] for k in ['variant','numeric_oil','numeric_foam','review_status_counts','extrema','runtime_sec']}, ensure_ascii=False), flush=True)
    require(recipe.to_dict() == recipe_before, 'Recipe mutation')
    require(all(digest(root/p) == h for p,h in inputs.items()), 'input changed during run')
    require(all(digest(root/p) == h for p,h in sources.items()), 'production source changed during run')
    comparison = {'schema': 's11-role-consumer-context-v1', 'preflight': preflight,
                  'variants': summaries, 'baseline_complete_equal': True,
                  'production_changed': False, 'physical_discriminator': 'NOT_IMPLEMENTED',
                  'report_comprehension': 'NOT_HUMAN_EVALUATED', 'windows': 'NOT_RUN'}
    write_json(output/'comparison.json', comparison)
    payload = {'schema': 's11-role-consumer-complete-trace-v1', 'preflight': preflight, 'variants': results}
    (output/'readout.json.gz').write_bytes(gzip.compress(json.dumps(normalize(payload),
        ensure_ascii=False, allow_nan=False, sort_keys=True).encode(), mtime=0))
    sections = []
    for s in summaries:
        name=s['variant']
        image=next((output/name/'graphs').glob('*_detail.png'))
        sections.append(f'<h2>{html.escape(name)}</h2><p>Numeric Oil {s["numeric_oil"]}; Foam {s["numeric_foam"]}. Changed selections {len(s["changed_selections"])}.</p>'
                        f'<img src="{image.relative_to(output).as_posix()}" alt="Diagnostic report graph">'
                        f'<pre>{html.escape(json.dumps(s["extrema"],ensure_ascii=False,indent=2))}</pre>')
    (output/'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>DIAGNOSTIC ROLE ORACLE — NOT A DETECTOR RESULT</title><style>body{font:16px sans-serif;max-width:1280px;margin:24px auto}img{width:100%}pre{white-space:pre-wrap}</style><h1>DIAGNOSTIC ROLE ORACLE — NOT A DETECTOR RESULT</h1><p>Known exact reviewed candidates are injected to test consumer responsibility. These graphs do not demonstrate automated physical discrimination or human report comprehension. Unknown alternatives remain unassessed. No product behavior or thresholds changed.</p>'+''.join(sections)+'</html>', encoding='utf-8')
    return comparison


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--acknowledge-role-oracle', action='store_true', required=True)
    args=parser.parse_args()
    run(args.root.resolve(), args.output.resolve())


if __name__ == '__main__':
    main()
