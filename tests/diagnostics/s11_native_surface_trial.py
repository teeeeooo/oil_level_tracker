"""One frozen, offline native surface/non-surface capability trial, never production.

Preparation reuses the G0 qualifier; the training entry reads only pinned JSON/RGB
with NumPy/Pillow so the isolated Torch environment does not need OpenCV. Context
facets remain review metadata. No dense labels, new paths or adaptive retries.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from importlib.metadata import version
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

from tests.diagnostics import s11_interface_shadow_evaluation as o2

SCHEMA = "s11-native-surface-trial-v1"
CLASSES = ["EXTERNAL_SURFACE", "NON_EXTERNAL_SURFACE"]
TARGETS = {"EXTERNAL_SURFACE": 0, "INTERNAL_FOAM_CHANGE": 1, "STRUCTURE_BOUNDARY": 1}
SPLIT = {"train": ["N1", "N2"], "transfer": ["N3", "N4", "N5"]}
CONFIG = dict(seed=20261013, device="cpu", dtype="float32", threads=2, steps=1000,
              optimizer="Adam", lr=0.001, betas=[0.9, 0.999], eps=1e-8, weight_decay=0,
              parameters=1118, augmentation=False, calibration=False, checkpoint="FINAL_ONLY")
LIMITS = dict(seconds=600, peak_rss_bytes=1_000_000_000, scratch_bytes=32_000_000,
              retained_bytes=6_000_000, aggregate_workspace_bytes=3_000_000_000)
PACKAGES = {"torch": "2.14.1", "numpy": "2.5.4", "pillow": "12.3.0"}
GUARD = "docs/50-diagnostics/s11/2026-10-12-cr1-context-comparison/probe.py"
PREDECESSOR = "docs/50-diagnostics/s11/2026-10-13-native-role-qualification/g1-pilot-proposal.json"


def pin(root, path):
    path = Path(path).resolve()
    return {"path": path.relative_to(root).as_posix(), "sha256": o2.sha256_file(path)}


def verified(root, entry):
    relative = Path(entry["path"])
    path = (root / relative).resolve()
    o2.require(not relative.is_absolute() and ".." not in relative.parts and path.is_relative_to(root),
               "input escapes repository")
    o2.require(o2.sha256_file(path) == entry["sha256"], "input hash mismatch: " + entry["path"])
    return path


def array_hash(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def patches(rgb, centers):
    o2.require(centers and len({tuple(p) for p in centers}) == len(centers), "empty or duplicate patches")
    height, width, channels = rgb.shape
    o2.require(channels == 3 and rgb.dtype == np.uint8, "native RGB uint8 required")
    o2.require(all(type(x) is int and type(y) is int and 3 <= x < width-3 and 3 <= y < height-3
                   for x, y in centers), "incomplete native footprint; no padding")
    return np.ascontiguousarray(np.stack([rgb[y-3:y+4, x-3:x+4].transpose(2, 0, 1)
                                         for x, y in centers]))


def validate_split(units, split):
    indexed = o2.unique(units, "id", "trial unit")
    ids = split["train"] + split["transfer"]
    o2.require(len(ids) == len(set(ids)) and set(ids) == set(indexed), "split must account for every unit once")
    sources = [{indexed[s]["source_recording"]["sha256"] for s in split[k]} for k in ("train", "transfer")]
    o2.require(all(sources) and not sources[0] & sources[1], "source leakage across fit/transfer")
    for unit in units:
        o2.require(unit["review_role"] in TARGETS and unit["target"] == TARGETS[unit["review_role"]],
                   "target must preserve reviewed role mapping")
    o2.require({indexed[s]["target"] for s in split["train"]} == {0, 1}, "fit needs both capability targets")


def prepare(root, replies, qualifications):
    from tests.diagnostics import s11_native_role_qualification as q  # preparation environment only
    o2.require(len(replies) == len(qualifications) == 2, "two existing scoped supplements required")
    units, input_pins = [], []
    baseline = None
    for reply_path, qualified_path in zip(replies, qualifications):
        reply, saved = o2.read_json(reply_path), o2.read_json(qualified_path)
        fresh = q.qualify(root, reply)
        o2.require(o2.fingerprint_json(fresh) == o2.fingerprint_json(saved), "qualification no longer reproducible")
        proposal = q.read_pin(root, reply["proposal"])
        if baseline is None:
            baseline = saved["g0_readout"]
        o2.require(saved["g0_readout"] == baseline, "incompatible G0 snapshots")
        g0 = q.read_pin(root, baseline)
        subjects, views = q.by_id(proposal["subjects"], "subject"), q.by_id(proposal["views"], "view")
        input_pins.extend([pin(root, reply_path), pin(root, qualified_path)])
        for result in saved["subjects"]:
            sid = result["id"]
            view = views[subjects[sid]["view_id"]]
            context = g0["contexts"][result["g0_pointer"][1]]
            ox, oy = context["geometry"]["origin"]
            vx, vy = view["image_origin_xy"]
            o2.require(result["proposed_context"]["status"] == "AVAILABLE_PARTIAL_CONTEXT", "required side unavailable")
            with Image.open(q.g0.pinned_path(root, view["source"])) as image:
                rgb = np.array(image.convert("RGB"))
            sides = {}
            for side in ("upper", "lower"):
                centers = [[x+ox-vx, y+oy-vy] for x, y in
                           result["proposed_context"]["sides"][side]["complete_centers_xy"]]
                raw = patches(rgb, centers)
                sides[side] = dict(centers_image_xy=centers, shape=list(raw.shape), uint8_sha256=array_hash(raw))
            units.append(dict(id=sid, qualification=pin(root, qualified_path), subject_sha256=result["subject_sha256"],
                              source_recording=result["source_recording"], frame=result["frame"],
                              review_role=result["capability_target"], target=TARGETS[result["capability_target"]],
                              rgb=view["source"], sides=sides))
    units.sort(key=lambda u: u["id"])
    validate_split(units, SPLIT)
    sources = [Path(__file__), Path(q.__file__), Path(q.g0.__file__), Path(q.g0.cr1.__file__),
               Path(q.g0.contours.__file__), Path(q.g0.material.__file__), Path(q.g0.faces.__file__),
               Path(o2.__file__), root / GUARD,
               root / "src/oil_tracker/application/services/truth_identity.py",
               root / "src/oil_tracker/domain/detector_benchmark.py"]
    return dict(schema=SCHEMA, capability="external surface compatibility on reviewed native paths",
                classes=CLASSES, split=SPLIT, configuration=CONFIG, resource_limits=LIMITS,
                packages=PACKAGES, python="3.14.7", sources=[pin(root, p) for p in sources],
                inputs=input_pins, predecessor=pin(root, root / PREDECESSOR), g0_readout=baseline, units=units,
                architecture="Shared valid Conv3x3 3->8->8->4; ReLU after first two; mean per side; ordered concat; Linear8->2, all biases",
                features="RGB /255 only; no resize, pad, normalization, coordinates, IDs, patch counts, role or facet metadata",
                supervision="Equal weight fragment cross-entropy on N1/N2 only; no side/pixel labels; no structure fit example",
                evaluation="One final-step transfer evaluation on N3/N4/N5; already exposed development, no blind holdout",
                unknown="Exact tied logits UNKNOWN; unavailable support separate; neither counts as success",
                success="All 2 fit and 3 transfer units correct: LIMITED_EXPOSED_TRANSFER_ONLY; never full G1/O2/FIELD",
                failure="Any wrong/unknown required unit closes this fixed trial without promotion; no seed/crop/offset/threshold/head/optimizer retry",
                population="Only five qualified fragments evaluated; other G0 rows remain unreviewed/unavailable, never negative successes; use pinned full roster",
                shared_pixels={"N1_N2": 90, "N3_N4": 98}, untouched_holdout_recordings=0,
                production_changed=False, raw_front_integration=False)


def load_inputs(root, manifest):
    o2.require(manifest["schema"] == SCHEMA and manifest["classes"] == CLASSES and
               manifest["configuration"] == CONFIG and manifest["split"] == SPLIT and
               manifest["resource_limits"] == LIMITS, "frozen trial protocol changed")
    for entry in manifest["sources"] + manifest["inputs"] + [manifest["predecessor"], manifest["g0_readout"]]:
        verified(root, entry)
    validate_split(manifest["units"], manifest["split"])
    arrays = {}
    for unit in manifest["units"]:
        o2.require(set(unit["sides"]) == {"upper", "lower"}, "ordered upper/lower input required")
        saved = o2.read_json(verified(root, unit["qualification"]))
        subject = o2.unique(saved["subjects"], "id", "qualified unit")[unit["id"]]
        o2.require(subject["subject_sha256"] == unit["subject_sha256"] and
                   subject["capability_target"] == unit["review_role"] and
                   subject["source_recording"] == unit["source_recording"] and subject["frame"] == unit["frame"],
                   "trial unit differs from qualified source/role")
        with Image.open(verified(root, unit["rgb"])) as image:
            rgb = np.array(image.convert("RGB"))
        arrays[unit["id"]] = {}
        for side, descriptor in unit["sides"].items():
            value = patches(rgb, descriptor["centers_image_xy"])
            o2.require(list(value.shape) == descriptor["shape"] and array_hash(value) == descriptor["uint8_sha256"],
                       "patch input differs from frozen native context")
            arrays[unit["id"]][side] = value.astype(np.float32) / np.float32(255)
    return arrays


def make_model(torch):
    class NativeSurface(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = torch.nn.Sequential(torch.nn.Conv2d(3, 8, 3), torch.nn.ReLU(),
                                               torch.nn.Conv2d(8, 8, 3), torch.nn.ReLU(),
                                               torch.nn.Conv2d(8, 4, 3))
            self.classifier = torch.nn.Linear(8, 2)

        def forward(self, upper, lower):
            # Only RGB tensors cross this boundary. Mean pooling gives one vote per fragment.
            sides = [self.encoder(x).mean(dim=(0, 2, 3)) for x in (upper, lower)]
            return self.classifier(torch.cat(sides))
    return NativeSurface().to(device="cpu", dtype=torch.float32)


def fit(torch, model, train, targets, check):
    optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG["lr"], betas=tuple(CONFIG["betas"]),
                                 eps=CONFIG["eps"], weight_decay=0)
    losses = []
    model.train()
    for step in range(CONFIG["steps"]):
        check(step)
        optimizer.zero_grad(set_to_none=True)
        logits = torch.stack([model(*pair) for pair in train])
        loss = torch.nn.functional.cross_entropy(logits, targets, reduction="mean")
        o2.require(bool(torch.isfinite(loss)), "nonfinite loss")
        loss.backward()
        o2.require(all(p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in model.parameters()),
                   "missing/nonfinite gradient")
        optimizer.step()
        if step in (0, CONFIG["steps"]-1):
            losses.append(dict(step_before_update=step+1, mean_fragment_cross_entropy=float(loss.detach())))
    check(CONFIG["steps"])
    return losses


def decision(logits):
    value = np.asarray(logits)
    o2.require(value.shape == (2,) and np.isfinite(value).all(), "nonfinite or invalid logits")
    return "UNKNOWN" if value[0] == value[1] else CLASSES[int(np.argmax(value))]


def summarize(rows):
    summary = {}
    for partition in ("train", "transfer"):
        subset = [r for r in rows if r["partition"] == partition]
        summary[partition] = dict(units=len(subset), correct=sum(r["decision"] == r["expected"] for r in subset),
                                  unknown=sum(r["decision"] == "UNKNOWN" for r in subset),
                                  target_loss=sum(r["expected"] == CLASSES[0] and r["decision"] != CLASSES[0] for r in subset),
                                  wrong_external_acceptance=sum(r["expected"] == CLASSES[1] and r["decision"] == CLASSES[0] for r in subset))
    return summary


def run(root, manifest_path, output):
    o2.require(not output.exists(), "refuse overwrite")
    started = time.monotonic()
    manifest = o2.read_json(manifest_path)
    arrays = load_inputs(root, manifest)  # before any model creation or output mutation
    o2.require(platform.python_version() == manifest["python"] and
               {p: version(p) for p in PACKAGES} == manifest["packages"] == PACKAGES, "runtime mismatch")
    # Existing CR1 guard has no model import/inference at module load; reuse only its offline/write guard and meters.
    spec = importlib.util.spec_from_file_location("native_trial_runtime_guard", verified(root, next(
        p for p in manifest["sources"] if p["path"] == GUARD)))
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    o2.require(root == base.ROOT and output.resolve().is_relative_to(base.WORKSPACE / "runs"),
               "trial output must be in existing isolated workspace/runs")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True)
    o2.require(not status.strip(), "trial requires a clean frozen head")
    allocated_before = base.allocated(base.WORKSPACE)
    o2.require(allocated_before + LIMITS["scratch_bytes"] < LIMITS["aggregate_workspace_bytes"], "workspace budget")
    denied = base.sandbox()
    output.mkdir()
    result = dict(schema=SCHEMA, head=head, manifest=pin(root, manifest_path), status="STOPPED_WITHOUT_RESULT",
                  production_changed=False, training_steps=0, untouched_holdout_recordings=0)
    try:
        import torch
        torch.set_num_threads(CONFIG["threads"])
        torch.set_num_interop_threads(CONFIG["threads"])
        torch.use_deterministic_algorithms(True)
        torch.manual_seed(CONFIG["seed"])
        model = make_model(torch)
        o2.require(sum(p.numel() for p in model.parameters()) == CONFIG["parameters"], "architecture parameter mismatch")
        initial = {k: array_hash(v.detach().numpy()) for k, v in model.state_dict().items()}
        tensors = {sid: tuple(torch.from_numpy(side[k]) for k in ("upper", "lower")) for sid, side in arrays.items()}
        indexed = o2.unique(manifest["units"], "id", "trial unit")

        def check(completed=None):
            if completed is not None:
                result["training_steps"] = completed
            o2.require(time.monotonic()-started < LIMITS["seconds"], "time budget")
            o2.require(base.rss() < LIMITS["peak_rss_bytes"], "RSS budget")
        train_ids = manifest["split"]["train"]
        losses = fit(torch, model, [tensors[s] for s in train_ids],
                     torch.tensor([indexed[s]["target"] for s in train_ids], dtype=torch.long), check)
        result["training_steps"] = CONFIG["steps"]
        model.eval()
        rows = []
        with torch.no_grad():
            for partition, ids in manifest["split"].items():
                for sid in ids:
                    check()
                    logits = model(*tensors[sid]).numpy().astype(float)
                    rows.append(dict(id=sid, partition=partition, review_role=indexed[sid]["review_role"],
                                     expected=CLASSES[indexed[sid]["target"]], logits=logits.tolist(),
                                     external_minus_nonexternal=float(logits[0]-logits[1]), decision=decision(logits)))
        weights = {k: v.detach().numpy() for k, v in model.state_dict().items()}
        o2.require(all(np.isfinite(v).all() for v in weights.values()), "nonfinite weights")
        np.savez(output / "final-weights.npz", **weights)
        all_correct = all(r["expected"] == r["decision"] for r in rows)
        result.update(status="LIMITED_EXPOSED_TRANSFER_ONLY" if all_correct else "CLOSED_WITHOUT_PROMOTION",
                      rows=rows, accounting=summarize(rows), losses=losses, weights_sha256=o2.sha256_file(output / "final-weights.npz"),
                      initial_parameter_hashes=initial, final_parameter_hashes={k: array_hash(v) for k, v in weights.items()},
                      model_fragment_calls=dict(training=CONFIG["steps"]*len(train_ids), final_fit=2, final_transfer=3),
                      runtime=dict(python=platform.python_version(), packages=PACKAGES, torch_build=torch.__config__.show()),
                      unassessed="Full G0 population, Oil/material roles, other internal appearances/optical controls, calibration, raw fronts, numeric/report effect, Windows/FIELD")
        check()
    except Exception as exc:
        result.update(status="STOPPED_WITHOUT_RESULT", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        result.update(resources=dict(elapsed_seconds=time.monotonic()-started, peak_rss_bytes=base.rss(),
                                     workspace_allocated_before=allocated_before, workspace_allocated_after=base.allocated(base.WORKSPACE)),
                      runtime_guard=dict(denied_events=denied, scope="Existing CR1 Python audit hook, not OS confinement"))
        o2.write_new(output / "readout.json", result)
        o2.require(sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) < LIMITS["retained_bytes"], "output budget")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--reply", type=Path, action="append", default=[])
    parser.add_argument("--qualification", type=Path, action="append", default=[])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    if args.mode == "prepare":
        result = prepare(args.root.resolve(), args.reply, args.qualification)
        o2.write_new(args.output, result)
        print(json.dumps(dict(status="FROZEN_INPUTS_PREPARED", units=len(result["units"]))))
    else:
        o2.require(args.manifest is not None, "manifest required")
        result = run(args.root.resolve(), args.manifest, args.output)
        print(json.dumps(dict(status=result["status"], accounting=result["accounting"], resources=result["resources"])))


if __name__ == "__main__":
    main()
