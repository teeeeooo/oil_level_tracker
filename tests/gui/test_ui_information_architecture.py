from __future__ import annotations

import re

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QToolBar

from oil_tracker.bootstrap import build_main_window
from oil_tracker.ui.redetection_result_review_window import RedetectionResultReviewWindow
from oil_tracker.ui.presentation_labels import review_reason_label
from oil_tracker.ui.result_review_window import ResultReviewWindow
from oil_tracker.ui.style import load_application_stylesheet


def _action_texts(owner) -> set[str]:
    return {
        action.text()
        for action in owner.actions()
        if not action.isSeparator() and action.text()
    }


def test_workbench_keeps_primary_navigation_visible_and_secondary_actions_in_one_menu(qtbot):
    window = build_main_window()
    qtbot.addWidget(window)
    toolbar = window.findChild(QToolBar, "mainToolBar")
    assert toolbar is not None

    assert _action_texts(toolbar) == {"새 프로필", "프로필 열기", "결과 검토"}
    menu_actions = _action_texts(window.workbench_menu)
    assert {
        "프로필 저장",
        "결과 보고서",
        "여러 시점 점검",
        "분석 영역 상세보기",
        "실행 취소",
        "다시 실행",
    }.issubset(menu_actions)
    assert window.profile_context.title() == "Profile — 재사용 설정"
    assert window.session_bar.title() == "현재 시험 — Profile에는 저장되지 않음"
    assert window.settings.scroll.isHidden()
    assert not window.settings.empty_state.isHidden()


def test_result_review_defaults_to_focused_canvas_and_keeps_secondary_work_at_depth_two(qtbot):
    window = ResultReviewWindow()
    qtbot.addWidget(window)
    window.show()

    toolbar = window.findChild(QToolBar, "resultReviewToolBar")
    assert toolbar is not None
    assert _action_texts(toolbar) == {"결과 열기"}
    assert {
        "세부 정보 보기",
        "원본 영상 다시 지정",
        "결과 보고서 열기",
        "결과 폴더 열기",
        "선택 이벤트 캡처 열기",
        "현재 장면 PNG 저장",
        "주석 MP4 내보내기",
        "같은 프로필로 새 영상 분석",
    }.issubset(_action_texts(window.review_actions_menu))
    assert window.detail_stack.isHidden()

    window.details_action.setChecked(True)
    assert not window.detail_stack.isHidden()
    window.details_action.setChecked(False)
    assert window.detail_stack.isHidden()


def test_developer_review_actions_share_the_existing_result_menu(qtbot):
    window = RedetectionResultReviewWindow()
    qtbot.addWidget(window)

    menu_actions = _action_texts(window.review_actions_menu)
    assert "부분 재검출과 비교" in menu_actions
    assert "사용자 정답으로 확인" in menu_actions
    toolbar = window.findChild(QToolBar, "resultReviewToolBar")
    assert "부분 재검출과 비교" not in _action_texts(toolbar)
    assert "사용자 정답으로 확인" not in _action_texts(toolbar)


def test_application_chrome_uses_only_neutral_blue_and_red_color_roles():
    colors = {
        match.lower()
        for match in re.findall(r"#[0-9a-fA-F]{6}", load_application_stylesheet())
    }
    assert colors
    for value in colors:
        hue, saturation, _lightness, _alpha = QColor(value).getHslF()
        if saturation < 0.12:
            continue
        assert hue <= 0.04 or hue >= 0.94 or 0.54 <= hue <= 0.66, value


def test_detector_review_flags_collapse_to_user_facing_labels():
    assert review_reason_label("FOAM_COMPONENT_REJECTED") == "거품 영향"
    assert review_reason_label("R16_OBSERVATION_UNAVAILABLE") == "검출 정보 부족"
    assert review_reason_label("REVIEW_REQUIRED") == "사용자 확인 필요"
    assert review_reason_label("신뢰도 기준 미달") == "신뢰도 기준 미달"
