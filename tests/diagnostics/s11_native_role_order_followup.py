"""Fixed mean-RGB milk comparison; load saved weights, never fit or select a model.

The frozen order runner owns fitting on its original roster. This supplement
reuses its transforms/comparison and encoder for newly qualified source evidence.
"""
from __future__ import annotations

import argparse
import importlib.util
from importlib.metadata import version
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

from tests.diagnostics import s11_native_role_order_trial as order

old, o2 = order.old, order.o2
SCHEMA = "s11-frozen-mean-role-followup-v1"
REVIEW = "docs/50-diagnostics/s11/2026-10-14-native-milk-review/"
PREVIOUS = "docs/50-diagnostics/s11/2026-10-14-native-role-order/"
ROLES = {444: "STRUCTURE_BOUNDARY", 453: "STRUCTURE_BOUNDARY", 687: "EXTERNAL_SURFACE"}
LIMITS = dict(seconds=60, peak_rss_bytes=500_000_000, scratch_bytes=3_000_000,
              retained_bytes=1_000_000, aggregate_workspace_bytes=3_000_000_000)


def validate_roster(units, packet, fit_sources):
    indexed = o2.unique(units, "id", "followup unit")
    saved = o2.unique(packet["fragments"], "id", "saved fragment")
    o2.require(set(indexed) == set(saved), "complete source population changed")
    o2.require(packet["source_recording"]["sha256"] not in fit_sources, "source leakage")
    o2.require(set(ROLES) <= {u["native_fragment_id"] for u in units}, "missing required roles")
    for sid, unit in indexed.items():
        f = saved[sid]
        o2.require(unit["native_fragment_id"] == f["fragment_id"] and
                   unit["source_recording"] == packet["source_recording"] and
                   unit["frame"] == packet["frame"] and unit["context"] == f["context_support"] and
                   unit["path_sha256"] == o2.fingerprint_json(f["source_path_xy"]), "source/path/support changed")
        o2.require(unit["availability"] == f["context_support"]["status"] and
                   unit["partition"] == "followup", "availability/partition changed")
        o2.require(unit["review_role"] == ROLES.get(f["fragment_id"]), "unreviewed or required role changed")
        if unit["review_role"] is not None:
            o2.require(unit["context"]["status"] == order.READY, "required support unavailable")


def prepare(root):
    from tests.diagnostics import s11_native_role_qualification as q
    base = o2.read_json(root / PREVIOUS / "manifest.json")
    original = o2.read_json(root / PREVIOUS / "readout.json")
    source_manifest = o2.read_json(root / REVIEW / "source-manifest.json")
    packet_readout = o2.read_json(root / REVIEW / "native-packet.json")
    o2.require(packet_readout["manifest_sha256"] == o2.fingerprint_json(source_manifest), "packet manifest changed")
    packet, = packet_readout["native_review_packets"]
    o2.require(packet["case_id"] == "s7-settled-native" and len(packet["fragments"]) == 16, "milk roster changed")
    o2.require(packet["source_recording"]["sha256"] not in base["pairs"]["transfer"], "previous evaluation source reused")
    inputs = [old.pin(root, root / prefix / name) for prefix, names in
              [(PREVIOUS, ["manifest.json", "readout.json", "mean_rgb-weights.npz"]),
               (REVIEW, ["source-manifest.json", "native-packet.json"])] for name in names]
    weights = old.pin(root, root / PREVIOUS / "mean_rgb-weights.npz")
    o2.require(weights["sha256"] == original["arms"]["mean_rgb"]["weights_sha256"], "saved weights changed")
    qualified = {}
    for reply_name, readout_name in [("reply.json", "qualification.json"),
                                   ("location-reply.json", "location-qualification.json")]:
        rp, qp = root / REVIEW / reply_name, root / REVIEW / readout_name
        reply = o2.read_json(rp); saved = q.qualify(root, reply)
        o2.require(saved == o2.read_json(qp), "qualification changed")
        proposal = q.read_pin(root, reply["proposal"])
        subjects = q.by_id(proposal["subjects"], "subject")
        inputs.extend([old.pin(root, rp), old.pin(root, qp), reply["proposal"]])
        for result in saved["subjects"]:
            if result["review_status"] != "QUALIFIED_ROLE":
                continue
            sid = result["id"]
            o2.require(sid not in qualified, "duplicate qualified role")
            qualified[sid] = (result, subjects[sid], old.pin(root, qp))
    rgb_pin = source_manifest["review_source_image"]
    with Image.open(old.verified(root, rgb_pin)) as image:
        rgb = np.array(image.convert("RGB"))
    units = []
    ox, oy = packet["geometry"]["origin"]
    for f in packet["fragments"]:
        sid = f["id"]; review = qualified.get(sid)
        if review:
            result, subject, _ = review
            o2.require(subject["source_path_xy"] == f["source_path_xy"] and
                       result["source_recording"] == packet["source_recording"] and
                       result["frame"] == packet["frame"] and result["proposed_context"] == f["context_support"],
                       "qualified path/source/support mismatch")
        sides = {}
        if f["context_support"]["status"] == order.READY:
            for side in ("upper", "lower"):
                centers = [[x+ox, y+oy] for x, y in f["context_support"]["sides"][side]["complete_centers_xy"]]
                raw = old.patches(rgb, centers)
                sides[side] = dict(centers_image_xy=centers, shape=list(raw.shape), uint8_sha256=old.array_hash(raw))
        units.append(dict(id=sid, native_fragment_id=f["fragment_id"], source_recording=packet["source_recording"],
                          frame=packet["frame"], path_sha256=o2.fingerprint_json(f["source_path_xy"]),
                          context=f["context_support"], review_role=review[0]["capability_target"] if review else None,
                          qualification=review[2] if review else None,
                          subject_sha256=review[0]["subject_sha256"] if review else None,
                          sides=sides, partition="followup", availability=f["context_support"]["status"]))
    validate_roster(units, packet, set(base["pairs"]["train"]))
    pairs = order.pairs_by_source(units, "followup")
    o2.require([len(p) for p in pairs.values()] == [2], "two comparisons required")
    return dict(schema=SCHEMA, sources=base["sources"]+[old.pin(root, Path(__file__))], inputs=inputs,
                previous_manifest=old.pin(root, root / PREVIOUS / "manifest.json"),
                previous_readout=old.pin(root, root / PREVIOUS / "readout.json"), weights=weights,
                rgb=rgb_pin, packet=old.pin(root, root / REVIEW / "native-packet.json"), units=units, pairs=pairs,
                fit_sources=sorted(base["pairs"]["train"]), limits=LIMITS, python=base["python"], packages=base["packages"],
                arm="mean_rgb", training_updates=0, absolute_classification=False, physical_winner=None,
                scope="Two same-frame constraints: one large bubble's actual top above two cup-top structures. Unknowns are not truth; no stable-layer/front/episode or independent accuracy claim.")


