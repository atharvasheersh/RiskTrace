"""Bounded predictive baselines on frozen rolling-origin memberships."""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression

from .analysis import load_analysis, sha, transform
from .core import ROOT, write_json
from .metrics import alarm_threshold, calibration_table, prediction_metrics


def settings():
    return yaml.safe_load((ROOT / "configs/experiments.yaml").read_text())


def code_commit():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def probability_frame(panel, probability):
    return pd.DataFrame(dict(row_id=panel.row_id.to_numpy(), CERT=panel.CERT.to_numpy(),
                             report_date=panel.report_date.to_numpy(), availability_date=panel.availability_date.to_numpy(),
                             failure_date=panel.failure_date.to_numpy(), y=panel.label_12m.to_numpy(int),
                             probability=np.asarray(probability)))


def role_frame(panel, roles, fold, role):
    keys = set(roles.loc[roles.fold.eq(fold) & roles.role.eq(role), "row_id"])
    return panel.loc[panel.row_id.isin(keys)]


def fit_tabular(family, candidate, seed, fit, prep, directory):
    x, y = transform(fit, prep), fit.label_12m.to_numpy(int)
    if family == "prevalence":
        model = dict(kind="prevalence", probability=float(y.mean()))
        write_json(directory / "model.json", model)
    elif family == "logistic":
        fitted = LogisticRegression(C=candidate["C"], max_iter=2000, solver="lbfgs").fit(x, y)
        model = dict(kind="logistic", coefficients=fitted.coef_.ravel().tolist(), intercept=float(fitted.intercept_[0]))
        write_json(directory / "model.json", model)
    elif family == "xgboost":
        from xgboost import XGBClassifier
        model = XGBClassifier(max_depth=candidate["max_depth"], n_estimators=candidate["n_estimators"],
                              learning_rate=candidate["learning_rate"], tree_method="hist", n_jobs=2,
                              subsample=.8, colsample_bytree=1., min_child_weight=3, reg_lambda=1.,
                              scale_pos_weight=1., base_score=float(y.mean()), random_state=seed,
                              objective="binary:logistic", eval_metric="logloss")
        model.fit(x, y)
        model.save_model(directory / "model.ubj")
    else:
        raise ValueError(family)
    return model


def predict_tabular(model, evaluation, prep):
    x = transform(evaluation, prep)
    if isinstance(model, dict):
        if model["kind"] == "prevalence":
            return np.full(len(x), model["probability"])
        logit = x @ model["coefficients"] + model["intercept"]
        return 1/(1+np.exp(-np.clip(logit, -40, 40)))
    return model.predict_proba(x)[:, 1]


