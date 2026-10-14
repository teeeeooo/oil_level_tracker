"""Test interaction capacity, source isolation and partial-label accounting."""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from tests.diagnostics import s11_native_contact_trial as trial


def pair(a=255, b=0, n=2):
    return {"upper": np.full((n, 3, 7, 7), a, dtype=np.uint8),
            "lower": np.full((n, 3, 7, 7), b, dtype=np.uint8)}


def row(sid, source, role=None, available=True, frame=1):
    r = dict(id=sid, source_recording=dict(path=source+".mp4", sha256=source), frame=frame,
             path_sha256=sid, availability="AVAILABLE_PARTIAL_CONTEXT" if available else "UNAVAILABLE",
             native_sides={"upper": True, "lower": True} if available else {},
             certain_boundary_role=role, allowed_boundary_roles=[role] if role else [])
    r["targets"] = trial.corpus.targets(r)
    return r


def test_interaction_equals_explicit_tensor_product_and_is_positive_semidefinite():
    rng = np.random.default_rng(5)
    a = rng.uniform(-1, 1, (4, 2, 147))
    explicit = np.stack([np.r_[1, x[0]/np.sqrt(147), x[1]/np.sqrt(147),
                                np.outer(x[0], x[1]).ravel()/147] for x in a])
    k = trial.kernel(a, a, "native_joint")
    np.testing.assert_allclose(k, explicit @ explicit.T, atol=1e-12)
    assert np.linalg.eigvalsh(k).min() > -1e-12


def test_joint_relation_can_express_xor_that_additive_sides_cannot():
    x = np.stack([trial.feature(pair(a, b), "native_joint") for a, b in
                  [(0, 0), (0, 255), (255, 0), (255, 255)]])
    y = np.array([1., -1., -1., 1.]); w = np.full(4, .25)
    for arm in ("native_joint", "native_additive"):
        alpha = trial.fit(x, y, w, arm)
        scores = trial.kernel(x, x, arm) @ alpha
        if arm == "native_joint": assert (np.sign(scores) == y).all()
        else: assert all(trial.decision(s) == "UNKNOWN" for s in scores)


def test_weighted_dual_matches_independent_primal_normal_equations():
    rng = np.random.default_rng(4)
    x = rng.uniform(-1, 1, (5, 2, 147)); y = np.array([1., -1., 1., -1., 1.])
    w = np.array([.1, .2, .2, .3, .2]); phi = np.c_[np.ones(5), x.reshape(5, -1)/np.sqrt(147)]
    primal = np.linalg.solve(phi.T @ (w[:, None]*phi) + trial.CONFIG["ridge"]*np.eye(295), phi.T @ (w*y))
    alpha = trial.fit(x, y, w, "native_additive")
    np.testing.assert_allclose(trial.kernel(x, x, "native_additive") @ alpha, phi @ primal, atol=1e-11)


def test_native_pattern_ablation_and_equal_path_weight():
    p = pair(); p["upper"][:, :, :, ::2] = 0
    native = trial.feature(p, "native_joint"); mean = trial.feature(p, "mean_joint")
    assert not np.allclose(native, mean)
    np.testing.assert_allclose(native.mean(axis=1), mean.mean(axis=1))
    duplicated = {k: np.tile(v, (3, 1, 1, 1)) for k, v in p.items()}
    np.testing.assert_allclose(trial.feature(duplicated, "native_joint"), native, atol=1e-15)
    np.testing.assert_allclose(trial.feature(p, "native_additive"), native)


@pytest.mark.parametrize("fault", ["missing_side", "empty", "float", "shape"])
def test_feature_input_fails_closed(fault):
    p = pair()
    if fault == "missing_side": del p["upper"]
    if fault == "empty": p["upper"] = p["upper"][:0]
    if fault == "float": p["upper"] = p["upper"].astype(float)
    if fault == "shape": p["upper"] = p["upper"][:, :, :, :6]
    with pytest.raises(ValueError): trial.feature(p, "native_joint")


def test_all_frames_of_held_recording_and_unlabelled_paths_stay_out_of_fit():
    rows = [row("a", "train", "FOAM_UPPER"), row("b", "train", "STRUCTURE_BOUNDARY"),
            row("c", "held", "FOAM_UPPER"), row("d", "held", "STRUCTURE_BOUNDARY", frame=2),
            row("unknown", "train"), row("liquid", "train", "LIQUID_UPPER"),
            row("unavailable", "train", "FOAM_UPPER", available=False)]
    chosen, y, w = trial.training_rows(rows, "held", "FOAM_UPPER")
    assert [r["id"] for r in chosen] == ["a", "b"]
    np.testing.assert_array_equal(y, [1, -1]); np.testing.assert_array_equal(w, [.5, .5])


def test_class_and_source_weighting_not_path_count_dominance():
    rows = [row("a", "one", "FOAM_UPPER"), row("b", "one", "FOAM_UPPER"),
            row("c", "two", "FOAM_UPPER"), row("d", "one", "STRUCTURE_BOUNDARY")]
    _, _, w = trial.training_rows(rows, "held", "FOAM_UPPER")
    np.testing.assert_allclose(w, [.125, .125, .25, .5])


