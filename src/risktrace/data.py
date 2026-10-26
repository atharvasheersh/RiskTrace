"""Official FDIC acquisition, cached provenance, panel QA and collection."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .core import ROOT, allocate, config, label_panel, normalize, report_dates, write_json


def utcnow():
    return datetime.now(timezone.utc).isoformat()


class FDIC:
    def __init__(self, spec, root=ROOT):
        self.spec, self.root = spec, Path(root)
        self.manifest, self.issues = [], []

    def page(self, endpoint, params):
        url = self.spec["api"]["base"] + "/" + endpoint + "?" + urllib.parse.urlencode(params)
        key = hashlib.sha256(url.encode()).hexdigest()[:24]
        path = self.root / self.spec["paths"]["raw"] / f"{endpoint}_{key}.json"
        info_path = path.with_suffix(".meta.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and info_path.exists():
            body = path.read_bytes()
            info = json.loads(info_path.read_text())
            if hashlib.sha256(body).hexdigest() != info["sha256"]:
                raise ValueError(f"Cache checksum mismatch: {path}")
        else:
            for attempt in range(1, 4):
                try:
                    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "RiskTrace-research/0.1"})
                    with urllib.request.urlopen(req, timeout=self.spec["api"]["timeout_seconds"]) as response:
                        body = response.read()
                    payload = json.loads(body)
                    if not isinstance(payload.get("data"), list) or "total" not in payload.get("meta", {}):
                        raise ValueError("Unexpected FDIC response schema")
                    info = dict(url=url, endpoint=endpoint, parameters=params, retrieved_utc=utcnow(),
                                path=path.relative_to(self.root).as_posix(), sha256=hashlib.sha256(body).hexdigest(),
                                bytes=len(body), total=payload["meta"]["total"], returned=len(payload["data"]),
                                source_index=payload["meta"].get("index"))
                    path.write_bytes(body)
                    write_json(info_path, info)
                    break
                except Exception as exc:
                    self.issues.append(dict(url=url, attempt=attempt, utc=utcnow(), error=str(exc)))
                    self.save("partial")
                    if attempt == 3:
                        raise
                    time.sleep(attempt)
        self.manifest.append(info)
        return json.loads(body)

    def fetch(self, endpoint, filters, fields):
        all_rows, total, offset = [], None, 0
        while total is None or offset < total:
            p = dict(filters=filters, fields=",".join(fields), limit=self.spec["api"]["page_size"],
                     offset=offset, sort_by="CERT" if endpoint == "financials" else "FAILDATE",
                     sort_order="ASC", format="json")
            result = self.page(endpoint, p)
            expected = int(result["meta"]["total"])
            if total is not None and expected != total:
                raise ValueError("Source total changed during pagination")
            total = expected
            rows = [r["data"] for r in result["data"]]
            if not rows and offset < total:
                raise ValueError("Premature empty page")
            all_rows.extend(rows)
            offset += len(rows)
        if len(all_rows) != total:
            raise ValueError("Returned count differs from source total")
        return all_rows

    def save(self, mode):
        write_json(self.root / "data/manifests" / f"{mode}_sources.json", self.manifest)
        write_json(self.root / "data/manifests" / f"{mode}_request_issues.json", self.issues)


def quarter_filter(date, spec):
    classes = " OR ".join(spec["bank_classes"])
    # Source balance amounts are integer thousands; explicit client check also runs.
    return (f"REPDTE:{date} AND ASSET:[{spec['asset_min_thousands']} TO "
            f"{spec['asset_max_exclusive_thousands'] - 1}] AND BKCLASS:({classes})")


def summarize(panel, failures, spec):
    y = f"label_{spec['horizon_months']}m"
    usable = panel.usable_financials & ~panel.already_failed & panel[y].notna()
    events = panel.loc[panel[y].eq(1), "CERT"].nunique()
    missing = {k: int(panel[k].isna().sum()) for k in spec["api"]["financial_fields"]}
    quarters = []
    for date, g in panel.groupby("report_date", sort=True):
        quarters.append(dict(report_date=str(date.date()), rows=len(g), banks=g.CERT.nunique(),
                             usable=int(usable.loc[g.index].sum()), positive_quarters=int(g[y].eq(1).sum()),
                             invalid_accounting=int((~g.accounting_valid).sum()), invalid_ranges=int((~g.range_valid).sum())))
    return dict(rows=len(panel), banks=panel.CERT.nunique(), quarters=panel.report_date.nunique(),
                eligible_rows=int(panel.eligible.sum()), financial_usable_rows=int(panel.usable_financials.sum()),
                usable_labeled_rows=int(usable.sum()), positive_quarters=int(panel[y].eq(1).sum()),
                distinct_positive_banks=events, already_failed_rows=int(panel.already_failed.sum()),
                censored_rows=int((panel[y].isna() & ~panel.already_failed).sum()),
                failure_source_records=len(failures), missing_fields=missing, quarter_coverage=quarters)


def collect(mode="pilot"):
    spec = config()
    client = FDIC(spec)
    start, end = (spec["pilot_start"], spec["pilot_end"]) if mode == "pilot" else (spec["start"], spec["end"])
    dates = report_dates(start, end)
    failures = client.fetch("failures", f"FAILDATE:[2010-01-01 TO {spec['as_of']}]", spec["api"]["failure_fields"])
    # API index age is not a guarantee of completeness; use its date as a conservative censoring bound.
    index_date = client.manifest[-1]["source_index"]["createTimestamp"][:10]
    spec["as_of"] = min(spec["as_of"], index_date)
    all_rows, counts = [], []
    try:
        for i, date in enumerate(dates, 1):
            rows = client.fetch("financials", quarter_filter(date, spec), spec["api"]["financial_fields"])
            all_rows.extend(rows)
            counts.append(dict(report_date=date, source_count=len(rows)))
            client.save(mode)
            print(f"{mode} {i}/{len(dates)} {date}: {len(rows)} source rows", flush=True)
    finally:
        client.save(mode)
    panel = label_panel(normalize(all_rows, spec), failures, spec)
    if not panel.eligible.all():
        raise ValueError("Source filter returned ineligible rows")
    directory = ROOT / spec["paths"]["processed"]
    directory.mkdir(parents=True, exist_ok=True)
    panel.to_csv(directory / f"{mode}_panel.csv", index=False)
    pd.DataFrame(failures).to_csv(directory / "failures.csv", index=False)
    summary = summarize(panel, failures, spec)
    summary.update(label_cutoff=spec["as_of"], source_quarter_counts=counts,
                   config_sha256=hashlib.sha256((ROOT / "configs/data_spec.yaml").read_bytes()).hexdigest(),
                   panel_sha256=hashlib.sha256((directory / f"{mode}_panel.csv").read_bytes()).hexdigest())
    write_json(ROOT / "results" / f"{mode}_data_summary.json", summary)
    if mode != "pilot":
        raise NotImplementedError("Full allocation workflow is added after the novelty pilot")
    # Small committed excerpt is intentionally nonrepresentative and carries CERT/date keys.
    panel.sort_values(["CERT", "report_date"]).groupby("CERT").head(1).head(12).to_csv(ROOT / "results/pilot_panel_excerpt.csv", index=False)
    return summary
