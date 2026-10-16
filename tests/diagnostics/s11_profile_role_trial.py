"""PWC-1 frozen pixel preferences and completed consumer experiments."""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import asdict
import gzip
import json
from pathlib import Path
import subprocess
import time
import cv2
import numpy as np
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.adapters.reporting.csv_exporter import CsvExporter
from oil_tracker.application.services.report_presentation import build_report_presentation
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from tests.diagnostics import s11_role_consumer_intervention as rci
from tests.diagnostics.s11_profile_role_witness import observe, decision_controls, ARMS
from tests.diagnostics.s11_role_source_context import VIDEO_SHA
from tests.diagnostics.s11_corroboration_geometry_screen import PREPARED

MODES = ('negative_member_veto', 'positive_authority_only', 'negative_veto_positive_authority')


def save_gzip(path: Path, obj: object) -> None:
    with path.open('xb') as stream:
        stream.write(gzip.compress(json.dumps(rci.normalize(obj), allow_nan=False,
                                              sort_keys=True).encode(), mtime=0))


def measure(root: Path, raw: list[dict], glass, roster: dict) -> tuple[list, list, dict]:
    prepared = json.loads((root / PREPARED).read_text())
    frames, measurements, pins = {}, [], {}
    video = root / 'sample/sample4.mp4'
    rci.require(rci.digest(video) == VIDEO_SHA, 'video hash changed')
    pins[str(video.relative_to(root))] = VIDEO_SHA
    shared_checks = []
    with OpenCvVideoReader(video) as reader:
        for detection in raw:
            frame, index, timestamp = reader.read_at(detection['time_sec'])
            rci.require(index == detection['frame_index'] and
                        abs(timestamp - detection['time_sec']) < 1e-6, 'frame/time mismatch')
            bundle = build_mask_bundle(frame, glass)
            raster = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
            gray = raster.gray
            visible = (bundle.effective_mask > 0) & (raster.glare_mask == 0)
            fid = f'sample4-f{index}'
            frame_binding = {'frame': index, 'time_sec': timestamp, 'origin': list(bundle.crop_origin),
                             'gray_sha256': __import__('hashlib').sha256(gray.tobytes()).hexdigest(),
                             'visible_sha256': __import__('hashlib').sha256(visible.tobytes()).hexdigest()}
            frames[fid] = frame_binding
            if fid in prepared['frames']:
                spec = prepared['frames'][fid]
                for item in ('rgb', 'visibility'):
                    rel, sha = spec[item]['path'], spec[item]['sha256']
                    rci.require(rci.digest(root / rel) == sha, 'prepared input hash changed')
                    pins[rel] = sha
                old = cv2.cvtColor(cv2.imread(str(root/spec['rgb']['path'])), cv2.COLOR_BGR2GRAY)
                with np.load(root/spec['visibility']['path'], allow_pickle=False) as archive:
                    old_mask = archive[spec['mask_key']]
                    rci.require(np.array_equal(old_mask, visible), 'saved/current mask differs')
                rci.require(np.array_equal(old, gray), 'saved/current raster differs')
                rci.require(spec['origin'] == list(bundle.crop_origin), 'saved origin differs')
                shared_checks.append(fid)
            for i, candidate in enumerate(detection['candidates']):
                if candidate['kind'] == 'oil_air':
                    measurements.append(observe(gray, visible, origin=bundle.crop_origin,
                        frame=index, index=i, source=candidate['source'], y=candidate['y']))
    by_key = {(m['frame'], m['index']): m for m in measurements}
    public_spec = prepared['frames']['public-f1499']
    for item in ('rgb', 'visibility'):
        rel, sha = public_spec[item]['path'], public_spec[item]['sha256']
        rci.require(rci.digest(root/rel) == sha, 'public input hash changed')
        pins[rel] = sha
    with np.load(root/public_spec['rgb']['path'], allow_pickle=False) as archive:
        public_gray = cv2.cvtColor(archive['original_roi'], cv2.COLOR_BGR2GRAY)
        public_visible = (archive['effective_mask'] > 0) & (archive['glare_mask'] == 0)
    screened = []
    for unit in roster['units']:
        if 'raster_witness' not in unit:
            continue
        query = unit['query']
        if unit['group'] == 'sample4':
            value = by_key[(query['frame'], query['candidate_index'])]
        else:
            rci.require(unit['raw_frame_id'] == 'public-f1499', 'unexpected source')
            value = observe(public_gray, public_visible, origin=tuple(public_spec['origin']),
                frame=query['frame'], index=query['candidate_index'],
                source=query['source'], y=query['source_xy'][1])
        rci.require((value['source'], value['y']) == (query['source'], query['source_xy'][1]),
                    'roster source/index/Y mismatch')
        screened.append({k: unit[k] for k in ('id', 'raw_frame_id', 'group', 'review_label', 'label_basis')}
                        | {'measurement': value})
    rci.require(len(screened) == 175 and len(shared_checks) == 7, 'population drift')
    return measurements, screened, {'pins': pins, 'frames': frames, 'shared_equal': shared_checks}


