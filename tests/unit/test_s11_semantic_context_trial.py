"""Geometry, availability and frozen semantic reduction boundaries; no weights."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.diagnostics import s11_semantic_context_trial as trial


def test_existing_roi_origin_is_reconciled_with_capture_origin():
    rgb = np.arange(8*10*3, dtype=np.uint8).reshape(8, 10, 3)
    geometry = dict(origin=[102, 203], shape=[3, 4], scale_xy=[1, 1])
    roi = trial.crop_roi(rgb, geometry, [100, 200])
    np.testing.assert_array_equal(roi, rgb[3:6, 2:6])
    np.testing.assert_array_equal(trial.crop_roi(roi, geometry, [102, 203]), roi)


@pytest.mark.parametrize("geometry", [dict(origin=[99, 200], shape=[3, 4], scale_xy=[1, 1]),
    dict(origin=[102, 203], shape=[6, 4], scale_xy=[1, 1]),
    dict(origin=[102, 203], shape=[3, 4], scale_xy=[2, 2])])
def test_crop_cannot_invent_pixels_or_scale(geometry):
    with pytest.raises(ValueError, match="native ROI"):
        trial.crop_roi(np.zeros((8, 10, 3), np.uint8), geometry, [100, 200])


def test_union_is_pixelwise_before_patch_means_and_rim_is_not_a_veto():
    support = np.zeros((3, 9, 9), np.float32)
    support[0, :, ::2] = 1
    support[1, :, 1::2] = 1
    support[2] = 1
    row = trial.reduce_support(support, [[4, 4]])
    assert row["foreground_mean"] == 1
    assert row["prompt_means"] == [3/7, 4/7, 1]
    assert max(row["prompt_means"][:2]) < row["foreground_mean"]


def test_equal_patch_weight_and_signed_foreground_transition():
    support = np.zeros((3, 19, 15), np.float32)
    support[0, 9:] = 0.75
    support[1, 9:] = 0.5
    upper = trial.reduce_support(support, [[4, 4], [10, 4]])
    lower = trial.reduce_support(support, [[4, 14], [10, 14]])
    assert upper["foreground_mean"] == 0
    assert lower["foreground_mean"] == 0.75
    assert len(lower["foreground_patch_means"]) == 2
    pairs = {"recording": [["upper", "structure"]]}
    assert trial.order.compare({"upper": 0.75, "structure": 0.1}, pairs)["ordered"] == 1
    assert trial.order.compare({"upper": -0.75, "structure": 0.1}, pairs)["ordered"] == 0
    assert trial.order.compare({"upper": 0, "structure": 0}, pairs)["ties"] == 1


@pytest.mark.parametrize("centers", [[], [[4, 4], [4, 4]], [[2, 4]], [[6, 4]], [[4.0, 4]]])
def test_unavailable_duplicate_or_outside_support_cannot_get_a_score(centers):
    with pytest.raises(ValueError, match="support"):
        trial.reduce_support(np.zeros((3, 9, 9)), centers)


@pytest.mark.parametrize("value", [np.full((3, 9, 9), np.nan), np.full((3, 9, 9), -0.1),
                                   np.ones((2, 9, 9)), np.full((3, 9, 9), 1.1)])
def test_invalid_model_support_fails_closed(value):
    with pytest.raises(ValueError, match="finite support"):
        trial.reduce_support(value, [[4, 4]])


def test_independent_interpolation_preserves_constant_planes_at_edges():
    raw = np.stack([np.full((2, 2), x) for x in [-1., 1., 0.]])
    value = trial.sparse_reference(raw, (10, 12), [[3, 3], [8, 6]])
    expected = 1/(1+np.exp(-np.array([-1., 1., 0.])))
    np.testing.assert_allclose(value["prompt_patch_means"], [expected, expected], atol=1e-14)
    assert value["foreground_mean"] == pytest.approx(expected[1])


def test_independent_interpolation_at_native_scale_does_not_shift_pixels():
    raw = np.arange(3*9*9, dtype=float).reshape(3, 9, 9)/60-2
    value = trial.sparse_reference(raw, (9, 9), [[4, 4]])
    exact = 1/(1+np.exp(-raw[:, 1:8, 1:8]))
    np.testing.assert_allclose(value["prompt_patch_means"][0], exact.mean(axis=(1, 2)), atol=1e-14)
    assert value["foreground_mean"] == pytest.approx(np.maximum(exact[0], exact[1]).mean())


def test_existing_output_refused_before_loading_model_or_manifest(tmp_path):
    output = tmp_path / "readout.json"; output.write_bytes(b"preserved")
    with pytest.raises(ValueError, match="overwrite"):
        trial.run(tmp_path, tmp_path / "absent.json", output)
    assert output.read_bytes() == b"preserved"


def test_real_cli_help_outside_repository_needs_no_transformers(tmp_path):
    result = subprocess.run([sys.executable, str(Path(trial.__file__).resolve()), "--help"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20,
                            stdin=subprocess.DEVNULL, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert "prepare,run" in result.stdout
