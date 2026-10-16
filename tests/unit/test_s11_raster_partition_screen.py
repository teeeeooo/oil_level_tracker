"""Synthetic contracts, not field efficacy, for CRW-1."""
from copy import deepcopy
import numpy as np
import pytest
from tests.diagnostics.s11_raster_partition_screen import (
    observe, paired_gradient, paired_partition, peak_groups, shared_measurements,
)


def fixture(y=30.0, origin=(0,0), native=False):
    sectors = [{"sector":s,"source_x_range":[origin[0]+s*10,origin[0]+(s+1)*10]}
               for s in range(5)]
    path = {"reason":"no_captured_native_path","sectors":[]}
    if native:
        path = {"reason":"native_generator_path","sectors":[
            {**s,"path_source_y":y+origin[1]+s["sector"]-2} for s in sectors]}
    row = {"canonical_y":y+origin[1],"candidate_input_index":7,"source":"synthetic",
           "sectors":sectors,"path_aligned":path}
    gray = np.full((64,50),40,dtype=np.uint8)
    gray[30:]=160
    return gray,np.ones_like(gray,dtype=bool),list(origin),row


def observed(args, key="synthetic-A"):
    return observe(*args,3,frame_key=key)


@pytest.mark.parametrize("reverse",[False,True])
def test_step_both_polarities_preserves_ties_and_no_authority(reverse):
    args = fixture()
    if reverse:
        args[0][:] = 255-args[0]
    before = [args[0].copy(),args[1].copy(),deepcopy(args[3])]
    out = observed(args)
    assert out["partition_sector_count"] == 5
    assert out["localized_sector_count"] == 5
    assert out["sectors"][0]["peak_groups"][0]["source_rows"] == [29,30]
    assert out["authority"] == "NONE" and not out["native_path_created"]
    assert not out["continuous_contour_qualified"]
    assert out["physical_role"] == "NOT_EVALUATED"
    assert np.array_equal(before[0],args[0]) and np.array_equal(before[1],args[1])
    assert before[2] == args[3]


@pytest.mark.parametrize("mode",["flat","ramp","stripe"])
def test_nonpartition_patterns(mode):
    gray,mask,origin,row = fixture()
    if mode=="flat": gray[:]=80
    elif mode=="ramp": gray[:]=np.arange(64,dtype=np.uint8)[:,None]*3
    else:
        gray[:]=40
        gray[28:33]=160
    out = observed((gray,mask,origin,row))
    assert out["partition_sector_count"] == 0
    if mode=="ramp":
        assert paired_partition(gray,mask,0,10,30,3)["integer_margin"] == 0
    if mode=="flat": assert out["localized_sector_count"] == 0

def test_matched_support_removes_horizontal_mask_confound():
    gray,mask,_,_ = fixture()
    gray[:,:25]=40
    gray[:,25:]=160
    mask[:30,:25]=False
    mask[30:,25:]=False
    out=paired_partition(gray,mask,0,50,30,3)
    assert out["status"] == "UNAVAILABLE_SUPPORT" and out["margin"] is None
    assert not paired_gradient(gray,mask,0,50,30)["available"]


@pytest.mark.parametrize("mode",["crop","mask","tiny"])
def test_unavailable_is_not_physical_absence(mode):
    gray,mask,_,_=fixture()
    y,x1=30,10
    if mode=="crop": y=2
    elif mode=="mask": mask[:]=False
    else: x1=2
    out=paired_partition(gray,mask,0,x1,y,3)
    assert out["status"].startswith("UNAVAILABLE")
    assert out["margin"] is None and "physical_role" not in out


def test_native_hints_do_not_become_new_native_truth():
    args=fixture(native=True)
    out=observed(args)
    assert [s["seed_source_y"] for s in out["sectors"]] == [28,29,30,31,32]
    assert out["canonical_y_unchanged"] == 30 and not out["native_path_created"]

def test_fractional_seed_and_translated_coordinates():
    out=observed(fixture(30.5,origin=(101,203)))
    assert out["canonical_y_unchanged"] == 233.5
    sector=out["sectors"][0]
    assert sector["search_source_rows"] == [230,237]
    assert sector["peak_groups"][0]["source_rows"] == [232,233]


@pytest.mark.parametrize("values,expected,censored",[
    ([0,1,1,0],[[1,2]],[False]),
    ([1,1,0],[[0,1]],[True]),
    ([0,1,0,2,0],[[1],[3]],[False,False]),
    ([0,None,1,0],[[2]],[True]),
    ([0,0,0],[],[]),
])
def test_alternatives_and_censoring(values,expected,censored):
    profile=[{"local_y":i,"available":v is not None,"value":v}
             for i,v in enumerate(values)]
    result=peak_groups(profile)
    assert [g["local_rows"] for g in result] == expected
    assert [g["search_censored"] for g in result] == censored


def test_shared_pixels_are_not_independent_votes():
    out=observed(fixture())
    peer=deepcopy(out)
    peer["input_source"]="renamed-descendant"
    shared=shared_measurements(out,peer)
    assert len(shared)==5
    assert all(s["relationship"]=="SAME_MEASUREMENT_NOT_INDEPENDENT" for s in shared)


@pytest.mark.parametrize("field",["frame_key","gray_sha256","visible_sha256","band","origin"])
def test_cross_frame_or_raster_alias_rejected(field):
    out=observed(fixture())
    peer=deepcopy(out)
    peer["raster_binding"][field]="different"
    with pytest.raises(ValueError,match="different raster"):
        shared_measurements(out,peer)


@pytest.mark.parametrize("field",["dtype","mask","band","sectors","y","frame"])
def test_invalid_input_rejected(field):
    gray,mask,origin,row=fixture()
    band,key=3,"synthetic-A"
    if field=="dtype": gray=gray.astype(float)
    elif field=="mask": mask=mask.astype(np.uint8)
    elif field=="band": band=0
    elif field=="sectors": row["sectors"][4]["sector"]=3
    elif field=="y": row["canonical_y"]=float("nan")
    else: key=""
    with pytest.raises(ValueError):
        observe(gray,mask,origin,row,band,frame_key=key)


def test_edge_and_context_sample_rows_are_disjoint():
    gray,mask,_,_=fixture()
    result=paired_partition(gray,mask,0,10,30,3)
    assert not {29,31}.intersection(y for rows in result["rows"] for y in rows)


@pytest.mark.parametrize("corrupt",[False,True])
def test_direct_loop_oracle_with_corruption_control(tmp_path,corrupt):
    import gzip,json,cv2
    from tests.diagnostics.s11_raster_partition_verify import verify
    gray,mask,origin,row=fixture()
    cv2.imwrite(str(tmp_path/'frame.png'),gray)
    np.savez(tmp_path/'mask.npz',visible=mask)
    spec={'rgb_format':'RGB_PNG','rgb':{'path':'frame.png'},
          'visibility':{'path':'mask.npz'},'mask_key':'visible','origin':origin}
    prepared=tmp_path/'docs/50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepared.json'
    prepared.parent.mkdir(parents=True)
    prepared.write_text(json.dumps({'frames':{'synthetic-A':spec}}))
    witness=observed((gray,mask,origin,row))
    if corrupt:
        witness['sectors'][0]['peak_groups'][0]['partitions'][0]['integer_margin']+=1
    data={'inputs':{},'units':[{'id':'one','raw_frame_id':'synthetic-A','raster_witness':witness}]}
    path=tmp_path/'readout.json.gz'
    path.write_bytes(gzip.compress(json.dumps(data).encode()))
    result=verify(tmp_path,path)
    assert (result['error_count']>0)==corrupt
