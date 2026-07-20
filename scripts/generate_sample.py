from __future__ import annotations

from pathlib import Path
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.domain.recipe import InspectionRecipe


def main() -> None:
    out = ROOT / "sample"; out.mkdir(exist_ok=True)
    video = out / "synthetic_oil_test.avi"
    width, height, fps, seconds = 640, 480, 10.0, 8
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), fps, (width, height))
    for i in range(int(fps * seconds)):
        frame = np.full((height, width, 3), 225, dtype=np.uint8)
        center, axes = (320, 240), (100, 180)
        cv2.ellipse(frame, center, axes, 0, 0, 360, (80, 80, 80), 4)
        y = int(400 - min(1.0, i / (fps * 5)) * 220)
        mask = np.zeros((height, width), dtype=np.uint8); cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        oil = np.zeros_like(mask); oil[y:, :] = 255; oil = cv2.bitwise_and(oil, mask)
        frame[oil > 0] = (70, 85, 95)
        cv2.line(frame, (230, y), (410, y), (30, 30, 30), 3)
        if i > fps * 5:
            rng = np.random.default_rng(i)
            for _ in range(25):
                x = int(rng.integers(260, 380)); yy = int(rng.integers(310, 400)); r = int(rng.integers(2, 7))
                cv2.circle(frame, (x, yy), r, (190, 190, 190), 1)
        writer.write(frame)
    writer.release()
    recipe = InspectionRecipe.empty(width, height, "Synthetic Sample")
    glass = recipe.default_glass(width, height, 1)
    glass.geometry.ellipse = glass.geometry.ellipse.__class__(320, 240, 100, 180)
    glass.geometry.zero_line_y = 260
    glass.mm_per_pixel = 0.25
    glass.judgment_rule.recovery_limit_sec = 7.0
    glass.judgment_rule.stable_hold_sec = 0.5
    recipe.glasses.append(glass)
    JsonRecipeRepository().save(out / "synthetic_sample.oilrecipe", recipe)
    print(video)


if __name__ == "__main__": main()
