"""FLB-1/FLB-2: desk emulation of "Oil follows the dense-Foam layer bottom, then hands off explicitly".

Protocols (each frozen before its run): docs/50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow.md (FLB-1,
closed) and docs/50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md (FLB-2).

The emulation reads, per frame, the detector's own Foam front candidates (eligibility and
``material_component_bottom_y``), the same-frame eligible Oil candidate rows and the ordinary
output. It changes no detector code: it only recomputes which existing Oil candidate row a
follow rule would publish. sample4 replays the saved P5 capture (the LBT-2 ordinary arm); the
descriptive controls run the ordinary analysis entry with a read-only capture of each frame.

Usage (repository root, inside a managed run):
    PYTHONPATH=src python -m tests.diagnostics.s11_foam_layer_bottom_follow --work <work>
FLB-2 on a saved FULL-debug bundle (no detector run; Windows):
    ... --work <work> --bundle <bundle> --glass-name <name> --start <s> --end <s>
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

PROTOCOL = Path('docs/50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow.md')
REVIEW014 = Path('docs/50-diagnostics/s11/2026-10-23-review-014-sample4-reply.json')
C1_PX = 5.2  # P0 C1: 5 % of the sample4 Glass diameter (2 x 52 px)
CONTROLS = ('base_sample_1', 'sample2', 'sample5', 'sample7')

NONE, FOLLOW, HANDOFF = 'NONE', 'FOLLOW', 'HANDOFF'


def witness(frame):
    """The eligible Foam front with a recorded component bottom, or None (the first such, by front Y)."""
    eligible = sorted((front, bottom) for front, bottom, ok in frame['foam'] if ok and bottom is not None)
    return eligible[0][1] if eligible else None


def nearest_row(rows, target, tolerance):
    """Nearest same-frame eligible Oil row within tolerance of the target; a tie goes to the lower row."""
    near = [y for y in rows if abs(y - target) <= tolerance]
    return min(near, key=lambda y: (abs(y - target), -y)) if near else None


def follow(frames, *, tolerance, max_jump):
    """Frozen rule (FLB-1): per frame (y, state, reason). Outside FOLLOW/HANDOFF the ordinary output stands."""
    state, last_bottom, last_y, out = NONE, None, None, []
    for frame in frames:
        bottom = witness(frame)
        if bottom is not None and last_bottom is not None and state == FOLLOW and abs(bottom - last_bottom) > max_jump:
            bottom = None  # a discontinuous layer bottom is not the same layer
        if state == HANDOFF and bottom is not None:
            anchor = last_y if last_y is not None else last_bottom
            if abs(bottom - anchor) > tolerance:
                bottom = None  # a layer bottom away from the handed-off Oil does not re-enter
        if bottom is not None:
            state, last_bottom = FOLLOW, bottom
            y = nearest_row(frame['oil_rows'], bottom, tolerance)
            reason = 'FOLLOW_LAYER_BOTTOM' if y is not None else 'FOLLOW_NO_ROW'
        elif state in (FOLLOW, HANDOFF):
            state = HANDOFF
            ordinary = frame['ordinary_y']
            if ordinary is not None and ordinary >= last_bottom - tolerance:
                y, reason = ordinary, 'HANDOFF_BELOW_LAST_BOTTOM'
            else:
                y, reason = None, 'HANDOFF_NO_LOWER_OUTPUT' if ordinary is None else 'HANDOFF_ABOVE_LAST_BOTTOM'
        else:
            y, reason = frame['ordinary_y'], 'ORDINARY'
        if y is not None:
            last_y = y
        out.append(dict(time=frame['time'], frame=frame['frame'], y=y, state=state, reason=reason,
                        bottom=bottom, ordinary_y=frame['ordinary_y']))
    return out


# --- FLB-2 (successor; protocol docs/50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow-2.md) ---

SEED_LIMIT_SEC = 3.0  # existing ORDERED_LOWER_INTERFACE Foam seed-age limit (oil_phase_identity)


def layer_witness(frame):
    """FLB-2 witness: an eligible detached-layer Foam front with a recorded bottom (highest front first)."""
    layers = sorted((item['y'], item['bottom']) for item in frame['foam_full']
                    if item['eligible'] and item['phenotype'] == 'detached_layer' and item['bottom'] is not None)
    return layers[0][1] if layers else None


def follow2(frames, *, tolerance, max_jump, memory_sec=SEED_LIMIT_SEC):
    """Frozen FLB-2 rule: per frame (y, state, reason); NONE keeps the ordinary output."""
    state, last_bottom, last_witness_time = NONE, None, None
    published = []  # (time, y) of this rule's numeric outputs
    out = []
    for frame in frames:
        now = frame['time']
        bottom = layer_witness(frame)
        recent = [y for t, y in published if now - t <= memory_sec]
        if bottom is not None:
            if state == FOLLOW:
                accept = abs(bottom - last_bottom) <= max_jump
            else:
                accept = not recent or abs(bottom - recent[-1]) <= tolerance
            if not accept:
                bottom = None
        if state == HANDOFF and bottom is None and now - last_witness_time > memory_sec:
            state = NONE  # the hand-off memory expires with the existing seed-age limit
        if bottom is not None:
            state, last_bottom, last_witness_time = FOLLOW, bottom, now
            y = nearest_row(frame['oil_rows'], bottom, tolerance)
            reason = 'FOLLOW_LAYER_BOTTOM' if y is not None else 'FOLLOW_NO_ROW'
        elif state in (FOLLOW, HANDOFF):
            state = HANDOFF
            ordinary = frame['ordinary_y']
            if ordinary is not None and ordinary >= last_bottom - tolerance:
                y, reason = ordinary, 'HANDOFF_BELOW_LAST_BOTTOM'
            else:
                y, reason = None, 'HANDOFF_NO_LOWER_OUTPUT' if ordinary is None else 'HANDOFF_ABOVE_LAST_BOTTOM'
        else:
            y, reason = frame['ordinary_y'], 'ORDINARY'
        if y is not None:
            published.append((now, y))
        out.append(dict(time=now, frame=frame['frame'], y=y, state=state, reason=reason,
                        bottom=bottom, ordinary_y=frame['ordinary_y']))
    return out


# --- strict sample4 references and scoring ------------------------------------------

def references(controls, reply):
    """Per frame index, strict rule (2026-10-23): P0/LBT-1 values, LBQ-1, CAF-1 and the review-014 bands."""
    refs = {}

    def at(frame):
        return refs.setdefault(int(frame), dict(accepted=[], wrong=[], band=None, confidence='clear'))

    for control in controls:
        at(control['frame'])['accepted' if control['review_label'] == 'ACCEPTED' else 'wrong'].append(float(control['y']))
    at(1275)['wrong'].append(805.0)  # LBQ-1 opposed, 42.5 s
    for frame, y in ((1530, 861.5), (1545, 862.0), (1560, 862.0)):  # CAF-1: wrong 51-52 s run
        at(frame)['wrong'].append(y)
    for item in reply['q1_marks']['frames']:  # review-014, x 575-615, widened by C1
        low, high = item['y_range_x575_615']
        ref = at(item['frame_index'])
        ref['band'] = [round(low - C1_PX, 1), round(high + C1_PX, 1)]
        ref['confidence'] = ('approximate' if 54.0 <= item['time_sec'] <= 54.5
                             else 'foam_region_bottom' if item['time_sec'] >= 55.0 else 'clear')
    return refs


def outcome(y, ref):
    """C right, A wrong value, B miss, U value without a matching reference; None without a positive reference."""
    accepted, wrong, band = ref['accepted'], ref['wrong'], ref['band']
    if ref['confidence'] == 'not_visible':  # the user saw no Oil boundary: abstaining is right
        return 'C' if y is None else 'A'
    if y is None:
        return 'B' if accepted or band else None
    if band and band[0] <= y <= band[1]:
        return 'C'
    if any(abs(y - value) <= C1_PX for value in accepted):
        return 'C'
    if any(abs(y - value) <= C1_PX for value in wrong):
        return 'A'
    return 'A' if band or accepted else 'U'


def score(rows, refs):
    table, counts = [], {'ordinary': {}, 'rule': {}}
    for row in rows:
        ref = refs.get(row['frame'])
        if ref is None:
            continue
        pair = dict(time=row['time'], frame=row['frame'], confidence=ref['confidence'],
                    ordinary=row['ordinary_y'], ordinary_class=outcome(row['ordinary_y'], ref),
                    rule=row['y'], rule_class=outcome(row['y'], ref), reason=row['reason'])
        for arm in ('ordinary', 'rule'):
            key = pair[f'{arm}_class']
            if key is not None:
                counts[arm][key] = counts[arm].get(key, 0) + 1
        table.append(pair)
    return table, counts


def review_references(table_v, c1):
    """FLB-2 held-out references from review-012's table V: per frame, the marks' y range widened by C1.

    Each item: frame, y_range ([low, high] or None) and the user's words (대략, 최하단, 안 보임 or empty).
    A frame without marks or words is not scored.
    """
    refs = {}
    for item in table_v:
        words = item.get('words') or ''
        if '안 보임' in words:
            refs[int(item['frame'])] = dict(accepted=[], wrong=[], band=None, confidence='not_visible')
        elif item.get('y_range'):
            low, high = item['y_range']
            refs[int(item['frame'])] = dict(
                accepted=[], wrong=[], band=[round(low - c1, 1), round(high + c1, 1)],
                confidence='foam_region_bottom' if '최하단' in words else 'approximate' if '대략' in words else 'clear')
    return refs


def held_out(rows, table_v, c1):
    """Frozen FLB-2 readings R1-R3 on review-012 (R4, the controls, is read against the reviewed truth)."""
    table, counts = score(rows, review_references(table_v, c1))
    regressions = [pair for pair in table if pair['confidence'] == 'clear'
                   and pair['ordinary_class'] == 'C' and pair['rule_class'] in ('A', 'B')]
    wrong = {arm: sum(counts[arm].get(key, 0) for key in 'AB') for arm in counts}
    return dict(scored=table, counts=counts, regressions=regressions,
                r1_no_clear_regression=not regressions, r2_fewer_wrong=wrong['rule'] < wrong['ordinary'],
                r3_follow_tested=any(pair['reason'].startswith('FOLLOW') for pair in table))


# --- inputs -------------------------------------------------------------------------

def sample4_frames(root):
    from oil_tracker.adapters.vision.foam_material_identity import foam_material_identity_tolerance
    from tests.diagnostics import s11_role_consumer_intervention as rci
    from tests.diagnostics import s11_single_observation_influence as soi

    raw = json.loads((root / rci.SAVED / 'raw.json').read_text(encoding='utf-8'))
    recipe = rci.JsonRecipeRepository().load(root / rci.BUNDLE / 'recipe_snapshot.oilrecipe')
    record, _, _, _ = soi.execute(raw, recipe, None)
    frames = [dict(time=float(row['time_sec']), frame=int(row['frame_index']),
                   ordinary_y=None if out['oil_y'] is None else float(out['oil_y']),
                   foam=[(float(c['y']), _float(c['features'].get('material_component_bottom_y')),
                          float(c['features'].get('sequence_foam_eligible', 0.0)) >= 0.5)
                         for c in row['candidates'] if c['kind'] == 'foam_front'],
                   foam_full=[_foam_item(c['y'], c['features']) for c in row['candidates'] if c['kind'] == 'foam_front'],
                   oil_rows=sorted({float(c['y']) for c in row['candidates'] if c['kind'] == 'oil_air'
                                    and float(c['features'].get('sequence_eligible', 0.0)) >= 0.5}))
              for row, out in zip(raw, record['rows'], strict=True)]
    glass = recipe.glasses[0]
    return frames, dict(tolerance=foam_material_identity_tolerance(glass),
                        max_jump=float(glass.detector_settings.temporal_max_jump_px))


def _float(value):
    return None if value is None else float(value)


# Existing Foam front features copied by the FLB-2 design readout (read-only).
FOAM_READOUT = ('foam_score', 'foam_material_phenotype', 'foam_layer_coherent', 'foam_wide_layer',
                'foam_dynamic_narrow_layer', 'foam_detached_droplet', 'foam_dynamic_detached_droplet',
                'material_component_bottom_y', 'sequence_foam_eligible', 'sequence_foam_eligibility_failed_gates')


def _foam_item(y, features):
    return dict(y=float(y), bottom=_float(features.get('material_component_bottom_y')),
                eligible=float(features.get('sequence_foam_eligible', 0.0)) >= 0.5,
                phenotype=features.get('foam_material_phenotype'))


def _plain(value):
    return value if value is None or isinstance(value, (str, bool, int, float)) else str(value)


def design_readout(root, work):
    """FLB-2 design readout: per control and frame, the Foam front features and the ordinary output."""
    from tests.diagnostics import s11_role_consumer_intervention as rci

    raw = json.loads((root / rci.SAVED / 'raw.json').read_text(encoding='utf-8'))
    frames, _ = sample4_frames(root)
    out = {'sample4': [dict(time=f['time'], ordinary_y=f['ordinary_y'],
                            foam=[{key: _plain(c['features'].get(key)) for key in FOAM_READOUT} | {'y': c['y']}
                                  for c in row['candidates'] if c['kind'] == 'foam_front'])
                       for f, row in zip(frames, raw, strict=True)]}
    for sample in CONTROLS:
        for name, (rows, _params) in control_frames(sample, root, work).items():  # noqa: B007
            out[f'{sample}/{name}'] = [dict(time=r['time'], frame=r['frame'], ordinary_y=r['ordinary_y'],
                                            oil_rows=r['oil_rows'], foam_full=r['foam_full'],
                                            foam=[feat | {'y': y} for feat, (y, _b, _e)
                                                  in zip(r['foam_features'], r['foam'], strict=True)])
                                       for r in rows]
            out[f'{sample}/{name}/params'] = _params
    return out


@contextmanager
def captured():
    """Read-only copy of every detection's candidates; the detection itself is returned untouched."""
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector

    frames, original = {}, OpenCvPhaseDetector.detect

    def detect(self, *args, **kwargs):
        detection, artifacts = original(self, *args, **kwargs)
        frames[(detection.glass_id, detection.frame_index)] = dict(
            time=float(detection.time_sec), frame=int(detection.frame_index),
            foam=[(float(c.y), _float(c.features.get('material_component_bottom_y')),
                   float(c.features.get('sequence_foam_eligible', 0.0)) >= 0.5)
                  for c in detection.candidates if c.kind.value == 'foam_front'],
            foam_features=[{key: _plain(c.features.get(key)) for key in FOAM_READOUT}
                           for c in detection.candidates if c.kind.value == 'foam_front'],
            foam_full=[_foam_item(c.y, c.features) for c in detection.candidates if c.kind.value == 'foam_front'],
            oil_rows=sorted({float(c.y) for c in detection.candidates if c.kind.value == 'oil_air'
                             and float(c.features.get('sequence_eligible', 0.0)) >= 0.5}))
        return detection, artifacts

    with patch.object(OpenCvPhaseDetector, 'detect', detect):
        yield frames


