"""LBT-2 layer-bottom topology with a Foam-visible fill guard. Not a promoted policy.

LBT-1's E1 topology and context-limited support exemption, unchanged, plus F:
a fill chain whose last row lies at least the existing lower separation below a
Foam material identity row seeded within 3 s cannot confirm a fill (T1, the
OPEN/FILLING -> FILLED_BARRIER span confirmation). Refill closures, releases and
every other transition are untouched. The evaluation is the pre-registered P0
net procedure N. See docs/50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager, nullcontext
import gzip
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from oil_tracker.adapters.vision import oil_observation_resolver as resolver
from oil_tracker.adapters.vision.foam_material_identity import foam_material_identity_tolerance
from oil_tracker.adapters.vision.oil_phase_lifecycle import (
    OilFillConfirmationProfile,
    OilMaterialPhaseLifecycleOwner,
)
from oil_tracker.domain.enums import BoundaryKind
from tests.diagnostics import s11_clean_anchor_fill as caf
from tests.diagnostics import s11_layer_bottom_qualified_authority as lbq
from tests.diagnostics import s11_layer_bottom_topology as lbt1
from tests.diagnostics import s11_layer_bottom_witness as lbw
from tests.diagnostics import s11_role_consumer_intervention as rci
from tests.diagnostics import s11_single_observation_influence as soi

PROTOCOL = Path('docs/50-diagnostics/s11/2026-10-22-layer-bottom-topology-2.md')
REVIEW_REPLY = Path('docs/50-diagnostics/s11/2026-10-22-review-013-sample4-reply.json')
LBT1_POPULATION = Path('sample/output/s11-layer-bottom-topology-20261020-001/evidence/population/population.jsonl.gz')
ROI_INPUTS = Path('sample/output/s11-empty-fill-roi-20261022-001/evidence/inputs')
DESCRIPTIVE = ('base_sample_1', 'sample2', 'sample5', 'sample7')
EMPTY_START = ('sample5', 'sample7')  # the user: both start EMPTY and never become full
C1_PX = 5.2  # P0 C1: 5 % of the sample4 Glass diameter (2 x 52 px)
FPS = 30.0
FOAM_REVIEW_SEC = (39.5, 56.0)  # review-013 Q1: a Foam layer is visible in every frame


# --- F, the Foam-visible fill guard -----------------------------------------------

def foam_above(identity, separation, frame, y):
    """The chain's last row lies at least `separation` below a Foam row seeded within the limit."""
    row = identity.row(frame)
    age = identity.seed_age_seconds(frame)
    return bool(row is not None and age is not None and age <= lbt1.SEED_LIMIT
                and float(y) >= float(row) + float(separation))


@contextmanager
def fill_guard(*, enabled=True):
    """F: withhold the T1 fill confirmation; yield the withheld confirmations."""
    original_track = resolver.track_foam_material_identity
    original_profile = OilMaterialPhaseLifecycleOwner._fill_confirmation_profile
    passes, operations = [], []

    def track(detections, glass, **kwargs):
        identity = original_track(detections, glass, **kwargs)
        passes.append((identity, foam_material_identity_tolerance(glass) + 2.0))
        return identity

    def profile(self, chain):
        result = original_profile(self, chain)
        if enabled and result is not OilFillConfirmationProfile.NONE and passes:
            identity, separation = passes[-1]
            last = chain.last
            if foam_above(identity, separation, last.frame, last.y):
                operations.append(dict(consumer='F', frame=int(last.frame), y=float(last.y),
                                       foam_row=float(identity.row(last.frame)), withheld=result.value))
                return OilFillConfirmationProfile.NONE
        return result

    with patch.object(resolver, 'track_foam_material_identity', track), \
            patch.object(OilMaterialPhaseLifecycleOwner, '_fill_confirmation_profile', profile):
        yield operations
    rci.require(resolver.track_foam_material_identity is original_track
                and OilMaterialPhaseLifecycleOwner._fill_confirmation_profile is original_profile,
                'LBT-2 patch leak')


@contextmanager
def changes(*, guard=True):
    """LBT-1's E1 and support exemption plus F; the list is complete after the block."""
    operations = []
    with lbt1.topology() as topology_operations, fill_guard(enabled=guard) as guard_operations:
        yield operations
    operations.extend(topology_operations)
    operations.extend(guard_operations)


