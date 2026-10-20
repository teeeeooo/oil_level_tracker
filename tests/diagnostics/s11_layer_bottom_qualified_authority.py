"""LBQ-1 layer-bottom-qualified ordered-lower authority diagnostic. Not a promoted policy.

The unchanged LBW-3 unit (the frame's first supported layer bottom) qualifies two
existing OIL-AUTHORITY steps: texture-only peer exclusion in cross-representation
support, and the nearest ordered-lower anchor. See
docs/50-diagnostics/s11/2026-10-20-layer-bottom-qualified-authority.md.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, nullcontext
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.domain.enums import BoundaryKind
from tests.diagnostics import s11_clean_anchor_fill as caf
from tests.diagnostics import s11_layer_bottom_witness as lbw
from tests.diagnostics import s11_role_consumer_intervention as rci
from tests.diagnostics import s11_single_observation_influence as soi

PROTOCOL = Path('docs/50-diagnostics/s11/2026-10-20-layer-bottom-qualified-authority.md')
FEATURE = 'diagnostic_lbw3_unit'
ABOVE_GATE = 'above_supported_layer_bottom'
NEAREST_GATE = 'nearest_ordered_lower_interface'


def in_unit(candidate):
    return resolver._unit(candidate.features.get(FEATURE, 0.0)) >= 0.5


# --- witness unit -----------------------------------------------------------------

def frame_unit(detection, artifacts, tolerance):
    """LBW-3 rows for one detection, computed on the detector's own artifact rasters."""
    images = artifacts.images
    candidates = [dict(kind=c.kind.value, canonical_y=c.y, source=c.source, candidate_input_index=i,
                       local_y=c.features.get('local_y'), features=dict(c.features))
                  for i, c in enumerate(detection.candidates)]
    origin_y, _ = lbw.origin_from_record(dict(state=dict(artifacts.state), candidates=candidates))
    rasters = (images['foam_combined_evidence'].astype(np.float64) / 255.0,
               images['effective_mask'], images['glare_mask'])
    return lbw.accept(lbw.evaluate(rasters, candidates, origin_y, tolerance), 'lbw3', tolerance)


@contextmanager
def live_units(tolerances, *, inject):
    """Compute the unit for every detected frame; optionally attach it as the inert feature."""
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    frames = {}
    original = OpenCvPhaseDetector.detect

    def detect(self, *args, **kwargs):
        detection, artifacts = original(self, *args, **kwargs)
        rci.require(artifacts is not None, 'detector artifacts unavailable; a debug trace level is required')
        rows = frame_unit(detection, artifacts, tolerances[detection.glass_id])
        unit = {row['idx'] for row in rows if row['accepted']}
        frames[(detection.glass_id, detection.frame_index)] = dict(
            time=float(detection.time_sec), unit=sorted(unit),
            candidates=[(c.kind.value, c.source, float(c.y)) for c in detection.candidates],
            rows=[{k: row[k] for k in ('idx', 'y', 'source', 'decision', 'accepted', 'counts', 'check')}
                  for row in rows])
        if inject:
            for index, candidate in enumerate(detection.candidates):
                if candidate.kind is BoundaryKind.OIL_AIR:
                    candidate.features[FEATURE] = float(index in unit)
        return detection, artifacts

    with patch.object(OpenCvPhaseDetector, 'detect', detect):
        yield frames


def attach(raw, units):
    """Copy saved raw rows with the unit attached to every Oil candidate."""
    copied = deepcopy(raw)
    for row in copied:
        unit = set(units[row['frame_index']])
        for index, candidate in enumerate(row['candidates']):
            if candidate['kind'] == 'oil_air':
                candidate['features'][FEATURE] = float(index in unit)
    return copied


def bind_units(raw, frames):
    """Require captured candidates to equal the saved raw candidates frame by frame."""
    by_frame = {frame: item for (_, frame), item in frames.items()}
    rci.require(len(by_frame) == len(frames), 'one Glass expected')
    units = {}
    for row in raw:
        item = by_frame.get(row['frame_index'])
        rci.require(item is not None, f"frame {row['frame_index']} not captured")
        saved = [(c['kind'], c['source'], float(c['y'])) for c in row['candidates']]
        rci.require([tuple(c) for c in item['candidates']] == saved,
                    f"captured candidates differ from raw.json at frame {row['frame_index']}")
        units[row['frame_index']] = list(item['unit'])
    return units


