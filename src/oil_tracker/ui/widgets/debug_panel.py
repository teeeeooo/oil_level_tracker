from __future__ import annotations

import numpy as np
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


_IMAGE_LABELS = {
    "overlay": "검출 결과 화면",
    "original_roi": "원본 ROI",
    "ellipse_mask": "타원 영역 마스크",
    "effective_mask": "실제 검출 영역",
    "grayscale": "흑백 변환",
    "normalized": "명암 보정",
    "blurred": "노이즈 완화",
    "sobel": "수평 경계 강도",
    "canny": "경계 검출",
    "horizontal_mask": "수평 경계 마스크",
    "glare_mask": "빛 반사 영역",
    "exclusion_mask": "검출 제외 영역",
    "static_artifact_map": "고정 반사·잔류물 영역",
    "foam_mask": "하단 연결 거품 영역",
    "foam_variance": "거품 질감 점수",
}


class DebugPanel(QWidget):
    exportRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(760, 560)
        self.tabs = QTabWidget()
        self.tabs.setMinimumSize(720, 500)
        self.image_labels = {}
        groups = {
            "검출 화면": ["overlay"],
            "ROI 상세보기": [
                "original_roi",
                "ellipse_mask",
                "effective_mask",
                "grayscale",
                "normalized",
                "blurred",
            ],
            "경계 / 마스크": [
                "sobel",
                "canny",
                "horizontal_mask",
                "glare_mask",
                "exclusion_mask",
                "static_artifact_map",
            ],
            "거품": ["foam_mask", "foam_variance"],
        }
        for title, keys in groups.items():
            page = QWidget()
            page_layout = QVBoxLayout(page)
            for key in keys:
                heading = QLabel(_IMAGE_LABELS[key])
                heading.setObjectName("debugImageTitle")
                label = QLabel("분석 결과 없음")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setMinimumSize(720, 360)
                page_layout.addWidget(heading)
                page_layout.addWidget(label)
                self.image_labels[key] = label
            page_layout.addStretch(1)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setWidget(page)
            self.tabs.addTab(scroll, title)

        self.candidates = QTableWidget()
        self.tabs.addTab(self.candidates, "후보 점수")
        self.state = QTextEdit()
        self.state.setReadOnly(True)
        self.tabs.addTab(self.state, "상태")
        self.export = QPushButton("현재 장면 상세 정보 내보내기")
        self.export.clicked.connect(self.exportRequested)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.export)
        self._artifacts = None

    @property
    def artifacts(self):
        return self._artifacts

    def set_artifacts(self, artifacts) -> None:
        self._artifacts = artifacts
        if artifacts is None:
            return
        for key, label in self.image_labels.items():
            image = artifacts.images.get(key)
            if image is not None:
                label.setPixmap(
                    _pixmap(image).scaled(
                        900,
                        520,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
        rows = artifacts.candidate_rows
        columns = [
            "rank", "kind", "source", "y", "edge_strength", "horizontal_coverage",
            "region_contrast", "temporal_score", "glare_penalty", "border_penalty",
            "jump_penalty", "final_score", "selected", "rejected", "reject_reason",
        ]
        self.candidates.setColumnCount(len(columns))
        self.candidates.setHorizontalHeaderLabels(columns)
        self.candidates.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, key in enumerate(columns):
                self.candidates.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(str(row.get(key, ""))),
                )
        self.candidates.resizeColumnsToContents()
        self.state.setPlainText("\n".join(f"{key}: {value}" for key, value in artifacts.state.items()))


def _pixmap(image: np.ndarray) -> QPixmap:
    if image.ndim == 2:
        arr = np.ascontiguousarray(image)
        qimage = QImage(
            arr.data,
            arr.shape[1],
            arr.shape[0],
            arr.strides[0],
            QImage.Format.Format_Grayscale8,
        ).copy()
    else:
        arr = np.ascontiguousarray(image[:, :, ::-1])
        qimage = QImage(
            arr.data,
            arr.shape[1],
            arr.shape[0],
            arr.strides[0],
            QImage.Format.Format_RGB888,
        ).copy()
    return QPixmap.fromImage(qimage)
