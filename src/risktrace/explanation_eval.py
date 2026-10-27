"""Vectorized conditional/pipeline financial audits and edge-mask explanations."""
from __future__ import annotations

import hashlib
import itertools
import json
import time

import numpy as np
import pandas as pd
import torch
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist

from .analysis import load_analysis,transform
from .audit import RAW,COL,GROUPS,feature_array,financially_valid,replace_groups,ranking_agreement
from .core import ROOT,write_json
from .graph_models import prepare_graph
from .holdout import load_checkpoint,require_frozen_plan
from .predictive import role_frame
from .temporal import sequence

SUBSETS=[s for size in [1,2,3] for s in itertools.combinations(GROUPS,size)]


def parameter_hash(model):
    return hashlib.sha256(b"".join(t.detach().numpy().tobytes() for t in model.state_dict().values())).hexdigest()


def readout(model,embedding,previous):
    h=model.cell(embedding,previous) if model.cell is not None else embedding
    return torch.sigmoid(model.output(h).squeeze(-1)-np.log(model.positive_weight)),h


def target_neighbors(changed_z,original_z,active,targets,k):
    # Sorted global CERT indices preserve the full builder's deterministic tie rule.
    live=np.flatnonzero(active)
    distance=cdist(changed_z,original_z[live],metric="sqeuclidean")
    position={i:j for j,i in enumerate(live)}
    for row,i in enumerate(targets):distance[row,position[i]]=np.inf
    count=min(k,len(live)-1)
    neighbors=np.repeat(np.asarray(targets)[:,None],k+1,axis=1)
    valid=np.zeros(neighbors.shape,bool);valid[:,0]=True
    neighbors[:,1:count+1]=live[np.argsort(distance,axis=1,kind="stable")[:,:count]]
    valid[:,1:count+1]=True
    return torch.tensor(neighbors),torch.tensor(valid)


def edited_probabilities(model,seq,states,forecast,edit,targets,changed_z,rebuild):
    targets=np.asarray(targets)
    changed_z=np.asarray(changed_z,dtype=np.float32)
    neighbors=seq["neighbors"][edit,targets]
    valid=seq["edge_valid"][edit,targets]
    if rebuild and model.kind=="feature":
        neighbors,valid=target_neighbors(changed_z,seq["x"][edit].numpy(),seq["active"][edit].numpy(),targets,model.k)
    messages=seq["x"][edit,neighbors].clone()
    z=torch.tensor(changed_z,dtype=torch.float32)
    same=neighbors.eq(torch.tensor(targets)[:,None])
    messages=torch.where(same[:,:,None],z[:,None,:],messages)
    with torch.no_grad():
        previous=torch.zeros(len(targets),model.hidden) if edit==0 else states[edit-1,targets].clone()
        previous=previous*~seq["reset"][edit,targets,None]
        embedding,_=model.attend(model.project(z),model.project(messages),valid)
        probability,h=readout(model,embedding,previous)
        for q in range(edit+1,forecast+1):
            h=h*~seq["reset"][q,targets,None]
            zq=seq["x"][q]
            embedding,_=model.attend(model.project(zq[targets]),model.project(zq[seq["neighbors"][q,targets]]),seq["edge_valid"][q,targets])
            probability,h=readout(model,embedding,h)
            h=h*seq["active"][q,targets,None]
    changed=[]
    for a,b,va,vb in zip(neighbors.numpy(),seq["neighbors"][edit,targets].numpy(),valid.numpy(),seq["edge_valid"][edit,targets].numpy()):
        changed.append(len(set(a[va])^set(b[vb])))
    return probability.numpy(),np.array(changed)


