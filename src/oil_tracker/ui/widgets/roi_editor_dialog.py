from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from oil_tracker.domain.geometry import ExclusionZone, Rect
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas


class RoiEditorDialog(QDialog):
    """Edit one observation ROI on a private copy until the user applies it."""

    def __init__(self, frame: np.ndarray, glass, frame_width: int, frame_height: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("ROI 집중 편집")
        self.setMinimumSize(980, 700)
        self.resize(1200, 840)
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._working = deepcopy(glass)

        instruction = QLabel(
            "타원의 파란 조절점을 드래그해 크기를 바꾸고, 노란 기준선을 위아래로 움직이세요. "
            "적용하기 전까지 원래 프로필은 변경되지 않습니다."
        )
        instruction.setWordWrap(True)
        instruction.setObjectName("roiEditorHint")

        self.canvas = VideoOverlayCanvas()
        self.canvas.setMinimumSize(900, 560)
        self.canvas.set_frame(frame)
        self.canvas.geometryChanged.connect(self._ellipse_changed)
        self.canvas.zeroLineChanged.connect(self._zero_changed)
        self.canvas.exclusionChanged.connect(self._exclusion_changed)

        self.exclusion_combo = QComboBox()
        self.add_exclusion_button = QPushButton("제외 영역 추가")
        self.delete_exclusion_button = QPushButton("선택 제외 영역 삭제")
        self.reset_geometry_button = QPushButton("관찰창 위치 초기화")

        controls = QHBoxLayout()
        controls.setSpacing(7)
        controls.addWidget(QLabel("검출 제외 영역"))
        controls.addWidget(self.exclusion_combo, 1)
        controls.addWidget(self.add_exclusion_button)
        controls.addWidget(self.delete_exclusion_button)
        controls.addStretch(1)
        controls.addWidget(self.reset_geometry_button)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("적용")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(instruction)
        layout.addWidget(self.canvas, 1)
        layout.addLayout(controls)
        layout.addWidget(self.buttons)

        self.add_exclusion_button.clicked.connect(self._add_exclusion)
        self.delete_exclusion_button.clicked.connect(self._delete_exclusion)
        self.reset_geometry_button.clicked.connect(self._reset_geometry)
        self._refresh()

    def edited_glass(self):
        return deepcopy(self._working)

    def _refresh(self) -> None:
        self.canvas.set_glasses([self._working], self._working.id)
        current_id = self.exclusion_combo.currentData()
        self.exclusion_combo.clear()
        for zone in self._working.geometry.exclusions:
            self.exclusion_combo.addItem(zone.name, zone.id)
        if current_id is not None:
            index = self.exclusion_combo.findData(current_id)
            if index >= 0:
                self.exclusion_combo.setCurrentIndex(index)
        self.delete_exclusion_button.setEnabled(self.exclusion_combo.count() > 0)

    def _ellipse_changed(self, _glass_id: str, ellipse) -> None:
        self._working.geometry.ellipse = ellipse
        if self._working.geometry.zero_line_y is not None:
            top = ellipse.center_y - ellipse.radius_y
            bottom = ellipse.center_y + ellipse.radius_y
            self._working.geometry.zero_line_y = min(bottom, max(top, self._working.geometry.zero_line_y))
        self._refresh()

    def _zero_changed(self, _glass_id: str, y: float) -> None:
        self._working.geometry.zero_line_y = y
        self._refresh()

    def _exclusion_changed(self, _glass_id: str, zone_id: str, rect: Rect) -> None:
        for index, zone in enumerate(self._working.geometry.exclusions):
            if zone.id == zone_id:
                self._working.geometry.exclusions[index] = ExclusionZone(zone.id, rect, zone.name, zone.note)
                break
        self._refresh()

    def _add_exclusion(self) -> None:
        ellipse = self._working.geometry.ellipse
        rect = Rect(
            ellipse.center_x - ellipse.radius_x * 0.3,
            ellipse.center_y - ellipse.radius_y * 0.1,
            ellipse.radius_x * 0.6,
            ellipse.radius_y * 0.2,
        )
        number = len(self._working.geometry.exclusions) + 1
        self._working.geometry.exclusions.append(
            ExclusionZone(str(uuid4()), rect, f"검출 제외 영역 {number}")
        )
        self._refresh()
        self.exclusion_combo.setCurrentIndex(self.exclusion_combo.count() - 1)

    def _delete_exclusion(self) -> None:
        zone_id = self.exclusion_combo.currentData()
        if zone_id is None:
            return
        self._working.geometry.exclusions = [
            zone for zone in self._working.geometry.exclusions if zone.id != zone_id
        ]
        self._refresh()

    def _reset_geometry(self) -> None:
        default = InspectionRecipe.default_glass(self._frame_width, self._frame_height)
        self._working.geometry = deepcopy(default.geometry)
        self._refresh()
