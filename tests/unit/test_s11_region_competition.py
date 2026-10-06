"""Synthetic appearance controls and the actual saved-output CLI, not Oil truth."""
import copy
import csv
import json
import os
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np
import pytest

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_joint_context_run as run
from tests.diagnostics import s11_region_competition as model
from tests.diagnostics import s11_spatial_context_probe as probe
from tests.unit.test_s11_joint_context import stored  # real producer/extractor fixture


def fixture(kind='partition', reverse=False):
    yy, xx = np.indices((80, 32))
    if kind == 'ramp': gray = 40+yy+xx
    elif kind == 'partition': gray = 40+120*(yy >= 40)
    elif kind == 'ribbon_bw': gray = 40+120*(np.abs(yy-40) < 8)
    elif kind == 'ribbon_2bw': gray = 40+120*(np.abs(yy-40) < 16)
    elif kind == 'flat': gray = np.full_like(yy, 80)
    else: raise AssertionError(kind)
    crop = np.repeat(gray.astype(np.uint8)[..., None], 3, axis=-1)
    if reverse: crop = 255-crop
    mask = np.ones_like(gray, dtype=np.uint8)
    glare = np.zeros_like(mask)
    bands = [{'name': name, 'local_y_range': [a, b], 'clipped_local_y_range': [a, b],
              'available': True, 'reason': 'available', 'valid_pixel_count': (b-a)*32}
             for name, a, b in [('near_above',31,39), ('near_below',42,50),
                                ('far_above',15,23), ('far_below',58,66)]]
    p = {'candidate_input_index': 7, 'geometry_basis': 'native_path',
         'source_x_range': [40,72], 'source_y':100,
         'band_binding':'exact_role', 'band_center_role':'native_path',
         'scales':[{'band_width_px':8, 'bands':bands}]}
    return crop, mask, glare, [p]


def measure(args):
    crop, mask, glare, points = args
    return model.measure(crop, cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), mask, glare, points, origin=(40,60))


def views(result):
    return {(v['support'], v['channels']): v for v in result['points'][0]['scales'][0]['views']}


@pytest.mark.parametrize('kind', ['ramp', 'partition', 'ribbon_bw', 'ribbon_2bw'])
@pytest.mark.parametrize('reverse', [False, True])
def test_fixed_model_explains_its_appearance_on_heldout_columns(kind, reverse):
    result = measure(fixture(kind, reverse))
    v = views(result)['candidate_envelope','gray']
    expected = 'smooth' if kind == 'ramp' else kind
    assert v['models'][expected]['heldout_mse'] < 1e-26
    if kind != 'ramp':
        for other in v['models']:
            if other != expected: assert v['models'][other]['heldout_mse'] > 1e-5
    assert result['decision'] == 'NOT_EVALUATED'
    assert v['physical_identity'] == 'UNRESOLVED'


def test_achromatic_normalization_and_factorial_support_are_identical():
    args = fixture()
    result = measure(args)
    values = views(result)
    for support in model.SPEC['support']:
        gray, bgr = values[support,'gray'], values[support,'BGR']
        assert gray['train_pixels'] == bgr['train_pixels']
        assert gray['test_pixels'] == bgr['test_pixels']
        assert gray['within_side_adjacency'] == bgr['within_side_adjacency']
        for name in gray['models']:
            assert gray['models'][name]['heldout_mse'] == pytest.approx(bgr['models'][name]['heldout_mse'], rel=1e-12, abs=1e-25)
    s = result['points'][0]['scales'][0]
    assert s['original_band_visible_pixels'] == 32*32
    assert s['added_envelope_visible_pixels'] == 19*32
    assert s['envelope_pixels'] == 51*32


def test_equal_gray_chromatic_partition_has_information_without_identity():
    args = fixture()
    args[0][:40] = [0,0,100]; args[0][40:] = [0,51,0]
    v = views(measure(args))
    for support in model.SPEC['support']:
        gray, bgr = v[support,'gray'], v[support,'BGR']
        assert gray['models']['smooth']['heldout_mse'] < 1e-26
        assert bgr['models']['smooth']['heldout_mse'] > 1e-4
        assert bgr['models']['partition']['heldout_mse'] < 1e-26
        assert bgr['physical_identity'] == 'UNRESOLVED'


