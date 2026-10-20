"""LBT-1 layer-bottom topology diagnostic. Not a promoted policy.

In the ordered-lower context, an Oil candidate above the top of the unchanged
LBW-3 unit (the frame's first supported layer bottom) is not Oil-eligible, and
LBQ-1's unit-pair support exemption is limited to ordered-lower candidates. See
docs/50-diagnostics/s11/2026-10-20-layer-bottom-topology.md.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, nullcontext
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.adapters.vision.oil_candidate_authority import (
    AuthorityDecision,
    AuthorityReason,
    OilCandidateAuthority,
)
from oil_tracker.domain.enums import BoundaryKind
from tests.diagnostics import s11_clean_anchor_fill as caf
from tests.diagnostics import s11_layer_bottom_qualified_authority as lbq
from tests.diagnostics import s11_layer_bottom_witness as lbw
from tests.diagnostics import s11_role_consumer_intervention as rci
from tests.diagnostics import s11_single_observation_influence as soi

PROTOCOL = Path('docs/50-diagnostics/s11/2026-10-20-layer-bottom-topology.md')
UNIT = lbq.FEATURE
TOP = 'diagnostic_lbw3_unit_top'
GATE = 'above_layer_bottom'
SEED_LIMIT = 3.0  # existing ORDERED_LOWER_INTERFACE Foam seed-age limit in oil_phase_identity


def unit_top(candidate):
    value = candidate.features.get(TOP)
    return None if value is None else float(value)


def in_context(candidate, context):
    """Frame-level ordered-lower context, from existing authority-context values only."""
    top = unit_top(candidate)
    return bool(
        top is not None
        and context.foam_material_row is not None
        and context.foam_seed_age_seconds is not None
        and context.foam_seed_age_seconds <= SEED_LIMIT
        and top >= float(context.foam_material_row) + float(context.lower_separation_px))


def ordered_lower(candidate):
    return resolver._unit(candidate.features.get('composition_lower_reserve', 0.0)) >= 0.5


# --- unit features ---------------------------------------------------------------

def attach(raw, units):
    """Copy saved raw rows with the unit flag and, when the unit is non-empty, its top B."""
    copied = deepcopy(raw)
    for row in copied:
        unit = set(units[row['frame_index']])
        top = min((float(row['candidates'][index]['y']) for index in unit), default=None)
        for index, candidate in enumerate(row['candidates']):
            if candidate['kind'] == 'oil_air':
                candidate['features'][UNIT] = float(index in unit)
                if top is not None:
                    candidate['features'][TOP] = top
    return copied


@contextmanager
def live_units(tolerances, *, inject):
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    frames = {}
    original = OpenCvPhaseDetector.detect

    def detect(self, *args, **kwargs):
        detection, artifacts = original(self, *args, **kwargs)
        rci.require(artifacts is not None, 'detector artifacts unavailable; a debug trace level is required')
        rows = lbq.frame_unit(detection, artifacts, tolerances[detection.glass_id])
        unit = {row['idx'] for row in rows if row['accepted']}
        top = min((float(detection.candidates[index].y) for index in unit), default=None)
        frames[(detection.glass_id, detection.frame_index)] = dict(
            time=float(detection.time_sec), unit=sorted(unit), top=top,
            candidates=[(c.kind.value, c.source, float(c.y)) for c in detection.candidates])
        if inject:
            for index, candidate in enumerate(detection.candidates):
                if candidate.kind is BoundaryKind.OIL_AIR:
                    candidate.features[UNIT] = float(index in unit)
                    if top is not None:
                        candidate.features[TOP] = top
        return detection, artifacts

    with patch.object(OpenCvPhaseDetector, 'detect', detect):
        yield frames


# --- changes ---------------------------------------------------------------------

@contextmanager
def topology(*, verify_copy=True, enabled=True):
    """Patch E1 and the context-limited support exemption; yield changed-value operations."""
    original_authority = resolver.evaluate_candidate_authority
    original_support = resolver._cross_representation_support
    original_demote = resolver._demote_non_nearest_ordered_lower_anchors
    operations = []

    def patched_authority(candidate, config, context, evidence=None):
        decision = original_authority(candidate, config, context, evidence=evidence)
        top = unit_top(candidate)
        if (enabled and decision.tier is not OilCandidateAuthority.HARD_INVALID
                and in_context(candidate, context) and float(candidate.y) < top):
            operations.append(dict(consumer='E1', y=float(candidate.y), source=candidate.source, top=top,
                                   foam_row=float(context.foam_material_row), ordinary=decision.reason.value))
            return AuthorityDecision(OilCandidateAuthority.HARD_INVALID, AuthorityReason.INELIGIBLE, (GATE,))
        return decision

    def patched_support(candidate, candidates, glass, *, evidence_index):
        if verify_copy:
            rci.require(lbq.support(candidate, candidates, glass, evidence_index=evidence_index, qualified=False)
                        == original_support(candidate, candidates, glass, evidence_index=evidence_index),
                        'LBT-1 support copy diverges from the original')
        exemptions = []
        trial = lbq.support(candidate, candidates, glass, evidence_index=evidence_index,
                            qualified=enabled and ordered_lower(candidate), exemptions=exemptions)
        if exemptions:
            ordinary = original_support(candidate, candidates, glass, evidence_index=evidence_index)
            if trial != ordinary:
                operations.append(dict(consumer='support', y=float(candidate.y), source=candidate.source,
                                       ordinary=ordinary, trial=trial))
        return trial

    with patch.object(resolver, 'evaluate_candidate_authority', patched_authority), \
            patch.object(resolver, '_cross_representation_support', patched_support):
        rci.require(resolver._demote_non_nearest_ordered_lower_anchors is original_demote,
                    'LBT-1 must not patch the nearest-anchor rule')
        yield operations
    rci.require(resolver.evaluate_candidate_authority is original_authority
                and resolver._cross_representation_support is original_support, 'LBT-1 patch leak')


# --- sample4 population -----------------------------------------------------------

def _pipeline(sample, root, scratch, *, trial):
    from tests.diagnostics.s11_report_observability_replay import _session, QUALIFICATION_WINDOWS
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.session import DebugTraceLevel

    recipe, session = _session(sample, root / 'sample' / f'{sample}.mp4', Path(scratch),
                               *QUALIFICATION_WINDOWS[sample], run_label='LBT-1', run_note='off')
    session.debug_trace_level = DebugTraceLevel.BASIC
    tolerances = {g.id: lbw.same_boundary_tolerance(g) for g in recipe.glasses if g.enabled}
    with live_units(tolerances, inject=trial) as frames, \
            (topology() if trial else nullcontext([])) as operations:
        result = AnalysisPipeline(OpenCvVideoReader, OpenCvPhaseDetector(), RecipeValidationService(),
                                  JsonlDebugTraceWriterFactory(Path(scratch))).run(recipe, session)
    rci.require(not result.errors, f'{sample} analysis errors: {result.errors}')
    return result, frames, list(operations)


def prepare_sample4(root, work):
    from tests.diagnostics.s11_report_observability_replay import _tracking_fingerprint
    with TemporaryDirectory(dir=work) as scratch:
        result, frames, _ = _pipeline('sample4', root, scratch, trial=False)
    fingerprint = _tracking_fingerprint(result)
    rci.require(fingerprint == lbw.P5_FINGERPRINT, f'sample4 fingerprint {fingerprint} differs from P5')
    raw = json.loads((root / rci.SAVED / 'raw.json').read_text(encoding='utf-8'))
    units = lbq.bind_units(raw, frames)
    return raw, units, frames, dict(fingerprint=fingerprint)


def make_trial(units):
    def execute(raw, recipe, case):
        with topology() as operations:
            result = soi.execute(attach(raw, units), recipe, case)
        return (*result, operations)
    return execute


def _members(detection):
    return [(float(c.y), c.features.get('sequence_tracklet_id'), c.features.get('sequence_authority_reason'))
            for c in detection.candidates
            if c.kind is BoundaryKind.OIL_AIR and c.features.get('sequence_tracklet_id')]


def layer_report(raw, recipe, units):
    """Per frame: E1 removals, published row, fill state; plus the SFR-1 mixing check."""
    attached = attach(raw, units)
    with topology() as operations:
        trial_record, trial, _, _ = soi.execute(attached, recipe, None)
    ordinary_record, ordinary, _, _ = soi.execute(raw, recipe, None)
    removed = {}
    for op in operations:
        if op['consumer'] == 'E1':
            removed.setdefault(op['top'], set()).add(op['y'])
    frames, above, inside = [], {}, {}
    for offset, row in enumerate(raw):
        unit = set(units[row['frame_index']])
        detection = trial.detections[offset]
        foam = [float(c.y) for c in detection.candidates if c.kind is BoundaryKind.FOAM_FRONT
                and resolver._unit(c.features.get('sequence_foam_eligible', 0.0)) >= 0.5]
        unit_ys = {float(row['candidates'][i]['y']) for i in unit}
        top = min(unit_ys, default=None)
        for y, tracklet, _ in _members(detection):
            if foam and y < min(foam):
                above.setdefault(tracklet, []).append((row['time_sec'], y))
            if y in unit_ys:
                inside.setdefault(tracklet, []).append((row['time_sec'], y))
        metrics = detection.debug_metrics
        selected = trial_record['rows'][offset]['selected']
        published = None
        if selected is not None:
            features = detection.candidates[selected['candidate_offset']].features
            published = dict(y=selected['y'], authority=features.get('sequence_authority_reason'),
                             lifecycle=features.get('sequence_tracklet_lifecycle'), tracklet=selected['tracklet_id'],
                             in_unit=selected['candidate_offset'] in unit)
        frames.append(dict(
            frame=row['frame_index'], time=row['time_sec'], foam=foam, unit_top=top,
            ordinary_oil=ordinary_record['rows'][offset]['oil_y'], trial_oil=trial_record['rows'][offset]['oil_y'],
            phase=metrics['sequence_material_phase'], reason=metrics['sequence_material_phase_reason'],
            fill_profile=metrics.get('sequence_material_phase_fill_confirmation_profile'),
            owner_chain=metrics.get('sequence_material_phase_owner_chain'), published=published,
            owner_rows=[m for m in _members(detection)
                        if m[1] and m[1] in str(metrics.get('sequence_material_phase_owner_chain') or '')]))
    mixing = {t: dict(above=above[t], unit=inside[t]) for t in sorted(set(above) & set(inside))}
    return dict(frames=frames, mixing=mixing, e1_operations=sum(op['consumer'] == 'E1' for op in operations),
                support_operations=sum(op['consumer'] == 'support' for op in operations))


def descriptive(sample, root, work):
    from tests.diagnostics.s11_report_observability_replay import _tracking_fingerprint
    outputs = {}
    for arm, trial in (('ordinary', False), ('trial', True)):
        with TemporaryDirectory(dir=work) as scratch:
            result, frames, operations = _pipeline(sample, root, scratch, trial=trial)
        rows = [(s.timestamp_sec, s.raw_oil_air_level_y, s.raw_foam_front_y)
                for g in result.glass_results for s in g.samples]
        outputs[arm] = dict(fingerprint=_tracking_fingerprint(result), rows=rows, operations=operations,
                            unit_frames=sum(bool(item['unit']) for item in frames.values()), frames=len(frames))
    changed = [(o, t) for o, t in zip(outputs['ordinary']['rows'], outputs['trial']['rows'], strict=True) if o != t]
    ops = outputs['trial']['operations']
    return dict(sample=sample, unit_frames=outputs['trial']['unit_frames'], frames=outputs['trial']['frames'],
                e1_operations=sum(op['consumer'] == 'E1' for op in ops),
                support_operations=sum(op['consumer'] == 'support' for op in ops),
                fingerprint_equal=outputs['ordinary']['fingerprint'] == outputs['trial']['fingerprint'],
                changed_rows=changed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=rci.ROOT)
    parser.add_argument('--work', type=Path, required=True, help='managed run work directory')
    args = parser.parse_args()
    root, work = args.root.resolve(), args.work.resolve()
    raw, units, frames, prep = prepare_sample4(root, work)
    recipe = rci.JsonRecipeRepository().load(root / rci.BUNDLE / 'recipe_snapshot.oilrecipe')
    inert = soi.execute(attach(raw, units), recipe, None)[0]
    rci.require(inert == soi.execute(raw, recipe, None)[0], 'inert features change the ordinary result')
    print('prepared', prep, 'unit frames', sum(bool(u) for u in units.values()), flush=True)
    rci.write_json(work / 'units.json', dict(prep=prep, units=units,
                                             frames={str(f): item for (_, f), item in frames.items()}))
    population = work / 'population'
    population.mkdir()
    caf.run(root, population, trial=make_trial(units), protocol=PROTOCOL,
            schema='s11-layer-bottom-topology-v1',
            scope='LBT-1 diagnostic wrapper; not production adoption',
            extra_sources=(Path(__file__), Path(lbq.__file__), Path(lbw.__file__)))
    rci.write_json(work / 'layers.json', layer_report(raw, recipe, units))
    rci.write_json(work / 'descriptive.json', [descriptive(s, root, work) for s in ('base_sample_1', 'sample2')])
    print('LBT-1 COMPLETE', flush=True)


if __name__ == '__main__':
    main()
