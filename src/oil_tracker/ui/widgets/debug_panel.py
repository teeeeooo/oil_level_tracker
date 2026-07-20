from __future__ import annotations

import numpy as np
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit, QVBoxLayout, QWidget


class DebugPanel(QWidget):
    exportRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.tabs = QTabWidget()
        self.image_labels = {}
        groups = {
            "Overlay": ["overlay"],
            "ROI / Preprocess": ["original_roi", "ellipse_mask", "effective_mask", "grayscale", "normalized", "blurred"],
            "Edges / Masks": ["sobel", "canny", "horizontal_mask", "glare_mask", "exclusion_mask", "static_artifact_map"],
            "Foam": ["foam_mask", "foam_variance"],
        }
        for title, keys in groups.items():
            page = QWidget(); layout = QVBoxLayout(page)
            for key in keys:
                label = QLabel(key); label.setAlignment(Qt.AlignmentFlag.AlignCenter); label.setMinimumHeight(120)
                layout.addWidget(label); self.image_labels[key] = label
            scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(page); self.tabs.addTab(scroll, title)
        self.candidates = QTableWidget(); self.tabs.addTab(self.candidates, "Candidates")
        self.state = QTextEdit(); self.state.setReadOnly(True); self.tabs.addTab(self.state, "State")
        self.export = QPushButton("선택 frame debug export"); self.export.clicked.connect(self.exportRequested)
        layout = QVBoxLayout(self); layout.addWidget(self.tabs); layout.addWidget(self.export)
        self._artifacts = None

    @property
    def artifacts(self): return self._artifacts

    def set_artifacts(self, artifacts) -> None:
        self._artifacts = artifacts
        if artifacts is None: return
        for key, label in self.image_labels.items():
            image = artifacts.images.get(key)
            if image is not None:
                label.setPixmap(_pixmap(image).scaled(640, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        rows = artifacts.candidate_rows
        columns = ["rank", "kind", "source", "y", "edge_strength", "horizontal_coverage", "region_contrast", "temporal_score", "glare_penalty", "border_penalty", "jump_penalty", "final_score", "selected", "rejected", "reject_reason"]
        self.candidates.setColumnCount(len(columns)); self.candidates.setHorizontalHeaderLabels(columns); self.candidates.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, key in enumerate(columns): self.candidates.setItem(r, c, QTableWidgetItem(str(row.get(key, ""))))
        self.candidates.resizeColumnsToContents()
        self.state.setPlainText("\n".join(f"{k}: {v}" for k, v in artifacts.state.items()))


def _pixmap(image: np.ndarray) -> QPixmap:
    if image.ndim == 2:
        arr = np.ascontiguousarray(image); q = QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format.Format_Grayscale8).copy()
    else:
        arr = np.ascontiguousarray(image[:, :, ::-1]); q = QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format.Format_RGB888).copy()
    return QPixmap.fromImage(q)
