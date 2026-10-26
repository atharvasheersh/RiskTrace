# Leakage audit at the Step 8 freeze

Status: implemented/tested computational guards; historical data-vintage and
entity-review limitations remain. This is not independent source certification.

| Risk | Guard/evidence | Remaining limit |
|---|---|---|
| Future training outcomes | Both classes require availability + 12 calendar months strictly before each model origin | Historical publication of the failure itself is approximated by effective date |
| Late validation/calibration outcomes | OOF reports stop at 2020; every outcome matures before 30 May 2022 | Only six positive banks support selection |
| Test-driven tuning | Original 2022--2025 membership retained; no performance inspected; dedicated opening gate will precede evaluation | Counts/identity metadata were previously inspected for QA; holdout is not completely unseen |
| Full-panel preprocessing | Fold medians/means/scales fit only exact training keys; saved lineage and boundary tests | Revised training values could differ from actual historical vintages |
| Target/identity feature leakage | Five explicit ratio features; no failure dates, CERT, RSSD, names, ownership, labels or legacy split flags as inputs | Implementation of new model families must preserve whitelist |
| Duplicate/conflicting data | Verified source keys/counts; raw-field reconciliation rejects changed values and unexpected keys | No actual Ayush submission received; future revisions need reconciliation |
| Entity/history splicing | CERT-level nodes and outcomes, aliases flagged, state reset at gaps/RSSD changes | Three multiple-RSSD CERTs and shared RSSDs need source/finance review |
| Future graph correlations | No graph is fitted at Step 8; future implementations must use forecast-origin covariates only and frozen metrics | Step 10 temporal/index tests still required |
| Asymmetric outcome ascertainment | Training uniformly full-mature; final evaluation also requires full horizon maturity for both classes | Snapshot failure coverage may be incomplete despite conservative cutoff |
| Future history/state | 2021 covariates may warm states by availability; no 2021 training labels used at first test fit | Model-specific replay/reset tests still required |
| Financial scope/units | EQTOT identity, raw-to-ratio checks; uninsured domestic ratio excluded | Duration/concentration unavailable; no causal financial-shock interpretation |

The previous `label_panel` columns described coarse split membership and purging;
they did not by themselves enforce every fitted model's label-knowledge cutoff.
They remain explicitly named legacy_split/legacy_purged in the new canonical data.
Use the frozen role keys and protocol.training_mask, not those legacy columns.

Current tests cover class-independent maturity including same-day exclusion,
held-out extremes leaving preprocessing unchanged, immutable snapshots, changed
values despite matching keys, and development-only protocol counting. Existing
tests also cover duplicate keys, date/unit/label semantics, tampered caches,
financial interventions and temporal replay. New model-specific boundaries will
be audited before interpreting their results.