def control_frames(sample, root, work):
    """Ordinary analysis entry of LBT-2's descriptive controls, with the read-only capture.

    Returns {glass name: (frames, params)}, the params taken from the Recipe the run used.
    """
    from oil_tracker.adapters.vision.foam_material_identity import foam_material_identity_tolerance
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from tests.diagnostics import s11_layer_bottom_topology_2 as lbt2

    recipes, run = [], AnalysisPipeline.run

    def keep_recipe(self, recipe, session, *args, **kwargs):
        recipes.append(recipe)
        return run(self, recipe, session, *args, **kwargs)

    with TemporaryDirectory(dir=work) as scratch, captured() as frames, \
            patch.object(AnalysisPipeline, 'run', keep_recipe):
        result, _, _ = lbt2._pipeline(sample, root, scratch, trial=False)
    glasses = {glass.id: glass for glass in recipes[0].glasses}
    by_glass = {}
    for glass_result in result.glass_results:
        rows = []
        for sample_row in glass_result.samples:
            frame = dict(frames[(glass_result.glass_id, sample_row.frame_index)])
            frame['ordinary_y'] = _float(sample_row.raw_oil_air_level_y)
            rows.append(frame)
        glass = glasses[glass_result.glass_id]
        by_glass[glass_result.glass_name] = (rows, dict(tolerance=foam_material_identity_tolerance(glass),
                                                        max_jump=float(glass.detector_settings.temporal_max_jump_px)))
    return by_glass


