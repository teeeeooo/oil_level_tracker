"""One frozen Local XY regression run through the real analysis/report owners.

The rectangle is an explicit experiment input, never a production special case.
Reuses canonical public windows; saves complete raw/completed/tracking records.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]

from tests.diagnostics.s11_report_observability_replay import _session, QUALIFICATION_WINDOWS, _tracking_fingerprint
from tests.diagnostics.s11_replay_provenance import capture_runtime_provenance
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.adapters.vision.oil_measurement_scope import OilMeasurementScope
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.services.report_presentation import build_report_presentation
from oil_tracker.domain.geometry import Rect
from oil_tracker.domain.session import DebugTraceLevel


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(value):
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items() if k != 'run_id'}
    if isinstance(value, (list, tuple)):
        return [stable(v) for v in value]
    return value


def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False, default=lambda v: v.value)
        f.write('\n')


class Recorder(OpenCvPhaseDetector):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.raw, self.completed, self.lineage, self.foam = [], [], [], []

    def detect(self, *args, **kwargs):
        detection, artifacts = super().detect(*args, **kwargs)
        self.raw.append(deepcopy(asdict(detection)))
        if artifacts is not None:
            self.lineage.append(artifacts.state['oil_measurement_lineage'])
            self.foam.append(artifacts.state['foam_component_diagnostics'])
        return detection, artifacts

    def resolve_sequence(self, *args, **kwargs):
        resolution = super().resolve_sequence(*args, **kwargs)
        self.completed.extend(deepcopy(asdict(d)) for d in resolution.detections)
        return resolution


def run(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pre = json.loads(args.preflight.read_text(encoding='utf-8'))
    for path, digest in {**pre['inputs'], **pre['source_files']}.items():
        assert sha(ROOT / path) == digest, path
    recipe, session = _session(args.sample, ROOT/'sample'/f'{args.sample}.mp4', out,
        *QUALIFICATION_WINDOWS[args.sample], run_label='Local XY fixed comparison', run_note=args.variant)
    original = recipe.to_dict()
    session.debug_trace_level = DebugTraceLevel[args.level]
    scopes = ()
    if args.variant == 'scoped':
        assert args.sample == 'sample4'  # frozen regression scope, not detector logic
        x0, y0, x1, y1 = pre['rect_source_xyxy']
        scopes = tuple(OilMeasurementScope.bind(g,
            frame_size=(recipe.reference_frame_width, recipe.reference_frame_height),
            reference_sha256=pre['reference_sha256'], rectangles=(Rect(x0,y0,x1-x0,y1-y0),))
            for g in recipe.glasses if g.enabled)
        session.run_note += ' scope=' + ','.join(s.sha256 for s in scopes)
    detector = Recorder(oil_measurement_scopes=scopes)
    started = time.monotonic()
    result = AnalysisPipeline(OpenCvVideoReader, detector, RecipeValidationService(),
        JsonlDebugTraceWriterFactory(out)).run(recipe, session)
    elapsed = time.monotonic()-started
    assert not result.errors, result.errors
    assert recipe.to_dict() == original
    rows = stable([asdict(s) for g in result.glass_results for s in g.samples])
    assert len(rows) == len(detector.raw) == len(detector.completed)
    for name, value in [('raw', detector.raw), ('completed', detector.completed), ('tracking', rows),
                        ('report', stable(asdict(build_report_presentation(result,recipe)))),
                        ('lineage', detector.lineage), ('foam', detector.foam)]:
        save(out/f'{name}.json', value)
    bundle = OutputBundleStore().write_bundle(result, recipe, session, out) if args.level == 'NONE' else None
    for path, digest in {**pre['inputs'], **pre['source_files']}.items():
        assert sha(ROOT / path) == digest, path
    summary = {'sample':args.sample, 'variant':args.variant, 'level':args.level,
        'source_sha256':hashlib.sha256(json.dumps(pre['source_files'],sort_keys=True).encode()).hexdigest(),
        'preflight_sha256':sha(args.preflight), 'runtime':capture_runtime_provenance(ROOT/'sample'/f'{args.sample}.mp4'),
        'detector_version':detector.version, 'scopes':detector.measurement_scope_manifest,
        'rows':len(rows), 'fingerprint':_tracking_fingerprint(result), 'elapsed_sec':elapsed,
        'peak_rss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'numeric_oil':sum(r['raw_oil_air_level_y'] is not None for r in rows),
        'numeric_foam':sum(r['raw_foam_front_y'] is not None for r in rows),
        'valid_oil':sum(r['oil_is_valid'] for r in rows), 'valid_foam':sum(r['foam_is_valid'] for r in rows),
        'report_bundle':str(bundle) if bundle else None, 'inputs_preserved':True,
        'outputs':{p.name:sha(p) for p in sorted(out.glob('*.json'))}}
    save(out/'summary.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('runtime','outputs','scopes')},ensure_ascii=False),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', choices=tuple(QUALIFICATION_WINDOWS), required=True)
    parser.add_argument('--variant', choices=('off','scoped'), required=True)
    parser.add_argument('--level', choices=('NONE','BASIC','FULL'), default='NONE')
    parser.add_argument('--preflight', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args())
