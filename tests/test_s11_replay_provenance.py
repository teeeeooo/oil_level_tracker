from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pytest

from tests.diagnostics import s11_r16_performance_profile as performance_profile
from tests.diagnostics.s11_replay_provenance import (
    ReplayInputIdentityError,
    ReplayInputUnavailableError,
    classify_exact_reproducibility,
    enforce_exact_tracking_contract,
    validate_frozen_inputs,
)


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _write_input(root: Path, sample: str, suffix: str, data: bytes) -> None:
    path = root / "sample" / f"{sample}.{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _expected(sample: str = "sample4") -> dict[str, dict[str, str]]:
    return {
        sample: {
            suffix: _digest(f"{sample}-{suffix}".encode())
            for suffix in ("mp4", "oilrecipe", "oiltruth")
        }
    }


def test_replay_input_preflight_covers_media_recipe_and_truth(tmp_path: Path) -> None:
    expected = _expected()
    for suffix in ("mp4", "oilrecipe", "oiltruth"):
        _write_input(tmp_path, "sample4", suffix, f"sample4-{suffix}".encode())

    assert validate_frozen_inputs(
        root=tmp_path,
        expected_inputs=expected,
        samples=("sample4",),
    ) == expected

    _write_input(tmp_path, "sample4", "oilrecipe", b"changed-recipe")
    with pytest.raises(ReplayInputIdentityError, match="oilrecipe"):
        validate_frozen_inputs(
            root=tmp_path,
            expected_inputs=expected,
            samples=("sample4",),
        )


def test_replay_input_preflight_reports_missing_truth(tmp_path: Path) -> None:
    expected = _expected()
    for suffix in ("mp4", "oilrecipe"):
        _write_input(tmp_path, "sample4", suffix, f"sample4-{suffix}".encode())

    with pytest.raises(ReplayInputUnavailableError, match="oiltruth"):
        validate_frozen_inputs(
            root=tmp_path,
            expected_inputs=expected,
            samples=("sample4",),
        )


def test_tracking_mismatch_is_hard_failure_in_same_runtime() -> None:
    classification = classify_exact_reproducibility(
        actual_tracking_fingerprint="actual",
        expected_tracking_fingerprint="expected",
        actual_runtime_fingerprint="runtime-a",
        expected_runtime_fingerprint="runtime-a",
    )
    assert classification == {
        "runtime_status": "MATCH",
        "tracking_status": "MISMATCH",
        "interpretation": "TRACKING_MISMATCH_SAME_RUNTIME",
    }
    with pytest.raises(AssertionError, match="TRACKING_MISMATCH_SAME_RUNTIME"):
        enforce_exact_tracking_contract(
            actual_tracking_fingerprint="actual",
            expected_tracking_fingerprint="expected",
            actual_runtime_fingerprint="runtime-a",
            expected_runtime_fingerprint="runtime-a",
        )


def test_tracking_mismatch_is_classified_as_environment_drift() -> None:
    classification = enforce_exact_tracking_contract(
        actual_tracking_fingerprint="actual",
        expected_tracking_fingerprint="expected",
        actual_runtime_fingerprint="runtime-b",
        expected_runtime_fingerprint="runtime-a",
    )
    assert classification == {
        "runtime_status": "ENVIRONMENT_DRIFT",
        "tracking_status": "MISMATCH",
        "interpretation": "ENVIRONMENT_DRIFT",
    }


def test_performance_profile_rejects_runtime_drift_before_comparison() -> None:
    performance_profile._require_runtime_match("runtime-a", None)
    performance_profile._require_runtime_match("runtime-a", "runtime-a")
    with pytest.raises(RuntimeError, match="runtime environment drift"):
        performance_profile._require_runtime_match("runtime-b", "runtime-a")
