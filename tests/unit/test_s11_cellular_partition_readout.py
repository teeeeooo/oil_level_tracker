from __future__ import annotations
import math
import numpy as np
import pytest
from tests.diagnostics import s11_cellular_basin_readout as base
from tests.diagnostics import s11_cellular_partition_readout as revised

@pytest.mark.parametrize('counts, expected', [([5,5],1),([0,10],0),([10,0],0),([1,99],math.sqrt(.0396))])
def test_extent_support_analytic(counts, expected):
    assert revised.extent_support(counts) == pytest.approx(expected)

@pytest.mark.parametrize('a,b,expected', [([1],[0],1),([0],[1],-1),([1],[1],0),([0,1],[0,1],0)])
def test_rank_biserial_ties(a,b,expected):
    assert base.rank_biserial(a,b) == expected

def test_imbalance_cannot_beat_substantial_separation_by_tail_purity_alone():
    assert 1*revised.extent_support([99,1]) < .7*revised.extent_support([50,50])
    assert revised.extent_support([3,7]) == revised.extent_support([30,70])

def test_constant_image_has_no_cellular_authority_and_is_immutable():
    image = np.full((80,80,3), 120, np.uint8); mask = np.ones((80,80),bool)
    before, valid_before = image.copy(), mask.copy()
    energy, valid = base.cellular_map(image, mask)
    assert np.allclose(energy[valid],0,atol=1e-10)
    assert np.array_equal(image,before) and np.array_equal(mask,valid_before)
    assert base.SPEC['physical_identity_sufficient'] is False
    assert revised.SPEC['physical_identity_sufficient'] is False

def test_masks_are_unavailable_not_negative_and_hide_invalid_pixels():
    image = np.full((80,80,3),120,np.uint8); mask = np.ones((80,80),bool)
    mask[20:40,20:40] = False
    alternate = image.copy(); alternate[~mask] = [255,0,255]
    a,av = base.cellular_map(image,mask); b,bv = base.cellular_map(alternate,mask)
    assert np.array_equal(av,bv) and np.array_equal(a,b)
    z,zv = base.cellular_map(image,np.zeros_like(mask))
    r = base.measure_sector(z,zv,x_range=[0,80],current_y=40)
    assert r['status']=='UNAVAILABLE' and r['score'] is None

def test_cellular_partition_and_internal_gap_control():
    energy = np.zeros((80,80),float); energy[:40] = 10
    energy[14:18] = 0  # an internal gap is not the lower material boundary
    valid = np.ones((80,80),bool)
    def at(y):
        views = [dict(sector=s,measurement=base.measure_sector(energy,valid,
                     x_range=[s*16,(s+1)*16],current_y=y)) for s in range(5)]
        return revised.score_candidate(views)
    assert at(40) > at(14) and at(40) > at(70)
    # The same raster can be a printed texture. Pixel evidence cannot disambiguate it.
    assert at(40) > 0 and not revised.SPEC['physical_identity_sufficient']

@pytest.mark.parametrize('y', [-1,80,float('nan'),True])
def test_invalid_coordinate_rejected(y):
    with pytest.raises(ValueError):
        base.measure_sector(np.zeros((80,80)),np.ones((80,80),bool),x_range=[0,40],current_y=y)

def test_distinct_sectors_and_ties_remain_explicit():
    available = dict(status='AVAILABLE',score=.5,counts=[20,20])
    assert revised.score_candidate([dict(sector=0,measurement=available)]) is None
    with pytest.raises(ValueError):
        revised.score_candidate([dict(sector=0,measurement=available)]*3)
    rows = [dict(candidate_input_index=i,score=.5) for i in range(2)]
    assert base.select_candidate(rows)==[0,1]
    assert base.select_candidate([dict(candidate_input_index=0,score=0)])==[]

def test_cellular_energy_distinguishes_two_direction_texture_from_line_interior():
    y,x = np.mgrid[:80,:80]
    texture = np.clip(120+50*np.sin(x*.6)*np.sin(y*.7),0,255).astype(np.uint8)
    line = np.where(y<40,60,180).astype(np.uint8)
    valid = np.ones((80,80),bool)
    a,av = base.cellular_map(np.repeat(texture[:,:,None],3,axis=2),valid)
    b,bv = base.cellular_map(np.repeat(line[:,:,None],3,axis=2),valid)
    assert np.median(a[20:60,20:60]) > 1
    assert np.max(b[20:60,20:60]) < 1e-6

@pytest.mark.parametrize('image,mask', [(np.zeros((4,4,3),np.uint8),np.ones((4,4),bool)),
    (np.zeros((10,10,3)),np.ones((10,10),bool)),
    (np.zeros((10,10,3),np.uint8),np.ones((10,10),np.uint8))])
def test_invalid_rasters_rejected(image,mask):
    with pytest.raises(ValueError): base.cellular_map(image,mask)
