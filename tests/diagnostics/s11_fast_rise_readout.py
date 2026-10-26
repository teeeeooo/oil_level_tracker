"""Fast-rise readout: witnessed upward triplets beyond the association cap in a saved bundle. Read-only.

Rebuilds each analysed frame's tracklet row hypotheses from a FULL debug trace
(the `sequence_row_hypothesis_id` groups of builder-eligible Oil candidates) and
applies the frozen seed's row conditions with the builder's own policy and
`_independent_witness` minima. It answers the frozen first Windows step of the
fast-rise association checks: does a witnessed upward triplet beyond the cap, in
a constant-velocity line, exist? It does not test the seed's tracklet conditions
(single-row, unassigned A and B; uniqueness), which only a run can. See
docs/30-validation/s11-physical-interface-evidence-repair-validation.md#fast-rise-association-checks--2026-10-23.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory

from oil_tracker.adapters.vision.oil_candidate_authority import OilCandidateAuthority
from oil_tracker.adapters.vision.oil_interface_tracklets import FAST_RISE_MAX_CAP_MULTIPLE

TRIPLET_LINES = 40
ROW_FIELDS = ('id', 'y', 'members', 'classes', 'anchor', 'physical', 'motion', 'coverage', 'witness')


def _unit(value):
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def policy_for(glass):
    """The production tracklet policy values the seed uses, for one Glass."""
    from oil_tracker.adapters.vision import oil_observation_resolver as resolver
    policy = resolver._tracklet_policy((), glass, resolver.OilObservationResolverConfig())
    return dict(cap=float(policy.maximum_jump_px), bound=float(policy.maximum_jump_px) * FAST_RISE_MAX_CAP_MULTIPLE,
                row_tolerance=float(policy.row_hypothesis_tolerance_px),
                motion_min=float(policy.confirmation_min_motion_support),
                coverage_min=float(policy.confirmation_min_motion_coverage))


TIERS = {item.name: int(item) for item in OilCandidateAuthority}


def joined(record):
    """The sequence snapshot's Oil candidates, each with its detector features (matched on source and y).

    The snapshot carries authority, ordered-lower and the row and tracklet IDs; the detector features carry the
    registered motion and the high-recall flag. A key that matches several detector candidates is marked ambiguous.
    """
    features = {}
    for candidate in record['candidates']:
        if candidate['kind'] == 'oil_air':
            features.setdefault((candidate['source'], float(candidate['canonical_y'])), []).append(candidate['features'])
    out = []
    for candidate in (record.get('sequence') or {}).get('candidates', []):
        if candidate['kind'] == 'oil_air':
            matches = features.get((candidate['source'], float(candidate['canonical_y'])), [])
            out.append((candidate, matches))
    return out


def member(candidate, matches):
    """One builder-eligible Oil candidate, or None. Eligibility is the builder's: post-track tier >= CONTINUATION."""
    tier = TIERS.get(candidate.get('post_track_authority'))
    if tier is None or tier < OilCandidateAuthority.CONTINUATION_ELIGIBLE:
        return None
    if not matches:
        raise SystemExit(f"STOP: no detector candidate for {candidate['source']} y {candidate['canonical_y']}")
    high_recall = [_unit(f.get('calibrated_high_recall', f.get('r9_calibrated_high_recall', 0.0))) >= 0.5
                   for f in matches]
    return dict(
        y=float(candidate['canonical_y']), source=candidate['source'], tier=tier,
        initial_tier=candidate.get('initial_authority'), final_tier=candidate.get('authority'),
        authority_reason=candidate.get('authority_reason'),
        ordered_lower=_unit(candidate.get('ordered_lower') or 0.0) >= 0.5,
        # Several matches: the most permissive reading, so a witness is never missed.
        high_recall=all(high_recall), ambiguous_join=len(matches) > 1,
        motion=max(_unit(f.get('registered_oil_band_motion_support', 0.0)) for f in matches),
        coverage=max(_unit(f.get('registered_oil_band_motion_coverage', 0.0)) for f in matches),
        row_id=candidate.get('row_hypothesis_id') or '',
        tracklet=candidate.get('tracklet_id') or '',
        lifecycle=candidate.get('tracklet_lifecycle'),
        admitted=_unit(candidate.get('tracklet_admitted') or 0.0) >= 0.5,
        failure=candidate.get('tracklet_failure_reason'),
        selected=bool(candidate.get('selected')))


