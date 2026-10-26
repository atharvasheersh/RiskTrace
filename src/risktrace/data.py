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
        write_json(self.root / self.spec["paths"]["manifests"] / f"{mode}_sources.json", self.manifest)
        write_json(self.root / self.spec["paths"]["manifests"] / f"{mode}_request_issues.json", self.issues)


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
        return finalize_collection(panel, summary, spec)
    # Small committed excerpt is intentionally nonrepresentative and carries CERT/date keys.
    panel.sort_values(["CERT", "report_date"]).groupby("CERT").head(1).head(12).to_csv(ROOT / "results/pilot_panel_excerpt.csv", index=False)
    return summary


def coverage_register(panel, owners):
    """Source-backed eligible coverage, with interrupted histories kept separate."""
    records, gaps = [], []
    for key, g in panel.groupby("CERT", sort=True):
        dates = set(g.report_date)
        missing = sorted(set(pd.date_range(g.report_date.min(), g.report_date.max(), freq="QE")) - dates)
        for date in missing:
            gaps.append(dict(CERT=key, owner=owners[key], report_date=str(date.date()),
                             issue="No eligible financial record; band exit, lifecycle or source omission unresolved"))
        y = g.label_12m
        records.append(dict(CERT=key, owner=owners[key], latest_name=g.iloc[-1]["NAME"],
                            first_eligible=str(g.report_date.min().date()), last_eligible=str(g.report_date.max().date()),
                            expected_eligible_records=len(g), bulk_available_records=len(g),
                            collected_records=len(g) if owners[key].startswith("Atharva") else None,
                            missing_eligible_records=0 if owners[key].startswith("Atharva") else None,
                            financial_usable_records=int(g.usable_financials.sum()),
                            usable_labeled_records=int((g.usable_financials & ~g.already_failed & y.notna()).sum()),
                            censored_records=int((y.isna() & ~g.already_failed).sum()),
                            already_failed_records=int(g.already_failed.sum()),
                            potential_interruption_quarters=len(missing),
                            collaboration_status="Atharva collection validated" if owners[key].startswith("Atharva")
                            else "Ayush submission not received or checked; broader bulk exists"))
    return pd.DataFrame(records), pd.DataFrame(gaps, columns=["CERT", "owner", "report_date", "issue"])


def finalize_collection(panel, source_summary, spec):
    owners = allocate(panel.CERT, spec["allocation_salt"])
    register, gaps = coverage_register(panel, owners)
    gaps = verify_gaps(gaps, spec)
    unresolved = gaps.loc[gaps.resolution.eq("no source report returned")].groupby("CERT").size()
    register["unresolved_interruption_quarters"] = register.CERT.map(unresolved).fillna(0).astype(int)
    register.to_csv(ROOT / "data/bank_allocation.csv", index=False)
    gaps.to_csv(ROOT / "results/bank_period_gaps.csv", index=False)
    assigned = panel.loc[panel.CERT.map(owners).eq("Atharva Sheersh Pandey")].copy()
    assigned["owner"] = "Atharva Sheersh Pandey"
    path = ROOT / spec["paths"]["processed"] / "atharva_bank_panel.csv"
    assigned.to_csv(path, index=False)
    assigned.head(16).to_csv(ROOT / "results/atharva_panel_excerpt.csv", index=False)
    coverage = []
    for owner, banks in register.groupby("owner"):
        subset = panel.loc[panel.CERT.isin(banks.CERT)]
        coverage.append(dict(owner=owner, assigned_banks=len(banks),
                             expected_eligible_bank_quarters=int(banks.expected_eligible_records.sum()),
                             collected_eligible_bank_quarters=len(subset) if owner.startswith("Atharva") else None,
                             missing_eligible_records=0 if owner.startswith("Atharva") else None,
                             unusable_financial_records=int((~subset.usable_financials).sum()) if owner.startswith("Atharva") else None,
                             usable_labeled_records=int((subset.usable_financials & ~subset.already_failed & subset.label_12m.notna()).sum()) if owner.startswith("Atharva") else None,
                             potential_interruption_quarters=int(banks.potential_interruption_quarters.sum()),
                             unresolved_interruption_quarters=int(banks.unresolved_interruption_quarters.sum()),
                             status="validated against bulk source totals; interruption resolutions recorded separately" if owner.startswith("Atharva") else "submission not received or checked; no completion claim"))
    write_json(ROOT / "results/collection_coverage.json", dict(
        eligible_banks=len(owners), total_eligible_bank_quarters=len(panel), quarters=panel.report_date.nunique(),
        allocation_rule="SHA256('RiskTrace-v1:' + canonical CERT), ascending, alternating Atharva then Ayush; odd extra to Atharva",
        expected_definition="all official returned eligible CERT/quarter records after count/uniqueness checks, not 64 rows for every bank",
        label_cutoff=source_summary["label_cutoff"], owners=coverage,
        scope_limit="No independent historical roster reconciliation or point-in-time publication vintages; merger/competing-risk analysis remains incomplete"))
    files = []
    for p in [ROOT / "data/processed/full_panel.csv", path, ROOT / "data/processed/failures.csv"]:
        files.append(dict(path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                          bytes=p.stat().st_size, generated_utc=utcnow()))
    write_json(ROOT / "data/manifests/processed_datasets.json", dict(
        files=files, config_sha256=source_summary["config_sha256"], label_cutoff=source_summary["label_cutoff"],
        source_manifest="data/manifests/full_sources.json", transform="risktrace.core.normalize/label_panel; risktrace.data.finalize_collection"))
    missing = []
    for date, g in assigned.groupby("report_date"):
        for field in spec["api"]["financial_fields"]:
            count = int(g[field].isna().sum())
            if count:
                missing.append(dict(report_date=str(date.date()), field=field, missing_rows=count, total_rows=len(g)))
    pd.DataFrame(missing, columns=["report_date", "field", "missing_rows", "total_rows"]).to_csv(ROOT / "results/atharva_missing_fields.csv", index=False)
    assigned.loc[~assigned.usable_financials | assigned.already_failed,
                 ["CERT", "REPDTE", "accounting_valid", "range_valid", "feature_complete", "already_failed"]].to_csv(
                     ROOT / "results/atharva_unusable_records.csv", index=False)
    feasibility = []
    for split, g in panel.groupby("split"):
        eligible = g.usable_financials & ~g.already_failed & ~g.purged & g.label_12m.notna()
        h = g.loc[eligible]
        feasibility.append(dict(split=split, raw_rows=len(g), usable_unpurged_rows=len(h),
                                positive_bank_quarters=int(h.label_12m.eq(1).sum()),
                                distinct_positive_banks=h.loc[h.label_12m.eq(1), "CERT"].nunique(),
                                note="descriptive event sufficiency only; no final-test model fitting or tuning"))
    pd.DataFrame(feasibility).to_csv(ROOT / "results/event_feasibility_by_split.csv", index=False)
    return source_summary


