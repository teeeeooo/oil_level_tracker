"""Frozen within-source role-order experiment; no detector or absolute classifier.

Reuse the closed trial's encoder and pixel/pin helpers, not its five-unit protocol.
New supervision is source-balanced positive/opposition ordering. The public source
is held out from fitting, including all its unreviewed/unavailable native paths.
"""
from __future__ import annotations

import argparse
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

from tests.diagnostics import s11_native_surface_trial as old

o2 = old.o2
SCHEMA = "s11-native-role-order-trial-v1"
CONFIG = dict(old.CONFIG, objective="source-balanced pairwise softplus", arms=["native", "mean_rgb"])
LIMITS = dict(old.LIMITS, seconds=600)
TRAIN = ["N1", "N2", "N3", "N4", "N5"]
POSITIVE = ["fragment-963", "fragment-995", "fragment-1029", "fragment-1031"]
RIM = ["fragment-1769", "fragment-1788", "fragment-1789"]
READY = "AVAILABLE_PARTIAL_CONTEXT"
REUSE = "docs/50-diagnostics/s11/2026-10-13-existing-material-execution/readout.json"


def pairs_by_source(units, partition):
    """Roles remain distinct; unknown and unavailable units supply no pair."""
    groups = {}
    for source in sorted({u["source_recording"]["sha256"] for u in units if u["partition"] == partition}):
        rows = [u for u in units if u["partition"] == partition and u["source_recording"]["sha256"] == source]
        positive = [u["id"] for u in rows if u["review_role"] == "EXTERNAL_SURFACE" and u["availability"] == READY]
        opposed = [u["id"] for u in rows if u["review_role"] in ("INTERNAL_FOAM_CHANGE", "STRUCTURE_BOUNDARY")
                   and u["availability"] == READY]
        groups[source] = [[a, b] for a in positive for b in opposed]
    return groups


def validate_units(units):
    indexed = o2.unique(units, "id", "role-order unit")
    o2.require({u["id"] for u in units if u["partition"] == "train"} == set(TRAIN), "frozen fit roster changed")
    o2.require(set(indexed) == set(TRAIN) | {f"fragment-{u['native_fragment_id']}" for u in units
                                          if u["partition"] == "transfer"}, "unaccounted partition")
    sources = [{u["source_recording"]["sha256"] for u in units if u["partition"] == p}
               for p in ("train", "transfer")]
    o2.require(len(sources[0]) == 2 and len(sources[1]) == 1 and not sources[0] & sources[1], "source leakage or split changed")
    roles = {"N1": "EXTERNAL_SURFACE", "N2": "INTERNAL_FOAM_CHANGE", "N3": "EXTERNAL_SURFACE",
             "N4": "INTERNAL_FOAM_CHANGE", "N5": "STRUCTURE_BOUNDARY",
             **{sid: "EXTERNAL_SURFACE" for sid in POSITIVE}, **{sid: "STRUCTURE_BOUNDARY" for sid in RIM}}
    o2.require(set(roles) <= set(indexed), "missing required role unit")
    for unit in units:
        o2.require(unit["review_role"] == roles.get(unit["id"]), "unreviewed unit acquired a role or reviewed role changed")
        if unit["review_role"] is not None:
            o2.require(unit["availability"] == READY, "required role input unavailable")
    o2.require(sorted(map(len, pairs_by_source(units, "train").values())) == [1, 2], "training pair coverage changed")
    o2.require(list(map(len, pairs_by_source(units, "transfer").values())) == [12], "public pair coverage changed")


def validate_public_roster(units, packet):
    public = {u["id"]: u for u in units if u["partition"] == "transfer"}
    original = {f"fragment-{f['fragment_id']}": f for f in packet["fragments"]}
    o2.require(set(public) == set(original), "public population dropped or added a path")
    reference = public[POSITIVE[0]]
    for sid, unit in public.items():
        saved = original[sid]
        o2.require(unit["source_recording"] == packet["source_recording"] and unit["frame"] == packet["frame"] and
                   unit["path_sha256"] == o2.fingerprint_json(saved["source_path_xy"]) and
                   unit["context"] == saved["context_support"] and unit["availability"] == saved["context_support"]["status"] and
                   unit["origin"] == packet["geometry"]["origin"] and unit["rgb"] == reference["rgb"] and
                   unit["image_origin"] == reference["image_origin"], "public path/source/support changed")


