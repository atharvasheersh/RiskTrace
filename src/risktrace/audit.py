"""Minimal frozen graph-aggregation/recurrent-state pilot; not the proposed TGNN."""
from __future__ import annotations

import hashlib
import itertools
import json
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

from .core import ROOT, config, write_json

RAW = ["ASSET", "LIAB", "EQ", "EQTOT", "DEP", "DEPDOM", "DEPUNINS", "CHBAL",
       "LNLSNET", "LNLSGR", "NCLNLS", "SC", "SCAF"]
COL = {s: i for i, s in enumerate(RAW)}
GROUPS = ["capital", "asset_mix", "credit_quality"]


def feature_array(raw):
    """Five descendants of raw records; undefined inactive rows become zero later."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.stack([raw[..., COL[n]] / raw[..., COL[d]] for n, d in
                         [("EQTOT", "ASSET"), ("CHBAL", "ASSET"), ("LNLSNET", "ASSET"),
                          ("SC", "ASSET"), ("NCLNLS", "LNLSGR")]], axis=-1)


def financially_valid(r):
    a, liab, eq = (r[COL[k]] for k in ["ASSET", "LIAB", "EQTOT"])
    if not np.isfinite(r).all() or a <= 0 or abs(a - liab - eq) > max(5, a * 1e-5):
        return False
    if any(r[COL[k]] < 0 for k in ["DEP", "CHBAL", "LNLSNET", "LNLSGR", "NCLNLS", "SC"]):
        return False
    return (r[COL["CHBAL"]] + r[COL["LNLSNET"]] + r[COL["SC"]] <= a * 1.00001
            and r[COL["DEP"]] <= liab * 1.00001 and 0 < r[COL["LNLSGR"]]
            and r[COL["NCLNLS"]] <= r[COL["LNLSGR"]]
            and r[COL["LNLSNET"]] <= r[COL["LNLSGR"]])


def replace_groups(original, donor, groups):
    """Scale a same-quarter donor to target assets; preserve unedited identities."""
    r = original.copy()
    scale = original[COL["ASSET"]] / donor[COL["ASSET"]]
    if "capital" in groups:
        for f in ["EQ", "EQTOT"]:
            r[COL[f]] = donor[COL[f]] * scale
        r[COL["LIAB"]] = r[COL["ASSET"]] - r[COL["EQTOT"]]
    if "asset_mix" in groups:
        for f in ["CHBAL", "LNLSNET", "LNLSGR", "SC", "SCAF"]:
            r[COL[f]] = donor[COL[f]] * scale
        # Changing gross loans must preserve the original credit-quality fraction.
        r[COL["NCLNLS"]] = original[COL["NCLNLS"]] / original[COL["LNLSGR"]] * r[COL["LNLSGR"]]
    if "credit_quality" in groups:
        r[COL["NCLNLS"]] = donor[COL["NCLNLS"]] / donor[COL["LNLSGR"]] * r[COL["LNLSGR"]]
    return r


def graph(z, active, kind, k, states, seed):
    n = len(z)
    a = np.zeros((n, n))
    ids = np.flatnonzero(active)
    if kind == "none" or len(ids) < 2:
        return a
    distance = ((z[:, None] - z[None, :]) ** 2).sum(axis=-1)
    if kind == "exogenous":
        distance = (states[:, None] != states[None, :]).astype(float)
    elif kind == "random":
        distance = np.random.default_rng(seed).random((n, n))
    distance[:, ~active] = np.inf
    np.fill_diagonal(distance, np.inf)
    neighbors = np.argsort(distance, axis=1, kind="stable")[:, :min(k, len(ids) - 1)]
    for i in ids:
        a[i, neighbors[i]] = 1 / neighbors.shape[1]
    return a


def replay(representations, active, decay=.5):
    """Full common-history replay, resetting state across unavailable reports."""
    h = np.zeros_like(representations[0])
    output = []
    for r, valid in zip(representations, active):
        h = (decay * h + (1 - decay) * r) * valid[:, None]
        output.append(h.copy())
    return np.array(output)


@dataclass
class Data:
    name: str
    raw: np.ndarray
    active: np.ndarray
    labels: np.ndarray
    ids: list
    states: np.ndarray
    classes: np.ndarray
    fingerprint: str
    description: str


def synthetic_data():
    """Known feature->kNN->memory->Bernoulli dependency, intentionally synthetic."""
    rng = np.random.default_rng(2026)
    t, n = 12, 64
    raw = np.zeros((t, n, len(RAW)))
    latent = rng.normal(size=(n, 4))
    for q in range(t):
        latent = .8 * latent + .2 * rng.normal(size=latent.shape)
        capital = .04 + .14 / (1 + np.exp(-latent[:, 0] * 3))
        cash = .02 + .22 / (1 + np.exp(-latent[:, 1] * 3))
        loans = .25 + .35 / (1 + np.exp(-latent[:, 2] * 3))
        quality = .005 + .15 / (1 + np.exp(-latent[:, 3] * 3))
        for i in range(n):
            a = 2e6 * np.exp(.3 * rng.normal())
            values = dict(ASSET=a, EQTOT=a * capital[i], EQ=a * capital[i], LIAB=a * (1 - capital[i]),
                          DEP=.72 * a, DEPDOM=.72 * a, DEPUNINS=.2 * a, CHBAL=a * cash[i],
                          LNLSNET=a * loans[i], LNLSGR=a * loans[i] * 1.02,
                          NCLNLS=a * loans[i] * 1.02 * quality[i], SC=.12 * a, SCAF=.1 * a)
            raw[q, i] = [values[f] for f in RAW]
    assert all(financially_valid(r) for r in raw.reshape(-1, len(RAW)))
    active = np.ones((t, n), bool)
    x = feature_array(raw)
    mu, sd = x[:4].reshape(-1, 5).mean(axis=0), x[:4].reshape(-1, 5).std(axis=0)
    # SC is constant by design: use unit scale for numerically constant features.
    sd[sd < 1e-10] = 1
    z = (x - mu) / sd
    states = np.array([str(i % 4) for i in range(n)])
    reps = np.array([np.concatenate([zq, graph(zq, active[q], "feature", 3, states, 0) @ zq], axis=1)
                     for q, zq in enumerate(z)])
    h = replay(reps, active)
    logit = -.8 - .6 * h[..., 0] + 1.4 * h[..., 4] - 1.2 * h[..., 5] + 1.5 * h[..., 9]
    probability = 1 / (1 + np.exp(-logit))
    y = (rng.random((t, n)) < probability).astype(float)
    return Data("synthetic", raw, active, y, [f"S{i:03}" for i in range(n)], np.tile(states, (t, 1)),
                np.full((t, n), "synthetic"), hashlib.sha256(raw.tobytes() + y.tobytes()).hexdigest(),
                "64 artificial banks, 12 periods; known k=3 graph and recurrent Bernoulli generator; not real-bank evidence")


def bank_data():
    path = ROOT / "data/processed/pilot_panel.csv"
    frame = pd.read_csv(path, dtype={"CERT": str})
    good = frame.usable_financials & ~frame.already_failed & frame.label_12m.notna()
    frame = frame.loc[good].copy()
    positive = set(frame.loc[frame.label_12m.eq(1), "CERT"])
    remaining = sorted(set(frame.CERT) - positive, key=lambda c: hashlib.sha256(c.encode()).hexdigest())
    ids = sorted(positive | set(remaining[:96]))
    # Enrichment uses only development outcomes; it invalidates population performance estimates.
    dates = sorted(frame.REPDTE.unique())
    raw = np.zeros((len(dates), len(ids), len(RAW)))
    active, labels = np.zeros(raw.shape[:2], bool), np.full(raw.shape[:2], np.nan)
    states, classes = np.full(active.shape, "", dtype=object), np.full(active.shape, "", dtype=object)
    index = {c: i for i, c in enumerate(ids)}
    for q, date in enumerate(dates):
        for _, row in frame.loc[frame.REPDTE.eq(date) & frame.CERT.isin(ids)].iterrows():
            i = index[row.CERT]
            raw[q, i] = row[RAW].to_numpy(float)
            active[q, i], labels[q, i] = True, row.label_12m
            states[q, i], classes[q, i] = row.STALP, row.BKCLASS
    return Data("bank", raw, active, labels, ids, states, classes, hashlib.sha256(path.read_bytes()).hexdigest(),
                "development-only case-enriched subset: all positive CERTs plus 96 hash-selected others; population scores invalid")


class FrozenPilot:
    def __init__(self, data, kind, k, seed, decay=.5):
        self.data, self.kind, self.k, self.seed, self.decay = data, kind, k, seed, decay
        x = feature_array(data.raw)
        fit = x[:4][data.active[:4]]
        self.mu, self.sd = fit.mean(axis=0), fit.std(axis=0)
        self.sd[self.sd < 1e-10] = 1
        self.z = np.zeros_like(x)
        self.z[data.active] = (x[data.active] - self.mu) / self.sd
        self.graphs = [graph(z, data.active[q], kind, k, data.states[q], seed + q) for q, z in enumerate(self.z)]
        self.reps = np.array([np.concatenate([z, a @ z], axis=1) for z, a in zip(self.z, self.graphs)])
        self.h = replay(self.reps, data.active, decay)
        # Train only periods 0..3. Periods 4..7 form a label-window embargo.
        # For banks these are 2010 / embargo 2011 / evaluation 2012.
        rng = np.random.default_rng(seed)
        sampled_banks = rng.integers(0, len(data.ids), len(data.ids))
        h, y, count = [], [], 0
        for i in sampled_banks:
            valid = data.active[:4, i] & np.isfinite(data.labels[:4, i])
            h.extend(self.h[:4, i][valid]); y.extend(data.labels[:4, i][valid]); count += valid.sum()
        if len(set(y)) < 2:
            raise ValueError("Bootstrap has fewer than two label classes; model inadequate")
        self.model = LogisticRegression(C=1, class_weight="balanced", max_iter=1000).fit(h, y)
        self.train_rows = int(count)
        self.train_min, self.train_max = fit.min(axis=0), fit.max(axis=0)
        self.fit_z = (fit - self.mu) / self.sd
        self.pred = self.model.predict_proba(self.h.reshape(-1, 10))[:, 1].reshape(data.active.shape)

    def fingerprint(self):
        return hashlib.sha256(b"".join(v.tobytes() for v in
                             [self.mu, self.sd, self.model.coef_, self.model.intercept_])).hexdigest()

    def edited_prediction(self, raw, target, edit, rebuild):
        z = self.z[edit].copy()
        z[target] = (feature_array(raw) - self.mu) / self.sd
        a = self.graphs[edit]
        if rebuild and self.kind == "feature":
            a = graph(z, self.data.active[edit], self.kind, self.k, self.data.states[edit], self.seed + edit)
        reps = self.reps.copy()
        reps[edit] = np.concatenate([z, a @ z], axis=1)
        h = replay(reps, self.data.active, self.decay)
        p = self.model.predict_proba(h[-1, target].reshape(1, -1))[0, 1]
        changed_edges = int(np.count_nonzero((a > 0) != (self.graphs[edit] > 0)))
        f = feature_array(raw)
        outside = int(((f < self.train_min) | (f > self.train_max)).sum())
        nearest = float(np.sqrt(((self.fit_z - z[target]) ** 2).sum(axis=1)).min())
        return float(p), changed_edges, outside, nearest


def ranking_agreement(a, b):
    ra, rb = rankdata(a), rankdata(b)
    if np.std(ra) == 0 or np.std(rb) == 0:
        return 1.0 if np.allclose(a, b) else 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def run_condition(data, kind, k, seed, max_banks, decay):
    begin = time.perf_counter()
    m = FrozenPilot(data, kind, k, seed, decay)
    before = m.fingerprint()
    rng = np.random.default_rng(seed)
    targets = [i for i in range(len(data.ids)) if data.active[8:, i].all()]
    targets = sorted(targets, key=lambda i: hashlib.sha256(data.ids[i].encode()).hexdigest())[:max_banks]
    cases, invalid = [], []
    attempts, bad = 0, 0
    for edit in [8, 11]:
        for target in targets:
            original = data.raw[edit, target]
            candidates = [i for i in np.flatnonzero(data.active[edit]) if i != target
                          and data.classes[edit, i] == data.classes[edit, target]
                          and abs(np.log(data.raw[edit, i, COL["ASSET"]] / original[COL["ASSET"]])) <= np.log(2)]
            candidates.sort(key=lambda i: abs(np.log(data.raw[edit, i, COL["ASSET"]] / original[COL["ASSET"]])))
            if not candidates:
                invalid.append(dict(dataset=data.name, seed=seed, kind=kind, k=k, target=data.ids[target],
                                    edit_period=edit, groups="none", reason="no same-class donor within factor-two assets"))
                continue
            donor_id = int(rng.choice(candidates[:8]))
            donor = data.raw[edit, donor_id]
            responses, edge_changes, diagnostics = {}, [], []
            for size in [1, 2, 3]:
                for selected in itertools.combinations(GROUPS, size):
                    attempts += 1
                    changed = replace_groups(original, donor, selected)
                    if not financially_valid(changed):
                        bad += 1
                        invalid.append(dict(dataset=data.name, seed=seed, kind=kind, k=k, target=data.ids[target],
                                            edit_period=edit, groups="+".join(selected), reason="accounting/range constraint"))
                        continue
                    a = m.edited_prediction(changed, target, edit, False)
                    b = m.edited_prediction(changed, target, edit, True)
                    responses[frozenset(selected)] = (a[0], b[0])
                    edge_changes.append(b[1]); diagnostics.append((b[2], b[3]))
            if len(responses) != 7:
                continue  # Exclusions counted; no donor resampling to force validity.
            p = float(m.pred[-1, target])
            scores = np.array([[abs(p - responses[frozenset([g])][mode]) for g in GROUPS] for mode in [0, 1]])
            top = np.argmax(scores, axis=1)
            rec = dict(dataset=data.name, seed=seed, kind=kind, k=k, target=data.ids[target],
                       donor=data.ids[donor_id], edit_period=edit, evaluation_period=11, original_probability=p,
                       max_response_gap=max(abs(a - b) for a, b in responses.values()),
                       mean_response_gap=float(np.mean([abs(a - b) for a, b in responses.values()])),
                       ranking_spearman=ranking_agreement(scores[0], scores[1]),
                       top1_disagrees=bool(top[0] != top[1]), max_changed_edges=max(edge_changes),
                       max_outside_training_ranges=max(d[0] for d in diagnostics),
                       max_nearest_training_distance=max(d[1] for d in diagnostics))
            random_group = GROUPS[int(rng.integers(3))]
            for subset, paired in responses.items():
                tag = "_".join(g for g in GROUPS if g in subset)
                rec[f"conditional_p_{tag}"], rec[f"pipeline_p_{tag}"] = paired
            for mode, label in [(0, "conditional"), (1, "pipeline")]:
                chosen = GROUPS[top[mode]]
                rec[f"{label}_top1"] = chosen
                rec[f"{label}_necessity"] = p - responses[frozenset([chosen])][mode]
                keep = responses[frozenset(set(GROUPS) - {chosen})][mode]
                rec[f"{label}_sufficiency_gap"] = p - keep
                rec[f"{label}_sufficiency_gain"] = keep - responses[frozenset(GROUPS)][mode]
                rec[f"{label}_random_necessity"] = p - responses[frozenset([random_group])][mode]
                for group, score in zip(GROUPS, scores[mode]):
                    rec[f"{label}_score_{group}"] = float(score)
            cases.append(rec)
    assert before == m.fingerprint(), "Parameters mutated during paired audit"
    mask = data.active[8:] & np.isfinite(data.labels[8:])
    truth, prediction = data.labels[8:][mask], m.pred[8:][mask]
    run = dict(dataset=data.name, kind=kind, k=k, seed=seed, data_sha256=data.fingerprint,
               parameter_sha256=before, frozen_parameters_verified=True, train_rows=m.train_rows,
               eval_rows=int(mask.sum()), eval_positive_rows=int(truth.sum()),
               eval_distinct_positive_banks=int(np.any((data.labels[8:] == 1) & data.active[8:], axis=0).sum()),
               eval_auroc=float(roc_auc_score(truth, prediction)) if len(set(truth)) > 1 else None,
               eval_average_precision=float(average_precision_score(truth, prediction)) if truth.sum() else None,
               audited_cases=len(cases), perturbations_attempted=attempts, invalid_perturbations=bad,
               invalid_rate=bad / attempts if attempts else None, seconds=time.perf_counter() - begin,
               mean_response_gap=float(np.mean([c["mean_response_gap"] for c in cases])) if cases else None,
               max_response_gap=max((c["max_response_gap"] for c in cases), default=None),
               top1_disagreement_rate=float(np.mean([c["top1_disagrees"] for c in cases])) if cases else None)
    parameters = dict(dataset=data.name, kind=kind, k=k, seed=seed, mean=m.mu.tolist(), scale=m.sd.tolist(),
                      coefficients=m.model.coef_.tolist(), intercept=m.model.intercept_.tolist(), sha256=before)
    return run, cases, invalid, parameters


def run_audit():
    spec = config()
    runs, cases, invalid, params = [], [], [], []
    for data in [synthetic_data(), bank_data()]:
        for kind, k in [("none", 0), ("exogenous", 3), ("random", 3)] + [("feature", k) for k in spec["audit"]["knn"] if k]:
            for seed in spec["audit"]["seeds"]:
                run, c, bad, p = run_condition(data, kind, k, seed, spec["audit"]["max_evaluation_banks"], spec["audit"]["memory_decay"])
                runs.append(run); cases.extend(c); invalid.extend(bad); params.append(p)
                print(f"{data.name} {kind} k={k} seed={seed}: {run['audited_cases']} cases, max gap={run['max_response_gap']}", flush=True)
    frame = pd.DataFrame(cases)
    controls = frame.kind.ne("feature")
    assert (frame.loc[controls, "max_response_gap"] < 1e-12).all()
    pd.DataFrame(runs).to_csv(ROOT / "results/audit_runs.csv", index=False)
    frame.to_csv(ROOT / "results/audit_cases.csv", index=False)
    pd.DataFrame(invalid, columns=["dataset", "seed", "kind", "k", "target", "edit_period", "groups", "reason"]).to_csv(ROOT / "results/invalid_perturbations.csv", index=False)
    write_json(ROOT / "results/audit_parameters.json", params)
    summary = frame.groupby(["dataset", "kind", "k", "edit_period"]).agg(
        cases=("target", "size"), mean_gap=("mean_response_gap", "mean"), max_gap=("max_response_gap", "max"),
        top1_disagreement=("top1_disagrees", "mean"), mean_rank_agreement=("ranking_spearman", "mean"),
        outside_range_rate=("max_outside_training_ranges", lambda s: float((s > 0).mean()))).reset_index()
    summary.to_csv(ROOT / "results/audit_summary.csv", index=False)
    write_json(ROOT / "results/audit_protocol.json", dict(
        model="standardized raw ratios; directed feature-kNN neighbor mean; exponential-memory state; logistic readout",
        seeds=spec["audit"]["seeds"], predictor_fit="periods 0-3 only, bank bootstrap, balanced logistic readout",
        embargo="periods 4-7; replay states but do not use labels for fitting",
        evaluation="periods 8-11; edit period 8 or 11 and predict period 11",
        explanation="absolute leave-one-group-out response; equal top-one group budget; three prespecified groups",
        necessity="p(original)-p(replace selected group)",
        sufficiency_gap="p(original)-p(keep selected group and replace others)",
        sufficiency_gain="p(keep selected group)-p(replace all groups)",
        invalid="count every attempted group subset; reject invalid without resampling; whole-case comparisons require seven valid subsets",
        limitations=["Not a full temporal GNN", "No point-in-time data vintages", "Donors and graph rebuild do not ensure in-distribution or causal validity",
                     "Development bank subset is case-enriched; scores cannot estimate population performance",
                     "Seeds vary bank bootstrap, donor choice and random control; effects are not isolated training-seed uncertainty",
                     "No human explanation ground truth, significance test or financial materiality threshold established"],
        no_graph_and_exogenous_zero_gap_verified=True, frozen_parameters_all_runs=all(r["frozen_parameters_verified"] for r in runs)))
    return summary
