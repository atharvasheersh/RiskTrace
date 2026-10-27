import numpy as np
import pandas as pd
import torch
import pytest
from risktrace.graph_models import GraphTemporal,snapshot_neighbors
from risktrace.temporal import deterministic
from risktrace.explanation_eval import edited_probabilities,target_neighbors
from risktrace.holdout import require_frozen_plan
from risktrace.robustness import crossed_draws,institution_components


def fixture_model(kind='feature'):
    deterministic(11)
    family='gat_gru' if kind=='feature' else 'gat_gru_'+kind
    model=GraphTemporal(family,8,2,10,11)
    x=torch.randn(3,4,5)
    ids=['a','b','c','d'];active=np.ones((3,4),bool);states=np.full((3,4),'AA')
    pairs=[snapshot_neighbors(z,a,kind,2,s,ids,11+q) for q,(z,a,s) in enumerate(zip(x.numpy(),active,states))]
    seq=dict(x=x,ids=ids,active=torch.tensor(active),reset=torch.zeros(3,4,dtype=torch.bool),
             neighbors=torch.tensor(np.array([p[0] for p in pairs])),edge_valid=torch.tensor(np.array([p[1] for p in pairs])))
    return model,seq


def test_target_shortcut_equals_complete_snapshot_rebuild_and_historical_replay():
    model,seq=fixture_model()
    with torch.no_grad():_,states=model(seq,True)
    target=1;changed=seq['x'][1,target].numpy()+2
    probability,_=edited_probabilities(model,seq,states,2,1,[target],changed[None],True)
    full=dict(seq);full['x']=seq['x'].clone();full['x'][1,target]=torch.tensor(changed)
    n,v=snapshot_neighbors(full['x'][1].numpy(),np.ones(4,bool),'feature',2,np.full(4,'AA'),seq['ids'],12)
    full['neighbors']=seq['neighbors'].clone();full['neighbors'][1]=torch.tensor(n)
    full['edge_valid']=seq['edge_valid'].clone();full['edge_valid'][1]=torch.tensor(v)
    with torch.no_grad():expected=torch.sigmoid(model(full)[2,target]-np.log(10)).item()
    assert np.isclose(probability[0],expected,rtol=1e-6,atol=1e-8)


def test_new_attention_model_null_graph_audits_have_zero_paired_gap():
    for kind in ['random','exogenous']:
        model,seq=fixture_model(kind)
        with torch.no_grad():_,states=model(seq,True)
        z=seq['x'][1,[0,1]].numpy()+1
        a,_=edited_probabilities(model,seq,states,2,1,[0,1],z,False)
        b,_=edited_probabilities(model,seq,states,2,1,[0,1],z,True)
        np.testing.assert_array_equal(a,b)


def test_no_test_evaluation_without_a_frozen_plan(tmp_path,monkeypatch):
    import risktrace.holdout as module
    monkeypatch.setattr(module,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='plan is required'):require_frozen_plan()


def test_uncertainty_keeps_shared_id_clusters_and_common_year_shocks():
    p=pd.DataFrame(dict(CERT=['a','b','b','c'],RSSDID=[1,1,2,3],report_date=['2022-03-31','2022-03-31','2023-03-31','2023-03-31']))
    components=institution_components(p)
    assert components['a']==components['b'] and components['a']!=components['c']
    for w in crossed_draws(p,components,10,11):assert w[0]==w[1]
