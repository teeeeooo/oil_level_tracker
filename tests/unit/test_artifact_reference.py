from copy import deepcopy
from dataclasses import asdict, replace

import numpy as np
import pytest

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.artifact_calibration import apply_artifact_templates
from oil_tracker.adapters.vision.artifact_proposal import propose_artifact_templates
from oil_tracker.adapters.vision.artifact_reference import capture_reference, decode_reference, reviewed_edge_mask
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.application.preflight import preflight_context_key
from oil_tracker.domain.artifact_reference import ArtifactSupportReference, MAX_REFERENCES_PER_GLASS
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from tests.fixtures.artifact_reference import reference_fixture
from tests.fixtures.synthetic import empty_frame, glass_config, partial_frame, foam_bottom_frame
from tests.unit.test_preflight_context import _context


def test_reference_moves_with_recipe_and_loads_outside_repo(tmp_path, monkeypatch):
    frame, glass, template, _, _ = reference_fixture()
    ref = template.support_reference.with_source_position(1260, 42.0)
    template = replace(template, support_reference=replace(ref, review_rect=(15, 20, 10, 10), review_state="mixed_or_uncertain"))
    glass.geometry.artifact_templates = [template]
    recipe = InspectionRecipe.empty(160, 120)
    recipe.glasses = [glass]
    repository = JsonRecipeRepository()
    source = tmp_path / "저장 프로필.oilrecipe"
    repository.save(source, recipe)
    destination = tmp_path / "옮긴 폴더"
    destination.mkdir()
    moved = destination / source.name
    source.rename(moved)
    monkeypatch.chdir(destination)
    loaded = repository.load(moved)
    assert loaded.to_dict() == recipe.to_dict()
    saved = loaded.glasses[0].geometry.artifact_templates[0].support_reference
    snap, images = decode_reference(saved)
    x, y = snap["crop_origin"]
    w, h = snap["crop_size"]
    assert np.array_equal(images["original_roi"], frame[y:y+h, x:x+w])
    assert snap["frame_index"] == 1260 and snap["time_sec"] == 42
    assert snap["proposal"]["native_path"]["sectors"][0]["path_source_y"] == 65
    frame[:] = 255
    assert not np.array_equal(images["original_roi"], frame[y:y+h, x:x+w])


def test_scope_selects_only_explicit_visible_edges_not_connected_component():
    _, _, template, _, _ = reference_fixture()
    snap, images = decode_reference(template.support_reference)
    ox, oy = snap["crop_origin"]
    rect = (25-ox, 58-oy, 60, 3)
    mask = reviewed_edge_mask(images, rect)
    assert mask.sum() == 70  # 58 horizontal, 2 vertical, 10 disconnected visible pixels.
    assert not mask[50-oy, 70-ox]  # Connected vertical arm is outside this scope.
    assert not mask[58-oy, 45-ox]  # Rectangle interiors are not filled.
    assert np.count_nonzero(images["horizontal_mask"]) > mask.sum()
    with pytest.raises(ValueError, match="outside"):
        reviewed_edge_mask(images, (-1, 0, 4, 4))


@pytest.mark.parametrize("change", ["size", "ellipse", "settings", "glass"])
def test_context_changes_invalidate_without_remapping_reference(change):
    _, glass, template, _, _ = reference_fixture()
    reference = template.support_reference
    assert reference.correspondence_status(glass, 160, 120) == "bound_reference"
    width, height = 160, 120
    if change == "size":
        glass.geometry = glass.geometry.remapped(160, 120, 320, 240)
        width, height = 320, 240
    elif change == "ellipse":
        glass.geometry.ellipse = replace(glass.geometry.ellipse, center_x=81)
    elif change == "settings":
        glass.detector_settings.canny_low += 1
    else:
        glass.id = "different-glass"
    assert reference.correspondence_status(glass, width, height) == "context_mismatch"
    assert reference.snapshot()["frame_size"] == [160, 120]


def test_corrupt_missing_and_oversized_assets_are_not_usable():
    _, glass, template, _, _ = reference_fixture()
    ref = template.support_reference
    corrupt = replace(ref, snapshot_json=ref.snapshot_json + " ")
    assert corrupt.correspondence_status(glass, 160, 120) == "reference_unavailable"
    with pytest.raises(ValueError, match="hash"):
        decode_reference(corrupt)
    missing = ref.snapshot()
    del missing["images"]["canny"]
    with pytest.raises(ValueError, match="missing"):
        decode_reference(ArtifactSupportReference.capture(missing))
    tampered = ref.snapshot()
    tampered["images"]["canny"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="hash"):
        decode_reference(ArtifactSupportReference.capture(tampered))
    oversized = ref.snapshot()
    oversized["crop_size"] = [100000, 100000]
    with pytest.raises(ValueError, match="dimensions"):
        decode_reference(ArtifactSupportReference.capture(oversized))
    with pytest.raises(ValueError, match="size"):
        ArtifactSupportReference.capture({"large": "a" * 1_048_576})
    with pytest.raises(ValueError, match="no reviewed"):
        decode_reference(replace(ref, review_state="reviewed_support"))


