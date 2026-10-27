"""Prespecified sparse-event, bank/time robustness summaries and case packets."""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from .analysis import load_analysis
from .core import ROOT,write_json
from .holdout import require_frozen_plan
from .metrics import prediction_metrics


def institution_components(panel):
    parent={c:c for c in panel.CERT.unique()}
    def find(c):
        while parent[c]!=c:
            parent[c]=parent[parent[c]];c=parent[c]
        return c
    for _,g in panel.groupby("RSSDID"):
        ids=sorted(g.CERT.unique())
        for c in ids[1:]:parent[find(c)]=find(ids[0])
    return {c:find(c) for c in parent}


def crossed_draws(frame,components,replicates,seed):
    bank=frame.CERT.map(components).astype(str)
    time=pd.to_datetime(frame.report_date).dt.year
    bi,banks=pd.factorize(bank,sort=True);ti,times=pd.factorize(time,sort=True)
    rng=np.random.default_rng(seed)
    for _ in range(replicates):
        bw=np.bincount(rng.integers(len(banks),size=len(banks)),minlength=len(banks))
        tw=np.bincount(rng.integers(len(times),size=len(times)),minlength=len(times))
        yield bw[bi]*tw[ti]


def weighted_metric(y,p,w,metric):
    total=w.sum()
    if total==0:return np.nan
    if metric=="brier":return float(np.average((y-p)**2,weights=w))
    if metric=="average_precision":
        if (w*y).sum()==0:return np.nan
        return float(average_precision_score(y,p,sample_weight=w))
    raise ValueError(metric)


def robustness_results():
    plan=require_frozen_plan();panel,_,_,meta=load_analysis()
    config=plan["settings"]["robustness"]
    components=institution_components(panel)
    directory=ROOT/"results/final_evaluation"
    table=pd.read_csv(directory/"results.csv")
    frames={name:pd.read_csv(directory/f"{name}_predictions.csv.gz",dtype={"CERT":str}) for name in table.model}
    for frame in frames.values():frame.sort_values("row_id",inplace=True);frame.reset_index(drop=True,inplace=True)
    first=next(iter(frames.values()))
    assert all(first.row_id.equals(f.row_id) for f in frames.values())
    weights=list(crossed_draws(first,components,config["paired_bootstrap_replicates"],config["seed"]))
    y=first.y.to_numpy(float)
    records=[]
    draws={}
    for name,frame in frames.items():
        for metric in ["average_precision","brier"]:
            values=np.array([weighted_metric(y,frame.probability.to_numpy(),w,metric) for w in weights])
            draws[(name,metric)]=values
            valid=values[np.isfinite(values)]
            records.append(dict(model=name,metric=metric,point=float(table.set_index("model").loc[name,metric]),
                                lower=float(np.quantile(valid,.025)) if len(valid) else None,
                                upper=float(np.quantile(valid,.975)) if len(valid) else None,
                                defined_draws=len(valid),undefined_draws=len(values)-len(valid),
                                status="exploratory percentile interval conditional on defined draws; coverage unverified"))
    pairs=[]
    for name in table.model:
        if name=="xgboost":continue
        for metric in ["average_precision","brier"]:
            difference=draws[(name,metric)]-draws[("xgboost",metric)]
            valid=difference[np.isfinite(difference)]
            pairs.append(dict(model=name,reference="xgboost",metric=metric,
                              point=float(table.set_index("model").loc[name,metric]-table.set_index("model").loc["xgboost",metric]),
                              lower=float(np.quantile(valid,.025)),upper=float(np.quantile(valid,.975)),defined_draws=len(valid)))
    output=ROOT/"results/robustness";output.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(records).to_csv(output/"crossed_intervals.csv",index=False)
    pd.DataFrame(pairs).to_csv(output/"paired_differences_vs_xgboost.csv",index=False)
    periods=[]
    for name,frame in frames.items():
        threshold=float(table.set_index("model").loc[name,"threshold"])
        for year,g in frame.groupby(pd.to_datetime(frame.report_date).dt.year):
            m,_=prediction_metrics(g,threshold);periods.append(dict(model=name,year=int(year),**m))
    pd.DataFrame(periods).to_csv(output/"calendar_period_results.csv",index=False)
    seed=pd.read_csv(directory/"seed_results.csv")
    seed.groupby("model").agg(seeds=("seed","size"),ap_min=("average_precision","min"),ap_max=("average_precision","max"),
                              brier_min=("brier","min"),brier_max=("brier","max")).to_csv(output/"seed_sensitivity.csv")
    financial=pd.read_csv(ROOT/"results/explanations/financial_cases.csv.gz",dtype={"CERT":str})
    primary=financial.loc[financial.seed.eq(plan["settings"]["explanations"]["primary_seed"])].copy()
    audit_intervals=[]
    for lag,g in primary.groupby("lag"):
        values=[]
        for w in crossed_draws(g,components,config["paired_bootstrap_replicates"],config["seed"]+int(lag)):
            values.append(np.average(g.mean_gap,weights=w) if w.sum() else np.nan)
        valid=np.array(values)[np.isfinite(values)]
        audit_intervals.append(dict(lag=int(lag),mean_gap=float(g.mean_gap.mean()),lower=float(np.quantile(valid,.025)),
                                    upper=float(np.quantile(valid,.975)),defined_draws=len(valid),bank_quarters=len(g)))
    pd.DataFrame(audit_intervals).to_csv(output/"financial_gap_intervals.csv",index=False)
    write_json(output/"method.json",dict(dataset_id=meta["dataset_id"],replicates=len(weights),
        institutions="connected CERT/RSSD components; no identity features enter models",time="calendar-year blocks",
        bootstrap="independently resample institutions and year blocks; multiply row counts; paired weights across models",
        interpretation="exploratory pigeonhole-style sensitivity, not a guaranteed nominal 95% CI for nonlinear rare-event AP",
        limitations=["Only four positive test banks and four calendar-year blocks (2025 partial)",
                     "Undefined zero-positive resamples are counted; AP quantiles condition on valid draws",
                     "Year blocking does not guarantee all serial/common-shock dependence captured",
                     "Seed ranges are sensitivity, not independent-data confidence intervals"],
        reference="Art B. Owen (2007), The pigeonhole bootstrap, https://arxiv.org/abs/0712.1111"))
    return table


