from __future__ import annotations

import ast
from pathlib import Path

from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector


ROOT = Path(__file__).resolve().parents[1]
APPLICATION_ROOT = ROOT / "src" / "oil_tracker" / "application"
DETECTOR_CAPABILITIES = {
    "detect",
    "reset",
    "learn_static_artifact",
    "resolve_sequence",
    "version",
}


def _probed_attributes(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        str(node.args[1].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "getattr"
        and len(node.args) >= 2
        and isinstance(node.args[1], ast.Constant)
        and isinstance(node.args[1].value, str)
    }


def test_application_does_not_probe_detector_capabilities_dynamically() -> None:
    violations = {
        path.relative_to(ROOT).as_posix(): sorted(
            _probed_attributes(path).intersection(DETECTOR_CAPABILITIES)
        )
        for path in APPLICATION_ROOT.rglob("*.py")
        if _probed_attributes(path).intersection(DETECTOR_CAPABILITIES)
    }
    assert violations == {}


def test_one_production_detector_implements_the_complete_analysis_lifecycle() -> None:
    detector = OpenCvPhaseDetector()
    assert detector.version
    assert all(
        callable(getattr(detector, capability))
        for capability in (
            "detect",
            "reset",
            "learn_static_artifact",
            "resolve_sequence",
        )
    )
