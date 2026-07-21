from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt

from oil_tracker.adapters.storage.json_truth_repository import build_truth_bundle_identity
from oil_tracker.application.services.user_truth import TruthFrameContext, UserTruthService
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType
from oil_tracker.ui.truth_annotation_window import TruthAnnotationWindow
from user_truth_fixtures import make_truth_bundle, make_truth_set_and_annotation


def _window(qtbot, tmp_path):
    bundle = make_truth_bundle(tmp_path)
    glass = bundle.recipe.glasses[0]
    service = UserTruthService()
    official = service.official_reference(bundle, glass, 2.0)
    window = TruthAnnotationWindow()
    qtbot.addWidget(window)
    window.show()
    context = TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60)
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    window.set_context(frame, glass, context, official)
    return window, bundle, glass, official, context


def test_window_without_context_disables_annotation_actions(qtbot):
    window = TruthAnnotationWindow()
    qtbot.addWidget(window)
    assert not window.save_annotation_button.isEnabled()
    assert not window.confirm_official_button.isEnabled()
    assert not window.export_current_button.isEnabled()


def test_current_frame_context_is_snapshot_and_not_silently_rebound(qtbot, tmp_path):
    window, _bundle, _glass, _official, context = _window(qtbot, tmp_path)
    assert window.context() is context
    assert "decoded 2.000s" in window.context_label.text()
    assert "frame 60" in window.context_label.text()
    original = window.context()
    unrelated = TruthFrameContext("glass-1", "관찰창 1", 3.0, 3.0, 90)
    assert unrelated != original
    assert window.context() is original


def test_confirm_official_is_explicit_and_copies_fill_and_lines(qtbot, tmp_path):
    window, _bundle, _glass, official, _context = _window(qtbot, tmp_path)
    for check in window.error_checks.values():
        check.setChecked(True)
    window.apply_official_reference()
    values = window.draft_values()
    assert values.disposition is TruthDisposition.CONFIRMED_CORRECT
    assert window.fill_state.currentData() is official.fill_state
    assert values.oil_source_y == official.oil_boundary.source_frame_y
    assert values.foam_source_y == official.foam_front.source_frame_y
    assert values.error_types == ()
    assert window.save_annotation_button.isEnabled()


def test_corrected_visible_state_disables_save_until_oil_and_error_are_present(qtbot, tmp_path):
    window, _bundle, _glass, _official, _context = _window(qtbot, tmp_path)
    window.disposition_buttons[TruthDisposition.CORRECTED].setChecked(True)
    window.fill_state.setCurrentIndex(window.fill_state.findData(FillState.PARTIAL_VISIBLE))
    window.oil_present.setChecked(False)
    for check in window.error_checks.values():
        check.setChecked(False)
    assert not window.save_annotation_button.isEnabled()
    window.oil_present.setChecked(True)
    window.oil_y.setValue(128.0)
    assert not window.save_annotation_button.isEnabled()
    window.error_checks[TruthErrorType.WRONG_CANDIDATE].setChecked(True)
    assert window.save_annotation_button.isEnabled()


def test_unusable_requires_error_but_not_numeric_truth(qtbot, tmp_path):
    window, _bundle, _glass, _official, _context = _window(qtbot, tmp_path)
    window.disposition_buttons[TruthDisposition.UNUSABLE].setChecked(True)
    window.oil_present.setChecked(True)
    window.foam_present.setChecked(True)
    for check in window.error_checks.values():
        check.setChecked(False)
    assert not window.save_annotation_button.isEnabled()
    window.error_checks[TruthErrorType.VIDEO_UNUSABLE].setChecked(True)
    values = window.draft_values()
    assert values.disposition is TruthDisposition.UNUSABLE
    assert values.fill_state is None
    assert window.save_annotation_button.isEnabled()


def test_other_error_requires_note_and_multiselect_is_preserved(qtbot, tmp_path):
    window, _bundle, _glass, _official, _context = _window(qtbot, tmp_path)
    window.disposition_buttons[TruthDisposition.CORRECTED].setChecked(True)
    window.oil_present.setChecked(True)
    window.oil_y.setValue(128.0)
    window.error_checks[TruthErrorType.OTHER].setChecked(True)
    window.error_checks[TruthErrorType.GLARE_OR_REFLECTION].setChecked(True)
    window.note.clear()
    assert not window.save_annotation_button.isEnabled()
    window.note.setPlainText("반사광과 다른 현상이 함께 있음")
    values = window.draft_values()
    assert set(values.error_types) == {
        TruthErrorType.OTHER,
        TruthErrorType.GLARE_OR_REFLECTION,
    }
    assert window.save_annotation_button.isEnabled()


