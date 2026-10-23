"""FFF-1 local cause check: does a per-sample move above the tracklet association cap stop level admission?

Two arms move the local fills past the cap that SPL#4's fast rise exceeds (about 70 px per sample
against 32 px): a lower sampling rate (session setting), and the 2 fps run with only the tracklet
association cap narrowed. Diagnostics only; the detector, Recipes and every other policy are unchanged.
Use a managed experiment's work directory.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict, replace
import gzip
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time

ROOT = Path(__file__).resolve().parents[2]
ROI_INPUTS = ROOT / "sample/output/s11-empty-fill-roi-20261022-001/evidence/inputs"
FOA_RUN = ROOT / "sample/output/s11-fill-owner-readout-20261022-001/evidence"
NEAR_LEVEL_PX = 32.0  # FOA-1's distance unit: one association jump at the Recipe value
# Rising windows with an agent surface estimate (FOA-1 surface-estimates.json).
RISING_WINDOWS = {"sample5": (10.0, 18.0), "sample7": (9.5, 21.0)}
# arm -> (sampling fps, tracklet association cap in px or None for the Recipe value)
ARMS = {
    "baseline": (2.0, None),
    "fps0.5": (0.5, None),
    "fps1": (1.0, None),
    "cap9": (2.0, 9.0),
}


def surface_at(estimates: list[dict], t: float) -> float | None:
    """Linear interpolation of the agent estimates; None outside their span."""
    points = sorted((float(e["t"]), float(e["y"])) for e in estimates)
    if not points or t < points[0][0] or t > points[-1][0]:
        return None
    for (t0, y0), (t1, y1) in zip(points, points[1:]):
        if t0 <= t <= t1:
            return y0 if t1 == t0 else y0 + (y1 - y0) * (t - t0) / (t1 - t0)
    return points[-1][1]


def readings(readout: list[dict], times: list[float], estimates: list[dict], window: tuple[float, float]) -> dict:
    """Frozen readings over the rising window: admitted-level share L, net-progress frames and FOA-1's M3."""
    frames, admitted, unadmitted_only, net_progress, reasons = 0, 0, 0, 0, Counter()
    published = []
    ambiguous = 0
    for frame, t in zip(readout, times, strict=True):
        if not window[0] <= t <= window[1]:
            continue
        surface = surface_at(estimates, t)
        if surface is None:
            continue
        frames += 1
        ambiguous += frame["reason"] == "FILL_OWNER_AMBIGUOUS"
        near = [c for c in frame["oil_candidates"] if abs(c["y"] - surface) <= NEAR_LEVEL_PX]
        if any(c["sequence_tracklet_admitted"] for c in near):
            admitted += 1
        elif near:
            unadmitted_only += 1
            frame_reasons = [c["sequence_tracklet_failure_reason"] for c in near
                             if c["sequence_tracklet_failure_reason"]]
            reasons.update(frame_reasons)
            net_progress += "INSUFFICIENT_NET_PROGRESS" in frame_reasons
        if frame["published_oil_y"] is not None:
            published.append(round(frame["published_oil_y"] - surface, 1))
    commonest = reasons.most_common(1)[0][0] if reasons else None
    return dict(
        frames=frames,
        level_admitted_frames=admitted,
        level_admitted_share=round(admitted / frames, 3) if frames else None,
        near_level_unadmitted_only_frames=unadmitted_only,
        net_progress_frames=net_progress,
        unadmitted_reasons=dict(reasons),
        m3_holds=bool(frames) and unadmitted_only * 2 >= frames and commonest == "INSUFFICIENT_NET_PROGRESS",
        fill_owner_ambiguous_frames=ambiguous,
        published_offsets_px=published,
    )


@contextmanager
def association_cap(cap: float | None):
    """Narrow only the tracklet association cap; row tolerance and every other policy keep the Recipe value."""
    from oil_tracker.adapters.vision import oil_observation_resolver as resolver

    if cap is None:
        yield
        return
    original = resolver._tracklet_policy

    def narrowed(*args, **kwargs):
        return replace(original(*args, **kwargs), maximum_jump_px=cap)

    resolver._tracklet_policy = narrowed
    try:
        yield
    finally:
        resolver._tracklet_policy = original


