"""Read-only texture-gate extraction from a saved debug trace (Windows Accum layered Foam).

Reads indexed debug records and their final ``sequence`` snapshot only. No
detector, resolver, pipeline or comparison run occurs and nothing is written.
Stored gate values are reported as saved. Peer exclusion reasons follow the
conditions of ``_cross_representation_support``; the resolver function itself
recomputes each stored support value as a self-check, and the counterfactual
``sup*`` calls it again with only texture-excluded peers' conflict cleared.
Prints short text tables for manual transcription. Not a promoted policy.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
import math
from pathlib import Path

from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader
from oil_tracker.adapters.storage.debug_trace_repository import DebugTraceRepository
from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidenceIndex
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind

TIMES = (673.0, 675.0, 677.0, 678.5, 679.0, 684.0)  # layered Foam interval + one post-Foam frame
SUMMARY = (671.0, 681.0)
MATCH_SEC = 0.6
CROSS_MIN = 0.12  # ORDERED_LOWER_INTERFACE representation-support floor
TEX_LIMIT = 0.60
ROWS_PER_FRAME = 5
SHORT = {'continuation_only': 'CONT', 'direct_interface': 'DIRECT', 'ordered_lower_interface': 'OLOWER',
         'opposed_material': 'OPPOSED', 'ordered_lower_cross_representation': 'olX',
         'ordered_lower_recent_direct_foam': 'olFoam', 'material_texture_conflict<0.60': 'tex',
         'calibrated_independent_representation': 'calX'}


def _f(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _candidate(raw):
    return BoundaryCandidate(
        str(raw['source']), BoundaryKind(raw['kind']), float(raw['canonical_y']),
        features=dict(raw.get('features') or {}), penalties=dict(raw.get('penalties') or {}),
        feature_score=_f(raw.get('feature_score')) or 0.0, penalty=_f(raw.get('total_penalty')) or 0.0,
        final_score=_f(raw.get('final_score')) or 0.0, selected=bool(raw.get('selected')),
        rejected=bool(raw.get('rejected')), reject_reason=str(raw.get('reject_reason') or ''))


def peer_reasons(candidate, oil, glass, index):
    """Per-peer exclusion classes within the resolver's Y tolerance."""
    family = resolver._candidate_representation_family(candidate, index.evidence(candidate))
    tolerance = max(8.0, float(glass.detector_settings.temporal_max_jump_px) * 0.375)
    counts, texture_only = Counter(), []
    for peer in oil:
        if peer is candidate or abs(float(peer.y) - float(candidate.y)) > tolerance:
            continue
        evidence = index.evidence(peer)
        peer_family = resolver._candidate_representation_family(peer, evidence)
        if peer_family == family:
            counts['same'] += 1
            continue
        if not resolver._candidate_eligible(peer, evidence):
            counts['inel'] += 1
            continue
        reasons = [name for name, hit in (
            ('tex', evidence.material_texture_conflict >= TEX_LIMIT),
            ('art', evidence.artifact_signature >= 0.44),
            ('opt', evidence.optics_opposition >= 0.46),
            ('raster', 'calibrated_raster' in {family, peer_family} and 'material' not in {family, peer_family}),
        ) if hit]
        if reasons == ['tex']:
            texture_only.append(peer)
        counts['+'.join(reasons) or 'counted'] += 1
    return counts, texture_only


def support_without_texture(candidate, oil, glass, index, texture_only):
    """Resolver support with only texture-excluded peers' conflict cleared (diagnostic)."""
    trial = OilCandidateEvidenceIndex()
    for item in oil:
        evidence = index.evidence(item)
        if any(item is peer for peer in texture_only):
            evidence = replace(evidence, material_texture_conflict=0.0)
        trial.register(item, evidence)
    return resolver._cross_representation_support(candidate, oil, glass, evidence_index=trial)


def pattern(seq, counts, counterfactual):
    if _f(seq.get('ordered_lower')) != 1.0 or seq.get('phase_identity') != 'continuation_only':
        return '-'
    gates = {gate for gate in str(seq.get('phase_identity_failed_gates') or '').split(';') if gate}
    if gates != {'ordered_lower_cross_representation'}:
        return 'GATE_OTHER'
    if counts.get('tex'):
        return 'TEX0' if counterfactual >= CROSS_MIN else 'TEX_WEAK'
    if not sum(value for key, value in counts.items() if key not in {'same'}):
        return 'NOPEER'
    return 'OTHER_EXCL'


