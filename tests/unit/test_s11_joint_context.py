"""Joint arrangement controls and a saved-output CLI entry, not physical truth."""
import copy
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np
import pytest

from tests.diagnostics import s11_joint_context_run as run
from tests.diagnostics import s11_spatial_context_probe as probe
from tests.diagnostics import s11_spatial_context_run as source_run
from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.unit.test_oil_interface_witness import measure
from tests.unit.test_oil_interface_diagnostics import _native_path
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from tests.unit.test_s11_spatial_context_probe import point


def joint(gray, mask=None, glare=None, points=None, origin=(0,0)):
    return probe.measure_joint_context(gray, np.ones_like(gray) if mask is None else mask,
                                       np.zeros_like(gray) if glare is None else glare,
                                       [point()] if points is None else points, origin=origin)


def collision():
    a = np.zeros((200,200), np.uint8)
    b = a.copy()
    a[90:94,:100] = 180; a[94:98,100:] = 180
    b[90:94,100:] = 180; b[94:98,:100] = 180
    return a,b


@pytest.mark.parametrize('invert', [False,True])
def test_joint_map_breaks_known_joint_marginal_collision(invert):
    a,b = collision()
    if invert: a,b = 255-a,255-b
    prior = [probe.measure_lateral_context(g,np.ones_like(g),np.zeros_like(g),[point()],band_width=9) for g in (a,b)]
    assert prior[0] == prior[1]
    left,right = [joint(g) for g in (a,b)]
    assert not np.array_equal(left[1]['gradient_magnitude'],right[1]['gradient_magnitude'])
    assert left[0]['decision'] == right[0]['decision'] == 'NOT_EVALUATED'
    # Origin and supplied candidate labels do not alter raster values.
    shifted = joint(a,points=[point(x=(40,240),y=160)],origin=(40,60))
    for key in left[1]: np.testing.assert_array_equal(left[1][key],shifted[1][key])


@pytest.mark.parametrize('kind',['mask','glare'])
def test_hidden_differences_cannot_leak_through_neighbours(kind):
    a,b = collision(); mask=np.ones_like(a); glare=np.zeros_like(a)
    if kind == 'mask': mask[a!=b]=0
    else: glare[a!=b]=255
    originals = [x.copy() for x in (a,b,mask,glare)]
    left,right = [joint(g,mask,glare) for g in (a,b)]
    assert left[0] == right[0]
    for key in left[1]: np.testing.assert_array_equal(left[1][key],right[1][key])
    for actual,original in zip((a,b,mask,glare), originals,strict=True): np.testing.assert_array_equal(actual,original)


def test_stencil_validity_zero_borders_and_orientation():
    a=np.zeros((200,200),np.uint8);a[100:]=200
    _,r=joint(a)
    assert not r['gradient_valid'][0].any() and not r['gradient_valid'][:,-1].any()
    assert r['gradient_valid'][50,50] == 1 and r['gradient_magnitude'][50,50] == 0
    assert r['gradient_magnitude'][99,50] == pytest.approx(100/255)
    assert r['vertical_magnitude'][99,50] == pytest.approx(100/255)
    _,horizontal=joint(a.T.copy())
    assert horizontal['vertical_magnitude'][50,99] == 0
    mask=np.ones_like(a);mask[99,50]=0
    _,blocked=joint(a,mask)
    for y,x in [(99,50),(98,50),(100,50),(99,49),(99,51)]:
        assert blocked['gradient_valid'][y,x] == blocked['gradient_magnitude'][y,x] == 0


def test_identical_pixels_and_polarity_collision_remain_unclassified():
    a=np.zeros((200,200),np.uint8);a[100:]=200
    _,r=joint(a);info,reflection=joint(a.copy());_,opposite=joint(255-a)
    for key in r:
        np.testing.assert_array_equal(r[key],reflection[key])
        np.testing.assert_allclose(r[key],opposite[key],rtol=0,atol=1e-15)
    assert info['spec']['threshold'] is None
    json.dumps(info,allow_nan=False)
    small=np.zeros((1,1),np.uint8)
    _,empty=joint(small,points=[],origin=(3,7))
    assert not empty['gradient_valid'].any()