def run_arm(sample: str, arm: str, work: Path, *, fast_rise: bool = False) -> dict:
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.enums import InitialObservationState
    from oil_tracker.domain.session import InitialStateConfirmation
    from tests.diagnostics.s11_initial_full_comparison import EMPTY_FILL_CONTROLS, _owner_readout
    from tests.diagnostics.s11_local_xy_replay import Recorder, stable
    from tests.diagnostics.s11_report_observability_replay import _session

    fps, cap = ARMS[arm]
    video = ROOT / "sample" / f"{sample}.mp4"
    recipe_path = ROI_INPUTS / f"{sample}.oilrecipe"
    frozen = json.loads((ROI_INPUTS / "roi-inputs.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(recipe_path.read_bytes()).hexdigest() == frozen["recipes"][sample]["comparison_recipe_sha256"]
    with TemporaryDirectory(prefix=f"{sample}-{arm}-", dir=work) as scratch:
        _, session = _session(sample, video, Path(scratch), *EMPTY_FILL_CONTROLS[sample]["window"],
                              run_label="FFF-1 cause check", run_note=arm, recipe_path=recipe_path)
        session.sampling_fps = fps
        recipe = JsonRecipeRepository().load(recipe_path)
        for glass in recipe.glasses:
            glass.initial_state = InitialObservationState.EMPTY_NO_INTERFACE
            session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
                InitialObservationState.EMPTY_NO_INTERFACE, str(video), session.analysis_start_sec)
        # FOA-1's top_exit arm: the integrated candidate (IFO v2 + top-exit v3).
        detector = Recorder(initial_full_observation=True, top_exit_full=True, fast_rise_association=fast_rise)
        started = time.monotonic()
        with association_cap(cap):
            result = AnalysisPipeline(OpenCvVideoReader, detector, RecipeValidationService(), None).run(recipe, session)
        assert not result.errors, result.errors
        rows = stable([asdict(s) for g in result.glass_results for s in g.samples])
    return dict(sample=sample, arm=arm, fast_rise_association=fast_rise, sampling_fps=fps, association_cap_px=cap,
                analysis_seconds=round(time.monotonic() - started, 1),
                detector_version=detector.version, rows=rows,
                owner_readout=[_owner_readout(d) for d in detector.completed],
                fast_rise_seed_frames=sorted({frame for d in detector.completed
                                              for frame in d["debug_metrics"].get("sequence_fast_rise_seed_frames") or ()}))


def foa_baseline(sample: str) -> dict:
    with gzip.open(FOA_RUN / sample / "comparison.json.gz", "rt", encoding="utf-8") as stream:
        return json.load(stream)["variants"]["top_exit"]


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--sample", choices=tuple(RISING_WINDOWS), required=True)
    parser.add_argument("--arm", choices=tuple(ARMS), required=True)
    parser.add_argument("--fast-rise", action="store_true", help="the frozen fast-rise association checks F2-F4")
    args = parser.parse_args(argv)
    args.work.mkdir(parents=True, exist_ok=True)
    out = run_arm(args.sample, args.arm, args.work, fast_rise=args.fast_rise)
    if args.arm == "baseline" and not args.fast_rise:
        kept = foa_baseline(args.sample)
        out["identity_rows_equal_foa"] = out["rows"] == kept["rows"]
        out["identity_readout_equal_foa"] = out["owner_readout"] == kept.get("owner_readout")
    estimates = json.loads((FOA_RUN / "surface-estimates.json").read_text(encoding="utf-8"))[args.sample]["estimates"]
    times = [row["timestamp_sec"] for row in out["rows"]]
    out["readings"] = readings(out["owner_readout"], times, estimates, RISING_WINDOWS[args.sample])
    target = args.work / f"fff-{args.sample}-{args.arm}{'-fastrise' if args.fast_rise else ''}.json.gz"
    payload = json.dumps(out, ensure_ascii=False, allow_nan=False, default=str).encode("utf-8")
    target.write_bytes(gzip.compress(payload, mtime=0))  # mtime 0: the hash depends on the content only
    summary = {k: out[k] for k in ("sample", "arm", "fast_rise_association", "sampling_fps", "association_cap_px",
                                   "analysis_seconds", "fast_rise_seed_frames")}
    summary |= {k: out[k] for k in ("identity_rows_equal_foa", "identity_readout_equal_foa") if k in out}
    summary |= dict(rows=len(out["rows"]), numeric_oil=sum(r["raw_oil_air_level_y"] is not None for r in out["rows"]),
                    readings={k: v for k, v in out["readings"].items() if k != "published_offsets_px"},
                    sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
