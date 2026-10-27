# Frozen final predictive evaluation: negative practical finding

The corrected pre-opening plan was committed as 86f3f7c, after a rejected CRLF/LF
guard attempt that did not access test performance. The first actual opening is
timestamped in results/final_evaluation/holdout_opening.json. No model settings,
thresholds, data membership or graph choices were retuned after opening.

There are 12,783 usable, fully mature test bank-quarters, with 16 positive quarters
from **four distinct failed banks**. The nominal holdout is 2022--2025, but the
observable report range is **2022Q1--2025Q1**: late-2025 horizons are censored by the
preserved August 2026 outcome cutoff. No censored negative is invented.

| Model | Test AP | Brier | Achieved false-alarm rate | Quarter recall | Detected failed banks |
|---|---:|---:|---:|---:|---:|
| Prevalence | 0.001252 | 0.0012507 | 0.0000 | 0.00 | 0/4 |
| Logistic | 0.017785 | 0.0016165 | 0.0201 | 0.25 | 1/4 |
| XGBoost | 0.006225 | 0.0012527 | 0.0033 | 0.00 | 0/4 |
| GRU | 0.001614 | 0.0012540 | 0.0016 | 0.00 | 0/4 |
| Static GAT | 0.007536 | 0.0012499 | 0.0006 | 0.00 | 0/4 |
| Financial GAT+GRU | 0.001961 | 0.0012541 | 0.0034 | 0.00 | 0/4 |
| Random GAT+GRU | 0.001923 | 0.0012519 | 0.0017 | 0.00 | 0/4 |
| State-first GAT+GRU | 0.001054 | 0.0012523 | 0.0002 | 0.00 | 0/4 |
| Other-k GAT+GRU sensitivity | 0.001538 | 0.0012527 | 0.0026 | 0.00 | 0/4 |

The alert thresholds target 1% false alarms **on validation**. The achieved test
rates above are measured, not forced to 1% through test retuning. Logistic's one
detected bank has a 332-day first warning under assumed availability; this is
conditional on detection and does not describe the three missed failures.

No deployable warning-system or predictive-superiority claim is supported. Static
GAT ranks above XGBoost on test AP but far below logistic and detects no event at
its fixed threshold; its tiny Brier difference is not established as meaningful.
The development winner did not transfer well. The cause of that change is not
identified causally by these experiments, and four events are insufficient for
strong model ranking. Do not select a new winner or search new settings on this
test. Continue the prespecified explanation mechanism audit, with its weak
predictor and sparse-event limits explicit.

Twenty-three final model fits cover all selected families/seeds plus the
prespecified other-k sensitivity. Small checkpoints/preprocessing are preserved
under artifacts and hash-referenced by fit_manifest.json; source data remain in
the versioned local snapshot. Individual forecasts, seed metrics, warning records
and calibration bins are under results/final_evaluation. Independent verification
and prespecified bank/time uncertainty follow; they do not turn this into strong
financial prediction evidence or publication readiness.
