# Minimal paired audit: implementation and interpretation

The pilot is a graph-augmented logistic predictor with exponentially decayed
representations, **not GAT/GRU or a full temporal GNN**. Its purpose is to check an
evaluation mechanism before paying for a large model. It makes no SOTA claim.

Five accounting ratios are standardized using periods 0--3 only. The representation
concatenates own ratios and the mean of directed k-nearest neighbors. Recurrent
state is h[t] = 0.5 h[t-1] + 0.5 representation[t]; an unavailable report resets that
bank's state. A balanced logistic readout fits periods 0--3. Periods 4--7 are an
outcome-window embargo; labels from those periods are not fitted. Periods 8--11
are held out for the development performance description. For bank data this is
2010 fit / 2011 embargo / 2012 evaluation, with no use of final 2022--2025 data.

The bank subset includes every positive CERT in the development panel plus 96
hash-selected other CERTs. It is intentionally **case enriched**. This selection
uses development outcomes and prevents population performance interpretation.
Do not present these AUROC/AP values as a representative bank-distress benchmark.
Metadata (state and charter class) is taken from each report date, not a future
record. Banks can enter/exit; absent statements are not fabricated or forward filled.

Synthetic data have 64 artificial banks and 12 periods. The known generator uses
feature-derived k=3 neighbors, the same memory equation, specified logit coefficients
and Bernoulli outcomes. This deliberately contains the dependency being tested.
It verifies recovery of a mechanism, not its prevalence in finance or novelty.

## Conditions and interventions

Three seeds (11, 29, 47) vary bank bootstrap fitting and donor choice. They do not
separately identify training, data and perturbation uncertainty. Conditions are:
feature-derived kNN k=3/7; no graph; random graph; and state-first exogenous graph.
The latter prefers same-state neighbors with deterministic ties, then other states
if needed, bounded by k=3. Random/exogenous adjacency is fixed within each pair.
None is claimed to reconstruct actual interbank exposures.

For up to 32 banks observed in all four evaluation quarters, edit period 8 or 11
and predict period 11. Donors are observed in the same quarter, same charter class,
and within a factor of two in assets; sample from the eight nearest by log assets.
Three groups: capital; cash/loan/securities asset mix; noncurrent-loan quality.
Scale donor amounts to target assets; capital adjusts liabilities; loan changes
preserve credit-quality share unless that group is also replaced. Deposits remain
fixed. Never resample an invalid donor to hide exclusions. Equal explanation size
means **one prespecified group**, not equal numbers of underlying raw fields.

Enumerate all seven nonempty group subsets. Conditional audit retains original
adjacency; pipeline audit rebuilds only the edited quarter's feature-derived graph.
Both recompute financial ratios and replay the complete history from a shared zero
initial state. Later-quarter adjacency is unaffected because only one historical
raw report changed. Fitted scaler/readout fingerprints must remain identical.
No retraining occurs within an audit; fitting each condition/seed is separate.

Reject violations of accounting, nonnegativity, loan-share and asset-composition
constraints. A complete case requires all seven interventions valid; invalid rows
and denominators remain in the logs. Algebraic validity is weaker than economic
plausibility. Record feature-range exceedances and nearest standardized training-
record distance. Neither absence of a range violation nor graph rebuilding proves
in-distribution inputs. Perturbations are model probes, not estimated causal shocks.

## Metrics

Original probability p; response to group replacements p(S). Explain each target
by descending absolute |p - p({group})|, with one-group top-1 budget and deterministic
ties. Save every subset probability, all group scores and selected group.

* Response gap: |p_conditional(S) - p_pipeline(S)|; case mean over seven subsets.
* Necessity: signed p - p(replace selected group).
* Sufficiency gap: signed p - p(keep selected group, replace other groups).
* Sufficiency gain: p(keep selected group) - p(replace all groups).
* Ranking: Spearman over three absolute scores and top-1 disagreement.
* Random explanation: the same random one-group choice for both paired targets.
* Diagnostics: changed directed edges, invalid subsets, range violations, nearest
  training distance, parameter invariance and wall-clock runtime.

Signed metrics can be negative. A larger response alone does not establish a better
explanation; the two audits define different targets. Controls' zero paired gaps
are expected by construction, and checked as software invariants.

Run `uv run --locked risktrace audit` after `pilot-data`. Output: audit_runs.csv,
audit_cases.csv, audit_summary.csv, invalid_perturbations.csv, audit_parameters.json
and audit_protocol.json under results. Seeds are sensitivity replicates, **not
independent banks**; pooled case counts are not effective sample sizes or CIs.
