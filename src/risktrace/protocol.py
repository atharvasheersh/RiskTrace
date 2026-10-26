"""Forecast clocks and descriptive protocol alternatives; no model fitting."""
from __future__ import annotations

import pandas as pd

from .core import ROOT, write_json


def training_mask(panel, origin, horizon_months=12):
    """Uniformly require both classes' complete outcomes strictly before origin."""
    origin = pd.Timestamp(origin)
    available = pd.to_datetime(panel.availability_date)
    end = available + pd.DateOffset(months=horizon_months)
    return (panel.usable_financials & ~panel.already_failed
            & panel[f"label_{horizon_months}m"].notna()
            & available.lt(origin) & end.lt(origin))


def event_counts(panel):
    positive = panel.label_12m.eq(1)
    return dict(rows=len(panel), banks=panel.CERT.nunique(),
                positive_quarters=int(positive.sum()),
                distinct_positive_banks=panel.loc[positive, "CERT"].nunique())


def protocol_review(panel, directory=None):
    directory = directory or ROOT / "results/protocol_review"
    directory.mkdir(parents=True, exist_ok=True)
    # Do not inspect final-test feature values or outcomes to choose these alternatives.
    report = pd.to_datetime(panel.report_date)
    dev = panel.loc[report.lt("2022-01-01")].copy()
    valid = dev.usable_financials & ~dev.already_failed & dev.label_12m.notna()
    dev = dev.loc[valid]
    years = pd.to_datetime(dev.report_date).dt.year
    folds = []
    for year in range(2012, 2021):
        origin = pd.Timestamp(f"{year}-03-31") + pd.Timedelta(days=60)
        fit = dev.loc[training_mask(dev, origin)]
        evaluation = dev.loc[years.eq(year)]
        folds.append(dict(fold_id=f"annual_{year}", fit_as_of=str(origin.date()),
                          evaluation_report_year=year,
                          max_training_report_date=str(pd.to_datetime(fit.report_date).max().date()),
                          **{f"train_{k}": v for k, v in event_counts(fit).items()},
                          **{f"validation_{k}": v for k, v in event_counts(evaluation).items()}))
    pd.DataFrame(folds).to_csv(directory / "candidate_annual_folds.csv", index=False)
    options = []
    for name, first, last in [("original_fixed", 2019, 2021),
                              ("annual_2012_2020", 2012, 2020),
                              ("fixed_2013_2018", 2013, 2018)]:
        selection = dev.loc[years.between(first, last)]
        options.append(dict(protocol=name, first_report_year=first, last_report_year=last,
                            **event_counts(selection)))
    pd.DataFrame(options).to_csv(directory / "candidate_protocol_counts.csv", index=False)
    pd.DataFrame([dict(report_year=int(year), **event_counts(g))
                  for year, g in dev.groupby(years)]).to_csv(directory / "development_event_counts.csv", index=False)
    first_test_origin = pd.Timestamp("2022-03-31") + pd.Timedelta(days=60)
    oof = dev.loc[years.between(2012, 2020)]
    mature_oof = (pd.to_datetime(oof.availability_date) + pd.DateOffset(months=12)).lt(first_test_origin)
    assert mature_oof.all()
    final_fit = dev.loc[training_mask(dev, first_test_origin)]
    summary = dict(status="proposal_only_not_approved", development_only=True,
                   recommended_protocol="annual_2012_2020", options=options,
                   first_test_forecast_origin=str(first_test_origin.date()),
                   parameter_selection_latest_date=str((first_test_origin - pd.Timedelta(days=1)).date()),
                   all_proposed_validation_labels_mature_before_first_test=bool(mature_oof.all()),
                   latest_final_fit_report_date=str(pd.to_datetime(final_fit.report_date).max().date()),
                   final_fit_counts=event_counts(final_fit),
                   limitations=["Only six independent positive banks in pooled candidate validation",
                                "Same failure can contribute quarters to adjacent folds; do not sum fold event counts",
                                "2021 labels cannot all be known by the first 2022 forecast",
                                "No preprocessing fitted, model trained or test performance inspected"])
    write_json(directory / "protocol_review_summary.json", summary)
    return summary
