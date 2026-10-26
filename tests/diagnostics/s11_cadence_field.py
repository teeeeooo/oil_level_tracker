"""CAD-1 Windows: a saved field session at another sampling rate, with a timing breakdown. Not a promoted policy.

`run` repeats a saved bundle's session (video, Recipe snapshot, window, initial-state confirmations) with IFO v2 +
top-exit v3. Only the sampling rate and the debug level named on the command line change. It writes a new bundle
and prints where the run time went. `identity` compares two bundles row by row and, when both have one, their
debug traces with the run ID normalized. `cadence` reads a trial bundle against the frozen SPL#4 windows and the
2 fps reference. `stages` is read-only: per row, the phase, its reason, the allowed tracklet set and each path stage. See docs/50-diagnostics/s11/2026-10-26-cadence-diagnostic.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from contextlib import contextmanager
import functools
import hashlib
import json
from pathlib import Path
import time

from tests.diagnostics.s11_layer_bottom_topology_2_field import (
    DIFF_FIELDS,
    VERSION_SUFFIXES,
    _stop,
    _y,
    check_video,
    load_session,
    tracking,
)

DEBUG_LEVELS = ('none', 'basic', 'full')
FULL_STATES = frozenset({'FULL_NO_INTERFACE', 'FULL_WITH_FOAM'})
TOP_EXIT_FLAG = 'OIL_TOP_EXIT_FULL'
# SPL#4 windows, frozen 2026-10-22 from the user's timeline (validation: Windows SPL#4 entry conditions).
FIRST_FULL_SEC = (22.0, 27.0)  # BASE FULL reached at 24-25 s, widened by 2 s
HOLD_UNTIL_SEC = 61.0  # BASE FULL, filled with Oil, 25-63 s
RELEASE_SEC = (61.0, 65.0)  # BASE drain from FULL at 63 s
NO_FULL_AFTER_SEC = (65.0, 90.0)  # BASE not FULL after the drain
WINDOW_TABLE_SEC = (20.0, 28.0)  # BASE rows printed around the fast rise
PHASES_SEC = ((0.0, 20.5), (20.5, 27.0), (27.0, 61.0), (61.0, 65.0), (65.0, 90.01))
TIMED = ('decode', 'static artifacts', 'detect', 'debug-only diagnostics', 'trace write', 'png',
         'trace finalize', 'sequence', 'bundle')


@contextmanager
def timers():
    """Accumulate wall time per stage by wrapping the production entry points; restores them afterwards."""
    from oil_tracker.adapters.storage import jsonl_debug_trace_writer as writer
    from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
    from oil_tracker.adapters.vision import phase_frame_detection
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader

    totals = Counter()
    targets = (
        (OpenCvVideoReader, 'read_at', 'decode'),
        (OpenCvPhaseDetector, 'learn_static_artifact', 'static artifacts'),
        (OpenCvPhaseDetector, 'detect', 'detect'),
        (phase_frame_detection, 'measure_oil_interfaces', 'debug-only diagnostics'),
        (writer.JsonlDebugTraceWriter, 'write', 'trace write'),
        (writer, '_write_png', 'png'),
        (writer.JsonlDebugTraceWriter, 'finalize', 'trace finalize'),
        (OpenCvPhaseDetector, 'resolve_sequence', 'sequence'),
        (OutputBundleStore, 'write_bundle', 'bundle'),
    )
    originals = []
    for owner, name, label in targets:
        original = owner.__dict__[name]

        def wrapped(*args, _original=original, _label=label, **kwargs):
            started = time.perf_counter()
            try:
                return _original(*args, **kwargs)
            finally:
                totals[_label] += time.perf_counter() - started

        setattr(owner, name, functools.wraps(original)(wrapped))
        originals.append((owner, name, original))
    try:
        yield totals
    finally:
        for owner, name, original in originals:
            setattr(owner, name, original)


def run(reference_bundle, out, *, fps=None, debug=None, video=None, run_name=None, parallel_glasses=False):
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.session import DebugTraceLevel

    session, recipe = load_session(reference_bundle, video)
    metadata = check_video(session)
    if fps is not None:
        if not 0 < fps <= metadata.fps:
            _stop(f'sampling rate {fps} outside (0, {metadata.fps}]')
        session.sampling_fps = float(fps)
    if debug is not None:
        session.debug_trace_level = DebugTraceLevel(debug)
    out.mkdir(parents=True, exist_ok=True)
    session.output_directory = str(out)
    session.run_name = run_name or f'CAD_{session.sampling_fps:g}fps_{session.debug_trace_level.value}'
    detector = OpenCvPhaseDetector(initial_full_observation=True, top_exit_full=True)
    if not all(suffix in detector.version for suffix in VERSION_SUFFIXES):
        _stop(f'unexpected detector version {detector.version}')
    factory = None if session.debug_trace_level is DebugTraceLevel.NONE else JsonlDebugTraceWriterFactory(out)
    pipeline = AnalysisPipeline(OpenCvVideoReader, detector, RecipeValidationService(), factory,
                                parallel_glasses=parallel_glasses)
    with timers() as totals:
        started = time.perf_counter()
        result = pipeline.run(recipe, session)
        if result.errors:
            _stop(f'analysis errors {result.errors}')
        bundle = OutputBundleStore().write_bundle(result, recipe, session, out)
        wall = time.perf_counter() - started
    rows = {glass.glass_id: len(glass.samples) for glass in result.glass_results}
    names = {glass.id: glass.name for glass in recipe.glasses}
    glass_frames = sum(rows.values())
    run_id = result.run_id
    print(f'run | run_id {run_id} | run_name {session.run_name} | version {detector.version}')
    print(f'bundle {bundle}')
    if parallel_glasses:
        print(f'parallel glasses requested | used {pipeline.last_run_parallel}')
    print(f'window {session.analysis_start_sec}-{session.analysis_end_sec} s | fps {session.sampling_fps} | '
          f'debug {session.debug_trace_level.value} | rows ' + ', '.join(f'{names[g]} {n}' for g, n in rows.items()))
    timing = dict(wall_sec=round(wall, 2), glass_frames=glass_frames,
                  per_glass_frame_sec=round(wall / glass_frames, 4) if glass_frames else None,
                  stages_sec={label: round(totals.get(label, 0.0), 2) for label in TIMED})
    print(f"timing wall {timing['wall_sec']} s | glass-frames {glass_frames} | per glass-frame "
          f"{timing['per_glass_frame_sec']} s")
    print('-- stages (nested: detect includes debug-only diagnostics; trace write includes png; bundle includes '
          'trace finalize and the report source-frame decoding, which decode also counts) --')
    for label, seconds in timing['stages_sec'].items():
        print(f'{label} | {seconds} s')
    path = out / f'cadence-timing-{run_id}.json'
    path.write_text(json.dumps(dict(run_id=run_id, bundle=str(bundle), fps=session.sampling_fps,
                                    debug=session.debug_trace_level.value, version=detector.version,
                                    parallel_glasses=pipeline.last_run_parallel,
                                    **timing), indent=1) + '\n', encoding='utf-8')
    return bundle


# --- identity ------------------------------------------------------------------------------

def _run_id(bundle):
    with (bundle / 'tracking_data.csv').open(encoding='utf-8-sig', newline='') as handle:
        return next(csv.DictReader(handle), {}).get('run_id')


def trace_identity(reference, trial):
    """Line-by-line byte equality of two debug traces after replacing the reference run ID with the trial's."""
    paths = [bundle / 'debug' / name for bundle in (reference, trial) for name in ('debug_trace.jsonl', 'debug_index.json')]
    if not all(path.is_file() for path in paths):
        return None
    old, new = (f'"run_id":"{_run_id(bundle)}"'.encode() for bundle in (reference, trial))
    lines = equal = 0
    first_difference = None
    with paths[0].open('rb') as a, paths[2].open('rb') as b:
        for left, right in zip(a, b, strict=False):
            lines += 1
            if left.replace(old, new) == right:
                equal += 1
            elif first_difference is None:
                first_difference = lines
        extra = len(a.read()) + len(b.read())
    index_old, index_new = (json.loads(path.read_text(encoding='utf-8')) for path in (paths[1], paths[3]))
    index_old['run_id'] = index_new.get('run_id')
    for summary in index_old.get('records', []):
        summary['run_id'] = index_new.get('run_id')
    return dict(lines=lines, equal=equal, first_difference=first_difference, trailing_bytes=extra,
                index_equal=index_old == index_new)


