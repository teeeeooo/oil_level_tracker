"""Frozen public-source linkage through the existing application pipeline.

The existing replay CLI binds old sample recipes/windows. This adapter supplies
the pinned new-source fixture; Recorder, pipeline, report and CSV owners are reused.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--level', choices=('NONE', 'FULL'), required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output.resolve()
    preflight = Path(__file__).with_name('pipeline-preflight.json')
    pre = json.loads(preflight.read_text())
    baseline = json.loads((root / pre['production_manifest']).read_text())
    pins = {**baseline['source_files'], **pre['inputs']}
    assert all(sha(root / p) == h for p, h in pins.items())
    assert sha(__file__) == pre['runner_sha256']
    out.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(root / 'src'), str(root)]

    from tests.diagnostics.s11_local_xy_replay import Recorder, save, stable
    from tests.diagnostics.s11_replay_provenance import capture_runtime_provenance
    from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.reporting.csv_exporter import CsvExporter
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline, timestamp_schedule
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.application.services.report_presentation import build_report_presentation
    from oil_tracker.domain.enums import InitialObservationState, JudgmentMode
    from oil_tracker.domain.geometry import EllipseGeometry, GlassGeometry
    from oil_tracker.domain.recipe import GlassInspectionConfig, InspectionRecipe, JudgmentRule
    from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel, InitialStateConfirmation

    source = root / pre['source']['local_path']
    runtime = capture_runtime_provenance(source)
    with OpenCvVideoReader(source) as reader:
        metadata = reader.metadata
    decoded = []

    class AuditedReader(OpenCvVideoReader):
        def read_at(self, timestamp_sec):
            frame, index, actual = super().read_at(timestamp_sec)
            decoded.append({'requested_sec': timestamp_sec, 'frame_index': index,
                            'timestamp_sec': actual,
                            'bgr_sha256': hashlib.sha256(frame.tobytes()).hexdigest()})
            return frame, index, actual

    g = pre['geometry']
    glass = GlassInspectionConfig(id=pre['glass_id'], name='Public source linkage fixture',
        geometry=GlassGeometry(EllipseGeometry(*g['ellipse_center_xy'], *g['ellipse_radii_xy']),
                               zero_line_y=g['zero_line_y'], margin_ratio=g['margin_ratio']),
        initial_state=InitialObservationState.UNKNOWN_REVIEW,
        judgment_rule=JudgmentRule(mode=JudgmentMode.HOLD_BELOW_ZERO))
    recipe = InspectionRecipe(name='Public source linkage fixture',
        reference_frame_width=1280, reference_frame_height=720, glasses=[glass],
        recipe_id=pre['recipe_id'], created_at=pre['fixture_date'], updated_at=pre['fixture_date'])
    session = AnalysisSession(input_video_path=str(source), video_metadata=metadata,
        analysis_start_sec=pre['window']['start_sec'], analysis_end_sec=pre['window']['end_sec'],
        sampling_fps=pre['window']['sampling_fps'], output_directory=str(out),
        run_name='Public source bounded pipeline linkage', run_note=pre['fixture_scope'],
        debug_trace_level=DebugTraceLevel[args.level])
    session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
        glass.initial_state, session.input_video_path, session.analysis_start_sec)
    assert timestamp_schedule(session.analysis_start_sec, session.analysis_end_sec,
                              session.sampling_fps) == pre['window']['requested_times']
    original = recipe.to_dict()
    save(out / 'recipe.json', original)
    save(out / 'session.json', session.to_dict())
    detector = Recorder()
    started = time.monotonic()
    result = AnalysisPipeline(AuditedReader, detector, RecipeValidationService(),
        JsonlDebugTraceWriterFactory(out)).run(recipe, session)
    assert not result.errors, result.errors
    assert recipe.to_dict() == original and not detector.measurement_scope_manifest
    rows = stable([asdict(s) for gr in result.glass_results for s in gr.samples])
    assert len(rows) == len(detector.raw) == len(detector.completed) == 3
    for name, value in [('raw', detector.raw), ('completed', detector.completed),
                        ('tracking', rows), ('lineage', detector.lineage), ('foam', detector.foam),
                        ('report', stable(asdict(build_report_presentation(result, recipe))))]:
        save(out / f'{name}.json', value)
    CsvExporter().export(result, out / 'tracking.csv', out / 'events.csv')
    save(out / 'decodes.json', decoded)
    expected = pre['window']['expected_decodes']
    assert len(decoded) == len(expected) * 2
    for actual, wanted in zip(decoded, expected * 2):
        assert actual['frame_index'] == wanted['frame_index']
        assert actual['bgr_sha256'] == wanted['bgr_sha256']
        assert abs(actual['timestamp_sec'] - wanted['timestamp_sec']) < 1e-9
    elapsed = time.monotonic() - started
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = rss if sys.platform == 'darwin' else rss * 1024
    assert all(sha(root / p) == h for p, h in pins.items())
    summary = {
        'schema': 's11-public-source-pipeline-run-v1', 'level': args.level,
        'execution_head': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
        'preflight_sha256': sha(preflight), 'runner_sha256': sha(__file__),
        'runtime': runtime, 'detector_version': detector.version,
        'rows': len(rows), 'decodes': len(decoded), 'production_files_unchanged': len(baseline['source_files']),
        'recipe_preserved': True, 'pins_preserved': True,
        'resources': {'elapsed_sec': elapsed, 'peak_rss_bytes': rss_bytes,
                      'within_bounds': elapsed <= pre['resource']['seconds_limit']
                      and rss_bytes <= pre['resource']['rss_bytes_limit']},
        'outputs': {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file()},
    }
    save(out / 'summary.json', summary)
    assert summary['resources']['within_bounds']
    print(json.dumps({k: summary[k] for k in ('level', 'rows', 'decodes', 'resources')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
