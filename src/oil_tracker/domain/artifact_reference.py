"""Immutable recipe evidence; deliberately has no detector/matching authority."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math


MAX_REFERENCE_BYTES = 1_048_576
MAX_REFERENCES_PER_GLASS = 16
REFERENCE_SCHEMA = "artifact-support-reference-v1"


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(value) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def geometry_fingerprint(glass) -> str:
    geometry = glass.geometry
    return fingerprint({
        "glass_id": glass.id, "ellipse": asdict(geometry.ellipse),
        "margin_ratio": geometry.margin_ratio,
        "exclusions": [asdict(zone) for zone in geometry.exclusions],
    })


@dataclass(frozen=True)
class ArtifactSupportReference:
    # Canonical JSON keeps image bytes and provenance immutable, including across
    # editor working copies. This nested payload has its own version and digest.
    snapshot_json: str
    snapshot_sha256: str
    review_state: str = "unreviewed"
    review_rect: tuple[int, int, int, int] | None = None

    @classmethod
    def capture(cls, snapshot) -> "ArtifactSupportReference":
        encoded = canonical_json(snapshot)
        if len(encoded.encode()) > MAX_REFERENCE_BYTES:
            raise ValueError("Reference exceeds the bounded snapshot size.")
        return cls(encoded, hashlib.sha256(encoded.encode()).hexdigest())

    @classmethod
    def from_dict(cls, value) -> "ArtifactSupportReference | None":
        if value is None:
            return None
        encoded = value["snapshot_json"]
        if not isinstance(encoded, str) or len(encoded.encode()) > MAX_REFERENCE_BYTES:
            raise ValueError("Invalid or oversized artifact reference.")
        rect = value.get("review_rect")
        return cls(encoded, value["snapshot_sha256"], value.get("review_state", "unreviewed"),
                   tuple(rect) if rect is not None else None)

    def snapshot(self) -> dict:
        if len(self.snapshot_json.encode()) > MAX_REFERENCE_BYTES:
            raise ValueError("Reference exceeds the bounded snapshot size.")
        if hashlib.sha256(self.snapshot_json.encode()).hexdigest() != self.snapshot_sha256:
            raise ValueError("Reference content hash mismatch.")
        snapshot = json.loads(self.snapshot_json)
        if snapshot.get("schema") != REFERENCE_SCHEMA:
            raise ValueError("Unsupported reference schema.")
        return snapshot

    def with_source_position(self, frame_index, time_sec) -> "ArtifactSupportReference":
        if frame_index is not None and (not isinstance(frame_index, int) or frame_index < 0):
            raise ValueError("Invalid source frame index.")
        if time_sec is not None and (not math.isfinite(time_sec) or time_sec < 0):
            raise ValueError("Invalid source time.")
        snapshot = self.snapshot()
        snapshot["frame_index"], snapshot["time_sec"] = frame_index, time_sec
        bound = self.capture(snapshot)
        return replace(bound, review_state=self.review_state, review_rect=self.review_rect)

    def correspondence_status(self, glass, width, height, template=None) -> str:
        try:
            snapshot = self.snapshot()
            if (snapshot["frame_size"] != [width, height]
                    or snapshot["geometry_sha256"] != geometry_fingerprint(glass)
                    or snapshot["settings_sha256"] != fingerprint(asdict(glass.detector_settings))):
                return "context_mismatch"
            if template is not None and snapshot["template_geometry"] != template_geometry(template):
                return "context_mismatch"
        except (ValueError, TypeError, KeyError):
            return "reference_unavailable"
        return "bound_reference"  # Not a claim about visibility in a new frame.


def template_geometry(template) -> dict:
    return {key: getattr(template, key) for key in ("id", "kind", "center_x", "center_y", "width", "height", "angle_deg")}
