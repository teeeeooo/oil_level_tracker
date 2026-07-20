from __future__ import annotations

import csv
import json
from pathlib import Path

import cv2

from .opencv_phase_detector import PhaseDetectionDebugArtifacts


class DebugRenderer:
    def export(self, directory: Path, frame_index: int, artifacts: PhaseDetectionDebugArtifacts) -> list[Path]:
        directory.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        image_aliases = {
            "overlay": "overlay",
            "original_roi": "roi",
            "normalized": "preprocessed",
            "canny": "canny",
            "effective_mask": "masks",
            "foam_mask": "foam",
        }
        for key, suffix in image_aliases.items():
            image = artifacts.images.get(key)
            if image is None:
                continue
            path = directory / f"frame_{frame_index:06d}_{suffix}.png"
            cv2.imwrite(str(path), image)
            written.append(path)
        csv_path = directory / f"frame_{frame_index:06d}_candidates.csv"
        rows = artifacts.candidate_rows
        fieldnames = sorted({key for row in rows for key in row}) if rows else ["rank", "source", "y", "final_score"]
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        written.append(csv_path)
        json_path = directory / f"frame_{frame_index:06d}_debug.json"
        json_path.write_text(json.dumps({"state": artifacts.state, "candidates": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(json_path)
        return written