def analyze(record, glass, requested=()):
    """Return frame summary and per-candidate rows for one saved record (pure).

    Rows cover the top-K refs plus any requested ``candidate_input_index`` values,
    including candidates without stored gate fields (``NOT_TOPK``).
    """
    sequence = record.get('sequence')
    frame = dict(frame=record['frame_index'], time=float(record['timestamp_sec']),
                 reasons=list(record.get('capture_reasons') or []), sequence=sequence is not None, rows=[],
                 check_ok=0, check_total=0, ambiguous=0, selected=None, anchors=0, foam=[])
    if sequence is None:
        return frame
    raw = [item for item in record.get('candidates') or []
           if item.get('kind') == 'oil_air' and _f(item.get('canonical_y')) is not None]
    oil = tuple(_candidate(item) for item in raw)
    input_index = {id(item): source.get('candidate_input_index') for item, source in zip(oil, raw)}
    index = OilCandidateEvidenceIndex()
    for item in oil:
        index.register(item)
    by_key = {}
    for item in oil:
        by_key.setdefault((item.source, float(item.y)), []).append(item)
    frame['raw_oil'] = len(oil)
    frame['foam'] = sorted(round(float(item['canonical_y'])) for item in sequence.get('candidates') or []
                           if item.get('kind') == 'foam_front' and (_f(item.get('sequence_foam_eligible')) or 0) >= 0.5
                           and _f(item.get('canonical_y')) is not None)
    frame['version'] = (sequence.get('state') or {}).get('sequence_resolver_version')
    sequence_oil = [item for item in sequence.get('candidates') or [] if item.get('kind') == 'oil_air']
    frame['top_k'] = sum(item.get('phase_identity') is not None for item in sequence_oil)
    for seq in sequence_oil:
        matches = by_key.get((str(seq['source']), float(seq['canonical_y'])), [])
        top = seq.get('phase_identity') is not None
        if not top and not any(input_index[id(item)] in requested for item in matches):
            continue
        row = dict(y=float(seq['canonical_y']), source=str(seq['source']), authority=seq.get('authority'),
                   reason=seq.get('authority_reason'), identity=seq.get('phase_identity'),
                   identity_gates=seq.get('phase_identity_failed_gates') or '',
                   ordered_lower=_f(seq.get('ordered_lower')), support=_f(seq.get('cross_representation_support')),
                   admitted=_f(seq.get('tracklet_admitted')), stage=seq.get('reject_stage'),
                   selected=bool(seq.get('selected')), top_k=top)
        if seq.get('selected'):
            frame['selected'] = f"Y{row['y']:.0f} {row['reason']}"
        if row['authority'] == 'ANCHOR_ELIGIBLE':
            frame['anchors'] += 1
        if len(matches) != 1:
            frame['ambiguous'] += 1
            row.update(pattern='AMBIG')
            frame['rows'].append(row)
            continue
        candidate = matches[0]
        evidence = index.evidence(candidate)
        recomputed = resolver._cross_representation_support(candidate, oil, glass, evidence_index=index)
        if top:
            frame['check_total'] += 1
            frame['check_ok'] += int(row['support'] is not None and abs(recomputed - row['support']) <= 1e-6)
        else:
            row['support'] = recomputed  # what the resolver would compute; no stored value exists
        counts, texture_only = peer_reasons(candidate, oil, glass, index)
        counterfactual = support_without_texture(candidate, oil, glass, index, texture_only)
        features = candidate.features
        row.update(idx=input_index[id(candidate)], conflict=evidence.material_texture_conflict,
                   terminal=_f(features.get('material_terminal_partition_support')),
                   row_support=_f(features.get('raw_material_row_support')),
                   counts=dict(counts), counterfactual=counterfactual,
                   final_score=candidate.final_score,
                   pattern=pattern(seq, counts, counterfactual) if top else 'NOT_TOPK')
        frame['rows'].append(row)
    return frame


def _pick(rows):
    keep = [row for row in rows if row['top_k'] and (row['selected'] or row['authority'] == 'ANCHOR_ELIGIBLE'
                                                   or row.get('ordered_lower') == 1.0)]
    keep.sort(key=lambda row: (not row['selected'], row['authority'] != 'ANCHOR_ELIGIBLE', row['y']))
    return sorted(keep[:ROWS_PER_FRAME], key=lambda row: row['y'])