# --- consumers --------------------------------------------------------------------

def support(candidate, candidates, glass, *, evidence_index, qualified, exemptions=None):
    """Copy of resolver._cross_representation_support differing only in the texture peer exclusion."""
    unit = resolver._unit
    candidate_family = resolver._candidate_representation_family(candidate, evidence_index.evidence(candidate))
    tolerance = max(8.0, float(glass.detector_settings.temporal_max_jump_px) * 0.375)
    value = 0.0
    for peer in candidates:
        if peer is candidate:
            continue
        peer_evidence = evidence_index.evidence(peer)
        peer_family = resolver._candidate_representation_family(peer, peer_evidence)
        if peer_family == candidate_family or not resolver._candidate_eligible(peer, peer_evidence):
            continue
        texture_excluded = peer_evidence.material_texture_conflict >= 0.60
        if texture_excluded and qualified and in_unit(candidate) and in_unit(peer):
            texture_excluded = False
            if exemptions is not None:
                exemptions.append((float(peer.y), peer.source))
        if (texture_excluded or peer_evidence.artifact_signature >= 0.44
                or peer_evidence.optics_opposition >= 0.46):
            continue
        if "calibrated_raster" in {candidate_family, peer_family} and "material" not in {
                candidate_family, peer_family}:
            continue
        distance = abs(float(peer.y) - float(candidate.y))
        if distance > tolerance:
            continue
        peer_features = peer.features
        peer_boundary = unit(peer_features.get("boundary_likelihood", peer.feature_score))
        peer_artifact = unit(peer_features.get(
            "artifact_likelihood", peer.penalties.get("artifact_likelihood", 0.0)))
        peer_coverage = unit(peer_features.get(
            "narrow_horizontal_coverage", peer_features.get("horizontal_coverage", 0.0)))
        advantage = unit((peer_boundary - peer_artifact + 0.10) / 0.30)
        evidence = unit(0.55 * peer_evidence.material_support + 0.25 * peer_coverage + 0.20 * advantage)
        proximity = 0.75 + 0.25 * unit(1.0 - distance / tolerance)
        value = max(value, evidence * proximity)
    return unit(value)


def demote(refs, glass, *, qualified, changes=None):
    """Copy of resolver._demote_non_nearest_ordered_lower_anchors with the unit-qualified first anchor."""
    anchors = tuple(ref for ref in refs
                    if ref.phase_identity is resolver.OilPhaseIdentity.ORDERED_LOWER_INTERFACE
                    and ref.authority is resolver.OilCandidateAuthority.ANCHOR_ELIGIBLE)
    if not anchors:
        return refs
    unit_anchors = [ref for ref in anchors if in_unit(ref.candidate)] if qualified else []
    first_y = min(float(ref.candidate.y) for ref in (unit_anchors or anchors))
    tolerance = max(6.0, float(glass.detector_settings.temporal_max_jump_px) * 0.25)
    output = []
    for ref in refs:
        y = float(ref.candidate.y)
        gate = None
        if ref in anchors and y > first_y + tolerance:
            gate = NEAREST_GATE
        elif ref in anchors and unit_anchors and y < first_y and not in_unit(ref.candidate):
            gate = ABOVE_GATE
        if gate is None:
            output.append(ref)
            continue
        if changes is not None and gate == ABOVE_GATE:
            changes.append(dict(y=y, source=ref.candidate.source, gate=gate, first_y=first_y))
        output.append(replace(
            ref,
            authority=resolver.OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            initial_authority=resolver.OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            post_track_authority=resolver.OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            authority_reason=resolver.AuthorityReason.CONTINUATION,
            authority_failed_gates=(gate,),
            phase_identity=resolver.OilPhaseIdentity.CONTINUATION_ONLY,
            phase_identity_failed_gates=(gate,),
            identity_contradiction=resolver.OilIdentityContradiction.NON_NEAREST_ORDERED_LOWER,
        ))
    return output


