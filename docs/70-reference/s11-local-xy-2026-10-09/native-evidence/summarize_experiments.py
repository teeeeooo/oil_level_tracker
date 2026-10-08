"""Complete-run readout with separate current, completed and report meaning."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
variants=['baseline','local_xy_rectangle','oil_measurement_only','oil_measurement_paired_phase','paired_phase_no_exclusion']
labels=['Baseline','Shared XY mask','Oil measurement XY only','Oil XY + paired phase','Paired phase, no XY']
read=lambda p:json.loads(p.read_text())
rows={v:read(OUT/f'sample4-{v}/tracking.json') for v in variants}
raw={v:read(OUT/f'sample4-{v}/raw.json') for v in variants}
completed={v:read(OUT/f'sample4-{v}/completed.json') for v in variants}
pre=read(OUT/'preflight.json')

def runs(rs,key,present,lo=0,hi=56):
    result=[];start=None;previous=None;count=0
    for r in rs:
        t=r['timestamp_sec']
        if not lo<=t<=hi:continue
        flag=(r[key] is not None)==present
        if flag:
            if start is None:start=t;count=0
            count+=1;previous=t
        elif start is not None:
            result.append({'start_sec':start,'last_sample_sec':previous,'sample_count':count,'sample_support_sec':count*.5,'endpoint_span_sec':previous-start});start=None
    if start is not None:result.append({'start_sec':start,'last_sample_sec':previous,'sample_count':count,'sample_support_sec':count*.5,'endpoint_span_sec':previous-start})
    return result

baseline=rows['baseline'];rbase=raw['baseline'];frames=[1140,1200,1260,1275,1320,1485,1560];summaries=[]
for v in variants:
    r=rows[v];rr=raw[v];cc=completed[v]
    result=read(OUT/f'sample4-{v}/summary.json')
    result.update(public_changed_rows=sum(any(a[k]!=b[k] for k in ['raw_oil_air_level_y','raw_foam_front_y','oil_is_valid','foam_is_valid','fill_state']) for a,b in zip(baseline,r,strict=True)),
      oil_changed_rows=sum(a['raw_oil_air_level_y']!=b['raw_oil_air_level_y'] for a,b in zip(baseline,r,strict=True)),
      foam_completed_exact_equal=all((a['raw_foam_front_y'],a['foam_is_valid'])==(b['raw_foam_front_y'],b['foam_is_valid']) for a,b in zip(baseline,r,strict=True)),
      current_foam_metrics_equal_rows=sum(all(a['debug_metrics'][k]==b['debug_metrics'][k] for k in a['debug_metrics'] if k.startswith('foam_')) and a['raw_foam_front_y']==b['raw_foam_front_y'] for a,b in zip(rbase,rr,strict=True)),
      oil_missing_runs=runs(r,'raw_oil_air_level_y',False),
      foam_numeric_runs=runs(r,'raw_foam_front_y',True),
      checkpoints=[{'frame_index':f,'time_sec':f/30,'completed_oil_y':next(z['raw_oil_air_level_y'] for z in r if z['frame_index']==f),
                    'current_oil_y':next(z['raw_oil_air_level_y'] for z in rr if z['frame_index']==f),
                    'material_phase':next(z['debug_metrics'].get('sequence_material_phase') for z in cc if z['frame_index']==f),
                    'phase_reason':next(z['debug_metrics'].get('sequence_material_phase_reason') for z in cc if z['frame_index']==f),
                    'selected_source':next(z['debug_metrics'].get('sequence_decision_witness') for z in cc if z['frame_index']==f)} for f in frames])
    # Preserve detailed decision witnesses locally; compact summary excludes nested witness.
    summaries.append(result)
oldroot=ROOT/'sample/output/s11-d2-support-comparison-20261009-001'
baseline_matches=[]
for sample in pre['windows']:
    old=read(oldroot/f'new-{sample}-none.json');new=read(OUT/f'{sample}-baseline/summary.json')
    baseline_matches.append({'sample':sample,'rows':new['results'],'previous_fingerprint':old['fingerprint'],'current_fingerprint':new['fingerprint'],'exact_fingerprint_match':old['fingerprint']==new['fingerprint']})
all_source_match=all(sha(ROOT/n)==h for n,h in pre['source_files'].items())
all_input_match=all(sha(ROOT/n)==h for n,h in pre['inputs'].items())
summary={'schema':'s11-local-xy-experiment-summary-v1','source_head':pre['source_head'],'total_replayed_result_rows':299+113*4,'unique_baseline_result_rows':299,'baseline_replay_matches':baseline_matches,'all_source_files_unchanged':all_source_match,'all_frozen_inputs_unchanged':all_input_match,'source_file_count':len(pre['source_files']),'input_pin_count':len(pre['inputs']),'experiments':summaries,'review_labels':'Baseline original candidate identities remain bound; changes are not automatically given identity/scalar labels. Empty output on a reviewed positive is a miss.','timing_caveat':'Runs overlap with independent probes/control processes; elapsed times are not throughput acceptance.','claim_boundary':'Only shared-rectangle and existing-family sampling operations were tested, not complete masked preprocessing, all-family integration, fragment-aware contour reconstruction, or Windows efficacy.'}
(OUT/'detailed-summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
for kind,key in [('oil','raw_oil_air_level_y'),('foam','raw_foam_front_y')]:
    fig,ax=plt.subplots(figsize=(13,5))
    for v,label in zip(variants,labels,strict=True):
        ts=[r['timestamp_sec'] for r in rows[v]];ys=[850-r[key] if r[key] is not None else np.nan for r in rows[v]]
        ax.plot(ts,ys,marker='.',markersize=3,linewidth=1,label=label)
    ax.set_xlabel('Source time (s)');ax.set_ylabel(f'{kind.capitalize()} height from zero (px)');ax.set_title(f'Sample4 / {kind} / recorded completed values; missing samples break lines')
    ax.legend();ax.grid(True);fig.tight_layout();fig.savefig(OUT/f'{kind}-comparison.png',dpi=140);plt.close(fig)
compact={**summary,'experiments':[{**e,'checkpoints':[{k:v for k,v in c.items() if k!='selected_source'} for c in e['checkpoints']]} for e in summaries]}
(OUT/'compact-summary.json').write_text(json.dumps(compact,indent=2,allow_nan=False)+'\n')
print(json.dumps({'total_rows':summary['total_replayed_result_rows'],'baseline_matches':baseline_matches,'source_unchanged':all_source_match,'inputs_unchanged':all_input_match,'variants':[{k:v for k,v in e.items() if k not in ['checkpoints','oil_missing_runs','foam_numeric_runs']} for e in summaries],'checkpoints':{v:[next(r['raw_oil_air_level_y'] for r in rows[v] if r['frame_index']==f) for f in frames] for v in variants},'longest_oil_missing_run':{e.get('variant','baseline'):max(e['oil_missing_runs'],key=lambda x:x['sample_count'],default=None) for e in summaries}},indent=2),flush=True)
