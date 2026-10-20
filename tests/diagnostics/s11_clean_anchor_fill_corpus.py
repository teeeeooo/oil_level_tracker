"""CAF-1 stage 2: ordinary vs clean-anchor fill on local whole-video windows.

Runs full extraction and completed analysis through the ordinary pipeline for
recordings with a stored Recipe (sample3 stays quarantined; sample4 is stage 1).
Not a promoted production policy.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import subprocess

from oil_tracker.adapters.reporting.csv_exporter import CsvExporter
from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.services.report_presentation import build_report_presentation
from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_clean_anchor_fill import clean_anchor
from tests.diagnostics import s11_role_consumer_intervention as rci

SAMPLES = ('base_sample_1', 'sample2')


def _analyze(root, sample, output):
    start, end = replay.QUALIFICATION_WINDOWS[sample]
    video = root / 'sample' / f'{sample}.mp4'
    recipe, session = replay._session(sample, video, output, start, end,
                                      run_label='CAF-1', run_note='CAF-1 stage 2 diagnostic')
    result = AnalysisPipeline(lambda path: OpenCvVideoReader(path), OpenCvPhaseDetector(),
                              RecipeValidationService()).run(recipe, session)
    return recipe, result


def _rows(result):
    return [dict(glass=g.glass_name, frame_index=s.frame_index, time_sec=s.timestamp_sec,
                 oil_y=s.raw_oil_air_level_y, foam_y=s.raw_foam_front_y, fill_state=s.fill_state.value)
            for g in result.glass_results for s in g.samples]


def run(root, output):
    rci.require(output.is_dir() and not any(output.iterdir()), 'empty managed work required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True,
                                   encoding='utf-8', stdin=subprocess.DEVNULL).strip()
    summary = dict(schema='s11-clean-anchor-fill-corpus-v1', head=head, samples={})
    for sample in SAMPLES:
        policies = {}
        for policy in ('ordinary', 'caf1'):
            directory = output / sample / policy
            directory.mkdir(parents=True)
            if policy == 'ordinary':
                recipe, result = _analyze(root, sample, directory)
                operations = []
            else:
                with clean_anchor() as operations:
                    recipe, result = _analyze(root, sample, directory)
            presentation = build_report_presentation(result, recipe)
            CsvExporter().export(result, directory / 'tracking.csv', directory / 'events.csv')
            GraphRenderer().render(result, directory / 'graphs', recipe, presentation=presentation)
            policies[policy] = dict(rows=_rows(result), operations=operations,
                                    presentation=rci.normalize(asdict(presentation)))
            print(sample, policy, len(operations), flush=True)
        ordinary, trial = policies['ordinary'], policies['caf1']
        changed = [(a['glass'], a['time_sec'], a['oil_y'], b['oil_y'], a['foam_y'], b['foam_y'])
                   for a, b in zip(ordinary['rows'], trial['rows'], strict=True)
                   if (a['oil_y'], a['foam_y'], a['fill_state']) != (b['oil_y'], b['foam_y'], b['fill_state'])]
        summary['samples'][sample] = dict(
            window=replay.QUALIFICATION_WINDOWS[sample], rows=len(ordinary['rows']),
            activations=len(trial['operations']), operations=trial['operations'], changed_rows=changed,
            ordinary_oil_numeric=sum(r['oil_y'] is not None for r in ordinary['rows']),
            trial_oil_numeric=sum(r['oil_y'] is not None for r in trial['rows']),
            presentation_equal=ordinary['presentation'] == trial['presentation'])
    summary.update(physical_accuracy='NOT_EVALUATED', production_unchanged=True)
    rci.write_json(output / 'comparison.json', summary)
    print('COMPLETE', json.dumps({k: (v['activations'], len(v['changed_rows'])) for k, v in summary['samples'].items()}))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=rci.ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.output.resolve())


if __name__ == '__main__':
    main()
