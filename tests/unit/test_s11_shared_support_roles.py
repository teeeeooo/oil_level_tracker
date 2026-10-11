"""Common support and ambiguity contracts, independently reconstructed costs."""
import numpy as np
import pytest

from tests.diagnostics import s11_boundary_temporal_probe as probe


def fixture():
    rng = np.random.default_rng(1110)
    a = rng.integers(20, 220, (25, 25, 3), dtype=np.uint8)
    v = np.ones((25, 25), bool)
    e = np.zeros_like(v)
    p = np.array([[6,11], [12,12], [18,13]], np.int64)
    e[p[:,1],p[:,0]] = True
    refs = {'interface': (a.copy(),v.copy(),e.copy())}
    for role in ('structure','texture'):
        refs[role] = (rng.integers(20,220,a.shape,dtype=np.uint8),v.copy(),np.zeros_like(e))
    return a,v,e,p,refs


def test_same_samples_and_direct_residual_geometry_oracle():
    a,v,e,p,refs = fixture()
    r = probe.compare_shared_support_roles(a,v,e,p,refs)
    assert r['status'] == 'MEASURED'
    assert r['appearance_preference'] == 'interface'
    assert r['physical_identity'] == 'UNRESOLVED' and r['selected_front'] is None
    xy = np.asarray(r['sample_xy']); x,y=xy.T
    for role,(b,_,be) in refs.items():
        for j,(dx,dy) in enumerate(r['common_shifts_xy']):
            d = a[y,x].astype(float)-b[y+dy,x+dx].astype(float)
            expected = .75*np.mean((d-d.mean(axis=0))**2)/255**2
            expected += .25*np.mean(~be[p[:,1]+dy,p[:,0]+dx])
            assert r['roles'][role]['costs'][j] == pytest.approx(expected,abs=1e-14)


def test_copied_distractor_and_role_alias_are_unresolved():
    a,v,e,p,refs = fixture()
    refs['structure'] = refs['interface']
    r = probe.compare_shared_support_roles(a,v,e,p,refs)
    assert r['roles']['interface']['best_cost'] == r['roles']['structure']['best_cost'] == 0
    assert r['appearance_preference'] is None


def test_stationary_and_translated_interface_with_channel_offset():
    a,v,e,p,refs = fixture()
    shifted = np.zeros_like(a); shifted[1:,2:] = a[:-1,:-2]+[2,3,4]
    se = np.zeros_like(e); se[1:,2:] = e[:-1,:-2]
    refs['interface'] = (shifted,v.copy(),se)
    r = probe.compare_shared_support_roles(a,v,e,p,refs)
    assert r['roles']['interface']['best_shifts_xy'] == [[2,1]]
    assert r['roles']['interface']['best_cost'] == 0


def test_each_role_has_identical_translation_domain_after_masking():
    a,v,e,p,refs = fixture()
    refs['structure'][1][8:15,4] = False
    r = probe.compare_shared_support_roles(a,v,e,p,refs)
    assert all(dx != -2 for dx,dy in r['common_shifts_xy'])
    assert all(len(s['costs']) == len(r['common_shifts_xy']) for s in r['roles'].values())


@pytest.mark.parametrize('role',probe.SHARED_ROLE_SPEC['roles'])
def test_missing_role_is_never_a_win(role):
    a,v,e,p,refs = fixture(); refs[role] = None
    r = probe.compare_shared_support_roles(a,v,e,p,refs)
    assert r['reason'] == 'missing_'+role+'_reference'
    assert r['appearance_preference'] is None


def test_cropped_or_masked_current_support_does_not_shrink():
    a,v,e,p,refs = fixture(); v[10,6] = False
    r = probe.compare_shared_support_roles(a,v,e,p,refs)
    assert r['status'] == 'UNAVAILABLE'
    assert 'reference_stencil_masked' in r['reason']


def test_duplicate_or_reordered_points_have_no_extra_vote():
    a,v,e,p,refs = fixture()
    first = probe.compare_shared_support_roles(a,v,e,p,refs)
    second = probe.compare_shared_support_roles(a,v,e,np.concatenate([p[::-1],p]),refs)
    assert first == second