def prepare(root, readiness_path):
    from tests.diagnostics import s11_native_role_qualification as q
    readiness = o2.read_json(readiness_path)
    units, inputs, identities = [], [old.pin(root, readiness_path)], set()
    public_view = public_context = baseline_pin = None
    for pair in readiness["qualification_pairs"]:
        reply = q.read_pin(root, pair["reply"])
        result = q.qualify(root, reply)
        o2.require(result == q.read_pin(root, pair["readout"]), "qualification changed")
        proposal = q.read_pin(root, reply["proposal"])
        if baseline_pin is None:
            baseline_pin = proposal["g0_readout"]
        o2.require(proposal["g0_readout"] == baseline_pin, "mixed G0 snapshots")
        baseline = q.read_pin(root, baseline_pin)
        subjects, views = q.by_id(proposal["subjects"], "subject"), q.by_id(proposal["views"], "view")
        inputs.extend([pair["reply"], pair["readout"], reply["proposal"]])
        for subject in result["subjects"]:
            raw = subjects[subject["id"]]
            key = (subject["source_recording"]["sha256"], subject["frame"], o2.fingerprint_json(raw["source_path_xy"]))
            o2.require(key not in identities, "duplicate source/frame/path")
            identities.add(key)
            context = baseline["contexts"][subject["g0_pointer"][1]]
            view = views[raw["view_id"]]
            unit = dict(id=subject["id"], native_fragment_id=raw["native_fragment_id"],
                        source_recording=subject["source_recording"], frame=subject["frame"],
                        review_role=subject["capability_target"], qualification=pair["readout"],
                        subject_sha256=subject["subject_sha256"], context=subject["proposed_context"],
                        path_sha256=key[-1], rgb=view["source"], origin=context["geometry"]["origin"],
                        image_origin=view["image_origin_xy"])
            units.append(unit)
            if subject["id"] in POSITIVE:
                public_view, public_context = view, context
    reused = q.o2.read_json(root / REUSE)
    packet, = reused["native_review_packets"]
    o2.require(public_context is not None and packet["case_id"] == public_context["id"], "public roster mismatch")
    qualified = {u["id"]: u for u in units}
    for fragment in packet["fragments"]:
        sid = f"fragment-{fragment['fragment_id']}"
        if sid in qualified:
            o2.require(qualified[sid]["path_sha256"] == o2.fingerprint_json(fragment["source_path_xy"]) and
                       qualified[sid]["context"] == fragment["context_support"], "review and saved native support differ")
        else:
            units.append(dict(id=sid, native_fragment_id=fragment["fragment_id"], source_recording=packet["source_recording"],
                              frame=packet["frame"], review_role=None, qualification=None, subject_sha256=None,
                              context=fragment["context_support"], path_sha256=o2.fingerprint_json(fragment["source_path_xy"]),
                              rgb=public_view["source"], origin=packet["geometry"]["origin"], image_origin=public_view["image_origin_xy"]))
    for unit in units:
        unit["partition"] = "train" if unit["id"] in TRAIN else "transfer"
        unit["availability"] = unit["context"]["status"]
        unit["sides"] = {}
        if unit["availability"] != READY:
            continue
        with Image.open(old.verified(root, unit["rgb"])) as image:
            rgb = np.array(image.convert("RGB"))
        ox, oy = unit["origin"]; vx, vy = unit["image_origin"]
        for side, support in unit["context"]["sides"].items():
            centers = [[x+ox-vx, y+oy-vy] for x, y in support["complete_centers_xy"]]
            raw = old.patches(rgb, centers)
            unit["sides"][side] = dict(centers_image_xy=centers, shape=list(raw.shape), uint8_sha256=old.array_hash(raw))
    validate_units(units)
    validate_public_roster(units, packet)
    o2.require(len(units) == 5+len(packet["fragments"]) == 32, "complete public roster changed")
    inputs += [baseline_pin, old.pin(root, root / REUSE)]
    sources = [Path(__file__), Path(old.__file__), Path(q.__file__), Path(q.g0.__file__),
               Path(q.g0.cr1.__file__), Path(q.g0.contours.__file__), Path(q.g0.material.__file__),
               Path(q.g0.faces.__file__), Path(o2.__file__), root / old.GUARD,
               root / "src/oil_tracker/application/services/truth_identity.py",
               root / "src/oil_tracker/domain/detector_benchmark.py"]
    return dict(schema=SCHEMA, configuration=CONFIG, resource_limits=LIMITS, packages=old.PACKAGES,
                python="3.14.7", sources=[old.pin(root, p) for p in sources], inputs=inputs, units=units,
                pairs={p: pairs_by_source(units, p) for p in ("train", "transfer")},
                capability="Within-source relative ordering of qualified external paths above internal/structure paths",
                absolute_classification=False, production_changed=False, untouched_holdout_recordings=0,
                prior_failed_transfer="N3 now enters fit in this NEW data/loss contract; its old transfer failure remains. No independent N3 success.",
                feature_boundary="Only saved RGB/255 tensors; source/position/role/facets/count are not inference features.",
                loss="Mean softplus(-(positive margin - opposition margin)) within each training source, then mean sources. Margin is logit0-logit1; no absolute cutoff.",
                arms="Same 1118-parameter encoder/init/schedule. native versus per-patch RGB mean tiled to 7x7; each arm fitted once.",
                success="Every 3 fit and 12 public pair comparisons strict positive; native must additionally beat mean_rgb on a required public pair to establish spatial-pattern advantage.",
                stop="Any native required pair error/tie closes without promotion; no threshold/seed/crop/architecture/split retry.",
                unknowns="All 27 public paths retained; 20 unreviewed paths never targets. No top-score selection or negative success from unavailable input.")


