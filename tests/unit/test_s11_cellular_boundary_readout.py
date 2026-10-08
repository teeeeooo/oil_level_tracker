import numpy as np
from tests.diagnostics import s11_cellular_boundary_readout as model

def test_no_current_edge_cannot_gain_from_a_region_score():
    features=np.zeros((80,80,3)); features[:40,:,0]=10; features[:,:,2]=1
    valid=np.ones((80,80),bool)
    views=[dict(sector=s,measurement=model.measure_sector(features,valid,
        x_range=[s*16,(s+1)*16],current_y=40)) for s in range(5)]
    assert model.score_candidate(views)==0
    features[39:42,:,1]=1
    views=[dict(sector=s,measurement=model.measure_sector(features,valid,
        x_range=[s*16,(s+1)*16],current_y=40)) for s in range(5)]
    assert model.score_candidate(views)>0

def test_gradient_validity_cannot_be_replaced_by_available_region_pixels():
    features=np.ones((80,80,3)); features[:40,:,0]=10; features[38:44,:,2]=0
    r=model.measure_sector(features,np.ones((80,80),bool),x_range=[0,80],current_y=40)
    assert r['status']=='UNAVAILABLE' and r['relative_edge'] is None

def test_constant_frame_is_safe_and_coordinate_is_not_relocated():
    f,v=model.cellular_map(np.full((80,80,3),120,np.uint8),np.ones((80,80),bool))
    r=model.measure_sector(f,v,x_range=[20,60],current_y=40.25)
    assert r['current_y']==40.25 and r['relative_edge']==0
    assert not model.SPEC['physical_identity_sufficient']
