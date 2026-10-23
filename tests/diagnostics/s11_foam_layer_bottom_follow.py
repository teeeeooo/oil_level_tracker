"""FLB-1: desk emulation of "Oil follows the dense-Foam layer bottom, then hands off explicitly".

Protocol: docs/50-diagnostics/s11/2026-10-23-foam-layer-bottom-follow.md (frozen before any run).

The emulation reads, per frame, the detector's own Foam front candidates (eligibility and
``material_component_bottom_y``), the same-frame eligible Oil candidate rows and the ordinary
output. It changes no detector code: it only recomputes which existing Oil candidate row a
follow rule would publish. sample4 replays the saved P5 capture (the LBT-2 ordinary arm); the
descriptive controls run the ordinary analysis entry with a read-only capture of each frame.

Usage (repository root, inside a managed run):
    PYTHONPATH=src python -m tests.diagnostics.s11_foam_layer_bottom_follow --work <work>
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
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
                   oil_rows=sorted({float(c['y']) for c in row['candidates'] if c['kind'] == 'oil_air'
                                    and float(c['features'].get('sequence_eligible', 0.0)) >= 0.5}))
              for row, out in zip(raw, record['rows'], strict=True)]
    glass = recipe.glasses[0]
    return frames, dict(tolerance=foam_material_identity_tolerance(glass),
                        max_jump=float(glass.detector_settings.temporal_max_jump_px))


def _float(value):
    return None if value is None else float(value)


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


def main(argv=None):
    from tests.diagnostics import s11_role_consumer_intervention as rci

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args(argv)
    root = rci.ROOT
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