def load_inputs(root, manifest):
    o2.require(manifest["schema"] == SCHEMA and manifest["configuration"] == CONFIG and
               manifest["resource_limits"] == LIMITS, "frozen order protocol changed")
    for entry in manifest["sources"] + manifest["inputs"]:
        old.verified(root, entry)
    validate_units(manifest["units"])
    packet, = o2.read_json(root / REUSE)["native_review_packets"]
    validate_public_roster(manifest["units"], packet)
    o2.require(manifest["pairs"] == {p: pairs_by_source(manifest["units"], p) for p in ("train", "transfer")}, "pair roster changed")
    arrays = {}
    for unit in manifest["units"]:
        if unit["qualification"] is not None:
            saved = o2.read_json(old.verified(root, unit["qualification"]))
            subject = o2.unique(saved["subjects"], "id", "qualified subject")[unit["id"]]
            o2.require(subject["subject_sha256"] == unit["subject_sha256"] and
                       subject["capability_target"] == unit["review_role"] and
                       subject["source_recording"] == unit["source_recording"] and subject["frame"] == unit["frame"] and
                       subject["proposed_context"] == unit["context"], "unit differs from qualified role/source/support")
        if unit["availability"] != READY:
            o2.require(not unit["sides"], "unavailable input has tensors")
            continue
        with Image.open(old.verified(root, unit["rgb"])) as image:
            rgb = np.array(image.convert("RGB"))
        arrays[unit["id"]] = {}
        for side, descriptor in unit["sides"].items():
            ox, oy = unit["origin"]; vx, vy = unit["image_origin"]
            centers = [[x+ox-vx, y+oy-vy] for x, y in unit["context"]["sides"][side]["complete_centers_xy"]]
            o2.require(centers == descriptor["centers_image_xy"], "context footprint changed")
            raw = old.patches(rgb, centers)
            o2.require(list(raw.shape) == descriptor["shape"] and old.array_hash(raw) == descriptor["uint8_sha256"], "RGB input changed")
            arrays[unit["id"]][side] = raw.astype(np.float32) / np.float32(255)
        o2.require(set(arrays[unit["id"]]) == {"upper", "lower"}, "both sides required")
    return arrays