def verify_gaps(gaps, spec):
    """Query interrupted CERT histories without the asset/class filter."""
    client, source = FDIC(spec), []
    ids = sorted(set(gaps.CERT))
    try:
        for offset in range(0, len(ids), 40):
            batch = ids[offset:offset + 40]
            filters = ("CERT:(" + " OR ".join(batch) + ") AND REPDTE:["
                       + spec["start"].replace("-", "") + " TO " + spec["end"].replace("-", "") + "]")
            source.extend(client.fetch("financials", filters, ["CERT", "REPDTE", "ASSET", "BKCLASS"]))
            client.save("gap_validation")
            print(f"Validated unfiltered histories for gap banks {min(offset + 40, len(ids))}/{len(ids)}", flush=True)
    finally:
        client.save("gap_validation")
    lookup = {}
    for row in source:
        key = (str(int(row["CERT"])), str(pd.to_datetime(str(row["REPDTE"]), format="%Y%m%d").date()))
        if key in lookup:
            raise ValueError("Duplicate key in gap-validation history")
        lookup[key] = row
    resolutions, assets, classes = [], [], []
    for row in gaps.itertuples():
        record = lookup.get((row.CERT, row.report_date))
        if record is None:
            resolutions.append("no source report returned"); assets.append(None); classes.append(None)
        else:
            asset = record.get("ASSET")
            bkclass = record.get("BKCLASS")
            if asset is not None and spec["asset_min_thousands"] <= asset < spec["asset_max_exclusive_thousands"] and bkclass in spec["bank_classes"]:
                raise ValueError(f"Eligible report omitted from primary download: {row.CERT} {row.report_date}")
            resolutions.append("confirmed outside asset band" if asset is not None and not
                               spec["asset_min_thousands"] <= asset < spec["asset_max_exclusive_thousands"]
                               else "confirmed outside bank class or unavailable eligibility field")
            assets.append(asset); classes.append(bkclass)
    result = gaps.copy()
    result["resolution"], result["source_ASSET_thousands"], result["source_BKCLASS"] = resolutions, assets, classes
    return result


def verify_integration(path):
    """Validate a submitted Ayush raw-schema CSV without overwriting collected data."""
    spec = config()
    incoming = pd.read_csv(path, dtype={"CERT": str, "REPDTE": str})
    missing = set(spec["api"]["financial_fields"]) - set(incoming.columns)
    if missing:
        raise ValueError(f"Missing raw columns: {sorted(missing)}")
    parsed = normalize(incoming.to_dict("records"), spec)
    allocation = pd.read_csv(ROOT / "data/bank_allocation.csv", dtype={"CERT": str})
    expected_ids = set(allocation.loc[allocation.owner.eq("Ayush Sinha"), "CERT"])
    if not set(parsed.CERT) <= expected_ids:
        raise ValueError("Submission includes banks outside Ayush's allocation")
    full = pd.read_csv(ROOT / "data/processed/full_panel.csv", dtype={"CERT": str, "REPDTE": str}, low_memory=False)
    expected = set(zip(full.loc[full.CERT.isin(expected_ids), "CERT"], full.loc[full.CERT.isin(expected_ids), "REPDTE"]))
    observed = set(zip(parsed.CERT, parsed.REPDTE.astype(str)))
    if observed - expected:
        raise ValueError("Submission includes unexpected bank-quarter keys")
    return dict(expected=len(expected), observed=len(observed), missing=len(expected - observed),
                unusable_financials=int((~parsed.usable_financials).sum()),
                complete=(observed == expected), note="Schema/key/QA validation only; compare source hashes and substantive field values before integration")
