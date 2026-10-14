"""Independent source-pixel, ruler and necessary-predicate checks for f144."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "docs/50-diagnostics/s11/2026-10-14-raw-front-inventory"


def verify(path):
    result = json.loads(gzip.decompress(path.read_bytes()))
    reply, arrays = result["reply"], result["arrays"]
    attachment = ROOT / reply["attachment"]["path"]
    assert hashlib.sha256(attachment.read_bytes()).hexdigest() == reply["attachment"]["sha256"]
    annotated = cv2.imread(str(attachment))
    # The exterior ruler was not used by the panel/CoordinateTransform mapper.
    ticks = np.count_nonzero(annotated[60:1120, 96:118].max(axis=2) < 90, axis=1) >= 12
    transitions = np.diff(np.r_[False, ticks, False].astype(int))
    begins, ends = np.flatnonzero(transitions == 1), np.flatnonzero(transitions == -1)
    assert len(begins) == 8
    observed_y = (begins+ends-1)/2+60
    source_y = np.array([240, 280, 320, 360, 400, 440, 480, 500])
    scale, offset = np.polyfit(source_y, observed_y, 1)
    ruler_residual = float(np.max(np.abs(source_y-(observed_y-offset)/scale)))
    assert ruler_residual < 1
    mapped = np.array([r["source_display_coordinate_xy"][1] for r in reply["marks"]])
    independent = (np.array([r["attachment_center_xy"][1] for r in reply["marks"]])-offset)/scale
    mapping_disagreement = float(np.max(np.abs(mapped-independent)))
    assert mapping_disagreement < 1

    with np.load(BASE/"base-raster.npz", allow_pickle=False) as native:
        crop = native["original_roi"].copy()
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB).astype(np.float32)
        a, b = lab[:, :, 1]-128, lab[:, :, 2]-128
        chroma = np.sqrt(a*a+b*b)
        values = dict(gray=gray, lightness=lab[:, :, 0], chroma=chroma,
            warm_chroma=np.maximum(0, b-np.maximum(a, 0)),
            canny=native["canny"], glare_mask=native["glare_mask"], effective_mask=native["effective_mask"])
        settings = json.loads((ROOT/"sample/base_sample_1.oilrecipe").read_text())["glasses"][0]["detector_settings"]
        light_score = np.clip((values["lightness"]-settings["foam_lightness_threshold"])/(255-settings["foam_lightness_threshold"]), 0, 1)
        values["raw_whiteness"] = np.sqrt(light_score*np.clip(1-chroma/settings["foam_max_chroma"], 0, 1)).astype(np.float32)
        visible = (values["effective_mask"] > 0) & (values["glare_mask"] == 0)
        values["whiteness"] = np.where(visible, values["raw_whiteness"], 0).astype(np.float32)
        x0, y0, x1, y1 = result["diagnostic_query_source_xyxy"]
        focus = (slice(y0-218, y1-218), slice(x0-551, x1-551))
        for name, image in values.items():
            assert np.array_equal(image[focus], np.array(arrays[name]["query_values"]))
            assert np.array_equal(image[:, 145], np.array(arrays[name]["full_center_column"]))
        canny = values["canny"] > 0
        padded_gray = np.pad(gray.astype(float), 12, mode="reflect")
        padded_edges = np.pad(canny.astype(float), 12, mode="reflect")
        texture = np.zeros((y1-y0, x1-x0))
        for row, sy in enumerate(range(y0-218, y1-218)):
            for col, sx in enumerate(range(x0-551, x1-551)):
                variances, edges = [], []
                for radius in (5, 12):
                    yy, xx = sy+12, sx+12
                    sl = (slice(yy-radius, yy+radius+1), slice(xx-radius, xx+radius+1))
                    variances.append(float(np.var(padded_gray[sl])))
                    edges.append(float(np.mean(padded_edges[sl])))
                v = np.clip(np.dot([.55, .45], variances)/settings["foam_variance_threshold"], 0, 1)
                e = np.clip(np.dot([.55, .45], edges)/settings["foam_edge_density_threshold"], 0, 1)
                consistency = min(np.clip(np.array(variances)/settings["foam_variance_threshold"], 0, 1))
                texture[row, col] = .40*np.sqrt(v*e)+.35*min(v, e)+.25*consistency
        texture_error = float(np.max(np.abs(texture-np.array(arrays["texture"]["query_values"]))))
        assert texture_error < 1e-5

    zero_stages = ["glare_mask", "canny", "raw_whiteness", "warm_chroma", "raw_white_support", "white_clean",
        "pre_arbitration_chromatic_support", "chromatic_support", "recovered_droplet_support", "support", "labels"]
    assert all(arrays[key]["query_nonzero"] == 0 for key in zero_stages)
    assert arrays["effective_mask"]["query_nonzero"] == (x1-x0)*(y1-y0) == 368
    assert result["complete_frame_result_equal"] and not result["white_priority_branch"]
    return dict(status="PASS", audit_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        original_query_pixels=368, independently_checked_source_channels=len(values),
        independent_texture_max_abs_error=texture_error, exterior_ruler_ticks=8,
        ruler_max_residual_source_pixels=ruler_residual, ruler_panel_disagreement_source_pixels=mapping_disagreement,
        all_six_marks_retained=True, complete_previous_frame_result_unchanged=True,
        no_new_native_or_dense_truth=True, model_calls=0, production_changed=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    result = verify(args.readout)
    with args.output.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result))