def test_raw_adjacency_exposes_full_color_side_collision():
    a = fixture('flat'); b = copy.deepcopy(a)
    colors = np.array([[0,0,100], [0,51,0]], dtype=np.uint8)
    yy, xx = np.indices((80,32))
    a[0][:] = colors[yy % 2]; b[0][:] = colors[(yy+xx) % 2]
    def color(args):
        c,m,g,p=args
        return probe.measure_color_side(c,cv2.cvtColor(c,cv2.COLOR_BGR2GRAY),m,g,p,origin=(40,60))
    assert color(a) == color(b)
    av, bv = views(measure(a)), views(measure(b))
    assert av['candidate_envelope','gray'] == bv['candidate_envelope','gray']
    for support in model.SPEC['support']:
        ah = av[support,'BGR']['within_side_adjacency']['horizontal']
        bh = bv[support,'BGR']['within_side_adjacency']['horizontal']
        assert ah['pair_count'] == bh['pair_count']
        assert ah['mean_squared_difference'] == 0
        assert bh['mean_squared_difference'] > 0


def recount(args):
    _, mask, glare, points = args
    for p in points:
        for s in p['scales']:
            for b in s['bands']:
                a,z=b['clipped_local_y_range']
                b['valid_pixel_count'] = int(((mask[a:z]>0)&(glare[a:z]==0)).sum())


@pytest.mark.parametrize('mask_kind',['effective','glare'])
def test_missing_pixels_never_leak_or_bridge(mask_kind):
    a = fixture()
    (a[1] if mask_kind=='effective' else a[2])[:,16] = 0 if mask_kind=='effective' else 255
    recount(a)
    first = measure(a)
    a[0][:,16] = [17,255,9]
    assert first == measure(a)
    v = views(first)['candidate_envelope','BGR']
    assert v['within_side_adjacency']['horizontal']['pair_count'] == 29*51
    assert first['points'][0]['scales'][0]['masked_pixels'] == 51


def test_band_gap_is_not_bridged_and_new_support_effect_is_separate():
    args = fixture('flat')
    before = views(measure(args))
    args[0][40:42] = [255,0,0]  # ONLY in new center gap support
    after = views(measure(args))
    for channel in model.SPEC['channels']:
        assert before['recorded_bands',channel] == after['recorded_bands',channel]
        assert before['candidate_envelope',channel] != after['candidate_envelope',channel]
        assert after['recorded_bands',channel]['within_side_adjacency']['vertical']['pair_count'] == 4*7*32


def test_heldout_pixels_do_not_fit_coefficients():
    args=fixture(); before=views(measure(args))
    args[0][:,::4]=255-args[0][:,::4]
    after=views(measure(args))
    for key in before:
        for name in before[key]['models']:
            a,b=before[key]['models'][name],after[key]['models'][name]
            assert a['coefficients']==b['coefficients']
            assert a['train_mse']==b['train_mse']
            assert a['heldout_mse']!=b['heldout_mse']


def test_unavailable_and_outside_crop_cannot_be_rescued_or_converted_to_zero():
    args=fixture()
    b=args[3][0]['scales'][0]['bands'][2]
    b.update(local_y_range=[-4,23], clipped_local_y_range=[0,23], available=False, reason='outside_crop')
    recount(args)
    result=measure(args)
    assert result['points'][0]['scales'][0]['crop_clipped']
    for v in views(result).values():
        assert v['status']=='o1_unavailable'
        assert all(f['heldout_mse'] is None for f in v['models'].values())
        assert v['physical_identity']=='UNRESOLVED'


def test_same_pixels_static_template_and_truth_metadata_cannot_change_model():
    args=fixture(); first=measure(args)
    args[3][0].update(identity='non_interface', rejected=True, template_match=1.0, static=True)
    assert measure(args)==first  # ignored metadata cannot certify or veto a region
    assert first['opposition_status']=='not_measured'
    assert first['physical_identity']=='UNRESOLVED'
    json.dumps(first,allow_nan=False)


