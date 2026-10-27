"""Level authority readout: why the Oil candidates at a reviewed level mark have their authority tier. Read-only.

Reads a saved bundle's FULL debug trace. For each `time:y` mark it prints every Oil candidate within `--near` px of the
mark, one line per candidate: the initial authority with its reason and failed gates, the phase identity and its
failed gates, the post-track authority and recurring-row opposition, the candidate-local contradiction inputs of the
recurrence demotion (`recurrence_hard_contradiction`) and the reject stage. For each candidate with opposition it also
prints how often an Oil candidate recurs at that height over the whole Glass trace, an approximation of the
resolver's recurring-row check (`OilTrackletOppositionOwner._apply_track_opposition`). It runs no detector.
See docs/50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tests.diagnostics.s11_cadence_field import _rows
from tests.diagnostics.s11_layer_bottom_topology_2_field import _stop
from tests.diagnostics.s11_level_coverage_readout import TIME_TOLERANCE_SEC, parse_marks

RECURRING_TOLERANCE_RATIO = 0.018  # recurring_track_tolerance_ratio
REJECT_OPPOSITION = 0.60  # recurring_track_reject_opposition
SNAPSHOT_FIELDS = (
    'source', 'initial_authority', 'authority_reason', 'authority_failed_gates', 'phase_identity',
    'phase_identity_failed_gates', 'post_track_authority', 'track_opposition', 'effective_track_opposition',
    'reject_stage',
)
LOCAL_FIELDS = (  # the inputs of recurrence_hard_contradiction, read from the detector candidate
    'material_texture_conflict', 'artifact_likelihood', 'static_prior_contribution', 'optics',
    'registered_oil_band_motion_support', 'registered_oil_band_motion_coverage',
)


def _float(value):
    try:
        return round(float(value), 3)
    except (TypeError, ValueError):
        return None


def local_fields(features: dict, penalties: dict) -> dict:
    optics = max(_float(penalties.get('optics_conflict')) or 0.0,
                 _float(penalties.get('glare_conflict', penalties.get('glare_penalty'))) or 0.0)
    return dict(
        material_texture_conflict=max(_float(features.get('material_texture_conflict')) or 0.0,
                                      _float(penalties.get('material_texture_conflict')) or 0.0),
        artifact_likelihood=_float(features.get('artifact_likelihood', penalties.get('artifact_likelihood'))),
        static_prior_contribution=_float(features.get('static_prior_contribution',
                                                      penalties.get('static_artifact_penalty'))),
        optics=round(optics, 3),
        registered_oil_band_motion_support=_float(features.get('registered_oil_band_motion_support')),
        registered_oil_band_motion_coverage=_float(features.get('registered_oil_band_motion_coverage')))


def recurrence(all_ys: dict[int, list[float]], y: float, tolerance: float, times: dict[int, float]) -> dict:
    """Frames with an Oil candidate within the tolerance of y, and their longest consecutive run."""
    frames = sorted(frame for frame, ys in all_ys.items() if any(abs(v - y) <= tolerance for v in ys))
    order = {frame: index for index, frame in enumerate(sorted(all_ys))}
    best, start, run_start, previous = 0, None, None, None
    for frame in frames:
        if previous is None or order[frame] != order[previous] + 1:
            run_start = frame
        length = order[frame] - order[run_start] + 1
        if length > best:
            best, start = length, run_start
        previous = frame
    end = None if start is None else frames[frames.index(start) + best - 1]
    return dict(present=len(frames), of=len(all_ys), longest_run=best,
                run=None if start is None else [times[start], times[end]])


def readout(bundle: Path, glass: str, marks: list[tuple[float, float]], near: float) -> dict:
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository

    recipe = JsonRecipeRepository().load(bundle / 'recipe_snapshot.oilrecipe')
    config = next((g for g in recipe.glasses if g.name == glass), None)
    if config is None:
        _stop(f'no Glass {glass} in the Recipe snapshot')
    height = max(1.0, float(config.geometry.ellipse.radius_y) * 2.0)
    tolerance = max(3.0, height * RECURRING_TOLERANCE_RATIO)
    tracking = _rows(bundle, glass)
    times = {int(r['frame_index']): float(r['timestamp_sec']) for r in tracking}
    wanted = {}
    for mark_time, mark_y in marks:
        row = min(tracking, key=lambda r: abs(float(r['timestamp_sec']) - mark_time), default=None)
        if row is None or abs(float(row['timestamp_sec']) - mark_time) > TIME_TOLERANCE_SEC:
            _stop(f'no tracking row within {TIME_TOLERANCE_SEC} s of mark time {mark_time}')
        wanted[int(row['frame_index'])] = (mark_time, mark_y)
    trace = bundle / 'debug' / 'debug_trace.jsonl'
    if not trace.is_file():
        _stop(f'no debug trace in {bundle}')
    all_ys, records, run_ids = {}, {}, set()
    with trace.open(encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            if record.get('glass_name') != glass:
                continue
            if 'sequence' not in record:
                _stop(f"record {record.get('record_id')} has no sequence snapshot")
            frame = record.get('frame_index')
            all_ys[frame] = [float(c['canonical_y']) for c in record['sequence'].get('candidates') or ()
                             if c.get('kind') == 'oil_air' and c.get('canonical_y') is not None]
            if frame in wanted:
                records[frame] = record
                run_ids.add(record.get('run_id'))
    frames, joins_missing, joins_ambiguous = [], 0, 0
    for frame, (mark_time, mark) in sorted(wanted.items()):
        record = records.get(frame)
        if record is None:
            _stop(f'no trace record for frame {frame}')
        detector = {}
        for candidate in record.get('candidates') or ():
            if candidate.get('kind') == 'oil_air':
                detector.setdefault((candidate.get('source'), float(candidate['canonical_y'])), []).append(candidate)
        lines = []
        for candidate in record['sequence'].get('candidates') or ():
            if candidate.get('kind') != 'oil_air' or candidate.get('canonical_y') is None:
                continue
            distance = float(candidate['canonical_y']) - mark
            if abs(distance) > near:
                continue
            matches = detector.get((candidate.get('source'), float(candidate['canonical_y'])), [])
            joins_missing += not matches
            joins_ambiguous += len(matches) > 1
            local = local_fields(matches[0].get('features') or {}, matches[0].get('penalties') or {}) if len(matches) == 1 \
                else {f: None for f in LOCAL_FIELDS}
            opposition = _float(candidate.get('track_opposition')) or 0.0
            lines.append(dict(
                y=float(candidate['canonical_y']), d=round(distance, 1), join=len(matches),
                **{f: candidate.get(f) for f in SNAPSHOT_FIELDS}, **local,
                recurrence=recurrence(all_ys, float(candidate['canonical_y']), tolerance, times)
                if opposition > 0.0 else None))
        lines.sort(key=lambda item: (abs(item['d']), item['y'], str(item['source'])))
        frames.append(dict(time=mark_time, frame=frame, mark=mark, candidates=lines))
    return dict(bundle=str(bundle), glass=glass, run_ids=sorted(map(str, run_ids)), near_px=near,
                recurring_tolerance_px=round(tolerance, 3), trace_frames=len(all_ys),
                joins_missing=joins_missing, joins_ambiguous=joins_ambiguous, frames=frames)


def _value(value) -> str:
    if value is None:
        return '-'
    if isinstance(value, (list, tuple)):
        return ';'.join(map(_value, value)) or '-'
    if isinstance(value, float):
        return f'{value:.3f}'.rstrip('0').rstrip('.') if value % 1 else str(value)
    return str(value).split(':')[0] if isinstance(value, str) and value.startswith('oil_hypothesis:') else str(value)


def print_readout(result: dict) -> None:
    print(f"level authority readout {result['glass']} | bundle {result['bundle']} | run_id {','.join(result['run_ids'])} | "
          f"near <= {result['near_px']} px | recurring tolerance {result['recurring_tolerance_px']} px | "
          f"trace frames {result['trace_frames']} | joins missing {result['joins_missing']} ambiguous {result['joins_ambiguous']}")
    print('-- candidates: time | mark | y | d | ' + ' | '.join(SNAPSHOT_FIELDS + LOCAL_FIELDS)
          + ' | recurrence present/of, longest run, run span s --')
    for frame in result['frames']:
        for line in frame['candidates']:
            recur = line['recurrence']
            recur_text = '-' if recur is None else (
                f"{recur['present']}/{recur['of']}, {recur['longest_run']}, {_value(recur['run'])}")
            print(f"{frame['time']:.3f} | {frame['mark']} | {line['y']} | {line['d']} | "
                  + ' | '.join(_value(line[f]) for f in SNAPSHOT_FIELDS + LOCAL_FIELDS) + f" | {recur_text}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--glass-name', default='BASE')
    parser.add_argument('--marks', required=True, help='comma-separated time:y pairs (source Y)')
    parser.add_argument('--near', type=float, default=32.0)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    result = readout(args.bundle, args.glass_name, parse_marks(args.marks), args.near)
    print_readout(result)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / 'level_authority_readout.json'
    path.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(f"json {path.name} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


if __name__ == '__main__':
    main()
