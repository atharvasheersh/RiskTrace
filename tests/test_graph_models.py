import numpy as np
import torch
from risktrace.graph_models import GraphTemporal,snapshot_neighbors
from risktrace.temporal import deterministic


def test_graph_excludes_future_inactive_nodes_and_is_permutation_equivariant():
    z=np.array([[0.,0.,0.,0.,0.],[1.,1.,1.,1.,1.],[999.,999.,999.,999.,999.]])
    active=np.array([True,True,False]);states=np.array(['AA','AA','BB']);ids=['a','b','future']
    for kind in ['feature','exogenous','random']:
        n,v=snapshot_neighbors(z,active,kind,1,states,ids,11)
        assert n[:2,1].tolist()==[1,0]
        permutation=np.array([1,2,0])
        nn,vv=snapshot_neighbors(z[permutation],active[permutation],kind,1,states[permutation],[ids[i] for i in permutation],11)
        for j,old in enumerate(permutation):
            np.testing.assert_array_equal(permutation[nn[j,vv[j]]],n[old,v[old]])


def test_local_replay_matches_batched_gat_gru_and_attention_normalizes():
    deterministic(11)
    m=GraphTemporal('gat_gru',8,1,10,11)
    x=torch.randn(3,2,5)
    sequence=dict(x=x,ids=['a','b'],reset=torch.zeros(3,2,dtype=torch.bool),active=torch.ones(3,2,dtype=torch.bool),
                  neighbors=torch.tensor([[[0,1],[1,0]]]*3),edge_valid=torch.ones(3,2,2,dtype=torch.bool))
    with torch.no_grad():
        logits,h=m(sequence,True)
        local,_,weights=m.local_step(x[2,0],x[2,[0,1]],h[1,0])
        torch.testing.assert_close(local,logits[2,0]);torch.testing.assert_close(weights.sum(),torch.tensor(1.))
        changed=x.clone();changed[-1]+=100
        torch.testing.assert_close(logits[:-1],m(dict(sequence,x=changed))[:-1])
