"""Bind a regional user mark, then observe existing Foam stages without mutation.

CoordinateTransform owns display/source scaling. The saved water audit owns the
return-event observer; the existing exact-frame probe owns actual detector entry.
This adapter only connects the new attachment and fixed diagnostic queries.
"""
import argparse
import ast
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

import cv2
import numpy as np
from oil_tracker.domain.geometry import CoordinateTransform
from tests.diagnostics import s11_interface_shadow_evaluation as o2


def verified(pin):
    path = (ROOT / pin["path"]).resolve()
    o2.require(path.is_relative_to(ROOT) and o2.sha256_file(path) == pin["sha256"], "input pin changed")
    return path


def read(pin):
    path = verified(pin)
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def bind(plan):
    inputs = plan["inputs"]
    review = read(inputs["review"])
    attached = cv2.imread(str(verified(inputs["attachment"])))
    display = cv2.imread(str(verified(review["display"])))
    x0, y0, x1, y1 = plan["annotation_panel_xyxy"]
    ox, oy, width, height = review["source_roi_xywh"]
    transform = CoordinateTransform(width, height, x1-x0, y1-y0)
    o2.require(max(transform.offset) < 1, "panel aspect ratio changed")
    panel = attached[y0:y1, x0:x1]
    blue, green, red = cv2.split(panel)
    markup = ((red > 160) & (green < 100) & (blue < 100) &
              (red.astype(int) - np.maximum(green, blue) > 90)).astype(np.uint8)
    count, _, stats, centroids = cv2.connectedComponentsWithStats(markup, connectivity=8)
    o2.require(count-1 == plan["expected_red_marks"], "annotation population changed")
    rx, ry, rw, rh = plan["original_display_panel_xywh"]
    resized = cv2.resize(display[ry:ry+rh, rx:rx+rw], (x1-x0, y1-y0), interpolation=cv2.INTER_LINEAR)
    visible = cv2.dilate(markup, np.ones((9, 9), np.uint8)) == 0
    error = np.abs(panel.astype(float)-resized.astype(float))[visible]
    correlation = float(np.corrcoef(panel[visible].ravel(), resized[visible].ravel())[0, 1])
    o2.require(float(error.mean()) < 4 and correlation > .97, "attachment does not match the reviewed ROI")
    marks = []
    for stat, center in zip(stats[1:], centroids[1:]):
        sx, sy = transform.display_to_source(*center)
        marks.append(dict(attachment_center_xy=[float(center[0]+x0), float(center[1]+y0)],
            source_display_coordinate_xy=[sx+ox, sy+oy],
            attachment_bbox_xywh=[int(stat[0]+x0), int(stat[1]+y0), int(stat[2]), int(stat[3])],
            marked_core_pixels=int(stat[4])))
    starts = np.min(stats[1:, :2], axis=0)
    stops = np.max(stats[1:, :2]+stats[1:, 2:4], axis=0)
    ax, ay = transform.display_to_source(*starts)
    bx, by = transform.display_to_source(*stops)
    query = [math.floor(ax+ox)-1, math.floor(ay+oy)-1, math.ceil(bx+ox)+1, math.ceil(by+oy)+1]
    o2.require(query[0] <= review["fixed_source_column"] < query[2], "marks miss the reviewed center region")
    return dict(schema="s11-regional-foam-upper-reply-v1", review=inputs["review"],
        attachment=inputs["attachment"], response_ko=plan["response_ko"], source=review["source"],
        frame=review["frame"], time_sec=review["time_sec"], role="REGIONAL_FOAM_UPPER",
        fixed_source_column=review["fixed_source_column"], annotation_panel_xyxy=plan["annotation_panel_xyxy"],
        transform=dict(scale=transform.scale, offset_xy=list(transform.offset), source_origin_xy=[ox, oy]),
        registration_check=dict(mean_absolute_error=float(error.mean()), p99_absolute_error=float(np.percentile(error, 99)),
            correlation=correlation, scope="Resized JPEG correspondence; not byte-identical pixels"),
        marks=marks, diagnostic_query_source_xyxy=query, query_padding_source_pixels=1,
        scope="Marked local upper feature only; query rectangle is not a dense material label or error tolerance",
        dense_labels=False, scalar_qualified=False, native_path_qualified=False,
        pure_side_material_truth=False, adjacent_frame_truth=False, qualified_new_native_paths=0,
        status="REGIONAL_REPLY_BOUND")