def bundle_frames(bundle, glass_name):
    """Frames for one Glass from a saved bundle: the debug trace's detector candidates and the tracking rows.

    Needs a FULL debug trace (a record per analysed frame). Parameters come from the bundle's Recipe snapshot.
    Returns (frames, params, info); info carries the run ID and the Glass's C1 (5 % of 2 x radius_y).
    """
    import csv

    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
    from oil_tracker.adapters.vision.foam_material_identity import foam_material_identity_tolerance

    recipe = JsonRecipeRepository().load(bundle / 'recipe_snapshot.oilrecipe')
    (glass,) = [item for item in recipe.glasses if item.name == glass_name]
    with (bundle / 'tracking_data.csv').open(encoding='utf-8-sig', newline='') as handle:
        tracking = {int(row['frame_index']): row for row in csv.DictReader(handle) if row['glass_id'] == str(glass.id)}
    records, run_ids = {}, set()
    with (bundle / 'debug' / 'debug_trace.jsonl').open(encoding='utf-8') as handle:
        for line in handle:
            record = json.loads(line)
            run_ids.add(record.get('run_id'))
            if record.get('glass_id') == str(glass.id):
                records[int(record['frame_index'])] = record
    missing = sorted(set(tracking) - set(records))
    if missing:
        raise SystemExit(f'STOP: {len(missing)} tracking rows have no debug record (first {missing[:5]}); FULL debug is required')
    frames = []
    for index in sorted(tracking):
        candidates = records[index]['candidates']
        value = tracking[index]['raw_oil_air_level_y']
        frames.append(dict(
            time=float(tracking[index]['timestamp_sec']), frame=index,
            ordinary_y=float(value) if value not in ('', None) else None,
            foam=[], foam_full=[_foam_item(c['canonical_y'], c['features']) for c in candidates if c['kind'] == 'foam_front'],
            oil_rows=sorted({float(c['canonical_y']) for c in candidates if c['kind'] == 'oil_air'
                             and float(c['features'].get('sequence_eligible', 0.0)) >= 0.5})))
    params = dict(tolerance=foam_material_identity_tolerance(glass),
                  max_jump=float(glass.detector_settings.temporal_max_jump_px))
    info = dict(run_ids=sorted(map(str, run_ids)), glass_id=str(glass.id),
                c1_px=round(0.05 * 2.0 * float(glass.geometry.ellipse.radius_y), 2))
    return frames, params, info