def test_partial_path_is_kept_separate_without_candidate_max_or_vote():
    args=fixture()
    # One candidate, two disjoint X pieces: step on the left, smooth on the
    # right. Strong local support must never be pooled into a candidate result.
    args[0][:,16:]=80
    args[3][0]['source_x_range']=[40,56]
    for b in args[3][0]['scales'][0]['bands']: b['valid_pixel_count']//=2
    other=copy.deepcopy(args[3][0]); other['source_x_range']=[56,72]
    args[3].append(other)
    result=measure(args)
    assert len(result['points'])==2
    assert result['points'][0]['candidate_input_index']==result['points'][1]['candidate_input_index']
    left,right=[p['scales'][0]['views'][2]['models']['smooth']['heldout_mse'] for p in result['points']]
    assert left>1e-4 and right<1e-26
    assert 'candidate_score' not in result and 'selected_candidate' not in result


@pytest.mark.parametrize('bound',['max_patch_pixels','max_total_patch_pixels'])
def test_resources_reject_before_fitting(bound,monkeypatch):
    monkeypatch.setitem(model.SPEC,bound,1)
    monkeypatch.setattr(model,'_fit_view',lambda *a: pytest.fail('fit ran before preflight'))
    with pytest.raises(ValueError,match='resource bound'): measure(fixture())


def test_insufficient_split_support_and_rank_deficiency_are_explicit():
    args=fixture(); args[1][:]=0;args[1][40:43,0:2]=1;recount(args)
    for v in views(measure(args)).values():
        assert v['status']=='insufficient_split_support'
        assert all(f['heldout_mse'] is None for f in v['models'].values())
    args=fixture();args[1][40:]=0;recount(args)
    for v in views(measure(args)).values():
        assert v['status']=='incomplete_model_support'
        assert v['models']['partition']['status']=='rank_deficient'
        assert v['models']['partition']['heldout_mse'] is None


def test_real_cli_unicode_cwd_receipt_all_views_aliases_and_inputs(stored,tmp_path):
    root,digest=stored; out=tmp_path/'영역 결과'
    before={p.name:p.read_bytes() for p in root.iterdir()}
    proc=subprocess.run([sys.executable,str(Path(run.__file__).resolve()),'--source',str(root),
        '--expected-source-artifact',digest,'--output',str(out),'--region-competition'],
        cwd=tmp_path,stdin=subprocess.DEVNULL,capture_output=True,text=True,encoding='utf-8',
        env={**os.environ,'PYTHONUTF8':'1'},timeout=60)
    assert proc.returncode==0,proc.stdout+proc.stderr
    report=o2.read_json(out/'experiment.json'); receipt=o2.read_json(out/'complete.json')
    assert receipt['schema_version']==run.REGION_SCHEMA and receipt['status']=='COMPLETE'
    assert set(receipt['outputs'])=={'experiment.json','summary.md','region-competition.csv'}
    for name,digest in receipt['outputs'].items(): assert o2.sha256_file(out/name)==digest
    assert report['artifact']['sha256']==receipt['artifact_sha256']
    assert any(k.endswith('s11_region_competition.py') for k in report['artifact']['code'])
    assert {p.name:p.read_bytes() for p in root.iterdir()}==before
    points=report['cases'][0]['region_competition']['points']
    assert len(points)==6
    alias=next(p for p in points if p['band_binding']=='coincident_recorded_native_center')
    native=next(p for p in points if p['geometry_basis']=='native_path' and p['source_y']==alias['source_y'])
    assert alias['scales']==native['scales']
    with (out/'region-competition.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    assert len(rows)==6*3*4*4
    assert {r['physical_identity'] for r in rows}=={'UNRESOLVED'}
    assert not report['production_decisions_emitted']


@pytest.mark.parametrize('phase',['measure','publish'])
def test_mutation_never_publishes_complete(stored,tmp_path,monkeypatch,phase):
    root,digest=stored
    owner,name=(model,'measure') if phase=='measure' else (run,'_write_region_outputs')
    original=getattr(owner,name)
    def mutate(*args,**kwargs):
        result=original(*args,**kwargs); (root/'gray.png').write_bytes(b'changed');return result
    monkeypatch.setattr(owner,name,mutate)
    out=tmp_path/'failure'
    with pytest.raises(ValueError,match='changed'):
        run.run(root,out,expected_source_artifact=digest,region_competition=True)
    assert not (out/'complete.json').exists()


def test_modes_are_mutually_exclusive(stored,tmp_path):
    root,digest=stored
    with pytest.raises(ValueError,match='one measurement mode'):
        run.run(root,tmp_path/'bad',expected_source_artifact=digest,color_side=True,region_competition=True)
