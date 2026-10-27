"""Level peer readout: the same-frame partition peers of demoted level candidates. Read-only.

Reads a saved bundle's FULL debug trace. For each `time:y` mark it lists the demoted level candidates (within
`--near` px of the mark, post-track `CANDIDATE_ONLY`, track opposition >= 0.60) and every Oil candidate of the same
frame that meets the structural conditions of the superior-partition demotion in
`OilTrackletOppositionOwner._apply_track_opposition`: a material path, terminal-partition support >= 0.60 and layer
topology < 0.5. The rule's local-quality comparison is not traced and is not evaluated. Per frame it also prints the
number of material-path Oil candidates and their largest terminal-partition support. It runs no detector.
See docs/50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tests.diagnostics.s11_cadence_field import _rows
from tests.diagnostics.s11_layer_bottom_topology_2_field import _stop
from tests.diagnostics.s11_level_authority_readout import REJECT_OPPOSITION, _float, _value
from tests.diagnostics.s11_level_coverage_readout import TIME_TOLERANCE_SEC, parse_marks

TERMINAL_MINIMUM = 0.60  # superior partition: peer terminal support
TOPOLOGY_LIMIT = 0.50  # superior partition: peer layer topology below this
MINIMUM_SEPARATION_PX = 8.0  # superior partition: peer at least this far from the demoted candidate


def _unit(value) -> float:
    number = _float(value)
    return 0.0 if number is None else max(0.0, min(1.0, number))


def peer_fields(features: dict) -> dict:
    return dict(
        material_path=_unit(features.get('material_path', features.get('r6_material_path', 0.0))) >= 0.5,
        terminal=_unit(features.get('material_terminal_partition_support', 0.0)),
        topology=_unit(features.get('sequence_material_layer_topology', 0.0)))


def readout(bundle: Path, glass: str, marks: list[tuple[float, float]], near: float) -> dict:
    tracking = _rows(bundle, glass)
    wanted = {}
    for mark_time, mark_y in marks:
        row = min(tracking, key=lambda r: abs(float(r['timestamp_sec']) - mark_time), default=None)
        if row is None or abs(float(row['timestamp_sec']) - mark_time) > TIME_TOLERANCE_SEC:
            _stop(f'no tracking row within {TIME_TOLERANCE_SEC} s of mark time {mark_time}')
        wanted[int(row['frame_index'])] = (mark_time, mark_y)
    trace = bundle / 'debug' / 'debug_trace.jsonl'
    if not trace.is_file():
        _stop(f'no debug trace in {bundle}')
    records, run_ids = {}, set()
    with trace.open(encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            if record.get('glass_name') == glass and record.get('frame_index') in wanted:
                if 'sequence' not in record:
                    _stop(f"record {record.get('record_id')} has no sequence snapshot")
                records[record['frame_index']] = record
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
        demoted, peers, material_paths, terminal_max = [], [], 0, 0.0
        for candidate in record['sequence'].get('candidates') or ():
            if candidate.get('kind') != 'oil_air' or candidate.get('canonical_y') is None:
                continue
            y = float(candidate['canonical_y'])
            matches = detector.get((candidate.get('source'), y), [])
            joins_missing += not matches
            joins_ambiguous += len(matches) > 1
            if len(matches) != 1:
                continue
            fields = peer_fields(matches[0].get('features') or {})
            if fields['material_path']:
                material_paths += 1
                terminal_max = max(terminal_max, fields['terminal'])
            if (abs(y - mark) <= near and candidate.get('post_track_authority') == 'CANDIDATE_ONLY'
                    and (_float(candidate.get('track_opposition')) or 0.0) >= REJECT_OPPOSITION):
                demoted.append(y)
            if fields['material_path'] and fields['terminal'] >= TERMINAL_MINIMUM and fields['topology'] < TOPOLOGY_LIMIT:
                peers.append(dict(y=y, source=candidate.get('source'), tracklet=candidate.get('tracklet_id'),
                                  post_track_authority=candidate.get('post_track_authority'),
                                  terminal=fields['terminal'], topology=fields['topology'],
                                  track_opposition=_float(candidate.get('track_opposition')),
                                  selected=bool(candidate.get('selected'))))
        demoted.sort()
        for peer in peers:
            separations = [abs(peer['y'] - y) for y in demoted]
            peer['min_separation_px'] = round(min(separations), 1) if separations else None
            peer['separated'] = bool(separations) and all(s >= MINIMUM_SEPARATION_PX for s in separations)
        peers.sort(key=lambda p: (p['y'], str(p['source'])))
        frames.append(dict(time=mark_time, frame=frame, mark=mark, demoted=demoted,
                           material_path_candidates=material_paths, terminal_max=round(terminal_max, 3), peers=peers))
    return dict(bundle=str(bundle), glass=glass, run_ids=sorted(map(str, run_ids)), near_px=near,
                joins_missing=joins_missing, joins_ambiguous=joins_ambiguous, frames=frames)


PEER_FIELDS = ('y', 'source', 'tracklet', 'post_track_authority', 'terminal', 'topology', 'track_opposition',
               'selected', 'min_separation_px', 'separated')


def print_readout(result: dict) -> None:
    print(f"level peer readout {result['glass']} | bundle {result['bundle']} | run_id {','.join(result['run_ids'])} | "
          f"near <= {result['near_px']} px | joins missing {result['joins_missing']} ambiguous {result['joins_ambiguous']}")
    print('-- frames: time | mark | demoted level ys | material-path oil candidates | terminal max | partition peers --')
    for frame in result['frames']:
        print(f"{frame['time']:.3f} | {frame['mark']} | {_value(frame['demoted'])} | {frame['material_path_candidates']} | "
              f"{frame['terminal_max']} | {len(frame['peers'])}")
    print('-- partition peers: time | ' + ' | '.join(PEER_FIELDS) + ' --')
    for frame in result['frames']:
        for peer in frame['peers']:
            print(f"{frame['time']:.3f} | " + ' | '.join(_value(peer[f]) for f in PEER_FIELDS))


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
    path = args.out / 'level_peer_readout.json'
    path.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(f"json {path.name} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


if __name__ == '__main__':
    main()
