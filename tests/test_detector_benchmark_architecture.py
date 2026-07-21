from __future__ import annotations

import ast
from pathlib import Path

from oil_tracker.adapters.storage.regression_fixture_exporter import (
    DATASET_SCHEMA_VERSION,
    FIXTURE_SCHEMA_VERSION,
    TRUTH_FIXTURE_SCHEMA_VERSION,
)
from oil_tracker.domain.user_truth import TRUTH_SCHEMA_VERSION


ROOT = Path(__file__).resolve().parents[1]


def _import_roots(path: Path) -> set[str]:
    roots = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def test_benchmark_domain_and_application_keep_vision_and_ui_dependencies_out():
    paths = [
        ROOT / "src/oil_tracker/domain/detector_benchmark.py",
        ROOT / "src/oil_tracker/application/ports/regression_dataset_reader.py",
        ROOT / "src/oil_tracker/application/ports/benchmark_result_writer.py",
        ROOT / "src/oil_tracker/application/services/detector_benchmark_service.py",
    ]
    forbidden = {"PySide6", "cv2", "numpy", "matplotlib", "jinja2"}
    assert {path.name: _import_roots(path) & forbidden for path in paths} == {
        "detector_benchmark.py": set(),
        "regression_dataset_reader.py": set(),
        "benchmark_result_writer.py": set(),
        "detector_benchmark_service.py": set(),
    }


def test_benchmark_cli_has_no_pyside_or_ui_import():
    path = ROOT / "src/oil_tracker/cli.py"
    source = path.read_text(encoding="utf-8")
    assert "PySide6" not in _import_roots(path)
    assert "oil_tracker.ui" not in source
    assert "oil_tracker.bootstrap" not in source


def test_phase_2c3_truth_and_fixture_schema_versions_remain_unchanged():
    assert TRUTH_SCHEMA_VERSION == 1
    assert DATASET_SCHEMA_VERSION == 1
    assert FIXTURE_SCHEMA_VERSION == 1
    assert TRUTH_FIXTURE_SCHEMA_VERSION == 1


def test_benchmark_does_not_change_official_bundle_or_truth_modules():
    output_store = (ROOT / "src/oil_tracker/adapters/storage/output_bundle_store.py").read_text(
        encoding="utf-8"
    )
    truth_domain = (ROOT / "src/oil_tracker/domain/user_truth.py").read_text(
        encoding="utf-8"
    )
    exporter = (
        ROOT / "src/oil_tracker/adapters/storage/regression_fixture_exporter.py"
    ).read_text(encoding="utf-8")
    assert "detector_benchmark" not in output_store
    assert "detector_benchmark" not in truth_domain
    assert "benchmark_catalog" not in exporter