@contextmanager
def qualified_authority(*, verify_copy=True, enabled=True):
    """Patch both consumers; yield the list of operations that changed a value.

    With ``verify_copy`` every call also evaluates the copy with the consumer off and
    requires exact equality with the original function.
    """
    original_support = resolver._cross_representation_support
    original_demote = resolver._demote_non_nearest_ordered_lower_anchors
    operations = []

    def patched_support(candidate, candidates, glass, *, evidence_index):
        if verify_copy:
            rci.require(support(candidate, candidates, glass, evidence_index=evidence_index, qualified=False)
                        == original_support(candidate, candidates, glass, evidence_index=evidence_index),
                        'LBQ-1 support copy diverges from the original')
        exemptions = []
        trial = support(candidate, candidates, glass, evidence_index=evidence_index,
                        qualified=enabled, exemptions=exemptions)
        if exemptions:
            ordinary = original_support(candidate, candidates, glass, evidence_index=evidence_index)
            if trial != ordinary:
                operations.append(dict(consumer='support', candidate_y=float(candidate.y),
                                       source=candidate.source, ordinary=ordinary, trial=trial,
                                       exempted_peers=[dict(y=y, source=s) for y, s in exemptions]))
        return trial

    def patched_demote(refs, glass):
        if verify_copy:
            rci.require(demote(refs, glass, qualified=False) == original_demote(refs, glass),
                        'LBQ-1 demotion copy diverges from the original')
        changes = []
        output = demote(refs, glass, qualified=enabled, changes=changes)
        operations.extend(dict(consumer='demote', **change) for change in changes)
        return output

    with patch.object(resolver, '_cross_representation_support', patched_support), \
            patch.object(resolver, '_demote_non_nearest_ordered_lower_anchors', patched_demote):
        yield operations
    rci.require(resolver._cross_representation_support is original_support
                and resolver._demote_non_nearest_ordered_lower_anchors is original_demote, 'LBQ-1 patch leak')


# --- sample4 population -----------------------------------------------------------

def _pipeline(sample, root, scratch, *, trial, inject):
    from tests.diagnostics.s11_report_observability_replay import _session, QUALIFICATION_WINDOWS
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.session import DebugTraceLevel

    recipe, session = _session(sample, root / 'sample' / f'{sample}.mp4', Path(scratch),
                               *QUALIFICATION_WINDOWS[sample], run_label='LBQ-1', run_note='off')
    session.debug_trace_level = DebugTraceLevel.BASIC
    tolerances = {g.id: lbw.same_boundary_tolerance(g) for g in recipe.glasses if g.enabled}
    with live_units(tolerances, inject=inject) as frames, \
            (qualified_authority() if trial else nullcontext([])) as operations:
        result = AnalysisPipeline(OpenCvVideoReader, OpenCvPhaseDetector(), RecipeValidationService(),
                                  JsonlDebugTraceWriterFactory(Path(scratch))).run(recipe, session)
    rci.require(not result.errors, f'{sample} analysis errors: {result.errors}')
    return result, frames, list(operations)


def prepare_sample4(root, work):
    """Capture sample4 rasters once; return units bound to the saved raw rows."""
    from tests.diagnostics.s11_report_observability_replay import _tracking_fingerprint
    with TemporaryDirectory(dir=work) as scratch:
        result, frames, _ = _pipeline('sample4', root, scratch, trial=False, inject=False)
    fingerprint = _tracking_fingerprint(result)
    rci.require(fingerprint == lbw.P5_FINGERPRINT, f'sample4 fingerprint {fingerprint} differs from P5')
    raw = json.loads((root / rci.SAVED / 'raw.json').read_text(encoding='utf-8'))
    units = bind_units(raw, frames)
    rows = [row for item in frames.values() for row in item['rows']]
    valid, failed, checked = lbw._check_valid(rows)
    rci.require(valid, f'witness self-check invalid: {failed}/{checked}')
    return raw, units, frames, dict(fingerprint=fingerprint, self_check_failed=failed, self_check_checked=checked)


