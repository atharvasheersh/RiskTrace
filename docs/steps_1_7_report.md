# RiskTrace: Steps 1--7 completion and research handoff

Executed locally on 27 October 2026. Repository:
https://github.com/atharvasheersh/RiskTrace. Dedicated checkout is the RiskTrace
subfolder of the original artifact directory. Main branch; local identity
atharvasheersh <171888881+atharvasheersh@users.noreply.github.com>.
No push, pull request, submission, purchase or collaborator contact was performed.

**All seven authorized stages have artifacts and working code where required.
The publication contribution is not validated, and the original validation split
must change before further modeling.** Collection completion is defined against
the official source's eligible bank-quarter records, not an independently certified
historical population or point-in-time data vintage.

## Stage status and artifacts

| Step | Status | Main evidence |
|---|---|---|
| 1 Research question | Complete as a proposed protocol | docs/research_spec.md: bank-level failure forecast; conditional vs full-pipeline explanations; falsification criteria; no systemic-risk claim |
| 2 Literature/journals | Complete with verification limits | 13-record docs/literature_matrix.csv, novelty_assessment.md, journal_shortlist.md, selected implementation inspection in literature_search_log.json, paper/references.bib |
| 3 Dataset/labels | Complete, transparently amended by pilot | configs/data_spec.yaml, docs/data_dictionary.csv, population_and_labels.md and schema hashes; CERT-quarter unit; EQTOT correction and conservative cutoff |
| 4 Foundation | Complete and executable | README.md, pyproject.toml, uv.lock, src/risktrace, tests, raw/derived separation, reproducibility guide |
| 5 Data feasibility | Complete for development sample | 7,900 reports / 793 banks / 12 quarters; data_feasibility_pilot.md; manifests, counts, issues and excerpt |
| 6 Novelty pilot | Complete as a small mechanism check; research novelty unproved | audit.py, audit_methods.md, novelty_pilot_decision.md, 30 condition logs, parameters, 1,660 accepted paired audit cases |
| 7 Assigned collection | Complete against source-defined eligible coverage | data/bank_allocation.csv, full/gap/processed manifests, Atharva panel, collection_coverage.json and integration instructions |

The minimal BibTeX entries identify verified titles/year/URLs; they are intentionally
not submission-ready author/DOI metadata. Current direct ranking-provider access,
journal-specific fee terms and some author-guide requirements remain unverified.
Existing PDF/DOCX files outside the checkout were context, not overwritten outputs.

## Local commits

Each commit has Purpose, Changes, Validation and Limitations in its body.

| Step | Hash | Subject and substantive content |
|---|---|---|
| 1 | 7422dd4 | docs(research): define the bank-level dependency-aware audit protocol — explicit audit targets, population/outcome hypotheses and failure criteria |
| 2 | 996d206 | docs(literature): bound the novelty claim and qualify journal evidence — primary-source matrix, code overlap, provisional gap and shortlist |
| 2 follow-up | a90122f | docs(journals): document historical JCR quartile evidence — institutional reproduction, exact categories/pages/year and checksum |
| 3 | 9643ca8 | docs(data): specify historical bank population and failure labels — schema, availability, censoring, ratios, allocation and coverage rules |
| 4 | 018032c | chore(repro): establish locked environment and tested data contracts — isolated dependencies, package, configuration, critical tests and provenance formats |
| 5 | c23b08a | feat(data): acquire and validate the development bank panel — actual source download, EQTOT fix, failed-query log, validation and feasibility report |
| 6 | 5dd3d7e | feat(audit): test frozen dependency-aware explanations on synthetic and bank pilots — mechanism experiments, controls, replay, invalid attempts and cautious decision |
| 7 | Final collection commit (HEAD) | feat(data): collect and reconcile Atharva's assigned historical bank panel — full population/allocation, assigned data, unfiltered gap checks, event sufficiency, integration and snapshot validation |

Resolve the final commit with `git rev-parse HEAD`; it cannot include its own hash
inside the same committed document. Inspect bodies with `git log --format=fuller`.
All author/committer records are checked separately from GitHub authentication.

## Collection actually obtained

2010Q1--2025Q4, 64 quarter ends, historical USD 1B inclusive to USD 250B exclusive,
domestic insured commercial/savings bank classes, individual CERTs. No filter for
current survival. **51,339 eligible bank-quarters / 1,614 banks.**

| Measure | Atharva | Ayush |
|---|---:|---:|
| Assigned banks | 807 | 807 |
| Expected eligible bank-quarters | 25,517 | 25,822 |
| Assigned collection verified | 25,517 | Submission not received/checked |
| Missing source-eligible quarters | 0 | No collaborator completion claim |
| Financially unusable rows retained with flags | 123 | Not reported as collaborator completion |
| Usable, labeled rows before split purging | 23,852 | Not reported as collaborator completion |

Atharva's CSV is data/processed/atharva_bank_panel.csv (9,904,015 bytes); all 22 raw
fields are present/nonmissing. 118 derived noncurrent-loan ratios are undefined
because gross loans are zero; five records fail range checks. Every accounting
identity passes with EQTOT. Ten records already failed by assumed availability.
Primary labels are censored where the failure-index cutoff cannot observe the full
horizon. These rows remain collected; model usability is a separate concept.

Hash-sorted alternating allocation balances **banks**, not report counts. Both
halves appear in the official broader bulk cache, which is allowed and does not
prove Ayush's own submission or verification. He remains responsible for his half's
collection, finance sources/cases and literature; no ML work is assigned to him.

