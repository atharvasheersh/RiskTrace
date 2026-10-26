"""Auditable one-head GAT, optional own-bank GRU, and causal snapshot builders."""
from __future__ import annotations

import hashlib
import inspect
import numpy as np
import torch
from scipy.spatial.distance import cdist
from torch import nn

from .core import ROOT


def snapshot_neighbors(z, active, kind, k, states, ids, seed):
    n=len(z)
    neighbors=np.repeat(np.arange(n)[:,None],k+1,axis=1)
    valid=np.zeros((n,k+1),bool);valid[:,0]=True
    live=np.array(sorted(np.flatnonzero(active),key=lambda i:ids[i]),dtype=int)
    if len(live)<2:return neighbors,valid
    if kind=="feature":distance=cdist(z[live],z[live],metric="sqeuclidean")
    elif kind=="exogenous":distance=(states[live,None]!=states[None,live]).astype(float)
    elif kind=="random":distance=np.random.default_rng(seed).random((len(live),len(live)))
    else:raise ValueError(kind)
    np.fill_diagonal(distance,np.inf)
    count=min(k,len(live)-1)
    chosen=np.argsort(distance,axis=1,kind="stable")[:,:count]
    neighbors[live,1:count+1]=live[chosen];valid[live,1:count+1]=True
    return neighbors,valid


def prepare_graph(seq,kind,k,seed):
    h=hashlib.sha256()
    h.update(inspect.getsource(snapshot_neighbors).encode())
    for value in [seq["x"].numpy().tobytes(),seq["active"].numpy().tobytes(),
                  "|".join(seq["ids"]).encode(),seq["states"].astype("U2").tobytes(),f"{kind}:{k}:{seed if kind=='random' else 0}".encode()]:h.update(value)
    path=ROOT/"results/cache/graphs"/(h.hexdigest()[:24]+".npz")
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        with np.load(path) as data:neighbors,valid=data["neighbors"],data["valid"]
    else:
        pairs=[snapshot_neighbors(z,a,kind,k,s,seq["ids"],seed+q) for q,(z,a,s) in enumerate(
            zip(seq["x"].numpy(),seq["active"].numpy(),seq["states"]))]
        neighbors=np.array([p[0] for p in pairs]);valid=np.array([p[1] for p in pairs])
        np.savez_compressed(path,neighbors=neighbors,valid=valid)
    seq["neighbors"],seq["edge_valid"]=torch.tensor(neighbors),torch.tensor(valid)
    seq["graph_sha256"]=hashlib.sha256(neighbors.tobytes()+valid.tobytes()).hexdigest()
    return seq


class GraphTemporal(nn.Module):
    def __init__(self,family,hidden,k,positive_weight,seed):
        super().__init__()
        self.family,self.hidden,self.k,self.positive_weight,self.seed=family,hidden,k,positive_weight,seed
        self.kind="random" if family.endswith("random") else "exogenous" if family.endswith("exogenous") else "feature"
        self.project=nn.Linear(5,hidden,bias=False)
        self.a_query=nn.Parameter(torch.empty(hidden));self.a_source=nn.Parameter(torch.empty(hidden))
        nn.init.normal_(self.a_query,std=.1);nn.init.normal_(self.a_source,std=.1)
        self.cell=nn.GRUCell(hidden,hidden) if family!="gat" else None
        self.output=nn.Linear(hidden,1)
        self.metadata=dict(family=family,hidden=hidden,k=k,kind=self.kind,positive_weight=positive_weight,seed=seed)

    def attend(self,query,messages,valid,edge_mask=None):
        score=torch.nn.functional.leaky_relu((query*self.a_query).sum(-1)[:,None]
                     +(messages*self.a_source).sum(-1),negative_slope=.2)
        weights=torch.softmax(score.masked_fill(~valid,-1e9),dim=-1)
        if edge_mask is not None:
            weights=weights*edge_mask
            weights=weights/weights.sum(-1,keepdim=True).clamp_min(1e-12)
        embedding=torch.nn.functional.elu((weights[:,:,None]*messages).sum(1))
        return embedding,weights

    def local_step(self,z_target,z_neighbors,previous,valid=None,edge_mask=None):
        query=self.project(z_target.reshape(1,5))
        messages=self.project(z_neighbors).reshape(1,-1,self.hidden)
        if valid is None:valid=torch.ones(messages.shape[:2],dtype=torch.bool)
        embedding,weights=self.attend(query,messages,valid,edge_mask)
        hidden=self.cell(embedding,previous.reshape(1,self.hidden)) if self.cell is not None else embedding
        return self.output(hidden).squeeze(),hidden.squeeze(0),weights.squeeze(0)

    def forward(self,seq,return_states=False):
        h=torch.zeros(len(seq["ids"]),self.hidden)
        logits,states=[],[]
        for q,z in enumerate(seq["x"]):
            h=h*~seq["reset"][q,:,None]
            projected=self.project(z)
            embedding,_=self.attend(projected,projected[seq["neighbors"][q]],seq["edge_valid"][q])
            h=(self.cell(embedding,h) if self.cell is not None else embedding)*seq["active"][q,:,None]
            logits.append(self.output(h).squeeze(-1))
            if return_states:states.append(h)
        return (torch.stack(logits),torch.stack(states)) if return_states else torch.stack(logits)