def edge_explanations(model,seq,states,q,targets,row_ids,spec):
    targets=np.asarray(targets)
    with torch.no_grad():
        query=model.project(seq["x"][q,targets])
        messages=model.project(seq["x"][q,seq["neighbors"][q,targets]])
        valid=seq["edge_valid"][q,targets]
        previous=torch.zeros(len(targets),model.hidden) if q==0 else states[q-1,targets].clone()
        previous=previous*~seq["reset"][q,targets,None]
        embedding,attention=model.attend(query,messages,valid)
        original,_=readout(model,embedding,previous)
        original_class=original.ge(.5).float()
    mask_logits=torch.nn.Parameter(torch.zeros(len(targets),model.k))
    optimizer=torch.optim.Adam([mask_logits],lr=spec["edge_mask_learning_rate"])
    for step in range(spec["edge_mask_steps"]):
        optimizer.zero_grad()
        gate=torch.sigmoid(mask_logits)
        full=torch.cat([torch.ones(len(targets),1),gate],1)
        embedding,_=model.attend(query,messages,valid,full)
        probability,_=readout(model,embedding,previous)
        fidelity=torch.nn.functional.binary_cross_entropy(probability.clamp(1e-7,1-1e-7),original_class,reduction="none")
        entropy=-(gate*torch.log(gate.clamp_min(1e-7))+(1-gate)*torch.log((1-gate).clamp_min(1e-7))).mean(1)
        objective=(fidelity+spec["edge_mask_size_penalty"]*gate.mean(1)+spec["edge_mask_entropy_penalty"]*entropy).sum()
        objective.backward();optimizer.step()
    scores={"attention":attention[:,1:].numpy(),"GNNExplainer_style_edge_mask":torch.sigmoid(mask_logits).detach().numpy()}
    scores["random"]=np.array([np.random.default_rng(int(hashlib.sha256((r+":edges").encode()).hexdigest()[:8],16)).random(model.k) for r in row_ids])
    output=[]
    for method,score in scores.items():
        score=np.where(valid[:,1:].numpy(),score,-np.inf)
        chosen=np.argsort(-score,axis=1,kind="stable")[:,:min(spec["edge_budget"],model.k)]
        keep=torch.zeros(len(targets),model.k+1);keep[:,0]=1
        for row in range(len(targets)):keep[row,torch.tensor(chosen[row]+1)]=1
        delete=1-keep;delete[:,0]=1
        with torch.no_grad():
            emb,_=model.attend(query,messages,valid,keep);sufficient,_=readout(model,emb,previous)
            emb,_=model.attend(query,messages,valid,delete);removed,_=readout(model,emb,previous)
        for row,key in enumerate(row_ids):
            output.append(dict(row_id=key,method=method,edge_budget=min(spec["edge_budget"],model.k),
                               original_probability=float(original[row]),necessity=float(original[row]-removed[row]),
                               sufficiency_gap=float(original[row]-sufficient[row]),
                               selected_neighbor_certs=";".join(seq["ids"][j] for j in seq["neighbors"][q,targets[row],chosen[row]+1].numpy())))
    return output


def donor_for(row,candidates):
    eligible=candidates.loc[candidates.BKCLASS.eq(row.BKCLASS)&candidates.CERT.ne(row.CERT)
                            &candidates.ASSET.between(row.ASSET/2,row.ASSET*2)].copy()
    if not len(eligible):return None
    eligible["distance"]=np.abs(np.log(eligible.ASSET/row.ASSET))
    eligible=eligible.sort_values(["distance","CERT"]).head(8)
    number=int(hashlib.sha256((row.row_id+":donor").encode()).hexdigest()[:8],16)%len(eligible)
    return eligible.iloc[number]


