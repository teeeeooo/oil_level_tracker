from __future__ import annotations

from datetime import datetime
from pathlib import Path

from oil_tracker.adapters.storage.output_bundle_store import (
    _result_bundle_name,
    _safe_run_name_component,
    _unique_path,
)
from oil_tracker.domain.session import AnalysisSession


_NOW = datetime(2026, 8, 3, 12, 34, 56)


def test_meaningful_unicode_run_name_is_recognizable():
    name = _result_bundle_name(AnalysisSession(run_name="냉방 반복 시험 03"), _NOW)

    assert name == "oil_level_analysis_냉방_반복_시험_03_20260803_123456"


def test_empty_or_unusable_run_name_uses_timestamp_fallback():
    assert _result_bundle_name(AnalysisSession(run_name=""), _NOW) == "oil_level_analysis_20260803_123456"
    assert _result_bundle_name(AnalysisSession(run_name="/\\\n\t"), _NOW) == "oil_level_analysis_20260803_123456"


def test_unsafe_filename_content_cannot_create_path_components():
    component = _safe_run_name_component("../시험/A:B*?\x00\x85 C")

    assert component == "시험_A_B_C"
    assert "/" not in component and "\\" not in component
    assert Path(component).name == component


def test_collision_suffix_is_deterministic_and_non_overwriting(tmp_path):
    requested = tmp_path / "oil_level_analysis_시험_20260803_123456"
    requested.mkdir()
    second = requested.with_name(f"{requested.name}_2")
    second.mkdir()

    candidate = _unique_path(requested)

    assert candidate.name == f"{requested.name}_3"
    assert requested.is_dir()
    assert second.is_dir()
