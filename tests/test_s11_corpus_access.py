from __future__ import annotations

from hashlib import sha256
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_corpus_access import (
    SAMPLE3_PURPOSE_ENV,
    SAMPLE3_PURPOSES,
    RestrictedCorpusUseError,
    require_corpus_access,
)
from tests.diagnostics.s11_evidence_probe import (
    CORPUS_MANIFEST_RELATIVE_PATH,
    CORPUS_STEMS,
    load_cases,
    repository_root,
)
from tests.diagnostics.s11_replay_provenance import validate_frozen_inputs
from tests.diagnostics import s11_replay_provenance as provenance
from tests.s11_local_corpus import require_s11_local_corpus


@pytest.fixture(autouse=True)
def no_ambient_permission(monkeypatch):
    monkeypatch.delenv(SAMPLE3_PURPOSE_ENV, raising=False)


@pytest.mark.parametrize("purpose", [None, "", "physical-accuracy", "true"])
def test_missing_or_unrecognized_purpose_blocks_sample3(monkeypatch, purpose):
    if purpose is not None:
        monkeypatch.setenv(SAMPLE3_PURPOSE_ENV, purpose)
    with pytest.raises(RestrictedCorpusUseError, match="QUARANTINED"):
        require_corpus_access(CORPUS_STEMS)
    assert require_corpus_access(("sample4",))["restricted_samples"] == []


@pytest.mark.parametrize("purpose", SAMPLE3_PURPOSES)
def test_explicit_purpose_is_recorded_without_physical_acceptance(monkeypatch, purpose):
    monkeypatch.setenv(SAMPLE3_PURPOSE_ENV, purpose)
    result = require_corpus_access(CORPUS_STEMS)
    assert result["sample3_purpose"] == purpose
    assert result["restricted_samples"] == ["sample3"]
    assert result["physical_acceptance"] == "NOT_EVALUATED"


@pytest.mark.parametrize("module,entry", [
    ("s11_report_observability_replay", "run_replay"),
    ("s11_r7_evidence_tiered_replay", "run_r7_replay"),
    ("s11_r8_observation_recovery_replay", "run_r8_replay"),
    ("s11_r9_calibrated_observation_replay", "run_r9_replay"),
    ("s11_r10_calibrated_path_and_layer_replay", "run_r10_replay"),
    ("s11_r11_bounded_material_identity_replay", "run_r11_replay"),
    ("s11_r12_phase_composition_replay", "run_r12_replay"),
    ("s11_r13_phase_identity_replay", "run_r13_replay"),
    ("s11_r14_phase_component_replay", "run_r14_replay"),
    ("s11_r15_material_ownership_replay", "run_r15_replay"),
    ("s11_r17_physical_observation_ownership_replay", "run_r17_replay"),
    ("s11_r18_lifecycle_closure_replay", "run_r18_replay"),
])
def test_full_replay_entries_stop_before_loading_or_starting_workers(tmp_path, module, entry):
    run = getattr(importlib.import_module(f"tests.diagnostics.{module}"), entry)
    output = tmp_path / "no partial replay"
    with pytest.raises(RestrictedCorpusUseError, match="QUARANTINED"):
        run(root=tmp_path, output_root=output)
    assert not output.exists()


def test_direct_session_stops_before_reading_recipe_or_video(tmp_path):
    with pytest.raises(RestrictedCorpusUseError, match="QUARANTINED"):
        replay._session("sample3", tmp_path / "sample3.mp4", tmp_path,
                        30.03, 105.0, run_label="test", run_note="test")


def test_frozen_input_preflight_requires_purpose_without_changing_identities(tmp_path, monkeypatch):
    expected = {"sample3": {}}
    sample_dir = tmp_path / "sample"
    sample_dir.mkdir()
    for suffix in ("mp4", "oilrecipe", "oiltruth"):
        data = f"sample3-{suffix}".encode("utf-8")
        (sample_dir / f"sample3.{suffix}").write_bytes(data)
        expected["sample3"][suffix] = sha256(data).hexdigest()
    with pytest.raises(RestrictedCorpusUseError):
        validate_frozen_inputs(root=tmp_path, expected_inputs=expected, samples=("sample3",))
    monkeypatch.setenv(SAMPLE3_PURPOSE_ENV, "engineering-replay")
    assert validate_frozen_inputs(
        root=tmp_path, expected_inputs=expected, samples=("sample3",)
    ) == expected


