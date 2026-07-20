from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected text was not found in {path}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace(
    "src/oil_tracker/ui/readiness.py",
    '    video_fields = {"input_video_path", "video_metadata", "reference_frame"}\n',
    '    video_fields = {"input_video_path", "video_metadata"}\n',
)

unit_test = '''


def test_progress_assigns_time_and_reference_errors_to_their_own_steps():
    recipe = InspectionRecipe.empty(640, 480)
    glass = InspectionRecipe.default_glass(640, 480)
    recipe.glasses = [glass]
    session = AnalysisSession(
        input_video_path="video.mp4",
        video_metadata=VideoMetadata("video.mp4", 640, 480, 30.0, 10.0, 300),
        analysis_end_sec=10.0,
        compressor_start_sec=1.0,
    )
    reference_issue = ValidationIssue(
        ValidationSeverity.ERROR,
        "READY_REFERENCE",
        "reference",
        glass.id,
        "reference_frame",
    )
    reference_steps = build_workbench_progress(
        recipe,
        session,
        WorkbenchState.DRAFT,
        ValidationResult([reference_issue]),
    )
    assert reference_steps[0].state == ProgressStepState.COMPLETE
    assert reference_steps[2].state == ProgressStepState.ERROR

    time_issue = ValidationIssue(
        ValidationSeverity.ERROR,
        "READY_RANGE",
        "range",
        field="analysis_range",
    )
    time_steps = build_workbench_progress(
        recipe,
        session,
        WorkbenchState.DRAFT,
        ValidationResult([time_issue]),
    )
    assert time_steps[0].state == ProgressStepState.COMPLETE
    assert time_steps[1].state == ProgressStepState.ERROR
'''
unit_path = ROOT / "tests/unit/test_readiness_feedback.py"
unit_path.write_text(unit_path.read_text(encoding="utf-8") + unit_test, encoding="utf-8")

replace(
    "tests/gui/test_workbench_readiness_feedback.py",
    '''    window._preview_ready(current, None)\n    assert window.canvas._detection is current\n    window.schedule_preview()\n''',
    '''    window._preview_ready(current, None)\n    assert window.canvas._detection is current\n\n    other = workbench.add_glass()\n    window._preview_context = (other.id, 10, 1.0)\n    window.canvas.set_detection(None)\n    window._preview_ready(current, None)\n    assert window.canvas._detection is None\n\n    window.schedule_preview()\n''',
)

print("Phase 2A-1 readiness boundaries refined.")
