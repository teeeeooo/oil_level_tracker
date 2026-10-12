"""Prepare frozen saved rasters through the existing S1 owner, without an encoder.

Run in the existing application environment; probe.py uses only the isolated ML
environment. No production entry point imports either diagnostic.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def prepare(out):
    pre = read(HERE / 'preflight.json')
    pins = {**pre['inputs'], **pre['original_capture_pins'], **pre['production_source_pins']}
    for rel, digest in pins.items():
        assert sha(ROOT / rel) == digest, rel
    old_dir = HERE.parent / '2026-10-11-p2-shared-support'
    source = read(old_dir / 'preflight.json')
    old = module('cr1_saved_raster_owner', old_dir / 'run.py')
    inventory = module('cr1_inventory_owner', HERE.parent / '2026-10-12-p2-row-distributions/candidates.py')
    queries, captures = inventory.inventory(source)
    frozen = read(HERE.parent / '2026-10-12-p2-row-distributions/candidates-preflight.json')
    assert queries == frozen['queries'] and captures == frozen['captures']
    images = old.load_images(source)
    import numpy as np
    mask_path = out / 'visibility.npz'
    if mask_path.exists() or (out / 'prepared.json').exists():
        raise FileExistsError('prepared output already exists')
    np.savez_compressed(mask_path, **{str(f): value[1] for f, value in images.items()})
    value = dict(
        preflight_sha256=sha(HERE / 'preflight.json'),
        mask_sha256=sha(mask_path), masks_file=mask_path.name,
        images={f: files['original_roi'] for f, files in source['images'].items()},
        queries=queries, captures=captures, checked_pins=len(pins),
        unchanged_preprocessing_canny_and_saved_glare='PASS',
        original_frame_times={str(q['frame']): old.read(ROOT / source['images'][str(q['frame'])]['capture'])['current']['time_sec']
                              for q in queries if 'candidate_index' in q},
        video_decode=False, preparation_runtime=dict(python=sys.version, numpy=np.__version__),
    )
    (out / 'prepared.json').write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(queries=len(queries), images=len(images), checked_pins=len(pins))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    prepare(parser.parse_args().out)
