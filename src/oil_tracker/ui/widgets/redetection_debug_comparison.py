from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QSplitter, QVBoxLayout, QWidget

from oil_tracker.ui.widgets.result_debug_panel import ResultDebugPanel


class RedetectionDebugComparison(QWidget):
    officialArtifactRequested = Signal(str)
    rerunArtifactRequested = Signal(str)

    def __init__(self, *, artifact_only: bool, parent=None) -> None:
        super().__init__(parent)
        self.artifact_only = artifact_only
        self.message = QLabel()
        self.message.setWordWrap(True)
        self.official = ResultDebugPanel()
        self.rerun = ResultDebugPanel()
        self.official.export_button.hide()
        self.rerun.export_button.hide()
        if artifact_only:
            self.official.tabs.setTabVisible(0, False)
            self.official.tabs.setTabVisible(1, False)
            self.rerun.tabs.setTabVisible(0, False)
            self.rerun.tabs.setTabVisible(1, False)
            self.official.tabs.setCurrentIndex(2)
            self.rerun.tabs.setCurrentIndex(2)
        else:
            self.official.tabs.setTabVisible(1, False)
            self.official.tabs.setTabVisible(2, False)
            self.rerun.tabs.setTabVisible(1, False)
            self.rerun.tabs.setTabVisible(2, False)
            self.official.tabs.setCurrentIndex(0)
            self.rerun.tabs.setCurrentIndex(0)
        split = QSplitter()
        split.addWidget(self.official)
        split.addWidget(self.rerun)
        split.setSizes([600, 600])
        layout = QVBoxLayout(self)
        layout.addWidget(self.message)
        layout.addWidget(split, 1)
        self.official.artifactRequested.connect(self.officialArtifactRequested)
        self.rerun.artifactRequested.connect(self.rerunArtifactRequested)
        self.clear()

    def clear(self, message: str = "comparison sample을 선택해 주세요.") -> None:
        self.message.setText(message)
        self.official.clear("공식 debug record 없음")
        self.rerun.clear("재검출 debug record 없음")

    def set_records(self, official_record, rerun_record, *, official_message: str = "") -> None:
        if official_record is None:
            self.official.clear(
                official_message
                or "공식 분석 당시 후보 상세가 저장되지 않아 candidate 단위 비교는 제공할 수 없습니다."
            )
        else:
            self.official.set_record(official_record)
        if rerun_record is None:
            self.rerun.clear("선택한 재검출 sample에 debug record가 없습니다.")
        else:
            self.rerun.set_record(rerun_record)
        self.message.setText(
            "왼쪽: 공식 분석 · 오른쪽: 임시 설정 재검출"
            if official_record is not None
            else "공식 debug baseline 없이 재검출 후보와 artifact만 표시합니다."
        )

    def set_official_artifact(self, key: str, image, error: str = "") -> None:
        self.official.set_artifact(key, image, error)

    def set_rerun_artifact(self, key: str, image, error: str = "") -> None:
        self.rerun.set_artifact(key, image, error)
