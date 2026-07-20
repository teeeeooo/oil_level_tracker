from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected pattern not found in {path}: {old[:120]!r}")
    file_path.write_text(text.replace(old, new, count), encoding="utf-8")


replace(
    "src/oil_tracker/ui/main_window.py",
    '            ("debug", "상세 검출 정보", QStyle.StandardPixmap.SP_ComputerIcon),',
    '            ("debug", "ROI 상세보기", QStyle.StandardPixmap.SP_ComputerIcon),',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    "        left = max(190, int(width * 0.14))\n"
    "        right = max(350, int(width * 0.23))\n"
    "        self.splitter.setSizes([left, max(700, width - left - right), right])\n",
    "        left = max(180, int(width * 0.12))\n"
    "        right = max(460, int(width * 0.28))\n"
    "        self.splitter.setSizes([left, max(660, width - left - right), right])\n",
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '        self.debug_panel = DebugPanel()\n'
    '        self.debug_dock = QDockWidget("상세 검출 정보", self)\n'
    '        self.debug_dock.setWidget(self.debug_panel)\n'
    '        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.debug_dock)\n'
    '        self.debug_dock.hide()\n',
    '        self.debug_panel = DebugPanel()\n'
    '        self.debug_dock = QDockWidget("ROI 및 상세 검출 정보", self)\n'
    '        self.debug_dock.setWidget(self.debug_panel)\n'
    '        self.debug_dock.setMinimumSize(760, 560)\n'
    '        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.debug_dock)\n'
    '        self.debug_dock.setFloating(True)\n'
    '        self.debug_dock.resize(980, 720)\n'
    '        self.debug_dock.hide()\n',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '        layout.addWidget(QLabel("분석 빈도"), 2, 0)\n'
    '        layout.addWidget(self.sampling_spin, 2, 1)\n'
    '        layout.addWidget(QLabel("영상 1초당 분석할 장면 수"), 2, 2, 1, 4)\n'
    '        layout.setColumnStretch(1, 1)\n'
    '        layout.setColumnStretch(3, 1)\n'
    '        layout.setColumnStretch(5, 1)\n',
    '        layout.addWidget(QLabel("분석 빈도"), 1, 6)\n'
    '        layout.addWidget(self.sampling_spin, 1, 7)\n'
    '        layout.setColumnStretch(1, 1)\n'
    '        layout.setColumnStretch(3, 1)\n'
    '        layout.setColumnStretch(5, 1)\n'
    '        layout.setColumnStretch(7, 1)\n',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '        self.actions["debug"].toggled.connect(self.debug_dock.setVisible)\n',
    '        self.actions["debug"].toggled.connect(self._toggle_debug_view)\n'
    '        self.debug_dock.visibilityChanged.connect(self._sync_debug_action)\n',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '    def _build_session_bar(self) -> QWidget:\n',
    '    def _toggle_debug_view(self, visible: bool) -> None:\n'
    '        if visible:\n'
    '            if not self.debug_dock.isFloating():\n'
    '                self.debug_dock.setFloating(True)\n'
    '            self.debug_dock.resize(980, 720)\n'
    '            self.debug_dock.show()\n'
    '            self.debug_dock.raise_()\n'
    '            self.debug_dock.activateWindow()\n'
    '        else:\n'
    '            self.debug_dock.hide()\n\n'
    '    def _sync_debug_action(self, visible: bool) -> None:\n'
    '        self.actions["debug"].blockSignals(True)\n'
    '        self.actions["debug"].setChecked(visible)\n'
    '        self.actions["debug"].blockSignals(False)\n\n'
    '    def _build_session_bar(self) -> QWidget:\n',
)

replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "        self._detection = None\n        self.setMinimumSize(640, 420)\n",
    "        self._detection = None\n"
    "        self._detection_badge = None\n"
    "        self._editable_ellipse_item = None\n"
    "        self.setMinimumSize(640, 420)\n",
)
replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "    def set_detection(self, detection) -> None:\n"
    "        self._detection = detection\n"
    "        self.rebuild_overlays()\n",
    "    def set_detection(self, detection) -> None:\n"
    "        self._detection = detection\n"
    "        self._refresh_detection_status()\n",
)
replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "        frame_rect = QRectF(0, 0, self._frame_size[0], self._frame_size[1])\n"
    "        selected = None\n",
    "        frame_rect = QRectF(0, 0, self._frame_size[0], self._frame_size[1])\n"
    "        self._detection_badge = None\n"
    "        self._editable_ellipse_item = None\n"
    "        selected = None\n",
)
replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "                item.setData(0, glass.id)\n"
    "                self._scene.addItem(item)\n",
    "                item.setData(0, glass.id)\n"
    "                self._editable_ellipse_item = item\n"
    "                self._scene.addItem(item)\n",
)
replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "        self.setPen(QPen(QColor(255, 220, 0), 3, Qt.PenStyle.DashLine))\n",
    "        self.setData(0, glass_id)\n"
    "        self.setPen(QPen(QColor(255, 220, 0), 3, Qt.PenStyle.DashLine))\n",
)
replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)\n"
    "        self._position_label()\n",
    "        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)\n"
    "        self.label.setAcceptedMouseButtons(Qt.MouseButton.NoButton)\n"
    "        self._position_label()\n",
)
replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "            self._dragging = True\n"
    "            self._set_y(event.scenePos().y())\n"
    "            event.accept()\n",
    "            self._dragging = True\n"
    "            event.accept()\n",
)
replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "        badge.setZValue(90)\n"
    "        self._scene.addItem(badge)\n\n"
    "    def _ellipse_changed",
    "        badge.setZValue(90)\n"
    "        badge.setAcceptedMouseButtons(Qt.MouseButton.NoButton)\n"
    "        self._detection_badge = badge\n"
    "        self._scene.addItem(badge)\n\n"
    "    def _refresh_detection_status(self) -> None:\n"
    "        if self._detection_badge is not None and self._detection_badge.scene() is self._scene:\n"
    "            self._scene.removeItem(self._detection_badge)\n"
    "        self._detection_badge = None\n"
    "        if self._detection is None or self._detection.glass_id != self._selected_id:\n"
    "            return\n"
    "        selected = next((glass for glass in self._glasses if glass.id == self._selected_id), None)\n"
    "        if selected is not None:\n"
    "            self._add_detection_status(selected, self._detection)\n\n"
    "    def _ellipse_changed",
)
replace(
    "src/oil_tracker/ui/widgets/video_overlay_canvas.py",
    "    def mousePressEvent(self, event) -> None:\n"
    "        item = self.itemAt(event.position().toPoint())\n"
    "        current = item\n"
    "        while current is not None:\n"
    "            glass_id = current.data(0)\n"
    "            if glass_id:\n"
    "                self.glassSelected.emit(str(glass_id))\n"
    "                break\n"
    "            current = current.parentItem()\n"
    "        super().mousePressEvent(event)\n",
    "    def mousePressEvent(self, event) -> None:\n"
    "        item = self.itemAt(event.position().toPoint())\n"
    "        clicked_auxiliary = isinstance(item, (ResizeHandleItem, DraggableZeroLine))\n"
    "        current = item\n"
    "        while current is not None:\n"
    "            glass_id = current.data(0)\n"
    "            if glass_id:\n"
    "                if str(glass_id) != self._selected_id:\n"
    "                    self.glassSelected.emit(str(glass_id))\n"
    "                break\n"
    "            current = current.parentItem()\n"
    "        super().mousePressEvent(event)\n"
    "        if clicked_auxiliary and self._editable_ellipse_item is not None:\n"
    "            self._editable_ellipse_item.setSelected(True)\n",
)
