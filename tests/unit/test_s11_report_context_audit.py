from copy import deepcopy
import json

from PIL import Image
import pytest

from tests.diagnostics.s11_report_context_audit import (
    authority_collisions, confidence_obstruction, inspect_sequences, local_asset,
)


def unit(identity, role, *, ready=True, gates=None):
    return {"query": {"id": identity}, "physical_claim": role,
            "candidate_role_comparison_ready": ready,
            "authority": {"authority": "CONTINUATION_ELIGIBLE", "reason": "continuation",
                          "failed_gates": gates or []}}


@pytest.mark.parametrize("wrong", [0.8, 0.9])
def test_confidence_equal_or_higher_is_obstruction(wrong):
    positive, opposition = [{"id": "p", "confidence": 0.8}], [{"id": "n", "confidence": wrong}]
    assert confidence_obstruction(positive, opposition) == [{"positive": positive[0], "opposition": opposition[0]}]


def test_reverse_confidence_order_is_not_an_obstruction_or_an_acceptance():
    assert confidence_obstruction([{"confidence": 0.8}], [{"confidence": 0.7}]) == []


@pytest.mark.parametrize("bad", [float('nan'), float('inf'), True, None, "0.8"])
def test_invalid_confidence_fails(bad):
    with pytest.raises(ValueError, match="finite numeric"):
        confidence_obstruction([{"confidence": bad}], [{"confidence": 0.7}])


def test_authority_collision_does_not_promote_unknown():
    units = [unit("p", "TARGET_CORRESPONDENCE", gates=["b", "a"]),
             unit("n", "OPPOSED_OIL_TARGET", gates=["a", "b"]),
             unit("u", "UNASSESSED", ready=False)]
    before = deepcopy(units)
    result = authority_collisions(units)
    assert len(result) == 1 and len(result[0]["subjects"]) == 2
    assert units == before


def test_authority_different_tuple_is_not_collision():
    assert not authority_collisions([unit("p", "TARGET_CORRESPONDENCE", gates=["a"]),
                                     unit("n", "OPPOSED_OIL_TARGET", gates=["b"])])


def test_duplicate_unknown_identity_fails():
    with pytest.raises(ValueError, match="duplicate"):
        authority_collisions([unit("u", "UNASSESSED", ready=False)] * 2)


def test_false_qualified_unknown_fails():
    with pytest.raises(ValueError, match="unsupported qualified"):
        authority_collisions([unit("u", "UNASSESSED")])


@pytest.mark.parametrize("reference", ["../outside.png", "https://example.invalid/p.png", "missing.png"])
def test_asset_escape_external_and_missing_fail(tmp_path, reference):
    with pytest.raises(ValueError):
        local_asset(tmp_path, reference)


def report_fixture(tmp_path):
    Image.new("RGB", (4, 4), (1, 2, 3)).save(tmp_path / "page.png")
    seq = {"metadata_path": "seq.json", "numeric_measurement": False, "tile_size": 4,
           "geometry": {"tile_content_xywh": [1, 1, 2, 2], "crop_source_xyxy": [0, 0, 2, 2],
                        "resize_scale": 1, "resize_method": "none"},
           "frame_count": 1, "available_count": 1, "glass_id": "glass", "start_sec": 0, "end_sec": 0,
           "reasons": [], "subsampled": False,
           "frames": [{"status": "AVAILABLE", "frame_index": 0, "actual_time_sec": 0,
                       "page_path": "page.png", "tile_xy": [0, 0]}]}
    def write(sequences):
        for item in sequences:
            (tmp_path / item["metadata_path"]).write_text(json.dumps(item))
        (tmp_path / "report.html").write_text("".join(
            '<script class="sequence-data" type="application/json">'+json.dumps(item)+'</script>' for item in sequences))
        return tmp_path / "report.html"
    return seq, write


def test_original_overlap_checked_without_double_counting(tmp_path):
    seq, write = report_fixture(tmp_path)
    second = {**deepcopy(seq), "metadata_path": "seq2.json"}
    result = inspect_sequences(write([seq, second]))
    assert result["records"] == 2 and result["unique_source_frames"] == 1
    assert result["overlap_pixel_checks"] == 1


def test_same_frame_different_pixels_fail(tmp_path):
    seq, write = report_fixture(tmp_path)
    second = {**deepcopy(seq), "metadata_path": "seq2.json"}
    Image.new("RGB", (4, 4), (4, 5, 6)).save(tmp_path / "changed.png")
    second["frames"][0]["page_path"] = "changed.png"
    with pytest.raises(ValueError, match="different original pixels"):
        inspect_sequences(write([seq, second]))


@pytest.mark.parametrize("fault", ["sidecar", "bounds", "count", "duplicate", "numeric", "resize"])
def test_sequence_contract_failures(tmp_path, fault):
    seq, write = report_fixture(tmp_path)
    if fault == "bounds": seq["frames"][0]["tile_xy"] = [2, 0]
    if fault == "count": seq["available_count"] = 0
    if fault == "duplicate": seq["frames"] *= 2; seq["frame_count"] = 2
    if fault == "numeric": seq["numeric_measurement"] = True
    if fault == "resize": seq["geometry"]["resize_scale"] = 2
    path = write([seq])
    if fault == "sidecar": (tmp_path / "seq.json").write_text('{}')
    with pytest.raises(ValueError): inspect_sequences(path)
