from __future__ import annotations

import sys
import argparse

from PySide6.QtWidgets import QApplication

from oil_tracker.bootstrap import build_main_window
from oil_tracker.ui.style import load_application_stylesheet


def main() -> int:
    parser = argparse.ArgumentParser(description="Rotary Oil Level Tracker")
    parser.add_argument(
        "--initial-full-observation", action="store_true",
        help="초기 FULL에서 계면 관측을 허용하는 비교 모드 (기본 OFF)",
    )
    parser.add_argument(
        "--oil-cost-first-assignment", action="store_true",
        help="Oil 추적선 연결 비용을 우선하는 비교 모드 (기본 OFF)",
    )
    options, qt_args = parser.parse_known_args(sys.argv[1:])
    app = QApplication.instance() or QApplication([sys.argv[0], *qt_args])
    app.setApplicationName("Rotary Oil Level Tracker")
    app.setOrganizationName("Oil Level Tracker")
    app.setStyleSheet(load_application_stylesheet())
    comparison_options = {}
    if options.initial_full_observation:
        comparison_options["initial_full_observation"] = True
    if options.oil_cost_first_assignment:
        comparison_options["cost_first_assignment"] = True
    window = build_main_window(**comparison_options)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
