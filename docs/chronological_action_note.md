# RiskTrace: reviewed status and chronological work note

Reviewed 27 October 2026. This is the execution order, not a claim that future work
has been done. The latest pasted request authorizes Steps 8--14 subject to its
scientific and submission gates. Existing Step 7 code is at 1e502e3; verified
against GitHub before this continuation. Raw snapshots and prior results survive.

## What the review established

The source collection and minimal paired audit are real, reproducible artifacts.
The existing 13 tests and 85-source snapshot verification passed again. The
implementation is a small graph-aggregation/memory/logistic pilot, not GAT+GRU.
Its bank sample is case-enriched and has only two positive evaluation banks;
high AUROC is not a publishable predictive result. Novelty remains provisional.
Ayush's raw-schema submission has not been located among the supplied workspace
artifacts. The centrally downloaded official panel must not be attributed to him.

Two issues take priority over adding models: the validation block has zero events,
and selecting/calibrating a 2022 model on all 2021 outcomes would use labels that
were not yet known. Existing label/split flags do not themselves enforce every
model's historical label-maturity cutoff. Add explicit forecast-origin contracts.

## Work in dependency order

| Order | Action and owner | Exit evidence | Current status |
|---:|---|---|---|
| 1 | Atharva: verify checkout, source hashes, counts, existing tests, attribution and remote | Existing source snapshot reproduced; no unrelated work altered | Verified |
| 2 | Atharva: quantify development-only protocol alternatives; authors choose | docs/evaluation_protocol_revision.md plus recorded decision | User approved annual 2012--2020 rolling validation |
| 3 | Atharva: rebuild canonical data directly from official snapshots; reconcile any collaborator file field by field | Source lineage, conflict/exclusion logs, identifier/missingness/unit checks | In progress; Ayush submission absent |
| 4 | Atharva: implement the approved maturity-aware chronological folds and training-only preprocessing; Ayush: finance/source review | Versioned analysis dataset, fixed split keys, leakage audit, decision/config hashes | Dependent on order 2; do not mark frozen yet |
| 5 | Atharva: train prevalence reference, logistic regression, XGBoost, then GRU | Development baseline table, calibration/Brier/AP, false-alarm thresholds and event warnings | Not started |
| 6 | Atharva: bounded static GAT and temporal GAT+GRU; matched no-graph/shuffled/exogenous controls | Trained checkpoints and development evidence of graph value or its absence | Not started |
| 7 | Atharva and authors: lock models, thresholds, explanation settings, robustness analyses and primary claims | Signed/recorded analysis plan; immutable version/run identifiers | Not started; precedes any test-performance inspection |
| 8 | Atharva: run the fixed final predictive evaluation and attention/established-explainer/random comparisons | Final predictions and equal-budget explanation outputs | Not started |
| 9 | Atharva: paired conditional/pipeline audit, valid financial edits, dependency recomputation, temporal replay and support diagnostics | Per-case tables, uncertainty, invalid attempts and failure cases | Full evaluation not started; exploratory pilot exists |
| 10 | Atharva: prespecified robustness and bank/time uncertainty; Ayush: finance cases and plausible matched controls | Robustness tables, figures, explicit finance-review status | Not started |
| 11 | Atharva: assemble manuscript and reproducible package; independent reviewer checks claims/leakage/methods | Clean-environment table reproduction, claim-to-evidence map and resolved findings | Not started; existing bibliography is minimal metadata |
| 12 | Authors: choose/recheck venue; Atharva: prepare exact package | Current scope/ranking/category/year/fees/guide checks and exact manuscript version | Historical shortlist only |
| 13 | Both authors approve; user authorizes external submission and any charges | Recorded approvals, then actual confirmation if submitted | Not approved; no submission performed |
| 14 | Authors: respond to actual reviews, rerun justified revisions and reapprove | Evidence-linked response and revised package; acceptance/publication only if received | Conditional future work |

All programming/ML and technical evaluation stay with Atharva. Ayush owns his
allocated data/source verification, finance literature, plausibility and case
interpretation; no implementation/training/tuning tasks are assigned to him.
No collaborator/editor/reviewer contact is automatic.

## Practical priorities

Do not repeat the first-week foundations; they exist. Use a revisable approximate
16-week submission-readiness plan only after the event-protocol decision. A
12-logical-processor, approximately 16.8-GB RAM machine is available; no NVIDIA
runtime was found in PATH. Start with CPU smoke tests and set a bounded training
budget before neural runs. No paid compute has been authorized.

Continue brief progress reports and detailed reviewable commits with Purpose,
Changes, Validation and Limitations, followed by verified ordinary pushes. Preserve
raw/processed local artifacts and commit their lineage/manifests rather than large
datasets. Negative graph/novelty results remain valid findings, not reasons to tune
on the test set or invent a different outcome.
