# RiskTrace research progress and revised work allocation

For Ayush Sinha and Atharva Sheersh Pandey | 27 October 2026

Ayush will now own finance verification and a defined ML workstream. Atharva will retain the primary pipeline and research integration. This replaces the earlier allocation that assigned no ML work to Ayush. The immediate goal is to verify and strengthen an exploratory research study before deciding its publication direction.

## Work completed on Atharva side

The repository contains the official-source collection, allocation of 807 banks to each person, validated canonical panel, chronological splits, training-only preprocessing, logistic regression, XGBoost, GRU, static GAT, temporal GAT plus GRU, graph controls, explanation audits and robustness analysis. There are 297 development fits and 23 final fits. These are repository artifacts produced with AI assistance; they do not establish unrecorded human review or authorship contributions.

The dataset has 51,339 eligible bank-quarter reports from 1,614 banks during 2010Q1 to 2025Q4. Annual rolling validation uses 2012 to 2020 and only six distinct failed banks. The observable test contains 12,783 reports and four distinct failed banks. The source is a centrally assembled official panel; Ayush's separate submission has not been received or verified.

## What the actual results mean

At the unchanged validation-derived thresholds, XGBoost and every graph variant detect zero of four failed test banks. Logistic regression detects one, with achieved test false-alarm rate 2.005%. The graph models have not shown useful warning superiority.

Current financial-input edits change the top-ranked group in 13.49% of complete audits, but the mean probability gap is only 0.015143 percentage points. All edge masks explain nonfailure at the 0.5 class boundary. In 82 of 500 bootstrap draws AP is undefined. Financial usefulness, high novelty and Q1 readiness are unestablished.

The manuscript, claim map, saved checkpoints, case packets and reproduction tools are assembled. Fresh-environment inference has been exercised; the final verification report accompanies the handoff. Author review, finance validation, the final venue and submission approval are pending.

# Supported novelty and research questions

The defensible contribution is a dependency-aware empirical audit of bank-forecast explanations. It compares the same financial edit with the original graph retained and with feature-derived links and affected temporal states recomputed, while keeping fitted weights and preprocessing unchanged. These answer two legitimate explanation questions. A difference does not prove that either explanation is wrong or causal.

| Research question | What this study answers | Gap addressed and limit |
| --- | --- | --- |
| Do financial dependencies change explanation conclusions? | Yes for some ranking conclusions: current top-one disagreement is 13.49% among complete audits; the mean probability gap is small. | Makes raw inputs, derived ratios, graph links and temporal replay explicit. Does not establish a first-ever method. |
| Do similarity graphs improve failure warnings? | No useful gain is demonstrated under this bounded protocol; all graph variants miss the four test failures at fixed thresholds. | Adds transparent tabular, no-graph and graph controls. Four events cannot settle graph usefulness generally. |
| Do rankings imply materially different alerts? | The two audit targets cross the same alert threshold differently in about 0.88% of donor-matched current-edit cases. | Separates ranking changes from probability and alert changes. Economic materiality and causal validity remain unproved. |
| How reliable is sparse-event evidence? | Six development and four test failures limit selection and uncertainty; 82 AP resamples are undefined. | Records label maturity, event counts, invalid probes and dependence-aware sensitivity. This is methodological discipline, not inherently novel. |

An additional finding is a target mismatch: a model can generate low-probability operational alerts while a binary-class explainer still explains nonfailure. This was observed here; a general solution has not been developed or validated.

The study does not fill the gaps of causal contagion identification, measured interbank exposure reconstruction, strict historical-vintage backtesting or a deployable early-warning system. It also does not establish that GAT plus GRU, attention plots or graph rebuilding are new.

Closest overlaps to check: CF3 financial factual/counterfactual explanation; GInX-Eval, DSE and Robust Fidelity evaluation; temporal bank graph forecasting. The comparison matrix exists, but close-method reproduction and proof of a distinct methodological advance remain pending. Sources: docs/literature_matrix.csv, docs/final_novelty_and_research_questions.md and paper/references.bib.

# Ayush tasks for finance and baseline modeling

## 1 Verify the allocated banks and financial definitions

Use data/bank_allocation.csv to reconcile your 807 banks with source IDs and report keys. If you have a separate collection, provide its raw files, source URLs, retrieval dates, units and missing-value flags. Review EQTOT versus EQ, deposits scope, failure versus assistance transactions, mergers and renamed entities. Record disagreements without editing the frozen panel.

Deliverable: A source and entity discrepancy ledger, plus your actual collection manifest or an explicit statement that no separate collection is supplied.

Complete when: Each issue cites a CERT, report date, source and proposed resolution; Atharva can reproduce it.

## 2 Reproduce logistic regression and XGBoost independently

Own the ML implementation of a separate baseline replication runner. Use the approved annual 2012 to 2020 folds, original training keys and supplied training-fitted preprocessing. Take the already selected hyperparameters from selected_models.json. Start with the 2012 fold and one seed, then run all nine folds. Use seed11 for logistic and seeds11,29,47 for XGBoost. Do not select parameters from the final test or overwrite primary results.