def make_trial(units, *, guard=True):
    def execute(raw, recipe, case):
        with changes(guard=guard) as operations:
            result = soi.execute(lbt1.attach(raw, units), recipe, case)
        return (*result, operations)
    return execute


# --- sample4 layer report -----------------------------------------------------------

def layer_report(raw, recipe, units):
    """Per frame: Foam rows, unit top, both arms' Oil, phase and the published row; F and mixing."""
    with changes() as operations:
        trial_record, trial, _, _ = soi.execute(lbt1.attach(raw, units), recipe, None)
    ordinary_record, _, _, _ = soi.execute(raw, recipe, None)
    frames, above, inside = [], {}, {}
    for offset, row in enumerate(raw):
        unit = set(units[row['frame_index']])
        detection = trial.detections[offset]
        foam = [float(c.y) for c in detection.candidates if c.kind is BoundaryKind.FOAM_FRONT
                and resolver._unit(c.features.get('sequence_foam_eligible', 0.0)) >= 0.5]
        unit_ys = {float(row['candidates'][i]['y']) for i in unit}
        for y, tracklet, _ in lbt1._members(detection):
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
            frame=row['frame_index'], time=row['time_sec'], foam=foam, unit_top=min(unit_ys, default=None),
            ordinary_oil=ordinary_record['rows'][offset]['oil_y'], trial_oil=trial_record['rows'][offset]['oil_y'],
            ordinary_foam=ordinary_record['rows'][offset]['foam_y'], trial_foam=trial_record['rows'][offset]['foam_y'],
            phase=metrics['sequence_material_phase'], reason=metrics['sequence_material_phase_reason'],
            fill_profile=metrics.get('sequence_material_phase_fill_confirmation_profile'),
            owner_chain=metrics.get('sequence_material_phase_owner_chain'), published=published))
    mixing = {t: dict(above=above[t], unit=inside[t]) for t in sorted(set(above) & set(inside))}
    counts = Counter(op['consumer'] for op in operations)
    return dict(frames=frames, mixing=mixing, operations=dict(counts),
                f_operations=[op for op in operations if op['consumer'] == 'F'])


# --- descriptive controls -----------------------------------------------------------

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _pipeline(sample, root, scratch, *, trial):
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.enums import InitialObservationState
    from oil_tracker.domain.session import DebugTraceLevel, InitialStateConfirmation
    from tests.diagnostics.s11_initial_full_comparison import EMPTY_FILL_CONTROLS
    from tests.diagnostics.s11_report_observability_replay import QUALIFICATION_WINDOWS, _session

    video = root / 'sample' / f'{sample}.mp4'
    recipe_path, window = None, QUALIFICATION_WINDOWS.get(sample)
    if sample in EMPTY_START:
        recipe_path = root / ROI_INPUTS / f'{sample}.oilrecipe'
        frozen = json.loads((root / ROI_INPUTS / 'roi-inputs.json').read_text(encoding='utf-8'))
        rci.require(_sha(recipe_path) == frozen['recipes'][sample]['comparison_recipe_sha256'],
                    f'{sample} Recipe differs from the frozen ROI input')
        window = EMPTY_FILL_CONTROLS[sample]['window']
    recipe, session = _session(sample, video, Path(scratch), *window, run_label='LBT-2',
                               run_note='trial' if trial else 'ordinary', recipe_path=recipe_path)
    if sample in EMPTY_START:
        for glass in recipe.glasses:
            glass.initial_state = InitialObservationState.EMPTY_NO_INTERFACE
            session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
                InitialObservationState.EMPTY_NO_INTERFACE, session.input_video_path, session.analysis_start_sec)
    session.debug_trace_level = DebugTraceLevel.BASIC
    tolerances = {g.id: lbw.same_boundary_tolerance(g) for g in recipe.glasses if g.enabled}
    with lbt1.live_units(tolerances, inject=trial) as frames, \
            (changes() if trial else nullcontext([])) as operations:
        result = AnalysisPipeline(OpenCvVideoReader, OpenCvPhaseDetector(), RecipeValidationService(),
                                  JsonlDebugTraceWriterFactory(Path(scratch))).run(recipe, session)
    rci.require(not result.errors, f'{sample} analysis errors: {result.errors}')
    return result, frames, list(operations)


