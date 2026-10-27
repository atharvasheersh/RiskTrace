"""Hash-gated final evaluation; called only after a committed analysis plan."""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime,timezone

import numpy as np
import pandas as pd
import yaml

from .analysis import load_analysis,sha
from .core import ROOT,write_json
from .metrics import alarm_threshold,calibration_table,prediction_metrics
from .predictive import code_commit,fit_condition,role_frame,settings

MODEL_FILES=["analysis.py","core.py","protocol.py","audit.py","metrics.py","predictive.py","temporal.py",
             "graph_models.py","holdout.py","explanation_eval.py","robustness.py"]


def text_sha(path):
    """Hash tracked text in canonical LF form; raw data/checkpoint hashes stay byte-exact."""
    return sha(path.read_text(encoding="utf8").encode("utf8"))


def source_fingerprint():
    return {name:text_sha(ROOT/"src/risktrace"/name) for name in MODEL_FILES}


def freeze_plan():
    _,_,_,data=load_analysis()
    selected=json.loads((ROOT/"results/predictive/selected_models.json").read_text())
    spec=yaml.safe_load((ROOT/"configs/final_evaluation.yaml").read_text())
    if set(spec["families"])-set(selected):raise ValueError("Development model selection incomplete")
    directory=ROOT/"results/final_evaluation"
    if (directory/"holdout_opening.json").exists():raise ValueError("Holdout already opened; no silent plan refreeze")
    seed_thresholds={}
    for family in ["gat_gru","gat_gru_random","gat_gru_exogenous","gru"]:
        p=pd.read_csv(ROOT/f"results/cache/{family}_validation_seeds.csv.gz")
        seed_thresholds[family]={str(seed):alarm_threshold(g.y,g.probability) for seed,g in p.groupby("seed")}
    plan=dict(status="frozen_before_first_test_performance",created_utc=datetime.now(timezone.utc).isoformat(),
              code_commit=code_commit(),source_hashes=source_fingerprint(),dataset_sha256=data["sha256"],
              split_sha256=data["split_keys_sha256"],
              selected_models_sha256=text_sha(ROOT/"results/predictive/selected_models.json"),
              experiments_sha256=text_sha(ROOT/"configs/experiments.yaml"),
              environment_lock_sha256=text_sha(ROOT/"uv.lock"),
              data_spec_sha256=text_sha(ROOT/"configs/data_spec.yaml"),
              splits_config_sha256=text_sha(ROOT/"configs/splits.yaml"),
              evaluation_config_sha256=text_sha(ROOT/"configs/final_evaluation.yaml"),
              settings=spec,seed_alert_thresholds=seed_thresholds,
              test_status="previously_counted_for_feasibility; performance_not_inspected",
              interpretation="exploratory sparse-event study; finance materiality and publication novelty unproved")
    write_json(ROOT/"docs/final_analysis_plan.json",plan)
    return plan


def require_frozen_plan():
    path=ROOT/"docs/final_analysis_plan.json"
    if not path.exists():raise ValueError("Final analysis plan is required before test evaluation")
    committed=subprocess.run(["git","show","HEAD:docs/final_analysis_plan.json"],cwd=ROOT,capture_output=True)
    if committed.returncode or sha(committed.stdout.replace(b"\r\n",b"\n"))!=text_sha(path):
        raise ValueError("Final analysis plan must be committed and unchanged before test evaluation")
    plan=json.loads(path.read_text())
    if plan["source_hashes"]!=source_fingerprint():raise ValueError("Model/evaluation code changed after plan freeze")
    for file,key in [("results/predictive/selected_models.json","selected_models_sha256"),
                     ("uv.lock","environment_lock_sha256"),
                     ("configs/data_spec.yaml","data_spec_sha256"),("configs/splits.yaml","splits_config_sha256"),
                     ("configs/experiments.yaml","experiments_sha256"),("configs/final_evaluation.yaml","evaluation_config_sha256")]:
        if text_sha(ROOT/file)!=plan[key]:raise ValueError("Frozen settings changed")
    _,_,_,meta=load_analysis()
    if meta["sha256"]!=plan["dataset_sha256"] or meta["split_keys_sha256"]!=plan["split_sha256"]:
        raise ValueError("Frozen data/splits changed")
    return plan


