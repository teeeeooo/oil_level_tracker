#!/usr/bin/env python3
"""Enforce the S11 detector history/evidence review contract.

The checker intentionally owns all policy. Hooks and CI only choose commit
ranges and invoke this module; they do not duplicate any of these rules.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import subprocess
import sys
import stat
import tokenize
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
LOGIC_MAP = "docs/20-architecture/s11-current-detector-logic-map.md"
FAILURE_REGISTRY = "docs/50-diagnostics/s11/s11-detector-mechanism-failure-registry.md"
GOVERNANCE_DOC = "docs/30-validation/s11-detector-change-governance.md"

# These are the completed-window/publication owners named in the current map.
# The whole vision package is deliberately included because every file there
# can alter detector evidence or an ownership boundary.
DETECTOR_BOUNDARIES = frozenset(
    {
        "src/oil_tracker/application/services/detection_run.py",
        "src/oil_tracker/application/services/analysis_pipeline.py",
        "src/oil_tracker/application/services/detection_processing.py",
        "src/oil_tracker/application/services/analysis_outcome.py",
        "src/oil_tracker/application/services/graph_series.py",
        "src/oil_tracker/application/services/report_presentation.py",
        "src/oil_tracker/application/services/review_graph.py",
        "src/oil_tracker/adapters/reporting/csv_exporter.py",
        "src/oil_tracker/adapters/reporting/graph_renderer.py",
        "src/oil_tracker/adapters/storage/output_bundle_store.py",
        "src/oil_tracker/adapters/storage/jsonl_debug_trace_writer.py",
    }
)

HISTORY_FIELDS = (
    "Logic-map nodes",
    "Failure-registry entries",
    "Prior mechanisms reviewed",
    "Prior mechanisms rejected",
    "Preserved contracts",
    "Difference from prior failures",
    "Logic-map impact",
    "Failure-registry impact",
)
GOVERNANCE_FIELDS = (
    "Logic-map nodes",
    "Failure-registry entries",
    "First harmful stage",
    "Logic-map impact",
    "Failure-registry impact",
)


def _normalise_path(path: str | Path) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def is_detector_code_path(path: str | Path) -> bool:
    normalized = _normalise_path(path)
    return normalized.startswith("src/oil_tracker/adapters/vision/") or normalized in DETECTOR_BOUNDARIES


def is_detector_design_path(path: str | Path) -> bool:
    normalized = _normalise_path(path)
    if normalized == LOGIC_MAP:
        return False
    return (
        normalized.endswith(".md")
        and normalized.startswith("docs/20-architecture/")
        and "/s11-" in normalized
    )


def is_detector_validation_path(path: str | Path) -> bool:
    normalized = _normalise_path(path)
    if normalized == GOVERNANCE_DOC:
        return False
    return (
        normalized.endswith(".md")
        and normalized.startswith("docs/30-validation/s11-")
    )


def is_field_evidence_path(path: str | Path) -> bool:
    normalized = _normalise_path(path)
    if normalized in {FAILURE_REGISTRY, "docs/50-diagnostics/s11/README.md"}:
        return False
    return normalized.endswith(".md") and (
        normalized.startswith("docs/50-diagnostics/s11/")
        or normalized.startswith("docs/60-evidence/s11/")
    )


def _git(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def discover_changed_files(
    base_ref: str,
    head_ref: str = "HEAD",
    *,
    cwd: Path = ROOT,
) -> set[str]:
    """Return paths changed between two refs, using git's merge-base range."""

    output = _git("diff", "--name-only", f"{base_ref}...{head_ref}", cwd=cwd)
    return {_normalise_path(line) for line in output.splitlines() if line.strip()}


def discover_worktree_files(*, cwd: Path = ROOT) -> set[str]:
    """Return tracked and untracked worktree paths relative to HEAD."""

    tracked = _git("diff", "--name-only", "HEAD", cwd=cwd)
    untracked = _git("ls-files", "--others", "--exclude-standard", cwd=cwd)
    return {
        _normalise_path(line)
        for line in (*tracked.splitlines(), *untracked.splitlines())
        if line.strip()
    }


def _read_at_ref(path: str, ref: str, *, cwd: Path) -> str | None:
    try:
        return _git("show", f"{ref}:{path}", cwd=cwd)
    except (OSError, subprocess.CalledProcessError):
        worktree_path = cwd / path
        if worktree_path.is_file():
            return worktree_path.read_text(encoding="utf-8")
        return None