def case_packets():
    plan=require_frozen_plan();panel,_,_,_=load_analysis()
    predictions={m:pd.read_csv(ROOT/f"results/final_evaluation/{m}_predictions.csv.gz",dtype={"CERT":str}) for m in ["xgboost","gat_gru"]}
    p=predictions["xgboost"];positive=p.loc[p.y.eq(1)]
    components=institution_components(panel)
    cases=[];trajectories=[]
    for cert,g in positive.groupby("CERT"):
        report=pd.to_datetime(g.report_date).max()
        row=panel.loc[panel.CERT.eq(cert)&panel.report_date.eq(report)].iloc[0]
        eligible=panel.loc[panel.report_date.eq(report)&panel.BKCLASS.eq(row.BKCLASS)
                           &panel.ASSET.between(row.ASSET/2,row.ASSET*2)&panel.label_12m.eq(0)
                           &panel.usable_financials&panel.label_mature_by_snapshot].copy()
        eligible=eligible.loc[eligible.CERT.map(components).ne(components[cert])]
        eligible["distance"]=np.abs(np.log(eligible.ASSET/row.ASSET))
        eligible=eligible.sort_values(["distance","CERT"])
        survivor=None if not len(eligible) else eligible.iloc[0].CERT
        cases.append(dict(CERT=cert,name=row.NAME,failure_date=str(row.failure_date.date()),
                          matched_survivor=survivor,matching_report=str(report.date()),
                          finance_review="pending Ayush case selection and interpretation; not claimed received",
                          evidence="revised-snapshot heldout model reconstruction; not a contemporaneously issued forecast"))
        for family,frame in predictions.items():
            subset=frame.loc[frame.CERT.isin([cert,survivor])&pd.to_datetime(frame.availability_date).lt(row.failure_date)
                              &pd.to_datetime(frame.report_date).le(report)].copy()
            subset["case_CERT"],subset["model"]=cert,family
            trajectories.append(subset)
    directory=ROOT/"results/case_studies";directory.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(cases).to_csv(directory/"proposed_case_register.csv",index=False)
    pd.concat(trajectories).to_csv(directory/"forecast_trajectories.csv",index=False)
    write_json(directory/"review_status.json",dict(status="technical packets prepared; finance interpretation and coauthor selection pending",
        matching="same pre-event report, same charter, within factor-two assets, nearest log assets, observed nonfailure horizon, exclude linked identity component",
        selection="retrospective illustrative case-control packets, separate from primary test-population evaluation",
        contacts_sent=False,author_approval_received=False,
        warning="Source revisions/assumed availability prevent a claim these predictions were issued prospectively"))
