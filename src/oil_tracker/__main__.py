from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from oil_tracker.bootstrap import build_main_window
from oil_tracker.ui.style import load_application_stylesheet


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Rotary Oil Level Tracker")
    app.setOrganizationName("Oil Level Tracker")
    app.setStyleSheet(load_application_stylesheet())
    window = build_main_window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
