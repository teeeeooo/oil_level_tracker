from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .enums import InitialObservationState, JudgmentMode
from .geometry import EllipseGeometry, ExclusionZone, GlassGeometry, Rect

SCHEMA_VERSION = 1


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DetectorSettings:
    canny_low: int = 45
    canny_high: int = 130
    hough_threshold: int = 18
    hough_min_line_length_ratio: float = 0.30
    hough_max_line_gap: int = 8
    hough_max_angle_deg: float = 8.0
    minimum_horizontal_coverage: float = 0.22
    minimum_region_contrast: float = 0.08
    minimum_final_confidence: float = 0.42
    temporal_max_jump_px: float = 32.0
    smoothing_window: int = 5
    glare_threshold: int = 245
    glare_ratio_unknown: float = 0.40
    foam_variance_threshold: float = 120.0
    foam_edge_density_threshold: float = 0.08
    foam_min_area_ratio: float = 0.025
    state_hold_frames: int = 2
    candidate_top_k: int = 8
    weight_edge: float = 0.22
    weight_coverage: float = 0.20
    weight_region: float = 0.22
    weight_gradient_direction: float = 0.05
    weight_temporal: float = 0.18
    weight_state: float = 0.13
    penalty_glare: float = 0.26
    penalty_border: float = 0.24
    penalty_exclusion: float = 0.30
    penalty_static: float = 0.12
    penalty_jump: float = 0.25


@dataclass
class JudgmentRule:
    mode: JudgmentMode = JudgmentMode.RECOVERY
    recovery_limit_sec: float = 120.0
    stable_hold_sec: float = 5.0
    minimum_valid_coverage_ratio: float = 0.70
    allowed_excursion_sec: float = 1.0
    allowed_excursion_height: float = 0.0
    allowed_violation_sec: float = 1.0
    allowed_violation_depth: float = 0.0
    unknown_policy: str = "review"


@dataclass
class GlassInspectionConfig:
    id: str
    name: str
    geometry: GlassGeometry
    enabled: bool = True
    description: str = ""
    initial_state: InitialObservationState = InitialObservationState.AUTO
    mm_per_pixel: float | None = None
    judgment_rule: JudgmentRule = field(default_factory=JudgmentRule)
    detector_settings: DetectorSettings = field(default_factory=DetectorSettings)


@dataclass
class InspectionRecipe:
    name: str
    reference_frame_width: int
    reference_frame_height: int
    glasses: list[GlassInspectionConfig] = field(default_factory=list)
    description: str = ""
    recipe_id: str = field(default_factory=lambda: str(uuid4()))
    schema_version: int = SCHEMA_VERSION
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    @classmethod
    def empty(cls, width: int = 1280, height: int = 720, name: str = "새 유면 분석 프로필") -> "InspectionRecipe":
        return cls(name=name, reference_frame_width=width, reference_frame_height=height)

    @staticmethod
    def default_glass(width: int, height: int, index: int = 1) -> GlassInspectionConfig:
        rx, ry = width * 0.12, height * 0.27
        ellipse = EllipseGeometry(width * 0.5, height * 0.5, rx, ry)
        geometry = GlassGeometry(ellipse=ellipse, zero_line_y=height * 0.55, margin_ratio=0.08)
        return GlassInspectionConfig(id=str(uuid4()), name=f"유면 관찰창 {index}", geometry=geometry)

    def touch(self) -> None:
        self.updated_at = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        def rect_dict(r: Rect) -> dict[str, float]:
            return {"x": r.x, "y": r.y, "width": r.width, "height": r.height}

        glasses: list[dict[str, Any]] = []
        for g in self.glasses:
            e = g.geometry.ellipse
            glasses.append(
                {
                    "id": g.id,
                    "name": g.name,
                    "enabled": g.enabled,
                    "description": g.description,
                    "geometry": {
                        "ellipse": {"center_x": e.center_x, "center_y": e.center_y, "radius_x": e.radius_x, "radius_y": e.radius_y},
                        "zero_line_y": g.geometry.zero_line_y,
                        "margin_ratio": g.geometry.margin_ratio,
                        "exclusions": [
                            {"id": z.id, "name": z.name, "note": z.note, "rect": rect_dict(z.rect)} for z in g.geometry.exclusions
                        ],
                    },
                    "initial_state": g.initial_state.value,
                    "mm_per_pixel": g.mm_per_pixel,
                    "judgment_rule": {**asdict(g.judgment_rule), "mode": g.judgment_rule.mode.value},
                    "detector_settings": asdict(g.detector_settings),
                }
            )
        return {
            "schema_version": self.schema_version,
            "recipe_id": self.recipe_id,
            "name": self.name,
            "description": self.description,
            "reference_frame": {"width": self.reference_frame_width, "height": self.reference_frame_height},
            "glasses": glasses,
            "defaults": {},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InspectionRecipe":
        version = int(data.get("schema_version", -1))
        if version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported recipe schema_version: {version}")
        frame = data["reference_frame"]
        glasses: list[GlassInspectionConfig] = []
        for raw in data.get("glasses", []):
            geo = raw["geometry"]
            eraw = geo["ellipse"]
            ellipse = EllipseGeometry(float(eraw["center_x"]), float(eraw["center_y"]), float(eraw["radius_x"]), float(eraw["radius_y"]))
            exclusions = []
            for z in geo.get("exclusions", []):
                r = z["rect"]
                exclusions.append(ExclusionZone(z["id"], Rect(float(r["x"]), float(r["y"]), float(r["width"]), float(r["height"])), z.get("name", "Exclusion"), z.get("note", "")))
            geometry = GlassGeometry(ellipse, geo.get("zero_line_y"), float(geo.get("margin_ratio", 0.08)), exclusions)
            jr = dict(raw.get("judgment_rule", {}))
            jr["mode"] = JudgmentMode(jr.get("mode", JudgmentMode.RECOVERY.value))
            ds = DetectorSettings(**raw.get("detector_settings", {}))
            glasses.append(
                GlassInspectionConfig(
                    id=raw["id"],
                    name=raw["name"],
                    geometry=geometry,
                    enabled=bool(raw.get("enabled", True)),
                    description=raw.get("description", ""),
                    initial_state=InitialObservationState(raw.get("initial_state", InitialObservationState.AUTO.value)),
                    mm_per_pixel=raw.get("mm_per_pixel"),
                    judgment_rule=JudgmentRule(**jr),
                    detector_settings=ds,
                )
            )
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            reference_frame_width=int(frame["width"]),
            reference_frame_height=int(frame["height"]),
            glasses=glasses,
            recipe_id=data["recipe_id"],
            schema_version=version,
            created_at=data.get("created_at", utc_now_iso()),
            updated_at=data.get("updated_at", utc_now_iso()),
        )
