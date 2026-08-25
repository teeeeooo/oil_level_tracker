from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "detector_governance", ROOT / "scripts" / "check_detector_governance.py"
)
assert SPEC and SPEC.loader
governance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(governance)

MAP = """
`OIL-PHASE-FILL`
`FOAM-EPISODE`
"""
REGISTRY = """
### S11-F01 — Example
### S11-F07 — Example
"""


def history(*, node: str = "OIL-PHASE-FILL", failure: str = "S11-F01", map_impact: str = "NONE — owner is unchanged", registry_impact: str = "NONE — no mechanism changed") -> str:
    return f"""## History Review

- Logic-map nodes: `{node}`
- Failure-registry entries: `{failure}`
- Prior mechanisms reviewed: reviewed the linked prior diagnostic
- Prior mechanisms rejected: rejected the unbounded shortcut
- Preserved contracts: fail-closed same-frame provenance
- Difference from prior failures: bounded owner remains explicit
- Logic-map impact: {map_impact}
- Failure-registry impact: {registry_impact}
"""


def field(*, node: str = "FOAM-EPISODE", failure: str = "S11-F07", map_impact: str = "NONE — field evidence does not alter source ownership", registry_impact: str = "NONE — no causal mechanism entry changed") -> str:
    return f"""## Detector Governance

- **Logic-map nodes:** `{node}`
- **Failure-registry entries:** `{failure}`
- **First harmful stage:** `NOT_PROVEN` — the required bundle is absent
- **Logic-map impact:** `{map_impact}`
- **Failure-registry impact:** `{registry_impact}`
"""


def run(changed: set[str], contents: dict[str, str]) -> list[str]:
    return governance.check_changed_files(
        changed,
        contents=contents,
        logic_map_text=MAP,
        registry_text=REGISTRY,
    )


def test_out_of_scope_change_passes() -> None:
    assert run({"src/oil_tracker/ui/main_window.py"}, {}) == []


def test_non_markdown_diagnostic_manifest_passes() -> None:
    assert run({"docs/50-diagnostics/s11/probe-manifest.json"}, {}) == []


def test_detector_code_without_design_fails() -> None:
    errors = run({"src/oil_tracker/adapters/vision/new_owner.py"}, {})
    assert any("without a changed S11 architecture/design" in error for error in errors)


def test_result_presentation_owner_is_detector_boundary() -> None:
    errors = run({"src/oil_tracker/application/services/graph_series.py"}, {})
    assert any("without a changed S11 architecture/design" in error for error in errors)


def test_detector_validation_without_design_fails() -> None:
    errors = run({"docs/30-validation/s11-r19-validation.md"}, {})
    assert any("validation changed without a companion" in error for error in errors)


def test_valid_design_and_detector_code_pass() -> None:
    path = "docs/20-architecture/s11-next-architecture.md"
    assert run(
        {"src/oil_tracker/adapters/vision/new_owner.py", path},
        {path: history()},
    ) == []


def test_unknown_node_fails() -> None:
    path = "docs/20-architecture/s11-next-architecture.md"
    errors = run({path}, {path: history(node="UNKNOWN-NODE")})
    assert any("unknown logic-map node `UNKNOWN-NODE`" in error for error in errors)


def test_unknown_failure_id_fails() -> None:
    path = "docs/20-architecture/s11-next-architecture.md"
    errors = run({path}, {path: history(failure="S11-F99")})
    assert any("unknown failure-registry entry `S11-F99`" in error for error in errors)


def test_none_without_reason_fails() -> None:
    path = "docs/20-architecture/s11-next-architecture.md"
    errors = run({path}, {path: history(map_impact="NONE")})
    assert any("Logic-map impact" in error and "NONE" in error for error in errors)


def test_updated_without_owner_change_fails() -> None:
    path = "docs/20-architecture/s11-next-architecture.md"
    errors = run({path}, {path: history(registry_impact="UPDATED — registry changed")})
    assert any("requires changed owner" in error for error in errors)


def test_logic_map_change_without_design_fails() -> None:
    errors = run(
        {governance.LOGIC_MAP},
        {governance.LOGIC_MAP: MAP},
    )
    assert any("logic map changed without" in error for error in errors)


def test_windows_field_evidence_without_governance_fails() -> None:
    path = "docs/60-evidence/s11/new-field-result.md"
    errors = run({path}, {path: "# Field result\nNo block yet.\n"})
    assert any("missing `## Detector Governance` block" in error for error in errors)


def test_valid_field_evidence_with_none_reason_passes() -> None:
    path = "docs/60-evidence/s11/new-field-result.md"
    assert run({path}, {path: field()}) == []