def test_current_geometry_cannot_be_invented():
    a,v,e,p,refs = fixture(); e[p[0,1],p[0,0]] = False
    with pytest.raises(ValueError,match='observed Canny'):
        probe.compare_shared_support_roles(a,v,e,p,refs)


def test_no_edges_is_unavailable():
    a,v,e,p,refs = fixture()
    r = probe.compare_shared_support_roles(a,v,e,p[:0],refs)
    assert r['reason'] == 'no_current_edge_support'


def test_joint_geometry_opposes_independent_part_placements():
    a,v,e,p,refs = fixture()
    b = np.zeros_like(a); be = np.zeros_like(e)
    for (x,y),dy in zip(p,(-2,0,2),strict=True):
        b[y+dy-2:y+dy+3,x] = a[y-2:y+3,x]
        be[y+dy,x] = True
    refs['interface'] = (b,v.copy(),be)
    r = probe.compare_shared_support_roles(a,v,e,p,refs)
    assert r['roles']['interface']['best_cost'] >= .25*(2/3)
    assert r['appearance_preference'] is None


def test_coherent_warp_with_identical_opposition_remains_ambiguous():
    a,v,e,p,refs = fixture()
    warped = a.copy(); we=e.copy()
    # A fixed pattern and fluid appearance with identical observed deformation
    # supply identical model inputs; shared geometry cannot distinguish them.
    warped[::2] = np.roll(a[::2],1,axis=1)
    refs['interface']=(warped,v.copy(),we)
    refs['texture']=(warped.copy(),v.copy(),we.copy())
    r=probe.compare_shared_support_roles(a,v,e,p,refs)
    assert r['appearance_preference'] is None


def test_disjoint_visible_role_domains_are_not_comparable():
    a,v,e,p,refs = fixture()
    samples=np.unique((p[:,None,:]+np.array([(0,y) for y in range(-2,3)])).reshape(-1,2),axis=0)
    for role,dx in zip(probe.SHARED_ROLE_SPEC['roles'],(-2,0,2),strict=True):
        mask=np.zeros_like(v)
        mask[samples[:,1],samples[:,0]+dx]=True
        refs[role]=(refs[role][0],mask,refs[role][2])
    r=probe.compare_shared_support_roles(a,v,e,p,refs)
    assert r['reason']=='no_common_visible_translation'
    assert r['appearance_preference'] is None


@pytest.mark.parametrize('count',[76,1000])
def test_input_center_budget_is_enforced_before_search(count):
    a,v,e,p,refs=fixture()
    with pytest.raises(ValueError,match='bounded integer'):
        probe.compare_shared_support_roles(a,v,e,np.tile(p[:1],(count,1)),refs)


@pytest.mark.parametrize('fault',['input','operation','existing_output'])
def test_runner_fails_before_raster_load_from_other_cwd(tmp_path,monkeypatch,fault):
    import hashlib
    import importlib.util
    import json
    from pathlib import Path

    script=Path(__file__).resolve().parents[2]/'docs/50-diagnostics/s11/2026-10-11-p2-shared-support/run.py'
    spec=importlib.util.spec_from_file_location('p2_frozen_runner_test',script)
    runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    data=tmp_path/'data'; data.mkdir(); (data/'input').write_bytes(b'pinned')
    manifest=tmp_path/'manifest.json'; out=tmp_path/'out'
    pre=dict(inputs={'input':hashlib.sha256(b'pinned').hexdigest()},production_sources={},
             operation=probe.SHARED_ROLE_SPEC.copy())
    if fault=='input':
        (data/'input').write_bytes(b'changed')
    elif fault=='operation':
        pre['operation']['minimum_margin']=0
    else:
        out.mkdir(); (out/'keep').write_bytes(b'original')
    manifest.write_text(json.dumps(pre),encoding='utf-8')
    monkeypatch.setattr(runner,'ROOT',data)
    monkeypatch.setattr(runner,'load_images',lambda _:pytest.fail('must reject before raster read'))
    elsewhere=tmp_path/'elsewhere'; elsewhere.mkdir(); monkeypatch.chdir(elsewhere)
    with pytest.raises(FileExistsError if fault=='existing_output' else ValueError):
        runner.run(manifest,out)
    if fault=='existing_output':
        assert (out/'keep').read_bytes()==b'original'
    else:
        assert not out.exists()
