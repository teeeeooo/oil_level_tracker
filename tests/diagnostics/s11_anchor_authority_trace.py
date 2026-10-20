"""Read-only trace of Oil phase-identity and anchor-authority decisions on saved sample4.

Records, for reviewed frames, the exact inputs and gate outcomes behind
`evaluate_phase_identity` / `evaluate_candidate_authority` and the final
post-demotion authority. Detector behavior is unchanged (the wrappers return the
original decisions). Not a promoted policy.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import gzip
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidence
from tests.diagnostics import s11_role_consumer_intervention as rci
from tests.diagnostics import s11_single_observation_influence as soi

SOI_COMPARISON = Path('sample/output/s11-single-observation-20261016-001/evidence/comparison.json')
EXTRA_FRAMES = (1530, 1545)  # 51.0 / 51.5 s, the user-confirmed false Y862 run (CAF-1)
EVIDENCE_FIELDS = (
    'material_support', 'boundary', 'artifact_likelihood', 'artifact_signature', 'ambiguity',
    'optics_opposition', 'narrow_strength', 'horizontal_coverage', 'material_texture_conflict',
    'material_path', 'calibrated_high_recall', 'registered_motion', 'registered_motion_coverage')


def _evidence(evidence: OilCandidateEvidence):
    out = {name: getattr(evidence, name) for name in EVIDENCE_FIELDS}
    out['phase_available'] = evidence.availability.phase
    out['material_texture_available'] = evidence.availability.material_texture
    return out


@contextmanager
def trace(frames):
    records = {}
    original_identity = resolver.evaluate_phase_identity
    original_authority = resolver.evaluate_candidate_authority

    def identity(candidate, config, context, evidence=None):
        decision = original_identity(candidate, config, context, evidence=evidence)
        caller = sys._getframe(1).f_locals
        frame_index = caller['detection'].frame_index
        if frame_index in frames:
            records[(frame_index, caller['candidate_offset'])] = dict(
                frame_index=frame_index, time_sec=caller['detection'].time_sec,
                candidate_offset=caller['candidate_offset'], source=candidate.source, y=candidate.y,
                foam_material_row=context.foam_material_row, lower_separation_px=context.lower_separation_px,
                foam_material_identity=context.foam_material_identity,
                foam_seed_age_seconds=context.foam_seed_age_seconds,
                representation_support=context.representation_support,
                phase_transition_scan=float(candidate.features.get('phase_transition_scan', 0.0)),
                broad_strength=float(candidate.features.get('broad_strength', 0.0)),
                evidence=_evidence(evidence),
                identity=decision.identity.value, ordered_lower=decision.ordered_lower,
                identity_failed_gates=list(decision.failed_gates))
        return decision

    def authority(candidate, config, context, evidence=None):
        decision = original_authority(candidate, config, context, evidence=evidence)
        caller = sys._getframe(1).f_locals
        key = (caller['detection'].frame_index, caller['candidate_offset'])
        if key in records:
            records[key].update(authority=decision.tier.name, authority_reason=decision.reason.value,
                                authority_failed_gates=list(decision.failed_gates))
        return decision

    with patch.object(resolver, 'evaluate_phase_identity', identity), \
            patch.object(resolver, 'evaluate_candidate_authority', authority):
        yield records
    rci.require(resolver.evaluate_phase_identity is original_identity
                and resolver.evaluate_candidate_authority is original_authority, 'trace patch leak')


def run(root, output):
    rci.require(output.is_dir() and not any(output.iterdir()), 'empty managed work required')
    controls = json.loads((root / SOI_COMPARISON).read_text(encoding='utf-8'))['preflight']['controls']
    frames = sorted({c['frame'] for c in controls} | set(EXTRA_FRAMES))
    raw = json.loads((root / rci.SAVED / 'raw.json').read_text(encoding='utf-8'))
    recipe = rci.JsonRecipeRepository().load(root / rci.BUNDLE / 'recipe_snapshot.oilrecipe')
    with trace(set(frames)) as records:
        record, complete, _, _ = soi.execute(raw, recipe, None)
    with gzip.open(root / SOI_COMPARISON.parent / 'population.jsonl.gz', 'rt', encoding='utf-8') as stream:
        saved_baseline = json.loads(stream.readline())
    rci.require(saved_baseline['id'] == 'baseline' and record['rows'] == saved_baseline['rows'],
                'traced baseline does not reproduce saved SOI baseline rows')
    final = {}
    for detection in complete.detections:
        if detection.frame_index not in frames:
            continue
        witness = detection.debug_metrics['sequence_decision_witness']
        for row in witness['rows']:
            for member in row['members']:
                final[(detection.frame_index, member['candidate_offset'])] = dict(
                    final_authority=member['authority'], final_reason=member['authority_reason'],
                    tracklet_id=row['tracklet_id'], tracklet_admitted=member['tracklet_admitted'],
                    selected=member['selected'])
    labels = {(c['frame'], c['index']): c for c in controls}
    rows = []
    for key in sorted(records):
        item = dict(records[key])
        item.update(final.get(key, dict(final_authority=None)))
        control = labels.get(key)
        item['review'] = None if control is None else dict(id=control['id'], label=control['review_label'],
                                                          physical=control['label_basis']['physical'])
        rows.append(item)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True,
                                   encoding='utf-8', stdin=subprocess.DEVNULL).strip()
    rci.write_json(output / 'authority-trace.json', dict(
        schema='s11-anchor-authority-trace-v1', head=head, frames=frames, controls=controls, rows=rows,
        baseline_rows_equal_saved=True, production_unchanged=True, physical_accuracy='NOT_EVALUATED'))
    print('COMPLETE', len(frames), len(rows))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=rci.ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.output.resolve())


if __name__ == '__main__':
    main()