def transform(array, arm):
    o2.require(arm in CONFIG["arms"], "unknown ablation arm")
    if arm == "native":
        return array.copy()
    return np.broadcast_to(array.mean(axis=(-2, -1), keepdims=True), array.shape).copy()


def pair_loss(torch, scores, groups):
    o2.require(groups and all(groups.values()), "empty training pairs")
    return torch.stack([torch.stack([torch.nn.functional.softplus(-(scores[a]-scores[b]))
                                     for a, b in pairs]).mean() for pairs in groups.values()]).mean()


def fit(torch, model, tensors, groups, check, steps=CONFIG["steps"]):
    optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG["lr"], betas=tuple(CONFIG["betas"]),
                                 eps=CONFIG["eps"], weight_decay=CONFIG["weight_decay"])
    losses = []
    ids = sorted({sid for pairs in groups.values() for pair in pairs for sid in pair})
    model.train()
    for step in range(steps):
        check(step); optimizer.zero_grad(set_to_none=True)
        logits = {sid: model(*tensors[sid]) for sid in ids}
        loss = pair_loss(torch, {sid: value[0]-value[1] for sid, value in logits.items()}, groups)
        o2.require(bool(torch.isfinite(loss)), "nonfinite pair loss")
        loss.backward()
        o2.require(all(p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in model.parameters()), "missing/nonfinite gradient")
        optimizer.step()
        if step in (0, steps-1):
            losses.append(dict(step_before_update=step+1, source_balanced_pair_loss=float(loss.detach())))
    check(steps)
    return losses


def compare(scores, groups):
    rows = []
    for source, pairs in groups.items():
        for a, b in pairs:
            gap = float(scores[a]-scores[b])
            o2.require(np.isfinite(gap), "nonfinite order score")
            rows.append(dict(source_sha256=source, positive=a, opposition=b, score_gap=gap,
                             status="ORDERED" if gap > 0 else "TIE" if gap == 0 else "REVERSED"))
    return dict(pairs=len(rows), ordered=sum(r["status"] == "ORDERED" for r in rows),
                ties=sum(r["status"] == "TIE" for r in rows), rows=rows,
                independent_trials=False, absolute_accuracy=None)


def disposition(arms):
    native, mean = arms["native"], arms["mean_rgb"]
    if any(native[p]["ordered"] != native[p]["pairs"] for p in ("train", "transfer")):
        return "CLOSED_WITHOUT_PROMOTION"
    if mean["transfer"]["ordered"] == mean["transfer"]["pairs"]:
        return "NO_NATIVE_PATTERN_ADVANTAGE"
    return "LIMITED_EXPOSED_ORDER_INFORMATION"