def rows_of(members, params):
    """Row hypotheses as the builder forms them: the trace's row groups; id-less members grouped by its span rule."""
    groups, loose = {}, []
    for item in members:
        (groups.setdefault(item['row_id'], []) if item['row_id'] else loose).append(item)
    for item in sorted(loose, key=lambda m: m['y']):
        if loose_groups := [k for k in groups if k.startswith('no-id:')]:
            last = groups[loose_groups[-1]]
            span = max(max(m['y'] for m in last), item['y']) - min(min(m['y'] for m in last), item['y'])
            if span <= params['row_tolerance']:
                last.append(item)
                continue
        groups[f'no-id:{len(loose_groups)}'] = [item]
    rows = []
    for key, items in groups.items():
        row = dict(
            id=key, y=float(median(m['y'] for m in items)), members=len(items),
            classes=sorted({'ordered_lower' if m['ordered_lower'] else 'direct' for m in items}),
            anchor=any(m['tier'] == OilCandidateAuthority.ANCHOR_ELIGIBLE for m in items),
            physical=any(not m['high_recall'] for m in items),
            motion=max(m['motion'] for m in items), coverage=max(m['coverage'] for m in items),
            tracklet=items[0]['tracklet'], lifecycle=items[0]['lifecycle'], admitted=items[0]['admitted'],
            failure=items[0]['failure'], selected=any(m['selected'] for m in items),
            tiers=sorted({m['tier'] for m in items}))
        row['witness'] = bool(row['anchor'] and row['physical'] and row['motion'] >= params['motion_min']
                              and row['coverage'] >= params['coverage_min'])
        rows.append(row)
    return sorted(rows, key=lambda r: r['y'])


def triplets(frames, params):
    """Every upward beyond-cap step pair over three consecutive analysed frames, with the seed's row conditions."""
    found = []
    for first, second, third in zip(frames, frames[1:], frames[2:]):
        if not (second['offset'] == first['offset'] + 1 and third['offset'] == second['offset'] + 1):
            continue
        for a in first['rows']:
            for b in second['rows']:
                for c in third['rows']:
                    steps = (b['y'] - a['y'], c['y'] - b['y'])
                    if not all(-params['bound'] <= step < -params['cap'] for step in steps):
                        continue
                    found.append(dict(
                        times=[first['time'], second['time'], third['time']],
                        frames=[first['frame'], second['frame'], third['frame']],
                        ys=[a['y'], b['y'], c['y']], steps=[round(s, 2) for s in steps],
                        constant_velocity=abs(steps[1] - steps[0]) <= params['row_tolerance'],
                        same_representation=bool(set(a['classes']) & set(b['classes']) & set(c['classes'])),
                        witness=[a['witness'], b['witness'], c['witness']],
                        tracklets=[a['tracklet'], b['tracklet'], c['tracklet']]))
    for item in found:
        item['qualifies'] = bool(item['constant_velocity'] and item['same_representation'] and all(item['witness']))
    return found


