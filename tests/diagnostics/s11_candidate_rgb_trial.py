"""Frozen candidate-local RGB feasibility, separate from native-path supervision.

Reuse the native trial's 1,118-parameter model, patch reader and resource guard.
The new owner is necessary for candidate/variant loss and whole-population input,
which the closed five-fragment surface trial cannot express without changing it.
No model input contains a coordinate, family, review, source or reference ID.
"""
from __future__ import annotations

import argparse
import importlib.util
from importlib.metadata import version
import json
import math
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
from tests.diagnostics import s11_native_surface_trial as native

o2 = native.o2
SCHEMA = "s11-candidate-rgb-trial-v1"
CLASSES = ["OIL_CANDIDATE_COMPATIBLE", "OPPOSED_OIL_CANDIDATE"]
CONFIG = native.CONFIG  # same fixed seed/optimizer/capacity, no head search
LIMITS = native.LIMITS


def context(rgb, visible, xy):
    """All complete 7x7 patches in the original ±12, gap-3 side strips."""
    o2.require(rgb.dtype == np.uint8 and rgb.shape == (*visible.shape, 3), "RGB/mask shape mismatch")
    x, y = xy
    o2.require(type(x) is int and type(y) is int, "integer anchor required")
    h, w = visible.shape
    if not (12 <= x < w-12 and 12 <= y < h-12):
        return {"status": "UNAVAILABLE_CROP", "sides": {}}
    sides = {}
    for name, offsets in (("upper", range(-9, -4)), ("lower", range(5, 10))):
        centers = [[x+dx, y+dy] for dy in offsets for dx in range(-9, 10)
                   if visible[y+dy-3:y+dy+4, x+dx-3:x+dx+4].all()]
        sides[name] = {"centers": centers, "patches": len(centers),
                       "uint8_sha256": native.array_hash(native.patches(rgb, centers)) if centers else None}
    return {"status": "AVAILABLE" if all(s["patches"] for s in sides.values()) else "UNAVAILABLE_SIDE",
            "sides": sides}


def load_frame(root, frame):
    path = native.verified(root, frame["rgb"])
    if frame["rgb_format"] == "RGB_PNG":
        with Image.open(path) as image:
            rgb = np.array(image.convert("RGB"))
    else:
        o2.require(frame["rgb_format"] == "BGR_NPZ", "unsupported RGB format")
        with np.load(path, allow_pickle=False) as archive:
            rgb = archive["original_roi"][:, :, ::-1].copy()
    with np.load(native.verified(root, frame["visibility"]), allow_pickle=False) as archive:
        if frame["mask_key"]:
            visible = archive[frame["mask_key"]].astype(bool)
        else:
            visible = (archive["effective_mask"] > 0) & (archive["glare_mask"] == 0)
    o2.require(list(rgb.shape[:2]) == frame["shape"] == list(visible.shape), "frame geometry changed")
    return rgb, visible


def validate_units(units, plan):
    indexed = o2.unique(units, "id", "candidate unit")
    controls = plan["controls"]
    o2.require(set(controls) <= set(indexed), "required candidate missing")
    o2.require(o2.fingerprint_json([{k: u[k] for k in ("id", "query_sha256", "group", "is_oil_candidate")}
                                   for u in units]) == plan["population_sha256"], "complete population changed")
    for unit in units:
        expected = controls.get(unit["id"])
        o2.require(o2.fingerprint_json(unit["query"]) == unit["query_sha256"], "candidate query changed")
        o2.require(unit["target"] == (expected["target"] if expected else None), "candidate target changed")
        o2.require(unit["partition"] == (expected["partition"] if expected else
                   "unreviewed" if unit["is_oil_candidate"] else "excluded_context"), "candidate partition changed")
        source = plan["sources_by_group"][unit["group"]]
        o2.require(unit["source_recording"] == source, "candidate source group changed")
    fit = [u for u in units if u["partition"] == "fit"]
    transfer = [u for u in units if u["partition"] == "transfer"]
    o2.require(fit and transfer and {u["target"] for u in fit} == {0, 1}, "both fit classes required")
    o2.require(not {u["source_recording"]["sha256"] for u in fit}
               & {u["source_recording"]["sha256"] for u in transfer}, "source leakage")


