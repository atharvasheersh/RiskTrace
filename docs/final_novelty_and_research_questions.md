# Supported novelty and research questions after the frozen experiments

Updated 27 October 2026. This assessment uses completed experiments, not the
original architecture proposal. The defensible contribution is a **scoped
dependency-aware empirical audit**, with modest and provisional methodological
novelty. A high-novelty or Q1-readiness claim is not supported by the current study.

## The contribution that survives

For the same accounting-constrained financial-input edit, compare two legitimate
prediction/explanation targets: retain the observed similarity graph, or propagate
the edit through derived features, feature-derived links and affected temporal
states. Keep learned weights, fitted preprocessing and common initial states
fixed. Explicit dependency contracts and null controls make the comparison
falsifiable; invalid attempts and unsupported probes remain visible.

The contribution is the implemented audit protocol and its measured behavior in
this sparse-event banking setting. GAT plus GRU, financial graph learning,
attention plots, counterfactual explanations, graph rebuilding and the elementary
function-composition identity are not individually new contributions. A first-ever
method claim has not been established. More code and more model fits do not
increase scientific novelty by themselves.

## Questions effectively answered

| Question | Answer under the frozen study | Evidence and limits |
|---|---|---|
| RQ1 Does following financial dependencies change current-input explanation conclusions? | Sometimes. The top-ranked financial group differs in 13.49% of complete audits. The mean paired probability gap is only 0.015143 percentage points. | Seed11: 12,780 donor-matched cases, 10,995 complete seven-subset audits; not an ensemble effect or causal financial shock. Maximum gap3.951038pp. |
| RQ2 Does historical replay matter for the comparison? | One-lag historical edits also produce differences: mean gap0.006993pp and top-one disagreement13.66%. | 12,509 matched cases, 10,689 complete audits; current/lag1 only. Exact target-local replay is tested against full computation for this architecture. It does not establish behavior for arbitrary temporal GNNs. |
| RQ3 Are ranking changes operationally material? | Ranking differences are more common than alert differences. The two counterfactual audit targets disagree across the same frozen seed-specific alert threshold in0.8764% of matched current-edit cases. | This is an audit-target alert disagreement, not realized failure detection improvement, an original-prediction alarm rate or economic utility. Financial interpretation is pending. |
| RQ4 Do the graph models justify their complexity against strong baselines? | No useful warning gain is demonstrated. XGBoost and all graph variants miss all four test failing banks at their frozen development thresholds. Logistic detects one at achievedFPR2.005%. | Four test events and six development events provide weak power. AP/Brier are reported; this does not prove all graph models are ineffective. |
| RQ5 Does the explainer comparison validate failure-risk explanations? | Only partially. All edge-mask targets have predictedp1 below0.5, so the masks explain nonfailure. Signed response scores cannot be used to declare one method universally more faithful. | The observed target mismatch is a finding, not a solved new algorithm. Attention/edge-mask/random comparisons use equal two-edge budgets; financial-group units are separate. |
| RQ6 Is the evidence stable enough for broad claims? | No broad stability claim follows. Seeds, alternativegraphs, null controls and bank/time resampling are transparent, but82/500 AP draws are undefined. | AP ranges condition on418 defined draws; nominal95% coverage is unestablished. Seed dispersion is not a populationconfidence interval. |

## Research gaps addressed and gaps remaining

1. **Raw-input dependency accountability:** provides an executable financial
   dependency contract and paired conditional/pipeline response ledger. This is
   the narrowest credible candidate research contribution. Existing joint
   feature/edge attribution overlaps and must be compared directly.
2. **Temporal explanation consistency:** supplies exact affected-state replay and
   tests for this own-bank recurrent architecture. Cross-bank hidden-state
   propagation and arbitrary learned/rolling graph builders remain outside scope.
3. **Ranking versus operational response:** separately measures rank, probability
   and alert-threshold differences. Whether these differences matter economically
   remains unresolved.
4. **Sparse-event reproducibility:** supplies label-maturity gates, fixed splits,
   strong baseline controls, institution/time uncertainty diagnostics and invalid
   probe accounting. These improve evidence quality; they are not automatically
   methodological inventions.

The study does not close the gaps of causal contagion identification, systemic
risk measurement, observed bilateral exposures, verified historical data vintages,
human-ground-truth explanations or deployable bank-failure early warning.

## Closest prior work and the limits of the search

CF3 already addresses factual/counterfactual financial-risk explanation with joint
edge/feature reasoning. Its assessed version uses company knowledge graphs and
learned evidence generators; RiskTrace's candidate distinction is deterministic
raw-bank-record dependency propagation in a frozen predictor. This is a candidate
distinction, not proof of non-equivalence:
https://arxiv.org/html/2503.06441v1.

GInX-Eval explicitly addresses distributional problems in explanation evaluation
and uses fine-tuning of degraded graphs. RiskTrace's frozen-model audit asks a
different operational question; it must not claim to have invented faithful or
distribution-aware evaluation: https://arxiv.org/abs/2309.16223.

DSE, Robust Fidelity, explanation fragility/uncertainty, reconstructed-network risk
and temporal banking graph work remain close comparisons in
`docs/literature_matrix.csv`. Selected papers and implementation paths were checked;
the search was not exhaustive and close methods were not all independently
reproduced. The manuscript therefore avoids priority and general-superiority
claims. Updated verified metadata are in `paper/references.bib`.

## What would strengthen a future paper

Complete independent baseline reproduction, primary-source finance review and
close-method comparison. Develop any alert-target explainer change on development
data and label it exploratory. A new confirmatory design needs a new protocol and
credible evaluation data because this holdout is now inspected. Do not tune the
existing test, broaden outcomes or change the population solely to manufacture a
positive result. Authors must decide whether to submit a modest audit/negative
finding or pursue a separately designed stronger study.

Numerical sources: `results/final_evaluation/results.csv`,
`results/explanations/financial_summary.csv`, `edge_cases.csv.gz`,
`results/robustness/crossed_intervals.csv`, and `docs/claim_evidence_map.csv`.