def financial_audit(model,seq,states,panel,test,prep,spec,seed,output):
    frame=panel.set_index(["report_date","CERT"],drop=False)
    training=panel.loc[panel.row_id.isin(set(output["train_keys"]))]
    training_z=transform(training,prep)
    tree=cKDTree(training_z)
    minimum,maximum=training[prep["features"]].min().to_numpy(),training[prep["features"]].max().to_numpy()
    cases,invalid=[],[]
    with torch.no_grad():base_logits=model(seq)
    base_probability=torch.sigmoid(base_logits-np.log(model.positive_weight)).numpy()
    threshold=output["threshold"]
    for forecast_date,group in test.groupby("report_date",sort=True):
        forecast=seq["dates"].index(forecast_date)
        if output.get("sample"):
            group=group.assign(order=group.row_id.map(lambda r:hashlib.sha256(r.encode()).hexdigest())).sort_values("order").head(spec["sensitivity_rows_per_quarter"])
        for lag in spec["edit_lags_quarters"]:
            edit=forecast-lag
            targets,originals,donors,rows,donor_ids=[],[],[],[],[]
            if edit<0:continue
            candidates=panel.loc[panel.report_date.eq(seq["dates"][edit])&panel.usable_financials&~panel.already_failed]
            for row in group.itertuples():
                i=seq["ids"].index(row.CERT)
                if not seq["active"][edit,i]:
                    invalid.append(dict(row_id=row.row_id,lag=lag,seed=seed,subset="not_attempted",reason="historical report unavailable/unusable"));continue
                original=frame.loc[(seq["dates"][edit],row.CERT)]
                donor=donor_for(original,candidates)
                if donor is None:
                    invalid.append(dict(row_id=row.row_id,lag=lag,seed=seed,subset="not_attempted",reason="no matched donor"));continue
                targets.append(i);originals.append(original[RAW].to_numpy(float));donors.append(donor[RAW].to_numpy(float));rows.append(row);donor_ids.append(donor.CERT)
            if not targets:continue
            targets=np.array(targets);originals=np.array(originals);donors=np.array(donors)
            probability=base_probability[forecast,targets]
            response=np.full((len(targets),7,2),np.nan)
            edges=np.zeros(len(targets),int);outside=np.zeros(len(targets),int);distance=np.zeros(len(targets))
            original_distance=tree.query(seq["x"][edit,targets].numpy())[0]
            for subset_index,subset in enumerate(SUBSETS):
                changes=np.array([replace_groups(a,b,subset) for a,b in zip(originals,donors)])
                valid=np.array([financially_valid(r) for r in changes])
                for j in np.flatnonzero(~valid):
                    invalid.append(dict(row_id=rows[j].row_id,lag=lag,seed=seed,subset="+".join(subset),reason="financial accounting/range constraint"))
                if not valid.any():continue
                features=feature_array(changes[valid]);z=(features-prep["mean"])/prep["scale"]
                a,_=edited_probabilities(model,seq,states,forecast,edit,targets[valid],z,False)
                b,changed=edited_probabilities(model,seq,states,forecast,edit,targets[valid],z,True)
                response[valid,subset_index,0]=a;response[valid,subset_index,1]=b
                edges[valid]=np.maximum(edges[valid],changed)
                outside[valid]=np.maximum(outside[valid],((features<minimum)|(features>maximum)).sum(1))
                distance[valid]=np.maximum(distance[valid],tree.query(z)[0])
            for j,row in enumerate(rows):
                observed=np.isfinite(response[j,:,0])
                if not observed.any():continue
                complete=bool(observed.all())
                rec=dict(row_id=row.row_id,CERT=row.CERT,report_date=str(forecast_date.date()),seed=seed,
                         lag=lag,donor=donor_ids[j],original_probability=float(probability[j]),
                         valid_subsets=int(observed.sum()),complete_group_audit=complete,
                         mean_gap=float(np.abs(response[j,observed,0]-response[j,observed,1]).mean()),
                         max_gap=float(np.abs(response[j,observed,0]-response[j,observed,1]).max()),
                         max_changed_target_edges=int(edges[j]),outside_training_features=int(outside[j]),
                         nearest_training_original=float(original_distance[j]),max_nearest_training_edited=float(distance[j]),
                         any_paired_alert_disagreement=bool(((response[j,observed,0]>threshold)!=(response[j,observed,1]>threshold)).any()))
                for m,subset in enumerate(SUBSETS):
                    tag="_".join(subset)
                    rec[f"conditional_p_{tag}"]=float(response[j,m,0]);rec[f"pipeline_p_{tag}"]=float(response[j,m,1])
                if complete:
                    scores=np.abs(probability[j]-response[j,:3,:].T)
                    top=np.argmax(scores,axis=1)
                    rec.update(top1_disagrees=bool(top[0]!=top[1]),ranking_spearman=ranking_agreement(scores[0],scores[1]),
                               ranking_negligible=bool(scores.max()<1e-6))
                    for m,label in enumerate(["conditional","pipeline"]):
                        rec[f"{label}_top1"]=GROUPS[top[m]]
                        rec[f"{label}_necessity"]=float(probability[j]-response[j,top[m],m])
                        rec[f"{label}_sufficiency_gap"]=float(probability[j]-response[j,5-top[m],m])
                cases.append(rec)
            print(f"financial audit seed={seed} {forecast_date.date()} lag={lag}: {len(targets)} donor-matched cases",flush=True)
    return pd.DataFrame(cases),pd.DataFrame(invalid,columns=["row_id","lag","seed","subset","reason"])