All 579 interruption quarters in Atharva's histories were checked against unfiltered
source histories and confirmed outside the size band. The same check resolves 554
for the other allocation; zero unexplained interruption quarters remain. This does
not resolve merger competing risks or prove the endpoint has every historical bank.
Exact records and source values are in results/bank_period_gaps.csv.

Raw JSON snapshots (~official public data), metadata sidecars, full/assigned CSVs
and failure records are preserved locally and ignored by Git. Small allocation,
manifests, excerpts, coverage and issue artifacts are committed. Source snapshots
are revised API data: preserved hashes are needed for exact replication.

## Validation performed

* Isolated Python 3.12.14 with locked numpy/pandas/scikit-learn/PyYAML dependencies.
* **13 focused tests pass**: identifiers, units/denominators, bounds, duplicates,
  label clocks/censoring/purging, pagination, tampered caches, financial edits,
  real dependency rebuilding, temporal replay, coverage gaps and integration keys.
* All 64 source financial counts reconcile to unique processed keys. All eligible
  reports and assigned CERT/date ownership sets reconcile; source fields are kept.
* Real FDIC ratio cross-checks agree within 1e-8 percentage points. An initial EQ
  identity error was corrected against official EQTOT and four observed records;
  original diagnostics and failed ID-sort requests are preserved transparently.
* `python scripts/verify_snapshot.py` verifies **85 distinct raw response hashes,
  three processed-file hashes, all 51,339 rows' derived features, labels and flags,
  allocation, 30 parameter fingerprints and 1,660 unique accepted audit cases**.
* All 30 paired audits keep fitted parameters fixed; no-graph/exogenous/random
  conditions have zero conditional/pipeline response gap. Meaningful invariants
  are checked, not a claim of independent source accuracy or a correct risk model.

See results/snapshot_validation.json, the test suite and experiment CSVs. Full
evaluation-period data were ingested and checked for event sufficiency; no model
was fitted, selected or tuned on the final 2022--2025 period.

## Novelty and journal assessment

The candidate distinction survives the targeted review **provisionally**: conditional
network explanations and frozen-predictor full-pipeline explanations can differ
when banking features construct graph connections. CF3 already explains financial
GNNs with feature/edge counterfactuals; GInX-Eval, DSE, Robust Fidelity and fragility/
uncertainty work overlap heavily. The simple pipeline identity and graph rebuilding
are not new contributions. Selected code inspection found different targets, not
proof that no equivalent method exists anywhere in those projects/literature.

The small real-bank mechanism check finds a 1.338-percentage-point average current-
quarter gap at k=3 and 9.72% top-1 disagreement across accepted sensitivity cases.
That is exploratory, not a population/causal/financial-materiality result: only
27 unique bank targets survive at least once, the bank evaluation has three positive
quarters from two banks, and 12.70% of attempted bank perturbations fail constraints.
There is no consistent predictive gain over the no-graph pilot. Strong contribution
claims require new evidence, not a bigger architecture or its high pilot AUROC.

Shortlist: Expert Systems with Applications (technical audit contribution), Decision
Support Systems (demonstrated decision support) and Research in International
Business and Finance (finance significance). Their official Elsevier scope pages
were checked. An institutional reproduction of **JCR/JIF 2024, June 2025 release**
shows Q1 for ESWA/DSS in Computer Science, Artificial Intelligence and RIBAF in
Business, Finance, with separate JIF/AIS columns. This is historical institutional
evidence; current direct Clarivate/SCImago ranking and exact charges were not
verified. Sources, page numbers and checksum are in journal_shortlist.md and
journal_rank_evidence.json. No acceptance or Q1-level novelty promise is made.

## Critical limitations and precise next actions (Steps 8 onward)

**Event sufficiency is the immediate gate.** After financial checks, censoring and
purging, training has 22 distinct positive banks (64 positive quarters), validation
2019--2021 has **zero**, and the final test has four (16 positive quarters). The
planned validation block cannot estimate failure discrimination or support ordinary
failure-based model selection. Do not tune on the final test or broaden failure
labels just to improve class balance. The source-backed event count refutes the
blueprint's unverified positive-percentage assumptions.

1. Decide and document an event-sufficient evaluation protocol within the financial
   task. Assess longer historical coverage or prespecified temporal/event-aware
   validation alternatives and independent-event power. A population, period or
   outcome change is a material research decision; do not silently implement it.
2. Resolve publication timestamps/vintages or explicitly design a revision-aware
   study. Refresh failure-source coverage beyond its 25 August 2026 index cutoff.
   Independently reconcile historical bank roster/lifecycle/mergers and deposit scope.
3. Obtain and validate Ayush's raw-schema submission using the integration checks;
   compare source values and revisions, then centrally recompute labels/features.
4. Preregister hypotheses, financial materiality, dependency contracts, donor/probe
   rules, graph choices, primary metrics, bank-level uncertainty and stop conditions.
5. Implement strong tabular/no-graph baselines and close explanation-evaluation
   baselines under a leakage-safe development protocol. Require useful graph signal
   before investing in the intended temporal architecture.
6. Expand audits across defensible feature-derived/exogenous graphs, plausible and
   OOD-sensitive probes, equal explanation budgets, seeds and bank-clustered CIs;
   obtain finance review of the cases. Reconsider the novelty if effects disappear
   or equivalent prior work is confirmed.
7. Only after those gates: freeze the analysis, run the final held-out evaluation,
   draft the manuscript and reproducibility package, complete reference metadata,
   reverify the chosen journal's current ranking/guide/fees and prepare submission.

Stop here as requested: no full-scale TGNN training or manuscript submission began.