BUNDLE_FIELDS = ('time', 'frame', 'ordinary_y', 'foam_full', 'oil_rows')


def bundle_check(root, work, sample='sample4'):
    """One FULL-debug analysis through the headless bundle path: does ``bundle_frames`` read what the run saw?"""
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
    from oil_tracker.adapters.vision.foam_material_identity import foam_material_identity_tolerance
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.session import DebugTraceLevel
    from tests.diagnostics.s11_report_observability_replay import QUALIFICATION_WINDOWS, _session

    with TemporaryDirectory(dir=work) as scratch:
        recipe, session = _session(sample, root / 'sample' / f'{sample}.mp4', Path(scratch),
                                   *QUALIFICATION_WINDOWS[sample], run_label='FLB-2', run_note='bundle check')
        session.debug_trace_level = DebugTraceLevel.FULL
        with captured() as live:
            result = AnalysisPipeline(OpenCvVideoReader, OpenCvPhaseDetector(), RecipeValidationService(),
                                      JsonlDebugTraceWriterFactory(Path(scratch))).run(recipe, session)
        if result.errors:
            raise SystemExit(f'STOP: analysis errors {result.errors}')
        bundle = OutputBundleStore().write_bundle(result, recipe, session, Path(scratch))
        (glass,) = [item for item in recipe.glasses if item.enabled]
        (glass_result,) = result.glass_results
        direct = [dict(live[(glass.id, row.frame_index)], ordinary_y=_float(row.raw_oil_air_level_y))
                  for row in glass_result.samples]
        direct_params = dict(tolerance=foam_material_identity_tolerance(glass),
                             max_jump=float(glass.detector_settings.temporal_max_jump_px))
        read, params, _info = bundle_frames(bundle, glass.name)
        main(['--work', str(work), '--bundle', str(bundle), '--glass-name', glass.name,
              '--start', '38', '--end', '56'])  # the Windows entry on the same bundle
    differences = [dict(frame=a['frame'], field=key, direct=a[key], bundle=b[key])
                   for a, b in zip(direct, read, strict=True) for key in BUNDLE_FIELDS if a[key] != b[key]]
    rule_direct, rule_bundle = follow2(direct, **direct_params), follow2(read, **params)
    return dict(sample=sample, frames=len(read), params=params, params_equal=params == direct_params,
                field_differences=differences, follow2_equal=rule_direct == rule_bundle,
                follow2_active=sum(row['state'] != NONE for row in rule_bundle),
                layer_witness_frames=sum(layer_witness(frame) is not None for frame in read))


