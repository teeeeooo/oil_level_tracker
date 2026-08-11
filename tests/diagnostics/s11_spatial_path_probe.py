from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import time

import numpy as np

from oil_tracker.adapters.vision import oil_shadow_observations as observations
from oil_tracker.adapters.vision.foam_front_detector import (
    detect_bottom_connected_foam,
    evaluate_foam_layer_coherence,
)
from oil_tracker.adapters.vision.foam_temporal_gate import FoamStaticMatch, FoamTemporalGate
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_shadow_types import OilShadowBounds
from oil_tracker.adapters.vision.preprocessing import preprocess
from tests.diagnostics import s11_evidence_probe as prior_probe


BASELINE_MAIN_SHA = "3305cb8268fd4e1612105cba6144c2083066ff8c"
SECTOR_COUNT = 5


@dataclass(frozen=True)
class SpatialPathEvidence:
    accepted: bool
    reason: str
    candidate_local_y: float
    path_sector_count: int
    path_sector_indices: tuple[int, ...]
    path_rows: tuple[int, ...]
    phase_sign: int
    path_span_px: int
    maximum_adjacent_jump_px: int
    path_median_local_y: float | None
    candidate_alignment_px: float | None


@dataclass(frozen=True)
class SpatialProbeResult:
    case_id: str
    truth_oil_y: float
    p0_oil_y: float | None
    p0_current_kind: str
    candidate_oil_y: float | None
    oil_y: float | None
    oil_error_px: float | None
    foam_y: float | None
    route: str
    path: SpatialPathEvidence | None
    elapsed_ms: float


def _spatial_inputs(frame: np.ndarray, case: prior_probe.ProbeCase):
    bundle = build_mask_bundle(frame, case.glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, case.glass.detector_settings)
    foam = detect_bottom_connected_foam(
        bundle.crop,
        pre.gray,
        pre.canny,
        pre.glare_mask,
        bundle.effective_mask,
        case.glass.detector_settings,
    )
    foam_temporal = FoamTemporalGate().evaluate(
        case.glass.id,
        foam,
        case.glass.detector_settings,
    )
    foam_candidate = prior_probe._historical_foam_oil_constraint_candidate(
        foam,
        foam_temporal,
        layer_coherent=evaluate_foam_layer_coherence(foam).coherent,
        static_match=FoamStaticMatch(),
    )
    foam_mask = None if foam_candidate is None else foam.mask
    foam_y = (
        None
        if foam_temporal.candidate is None
        else float(foam_temporal.candidate.y + bundle.crop_origin[1])
    )
    return bundle, pre, foam_mask, foam_y


def _best_sector_phase(
    pre,
    visible: np.ndarray,
    residual: np.ndarray,
    *,
    center: float,
    first_column: int,
    last_column: int,
    depth: int,
    gap: int,
    radius: int,
) -> tuple[int, int, bool, float] | None:
    height = visible.shape[0]
    quantization = observations._gray_quantization_step(pre.blurred)
    gray_scale = observations._gray_scale(pre.blurred)
    best = None
    for row in range(
        max(depth + gap, int(round(center)) - radius),
        min(height - depth - gap, int(round(center)) + radius + 1),
    ):
        top = observations._robust_sector_phase(
            pre.blurred,
            visible,
            residual,
            range(row - gap - depth, row - gap),
            first_column,
            last_column,
        )
        bottom = observations._robust_sector_phase(
            pre.blurred,
            visible,
            residual,
            range(row + gap, row + gap + depth),
            first_column,
            last_column,
        )
        if top is None or bottom is None:
            continue
        top_median, top_mad = top
        bottom_median, bottom_mad = bottom
        contrast = (top_median - bottom_median) / gray_scale
        noise = max(top_mad, bottom_mad, quantization) / gray_scale
        strength = abs(contrast) / max(noise, 1e-12)
        key = (-strength, abs(float(row) - center), row)
        if best is None or key < best[0]:
            sign = 1 if contrast > 0.0 else -1
            strong = abs(contrast) > noise and abs(contrast) > quantization / gray_scale
            best = (key, row, sign, strong, strength)
    if best is None:
        return None
    _key, row, sign, strong, strength = best
    return int(row), int(sign), bool(strong), float(strength)


