from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication

from oil_tracker.ui.widgets.transport_bar import TransportBar, _parse_timecode


def test_transport_uses_full_width_second_row_and_emits_precision_steps(qtbot):
    transport = TransportBar()
    qtbot.addWidget(transport)
    transport.resize(1000, 110)
    transport.show()
    QApplication.processEvents()

    assert transport.slider.geometry().top() >= transport.play.geometry().bottom()
    assert transport.slider.width() >= 900

    deltas = []
    transport.skipRequested.connect(deltas.append)
    transport.skip_back_10.click()
    transport.skip_back_5.click()
    transport.skip_forward_5.click()
    transport.skip_forward_10.click()
    assert deltas == [-10.0, -5.0, 5.0, 10.0]


def test_transport_accepts_direct_time_and_rejects_invalid_input(qtbot):
    transport = TransportBar()
    qtbot.addWidget(transport)
    transport.set_position(12.0, 90.0, 360)
    requested = []
    transport.timeRequested.connect(requested.append)

    transport.time_input.setText("01:05.250")
    transport.time_input.editingFinished.emit()
    assert requested == [65.25]

    transport.time_input.setText("not-a-time")
    transport.time_input.editingFinished.emit()
    assert requested == [65.25]
    assert transport.time_input.text() == "00:12.000"


def test_slider_click_seeks_immediately_and_drag_is_throttled(qtbot):
    transport = TransportBar()
    qtbot.addWidget(transport)
    transport.resize(800, 110)
    transport.show()
    QApplication.processEvents()
    requested = []
    transport.seekRequested.connect(requested.append)

    qtbot.mouseClick(
        transport.slider,
        Qt.MouseButton.LeftButton,
        pos=QPoint(round(transport.slider.width() * 0.75), transport.slider.height() // 2),
    )
    assert requested and 0.70 <= requested[-1] <= 0.80

    requested.clear()
    transport.slider.sliderMoved.emit(1000)
    transport.slider.sliderMoved.emit(2000)
    transport.slider.sliderMoved.emit(3000)
    assert requested == []
    qtbot.wait(70)
    assert requested == [0.3]


def test_timecode_parser_supports_seconds_minutes_and_hours():
    assert _parse_timecode("5.5") == 5.5
    assert _parse_timecode("01:05.5") == 65.5
    assert _parse_timecode("1:02:03") == 3723.0
