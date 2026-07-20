from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox, QDoubleSpinBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QVBoxLayout, QWizard, QWizardPage,
)

from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader


class NewRecipeWizard(QWizard):
    skipRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("새 Recipe Wizard")
        self.skipped = False
        self.video_path = QLineEdit(); browse = QPushButton("찾아보기")
        browse.clicked.connect(self._browse)
        video_row = QHBoxLayout(); video_row.addWidget(self.video_path); video_row.addWidget(browse)
        self.metadata = QLabel("영상이 선택되지 않았습니다.")
        page1 = QWizardPage(); page1.setTitle("영상 선택")
        p1 = QVBoxLayout(page1); p1.addLayout(video_row); p1.addWidget(self.metadata)
        skip = QPushButton("Wizard 건너뛰기"); skip.clicked.connect(self._skip); p1.addWidget(skip)
        self.addPage(page1)

        page2 = QWizardPage(); page2.setTitle("시험 시간 조건")
        form2 = QFormLayout(page2)
        self.start = _spin(); self.end = _spin(); self.compressor = _spin(); self.sampling = _spin(); self.sampling.setValue(2.0)
        form2.addRow("분석 시작 (s)", self.start); form2.addRow("분석 종료 (s)", self.end)
        form2.addRow("압축기 기동 (s)", self.compressor); form2.addRow("Sampling FPS", self.sampling)
        self.addPage(page2)

        page3 = QWizardPage(); page3.setTitle("Recipe 기본 정보")
        form3 = QFormLayout(page3)
        self.recipe_name = QLineEdit("Untitled Recipe"); self.description = QTextEdit(); self.create_glass = QCheckBox("기본 Glass A 생성"); self.create_glass.setChecked(True)
        form3.addRow("Recipe 이름", self.recipe_name); form3.addRow("메모", self.description); form3.addRow(self.create_glass)
        self.addPage(page3)
        self._video_metadata = None

    @property
    def video_metadata(self): return self._video_metadata

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "영상 선택", "", "Video (*.mp4 *.mkv *.avi *.mov);;All files (*)")
        if not path: return
        self.video_path.setText(path)
        try:
            reader = OpenCvVideoReader(path); metadata = reader.metadata; reader.close(); self._video_metadata = metadata
            self.end.setValue(metadata.duration_sec)
            self.sampling.setMaximum(max(0.1, metadata.fps)); self.sampling.setValue(min(2.0, metadata.fps))
            self.metadata.setText(f"{Path(path).name}\n{metadata.width}×{metadata.height}, {metadata.fps:.3f} FPS, {metadata.duration_sec:.3f}s, {metadata.frame_count} frames, codec {metadata.codec}")
        except Exception as exc:
            self._video_metadata = None; self.metadata.setText(f"열기 실패: {exc}")

    def _skip(self) -> None:
        self.skipped = True; self.skipRequested.emit(); self.accept()


def _spin() -> QDoubleSpinBox:
    box = QDoubleSpinBox(); box.setRange(0, 1_000_000); box.setDecimals(3); box.setKeyboardTracking(False); return box
