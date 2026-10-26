# Prespecified bounded development budget

Dataset analysis-v1-15e5448d4a96, nine approved expanding-origin folds. No final
test performance may be opened during candidate selection. All zero-event years
remain in the pooled OOF predictions. Settings are in configs/experiments.yaml.

Fit prevalence reference, logistic regression (C=.1/1), XGBoost (depth2/3, 80 trees)
and GRU (hidden8/16, 40 fixed epochs) in that order. Deterministic tabular reference/
logistic use one seed; stochastic XGBoost/GRU use 11/29/47. Each learned family has
two candidate configurations, not unlimited tuning. Selection uses AP of mean
seed probabilities, with lower Brier as tie-break. AUROC is secondary. No oversampling
or test-based early stopping. Neural models use two CPU threads, clipping and fixed
L2 decay; no dropout or paid compute.

The neural weighted training objective caps positive weight at 100, fitted from
training class counts. Subtract log(weight) from logits for analytic prior
correction. This is not a guarantee of calibration. Tabular models use unweighted
objectives. Given six positive validation banks, no flexible Platt/isotonic calibrator
is fitted; evaluate Brier and quantile-bin calibration and report residual error.
These choices prioritize bounded exploratory comparisons and do not make the
deep baseline exhaustive or state of the art.

Alert thresholds use the pooled validation-negative 99th percentile with strict
greater-than comparison; ties cannot exceed the target 1% bank-quarter false-alarm
rate. Event recall/warning time deduplicate CERTs and use assumed availability
dates. Average precision is the primary PR summary, not trapezoidal PR area.

Graph development will receive the same two-width/two-configuration, three-seed,
fixed-epoch budget and the same folds/preprocessing where applicable. Record
runtime/checkpoint hashes. Run small smoke checks first, then commit implementation
before the frozen development runs; outcomes are saved under identifiable code.

Pinned XGBoost 2.1.4 is documented as compatible with scikit-learn 1.6:
https://xgboost.readthedocs.io/en/stable/changes/v2.1.0.html.
PyTorch CPU binaries are from its official version index:
https://pytorch.org/get-started/previous-versions/.
Pins are deliberate reproducibility choices, not claims these are newest releases.