def run_explanations():
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    plan=require_frozen_plan()
    panel,roles,preprocessing,meta=load_analysis()
    test=role_frame(panel,roles,"final","test")
    fit=role_frame(panel,roles,"final","train")
    spec=plan["settings"]["explanations"]
    records=json.loads((ROOT/"results/final_evaluation/fit_manifest.json").read_text())
    output=ROOT/"results/explanations";output.mkdir(parents=True,exist_ok=True)
    case_frames,invalid_frames,edge_rows,logs=[],[],[],[]
    for seed in [spec["primary_seed"]]+spec["additional_seeds"]:
        record=next(r for r in records if r["report_label"]=="gat_gru" and r["seed"]==seed)
        model=load_checkpoint(record)
        for p in model.parameters():p.requires_grad_(False)
        before=parameter_hash(model)
        seq=sequence(panel,preprocessing["final"],test.report_date.max())
        prepare_graph(seq,model.kind,model.k,seed)
        with torch.no_grad():_,states=model(seq,True)
        start=time.perf_counter()
        if seed==spec["primary_seed"]:
            for date,group in test.groupby("report_date",sort=True):
                q=seq["dates"].index(date);targets=[seq["ids"].index(c) for c in group.CERT]
                edge_rows.extend(edge_explanations(model,seq,states,q,targets,group.row_id.tolist(),spec))
                print(f"edge explanations {date.date()}: {len(group)} targets",flush=True)
        cases,bad=financial_audit(model,seq,states,panel,test,preprocessing["final"],spec,seed,
                   dict(sample=seed!=spec["primary_seed"],train_keys=fit.row_id,
                        threshold=plan["seed_alert_thresholds"]["gat_gru"][str(seed)]))
        assert parameter_hash(model)==before
        case_frames.append(cases);invalid_frames.append(bad)
        logs.append(dict(seed=seed,parameter_sha256=before,parameters_unchanged=True,cases=len(cases),
                         invalid_records=len(bad),seconds=time.perf_counter()-start,
                         target="individual fitted seed model, not the predictive ensemble"))
    cases=pd.concat(case_frames);invalid=pd.concat(invalid_frames);edges=pd.DataFrame(edge_rows)
    controls=[]
    for family in spec["null_controls"]+["gat_gru_other_k"]:
        record=next(r for r in records if r["report_label"]==family and r["seed"]==spec["primary_seed"])
        model=load_checkpoint(record)
        for p in model.parameters():p.requires_grad_(False)
        before=parameter_hash(model)
        seq=sequence(panel,preprocessing["final"],test.report_date.max());prepare_graph(seq,model.kind,model.k,model.seed)
        with torch.no_grad():_,states=model(seq,True)
        threshold_family="gat_gru" if family=="gat_gru_other_k" else family
        c,bad=financial_audit(model,seq,states,panel,test,preprocessing["final"],spec,spec["primary_seed"],
                   dict(sample=True,train_keys=fit.row_id,threshold=plan["seed_alert_thresholds"][threshold_family][str(spec["primary_seed"])]))
        assert parameter_hash(model)==before
        if family in spec["null_controls"]:assert c.max_gap.eq(0).all()
        c["family"]=family;controls.append(c)
        logs.append(dict(family=family,seed=spec["primary_seed"],parameters_unchanged=True,
                         null_gap_verified=family in spec["null_controls"],cases=len(c),invalid_records=len(bad)))
    pd.concat(controls).to_csv(output/"control_financial_cases.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    cases.to_csv(output/"financial_cases.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    invalid.to_csv(output/"invalid_attempts.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    edges.to_csv(output/"edge_cases.csv.gz",index=False,compression={"method":"gzip","mtime":0})
    cases.groupby(["seed","lag"]).agg(cases=("row_id","size"),mean_gap=("mean_gap","mean"),max_gap=("max_gap","max"),
          complete_audits=("complete_group_audit","sum"),top1_disagreement=("top1_disagrees","mean"),
          alert_disagreement=("any_paired_alert_disagreement","mean"),outside_range=("outside_training_features",lambda v:(v>0).mean())).to_csv(output/"financial_summary.csv")
    edges.groupby("method").agg(cases=("row_id","size"),necessity=("necessity","mean"),sufficiency_gap=("sufficiency_gap","mean")).to_csv(output/"edge_summary.csv")
    write_json(output/"run_manifest.json",dict(dataset_id=meta["dataset_id"],plan_sha256=hashlib.sha256((ROOT/"docs/final_analysis_plan.json").read_bytes()).hexdigest(),runs=logs,
        caveats=["GNNExplainer-style edge-only optimization adaptation, not a full benchmark reproduction",
                 "Financial groups and edge explanations have different units and are not cross-ranked",
                 "Valid accounting and range support do not establish economic/causal plausibility",
                 "Efficient own-bank replay is exact for this architecture; global spillovers are not measured"]))