def _python_snapshot(path: str, ref: str | None, *, root: Path) -> tuple[str, str] | None:
    """Read a regular file's mode/text; never substitute worktree text for a ref."""
    try:
        if ref is None:
            file = root / path
            mode = file.lstat().st_mode
            if not stat.S_ISREG(mode):
                return None
            return ("100755" if mode & stat.S_IXUSR else "100644", file.read_text(encoding="utf-8"))
        entry = _git("ls-tree", ref, "--", path, cwd=root)
        if not entry:
            return None
        mode = entry.split()[0]
        if mode not in {"100644", "100755"}:
            return None
        return mode, _git("show", f"{ref}:{path}", cwd=root)
    except (OSError, UnicodeError, subprocess.CalledProcessError):
        return None


def _same_python_ast(before: tuple[str, str] | None, after: tuple[str, str] | None) -> bool:
    if before is None or after is None or before[0] != after[0]:
        return False
    try:
        encodings = [tokenize.detect_encoding(io.BytesIO(item[1].encode("utf-8")).readline)[0] for item in (before, after)]
        shebangs = [item[1].splitlines()[0] if item[1].startswith("#!") else None for item in (before, after)]
        if encodings[0] != encodings[1] or shebangs[0] != shebangs[1]:
            return False
        trees = [ast.parse(item[1], type_comments=True) for item in (before, after)]
        for tree in trees:
            compile(tree, "<detector-governance>", "exec")
    except (SyntaxError, ValueError, RecursionError):
        return False
    # Keep docstrings, type comments, constants, and every executable AST node.
    return ast.dump(trees[0], include_attributes=False) == ast.dump(trees[1], include_attributes=False)


def _owner_ids(text: str) -> tuple[set[str], set[str]]:
    # IDs are rendered as code spans in both owner documents. Restricting the
    # node pattern avoids treating ordinary prose/code tokens as node IDs.
    nodes = set(
        re.findall(
            r"`((?:FRAME|OIL|FOAM|SEQUENCE|PUBLICATION|CSV|TRACE|RESULT)-[A-Z0-9-]+)`",
            text,
        )
    )
    failures = set(re.findall(r"`(S11-F\d+)`", text))
    failures.update(re.findall(r"^###\s+S11-(F\d+)\b", text, re.MULTILINE))
    failures = {item if item.startswith("S11-") else f"S11-{item}" for item in failures}
    return nodes, failures


def _extract_block(text: str, heading: str, fields: Sequence[str]) -> tuple[dict[str, str] | None, list[str]]:
    lines = text.splitlines()
    heading_index = next(
        (index for index, line in enumerate(lines) if line.strip() == heading), None
    )
    if heading_index is None:
        return None, [f"missing `{heading}` block"]

    end = len(lines)
    for index in range(heading_index + 1, len(lines)):
        if re.match(r"^##(?!#)\s+", lines[index]):
            end = index
            break

    field_pattern = re.compile(
        r"^\s*(?:[-*]\s*)?(?:\*\*)?"
        + r"(" + "|".join(re.escape(field) for field in fields) + r")"
        + r"(?:\*\*)?\s*:\s*(?:\*\*)?\s*(.*)\s*$"
    )
    values: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[heading_index + 1 : end]:
        match = field_pattern.match(line)
        if match:
            current = match.group(1)
            values.setdefault(current, []).append(match.group(2).strip())
        elif current is not None and line.strip():
            # Bold-label field blocks often wrap a value on the next line.
            values[current].append(line.strip())

    errors: list[str] = []
    result: dict[str, str] = {}
    for field in fields:
        if field not in values:
            errors.append(f"missing `{field}:` field in `{heading}`")
            continue
        value = " ".join(part for part in values[field] if part).strip()
        if not value or _is_placeholder(value):
            errors.append(f"`{field}:` must contain a specific value")
        result[field] = value
    return result, errors


def _is_placeholder(value: str) -> bool:
    compact = re.sub(r"[`*_]", "", value).strip().lower()
    return compact in {"tbd", "todo", "n/a", "na", "not applicable", "none"} or compact.startswith("<")


def _reference_values(value: str, pattern: str) -> list[str]:
    return re.findall(pattern, value)


