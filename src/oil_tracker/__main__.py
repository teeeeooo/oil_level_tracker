from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from oil_tracker.bootstrap import build_main_window


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Rotary Oil Level Tracker")
    app.setOrganizationName("Oil Level Tracker")
    window = build_main_window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