def test_no_interface_state_removes_oil_line_before_save(qtbot, tmp_path):
    window, _bundle, _glass, _official, _context = _window(qtbot, tmp_path)
    window.disposition_buttons[TruthDisposition.CORRECTED].setChecked(True)
    window.oil_present.setChecked(True)
    window.oil_y.setValue(128.0)
    window.fill_state.setCurrentIndex(window.fill_state.findData(FillState.FULL_NO_INTERFACE))
    assert not window.oil_present.isChecked()
    assert window.canvas.oil_y is None


def test_full_with_foam_requires_line_when_foam_present(qtbot, tmp_path):
    window, _bundle, _glass, _official, _context = _window(qtbot, tmp_path)
    window.disposition_buttons[TruthDisposition.CORRECTED].setChecked(True)
    window.fill_state.setCurrentIndex(window.fill_state.findData(FillState.FULL_WITH_FOAM))
    window.error_checks[TruthErrorType.FOAM_MISCLASSIFIED].setChecked(True)
    window.foam_present.setChecked(True)
    window.canvas.remove_line("foam")
    window._building = True
    window.foam_y.setValue(0.0)
    window._building = False
    assert not window.save_annotation_button.isEnabled()
    window.foam_y.setValue(118.0)
    assert window.save_annotation_button.isEnabled()


def test_source_missing_keeps_list_metadata_but_disables_new_and_export(qtbot, tmp_path):
    window, bundle, _glass, _official, _context = _window(qtbot, tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    window.set_annotations(truth_set.sorted_annotations())
    assert window.annotation_list.count() == 1
    window.set_source_available(False, "원본 영상 다시 지정")
    assert window.annotation_list.count() == 1
    assert not window.load_current_button.isEnabled()
    assert not window.export_current_button.isEnabled()
    assert "원본 영상 다시 지정" in window.validation_label.text()


def test_annotation_list_sort_filter_and_selection(qtbot, tmp_path):
    window, bundle, _glass, _official, _context = _window(qtbot, tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    second = annotation.__class__.from_dict(
        {
            **annotation.to_dict(),
            "annotation_id": "unusable-1",
            "frame_index": 30,
            "requested_timestamp_sec": 1.0,
            "actual_decoded_timestamp_sec": 1.0,
            "disposition": "unusable",
            "truth_fill_state": None,
            "oil_boundary": None,
            "foam_front": None,
            "foam_present": False,
            "error_types": ["video_unusable"],
        }
    )
    truth_set.upsert(second)
    window.set_annotations(truth_set.sorted_annotations())
    assert window.annotation_list.count() == 2
    assert "1.000s" in window.annotation_list.item(0).text()
    window.disposition_filter.setCurrentIndex(
        window.disposition_filter.findData(TruthDisposition.UNUSABLE)
    )
    window.set_annotations(truth_set.sorted_annotations())
    assert window.annotation_list.count() == 1
    assert "판정 불가" in window.annotation_list.item(0).text()
    window.disposition_filter.setCurrentIndex(0)
    window.error_filter.setCurrentIndex(
        window.error_filter.findData(TruthErrorType.WRONG_CANDIDATE)
    )
    window.set_annotations(truth_set.sorted_annotations())
    assert window.annotation_list.count() == 1
    assert window.current_annotation_id() in {"", annotation.annotation_id}


def test_decode_delta_and_export_progress_are_visible(qtbot, tmp_path):
    window, _bundle, _glass, _official, _context = _window(qtbot, tmp_path)
    window.set_decode_delta(2.0, 2.02)
    assert "+0.020000초" in window.decode_delta_label.text()

    class Progress:
        fraction = 0.5
        processed_fixtures = 1
        total_fixtures = 2
        message = "hash 계산"

    window.set_export_running(True)
    window.set_export_progress(Progress())
    assert window.export_progress.value() == 500
    assert "1/2" in window.validation_label.text()
    assert window.cancel_export_button.isEnabled()
    window.set_export_running(False)