def _num(value, digits=2):
    return '-' if value is None else f'{value:.{digits}f}'


def _short(value):
    return ','.join(SHORT.get(part, part) for part in str(value or '').split(';') if part) or '-'


def _peers(counts):
    if not counts:
        return '-'
    return ' '.join(f'{key}{value}' for key, value in sorted(counts.items()))


def _load(bundle_path, glass_key):
    bundle = ResultBundleReader().read(bundle_path)
    repository = DebugTraceRepository(bundle)
    glass = next((item for item in bundle.recipe.glasses
                  if glass_key.lower() in {str(item.id).lower(), str(item.name).lower()}), None)
    if glass is None:
        names = ', '.join(f'{item.name}({item.id})' for item in bundle.recipe.glasses)
        raise SystemExit(f'glass not found: {glass_key}; available: {names}')
    return bundle, repository, glass


def _records(bundle, summaries):
    path = Path(bundle.root) / bundle.debug_trace_path
    with path.open('rb') as handle:
        for summary in summaries:
            handle.seek(summary.byte_offset)
            yield json.loads(handle.read(summary.byte_length).decode('utf-8'))


def run(bundle_path, glass_key, times, requested=None):
    bundle, repository, glass = _load(bundle_path, glass_key)
    summaries = repository.summaries(str(glass.id))
    if requested:
        report_requested(bundle, summaries, glass, requested)
    else:
        report(bundle, summaries, glass, times)


def parse_rows(text):
    """'16184:10,22;16232:10' -> {16184: {10, 22}, 16232: {10}}."""
    rows = {}
    for part in filter(None, (item.strip() for item in text.split(';'))):
        frame, indices = part.split(':')
        rows[int(frame)] = {int(value) for value in indices.split(',') if value.strip()}
    return rows


def report_requested(bundle, summaries, glass, requested):
    """Table D: exactly the requested candidates, whether or not they were top-K."""
    by_frame = {item.frame_index: item for item in summaries}
    print(f'run_id={bundle.run_id} trace={bundle.debug_trace_level} glass={glass.name}')
    print('[D] frame | actual s | Y | idx | source | topK | authority/reason | identity [failed gates] | '
          'ol | sup | sup* | conflict | terminal | row | peers | admitted/stage | final | pattern')
    for frame_index in sorted(requested):
        summary = by_frame.get(frame_index)
        if summary is None:
            print(f'f{frame_index} | NOT_CAPTURED')
            continue
        record = next(_records(bundle, [summary]))
        frame = analyze(record, glass, requested[frame_index])
        if not frame['sequence']:
            print(f'f{frame_index} | NO_SEQUENCE')
            continue
        rows = {row.get('idx'): row for row in frame['rows'] if row.get('idx') in requested[frame_index]}
        for idx in sorted(requested[frame_index], key=lambda value: (rows[value]['y'] if value in rows else 1e9, value)):
            row = rows.get(idx)
            if row is None:
                print(f"f{frame_index} | {frame['time']:.3f} | - | {idx} | NOT_FOUND_OR_AMBIG")
                continue
            print(f"f{frame_index} | {frame['time']:.3f} | {row['y']:.0f}{'*' if row['selected'] else ''} | {idx} | "
                  f"{row['source'][:20]} | {'Y' if row['top_k'] else 'N'} | "
                  f"{(row['authority'] or '-')[:4]}/{row['reason'] or '-'} | "
                  f"{_short(row['identity'])} [{_short(row['identity_gates'])}] | {_num(row['ordered_lower'], 0)} | "
                  f"{_num(row['support'])} | {_num(row.get('counterfactual'))} | {_num(row.get('conflict'))} | "
                  f"{_num(row.get('terminal'))} | {_num(row.get('row_support'))} | {_peers(row.get('counts'))} | "
                  f"{_num(row['admitted'], 0)}/{row['stage']} | {_num(row.get('final_score'))} | {row['pattern']}")


