from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Iterable


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def clipped(self, frame_width: int, frame_height: int) -> "Rect":
        left = max(0.0, self.x)
        top = max(0.0, self.y)
        right = min(float(frame_width), self.right)
        bottom = min(float(frame_height), self.bottom)
        return Rect(left, top, max(0.0, right - left), max(0.0, bottom - top))

    def contains(self, x: float, y: float) -> bool:
        return self.x <= x <= self.right and self.y <= y <= self.bottom


@dataclass(frozen=True)
class EllipseGeometry:
    center_x: float
    center_y: float
    radius_x: float
    radius_y: float

    @property
    def bounds(self) -> Rect:
        return Rect(
            self.center_x - self.radius_x,
            self.center_y - self.radius_y,
            self.radius_x * 2.0,
            self.radius_y * 2.0,
        )

    def contains(self, x: float, y: float) -> bool:
        if self.radius_x <= 0 or self.radius_y <= 0:
            return False
        dx = (x - self.center_x) / self.radius_x
        dy = (y - self.center_y) / self.radius_y
        return dx * dx + dy * dy <= 1.0

    def horizontal_extent_at(self, y: float) -> tuple[float, float] | None:
        normalized = (y - self.center_y) / self.radius_y
        if abs(normalized) > 1.0:
            return None
        half_width = self.radius_x * math.sqrt(max(0.0, 1.0 - normalized * normalized))
        return self.center_x - half_width, self.center_x + half_width

    def validate(self, frame_width: int, frame_height: int, minimum_radius: float = 8.0) -> list[str]:
        errors: list[str] = []
        values = (self.center_x, self.center_y, self.radius_x, self.radius_y)
        if not all(math.isfinite(v) for v in values):
            errors.append("Ellipse coordinates must be finite.")
            return errors
        if self.radius_x < minimum_radius or self.radius_y < minimum_radius:
            errors.append("Ellipse is smaller than the minimum supported size.")
        b = self.bounds
        if b.x < 0 or b.y < 0 or b.right > frame_width or b.bottom > frame_height:
            errors.append("Ellipse must remain inside the source frame.")
        return errors


@dataclass(frozen=True)
class ExclusionZone:
    id: str
    rect: Rect
    name: str = "Exclusion"
    note: str = ""


@dataclass(frozen=True)
class ArtifactTemplate:
    """User-confirmed visual artifact in normalized ellipse coordinates."""

    id: str
    kind: str
    center_x: float
    center_y: float
    width: float
    height: float
    angle_deg: float = 0.0
    name: str = "Artifact"
    note: str = ""


@dataclass
class GlassGeometry:
    ellipse: EllipseGeometry
    zero_line_y: float | None = None
    margin_ratio: float = 0.08
    exclusions: list[ExclusionZone] = field(default_factory=list)
    artifact_templates: list[ArtifactTemplate] = field(default_factory=list)

    @property
    def crop_roi(self) -> Rect:
        return self.ellipse.bounds

    def level_px_from_zero(self, boundary_y: float | None) -> float | None:
        if boundary_y is None or self.zero_line_y is None:
            return None
        return self.zero_line_y - boundary_y

    def level_mm_from_zero(self, boundary_y: float | None, mm_per_pixel: float | None) -> float | None:
        px = self.level_px_from_zero(boundary_y)
        return None if px is None or mm_per_pixel is None else px * mm_per_pixel

    def normalized(self, width: int, height: int) -> dict[str, float]:
        e = self.ellipse
        return {
            "center_x": e.center_x / width,
            "center_y": e.center_y / height,
            "radius_x": e.radius_x / width,
            "radius_y": e.radius_y / height,
            "zero_line_y": (self.zero_line_y / height) if self.zero_line_y is not None else -1.0,
        }

    def remapped(self, old_width: int, old_height: int, new_width: int, new_height: int) -> "GlassGeometry":
        sx, sy = new_width / old_width, new_height / old_height
        e = self.ellipse
        exclusions = [
            ExclusionZone(
                z.id,
                Rect(z.rect.x * sx, z.rect.y * sy, z.rect.width * sx, z.rect.height * sy),
                z.name,
                z.note,
            )
            for z in self.exclusions
        ]
        return GlassGeometry(
            EllipseGeometry(e.center_x * sx, e.center_y * sy, e.radius_x * sx, e.radius_y * sy),
            self.zero_line_y * sy if self.zero_line_y is not None else None,
            self.margin_ratio,
            exclusions,
            list(self.artifact_templates),
        )


def artifact_template_source_rect(
    template: ArtifactTemplate,
    geometry: GlassGeometry,
) -> Rect:
    """Project a normalized artifact template into source-frame geometry."""

    bounds = geometry.ellipse.bounds
    width = template.width * bounds.width
    height = template.height * bounds.height
    center_x = bounds.x + template.center_x * bounds.width
    center_y = bounds.y + template.center_y * bounds.height
    return Rect(center_x - width * 0.5, center_y - height * 0.5, width, height)


@dataclass(frozen=True)
class CoordinateTransform:
    source_width: float
    source_height: float
    display_width: float
    display_height: float

    @property
    def scale(self) -> float:
        return min(self.display_width / self.source_width, self.display_height / self.source_height)

    @property
    def offset(self) -> tuple[float, float]:
        s = self.scale
        return ((self.display_width - self.source_width * s) / 2.0, (self.display_height - self.source_height * s) / 2.0)

    def source_to_display(self, x: float, y: float) -> tuple[float, float]:
        ox, oy = self.offset
        s = self.scale
        return x * s + ox, y * s + oy

    def display_to_source(self, x: float, y: float) -> tuple[float, float]:
        ox, oy = self.offset
        s = self.scale
        return (x - ox) / s, (y - oy) / s


def all_finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(v) for v in values)
