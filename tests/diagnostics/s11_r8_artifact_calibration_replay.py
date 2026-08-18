from __future__ import annotations

"""Replay sample4 after selecting one detector-proposed artifact like the ROI UI."""

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path

from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.vision.artifact_calibration import template_from_candidate
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_observation_replay_audit import (
    provisional_audit,
    sequence_audit,
    tracking_rows,
    user_truth_audit,
)
from tests.diagnostics import s11_report_observability_replay as replay


def detector_proposals(frame, glass, frame_index: int, time_sec: float):
    detector_glass = deepcopy(glass)
    detector_glass.geometry.artifact_templates.clear()
    detection, _artifacts = OpenCvPhaseDetector().detect(
        frame,
        detector_glass,
        frame_index,
        time_sec,
        debug=True,
    )
    proposals = []
    candidates = sorted(
        detection.candidates,
        key=lambda candidate: (-float(candidate.final_score), float(candidate.y)),
    )
    for candidate in candidates:
        if not math.isfinite(float(candidate.y)):
            continue
        template = template_from_candidate(
            candidate,
            name=f"경계 후보 {len(proposals) + 1}",
        )
        if template is None or any(
            abs(template.center_y - existing[1].center_y) <= 0.025
            and abs(template.center_x - existing[1].center_x) <= 0.08
            for existing in proposals
        ):
            continue
        proposals.append((candidate, template))
        if len(proposals) >= 10:
            break
    return proposals


def run(
    *,
    root: Path,
    output_root: Path,
    proposal_index: int,
    proposal_time_sec: float = 3.0,
    run_label: str = "S11-R8-CAL",
    run_note: str = "User-selected detector artifact proposal replay",
    minimum_numeric_reference: int = 76,
    allow_public_foam: bool = False,
) -> dict[str, object]:
    sample = "sample4"
    video = root / "sample" / f"{sample}.mp4"
    recipe, session = replay._session(
        sample,
        video,
        output_root,
        *replay.QUALIFICATION_WINDOWS[sample],
        run_label=run_label,
        run_note=run_note,
    )
    glass = next(item for item in recipe.glasses if item.enabled)
    reader = OpenCvVideoReader(video)
    try:
        frame, frame_index, actual_time = reader.read_at(proposal_time_sec)
    finally:
        reader.close()
    proposals = detector_proposals(frame, glass, frame_index, actual_time)
    if not 0 <= proposal_index < len(proposals):
        raise IndexError(
            f"proposal index {proposal_index} outside 0..{len(proposals) - 1}"
        )
    candidate, template = proposals[proposal_index]
    glass.geometry.artifact_templates.append(template)
    result = AnalysisPipeline(
        lambda path: OpenCvVideoReader(path),
        OpenCvPhaseDetector(),
        RecipeValidationService(),
    ).run(recipe, session)
    bundle = OutputBundleStore().write_bundle(
        result,
        recipe,
        session,
        output_root,
    )
    rows = tracking_rows(bundle)
    payload = {
        "schema": "s11-r8-artifact-calibration-replay-v1",
        "sample": sample,
        "proposal_time_sec": proposal_time_sec,
        "selected_proposal_index": proposal_index,
        "selected_candidate": {
            "source": candidate.source,
            "kind": candidate.kind.value,
            "source_y": candidate.y,
            "final_score": candidate.final_score,
        },
        "selected_template": template.__dict__,
        "proposal_count": len(proposals),
        "summary": replay._sample_summary(sample, result, recipe, bundle),
        "sequence": sequence_audit(rows),
        "user_truth": user_truth_audit(root, sample, rows),
        "provisional_visual": provisional_audit(root, sample, rows),
        "uncalibrated_r8_numeric_reference": 76,
    }
    if payload["sequence"]["numeric_count"] < minimum_numeric_reference:
        raise AssertionError("Selected artifact reduced sample4 Oil coverage")
    if payload["sequence"]["foam_numeric_count"] and not allow_public_foam:
        raise AssertionError("Selected artifact introduced public Foam")
    if payload["sequence"]["numeric_without_same_frame_provenance"]:
        raise AssertionError("Selected artifact introduced unprovenanced Oil")
    output_root.mkdir(parents=True, exist_ok=True)
    manifest = output_root / "artifact_calibration_manifest.json"
    manifest.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r8-artifact-calibration"),
    )
    parser.add_argument("--proposal-index", type=int, required=True)
    parser.add_argument("--proposal-time-sec", type=float, default=3.0)
    args = parser.parse_args()
    payload = run(
        root=repository_root() if args.root is None else args.root,
        output_root=args.output_root.resolve(),
        proposal_index=args.proposal_index,
        proposal_time_sec=args.proposal_time_sec,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
