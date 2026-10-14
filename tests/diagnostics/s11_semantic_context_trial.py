"""SCM-1: one offline pretrained semantic observation on existing native ROIs.

No fitting, source-specific prompts, contour generation or production consumer.
Frozen NRO/MRO owners still validate every old role, path and RGB footprint.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import importlib.util
from importlib.metadata import distributions
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_native_role_order_followup as milk

order, old, o2 = milk.order, milk.old, milk.o2
SCHEMA = "s11-semantic-context-trial-v1"
HERE = "docs/50-diagnostics/s11/2026-10-14-semantic-context"
BASE = "docs/50-diagnostics/s11/2026-10-14-native-role-order/manifest.json"
MILK = "docs/50-diagnostics/s11/2026-10-14-native-milk-order/manifest.json"
G0 = "docs/50-diagnostics/s11/2026-10-13-native-role-readiness/readout.json.gz"
MODEL = "sample/output/s11-cr1-workspace/models/clipseg-rd64-refined"
MODEL_SHA = "d00ca85d6b859f9d07b7cfb8ef26fe9771cb275b34c9368f2ecf603139307f55"
PROMPTS = ["foam", "liquid", "glass rim"]
CONFIG = dict(prompts=PROMPTS, size=[352, 352], device="cpu", dtype="float32", threads=2,
              processor="slow/Pillow", attention="eager",
              resize="checkpoint bilinear, native ROI stretched to square",
              upsample="bilinear logits, align_corners=False, then sigmoid",
              foreground="pixelwise max(foam, liquid)",
              score="mean lower patches minus mean upper patches", training_updates=0)
LIMITS = dict(seconds=900, peak_rss_bytes=2_500_000_000, scratch_bytes=32_000_000,
              retained_bytes=6_000_000, aggregate_workspace_bytes=3_000_000_000)


def packages():
    return dict(sorted((d.metadata["Name"].lower().replace("_", "-"), d.version)
                       for d in distributions()))


def crop_roi(rgb, geometry, image_origin):
    """Source-coordinate geometry is not a capture-local crop or a new ROI."""
    h, w = geometry["shape"]
    x, y = [a-b for a, b in zip(geometry["origin"], image_origin)]
    o2.require(geometry["scale_xy"] == [1, 1] and h > 0 and w > 0 and
               x >= 0 and y >= 0 and y+h <= rgb.shape[0] and x+w <= rgb.shape[1],
               "native ROI outside pinned capture")
    return np.ascontiguousarray(rgb[y:y+h, x:x+w])


def inputs(root):
    base = o2.read_json(root / BASE); follow = o2.read_json(root / MILK)
    order.load_inputs(root, base); milk.load_inputs(root, follow)
    g0 = json.loads(gzip.decompress((root / G0).read_bytes()))
    packet, = o2.read_json(old.verified(root, follow["packet"]))["native_review_packets"]
    units = copy.deepcopy(base["units"] + follow["units"])
    frames = {}; rois = {}
    for u in units:
        if u["partition"] == "followup":
            geometry, rgb_pin, image_origin = packet["geometry"], follow["rgb"], [0, 0]
        else:
            candidates = [c for c in g0["contexts"] if c["source_recording"] == u["source_recording"]
                          and c["frame"] == u["frame"] and c["geometry"]["origin"] == u["origin"]]
            o2.require(len(candidates) == 1, "ambiguous source/frame/geometry")
            geometry, rgb_pin, image_origin = candidates[0]["geometry"], u["rgb"], u["image_origin"]
        key = u["source_recording"]["sha256"] + ":" + str(u["frame"])
        if key not in frames:
            with Image.open(old.verified(root, rgb_pin)) as image:
                rgb = np.array(image.convert("RGB"))
            roi = crop_roi(rgb, geometry, image_origin)
            frames[key] = dict(source_recording=u["source_recording"], frame=u["frame"],
                               rgb=rgb_pin, image_origin=image_origin, geometry=geometry,
                               roi_sha256=old.array_hash(roi),
                               model_scale_xy=[352/roi.shape[1], 352/roi.shape[0]], units=[])
            rois[key] = roi
        o2.require(frames[key]["geometry"] == geometry and frames[key]["rgb"] == rgb_pin,
                   "same source/frame has inconsistent input")
        frames[key]["units"].append(u["id"])
        u["frame_key"] = key; u["roi_centers"] = {}
        for side, descriptor in u["sides"].items():
            centers = [[x+image_origin[0]-geometry["origin"][0],
                        y+image_origin[1]-geometry["origin"][1]] for x, y in descriptor["centers_image_xy"]]
            o2.require(old.array_hash(old.patches(rois[key], centers)) == descriptor["uint8_sha256"],
                       "ROI crop changed native RGB footprint")
            u["roi_centers"][side] = centers
    o2.unique(units, "id", "semantic unit")
    pairs = {**base["pairs"]["train"], **base["pairs"]["transfer"], **follow["pairs"]}
    counts = dict(total=len(units), available=sum(bool(u["roi_centers"]) for u in units),
                  qualified=sum(u["review_role"] is not None for u in units),
                  unknown=sum(u["review_role"] is None for u in units),
                  recordings=len(pairs), frames=len(frames), pairs=sum(map(len, pairs.values())))
    o2.require(counts == dict(total=48, available=39, qualified=15, unknown=33,
                             recordings=4, frames=5, pairs=17), "complete population changed")
    return units, frames, rois, pairs, counts


def prepare(root):
    _, frames, _, pairs, counts = inputs(root)
    setup = o2.read_json(root / HERE / "setup.json")
    o2.require(setup["packages"] == packages() and setup["python"] == platform.python_version(),
               "setup runtime changed")
    for name, wanted in old.PACKAGES.items():
        o2.require(packages()[name] == wanted, "existing core package changed")
    o2.require(packages()["transformers"] == "4.57.6", "wrong pretrained implementation")
    for asset in setup["model_files"]:
        old.verified(root, asset)
    for asset in setup["implementation_files"]:
        old.verified(root, asset)
    o2.require(old.pin(root, root / MODEL / "model.safetensors")["sha256"] == MODEL_SHA,
               "checkpoint changed")
    return dict(schema=SCHEMA, configuration=CONFIG, limits=LIMITS, frames=frames,
                pairs=pairs, counts=counts, python=platform.python_version(), packages=packages(),
                inputs=[old.pin(root, root / p) for p in [BASE, MILK, G0, HERE+"/setup.json"]],
                sources=[old.pin(root, p) for p in [Path(__file__), root / old.GUARD,
                         root / "tests/unit/test_s11_semantic_context_trial.py"]],
                model_files=setup["model_files"], model_directory=MODEL,
                pure_side_material_truth=False, absolute_classification=False, physical_winner=None)


def reduce_support(probabilities, centers):
    """Equal patch weights; the fuzzy foreground union precedes spatial means."""
    a = np.asarray(probabilities)
    o2.require(a.ndim == 3 and a.shape[0] == 3 and np.isfinite(a).all() and
               (a >= 0).all() and (a <= 1).all(), "three finite support planes required")
    h, w = a.shape[1:]
    o2.require(centers and len({tuple(p) for p in centers}) == len(centers) and
               all(type(x) is int and type(y) is int and 3 <= x < w-3 and 3 <= y < h-3
                   for x, y in centers), "incomplete or duplicate support")
    values = np.stack([a[:, y-3:y+4, x-3:x+4] for x, y in centers])
    prompt = values.mean(axis=(2, 3), dtype=np.float64)
    union = np.maximum(values[:, 0], values[:, 1]).mean(axis=(1, 2), dtype=np.float64)
    return dict(prompt_patch_means=prompt.tolist(), foreground_patch_means=union.tolist(),
                prompt_means=prompt.mean(axis=0).tolist(), foreground_mean=float(union.mean()))


def sparse_reference(logits, shape, centers):
    """Independent float64 half-pixel interpolation at every sampled native pixel."""
    raw = np.asarray(logits, dtype=np.float64)
    h, w = shape; ih, iw = raw.shape[1:]
    rows = []
    for x, y in centers:
        xx = np.clip((np.arange(x-3, x+4)+0.5)*iw/w-0.5, 0, iw-1)
        yy = np.clip((np.arange(y-3, y+4)+0.5)*ih/h-0.5, 0, ih-1)
        x0, y0 = xx.astype(int), yy.astype(int)
        x1, y1 = np.minimum(x0+1, iw-1), np.minimum(y0+1, ih-1)
        wx, wy = xx-x0, yy-y0
        top = raw[:, y0[:, None], x0]*(1-wx)+raw[:, y0[:, None], x1]*wx
        bot = raw[:, y1[:, None], x0]*(1-wx)+raw[:, y1[:, None], x1]*wx
        value = top*(1-wy[:, None])+bot*wy[:, None]
        rows.append(1/(1+np.exp(-value)))
    values = np.stack(rows)
    prompt = values.mean(axis=(2, 3))
    foreground = np.maximum(values[:, 0], values[:, 1]).mean(axis=(1, 2))
    return dict(prompt_patch_means=prompt.tolist(), foreground_patch_means=foreground.tolist(),
                foreground_mean=float(foreground.mean()))


def parameters_sha(model):
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        value = tensor.detach().cpu().contiguous().numpy()
        digest.update(name.encode()); digest.update(str(value.shape).encode())
        digest.update(str(value.dtype).encode()); digest.update(memoryview(value).cast("B"))
    return digest.hexdigest()


def run(root, manifest_path, output):
    o2.require(not output.exists(), "refuse overwrite")
    m = o2.read_json(manifest_path)
    o2.require(m == prepare(root), "frozen source/input/runtime protocol changed")
    o2.require(not subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip(),
               "clean frozen head required")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    units, frames, rois, pairs, counts = inputs(root)
    spec = importlib.util.spec_from_file_location("semantic_guard", root / old.GUARD)
    guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
    o2.require(root == guard.ROOT and output.resolve().is_relative_to(guard.WORKSPACE / "runs"),
               "isolated workspace output required")
    before = guard.allocated(guard.WORKSPACE)
    # Conservatively include both complete S11 evidence trees, not only this probe.
    external = sum(guard.allocated(root / p) for p in ["docs/50-diagnostics/s11", "docs/60-evidence/s11"])
    o2.require(before + external + LIMITS["scratch_bytes"] < LIMITS["aggregate_workspace_bytes"], "workspace budget")
    denied = guard.sandbox(); started = time.monotonic()
    import torch
    from transformers import CLIPSegForImageSegmentation, CLIPSegProcessor
    torch.set_num_threads(2); torch.set_num_interop_threads(2); torch.use_deterministic_algorithms(True)
    model, loading = CLIPSegForImageSegmentation.from_pretrained(
        root / MODEL, local_files_only=True, use_safetensors=True, trust_remote_code=False,
        torch_dtype=torch.float32, attn_implementation="eager", output_loading_info=True)
    o2.require(not loading["missing_keys"] and not loading["mismatched_keys"] and not loading["error_msgs"] and
               all(k.endswith("position_ids") for k in loading["unexpected_keys"]), "incomplete checkpoint")
    processor = CLIPSegProcessor.from_pretrained(root / MODEL, local_files_only=True,
                                                trust_remote_code=False, use_fast=False)
    model.requires_grad_(False); model.eval(); weight_hash = parameters_sha(model)
    load_seconds = time.monotonic()-started
    rows = {}; scores = {}; independent_scores = {}; frame_results = []; max_error = 0.0

    def budget():
        o2.require(time.monotonic()-started < LIMITS["seconds"] and
                   guard.rss() < LIMITS["peak_rss_bytes"], "runtime budget")

    for key, frame in frames.items():
        budget(); roi = rois[key]; image = Image.fromarray(roi); frame_started = time.monotonic()
        tensors = processor(text=PROMPTS, images=[image]*len(PROMPTS), padding=True, return_tensors="pt")
        o2.require(list(tensors["pixel_values"].shape) == [3, 3, 352, 352], "processor geometry changed")
        with torch.inference_mode():
            logits = model(**tensors).logits
            o2.require(list(logits.shape) == [3, 352, 352] and torch.isfinite(logits).all().item(),
                       "invalid semantic output")
            prob = torch.nn.functional.interpolate(logits[:, None], size=roi.shape[:2],
                     mode="bilinear", align_corners=False)[:, 0].sigmoid().numpy()
        raw = logits.numpy(); native_seconds = time.monotonic()-frame_started
        frame_results.append(dict(frame_key=key, seconds=native_seconds,
                                  pixel_values_sha256=old.array_hash(tensors["pixel_values"].numpy()),
                                  input_ids=tensors["input_ids"].tolist(), logits_sha256=old.array_hash(raw)))
        for u in [u for u in units if u["frame_key"] == key]:
            sides = {}; reference = {}
            for side, centers in u["roi_centers"].items():
                sides[side] = reduce_support(prob, centers)
                reference[side] = sparse_reference(raw, roi.shape[:2], centers)
                for field in ("prompt_patch_means", "foreground_patch_means"):
                    error = float(np.max(np.abs(np.array(sides[side][field])-np.array(reference[side][field]))))
                    max_error = max(max_error, error)
                    o2.require(error < 1e-5, "independent interpolation/reduction mismatch")
            score = sides["lower"]["foreground_mean"]-sides["upper"]["foreground_mean"] if sides else None
            if score is not None:
                scores[u["id"]] = score
                independent_scores[u["id"]] = reference["lower"]["foreground_mean"]-reference["upper"]["foreground_mean"]
            rows[u["id"]] = dict(id=u["id"], frame_key=key, role=u["review_role"],
                availability=u["availability"], sides=sides, order_score=score, absolute_decision=None,
                physical_evaluation="UNREVIEWED" if u["review_role"] is None else "PAIR_ORDER_ONLY")
        del tensors, logits, raw, prob, image
        budget()
    comparison = order.compare(scores, pairs); independent = order.compare(independent_scores, pairs)
    decisions_equal = [r["status"] for r in comparison["rows"]] == [r["status"] for r in independent["rows"]]
    o2.require(parameters_sha(model) == weight_hash, "pretrained parameters changed")
    for asset in m["model_files"]: old.verified(root, asset)
    after = guard.allocated(guard.WORKSPACE)
    o2.require(after + external + LIMITS["scratch_bytes"] < LIMITS["aggregate_workspace_bytes"], "final workspace budget")
    budget()
    result = dict(schema=SCHEMA, head=head, manifest=old.pin(root, manifest_path),
        status=("NUMERICAL_ORDER_UNRESOLVED" if not decisions_equal else
                "LIMITED_EXPOSED_ORDER_ONLY" if comparison["ordered"] == 17 else "CLOSED_WITHOUT_PROMOTION"),
        counts=counts, rows=[rows[u["id"]] for u in units], comparison=comparison,
        verification=dict(max_patch_mean_error=max_error, pair_decisions_equal=decisions_equal,
                          independent_comparison=independent, state_sha256=weight_hash, parameters_unchanged=True),
        frame_results=frame_results, loading=loading, training_updates=0, source_forward_batches=len(frames),
        physical_winner=None, absolute_classification=False, production_changed=False,
        resources=dict(elapsed_seconds=time.monotonic()-started, load_seconds=load_seconds,
                       peak_rss_bytes=guard.rss(), allocated_before=before, allocated_after=after), runtime_guard=denied)
    result["resources"]["external_evidence_allocated_bytes"] = external
    o2.write_new(output, result)
    o2.require(output.stat().st_size < LIMITS["retained_bytes"], "retained budget")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run"])
    parser.add_argument("--manifest", type=Path, default=ROOT / HERE / "manifest.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "prepare":
        o2.write_new(args.output, prepare(ROOT))
    else:
        result = run(ROOT, args.manifest.resolve(), args.output.resolve())
        print(json.dumps({k: result[k] for k in ["status", "counts", "resources"]}))


if __name__ == "__main__":
    main()
