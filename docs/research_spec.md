# RiskTrace research specification

Version 0.1, 27 October 2026. Step 1 is a proposed protocol, not an empirical result.

Implementation amendments are recorded in population_and_labels.md (v1.1): use
EQTOT for total-equity accounting/ratios, and conservatively bound outcome censoring
by the failure-source index date. Those checked source definitions supersede the
initial financial-field proposals below.

## Problem and intended use

Study the reliability of explanations of bank-level distress forecasts when a
temporal predictor uses a network constructed from the same financial information
that its explanations perturb. The intended use is model audit and research;
outputs are not operational supervisory recommendations or investment advice.

Primary question: **How much do financial explanation conclusions depend on
holding a feature-derived bank network fixed rather than propagating a financial
input change through its actual computational dependencies?**

Secondary questions concern whether discrepancies are attributable to graph
construction, perturbation validity, model training randomness, or temporal state,
and whether network information adds predictive value to bank fundamentals.

## Evaluation targets

Let B denote raw bank records, T the fitted financial-feature transformation,
g the graph builder, and f the frozen predictor. The implemented pipeline is
F(B) = f(T(B), g(T(B))). For a documented input replacement P:

* Conditional graph response: f(T(P(B)), g(T(B))).
* Pipeline response: f(T(P(B)), g(T(P(B)))).

The first is a legitimate conditional question. Their disagreement alone does not
prove a faulty explanation. RiskTrace must identify which question an explanation
answers and test whether the difference changes a meaningful model-audit conclusion.
Only actual descendants of edited inputs are recomputed. Exogenous graph components
remain unchanged. Fitted transformations and predictor parameters stay fixed in a
paired audit. Historical edits require replay from a common pre-edit recurrent state.

## Candidate contribution and competing explanations

Proposed contribution: an explicit dependency contract and paired evaluation for
feature-derived financial graphs, with coherent raw-input perturbations and
empirical comparison of necessity, sufficiency, rankings, and computational cost.
This is not yet established as a new method or a Q1-level contribution.

Competing explanations include out-of-distribution perturbations, arbitrary graph
density, correlated substitute features, random initialization, threshold effects,
and weak predictive models. Controls must distinguish these from deterministic
input-to-feature-to-edge dependency effects. Compare to established faithfulness,
deconfounded, robust, and uncertain graph-explanation methods after literature review.

## Initial population proposal

* Unit: an FDIC-insured individual bank, keyed by FDIC certificate number and report
  date. RSSD identifiers are retained if obtainable. Certificate lifecycle and merger
  changes must be audited; names alone are not identifiers.
* Operational asset band: USD 1 billion inclusive to USD 250 billion exclusive at
  each quarter. This is a research inclusion rule, not a regulatory definition of
  a regional bank. The lower bound is proposed for financial-field availability;
  Step 5 must verify coverage. Do not force a target number of institutions.
* Quarterly reports: 2010 Q1 through 2025 Q4. These are 64 scheduled reporting dates;
  the actual bank-quarter count remains unmeasured at Step 1.
* Include historically eligible failed and exited banks; do not choose the cohort
  from banks surviving today. Eligibility is evaluated without future failure status.
* Do not combine holding-company FR Y-9C records with bank-level labels. Any later
  holding-company study requires an explicit entity mapping and separate protocol.

This differs from the original blueprint's bank-holding-company framing. Bank-level
units make the proposed public financial sources and FDIC receivership dates align
more directly. The final coverage and sample-size consequences require a data audit.

## Outcome, timing, and splits

Primary outcome proposal: FDIC-recorded failure/receivership in the next four
calendar quarters after information availability. One-quarter horizon is secondary.
This measures failure, not all possible distress; assistance, poor profitability,
and voluntary mergers are not automatically positive labels.

Preserve report_date, available_date, availability_basis, source retrieval date,
failure_date, and outcome observation cutoff. If historical publication dates are
unavailable, initially use a conservative, explicitly assumed 60-calendar-day lag
and test sensitivity later. Revised data are not automatically point-in-time data.
Do not turn censored horizons into negatives.