def descriptive(sample, root, work):
    from tests.diagnostics.s11_report_observability_replay import _tracking_fingerprint
    outputs = {}
    for arm, trial in (('ordinary', False), ('trial', True)):
        with TemporaryDirectory(dir=work) as scratch:
            result, frames, operations = _pipeline(sample, root, scratch, trial=trial)
        rows = [(s.timestamp_sec, s.raw_oil_air_level_y, s.raw_foam_front_y, s.fill_state.value)
                for g in result.glass_results for s in g.samples]
        outputs[arm] = dict(fingerprint=_tracking_fingerprint(result), rows=rows, operations=operations,
                            unit_frames=sum(bool(item['unit']) for item in frames.values()), frames=len(frames))
    changed = [(o, t) for o, t in zip(outputs['ordinary']['rows'], outputs['trial']['rows'], strict=True) if o != t]
    counts = Counter(op['consumer'] for op in outputs['trial']['operations'])
    return dict(sample=sample, initial_state='EMPTY' if sample in EMPTY_START else 'UNKNOWN',
                unit_frames=outputs['trial']['unit_frames'], frames=outputs['trial']['frames'],
                operations=dict(counts),
                f_operations=[op for op in outputs['trial']['operations'] if op['consumer'] == 'F'],
                fingerprint_equal=outputs['ordinary']['fingerprint'] == outputs['trial']['fingerprint'],
                changed_rows=changed)


# --- pre-registered evaluation (N) ----------------------------------------------------

def references(controls, reply):
    """Per frame index: accepted values, wrong-target values and the review-013 band, all from user judgments."""
    refs = {}

    def at(frame):
        return refs.setdefault(int(frame), dict(accepted=[], wrong=[], band=None))

    for control in controls:  # LBT-1's frozen controls
        at(control['frame'])['accepted' if control['review_label'] == 'ACCEPTED' else 'wrong'].append(
            float(control['y']))
    at(1275)['wrong'].append(805.0)  # LBQ-1 opposed, 42.5 s
    for frame, y in ((1530, 861.5), (1545, 862.0), (1560, 862.0)):  # CAF-1 user judgment: wrong 51-52 s run
        at(frame)['wrong'].append(y)
    for frame, y in ((1620, 833.0), (1665, 837.0), (1680, 838.0)):  # 2026-10-09 reply: internal Foam texture
        at(frame)['wrong'].append(y)
    for item in reply['q2_reading']['frames']:  # review-013 Q2: marked surface, widened by C1
        low, high = item['y_range']
        at(item['frame_index'])['band'] = [round(low - C1_PX, 1), round(high + C1_PX, 1)]
    return refs


def outcome(y, ref):
    """A, B, C or U for one published Oil value; None when the frame has no positive reference and no value."""
    accepted, wrong, band = ref['accepted'], ref['wrong'], ref['band']
    if y is None:
        return 'B' if accepted or band else None
    y = float(y)
    if band and band[0] <= y <= band[1]:
        return 'C'
    if any(abs(y - value) <= C1_PX for value in accepted):
        return 'C'
    if any(abs(y - value) <= C1_PX for value in wrong):
        return 'A'
    return 'A' if band else 'U'


def transition(ordinary, trial):
    """worse: the trial gains an A or loses a C; better: it loses an A or gains a C."""
    if (trial == 'A' and ordinary != 'A') or (ordinary == 'C' and trial != 'C'):
        return 'worse'
    if (ordinary == 'A' and trial != 'A') or (trial == 'C' and ordinary != 'C'):
        return 'better'
    return 'same'


def foam_change(ordinary_y, trial_y, time_sec):
    """Option (b) against review-013 Q1: Foam is visible in every frame of the reviewed window."""
    if ordinary_y == trial_y:
        return None
    if not FOAM_REVIEW_SEC[0] <= float(time_sec) <= FOAM_REVIEW_SEC[1]:
        return 'U'
    if ordinary_y is None:
        return 'right'
    if trial_y is None:
        return 'wrong'
    return 'U'


def _owner(row):
    selected = row.get('selected') or {}
    return dict(y=row['oil_y'], tracklet=selected.get('tracklet_id'), source=selected.get('source'),
                phase=row['phase']['value'], reason=row['phase']['reason'])


