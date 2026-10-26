import numpy as np
import pandas as pd
import pytest
from risktrace.analysis import compare_raw_fields, immutable, preprocess_fit, transform


def test_matching_keys_do_not_hide_conflicting_source_values():
    a = pd.DataFrame(dict(CERT=["123"], REPDTE=["20100331"], ASSET=[1000000], NAME=["Source name"]))
    b = a.copy(); b["ASSET"] = 1000001
    result = compare_raw_fields(a, b, list(a.columns))
    assert result.field.tolist() == ["ASSET"]
    with pytest.raises(ValueError, match="Duplicate"):
        compare_raw_fields(a, pd.concat([a, a]), list(a.columns))


def test_immutable_data_cannot_be_silently_replaced(tmp_path):
    p = tmp_path / "snapshot.csv"
    immutable(p, b"first")
    immutable(p, b"first")
    with pytest.raises(ValueError, match="immutable"):
        immutable(p, b"different")


def test_heldout_extreme_values_cannot_change_training_preprocessing():
    fit = pd.DataFrame(dict(x=[1., 3.], report_date=pd.to_datetime(["2010-03-31", "2010-06-30"]),
                            horizon_end_12m=pd.to_datetime(["2011-05-30", "2011-08-29"]), row_id=["a", "b"]))
    prep = preprocess_fit(fit, ["x"], "2012-05-30", "source-hash")
    np.testing.assert_array_equal(transform(pd.DataFrame({"x":[1000000]}), prep), [[999998]])
    assert prep["mean"] == [2.] and prep["scale"] == [1.]
