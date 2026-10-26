"""Shared contract logic. All dates are calendar dates, amounts USD thousands."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
RATIOS = {
    "equity_ratio": ("EQ", "ASSET"),
    "cash_ratio": ("CHBAL", "ASSET"),
    "loan_ratio": ("LNLSNET", "ASSET"),
    "securities_ratio": ("SC", "ASSET"),
    "noncurrent_ratio": ("NCLNLS", "LNLSGR"),
    "uninsured_domestic_ratio": ("DEPUNINS", "DEPDOM"),
}


def config(path=None):
    return yaml.safe_load(Path(path or ROOT / "configs/data_spec.yaml").read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False, default=str) + "\n", encoding="utf8")


def cert(value):
    """Canonicalize numeric certificates without silently truncating fractions."""
    number = float(value)
    if not np.isfinite(number) or number <= 0 or number != int(number):
        raise ValueError(f"Invalid CERT: {value!r}")
    return str(int(number))


def report_dates(start, end):
    return pd.date_range(start, end, freq="QE").strftime("%Y%m%d").tolist()


def allocate(ids, salt="RiskTrace-v1"):
    unique = {cert(c) for c in ids}
    ordered = sorted(unique, key=lambda c: (hashlib.sha256(f"{salt}:{c}".encode()).hexdigest(), c))
    return {c: ("Atharva Sheersh Pandey" if i % 2 == 0 else "Ayush Sinha") for i, c in enumerate(ordered)}


def normalize(rows, spec):
    frame = pd.DataFrame(rows).copy()
    frame["CERT"] = frame.CERT.map(cert)
    frame["report_date"] = pd.to_datetime(frame.REPDTE.astype(str), format="%Y%m%d", errors="raise")
    if not frame.report_date.dt.is_quarter_end.all():
        raise ValueError("Non-quarter-end report")
    if frame.duplicated(["CERT", "report_date"]).any():
        raise ValueError("Duplicate CERT/report_date keys")
    text = {"CERT", "REPDTE", "NAME", "RSSDID", "STALP", "BKCLASS", "INSAGNT1"}
    for name in spec["api"]["financial_fields"]:
        if name not in frame:
            frame[name] = np.nan
        if name not in text:
            frame[name] = pd.to_numeric(frame[name], errors="raise")
    for name, (num, den) in RATIOS.items():
        frame[name] = frame[num] / frame[den].where(frame[den] > 0)
    frame["eligible"] = (frame.ASSET.ge(spec["asset_min_thousands"])
                         & frame.ASSET.lt(spec["asset_max_exclusive_thousands"])
                         & frame.BKCLASS.isin(spec["bank_classes"]))
    residual = (frame.ASSET - frame.LIAB - frame.EQ).abs()
    frame["accounting_valid"] = residual.le(np.maximum(5, frame.ASSET * 1e-5))
    nonneg = ["DEP", "CHBAL", "LNLSNET", "LNLSGR", "NCLNLS", "SC"]
    ranges = frame[nonneg].ge(0).all(axis=1)
    ranges &= frame.CHBAL.add(frame.LNLSNET).add(frame.SC).le(frame.ASSET * 1.00001)
    ranges &= frame.NCLNLS.le(frame.LNLSGR) & frame.LNLSNET.le(frame.LNLSGR)
    ranges &= frame.DEP.le(frame.LIAB * 1.00001)
    frame["range_valid"] = ranges
    frame["feature_complete"] = np.isfinite(frame[spec["features"]]).all(axis=1)
    frame["usable_financials"] = frame.accounting_valid & ranges & frame.feature_complete
    return frame.sort_values(["report_date", "CERT"]).reset_index(drop=True)


def label_panel(frame, failures, spec):
    out = frame.copy()
    allowed = set(spec["failure_types"])
    events = {}
    for row in failures:
        if row.get("RESTYPE1") in allowed:
            key = cert(row["CERT"])
            date = pd.Timestamp(row["FAILDATE"])
            events[key] = min(date, events.get(key, date))
    out["availability_date"] = out.report_date + pd.to_timedelta(spec["availability_lag_days"], unit="D")
    out["failure_date"] = pd.to_datetime(out.CERT.map(events))
    out["already_failed"] = out.failure_date.le(out.availability_date)
    cutoff = pd.Timestamp(spec["as_of"])
    for months in [spec["horizon_months"], spec["secondary_horizon_months"]]:
        end = out.availability_date + pd.DateOffset(months=months)
        positive = (out.failure_date.gt(out.availability_date) & out.failure_date.le(end)
                    & out.failure_date.le(cutoff))
        y = pd.Series(pd.NA, index=out.index, dtype="Int64")
        y.loc[end.le(cutoff)] = 0
        y.loc[positive] = 1
        y.loc[out.already_failed] = pd.NA
        out[f"label_{months}m"] = y
    # Split by report date; enforce non-overlap of outcome windows with next split.
    out["split"] = np.select([out.report_date.le(spec["train_end"]), out.report_date.le(spec["validation_end"])],
                              ["train", "validation"], default="test")
    out["purged"] = False
    for split, boundary in [("train", spec["train_end"]), ("validation", spec["validation_end"])]:
        next_report = pd.Timestamp(boundary) + pd.offsets.QuarterEnd()
        next_available = next_report + pd.Timedelta(days=spec["availability_lag_days"])
        out.loc[out.split.eq(split) & (out.availability_date + pd.DateOffset(months=12)).ge(next_available), "purged"] = True
    return out