def identity(reference, trial):
    ref_rows, trial_rows = tracking(reference), tracking(trial)
    changed = []
    for key in sorted(set(ref_rows) & set(trial_rows)):
        a, b = ref_rows[key], trial_rows[key]
        if a['timestamp_sec'] != b['timestamp_sec'] or any(a[field] != b[field] for field in DIFF_FIELDS):
            changed.append(dict(glass=key[0], frame=key[1], ref=[a['timestamp_sec'], *(a[f] for f in DIFF_FIELDS)],
                                trial=[b['timestamp_sec'], *(b[f] for f in DIFF_FIELDS)]))
    return dict(reference=str(reference), trial=str(trial), run_ids=[_run_id(reference), _run_id(trial)],
                rows=[len(ref_rows), len(trial_rows)], unmatched=len(set(ref_rows) ^ set(trial_rows)),
                changed=changed, trace=trace_identity(reference, trial))


def print_identity(result):
    print(f"reference run_id {result['run_ids'][0]} | trial run_id {result['run_ids'][1]}")
    print(f"rows {result['rows'][0]}/{result['rows'][1]} | unmatched {result['unmatched']} | "
          f"changed {len(result['changed'])}")
    trace = result['trace']
    if trace is None:
        print('trace not compared (a bundle has no debug trace)')
    else:
        print(f"trace lines {trace['lines']} | equal {trace['equal']} | first difference {trace['first_difference']} | "
              f"trailing bytes {trace['trailing_bytes']} | index equal {trace['index_equal']}")
    for row in result['changed'][:40]:
        print(f"{row['glass']} | {row['frame']} | {row['ref']} | {row['trial']}")


