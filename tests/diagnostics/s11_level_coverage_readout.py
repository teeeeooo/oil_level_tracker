"""Level coverage readout: the Oil candidates near a reviewed level mark, per marked row. Read-only.

Reads a saved bundle's FULL debug trace (the `sequence` snapshot of each record) and its tracking rows. For each
`time:y` mark it prints the row's output and phase reason, the number of Oil candidates and the nearest one's
distance, then the Oil candidates within `--near` px of the mark, one line per tracklet and row hypothesis, with
the tracklet fields, sources, post-track tiers and reject stages. It runs no detector. The trace loading follows `s11_fill_owner_trace_readout`, which is left
unchanged because its hash is part of the step-12 record.
See docs/50-diagnostics/s11/2026-10-27-fast-rise-owner-desk-review.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tests.diagnostics.s11_cadence_field import _rows
from tests.diagnostics.s11_layer_bottom_topology_2_field import _stop, _y

TIME_TOLERANCE_SEC = 0.2
# Printed per (tracklet, row hypothesis) group as the set of member values; the tracklet fields have one value in a
# tracked group, and the untracked group ('-') collects candidates that never entered a tracklet.
FIELDS = (
    'tracklet_lifecycle', 'tracklet_admitted', 'tracklet_confirmation_profile', 'tracklet_net_progress_px',
    'tracklet_failure_reason', 'source', 'post_track_authority', 'authority_reason', 'reject_stage',
)


def parse_marks(text: str) -> list[tuple[float, float]]:
    marks = []
    for item in text.split(','):
        if item.strip():
            time, y = item.split(':')
            marks.append((float(time), float(y)))
    return marks


def readout(bundle: Path, glass: str, marks: list[tuple[float, float]], near: float) -> dict:
    tracking = _rows(bundle, glass)
    rows = {}
    for mark_time, _ in marks:  # the nearest row; the sampled times of a 29.97 fps video drift from the 0.5 s grid
        row = min(tracking, key=lambda r: abs(float(r['timestamp_sec']) - mark_time), default=None)
        if row is None or abs(float(row['timestamp_sec']) - mark_time) > TIME_TOLERANCE_SEC:
            _stop(f'no tracking row within {TIME_TOLERANCE_SEC} s of mark time {mark_time}')
        rows[int(row['frame_index'])] = (mark_time, row)
    trace = bundle / 'debug' / 'debug_trace.jsonl'
    if not trace.is_file():
        _stop(f'no debug trace in {bundle}')
    sequences, run_ids = {}, set()
    with trace.open(encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            if record.get('glass_name') == glass and record.get('frame_index') in rows:
                if 'sequence' not in record:
                    _stop(f"record {record.get('record_id')} has no sequence snapshot")
                sequences[record['frame_index']] = record['sequence']
                run_ids.add(record.get('run_id'))
    mark_y = dict(marks)
    frames = []
    for frame, (mark_time, row) in sorted(rows.items()):
        sequence = sequences.get(frame)
        if sequence is None:
            _stop(f'no trace record for frame {frame}')
        state = sequence.get('state') or {}
        mark = mark_y[mark_time]
        oil = [c for c in sequence.get('candidates') or () if c.get('kind') == 'oil_air' and c.get('canonical_y') is not None]
        groups: dict[tuple, dict] = {}
        for candidate in oil:
            distance = candidate['canonical_y'] - mark
            if abs(distance) > near:
                continue
            key = (candidate.get('tracklet_id') or '-', candidate.get('row_hypothesis_id') or '-')
            group = groups.setdefault(key, dict(
                tracklet=key[0], row=key[1], y=[], d=None, selected=False, **{f: set() for f in FIELDS}))
            group['y'].append(candidate['canonical_y'])
            if group['d'] is None or abs(distance) < abs(group['d']):
                group['d'] = round(distance, 1)
            group['selected'] = group['selected'] or bool(candidate.get('selected'))
            for f in FIELDS:
                value = candidate.get(f)
                group[f].add(_short(value) if f == 'source' else _value(value))
        near_rows = sorted(groups.values(), key=lambda g: (abs(g['d']), g['tracklet']))
        for group in near_rows:
            group['y'] = sorted(group['y'])
            for f in FIELDS:
                group[f] = sorted(group[f])
        nearest = min((abs(c['canonical_y'] - mark) for c in oil), default=None)
        frames.append(dict(
            time=mark_time, row_time=float(row['timestamp_sec']), frame=frame, mark=mark, fill=row['fill_state'], oil=_y(row['raw_oil_air_level_y']),
            reason=state.get('sequence_material_phase_reason'), oil_candidates=len(oil),
            nearest_px=None if nearest is None else round(nearest, 1),
            y_range=[min((c['canonical_y'] for c in oil), default=None), max((c['canonical_y'] for c in oil), default=None)],
            near=near_rows))
    return dict(bundle=str(bundle), glass=glass, run_ids=sorted(map(str, run_ids)), near_px=near, frames=frames)


def _short(source) -> str:
    """`oil_hypothesis:<hash>` → `oil_hypothesis`; the hash names one detector hypothesis, not a source kind."""
    return str(source).split(':')[0]


def _value(value) -> str:
    return '-' if value is None else str(value)


def print_readout(result: dict) -> None:
    print(f"level coverage readout {result['glass']} | bundle {result['bundle']} | run_id {','.join(result['run_ids'])} | "
          f"near <= {result['near_px']} px")
    print('-- frames: time | frame | mark | fill | oil | reason | oil candidates | nearest px | candidate y min / max --')
    for row in result['frames']:
        print(f"{row['time']:.3f} | {row['frame']} | {row['mark']} | {row['fill']} | {_value(row['oil'])} | "
              f"{_value(row['reason'])} | {row['oil_candidates']} | {_value(row['nearest_px'])} | "
              f"{_value(row['y_range'][0])} / {_value(row['y_range'][1])}")
    print('-- near groups (one per tracklet and row hypothesis): time | tracklet | row | ys | d | selected | '
          + ' | '.join(FIELDS) + ' --')
    for row in result['frames']:
        for group in row['near']:
            print(f"{row['time']:.3f} | {group['tracklet']} | {group['row']} | {','.join(map(str, group['y']))} | "
                  f"{group['d']} | {group['selected']} | " + ' | '.join(','.join(group[f]) for f in FIELDS))

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--glass-name', default='BASE')
    parser.add_argument('--marks', required=True, help='comma-separated time:y pairs (source Y)')
    parser.add_argument('--near', type=float, default=48.0)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    result = readout(args.bundle, args.glass_name, parse_marks(args.marks), args.near)
    print_readout(result)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / 'level_coverage_readout.json'
    path.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(f"json {path.name} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


if __name__ == '__main__':
    main()
