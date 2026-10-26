# Step 6 decision: continue narrowly; publication novelty remains unproved

Executed 27 October 2026. The computational distinction is observable in the small
pilot. **A discrepancy is expected from the pipeline definition; demonstrating one
does not by itself constitute a strong research contribution.** No material change
of financial task is proposed. Continue the original bank-distress audit scope,
conditional on stronger baseline, uncertainty and financial-plausibility evidence.
Complete the authorized data collection before any full-scale model development.

## What actually ran

Thirty conditions: two datasets x five graph definitions x three seeds. Each uses
a freshly fitted small graph-aggregation/memory/logistic predictor; scaler and
readout are then frozen within paired interventions. Synthetic data deliberately
contain a known feature/graph/state dependency. The real-bank mechanism check uses
a case-enriched 2010--2012 development subset, not the full intended TGNN.

All 30 parameter fingerprints stayed unchanged during paired evaluation. Directed
feature kNN graphs rebuild only where inputs changed; exogenous/random graphs stay
fixed. Historical edits replay states from the same initial history. All seven
nonempty subsets of three coherent financial groups are evaluated. Explanation
budget is top one group in both targets; signed necessity/sufficiency and a common
random-group baseline are saved. Methods and exact definitions: audit_methods.md.

## Observed effects

The following pool three sensitivity seeds; rows are **not independent replicates**.
Mean gap averages all seven subset probability differences per accepted case.
Values in the two gap columns are **probability percentage points**.

| Data / graph | Edit | Accepted cases | Mean gap (pp) | Largest gap (pp) | Top-1 disagreement |
|---|---|---:|---:|---:|---:|
| Synthetic feature k=3 | Current period | 96 | 5.438 | 35.258 | 11.46% |
| Synthetic feature k=7 | Current period | 96 | 3.525 | 17.244 | 8.33% |
| Bank feature k=3 | Current 2012Q4 | 72 | 1.338 | 36.314 | 9.72% |
| Bank feature k=7 | Current 2012Q4 | 72 | 0.622 | 17.816 | 6.94% |
| Bank feature k=3 | Historical 2012Q1, replay to Q4 | 68 | 0.079 | 1.736 | 16.18% |
| Bank feature k=7 | Historical 2012Q1, replay to Q4 | 68 | 0.049 | 1.312 | 5.88% |

No-graph, exogenous and random-graph paired gaps are exactly zero in both datasets,
as required by their definitions. This checks implementation, not a victory over
those models. Feature-graph responses and ranking shifts depend on k and seed.
See audit_summary.csv for all cells, audit_runs.csv for seed-specific effects and
runtime, and audit_cases.csv for every subset response, scores and chosen groups.

## Limits that prevent a strong novelty/finance claim

* Real-bank evaluation has **329 rows, only three positive quarters from two banks**
  per fitted model. Case enrichment, persistent-report audit targets and outcome
  rarity invalidate population performance claims. AUROC around 0.98--0.99 is
  misleading without these facts; it is not evidence of a publishable predictor.
  There is no consistent predictive advantage over the no-graph pilot.
* At each graph definition, 160 of 1,260 attempted bank perturbations across seeds
  fail algebraic/range constraints (12.70%). Twelve additional target/seed/edit
  cases have no matched donor. No retries hide them. Complete-case filtering may
  select easier banks. Only 27 distinct bank targets survive at least one paired
  audit; pooled case counts substantially overstate independent evidence.
* Some synthetic probes exceed training feature ranges. Bank probes do not exceed
  this simple range diagnostic, but that does not demonstrate joint support or
  plausible economic interventions. Nearest-record distances are retained.
* The largest bank discrepancy is an extreme example, not the average impact.
  Historical ranking flips can occur despite tiny absolute response gaps.
* Preprocessing, availability assumptions, data revisions, graph definitions and
  donor selection still need independent stress tests. There are no bank-clustered
  confidence intervals, preregistered financial materiality thresholds, expert
  explanation judgments, actual exposure-network validation or supervisory benefit.
* Runtime is for this small CPU pilot only; it says nothing about full TGNN scale.

## Relation to existing work and decision gates

[CF3](https://arxiv.org/html/2503.06441v1) already studies financial graph
explanations with feature/edge counterfactuals. [GInX-Eval](https://arxiv.org/abs/2309.16223)
addresses distribution-aware explanation evaluation through a different retraining
target. [Robust Fidelity](https://arxiv.org/html/2310.01820v2), DSE and fragility/
uncertainty work already address substantial parts of the evaluation problem.
The literature matrix and selected implementation inspections found no verified
equivalent end-to-end bank dependency audit, but the search is not exhaustive.

The remaining candidate is an **explicit, falsifiable comparison of conditional
network explanations and frozen-predictor pipeline explanations under audited
bank-feature dependencies**, with temporal replay and valid-intervention accounting.
Existing concepts and the elementary pipeline identity are not new. A reusable
benchmark plus convincing financial evidence could be a contribution; a graph
rebuild toggle plus a positive discrepancy is weak on its own.

Before a Q1-level claim, require: direct close-baseline implementations; stable
effects across defensible graph builders and perturbation schemes; sufficient
independent failures and bank-clustered uncertainty; point-in-time or explicitly
revision-aware evaluation; and a finance-motivated materiality criterion. If graph
information adds no predictive value, effects disappear with plausible probes, or
equivalent prior work is confirmed, narrow/reconsider the contribution before
investing in a full architecture. No acceptance or novelty strength is guaranteed.
