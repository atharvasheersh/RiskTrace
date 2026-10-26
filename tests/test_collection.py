import pandas as pd
from risktrace.core import allocate
from risktrace.data import coverage_register


def test_interrupted_history_is_not_mistaken_for_missing_eligible_source_rows():
    panel = pd.DataFrame(dict(CERT=["11", "11", "22"], NAME=["Bank A", "Bank A", "Bank B"],
                              report_date=pd.to_datetime(["2010-03-31", "2010-09-30", "2010-03-31"]),
                              usable_financials=[True, False, True], label_12m=[0, 1, 0],
                              already_failed=[False, False, False]))
    r, gaps = coverage_register(panel, allocate(panel.CERT))
    a = r.set_index("CERT").loc["11"]
    assert a.expected_eligible_records == a.bulk_available_records == 2
    if a.owner.startswith("Atharva"):
        assert a.collected_records == 2 and a.missing_eligible_records == 0
    else:
        assert pd.isna(a.collected_records) and pd.isna(a.missing_eligible_records)
    assert a.potential_interruption_quarters == 1
    assert a.financial_usable_records == 1
    assert gaps.iloc[0].report_date == "2010-06-30"


def test_integration_checks_ownership_and_expected_keys_before_merge(tmp_path, monkeypatch):
    import pytest
    import risktrace.data as module
    from risktrace.core import config
    monkeypatch.setattr(module, "ROOT", tmp_path)
    (tmp_path / "data/processed").mkdir(parents=True)
    pd.DataFrame({"CERT": ["123", "124"], "owner": ["Ayush Sinha", "Atharva Sheersh Pandey"]}).to_csv(
        tmp_path / "data/bank_allocation.csv", index=False)
    sample = {k: 0 for k in config()["api"]["financial_fields"]}
    sample.update(CERT="123", REPDTE="20100331", NAME="Constructed test bank", BKCLASS="NM", ASSET=1000000,
                  LIAB=900000, EQ=100000, EQTOT=100000, DEP=800000, DEPDOM=800000, CHBAL=100000,
                  LNLSNET=500000, LNLSGR=510000, NCLNLS=10000, SC=200000)
    pd.DataFrame([sample]).to_csv(tmp_path / "data/processed/full_panel.csv", index=False)
    incoming = tmp_path / "incoming.csv"
    pd.DataFrame([sample]).to_csv(incoming, index=False)
    result = module.verify_integration(incoming)
    assert result["complete"] and result["observed"] == 1 and result["missing"] == 0
    pd.DataFrame([sample | {"CERT": "124"}]).to_csv(incoming, index=False)
    with pytest.raises(ValueError, match="outside Ayush"):
        module.verify_integration(incoming)
    pd.DataFrame([sample | {"REPDTE": "20100630"}]).to_csv(incoming, index=False)
    with pytest.raises(ValueError, match="unexpected bank-quarter"):
        module.verify_integration(incoming)


def test_unfiltered_gap_validation_detects_omitted_eligible_records(monkeypatch):
    import pytest
    import risktrace.data as module
    from risktrace.core import config
    rows = [dict(CERT=11, REPDTE="20100630", ASSET=999999, BKCLASS="NM")]
    class Source:
        def fetch(self, *args):
            return rows
        def save(self, *args):
            pass
    monkeypatch.setattr(module, "FDIC", lambda spec: Source())
    gaps = pd.DataFrame([dict(CERT="11", owner="Atharva Sheersh Pandey", report_date="2010-06-30", issue="gap")])
    checked = module.verify_gaps(gaps, config())
    assert checked.iloc[0].resolution == "confirmed outside asset band"
    rows[0]["ASSET"] = 1000000
    with pytest.raises(ValueError, match="Eligible report omitted"):
        module.verify_gaps(gaps, config())
