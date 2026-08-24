from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.ui.widgets.transport_bar import TransportBar
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas


class VideoPlaybackPanel(QFrame):
    """Keep the editable video canvas and transport in separate layout rows."""

    def __init__(
        self,
        canvas: VideoOverlayCanvas | None = None,
        transport: TransportBar | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("videoPlaybackPanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.canvas = canvas or VideoOverlayCanvas()
        self.transport = transport or TransportBar()
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.transport.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.transport.setMinimumHeight(max(38, self.transport.sizeHint().height()))
        self.view_controls = QWidget()
        self.view_controls.setObjectName("canvasViewControls")
        controls = QHBoxLayout(self.view_controls)
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(4)
        controls.addWidget(QLabel("화면"))
        self.zoom_in_button = self._view_button("확대", "zoomInButton", self.canvas.zoom_in)
        self.zoom_out_button = self._view_button("축소", "zoomOutButton", self.canvas.zoom_out)
        self.fit_button = self._view_button("맞춤", "fitViewButton", self.canvas.fit_to_view)
        self.actual_size_button = self._view_button("100%", "actualSizeButton", self.canvas.actual_size)
        for button in (
            self.zoom_in_button,
            self.zoom_out_button,
            self.fit_button,
            self.actual_size_button,
        ):
            controls.addWidget(button)
        hint = QLabel("Ctrl+휠 확대/축소 · 가운데 버튼 드래그 이동", self.view_controls)
        hint.setObjectName("canvasViewHint")
        hint.hide()
        self.view_controls.setToolTip(hint.text())
        controls.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.addWidget(self.view_controls, 0)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.transport, 0)

    def _view_button(self, text: str, object_name: str, callback) -> QToolButton:
        button = QToolButton(self)
        button.setText(text)
        button.setObjectName(object_name)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(callback)
        return button