# --- cadence -------------------------------------------------------------------------------

def _rows(bundle, glass, *, required=True):
    rows = [(frame, row) for (name, frame), row in tracking(bundle).items() if name == glass]
    if not rows and required:
        _stop(f'no rows for Glass {glass} in {bundle}')
    return [row for _frame, row in sorted(rows)]


def _full(row):
    return row['fill_state'] in FULL_STATES


def _holds_full(row):
    return (_full(row) or row['fill_state'] == 'UNKNOWN_REVIEW') and _y(row['raw_oil_air_level_y']) is None


def readings(base, accum):
    """C1-C5 on one bundle's BASE and Accum rows (the SPL#4 windows above); no Accum leaves C5 None."""
    t = lambda row: float(row['timestamp_sec'])  # noqa: E731
    first = next((row for row in base if _full(row)), None)
    first_time = None if first is None else t(first)
    c1 = first is not None and FIRST_FULL_SEC[0] <= first_time <= FIRST_FULL_SEC[1]
    hold = [] if first is None else [row for row in base if first_time <= t(row) <= HOLD_UNTIL_SEC]
    breaks = [row for row in hold if not _holds_full(row)]
    end = None if first is None else next((row for row in base if t(row) > first_time and not _holds_full(row)), None)
    end_time = None if end is None else t(end)
    late_full = [row for row in base if NO_FULL_AFTER_SEC[0] <= t(row) <= NO_FULL_AFTER_SEC[1] and _full(row)]
    accum_full = None if accum is None else [row for row in accum if _full(row)]
    return dict(
        first_full_sec=first_time, first_full_top_exit=None if first is None else TOP_EXIT_FLAG in first['flags'],
        c1=c1, hold_rows=len(hold), hold_breaks=[[t(row), row['fill_state'], _y(row['raw_oil_air_level_y'])]
                                                 for row in breaks[:20]],
        c2=first is not None and not breaks, episode_end_sec=end_time,
        c3=end_time is not None and RELEASE_SEC[0] <= end_time <= RELEASE_SEC[1],
        late_full_rows=len(late_full), c4=not late_full,
        accum_full_rows=None if accum_full is None else len(accum_full), c5=None if accum_full is None else not accum_full)


def _band_end(bundle, glass):
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
    from oil_tracker.adapters.vision.oil_observation_resolver import OilObservationResolverConfig

    config = next(g for g in JsonRecipeRepository().load(bundle / 'recipe_snapshot.oilrecipe').glasses if g.name == glass)
    ellipse = config.geometry.ellipse
    top = ellipse.center_y - ellipse.radius_y
    return top + OilObservationResolverConfig().entrance_band_ratio * 2.0 * ellipse.radius_y


