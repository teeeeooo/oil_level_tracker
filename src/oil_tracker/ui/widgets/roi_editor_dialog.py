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
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.application.ports.review_io import ArtifactProposalPort
from oil_tracker.domain.geometry import ExclusionZone, Rect
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas


class RoiEditorDialog(QDialog):
    """Edit one analysis region on a private copy until the user applies it."""

    def __init__(
        self,
        frame,
        glass,
        frame_width: int,
        frame_height: int,
        parent=None,
        *,
        artifact_proposer: ArtifactProposalPort | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("분석 영역 편집")
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setSizeGripEnabled(True)
        self.setMinimumSize(980, 650)
        self.resize(1280, 800)
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._frame = frame
        self._working = deepcopy(glass)
        self._artifact_proposals = []
        self._artifact_proposer = artifact_proposer

        instruction = QLabel(
            "분석 영역 타원의 파란 조절점을 드래그해 크기를 바꾸고, 노란 기준선을 위아래로 움직이세요. "
            "적용하기 전까지 원래 프로필은 변경되지 않습니다."
        )
        instruction.setWordWrap(True)
        instruction.setObjectName("roiEditorHint")

        self.canvas = VideoOverlayCanvas()
        self.canvas.setMinimumSize(520, 320)
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
        artifact_group.setMinimumWidth(350)
        artifact_layout = QVBoxLayout(artifact_group)
        artifact_hint = QLabel(
            "현재 화면에서 detector가 제안한 고정 반사·흠집 후보를 선택하면 "
            "정규화된 점·선·구역 템플릿으로 저장됩니다. 같은 Y 전체를 제외하지 않습니다."
        )
        artifact_hint.setWordWrap(True)
        artifact_layout.addWidget(artifact_hint)

        self.scan_artifacts_button = QPushButton("Detector 후보 찾기")
        self.scan_artifacts_button.setObjectName("primaryArtifactAction")
        artifact_layout.addWidget(self.scan_artifacts_button)

        artifact_buttons = QHBoxLayout()
        self.select_all_artifacts_button = QPushButton("모든 후보 선택")
        self.accept_artifact_button = QPushButton("선택 후보 일괄 Artifact 지정")
        artifact_buttons.addWidget(self.select_all_artifacts_button)
        artifact_buttons.addWidget(self.accept_artifact_button, 1)
        artifact_layout.addLayout(artifact_buttons)

        self.artifact_status = QLabel("후보 찾기를 실행한 뒤 필요한 항목만 선택하세요.")
        self.artifact_status.setObjectName("ownershipHint")
        self.artifact_status.setWordWrap(True)
        artifact_layout.addWidget(self.artifact_status)

        self.artifact_proposal_list = QListWidget()
        self.artifact_proposal_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.artifact_template_list = QListWidget()
        self.artifact_template_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        proposal_panel = QWidget()
        proposal_layout = QVBoxLayout(proposal_panel)
        proposal_layout.setContentsMargins(0, 0, 0, 0)
        proposal_layout.addWidget(QLabel("Detector 제안 후보"))
        proposal_layout.addWidget(self.artifact_proposal_list, 1)
        template_panel = QWidget()
        template_layout = QVBoxLayout(template_panel)
        template_layout.setContentsMargins(0, 0, 0, 0)
        template_layout.addWidget(QLabel("지정된 Artifact"))
        template_layout.addWidget(self.artifact_template_list, 1)
        artifact_lists = QSplitter(Qt.Orientation.Vertical)
        artifact_lists.setChildrenCollapsible(False)
        artifact_lists.addWidget(proposal_panel)
        artifact_lists.addWidget(template_panel)
        artifact_lists.setStretchFactor(0, 3)
        artifact_lists.setStretchFactor(1, 2)
        artifact_lists.setSizes([280, 180])
        artifact_layout.addWidget(artifact_lists, 1)

        template_buttons = QHBoxLayout()
        self.select_all_templates_button = QPushButton("지정 Artifact 모두 선택")
        self.clear_template_selection_button = QPushButton("선택 해제")
        self.delete_artifact_button = QPushButton("선택 Artifact 일괄 삭제")
        template_buttons.addWidget(self.select_all_templates_button)
        template_buttons.addWidget(self.clear_template_selection_button)
        template_buttons.addWidget(self.delete_artifact_button, 1)
        artifact_layout.addLayout(template_buttons)
        self.artifact_group = artifact_group
        self.artifact_lists_splitter = artifact_lists

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("적용")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(instruction)
        video_panel = QWidget()
        video_layout = QVBoxLayout(video_panel)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(7)
        video_layout.addWidget(self.canvas, 1)
        video_layout.addLayout(controls)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        splitter.addWidget(video_panel)
        splitter.addWidget(artifact_group)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([790, 450])
        self.content_splitter = splitter
        self.video_panel = video_panel
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
        self.select_all_templates_button.clicked.connect(
            self.artifact_template_list.selectAll
        )
        self.clear_template_selection_button.clicked.connect(
            self.artifact_template_list.clearSelection
        )
        self.delete_artifact_button.clicked.connect(self._delete_artifact)
        self.artifact_proposal_list.itemSelectionChanged.connect(
            self._artifact_proposal_selection_changed
        )
        self.artifact_template_list.itemSelectionChanged.connect(
            self._artifact_template_selection_changed
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
        selected_template_ids = {
            str(item.data(Qt.ItemDataRole.UserRole))
            for item in self.artifact_template_list.selectedItems()
        }
        self.artifact_template_list.clear()
        for template in self._working.geometry.artifact_templates:
            item = QListWidgetItem(f"{template.name} · {template.kind}")
            item.setData(Qt.ItemDataRole.UserRole, template.id)
            self.artifact_template_list.addItem(item)
            if template.id in selected_template_ids:
                item.setSelected(True)
        self._artifact_template_selection_changed()
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
        if self._artifact_proposer is None:
            self.artifact_status.setText("Artifact 후보 생성 서비스가 구성되지 않았습니다.")
            return
        try:
            proposals = self._artifact_proposer.propose(
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

    def _artifact_template_selection_changed(self) -> None:
        template_ids = {
            str(item.data(Qt.ItemDataRole.UserRole))
            for item in self.artifact_template_list.selectedItems()
        }
        count = len(template_ids)
        self.canvas.set_highlighted_artifact_templates(template_ids)
        self.delete_artifact_button.setEnabled(count > 0)
        self.clear_template_selection_button.setEnabled(count > 0)
        self.select_all_templates_button.setEnabled(
            self.artifact_template_list.count() > count
        )
        self.delete_artifact_button.setText(
            f"선택 Artifact {count}개 일괄 삭제"
            if count
            else "선택 Artifact 일괄 삭제"
        )

    def _delete_artifact(self) -> None:
        items = self.artifact_template_list.selectedItems()
        if not items:
            return
        template_ids = {
            str(item.data(Qt.ItemDataRole.UserRole)) for item in items
        }
        if (
            template_ids
            and len(template_ids) == len(self._working.geometry.artifact_templates)
            and QMessageBox.question(
                self,
                "모든 Artifact 지정 삭제",
                "지정된 Artifact를 모두 삭제할까요? 적용 전까지는 원래 Profile이 변경되지 않습니다.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._working.geometry.artifact_templates = [
            template
            for template in self._working.geometry.artifact_templates
            if template.id not in template_ids
        ]
        self.artifact_status.setText(
            f"선택한 Artifact 지정 {len(template_ids)}개를 삭제했습니다. "
            "적용 버튼을 눌러 Profile에 저장하세요."
        )
        self._refresh()