def prepare(root, plan_path):
    from tests.diagnostics import s11_existing_material_reuse as reuse  # no OpenCV in training env
    plan = o2.read_json(plan_path)
    o2.require(plan["schema"] == SCHEMA and plan["configuration"] == CONFIG, "protocol changed")
    docs = {k: reuse.read_pin(root, p) for k, p in plan["inputs"].items()}
    fresh = reuse.audit(root, docs["reuse_manifest"])
    o2.require(fresh == docs["reuse_readout"], "candidate reuse changed")
    public = reuse.public_candidate_audit(root, docs["public_plan"])
    o2.require(public == docs["public_readout"], "public acceptance changed")
    source4 = next(s for s in fresh["sources"] if s["path"] == "sample/sample4.mp4")
    o2.require(plan["sources_by_group"] == {"sample4": {k: source4[k] for k in ("path", "sha256")},
                                           "public": public["source"]}, "source groups differ from bound evidence")
    old = docs["cr1_prepared"]
    mask = root / plan["inputs"]["cr1_prepared"]["path"]
    mask = mask.parent / old["masks_file"]
    o2.require(o2.sha256_file(mask) == old["mask_sha256"], "visibility changed")
    frame_roster, units = {}, []
    for bound in fresh["oil_units"]:
        query = bound["query"]
        is_candidate = "candidate_index" in query
        fid = f"sample4-f{query['frame']}"
        if is_candidate and fid not in frame_roster:
            frame_roster[fid] = {"rgb": native.pin(root, root / old["images"][str(query["frame"]) ]),
                "rgb_format": "RGB_PNG", "visibility": native.pin(root, mask), "mask_key": str(query["frame"]),
                "origin": docs["cr1_preflight"]["geometry"]["origin_xy"],
                "shape": docs["cr1_preflight"]["geometry"]["native_shape"]}
        target = (0 if bound["physical_claim"] == "TARGET_CORRESPONDENCE" or
                  bound["practical_acceptance"] == "ACCEPTED_APPROXIMATION" else
                  1 if bound["physical_claim"] == "OPPOSED_OIL_TARGET" else None)
        units.append({"id": query["id"], "query": query, "query_sha256": bound["query_sha256"],
            "group": "sample4", "source_recording": plan["sources_by_group"]["sample4"],
            "frame_id": fid if is_candidate else None, "is_oil_candidate": is_candidate,
            "partition": "fit" if target is not None else "unreviewed" if is_candidate else "excluded_context",
            "target": target, "label_basis": {"physical": bound["physical_claim"], "practical": bound["practical_acceptance"]}})
    review = docs["public_review_plan"]
    capture = reuse.read_pin(root, review["inputs"]["capture"])
    geometry = next(c for c in capture["cases"] if c["variant"]["id"] == "native")
    frame_roster["public-f1499"] = {"rgb": review["inputs"]["arrays"], "rgb_format": "BGR_NPZ",
        "visibility": review["inputs"]["arrays"], "mask_key": None,
        "origin": geometry["crop_origin"], "shape": geometry["crop_shape"][:2]}
    raw = reuse.read_pin(root, review["inputs"]["raw"])
    join = reuse.read_pin(root, review["inputs"]["join"])
    wrong = [i for i, c in enumerate(raw["candidates"]) if c["kind"] == "oil_air" and c["selected"]]
    o2.require(len(wrong) == 1 and raw["candidates"][wrong[0]]["y"] == join["oil_current"]["raw_y"]
               and join["oil_current"]["distance_to_oil_interval_px"] > 0, "opposition must bind wrong current published location")
    for row in public["candidate_rows"]:
        query = row["query"]
        target = 0 if row["practical_acceptance"] == "ACCEPTED_APPROXIMATION" else 1 if query["candidate_index"] in wrong else None
        is_oil = row["series"] == "oil_air"
        units.append({"id": query["id"], "query": query, "query_sha256": o2.fingerprint_json(query),
            "group": "public", "source_recording": plan["sources_by_group"]["public"],
            "frame_id": "public-f1499" if is_oil else None, "is_oil_candidate": is_oil,
            "partition": "transfer" if target is not None else "unreviewed" if is_oil else "excluded_context",
            "target": target, "label_basis": "PRACTICAL_ACCEPTANCE" if target == 0 else
                "WRONG_CURRENT_PUBLISHED_SCALAR" if target == 1 else "UNASSESSED"})
    validate_units(units, plan)
    frames = {fid: load_frame(root, f) for fid, f in frame_roster.items()}
    for u in units:
        u["variants"] = []
        if not u["is_oil_candidate"]:
            u["availability"] = "EXCLUDED_NON_OIL_CANDIDATE"
            continue
        frame = frame_roster[u["frame_id"]]
        x, y = u["query"]["source_xy"]
        o2.require(float(x).is_integer(), "fixed source X must be integral")
        for sy in sorted({math.floor(y), math.ceil(y)}):
            xy = [int(x)-frame["origin"][0], sy-frame["origin"][1]]
            u["variants"].append({"source_xy": [x, sy], "local_xy": xy,
                                  **context(*frames[u["frame_id"]], xy)})
        u["availability"] = "AVAILABLE" if all(v["status"] == "AVAILABLE" for v in u["variants"]) else "UNAVAILABLE_REQUIRED_VARIANT"
    missing = [u["id"] for u in units if u["target"] is not None and u["availability"] != "AVAILABLE"]
    sources = [Path(__file__), Path(native.__file__), Path(o2.__file__), root/native.GUARD]
    return {"schema": SCHEMA, "plan": native.pin(root, plan_path), "status": "INPUTS_READY" if not missing else "NOT_READY",
            "missing_controls": missing, "units": units, "frames": frame_roster,
            "sources": [native.pin(root, p) for p in sources], "configuration": CONFIG, "resource_limits": LIMITS,
            "packages": native.PACKAGES, "python": "3.14.7", "model_input": "RGB tensors only, /255; no resizing or coordinates",
            "production_changed": False, "native_path_labels": False}


