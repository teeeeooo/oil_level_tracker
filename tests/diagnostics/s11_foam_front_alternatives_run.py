"""Run bounded front-alternative inspection from an immutable Foam capture.

No video, model, recipe or label files are opened. Output must be a new folder.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.adapters.vision import oil_interface_witness
from tests.diagnostics import s11_foam_front_alternatives as probe
from tests.diagnostics import s11_foam_support_geometry


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(capture_dir, output_dir, expected_receipt):
    root, out = Path(capture_dir).resolve(), Path(output_dir).resolve()
    if out.is_relative_to(root):
        raise ValueError('output must be outside immutable capture')
    receipt_path = root / 'receipt.json'
    if sha(receipt_path) != expected_receipt:
        raise ValueError('capture receipt pin mismatch')
    receipt = json.loads(receipt_path.read_text())
    if receipt['schema_version'] != 's11-local-foam-component-capture-receipt-v1':
        raise ValueError('wrong capture schema')
    if receipt['status'] != 'CAPTURE_COMPLETE_NOT_EVALUATED':
        raise ValueError('capture incomplete')
    pins = dict(receipt['output_sha256s'])
    pins['receipt.json'] = expected_receipt

    def source(name):
        path = (root / name).resolve()
        if not path.is_relative_to(root) or name not in pins or sha(path) != pins[name]:
            raise ValueError(f'unpinned/changed capture file: {name}')
        return path

    for name in pins:
        source(name)
    capture = json.loads(source('capture.json').read_text())
    cases = []
    pictures = []
    for case in capture['cases']:
        trace_name = str(Path(case['trace_directory']) / 'debug_trace.jsonl')
        record = json.loads(source(trace_name).read_text())
        diag = record['state']['foam_component_diagnostics']
        if diag['truncated']:
            raise ValueError('truncated retained support')

        def raster(key):
            name = str(Path(case['trace_directory']) / record['images'][key])
            path = source(name)
            return cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

        labels = raster('foam_component_labels')
        gray = raster('grayscale')
        rgb = raster('original_roi')
        if not np.array_equal(gray, cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)):
            raise ValueError('saved gray is not raw original ROI gray')
        effective, glare = raster('effective_mask') > 0, raster('glare_mask') > 0
        expected_ids = {c['diagnostic_id'] for c in diag['components']}
        if expected_ids != set(np.unique(labels[labels > 0])):
            raise ValueError('raster/metadata component ID mismatch')
        for comp in diag['components']:
            ys, xs = np.where(labels == comp['diagnostic_id'])
            box = [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]
            if len(xs) != comp['pixel_count'] or box != comp['local_bbox_xyxy']:
                raise ValueError('raster/metadata geometry mismatch')
        result = probe.measure(gray, labels, effective, glare, origin=tuple(diag['crop_origin']))
        result['identity'] = {k: case[k] for k in ['case_id', 'frame_index', 'glass_id', 'run_id', 'record_id']}
        for comp in result['components']:
            comp['appearance_counts'] = {
                str(radius): dict(Counter(col['views'][i]['appearance_state'] for col in comp['columns']))
                for i, radius in enumerate(probe.RADII)}
        cases.append(result)
        picture = str(Path(case['trace_directory']) / record['images']['original_roi'])
        pictures.append(base64.b64encode(source(picture).read_bytes()).decode('ascii'))
    for name in pins:
        source(name)
    modules = [Path(__file__), Path(probe.__file__), Path(oil_interface_witness.__file__),
               Path(s11_foam_support_geometry.__file__)]
    report = {'schema_version': 's11-foam-front-alternatives-run-v1',
              'decision': 'NOT_EVALUATED', 'field_disposition': 'FIELD FAIL',
              'source_receipt_sha256': expected_receipt,
              'runtime': {'python': sys.version, 'numpy': np.__version__, 'opencv': cv2.__version__},
              'code_sha256s': {p.name: sha(p) for p in modules},
              'input_sha256s': pins, 'preserved_input_count': len(pins), 'cases': cases}
    # Only after all validation; no overwrite of any prior output.
    out.mkdir(parents=True, exist_ok=False)
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    lines = ['# Offline Foam front alternatives', '',
             'FIELD FAIL / NOT_EVALUATED. All fronts remain null; no identity or runtime selection.', '',
             '| Case | Component | Radius | Single peak | Multiple peaks | No bracketed peak | Censored |',
             '|---|---|---|---|---|---|---|']
    for case in cases:
        for comp in case['components']:
            for r, counts in comp['appearance_counts'].items():
                values = [counts.get(k, 0) for k in ['single_peak','multiple_peaks','no_bracketed_peak','censored']]
                lines.append(f'| {case["identity"]["case_id"]} | {comp["component_id"]} | {r} | '+
                             ' | '.join(map(str, values))+' |')
    lines += ['', 'Positive local maxima have no amplitude cutoff; weak texture/noise is retained.',
              'Single peak is not Foam identity. No peak/window censoring is not absence.',
              'No interpolation, component reordering, structure-veto removal or scalar replacement.',
              f'{len(pins)} capture files rehashed before and after; all unchanged.']
    (out / 'summary.md').write_text('\n'.join(lines)+'\n')
    data = json.dumps({'cases': cases, 'pictures': pictures}, ensure_ascii=False).replace('<', '\\u003c')
    (out / 'viewer.html').write_text(VIEWER.replace('__DATA__', data))
    outputs = {name: sha(out/name) for name in ['report.json', 'summary.md', 'viewer.html']}
    (out / 'receipt.json').write_text(json.dumps({
        'schema_version': 's11-foam-front-alternatives-receipt-v1',
        'status': 'MEASUREMENT_COMPLETE_NOT_EVALUATED', 'outputs': outputs,
        'source_receipt_sha256': expected_receipt, 'preserved_input_count': len(pins)
    }, indent=2)+'\n')
    return report


VIEWER = '''<!doctype html><meta charset="utf-8"><title>Foam boundary alternatives</title>
<style>body{background:#171b24;color:#eef1f8;font:16px system-ui;margin:24px;max-width:1180px}
select{font:inherit;margin:8px}canvas{width:520px;max-width:46vw;image-rendering:pixelated;background:#333}
pre{white-space:pre-wrap} .pair{display:flex;gap:16px}p{max-width:1000px}label{display:inline-block}</style>
<h1>Foam 경계 후보 — 원본과 저장 support 대조</h1>
<p>노랑: 각 열의 첫 support 픽셀. 파랑: 검사 범위 내 밝기 변화의 국소 최대 구간.
파랑은 Foam·구조물 판정이 아닙니다. 검사는 원본 픽셀에서 수행하며, 약한 질감도 모두 남깁니다.</p>
<label>장면 <select id="scene"></select></label><label>Component <select id="component"></select></label>
<label>검사 반경 <select id="radius"><option value="0">±4 px</option><option value="1">±8 px</option></select></label>
<label><input type="checkbox" id="peaks" checked>밝기 후보</label>
<label><input type="checkbox" id="tops" checked>support top</label>
<div class="pair"><div>원본 RGB<br><canvas id="plain"></canvas></div><div>같은 원본 + 후보<br><canvas id="overlay"></canvas></div></div>
<p>그림 위를 클릭하면 source 좌표와 해당 열의 전체 측정값이 표시됩니다. 확대는 원본 해상도를 늘리지 않습니다.</p>
<pre id="detail"></pre><p>FIELD FAIL / NOT_EVALUATED. 확정 경계·보간·scalar 없음.
sample2의 반사 의심과 sample4 중앙의 원형 특징 의심은 이 그림만으로 해소되지 않습니다.</p>
<script>const data=__DATA__; const $=id=>document.getElementById(id);let image=new Image();let selected=0;
for(let i=0;i<data.cases.length;i++)$('scene').add(new Option(data.cases[i].identity.case_id,i));
function current(){return data.cases[+$('scene').value]}
function comp(){return current().components.find(c=>c.component_id===+$('component').value)}
function draw(){const c=current(), [h,w]=c.shape, [ox,oy]=c.origin;for(const id of ['plain','overlay']){
 const can=$(id);can.width=w;can.height=h;can.getContext('2d').drawImage(image,0,0,w,h)}
 const ctx=$('overlay').getContext('2d');for(const col of (comp()?.columns||[])){const x=col.source_x-ox;
 if($('peaks').checked){ctx.fillStyle='#43bbff';for(const p of col.views[+$('radius').value].peaks){
 for(let y=p.source_y_range[0];y<p.source_y_range[1];y++)ctx.fillRect(x,y-oy,1,1)}}
 if($('tops').checked){ctx.fillStyle='#ffe04a';ctx.fillRect(x,col.support_top_source_y-oy,1,1)}}
 $('detail').textContent=JSON.stringify({identity:c.identity,component:comp()?.component_id??null,
 appearance_counts:comp()?.appearance_counts??null,physical_identity:'UNRESOLVED',foam_front:null},null,2)}
function load(){const c=current();$('component').replaceChildren();for(const k of c.components)
 $('component').add(new Option('C'+k.component_id,k.component_id));
 if(c.components.some(k=>k.component_id===2))$('component').value=2;
 const token=++selected;const next=new Image();next.onload=()=>{if(token!==selected)return;image=next;draw()};
 next.src='data:image/png;base64,'+data.pictures[+$('scene').value]}
$('scene').onchange=load;for(const id of ['component','radius','peaks','tops'])$(id).onchange=draw;
for(const id of ['plain','overlay'])$(id).onclick=e=>{const c=current(),rect=$(id).getBoundingClientRect();
 const x=Math.floor((e.clientX-rect.left)/rect.width*c.shape[1])+c.origin[0];
 const y=Math.floor((e.clientY-rect.top)/rect.height*c.shape[0])+c.origin[1];
 const col=comp()?.columns.find(p=>p.source_x===x);
 $('detail').textContent=JSON.stringify({clicked_source:[x,y],column:col||'no retained support in column'},null,2)};
load();</script>'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--expected-receipt-sha256', required=True)
    args = parser.parse_args()
    result = run(args.capture, args.output, args.expected_receipt_sha256)
    print(f'Measured {len(result["cases"])} cases; {result["preserved_input_count"]} files preserved. No front assigned.')
