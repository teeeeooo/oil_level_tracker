from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLabel, QVBoxLayout, QWidget

from oil_tracker.application.services.event_presentation import event_type_label
from oil_tracker.ui.presentation_labels import fill_state_label


class ResultReviewDetails(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.values: dict[str, QLabel] = {}
        form = QFormLayout()
        fields = (
            ("video_time", "영상 시각"),
            ("glass", "Glass"),
            ("fill_state", "관측 상태"),
            ("retrospective_state", "회고 해석"),
            ("retrospective_status", "회고 해석 상태"),
            ("oil_position", "유면 위치"),
            ("foam_position", "거품 위치"),
            ("active", "이벤트·확인 사항"),
            ("boundary_status", "화면 표시"),
        )
        for key, title in fields:
            label = QLabel("-")
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.values[key] = label
            form.addRow(title, label)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addStretch(1)

    def clear(self, message: str = "-") -> None:
        for label in self.values.values():
            label.setText(message)
            label.setToolTip("")

    def update_details(self, bundle, glass_id: str, overlay, frame_index: int, video_timestamp: float, active_events=()) -> None:
        glass = bundle.glass_config(glass_id)
        sample = overlay.sample
        self.values["video_time"].setText(f"{video_timestamp:.3f} 초")
        self.values["glass"].setText(glass.name if glass is not None else glass_id)
        retrospective = overlay.retrospective
        if retrospective is None:
            self.values["retrospective_state"].setText("별도 해석 없음")
            self.values["retrospective_status"].setText("관측 결과만 표시")
            self.values["retrospective_status"].setToolTip(
                f"result semantics v{bundle.result_semantics_version} · observed-only"
            )
        else:
            interpreted = (
                fill_state_label(retrospective.interpreted_state)
                if retrospective.interpreted_state is not None
                else "없음"
            )
            active = "현재 시각에 적용" if retrospective.contains(video_timestamp) else "현재 시각에는 적용되지 않음"
            self.values["retrospective_state"].setText(f"{interpreted} · {active}")
            status_labels = {
                "ACCEPTED": "확정됨",
                "UNRESOLVED": "근거 부족",
                "CONFLICT": "관측 결과와 충돌",
                "NOT_APPLICABLE": "적용 대상 아님",
            }
            self.values["retrospective_status"].setText(
                status_labels.get(retrospective.status.value, retrospective.status.value)
            )
            self.values["retrospective_status"].setToolTip(
                f"{retrospective.status.value} · {retrospective.provenance} · {retrospective.reason}"
            )
        if sample is None:
            for key in ("fill_state", "oil_position", "foam_position"):
                self.values[key].setText("-")
        else:
            self.values["fill_state"].setText(fill_state_label(sample.fill_state))
            self.values["oil_position"].setText(
                _position(
                    _first(sample.smoothed_oil_air_level_px_from_zero, sample.raw_oil_air_level_px_from_zero),
                    _first(sample.smoothed_oil_air_level_mm_from_zero, sample.raw_oil_air_level_mm_from_zero),
                )
            )
            self.values["foam_position"].setText(
                _position(
                    _first(sample.smoothed_foam_front_px_from_zero, sample.raw_foam_front_px_from_zero),
                    _first(sample.smoothed_foam_front_mm_from_zero, sample.raw_foam_front_mm_from_zero),
                )
            )
        event_text = [event_type_label(event.event_type) for event in active_events]
        event_text.extend(overlay.review_reasons)
        self.values["active"].setText(" · ".join(dict.fromkeys(event_text)) if event_text else "없음")
        status = overlay.boundary_status
        if not overlay.within_analysis_range:
            status = "분석 구간 밖 — 결과 선을 표시하지 않음"
        self.values["boundary_status"].setText(status or "정상 표시")


def _first(preferred, fallback):
    return preferred if preferred is not None else fallback


def _position(px_value, mm_value) -> str:
    if px_value is None:
        return "관측값 없음"
    text = f"기준점 대비 {float(px_value):.2f} px"
    if mm_value is not None:
        text += f" · {float(mm_value):.2f} mm"
    return text