def evaluate(records, refs):
    """Score every condition against its ordinary arm and apply the stop rules N."""
    units = Counter()
    worse, foam_counts, foam_wrong, baseline = [], Counter(), [], dict(units=[], new_a=[])
    for record in records:
        case_id = record['ordinary']['id']
        ordinary = {row['frame_index']: row for row in record['ordinary']['rows']}
        trial = {row['frame_index']: row for row in record['trial']['rows']}
        for frame, ref in sorted(refs.items()):
            o, t = outcome(ordinary[frame]['oil_y'], ref), outcome(trial[frame]['oil_y'], ref)
            if o is None and t is None:
                continue
            kind = transition(o, t)
            unit = dict(case=case_id, frame=frame, time=round(frame / FPS, 2), ordinary=o, trial=t, kind=kind,
                        ordinary_owner=_owner(ordinary[frame]), trial_owner=_owner(trial[frame]))
            if case_id == 'baseline':
                baseline['units'].append(unit)
                if t == 'A' and o != 'A':
                    baseline['new_a'].append(unit)
                continue
            units[kind] += 1
            if kind == 'worse':
                worse.append(unit)
        for frame in sorted(trial):
            change = foam_change(ordinary[frame]['foam_y'], trial[frame]['foam_y'], trial[frame]['time_sec'])
            if change is None:
                continue
            foam_counts[change] += 1
            if change == 'wrong':
                foam_wrong.append(dict(case=case_id, frame=frame, time=trial[frame]['time_sec'],
                                       ordinary=ordinary[frame]['foam_y'], trial=trial[frame]['foam_y']))
    stops = []
    if baseline['new_a']:
        stops.append('the baseline gains an A')
    if units['worse'] >= units['better']:
        stops.append('the population net does not improve')
    if foam_counts['wrong'] and foam_counts['wrong'] >= foam_counts['right']:
        stops.append('wrong Foam changes are not outweighed by right ones')
    return dict(units=dict(units), worse=worse, foam=dict(foam_counts), foam_wrong=foam_wrong,
                baseline=baseline, stops=stops, verdict='STOP' if stops else 'NO STOP')


def lbt1_equality(root, raw, recipe, units):
    """With F off, the baseline trial equals LBT-1's kept baseline trial."""
    with gzip.open(root / LBT1_POPULATION, 'rt', encoding='utf-8') as stream:
        kept = json.loads(stream.readline())
    rci.require(kept['ordinary']['id'] == 'baseline', 'LBT-1 kept population does not start with the baseline')
    record = make_trial(units, guard=False)(raw, recipe, None)[0]
    return record['rows'] == kept['trial']['rows'] and record['events'] == kept['trial']['events']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=rci.ROOT)
    parser.add_argument('--work', type=Path, required=True, help='managed run work directory')
    args = parser.parse_args()
    root, work = args.root.resolve(), args.work.resolve()
    raw, units, frames, prep = lbt1.prepare_sample4(root, work)
    recipe = rci.JsonRecipeRepository().load(root / rci.BUNDLE / 'recipe_snapshot.oilrecipe')
    rci.require(soi.execute(lbt1.attach(raw, units), recipe, None)[0] == soi.execute(raw, recipe, None)[0],
                'inert features change the ordinary result')
    rci.require(lbt1_equality(root, raw, recipe, units), 'with F off, the baseline differs from LBT-1')
    print('prepared', prep, 'unit frames', sum(bool(u) for u in units.values()), 'F-off equals LBT-1', flush=True)
    population = work / 'population'
    population.mkdir()
    caf.run(root, population, trial=make_trial(units), protocol=PROTOCOL,
            schema='s11-layer-bottom-topology-2-v1',
            scope='LBT-2 diagnostic wrapper; not production adoption',
            extra_sources=(Path(__file__), Path(lbt1.__file__), Path(lbq.__file__), Path(lbw.__file__)))
    rci.write_json(work / 'layers.json', layer_report(raw, recipe, units))
    controls = json.loads((population / 'comparison.json').read_text(encoding='utf-8'))['preflight']['controls']
    refs = references(controls, json.loads((root / REVIEW_REPLY).read_text(encoding='utf-8')))
    with gzip.open(population / 'population.jsonl.gz', 'rt', encoding='utf-8') as stream:
        records = [json.loads(line) for line in stream]
    rci.write_json(work / 'evaluation.json', dict(references={str(k): v for k, v in refs.items()},
                                                   **evaluate(records, refs)))
    rci.write_json(work / 'descriptive.json', [descriptive(s, root, work) for s in DESCRIPTIVE])
    print('LBT-2 COMPLETE', flush=True)


if __name__ == '__main__':
    main()