def run(root: Path, output: Path) -> dict:
    rci.require(not any(output.iterdir()), 'empty managed work directory required')
    sources = {str(p.relative_to(root)): rci.digest(p) for p in (root/'src').rglob('*.py')}
    pins = dict(rci.PINS)
    pins[str(rci.BUNDLE/'recipe_snapshot.oilrecipe')] = rci.digest(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    pins[PREPARED] = rci.digest(root/PREPARED)
    for rel, sha in pins.items():
        rci.require(rci.digest(root/rel) == sha, 'frozen input mismatch: '+rel)
    raw = json.loads((root/rci.SAVED/'raw.json').read_text())
    saved = json.loads((root/rci.SAVED/'completed.json').read_text())
    roster = json.loads(gzip.decompress((root/rci.ROSTER).read_bytes()))
    rci.require(pins[PREPARED] == roster['inputs'][PREPARED], 'prepared source manifest drift')
    truth = rci.bind_controls(raw, roster['units'])
    recipe = JsonRecipeRepository().load(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    recipe_before = recipe.to_dict()
    started = time.perf_counter()
    measurements, screened, source_binding = measure(root, raw, recipe.glasses[0], roster)
    pins.update(source_binding['pins'])
    measurement_time = time.perf_counter() - started
    preflight = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                 'inputs': pins, 'source_hashes': sources, 'controls': truth,
                 'source_binding': source_binding, 'measurement_seconds': measurement_time,
                 'scope': 'PIXEL_MODEL_PREFERENCES_NOT_QUALIFIED_PHYSICAL_ROLES',
                 'review_labels_used_for_runtime_decisions': False,
                 'all_optional_switches': 'OFF', 'windows': 'NOT_RUN'}
    rci.write_json(output/'preflight.json', preflight)
    save_gzip(output/'measurements.json.gz', {'preflight': preflight,
              'sample4': measurements, 'screened': screened})
    from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
    renderer = GraphRenderer()
    conditions = [('baseline', 'baseline', [])]
    for arm in ARMS:
        pixel_controls = decision_controls(measurements, arm)
        conditions.extend((f'{arm}_{mode}', mode, pixel_controls) for mode in MODES)
    results, summaries = [], []
    for name, mode, controls in conditions:
        readout, complete, result = rci.replay(raw, controls, recipe.glasses[0], mode,
            analysis_id='DIAGNOSTIC_PIXEL_PROFILE', marker='DIAGNOSTIC_PIXEL_PROFILE')
        if name == 'baseline':
            rci.require(complete == saved, 'full baseline mismatch')
        readout['variant'] = name
        for row in readout['rows']:
            row['review_status'] = rci.control_status(row, truth)
        directory = output/name
        directory.mkdir()
        CsvExporter().export(result, directory/'tracking.csv', directory/'events.csv')
        presentation = build_report_presentation(result, recipe)
        renderer.render(result, directory/'graphs', recipe, presentation=presentation)
        results.append(readout)
        summary = rci.summarize(readout, results[0], truth,
                               result.glass_results[0].events, presentation)
        summary['valid_oil'] = sum(r['oil_is_valid'] for r in readout['rows'])
        summary['valid_foam'] = sum(r['foam_is_valid'] for r in readout['rows'])
        summaries.append(summary)
        print(json.dumps({k: summary[k] for k in ('variant', 'numeric_oil', 'numeric_foam',
                          'valid_oil', 'valid_foam', 'review_status_counts', 'runtime_sec')}), flush=True)
    screen_summary = {arm: {label: dict(Counter(u['measurement']['preferences'][arm]
                     for u in screened if u['review_label'] == label))
                     for label in ('ACCEPTED', 'OPPOSED', 'UNASSESSED')} for arm in ARMS}
    for rel, sha in {**pins, **sources}.items():
        rci.require(rci.digest(root/rel) == sha, 'source/input mutation: '+rel)
    rci.require(recipe.to_dict() == recipe_before, 'Recipe mutation')
    comparison = {'schema': 's11-profile-witness-consumer-v1', 'preflight': preflight,
                  'variants': summaries, 'screen_summary': screen_summary,
                  'baseline_complete_equal': True, 'production_changed': False,
                  'report_comprehension': 'NOT_HUMAN_EVALUATED', 'windows': 'NOT_RUN'}
    rci.write_json(output/'comparison.json', comparison)
    save_gzip(output/'readout.json.gz', {'preflight': preflight, 'variants': results})
    headings = ''.join(f'<h2>{s["variant"]}</h2><img src="{s["variant"]}/graphs/sample4_sight_glass_detail.png">'
                       for s in summaries)
    (output/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>PWC-1 diagnostic</title>'
        '<style>body{font:16px sans-serif;max-width:1400px;margin:24px auto}img{width:100%}</style>'
        '<h1>PWC-1 — pixel-profile experiment, NOT accepted detector behavior</h1>'
        '<p>Runtime decisions are image-model preferences, not reviewed truth. Unknown replacement '
        'winners remain unassessed. No independent human report acceptance.</p>'+headings, encoding='utf-8')
    print(json.dumps({'screen_summary': screen_summary, 'measurement_seconds': measurement_time}), flush=True)
    return comparison


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.output.resolve())
