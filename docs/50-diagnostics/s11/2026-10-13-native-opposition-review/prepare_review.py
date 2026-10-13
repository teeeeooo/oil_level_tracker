"""Prepare two new human-review units from frozen G0, without assigning roles.

Reuse G0 graph/binding and the qualified RGB-context audit. The old N1-N3
renderer is a frozen, fixed-label artifact; this successor keeps its paired
original/path layout and adds a clearly distinguished, already-reviewed N3.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_native_role_preflight as g0
from tests.diagnostics import s11_native_role_qualification as qualification

G0 = "docs/50-diagnostics/s11/2026-10-13-native-role-readiness"
REVIEW = "docs/50-diagnostics/s11/2026-10-13-native-role-qualification"
SELECTION = [("N4", "s4-f1620", 295, 824, "sample4", [617, 835]),
             ("N5", "s4-f450", 1278, 880, "sample4-15s", [615, 869])]


def pin(root, path):
    return {"path": path, "sha256": g0.o2.sha256_file(root / path)}


def build(root):
    prior_pin = pin(root, f"{G0}/review-proposal.json")
    prior = qualification.read_pin(root, prior_pin)
    manifest = qualification.read_pin(root, prior["g0_manifest"])
    baseline = qualification.read_pin(root, prior["g0_readout"])
    g0.o2.require(baseline["manifest_sha256"] == g0.o2.fingerprint_json(manifest), "G0 mismatch")
    plan = qualification.read_pin(root, manifest["inputs"]["foam_preflight"])
    cases = qualification.by_id(plan["cases"], "case")
    contexts = qualification.by_id(baseline["contexts"], "context")
    bindings = qualification.by_id(manifest["bindings"], "binding")
    subjects, views, frames, supports, used = [], [], {}, {}, {}
    for sid, cid, fid, sy, view_id, label in SELECTION:
        case, context = cases[cid], contexts[cid]
        g0.o2.require(g0.o2.fingerprint_json(case) == bindings[cid]["case_sha256"], "case changed")
        for name in [case["rgb"], *case["images"].values()]:
            g0.pinned_path(root, {"path": name, "sha256": plan["pins"][name]})
        rgb, visible, _ = g0.material.load_case(root, case)
        edges, _ = g0.load_edges_labels(root, case, {"labels": None})
        graph = g0.contours.measure_edge_fragments(edges, visible)
        ox, oy = case["origin"]
        row = next(r for r in context["rows"] if r["source_xy"] == [ox+case["column"], sy])
        saved = next(p for p in row["incident_fragments"] if p["fragment_id"] == fid)
        actual = g0.fragment_binding(graph, fid, case["column"], row["row"], visible)
        g0.o2.require(g0.o2.fingerprint_json(actual) == g0.o2.fingerprint_json(saved),
                       "native fragment differs from frozen G0")
        path = graph["vertices_xy"][graph["fragments"][fid]].tolist()
        source = [[x+ox, y+oy] for x, y in path]
        subject = dict(id=sid, case_id=cid, frame=context["frame"], view_id=view_id,
                       fixed_column_xy=row["source_xy"], native_fragment_id=fid, source_path_xy=source,
                       raster_path_sha256=saved["path_sha256"], readout_subject_sha256=g0.o2.fingerprint_json(saved),
                       vertex_count=len(path), junction_incident=saved["junction_incident"],
                       display_label_xy=label, role="PENDING_USER_REVIEW",
                       scope="This complete highlighted saved fragment only; no family, adjacent frame, dense pixel mask or exact physical-coordinate tolerance.")
        subjects.append(subject)
        views.append(dict(id=view_id, title=f"Sample4 | frame {context['frame']} ({context['time_sec']:g} s)",
                          source=pin(root, case["rgb"]), image_origin_xy=[ox, oy],
                          display_xyxy=[ox, oy, ox+rgb.shape[1], oy+rgb.shape[0]]))
        frames[cid] = graph, visible, case
        supports[sid], used[sid] = qualification.context_support(visible, saved["support_columns_xy"], path)

    n3 = next(s for s in prior["subjects"] if s["id"] == "N3")
    prior_reply = qualification.read_pin(root, pin(root, f"{REVIEW}/review-reply.json"))
    reply = next(a for a in prior_reply["answers"] if a["id"] == "N3")
    g0.o2.require(reply["subject_sha256"] == g0.o2.fingerprint_json(n3) and
                   reply["allowed_interpretations"] == ["EXTERNAL_FOAM_UPPER"], "N3 authority changed")
    graph, visible, case = frames[n3["case_id"]]
    ox, oy = case["origin"]
    path = [[x-ox, y-oy] for x, y in n3["source_path_xy"]]
    g0.o2.require(g0.o2.fingerprint_json(path) == n3["raster_path_sha256"], "N3 geometry changed")
    columns = [(x, y) for x, y in path if abs(x-case["column"]) <= 12]
    supports["N3"], used["N3"] = qualification.context_support(visible, columns, path)

    survey = []
    for cid, ids in [("s4-f1620", [3, 24, 295, 564]), ("s4-f450", [1278, 908])]:
        graph, visible, case = frames[cid]
        for fid in ids:
            path = graph["vertices_xy"][graph["fragments"][fid]].tolist()
            columns = [(x, y) for x, y in path if abs(x-case["column"]) <= 12]
            support, _ = qualification.context_support(visible, columns, path)
            survey.append(dict(case_id=cid, fragment_id=fid, vertex_count=len(path),
                               selected_for_review=any(s["case_id"] == cid and s["native_fragment_id"] == fid for s in subjects),
                               complete_patches={side: data["complete_patches"] for side, data in support["sides"].items()},
                               status=support["status"], physical_role="UNREVIEWED"))
    return dict(schema="s11-native-fragment-role-review-proposal-v1", status="PENDING_USER_JUDGMENT",
                base_head="e688e7adccfe3553d9dd91b3b50ac36bfb692590",
                g0_manifest=prior["g0_manifest"], g0_readout=prior["g0_readout"], views=views, subjects=subjects,
                prior_context=dict(proposal=prior_pin, reply=pin(root, f"{REVIEW}/review-reply.json"), subject_id="N3",
                                   meaning="Already qualified external Foam upper; displayed only for context, not a new question."),
                question_ko="N4와 N5가 각각 어떤 대상을 따라가는지 알려주세요: 외부 Foam 상단 / Foam 내부 변화 / 액체 상단 / 다른 실제 경계 / 구조물 경계 / 반사·광학적 경계 / 위치 근사만 허용 / 판정 불가. 일부 구간만 해당하면 그 범위도 알려주세요. N3는 이미 확인된 기준이므로 다시 답할 필요가 없습니다.",
                precision=prior["precision"], prior_judgments="N1-N3 and all existing source/interval/R-L/A-B replies remain closed; no old guide is snapped or transferred.",
                selection_basis=dict(N4="New same-frame native path below the already qualified N3; possible internal opposition is a question, not a label. Old Y833 guide has no exact center edge and is not reused as truth for Y824.",
                                     N5="New complete native fragment near the earlier agent-observed lower-rim wrong-region context. Its exact physical/optical role still needs human judgment.",
                                     alternatives="Upper-rim fragments 3/24 remain input-unavailable, never negative successes. Central Y852 paths remain unreviewed: no qualified reason to call them internal or structure. Selection was made without any model score."),
                inspected_paths=survey, prospective_context=dict(operation=qualification.CONTEXT, subjects=supports,
                    N3_N4_shared_dependency_pixels=len(used["N3"] & used["N4"]), independent_N3_N4_split_allowed=False),
                exposure="N1/N2 are water; N3/N4/N5 are the same sample4 recording. Two exposed development recordings; zero untouched holdouts. Different sample4 frames are not independent sources.",
                inference_inputs=prior["inference_inputs"], training_authority="Opposition-first preparation adopted. No training, threshold fitting or model installation by this packet; reassess G1 only after scoped replies.",
                model_calls=0, video_decode=False)


def render(root, packet, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    prior = qualification.read_pin(root, packet["prior_context"]["proposal"])
    n3 = next(s for s in prior["subjects"] if s["id"] == "N3")
    fig, axes = plt.subplots(2, 2, figsize=(12, 11.5), dpi=140)
    for i, view in enumerate(packet["views"]):
        with Image.open(g0.pinned_path(root, view["source"])) as image:
            rgb = np.asarray(image.convert("RGB"))
        ox, oy = view["image_origin_xy"]
        x0, y0, x1, y1 = view["display_xyxy"]
        g0.o2.require(ox <= x0 < x1 <= ox+rgb.shape[1] and oy <= y0 < y1 <= oy+rgb.shape[0], "display outside RGB")
        for j, ax in enumerate(axes[i]):
            ax.imshow(rgb[y0-oy:y1-oy, x0-ox:x1-ox], interpolation="nearest", extent=(x0-.5, x1-.5, y1-.5, y0-.5))
            ax.set_title(view["title"]+(" | original pixels" if j == 0 else " | saved paths"), fontsize=12)
            ax.set_xlabel("Source X"); ax.set_ylabel("Source Y")
        for subject in [n3, *packet["subjects"]]:
            if subject["view_id"] != view["id"]:
                continue
            closed = subject["id"] == "N3"
            color = "#00f0ff" if closed else "#ff57e3"
            xy = np.asarray(subject["source_path_xy"])
            g0.o2.require(all(x0 <= x < x1 and y0 <= y < y1 for x, y in xy), "path outside display")
            axes[i, 1].plot(xy[:, 0], xy[:, 1], color=color, linewidth=1.15)
            axes[i, 1].annotate(subject["id"], xy=subject["fixed_column_xy"], xytext=subject["display_label_xy"],
                                fontsize=16, color=color, weight="bold", arrowprops={"arrowstyle": "->", "lw": 1, "color": color})
    fig.suptitle("N4 / N5: what does each highlighted path follow?", fontsize=17, y=.995)
    fig.tight_layout(rect=(0, .045, 1, .975))
    fig.text(.5, .025, "Magenta N4 / N5: new questions. Cyan N3: confirmed external Foam upper, context only.", ha="center", fontsize=11)
    fig.text(.5, .008, "Saved native RGB and exact fragments; nearest-neighbour display. No new physical labels.", ha="center", fontsize=10)
    with output.open("xb") as stream:
        fig.savefig(stream, format="png", metadata={"Software": "Matplotlib; saved RGB and exact native fragments"})
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    g0.o2.require(not any((args.output_dir / n).exists() for n in ["review-proposal.json", "native-opposition-review.png"]), "refuse overwrite")
    packet = build(args.root.resolve())
    g0.o2.write_new(args.output_dir / "review-proposal.json", packet)
    render(args.root.resolve(), packet, args.output_dir / "native-opposition-review.png")
    print(json.dumps(dict(status=packet["status"], subjects=[s["id"] for s in packet["subjects"]],
                         N3_N4_shared_pixels=packet["prospective_context"]["N3_N4_shared_dependency_pixels"], model_calls=0)))