def test_runtime_provenance_blocks_before_backend_open_and_keeps_fingerprint(monkeypatch):
    def unexpected_open(_path):
        pytest.fail("quarantined video backend must not be opened")

    monkeypatch.setattr(provenance, "_video_backend_name", unexpected_open)
    with pytest.raises(RestrictedCorpusUseError):
        provenance.capture_runtime_provenance(Path("sample3.mp4"))
    monkeypatch.setattr(provenance, "_video_backend_name", lambda _path: "TEST")
    captures = []
    for purpose in SAMPLE3_PURPOSES:
        monkeypatch.setenv(SAMPLE3_PURPOSE_ENV, purpose)
        capture = provenance.capture_runtime_provenance(Path("sample3.mp4"))
        assert capture["corpus_access"]["sample3_purpose"] == purpose
        captures.append(capture)
    assert captures[0]["runtime_fingerprint_sha256"] == captures[1]["runtime_fingerprint_sha256"]
    original_signature = {key: value for key, value in captures[0].items()
                          if key not in {"schema", "corpus_access", "runtime_fingerprint_sha256"}}
    encoded = json.dumps(original_signature, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    assert captures[0]["runtime_fingerprint_sha256"] == sha256(encoded).hexdigest()


def test_complete_corpus_is_explicitly_skipped_by_default(tmp_path):
    # Identity-correct synthetic files exercise admission without depending on media.
    (tmp_path / "sample").mkdir()
    inputs = {}
    for sample in CORPUS_STEMS:
        data = sample.encode("utf-8")
        (tmp_path / "sample" / f"{sample}.mp4").write_bytes(data)
        inputs[sample] = {"mp4": sha256(data).hexdigest()}
    manifest = tmp_path / CORPUS_MANIFEST_RELATIVE_PATH
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"inputs": inputs}), encoding="utf-8")
    with pytest.raises(pytest.skip.Exception, match="QUARANTINED"):
        require_s11_local_corpus(tmp_path)


def test_opt_in_retains_complete_original_thirteen_case_inventory(monkeypatch):
    monkeypatch.setenv(SAMPLE3_PURPOSE_ENV, "legacy-regression")
    root = require_s11_local_corpus()
    cases = load_cases(root)
    assert {case.case_id for case in cases} == {
        "base_sample_1:144", "base_sample_1:156", "base_sample_1:240",
        "sample2:0", "sample2:30", "sample2:60", "sample3:900", "sample3:1035",
        "sample4:0", "sample4:450", "sample4:900", "sample4:1470", "sample4:1680",
    }
    assert len(cases) == 13
    assert tuple(replay.QUALIFICATION_WINDOWS) == CORPUS_STEMS
    assert replay.ACCEPTED_ROW_COUNTS["sample3"] == 151


def _wrapper(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repository_root())
    env.pop(SAMPLE3_PURPOSE_ENV, None)
    return subprocess.run(
        [sys.executable, "-m", "tests.diagnostics.s11_corpus_access", *args],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )


def test_wrapper_scopes_permission_and_preserves_child_arguments_and_exit(tmp_path):
    script = (
        "import json, sys; "
        "from tests.diagnostics.s11_corpus_access import require_corpus_access; "
        "print(json.dumps([require_corpus_access(('sample3',)), sys.argv[1:]])); "
        "sys.exit(7)"
    )
    completed = _wrapper(tmp_path, "--purpose", "legacy-regression", "--",
                         sys.executable, "-c", script, "한글 path with spaces", "--literal")
    assert completed.returncode == 7
    access, arguments = json.loads(completed.stdout)
    assert access["sample3_purpose"] == "legacy-regression"
    assert arguments == ["한글 path with spaces", "--literal"]
    assert "physical_acceptance=NOT_EVALUATED" in completed.stderr
    assert SAMPLE3_PURPOSE_ENV not in os.environ


def test_real_replay_cli_rejects_default_before_creating_output(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repository_root())
    env.pop(SAMPLE3_PURPOSE_ENV, None)
    output = tmp_path / "blocked replay"
    completed = subprocess.run(
        [sys.executable, "-m", "tests.diagnostics.s11_r17_physical_observation_ownership_replay",
         "--root", str(repository_root()), "--output-root", str(output)],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert completed.returncode != 0
    assert "QUARANTINED" in completed.stderr
    assert not output.exists()


@pytest.mark.parametrize("args", [[], ["--purpose", "physical-accuracy"],
                                     ["--purpose", "engineering-replay", "--"]])
def test_wrapper_rejects_missing_purpose_command_or_unknown_use(tmp_path, args):
    assert _wrapper(tmp_path, *args).returncode == 2