def window_table(bundle, glass='BASE'):
    """Each row in WINDOW_TABLE_SEC with its selected Oil candidate's tracklet fields and the top-exit reason."""
    trace = bundle / 'debug' / 'debug_trace.jsonl'
    rows = [row for row in _rows(bundle, glass) if WINDOW_TABLE_SEC[0] <= float(row['timestamp_sec']) <= WINDOW_TABLE_SEC[1]]
    sequence = {}
    if trace.is_file():
        frames = {int(row['frame_index']) for row in rows}
        with trace.open(encoding='utf-8') as handle:
            for line in handle:
                record = json.loads(line)
                if record.get('glass_name') == glass and record.get('frame_index') in frames:
                    sequence[record['frame_index']] = record.get('sequence') or {}
    admitted_min_y = None
    table = []
    for row in rows:
        snapshot = sequence.get(int(row['frame_index']), {})
        oil = [c for c in snapshot.get('candidates', []) if c.get('kind') == 'oil_air']
        selected = next((c for c in oil if c.get('selected')), None)
        for candidate in oil:
            if candidate.get('tracklet_admitted') and candidate.get('canonical_y') is not None:
                y = float(candidate['canonical_y'])
                admitted_min_y = y if admitted_min_y is None else min(admitted_min_y, y)
        top_exit = ((snapshot.get('state') or {}).get('sequence_material_phase_diagnostics') or {}).get('top_exit_full') or {}
        table.append(dict(
            time=float(row['timestamp_sec']), frame=int(row['frame_index']), fill=row['fill_state'],
            oil=_y(row['raw_oil_air_level_y']), foam=_y(row['raw_foam_front_y']),
            top_exit_flag=TOP_EXIT_FLAG in row['flags'],
            selected=None if selected is None else [selected.get('canonical_y'), selected.get('tracklet_id'),
                                                    selected.get('tracklet_lifecycle'), selected.get('tracklet_admitted')],
            top_exit_reason=top_exit.get('reason')))
    return dict(traced=bool(sequence), band_end_y=round(_band_end(bundle, glass), 2),
                admitted_min_y=admitted_min_y, rows=table)


STAGE_KEYS = ('best_path', 'continuation_bound', 'spike_suppressed', 'completed_fill')