def stages(plan, reply):
    # Reuse only the saved function definition, not its old ten-frame loop or output paths.
    from oil_tracker.adapters.vision import foam_front_detector as owner
    from probe_base import probe
    history = read(plan["inputs"]["water_stage_owner"])
    source = history["scripts"]["stages.py"]
    o2.require(hashlib.sha256(source["text"].encode()).hexdigest() == source["sha256"], "saved observer changed")
    observer, = [node for node in ast.walk(ast.parse(source["text"]))
                 if isinstance(node, ast.FunctionDef) and node.name == "observe"]
    names = history["stage_preflight"]["capture_names"] + [
        "crop", "gray", "canny", "glare_mask", "effective_mask", "labels"]
    captured, branch = {}, []
    namespace = dict(owner=owner, captured=captured, branch=branch, captured_names=names)
    exec(compile(ast.Module(body=[observer], type_ignores=[]), "saved_water_stage_observer", "exec"), namespace)
    old_profile = sys.getprofile()
    try:
        sys.setprofile(namespace["observe"])
        current = probe(read(plan["inputs"]["frame_plan"]))
    finally:
        sys.setprofile(old_profile)
    previous = read(plan["inputs"]["frame_readout"])
    current.pop("detect_seconds"); previous.pop("detect_seconds")
    o2.require(current == previous, "observer or input changed the complete real frame result")
    o2.require(len(branch) == 1 and set(captured) == set(names)|{"pre_arbitration_chromatic_support"},
               "incomplete stage capture")
    ox, oy = read(plan["inputs"]["review"])["source_roi_xywh"][:2]
    x0, y0, x1, y1 = reply["diagnostic_query_source_xyxy"]
    focus = (slice(y0-oy, y1-oy), slice(x0-ox, x1-ox))
    column = reply["fixed_source_column"]-ox
    numeric = ["gray", "lightness", "chroma", "warm_chroma", "raw_whiteness", "whiteness", "texture"]
    masks = ["effective_mask", "glare_mask", "canny", "textured_white_support", "smooth_droplet_support",
             "raw_white_support", "white_clean", "pre_arbitration_chromatic_support", "chromatic_support",
             "recovered_droplet_support", "support", "labels"]
    tables = {}
    for key in numeric+masks:
        array = captured[key]
        selected = array[focus]
        tables[key] = dict(full_array_sha256=hashlib.sha256(array.tobytes()).hexdigest(),
            full_nonzero=int(np.count_nonzero(array)), query_nonzero=int(np.count_nonzero(selected)),
            query_min=float(selected.min()), query_max=float(selected.max()), query_values=selected.tolist(),
            full_center_column=array[:, column].tolist())
    return dict(schema="s11-regional-foam-stage-audit-v1", status="UNCHANGED_OWNER_CAPTURE_VERIFIED",
        plan_sha256=o2.fingerprint_json(plan), reply=reply, complete_frame_result_equal=True,
        frame_readout=plan["inputs"]["frame_readout"], observer_owner=plan["inputs"]["water_stage_owner"],
        white_priority_branch=branch[0], diagnostic_query_source_xyxy=[x0, y0, x1, y1],
        full_center_column_source_y=[oy, oy+captured["gray"].shape[0]], arrays=tables,
        model_calls=0, training_executed=False, production_changed=False, video_decodes=0,
        limitation="Regional representation audit only; no new exact contour, material mask or sequence truth")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    plan = o2.read_json(args.plan)
    for pin in plan["sources"]:
        verified(pin)
    o2.require(all(not (args.work/name).exists() for name in
                   ("base-foam-upper-reply.json", "base-foam-upper-stages.json.gz")), "refuse overwrite")
    reply = bind(plan)
    result = stages(plan, reply)
    payload = gzip.compress(json.dumps(result, ensure_ascii=False, allow_nan=False,
        separators=(",", ":")).encode(), mtime=0)
    o2.require(len(payload) < 300_000, "stage evidence budget exceeded")
    o2.write_new(args.work/"base-foam-upper-reply.json", reply)
    with (args.work/"base-foam-upper-stages.json.gz").open("xb") as handle:
        handle.write(payload)
    print(json.dumps(dict(status=result["status"], query=reply["diagnostic_query_source_xyxy"],
        stage_counts={key: value["query_nonzero"] for key, value in result["arrays"].items()})))
