"""Frozen candidate RGB inference for the opt-in completed-Oil comparison.

The archived model's class decision is an extra eligibility condition, never
positive authority. Shared valid convolutions equal its independent 7x7 patches.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import replace
import hashlib
from importlib.resources import files
from io import BytesIO
import math
from typing import Sequence

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind


RGB_VERSION = "candidate-rgb-v1"
WEIGHTS_SHA256 = "8daffcdff5a59f6c8b2212c3e41aa911d676ac391d152a23857bd65d185636db"
COMPATIBLE = "OIL_CANDIDATE_COMPATIBLE"
OPPOSED = "OPPOSED_OIL_CANDIDATE"
_SHAPES = {
    "encoder.0.weight": (8, 3, 3, 3), "encoder.0.bias": (8,),
    "encoder.2.weight": (8, 8, 3, 3), "encoder.2.bias": (8,),
    "encoder.4.weight": (4, 8, 3, 3), "encoder.4.bias": (4,),
    "classifier.weight": (2, 8), "classifier.bias": (2,),
}


def _load_weights() -> dict[str, np.ndarray]:
    payload = files("oil_tracker").joinpath("resources/models/candidate_rgb_weights.npz").read_bytes()
    if hashlib.sha256(payload).hexdigest() != WEIGHTS_SHA256:
        raise ValueError("Candidate RGB comparison weights differ from the frozen model.")
    with np.load(BytesIO(payload), allow_pickle=False) as archive:
        if set(archive.files) != set(_SHAPES):
            raise ValueError("Invalid candidate RGB model keys.")
        weights = {key: archive[key].astype(np.float64) for key in _SHAPES}
    if any(value.shape != _SHAPES[key] or not np.isfinite(value).all()
           for key, value in weights.items()):
        raise ValueError("Invalid candidate RGB model arrays.")
    return weights


def variant_decision(logits: Sequence[Sequence[float]]) -> str:
    values = np.asarray(logits, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 2 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Invalid candidate RGB logits.")
    margins = values[:, 0] - values[:, 1]
    if np.all(margins > 0):
        return COMPATIBLE
    if np.all(margins < 0):
        return OPPOSED
    return "UNKNOWN"


class OilCandidateRgb:
    def __init__(self) -> None:
        self._weights = _load_weights()

    def _encode(self, rgb: np.ndarray) -> np.ndarray:
        # Preserve the original uint8 -> float32 /255 input before evaluating
        # in float64, as in the archived independent arithmetic verification.
        values = (rgb.astype(np.float32) / np.float32(255)).transpose(2, 0, 1).astype(np.float64)
        for index in (0, 2, 4):
            windows = sliding_window_view(values, (3, 3), axis=(1, 2))
            values = np.einsum(
                "cyxij,ocij->oyx", windows, self._weights[f"encoder.{index}.weight"],
                optimize=True,
            ) + self._weights[f"encoder.{index}.bias"][:, None, None]
            if index != 4:
                values = np.maximum(values, 0)
        return values.transpose(1, 2, 0)

    def annotate(
        self, candidates: Sequence[BoundaryCandidate], *, crop_bgr: np.ndarray,
        effective_mask: np.ndarray, glare_mask: np.ndarray,
        crop_origin: tuple[int, int], source_center_x: float,
    ) -> tuple[list[BoundaryCandidate], dict]:
        if crop_bgr.dtype != np.uint8 or crop_bgr.shape != (*effective_mask.shape, 3) or glare_mask.shape != effective_mask.shape:
            raise ValueError("Candidate RGB crop/mask geometry mismatch.")
        height, width = effective_mask.shape
        source_x = int(round(source_center_x))
        local_x = source_x - crop_origin[0]
        rgb = visible = encoded = patches = complete = None
        if 12 <= local_x < width - 12 and height >= 25:
            rgb = crop_bgr[:, local_x - 12:local_x + 13, ::-1].copy()
            visible = ((effective_mask[:, local_x - 12:local_x + 13] > 0)
                       & (glare_mask[:, local_x - 12:local_x + 13] == 0))
            encoded = self._encode(rgb)
            patches = sliding_window_view(rgb, (7, 7), axis=(0, 1))
            complete = sliding_window_view(visible, (7, 7)).all(axis=(-1, -2))
        cache: dict[int, dict] = {}

        def evaluate(local_y: int) -> dict:
            if local_y in cache:
                return cache[local_y]
            result = {"source_y": local_y + crop_origin[1], "status": "UNAVAILABLE_CROP"}
            cache[local_y] = result
            if encoded is None or not 12 <= local_y < height - 12:
                return result
            sides = []
            for name, start, stop in (("upper", local_y - 12, local_y - 7),
                                      ("lower", local_y + 2, local_y + 7)):
                mask = complete[start:stop]
                count = int(np.count_nonzero(mask))
                result[f"{name}_patch_count"] = count
                values = np.ascontiguousarray(patches[start:stop][mask])
                result[f"{name}_input_sha256"] = hashlib.sha256(values.tobytes()).hexdigest() if count else None
                if count:
                    sides.append(encoded[start:stop][mask].mean(axis=0))
            if len(sides) != 2:
                result["status"] = "UNAVAILABLE_SIDE"
                return result
            logits = self._weights["classifier.weight"] @ np.concatenate(sides) + self._weights["classifier.bias"]
            if not np.isfinite(logits).all():
                raise ValueError("Nonfinite candidate RGB inference.")
            result.update(status="AVAILABLE", logits=logits.tolist())
            return result

        annotated = []
        counts: Counter[str] = Counter()
        for candidate in candidates:
            if candidate.kind is not BoundaryKind.OIL_AIR:
                annotated.append(candidate)
                continue
            if math.isfinite(candidate.y):
                y = candidate.y - crop_origin[1]
                variants = [evaluate(iy) for iy in sorted({math.floor(y), math.ceil(y)})]
                decision = (variant_decision([v["logits"] for v in variants])
                            if all(v["status"] == "AVAILABLE" for v in variants) else "UNAVAILABLE")
            else:
                variants, decision = [], "UNAVAILABLE"
            counts[decision] += 1
            annotated.append(replace(candidate, features={
                **candidate.features,
                "oil_candidate_rgb_eligible": float(decision == COMPATIBLE),
                "oil_candidate_rgb_decision": decision,
                "oil_candidate_rgb_source_x": source_x,
                "oil_candidate_rgb_variants": variants,
                "oil_candidate_rgb_model_sha256": WEIGHTS_SHA256,
            }))
        return annotated, {"version": RGB_VERSION, "model_sha256": WEIGHTS_SHA256,
                           "candidate_count": sum(counts.values()), "decisions": dict(counts)}
