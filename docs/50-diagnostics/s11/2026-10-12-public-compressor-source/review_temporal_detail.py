"""Source-only consecutive native crops for a frozen observability review."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
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
    plan_path = base / 'temporal-detail-preflight.json'
    plan = json.loads(plan_path.read_text())
    assert all(sha(root / p) == h for p, h in plan['inputs'].items())
    source = root / plan['source']['local_path']
    assert sha(source) == plan['source']['sha256']
    out.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(root / 'src'), str(root)]
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from tests.diagnostics.s11_corpus_access import require_corpus_access

    access = require_corpus_access(('public_miso_mHOS1-1ck60',))
    started = time.monotonic()
    crops, frames = [], []
    x0, y0, x1, y1 = plan['crop_source_xyxy']
    indices = range(plan['start_frame'], plan['end_frame_inclusive'] + 1)
    assert len(indices) == plan['maximum_decode_count']
    with OpenCvVideoReader(source) as reader:
        for i, expected_index in enumerate(indices):
            frame, index, actual = reader.read_next() if i else reader.read_at(plan['seek_second'])
            assert index == expected_index, (index, expected_index)
            assert frame.shape == (720, 1280, 3)
            frame_hash = hashlib.sha256(frame.tobytes()).hexdigest()
            if index == plan['anchor']['frame_index']:
                assert frame_hash == plan['anchor']['bgr_sha256']
                assert np.array_equal(frame, cv2.imread(str(base / 'native-at-50.png')))
            crop = frame[y0:y1, x0:x1].copy()
            crops.append(crop)
            frames.append({'frame_index': index, 'timestamp_sec': actual,
                           'full_bgr_sha256': frame_hash,
                           'crop_bgr_sha256': hashlib.sha256(crop.tobytes()).hexdigest()})
    arrays = np.stack(crops)
    np.savez_compressed(out / 'native-crops.npz', bgr=arrays)
    # Every source crop is retained. Display the five offsets chosen in advance.
    tiles = []
    for i in plan['display_offsets']:
        enlarged = np.repeat(np.repeat(arrays[i], 2, axis=0), 2, axis=1)
        tile = np.zeros((enlarged.shape[0] + 30, enlarged.shape[1], 3), np.uint8)
        tile[30:] = enlarged
        cv2.putText(tile, f"f{frames[i]['frame_index']} / {frames[i]['timestamp_sec']:.6f}s",
                    (8, 21), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)
        tiles.append(tile)
    sheet = np.concatenate(tiles, axis=1)
    assert cv2.imwrite(str(out / 'native-detail-sheet.png'), sheet)
    elapsed = time.monotonic() - started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == 'darwin' else rss * 1024
    assert elapsed <= plan['resource']['seconds_limit']
    assert rss_bytes <= plan['resource']['rss_bytes_limit']
    assert sha(source) == plan['source']['sha256']
    assert all(sha(root / p) == h for p, h in plan['inputs'].items())
    with np.load(out / 'native-crops.npz', allow_pickle=False) as saved:
        assert np.array_equal(arrays, saved['bgr'])
    result = {
        'schema': 's11-public-source-temporal-detail-readout-v1',
        'preflight_sha256': sha(plan_path), 'runner_sha256': sha(__file__),
        'corpus_access': access, 'crop_source_xyxy': plan['crop_source_xyxy'],
        'frames': frames, 'array_shape': list(arrays.shape),
        'outputs': {p.name: sha(p) for p in sorted(out.iterdir())},
        'verification': {'consecutive_frames': len(frames), 'anchor_pixels_equal': True,
                         'crop_roundtrip_equal': True, 'source_and_input_pins_preserved': True},
        'resources': {'decode_capture_seconds': elapsed, 'peak_rss_bytes': rss_bytes},
        'physical_event_labels': 'NOT_SUPPLIED', 'detector_runs': 0,
    }
    (out / 'readout.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'verification': result['verification'], 'resources': result['resources']}))


if __name__ == '__main__':
    main()
