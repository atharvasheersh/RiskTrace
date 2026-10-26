import pandas as pd
import pytest
from risktrace.core import allocate, cert, config, label_panel, normalize, report_dates


def row(**updates):
    base = dict(CERT=123, REPDTE="20100331", BKCLASS="NM", ASSET=1000000,
                LIAB=900000, EQ=99000, EQTOT=100000, DEP=800000, DEPDOM=700000, DEPUNINS=140000,
                CHBAL=100000, LNLSNET=500000, LNLSGR=510000, NCLNLS=10000, SC=200000)
    return base | updates


def test_identifiers_and_balanced_allocation():
    assert cert("123.0") == "123"
    for bad in [1.5, "nan", 0]:
        with pytest.raises(ValueError):
            cert(bad)
    a = allocate([1, 2, 3, 4, 5])
    assert a == allocate([5, 4, 3, 2, 1, 1])
    assert list(a.values()).count("Atharva Sheersh Pandey") == 3


def test_units_bounds_missingness_and_deposit_scope():
    s = config()
    d = normalize([row(), row(CERT=124, ASSET=250000000), row(CERT=125, CHBAL=None)], s)
    assert d.eligible.tolist() == [True, False, True]
    assert d.iloc[0].uninsured_domestic_ratio == .2
    assert not d.iloc[2].feature_complete
    assert not d.iloc[2].usable_financials
    assert not normalize([row(EQTOT=200000)], s).iloc[0].accounting_valid
    with pytest.raises(ValueError, match="Duplicate"):
        normalize([row(), row()], s)


def test_label_clock_event_types_and_censoring():
    s = config()
    x = normalize([row(), row(CERT=124), row(CERT=125, REPDTE="20251231")], s)
    f = [dict(CERT=123, FAILDATE="2010-06-01", RESTYPE1="PA"),
         dict(CERT=124, FAILDATE="2010-06-01", RESTYPE1="A/A")]
    d = label_panel(x, f, s).set_index("CERT")
    assert d.loc["123", "availability_date"] == pd.Timestamp("2010-05-30")
    assert d.loc["123", "label_12m"] == 1
    assert d.loc["124", "label_12m"] == 0
    assert pd.isna(d.loc["125", "label_12m"])
    d = label_panel(x, [dict(CERT=123, FAILDATE="2010-05-01", RESTYPE1="PA")], s).set_index("CERT")
    assert pd.isna(d.loc["123", "label_12m"])
    assert len(report_dates(s["start"], s["end"])) == 64


def test_outcome_windows_are_purged_at_split_boundaries():
    s = config()
    d = label_panel(normalize([row(REPDTE="20181231")], s), [], s)
    assert d.iloc[0].purged