@pytest.fixture
def stored(tmp_path):
    """Original producer's format, actual O1 extractor and PNG/receipt arithmetic."""
    root=tmp_path/'저장 측정';root.mkdir()
    gray=np.full((200,200),180,np.uint8);gray[100:]=80
    mask=np.ones_like(gray);glare=np.zeros_like(gray)
    witness=json.loads(json.dumps(asdict(measure(gray,origin=(40,60),paths={0:_native_path(160)},
        candidates=[BoundaryCandidate('material_path',BoundaryKind.OIL_AIR,160)]))))
    points=[{**g,'candidate_input_index':c['candidate_input_index']} for c in witness['candidates'] for g in o2.review_geometry(c)]
    arrays={'crop':np.repeat(gray[...,None],3,axis=2),'gray':gray,'effective-mask':mask,'glare-mask':glare}
    rasters={}
    for key,a in arrays.items():
        name=key+'.png';(root/name).write_bytes(cv2.imencode('.png',a)[1].tobytes())
        rasters[key]={'file':name,**source_run.raster_identity(a)}
    artifact={'spec':probe.SPEC,'schema_version':source_run.SCHEMA,'code':{'fixture':'synthetic actual extractor'}}
    artifact['sha256']=o2.fingerprint_json(artifact)
    case={'case_id':'synthetic','frame_index':27,'glass_id':'test-glass','revision':0,'labels_sha256':'fixture',
          'scene_sha256':'fixture','rasters':rasters,'measurement':probe.measure_context(gray,mask,glare,points,origin=(40,60)),
          'baseline_witness':witness,'baseline_check':source_run.baseline_check(gray,mask,glare,witness)}
    assert case['baseline_check']['status']=='MATCH'
    report={'schema_version':source_run.SCHEMA,'artifact':artifact,'decision':'NOT_EVALUATED','auto_acceptance':False,
            'production_decisions_emitted':False,'cases':[case]}
    o2.write_new(root/'experiment.json',report)
    reseal(root)
    return root,artifact['sha256']


def reseal(root):
    report=o2.read_json(root/'experiment.json')
    receipt={'schema_version':source_run.SCHEMA,'status':'COMPLETE','artifact_sha256':report['artifact']['sha256'],
             'outputs':{p.name:o2.sha256_file(p) for p in root.iterdir() if p.name!='complete.json'}}
    (root/'complete.json').write_text(json.dumps(receipt),encoding='utf-8')