def report(bundle, summaries, glass, times):
    tolerance = max(8.0, float(glass.detector_settings.temporal_max_jump_px) * 0.375)
    print(f'run_id={bundle.run_id} trace={bundle.debug_trace_level} glass={glass.name} '
          f'records={len(summaries)} tol={tolerance:.1f}px')
    targets = []
    for target in times:
        nearest = min(summaries, key=lambda item: abs(item.timestamp_sec - target), default=None)
        targets.append((target, nearest if nearest and abs(nearest.timestamp_sec - target) <= MATCH_SEC else None))
    chosen = [item for _, item in targets if item is not None]
    frames = {record['record_id']: analyze(record, glass) for record in _records(bundle, chosen)}
    version = next((frame.get('version') for frame in frames.values() if frame.get('version')), None)
    print(f'resolver={version}')
    print('\n[A] frame | target s | actual s | seq | foam eligible Y | selected Oil | anchors | topk/raw | recompute')
    for target, summary in targets:
        if summary is None:
            print(f'- | {target:.1f} | NOT_CAPTURED | | | | | |')
            continue
        frame = frames[summary.record_id]
        if not frame['sequence']:
            print(f"f{frame['frame']} | {target:.1f} | {frame['time']:.3f} | NO_SEQUENCE | | | | |")
            continue
        foam = ','.join(str(value) for value in frame['foam'][:3]) or '-'
        print(f"f{frame['frame']} | {target:.1f} | {frame['time']:.3f} | yes | {foam} | {frame['selected'] or '-'} | "
              f"{frame['anchors']} | {frame['top_k']}/{frame['raw_oil']} | {frame['check_ok']}/{frame['check_total']}")
    print('\ncodes: CONT/DIRECT/OLOWER identity; olX=ordered_lower_cross_representation, '
          'olFoam=ordered_lower_recent_direct_foam; sup*=support with texture-only peers kept; * selected')
    print('[B] actual s | Y | idx | source | authority/reason | identity [failed gates] | sup | sup* | conflict | '
          'terminal | row | peers | admitted/stage | pattern')
    for _, summary in targets:
        frame = frames.get(summary.record_id) if summary else None
        if not frame or not frame['sequence']:
            continue
        for row in _pick(frame['rows']):
            mark = '*' if row['selected'] else ''
            print(f"{frame['time']:.1f} | {row['y']:.0f}{mark} | {row.get('idx', '-')} | {row['source'][:20]} | "
                  f"{(row['authority'] or '-')[:4]}/{row['reason']} | {_short(row['identity'])} [{_short(row['identity_gates'])}] | "
                  f"{_num(row['support'])} | {_num(row.get('counterfactual'))} | {_num(row.get('conflict'))} | "
                  f"{_num(row.get('terminal'))} | {_num(row.get('row_support'))} | {_peers(row.get('counts'))} | "
                  f"{_num(row['admitted'], 0)}/{row['stage']} | {row['pattern']}")
    window = [item for item in summaries if SUMMARY[0] <= item.timestamp_sec <= SUMMARY[1]]
    totals = Counter()
    for record in _records(bundle, window):
        frame = analyze(record, glass)
        totals['frames'] += 1
        totals['no_sequence'] += int(not frame['sequence'])
        totals['selected'] += int(frame['selected'] is not None)
        totals['anchor_frames'] += int(frame['anchors'] > 0)
        totals['recompute_mismatch'] += frame['check_total'] - frame['check_ok']
        for name in ('TEX0', 'TEX_WEAK', 'NOPEER', 'OTHER_EXCL', 'GATE_OTHER', 'AMBIG'):
            totals[name] += int(any(row.get('pattern') == name for row in frame['rows']))
    print(f'\n[C] {SUMMARY[0]:.0f}-{SUMMARY[1]:.0f} s captured frames: ' + ' '.join(
        f'{key}={totals[key]}' for key in ('frames', 'no_sequence', 'selected', 'anchor_frames', 'TEX0', 'TEX_WEAK',
                                           'NOPEER', 'OTHER_EXCL', 'GATE_OTHER', 'AMBIG', 'recompute_mismatch')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--glass', default='Accum')
    parser.add_argument('--times', default=','.join(str(value) for value in TIMES))
    parser.add_argument('--rows', help="exact frame:idx list, e.g. '16184:10,22;16232:10' (prints table D only)")
    args = parser.parse_args()
    run(args.bundle.expanduser().resolve(), args.glass, tuple(float(value) for value in args.times.split(',')),
        parse_rows(args.rows) if args.rows else None)


if __name__ == '__main__':
    main()