def evaluate_spatial_path(
    pre,
    effective_mask: np.ndarray,
    *,
    candidate_local_y: float,
    accepted_foam_component_mask: np.ndarray | None,
    bounds: OilShadowBounds,
) -> SpatialPathEvidence:
    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    residual = (
        visible
        if accepted_foam_component_mask is None
        else visible & ~(accepted_foam_component_mask > 0)
    )
    columns = np.flatnonzero(np.any(effective, axis=0))
    depth = max(bounds.broad_band_scales)
    gap = max(2, int(round(bounds.maximum_proposal_diameter_px / 2.0)))
    center = float(candidate_local_y)
    height = effective.shape[0]
    if columns.size < SECTOR_COUNT:
        return _rejected_path(center, "insufficient_cross_roi_support")
    if center < depth + gap or center >= height - depth - gap:
        return _rejected_path(center, "candidate_lacks_symmetric_phase_window")
    edges = np.linspace(int(columns[0]), int(columns[-1]) + 1, SECTOR_COUNT + 1, dtype=int)
    records: list[tuple[int, int, int, bool, float]] = []
    for sector in range(SECTOR_COUNT):
        value = _best_sector_phase(
            pre,
            visible,
            residual,
            center=center,
            first_column=int(edges[sector]),
            last_column=int(edges[sector + 1]),
            depth=depth,
            gap=gap,
            radius=bounds.narrow_lobe_search_radius_px,
        )
        if value is not None:
            row, sign, strong, strength = value
            records.append((sector, row, sign, strong, strength))

    best_run: list[tuple[int, int, int, bool, float]] = []
    for sign in (-1, 1):
        current: list[tuple[int, int, int, bool, float]] = []
        for record in records:
            sector, _row, record_sign, strong, _strength = record
            if record_sign == sign and strong:
                if current and sector != current[-1][0] + 1:
                    current = []
                current.append(record)
                if _path_run_key(current, center) < _path_run_key(best_run, center):
                    best_run = list(current)
            else:
                current = []

    if not best_run:
        return _rejected_path(center, "no_contiguous_strong_phase_path")
    path_rows = tuple(record[1] for record in best_run)
    path_sectors = tuple(record[0] for record in best_run)
    path_span = max(path_rows) - min(path_rows)
    jumps = tuple(abs(path_rows[index + 1] - path_rows[index]) for index in range(len(path_rows) - 1))
    maximum_jump = max(jumps, default=0)
    path_median = float(np.median(path_rows))
    alignment = abs(path_median - center)
    minimum_sector_count = SECTOR_COUNT // 2 + 1
    maximum_jump_limit = 2.0 * bounds.maximum_proposal_diameter_px
    if len(best_run) < minimum_sector_count:
        reason = "insufficient_contiguous_cross_roi_support"
        accepted = False
    elif path_span <= 1:
        reason = "degenerate_scalar_row"
        accepted = False
    elif maximum_jump > maximum_jump_limit:
        reason = "spatial_path_jump_exceeds_bound"
        accepted = False
    elif alignment > bounds.narrow_lobe_search_radius_px:
        reason = "spatial_path_not_aligned_with_candidate"
        accepted = False
    else:
        reason = "nondegenerate_cross_roi_phase_path"
        accepted = True
    return SpatialPathEvidence(
        accepted=accepted,
        reason=reason,
        candidate_local_y=center,
        path_sector_count=len(best_run),
        path_sector_indices=path_sectors,
        path_rows=path_rows,
        phase_sign=int(best_run[0][2]),
        path_span_px=int(path_span),
        maximum_adjacent_jump_px=int(maximum_jump),
        path_median_local_y=path_median,
        candidate_alignment_px=float(alignment),
    )


def _path_run_key(records, center: float) -> tuple[float, ...]:
    if not records:
        return (float("inf"), float("inf"), float("inf"), float("inf"))
    rows = tuple(record[1] for record in records)
    jumps = tuple(abs(rows[index + 1] - rows[index]) for index in range(len(rows) - 1))
    return (
        -float(len(records)),
        float(max(jumps, default=0)),
        abs(float(np.median(rows)) - center),
        float(records[0][0]),
    )


