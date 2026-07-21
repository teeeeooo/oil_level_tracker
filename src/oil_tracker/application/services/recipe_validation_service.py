from __future__ import annotations

import math

from oil_tracker.application.services.detector_settings import validate_detector_settings
from oil_tracker.domain.enums import JudgmentMode, ValidationSeverity
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession
from oil_tracker.domain.validation import ValidationIssue, ValidationResult


class RecipeValidationService:
    def validate(
        self,
        recipe: InspectionRecipe,
        session: AnalysisSession | None = None,
        structural_only: bool = False,
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []
        if recipe.schema_version != 1:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "STRUCT_SCHEMA",
                    "Unsupported recipe schema version.",
                    field="schema_version",
                )
            )
        if recipe.reference_frame_width <= 0 or recipe.reference_frame_height <= 0:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "STRUCT_FRAME",
                    "Reference frame dimensions must be positive.",
                    field="reference_frame",
                )
            )
        seen: set[str] = set()
        for glass in recipe.glasses:
            if glass.id in seen:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "STRUCT_DUPLICATE_GLASS",
                        "Duplicate glass ID.",
                        glass.id,
                        "id",
                    )
                )
            seen.add(glass.id)
            for message in glass.geometry.ellipse.validate(
                recipe.reference_frame_width,
                recipe.reference_frame_height,
            ):
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "STRUCT_ELLIPSE",
                        message,
                        glass.id,
                        "geometry",
                    )
                )
            if not 0.0 <= glass.geometry.margin_ratio < 0.8:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "STRUCT_MARGIN",
                        "Margin ratio must be between 0 and 0.8.",
                        glass.id,
                        "margin",
                    )
                )
            if (
                glass.geometry.ellipse.radius_x * (1 - glass.geometry.margin_ratio) < 4
                or glass.geometry.ellipse.radius_y * (1 - glass.geometry.margin_ratio) < 4
            ):
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "STRUCT_MARGIN_AREA",
                        "Margin removes nearly all effective area.",
                        glass.id,
                        "margin",
                    )
                )
            for zone in glass.geometry.exclusions:
                rect = zone.rect
                values = (rect.x, rect.y, rect.width, rect.height)
                if not all(math.isfinite(value) for value in values) or rect.width <= 0 or rect.height <= 0:
                    issues.append(
                        ValidationIssue(
                            ValidationSeverity.ERROR,
                            "STRUCT_EXCLUSION",
                            "Exclusion rectangle is invalid.",
                            glass.id,
                            "exclusions",
                        )
                    )
                if (
                    rect.x < 0
                    or rect.y < 0
                    or rect.right > recipe.reference_frame_width
                    or rect.bottom > recipe.reference_frame_height
                ):
                    issues.append(
                        ValidationIssue(
                            ValidationSeverity.ERROR,
                            "STRUCT_EXCLUSION_BOUNDS",
                            "Exclusion rectangle must remain in frame.",
                            glass.id,
                            "exclusions",
                        )
                    )
            if glass.mm_per_pixel is not None:
                try:
                    scale = float(glass.mm_per_pixel)
                    scale_valid = math.isfinite(scale) and scale > 0
                except (TypeError, ValueError):
                    scale_valid = False
                if not scale_valid:
                    issues.append(
                        ValidationIssue(
                            ValidationSeverity.ERROR,
                            "STRUCT_SCALE",
                            "mm/pixel must be finite and positive when enabled.",
                            glass.id,
                            "mm_per_pixel",
                        )
                    )
            for field_name, message in validate_detector_settings(
                glass.detector_settings
            ).items():
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "STRUCT_DETECTOR_SETTING",
                        message,
                        glass.id,
                        f"detector_settings.{field_name}",
                    )
                )

        if structural_only:
            return ValidationResult(issues)

        enabled = [glass for glass in recipe.glasses if glass.enabled]
        if not enabled:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "READY_GLASS",
                    "At least one enabled Glass is required.",
                    field="glasses",
                )
            )
        for glass in enabled:
            if glass.geometry.zero_line_y is None:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "READY_ZERO",
                        "Zero line is required.",
                        glass.id,
                        "zero_line_y",
                    )
                )
            else:
                ellipse = glass.geometry.ellipse
                if not (
                    ellipse.center_y - ellipse.radius_y
                    <= glass.geometry.zero_line_y
                    <= ellipse.center_y + ellipse.radius_y
                ):
                    issues.append(
                        ValidationIssue(
                            ValidationSeverity.ERROR,
                            "READY_ZERO_BOUNDS",
                            "Zero line must be inside the ellipse.",
                            glass.id,
                            "zero_line_y",
                        )
                    )
                edge_distance = min(
                    glass.geometry.zero_line_y - (ellipse.center_y - ellipse.radius_y),
                    (ellipse.center_y + ellipse.radius_y) - glass.geometry.zero_line_y,
                )
                if edge_distance < ellipse.radius_y * 0.08:
                    issues.append(
                        ValidationIssue(
                            ValidationSeverity.WARNING,
                            "WARN_ZERO_EDGE",
                            "Zero line is close to the ellipse edge.",
                            glass.id,
                            "zero_line_y",
                        )
                    )
            if glass.geometry.margin_ratio > 0.30:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.WARNING,
                        "WARN_MARGIN",
                        "Detection margin is large.",
                        glass.id,
                        "margin",
                    )
                )
            if (
                glass.judgment_rule.mode == JudgmentMode.RECOVERY
                and session
                and session.compressor_start_sec is None
            ):
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "READY_COMPRESSOR",
                        "Compressor start is required for RECOVERY mode.",
                        glass.id,
                        "compressor_start",
                    )
                )

        if session is None or not session.input_video_path:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "READY_VIDEO",
                    "Input video is required.",
                    field="input_video_path",
                )
            )
            return ValidationResult(issues)
        if session.video_metadata is None:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "READY_METADATA",
                    "Video metadata is unavailable.",
                    field="video_metadata",
                )
            )
            return ValidationResult(issues)
        end = session.effective_end_sec()
        if (
            end is None
            or session.analysis_start_sec < 0
            or end <= session.analysis_start_sec
            or end > session.video_metadata.duration_sec + 0.05
        ):
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "READY_RANGE",
                    "Analysis time range is invalid.",
                    field="analysis_range",
                )
            )
        if (
            session.sampling_fps <= 0
            or session.sampling_fps > session.video_metadata.fps + 1e-6
        ):
            issues.append(
                ValidationIssue(
                    ValidationSeverity.ERROR,
                    "READY_FPS",
                    "Sampling FPS must be positive and not exceed source FPS.",
                    field="sampling_fps",
                )
            )
        if (session.video_metadata.width, session.video_metadata.height) != (
            recipe.reference_frame_width,
            recipe.reference_frame_height,
        ):
            if not session.resolution_confirmed:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.ERROR,
                        "READY_RESOLUTION",
                        "Resolution mismatch requires geometry review and confirmation.",
                        field="reference_frame",
                    )
                )
            else:
                issues.append(
                    ValidationIssue(
                        ValidationSeverity.WARNING,
                        "WARN_RESOLUTION",
                        "Video resolution differs from the Recipe reference frame.",
                        field="reference_frame",
                    )
                )
        if end is not None and end - session.analysis_start_sec < 1.0:
            issues.append(
                ValidationIssue(
                    ValidationSeverity.WARNING,
                    "WARN_DURATION",
                    "Analysis duration is very short.",
                    field="analysis_range",
                )
            )
        return ValidationResult(issues)
