# Step 11: frozen explanation audit results

Primary seed 11 attempts the entire 12,783-row observable test population. All
12,783 targets have two-edge attention, adapted GNNExplainer-style and random
explanations (38,349 rows). Financial current edits have 12,780 donor-matched cases
and three no-donor exclusions. Historical one-quarter edits have 12,509 cases and
274 unavailable-history/no-donor exclusions. Do not describe the latter as 12,783
successfully audited histories.

| Primary audit | Current report edit | Previous-quarter edit, replayed |
|---|---:|---:|
| Donor-matched cases | 12,780 | 12,509 |
| Seven-subset complete cases | 10,995 | 10,689 |
| Mean paired probability gap (percentage points) | 0.015143 | 0.006993 |
| Largest paired gap (percentage points) | 3.951038 | 1.477935 |
| Top-one disagreement, complete cases | 13.4879% | 13.6589% |
| Any paired threshold disagreement, matched cases | 0.8764% | 0.1119% |

The mean current gap is 0.000151 probability, **0.0151 percentage points**, not
1.51 pp. Largest cases must not replace that small average. Ranking disagreement
can occur despite small responses. Alert disagreement means at least one of up to
seven valid counterfactual subsets puts the two target probabilities on different
sides of the frozen seed-specific validation threshold. It is not an observed
bank failure, a causal decision effect or the headline ensemble's event recall.

Across the primary current/historical probes, 177,023 subset interventions were
attempted; 14,420 fail financial constraints (8.15%), leaving 162,603 valid subset
responses. Full ranking statistics use only 21,684 complete cases. Partial cases
retain their valid response subsets with explicit counts. Invalid attempts and
277 unattempted candidate cases remain in the ledger, without donor resampling.
Marginal training-range violations are rare; this does not prove joint or economic
support. Nearest-training distances are also retained.

Additional seeds audit the prespecified lowest-hash 32 rows per quarter (416
current/412 historical cases each), not the whole population. Random/exogenous
graph samples have exactly zero paired gaps as expected. The other k is a separate
fixed sensitivity, not a post-test model replacement. Parameters remain unchanged
in all audits; original fingerprints and runtime are logged.

## Edge interpretation is limited

**All 12,783 original edge targets have failure probability below 0.5** (maximum
approximately 0.04499). The prescribed class-conditional optimized masks therefore
explain nonfailure throughout, even though warning thresholds are much lower.
Saved necessity/sufficiency use signed changes in failure probability p1. A negative
necessity can mean deleting nonfailure-supporting edges raises risk. Do not rank
explainers by signed mean or call attention superior merely because its sign is
positive. The current-edge objective, fixed earlier state and rare-event operating
point do not establish high-quality explanations of actual risk alerts. A different
target would need a new development protocol, not silent post-test substitution.

The established explainer is an explicit edge-only GNNExplainer-style adaptation,
not a full reproduction of every original feature/temporal setting. Standard
conditional fidelity is an existing method; close-evaluator reproductions remain
outstanding. No ground-truth economic explanation, causal shock or first-method
novelty is established.

## Independent reporting correction

The independent reviewer identified that detailed control-invalid records were
not exported by the frozen runner, although counts were saved. The supplementary
script reconstructs them with the same frozen models/settings/code and checks
every retained case value/count and parameter hash. It exports 508 records per
control/sensitivity family. reporting_corrections.json documents this nonnumeric
provenance repair; no model, target or primary result changed.

Artifacts are under results/explanations. The immutable experiment code/plan remain
unchanged; scripts/supplement_control_ledgers.py adds reporting detail only.
