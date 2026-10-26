"""LBT-2 Windows S2: the frozen LBT-2 changes on a saved field session, and the comparison. Not a promoted policy.

`run` repeats a saved bundle's session (video, Recipe snapshot, window, sampling, initial-state confirmations and
debug level) with IFO v2 + top-exit v3, either plainly (`reference`) or under the frozen LBT-2 changes with live
LBW-3 units (`lbt2`), and writes a new bundle. `compare` lists every differing row of two bundles and the
per-segment counts against a reviewed-truth JSON. Nothing here changes the frozen wrappers. See the S2 protocol
in docs/50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import replace
import hashlib
import json
from pathlib import Path

ARMS = ('reference', 'lbt2')
VERSION_SUFFIXES = ('+initial-full-observation-v2', '+top-exit-full-v3')
DIFF_FIELDS = ('fill_state', 'raw_oil_air_level_y', 'raw_foam_front_y', 'oil_is_valid', 'foam_is_valid', 'flags')
UNIT_WINDOW_SEC = (668.0, 682.0)  # LBT-2 units printed for the layered-Foam segment and its edges
WATCH_SEC = (678.5, 679.0)  # Windows 678.5/679 s must stay unchanged (LBT-1 S2)
HELD_OUT_SEC = (672.0, 677.75)  # review-012 frames, 672.0-677.5 s


def _stop(message):
    raise SystemExit(f'STOP: {message}')


def load_session(bundle, video=None):
    """The saved bundle's session and Recipe snapshot; a video override also moves the confirmations' path."""
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
    from oil_tracker.domain.session import AnalysisSession

    session = AnalysisSession.from_dict(json.loads((bundle / 'session.json').read_text(encoding='utf-8')))
    recipe = JsonRecipeRepository().load(bundle / 'recipe_snapshot.oilrecipe')
    if video is not None and str(video) != session.input_video_path:
        for glass_id, confirmation in list(session.initial_state_confirmations.items()):
            if confirmation.input_video_path != session.input_video_path:
                _stop(f'confirmation for {glass_id} names another video: {confirmation.input_video_path}')
            session.initial_state_confirmations[glass_id] = replace(confirmation, input_video_path=str(video))
        session.input_video_path = str(video)
    return session, recipe


def check_video(session):
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader

    if not Path(session.input_video_path).is_file():
        _stop(f'video not found: {session.input_video_path} (pass --video)')
    reader = OpenCvVideoReader(session.input_video_path)
    try:
        metadata = reader.metadata
    finally:
        reader.close()
    saved = session.video_metadata
    keys = ('width', 'height', 'fps', 'frame_count')
    if saved is None or any(getattr(metadata, key) != getattr(saved, key) for key in keys):
        _stop(f'video metadata differs from the session: {[getattr(metadata, k) for k in keys]} vs '
              f'{[getattr(saved, k) for k in keys] if saved else None}')
    return metadata


def trace_version(bundle):
    with (bundle / 'debug' / 'debug_trace.jsonl').open(encoding='utf-8') as handle:
        record = json.loads(handle.readline())
    return record.get('run_id'), (record.get('sequence') or {}).get('state', {}).get('sequence_resolver_version')


def run(reference_bundle, out, arm, *, video=None, run_name=None):
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.session import DebugTraceLevel
    from tests.diagnostics import s11_layer_bottom_topology as lbt1
    from tests.diagnostics import s11_layer_bottom_topology_2 as lbt2
    from tests.diagnostics import s11_layer_bottom_witness as lbw

    session, recipe = load_session(reference_bundle, video)
    check_video(session)
    if session.debug_trace_level is DebugTraceLevel.NONE:
        _stop('the saved session has no debug trace; LBT-2 needs detector artifacts')
    out.mkdir(parents=True, exist_ok=True)
    session.output_directory = str(out)
    session.run_name = run_name or f'S2_{arm}'
    detector = OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)
    pipeline = AnalysisPipeline(OpenCvVideoReader, detector, RecipeValidationService(), JsonlDebugTraceWriterFactory(out))
    units, operations = {}, []
    if arm == 'lbt2':
        tolerances = {glass.id: lbw.same_boundary_tolerance(glass) for glass in recipe.glasses if glass.enabled}
        with lbt1.live_units(tolerances, inject=True) as units, lbt2.changes() as operations:
            result = pipeline.run(recipe, session)
    else:
        result = pipeline.run(recipe, session)
    if result.errors:
        _stop(f'analysis errors {result.errors}')
    bundle = OutputBundleStore().write_bundle(result, recipe, session, out)
    run_id, version = trace_version(bundle)
    names = {glass.id: glass.name for glass in recipe.glasses}
    print(f'arm {arm} | run_id {run_id} | run_name {session.run_name} | version {version}')
    print(f'bundle {bundle}')
    print(f'window {session.analysis_start_sec}-{session.analysis_end_sec} s | fps {session.sampling_fps} | '
          f'debug {session.debug_trace_level.value} | rows ' +
          ', '.join(f'{names[g.glass_id]} {len(g.samples)}' for g in result.glass_results))
    if version is None or not all(suffix in version for suffix in VERSION_SUFFIXES):
        _stop(f'unexpected resolver version {version}')
    if arm == 'lbt2':
        counts = Counter(op['consumer'] for op in operations)
        unit_frames = Counter(names[glass_id] for (glass_id, _), item in units.items() if item['unit'])
        print(f"operations E1 {counts.get('E1', 0)} | support {counts.get('support', 0)} | F {counts.get('F', 0)} | "
              f"unit frames {dict(unit_frames)}")
        print('-- F: frame offset | y | foam_row | withheld --')
        for op in operations:
            if op['consumer'] == 'F':
                print(f"{op['frame']} | {op['y']} | {op['foam_row']} | {op['withheld']}")
        print(f'-- units {UNIT_WINDOW_SEC[0]}-{UNIT_WINDOW_SEC[1]} s: glass | time | frame | unit size | unit top --')
        for (glass_id, frame), item in sorted(units.items(), key=lambda kv: (names[kv[0][0]], kv[0][1])):
            if UNIT_WINDOW_SEC[0] <= item['time'] <= UNIT_WINDOW_SEC[1]:
                print(f"{names[glass_id]} | {item['time']} | {frame} | {len(item['unit'])} | {item['top']}")
        (out / f'lbt2-operations-{run_id}.json').write_text(json.dumps(dict(
            operations=operations, units={f'{names[g]}:{f}': item for (g, f), item in units.items()}),
            indent=1, default=str) + '\n', encoding='utf-8')
    return bundle


# --- comparison --------------------------------------------------------------------------

def tracking(bundle):
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository

    names = {str(g.id): g.name for g in JsonRecipeRepository().load(bundle / 'recipe_snapshot.oilrecipe').glasses}
    with (bundle / 'tracking_data.csv').open(encoding='utf-8-sig', newline='') as handle:
        return {(names[row['glass_id']], int(row['frame_index'])): row for row in csv.DictReader(handle)}


def _y(value):
    return None if value in ('', None) else float(value)


def segment_of(segments, glass, time):
    own = [segment for segment in segments if segment['glass'] == glass]
    for segment in own:
        last = segment['end_sec'] == max(item['end_sec'] for item in own)
        if segment['start_sec'] <= time and (time < segment['end_sec'] or (last and time <= segment['end_sec'])):
            return segment['id']
    return None


def compare(reference, trial, truth):
    """Every differing row, and per reviewed segment the numeric Oil/Foam counts of both arms."""
    ref_rows, trial_rows = tracking(reference), tracking(trial)
    if set(ref_rows) != set(trial_rows):
        _stop(f'row keys differ: {len(set(ref_rows) ^ set(trial_rows))}')
    segments = json.loads(Path(truth).read_text(encoding='utf-8'))['segments']
    changed, per_segment = [], {}
    for key in sorted(ref_rows):
        a, b = ref_rows[key], trial_rows[key]
        if a['timestamp_sec'] != b['timestamp_sec']:
            _stop(f'timestamps differ at {key}')
        time = float(a['timestamp_sec'])
        segment = segment_of(segments, key[0], time)
        tally = per_segment.setdefault(segment, Counter())
        tally['rows'] += 1
        for arm, row in (('ref', a), ('trial', b)):
            tally[f'oil_{arm}'] += _y(row['raw_oil_air_level_y']) is not None
            tally[f'foam_{arm}'] += _y(row['raw_foam_front_y']) is not None
        if any(a[field] != b[field] for field in DIFF_FIELDS):
            tally['changed'] += 1
            changed.append(dict(glass=key[0], frame=key[1], time=time, segment=segment,
                                ref=[a['fill_state'], _y(a['raw_oil_air_level_y']), _y(a['raw_foam_front_y']), a['flags']],
                                trial=[b['fill_state'], _y(b['raw_oil_air_level_y']), _y(b['raw_foam_front_y']), b['flags']]))
    watch = [dict(time=float(row['timestamp_sec']), frame=key[1], ref=_y(row['raw_oil_air_level_y']),
                  trial=_y(trial_rows[key]['raw_oil_air_level_y']), equal=all(row[f] == trial_rows[key][f] for f in DIFF_FIELDS))
             for key, row in sorted(ref_rows.items()) if key[0] == 'Accum'
             and any(abs(float(row['timestamp_sec']) - sec) < 0.25 for sec in WATCH_SEC)]
    held_out = [dict(time=float(row['timestamp_sec']), frame=key[1], ref=_y(row['raw_oil_air_level_y']),
                     trial=_y(trial_rows[key]['raw_oil_air_level_y']))
                for key, row in sorted(ref_rows.items()) if key[0] == 'Accum'
                and HELD_OUT_SEC[0] <= float(row['timestamp_sec']) < HELD_OUT_SEC[1]]
    return dict(reference=str(reference), trial=str(trial), changed=changed,
                segments={str(k): dict(v) for k, v in per_segment.items()}, watch=watch, held_out=held_out)


def print_compare(result, reference, trial):
    for label, bundle in (('reference', reference), ('trial', trial)):
        run_id, version = trace_version(bundle)
        print(f'{label} run_id {run_id} | version {version}')
    print(f"changed rows {len(result['changed'])}")
    print('-- segments: id | rows | oil ref/trial | foam ref/trial | changed --')
    for segment, tally in result['segments'].items():
        print(f"{segment} | {tally.get('rows', 0)} | {tally.get('oil_ref', 0)}/{tally.get('oil_trial', 0)} | "
              f"{tally.get('foam_ref', 0)}/{tally.get('foam_trial', 0)} | {tally.get('changed', 0)}")
    print('-- held-out Accum 672.0-677.5 s: time | frame | ref oil | trial oil --')
    for row in result['held_out']:
        print(f"{row['time']} | {row['frame']} | {row['ref']} | {row['trial']}")
    print('-- watch Accum 678.5/679 s: time | frame | ref oil | trial oil | equal --')
    for row in result['watch']:
        print(f"{row['time']} | {row['frame']} | {row['ref']} | {row['trial']} | {row['equal']}")
    print('-- changed (flags in the JSON): glass | segment | time | frame | ref fill / oil / foam | '
          'trial fill / oil / foam --')
    for row in result['changed']:
        print(f"{row['glass']} | {row['segment']} | {row['time']} | {row['frame']} | "
              f"{' / '.join(map(str, row['ref'][:3]))} | {' / '.join(map(str, row['trial'][:3]))}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    run_parser = sub.add_parser('run', help='one arm on a saved bundle session')
    run_parser.add_argument('--reference-bundle', type=Path, required=True)
    run_parser.add_argument('--out', type=Path, required=True)
    run_parser.add_argument('--arm', choices=ARMS, required=True)
    run_parser.add_argument('--video', type=Path, help='the video, if it moved since the saved session')
    run_parser.add_argument('--run-name')
    compare_parser = sub.add_parser('compare', help='two bundles against a reviewed truth')
    compare_parser.add_argument('--reference', type=Path, required=True)
    compare_parser.add_argument('--trial', type=Path, required=True)
    compare_parser.add_argument('--truth', type=Path, required=True)
    compare_parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'run':
        run(args.reference_bundle, args.out, args.arm, video=args.video, run_name=args.run_name)
        return
    result = compare(args.reference, args.trial, args.truth)
    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / 'lbt2-s2-compare.json'
    out.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print_compare(result, args.reference, args.trial)
    print(f"json {out.name} sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}")


if __name__ == '__main__':
    main()