def make_trial(units):
    def execute(raw, recipe, case):
        with qualified_authority() as operations:
            result = soi.execute(attach(raw, units), recipe, case)
        return (*result, operations)
    return execute


def layer_report(raw, recipe, units):
    """Per frame with a non-empty unit: unit rows, authority and publication, ordinary versus trial."""
    attached = attach(raw, units)
    with qualified_authority() as _:
        trial = soi.execute(attached, recipe, None)
    ordinary = soi.execute(raw, recipe, None)
    report = []
    for offset, row in enumerate(raw):
        if not units[row['frame_index']]:
            continue
        entry = dict(frame=row['frame_index'], time=row['time_sec'], unit=[])
        for name, (record, result, _, _) in (('ordinary', ordinary), ('trial', trial)):
            detection = result.detections[offset]
            entry[f'{name}_oil'] = record['rows'][offset]['oil_y']
            entry[f'{name}_phase'] = record['rows'][offset]['phase']['value']
            selected = record['rows'][offset]['selected']
            if selected is not None:
                features = detection.candidates[selected['candidate_offset']].features
                entry[f'{name}_selected'] = dict(
                    y=selected['y'], source=selected['source'],
                    authority=features.get('sequence_authority_reason'),
                    lifecycle=features.get('sequence_tracklet_lifecycle'),
                    admitted=features.get('sequence_tracklet_admitted'),
                    in_unit=selected['candidate_offset'] in units[row['frame_index']])
            entry[f'{name}_anchors'] = sorted(
                (float(c.y), c.source) for c in detection.candidates
                if c.kind is BoundaryKind.OIL_AIR
                and c.features.get('sequence_authority_reason') == 'ordered_lower_interface')
        for index in units[row['frame_index']]:
            candidate = row['candidates'][index]
            entry['unit'].append(dict(idx=index, y=candidate['y'], source=candidate['source']))
        report.append(entry)
    return report


# --- descriptive recordings ------------------------------------------------------

def descriptive(sample, root, work):
    from tests.diagnostics.s11_report_observability_replay import _tracking_fingerprint
    outputs = {}
    for arm, trial in (('ordinary', False), ('trial', True)):
        with TemporaryDirectory(dir=work) as scratch:
            result, frames, operations = _pipeline(sample, root, scratch, trial=trial, inject=trial)
        rows = [(s.timestamp_sec, s.raw_oil_air_level_y, s.raw_foam_front_y)
                for g in result.glass_results for s in g.samples]
        outputs[arm] = dict(fingerprint=_tracking_fingerprint(result), rows=rows, operations=operations,
                            unit_frames=sum(bool(item['unit']) for item in frames.values()), frames=len(frames))
    changed = [(o, t) for o, t in zip(outputs['ordinary']['rows'], outputs['trial']['rows'], strict=True) if o != t]
    return dict(sample=sample, unit_frames=outputs['trial']['unit_frames'], frames=outputs['trial']['frames'],
                operations=len(outputs['trial']['operations']),
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
    rci.require(inert == soi.execute(raw, recipe, None)[0], 'inert feature changes the ordinary result')
    print('prepared', prep, 'unit frames', sum(bool(u) for u in units.values()), flush=True)
    rci.write_json(work / 'units.json', dict(prep=prep, units=units,
                                             frames={str(f): item for (_, f), item in frames.items()}))
    population = work / 'population'
    population.mkdir()
    caf.run(root, population, trial=make_trial(units), protocol=PROTOCOL,
            schema='s11-layer-bottom-qualified-authority-v1',
            scope='LBQ-1 diagnostic wrapper; not production adoption',
            extra_sources=(Path(__file__), Path(lbw.__file__)))
    rci.write_json(work / 'layers.json', layer_report(raw, recipe, units))
    rci.write_json(work / 'descriptive.json', [descriptive(s, root, work) for s in ('base_sample_1', 'sample2')])
    print('LBQ-1 COMPLETE', flush=True)


if __name__ == '__main__':
    main()
