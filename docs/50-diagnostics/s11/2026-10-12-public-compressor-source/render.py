"""Bounded source-quality review; no detector, Recipe or physical scoring."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import sys

import cv2
import numpy as np


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    base = Path(__file__).resolve().parent
    provenance = json.loads((base / "provenance.json").read_text())
    plan = json.loads((base / "native-review-plan.json").read_text())
    source = root / provenance["local_path"]
    assert digest(source) == provenance["sha256"]
    assert source.stat().st_size == provenance["bytes"]
    sys.path[:0] = [str(root / "src"), str(root)]
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from tests.diagnostics.s11_corpus_access import require_corpus_access

    access = require_corpus_access(("public_miso_mHOS1-1ck60",))
    # Refuse to replace any evidence, including partially produced outputs.
    args.output.mkdir(parents=True, exist_ok=False)
    frames, tiles = [], []
    with OpenCvVideoReader(source) as reader:
        metadata = asdict(reader.metadata)
        metadata["path"] = provenance["local_path"]
        for requested in plan["requested_seconds"]:
            frame, index, actual = reader.read_at(requested)
            assert frame.shape == (720, 1280, 3)
            row = {
                "requested_sec": requested, "frame_index": index,
                "actual_sec": actual, "shape": list(frame.shape),
                "bgr_sha256": hashlib.sha256(frame.tobytes()).hexdigest(),
            }
            if requested == plan["main_requested_second"]:
                target = args.output / "native-at-50.png"
                assert cv2.imwrite(str(target), frame)
                row["retained_image"] = target.name
                row["image_sha256"] = digest(target)
            frames.append(row)
            tile = np.zeros((390, 640, 3), dtype=np.uint8)
            tile[30:] = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_AREA)
            label = f"request {requested}s / f{index} / actual {actual:.6f}s"
            cv2.putText(tile, label, (8, 21), cv2.FONT_HERSHEY_SIMPLEX,
                        0.52, (255, 255, 255), 1, cv2.LINE_AA)
            tiles.append(tile)
    assert len(tiles) == 12
    sheet = np.concatenate([
        np.concatenate(tiles[start:start + 3], axis=1)
        for start in range(0, 12, 3)
    ], axis=0)
    sheet_path = args.output / "source-contact-sheet.jpg"
    assert cv2.imwrite(str(sheet_path), sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])
    pins = [Path(__file__).resolve(), base / "provenance.json",
            base / "native-review-plan.json", base / "screen-preflight.json",
            base / "upper-role-reply.json",
            root / "src/oil_tracker/adapters/vision/opencv_video_reader.py",
            root / "tests/diagnostics/s11_corpus_access.py"]
    result = {
        "schema": "s11-public-source-native-review-v1",
        "source": provenance, "metadata": metadata, "corpus_access": access,
        "versions": {"python": platform.python_version(), "opencv": cv2.__version__,
                     "numpy": np.__version__},
        "inputs": {str(p.relative_to(root)): digest(p) for p in pins},
        "frames": frames,
        "contact_sheet": {"path": sheet_path.name, "sha256": digest(sheet_path),
                          "shape": list(sheet.shape), "scale": 0.5,
                          "purpose": "Visual source context only; not a pixel scorer."},
        "source_unchanged_after": digest(source) == provenance["sha256"],
        "physical_accuracy": "NOT_EVALUATED",
    }
    assert result["source_unchanged_after"]
    (args.output / "native-review.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"frames": len(frames), "main": frames[5],
                      "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
