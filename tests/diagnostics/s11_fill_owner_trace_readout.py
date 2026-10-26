"""Fill-owner trace readout: per row, the lifecycle's fill owners and their tracklets' fixed and recent fields. Read-only.

Reads a saved bundle's FULL debug trace (the `sequence` snapshot of each record) and its tracking rows. Per row in
the window it prints the phase, its reason, the owner chain, the established fill owner, the dynamic fill owners
and the allowed set. Per Oil candidate whose tracklet is a dynamic owner of its frame or is named on the command
line, it prints the tracklet's confirmation profile and frames, its fixed direction, net progress and directional
agreement, the same three over the recent window, and FOR-1's recent-motion pass `P`. It runs no detector.
See docs/50-diagnostics/s11/2026-10-27-fill-owner-recency-local.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tests.diagnostics.s11_cadence_field import _rows
from tests.diagnostics.s11_layer_bottom_topology_2_field import _stop, _y

MINIMUM_DIRECTIONAL_AGREEMENT = 0.60  # tracklet_confirmation_min_directional_agreement
DRAIN_MINIMUM_PROGRESS_RATIO = 0.025  # completed_fill_release_min_downward_ratio
DEFAULT_TRACKLETS = ('0018', '0035')  # SPL#4 BASE owners of the 22.5-27.0 s ambiguity


def minimum_progress(bundle: Path, glass: str) -> tuple[float, float]:
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository

    recipe = JsonRecipeRepository().load(bundle / 'recipe_snapshot.oilrecipe')
    config = next((g for g in recipe.glasses if g.name == glass), None)
    if config is None:
        _stop(f'no Glass {glass} in the Recipe snapshot')
    height = max(1.0, float(config.geometry.ellipse.radius_y) * 2.0)
    return height, max(4.0, height * DRAIN_MINIMUM_PROGRESS_RATIO)


def recent_pass(candidate: dict, progress: float) -> bool:
    return bool(
        (candidate.get('tracklet_recent_direction') or 0) < 0
        and (candidate.get('tracklet_recent_directional_agreement') or 0.0) >= MINIMUM_DIRECTIONAL_AGREEMENT
        and (candidate.get('tracklet_recent_net_progress_px') or 0.0) >= progress
    )


def readout(bundle: Path, glass: str, window: tuple[float, float], tracklets=DEFAULT_TRACKLETS) -> dict:
    rows = {int(row['frame_index']): row for row in _rows(bundle, glass)
            if window[0] <= float(row['timestamp_sec']) <= window[1]}
    trace = bundle / 'debug' / 'debug_trace.jsonl'
    if not trace.is_file():
        _stop(f'no debug trace in {bundle}')
    records, run_ids = {}, set()
    with trace.open(encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            if record.get('glass_name') == glass and record.get('frame_index') in rows:
                if 'sequence' not in record:
                    _stop(f"record {record.get('record_id')} has no sequence snapshot")
                records[record['frame_index']] = record['sequence']
                run_ids.add(record.get('run_id'))
    height, progress = minimum_progress(bundle, glass)
    suffixes = tuple(f':{name}' for name in tracklets)
    frames, owner_rows = [], []
    for frame, row in sorted(rows.items()):
        sequence = records.get(frame)
        state = {} if sequence is None else sequence.get('state') or {}
        diagnostic = state.get('sequence_material_phase_diagnostics') or {}
        dynamic = sorted(diagnostic.get('dynamic_fill_owner_ids') or ())
        allowed = diagnostic.get('allowed_tracklet_ids')
        time_sec = float(row['timestamp_sec'])
        frames.append(dict(
            time=time_sec, frame=frame, fill=row['fill_state'], oil=_y(row['raw_oil_air_level_y']),
            traced=sequence is not None, phase=state.get('sequence_material_phase'),
            reason=state.get('sequence_material_phase_reason'),
            owner_chain=state.get('sequence_material_phase_owner_chain'),
            established=[diagnostic.get('established_fill_owner'), diagnostic.get('established_fill_last_y')],
            dynamic=dynamic, allowed=None if allowed is None else sorted(allowed)))
        for candidate in [] if sequence is None else sequence.get('candidates') or ():
            identity = candidate.get('tracklet_id') or ''
            if candidate.get('kind') != 'oil_air' or not (identity in dynamic or identity.endswith(suffixes)):
                continue
            merged = next((item for item in owner_rows if item['frame'] == frame and item['tracklet'] == identity), None)
            if merged is not None:  # the tracklet fields are per tracklet; only the candidate Y and selection vary
                merged['y'] = sorted(merged['y'] + [candidate.get('canonical_y')])
                merged['selected'] = merged['selected'] or bool(candidate.get('selected'))
                continue
            owner_rows.append(dict(
                time=time_sec, frame=frame, tracklet=identity, y=[candidate.get('canonical_y')],
                selected=bool(candidate.get('selected')), lifecycle=candidate.get('tracklet_lifecycle'),
                admitted=candidate.get('tracklet_admitted'), profile=candidate.get('tracklet_confirmation_profile'),
                confirmation=[candidate.get('tracklet_confirmation_start_frame'),
                              candidate.get('tracklet_confirmation_end_frame')],
                fixed=[candidate.get('tracklet_direction'), candidate.get('tracklet_net_progress_px'),
                       candidate.get('tracklet_directional_agreement')],
                recent=[candidate.get('tracklet_recent_direction'), candidate.get('tracklet_recent_net_progress_px'),
                        candidate.get('tracklet_recent_directional_agreement')],
                recent_end=candidate.get('tracklet_recent_window_end_frame'),
                motion=[candidate.get('tracklet_motion_support'), candidate.get('tracklet_motion_coverage')],
                passes=recent_pass(candidate, progress), dynamic=identity in dynamic))
    return dict(bundle=str(bundle), glass=glass, window=list(window), run_ids=sorted(map(str, run_ids)),
                geometry_height=height, minimum_recent_progress_px=round(progress, 3),
                tracklets=list(tracklets), frames=frames, owner_rows=owner_rows)


def _text(values) -> str:
    return ' / '.join('-' if value is None else str(value) for value in values)


def print_readout(result: dict) -> None:
    print(f"fill-owner trace readout {result['glass']} {result['window'][0]}-{result['window'][1]} s | "
          f"bundle {result['bundle']} | run_id {','.join(result['run_ids'])} | H {result['geometry_height']} | "
          f"P progress >= {result['minimum_recent_progress_px']} px")
    print('-- frames: time | frame | fill | oil | phase | reason | owner chain | established owner / last y | '
          'dynamic owners | allowed --')
    for row in result['frames']:
        allowed = '-' if row['allowed'] is None else ','.join(row['allowed']) or '(none)'
        print(f"{row['time']:.3f} | {row['frame']} | {row['fill']} | {row['oil']} | {row['phase']} | {row['reason']} | "
              f"{row['owner_chain'] or '-'} | {_text(row['established'])} | {','.join(row['dynamic']) or '(none)'} | "
              f"{allowed}" + ('' if row['traced'] else ' | untraced'))
    print('-- owner rows (one per tracklet and frame): time | frame | tracklet | candidate ys | any selected | lifecycle | admitted | profile | '
          'confirmation start / end | fixed dir / net / agree | recent dir / net / agree | recent end | '
          'motion support / coverage | P | dynamic --')
    for row in result['owner_rows']:
        print(f"{row['time']:.3f} | {row['frame']} | {row['tracklet']} | {','.join(map(str, row['y']))} | {row['selected']} | "
              f"{row['lifecycle']} | {row['admitted']} | {row['profile']} | {_text(row['confirmation'])} | "
              f"{_text(row['fixed'])} | {_text(row['recent'])} | {row['recent_end']} | {_text(row['motion'])} | "
              f"{row['passes']} | {row['dynamic']}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--glass-name', default='BASE')
    parser.add_argument('--start', type=float, default=20.0)
    parser.add_argument('--end', type=float, default=28.0)
    parser.add_argument('--tracklets', default=','.join(DEFAULT_TRACKLETS),
                        help='tracklet ID suffixes to print besides the dynamic owners')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    names = tuple(name for name in args.tracklets.split(',') if name)
    result = readout(args.bundle, args.glass_name, (args.start, args.end), names)
    print_readout(result)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / 'fill_owner_trace_readout.json'
    path.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(f"json {path.name} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


if __name__ == '__main__':
    main()
