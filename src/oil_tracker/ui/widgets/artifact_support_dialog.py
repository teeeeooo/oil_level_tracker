"""Optional reference review with no implicit rectangle/component labelling."""
from __future__ import annotations

from dataclasses import replace
import math

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout,
)

from oil_tracker.application.ports.review_io import ArtifactReferenceReviewPort
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas


class SupportReviewCanvas(VideoOverlayCanvas):
    """Reuse image/zoom/fit owner; a drag restricts review, never adds an exclusion."""
    reviewRectChanged = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 220)
        self.review_rect = None
        self._review_start = None
        self._review_item = None
        self.read_only = False

    def set_review_rect(self, rect):
        self.review_rect = rect
        self._draw_review_rect()
        self.reviewRectChanged.emit(rect)

    def rebuild_overlays(self):
        super().rebuild_overlays()
        self._review_item = None
        self._draw_review_rect()

    def _draw_review_rect(self):
        if self._review_item is not None:
            self.scene().removeItem(self._review_item)
            self._review_item = None
        if self.review_rect is not None:
            pen = QPen(QColor("#ffbd59"), 1, Qt.PenStyle.DashLine)
            pen.setCosmetic(True)
            self._review_item = self.scene().addRect(QRectF(*self.review_rect), pen)
            self._review_item.setZValue(50)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.read_only:
            self._review_start = self.mapToScene(event.position().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._review_start is not None:
            self._drag_to(self.mapToScene(event.position().toPoint()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._review_start is not None and event.button() == Qt.MouseButton.LeftButton:
            self._drag_to(self.mapToScene(event.position().toPoint()))
            self._review_start = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _drag_to(self, point):
        rect = QRectF(self._review_start, point).normalized().intersected(self.sceneRect())
        x, y = math.floor(rect.left()), math.floor(rect.top())
        right, bottom = math.ceil(rect.right()), math.ceil(rect.bottom())
        self.set_review_rect((x, y, right-x, bottom-y) if not rect.isEmpty() else None)


class ArtifactSupportDialog(QDialog):
    def __init__(self, template, glass, frame_width, frame_height, parent=None, *,
                 reference_reviewer: ArtifactReferenceReviewPort | None = None):
        super().__init__(parent)
        self.setWindowTitle("Artifact 원본·윤곽 확인")
        self.setSizeGripEnabled(True)
        self.resize(900, 620)
        available = self.screen().availableGeometry()
        self.resize(min(900, int(available.width() * 0.9)), min(620, int(available.height() * 0.9)))
        self._reference = template.support_reference
        self._reviewer = reference_reviewer
        self._result = self._reference
        self._images = None
        self._editable = False
        self._crop_origin = (0, 0)
        self._proposal_rect = None
        layout = QVBoxLayout(self)
        self.info = QLabel()
        self.info.setWordWrap(True)
        layout.addWidget(self.info)
        hint = QLabel("드래그해 확인할 범위를 좁히세요. 청록색은 범위 안의 보이는 원본 윤곽입니다. "
                      "상자 전체나 연결된 다른 윤곽은 지정되지 않습니다. 휠로 확대, 가운데 버튼으로 이동할 수 있습니다.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        toolbar = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItem("원본 + 확인할 윤곽", "review")
        self.mode.addItem("원본만 보기", "original_roi")
        self.mode.addItem("후보 위치 가이드 (실제 윤곽 아님)", "proposal")
        self.mode.addItem("원본 Canny 윤곽", "canny")
        self.mode.addItem("처리된 수평 지지 마스크", "horizontal_mask")
        toolbar.addWidget(self.mode, 1)
        clear = QPushButton("범위 지우기")
        fit = QPushButton("화면에 맞춤")
        toolbar.addWidget(clear)
        toolbar.addWidget(fit)
        layout.addLayout(toolbar)
        self.canvas = SupportReviewCanvas()
        layout.addWidget(self.canvas, 1)
        self.confirm_edges = QCheckBox("청록색으로 표시된 윤곽 부분을 구조물로 확인함")
        layout.addWidget(self.confirm_edges)
        self.status = QLabel("범위만 저장하면 윤곽의 정체성은 판단 보류로 남습니다. 기존 검출 제외 범위는 바뀌지 않습니다.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("판독 근거 저장")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("닫기 / 취소")
        layout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.mode.currentIndexChanged.connect(self._render)
        self.canvas.reviewRectChanged.connect(self._rect_changed)
        self.confirm_edges.toggled.connect(self._render)
        clear.clicked.connect(lambda: self.canvas.set_review_rect(None))
        fit.clicked.connect(self.canvas.fit_to_view)
        try:
            if self._reference is None:
                raise ValueError("저장된 원본이 없는 기존 템플릿입니다. 현재 화면으로 대체하지 않습니다.")
            if self._reviewer is None:
                raise ValueError("원본 근거 표시 서비스가 구성되지 않았습니다.")
            snapshot, self._images = self._reviewer.load(self._reference)
            self._crop_origin = snapshot["crop_origin"]
            source_rect = snapshot["proposal"]["envelope_source_xywh"]
            self._proposal_rect = QRectF(source_rect[0] - self._crop_origin[0], source_rect[1] - self._crop_origin[1],
                                        source_rect[2], source_rect[3])
            status = self._reference.correspondence_status(glass, frame_width, frame_height, template)
            self._editable = status == "bound_reference"
            self.canvas.set_frame(self._images["original_roi"])
            self.canvas.set_review_rect(self._reference.review_rect)
            self.confirm_edges.setChecked(self._reference.review_state == "reviewed_support")
            proposal = snapshot["proposal"]
            self.info.setText(
                f"{template.name} · {proposal['source']} · Y {proposal['y']}\n"
                f"원본 프레임 {snapshot['frame_index']} / {snapshot['time_sec']}초 · "
                f"원본 좌표 시작 {snapshot['crop_origin']} · 저장 크기 {snapshot['crop_size']}\n"
                + ("일부 주변 영역은 저장 범위 밖입니다. " if snapshot['context_clipped'] else "")
                + ("" if self._editable else "분석 영역·크기·설정이 달라 이전 근거를 보기만 할 수 있습니다.")
            )
        except (ValueError, TypeError, KeyError) as exc:
            self._editable = False
            self._images = None
            self.info.setText(f"원본 근거를 사용할 수 없습니다: {exc}")
        self.canvas.read_only = not self._editable
        self.confirm_edges.setEnabled(self._editable)
        clear.setEnabled(self._editable)
        if self._images is not None and "foam_material_support_mask" in self._images:
            self.mode.addItem("Foam 지지 마스크", "foam_material_support_mask")
        self._render()

    def _rect_changed(self, _rect):
        # A changed scope needs a new explicit confirmation.
        self.confirm_edges.setChecked(False)
        self._render()

    def _render(self, *_args):
        count = 0
        if self._images is not None:
            key = self.mode.currentData()
            image, count = self._reviewer.render(self._images, self.canvas.review_rect, key)
            self.canvas.set_frame(image)
            if key == "proposal" and self._proposal_rect is not None:
                pen = QPen(QColor("#eeeeee"), 1, Qt.PenStyle.DashLine)
                pen.setCosmetic(True)
                self.canvas.scene().addRect(self._proposal_rect, pen)
        self.confirm_edges.setEnabled(self._editable and count > 0 and self.mode.currentData() == "review")
        rect = self.canvas.review_rect
        if self._images is not None:
            scope = (f"원본 X {rect[0]+self._crop_origin[0]}–{rect[0]+rect[2]+self._crop_origin[0]}, "
                     f"Y {rect[1]+self._crop_origin[1]}–{rect[1]+rect[3]+self._crop_origin[1]} · 윤곽 {count}px. "
                     if rect is not None else "확인 범위 미지정. ")
            self.status.setText(scope + "범위만 저장하면 판단 보류입니다. 기존 검출 제외 범위는 바뀌지 않습니다.")
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            self._editable and (not self.confirm_edges.isChecked() or count > 0)
        )

    def accept(self):
        if not self.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled():
            return
        rect = self.canvas.review_rect
        self._result = replace(self._reference, review_rect=rect,
                               review_state="reviewed_support" if self.confirm_edges.isChecked()
                               else "mixed_or_uncertain" if rect is not None else "proposal_negative")
        super().accept()

    def reviewed_reference(self):
        return self._result
