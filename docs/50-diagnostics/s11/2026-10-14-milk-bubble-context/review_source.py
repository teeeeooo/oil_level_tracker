"""One frozen, source-only milk context extraction; no event detector."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import time

import cv2
import numpy as np


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output.resolve()
    # Refuse before loading the video, including an existing empty directory.
    require(not out.exists(), "output already exists")
    plan_path = Path(__file__).with_name("plan.json")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    for path, digest in plan["inputs"].items():
        require(sha(root / path) == digest, f"input changed: {path}")
    source = root / plan["source"]["path"]
    require(sha(source) == plan["source"]["sha256"], "video changed")
    anchor = cv2.imread(str(root / plan["anchor"]["path"]))
    shape = tuple(plan["full_bgr_shape"])
    require(anchor is not None and anchor.shape == shape, "anchor shape")
    indices = list(range(plan["first_frame"], plan["last_frame_inclusive"] + 1))
    require(len(indices) == plan["maximum_decode_count"] == 25, "decode bound")
    require(plan["anchor"]["frame_index"] in indices, "anchor outside range")
    x0, y0, x1, y1 = plan["crop_source_xyxy"]
    require(0 <= x0 < x1 <= shape[1] and 0 <= y0 < y1 <= shape[0], "crop bounds")
    h, w = y1 - y0, x1 - x0
    atlas = np.zeros((5 * h, 5 * w, 3), dtype=np.uint8)
    sys.path[:0] = [str(root / "src"), str(root)]
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from tests.diagnostics.s11_corpus_access import require_corpus_access

    access = require_corpus_access((plan["source"]["corpus_id"],))
    started = time.monotonic()
    frames = []
    anchor_verified = False
    with OpenCvVideoReader(source) as reader:
        for offset, expected in enumerate(indices):
            frame, index, timestamp = (
                reader.read_next() if offset else reader.read_at(plan["seek_second"])
            )
            require(index == expected, f"wrong frame: {index} != {expected}")
            require(frame.shape == shape and frame.dtype == np.uint8, "frame representation")
            expected_time = index * plan["fps_denominator"] / plan["fps_numerator"]
            require(abs(timestamp - expected_time) <= 1e-6, "unexpected timestamp")
            if index == plan["anchor"]["frame_index"]:
                require(np.array_equal(frame, anchor), "decoded anchor differs from saved pixels")
                anchor_verified = True
            crop = frame[y0:y1, x0:x1]
            row, col = divmod(offset, 5)
            atlas[row * h:(row + 1) * h, col * w:(col + 1) * w] = crop
            frames.append({
                "frame_index": index, "timestamp_sec": timestamp,
                "full_bgr_sha256": hashlib.sha256(frame.tobytes()).hexdigest(),
                "crop_bgr_sha256": hashlib.sha256(crop.tobytes()).hexdigest(),
                "atlas_xyxy": [col * w, row * h, (col + 1) * w, (row + 1) * h],
            })
    require(anchor_verified, "anchor never verified")
    out.mkdir(parents=True, exist_ok=False)
    atlas_path = out / "native-atlas.png"
    require(cv2.imwrite(str(atlas_path), atlas), "PNG write failed")
    saved = cv2.imread(str(atlas_path))
    require(np.array_equal(saved, atlas), "PNG roundtrip differs")
    for item in frames:
        a, b, c, d = item["atlas_xyxy"]
        digest = hashlib.sha256(saved[b:d, a:c].tobytes()).hexdigest()
        require(digest == item["crop_bgr_sha256"], "atlas tile differs")
    for path, digest in plan["inputs"].items():
        require(sha(root / path) == digest, f"input changed during extraction: {path}")
    require(sha(source) == plan["source"]["sha256"], "video changed during extraction")
    elapsed = time.monotonic() - started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == "darwin" else rss * 1024
    require(elapsed <= plan["resource"]["seconds_limit"], "time budget exceeded")
    require(rss_bytes <= plan["resource"]["rss_bytes_limit"], "memory budget exceeded")
    require(atlas_path.stat().st_size <= plan["resource"]["retained_bytes_limit"], "size budget exceeded")
    readout = {
        "schema": "s11-milk-bubble-context-readout-v1",
        "plan_sha256": sha(plan_path), "runner_sha256": sha(Path(__file__)),
        "corpus_access": access, "crop_source_xyxy": plan["crop_source_xyxy"],
        "frames": frames, "atlas_bgr_shape": list(atlas.shape),
        "outputs": {"native-atlas.png": sha(atlas_path)},
        "verification": {"consecutive_frames": len(frames), "anchor_pixels_equal": True,
                         "all_tiles_roundtrip_equal": True, "source_and_inputs_preserved": True},
        "runtime": {"python": platform.python_version(), "opencv": cv2.__version__,
                    "numpy": np.__version__, "platform": platform.platform()},
        "resources": {"elapsed_seconds": elapsed, "peak_rss_bytes": rss_bytes},
        "physical_event_labels": "NOT_SUPPLIED", "detector_runs": 0, "model_runs": 0,
    }
    (out / "readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require(sum(p.stat().st_size for p in out.iterdir()) <= plan["resource"]["retained_bytes_limit"], "total size budget exceeded")
    print(json.dumps({"verification": readout["verification"], "resources": readout["resources"]}))


if __name__ == "__main__":
    main()
