from copy import deepcopy
from dataclasses import asdict
import hashlib

import numpy as np
import pytest

from oil_tracker.adapters.vision import oil_candidate_rgb as rgb_module
from oil_tracker.adapters.vision.oil_candidate_evidence import candidate_is_eligible
from oil_tracker.adapters.vision.oil_candidate_rgb import COMPATIBLE, OPPOSED, OilCandidateRgb, variant_decision
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics import s11_candidate_rgb_trial as frozen


def _inputs():
    rgb = np.random.default_rng(12).integers(0, 256, (47, 49, 3), dtype=np.uint8)
    visible = np.ones(rgb.shape[:2], dtype=np.uint8) * 255
    return rgb, visible


def _annotate(model, rgb, visible, candidates, *, glare=None, origin=(100, 200), x=124):
    return model.annotate(candidates, crop_bgr=rgb[:, :, ::-1], effective_mask=visible,
                          glare_mask=np.zeros_like(visible) if glare is None else glare,
                          crop_origin=origin, source_center_x=x)


def test_native_context_and_fractional_variants_match_frozen_patch_reader():
    rgb, visible = _inputs()
    visible[10:13, 12:19] = 0
    candidates = [BoundaryCandidate("a", BoundaryKind.OIL_AIR, 222.5)]
    annotated, summary = _annotate(OilCandidateRgb(), rgb, visible, candidates)
    assert candidates[0].features == {}
    variants = annotated[0].features["oil_candidate_rgb_variants"]
    assert [v["source_y"] for v in variants] == [222, 223]
    for variant in variants:
        expected = frozen.context(rgb, visible > 0, [24, variant["source_y"] - 200])
        assert variant["status"] == expected["status"]
        for side in ("upper", "lower"):
            assert variant[f"{side}_patch_count"] == expected["sides"][side]["patches"]
            assert variant[f"{side}_input_sha256"] == expected["sides"][side]["uint8_sha256"]
    assert summary["candidate_count"] == 1


def test_shared_strip_equals_independent_patch_inference_and_ignores_middle_gap():
    rgb, visible = _inputs()
    model = OilCandidateRgb()
    candidates = [BoundaryCandidate("a", BoundaryKind.OIL_AIR, 222.)]
    result, _ = _annotate(model, rgb, visible, candidates)
    context = frozen.context(rgb, visible > 0, [24, 22])
    means = []
    for side in ("upper", "lower"):
        embeddings = [model._encode(rgb[y-3:y+4, x-3:x+4])[0, 0]
                      for x, y in context["sides"][side]["centers"]]
        means.append(np.mean(embeddings, axis=0))
    expected = model._weights["classifier.weight"] @ np.concatenate(means) + model._weights["classifier.bias"]
    logits = result[0].features["oil_candidate_rgb_variants"][0]["logits"]
    np.testing.assert_allclose(logits, expected, atol=1e-10, rtol=0)
    changed = rgb.copy()
    changed[21:24] ^= 255
    changed[:10] ^= 255
    repeated, _ = _annotate(model, changed, visible, candidates)
    assert repeated[0].features == result[0].features


@pytest.mark.parametrize("missing", ["mask", "glare", "crop_x", "crop_y", "one_variant", "nonfinite"])
def test_missing_support_stays_unavailable_and_ineligible(missing):
    rgb, visible = _inputs()
    glare = np.zeros_like(visible)
    x, y = 124, 222.
    if missing == "mask":
        visible[10:21] = 0
    elif missing == "glare":
        glare[10:21] = 255
    elif missing == "crop_x":
        x = 111
    elif missing == "crop_y":
        y = 211.
    elif missing == "one_variant":
        y = 234.5  # floor fits; ceil has less than 12 rows below
    else:
        y = float("nan")
    result, _ = _annotate(OilCandidateRgb(), rgb, visible,
                         [BoundaryCandidate("a", BoundaryKind.OIL_AIR, y, features={"sequence_eligible": 1.})],
                         glare=glare, x=x)
    assert result[0].features["oil_candidate_rgb_decision"] == "UNAVAILABLE"
    assert not candidate_is_eligible(result[0])


@pytest.mark.parametrize("logits,expected", [([[2, 1]], COMPATIBLE), ([[1, 2]], OPPOSED),
    ([[2, 1], [1, 2]], "UNKNOWN"), ([[1, 1]], "UNKNOWN")])
def test_frozen_variant_agreement(logits, expected):
    assert variant_decision(logits) == expected


def test_compatibility_never_rescues_rejection_or_changes_foam_or_candidates():
    rgb, visible = _inputs()
    model = OilCandidateRgb()
    model._weights["classifier.weight"][:] = 0
    model._weights["classifier.bias"][:] = [1, 0]
    candidates = [
        BoundaryCandidate("ok", BoundaryKind.OIL_AIR, 222., features={"sequence_eligible": 1.}),
        BoundaryCandidate("invalid", BoundaryKind.OIL_AIR, 222., features={"sequence_eligible": 0.}),
        BoundaryCandidate("artifact", BoundaryKind.OIL_AIR, 222., features={"sequence_eligible": 1., "calibrated_artifact_match": .9}),
        BoundaryCandidate("foam", BoundaryKind.FOAM_FRONT, 222., features={"sequence_foam_eligible": 1.}),
    ]
    before = deepcopy([asdict(c) for c in candidates])
    result, _ = _annotate(model, rgb, visible, candidates)
    assert [asdict(c) for c in candidates] == before
    assert result[-1] is candidates[-1]
    assert [candidate_is_eligible(c) for c in result[:-1]] == [True, False, False]
    for a, b in zip(before, map(asdict, result)):
        b["features"] = {k: v for k, v in b["features"].items() if not k.startswith("oil_candidate_rgb_")}
        assert a == b


def test_resource_is_exact_frozen_bytes_and_independent_of_cwd(monkeypatch, tmp_path):
    from pathlib import Path
    frozen_weights = Path(__file__).resolve().parents[2] / "docs/50-diagnostics/s11/2026-10-14-candidate-rgb-trial/final-weights.npz"
    assert hashlib.sha256(frozen_weights.read_bytes()).hexdigest() == rgb_module.WEIGHTS_SHA256
    monkeypatch.chdir(tmp_path)
    assert OilCandidateRgb()._weights["classifier.weight"].shape == (2, 8)


def test_off_never_loads_model_and_on_does_not_hide_corrupt_weights(monkeypatch, tmp_path):
    monkeypatch.setattr(rgb_module, "files", lambda _package: tmp_path)
    OpenCvPhaseDetector()
    with pytest.raises(FileNotFoundError):
        OpenCvPhaseDetector(candidate_rgb=True)
    target = tmp_path / "resources/models/candidate_rgb_weights.npz"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="frozen model"):
        OpenCvPhaseDetector(candidate_rgb=True)


def test_enabled_resolver_does_not_silently_use_unannotated_inputs():
    glass = InspectionRecipe.default_glass(320, 240)
    detection = PhaseDetection(glass.id, 0, 0., FillState.UNKNOWN_REVIEW,
                               candidates=[BoundaryCandidate("raw", BoundaryKind.OIL_AIR, 120.)])
    with pytest.raises(ValueError, match="annotated Oil"):
        OpenCvPhaseDetector(candidate_rgb=True).resolve_sequence([detection], glass)
    with pytest.raises(ValueError, match="separately"):
        OpenCvPhaseDetector(candidate_rgb=True, cost_first_assignment=True)
