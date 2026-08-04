from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import time

from oil_tracker.adapters.vision.oil_shadow_types import OilShadowBounds
from tests.diagnostics import s11_evidence_probe as evidence_probe
from tests.diagnostics import s11_spatial_path_probe as spatial_probe


BASELINE_MAIN_SHA = "fd3c7baa6cc6f6095343a1da2cdba4375914c799"
TRANSFORM_IDS = (
    "brightness_1.00",
    "brightness_0.60",
    "brightness_0.45",
)


@dataclass(frozen=True)
class InteractionProbeResult:
    case_id: str
    transform: str
    truth_oil_y: float
    p0_oil_y: float | None
    p0_current_kind: str
    p2_oil_y: float | None
    p2_current_kind: str
    spatial_oil_y: float | None
    spatial_route: str
    combined_candidate_oil_y: float | None
    combined_oil_y: float | None
    combined_error_px: float | None
    combined_route: str
    foam_y: float | None
    path: spatial_probe.SpatialPathEvidence | None
    elapsed_ms: float


def run_interaction_variant(
    frame,
    case: evidence_probe.ProbeCase,
    *,
    transform: str = "native",
) -> InteractionProbeResult:
    started = time.perf_counter_ns()
    p0 = evidence_probe.run_variant(frame.copy(), case, "P0")
    p2 = evidence_probe.run_variant(frame.copy(), case, "P2")
    spatial = spatial_probe.run_spatial_variant(frame.copy(), case)
    candidate = None
    path = None
    if p2.oil_y is not None or p2.current_kind != "ambiguous":
        selected = p2
        route = "P2_BASE"
    else:
        candidate = evidence_probe.run_variant(frame.copy(), case, "P3")
        if candidate.oil_y is None:
            selected = p2
            route = "P2_AMBIGUOUS_NO_SPATIAL_CANDIDATE"
        else:
            bundle, pre, foam_mask, _foam_y = spatial_probe._spatial_inputs(frame, case)
            path = spatial_probe.evaluate_spatial_path(
                pre,
                bundle.effective_mask,
                candidate_local_y=float(candidate.oil_y - bundle.crop_origin[1]),
                accepted_foam_component_mask=foam_mask,
                bounds=OilShadowBounds(),
            )
            selected = candidate if path.accepted else p2
            route = "COMBINED_ACCEPTED" if path.accepted else "COMBINED_REJECTED"
    oil_y = selected.oil_y
    return InteractionProbeResult(
        case_id=case.case_id,
        transform=transform,
        truth_oil_y=case.truth_oil_y,
        p0_oil_y=p0.oil_y,
        p0_current_kind=p0.current_kind,
        p2_oil_y=p2.oil_y,
        p2_current_kind=p2.current_kind,
        spatial_oil_y=spatial.oil_y,
        spatial_route=spatial.route,
        combined_candidate_oil_y=None if candidate is None else candidate.oil_y,
        combined_oil_y=oil_y,
        combined_error_px=None if oil_y is None else abs(float(oil_y) - case.truth_oil_y),
        combined_route=route,
        foam_y=selected.foam_y,
        path=path,
        elapsed_ms=(time.perf_counter_ns() - started) / 1_000_000.0,
    )


def run_experiment(root: Path | None = None) -> tuple[InteractionProbeResult, ...]:
    root = evidence_probe.repository_root() if root is None else Path(root)
    specs = {item.name: item for item in evidence_probe.TRANSFORMS}
    decoded = {case.case_id: evidence_probe.decode_frame(case) for case in evidence_probe.load_cases(root)}
    rows = []
    for transform_id in TRANSFORM_IDS:
        spec = specs[transform_id]
        for case in evidence_probe.load_cases(root):
            frame = evidence_probe.transform_frame(decoded[case.case_id], spec)
            rows.append(run_interaction_variant(frame, case, transform=transform_id))
    return tuple(rows)


def _variant_summary(rows, field: str) -> dict[str, object]:
    numeric = [row for row in rows if getattr(row, field) is not None]
    errors = [abs(float(getattr(row, field)) - row.truth_oil_y) for row in numeric]
    return {
        "oil_coverage": len(numeric),
        "oil_mae_px": None if not errors else sum(errors) / len(errors),
    }


def build_manifest(rows: tuple[InteractionProbeResult, ...]) -> dict[str, object]:
    canonical = []
    for row in sorted(rows, key=lambda item: (item.transform, item.case_id)):
        item = asdict(row)
        item.pop("elapsed_ms")
        canonical.append(item)
    fingerprint = sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    aggregate = {}
    for transform_id in TRANSFORM_IDS:
        selected = tuple(row for row in rows if row.transform == transform_id)
        aggregate[transform_id] = {
            "p0": _variant_summary(selected, "p0_oil_y"),
            "p2": _variant_summary(selected, "p2_oil_y"),
            "spatial": _variant_summary(selected, "spatial_oil_y"),
            "combined": _variant_summary(selected, "combined_oil_y"),
            "p2_no_interface_to_ambiguity": [
                row.case_id for row in selected
                if row.p0_current_kind == "no_interface" and row.p2_current_kind == "ambiguous"
            ],
            "combined_only_recovery": [
                row.case_id for row in selected
                if row.spatial_oil_y is None and row.combined_oil_y is not None
            ],
        }
    return {
        "schema": "s11-a-p2-spatial-interaction-probe-v1",
        "baseline_main_sha": BASELINE_MAIN_SHA,
        "mechanism": "p2-ambiguity-then-existing-relative-candidate-and-five-sector-spatial-gate",
        "result_fingerprint_sha256": fingerprint,
        "transforms": list(TRANSFORM_IDS),
        "aggregate": aggregate,
        "resource_bound": {
            "maximum_path_sector_row_evaluations": 5 * (2 * OilShadowBounds().narrow_lobe_search_radius_px + 1),
            "retained_temporal_state": 0,
            "new_dependencies": 0,
        },
        "rows": canonical,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the S11-A P2 x Spatial interaction probe.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = build_manifest(run_experiment())
    encoded = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(encoded, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
        print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