Proposed report-date development partition: 2010–2018 training, 2019–2021 validation,
2022–2025 final test. Training examples must also have matured outcome windows before
the next partition's forecast cutoff. Fit preprocessing only on training records.
Step 5 pilots use training dates; final test outcomes must not guide feature or model
selection. A limited bank pilot is not a final predictive benchmark.

## Features and network assumptions to audit

Candidate raw quantities: assets, liabilities, equity, deposits, uninsured deposits,
cash, loans, noncurrent loans, AFS/HTM securities, and income where definitions allow.
Define formulas, units, schedules, and coverage before use. Do not invent depositor
concentration or duration-gap measures from unrelated fields. Such features may be
unavailable in public aggregate records and must remain excluded unless justified.

Primary graph proposal: lagged financial-composition similarity with k-nearest
neighbors. Graph density and normalization are recorded configurations. Geographic
links serve as an exogenous comparison when location is available. Market-return
graphs are optional, with listed-only coverage reported separately rather than
silently excluding unlisted banks.

Raw changes must preserve stated accounting constraints and recompute dependent
ratios. For example, replacing uninsured with insured deposits at unchanged total
deposits does not justify editing total assets. Rebuilding edges does not guarantee
the modified input lies within the training distribution.

## Evidence and decision criteria

1. A synthetic known-dependency control verifies the evaluator and temporal replay;
   synthetic differences are implementation evidence, not financial findings.
2. A development-only bank audit compares paired responses and explanation rankings,
   with matched explanation sizes and appropriate controls. Report all attempted cases.
3. The main audit should report effect magnitudes and uncertainty. Select numerical
   materiality thresholds on development data before final testing; do not invent a
   universal threshold at Step 1.
4. Tabular/temporal/no-graph controls establish predictive usefulness. A complex model
   with weak calibration is insufficient evidence for a finance contribution.
5. Record bank counts and distinct failure events. Repeated positive bank-quarter
   windows are not independent failures. Report scarce events and clustered dependence.
6. Reject a first-method claim if equivalent prior methods are found. Narrow or stop
   the methodological claim if only arbitrary, invalid, or negligible changes remain.

## Scope, feasibility, and publication standard

Steps 1–7 finish at evidence collection and a novelty pilot. Full temporal GAT/GRU
training, final test evaluation, a completed manuscript, submission, and acceptance
are later work. No causal contagion or systemic-risk claim follows from similarity
edges or explanation fidelity. Three retrospective failure cases cannot establish
general predictive validity.

Target a relevant Q1 journal only if the completed research demonstrates an important
contribution, convincing comparisons, reproducibility, and honest limitations.
Quartile system, category, year, scope, and fees must be verified in Step 2; acceptance
is not promised. Record access restrictions and unverified rankings explicitly.

## Ownership and source precedence

Atharva Sheersh Pandey collects 50% of eligible banks and owns all software, data
engineering, models, explanations, and technical evaluation. Ayush Sinha collects
the other 50% and handles finance literature, source documentation, and financial
case studies. No ML implementation or evaluation is assigned to Ayush. Allocate
whole bank histories, not arbitrary halves of bank-quarter rows.

Source precedence: the latest direct user instruction and pasted execution request
govern; the revised 26 October work split supersedes older ownership tables. Original
blueprint assertions about novelty, 150–250 banks, 5–10% positives, or publication
fallbacks are proposals and require verification.

Read-only source artifacts outside the checkout, SHA-256:

| Artifact | SHA-256 |
|---|---|
| paper2.pdf | 0ed94ab8643202359fe24f81ea9421ef67e3071f5e59fc9314c7c6f045ff28a0 |
| Research_Work_Division_Ayush_Atharva.docx | febbedd36432468c75d328c8e6e0692fc8ceb79823f93c11b28c525359ffc73b |
| RiskTrace_Revised_Work_Division_50_Percent_Bank_Data.docx | 70777924b0c91eb5e83fd35ce272866afe2ee7cc12910b9d7bd5516dfa48b480 |

## Step 1 completion check

The question, candidate distinction, proposed population, outcome, timing, controls,
rejection conditions, and ownership are explicit. No observed coverage, predictive
performance, confirmed novelty, or journal ranking is asserted. Steps 2–5 may revise
the proposed choices through a recorded amendment rather than silent scope changes.