def bundle_frames(bundle, glass_name):
    """Analysed frames for one Glass of a FULL-debug bundle, with offsets in analysis order."""
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository

    recipe = JsonRecipeRepository().load(bundle / 'recipe_snapshot.oilrecipe')
    (glass,) = [item for item in recipe.glasses if item.name == glass_name]
    with (bundle / 'tracking_data.csv').open(encoding='utf-8-sig', newline='') as handle:
        tracking = {int(row['frame_index']): row for row in csv.DictReader(handle) if row['glass_id'] == str(glass.id)}
    records, run_ids = {}, set()
    with (bundle / 'debug' / 'debug_trace.jsonl').open(encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            if record.get('glass_id') == str(glass.id):
                run_ids.add(record.get('run_id'))
                records[int(record['frame_index'])] = record
    missing = sorted(set(tracking) - set(records))
    if missing:
        raise SystemExit(f'STOP: {len(missing)} tracking rows have no debug record (first {missing[:5]}); FULL debug is required')
    params = policy_for(glass)
    frames = []
    for offset, index in enumerate(sorted(tracking)):
        record = records[index]
        if 'sequence' not in record:
            raise SystemExit(f'STOP: frame {index} has no sequence snapshot; FULL debug is required')
        pairs = joined(record)
        members = [m for m in (member(c, matches) for c, matches in pairs) if m is not None]
        value = tracking[index]['raw_oil_air_level_y']
        frames.append(dict(
            offset=offset, frame=index, time=float(tracking[index]['timestamp_sec']),
            fill_state=tracking[index]['fill_state'], oil_y=float(value) if value not in ('', None) else None,
            oil_candidates=len(pairs), eligible=len(members),
            ambiguous_joins=sum(m['ambiguous_join'] for m in members),
            members=members, rows=rows_of(members, params)))
    info = dict(run_ids=sorted(map(str, run_ids)), glass_id=str(glass.id),
                version=next(iter(records.values()))['sequence']['state'].get('sequence_resolver_version'))
    return frames, params, info


def readout(frames, params, start, end):
    window = [f for f in frames if start <= f['time'] <= end]
    rows = [r for f in window for r in f['rows']]
    found = triplets(window, params)
    counts = dict(
        frames=len(window), oil_candidates=sum(f['oil_candidates'] for f in window),
        eligible=sum(f['eligible'] for f in window), ambiguous_joins=sum(f['ambiguous_joins'] for f in window),
        rows=len(rows),
        anchor=sum(r['anchor'] for r in rows), physical=sum(r['physical'] for r in rows),
        motion=sum(r['motion'] >= params['motion_min'] and r['coverage'] >= params['coverage_min'] for r in rows),
        witnessed=sum(r['witness'] for r in rows),
        upward_beyond_cap=len(found), constant_velocity=sum(t['constant_velocity'] for t in found),
        same_representation=sum(t['constant_velocity'] and t['same_representation'] for t in found),
        qualifying=sum(t['qualifies'] for t in found))
    return window, found, counts


def _flag(value):
    return 'Y' if value else '-'


def print_readout(info, glass_name, params, window, found, counts, *, summary_only):
    print(f"run_id {','.join(info['run_ids'])} | glass {glass_name} | version {info['version']}")
    print(f"cap {params['cap']} | bound {params['bound']} | row_tolerance {params['row_tolerance']} | "
          f"motion_min {params['motion_min']} | coverage_min {params['coverage_min']}")
    print(' | '.join(f'{key} {value}' for key, value in counts.items()))
    if summary_only:
        return
    print('-- rows: time | frame | output | y | members | classes | tiers | anchor | physical | motion | coverage | '
          'witness | tracklet | lifecycle | admitted | failure | selected --')
    for frame in window:
        if not frame['rows']:
            print(f"{frame['time']} | {frame['frame']} | {frame['oil_y']} | (no eligible row; "
                  f"{frame['oil_candidates']} Oil candidates)")
        for row in frame['rows']:
            print(f"{frame['time']} | {frame['frame']} | {frame['oil_y']} | {row['y']} | {row['members']} | "
                  f"{'+'.join(row['classes'])} | {','.join(map(str, row['tiers']))} | {_flag(row['anchor'])} | "
                  f"{_flag(row['physical'])} | {row['motion']:.3f} | {row['coverage']:.3f} | {_flag(row['witness'])} | "
                  f"{row['tracklet']} | {row['lifecycle']} | {_flag(row['admitted'])} | {row['failure']} | "
                  f"{_flag(row['selected'])}")
    listed = [item for item in found if item['constant_velocity']]
    print(f'-- constant-velocity triplets (upward, beyond the cap), {len(listed)} of {len(found)}, first '
          f'{TRIPLET_LINES}: times | ys | steps | constant velocity | same representation | witness per row | '
          'tracklets | qualifies --')
    for item in listed[:TRIPLET_LINES]:
        print(f"{item['times']} | {item['ys']} | {item['steps']} | {_flag(item['constant_velocity'])} | "
              f"{_flag(item['same_representation'])} | {''.join(_flag(w) for w in item['witness'])} | "
              f"{item['tracklets']} | {_flag(item['qualifies'])}")


# --- local check: does the trace reader rebuild the builder's row hypotheses? ------------------

def live_rows():
    """Patch the builder to record every row hypothesis it forms, per resolve call."""
    from contextlib import contextmanager
    from unittest.mock import patch

    from oil_tracker.adapters.vision.oil_interface_tracklets import DirectedInterfaceTrackletBuilder

    @contextmanager
    def capture():
        calls = []
        original_resolve = DirectedInterfaceTrackletBuilder.resolve
        original_rows = DirectedInterfaceTrackletBuilder._row_hypotheses

        def resolve(self, *args, **kwargs):
            calls.append({})
            return original_resolve(self, *args, **kwargs)

        def row_hypotheses(self, frame_offset, refs):
            hypotheses = original_rows(self, frame_offset, refs)
            calls[-1][frame_offset] = [dict(
                id=h.identity, y=float(h.y), members=len(h.members), classes=sorted(h.representation_classes),
                anchor=bool(h.anchor_signal), physical=bool(h.has_physical_proposal), motion=float(h.motion_support),
                coverage=float(h.motion_coverage), witness=bool(self._independent_witness(h))) for h in hypotheses]
            return hypotheses

        with patch.object(DirectedInterfaceTrackletBuilder, 'resolve', resolve), \
                patch.object(DirectedInterfaceTrackletBuilder, '_row_hypotheses', row_hypotheses):
            yield calls
    return capture()


def bundle_check(work, sample='sample5'):
    """One FULL-debug local run (IFO v2 + top-exit v3) through the bundle path; compare the reader with the builder."""
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.enums import InitialObservationState
    from oil_tracker.domain.session import DebugTraceLevel, InitialStateConfirmation
    from tests.diagnostics.s11_fast_fill_cadence import ROI_INPUTS, ROOT
    from tests.diagnostics.s11_initial_full_comparison import EMPTY_FILL_CONTROLS
    from tests.diagnostics.s11_report_observability_replay import _session

    video, recipe_path = ROOT / 'sample' / f'{sample}.mp4', ROI_INPUTS / f'{sample}.oilrecipe'
    with TemporaryDirectory(dir=work) as scratch:
        _, session = _session(sample, video, Path(scratch), *EMPTY_FILL_CONTROLS[sample]['window'],
                              run_label='fast-rise readout', run_note='bundle check', recipe_path=recipe_path)
        session.debug_trace_level = DebugTraceLevel.FULL
        recipe = JsonRecipeRepository().load(recipe_path)
        for glass in recipe.glasses:
            glass.initial_state = InitialObservationState.EMPTY_NO_INTERFACE
            session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
                InitialObservationState.EMPTY_NO_INTERFACE, str(video), session.analysis_start_sec)
        with live_rows() as calls:
            result = AnalysisPipeline(OpenCvVideoReader, OpenCvPhaseDetector(initial_full_observation=True,
                                                                             top_exit_full=True),
                                      RecipeValidationService(), JsonlDebugTraceWriterFactory(Path(scratch))).run(recipe, session)
        if result.errors:
            raise SystemExit(f'STOP: analysis errors {result.errors}')
        bundle = OutputBundleStore().write_bundle(result, recipe, session, Path(scratch))
        (glass,) = [item for item in recipe.glasses if item.enabled]
        frames, params, info = bundle_frames(bundle, glass.name)
        main(['--bundle', str(bundle), '--glass-name', glass.name, '--start', '0', '--end', '1e9',
              '--work', str(work), '--summary-only'])  # the Windows entry on the same bundle
    live = calls[-1]
    differences = []
    for frame in frames:
        read = [{key: row[key] for key in ROW_FIELDS} for row in frame['rows']]
        direct = sorted(live.get(frame['offset'], []), key=lambda r: r['y'])
        if read != direct:
            differences.append(dict(frame=frame['frame'], offset=frame['offset'], bundle=read, live=direct))
    return dict(sample=sample, resolve_calls=len(calls), frames=len(frames), params=params, version=info['version'],
                live_rows=sum(len(rows) for rows in live.values()), bundle_rows=sum(len(f['rows']) for f in frames),
                witnessed=sum(r['witness'] for f in frames for r in f['rows']),
                triplets=len(triplets(frames, params)), differences=differences)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--work', type=Path, required=True, help='output folder for the JSON')
    parser.add_argument('--bundle', type=Path, help='a saved FULL-debug bundle (no detector run)')
    parser.add_argument('--glass-name')
    parser.add_argument('--start', type=float, default=0.0)
    parser.add_argument('--end', type=float, default=1e9)
    parser.add_argument('--summary-only', action='store_true', help='print the three header lines only')
    parser.add_argument('--bundle-check', action='store_true', help='local: the reader against one live run')
    args = parser.parse_args(argv)
    args.work.mkdir(parents=True, exist_ok=True)
    if args.bundle_check:
        check = bundle_check(args.work)
        (args.work / 'fast-rise-readout-check.json').write_text(json.dumps(check, indent=1) + '\n', encoding='utf-8')
        print(json.dumps({key: value for key, value in check.items() if key != 'differences'}
                         | dict(differences=len(check['differences']))))
        return
    frames, params, info = bundle_frames(args.bundle, args.glass_name)
    window, found, counts = readout(frames, params, args.start, args.end)
    out = args.work / f"fast-rise-readout-{info['glass_id']}.json"
    out.write_text(json.dumps(dict(bundle=str(args.bundle), glass=args.glass_name, info=info, params=params,
                                   window=[args.start, args.end], counts=counts, triplets=found,
                                   frames=window), indent=1) + '\n', encoding='utf-8')
    print_readout(info, args.glass_name, params, window, found, counts, summary_only=args.summary_only)
    print(f"json {out.name} sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}")


if __name__ == '__main__':
    main()
