from __future__ import annotations

from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.transport, 0)
