from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from oil_tracker.application.ports.video_reader import VideoReaderFactory
from oil_tracker.ui.widgets.video_preview_widget import VideoPreviewWidget


class NewRecipeWizard(QWizard):
    skipRequested = Signal()

    def __init__(self, parent=None, *, reader_factory: VideoReaderFactory) -> None:
        super().__init__(parent)
        self.reader_factory = reader_factory
        self.setWindowTitle("새 분석 프로필 만들기")
        self.setMinimumSize(960, 700)
        self.resize(1120, 800)
        self.setButtonText(QWizard.WizardButton.BackButton, "이전")
        self.setButtonText(QWizard.WizardButton.NextButton, "다음")
        self.setButtonText(QWizard.WizardButton.FinishButton, "완료")
        self.setButtonText(QWizard.WizardButton.CancelButton, "취소")
        self.skipped = False
        self._video_metadata = None

        self.video_path = QLineEdit()
        self.video_path.setReadOnly(True)
        browse = QPushButton("영상 찾아보기")
        browse.clicked.connect(self._browse)
        video_row = QHBoxLayout()
        video_row.addWidget(self.video_path, 1)
        video_row.addWidget(browse)
        self.metadata = QLabel("분석할 시험 영상을 선택해 주세요.")
        self.metadata.setWordWrap(True)
        self.metadata.setObjectName("metadataCard")
        page1 = QWizardPage()
        page1.setTitle("1. 시험 영상 선택")
        page1.setSubTitle("유면을 확인할 녹화 영상을 선택합니다.")
        page1.registerField("videoPath*", self.video_path)
        p1 = QVBoxLayout(page1)
        p1.addLayout(video_row)
        p1.addWidget(self.metadata)
        p1.addStretch(1)
        skip = QPushButton("영상 없이 빈 설정 화면으로 시작")
        skip.clicked.connect(self._skip)
        p1.addWidget(skip)
        self.addPage(page1)

        page2 = QWizardPage()
        page2.setTitle("2. 분석 시간 설정")
        page2.setSubTitle("영상을 재생하거나 이동한 뒤 현재 위치를 각 시간으로 지정합니다.")
        page2_layout = QVBoxLayout(page2)
        page2_layout.setContentsMargins(4, 4, 4, 4)
        page2_layout.setSpacing(6)
        self.preview = VideoPreviewWidget(reader_factory=reader_factory)
        self.preview.videoError.connect(
            lambda message: QMessageBox.warning(self, "영상 미리보기 오류", message)
        )
        page2_layout.addWidget(self.preview, 1)

        time_group = QGroupBox("현재 위치 기준 시간 지정")
        time_grid = QGridLayout(time_group)
        time_grid.setContentsMargins(8, 8, 8, 8)
        time_grid.setHorizontalSpacing(8)
        time_grid.setVerticalSpacing(4)
        self.start = _time_spin()
        self.end = _time_spin()
        self.compressor = _time_spin()
        self.sampling = _spin()
        self.sampling.setDecimals(2)
        self.sampling.setRange(0.1, 240.0)
        self.sampling.setSuffix(" 회/초")
        self.sampling.setValue(2.0)
        self.set_start = QPushButton("현재 위치")
        self.set_end = QPushButton("현재 위치")
        self.set_compressor = QPushButton("현재 위치")
        fields = (
            (0, "분석 시작", self.start, self.set_start),
            (2, "분석 종료", self.end, self.set_end),
            (4, "압축기 기동", self.compressor, self.set_compressor),
        )
        for column, label, spin, button in fields:
            time_grid.addWidget(QLabel(label), 0, column, 1, 2)
            time_grid.addWidget(spin, 1, column)
            time_grid.addWidget(button, 1, column + 1)
            time_grid.setColumnStretch(column, 1)
        time_grid.addWidget(QLabel("분석 빈도"), 0, 6)
        time_grid.addWidget(self.sampling, 1, 6)
        time_grid.setColumnStretch(6, 1)
        page2_layout.addWidget(time_group)
        self.addPage(page2)

        self.set_start.clicked.connect(lambda: self._set_current_time(self.start))
        self.set_end.clicked.connect(lambda: self._set_current_time(self.end))
        self.set_compressor.clicked.connect(lambda: self._set_current_time(self.compressor))
        for spin in (self.start, self.end, self.compressor):
            spin.valueChanged.connect(self._update_markers)

        page3 = QWizardPage()
        page3.setTitle("3. 분석 프로필 정보")
        page3.setSubTitle("반복해서 사용할 설정의 이름과 메모를 입력합니다.")
        form3 = QFormLayout(page3)
        self.recipe_name = QLineEdit("새 유면 분석 프로필")
        self.description = QTextEdit()
        self.description.setPlaceholderText("시험 조건이나 관찰 목적을 기록할 수 있습니다.")
        self.create_glass = QCheckBox("기본 유면 관찰창 1개 만들기")
        self.create_glass.setChecked(True)
        form3.addRow("프로필 이름", self.recipe_name)
        form3.addRow("메모", self.description)
        form3.addRow(self.create_glass)
        self.addPage(page3)

    @property
    def video_metadata(self):
        return self._video_metadata

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "시험 영상 선택",
            "",
            "영상 파일 (*.mp4 *.mkv *.avi *.mov);;모든 파일 (*)",
        )
        if not path:
            return
        try:
            reader = None
            try:
                reader = self.reader_factory(path)
                metadata = reader.metadata
            finally:
                if reader is not None:
                    reader.close()
            self._video_metadata = metadata
            self.video_path.setText(path)
            self.start.setMaximum(metadata.duration_sec)
            self.end.setMaximum(metadata.duration_sec)
            self.compressor.setMaximum(metadata.duration_sec)
            self.end.setValue(metadata.duration_sec)
            self.sampling.setMaximum(max(0.1, metadata.fps))
            self.sampling.setValue(min(2.0, metadata.fps))
            self.metadata.setText(
                f"파일: {Path(path).name}\n"
                f"크기: {metadata.width} × {metadata.height}\n"
                f"영상 속도: {metadata.fps:.3f} 장면/초\n"
                f"전체 길이: {metadata.duration_sec:.3f}초 · 장면 수: {metadata.frame_count}\n"
                f"코덱: {metadata.codec or '확인 불가'}"
            )
            self.preview.open_video(path)
            self._update_markers()
        except Exception as exc:
            self._video_metadata = None
            self.video_path.clear()
            self.metadata.setText(f"영상을 열 수 없습니다.\n{exc}")
            QMessageBox.warning(self, "영상 열기 실패", str(exc))

    def _set_current_time(self, spin: QDoubleSpinBox) -> None:
        spin.setValue(self.preview.current_timestamp)
        self._update_markers()

    def _update_markers(self, *_args) -> None:
        self.preview.set_markers(self.start.value(), self.end.value(), self.compressor.value())

    def validateCurrentPage(self) -> bool:
        if self.currentId() == 1:
            if self.end.value() <= self.start.value():
                QMessageBox.warning(
                    self,
                    "시간 범위 확인",
                    "분석 종료 시각은 분석 시작 시각보다 뒤여야 합니다.",
                )
                return False
            duration = self._video_metadata.duration_sec if self._video_metadata else 0.0
            if self.compressor.value() > duration:
                QMessageBox.warning(
                    self,
                    "기동 시각 확인",
                    "압축기 기동 시각이 영상 길이를 벗어났습니다.",
                )
                return False
        return super().validateCurrentPage()

    def _skip(self) -> None:
        self.skipped = True
        self.skipRequested.emit()
        self.accept()

    def done(self, result: int) -> None:
        self.preview.close_video()
        super().done(result)


def _time_spin() -> QDoubleSpinBox:
    box = _spin()
    box.setSuffix(" 초")
    return box


def _spin() -> QDoubleSpinBox:
    box = QDoubleSpinBox()
    box.setRange(0, 1_000_000)
    box.setDecimals(3)
    box.setKeyboardTracking(False)
    return box
