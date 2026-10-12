"""Frozen current-frame baseline, using existing detector and capture owners."""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

import cv2
import numpy as np


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output.resolve()
    base = Path(__file__).resolve().parent
    preflight = base / 'current-frame-preflight.json'
    pre = json.loads(preflight.read_text())
    pins = {**pre['inputs'], **pre['source_files']}
    assert all(sha(root / p) == h for p, h in pins.items())
    out.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(root / 'src'), str(root)]
    from tests.diagnostics.s11_local_xy_replay import Recorder, save
    from tests.diagnostics.s11_corpus_access import require_corpus_access
    from oil_tracker.domain.geometry import EllipseGeometry, GlassGeometry
    from oil_tracker.domain.recipe import GlassInspectionConfig
    from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle

    access = require_corpus_access(('public_miso_mHOS1-1ck60',))
    source = cv2.imread(str(root / pre['source_frame']['path']))
    assert hashlib.sha256(source.tobytes()).hexdigest() == pre['source_frame']['bgr_sha256']
    cases = []
    started = time.monotonic()
    for variant in pre['variants']:
        name, scale = variant['id'], variant['scale']
        frame = source.copy() if scale == 1 else cv2.resize(
            source, tuple(variant['shape_wh']), interpolation=cv2.INTER_AREA)
        assert [frame.shape[1], frame.shape[0]] == variant['shape_wh']
        original = frame.copy()
        g = pre['native_geometry']
        point = lambda value: (value + .5) * scale - .5
        project = lambda value: (value + .5) / scale - .5
        ellipse = EllipseGeometry(*map(point, g['ellipse_center_xy']),
                                 *(value * scale for value in g['ellipse_radii_xy']))
        assert not ellipse.validate(frame.shape[1], frame.shape[0])
        geometry = GlassGeometry(ellipse=ellipse, zero_line_y=point(g['zero_line_y']),
                                 margin_ratio=g['margin_ratio'])
        glass = GlassInspectionConfig(id='public-source-current-frame',
                                      name='Public source current-frame diagnostic', geometry=geometry)
        config_before = deepcopy(asdict(glass))
        raw = []
        artifacts = None
        for debug in (False, True):
            detector = Recorder()
            detection, captured = detector.detect(frame, glass,
                pre['source_frame']['frame_index'], pre['source_frame']['timestamp_sec'], debug=debug)
            assert not detector.measurement_scope_manifest
            assert np.array_equal(frame, original) and asdict(glass) == config_before
            raw.append(detector.raw[0])
            save(out / f'{name}-{"full" if debug else "none"}.json', detector.raw[0])
            if debug:
                artifacts = captured
        assert artifacts is not None
        equal = raw[0] == raw[1]
        save(out / f'{name}-diagnostics.json', {
            'state': artifacts.state, 'profiles': artifacts.profiles,
            'candidate_rows': artifacts.candidate_rows})
        images = {key: np.asarray(value) for key, value in artifacts.images.items()}
        np.savez_compressed(out / f'{name}-images.npz', **images)
        bundle = build_mask_bundle(frame, glass)
        ox, oy = bundle.crop_origin
        column = int(round(ellipse.center_x - ox))
        visible = (bundle.effective_mask > 0) & (images['glare_mask'] == 0)
        observed = np.flatnonzero((images['canny'][:, column] > 0) & visible[:, column])
        cases.append({
            'variant': variant, 'geometry': asdict(geometry),
            'settings': asdict(glass.detector_settings), 'initial_state': glass.initial_state.value,
            'image_bgr_sha256': hashlib.sha256(frame.tobytes()).hexdigest(),
            'crop_origin': list(bundle.crop_origin), 'crop_shape': list(bundle.crop.shape),
            'none_full_complete_detection_equal': equal,
            'center_column': column, 'native_source_center_x': project(column + ox),
            'visible_center_edges': [
                {'local_y': int(y), 'frame_y': int(y + oy), 'native_source_y': project(y + oy)}
                for y in observed],
            'candidates': [
                {'input_index': i, 'kind': c['kind'].value, 'source': c['source'],
                 'frame_y': c['y'], 'native_source_y': project(c['y'])}
                for i, c in enumerate(raw[0]['candidates'])],
            'provisional': {key: raw[0][key] for key in (
                'raw_oil_air_level_y', 'raw_foam_front_y', 'oil_air_level_y', 'foam_front_y', 'flags')},
            'images': {key: {'shape': list(value.shape), 'dtype': str(value.dtype),
                            'array_sha256': hashlib.sha256(value.tobytes()).hexdigest()}
                       for key, value in images.items()},
        })
    elapsed = time.monotonic() - started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == 'darwin' else rss * 1024
    preserved = all(sha(root / p) == h for p, h in pins.items())
    report = {
        'schema': 's11-public-source-current-frame-readout-v1',
        'execution_head': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
        'preflight_sha256': sha(preflight), 'runner_sha256': sha(__file__),
        'corpus_access': access, 'detector_version': detector.version, 'cases': cases,
        'verification': {'pins_preserved': preserved, 'pin_count': len(pins),
                         'none_full_equal': all(c['none_full_complete_detection_equal'] for c in cases),
                         'detect_calls': 4, 'source_files_unchanged': len(pre['source_files']) if preserved else None},
        'resources': {'elapsed_sec': elapsed, 'peak_rss_bytes': rss_bytes,
                      'within_bounds': elapsed <= pre['resource']['seconds_limit']
                      and rss_bytes <= pre['resource']['rss_bytes_limit']},
        'versions': {'python': platform.python_version(), 'opencv': cv2.__version__, 'numpy': np.__version__},
        'outputs': {p.name: sha(p) for p in sorted(out.iterdir())},
        'physical_accuracy': 'NOT_EVALUATED', 'sequence_resolved': False,
    }
    save(out / 'current-frame-readout.json', report)
    print(json.dumps({'verification': report['verification'], 'resources': report['resources'],
                      'cases': [{k: c[k] for k in ('variant', 'crop_shape', 'provisional', 'candidates')}
                                for c in cases]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