def fit_condition(family, candidate, seed, fold, panel, roles, preprocessing, meta):
    spec = settings()
    configuration = dict(family=family, candidate=candidate, seed=seed, fold=fold,
                         code_commit=code_commit(), dataset_sha256=meta["sha256"], split_sha256=meta["split_keys_sha256"],
                         experiment_config_sha256=sha((ROOT / "configs/experiments.yaml").read_bytes()))
    run_id = sha(json.dumps(configuration, sort_keys=True).encode())[:20]
    directory = ROOT / "results/cache/models" / run_id
    directory.mkdir(parents=True, exist_ok=True)
    fit = role_frame(panel, roles, fold, "train")
    evaluation = role_frame(panel, roles, fold, "validation" if fold != "final" else "test")
    prep = preprocessing[fold]
    start = time.perf_counter()
    if family in ["gru", "gat", "gat_gru", "gat_gru_random", "gat_gru_exogenous"]:
        from .temporal import train_neural, predict_neural
        model, training_log = train_neural(family, candidate, seed, fit, panel, prep, spec)
        import torch
        torch.save(model.state_dict(), directory / "weights.pt")
        write_json(directory / "training.json", training_log)
        write_json(directory / "model.json", model.metadata)
        probability = predict_neural(model, panel, evaluation, prep)
    else:
        model = fit_tabular(family, candidate, seed, fit, prep, directory)
        probability = predict_tabular(model, evaluation, prep)
    out = probability_frame(evaluation, probability)
    record = dict(configuration, run_id=run_id, train_rows=len(fit), evaluation_rows=len(out),
                  origin=prep["fit_origin"], train_keys_sha256=prep["training_keys_sha256"],
                  preprocessing_sha256=sha(json.dumps(prep, sort_keys=True).encode()),
                  seconds=time.perf_counter()-start, artifact_directory=directory.relative_to(ROOT).as_posix())
    record["environment_lock_sha256"]=sha((ROOT/"uv.lock").read_bytes())
    record["python"]=platform.python_version()
    record["versions"]={name:version(name) for name in ["numpy","pandas","scikit-learn","torch","xgboost"]}
    if hasattr(model,"evaluation_graph_sha256"):
        record["evaluation_graph_sha256"]=model.evaluation_graph_sha256
    artifacts = [p for p in directory.iterdir() if p.is_file() and p.name!="run.json"]
    record["artifacts"] = [{"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p.read_bytes()),"bytes":p.stat().st_size} for p in artifacts]
    write_json(directory / "run.json", record)
    return out, record


def development(families):
    panel, roles, prep, meta = load_analysis()
    spec = settings()
    output = ROOT / "results/predictive"
    output.mkdir(parents=True, exist_ok=True)
    all_runs, scores = [], []
    selected_path = output / "selected_models.json"
    selected = json.loads(selected_path.read_text()) if selected_path.exists() else {}
    for family in families:
        candidates = []
        for candidate in spec["families"][family]:
            seed_frames = []
            seeds = [11] if family in ["prevalence", "logistic"] else spec["seeds"]
            for seed in seeds:
                pieces = []
                for fold in [f"annual_{y}" for y in range(2012,2021)]:
                    prediction, record = fit_condition(family, candidate, seed, fold, panel, roles, prep, meta)
                    all_runs.append(record); pieces.append(prediction)
                    print(f"development {family} {candidate['name']} seed={seed} {fold}: {record['seconds']:.2f}s", flush=True)
                seed_frame = pd.concat(pieces).sort_values("row_id").reset_index(drop=True)
                seed_frame["seed"] = seed
                seed_frames.append(seed_frame)
            ensemble = seed_frames[0].drop(columns="seed").copy()
            ensemble["probability"] = np.mean([f.probability.to_numpy() for f in seed_frames], axis=0)
            threshold = alarm_threshold(ensemble.y, ensemble.probability, spec["false_alarm_rate"])
            metrics, warnings = prediction_metrics(ensemble, threshold)
            score = dict(family=family, candidate=candidate["name"], **metrics)
            scores.append(score)
            candidates.append((score, candidate, ensemble, warnings, seed_frames))
        best = sorted(candidates, key=lambda row:(-row[0]["average_precision"],row[0]["brier"]))[0]
        score, candidate, ensemble, warnings, seed_frames = best
        ensemble.to_csv(output / f"{family}_validation.csv.gz", index=False, compression={"method":"gzip","mtime":0})
        pd.concat(seed_frames).to_csv(ROOT / f"results/cache/{family}_validation_seeds.csv.gz", index=False, compression={"method":"gzip","mtime":0})
        calibration_table(ensemble).to_csv(output / f"{family}_calibration.csv")
        pd.DataFrame(warnings).to_csv(output / f"{family}_warning_events.csv", index=False)
        selected[family] = dict(candidate=candidate, threshold=score["threshold"], metrics=score,
                                seeds=[11] if family in ["prevalence","logistic"] else spec["seeds"],
                                dataset_id=meta["dataset_id"], code_commit=code_commit(), calibration=spec["calibration"])
        write_json(selected_path, selected)
        write_json(output / f"{family}_run_manifest.json", [r for r in all_runs if r["family"]==family])
    existing_path = output / "candidate_scores.csv"
    earlier = pd.read_csv(existing_path) if existing_path.exists() else pd.DataFrame()
    if len(earlier):
        earlier = earlier.loc[~earlier.family.isin(families)]
    pd.concat([earlier,pd.DataFrame(scores)]).to_csv(existing_path,index=False)
    pd.DataFrame([v["metrics"] for v in selected.values()]).to_csv(output / "validation_results.csv",index=False)
    return selected
