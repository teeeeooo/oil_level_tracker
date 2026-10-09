"""Boundary conservation/visibility controls; no physical classifier truth."""
import numpy as np
import pytest

from tests.diagnostics import s11_foam_support_geometry as probe


def measure(labels, visible=None, **kw):
    return probe.measure_boundary_faces(labels, np.ones(labels.shape, bool) if visible is None else visible, **kw)


def edge_set(r):
    return {(int(k), tuple(a), tuple(b)) for k,a,b in zip(r['inside_label'],r['start_xy2'],r['end_xy2'],strict=True)}


def test_single_pixel_has_four_oriented_faces_and_exact_area():
    labels=np.zeros((3,3),np.uint16);labels[1,1]=65535;r=measure(labels)
    assert len(r['status'])==4 and not r['status'].any()
    assert set(map(tuple,r['outward_normal_xy']))=={(0,-1),(1,0),(0,1),(-1,0)}
    a,b=r['start_xy2'],r['end_xy2']
    assert np.sum(a[:,0]*b[:,1]-a[:,1]*b[:,0])==8  # doubled coordinates, area=1
    assert set(map(tuple,a))==set(map(tuple,b))
    assert r['label_ids'].tolist()==[65535] and r['label_pixel_counts'].tolist()==[1]


def test_layer_has_upper_lower_and_side_faces_without_two_material_roles():
    labels=np.zeros((9,13),np.uint16);labels[3:6,2:11]=8;r=measure(labels)
    assert len(r['status'])==2*(9+3)
    assert set(r['inside_label'])=={8}
    assert r['selected_front'] is None and r['physical_identity']=='UNRESOLVED'
    assert set(r['outward_normal_xy'][:,1])=={-1,0,1}


def test_hole_and_disconnected_pieces_do_not_get_filled_or_paired():
    labels=np.zeros((9,13),np.uint16);labels[1:6,1:6]=2;labels[2:5,2:5]=0;labels[7,10]=2;r=measure(labels)
    assert len(r['status'])==20+12+4
    a,b=r['start_xy2'],r['end_xy2']
    assert np.sum(a[:,0]*b[:,1]-a[:,1]*b[:,0])==8*np.count_nonzero(labels)
    assert r['label_pixel_counts'].tolist()==[17]
    assert r['decision']=='NOT_EVALUATED'  # same ID does not force a connected physical object


def test_diagonal_touch_preserves_all_corner_incidence_alternatives():
    labels=np.zeros((4,4),np.uint16);labels[1,1]=labels[2,2]=9;r=measure(labels)
    assert len(r['status'])==8
    assert np.count_nonzero((r['start_xy2']==[3,3]).all(1))==2
    assert np.count_nonzero((r['end_xy2']==[3,3]).all(1))==2


def test_two_labels_share_a_border_as_opposite_owner_views():
    labels=np.array([[2,3]],np.uint16);r=measure(labels)
    shared=r['status']==1;assert shared.sum()==2
    a,b=r['start_xy2'][shared],r['end_xy2'][shared]
    np.testing.assert_array_equal(a,b[::-1])
    assert r['outside_label'][shared].tolist()==[3,2]
    assert np.count_nonzero(r['status']==3)==6


def test_masked_neighbour_is_censored_and_hidden_values_are_ignored():
    labels=np.zeros((4,5),np.uint16);labels[1:3,1:4]=2
    visible=np.ones(labels.shape,bool);visible[1,2]=False
    r=measure(labels,visible);assert (r['status']==2).sum()==3
    assert (r['outside_label'][r['status']==2]==0).all()
    poisoned=labels.copy();poisoned[~visible]=65535;s=measure(poisoned,visible)
    for k,v in r.items():
        if isinstance(v,np.ndarray):np.testing.assert_array_equal(v,s[k])
        else:assert v==s[k]
    assert r['label_pixel_counts'].tolist()==[5]


def test_origin_changes_coordinates_only_and_outputs_are_owned():
    labels=np.zeros((6,7),np.uint16);labels[1:5,1:6]=256;before=labels.copy();r=measure(labels);s=measure(labels,origin=(543,798))
    for k in ['owner_pixel_xy','neighbour_pixel_xy']:np.testing.assert_array_equal(s[k],r[k]+[543,798])
    for k in ['start_xy2','end_xy2']:np.testing.assert_array_equal(s[k],r[k]+[1086,1596])
    s['inside_label'][:]=0;np.testing.assert_array_equal(labels,before)


def test_all_hidden_or_empty_preserves_typed_empty_arrays():
    for labels,visible in [(np.zeros((3,4),np.uint16),np.ones((3,4),bool)),(np.ones((3,4),np.uint16),np.zeros((3,4),bool))]:
        r=measure(labels,visible)
        assert r['owner_pixel_xy'].shape==r['start_xy2'].shape==(0,2)
        assert len(r['label_ids'])==0 and r['selected_front'] is None


def test_exhaustive_small_binary_masks_conserve_perimeter_and_area():
    for bits in range(512):
        labels=np.array([(bits>>i)&1 for i in range(9)],np.uint16).reshape(3,3)
        r=measure(labels);a,b=r['start_xy2'],r['end_xy2']
        horizontal=np.count_nonzero(np.diff(np.pad(labels,1).astype(int),axis=1))
        vertical=np.count_nonzero(np.diff(np.pad(labels,1).astype(int),axis=0))
        assert len(a)==horizontal+vertical
        assert np.sum(a[:,0]*b[:,1]-a[:,1]*b[:,0])==8*np.count_nonzero(labels)
        assert len(edge_set(r))==len(a)


@pytest.mark.parametrize('labels,visible,origin',[
    (np.zeros((0,2),np.uint16),np.ones((0,2),bool),(0,0)),
    (np.zeros((2,2),np.uint8),np.ones((2,2),bool),(0,0)),
    (np.zeros((2,2),np.uint16),np.ones((2,3),bool),(0,0)),
    (np.zeros((2,2),np.uint16),np.ones((2,2),np.uint8),(0,0)),
    (np.zeros((2,2),np.uint16),np.ones((2,2),bool),(0.,0)),
    (np.zeros((2,2),np.uint16),np.ones((2,2),bool),(True,0)),
    (np.zeros((2,2),np.uint16),np.ones((2,2),bool),(2**51,0)),
])
def test_malformed_input_rejected(labels,visible,origin):
    with pytest.raises(ValueError):measure(labels,visible,origin=origin)


def test_face_budget_stops_without_silent_truncation(monkeypatch):
    monkeypatch.setitem(probe.BOUNDARY_SPEC,'max_faces',3)
    with pytest.raises(ValueError,match='resource bound'):measure(np.ones((1,1),np.uint16))
