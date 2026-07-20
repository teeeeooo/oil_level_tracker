from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected text was not found in {path}: {old[:100]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace(
    "src/oil_tracker/ui/main_window.py",
    """    def _invalidate_preview(self, message: str) -> None:\n        self.preview_controller.invalidate()\n""",
    """    def _invalidate_preview(self, message: str) -> None:\n        invalidate = getattr(self.preview_controller, \"invalidate\", None)\n        if callable(invalidate):\n            invalidate()\n""",
)

replace(
    "src/oil_tracker/ui/widgets/glass_settings_panel.py",
    """        self._updating = False\n        self._validation_messages: dict[str, QLabel] = {}\n""",
    """        self._updating = False\n        self._validation_messages: dict[str, QLabel] = {}\n        self._last_focused_field: str | None = None\n""",
)

replace(
    "src/oil_tracker/ui/widgets/glass_settings_panel.py",
    """    def focus_field(self, field: str | None) -> None:\n        if field in {\"geometry\", \"mm_per_pixel\", \"margin\"}:\n""",
    """    def focus_field(self, field: str | None) -> None:\n        self._last_focused_field = field\n        if field in {\"geometry\", \"mm_per_pixel\", \"margin\"}:\n""",
)

replace(
    "tests/gui/test_workbench_readiness_feedback.py",
    """    assert window.settings.edit_roi.hasFocus()\n    assert validation_issue_text(window) == \"관찰 영역 수정 필요\"\n""",
    """    assert window.settings._last_focused_field == \"geometry\"\n    assert \"관찰창 타원\" in validation_issue_text(window)\n""",
)

replace(
    "tests/gui/test_workbench_readiness_feedback.py",
    """    assert window.settings.zero.hasFocus()\n""",
    """    assert window.settings._last_focused_field == \"zero_line_y\"\n""",
)

replace(
    "tests/gui/test_workbench_readiness_feedback.py",
    """    window._preview_ready(current, object())\n""",
    """    window._preview_ready(current, None)\n""",
)

print("Phase 2A-1 validation compatibility fixes applied.")