def load_inputs(root, manifest):
    o2.require(manifest["schema"] == SCHEMA and manifest["limits"] == LIMITS and
               manifest["arm"] == "mean_rgb" and manifest["training_updates"] == 0, "fixed followup changed")
    for pin in manifest["sources"]+manifest["inputs"]:
        old.verified(root, pin)
    packet, = o2.read_json(old.verified(root, manifest["packet"]))["native_review_packets"]
    base = o2.read_json(old.verified(root, manifest["previous_manifest"]))
    o2.require(packet["source_recording"]["sha256"] not in base["pairs"]["transfer"], "previous evaluation source reused")
    o2.require(manifest["fit_sources"] == sorted(base["pairs"]["train"]), "fit source roster changed")
    validate_roster(manifest["units"], packet, set(manifest["fit_sources"]))
    o2.require(manifest["pairs"] == order.pairs_by_source(manifest["units"], "followup"), "pair roster changed")
    with Image.open(old.verified(root, manifest["rgb"])) as image:
        rgb = np.array(image.convert("RGB"))
    arrays = {}; ox, oy = packet["geometry"]["origin"]
    for u in manifest["units"]:
        if u["review_role"] is not None:
            saved = o2.read_json(old.verified(root, u["qualification"]))
            subject = o2.unique(saved["subjects"], "id", "qualified subject")[u["id"]]
            o2.require(subject["subject_sha256"] == u["subject_sha256"] and
                       subject["capability_target"] == u["review_role"] and
                       subject["proposed_context"] == u["context"], "qualified role/context changed")
        if u["context"]["status"] != order.READY:
            o2.require(not u["sides"], "unavailable unit has tensors")
            continue
        o2.require(set(u["sides"]) == {"upper", "lower"}, "two sides required")
        arrays[u["id"]] = {}
        for side, descriptor in u["sides"].items():
            centers = [[x+ox, y+oy] for x, y in u["context"]["sides"][side]["complete_centers_xy"]]
            o2.require(centers == descriptor["centers_image_xy"], "footprint changed")
            raw = old.patches(rgb, centers)
            o2.require(list(raw.shape) == descriptor["shape"] and old.array_hash(raw) == descriptor["uint8_sha256"], "RGB changed")
            arrays[u["id"]][side] = raw.astype(np.float32)/np.float32(255)
    return arrays


def checked_weights(archive, expected_hashes):
    o2.require(set(archive) == set(expected_hashes), "weight keys changed")
    values = {k: np.array(archive[k], copy=True) for k in archive}
    o2.require(all(v.dtype == np.float32 and np.isfinite(v).all() and old.array_hash(v) == expected_hashes[k]
                   for k, v in values.items()), "weight bytes changed")
    return values


