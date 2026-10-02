"""Inspect saved spatial gradients or recorded-band color sides; no identity decision."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import platform
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ''):
    sys.path[:0] = [str(ROOT/'src'), str(ROOT)]

import cv2
import numpy as np
from oil_tracker.adapters.vision import oil_interface_witness, oil_interface_diagnostics, row_features
from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_spatial_context_probe as probe
from tests.diagnostics import s11_spatial_context_run as source_run

SCHEMA = 's11-o2-joint-context-v1'
COLOR_SCHEMA = 's11-o2-color-side-v1'


def _display(values, valid, maximum):
    """Fixed analytic scale, not per-image contrast stretch; invalid is magenta."""
    level = np.rint(np.clip(values/maximum, 0, 1)*255).astype(np.uint8)
    bgr = np.repeat(level[..., None], 3, axis=2)
    bgr[~valid.astype(bool)] = (255, 0, 255)
    return bgr


def _viewer(cases):
    # All paths below are generated basenames. Escape untrusted JSON before script embedding.
    data = json.dumps(cases, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c')
    return '''<!doctype html><html lang="en"><meta charset="utf-8">
<title>S11 joint spatial context</title><style>
body{font:16px system-ui;margin:20px;background:#eee;color:#222}select{max-width:100%;padding:6px}
.views{display:flex;gap:12px;overflow:auto}figure{margin:0;flex:none}svg{width:auto;height:680px;background:#ccc}
svg image{image-rendering:pixelated}pre{white-space:pre-wrap}button{padding:6px}</style>
<h1>Unpooled O1 spatial context</h1>
<p>NOT_EVALUATED / FIELD FAIL. Appearance only; no physical identity or connected region is inferred.
Y increases downward. Magenta = invalid stencil (center or neighbour masked, glare or crop border).
Black = valid zero gradient. Fixed scales: magnitude 0–sqrt(0.5), vertical magnitude 0–0.5.</p>
<p>Select a recorded point and scale. Green line is its exact source Y; rectangles are separate O1 bands,
blue when available, red when unavailable. Gaps remain gaps. Uncheck overlays to inspect pixels.</p>
<select id="case"></select> <select id="point"></select> <select id="scale"></select>
<label><input id="strip" type="checkbox" checked>Selected X strip</label>
<label><input id="overlay" type="checkbox" checked>Overlays</label><pre id="info"></pre>
<div class="views" id="views"></div><h2>Exact band metadata</h2><pre id="bands"></pre>
<script>const cases=DATA;
const byId=id=>document.getElementById(id); const ns='http://www.w3.org/2000/svg';
function option(select,text,value){const o=document.createElement('option');o.textContent=text;o.value=value;select.append(o)}
function node(tag,attrs){const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);return n}
function current(){return cases[Number(byId('case').value)]}
function setupPoints(){const c=current();byId('point').replaceChildren();c.points.forEach((p,i)=>option(byId('point'),`idx${p.candidate_input_index} ${p.geometry_basis} X=${p.source_x_range} Y=${p.source_y}`,i));setupScales()}
function setupScales(){const p=current().points[Number(byId('point').value)];byId('scale').replaceChildren();(p?.scales||[]).forEach((s,i)=>option(byId('scale'),`BW ${s.band_width_px}`,i));draw()}
function draw(){const c=current(), p=c.points[Number(byId('point').value)], s=p?.scales[Number(byId('scale').value)];const [h,w]=c.shape,[ox,oy]=c.origin;
byId('info').textContent=`${c.case_id}; frame ${c.frame_index}; Glass ${c.glass_id}; revision ${c.revision}\nSource X=[${ox},${ox+w}), Y=[${oy},${oy+h}); origin=${c.origin}; no historical pixel equality claim.`;
byId('views').replaceChildren();for(const [label,file] of Object.entries(c.images)){const fig=document.createElement('figure'),cap=document.createElement('figcaption');cap.textContent=label;fig.append(cap);const a=p&&byId('strip').checked?p.source_x_range[0]-ox:0, width=p&&byId('strip').checked?p.source_x_range[1]-p.source_x_range[0]:w;const svg=node('svg',{viewBox:`${a} 0 ${width} ${h}`,width:width,height:h});svg.append(node('image',{href:file,x:0,y:0,width:w,height:h}));
if(p&&byId('overlay').checked){const [a,b]=p.source_x_range;for(const band of s?.bands||[]){const [lo,hi]=band.clipped_local_y_range;svg.append(node('rect',{x:a-ox,y:lo,width:b-a,height:hi-lo,fill:'none',stroke:band.available?'#00aaff':'#ff3030','stroke-width':0.7}))}svg.append(node('line',{x1:a-ox,x2:b-ox,y1:p.source_y-oy,y2:p.source_y-oy,stroke:'#00e040','stroke-width':0.8}))}fig.append(svg);byId('views').append(fig)}
byId('bands').textContent=JSON.stringify({band_binding:p?.band_binding,recorded_role:p?.band_center_role,scale:s||{}},null,2)}
cases.forEach((c,i)=>option(byId('case'),c.case_id,i));byId('case').onchange=setupPoints;byId('point').onchange=setupScales;byId('scale').onchange=draw;byId('overlay').onchange=draw;byId('strip').onchange=draw;setupPoints();
</script></html>'''.replace('DATA;', data+';')


def run(source, output, *, expected_source_artifact, color_side=False):
    schema = COLOR_SCHEMA if color_side else SCHEMA
    source, output = Path(source).resolve(), Path(output).resolve()
    o2.require(source.is_dir(), 'source output directory missing')
    o2.require(not output.exists(), 'output already exists; choose a new directory')
    o2.require(source not in output.parents, 'output must be outside original experiment')
    snapshots = {}
    def read(name):
        o2.require(isinstance(name, str) and name not in ('', '.', '..') and '/' not in name and '\\' not in name,
                   'receipt paths must be basenames')
        path = source/name
        o2.require(path.resolve().parent == source and path.is_file(), 'input file missing or escapes source')
        o2.require(path.stat().st_size <= 128*1024**2, 'input file exceeds size bound')
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        o2.require(name not in snapshots or snapshots[name] == digest, 'input changed while reading')
        snapshots[name] = digest
        return raw
    receipt = json.loads(read('complete.json'))
    o2.require(receipt['schema_version'] == source_run.SCHEMA and receipt['status'] == 'COMPLETE', 'source receipt is not spatial COMPLETE')
    entries = receipt['outputs']
    o2.require(isinstance(entries, dict) and 1 <= len(entries) <= 128 and 'complete.json' not in entries,
               'invalid source output inventory')
    total = 0
    for name, digest in entries.items():
        total += len(read(name))
        o2.require(total <= 512*1024**2, 'source inventory exceeds size bound')
        o2.require(snapshots[name] == digest, f'source output hash mismatch: {name}')
    o2.require('experiment.json' in entries, 'experiment missing from receipt')
    old = json.loads(read('experiment.json'))
    artifact = old['artifact']
    o2.require(old['schema_version'] == source_run.SCHEMA and
               artifact['sha256'] == receipt['artifact_sha256'] == expected_source_artifact and
               o2.fingerprint_json({k:v for k,v in artifact.items() if k != 'sha256'}) == artifact['sha256'],
               'source artifact/schema mismatch')
    o2.require(old['decision'] == 'NOT_EVALUATED' and old['auto_acceptance'] is False and
               old['production_decisions_emitted'] is False, 'unexpected source decision flags')
    o2.require(1 <= len(old['cases']) <= 2, 'one or two source cases required')
    cases, numeric, images, seen = [], {}, {}, set()
    for number, case in enumerate(old['cases']):
        identity = (case['glass_id'], case['frame_index'])
        o2.require(identity not in seen, 'duplicate source frame/Glass')
        seen.add(identity)
        rasters = {}
        for kind in ('crop', 'gray', 'effective-mask', 'glare-mask'):
            meta = case['rasters'][kind]
            o2.require(meta['file'] in entries, 'raster not covered by receipt')
            raw = read(meta['file'])
            o2.require(raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[12:16] == b'IHDR', 'PNG raster required')
            w, h = struct.unpack('>II', raw[16:24])
            o2.require(0 < w <= 4096 and 0 < h <= 4096 and [h,w] == meta['shape'][:2], 'PNG dimensions mismatch or exceed bound')
            array = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
            o2.require(array is not None and source_run.raster_identity(array) == {k:v for k,v in meta.items() if k != 'file'}, 'raw raster identity mismatch')
            rasters[kind] = array
        gray, effective, glare = [rasters[k] for k in ('gray','effective-mask','glare-mask')]
        witness = case['baseline_witness']
        origin = case['measurement']['origin']
        o2.require(witness['source_frame_index'] == case['frame_index'] and witness['glass_id'] == case['glass_id'] and
                   origin == witness['crop_origin'] and list(gray.shape[::-1]) == witness['crop_size'] and
                   rasters['crop'].shape[:2] == gray.shape, 'witness/frame/crop mismatch')
        points = [{**g, 'candidate_input_index': c['candidate_input_index']}
                  for c in witness['candidates'] for g in o2.review_geometry(c)]
        rows = probe.measure_context(gray, effective, glare, points, origin=origin)
        o2.require(rows == case['measurement'], 'saved row context or point inventory mismatch')
        baseline = source_run.baseline_check(gray, effective, glare, witness)
        o2.require(baseline['status'] == case['baseline_check']['status'] == 'MATCH' and
                   baseline == case['baseline_check'], 'baseline reconstruction mismatch; inspect original reconstruction first')
        if color_side:
            context = {'origin': origin, 'shape': list(gray.shape), 'points': copy.deepcopy(points)}
        else:
            context, arrays = probe.measure_joint_context(gray, effective, glare, points, origin=origin)
        centers = {}
        for c in witness['candidates']:
            for sector in c['sectors']:
                for center in sector['centers']:
                    key = (c['candidate_input_index'], center['role'], tuple(sector['source_x_range']), center['source_y'])
                    o2.require(key not in centers, 'duplicate witness center')
                    scales = copy.deepcopy(center['scales'])
                    for scale in scales:
                        for band in scale['bands']:
                            band['source_y_range'] = [y+origin[1] for y in band['local_y_range']]
                    centers[key] = scales
        for p in context['points']:
            key = (p['candidate_input_index'], *o2.geometry_key(p))
            matched = key
            if key not in centers and p['geometry_basis'] == 'candidate_center':
                # O1 records only the native center when the candidate center is
                # exactly coincident. The validated inventory already proves the
                # candidate/source X/Y; never substitute a different Y or native role.
                matched = (p['candidate_input_index'], 'native_path', tuple(p['source_x_range']), p['source_y'])
            o2.require(matched in centers, 'point has no exact witness center')
            p['band_center_role'] = matched[1]
            p['band_binding'] = 'exact_role' if matched == key else 'coincident_recorded_native_center'
            p['scales'] = centers[matched]
        if color_side:
            color = probe.measure_color_side(rasters['crop'], gray, effective, glare, context['points'], origin=origin)
            cases.append({k:case[k] for k in ('case_id','frame_index','glass_id','revision','labels_sha256','scene_sha256')} | {
                'origin': origin, 'shape': list(gray.shape),
                'baseline_band_count': baseline['band_count'], 'baseline_status': 'MATCH',
                'color_side': color})
        else:
            prefix = f'case-{number}'
            numeric[prefix+'-gradients.npz'] = arrays
            images[prefix+'-crop.png'] = rasters['crop']
            images[prefix+'-gray.png'] = gray
            images[prefix+'-magnitude.png'] = _display(arrays['gradient_magnitude'], arrays['gradient_valid'], np.sqrt(.5))
            images[prefix+'-vertical.png'] = _display(arrays['vertical_magnitude'], arrays['gradient_valid'], .5)
            cases.append({k:case[k] for k in ('case_id','frame_index','glass_id','revision','labels_sha256','scene_sha256')} | context | {
                'baseline_band_count': baseline['band_count'], 'baseline_status': 'MATCH',
                'numeric_file': prefix+'-gradients.npz',
                'arrays': {k:source_run.raster_identity(a) for k,a in arrays.items()},
                'images': {k:prefix+'-'+v+'.png' for k,v in [('Original crop','crop'),('Raw gray','gray'),('Gradient magnitude','magnitude'),('Vertical magnitude','vertical')]}})
    def preservation():
        result = []
        for name, digest in list(snapshots.items()):
            read(name)
            result.append({'file':name, 'before_sha256':digest, 'after_sha256':snapshots[name]})
        return result
    code = {Path(p).resolve().relative_to(ROOT).as_posix():o2.sha256_file(p) for p in
            (__file__, probe.__file__, source_run.__file__, o2.__file__, oil_interface_witness.__file__, oil_interface_diagnostics.__file__, row_features.__file__)}
    artifact = {'schema_version':schema, 'spec':probe.COLOR_SIDE_SPEC if color_side else probe.JOINT_SPEC, 'code':code}
    artifact['sha256'] = o2.fingerprint_json(artifact)
    report = {'schema_version':schema, 'artifact':artifact, 'source_artifact_sha256':expected_source_artifact,
              'source_receipt_sha256':snapshots['complete.json'], 'source_experiment_sha256':snapshots['experiment.json'],
              'status':'EXPLORATORY_UNCALIBRATED', 'decision':'NOT_EVALUATED', 'auto_acceptance':False,
              'production_decisions_emitted':False, 'field_disposition':'FIELD FAIL', 'numeric_localization':'NOT_MEASURED',
              'runtime':{'python':platform.python_version(), 'numpy':np.__version__, 'opencv':cv2.__version__},
              'cases':cases, 'input_preservation':preservation(),
              'provenance_limit':'Only stored experiment outputs rehashed; original video/bundle/labels not reopened. No historical pixel equality proof.'}
    output.mkdir(parents=True, exist_ok=False)
    for name, arrays in numeric.items():
        with (output/name).open('xb') as handle: np.savez_compressed(handle, **arrays)
    for name, image in images.items():
        ok, encoded = cv2.imencode('.png', image)
        o2.require(ok, 'PNG encoding failed')
        (output/name).write_bytes(encoded.tobytes())
    if color_side:
        _write_color_outputs(output, report, len(snapshots))
    else:
        (output/'viewer.html').write_text(_viewer(cases), encoding='utf-8')
        lines = ['# S11 unpooled O1 spatial context', '',
                 'EXPLORATORY_UNCALIBRATED; FIELD FAIL; NOT_EVALUATED. No classifier or detector run.',
                 f'Artifact: `{artifact["sha256"]}`', f'Source artifact: `{expected_source_artifact}`',
                 '[Open local viewer](viewer.html). Fixed-scale previews are quantized; NPZ arrays own numbers.',
                 'Validity requires the center and its four neighbours. Invalid zeros are storage only.',
                 'This exposes existing pixel information lost by pooling. No identity, connectivity or ranking gain is claimed.', '',
                 '| Case | Frame | Glass | Revision | Origin | Shape | Points | Baseline bands |', '|---|---|---|---|---|---|---|---|']
        for c in cases:
            lines.append(f'| {c["case_id"]} | {c["frame_index"]} | {c["glass_id"]} | {c["revision"]} | {c["origin"]} | {c["shape"]} | {len(c["points"])} | MATCH / {c["baseline_band_count"]} |')
        lines += ['', '| Case | Profile | Source X | Visible pixels | Valid gradient stencils | Total pixels |', '|---|---|---|---|---|---|']
        for c in cases:
            for s in c['strips']:
                lines.append(f'| {c["case_id"]} | {s["profile_id"]} | {s["source_x_range"]} | {s["visible_pixel_count"]} | {s["gradient_valid_count"]} | {s["pixel_count"]} |')
        lines += ['', f'Stored inputs preserved: {len(snapshots)}/{len(snapshots)}. Original video/bundle/labels not reopened.',
                  'Human idx0/idx20 ambiguity remains unresolved. COMPLETE verifies measurement execution only.', '']
        o2.write_new(output/'experiment.json', report)
        (output/'summary.md').write_text('\n'.join(lines), encoding='utf-8')
    preservation()
    o2.write_new(output/'complete.json', {'schema_version':schema, 'status':'COMPLETE', 'artifact_sha256':artifact['sha256'],
                 'outputs':{p.name:o2.sha256_file(p) for p in sorted(output.iterdir())}})
    return report


def _write_color_outputs(output, report, input_count):
    """Machine-owned numbers for all points; no identity-based selection or ranking."""
    header = ['case_id', 'frame_index', 'candidate_input_index', 'geometry_basis',
              'source_x_start', 'source_x_stop', 'source_y', 'band_width_px', 'region',
              'status', 'paired_columns', 'total_columns', 'delta_B', 'delta_G', 'delta_R',
              'delta_gray', 'delta_B_minus_G', 'delta_R_minus_G']
    lines = ['# S11 recorded-band color-side measurement', '',
             'EXPLORATORY_UNCALIBRATED; FIELD FAIL; NOT_EVALUATED. No identity score or transparency estimate.',
             'Same visible pixels for B/G/R and gray. Deltas are below minus above, equal-weight over paired X columns.',
             'O1 unavailable stays unavailable. JSON null / empty CSV cells are not zero.',
             'All points/roles/widths are in color-side.csv; per-column deltas/support remain in experiment.json.',
             'Chromatic appearance may also be caused by reflections, illumination or structures.',
             f"Artifact: `{report['artifact']['sha256']}`",
             f"Source artifact: `{report['source_artifact_sha256']}`", '',
             '| Case | Frame | Glass | Revision | Points | Baseline bands | Observed / unavailable / no paired columns |',
             '|---|---|---|---|---|---|---|']
    with (output/'color-side.csv').open('x', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle); writer.writerow(header)
        for case in report['cases']:
            states = {'observed': 0, 'o1_unavailable': 0, 'no_paired_columns': 0}
            points = case['color_side']['points']
            for p in points:
                for scale in p['scales']:
                    for region, pair in scale['pairs'].items():
                        states[pair['status']] += 1
                        delta = pair['mean_column_delta_bgr_gray']
                        opponent = pair['mean_column_delta_opponents']
                        writer.writerow([case['case_id'], case['frame_index'], p['candidate_input_index'],
                            p['geometry_basis'], *p['source_x_range'], p['source_y'], scale['band_width_px'],
                            region, pair['status'], pair['observed_paired_columns'], pair['total_columns'],
                            *(delta if delta is not None else [None]*4),
                            *(opponent if opponent is not None else [None]*2)])
            lines.append(f"| {case['case_id']} | {case['frame_index']} | {case['glass_id']} | {case['revision']} | {len(points)} | MATCH / {case['baseline_band_count']} | {states['observed']} / {states['o1_unavailable']} / {states['no_paired_columns']} |")
    lines += ['', f'Stored inputs preserved: {input_count}/{input_count}. Original video/bundle/labels not reopened.',
              'COMPLETE verifies measurement execution only. Existing labels and human ambiguity remain unchanged.', '']
    o2.write_new(output/'experiment.json', report)
    (output/'summary.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, help='existing spatial-context output directory')
    parser.add_argument('--expected-source-artifact', required=True)
    parser.add_argument('--output', required=True, help='new directory outside the source output')
    parser.add_argument('--color-side', action='store_true', help='measure recorded-band BGR/gray sides; no new gradient map or identity score')
    args = parser.parse_args()
    run(args.source, args.output, expected_source_artifact=args.expected_source_artifact, color_side=args.color_side)
    print('Measurement complete. Read summary.md and ' + ('color-side.csv' if args.color_side else 'viewer.html') + '. No identity decision was made.')


if __name__ == '__main__':
    main()
