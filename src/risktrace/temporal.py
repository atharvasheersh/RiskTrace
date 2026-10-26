"""A shared-weight temporal baseline with explicit historical resets."""
from __future__ import annotations

import random
import numpy as np
import pandas as pd
import torch
from torch import nn

from .analysis import transform


def deterministic(seed, threads=2):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.set_num_threads(threads)
    torch.use_deterministic_algorithms(True)


def sequence(panel, preprocessing, end, selected_keys=()):
    p = panel.loc[panel.report_date.le(end)].copy()
    ids, dates = sorted(p.CERT.unique()), sorted(p.report_date.unique())
    ci, ti = {c:i for i,c in enumerate(ids)}, {t:i for i,t in enumerate(dates)}
    rows, banks = len(dates), len(ids)
    x = np.zeros((rows,banks,5),np.float32)
    active, reset, target = np.zeros((rows,banks),bool), np.ones((rows,banks),bool), np.zeros((rows,banks),bool)
    labels = np.zeros((rows,banks),np.float32)
    states=np.full((rows,banks),"",dtype="U2")
    mapping, keys = {}, set(selected_keys)
    z = transform(p,preprocessing)
    for offset, row in enumerate(p.itertuples()):
        q,i=ti[row.report_date],ci[row.CERT]
        good=bool(row.usable_financials and not row.already_failed)
        if good:x[q,i]=z[offset]
        active[q,i]=good;reset[q,i]=row.history_reset or not good
        target[q,i]=row.row_id in keys
        labels[q,i]=0 if pd.isna(row.label_12m) else row.label_12m
        states[q,i]=row.STALP
        mapping[row.row_id]=(q,i)
    return dict(x=torch.tensor(x),active=torch.tensor(active),reset=torch.tensor(reset),
                target=torch.tensor(target),y=torch.tensor(labels),mapping=mapping,ids=ids,dates=dates,states=states)


class TemporalBaseline(nn.Module):
    def __init__(self, hidden, positive_weight):
        super().__init__()
        self.cell=nn.GRUCell(5,hidden)
        self.output=nn.Linear(hidden,1)
        nn.init.zeros_(self.output.bias)
        self.hidden=hidden;self.positive_weight=positive_weight
        self.metadata=dict(family="gru",hidden=hidden,positive_weight=positive_weight)

    def forward(self, seq, return_states=False):
        h=torch.zeros(len(seq["ids"]),self.hidden)
        logits,states=[],[]
        for q,z in enumerate(seq["x"]):
            h=h*~seq["reset"][q,:,None]
            h=self.cell(z,h)*seq["active"][q,:,None]
            logits.append(self.output(h).squeeze(-1))
            if return_states:states.append(h)
        output=torch.stack(logits)
        return (output,torch.stack(states)) if return_states else output


def train_neural(family,candidate,seed,fit,panel,preprocessing,spec):
    deterministic(seed,spec["cpu_threads"])
    seq=sequence(panel,preprocessing,fit.report_date.max(),fit.row_id)
    y=seq["y"][seq["target"]]
    positive_weight=min(float((y==0).sum()/y.sum()),spec["neural"]["max_positive_weight"])
    if family=="gru":model=TemporalBaseline(candidate["hidden"],positive_weight)
    else:
        from .graph_models import GraphTemporal,prepare_graph
        model=GraphTemporal(family,candidate["hidden"],candidate["k"],positive_weight,seed)
        prepare_graph(seq,model.kind,model.k,seed)
    with torch.no_grad():
        model.output.bias.fill_(float(torch.log(positive_weight*y.mean()/(1-y.mean()))))
    optimizer=torch.optim.Adam(model.parameters(),lr=candidate["learning_rate"],weight_decay=spec["neural"]["weight_decay"])
    objective=nn.BCEWithLogitsLoss(pos_weight=torch.tensor(positive_weight))
    losses=[]
    for epoch in range(candidate["epochs"]):
        optimizer.zero_grad()
        logits=model(seq)
        loss=objective(logits[seq["target"]],y)
        if not torch.isfinite(loss):raise ValueError("Nonfinite training loss")
        loss.backward();nn.utils.clip_grad_norm_(model.parameters(),spec["neural"]["gradient_clip"]);optimizer.step()
        losses.append(float(loss.detach()))
    model.eval()
    return model,dict(loss=losses,positive_weight=positive_weight,epochs=len(losses),seed=seed,
                      graph_sha256=seq.get("graph_sha256"),
                      loss_labels=int(seq["target"].sum()),max_report=str(fit.report_date.max().date()),
                      probability_correction="subtract log(training positive_weight); no flexible posthoc calibrator")


def predict_neural(model,panel,evaluation,preprocessing):
    seq=sequence(panel,preprocessing,evaluation.report_date.max())
    if hasattr(model,"kind"):
        from .graph_models import prepare_graph
        prepare_graph(seq,model.kind,model.k,model.seed)
        model.evaluation_graph_sha256=seq["graph_sha256"]
    with torch.no_grad():
        logits=model(seq)-np.log(model.positive_weight)
        p=torch.sigmoid(logits).numpy()
    return np.array([p[seq["mapping"][key]] for key in evaluation.row_id])