def load_inputs(root, manifest):
    plan = o2.read_json(native.verified(root, manifest["plan"]))
    o2.require(manifest["schema"] == plan["schema"] == SCHEMA and manifest["status"] == "INPUTS_READY"
               and manifest["configuration"] == plan["configuration"] == CONFIG
               and manifest["resource_limits"] == LIMITS, "frozen candidate protocol changed")
    for pin in manifest["sources"] + list(plan["inputs"].values()) + list(plan["sources_by_group"].values()):
        native.verified(root, pin)
    validate_units(manifest["units"], plan)
    frames = {fid: load_frame(root, f) for fid, f in manifest["frames"].items()}
    arrays = {}
    for u in manifest["units"]:
        if not u["is_oil_candidate"]:
            continue
        rgb, visible = frames[u["frame_id"]]
        frame = manifest["frames"][u["frame_id"]]
        x, y = u["query"]["source_xy"]
        o2.require([v["source_xy"] for v in u["variants"]] == [[x, sy] for sy in sorted({math.floor(y), math.ceil(y)})],
                   "required floor/ceil variants changed")
        for v in u["variants"]:
            expected_xy = [int(x)-frame["origin"][0], v["source_xy"][1]-frame["origin"][1]]
            o2.require(v["local_xy"] == expected_xy and context(rgb, visible, expected_xy) ==
                       {k: v[k] for k in ("status", "sides")}, "native context changed")
        available = all(v["status"] == "AVAILABLE" for v in u["variants"])
        o2.require(available == (u["availability"] == "AVAILABLE"), "availability changed")
        if not available:
            o2.require(u["target"] is None, "required control unavailable")
            continue
        arrays[u["id"]] = [tuple(native.patches(rgb, v["sides"][s]["centers"]).astype(np.float32)/255
                                 for s in ("upper", "lower")) for v in u["variants"]]
    return arrays


