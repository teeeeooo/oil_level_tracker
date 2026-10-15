"""Frozen local inputs for the optional initial-FULL observation comparison.

Use a managed experiment's work directory. Original Recipes are never changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.domain.geometry import EllipseGeometry

ROOT = Path(__file__).resolve().parents[2]
SOURCE_VIEWS = ROOT / "sample/output/s11-truth-audit-20261010-002/sample4"
ROI_FRAMES = (0, 450, 900, 1470, 1680)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    repository = JsonRecipeRepository()
    records = {}
    for sample in ("base_sample_1", "sample4"):
        original = ROOT / "sample" / f"{sample}.oilrecipe"
        recipe = repository.load(original)
        if sample == "sample4":
            recipe.glasses[0].geometry.ellipse = EllipseGeometry(595, 842, 37, 34)
        target = output / f"{sample}.oilrecipe"
        repository.save(target, recipe)
        records[sample] = {
            "original_recipe_sha256": _sha(original),
            "comparison_recipe_sha256": _sha(target),
            "geometry": recipe.to_dict()["glasses"][0]["geometry"],
        }

    original = repository.load(ROOT / "sample/sample4.oilrecipe").glasses[0]
    interior = repository.load(output / "sample4.oilrecipe").glasses[0]
    panels = []
    source_hashes = {}
    for frame in ROI_FRAMES:
        path = SOURCE_VIEWS / f"f{frame:06d}.png"
        source_hashes[str(path.relative_to(ROOT))] = _sha(path)
        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Missing source view: {path}")
        canvas = image[785:910, 530:660].copy()
        for glass, color in ((original, (0, 165, 255)), (interior, (0, 255, 0))):
            mask = build_mask_bundle(image, glass)
            contours, _ = cv2.findContours(mask.effective_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            offset = np.array([mask.crop_origin[0] - 530, mask.crop_origin[1] - 785])
            cv2.drawContours(canvas, [c + offset for c in contours], -1, color, 1)
        panel = cv2.resize(canvas, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
        panel = cv2.copyMakeBorder(panel, 32, 0, 0, 0, cv2.BORDER_CONSTANT, value=(24, 24, 24))
        cv2.putText(panel, f"sample4 f{frame} | green: interior", (8, 22), cv2.FONT_HERSHEY_SIMPLEX, .52, (255, 255, 255), 1)
        panels.append(panel)
    if not cv2.imwrite(str(output / "roi-review.png"), np.concatenate(panels, axis=1)):
        raise OSError("Cannot save ROI review")
    manifest = {
        "status": "ROI_PREPARED_BEFORE_DETECTOR_COMPARISON",
        "source_views": source_hashes,
        "recipes": records,
        "selection_basis": "Vessel interior in retained source views; no detector output optimization or physical target relabeling",
        "windows_roi": "OPERATOR_CHECK_REQUIRED_ON_WINDOWS",
    }
    (output / "roi-inputs.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-roi", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.prepare_roi)