def run(root, manifest_path, output):
    o2.require(not output.exists(), "refuse overwrite")
    m = o2.read_json(manifest_path); arrays = load_inputs(root, m)
    o2.require(platform.python_version() == m["python"] and {p: version(p) for p in old.PACKAGES} == m["packages"], "runtime mismatch")
    o2.require(not subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip(), "clean frozen head required")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    base = o2.read_json(old.verified(root, m["previous_manifest"]))
    controls = order.load_inputs(root, base)
    previous = o2.read_json(old.verified(root, m["previous_readout"]))["arms"]["mean_rgb"]
    o2.require(m["weights"]["sha256"] == previous["weights_sha256"], "wrong saved model")
    with np.load(old.verified(root, m["weights"]), allow_pickle=False) as archive:
        weights = checked_weights(archive, previous["final_parameter_hashes"])
    spec = importlib.util.spec_from_file_location("followup_guard", root / old.GUARD)
    guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
    o2.require(root == guard.ROOT and output.resolve().is_relative_to(guard.WORKSPACE / "runs"), "isolated workspace output required")
    allocated = guard.allocated(guard.WORKSPACE)
    o2.require(allocated+LIMITS["scratch_bytes"] < LIMITS["aggregate_workspace_bytes"], "workspace budget")
    denied = guard.sandbox(); started = time.monotonic()
    import torch
    torch.set_num_threads(2); torch.set_num_interop_threads(2); torch.use_deterministic_algorithms(True)
    model = old.make_model(torch)
    model.load_state_dict({k: torch.from_numpy(v) for k, v in weights.items()}, strict=True)
    model.requires_grad_(False); model.eval()
    def infer(sides):
        o2.require(time.monotonic()-started < LIMITS["seconds"] and guard.rss() < LIMITS["peak_rss_bytes"], "runtime budget")
        tensors = [torch.from_numpy(order.transform(sides[k], "mean_rgb")) for k in ("upper", "lower")]
        with torch.inference_mode():
            logits = model(*tensors).numpy().astype(float).tolist()
        o2.require(np.isfinite(logits).all(), "nonfinite inference")
        return logits
    errors = [max(abs(a-b) for a,b in zip(infer(controls[r["id"]]), r["logits"]))
              for r in previous["rows"] if r["logits"] is not None]
    o2.require(len(errors) == 26 and max(errors) < 1e-4, "saved-score reproduction failed")
    rows, scores = [], {}
    for u in m["units"]:
        logits = infer(arrays[u["id"]]) if u["id"] in arrays else None
        score = logits[0]-logits[1] if logits is not None else None
        if score is not None: scores[u["id"]] = score
        rows.append(dict(id=u["id"], role=u["review_role"], availability=u["availability"], logits=logits,
                         order_score=score, absolute_decision=None,
                         physical_evaluation="UNREVIEWED" if u["review_role"] is None else "PAIR_ORDER_ONLY"))
    comparison = order.compare(scores, m["pairs"])
    checked_weights({k: v.numpy() for k,v in model.state_dict().items()}, previous["final_parameter_hashes"])
    old.verified(root, m["weights"])
    result = dict(schema=SCHEMA, head=head, manifest=old.pin(root, manifest_path),
                  status="LIMITED_EXPOSED_ORDER_ONLY" if comparison["ordered"] == 2 else "FALSIFIED_ON_MILK_ORDER",
                  rows=rows, comparison=comparison, training_updates=0, parameters_unchanged=True,
                  prior_scores_reproduced=dict(units=26, max_absolute_logit_error=max(errors)),
                  counts=dict(total=len(rows), available=len(arrays), qualified=3, unreviewed=13),
                  absolute_classification=False, physical_winner=None, production_changed=False,
                  resources=dict(elapsed_seconds=time.monotonic()-started, peak_rss_bytes=guard.rss(), allocated_before=allocated),
                  runtime_guard=denied)
    o2.require(guard.rss() < LIMITS["peak_rss_bytes"] and time.monotonic()-started < LIMITS["seconds"], "final runtime budget")
    o2.write_new(output, result)
    o2.require(output.stat().st_size < LIMITS["retained_bytes"], "retained budget")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "run"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    if args.mode == "prepare":
        result = prepare(args.root.resolve()); o2.write_new(args.output, result)
        print({"units": len(result["units"]), "pairs": result["pairs"], "model_calls": 0})
    else:
        o2.require(args.manifest is not None, "manifest required")
        result = run(args.root.resolve(), args.manifest, args.output)
        print({k: result[k] for k in ("status", "counts", "resources")})
