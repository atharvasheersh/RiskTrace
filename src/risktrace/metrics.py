"""Explicit rare-event metrics and alert clocks; no threshold fitting on test."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score


def alarm_threshold(y, probability, false_alarm_rate=.01):
    negative = np.asarray(probability)[np.asarray(y) == 0]
    if not len(negative):
        raise ValueError("No validation negatives for false-alarm threshold")
    # Strict > plus higher quantile keeps ties from exceeding the target FPR.
    return float(np.quantile(negative, 1-false_alarm_rate, method="higher"))


def prediction_metrics(frame, threshold):
    y, p = frame.y.to_numpy(int), frame.probability.to_numpy(float)
    alarm = p > threshold
    positive = y == 1
    negative = ~positive
    events = frame.loc[positive].copy()
    events["alarm"] = alarm[positive]
    warnings = []
    for key, g in events.groupby("CERT"):
        hits = g.loc[g.alarm]
        days = None if not len(hits) else int((pd.to_datetime(hits.failure_date).iloc[0]
                                               - pd.to_datetime(hits.availability_date).min()).days)
        warnings.append(dict(CERT=key, detected=bool(len(hits)), warning_days=days))
    detected = [r["warning_days"] for r in warnings if r["detected"]]
    both = len(np.unique(y)) > 1
    return dict(rows=len(frame), positive_quarters=int(positive.sum()),
                distinct_positive_banks=len(warnings), prevalence=float(y.mean()),
                average_precision=float(average_precision_score(y, p)) if positive.any() else None,
                auroc=float(roc_auc_score(y, p)) if both else None,
                brier=float(np.mean((y-p)**2)), threshold=float(threshold),
                false_alarm_rate=float(alarm[negative].mean()) if negative.any() else None,
                quarter_recall=float(alarm[positive].mean()) if positive.any() else None,
                event_recall=len(detected)/len(warnings) if warnings else None,
                detected_events=len(detected), missed_events=len(warnings)-len(detected),
                median_warning_days_detected=float(np.median(detected)) if detected else None), warnings


def calibration_table(frame, bins=10):
    p = frame.probability
    edges = np.unique(np.quantile(p, np.linspace(0, 1, bins+1)))
    groups = np.zeros(len(frame), int) if len(edges) < 2 else np.searchsorted(edges[1:-1], p, side="right")
    return frame.assign(bin=groups).groupby("bin").agg(rows=("y", "size"),
        mean_probability=("probability", "mean"), observed_frequency=("y", "mean"), positive_quarters=("y", "sum"))