def run(root, manifest_path, output):
    o2.require(not output.exists(), "refuse overwrite")
    manifest = o2.read_json(manifest_path); arrays = load_inputs(root, manifest)
    o2.require(platform.python_version() == manifest["python"] and
               {p: version(p) for p in old.PACKAGES} == manifest["packages"] == old.PACKAGES, "runtime mismatch")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    o2.require(not subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip(), "clean frozen head required")
    spec = importlib.util.spec_from_file_location("role_order_guard", old.verified(root, next(p for p in manifest["sources"] if p["path"] == old.GUARD)))
    guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
    o2.require(root == guard.ROOT and output.resolve().is_relative_to(guard.WORKSPACE / "runs"), "isolated workspace output required")
    allocated = guard.allocated(guard.WORKSPACE)
    o2.require(allocated+LIMITS["scratch_bytes"] < LIMITS["aggregate_workspace_bytes"], "workspace budget")
    denied = guard.sandbox(); output.mkdir(); started = time.monotonic()
    result = dict(schema=SCHEMA, head=head, manifest=old.pin(root, manifest_path), status="STOPPED_WITHOUT_RESULT",
                  arms={}, production_changed=False, absolute_classification=False, training_steps={})
    try:
        import torch
        torch.set_num_threads(CONFIG["threads"]); torch.set_num_interop_threads(CONFIG["threads"])
        torch.use_deterministic_algorithms(True)
        for arm in CONFIG["arms"]:
            torch.manual_seed(CONFIG["seed"]); model = old.make_model(torch)
            o2.require(sum(p.numel() for p in model.parameters()) == CONFIG["parameters"], "encoder changed")
            initial = {k: old.array_hash(v.detach().numpy()) for k, v in model.state_dict().items()}
            tensors = {sid: tuple(torch.from_numpy(transform(sides[k], arm)) for k in ("upper", "lower")) for sid, sides in arrays.items()}
            def check(step=None):
                if step is not None: result["training_steps"][arm] = step
                o2.require(time.monotonic()-started < LIMITS["seconds"] and guard.rss() < LIMITS["peak_rss_bytes"], "runtime budget")
            losses = fit(torch, model, tensors, manifest["pairs"]["train"], check)
            model.eval(); scores = {}; rows = []
            with torch.no_grad():
                for unit in manifest["units"]:
                    check(); sid = unit["id"]
                    logits = model(*tensors[sid]).numpy().astype(float).tolist() if sid in tensors else None
                    score = float(logits[0]-logits[1]) if logits is not None else None
                    if score is not None:
                        o2.require(np.isfinite(score), "nonfinite inference")
                        scores[sid] = score
                    rows.append(dict(id=sid, partition=unit["partition"], review_role=unit["review_role"],
                                     availability=unit["availability"], logits=logits, order_score=score,
                                     absolute_decision=None, physical_evaluation="UNREVIEWED" if unit["review_role"] is None else "PAIR_ORDER_ONLY"))
            weights = {k: v.detach().numpy() for k, v in model.state_dict().items()}
            np.savez(output / f"{arm}-weights.npz", **weights)
            result["arms"][arm] = dict(rows=rows, losses=losses, initial_parameter_hashes=initial,
                final_parameter_hashes={k: old.array_hash(v) for k, v in weights.items()},
                weights_sha256=o2.sha256_file(output / f"{arm}-weights.npz"),
                **{p: compare(scores, manifest["pairs"][p]) for p in ("train", "transfer")})
        result.update(status=disposition(result["arms"]), counts=dict(units=len(manifest["units"]),
                      available=len(arrays), qualified=sum(u["review_role"] is not None for u in manifest["units"]),
                      unreviewed=sum(u["review_role"] is None for u in manifest["units"]),
                      untouched_holdout_recordings=0), runtime=dict(python=platform.python_version(), packages=old.PACKAGES))
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        result.update(resources=dict(elapsed_seconds=time.monotonic()-started, peak_rss_bytes=guard.rss(),
                                     workspace_allocated_before=allocated, workspace_allocated_after=guard.allocated(guard.WORKSPACE)),
                      runtime_guard=dict(denied_events=denied, scope="Existing Python audit guard, not OS confinement"))
        o2.write_new(output / "readout.json", result)
        o2.require(sum(p.stat().st_size for p in output.rglob("*") if p.is_file()) < LIMITS["retained_bytes"], "output budget")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run")); parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--readiness", type=Path); parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True); args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    if args.mode == "prepare":
        o2.require(args.readiness is not None, "readiness required")
        result = prepare(args.root.resolve(), args.readiness); o2.write_new(args.output, result)
        print(json.dumps(dict(status="PREPARED", units=len(result["units"]))))
    else:
        o2.require(args.manifest is not None, "manifest required")
        result = run(args.root.resolve(), args.manifest, args.output)
        print(json.dumps(dict(status=result["status"], counts=result.get("counts"), resources=result["resources"])))


if __name__ == "__main__":
    main()
