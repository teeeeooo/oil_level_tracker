from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.adapters.vision.artifact_proposal import propose_artifact_templates
from oil_tracker.domain.geometry import ExclusionZone, Rect
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas


class RoiEditorDialog(QDialog):
    """Edit one analysis region on a private copy until the user applies it."""

    def __init__(self, frame, glass, frame_width: int, frame_height: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("분석 영역 편집")
        self.setMinimumSize(980, 700)
        self.resize(1200, 840)
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._frame = frame
        self._working = deepcopy(glass)
        self._artifact_proposals = []

        instruction = QLabel(
            "분석 영역 타원의 파란 조절점을 드래그해 크기를 바꾸고, 노란 기준선을 위아래로 움직이세요. "
            "적용하기 전까지 원래 프로필은 변경되지 않습니다."
        )
        instruction.setWordWrap(True)
        instruction.setObjectName("roiEditorHint")

        self.canvas = VideoOverlayCanvas()
        self.canvas.setMinimumSize(640, 320)
        self.canvas.set_frame(frame)
        self.canvas.geometryChanged.connect(self._ellipse_changed)
        self.canvas.zeroLineChanged.connect(self._zero_changed)
        self.canvas.exclusionChanged.connect(self._exclusion_changed)

        self.exclusion_combo = QComboBox()
        self.add_exclusion_button = QPushButton("제외 영역 추가")
        self.delete_exclusion_button = QPushButton("선택 제외 영역 삭제")
        self.reset_geometry_button = QPushButton("분석 영역 위치 초기화")

        controls = QHBoxLayout()
        controls.setSpacing(7)
        controls.addWidget(QLabel("검출 제외 영역"))
        controls.addWidget(self.exclusion_combo, 1)
        controls.addWidget(self.add_exclusion_button)
        controls.addWidget(self.delete_exclusion_button)
        controls.addStretch(1)
        controls.addWidget(self.reset_geometry_button)

        artifact_group = QGroupBox("사용자 Artifact Calibration")
        artifact_layout = QVBoxLayout(artifact_group)
        artifact_hint = QLabel(
            "현재 화면에서 detector가 제안한 고정 반사·흠집 후보를 선택하면 "
            "정규화된 점·선·구역 템플릿으로 저장됩니다. 같은 Y 전체를 제외하지 않습니다."
        )
        artifact_hint.setWordWrap(True)
        artifact_layout.addWidget(artifact_hint)
        artifact_lists = QHBoxLayout()
        self.artifact_proposal_list = QListWidget()
        self.artifact_proposal_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.artifact_template_list = QListWidget()
        artifact_lists.addWidget(self.artifact_proposal_list, 1)
        artifact_lists.addWidget(self.artifact_template_list, 1)
        artifact_layout.addLayout(artifact_lists)
        artifact_buttons = QHBoxLayout()
        self.scan_artifacts_button = QPushButton("Detector 후보 찾기")
        self.select_all_artifacts_button = QPushButton("모든 후보 선택")
        self.accept_artifact_button = QPushButton("선택 후보 일괄 Artifact 지정")
        self.delete_artifact_button = QPushButton("선택 Artifact 삭제")
        artifact_buttons.addWidget(self.scan_artifacts_button)
        artifact_buttons.addWidget(self.select_all_artifacts_button)
        artifact_buttons.addWidget(self.accept_artifact_button)
        artifact_buttons.addWidget(self.delete_artifact_button)
        artifact_layout.addLayout(artifact_buttons)
        self.artifact_status = QLabel("후보 찾기를 실행한 뒤 필요한 항목만 선택하세요.")
        self.artifact_status.setObjectName("ownershipHint")
        artifact_layout.addWidget(self.artifact_status)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("적용")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(instruction)
        settings = QWidget()
        settings_layout = QVBoxLayout(settings)
        settings_layout.setContentsMargins(4, 4, 4, 4)
        settings_layout.addLayout(controls)
        settings_layout.addWidget(artifact_group)
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        settings_scroll.setWidget(settings)
        settings_scroll.setMinimumHeight(210)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.canvas)
        splitter.addWidget(settings_scroll)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([560, 250])
        self.content_splitter = splitter
        self.settings_scroll = settings_scroll
        layout.addWidget(splitter, 1)
        layout.addWidget(self.buttons)

        self.add_exclusion_button.clicked.connect(self._add_exclusion)
        self.delete_exclusion_button.clicked.connect(self._delete_exclusion)
        self.reset_geometry_button.clicked.connect(self._reset_geometry)
        self.scan_artifacts_button.clicked.connect(self._scan_artifacts)
        self.select_all_artifacts_button.clicked.connect(
            self.artifact_proposal_list.selectAll
        )
        self.accept_artifact_button.clicked.connect(self._accept_artifact)
        self.delete_artifact_button.clicked.connect(self._delete_artifact)
        self.artifact_proposal_list.itemSelectionChanged.connect(
            self._artifact_proposal_selection_changed
        )
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
        current_template_id = (
            self.artifact_template_list.currentItem().data(Qt.ItemDataRole.UserRole)
            if self.artifact_template_list.currentItem() is not None
            else None
        )
        self.artifact_template_list.clear()
        for template in self._working.geometry.artifact_templates:
            item = QListWidgetItem(f"{template.name} · {template.kind}")
            item.setData(Qt.ItemDataRole.UserRole, template.id)
            self.artifact_template_list.addItem(item)
            if template.id == current_template_id:
                self.artifact_template_list.setCurrentItem(item)
        self.delete_artifact_button.setEnabled(
            bool(self._working.geometry.artifact_templates)
        )
        self.canvas.set_artifact_proposals(self._artifact_proposals)
        self._artifact_proposal_selection_changed()

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
        self._artifact_proposals = []
        self.artifact_proposal_list.clear()
        self._refresh()

    def _scan_artifacts(self) -> None:
        if self._frame is None:
            self.artifact_status.setText("현재 프레임이 없어 후보를 만들 수 없습니다.")
            return
        try:
            proposals = propose_artifact_templates(
                self._frame,
                self._working,
            )
        except Exception as exc:
            self.artifact_status.setText(f"후보 생성 실패: {exc}")
            return

        self._artifact_proposals = proposals
        self.artifact_proposal_list.clear()
        for index, template in enumerate(proposals):
            item = QListWidgetItem(
                f"{index + 1}. {template.kind} · Y {template.center_y:.3f}"
            )
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.artifact_proposal_list.addItem(item)
        self.artifact_status.setText(
            f"{len(proposals)}개 후보를 표시했습니다. 선택 전에는 Profile에 반영되지 않습니다."
        )
        self._refresh()

    def _accept_artifact(self) -> None:
        items = self.artifact_proposal_list.selectedItems()
        if not items:
            self.artifact_status.setText("먼저 Artifact 후보를 선택하세요.")
            return
        existing_ids = {
            template.id for template in self._working.geometry.artifact_templates
        }
        added = 0
        for item in items:
            index = int(item.data(Qt.ItemDataRole.UserRole))
            template = self._artifact_proposals[index]
            if template.id in existing_ids:
                continue
            self._working.geometry.artifact_templates.append(template)
            existing_ids.add(template.id)
            added += 1
        self.artifact_status.setText(
            f"선택한 후보 {added}개를 Artifact로 지정했습니다. "
            "적용 버튼을 눌러 Profile에 저장하세요."
        )
        self._refresh()

    def _artifact_proposal_selection_changed(self) -> None:
        proposal_ids = {
            self._artifact_proposals[int(item.data(Qt.ItemDataRole.UserRole))].id
            for item in self.artifact_proposal_list.selectedItems()
            if 0
            <= int(item.data(Qt.ItemDataRole.UserRole))
            < len(self._artifact_proposals)
        }
        self.canvas.set_highlighted_artifact_proposals(proposal_ids)

    def _delete_artifact(self) -> None:
        item = self.artifact_template_list.currentItem()
        if item is None:
            return
        template_id = str(item.data(Qt.ItemDataRole.UserRole))
        self._working.geometry.artifact_templates = [
            template
            for template in self._working.geometry.artifact_templates
            if template.id != template_id
        ]
        self.artifact_status.setText("선택한 Artifact 지정을 삭제했습니다.")
        self._refresh()
