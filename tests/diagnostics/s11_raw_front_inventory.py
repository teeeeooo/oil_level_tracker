"""Audit raw signed-gradient geometry without inventing native role labels.

Reuse the existing exact plateau and lossless graph owners. Unlike the former
Foam-component windows, this inventory covers the entire saved ROI, separately
for each gradient sign. No reference point, amplitude gate or winner enters it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

import cv2
import numpy as np

from oil_tracker.adapters.vision import oil_interface_witness as witness
from tests.diagnostics import s11_contour_contact_probe as contours
from tests.diagnostics import s11_foam_front_alternatives as fronts
from tests.diagnostics import s11_native_role_preflight as g0
from tests.diagnostics import s11_native_surface_trial as arrays

o2 = g0.o2
SCHEMA = "s11-raw-front-inventory-v1"


def measure(gray, effective, glare, *, origin, column):
    """Complete signed plateaus; a fixed-column readout never selects a path."""
    o2.require(isinstance(gray, np.ndarray) and gray.dtype == np.uint8 and
               gray.ndim == 2 and 0 < gray.size <= contours.MAX_PIXELS,
               "bounded raw uint8 gray required")
    for mask in (effective, glare):
        o2.require(isinstance(mask, np.ndarray) and mask.dtype == bool and
                   mask.shape == gray.shape, "same-shape boolean masks required")
    o2.require(len(origin) == 2 and all(type(v) is int for v in origin), "integer origin required")
    height, width = gray.shape
    o2.require(type(column) is int and 0 <= column < width, "fixed local column required")
    visible = effective & ~glare
    channels = witness._extra_channels(gray, visible, effective, np.zeros_like(gray))
    valid = channels["gradient_count"]
    signed = np.zeros(gray.shape, dtype=np.int16)
    signed[1:-1] = gray[2:].astype(np.int16) - gray[:-2].astype(np.int16)
    o2.require(np.array_equal(np.abs(signed[valid]), np.rint(channels["normal"][valid]*510)),
               "raw derivative differs from existing witness")
    ox, oy = origin
    signs = {}
    for name, sign in (("falling", -1), ("rising", 1)):
        values = np.maximum(sign * signed, 0)
        raster = np.zeros(gray.shape, bool)
        plateaus = []
        for x in range(width):
            for peak in fronts._peaks(values[:, x], valid[:, x], 0, height, oy):
                start, stop = peak["source_y_range"]
                raster[start-oy:stop-oy, x] = True
                plateaus.append([x+ox, start, stop, int(values[start-oy, x])])
        # Each sign remains separate; opposite slopes never acquire a graph link.
        graph = contours.measure_edge_fragments(raster, valid, origin=origin)
        selected = []
        for fid, ids in enumerate(graph["fragments"]):
            xy = graph["vertices_xy"][ids]
            if not np.any(xy[:, 0] == column+ox):
                continue
            selected.append(dict(id=f"{name}-{fid}", fragment_id=fid,
                source_path_xy=xy.tolist(), path_sha256=o2.fingerprint_json(xy.tolist()),
                fixed_column_rows=sorted(set(int(y) for x, y in xy if x == column+ox)),
                kind=graph["fragment_kinds"][fid],
                junction_incident=bool(np.any(graph["degree"][ids] > 2)),
                crop_adjacent=bool(graph["crop_adjacent"][ids].any()),
                invalid_stencil_adjacent=bool(graph["unavailable_adjacent"][ids].any()),
                physical_role="UNREVIEWED", native_canny_label=False))
        signs[name] = dict(sign=sign, plateaus=plateaus,
            raster_sha256=arrays.array_hash(raster),
            graph=dict(spec_id=contours.FRAGMENT_SPEC["id"], vertices=len(graph["vertices_xy"]),
                links=len(graph["links"]), fragments=len(graph["fragments"]),
                vertices_sha256=arrays.array_hash(graph["vertices_xy"]),
                links_sha256=arrays.array_hash(graph["links"]),
                fragments_sha256=o2.fingerprint_json(graph["fragments"])),
            fixed_column_fragments=selected)
    return dict(schema=SCHEMA, representation="RAW_SIGNED_GRADIENT_PLATEAUS",
        origin=list(origin), shape=list(gray.shape), fixed_source_x=column+ox,
        gray_sha256=arrays.array_hash(gray), visible_sha256=arrays.array_hash(visible),
        valid_stencil_sha256=arrays.array_hash(valid), valid_stencils=int(valid.sum()),
        plateau_columns=["source_x", "source_y_start", "source_y_stop_exclusive", "byte_difference_magnitude"],
        signs=signs, selected_front=None, qualified_paths=0,
        scope="Observed raw photometry, not Canny G0 geometry, material identity or a pixel truth")


def bind_contact(root, reply):
    """A source-point reply cannot enter the frozen native-path qualifier."""
    o2.require(set(reply) == {"schema", "review", "display", "subject_id", "subject_sha256",
               "response_ko", "contact", "scope"} and
               reply["schema"] == "s11-source-contact-type-reply-v1", "unsupported point reply")
    review = o2.read_json(g0.pinned_path(root, reply["review"]))
    g0.pinned_path(root, reply["display"])
    o2.require(reply["display"]["sha256"] == review["display_sha256"], "display changed")
    o2.require(reply["subject_sha256"] == review["subject_sha256"] ==
               o2.fingerprint_json(review["subject"]), "point subject changed")
    o2.require(reply["subject_id"] == review["subject"]["id"] and
               reply["scope"] == "CONTACT_TYPE_AT_PREVIOUSLY_ACCEPTED_CANDIDATE_ONLY" and
               review["prior_practical_acceptance"] == "ACCEPTED_APPROXIMATION",
               "unsupported point scope")
    o2.require(reply["contact"] in ("LIQUID_EMPTY_SPACE", "FOAM_LIQUID", "OTHER", "UNASSESSABLE"),
               "unsupported point contact")
    o2.text(reply["response_ko"], "verbatim point reply")
    return dict(subject_id=reply["subject_id"], subject_sha256=reply["subject_sha256"],
        response_ko=reply["response_ko"], contact=reply["contact"], scope=reply["scope"],
        native_labels_created=0, pure_side_labels=None, motion_labels=None, exact_y_truth=None)


def build(root, plan):
    # Lazy import: this established baseline loader also imports reporting code.
    from tests.diagnostics import s11_overlay_mask_comparison as comparison
    o2.require(plan["schema"] == "s11-raw-front-inventory-plan-v1", "unsupported inventory plan")
    for pin in plan["sources"]:
        g0.pinned_path(root, pin)
    documents = {k: o2.read_json(g0.pinned_path(root, v)) for k, v in plan["inputs"].items()}
    contact = bind_contact(root, documents["reply"])
    prep = documents["preparation_plan"]
    prior = {k: o2.read_json(g0.pinned_path(root, v)) for k, v in prep["inputs"].items()}
    review = documents["review"]
    o2.require(documents["reply"]["review"] == plan["inputs"]["review"], "review binding changed")
    subject = review["subject"]
    o2.require(subject["id"] == prep["subject_id"] == contact["subject_id"], "source point changed")
    for pin in prior["qualification_plan"]["source_pins"]:
        if pin["path"] != prior["comparison_plan"]["preprocessor"]:
            g0.pinned_path(root, pin)
    frame = cv2.imread(str(g0.pinned_path(root, subject["source_image"])))
    recipe = comparison.InspectionRecipe.from_dict(o2.read_json(g0.pinned_path(root,
        prior["qualification_plan"]["inputs"]["recipe"])))
    glass = recipe.glasses[0]
    bundle = comparison.build_mask_bundle(frame, glass)
    pre = comparison.baseline(prior["comparison_plan"]).preprocess(
        bundle.crop, bundle.effective_mask, glass.detector_settings)
    visible = (bundle.effective_mask > 0) & (pre.glare_mask == 0)
    old_frame = prior["qualification"]["frames"][str(subject["frame_index"])]
    o2.require(list(bundle.crop_origin) == old_frame["origin"] and
               arrays.array_hash(bundle.crop[:, :, ::-1]) == old_frame["rgb_sha256"] and
               arrays.array_hash(visible) == old_frame["visible_sha256"] and
               arrays.array_hash(pre.canny) == review["native_input"]["canny_sha256"],
               "original input or baseline changed")
    settings = glass.detector_settings
    before_mask = cv2.Canny(pre.blurred, settings.canny_low, settings.canny_high)
    o2.require(np.array_equal(pre.canny, cv2.bitwise_and(before_mask, bundle.effective_mask)),
               "baseline Canny path changed")
    column = int(subject["source_xy"][0] - bundle.crop_origin[0])
    result = measure(pre.gray, bundle.effective_mask > 0, pre.glare_mask > 0,
                     origin=tuple(bundle.crop_origin), column=column)
    result.update(plan_sha256=o2.fingerprint_json(plan), contact=contact,
        source_image=subject["source_image"], source_recording=review["source_recording"],
        frame_index=subject["frame_index"],
        baseline=dict(canny_low=settings.canny_low, canny_high=settings.canny_high,
            canny_before_effective_mask=int(np.count_nonzero(before_mask)),
            canny_after_effective_mask=int(np.count_nonzero(pre.canny)),
            canny_after_glare=int(np.count_nonzero((pre.canny > 0) & visible)),
            before_mask_sha256=arrays.array_hash(before_mask),
            canny_sha256=arrays.array_hash(pre.canny),
            input_gray_sha256=arrays.array_hash(pre.gray),
            normalized_sha256=arrays.array_hash(pre.normalized),
            blurred_sha256=arrays.array_hash(pre.blurred)),
        candidate_recomputed=False, candidate_y_used_for_geometry=False,
        video_decodes=0, model_calls=0, training_executed=False, production_changed=False)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    start = time.perf_counter()
    result = build(args.root.resolve(), o2.read_json(args.plan))
    o2.require(len(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))+1 < 3_000_000,
               "inventory resource bound exceeded")
    o2.write_new(args.output, result)
    print(json.dumps({"status": "MEASURED_UNQUALIFIED", "seconds": time.perf_counter()-start,
        "peak_rss": g0.peak_rss(), "baseline": result["baseline"],
        "signs": {k: dict(plateaus=len(v["plateaus"]), graph=v["graph"],
                         center_fragments=len(v["fixed_column_fragments"])) for k,v in result["signs"].items()}}))


if __name__ == "__main__":
    main()
