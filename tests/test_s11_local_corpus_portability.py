from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest

from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics.s11_evidence_probe import (
    CORPUS_MANIFEST_RELATIVE_PATH,
    CORPUS_STEMS,
    LocalCorpusIdentityError,
    LocalCorpusUnavailableError,
    ProbeCase,
    decode_frame,
    validate_local_corpus,
)


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _write_manifest(root: Path, expected: dict[str, bytes]) -> None:
    path = root / CORPUS_MANIFEST_RELATIVE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "inputs": {
            sample: {"mp4": _digest(expected[sample])}
            for sample in CORPUS_STEMS
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_mp4(root: Path, sample: str, data: bytes) -> Path:
    path = root / "sample" / f"{sample}.mp4"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def test_missing_required_corpus_is_explicitly_unavailable(tmp_path: Path) -> None:
    expected = {sample: f"expected-{sample}".encode() for sample in CORPUS_STEMS}
    _write_manifest(tmp_path, expected)
    with pytest.raises(LocalCorpusUnavailableError, match="NOT AVAILABLE"):
        validate_local_corpus(tmp_path)


def test_wrong_identity_fails_before_missing_corpus_can_skip(tmp_path: Path) -> None:
    expected = {sample: f"expected-{sample}".encode() for sample in CORPUS_STEMS}
    _write_manifest(tmp_path, expected)
    _write_mp4(tmp_path, CORPUS_STEMS[0], b"wrong-file-bytes")
    with pytest.raises(LocalCorpusIdentityError, match="identity mismatch") as exc:
        validate_local_corpus(tmp_path)
    assert "actual=" in str(exc.value)
    assert "expected=" in str(exc.value)


def test_all_correct_corpus_identities_are_accepted(tmp_path: Path) -> None:
    expected = {sample: f"expected-{sample}".encode() for sample in CORPUS_STEMS}
    _write_manifest(tmp_path, expected)
    for sample, data in expected.items():
        _write_mp4(tmp_path, sample, data)
    validate_local_corpus(tmp_path)


def test_correct_identity_decode_failure_remains_hard_failure(tmp_path: Path) -> None:
    expected = {sample: f"invalid-video-{sample}".encode() for sample in CORPUS_STEMS}
    _write_manifest(tmp_path, expected)
    paths = {
        sample: _write_mp4(tmp_path, sample, data)
        for sample, data in expected.items()
    }
    validate_local_corpus(tmp_path)

    glass = InspectionRecipe.default_glass(320, 240)
    case = ProbeCase(
        sample=CORPUS_STEMS[0],
        frame_index=0,
        time_sec=0.0,
        truth_oil_y=0.0,
        truth_foam_present=False,
        truth_foam_y=None,
        glass=glass,
        video_path=paths[CORPUS_STEMS[0]],
    )
    with pytest.raises(RuntimeError, match="Could not decode"):
        decode_frame(case)
