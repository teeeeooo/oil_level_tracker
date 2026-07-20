from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.domain.geometry import EllipseGeometry, ExclusionZone, Rect
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession


class WorkbenchController:
    def __init__(self, save_use_case: SaveRecipeUseCase, load_use_case: LoadRecipeUseCase, validate_use_case: ValidateWorkbenchUseCase) -> None:
        self.save_use_case = save_use_case
        self.load_use_case = load_use_case
        self.validate_use_case = validate_use_case
        self.recipe = InspectionRecipe.empty()
        self.session = AnalysisSession()
        self.state = WorkbenchState.EMPTY
        self.selected_glass_id: str | None = None
        self.recipe_path: Path | None = None
        self.video_reader: OpenCvVideoReader | None = None

    def new_document(self, width: int = 1280, height: int = 720, name: str = "새 유면 분석 프로필") -> None:
        self.close_video()
        self.recipe = InspectionRecipe.empty(width, height, name)
        self.session = AnalysisSession()
        self.state = WorkbenchState.EMPTY
        self.selected_glass_id = None
        self.recipe_path = None

    def open_video(self, path: str) -> None:
        self.close_video()
        reader = OpenCvVideoReader(path)
        self.video_reader = reader
        metadata = reader.metadata
        self.session.input_video_path = path
        self.session.video_metadata = metadata
        self.session.analysis_start_sec = 0.0
        self.session.analysis_end_sec = metadata.duration_sec
        self.session.sampling_fps = min(2.0, metadata.fps) if metadata.fps > 0 else 1.0
        self.session.resolution_confirmed = (metadata.width, metadata.height) == (self.recipe.reference_frame_width, self.recipe.reference_frame_height)
        if not self.recipe.glasses and self.state == WorkbenchState.EMPTY:
            self.recipe.reference_frame_width = metadata.width
            self.recipe.reference_frame_height = metadata.height
            self.session.resolution_confirmed = True
        self.mark_dirty()

    def close_video(self) -> None:
        if self.video_reader is not None:
            self.video_reader.close()
            self.video_reader = None

    def read_at(self, timestamp_sec: float):
        if self.video_reader is None:
            raise ValueError("열려 있는 시험 영상이 없습니다.")
        return self.video_reader.read_at(timestamp_sec)

    def add_glass(self):
        glass = InspectionRecipe.default_glass(self.recipe.reference_frame_width, self.recipe.reference_frame_height, len(self.recipe.glasses) + 1)
        self.recipe.glasses.append(glass)
        self.selected_glass_id = glass.id
        self.mark_dirty()
        return glass

    def delete_selected_glass(self) -> None:
        if self.selected_glass_id is None:
            return
        self.recipe.glasses = [g for g in self.recipe.glasses if g.id != self.selected_glass_id]
        self.selected_glass_id = self.recipe.glasses[0].id if self.recipe.glasses else None
        self.mark_dirty()

    def selected_glass(self):
        return next((g for g in self.recipe.glasses if g.id == self.selected_glass_id), None)

    def set_selected(self, glass_id: str | None) -> None:
        self.selected_glass_id = glass_id

    def update_ellipse(self, glass_id: str, ellipse: EllipseGeometry) -> None:
        glass = self._glass(glass_id)
        glass.geometry.ellipse = ellipse
        if glass.geometry.zero_line_y is not None:
            top, bottom = ellipse.center_y - ellipse.radius_y, ellipse.center_y + ellipse.radius_y
            glass.geometry.zero_line_y = min(bottom, max(top, glass.geometry.zero_line_y))
        self.mark_dirty()

    def update_zero_line(self, glass_id: str, y: float) -> None:
        glass = self._glass(glass_id)
        e = glass.geometry.ellipse
        glass.geometry.zero_line_y = min(e.center_y + e.radius_y, max(e.center_y - e.radius_y, y))
        self.mark_dirty()

    def add_exclusion(self, glass_id: str) -> ExclusionZone:
        glass = self._glass(glass_id)
        e = glass.geometry.ellipse
        rect = Rect(e.center_x - e.radius_x * 0.3, e.center_y - e.radius_y * 0.1, e.radius_x * 0.6, e.radius_y * 0.2)
        zone = ExclusionZone(str(uuid4()), rect, f"검출 제외 영역 {len(glass.geometry.exclusions) + 1}")
        glass.geometry.exclusions.append(zone)
        self.mark_dirty()
        return zone

    def update_exclusion(self, glass_id: str, zone_id: str, rect: Rect) -> None:
        glass = self._glass(glass_id)
        for i, zone in enumerate(glass.geometry.exclusions):
            if zone.id == zone_id:
                glass.geometry.exclusions[i] = ExclusionZone(zone.id, rect, zone.name, zone.note)
                self.mark_dirty()
                return

    def delete_exclusion(self, glass_id: str, zone_id: str) -> None:
        glass = self._glass(glass_id)
        glass.geometry.exclusions = [z for z in glass.geometry.exclusions if z.id != zone_id]
        self.mark_dirty()

    def mark_dirty(self) -> None:
        self.state = WorkbenchState.DRAFT_DIRTY if self.state in {WorkbenchState.VALIDATED, WorkbenchState.ANALYZED} else WorkbenchState.DRAFT

    def validate(self):
        result = self.validate_use_case.execute(self.recipe, self.session)
        self.state = WorkbenchState.VALIDATED if result.is_ready else WorkbenchState.DRAFT
        return result

    def save(self, path: Path) -> None:
        self.save_use_case.execute(path, self.recipe)
        self.recipe_path = path.with_suffix(".oilrecipe")
        if self.state == WorkbenchState.EMPTY:
            self.state = WorkbenchState.DRAFT

    def load(self, path: Path) -> None:
        self.recipe = self.load_use_case.execute(path)
        self.recipe_path = path
        self.selected_glass_id = self.recipe.glasses[0].id if self.recipe.glasses else None
        self.state = WorkbenchState.DRAFT

    def _glass(self, glass_id: str):
        glass = next((g for g in self.recipe.glasses if g.id == glass_id), None)
        if glass is None:
            raise KeyError(glass_id)
        return glass
