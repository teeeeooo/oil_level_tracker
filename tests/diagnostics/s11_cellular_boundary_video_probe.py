"""Headless source-video probe: unchanged report + separate experimental candidates.

Never publishes the cellular readout as Oil/Foam. All candidate coordinates are
copied from the same current detection. Private media remain on the executing PC.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time
import cv2
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.domain.session import AnalysisSession, InitialStateConfirmation, DebugTraceLevel
from tests.diagnostics import s11_cellular_boundary_readout as model
from tests.diagnostics.s11_report_observability_replay import _sample_summary


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def save(path, payload):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(payload,f,indent=2,allow_nan=False,ensure_ascii=False)
        f.write('\n')


def measure_frame(witness, image, effective, glare):
    features,valid=model.cellular_map(image,(effective>0)&(glare==0))
    ox,oy=witness['crop_origin']; rows=[]
    for candidate in witness['candidates']:
        points=[p for s in candidate['sectors'] for p in s['centers']]
        role='native_path' if any(p['role']=='native_path' for p in points) else 'candidate_center'
        views=[]
        for sector in candidate['sectors']:
            selected=[p for p in sector['centers'] if p['role']==role]
            if not selected: continue
            if len(selected)!=1: raise ValueError('multiple current centres in one sector')
            measurement=model.measure_sector(features,valid,
                x_range=[int(x-ox) for x in sector['source_x_range']],
                current_y=selected[0]['source_y']-oy)
            views.append(dict(sector=sector['sector'],role=role,measurement=measurement))
        rows.append(dict(candidate_input_index=candidate['candidate_input_index'],
            canonical_y=candidate['canonical_y'],source=candidate['source'],
            rejected=candidate['rejected'],score=model.score_candidate(views),views=views))
    return rows

class ProbeDetector(OpenCvPhaseDetector):
    def __init__(self, output: Path):
        super().__init__(); self.output=output; self.rows=[]; self.current=[]
        (output/'source-crops').mkdir()

    def detect(self, frame, glass, frame_index, time_sec, debug=False):
        detection,artifacts=super().detect(frame,glass,frame_index,time_sec,debug=True)
        before=json.dumps(asdict(detection),sort_keys=True,default=str)
        witness=artifacts.state['oil_interface_witness']
        if len(self.rows)>=4000 or len(witness['candidates'])>256:
            raise ValueError('probe resource bound exceeded')
        images=artifacts.images
        rows=measure_frame(witness,images['original_roi'],images['effective_mask'],images['glare_mask'])
        tied=model.select_candidate(rows); selected=tied[0] if len(tied)==1 else None
        chosen=next((r for r in rows if r['candidate_input_index']==selected),None)
        tag=hashlib.sha256(glass.id.encode()).hexdigest()[:12]
        crop=self.output/'source-crops'/f'{tag}-f{frame_index}.png'
        if not cv2.imwrite(str(crop),images['original_roi']): raise OSError('crop save failed')
        self.rows.append(dict(glass_id=glass.id,frame_index=frame_index,time_sec=time_sec,
            crop_origin=witness['crop_origin'],source_crop=str(crop),rows=rows,top_tie_set=tied,
            selected=selected,selected_y=None if chosen is None else chosen['canonical_y']))
        self.current.append(asdict(detection))
        assert before==json.dumps(asdict(detection),sort_keys=True,default=str)
        if chosen is not None:
            assert detection.candidates[selected].y==chosen['canonical_y']
        if len(self.rows)%20==0: print('CAPTURED',len(self.rows),frame_index,flush=True)
        return detection,artifacts if debug else None

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',type=Path,required=True)
    parser.add_argument('--recipe',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--start',type=float,default=0)
    parser.add_argument('--end',type=float,required=True)
    parser.add_argument('--fps',type=float,default=2)
    parser.add_argument('--baseline-only',action='store_true')
    states=parser.add_mutually_exclusive_group(required=True)
    states.add_argument('--unknown-initial-state',action='store_true')
    states.add_argument('--confirm-recipe-initial-states',action='store_true')
    args=parser.parse_args(argv)
    if not (0<=args.start<args.end and 0<args.fps<=60): parser.error('invalid time window/fps')
    with OpenCvVideoReader(args.video) as reader: metadata=reader.metadata
    if args.end>metadata.duration_sec+.05: parser.error('end exceeds source duration')
    recipe=JsonRecipeRepository().load(args.recipe)
    session=AnalysisSession(input_video_path=str(args.video.resolve()),video_metadata=metadata,
        analysis_start_sec=args.start,analysis_end_sec=min(args.end,metadata.duration_sec),
        compressor_start_sec=args.start,sampling_fps=args.fps,output_directory=str(args.output.resolve()),
        run_name='S11 cellular-boundary source probe',run_note='Experimental coordinates are separate; official detector unchanged.',
        resolution_confirmed=True,debug_trace_level=DebugTraceLevel.NONE)
    for glass in recipe.glasses:
        if not glass.enabled: continue
        if args.unknown_initial_state: glass.initial_state=InitialObservationState.UNKNOWN_REVIEW
        if glass.initial_state is InitialObservationState.AUTO:
            parser.error('AUTO is not a confirmed initial state; explicitly choose the UNKNOWN probe or a confirmed recipe')
        session.initial_state_confirmations[glass.id]=InitialStateConfirmation(
            glass.initial_state,session.input_video_path,session.analysis_start_sec)
    count=sum(g.enabled for g in recipe.glasses)
    if not count or (args.end-args.start)*args.fps*count+count>4000:
        parser.error('probe supports 1..4000 sampled glass frames per invocation')
    args.output=args.output.resolve(); args.output.mkdir(parents=True,exist_ok=False)
    repo=Path(__file__).resolve().parents[2]
    modules=[Path(__file__),Path(model.__file__),
        repo/'tests/diagnostics/s11_cellular_basin_readout.py',
        repo/'tests/diagnostics/s11_cellular_partition_readout.py']
    pinned=[args.video.resolve(),args.recipe.resolve(),*modules,*sorted((repo/'src').rglob('*.py'))]
    pins={str(p):sha(p) for p in pinned}
    design=repo/'docs/20-architecture/s11-cellular-basin-shadow-design.md'
    (args.output/'design-snapshot.md').write_bytes(design.read_bytes())
    save(args.output/'freeze.json',dict(method=model.SPEC,initial_states={g.id:g.initial_state.value for g in recipe.glasses},
        pins=pins,design_sha256=sha(design),metadata=asdict(metadata),baseline_only=args.baseline_only,
        warning='PRIVATE LOCAL ARTIFACTS; no upload is performed by this program'))
    detector=OpenCvPhaseDetector() if args.baseline_only else ProbeDetector(args.output)
    started=time.monotonic()
    result=AnalysisPipeline(lambda p:OpenCvVideoReader(p),detector,RecipeValidationService()).run(recipe,session)
    bundle=OutputBundleStore().write_bundle(result,recipe,session,args.output)
    summary=_sample_summary(args.video.stem,result,recipe,bundle)
    save(args.output/'final-samples.json',[asdict(s) for g in result.glass_results for s in g.samples])
    if not args.baseline_only:
        save(args.output/'measurements.json',detector.rows)
        save(args.output/'current-detections.json',detector.current)
    assert all(sha(p)==h for p,h in pins.items()),'pinned inputs or source changed during run'
    save(args.output/'receipt.json',dict(status='COMPLETE',elapsed_sec=time.monotonic()-started,
        summary=summary,production_coordinates_changed=False,inputs_preserved=True,
        experimental_rows=0 if args.baseline_only else len(detector.rows)))
    print(json.dumps(summary),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
