"""Bounded public-window equality/resource audit for trace-only witness changes.

Reuses the existing qualification sessions, pipeline, fingerprint and provenance
owners. Unlike the timing-only profiler, records every raw/completed detection
and old diagnostic hash for NONE/BASIC/FULL comparisons. Run serially, one fresh
process per sample/mode. Only the requested summary persists; generated bundles
are held in an owned TemporaryDirectory and removed after hashing.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import time
from unittest.mock import patch


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def run(root: Path, output: Path, sample: str, level: str, debug_copy_mode: str = "copy") -> dict:
    # Allows a separate immutable baseline archive with the same installed deps.
    sys.path[:0] = [str(root / "src"), str(root)]
    from tests.diagnostics.s11_report_observability_replay import _session, QUALIFICATION_WINDOWS, _tracking_fingerprint
    from tests.diagnostics.s11_replay_provenance import validate_frozen_inputs, capture_runtime_provenance
    from tests.diagnostics.s11_evidence_probe import authoritative_input_hashes
    from tests.diagnostics.s11_resolver_replacement_profile import peak_rss
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.domain.session import DebugTraceLevel

    class AuditDetector(OpenCvPhaseDetector):
        def __init__(self):
            super().__init__()
            self.raw, self.completed, self.old, self.witness = [], [], [], []

        def detect(self, *args, **kwargs):
            detection, artifacts = super().detect(*args, **kwargs)
            self.raw.append(_digest(asdict(detection)))
            if artifacts:
                self.old.append(_digest(artifacts.state["oil_interface_diagnostics"]))
                witness = artifacts.state.get("oil_interface_witness")
                self.witness.append(len(json.dumps(witness, allow_nan=False)) if witness else 0)
            return detection, artifacts

        def resolve_sequence(self, *args, **kwargs):
            result = super().resolve_sequence(*args, **kwargs)
            self.completed.extend(_digest(asdict(d)) for d in result.detections)
            return result

    source_files = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted((root / "src").rglob("*.py"))}
    inputs = validate_frozen_inputs(root=root, expected_inputs=authoritative_input_hashes(root), samples=(sample,))
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="oil-o1-replay-", dir=output.parent) as directory:
        work = Path(directory)
        recipe, session = _session(sample, root / "sample" / f"{sample}.mp4", work,
            *QUALIFICATION_WINDOWS[sample], run_label="O1 equality", run_note="same runtime")
        session.debug_trace_level = DebugTraceLevel(level)
        detector = AuditDetector()
        start = time.perf_counter()
        result = AnalysisPipeline(lambda p: OpenCvVideoReader(p), detector,
            RecipeValidationService(), JsonlDebugTraceWriterFactory(work)).run(recipe, session)
        original_copy = shutil.copy2

        def copy_debug_file(source, destination, **kwargs):
            # Finalized debug staging is immutable. Link only this run's owned
            # staging files; never modify application storage or user bundles.
            relative = Path(source).relative_to(work) if Path(source).is_relative_to(work) else None
            if debug_copy_mode == "hardlink" and relative and relative.parts[0].startswith("oil-debug-trace-"):
                os.link(source, destination)
                return destination
            return original_copy(source, destination, **kwargs)

        with patch("oil_tracker.adapters.storage.output_bundle_store.shutil.copy2", copy_debug_file):
            bundle = OutputBundleStore().write_bundle(result, recipe, session, work)
        summary = {
            "schema_version": "s11-o1-window-equality-v1", "sample": sample, "level": level,
            "debug_copy_mode": debug_copy_mode,
            "version": detector.version, "elapsed_seconds": time.perf_counter() - start,
            "peak_rss": peak_rss(),
            "runtime": capture_runtime_provenance(root / "sample" / f"{sample}.mp4"),
            "inputs": inputs, "source_files": source_files, "source_sha256": _digest(source_files),
            "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "fingerprint": _tracking_fingerprint(result), "raw": detector.raw,
            "completed": detector.completed, "old_diagnostics": detector.old,
            "witness_bytes": detector.witness,
            "trace_bytes": sum(p.stat().st_size for p in bundle.rglob("debug_trace.jsonl")),
        }
        for name in ("tracking_data.csv", "events.csv"):
            with (bundle / name).open(encoding="utf-8-sig", newline="") as handle:
                summary[name] = [{k: v for k, v in row.items() if k != "run_id"}
                                 for row in csv.DictReader(handle)]
    output.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample", choices=("base_sample_1", "sample2", "sample3", "sample4"), required=True)
    parser.add_argument("--debug-level", choices=("none", "basic", "full"), required=True)
    parser.add_argument("--debug-copy-mode", choices=("copy", "hardlink"), default="copy",
                        help="Audit-only disk-saving links for immutable owned staging; changes bundle I/O timing.")
    args = parser.parse_args()
    result = run(args.root.resolve(), args.output.resolve(), args.sample, args.debug_level, args.debug_copy_mode)
    print(args.sample, args.debug_level, result["elapsed_seconds"], result["trace_bytes"], flush=True)


if __name__ == "__main__":
    main()
