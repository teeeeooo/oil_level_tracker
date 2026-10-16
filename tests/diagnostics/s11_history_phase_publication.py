"""Publish every HPA quarantine activation against its unchanged-policy counterpart."""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
from tests.diagnostics import s11_history_phase_amplification as hpa
from tests.diagnostics import s11_terminal_veto_quarantine as trial
from tests.diagnostics import s11_single_observation_influence as soi
from tests.diagnostics import s11_role_consumer_intervention as rci
from oil_tracker.adapters.reporting.graph_renderer import GraphRenderer


def run(root,directory):
    summary=json.loads((directory/'comparison.json').read_text()); pre=summary['preflight']
    raw=json.loads((root/rci.SAVED/'raw.json').read_text())
    recipe=rci.JsonRecipeRepository().load(root/rci.BUNDLE/'recipe_snapshot.oilrecipe')
    originals={}; wanted={s['id'] for s in summary['cases'] if s['quarantined_frames']}; trials={}
    parent=root/next(p for p in pre['inputs'] if p.endswith('/population.jsonl.gz'))
    with gzip.open(parent,'rt') as f:
        for line in f:
            r=json.loads(line)
            if r['id'] in wanted: originals[r['id']]=r
    with gzip.open(directory/'population.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line)
            if r['record']['id'] in wanted: trials[r['record']['id']]=r
    rci.require(set(originals)==set(trials)==wanted,'activation denominator')
    entries=[];sources={str(Path(__file__).relative_to(root)):rci.digest(Path(__file__)),**pre['sources']}
    rci.require(all(rci.digest(root/p)==h for p,h in sources.items()),'source drift')
    for name in originals:
        for policy in ('default','trial'):
            reference=originals[name] if policy=='default' else trials[name]['record']
            if policy=='default': record,_,public,presentation=soi.execute(raw,recipe,reference['case'])
            else:
                record,_,public,presentation,ops=trial.execute(raw,recipe,reference['case'])
                rci.require(ops==trials[name]['operations'],'activation replay drift')
            rci.require(record==reference,'publication replay drift')
            relative=Path('paired-triggers')/name/policy;target=directory/relative
            target.mkdir(parents=True,exist_ok=False)
            rci.CsvExporter().export(public,target/'tracking.csv',target/'events.csv')
            GraphRenderer().render(public,target/'graphs',recipe,presentation=presentation)
            entries.append(dict(case=name,policy=policy,path=str(relative),rows=len(record['rows']),
                                exact_record_equality=True,movement_summary=record['presentation']['movement_summary']))
            print('PUBLISHED',name,policy,flush=True)
    rci.require(all(rci.digest(root/p)==h for p,h in sources.items()),'source mutation')
    result=dict(schema='s11-hpa-paired-publication-v1',sources=sources,entries=entries,windows=len(entries),
                population_sha256=rci.digest(directory/'population.jsonl.gz'),
                physical_accuracy='NOT_EVALUATED',report_comprehension='NOT_HUMAN_EVALUATED')
    rci.write_json(directory/'paired-publication.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=hpa.ROOT)
    p.add_argument('--directory',type=Path,required=True);a=p.parse_args()
    run(a.root.resolve(),a.directory.resolve())


if __name__=='__main__':main()