def load_checkpoint(record):
    directory=ROOT/record["artifact_directory"]
    for artifact in record["artifacts"]:
        if sha((ROOT/artifact["path"]).read_bytes())!=artifact["sha256"]:raise ValueError("Checkpoint artifact changed")
    family=record["family"]
    if family=="xgboost":
        from xgboost import XGBClassifier
        model=XGBClassifier();model.load_model(directory/"model.ubj");return model
    meta=json.loads((directory/"model.json").read_text())
    if family in ["prevalence","logistic"]:return meta
    import torch
    if family=="gru":
        from .temporal import TemporalBaseline
        model=TemporalBaseline(meta["hidden"],meta["positive_weight"])
    else:
        from .graph_models import GraphTemporal
        model=GraphTemporal(meta["family"],meta["hidden"],meta["k"],meta["positive_weight"],meta["seed"])
    model.load_state_dict(torch.load(directory/"weights.pt",map_location="cpu",weights_only=True));model.eval()
    model.metadata=meta
    return model


def evaluate_final():
    plan=require_frozen_plan()
    panel,roles,prep,meta=load_analysis()
    selected=json.loads((ROOT/"results/predictive/selected_models.json").read_text())
    output=ROOT/"results/final_evaluation";output.mkdir(parents=True,exist_ok=True)
    opening=output/"holdout_opening.json"
    if opening.exists():raise ValueError("Final evaluation already run; use preserved predictions, not silent retuning")
    write_json(opening,dict(utc=datetime.now(timezone.utc).isoformat(),plan_sha256=sha((ROOT/"docs/final_analysis_plan.json").read_bytes()),
                           code_commit=code_commit(),dataset_id=meta["dataset_id"],purpose="first frozen final performance evaluation"))
    conditions=[(family,selected[family]["candidate"],family) for family in plan["settings"]["families"]]
    alternative=[c for c in settings()["families"]["gat_gru"] if c["name"]!=selected["gat_gru"]["candidate"]["name"]][0]
    conditions.append(("gat_gru",alternative,"gat_gru_other_k"))
    runs,results,seed_results=[],[],[]
    for family,candidate,label in conditions:
        pieces=[]
        for seed in selected[family]["seeds"]:
            p,record=fit_condition(family,candidate,seed,"final",panel,roles,prep,meta)
            record["report_label"]=label;runs.append(record);p["seed"]=seed;pieces.append(p)
            seed_metrics,_=prediction_metrics(p,selected[family]["threshold"])
            seed_results.append(dict(model=label,seed=seed,**seed_metrics))
            write_json(output/"fit_manifest.json",runs)
            print(f"final {label} seed={seed}: {record['seconds']:.2f}s",flush=True)
        combined=pd.concat(pieces)
        combined.to_csv(ROOT/f"results/cache/{label}_test_seeds.csv.gz",index=False,compression={"method":"gzip","mtime":0})
        average=pieces[0].drop(columns="seed").copy()
        average["probability"]=np.mean([p.probability.to_numpy() for p in pieces],axis=0)
        average.to_csv(output/f"{label}_predictions.csv.gz",index=False,compression={"method":"gzip","mtime":0})
        # Sensitivity uses a fixed operating point, not a threshold fitted on its test outputs.
        threshold=selected[family]["threshold"]
        if label=="gat_gru_other_k":
            threshold_note="primary family's development threshold; other-k control not reselected"
        else:threshold_note="frozen selected validation threshold"
        metrics,warnings=prediction_metrics(average,threshold)
        results.append(dict(model=label,threshold_basis=threshold_note,**metrics))
        calibration_table(average).to_csv(output/f"{label}_calibration.csv")
        pd.DataFrame(warnings).to_csv(output/f"{label}_warning_events.csv",index=False)
        pd.DataFrame(results).to_csv(output/"results.csv",index=False)
        pd.DataFrame(seed_results).to_csv(output/"seed_results.csv",index=False)
    # Small final checkpoints are part of the versioned research package, unlike raw caches.
    for record in runs:
        destination=ROOT/"artifacts/models"/record["report_label"]/f"seed_{record['seed']}"
        destination.mkdir(parents=True,exist_ok=True)
        record["cached_artifact_directory"]=record["artifact_directory"]
        record["artifact_directory"]=destination.relative_to(ROOT).as_posix()
        for artifact in record["artifacts"]:
            target=destination/(__import__('pathlib').Path(artifact["path"]).name)
            shutil.copyfile(ROOT/artifact["path"],target)
            artifact["path"]=target.relative_to(ROOT).as_posix()
            assert sha(target.read_bytes())==artifact["sha256"]
    write_json(output/"fit_manifest.json",runs)
    analysis_directory=ROOT/"artifacts/analysis";analysis_directory.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/meta["preprocessing_path"],analysis_directory/"preprocessing.json")
    return pd.DataFrame(results)
