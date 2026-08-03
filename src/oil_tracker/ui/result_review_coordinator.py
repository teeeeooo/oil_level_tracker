from __future__ import annotations

import logging
import os
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStyle,
    QToolBar,
    QToolButton,
    QVBoxLayout,
)

from oil_tracker.adapters.storage.recent_result_history import RecentResultEntry, RecentResultHistory
from oil_tracker.ui.controllers.redetection_controller import RedetectionController
from oil_tracker.ui.redetection_comparison_coordinator import RedetectionComparisonCoordinator
from oil_tracker.ui.result_actions import ResultActionService
from oil_tracker.ui.truth_annotation_coordinator import TruthAnnotationCoordinator


LOGGER = logging.getLogger(__name__)


class ResultReviewCoordinator(QObject):
    """Own the single review window without coupling its playback to Workbench state."""

    def __init__(
        self,
        window,
        action_service: ResultActionService | None = None,
        same_profile_coordinator=None,
        redetection_service=None,
        viewer_factory=None,
        recent_result_history: RecentResultHistory | None = None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.action_service = action_service or ResultActionService()
        self.same_profile_coordinator = same_profile_coordinator
        self.redetection_service = redetection_service
        self.viewer_factory = viewer_factory
        self.recent_result_history = recent_result_history
        self.viewer = None
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
        entries = self._recent_entries()
        dialog = QDialog(self.window)
        dialog.setWindowTitle("결과 검토 열기")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("최근 분석 결과를 선택하거나 다른 결과 폴더를 직접 열 수 있습니다."))
        recent_list = QListWidget(dialog)
        recent_list.setObjectName("recentResultList")
        selected: dict[str, Path] = {}

        for entry in entries:
            item = QListWidgetItem(self._recent_entry_label(entry))
            item.setData(Qt.ItemDataRole.UserRole, entry.path)
            item.setToolTip(entry.path)
            if not entry.is_available():
                item.setText(item.text() + "\n[경로를 찾을 수 없음]")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            recent_list.addItem(item)
        if not entries:
            empty_item = QListWidgetItem("저장된 최근 결과가 없습니다.")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            recent_list.addItem(empty_item)
        layout.addWidget(recent_list)

        recent_button = QPushButton("선택한 최근 결과 열기")
        recent_button.setObjectName("recentResultOpenButton")
        recent_button.setEnabled(False)
        other_button = QPushButton("다른 결과 폴더 선택")
        other_button.setObjectName("otherResultFolderButton")
        cancel_button = QPushButton("취소")
        cancel_button.setObjectName("resultReviewOpenCancelButton")
        layout.addWidget(recent_button)
        layout.addWidget(other_button)
        layout.addWidget(cancel_button)

        def current_path() -> Path | None:
            item = recent_list.currentItem()
            if item is None or not bool(item.flags() & Qt.ItemFlag.ItemIsEnabled):
                return None
            raw = item.data(Qt.ItemDataRole.UserRole)
            return Path(str(raw)) if raw else None

        def update_recent_button() -> None:
            path = current_path()
            recent_button.setEnabled(path is not None and path.is_dir())

        def choose_recent() -> None:
            path = current_path()
            if path is not None and path.is_dir():
                selected["path"] = path
                dialog.accept()

        def choose_other() -> None:
            directory = QFileDialog.getExistingDirectory(
                dialog,
                "분석 결과 bundle 폴더 선택",
                str(self._default_browse_dir(entries)),
            )
            if directory:
                selected["path"] = Path(directory)
                dialog.accept()

        recent_list.currentItemChanged.connect(lambda *_args: update_recent_button())
        recent_list.itemDoubleClicked.connect(lambda _item: choose_recent())
        recent_button.clicked.connect(choose_recent)
        other_button.clicked.connect(choose_other)
        cancel_button.clicked.connect(dialog.reject)
        for row in range(recent_list.count()):
            item = recent_list.item(row)
            if bool(item.flags() & Qt.ItemFlag.ItemIsEnabled):
                recent_list.setCurrentRow(row)
                break
        update_recent_button()
        if dialog.exec() == QDialog.DialogCode.Accepted and "path" in selected:
            self.open_bundle(selected["path"])

    def _recent_entries(self) -> tuple[RecentResultEntry, ...]:
        entries = list(self.recent_result_history.entries()) if self.recent_result_history is not None else []
        last_path = str(getattr(self.window, "last_result_path", "") or "").strip()
        if last_path:
            key = _path_key(last_path)
            if all(_path_key(entry.path) != key for entry in entries):
                entries.insert(0, RecentResultEntry(path=last_path))
        return tuple(entries)

    @staticmethod
    def _recent_entry_label(entry: RecentResultEntry) -> str:
        title = entry.run_name or entry.source_video_name or Path(entry.path).name or entry.path
        details = [value for value in (entry.profile_name, entry.source_video_name) if value and value != title]
        detail_line = " · ".join(details)
        return "\n".join(value for value in (title, detail_line, entry.path) if value)

    def _default_browse_dir(self, entries: tuple[RecentResultEntry, ...]) -> Path:
        for entry in entries:
            path = Path(entry.path).expanduser()
            if path.is_dir():
                return path.parent
        return Path.home()

    def _remember_loaded_bundle(self) -> None:
        if self.recent_result_history is None or self.viewer is None:
            return
        bundle = getattr(self.viewer, "bundle", None)
        if bundle is None:
            return
        try:
            self.recent_result_history.record_bundle(bundle)
        except Exception:
            LOGGER.warning("Opened result could not be registered in recent history", exc_info=True)

    def open_bundle(self, path: str | Path) -> bool:
        if self.viewer is None:
            if self.viewer_factory is None:
                raise RuntimeError("Result Review viewer factory가 구성되지 않았습니다.")
            self.viewer = self.viewer_factory(self.window)
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
            self._remember_loaded_bundle()
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



def _path_key(value: str | Path) -> str:
    return os.path.normcase(os.path.normpath(os.path.expanduser(os.fspath(value))))
