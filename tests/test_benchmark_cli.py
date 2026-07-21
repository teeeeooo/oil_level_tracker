from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys

import pytest

from benchmark_fixtures import export_benchmark_dataset, fixture_directory
from oil_tracker import cli
from oil_tracker.domain.detector_benchmark import BenchmarkComparisonError


@dataclass
class _Run:
    output_path: Path
    payload: dict


class _FakeService:
    calls = []
    error = None

    def __init__(self, reader, writer, detector_factory):
        self.reader = reader
        self.writer = writer
        self.detector_factory = detector_factory

    def run(self, dataset, output, *, baseline_path=None):
        type(self).calls.append((dataset, output, baseline_path))
        if type(self).error is not None:
            raise type(self).error
        return _Run(
            Path(output) / "detector_benchmark_dataset_timestamp",
            {
                "case_count": 4,
                "usable_count": 3,
                "unusable_count": 1,
                "category_count": 2,
            },
        )


@pytest.fixture(autouse=True)
def _reset_fake():
    _FakeService.calls = []
    _FakeService.error = None


def test_parser_exposes_benchmark_dataset_output_and_baseline():
    args = cli.build_parser().parse_args(
        [
            "benchmark",
            "--dataset",
            "dataset",
            "--output",
            "output",
            "--baseline",
            "previous.json",
        ]
    )
    assert args.command == "benchmark"
    assert args.dataset == "dataset"
    assert args.output == "output"
    assert args.baseline == "previous.json"


def test_normal_benchmark_command_prints_output_path_and_counts(monkeypatch, capsys):
    monkeypatch.setattr(cli, "DetectorBenchmarkService", _FakeService)
    code = cli.main(
        ["benchmark", "--dataset", "data", "--output", "results"]
    )
    assert code == 0
    assert _FakeService.calls == [("data", "results", None)]
    output = capsys.readouterr().out
    assert "benchmark output: results/detector_benchmark_dataset_timestamp" in output
    assert "total=4 usable=3 unusable=1 categories=2" in output


def test_previous_baseline_option_is_forwarded(monkeypatch):
    monkeypatch.setattr(cli, "DetectorBenchmarkService", _FakeService)
    assert (
        cli.main(
            [
                "benchmark",
                "--dataset",
                "data",
                "--output",
                "results",
                "--baseline",
                "previous.json",
            ]
        )
        == 0
    )
    assert _FakeService.calls == [("data", "results", "previous.json")]


def test_invalid_dataset_and_baseline_mismatch_return_nonzero_without_traceback(
    monkeypatch, capsys
):
    monkeypatch.setattr(cli, "DetectorBenchmarkService", _FakeService)
    _FakeService.error = ValueError("malformed dataset")
    assert cli.main(["benchmark", "--dataset", "bad"]) == 2
    error = capsys.readouterr().err
    assert "malformed dataset" in error
    assert "Traceback" not in error

    _FakeService.error = BenchmarkComparisonError("dataset fingerprint mismatch")
    assert cli.main(["benchmark", "--dataset", "data", "--baseline", "old.json"]) == 2
    error = capsys.readouterr().err
    assert "dataset fingerprint mismatch" in error
    assert "Traceback" not in error


def test_real_hash_mismatch_is_rejected_before_detector_or_output(tmp_path, capsys):
    dataset_root = export_benchmark_dataset(tmp_path, label="cli-hash")
    frame = fixture_directory(dataset_root) / "frame.png"
    frame.write_bytes(frame.read_bytes() + b"tamper")
    output = tmp_path / "output"
    code = cli.main(
        [
            "benchmark",
            "--dataset",
            str(dataset_root),
            "--output",
            str(output),
        ]
    )
    assert code != 0
    assert "SHA-256 mismatch" in capsys.readouterr().err
    assert not list(output.glob("detector_benchmark_*")) if output.exists() else True


def test_cli_import_is_headless_and_does_not_initialize_qt(tmp_path):
    code = (
        "import sys; import oil_tracker.cli; "
        "assert 'PySide6' not in sys.modules; "
        "assert 'oil_tracker.bootstrap' not in sys.modules"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
