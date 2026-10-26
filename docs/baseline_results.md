# Step 9: completed development baselines

135 model fits ran from committed code d4c158d on the approved frozen dataset
analysis-v1-15e5448d4a96: nine prevalence, 18 logistic, 54 XGBoost and 54 GRU fits.
Each family's OOF table contains the same 26,104 observations, 17 positive quarters
and six distinct positive banks. Model/epoch/config choices were predeclared in
configs/experiments.yaml. No final-test prediction or metric was computed.

| Model | Selected configuration | Pooled OOF AP | Brier | Quarter recall at validation 1% FPR | Detected event fraction |
|---|---|---:|---:|---:|---:|
| Training-prevalence reference | Constant within each fold | 0.001347 | 0.0006823 | 0.0000 | 0/6 |
| Logistic | C=1 | 0.196702 | 0.0007285 | 0.8235 | 6/6 |
| XGBoost | depth2, 80 trees | 0.204230 | 0.0006598 | 0.7059 | 6/6 |
| GRU | hidden8, 40 epochs | 0.051660 | 0.0006733 | 0.7647 | 5/6 |

This is model selection on development data, not an unbiased estimate of future
generalization or a statistically established model ranking. The stochastic
families use the mean of seed 11/29/47 probabilities; logistic and the reference
are deterministic. AP is average precision, not trapezoidal PR area. The reference
probability changes by fold as its training prevalence changes, so its pooled AP
need not equal the overall validation event prevalence (17/26,104).

Alert thresholds come solely from pooled OOF negatives, with strict greater-than
comparison to handle ties. Event warnings deduplicate CERTs and measure time from
assumed availability; a long warning conditional on detection is not evidence that
every event was warned. Individual outcomes/warnings and quantile calibration bins
are saved. Flexible posthoc calibration was deliberately not fitted to six banks.
Analytic training-prior correction for GRU is not proof of calibration.

The logistic model ranks failures well in these folds yet has a worse Brier score
than the prevalence reference. Calibration and ranking are separate findings.
GRU does not improve on the tabular models under the bounded search. Graph models
must face these results, rather than an artificially weak tabular comparator.

Results: results/predictive/validation_results.csv, candidate_scores.csv,
selected_models.json, per-family validation.csv.gz/calibration/warning tables and
run manifests. Local checkpoints and all artifact hashes are identified by those
manifests under results/cache/models. Candidate configurations and selected-seed
predictions can be reproduced by `uv run --locked risktrace train-baselines`.
Data and code hashes, origins, training keys and timings are retained per run.