def main(argv=None):
    from tests.diagnostics import s11_role_consumer_intervention as rci

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--design-readout', action='store_true', help='FLB-2 design readout only')
    parser.add_argument('--bundle-check', action='store_true', help='FLB-2 bundle reader against one live run')
    parser.add_argument('--bundle', type=Path, help='FLB-2 on a saved FULL-debug bundle (no detector run)')
    parser.add_argument('--glass-name')
    parser.add_argument('--start', type=float, default=0.0)
    parser.add_argument('--end', type=float, default=1e9)
    args = parser.parse_args(argv)
    root = rci.ROOT
    if args.bundle_check:
        check = bundle_check(root, args.work)
        (args.work / 'flb2-bundle-check.json').write_text(json.dumps(check, indent=1) + '\n', encoding='utf-8')
        print(json.dumps({key: value for key, value in check.items() if key != 'field_differences'}
                         | dict(field_differences=len(check['field_differences']))))
        return
    if args.bundle:
        frames, params, info = bundle_frames(args.bundle, args.glass_name)
        rows = follow2(frames, **params)
        changed = [row for row in rows if row['y'] != row['ordinary_y']]
        result = dict(rule='FLB-2', bundle=str(args.bundle), glass=args.glass_name, params=params, info=info,
                      frames=len(rows), layer_witness_frames=sum(layer_witness(f) is not None for f in frames),
                      active_frames=sum(row['state'] != NONE for row in rows), changed=changed, rows=rows)
        out = args.work / f"flb2-bundle-{info['glass_id']}.json"
        out.write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
        print(f"run_id {','.join(info['run_ids'])} | glass {args.glass_name} | tolerance {params['tolerance']} | "
              f"max_jump {params['max_jump']} | C1 {info['c1_px']}")
        print(f"frames {result['frames']} | layer witness {result['layer_witness_frames']} | "
              f"active {result['active_frames']} | changed {len(changed)}")
        print('time | frame | ordinary | FLB-2 | state | reason | bottom')
        print('-- changed rows --')
        for row in changed:
            print(f"{row['time']} | {row['frame']} | {row['ordinary_y']} | {row['y']} | {row['state']} | "
                  f"{row['reason']} | {row['bottom']}")
        print(f"-- all rows {args.start}-{args.end} s --")
        for row in rows:
            if args.start <= row['time'] <= args.end:
                print(f"{row['time']} | {row['frame']} | {row['ordinary_y']} | {row['y']} | {row['state']} | "
                      f"{row['reason']} | {row['bottom']}")
        print(f"json {out.name} sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}")
        return
    if args.design_readout:
        readout = design_readout(root, args.work)
        (args.work / 'flb2-design-readout.json').write_text(json.dumps(readout, indent=1) + '\n', encoding='utf-8')
        print(json.dumps({key: len(rows) for key, rows in readout.items()}))
        return
    frames, params = sample4_frames(root)
    rows = follow(frames, **params)
    lbt2_run = root / 'sample/output/s11-layer-bottom-topology-2-20261022-001/evidence/population/comparison.json'
    controls = json.loads(lbt2_run.read_text(encoding='utf-8'))['preflight']['controls']
    refs = references(controls, json.loads((root / REVIEW014).read_text(encoding='utf-8')))
    table, counts = score(rows, refs)
    changed = [row for row in rows if row['y'] != row['ordinary_y']]
    result = dict(protocol=str(PROTOCOL), sample4=dict(params=params, scored=table, counts=counts,
                                                       changed=changed, rows=rows))
    descriptive = {}
    for sample in CONTROLS:
        descriptive[sample] = {}
        for name, (glass_rows, glass_params) in control_frames(sample, root, args.work).items():
            out = follow(glass_rows, **glass_params)
            descriptive[sample][name] = dict(
                params=glass_params, frames=len(out), witness_frames=sum(witness(f) is not None for f in glass_rows),
                active_frames=sum(row['state'] != NONE for row in out),
                changed=[row for row in out if row['y'] != row['ordinary_y']])
    result['controls'] = descriptive
    (args.work / 'flb1-result.json').write_text(json.dumps(result, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(dict(counts=counts, changed=[(r['time'], r['ordinary_y'], r['y'], r['reason']) for r in changed],
                          controls={s: {g: dict(witness=v['witness_frames'], active=v['active_frames'],
                                                changed=len(v['changed'])) for g, v in d.items()}
                                    for s, d in descriptive.items()}), indent=1))


if __name__ == '__main__':
    main()
