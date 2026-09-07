from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest


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


SOURCE = "src/oil_tracker/adapters/vision/example.py"


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", f"core.hooksPath={root / 'disabled-test-hooks'}", "-c", "user.name=Test",
         "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", *args],
        cwd=root, check=True, capture_output=True, text=True, encoding="utf-8",
        stdin=subprocess.DEVNULL,
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    target = tmp_path / SOURCE
    target.parent.mkdir(parents=True)
    target.write_text('"""Owner contract."""\nvalue = 1\n', encoding="utf-8")
    git(tmp_path, "add", SOURCE)
    git(tmp_path, "commit", "-qm", "baseline")
    git(tmp_path, "tag", "baseline")
    return tmp_path


def test_cosmetic_worktree_and_committed_change_pass_without_design(repo: Path) -> None:
    (repo / SOURCE).write_text('"""Owner contract."""\n# Explanation only\nvalue = (\n    1\n)\n', encoding="utf-8")
    assert governance.check_refs("baseline", root=repo, include_worktree=True) == []
    git(repo, "add", SOURCE)
    git(repo, "commit", "-qm", "format")
    assert governance.check_refs("baseline", root=repo) == []


@pytest.mark.parametrize("source", [
    '"""Owner contract."""\nvalue = 2\n',
    '"""Changed contract."""\nvalue = 1\n',
    'value = (\n',
    '# coding: latin-1\n"""Owner contract."""\nvalue = 1\n',
    '#!/usr/bin/python3\n"""Owner contract."""\nvalue = 1\n',
])
def test_non_cosmetic_changes_still_require_design(repo: Path, source: str) -> None:
    (repo / SOURCE).write_text(source, encoding="utf-8")
    assert governance.check_refs("baseline", root=repo, include_worktree=True)


@pytest.mark.parametrize("operation", ["add", "delete", "rename"])
def test_path_changes_are_not_exempt(repo: Path, operation: str) -> None:
    target = repo / SOURCE
    other = target.with_name("other.py")
    if operation == "add":
        other.write_bytes(target.read_bytes())
    elif operation == "delete":
        target.unlink()
    else:
        target.rename(other)
    assert governance.check_refs("baseline", root=repo, include_worktree=True)


def test_missing_baseline_does_not_fall_back_to_worktree(repo: Path) -> None:
    added = (repo / SOURCE).with_name("new.py")
    added.write_text("value = 1\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "add owner")
    assert governance.check_refs("baseline", root=repo)


def test_worktree_cannot_hide_committed_behavior_change(repo: Path) -> None:
    target = repo / SOURCE
    original = target.read_bytes()
    target.write_text("value = 2\n", encoding="utf-8")
    git(repo, "add", SOURCE)
    git(repo, "commit", "-qm", "behavior")
    target.write_bytes(original)
    assert governance.check_refs("baseline", root=repo)
    assert governance.check_refs("baseline", root=repo, include_worktree=True) == []


def test_modes_and_type_comments_remain_significant() -> None:
    assert not governance._same_python_ast(("100644", "x = 1\n"), ("100755", "x = 1\n"))
    assert not governance._same_python_ast(("100644", "x = 1\n"), ("100644", "x = 1  # type: int\n"))


def test_comparison_uses_merge_base_not_diverged_base_tip(repo: Path) -> None:
    target = repo / SOURCE
    original = target.read_text(encoding="utf-8")
    target.write_text("value = 2\n", encoding="utf-8")
    git(repo, "add", SOURCE)
    git(repo, "commit", "-qm", "base side behavior")
    git(repo, "tag", "base-tip")
    git(repo, "checkout", "-qb", "topic", "baseline")
    target.write_text(original + "# Cosmetic change on topic\n", encoding="utf-8")
    git(repo, "add", SOURCE)
    git(repo, "commit", "-qm", "topic comment")
    assert governance.check_refs("base-tip", root=repo) == []


def test_deleted_worktree_design_cannot_satisfy_gate(repo: Path) -> None:
    design = "docs/20-architecture/s11-example.md"
    target = repo / design
    target.parent.mkdir(parents=True)
    target.write_text(history(), encoding="utf-8")
    git(repo, "add", design)
    git(repo, "commit", "-qm", "design")
    target.unlink()
    (repo / SOURCE).write_text("value = 2\n", encoding="utf-8")
    errors = governance.check_refs("baseline", root=repo, include_worktree=True)
    assert any("without a changed S11 architecture/design" in error for error in errors)