def decision(logits):
    values = np.asarray(logits)
    o2.require(values.ndim == 2 and values.shape[0] > 0 and values.shape[1] == 2
               and np.isfinite(values).all(), "invalid variant logits")
    choices = [None if v[0] == v[1] else int(np.argmax(v)) for v in values]
    return CLASSES[choices[0]] if choices[0] is not None and all(c == choices[0] for c in choices) else "UNKNOWN"


def summarize(rows, field="decision"):
    fit = [r for r in rows if r["partition"] == "fit"]
    positive = [r for r in rows if r["partition"] == "transfer" and r["target"] == 0]
    opposed = [r for r in rows if r["partition"] == "transfer" and r["target"] == 1]
    o2.require(fit and positive and opposed, "required comparison populations missing")
    summary = {"fit_units": len(fit), "fit_correct": sum(r[field] == CLASSES[r["target"]] for r in fit),
               "transfer_accepted": len(positive), "transfer_accepted_preserved": sum(r[field] == CLASSES[0] for r in positive),
               "transfer_opposed": len(opposed), "transfer_opposed_correct": sum(r[field] == CLASSES[1] for r in opposed),
               "unknown": sum(r[field] in {"UNKNOWN", "UNAVAILABLE"} for r in rows if r["target"] is not None)}
    summary["required_capability"] = (summary["fit_correct"] == len(fit)
        and summary["transfer_accepted_preserved"] > 0 and summary["transfer_opposed_correct"] == len(opposed))
    return summary


