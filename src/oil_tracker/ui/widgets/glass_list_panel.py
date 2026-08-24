from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class GlassListPanel(QWidget):
    addRequested = Signal()
    deleteRequested = Signal()
    copyRequested = Signal()
    selectionChanged = Signal(str)
    enabledChanged = Signal(str, bool)
    issueActivated = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("glassListPanel")
        self.list = QListWidget()
        self.list.setWordWrap(True)
        self.list.setSpacing(2)
        self.list.currentItemChanged.connect(self._selected)
        self.list.itemChanged.connect(self._checked)
        self.list.itemDoubleClicked.connect(self._activated)
        self.add_button = QPushButton("Glass 추가")
        self.delete_button = QPushButton("삭제")
        self.copy_button = QPushButton("설정 복사")
        self.delete_button.hide()
        self.copy_button.hide()
        self.copy_button.setToolTip("현재 선택한 Glass의 공통 설정을 다른 Glass에 복사합니다.")
        self.delete_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.add_button.clicked.connect(self.addRequested)
        self.delete_button.clicked.connect(self.deleteRequested)
        self.copy_button.clicked.connect(self.copyRequested)
        self.more_menu = QMenu("Glass 작업", self)
        self.delete_action = self.more_menu.addAction("선택한 Glass 삭제")
        self.copy_action = self.more_menu.addAction("다른 Glass에 설정 복사")
        self.delete_action.setEnabled(False)
        self.copy_action.setEnabled(False)
        self.delete_action.triggered.connect(self.delete_button.click)
        self.copy_action.triggered.connect(self.copy_button.click)
        self.more_button = QToolButton()
        self.more_button.setObjectName("panelMenuButton")
        self.more_button.setText("더보기")
        self.more_button.setMenu(self.more_menu)
        self.more_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        primary_buttons = QHBoxLayout()
        primary_buttons.addWidget(self.add_button, 1)
        primary_buttons.addWidget(self.more_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        self.ownership_label = QLabel("Profile 설정 · Glass 목록")
        self.ownership_label.setObjectName("profileAreaHeading")
        self.ownership_hint = QLabel("이 목록과 Glass 구성은 .oilrecipe Profile에 저장되어 다시 사용됩니다.")
        self.ownership_hint.setObjectName("ownershipHint")
        self.ownership_hint.setWordWrap(True)
        self.ownership_label.setToolTip(self.ownership_hint.text())
        self.ownership_hint.hide()
        layout.addWidget(self.ownership_label)
        layout.addWidget(self.list, 1)
        layout.addLayout(primary_buttons)
        self.setMinimumWidth(230)

    def set_glasses(self, glasses, selected_id: str | None, readiness_by_id=None) -> None:
        readiness_by_id = readiness_by_id or {}
        self.list.blockSignals(True)
        self.list.clear()
        selected_row = -1
        for row, glass in enumerate(glasses):
            readiness = readiness_by_id.get(glass.id)
            if readiness is None:
                text = glass.name
                tooltip = glass.name
                issue = None
            else:
                suffix = f" · {readiness.reason}" if readiness.reason else ""
                text = f"{readiness.symbol} {glass.name}\n{readiness.label}{suffix}"
                tooltip = f"{glass.name}: {readiness.label}{suffix}"
                issue = readiness.issue
            item = QListWidgetItem(text)
            item.setToolTip(tooltip)
            item.setData(Qt.ItemDataRole.UserRole, glass.id)
            item.setData(Qt.ItemDataRole.UserRole + 1, issue)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if glass.enabled else Qt.CheckState.Unchecked)
            item.setSizeHint(QSize(0, 52 if readiness is not None else 32))
            self.list.addItem(item)
            if glass.id == selected_id:
                selected_row = row
        if selected_row >= 0:
            self.list.setCurrentRow(selected_row)
        self.list.blockSignals(False)
        self._set_action_state(selected_row >= 0, len(glasses) > 1)

    def _selected(self, current, _previous) -> None:
        self._set_action_state(current is not None, self.list.count() > 1)
        if current:
            self.selectionChanged.emit(current.data(Qt.ItemDataRole.UserRole))

    def _set_action_state(self, has_selection: bool, has_copy_target: bool) -> None:
        can_copy = has_selection and has_copy_target
        self.delete_button.setEnabled(has_selection)
        self.delete_action.setEnabled(has_selection)
        self.copy_button.setEnabled(can_copy)
        self.copy_action.setEnabled(can_copy)

    def _checked(self, item) -> None:
        self.enabledChanged.emit(
            item.data(Qt.ItemDataRole.UserRole),
            item.checkState() == Qt.CheckState.Checked,
        )

    def _activated(self, item) -> None:
        issue = item.data(Qt.ItemDataRole.UserRole + 1)
        if issue is not None:
            self.issueActivated.emit(issue)
