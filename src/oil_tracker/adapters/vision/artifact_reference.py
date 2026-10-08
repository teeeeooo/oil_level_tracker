"""Bounded saved support for recipe review, never consumed by the matcher."""
from __future__ import annotations

import base64
from dataclasses import asdict
import hashlib
import math
import struct

import cv2
import numpy as np

from oil_tracker.domain.artifact_reference import (
    ArtifactSupportReference, REFERENCE_SCHEMA, fingerprint, geometry_fingerprint, template_geometry,
)
from oil_tracker.domain.geometry import artifact_template_source_rect

MAX_CROP_WIDTH, MAX_CROP_HEIGHT = 640, 160
IMAGE_KEYS = ("original_roi", "effective_mask", "glare_mask", "canny", "horizontal_mask")


class OpenCvArtifactReferenceReviewer:
    """Raster boundary injected into review UI by the application bootstrap."""

    def load(self, reference):
        return decode_reference(reference)

    def render(self, images, rect, mode):
        mask = reviewed_edge_mask(images, rect)
        image = images["original_roi" if mode in {"review", "proposal"} else mode].copy()
        if mode == "review":
            if image.ndim == 2:
                image = np.repeat(image[:, :, None], 3, axis=2)
            image[mask] = (255, 230, 0)
        return image, int(np.count_nonzero(mask))


def capture_reference(frame, glass, template, artifacts, *, candidate=None, candidate_index=None):
    if artifacts is None:
        return None
    images = artifacts.images
    if any(key not in images for key in IMAGE_KEYS):
        return None
    original = images["original_roi"]
    height, width = original.shape[:2]
    bounds = glass.geometry.ellipse.bounds
    ox, oy = max(0, math.floor(bounds.x)), max(0, math.floor(bounds.y))
    if not np.array_equal(original, frame[oy:oy + height, ox:ox + width]):
        return None
    rect = artifact_template_source_rect(template, glass.geometry)
    cx, cy = rect.x + rect.width / 2 - ox, rect.y + rect.height / 2 - oy
    # Preserve original pixels, never downsample. Anything outside this bounded
    # context is explicitly omitted, not labelled negative or reconstructed.
    requested = [math.floor(cx - rect.width / 2 - 24), math.floor(cy - rect.height / 2 - 24),
                 math.ceil(cx + rect.width / 2 + 24), math.ceil(cy + rect.height / 2 + 24)]
    w, h = min(width, MAX_CROP_WIDTH, requested[2] - requested[0]), min(height, MAX_CROP_HEIGHT, requested[3] - requested[1])
    x, y = max(0, min(width - w, math.floor(cx - w / 2))), max(0, min(height - h, math.floor(cy - h / 2)))
    if w <= 0 or h <= 0:
        return None
    keys = list(IMAGE_KEYS)
    if "foam_material_support_mask" in images:
        keys.append("foam_material_support_mask")
    saved = {}
    for key in keys:
        raster = images[key]
        if raster.dtype != np.uint8 or raster.shape[:2] != (height, width):
            return None
        crop = raster[y:y+h, x:x+w]
        ok, encoded = cv2.imencode(".png", crop)
        if not ok:
            return None
        data = encoded.tobytes()
        saved[key] = {"png": base64.b64encode(data).decode("ascii"),
                      "sha256": hashlib.sha256(data).hexdigest()}
    diagnostics = getattr(artifacts, "state", {}).get("oil_interface_diagnostics", {})
    native = next((row.get("path_aligned") for row in diagnostics.get("candidates", [])
                   if row.get("candidate_input_index") == candidate_index), None)
    settings = asdict(glass.detector_settings)
    preprocess = {"contract": "r22-3-preprocess-v1", "opencv": cv2.__version__, "settings": settings}
    return ArtifactSupportReference.capture({
        "schema": REFERENCE_SCHEMA, "frame_size": [int(frame.shape[1]), int(frame.shape[0])],
        "frame_index": None, "time_sec": None,  # Internal detector frame zero is not source identity.
        "frame_sha256": hashlib.sha256(np.ascontiguousarray(frame).tobytes()).hexdigest(),
        "glass_id": glass.id, "geometry_sha256": geometry_fingerprint(glass),
        "template_geometry": template_geometry(template),
        "settings_sha256": fingerprint(settings), "preprocessing": preprocess,
        "preprocessing_sha256": fingerprint(preprocess),
        "crop_origin": [ox + x, oy + y], "crop_size": [w, h],
        "context_clipped": [x, y, x+w, y+h] != requested,
        "images": saved,
        "proposal": {"candidate_input_index": candidate_index,
                     "source": candidate.source if candidate is not None else "glare_component",
                     "kind": candidate.kind.value if candidate is not None else "region",
                     "y": float(candidate.y) if candidate is not None else None,
                     "envelope_source_xywh": list(asdict(rect).values()),
                     "geometry_basis": "candidate_center_envelope" if candidate is not None else "glare_region",
                     "native_path": native},
    })


def decode_reference(reference):
    if reference.review_state not in {"unreviewed", "proposal_negative", "mixed_or_uncertain", "reviewed_support"}:
        raise ValueError("Unknown reference review state.")
    snapshot = reference.snapshot()
    width, height = snapshot["crop_size"]
    if not (0 < width <= MAX_CROP_WIDTH and 0 < height <= MAX_CROP_HEIGHT):
        raise ValueError("Invalid reference dimensions.")
    images = {}
    for key in (*IMAGE_KEYS, "foam_material_support_mask"):
        value = snapshot["images"].get(key)
        if value is None:
            if key in IMAGE_KEYS:
                raise ValueError("Reference image missing.")
            continue
        data = base64.b64decode(value["png"], validate=True)
        if hashlib.sha256(data).hexdigest() != value["sha256"]:
            raise ValueError("Reference image hash mismatch.")
        # Check the PNG header before allocating a decoder output.
        if (data[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
                or len(data) < 24 or struct.unpack(">II", data[16:24]) != (width, height)):
            raise ValueError("Invalid reference image header.")
        raster = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if raster is None or raster.dtype != np.uint8 or raster.shape[:2] != (height, width):
            raise ValueError("Reference image unavailable.")
        if ((key != "original_roi" and raster.ndim != 2)
                or (key == "original_roi" and (raster.ndim not in (2, 3) or (raster.ndim == 3 and raster.shape[2] != 3)))):
            raise ValueError("Invalid reference image channels.")
        images[key] = raster
    mask = reviewed_edge_mask(images, reference.review_rect)
    if reference.review_state == "reviewed_support" and not np.any(mask):
        raise ValueError("Confirmed reference has no reviewed visible edges.")
    return snapshot, images


def reviewed_edge_mask(images, rect):
    """Only explicit visible raw edges in the inspection rectangle, no dilation."""
    mask = np.zeros_like(images["canny"], dtype=bool)
    if rect is None:
        return mask
    x, y, width, height = rect
    h, w = mask.shape
    if (not all(isinstance(v, int) for v in rect) or x < 0 or y < 0
            or width <= 0 or height <= 0 or x + width > w or y + height > h):
        raise ValueError("Review rectangle is outside the saved reference.")
    mask[y:y+height, x:x+width] = True
    return mask & (images["canny"] > 0) & (images["effective_mask"] > 0) & (images["glare_mask"] == 0)
