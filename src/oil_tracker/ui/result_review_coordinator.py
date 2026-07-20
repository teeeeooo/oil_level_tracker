from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QPushButton,
    QStyle,
    QToolBar,
    QVBoxLayout,
)

from oil_tracker.ui.result_review_window import ResultReviewWindow


class ResultReviewCoordinator(QObject):
    """Own the single review window without coupling it to Workbench state."""

    def __init__(self, window) -> None:
        super().__init__(window)
        self.window = window
        self.viewer: ResultReviewWindow | None = None
        self.action = QAction(
            window.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            "결과 검토",
            window,
        )
        window.actions["review"] = self.action
        toolbar = window.findChild(QToolBar, "mainToolBar")
        if toolbar is not None:
            toolbar.addAction(self.action)
        self.action.triggered.connect(self.open_dialog)
        window.installEventFilter(self)

    def open_dialog(self) -> None:
        recent = Path(self.window.last_result_path) if self.window.last_result_path else None
        dialog = QDialog(self.window)
        dialog.setWindowTitle("결과 검토 열기")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("검토할 분석 결과 bundle을 선택해 주세요."))
        recent_button = QPushButton("최근 결과 열기")
        recent_button.setEnabled(recent is not None and recent.is_dir())
        other_button = QPushButton("다른 결과 폴더 선택")
        cancel_button = QPushButton("취소")
        layout.addWidget(recent_button)
        layout.addWidget(other_button)
        layout.addWidget(cancel_button)
        selected: dict[str, Path] = {}

        def choose_recent() -> None:
            if recent is not None:
                selected["path"] = recent
                dialog.accept()

        def choose_other() -> None:
            directory = QFileDialog.getExistingDirectory(
                dialog,
                "분석 결과 bundle 폴더 선택",
                str(recent.parent if recent is not None else Path.home()),
            )
            if directory:
                selected["path"] = Path(directory)
                dialog.accept()

        recent_button.clicked.connect(choose_recent)
        other_button.clicked.connect(choose_other)
        cancel_button.clicked.connect(dialog.reject)
        if dialog.exec() == QDialog.DialogCode.Accepted and "path" in selected:
            self.open_bundle(selected["path"])

    def open_bundle(self, path: str | Path) -> bool:
        if self.viewer is None:
            self.viewer = ResultReviewWindow(parent=self.window)
        loaded = self.viewer.load_bundle(path)
        if loaded:
            self.viewer.show()
            self.viewer.raise_()
            self.viewer.activateWindow()
        return loaded

    def close(self) -> None:
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def eventFilter(self, watched, event) -> bool:
        if watched is self.window and event.type() == QEvent.Type.Close:
            self.close()
        return super().eventFilter(watched, event)