def test_saved_cli_unicode_nonrepo_cwd_all_hashes_and_npz(stored,tmp_path):
    root,digest=stored;before={p:p.read_bytes() for p in root.iterdir()}
    cwd=tmp_path/'외부';cwd.mkdir();out=tmp_path/'새 결과'
    result=subprocess.run([sys.executable,str(Path(run.__file__).resolve()),'--source',str(root),
                          '--expected-source-artifact',digest,'--output',str(out)],cwd=cwd,stdin=subprocess.DEVNULL,
                          env={**os.environ,'PYTHONUTF8':'1'},capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stderr
    receipt=o2.read_json(out/'complete.json');report=o2.read_json(out/'experiment.json')
    assert receipt['schema_version']==report['schema_version']==run.SCHEMA
    assert receipt['artifact_sha256']==report['artifact']['sha256']
    assert all(o2.sha256_file(out/name)==h for name,h in receipt['outputs'].items())
    assert all(p.read_bytes()==data for p,data in before.items())
    assert len(report['input_preservation'])==len(before)
    assert all(p['before_sha256']==p['after_sha256'] for p in report['input_preservation'])
    case=report['cases'][0]
    assert {p['geometry_basis'] for p in case['points']} == {'native_path','candidate_center'}
    assert [p['source_y'] for p in case['points'] if p['geometry_basis']=='native_path'] == [152,160,168]
    aliases=[p for p in case['points'] if p['band_binding']=='coincident_recorded_native_center']
    assert len(aliases)==1 and aliases[0]['source_y']==160 and aliases[0]['band_center_role']=='native_path'
    with np.load(out/case['numeric_file'],allow_pickle=False) as arrays:
        for key in arrays.files: assert source_run.raster_identity(arrays[key])==case['arrays'][key]
    for p in case['points']:
        for s in p['scales']:
            for b in s['bands']: assert b['source_y_range']==[v+60 for v in b['local_y_range']]
    assert not report['production_decisions_emitted'] and report['decision']=='NOT_EVALUATED'
    assert 'viewer.html' in receipt['outputs']
    with pytest.raises(ValueError,match='already exists'): run.run(root,out,expected_source_artifact=digest)


@pytest.mark.parametrize('fault',['hash','raw_identity','artifact','expected','schema','inventory','geometry','baseline','traversal','png_dimensions','inside','missing_center'])
def test_saved_input_failure_guards(stored,tmp_path,fault):
    root,digest=stored;out=tmp_path/'failure';path=root/'experiment.json';report=o2.read_json(path)
    if fault=='hash': (root/'gray.png').write_bytes(b'changed')
    elif fault=='expected': digest='0'*64
    elif fault=='inside': out=root/'new'
    else:
        case=report['cases'][0]
        if fault=='raw_identity': case['rasters']['gray']['sha256']='0'*64
        elif fault=='artifact': report['artifact']['spec']={'changed':True}
        elif fault=='schema': report['schema_version']='other'
        elif fault=='inventory': case['measurement']['points']=[]
        elif fault=='geometry': case['frame_index']=99
        elif fault=='baseline': case['baseline_witness']['candidates'][0]['sectors'][0]['centers'][0]['scales'][0]['bands'][0]['gray_mean']=.99
        elif fault=='missing_center': case['baseline_witness']['candidates'][0]['sectors'][0]['centers'].pop()
        elif fault=='png_dimensions': case['rasters']['gray']['shape']=[2,3]
        if fault=='missing_center':
            arrays=[cv2.imdecode(np.frombuffer((root/(k+'.png')).read_bytes(),np.uint8),cv2.IMREAD_UNCHANGED) for k in ('gray','effective-mask','glare-mask')]
            case['baseline_check']=source_run.baseline_check(*arrays,case['baseline_witness'])
        path.write_text(json.dumps(report),encoding='utf-8');reseal(root)
        if fault=='traversal':
            r=o2.read_json(root/'complete.json');r['outputs']['../escape']='0'*64
            (root/'complete.json').write_text(json.dumps(r),encoding='utf-8')
    with pytest.raises(ValueError): run.run(root,out,expected_source_artifact=digest)
    assert not (out/'complete.json').exists()


@pytest.mark.parametrize('phase',['measure','publish'])
def test_mutation_never_publishes_complete(stored,tmp_path,monkeypatch,phase):
    root,digest=stored;out=tmp_path/'failure'
    target=root/'gray.png'
    if phase=='measure':
        original=probe.measure_joint_context
        def change(*args,**kw):
            result=original(*args,**kw);target.write_bytes(b'changed');return result
        monkeypatch.setattr(probe,'measure_joint_context',change)
    else:
        original=run._viewer
        def change(*args):
            result=original(*args);target.write_bytes(b'changed');return result
        monkeypatch.setattr(run,'_viewer',change)
    with pytest.raises(ValueError,match='changed'): run.run(root,out,expected_source_artifact=digest)
    assert not (out/'complete.json').exists()


def test_viewer_data_cannot_break_script_context():
    page=run._viewer([{'case_id':'</script><script>bad</script>'}])
    assert '</script><script>bad' not in page and '\\u003c/script>' in page


def test_two_cases_and_every_center_use_their_own_geometry(stored,tmp_path):
    root,digest=stored;report=o2.read_json(root/'experiment.json')
    second=copy.deepcopy(report['cases'][0])
    second.update(case_id='second',glass_id='second-glass',frame_index=28)
    second['baseline_witness']['glass_id']='second-glass'
    second['baseline_witness']['source_frame_index']=28
    second['baseline_witness']['observability'].update(glass_id='second-glass',frame_index=28)
    report['cases'].append(second)
    (root/'experiment.json').write_text(json.dumps(report),encoding='utf-8');reseal(root)
    result=run.run(root,tmp_path/'two',expected_source_artifact=digest)
    assert len(result['cases'])==2
    assert [c['frame_index'] for c in result['cases']]==[27,28]
    assert [c['numeric_file'] for c in result['cases']]==['case-0-gradients.npz','case-1-gradients.npz']


def test_central_difference_alias_is_not_physical_discrimination():
    a=(np.indices((200,200)).sum(axis=0)%2*255).astype(np.uint8)
    _,left=joint(a);_,right=joint(255-a)
    assert not np.array_equal(a,255-a)
    assert not left['gradient_magnitude'].any()
    for key in left: np.testing.assert_array_equal(left[key],right[key])
