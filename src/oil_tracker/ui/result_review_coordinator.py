from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QPushButton,
    QStyle,
    QToolBar,
    QToolButton,
    QVBoxLayout,
)

from oil_tracker.ui.controllers.redetection_controller import RedetectionController
from oil_tracker.ui.redetection_comparison_coordinator import RedetectionComparisonCoordinator
from oil_tracker.ui.redetection_result_review_window import RedetectionResultReviewWindow
from oil_tracker.ui.result_actions import ResultActionService
from oil_tracker.ui.truth_annotation_coordinator import TruthAnnotationCoordinator


class ResultReviewCoordinator(QObject):
    """Own the single review window without coupling its playback to Workbench state."""

    def __init__(
        self,
        window,
        action_service: ResultActionService | None = None,
        same_profile_coordinator=None,
        redetection_service=None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.action_service = action_service or ResultActionService()
        self.same_profile_coordinator = same_profile_coordinator
        self.redetection_service = redetection_service
        self.viewer: RedetectionResultReviewWindow | None = None
        self.redetection_controller: RedetectionController | None = None
        self.redetection_coordinator: RedetectionComparisonCoordinator | None = None
        self.truth_coordinator: TruthAnnotationCoordinator | None = None
        self.action = QAction(
            window.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            "결과 검토",
            window,
        )
        window.actions["review"] = self.action
        toolbar = window.findChild(QToolBar, "mainToolBar")
        if toolbar is not None:
            toolbar.insertAction(window.actions.get("debug"), self.action)
            button = toolbar.widgetForAction(self.action)
            if isinstance(button, QToolButton):
                button.setObjectName("toolbarButton")
                button.setCursor(Qt.CursorShape.PointingHandCursor)
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
            self.viewer = RedetectionResultReviewWindow(
                action_service=self.action_service,
                parent=self.window,
            )
            self.truth_coordinator = TruthAnnotationCoordinator(
                self.viewer,
                parent=self.viewer,
            )
            self.viewer.truthMarkerRequested.connect(self._truth_marker_requested)
            if self.same_profile_coordinator is not None:
                self.viewer.sameProfileRequested.connect(
                    self.same_profile_coordinator.start
                )
            if self.redetection_service is not None:
                self.redetection_controller = RedetectionController(
                    self.redetection_service,
                    self.viewer,
                )
                self.redetection_coordinator = RedetectionComparisonCoordinator(
                    self.window,
                    self.viewer,
                    self.redetection_controller,
                    self.viewer,
                )
        loaded = self.viewer.load_bundle(path)
        if loaded:
            self.viewer.show()
            self.viewer.raise_()
            self.viewer.activateWindow()
        return loaded

    def _truth_marker_requested(self, annotation_id: str) -> None:
        coordinator = self.truth_coordinator
        if coordinator is None or coordinator.session.truth_set is None:
            return
        annotation = next(
            (
                value
                for value in coordinator.session.truth_set.annotations
                if value.annotation_id == annotation_id
            ),
            None,
        )
        if annotation is not None:
            coordinator.open()
            coordinator.activate_annotation(annotation)

    def close(self) -> None:
        if self.truth_coordinator is not None:
            self.truth_coordinator.close()
            self.truth_coordinator = None
        if self.redetection_coordinator is not None:
            self.redetection_coordinator.close()
            self.redetection_coordinator = None
        self.redetection_controller = None
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def eventFilter(self, watched, event) -> bool:
        if watched is self.window and event.type() == QEvent.Type.Close:
            self.close()
        return super().eventFilter(watched, event)
