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
    comparisons = parser.add_mutually_exclusive_group()
    comparisons.add_argument(
        "--oil-cost-first-assignment", action="store_true",
        help="Oil 추적선 연결 비용을 우선하는 비교 모드 (기본 OFF)",
    )
    comparisons.add_argument(
        "--oil-candidate-rgb", action="store_true",
        help="고정 RGB 모델로 Oil 후보를 거르는 비교 모드 (기본 OFF)",
    )
    comparisons.add_argument(
        "--oil-top-exit-full", action="store_true",
        help="상승 계면의 상단 이탈 후 FULL 상태를 연결하는 비교 모드 (기본 OFF)",
    )
    parser.add_argument(
        "--oil-fill-owner-contest", action="store_true",
        help="채움 주인이 모호했던 tracklet이 경쟁 탈락만으로 주인이 되지 않게 하는 비교 모드 (기본 OFF)",
    )
    parser.add_argument(
        "--oil-fast-rise-association", action="store_true",
        help="cap을 넘는 일정 속도 상승 행을 하나의 tracklet으로 잇는 비교 모드 (기본 OFF)",
    )
    parser.add_argument(
        "--oil-fill-owner-colocation", action="store_true",
        help="같은 프레임에서 한 연결 단계 안에 함께 관측된 채움 주인들을 모호로 닫지 않는 비교 모드 (기본 OFF)",
    )
    options, qt_args = parser.parse_known_args(sys.argv[1:])
    if options.oil_fill_owner_contest and (options.oil_cost_first_assignment or options.oil_candidate_rgb):
        parser.error("--oil-fill-owner-contest는 cost-first, RGB 비교와 함께 쓸 수 없습니다")
    if options.oil_fast_rise_association and (options.oil_cost_first_assignment or options.oil_candidate_rgb):
        parser.error("--oil-fast-rise-association은 cost-first, RGB 비교와 함께 쓸 수 없습니다")
    if options.oil_fill_owner_colocation and (options.oil_cost_first_assignment or options.oil_candidate_rgb):
        parser.error("--oil-fill-owner-colocation은 cost-first, RGB 비교와 함께 쓸 수 없습니다")
    app = QApplication.instance() or QApplication([sys.argv[0], *qt_args])
    app.setApplicationName("Rotary Oil Level Tracker")
    app.setOrganizationName("Oil Level Tracker")
    app.setStyleSheet(load_application_stylesheet())
    comparison_options = {}
    if options.initial_full_observation:
        comparison_options["initial_full_observation"] = True
    if options.oil_cost_first_assignment:
        comparison_options["cost_first_assignment"] = True
    if options.oil_candidate_rgb:
        comparison_options["candidate_rgb"] = True
    if options.oil_top_exit_full:
        comparison_options["top_exit_full"] = True
    if options.oil_fill_owner_contest:
        comparison_options["fill_owner_contest"] = True
    if options.oil_fast_rise_association:
        comparison_options["fast_rise_association"] = True
    if options.oil_fill_owner_colocation:
        comparison_options["fill_owner_colocation"] = True
    window = build_main_window(**comparison_options)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
