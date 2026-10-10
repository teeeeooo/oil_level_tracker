"""Time arithmetic and real saved-replay CLI controls, not detector efficacy."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_observation_cadence as cadence


def row(frame, timestamp, y="10", valid="True", glass="g"):
    return {"frame_index": str(frame), "timestamp_sec": str(timestamp),
            "raw_oil_air_level_y": y, "oil_is_valid": valid, "glass_id": glass}


def test_irregular_source_times_and_censored_ends_are_not_row_counts():
    rows = [row(0, 2, ""), row(1, 2.1), row(2, 2.2, ""), row(3, 3.1),
            row(4, 5.4, valid="False"), row(5, 8.1), row(6, 8.4, "")]
    before = copy.deepcopy(rows)
    result, = cadence.summarize_rows(rows)
    assert [gap["elapsed_sec"] for gap in result["intervals"]] == pytest.approx([1, 5])
    assert result["pairs_within_target"] == 1
    assert result["pairs_over_target"] == 1
    assert result["invalid_numeric_row_count"] == 1
    assert result["leading_unavailable"]["elapsed_sec"] == pytest.approx(.1)
    assert result["trailing_unavailable"]["elapsed_sec"] == pytest.approx(.3)
    assert result["physical_cadence"]["status"] == "NOT_EVALUATED"
    assert rows == before


def test_sampling_hole_counts_even_without_blank_rows_and_target_is_inclusive():
    result, = cadence.summarize_rows([row(0, 0), row(30, 1), row(90, 3)])
    assert result["pairs_within_target"] == result["pairs_over_target"] == 1
    assert result["maximum_interval_sec"] == 2
    assert all(gap["intervening_unavailable_rows"] == 0 for gap in result["intervals"])


@pytest.mark.parametrize("rows,expected_span", [
    ([row(1, 0, ""), row(3, 1, "")], [0, 1]),
    ([row(1, 0, ""), row(3, 1)], None),
    ([row(1, 0, "")], [0, 0]),
])
def test_zero_or_one_numeric_never_becomes_success(rows, expected_span):
    result, = cadence.summarize_rows(rows)
    assert result["numeric_cadence_status"] == "NO_PAIRS"
    assert result["pair_count"] == result["pairs_within_target"] == 0
    assert result["maximum_interval_sec"] is None
    assert result["all_unavailable_span_sec"] == expected_span
    assert result["physical_cadence"]["status"] == "NOT_EVALUATED"


def test_glass_streams_cannot_supply_each_others_anchors():
    results = cadence.summarize_rows([row(0, 0), row(0, 0, glass="other"),
                                     row(60, 2), row(30, 1, glass="other")])
    assert [(r["glass_id"], r["maximum_interval_sec"]) for r in results] == [("g", 2), ("other", 1)]


@pytest.mark.parametrize("bad", [
    [], [row(0, 0), row(0, 1)], [row(0, 0), row(1, 0)],
    [row(1, 1), row(2, .5)], [row(0, "NaN")], [row(0, -1)],
    [row(0, 0, "inf")], [row(0, 0, valid="yes")], [row(0, 0, glass="")],
    [row("1.0", 0)],
])
def test_bad_timeline_or_nonfinite_data_fails_closed(bad):
    with pytest.raises(ValueError):
        cadence.summarize_rows(bad)


def test_saved_cli_foreign_cwd_preserves_inputs_and_refuses_overwrite(tmp_path):
    work = tmp_path / "한글 작업 폴더"
    work.mkdir()
    source = work / "저장 결과.json"
    saved = {"schema_version": cadence.REPLAY_SCHEMA, "sample": "synthetic",
             "version": "test", "source_sha256": "a" * 64, "fingerprint": "b" * 64,
             "tracking_data.csv": [row(0, 0), row(60, 2)]}
    source.write_text(json.dumps(saved), encoding="utf-8")
    original = source.read_bytes()
    output = work / "관측 간격.json"
    command = [sys.executable, str(Path(cadence.__file__).resolve()), "--saved", str(source),
               "--output", str(output)]
    def invoke():
        return subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, encoding="utf-8", timeout=30)
    first = invoke()
    assert first.returncode == 0, first.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["comparison_scope"] == "unverified_numeric_cadence"
    assert report["physical_acceptance"] == "NOT_EVALUATED"
    assert report["saved_replays"][0]["glasses"][0]["pairs_over_target"] == 1
    published = output.read_bytes()
    assert invoke().returncode != 0
    assert output.read_bytes() == published
    assert source.read_bytes() == original


def test_measure_saved_rejects_changed_input_before_publishing(tmp_path, monkeypatch):
    source = tmp_path / "saved.json"
    source.write_text(json.dumps({"schema_version": cadence.REPLAY_SCHEMA,
        "sample": "test", "version": "test", "source_sha256": "a", "fingerprint": "b",
        "tracking_data.csv": [row(0, 0)]}), encoding="utf-8")
    read = cadence.evaluation.read_json
    def mutate(path):
        data = read(path)
        path.write_text("{}", encoding="utf-8")
        return data
    monkeypatch.setattr(cadence.evaluation, "read_json", mutate)
    with pytest.raises(ValueError, match="changed during measurement"):
        cadence.measure_saved([source])
