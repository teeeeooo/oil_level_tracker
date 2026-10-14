"""Representation boundaries: no threshold, candidate seed or label transfer."""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from tests.diagnostics import s11_raw_front_inventory as inventory


def measure(gray, *, mask=None, glare=None, origin=(0, 0)):
    mask = np.ones(gray.shape, bool) if mask is None else mask
    glare = np.zeros(gray.shape, bool) if glare is None else glare
    return inventory.measure(gray, mask, glare, origin=origin, column=gray.shape[1]//2)


def test_whole_roi_retains_weak_and_strong_plateaus_without_amplitude_rank():
    gray = np.zeros((20, 9), np.uint8)
    gray[5:12] = 1
    gray[12:] = 101
    original = gray.copy()
    result = measure(gray, origin=(100, 200))
    peaks = [p for p in result["signs"]["rising"]["plateaus"] if p[0] == 104]
    assert peaks == [[104, 204, 206, 1], [104, 211, 213, 100]]
    assert result["selected_front"] is None and result["qualified_paths"] == 0
    assert result["signs"]["falling"]["plateaus"] == []
    assert np.array_equal(gray, original)


def test_adjacent_opposite_slopes_keep_separate_graphs_and_entire_ties():
    gray = np.full((15, 9), 100, np.uint8)
    gray[6:8] = 0
    result = measure(gray)
    expected = {"falling": {5, 6}, "rising": {7, 8}}
    for name, ys in expected.items():
        sign = result["signs"][name]
        assert sign["graph"]["vertices"] == 7*2
        paths = sign["fixed_column_fragments"]
        assert set(y for p in paths for x,y in p["source_path_xy"]) == ys
        assert all(p["physical_role"] == "UNREVIEWED" and not p["native_canny_label"] for p in paths)
        assert set(y for p in paths for y in p["fixed_column_rows"]) == ys


def test_unavailable_stencil_is_censored_not_bridged_or_zero_filled():
    gray = np.zeros((13, 9), np.uint8)
    gray[6:] = 100
    mask = np.ones(gray.shape, bool)
    mask[6, 4] = False
    result = measure(gray, mask=mask)
    assert not result["signs"]["rising"]["fixed_column_fragments"]
    assert result["signs"]["rising"]["plateaus"]  # Other visible columns survive.
    assert result["signs"] == measure(gray, glare=~mask)["signs"]


def test_empty_and_crop_censored_inputs_are_not_physical_negatives():
    gray = np.full((8, 9), 20, np.uint8)
    for image, mask in ((gray, np.ones(gray.shape, bool)),
                        (np.arange(72, dtype=np.uint8).reshape(8,9), np.zeros(gray.shape, bool))):
        result = measure(image, mask=mask)
        assert all(s["plateaus"] == [] and s["graph"]["vertices"] == 0 for s in result["signs"].values())
        assert result["qualified_paths"] == 0 and result["selected_front"] is None


def test_origin_translates_every_observed_path_without_changing_population():
    gray = np.zeros((15, 9), np.uint8)
    gray[7:] = 80
    a, b = measure(gray), measure(gray, origin=(715,195))
    for name in a["signs"]:
        aa, bb = a["signs"][name], b["signs"][name]
        assert aa["raster_sha256"] == bb["raster_sha256"]
        assert len(aa["fixed_column_fragments"]) == len(bb["fixed_column_fragments"])
        for x,y in zip(aa["fixed_column_fragments"],bb["fixed_column_fragments"], strict=True):
            assert x["id"] == y["id"]
            assert (np.array(x["source_path_xy"])+[715,195]).tolist() == y["source_path_xy"]


def reply_fixture(tmp_path):
    o2 = inventory.o2
    display = tmp_path / "display.png"
    display.write_bytes(b"synthetic display")
    subject = dict(id="point", source_xy=[12,13], candidate_sha256="candidate")
    review = dict(subject=subject, subject_sha256=o2.fingerprint_json(subject),
        display_sha256=o2.sha256_file(display), prior_practical_acceptance="ACCEPTED_APPROXIMATION")
    o2.write_new(tmp_path/"review.json", review)
    return dict(schema="s11-source-contact-type-reply-v1",
        review=dict(path="review.json", sha256=o2.sha256_file(tmp_path/"review.json")),
        display=dict(path="display.png", sha256=o2.sha256_file(display)),
        subject_id="point", subject_sha256=review["subject_sha256"], response_ko="액체–빈공간",
        contact="LIQUID_EMPTY_SPACE", scope="CONTACT_TYPE_AT_PREVIOUSLY_ACCEPTED_CANDIDATE_ONLY")


def test_candidate_contact_never_increases_native_labels_or_pure_side_truth(tmp_path):
    reply = reply_fixture(tmp_path)
    original = deepcopy(reply)
    result = inventory.bind_contact(tmp_path, reply)
    assert result["contact"] == "LIQUID_EMPTY_SPACE" and result["native_labels_created"] == 0
    assert result["pure_side_labels"] is result["motion_labels"] is result["exact_y_truth"] is None
    assert reply == original


@pytest.mark.parametrize("fault", ["subject", "display", "scope", "extra"])
def test_changed_identity_or_expanded_scope_rejected(tmp_path, fault):
    reply = reply_fixture(tmp_path)
    if fault == "subject": reply["subject_sha256"] = "changed"
    if fault == "display": (tmp_path/"display.png").write_bytes(b"changed")
    if fault == "scope": reply["scope"] = "DISPLAYED_FRAGMENT_ROLE_ONLY"
    if fault == "extra": reply["native_path"] = [[12,13]]
    with pytest.raises(ValueError):
        inventory.bind_contact(tmp_path, reply)


def test_cli_foreign_cwd_refuses_overwrite_before_reading_inputs(tmp_path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    output = tmp_path / "기존 결과.json"
    output.write_bytes(b"preserve")
    result = subprocess.run([sys.executable, "-B", str(Path(inventory.__file__).resolve()),
        "--plan", "missing.json", "--output", str(output)], cwd=tmp_path, env=env,
        stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert result.returncode != 0 and "refuse overwrite" in result.stderr
    assert output.read_bytes() == b"preserve"
