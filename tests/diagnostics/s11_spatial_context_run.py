"""Read-only source-frame adapter for the ordered strip measurement. No detector run."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import html
import math
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ''):
    sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]

import cv2
import numpy as np
from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader
from oil_tracker.adapters.vision import geometry_masks, preprocessing, row_features, oil_interface_diagnostics
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_review_records as records
from tests.diagnostics import s11_spatial_context_probe as probe

SCHEMA = 's11-o2-spatial-context-v1'


def raster_identity(array):
    return {'shape': list(array.shape), 'dtype': str(array.dtype),
            'sha256': hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()}


def decode_exact(reader, frame):
    """Use existing reader; bounded forward decode may reach exact index, never nearest."""
    timestamp = o2.number(frame['timestamp_sec'], 'timestamp')
    o2.require(timestamp >= 0, 'negative timestamp')
    target = o2.integer(frame['frame_index'], 'frame index')
    image, index, actual = reader.read_at(timestamp)
    initial, advances = index, 0
    while index < target and target-index <= 120 and advances < 120:
        previous = index
        image, index, actual = reader.read_next()
        o2.require(index == previous+1, 'decoder did not advance one frame')
        advances += 1
    o2.require(index == target, f'exact frame mismatch: expected {target}, decoded {index}; no substitution')
    o2.number(actual, 'decoded timestamp')
    return image, {'requested_frame_index': target, 'decoded_frame_index': index,
                   'requested_timestamp_sec': timestamp, 'decoded_timestamp_sec': actual,
                   'initial_frame_index': initial, 'forward_decodes': advances,
                   'identity_basis': 'source bytes + backend-reported frame index; no historical pixel hash exists'}


def baseline_check(gray, effective, glare, witness):
    """Recompute existing band gray/support with its arithmetic owner, not scores.

    A tolerance of 1e-10 covers floating summation only (gray units 0..1).
    Differences remain explicit and prevent a claim that only extent changed.
    """
    visible = (effective > 0) & (glare == 0)
    glared = (effective > 0) & (glare > 0)
    empty_material = np.full(gray.shape, np.nan)
    cache, rows = {}, []
    ox = witness['crop_origin'][0]
    fields = ('available', 'valid_pixel_count', 'gray_mean', 'gray_std', 'glare_fraction')
    for candidate in witness['candidates']:
        for sector in candidate['sectors']:
            x0, x1 = sector['source_x_range']
            key = (x0, x1)
            if key not in cache:
                cache[key] = oil_interface_diagnostics._sector_profile(
                    gray, visible, empty_material, None, glared, x0-ox, x1-ox)[2]
            for center in sector['centers']:
                for scale in center['scales']:
                    for band in scale['bands']:
                        new = oil_interface_diagnostics._band(cache[key], *band['local_y_range'], gray.shape[0], x1-x0)
                        mismatch = []
                        for field in fields:
                            a, b = band[field], new[field]
                            equal = a == b
                            if a is not None and b is not None and field in ('gray_mean', 'gray_std', 'glare_fraction'):
                                equal = math.isclose(a, b, rel_tol=0, abs_tol=1e-10)
                            if not equal:
                                mismatch.append(field)
                        rows.append({'candidate_input_index': candidate['candidate_input_index'],
                                     'source_x_range': [x0, x1], 'source_y': center['source_y'],
                                     'geometry_basis': center['role'], 'band_width_px': scale['band_width_px'],
                                     'band': band['name'], 'source_y_range': [y+witness['crop_origin'][1] for y in band['local_y_range']],
                                     'original': {k: band[k] for k in fields}, 'reconstructed': {k: new[k] for k in fields},
                                     'mismatched_fields': mismatch})
    mismatches = sum(bool(r['mismatched_fields']) for r in rows)
    return {'band_count': len(rows), 'mismatched_band_count': mismatches,
            'status': 'MATCH' if rows and not mismatches else 'DIFFERENT' if rows else 'NOT_MEASURED',
            'float_absolute_tolerance': 1e-10, 'rows': rows,
            'scope': 'Only gray/support band fields; not historical pixel equality or classifier efficacy.'}


def render_profile(profile, points):
    """Deterministic numeric plot; gaps are never connected and no class is inferred."""
    start, stop = profile['source_y_start'], profile['source_y_stop_exclusive']
    height = stop-start
    elements = ['<svg xmlns="http://www.w3.org/2000/svg" width="540" height="820" viewBox="0 0 540 820">',
                '<rect width="540" height="820" fill="white"/>',
                '<text x="15" y="20">Raw gray 0..255 (horizontal); source Y downward</text>',
                f'<text x="15" y="40">X={profile["source_x_range"]}; Y=[{start},{stop}); gaps unavailable</text>']
    run = []
    def flush():
        if run:
            elements.append('<polyline fill="none" stroke="#246" stroke-width="1.5" points="'+' '.join(run)+'"/>')
            run.clear()
    for offset, mean in enumerate(profile['gray_mean']):
        if mean is None:
            flush()
        else:
            run.append(f'{40+mean*1.6:.3f},{65+offset/max(1,height-1)*700:.3f}')
    flush()
    for point in points:
        if point['profile_id'] == profile['profile_id']:
            y = 65+(point['source_y']-start)/max(1,height-1)*700
            label = html.escape(f"idx{point['candidate_input_index']} {point['geometry_basis']} Y={point['source_y']}")
            elements.append(f'<line x1="40" x2="448" y1="{y}" y2="{y}" stroke="#b66" opacity=".3"/>')
            elements.append(f'<text x="45" y="{y}" font-size="9">{label}</text>')
    elements.append('</svg>')
    return '\n'.join(elements)


def run(label_paths, output, *, bundle_path, video_path, expected_revisions):
    output, video_path = Path(output).resolve(), Path(video_path).resolve()
    paths = [Path(p).resolve() for p in label_paths]
    o2.require(not output.exists(), 'output directory already exists; choose a new name')
    o2.require(1 <= len(paths) <= 2 and len(set(paths)) == len(paths), 'one or two unique reviews required')
    o2.require(len(expected_revisions) == len(paths), 'one expected revision per review required')
    bundle = ResultBundleReader().read(bundle_path)
    protected = [Path(bundle.root).resolve(), *(p.parent for p in paths)]
    o2.require(all(output != p and p not in output.parents for p in protected), 'output must be outside bundle/review directories')
    snapshots = {}
    def snapshot(path):
        path = Path(path).resolve()
        digest = o2.sha256_file(path)
        o2.require(path not in snapshots or snapshots[path] == digest, 'input changed while loading')
        snapshots[path] = digest
        return digest
    def preserved():
        return [{'file_index': i, 'path': str(p), 'before_sha256': h,
                 'after_sha256': snapshot(p)} for i, (p, h) in enumerate(list(snapshots.items()))]
    for name in ('manifest', 'recipe_snapshot', 'session'):
        snapshot(bundle.files[name])
    o2.require(bundle.debug_trace_path and bundle.debug_index_path, 'indexed trace required')
    snapshot(Path(bundle.root)/bundle.debug_trace_path)
    snapshot(Path(bundle.root)/bundle.debug_index_path)
    bundle_identity = records._bundle_identity(bundle)
    video_sha = snapshot(video_path)
    glasses = {g.id: g for g in bundle.recipe.glasses}
    geometry = {g['id']: g['geometry'] for g in bundle.recipe.to_dict()['glasses']}
    bound, seen = [], set()
    for path, revision in zip(paths, expected_revisions, strict=True):
        o2.require(not Path(str(path)+'.lock').exists(), 'labels writer lock present')
        snapshot(path)
        labels = o2.read_json(path)
        o2.require(labels['schema_version'] == o2.LABEL_SCHEMA, 'v2 labels required')
        o2.require(len(labels.get('review_history', [])) == revision, 'label revision mismatch')
        o2.require(len(labels['cases']) == 1, 'exactly one existing frame per review required')
        for ref in labels['packets']:
            snapshot(path.parent/ref['path'])
        packets = o2.load_packets(labels, path.parent)
        o2.validate_labels(labels, packets)
        o2.require(all(c['partition'] == 'regression' for c in labels['cases']), 'regression inputs only')
        link_path = path.parent/'bundle-link.json'
        snapshot(link_path)
        link = records.load_link(link_path)
        o2.require(link['bundle_identity'] == bundle_identity, 'different bundle or changed bundle content')
        o2.require(link['source']['sha256'] == video_sha, 'different source video bytes')
        o2.require(set(link['packet_sha256s']) == set(packets), 'link/packet mismatch')
        frames = records._verify_packets(bundle, labels, path.parent)
        o2.require(len(frames) == 1, 'one packet frame per review required')
        frame = frames[0]
        key = (frame['glass_id'], frame['frame_index'])
        o2.require(key not in seen, 'duplicate frame/Glass')
        seen.add(key)
        scenes = [s for s in link['scenes'] if s['case_id'] == frame['case_id'] and s['glass_id'] == frame['glass_id']]
        o2.require(len(scenes) == 1, 'exact linked scene required')
        scene = scenes[0]
        expected = {'video_sha256': video_sha, 'frame_index': frame['frame_index'],
                    'coordinate_frame': {'width': bundle_identity['truth_identity']['source_width'],
                                         'height': bundle_identity['truth_identity']['source_height'],
                                         'coordinate_space': 'source_frame_y', 'positive_direction': 'down'},
                    'glass_geometry': geometry[frame['glass_id']]}
        o2.require(scene['scene_identity'] == expected and scene['scene_sha256'] == o2.fingerprint_json(expected), 'scene identity mismatch')
        bound.append((labels, frame, scene))
    cases, rasters = [], {}
    with OpenCvVideoReader(video_path) as reader:
        for number, (labels, frame, scene) in enumerate(bound):
            image, decoded = decode_exact(reader, frame)
            coord = scene['scene_identity']['coordinate_frame']
            o2.require(image.shape[:2] == (coord['height'], coord['width']), 'decoded source dimensions mismatch')
            o2.require(max(image.shape[:2]) <= probe.SPEC['max_dimension'], 'decoded frame exceeds resource bound')
            glass = glasses[frame['glass_id']]
            masks = geometry_masks.build_mask_bundle(image, glass)
            witness = frame['witness']
            o2.require(list(masks.crop_origin) == witness['crop_origin'] and
                       [masks.crop.shape[1], masks.crop.shape[0]] == witness['crop_size'], 'witness crop geometry mismatch')
            prep = preprocessing.preprocess(masks.crop, masks.effective_mask, glass.detector_settings)
            points = [{**p, 'candidate_input_index': c['candidate_input_index']}
                      for c in witness['candidates'] for p in o2.review_geometry(c)]
            measured = probe.measure_context(prep.gray, masks.effective_mask, prep.glare_mask, points, origin=masks.crop_origin)
            prefix = f'case-{number}'
            arrays = {'source': image, 'crop': masks.crop, 'gray': prep.gray,
                      'effective-mask': masks.effective_mask, 'glare-mask': prep.glare_mask}
            raster_rows = {}
            for name, array in arrays.items():
                filename = f'{prefix}-{name}.png'
                rasters[filename] = array
                raster_rows[name] = {'file': filename, **raster_identity(array)}
            cases.append({'case_id': frame['case_id'], 'frame_index': frame['frame_index'], 'glass_id': frame['glass_id'],
                          'revision': len(labels.get('review_history', [])), 'labels_sha256': o2.fingerprint_json(labels),
                          'scene_sha256': scene['scene_sha256'], 'decode': decoded,
                          'recipe_geometry': geometry[glass.id], 'settings': asdict(glass.detector_settings),
                          'rasters': raster_rows, 'measurement': measured,
                          'baseline_witness': witness,
                          'baseline_check': baseline_check(prep.gray, masks.effective_mask, prep.glare_mask, witness),
                          'baseline_note': 'Original O1 retained unchanged; reconstructed preprocessing is not asserted pixel-identical to historical decode.'})
    code = {str(Path(p).resolve().relative_to(ROOT)): o2.sha256_file(p) for p in
            (__file__, probe.__file__, records.__file__, o2.__file__, geometry_masks.__file__,
             preprocessing.__file__, row_features.__file__, oil_interface_diagnostics.__file__, sys.modules[OpenCvVideoReader.__module__].__file__)}
    artifact = {'spec': probe.SPEC, 'schema_version': SCHEMA, 'code': code}
    artifact['sha256'] = o2.fingerprint_json(artifact)
    report = {'schema_version': SCHEMA, 'artifact': artifact, 'status': 'EXPLORATORY_UNCALIBRATED',
              'decision': 'NOT_EVALUATED', 'auto_acceptance': False, 'production_decisions_emitted': False,
              'field_disposition': 'FIELD FAIL', 'numeric_localization': 'NOT_MEASURED',
              'runtime': {'python': platform.python_version(), 'platform': platform.platform(), 'opencv': cv2.__version__, 'numpy': np.__version__},
              'source_video_sha256': video_sha, 'cases': cases, 'input_preservation': preserved()}
    output.mkdir(parents=True, exist_ok=False)
    for name, array in rasters.items():
        ok, encoded = cv2.imencode('.png', array)
        o2.require(ok, 'PNG encoding failed')
        with (output/name).open('xb') as handle:
            handle.write(encoded.tobytes())
    lines = ['# S11 ordered spatial-context source probe', '',
             'EXPLORATORY_UNCALIBRATED; FIELD FAIL; NOT_EVALUATED. No classifier or detector run.',
             'Reconstructed raw-gray/effective/glare masks use the recorded recipe and current code.',
             'Full-height profiles preserve vertical order; horizontal averaging and masked gaps remain limitations.',
             'Human idx0/idx20 ambiguity remains unresolved. No threshold, relabeling or ranking gain is claimed.',
             f'Artifact: `{artifact["sha256"]}`', '']
    for number, case in enumerate(cases):
        m = case['measurement']
        lines += [f'## {case["case_id"]}', '',
                  f'Frame {case["frame_index"]}; Glass {case["glass_id"]}; revision {case["revision"]}.',
                  f'Points: {m["point_count"]}; exact X profiles: {len(m["profiles"])}; origin: {m["origin"]}; shape: {m["shape"]}.',
                  f'Decode: `{case["decode"]}`',
                  f'Baseline bands: {case["baseline_check"]["status"]}; mismatches {case["baseline_check"]["mismatched_band_count"]}/{case["baseline_check"]["band_count"]}.',
                  'If baseline differs, inspect reconstruction before attributing differences to wider sampling.', '',
                  '| Profile | X | Observed rows | Unavailable rows | Gray min/max |', '|---|---|---|---|---|']
        for p in m['profiles']:
            name = f'case-{number}-profile-{p["profile_id"]}.svg'
            (output/name).write_text(render_profile(p, m['points']), encoding='utf-8')
            vals = [v for v in p['gray_mean'] if v is not None]
            limits = f'{min(vals):.4f} / {max(vals):.4f}' if vals else 'unavailable'
            lines.append(f'| [{p["profile_id"]}]({name}) | {p["source_x_range"]} | {len(vals)} | {len(p["gray_mean"])-len(vals)} | {limits} |')
        lines += ['', '| Candidate | Basis | Source X | Source Y | Profile |', '|---|---|---|---|---|']
        for p in m['points']:
            lines.append(f'| {p["candidate_input_index"]} | {p["geometry_basis"]} | {p["source_x_range"]} | {p["source_y"]} | {p["profile_id"]} |')
    lines += ['', 'Return this generated summary, receipt/hash checks and revision/frame identities. Keep detailed JSON and images local.',
              'A COMPLETE receipt confirms measurement execution only; physical identity and historical pixel equality are not measured.', '']
    o2.write_new(output/'experiment.json', report)
    (output/'summary.md').write_text('\n'.join(lines), encoding='utf-8')
    preserved()
    o2.write_new(output/'complete.json', {'schema_version': SCHEMA, 'status': 'COMPLETE',
                 'artifact_sha256': artifact['sha256'],
                 'outputs': {p.name: o2.sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--labels', nargs='+', required=True)
    parser.add_argument('--expected-revisions', nargs='+', type=int, required=True)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--video', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run(args.labels, args.output, bundle_path=args.bundle, video_path=args.video, expected_revisions=args.expected_revisions)
    print('Measurement complete. Verify summary.md and complete.json; no identity decision was made.')


if __name__ == '__main__':
    main()