def stages(bundle, glass='BASE', window=WINDOW_TABLE_SEC):
    """Read-only: per row in the window, the phase, its reason, the allowed set and each path stage's node."""
    frames = {int(row['frame_index']): row for row in _rows(bundle, glass)
              if window[0] <= float(row['timestamp_sec']) <= window[1]}
    states = {}
    trace = bundle / 'debug' / 'debug_trace.jsonl'
    if not trace.is_file():
        _stop(f'no debug trace in {bundle}')
    with trace.open(encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            if record.get('glass_name') == glass and record.get('frame_index') in frames:
                states[record['frame_index']] = (record.get('sequence') or {}).get('state') or {}
    table = []
    for frame, row in sorted(frames.items()):
        state = states.get(frame, {})
        diagnostic = state.get('sequence_material_phase_diagnostics') or {}
        allowed = diagnostic.get('allowed_tracklet_ids')
        table.append(dict(
            time=float(row['timestamp_sec']), frame=frame, fill=row['fill_state'], oil=_y(row['raw_oil_air_level_y']),
            traced=frame in states, phase=state.get('sequence_material_phase'),
            phase_reason=state.get('sequence_material_phase_reason'),
            owner_chain=state.get('sequence_material_phase_owner_chain'),
            allowed_mode=diagnostic.get('allowed_mode'),
            allowed=None if allowed is None else sorted(allowed),
            stages={key: [state.get(f'sequence_stage_{key}_kind'), state.get(f'sequence_stage_{key}_y')]
                    for key in STAGE_KEYS}))
    return dict(bundle=str(bundle), glass=glass, window=list(window), rows=table)


def print_stages(result):
    print(f"stages {result['glass']} {result['window'][0]}-{result['window'][1]} s | bundle {result['bundle']}")
    print('-- time | frame | fill | oil | phase | phase reason | owner chain | allowed mode | allowed | '
          + ' | '.join(STAGE_KEYS) + ' --')
    for row in result['rows']:
        stage_text = ' | '.join(f'{kind}/{y}' for kind, y in row['stages'].values())
        allowed = '-' if row['allowed'] is None else ','.join(row['allowed']) or '(none)'
        print(f"{row['time']} | {row['frame']} | {row['fill']} | {row['oil']} | {row['phase']} | {row['phase_reason']} | "
              f"{row['owner_chain'] or '-'} | {row['allowed_mode']} | {allowed} | {stage_text}"
              + ('' if row['traced'] else ' | untraced'))


def shared_grid(reference, trial):
    """Rows at the reference's frames: per Glass and phase, rows, numeric Oil in both arms and changed rows."""
    ref_rows, trial_rows = tracking(reference), tracking(trial)
    tally = {}
    for key, a in ref_rows.items():
        b = trial_rows.get(key)
        time_sec = float(a['timestamp_sec'])
        phase = next(f'{lo}-{hi:g}' for lo, hi in PHASES_SEC if lo <= time_sec < hi)
        counts = tally.setdefault(f'{key[0]} {phase}', Counter())
        counts['rows'] += 1
        counts['missing'] += b is None
        if b is None:
            continue
        counts['oil_ref'] += _y(a['raw_oil_air_level_y']) is not None
        counts['oil_trial'] += _y(b['raw_oil_air_level_y']) is not None
        counts['changed'] += any(a[field] != b[field] for field in DIFF_FIELDS)
    return {key: dict(value) for key, value in sorted(tally.items())}


def cadence(reference, trial):
    out = {}
    for label, bundle in (('reference', reference), ('trial', trial)):
        base, accum = _rows(bundle, 'BASE'), _rows(bundle, 'Accum', required=False)
        out[label] = dict(run_id=_run_id(bundle), rows=dict(BASE=len(base), Accum=len(accum)),
                          readings=readings(base, accum or None))
    out['window'] = window_table(trial)
    out['shared_grid'] = shared_grid(reference, trial)
    return out


def print_cadence(result):
    for label in ('reference', 'trial'):
        item = result[label]
        r = item['readings']
        print(f"{label} run_id {item['run_id']} | rows BASE {item['rows']['BASE']}, Accum {item['rows']['Accum']}")
        print(f"  C1 first FULL {r['first_full_sec']} (top-exit flag {r['first_full_top_exit']}) -> {r['c1']} | "
              f"C2 hold rows {r['hold_rows']}, breaks {len(r['hold_breaks'])} -> {r['c2']} | "
              f"C3 episode end {r['episode_end_sec']} -> {r['c3']} | C4 late FULL {r['late_full_rows']} -> {r['c4']} | "
              f"C5 Accum FULL {r['accum_full_rows']} -> {r['c5']}")
        for row in r['hold_breaks']:
            print(f'  break {row}')
    window = result['window']
    print(f"-- trial BASE {WINDOW_TABLE_SEC[0]}-{WINDOW_TABLE_SEC[1]} s (traced {window['traced']}, band end "
          f"Y{window['band_end_y']}, admitted min Y {window['admitted_min_y']}): time | frame | fill | oil | foam | "
          f"top-exit flag | selected y / tracklet / lifecycle / admitted | top-exit reason --")
    for row in window['rows']:
        selected = ' / '.join(map(str, row['selected'])) if row['selected'] else '-'
        print(f"{row['time']} | {row['frame']} | {row['fill']} | {row['oil']} | {row['foam']} | "
              f"{row['top_exit_flag']} | {selected} | {row['top_exit_reason']}")
    print('-- shared 2 fps grid: glass phase s | rows | missing | oil ref/trial | changed --')
    for key, counts in result['shared_grid'].items():
        print(f"{key} | {counts.get('rows', 0)} | {counts.get('missing', 0)} | {counts.get('oil_ref', 0)}/"
              f"{counts.get('oil_trial', 0)} | {counts.get('changed', 0)}")


def _write(result, out, name):
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    path.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(f"json {path.name} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    run_parser = sub.add_parser('run', help='a saved bundle session at another rate or debug level')
    run_parser.add_argument('--reference-bundle', type=Path, required=True)
    run_parser.add_argument('--out', type=Path, required=True)
    run_parser.add_argument('--sampling-fps', type=float)
    run_parser.add_argument('--debug', choices=DEBUG_LEVELS)
    run_parser.add_argument('--video', type=Path, help='the video, if it moved since the saved session')
    run_parser.add_argument('--run-name')
    run_parser.add_argument('--parallel-glasses', action='store_true', help='one worker process per Glass (opt-in)')
    for name in ('identity', 'cadence'):
        compare_parser = sub.add_parser(name)
        compare_parser.add_argument('--reference', type=Path, required=True)
        compare_parser.add_argument('--trial', type=Path, required=True)
        compare_parser.add_argument('--out', type=Path, required=True)
    stages_parser = sub.add_parser('stages', help='read-only: phase, allowed set and path stages per row')
    stages_parser.add_argument('--bundle', type=Path, required=True)
    stages_parser.add_argument('--glass-name', default='BASE')
    stages_parser.add_argument('--start', type=float, default=WINDOW_TABLE_SEC[0])
    stages_parser.add_argument('--end', type=float, default=WINDOW_TABLE_SEC[1])
    stages_parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'run':
        run(args.reference_bundle, args.out, fps=args.sampling_fps, debug=args.debug, video=args.video,
            run_name=args.run_name, parallel_glasses=args.parallel_glasses)
    elif args.command == 'stages':
        result = stages(args.bundle, args.glass_name, (args.start, args.end))
        print_stages(result)
        _write(result, args.out, f'cadence-stages-{args.glass_name}.json')
    elif args.command == 'identity':
        result = identity(args.reference, args.trial)
        print_identity(result)
        _write(result, args.out, 'cadence-identity.json')
    else:
        result = cadence(args.reference, args.trial)
        print_cadence(result)
        _write(result, args.out, 'cadence-compare.json')


if __name__ == '__main__':
    main()