def test_proposal_preserves_original_input_index_and_no_fake_source_frame():
    frame, glass, _, candidate, artifacts = reference_fixture()
    class Detector:
        def detect(self, _frame, _glass, _index, _time, *, debug):
            return PhaseDetection(glass.id, 0, 0., FillState.UNKNOWN_REVIEW,
                                  candidates=[replace(candidate, final_score=.1), replace(candidate, final_score=.2), candidate]), artifacts
    proposals = propose_artifact_templates(frame, glass, detector=Detector())
    assert proposals[0].support_reference.snapshot()["proposal"]["candidate_input_index"] == 2
    assert proposals[0].support_reference.snapshot()["frame_index"] is None
    assert proposals[0].support_reference.snapshot()["time_sec"] is None
    del artifacts.images["canny"]
    assert propose_artifact_templates(frame, glass, detector=Detector())[0].support_reference is None


def test_reference_has_no_matching_or_preflight_authority():
    _, glass, template, candidate, _ = reference_fixture()
    candidates = [replace(candidate, y=float(y), selected=True,
                          features={**candidate.features, "artifact_center_y_norm": y / 120}) for y in range(10, 100)]
    glass.geometry.artifact_templates = [template]
    with_reference = apply_artifact_templates(candidates, glass)
    assert 0 < with_reference[1] < len(candidates)
    glass.geometry.artifact_templates = [replace(template, support_reference=None)]
    assert apply_artifact_templates(candidates, glass) == with_reference
    recipe, session = _context()
    recipe.glasses[0].geometry.artifact_templates = [replace(template, support_reference=None)]
    before = preflight_context_key(recipe, session)
    recipe.glasses[0].geometry.artifact_templates = [template]
    assert preflight_context_key(recipe, session) == before


def test_full_frame_detections_equal_with_and_without_reference():
    _, _, template, _, _ = reference_fixture()
    glass = glass_config()
    glass.geometry.artifact_templates = [replace(template, support_reference=None)]
    other = deepcopy(glass)
    other.geometry.artifact_templates = [template]
    left, right = OpenCvPhaseDetector(), OpenCvPhaseDetector()
    for index, frame in enumerate((empty_frame(), partial_frame(), foam_bottom_frame())):
        expected, _ = left.detect(frame, glass, index, float(index), debug=True)
        actual, _ = right.detect(frame, other, index, float(index), debug=True)
        assert asdict(actual) == asdict(expected)


def test_legacy_geometry_stays_legacy_and_reference_count_is_bounded():
    _, glass, template, _, _ = reference_fixture()
    glass.geometry.artifact_templates = [replace(template, support_reference=None)]
    recipe = InspectionRecipe.empty(160, 120)
    recipe.glasses = [glass]
    payload = recipe.to_dict()
    assert "support_reference" not in payload["glasses"][0]["geometry"]["artifact_templates"][0]
    assert InspectionRecipe.from_dict(payload).glasses[0].geometry.artifact_templates[0].support_reference is None
    glass.geometry.artifact_templates = [replace(template, id=str(i)) for i in range(MAX_REFERENCES_PER_GLASS + 1)]
    with pytest.raises(ValueError, match="Too many"):
        InspectionRecipe.from_dict(recipe.to_dict())


def test_changed_template_geometry_cannot_reuse_reference_attribution():
    _, glass, template, _, _ = reference_fixture()
    reference = template.support_reference
    assert reference.correspondence_status(glass, 160, 120, template) == "bound_reference"
    assert reference.correspondence_status(glass, 160, 120, replace(template, center_y=.7)) == "context_mismatch"


def test_capture_clips_large_support_without_resizing_or_inventing_native_path():
    from types import SimpleNamespace
    from oil_tracker.adapters.vision.artifact_reference import MAX_CROP_WIDTH, MAX_CROP_HEIGHT
    from oil_tracker.domain.geometry import EllipseGeometry
    frame, glass, template, candidate, _ = reference_fixture()
    frame = np.full((900, 1600, 3), 123, np.uint8)
    glass.geometry.ellipse = EllipseGeometry(800, 450, 750, 400)
    mask = np.full((800, 1500), 255, np.uint8)
    artifacts = SimpleNamespace(images={"original_roi": frame[50:850, 50:1550], "effective_mask": mask,
        "glare_mask": mask * 0, "canny": mask, "horizontal_mask": mask}, state={})
    template = replace(template, width=1., height=1., support_reference=None)
    reference = capture_reference(frame, glass, template, artifacts, candidate=candidate, candidate_index=0)
    snapshot, images = decode_reference(reference)
    assert snapshot["crop_size"][0] == MAX_CROP_WIDTH
    assert snapshot["crop_size"][1] == MAX_CROP_HEIGHT
    assert snapshot["context_clipped"] is True
    assert snapshot["proposal"]["native_path"] is None
    assert (images["original_roi"] == 123).all()