def _rejected_path(center: float, reason: str) -> SpatialPathEvidence:
    return SpatialPathEvidence(
        accepted=False,
        reason=reason,
        candidate_local_y=float(center),
        path_sector_count=0,
        path_sector_indices=(),
        path_rows=(),
        phase_sign=0,
        path_span_px=0,
        maximum_adjacent_jump_px=0,
        path_median_local_y=None,
        candidate_alignment_px=None,
    )


def run_spatial_variant(frame: np.ndarray, case: prior_probe.ProbeCase) -> SpatialProbeResult:
    started = time.perf_counter_ns()
    p0 = prior_probe.run_variant(frame.copy(), case, "P0")
    if p0.oil_y is not None or p0.current_kind != "ambiguous":
        return _result(case, p0, None, p0, "P0", None, started)

    relative = prior_probe.run_variant(frame.copy(), case, "P1")
    if relative.oil_y is None:
        return _result(case, p0, None, p0, "P0_FAIL_CLOSED", None, started)
    bundle, pre, foam_mask, _foam_y = _spatial_inputs(frame, case)
    path = evaluate_spatial_path(
        pre,
        bundle.effective_mask,
        candidate_local_y=float(relative.oil_y - bundle.crop_origin[1]),
        accepted_foam_component_mask=foam_mask,
        bounds=OilShadowBounds(),
    )
    if not path.accepted:
        return _result(case, p0, relative, p0, "SPATIAL_REJECTED", path, started)
    return _result(case, p0, relative, relative, "SPATIAL_ACCEPTED", path, started)


def _result(
    case: prior_probe.ProbeCase,
    p0,
    candidate,
    selected,
    route: str,
    path: SpatialPathEvidence | None,
    started_ns: int,
) -> SpatialProbeResult:
    oil_y = selected.oil_y
    return SpatialProbeResult(
        case_id=case.case_id,
        truth_oil_y=case.truth_oil_y,
        p0_oil_y=p0.oil_y,
        p0_current_kind=p0.current_kind,
        candidate_oil_y=None if candidate is None else candidate.oil_y,
        oil_y=oil_y,
        oil_error_px=None if oil_y is None else abs(float(oil_y) - case.truth_oil_y),
        foam_y=selected.foam_y,
        route=route,
        path=path,
        elapsed_ms=(time.perf_counter_ns() - started_ns) / 1_000_000.0,
    )


def run_native_experiment(root: Path | None = None) -> tuple[SpatialProbeResult, ...]:
    root = prior_probe.repository_root() if root is None else Path(root)
    rows = []
    for case in prior_probe.load_cases(root):
        rows.append(run_spatial_variant(prior_probe.decode_frame(case), case))
    return tuple(rows)


def build_manifest(rows: tuple[SpatialProbeResult, ...]) -> dict[str, object]:
    canonical = []
    for row in sorted(rows, key=lambda item: item.case_id):
        item = asdict(row)
        item.pop("elapsed_ms")
        canonical.append(item)
    numeric = [row for row in rows if row.oil_y is not None]
    errors = [row.oil_error_px for row in numeric if row.oil_error_px is not None]
    recovered = [row.case_id for row in rows if row.p0_oil_y is None and row.oil_y is not None]
    fingerprint = sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema": "s11-a-spatial-path-probe-v1",
        "baseline_main_sha": BASELINE_MAIN_SHA,
        "mechanism": "five-sector-nondegenerate-relative-phase-path-gate",
        "result_fingerprint_sha256": fingerprint,
        "native": {
            "case_count": len(rows),
            "oil_coverage": len(numeric),
            "oil_mae_px": None if not errors else sum(errors) / len(errors),
            "recovered_case_ids": recovered,
            "maximum_path_sector_row_evaluations": SECTOR_COUNT * (2 * OilShadowBounds().narrow_lobe_search_radius_px + 1),
            "retained_temporal_state": 0,
        },
        "rows": canonical,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the S11-A cross-ROI spatial path probe.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = build_manifest(run_native_experiment())
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