Deliverable: Your runner, environment details, fold predictions and a comparison report under results/ayush_replication/. Include AP, Brier, validation-selected thresholds, per-quarter recall and distinct-event warnings.

Complete when: Differences from saved development predictions/metrics are reconciled within a stated numerical tolerance, with a reason for every sample or implementation difference.

Study src/risktrace/predictive.py, analysis.py and metrics.py before implementing. Preserve horizon maturity at each forecast origin. Positive quarters are repeated windows, not additional independent failures. Atharva reviews the runner before the full replication. This is new assigned work; no Ayush implementation or completion is currently claimed.

Working estimate: source review and a one-fold ML smoke run in the first three working days; full fixed-setting replication by the end of the first working week, subject to setup and discrepancies. These are planning targets, not recorded commitments.

# Ayush tasks for explanation analysis and interpretation

## 3 Own development calibration and explanation diagnostics

Using your independent out-of-fold predictions, implement reliability tables, Brier calculation, false-alarm accounting and event-level warning reconstruction. Add an exploratory tabular explanation comparison: logistic coefficient contributions and XGBoost TreeSHAP on the same development records. Confirm the additive prediction scale, transformed-input units and comparable record selection. Explain what each method represents and avoid treating attribution as a causal effect.

Deliverable: A notebook or script, development-only diagnostic tables and five to ten correctly sourced example-bank explanations. Use an outcome-independent sample for aggregate summaries.

Complete when: Predictions and contribution totals reconcile to each model on the documented scale; metrics match the independent evaluation; no claims are selected from attractive examples.

## 4 Design a development experiment for explaining alerts

Study why the original binary-class masks explain nonfailure while operational alert thresholds are much lower. With Atharva, specify whether the new target is failure probability or distance above the frozen alert threshold. Prototype the comparison only on development data, retaining equal explanation budgets, random controls and valid financial probes. Label it exploratory and keep its outputs separate. Do not claim this solves the mismatch until tested.

Deliverable: A short ML experiment specification and a development prototype with unit checks, response curves, random controls and failure cases.

Complete when: The target, output scale, thresholds, sampling, budgets and temporal replay are explicit. Any new confirmatory claim requires a newly agreed evaluation protocol; the inspected test cannot become a fresh holdout.

## 5 Review cases and sharpen the literature comparison

Review the four proposed failure/control packets, distinguish Republic Bank from First Republic Bank, and check control comparability. Cite primary FDIC filings/releases for financial interpretation. Compare the exact research question with CF3, GInX-Eval, DSE and Robust Fidelity; record what each actually evaluates.

Deliverable: A sourced case commentary and close-paper comparison with overlap, differences and unresolved questions.

Complete when: Retrospective narrative is separate from prediction evidence; unsupported claims are removed. Approval or submission is not inferred from completion of a task.

# Atharva tasks and chronological handoff

Atharva retains primary data integration, frozen models, graph and temporal code, dependency replay, reproducibility tooling and the manuscript. Ayush now shares ML implementation through the separate workstream above; this is not a transfer of the original primary-result provenance.

| Order | Owner | Next action and required output |
| --- | --- | --- |
| 1 | Atharva | Hand over the fixed dataset manifest, split keys, selected settings, primary results and case packets. Preserve the original version. |
| 2 | Ayush | Reconcile allocated data and source/entity definitions; build one-fold independent baseline replication. |
| 3 | Atharva | Review the smoke run, resolve implementation discrepancies and document any proposed data correction as a new version. |
| 4 | Ayush | Complete fixed-setting baseline reproduction and development calibration/attribution diagnostics. |
| 5 | Both | Specify the alert-explanation development experiment; Ayush prototypes it and Atharva verifies temporal/dependency handling. |
| 6 | Ayush | Provide primary-source case interpretation and close-method overlap review. |
| 7 | Atharva | Integrate justified findings, rerun affected checks and update the manuscript with exact result provenance. Preserve all negative results. |
| 8 | Both | Decide whether the evidence supports a scoped audit/negative-result paper or requires a redesigned study with new evaluation data. |
| 9 | Both | Verify current venue requirements and ranking evidence, agree authorship and disclosures, review the exact version and approve before any submission. |

## Repository and review rules

Keep Ayush replication and exploratory outputs in clearly separate folders. Use detailed commits with purpose, changes, validation and limitations; review before merging. Never replace frozen predictions, thresholds or the analysis plan to improve a test result. A genuine correction needs a logged reason, version and downstream rerun.

For every handoff provide the commit SHA, commands, environment, dataset hash, output paths, checks passed and unresolved issues. No author order, affiliation, finance approval, Q1 status, submission or acceptance is assumed. The approximate 16-week target must be revised around the current evidence; publication timing is controlled by the venue.

Repository: https://github.com/atharvasheersh/RiskTrace | Primary evidence: results/final_evaluation/, results/explanations/, results/robustness/, results/case_studies/ and docs/claim_evidence_map.csv.
