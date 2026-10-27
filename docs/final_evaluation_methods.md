# Prespecified final evaluation and explanation methods

This protocol is committed before test performance is opened. Code, selected
models, data, split keys, environment lock and numeric settings are hash-checked by
the frozen analysis plan. The initial opening gets a timestamp and plan hash.
Do not refreeze after test inspection or choose settings from final results.

Train the selected static final models as of 30 May 2022 on the 31,319 mature
training examples. Keep thresholds selected on 2012--2020 OOF predictions. Evaluate
all 12,783 eligible, fully observable original test bank-quarters, preserving all
model inputs/selection rules. Seed means are the primary stochastic-model forecasts;
individual seed outputs are sensitivity, not independent data replicates. The other
predeclared GAT+GRU neighbor count is a sensitivity model with the original family's
operating threshold, never a replacement chosen from its test score.

## Two separate explanation units

Edge explanations compare attention rankings, random rankings, and a clearly
identified **GNNExplainer-style edge-only mask optimization adaptation**, all at a
two-nonself-edge budget on the selected GAT+GRU seed 11. It uses 30 Adam steps and
the original predicted binary class, with fixed size/entropy penalties. True failure
labels never optimize masks. Self edges are always retained; continuous masks
multiply attention weights and renormalize. This adapts the original mask objective
to this specified GAT/GRU interface; it is not a full reproduction of the original
paper or a claim to explain the entire historical sequence. Earlier states stay
fixed for this current-edge question. Majority-class explanation degeneracy is a
known limitation, not proof of useful risk reasoning.

For each method save selected neighbor CERTs, signed deletion necessity and keep-
only sufficiency gap. The original model probability is seed-specific, not the
headline ensemble. Compare explanation budgets within this edge unit only.

The financial-input audit separately compares the two legitimate input-edit
targets. It does not cross-rank edge and raw-group explanations as if their budgets
were equivalent. Prespecified raw groups are capital, asset mix and credit quality;
all seven nonempty subsets are probed, and the ranking budget is one group in both
targets. Donors are same-quarter/same-charter, within factor-two assets, sampled by
a stable row hash among the nearest eight log-asset matches. Never use outcomes to
select donors or resample an invalid edit away.

Both targets recompute the actual raw-to-ratio descendants, attention weights and
recurrent states; only feature-derived adjacency differs. Rebuild changed target
neighbors for the pipeline target and retain original neighbors for the conditional
target. Current and one-quarter-historical edits are tested. The model passes
contemporaneous projected ratios, not other banks' hidden states. Consequently
target-local graph rebuilding and own-bank replay are exact for its prediction;
unit tests compare the shortcut with a complete edited snapshot and full historical
forward pass. Changed connections outside this target's dependency path are not
interpreted as measured systemic spillovers. Query precision matches float32
model/graph inputs to avoid an inconsistent precision-only neighbor change.

Primary seed 11 is audited across all eligible test quarters, with explicit missing
historical report/no-donor exclusions. Seeds 29/47, null graph controls and the
other feature-graph k receive the lowest-hash 32 target rows per quarter, independent
of outcomes. This sensitivity sample is not described as the full population.
Model parameters and fitted preprocessing stay fixed; fingerprints are checked.

Report all attempted subsets, partial/complete case counts, signed and absolute
response gaps, top-one changes, ranking correlations, and seed-specific validation-
threshold crossings. Only complete seven-subset cases get full group rankings;
partially valid cases still contribute clearly labeled available-subset responses.
Per-feature training-range violations and nearest standardized training-record
distance diagnose support but do not establish joint-distribution or economic
validity. Historical balance-sheet coherence is not a causal intervention claim.

Standard conditional necessity/sufficiency is the existing fidelity comparison.
CF3, GInX-Eval, DSE and Robust Fidelity remain close conceptual/evaluator overlap;
we do not claim to reproduce or outperform all their implementations. GInX retraining
and DSE surrogate generation have different targets from this frozen audit.
Independent close-baseline reproductions remain a limitation for a strong novelty
claim, which cannot be replaced by this custom model comparison.

## Robustness, inference and cases

Keep selected models fixed. Report individual seed ranges, static/temporal/no-graph
and random/exogenous components, both neighbor counts, and calendar-year strata.
Undefined discrimination in zero-event strata is unavailable, not zero performance.

For uncertainty, separately resample connected CERT/RSSD institution clusters and
calendar-year blocks, multiply row counts and use the same 500 draws for paired
model comparisons. This pigeonhole-style diagnostic addresses crossed institution/
time dependence, but only four positive test banks and four year blocks (one partial)
make nominal interval coverage unverified. Record every zero-positive/undefined AP
draw; percentile ranges condition on defined draws and are explicitly exploratory.
Do not interpret seed spread as a bank-population CI or the AP bootstrap as a
certified significance test. Apply analogous clustered diagnostics to financial
response gaps with explicit denominators.

Prepare proposed technical packets for the eligible failed banks and pre-event
matched nonfailure-horizon controls. Matching uses the same report/charter, factor-
two assets, nearest log assets and excludes linked identity components. Outcomes
define retrospective case/control membership; these cases are distinct from the
primary all-population test. Only valid held-out forecast origins appear in plots;
do not fabricate 2021 forecasts with a model fitted in 2022. Ayush's case selection,
financial interpretation and approval remain pending; no contact is automatic.

References: GNNExplainer (Ying et al., 2019), https://arxiv.org/abs/1903.03894;
Owen's crossed bootstrap (2007), https://arxiv.org/abs/0712.1111. These citations
explain the adaptations' origins, not an equivalence or coverage guarantee.
