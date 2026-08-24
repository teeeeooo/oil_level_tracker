from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QVBoxLayout, QWidget

from oil_tracker.application.services.event_presentation import event_type_label
from oil_tracker.ui.presentation_labels import fill_state_label, review_reason_label


class ResultReviewDetails(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(330)
        self.values: dict[str, QLabel] = {}
        form = QFormLayout()
        fields = (
            ("video_time", "영상 시각"),
            ("frame_index", "장면 번호"),
            ("sample_time", "검출 시각"),
            ("glass", "선택 Glass"),
            ("fill_state", "관측 상태"),
            ("retrospective_state", "추정 상태"),
            ("retrospective_status", "추정 근거"),
            ("oil_y", "유면 Y"),
            ("oil_px", "기준점 대비 px"),
            ("oil_mm", "기준점 대비 mm"),
            ("foam_y", "거품 경계 Y"),
            ("foam_px", "거품 기준점 대비 px"),
            ("foam_mm", "거품 기준점 대비 mm"),
            ("confidence", "전체 신뢰도"),
            ("valid", "유효 여부"),
            ("flags", "검출 메모"),
            ("active", "활성 이벤트 / 검토 사유"),
            ("boundary_status", "표시 상태"),
        )
        for key, title in fields:
            label = QLabel("-")
            label.setWordWrap(True)
            label.setTextInteractionFlags(label.textInteractionFlags())
            self.values[key] = label
            form.addRow(title, label)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addStretch(1)

    def clear(self, message: str = "-") -> None:
        for label in self.values.values():
            label.setText(message)

    def update_details(self, bundle, glass_id: str, overlay, frame_index: int, video_timestamp: float, active_events=()) -> None:
        glass = bundle.glass_config(glass_id)
        sample = overlay.sample
        self.values["video_time"].setText(f"{video_timestamp:.3f} 초")
        self.values["frame_index"].setText(str(frame_index))
        self.values["glass"].setText(glass.name if glass is not None else glass_id)
        retrospective = overlay.retrospective
        if retrospective is None:
            self.values["retrospective_state"].setText("없음 (observed-only)")
            self.values["retrospective_status"].setText(
                f"result semantics v{bundle.result_semantics_version} · 별도 회고 해석 없음"
            )
        else:
            interpreted = (
                fill_state_label(retrospective.interpreted_state)
                if retrospective.interpreted_state is not None
                else "없음"
            )
            active = "현재 시각에 적용" if retrospective.contains(video_timestamp) else "현재 시각에는 미적용"
            self.values["retrospective_state"].setText(f"{interpreted} · {active}")
            self.values["retrospective_status"].setText(
                f"{retrospective.status.value} · {retrospective.provenance} · {retrospective.reason}"
            )
        if sample is None:
            for key in (
                "sample_time",
                "fill_state",
                "oil_y",
                "oil_px",
                "oil_mm",
                "foam_y",
                "foam_px",
                "foam_mm",
                "confidence",
                "valid",
                "flags",
            ):
                self.values[key].setText("-")
        else:
            self.values["sample_time"].setText(f"{sample.timestamp_sec:.3f} 초")
            self.values["fill_state"].setText(fill_state_label(sample.fill_state))
            self.values["oil_y"].setText(_number(overlay.oil_boundary_y, " px"))
            self.values["oil_px"].setText(_number(sample.smoothed_oil_air_level_px_from_zero, " px"))
            self.values["oil_mm"].setText(_number(sample.smoothed_oil_air_level_mm_from_zero, " mm"))
            self.values["foam_y"].setText(_number(overlay.foam_front_y, " px"))
            self.values["foam_px"].setText(_number(sample.smoothed_foam_front_px_from_zero, " px"))
            self.values["foam_mm"].setText(_number(sample.smoothed_foam_front_mm_from_zero, " mm"))
            self.values["confidence"].setText(f"{sample.overall_confidence:.3f}")
            self.values["valid"].setText("유효" if sample.is_valid else "확인 필요")
            self.values["flags"].setText(", ".join(sample.flags) if sample.flags else "없음")
        event_text = [event_type_label(event.event_type) for event in active_events]
        event_text.extend(review_reason_label(reason) for reason in overlay.review_reasons)
        self.values["active"].setText(", ".join(dict.fromkeys(event_text)) if event_text else "없음")
        status = overlay.boundary_status
        if not overlay.within_analysis_range:
            status = "분석 구간 밖 — tracking overlay를 표시하지 않음"
        self.values["boundary_status"].setText(status or "정상")


def _number(value, suffix: str) -> str:
    return "-" if value is None else f"{float(value):.3f}{suffix}"
