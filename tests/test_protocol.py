import pandas as pd
from risktrace.protocol import training_mask, protocol_review


def test_uniform_maturity_excludes_early_known_positives_and_same_day_boundary():
    p = pd.DataFrame(dict(availability_date=["2020-05-30", "2020-05-29", "2021-01-01"],
                          usable_financials=[True]*3, already_failed=[False]*3, label_12m=[0, 0, 1]))
    assert training_mask(p, "2021-05-30").tolist() == [False, True, False]


def test_protocol_review_never_includes_final_test_rows(tmp_path):
    rows = []
    for year in range(2010, 2026):
        rows.append(dict(CERT=str(year), report_date=f"{year}-03-31", availability_date=f"{year}-05-30",
                         usable_financials=True, already_failed=False, label_12m=int(year == 2024)))
    result = protocol_review(pd.DataFrame(rows), tmp_path)
    assert all(x["positive_quarters"] == 0 for x in result["options"])
    assert result["status"] == "proposal_only_not_approved"
    assert result["latest_final_fit_report_date"] == "2020-03-31"
