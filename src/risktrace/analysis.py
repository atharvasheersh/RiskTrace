"""Immutable source-backed analysis build with explicit, approved forecast clocks."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .core import ROOT, RATIOS, cert, config, label_panel, normalize, write_json
from .protocol import event_counts, training_mask


def sha(body):
    return hashlib.sha256(body).hexdigest()


def immutable(path, body):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != body:
        raise ValueError(f"Refusing to replace immutable artifact: {path}")
    if not path.exists():
        path.write_bytes(body)


def csv_bytes(frame):
    return frame.to_csv(index=False, lineterminator="\n").encode("utf8")


def source_records(root=ROOT):
    manifest = json.loads((root / "data/manifests/full_sources.json").read_text())
    financial, failures, lineage, indices = [], [], {}, []
    for record in manifest:
        body = (root / record["path"]).read_bytes()
        if sha(body) != record["sha256"]:
            raise ValueError("Official source checksum mismatch")
        payload = json.loads(body)
        if len(payload["data"]) != record["returned"] or payload["meta"]["total"] != record["total"]:
            raise ValueError("Source manifest/count mismatch")
        rows = [r["data"] for r in payload["data"]]
        if record["endpoint"] == "financials":
            for row in rows:
                key = (cert(row["CERT"]), str(row["REPDTE"]))
                if key in lineage:
                    raise ValueError("Duplicate official CERT/report key")
                lineage[key] = record["sha256"]
            financial.extend(rows)
        elif record["endpoint"] == "failures":
            failures.extend(rows)
            indices.append(record["source_index"]["createTimestamp"][:10])
    if not indices:
        raise ValueError("No verified outcome source")
    return financial, failures, lineage, min(indices)


def compare_raw_fields(reference, other, fields):
    """Reject changed values instead of trusting matching keys or merging by order."""
    keys = ["CERT", "REPDTE"]
    left, right = reference.copy(), other.copy()
    for frame in [left, right]:
        frame["CERT"] = frame.CERT.map(cert)
        frame["REPDTE"] = frame.REPDTE.astype(str)
        if frame.duplicated(keys).any():
            raise ValueError("Duplicate integration keys")
    left, right = left.set_index(keys).sort_index(), right.set_index(keys).sort_index()
    if not right.index.isin(left.index).all():
        raise ValueError("Unexpected submitted keys")
    left = left.loc[right.index]
    text = {"NAME", "STALP", "BKCLASS", "INSAGNT1"}
    conflicts = []
    for field in fields:
        if field in keys:
            continue
        if field not in right:
            raise ValueError(f"Missing submitted raw field: {field}")
        if field in text:
            equal = left[field].fillna("<null>").eq(right[field].fillna("<null>"))
        else:
            a, b = pd.to_numeric(left[field]), pd.to_numeric(right[field])
            equal = a.eq(b) | (a.isna() & b.isna())
        for key in right.index[~equal]:
            conflicts.append(dict(CERT=key[0], REPDTE=key[1], field=field,
                                  official_value=left.loc[key, field], submitted_value=right.loc[key, field]))
    return pd.DataFrame(conflicts, columns=["CERT", "REPDTE", "field", "official_value", "submitted_value"])


def preprocess_fit(frame, features, origin, dataset_sha):
    if len(frame) == 0:
        raise ValueError("Empty fold training set")
    x = frame[features].to_numpy(float)
    median = np.nanmedian(x, axis=0)
    x = np.where(np.isfinite(x), x, median)
    if not np.isfinite(x).all():
        raise ValueError("Unidentified training preprocessing statistic")
    mean, scale = x.mean(axis=0), x.std(axis=0)
    scale[scale < 1e-10] = 1
    return dict(features=features, median=median.tolist(), mean=mean.tolist(), scale=scale.tolist(),
                fit_origin=str(pd.Timestamp(origin).date()), rows=len(frame),
                max_training_report=str(frame.report_date.max().date()),
                max_training_horizon_end=str(frame.horizon_end_12m.max().date()),
                training_keys_sha256=sha("\n".join(frame.row_id).encode()), dataset_sha256=dataset_sha)


def transform(frame, preprocessing):
    x = frame[preprocessing["features"]].to_numpy(float)
    x = np.where(np.isfinite(x), x, np.array(preprocessing["median"]))
    return (x - preprocessing["mean"]) / preprocessing["scale"]


def analysis_build(root=ROOT):
    spec = config(root / "configs/data_spec.yaml")
    splits = yaml.safe_load((root / "configs/splits.yaml").read_text())
    if splits.get("status") != "approved":
        raise ValueError("Author protocol approval is required before analysis freeze")
    raw, failures, lineage, outcome_cutoff = source_records(root)
    spec["as_of"] = min(spec["as_of"], outcome_cutoff)
    frame = label_panel(normalize(raw, spec), failures, spec)
    if not frame.eligible.all() or not frame.INSAGNT1.eq("DIF").all():
        raise ValueError("Uninsured or ineligible official records require review")
    previous = pd.read_csv(root / "data/processed/full_panel.csv", dtype={"CERT": str, "REPDTE": str}, low_memory=False)
    conflicts = compare_raw_fields(frame, previous, spec["api"]["financial_fields"])
    if len(conflicts):
        raise ValueError("Preserved processed records conflict with raw source values")
    frame = frame.rename(columns={"split": "legacy_split", "purged": "legacy_purged"})
    frame["row_id"] = frame.CERT + "_" + frame.REPDTE.astype(str)
    frame["horizon_end_12m"] = frame.availability_date + pd.DateOffset(months=12)
    frame["availability_basis"] = "assumed_report_plus_60_days; revised_snapshot"
    frame["label_mature_by_snapshot"] = frame.horizon_end_12m.le(spec["as_of"])
    frame["source_sha256"] = [lineage[(c, str(d))] for c, d in zip(frame.CERT, frame.REPDTE)]
    allocation = pd.read_csv(root / "data/bank_allocation.csv", dtype={"CERT": str}).set_index("CERT")
    frame["owner"] = frame.CERT.map(allocation.owner)
    frame["source_attribution"] = "central_official_FDIC_bulk; not_Ayush_submission"
    # CERT remains the outcome unit; do not splice histories through ambiguous aliases.
    ordered = frame.sort_values(["CERT", "report_date"])
    quarter = ordered.report_date.dt.to_period("Q").astype(int)
    gap = quarter.groupby(ordered.CERT).diff().ne(1)
    alias_change = ordered.RSSDID.ne(ordered.groupby("CERT").RSSDID.shift())
    frame["history_reset"] = (gap | alias_change).reindex(frame.index)
    # Independent scalar ratios, not values trusted from previous derived files.
    for field, (n, d) in RATIOS.items():
        expected = np.divide(frame[n], frame[d], out=np.full(len(frame), np.nan), where=frame[d].gt(0))
        np.testing.assert_allclose(frame[field], expected, equal_nan=True, rtol=1e-12)
    body = csv_bytes(frame)
    digest = sha(body)
    dataset_id = f"analysis-v1-{digest[:12]}"
    directory = root / "data/processed/analysis" / dataset_id
    immutable(directory / "canonical.csv", body)
    good = frame.usable_financials & ~frame.already_failed & frame.label_12m.notna()
    roles, fold_summary, preprocessing = [], [], {}
    for year in splits["development_report_years"]:
        origin = pd.Timestamp(f"{year}-03-31") + pd.Timedelta(days=spec["availability_lag_days"])
        fit = frame.loc[training_mask(frame, origin)]
        valid = frame.loc[good & frame.report_date.dt.year.eq(year)]
        if not valid.horizon_end_12m.lt(splits["final_fit_origin"]).all():
            raise ValueError("Validation outcomes unavailable before first test origin")
        name = f"annual_{year}"
        preprocessing[name] = preprocess_fit(fit, splits["feature_list"], origin, digest)
        for role, subset in [("train", fit), ("validation", valid)]:
            roles.extend(dict(fold=name, role=role, row_id=r) for r in subset.row_id)
        fold_summary.append(dict(fold=name, origin=str(origin.date()),
                                 **{f"train_{k}":v for k,v in event_counts(fit).items()},
                                 **{f"validation_{k}":v for k,v in event_counts(valid).items()}))
    origin = pd.Timestamp(splits["final_fit_origin"])
    fit = frame.loc[training_mask(frame, origin)]
    test = frame.loc[good & frame.label_mature_by_snapshot & frame.report_date.between(splits["test_report_start"], splits["test_report_end"])]
    preprocessing["final"] = preprocess_fit(fit, splits["feature_list"], origin, digest)
    for role, subset in [("train", fit), ("test", test)]:
        roles.extend(dict(fold="final", role=role, row_id=r) for r in subset.row_id)
    keys = csv_bytes(pd.DataFrame(roles))
    compressed_keys = gzip.compress(keys, mtime=0)
    key_path = root / "data/manifests/analysis_v1_split_keys.csv.gz"
    immutable(key_path, compressed_keys)
    prep_body = (json.dumps(preprocessing, indent=2, allow_nan=False) + "\n").encode()
    immutable(directory / "preprocessing.json", prep_body)
    result = dict(dataset_id=dataset_id, status="frozen_revised_snapshot_exploratory", rows=len(frame),
                  banks=frame.CERT.nunique(), data_path=(directory / "canonical.csv").relative_to(root).as_posix(),
                  sha256=digest, bytes=len(body), outcome_cutoff=spec["as_of"],
                  split_keys_path=key_path.relative_to(root).as_posix(), split_keys_sha256=sha(compressed_keys),
                  uncompressed_split_keys_sha256=sha(keys), split_memberships=len(roles),
                  preprocessing_path=(directory / "preprocessing.json").relative_to(root).as_posix(),
                  preprocessing_sha256=sha(prep_body), config_sha256=sha((root / "configs/splits.yaml").read_bytes()),
                  source_manifest_sha256=sha((root / "data/manifests/full_sources.json").read_bytes()),
                  source_attribution="Central official bulk; no collaborator submission received", raw_value_conflicts=0,
                  final_fit_counts=event_counts(fit), final_test_eligible_rows=len(test),
                  test_performance_opened=False, folds=fold_summary,
                  limits=["Assumed 60-day public availability; revised snapshots, not point-in-time vintages",
                          "Only six positive validation banks; four positive test banks already counted in prior QA",
                          "Historical roster/merger competing events and deposit-scope review incomplete"])
    write_json(root / "data/manifests/analysis_v1.json", result)
    output = root / "results/analysis"
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(fold_summary).to_csv(output / "fold_counts.csv", index=False)
    frame.groupby([frame.report_date.dt.year.rename("report_year"), "BKCLASS"]).agg(
        rows=("CERT", "size"), financial_usable=("usable_financials", "sum"),
        positives=("label_12m", "sum")).to_csv(output / "coverage_by_year_class.csv")
    ids = frame.groupby("CERT").agg(rssd_ids=("RSSDID", "nunique"), historical_names=("NAME", "nunique"))
    ids.to_csv(output / "identifier_audit.csv")
    alias_records = frame.loc[frame.CERT.isin(ids.index[ids.rssd_ids.gt(1)]),
                              ["CERT", "REPDTE", "RSSDID", "NAME", "history_reset"]]
    alias_records.to_csv(output / "identifier_mapping_flags.csv", index=False)
    shared = frame.groupby("RSSDID").CERT.nunique()
    frame.loc[frame.RSSDID.isin(shared.index[shared.gt(1)]), ["CERT", "REPDTE", "RSSDID", "NAME"]].to_csv(
        output / "shared_rssd_flags.csv", index=False)
    result["identifier_audit"] = dict(certs_with_multiple_rssd_ids=int(ids.rssd_ids.gt(1).sum()),
                                     certs_with_multiple_names=int(ids.historical_names.gt(1).sum()),
                                     rssd_ids_shared_by_multiple_certs=int(shared.gt(1).sum()),
                                     handling="CERT outcome unit; no cross-CERT splicing; reset recurrent state at gaps/RSSD changes")
    write_json(root / "data/manifests/analysis_v1.json", result)
    return result


def load_analysis(root=ROOT):
    meta = json.loads((root / "data/manifests/analysis_v1.json").read_text())
    body = (root / meta["data_path"]).read_bytes()
    if sha(body) != meta["sha256"]:
        raise ValueError("Analysis dataset checksum mismatch")
    panel = pd.read_csv(io.BytesIO(body), dtype={"CERT": str}, low_memory=False, float_precision="round_trip")
    for field in ["report_date", "availability_date", "horizon_end_12m", "failure_date"]:
        panel[field] = pd.to_datetime(panel[field])
    key_body = (root / meta["split_keys_path"]).read_bytes()
    if sha(key_body) != meta["split_keys_sha256"]:
        raise ValueError("Frozen split keys changed")
    roles = pd.read_csv(io.BytesIO(gzip.decompress(key_body)))
    prep_body = (root / meta["preprocessing_path"]).read_bytes()
    if sha(prep_body) != meta["preprocessing_sha256"]:
        raise ValueError("Frozen preprocessing changed")
    return panel, roles, json.loads(prep_body), meta