def _validate_references(
    values: Mapping[str, str],
    *,
    nodes: set[str],
    failures: set[str],
    path: str,
    errors: list[str],
) -> None:
    node_refs = _reference_values(values.get("Logic-map nodes", ""), r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+\b")
    failure_refs = _reference_values(values.get("Failure-registry entries", ""), r"\bS11-F\d+\b")
    if not node_refs:
        errors.append(f"{path}: `Logic-map nodes:` must name at least one node ID")
    for ref in node_refs:
        if ref not in nodes:
            errors.append(f"{path}: unknown logic-map node `{ref}`")
    if not failure_refs:
        errors.append(f"{path}: `Failure-registry entries:` must name at least one S11-F## ID")
    for ref in failure_refs:
        if ref not in failures:
            errors.append(f"{path}: unknown failure-registry entry `{ref}`")


def _validate_impact(
    value: str,
    *,
    label: str,
    owner_path: str,
    changed_files: set[str],
    owner_changed: bool,
    path: str,
    errors: list[str],
) -> None:
    value = value.replace("`", "").strip()
    match = re.match(r"^(NONE|UPDATED)\s*(?:—|-|:)\s*(.*)$", value, re.IGNORECASE)
    if not match:
        errors.append(f"{path}: `{label}:` must be `NONE — <meaningful reason>` or `UPDATED — <reason>`")
        return
    status, reason = match.group(1).upper(), match.group(2).strip()
    if status == "NONE" and (not reason or _is_placeholder(reason) or reason.lower() in {"no impact", "unchanged"}):
        errors.append(f"{path}: `{label}: NONE` requires a meaningful reason")
    if status == "UPDATED" and not owner_changed:
        errors.append(
            f"{path}: `{label}: UPDATED` requires changed owner `{owner_path}` "
            f"(changed files: {', '.join(sorted(changed_files)) or 'none'})"
        )


def validate_history_review(
    path: str,
    text: str,
    *,
    changed_files: Iterable[str] = (),
    logic_map_text: str,
    registry_text: str,
) -> list[str]:
    changed = {_normalise_path(item) for item in changed_files}
    values, errors = _extract_block(text, "## History Review", HISTORY_FIELDS)
    if values is None:
        return [f"{path}: {error}" for error in errors]
    nodes, failures = _owner_ids(logic_map_text)[0], _owner_ids(registry_text)[1]
    _validate_references(values, nodes=nodes, failures=failures, path=path, errors=errors)
    _validate_impact(
        values.get("Logic-map impact", ""),
        label="Logic-map impact",
        owner_path=LOGIC_MAP,
        changed_files=changed,
        owner_changed=LOGIC_MAP in changed,
        path=path,
        errors=errors,
    )
    _validate_impact(
        values.get("Failure-registry impact", ""),
        label="Failure-registry impact",
        owner_path=FAILURE_REGISTRY,
        changed_files=changed,
        owner_changed=FAILURE_REGISTRY in changed,
        path=path,
        errors=errors,
    )
    return [f"{path}: {error}" if not error.startswith(path + ":") else error for error in errors]


def validate_detector_governance(
    path: str,
    text: str,
    *,
    changed_files: Iterable[str] = (),
    logic_map_text: str,
    registry_text: str,
) -> list[str]:
    changed = {_normalise_path(item) for item in changed_files}
    values, errors = _extract_block(text, "## Detector Governance", GOVERNANCE_FIELDS)
    if values is None:
        return [f"{path}: {error}" for error in errors]
    nodes, failures = _owner_ids(logic_map_text)[0], _owner_ids(registry_text)[1]
    _validate_references(values, nodes=nodes, failures=failures, path=path, errors=errors)
    first_stage = values.get("First harmful stage", "")
    if not first_stage or _is_placeholder(first_stage):
        errors.append(f"{path}: `First harmful stage:` must state the earliest stage or a supported unknown")
    _validate_impact(
        values.get("Logic-map impact", ""),
        label="Logic-map impact",
        owner_path=LOGIC_MAP,
        changed_files=changed,
        owner_changed=LOGIC_MAP in changed,
        path=path,
        errors=errors,
    )
    _validate_impact(
        values.get("Failure-registry impact", ""),
        label="Failure-registry impact",
        owner_path=FAILURE_REGISTRY,
        changed_files=changed,
        owner_changed=FAILURE_REGISTRY in changed,
        path=path,
        errors=errors,
    )
    return [f"{path}: {error}" if not error.startswith(path + ":") else error for error in errors]


def check_changed_files(
    changed_files: Iterable[str],
    *,
    root: Path = ROOT,
    head_ref: str = "HEAD",
    contents: Mapping[str, str | None] | None = None,
    logic_map_text: str | None = None,
    registry_text: str | None = None,
) -> list[str]:
    """Validate a supplied change set; useful for tests and non-Git callers."""

    changed = {_normalise_path(item) for item in changed_files}
    if not changed:
        return []
    supplied_contents = {_normalise_path(path): text for path, text in (contents or {}).items()}
    map_text = logic_map_text if logic_map_text is not None else supplied_contents.get(LOGIC_MAP)
    if map_text is None:
        map_text = _read_at_ref(LOGIC_MAP, head_ref, cwd=root) or ""
    registry_text = registry_text if registry_text is not None else supplied_contents.get(FAILURE_REGISTRY)
    if registry_text is None:
        registry_text = _read_at_ref(FAILURE_REGISTRY, head_ref, cwd=root) or ""

    def content_for(path: str) -> str | None:
        if path in supplied_contents:
            return supplied_contents[path]
        return _read_at_ref(path, head_ref, cwd=root)

    errors: list[str] = []
    design_docs = sorted(path for path in changed if is_detector_design_path(path))
    validation_docs = sorted(path for path in changed if is_detector_validation_path(path))
    field_docs = sorted(path for path in changed if is_field_evidence_path(path))
    detector_code = sorted(path for path in changed if is_detector_code_path(path))

    design_contents = {path: content_for(path) for path in design_docs}
    field_contents = {path: content_for(path) for path in field_docs}
    present_design_docs = sorted(path for path, text in design_contents.items() if text is not None)
    present_field_docs = sorted(path for path, text in field_contents.items() if text is not None)

    if detector_code and not present_design_docs:
        errors.append(
            "detector code changed without a changed S11 architecture/design document "
            "containing a valid `## History Review` block"
        )
    if validation_docs and not present_design_docs:
        errors.append(
            "S11 detector validation changed without a companion S11 architecture/design "
            "document containing a valid `## History Review` block"
        )
    if LOGIC_MAP in changed and not present_design_docs:
        errors.append(
            "current detector logic map changed without a changed S11 architecture/design "
            "document containing a valid `## History Review` block"
        )
    if FAILURE_REGISTRY in changed and not (present_design_docs or present_field_docs):
        errors.append(
            "detector mechanism failure registry changed without a changed S11 design, "
            "diagnostic, or evidence document explaining the impact"
        )

    for path in present_design_docs:
        errors.extend(
            validate_history_review(
                path,
                design_contents[path] or "",
                changed_files=changed,
                logic_map_text=map_text,
                registry_text=registry_text,
            )
        )
    for path in present_field_docs:
        errors.extend(
            validate_detector_governance(
                path,
                field_contents[path] or "",
                changed_files=changed,
                logic_map_text=map_text,
                registry_text=registry_text,
            )
        )
    return errors


def check_refs(
    base_ref: str,
    head_ref: str = "HEAD",
    *,
    root: Path = ROOT,
    include_worktree: bool = False,
) -> list[str]:
    try:
        comparison_base = _git("merge-base", base_ref, head_ref, cwd=root).strip()
        changed = discover_changed_files(base_ref, head_ref, cwd=root)
        worktree_changed = discover_worktree_files(cwd=root) if include_worktree else set()
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"unable to discover changes for {base_ref}...{head_ref}: {exc}"]
    changed.update(worktree_changed)
    # Only exact before/after evidence can exempt a source path. The path-only
    # check_changed_files API remains conservative when no baseline is supplied.
    changed = {
        path for path in changed
        if not (
            is_detector_code_path(path) and path.endswith(".py")
            and _same_python_ast(
                _python_snapshot(path, comparison_base, root=root),
                _python_snapshot(path, None if path in worktree_changed else head_ref, root=root),
            )
        )
    }
    contents: dict[str, str | None] = {}
    for path in worktree_changed:
        worktree_path = root / path
        if not worktree_path.is_file():
            contents[path] = None
            continue
        try:
            contents[path] = worktree_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    return check_changed_files(changed, root=root, head_ref=head_ref, contents=contents)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True, help="Git base ref for the change range")
    parser.add_argument("--head-ref", default="HEAD", help="Git head ref (default: HEAD)")
    parser.add_argument(
        "--include-worktree",
        action="store_true",
        help="also validate tracked and untracked worktree changes",
    )
    args = parser.parse_args(argv)
    errors = check_refs(
        args.base_ref,
        args.head_ref,
        include_worktree=args.include_worktree,
    )
    if errors:
        print("S11 detector governance FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("S11 detector governance passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
