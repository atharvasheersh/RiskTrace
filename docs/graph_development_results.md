# Step 10: graph development evidence

162 graph fits ran from committed implementation b83a7bc: 54 static GAT, 54
feature GAT+GRU, and 27 each of fixed random/state-first GAT+GRU controls. All use
the same 26,104 OOF records as the baselines, with 17 positive quarters from six
banks. Two kNN choices (3/7) were considered for feature models; k=3 won development
AP for both. The controls were fixed k=3. No final-test metric was inspected.

| Model | Selected graph | Development AP | Brier |
|---|---|---:|---:|
| XGBoost | No graph | 0.204230 | 0.00065985 |
| Logistic | No graph | 0.196702 | 0.00072852 |
| GRU | No graph | 0.051660 | 0.00067325 |
| Static GAT | Financial k=3 | 0.068351 | 0.00066136 |
| GAT+GRU | Financial k=3 | 0.060116 | 0.00065481 |
| GAT+GRU | Random k=3 | 0.027314 | 0.00066950 |
| GAT+GRU | State-first k=3 | 0.024304 | 0.00076596 |

Graph models do not justify a predictive-superiority claim against the strong
tabular models on AP. The temporal graph's slightly smaller Brier score is a
separate, exploratory loss/calibration finding, not proof of an important gain.
The financial graph outperforms these fixed random/exogenous controls on AP, but
six selected validation events and a bounded search prevent strong significance
or architectural-generalization claims. Static GAT exceeds GAT+GRU here; adding
recurrence does not automatically improve prediction.

All candidate metrics, selected configurations, OOF forecasts, calibration/warnings
and run/graph/checkpoint hashes are under results/predictive. Recorded graph
condition runtimes total approximately 827.7 seconds; these include preparation
and inference, are machine-specific and do not predict full-scale costs. Checkpoint
files remain local, referenced by manifests. The trained variants are actual GAT
and GRU models, unlike the separate Step 6 mechanism pilot.

Keep the chosen configurations. Do not enlarge the search or change the cohort/
label after seeing these results. Final model, explanation, perturbation and
uncertainty settings are to be hash-frozen before opening test performance.