@pytest.mark.parametrize("score,expected", [(None, "UNAVAILABLE"), (0, "UNKNOWN"),
    (1e-10, "UNKNOWN"), (-1e-10, "UNKNOWN"), (1e-8, "POSITIVE"), (-1e-8, "OPPOSITION")])
def test_fixed_operating_point_never_calls_missing_a_negative(score, expected):
    assert trial.decision(score) == expected


def test_nonfinite_prediction_rejected():
    with pytest.raises(ValueError): trial.decision(float("nan"))


def fixture():
    rows = []
    for source in ("one", "two"):
        rows += [row(source+"-foam", source, "FOAM_UPPER"), row(source+"-liquid", source, "LIQUID_UPPER"),
                 row(source+"-rim", source, "STRUCTURE_BOUNDARY"), row(source+"-unknown", source),
                 row(source+"-missing", source, available=False)]
    arrays = {r["id"]: pair(255 if r["certain_boundary_role"] == "STRUCTURE_BOUNDARY" else 0, 255)
              for r in rows if r["native_sides"]}
    return dict(rows=rows, counts=dict(total=10)), arrays


def test_full_entry_preserves_unknown_missing_and_channel_specific_targets():
    data, arrays = fixture(); original = deepcopy(data)
    result = trial.evaluate(data, arrays)
    assert len(result["rows"]) == 10 and result["total_fits"] == 12
    for r in result["rows"]:
        if r["id"].endswith("missing"):
            assert all(v == "UNAVAILABLE" for a in r["decisions"].values() for v in a.values())
        if r["id"].endswith("unknown"): assert all(v is None for v in r["targets"].values())
        if r["id"].endswith("foam"): assert r["targets"]["LIQUID_UPPER"] is None
    assert all(result["summaries"][a][c]["required"] == 4 for a in trial.ARMS for c in trial.corpus.CHANNELS)
    assert data == original


def test_held_source_labels_do_not_change_its_model_or_scores():
    data, arrays = fixture(); first = trial.evaluate(data, arrays)
    for r in data["rows"]:
        if r["source_recording"]["sha256"] == "two" and r["targets"]["values"]["FOAM_UPPER"] is not None:
            r["targets"]["values"]["FOAM_UPPER"] ^= 1
    second = trial.evaluate(data, arrays)
    assert [m for m in first["models"] if m["held_out_source"] == "two"] == [m for m in second["models"] if m["held_out_source"] == "two"]
    assert [r["scores"] for r in first["rows"] if r["source_recording"]["sha256"] == "two"] == [r["scores"] for r in second["rows"] if r["source_recording"]["sha256"] == "two"]


def test_unknown_on_required_opposition_cannot_pass():
    data, arrays = fixture(); result = trial.evaluate(data, arrays)
    rim = next(r for r in result["rows"] if r["id"] == "one-rim")
    rim["decisions"]["native_joint"]["FOAM_UPPER"] = "UNKNOWN"
    summary = trial.summarize(result["rows"], "native_joint")
    assert "one-rim" in summary["FOAM_UPPER"]["opposition_failure"]
    assert summary["status"] == "CLOSED_WITHOUT_PROMOTION"


def test_disjunction_cannot_be_counted_as_two_targets():
    data, arrays = fixture(); r = data["rows"][3]
    r["allowed_boundary_roles"] = ["FOAM_UPPER", "LIQUID_UPPER"]
    r["targets"] = trial.corpus.targets(r)
    result = trial.evaluate(data, arrays)
    for a in trial.ARMS:
        assert result["summaries"][a]["disjunction"]["required"] == 1
        assert all(result["summaries"][a][c]["required"] == 4 for c in trial.corpus.CHANNELS)


def test_changed_corpus_pin_rejected_before_fitting(tmp_path):
    p = tmp_path / "corpus.json"; p.write_text("{}", encoding="utf-8")
    plan = dict(schema=trial.SCHEMA, configuration=trial.CONFIG, limits=trial.LIMITS, runtime=trial.runtime(),
                sources=[], corpus=dict(path="corpus.json", sha256="0"*64))
    with pytest.raises(ValueError, match="hash mismatch"): trial.load_inputs(tmp_path, plan)


def test_cli_foreign_cwd_and_overwrite_refusal(tmp_path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1"); env.pop("PYTHONPATH", None)
    def invoke(*args):
        return subprocess.run([sys.executable, "-B", str(Path(trial.__file__).resolve()), *args],
            cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True,
            text=True, encoding="utf-8", timeout=20)
    assert invoke("--help").returncode == 0
    output = tmp_path / "고정 결과.json"; output.write_bytes(b"original")
    result = invoke("--plan", "missing.json", "--output", str(output))
    assert result.returncode != 0 and "refuse overwrite" in result.stderr
    assert output.read_bytes() == b"original"
