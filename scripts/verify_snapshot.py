"""Verify the preserved local source/processed/experiment snapshot without network."""
import hashlib
import json
import platform
from importlib.metadata import version

import numpy as np
import pandas as pd

from risktrace.core import ROOT, RATIOS, allocate, config, label_panel, normalize, write_json


def main():
    manifests = ["pilot", "pilot_v1", "full", "gap_validation", "unit_crosscheck", "accounting_crosscheck"]
    checked = {}
    for mode in manifests:
        for record in json.loads((ROOT / f"data/manifests/{mode}_sources.json").read_text()):
            path = ROOT / record["path"]
            body = path.read_bytes()
            assert hashlib.sha256(body).hexdigest() == record["sha256"], path
            assert len(body) == record["bytes"], path
            payload = json.loads(body)
            assert len(payload["data"]) == record["returned"]
            assert payload["meta"]["total"] == record["total"]
            checked[record["path"]] = record["sha256"]
    processed = json.loads((ROOT / "data/manifests/processed_datasets.json").read_text())
    for record in processed["files"]:
        body = (ROOT / record["path"]).read_bytes()
        assert hashlib.sha256(body).hexdigest() == record["sha256"]
        assert len(body) == record["bytes"]
    spec = config()
    spec["as_of"] = processed["label_cutoff"]
    panel = pd.read_csv(ROOT / "data/processed/full_panel.csv", dtype={"CERT": str, "REPDTE": str}, low_memory=False)
    failures = pd.read_csv(ROOT / "data/processed/failures.csv").to_dict("records")
    recomputed = label_panel(normalize(panel[spec["api"]["financial_fields"]].to_dict("records"), spec), failures, spec)
    assert len(recomputed) == len(panel) and recomputed.eligible.all()
    for field in RATIOS:
        np.testing.assert_allclose(recomputed[field], panel[field], rtol=1e-12, atol=1e-12, equal_nan=True)
    for field in ["accounting_valid", "range_valid", "feature_complete", "usable_financials", "already_failed", "purged"]:
        assert recomputed[field].tolist() == panel[field].tolist(), field
    for field in ["label_12m", "label_3m"]:
        np.testing.assert_array_equal(recomputed[field].fillna(-1).astype(int), panel[field].fillna(-1).astype(int))
    owners = allocate(panel.CERT, spec["allocation_salt"])
    register = pd.read_csv(ROOT / "data/bank_allocation.csv", dtype={"CERT": str})
    assert owners == dict(zip(register.CERT, register.owner))
    atharva = pd.read_csv(ROOT / "data/processed/atharva_bank_panel.csv", dtype={"CERT": str, "REPDTE": str})
    expected = panel.loc[panel.CERT.map(owners).eq("Atharva Sheersh Pandey")]
    assert set(zip(atharva.CERT, atharva.REPDTE)) == set(zip(expected.CERT, expected.REPDTE))
    assert not atharva.duplicated(["CERT", "REPDTE"]).any()
    sources = json.loads((ROOT / "data/manifests/full_sources.json").read_text())
    assert sum(m["total"] for m in sources if m["endpoint"] == "financials") == len(panel)
    params = json.loads((ROOT / "results/audit_parameters.json").read_text())
    for record in params:
        body = b"".join(np.asarray(record[k], dtype=float).tobytes() for k in ["mean", "scale", "coefficients", "intercept"])
        assert hashlib.sha256(body).hexdigest() == record["sha256"]
    cases = pd.read_csv(ROOT / "results/audit_cases.csv")
    assert cases.loc[cases.kind.ne("feature"), "max_response_gap"].eq(0).all()
    assert not cases.duplicated(["dataset", "kind", "k", "seed", "target", "edit_period"]).any()
    report = dict(status="passed", unique_source_snapshots=len(checked), processed_hashes_verified=len(processed["files"]),
                  full_bank_quarters=len(panel), eligible_banks=panel.CERT.nunique(),
                  atharva_banks=atharva.CERT.nunique(), atharva_bank_quarters=len(atharva),
                  all_financial_features_labels_and_flags_recomputed=True, allocation_recomputed=True,
                  audit_parameter_fingerprints_verified=len(params), audit_cases_verified=len(cases),
                  python=platform.python_version(), versions={k: version(k) for k in ["numpy", "pandas", "scikit-learn", "PyYAML"]},
                  caveat="Internal snapshot/provenance consistency only; not independent certification of source accuracy or publication novelty")
    write_json(ROOT / "results/snapshot_validation.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
