"""NCT-1: separate partial-role targets and an ordered-side interaction kernel.

One fixed source-held-out trial. No encoder restoration, cutoff search, pixel
labels or production consumer. Frozen corpus readers own source/path/RGB truth.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_native_role_corpus as corpus
from tests.diagnostics.s11_resolver_replacement_profile import peak_rss

old, o2 = corpus.old, corpus.o2
SCHEMA = "s11-native-contact-trial-v1"
ARMS = ("native_joint", "native_additive", "mean_joint")
CONFIG = dict(arms=list(ARMS), channels=list(corpus.CHANNELS), ridge=0.01, tie_epsilon=1e-9,
              normalization="RGB / 127.5 - 1; equal patch mean; no fitted transform",
              kernel="1 + upper_dot/147 + lower_dot/147 + product of both dots",
              loss="class-balanced, then source-balanced, then path-balanced squared error plus ridge",
              targets="positive +1; explicit internal/structure opposition -1; other roles masked",
              split="leave one entire recording out, all four fixed folds",
              operating_point=0, optimizer="one float64 linear solve per arm/channel/fold",
              calibration="NONE; scores are not probabilities", seed=None)
LIMITS = dict(seconds=120, peak_rss_bytes=1_000_000_000, scratch_bytes=8_000_000, retained_bytes=3_000_000)


def runtime():
    return dict(python=platform.python_version(), numpy=np.__version__, pillow=pillow_version,
                system=platform.system(), machine=platform.machine())


def feature(pair, arm):
    """The inference entry receives only the two native RGB arrays."""
    o2.require(arm in ARMS and set(pair) == {"upper", "lower"}, "unknown arm or incomplete side pair")
    sides = []
    for name in ("upper", "lower"):
        a = np.asarray(pair[name])
        o2.require(a.dtype == np.uint8 and a.ndim == 4 and a.shape[0] > 0 and
                   a.shape[1:] == (3, 7, 7), "expected native uint8 N x 3 x 7 x 7")
        f = a.astype(np.float64) / 127.5 - 1
        if arm == "mean_joint":
            f = np.broadcast_to(f.mean(axis=(2, 3), keepdims=True), f.shape)
        sides.append(f.mean(axis=0).reshape(147))
    return np.stack(sides)


def kernel(a, b, arm):
    o2.require(arm in ARMS, "unknown kernel arm")
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    o2.require(a.ndim == b.ndim == 3 and a.shape[1:] == b.shape[1:] == (2, 147) and
               np.isfinite(a).all() and np.isfinite(b).all(), "invalid feature matrix")
    upper, lower = (a[:, i] @ b[:, i].T / 147 for i in range(2))
    return 1 + upper + lower + (0 if arm == "native_additive" else upper * lower)


def training_rows(rows, held_source, channel):
    o2.require(channel in corpus.CHANNELS, "unknown target channel")
    o2.unique(rows, "id", "trial row")
    chosen = [r for r in rows if r["source_recording"]["sha256"] != held_source
              and r["targets"]["native_loss_mask"][channel]]
    labels = [r["targets"]["values"][channel] for r in chosen]
    o2.require(set(labels) == {0, 1}, "both certain classes required in fitting sources")
    weights = []
    for row, label in zip(chosen, labels):
        groups = {r["source_recording"]["sha256"] for r in chosen if r["targets"]["values"][channel] == label}
        count = sum(r["source_recording"]["sha256"] == row["source_recording"]["sha256"] and
                    r["targets"]["values"][channel] == label for r in chosen)
        weights.append(0.5 / len(groups) / count)
    return chosen, np.array(labels, dtype=np.float64) * 2 - 1, np.array(weights)


def fit(features, targets, weights, arm):
    o2.require(len(features) == len(targets) == len(weights) > 0 and
               set(targets) == {-1, 1} and np.isfinite(weights).all() and
               (weights > 0).all() and abs(float(weights.sum()) - 1) < 1e-12, "invalid weighted fit")
    k = kernel(features, features, arm)
    scale = np.sqrt(weights)
    system = scale[:, None] * k * scale[None, :] + CONFIG["ridge"] * np.eye(len(weights))
    alpha = scale * np.linalg.solve(system, scale * targets)
    residual = (k + CONFIG["ridge"] * np.diag(1 / weights)) @ alpha - targets
    o2.require(np.isfinite(alpha).all() and np.max(np.abs(residual)) < 1e-9, "ridge solve failed")
    return alpha


def decision(score):
    if score is None:
        return "UNAVAILABLE"
    o2.require(np.isfinite(score), "nonfinite prediction")
    return "UNKNOWN" if abs(score) <= CONFIG["tie_epsilon"] else "POSITIVE" if score > 0 else "OPPOSITION"


def load_inputs(root, plan):
    o2.require(plan["schema"] == SCHEMA and plan["configuration"] == CONFIG and
               plan["limits"] == LIMITS and plan["runtime"] == runtime(), "trial protocol/runtime changed")
    for pin in plan["sources"]:
        old.verified(root, pin)
    data = corpus.native.read_pin(root, plan["corpus"])
    source_plan = corpus.native.read_pin(root, plan["corpus_plan"])
    o2.require(corpus.build(root, source_plan) == data, "frozen complete corpus changed")
    images, arrays = {}, {}
    for key, frame in data["frames"].items():
        with Image.open(old.verified(root, frame["rgb"])) as image:
            images[key] = np.array(image.convert("RGB"))
    for row in data["rows"]:
        o2.require(row["targets"] == corpus.targets(row), "partial targets changed")
        if not row["native_sides"]:
            continue
        pair = {}
        for side, spec in row["native_sides"].items():
            raw = old.patches(images[row["frame_key"]], spec["centers_image_xy"])
            o2.require(list(raw.shape) == spec["shape"] and old.array_hash(raw) == spec["uint8_sha256"],
                       "native RGB tensor changed")
            pair[side] = raw
        arrays[row["id"]] = pair
    o2.require(len(arrays) == data["counts"]["native_available"], "native input population changed")
    return data, arrays


def summarize(rows, arm):
    result = {}
    for channel in corpus.CHANNELS:
        known = [r for r in rows if r["targets"][channel] is not None]
        positives = [r for r in known if r["targets"][channel] == 1]
        opposed = [r for r in known if r["targets"][channel] == 0]
        expected = lambda r: "POSITIVE" if r["targets"][channel] else "OPPOSITION"
        result[channel] = dict(required=len(known), correct=sum(r["decisions"][arm][channel] == expected(r) for r in known),
            positive_loss=[r["id"] for r in positives if r["decisions"][arm][channel] != "POSITIVE"],
            opposition_failure=[r["id"] for r in opposed if r["decisions"][arm][channel] != "OPPOSITION"],
            wrong_acceptance=[r["id"] for r in opposed if r["decisions"][arm][channel] == "POSITIVE"],
            unassessed=len(rows)-len(known))
    disjunction = [r for r in rows if len(r["allowed_roles"]) > 1]
    result["disjunction"] = dict(required=len(disjunction), compatible=sum(any(
        r["decisions"][arm][c] == "POSITIVE" for c in r["allowed_roles"]) for r in disjunction))
    passed = all(result[c]["correct"] == result[c]["required"] for c in corpus.CHANNELS)
    passed &= result["disjunction"]["compatible"] == len(disjunction)
    result["status"] = "LIMITED_EXPOSED_CONTROL_PASS" if passed else "CLOSED_WITHOUT_PROMOTION"
    return result


def evaluate(data, arrays, check=lambda: None):
    rows = data["rows"]
    sources = sorted({r["source_recording"]["sha256"] for r in rows})
    models, scores = [], {r["id"]: {arm: {} for arm in ARMS} for r in rows}
    feature_hashes = {}
    for arm in ARMS:
        features = {sid: feature(pair, arm) for sid, pair in arrays.items()}
        feature_hashes[arm] = {sid: old.array_hash(x) for sid, x in features.items()}
        for held in sources:
            held_rows = [r for r in rows if r["source_recording"]["sha256"] == held]
            for channel in corpus.CHANNELS:
                check()
                selected, labels, weights = training_rows(rows, held, channel)
                ids = [r["id"] for r in selected]
                x = np.stack([features[sid] for sid in ids])
                alpha = fit(x, labels, weights, arm)
                fitted = kernel(x, x, arm) @ alpha
                models.append(dict(arm=arm, channel=channel, held_out_source=held, fitting_ids=ids,
                    targets=labels.tolist(), path_weights=weights.tolist(), dual_coefficients=alpha.tolist(),
                    fitting_scores=fitted.tolist(), fitting_correct=sum(decision(s) ==
                        ("POSITIVE" if y == 1 else "OPPOSITION") for s, y in zip(fitted, labels))))
                for row in held_rows:
                    sid = row["id"]
                    scores[sid][arm][channel] = (float((kernel(features[sid][None], x, arm) @ alpha)[0])
                                               if sid in features else None)
    output = [dict(id=r["id"], source_recording=r["source_recording"], frame=r["frame"],
                   path_sha256=r["path_sha256"], corpus_pointer=f"/rows/{i}", availability=r["availability"],
                   targets=r["targets"]["values"], allowed_roles=r["allowed_boundary_roles"],
                   scores=scores[r["id"]], decisions={arm: {c: decision(v) for c, v in values.items()}
                                                     for arm, values in scores[r["id"]].items()})
              for i, r in enumerate(rows)]
    summaries = {arm: summarize(output, arm) for arm in ARMS}
    return dict(counts=data["counts"], rows=output, models=models, feature_sha256=feature_hashes,
                summaries=summaries, status=summaries["native_joint"]["status"],
                total_fits=len(models), untouched_holdout_recordings=0, production_changed=False,
                threshold_selected_after_results=False, new_encoder_calls=0, video_decodes=0)


def run(root, plan, output):
    o2.require(not output.exists(), "refuse overwrite")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, encoding="utf-8").strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True, encoding="utf-8")
    o2.require(not status.strip(), "trial requires clean frozen head")
    started = time.monotonic()
    def check():
        memory = peak_rss()
        o2.require(time.monotonic() - started <= LIMITS["seconds"], "trial time limit")
        o2.require(memory["bytes"] is not None and memory["bytes"] <= LIMITS["peak_rss_bytes"], "trial RSS limit or unavailable meter")
    data, arrays = load_inputs(root, plan)
    check()
    result = dict(schema=SCHEMA, plan_sha256=o2.fingerprint_json(plan), code_commit=head,
                  configuration=CONFIG, corpus=plan["corpus"], runtime=runtime(), **evaluate(data, arrays, check))
    check()
    result["resources"] = dict(seconds=time.monotonic()-started, peak_rss=peak_rss(), limits=LIMITS)
    o2.require(len(json.dumps(result).encode("utf-8")) < LIMITS["retained_bytes"], "result byte budget")
    output.parent.mkdir(parents=True, exist_ok=True)
    o2.write_new(output, result)
    print(json.dumps({k: result[k] for k in ("status", "total_fits", "summaries", "resources")}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    run(args.root.resolve(), o2.read_json(args.plan), args.output)


if __name__ == "__main__":
    main()