def run(root, manifest_path, output):
    o2.require(not output.exists(), "refuse overwrite")
    started = time.monotonic()
    manifest = o2.read_json(manifest_path)
    arrays = load_inputs(root, manifest)
    o2.require(platform.python_version() == manifest["python"] and
               {p: version(p) for p in native.PACKAGES} == manifest["packages"] == native.PACKAGES, "runtime mismatch")
    spec = importlib.util.spec_from_file_location("candidate_rgb_guard", root/native.GUARD)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    o2.require(root == base.ROOT and output.resolve().is_relative_to(base.WORKSPACE/"runs"), "isolated output required")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    o2.require(not subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip(), "clean frozen head required")
    allocated = base.allocated(base.WORKSPACE)
    o2.require(allocated + LIMITS["scratch_bytes"] < LIMITS["aggregate_workspace_bytes"], "workspace budget")
    denied = base.sandbox()
    output.mkdir()
    result = {"schema": SCHEMA, "head": head, "manifest": native.pin(root, manifest_path),
              "status": "STOPPED_WITHOUT_RESULT", "training_steps": 0, "production_changed": False}
    try:
        import torch
        torch.set_num_threads(CONFIG["threads"])
        torch.set_num_interop_threads(CONFIG["threads"])
        torch.use_deterministic_algorithms(True)
        torch.manual_seed(CONFIG["seed"])
        model = native.make_model(torch)
        o2.require(sum(p.numel() for p in model.parameters()) == CONFIG["parameters"], "model size changed")
        tensors = {sid: [tuple(torch.from_numpy(a) for a in pair) for pair in variants] for sid, variants in arrays.items()}
        fit = [u for u in manifest["units"] if u["partition"] == "fit"]
        optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG["lr"], betas=tuple(CONFIG["betas"]), eps=CONFIG["eps"], weight_decay=0)

        def check():
            o2.require(time.monotonic()-started < LIMITS["seconds"] and base.rss() < LIMITS["peak_rss_bytes"], "runtime resource budget")

        losses = []
        model.train()
        for step in range(CONFIG["steps"]):
            check()
            optimizer.zero_grad(set_to_none=True)
            per_candidate = [torch.nn.functional.cross_entropy(torch.stack([model(*pair) for pair in tensors[u["id"]]]),
                torch.full((len(tensors[u["id"]]),), u["target"], dtype=torch.long), reduction="mean") for u in fit]
            loss = torch.stack(per_candidate).mean()
            o2.require(bool(torch.isfinite(loss)), "nonfinite loss")
            loss.backward()
            o2.require(all(p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in model.parameters()), "nonfinite gradient")
            optimizer.step()
            result["training_steps"] = step+1
            if step in (0, CONFIG["steps"]-1):
                losses.append({"step_before_update": step+1, "mean_candidate_cross_entropy": float(loss.detach())})
        model.eval()
        rows = []
        with torch.no_grad():
            for u in manifest["units"]:
                check()
                row = {k: u[k] for k in ("id", "partition", "target", "availability", "label_basis")}
                if u["id"] not in tensors:
                    row.update(decision="UNAVAILABLE" if u["is_oil_candidate"] else "NOT_EVALUATED",
                               mean_color_decision="UNAVAILABLE" if u["is_oil_candidate"] else "NOT_EVALUATED")
                else:
                    full = [model(*p).numpy().astype(float).tolist() for p in tensors[u["id"]]]
                    ablated = [model(*(a.mean(dim=(0, 2, 3), keepdim=True).expand_as(a) for a in p)).numpy().astype(float).tolist()
                               for p in tensors[u["id"]]]
                    row.update(logits=full, decision=decision(full), mean_color_logits=ablated, mean_color_decision=decision(ablated))
                rows.append(row)
        accounting = summarize(rows)
        weights = {k: v.detach().numpy() for k, v in model.state_dict().items()}
        o2.require(all(np.isfinite(v).all() for v in weights.values()), "nonfinite weights")
        np.savez(output/"final-weights.npz", **weights)
        result.update(status="LIMITED_EXPOSED_CANDIDATE_TRANSFER" if accounting["required_capability"] else "CLOSED_WITHOUT_PROMOTION",
            rows=rows, accounting=accounting, mean_color_ablation=summarize(rows, "mean_color_decision"), losses=losses,
            weights_sha256=o2.sha256_file(output/"final-weights.npz"), configuration=CONFIG,
            model_calls={"training": CONFIG["steps"]*sum(len(tensors[u["id"]]) for u in fit),
                         "final_per_view": sum(len(v) for v in tensors.values()), "final_views": 2},
            runtime={"python": platform.python_version(), "packages": native.PACKAGES},
            untouched_holdout_recordings=0, physical_accuracy="NOT_EVALUATED", native_path_labels=False)
        check()
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        result.update(resources={"elapsed_seconds": time.monotonic()-started, "peak_rss_bytes": base.rss(),
            "workspace_allocated_before": allocated, "workspace_allocated_after": base.allocated(base.WORKSPACE)},
            runtime_guard={"denied_events": denied, "scope": "Python audit hook, not OS confinement"})
        o2.write_new(output/"readout.json", result)
        o2.require(sum(p.stat().st_size for p in output.iterdir()) < LIMITS["retained_bytes"], "output budget")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    if args.mode == "prepare":
        result = prepare(args.root.resolve(), args.manifest.resolve())
        o2.write_new(args.output, result)
        print(json.dumps({"status": result["status"], "units": len(result["units"]), "missing_controls": result["missing_controls"]}))
    else:
        result = run(args.root.resolve(), args.manifest.resolve(), args.output.resolve())
        print(json.dumps({k: result[k] for k in ("status", "accounting", "resources")}))


if __name__ == "__main__":
    main()
