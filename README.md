# RiskTrace

Research feasibility project on bank-failure forecasts and dependency-aware graph
explanation evaluation. **The novelty and publication prospects are unproven.**
Steps 1--12 have computational artifacts; the manuscript and research package are
prepared for review. Finance validation, author approvals and submission remain
pending. The final study found weak warning performance and small average audit
gaps, not graph superiority. See docs/steps_8_14_report.md and
docs/final_novelty_and_research_questions.md.
The completed work, commits, actual coverage and limitations are summarized in
docs/steps_1_7_report.md. The user approved annual 2012--2020 rolling validation
after the original zero-event validation finding. See docs/chronological_action_note.md,
docs/protocol_decision.md and docs/dataset_freeze.md; the event budget remains small.

## Setup (PowerShell)

```powershell
uv sync --locked --extra dev
uv run --locked risktrace check-config
uv run --locked pytest -q
```

Python 3.11/3.12; pinned dependencies and uv.lock. Configuration:
configs/data_spec.yaml. Research scope: docs/research_spec.md. Source/label contract:
docs/population_and_labels.md and docs/data_dictionary.csv. Literature and journal
evidence are in docs; verified reference metadata are in paper/references.bib.

Raw data belongs in data/raw; derived panels in data/processed. Both are ignored.
Small source manifests are committed under data/manifests; reports under docs and
results. See docs/reproducibility.md for evidence and experiment formats. Later
stage commits add executable download and paired-audit commands here.

```powershell
uv run --locked risktrace pilot-data
```

This retrieves only the 12 development quarters in 2010--2012, validates cached
responses against checksums, checks source counts, joins failure outcomes and
writes data/processed/pilot_panel.csv plus results/pilot_data_summary.json.
The failure source index date conservatively bounds the labeling cutoff.

```powershell
uv run --locked risktrace audit
```

Runs the synthetic demonstration and limited development-bank paired audit. See
docs/audit_methods.md and docs/novelty_pilot_decision.md before interpreting results.
The pilot uses a small graph-aggregation/memory/logistic model, not a full TGNN.

```powershell
uv run --locked risktrace collect-half
```

Creates data/bank_allocation.csv and Atharva's full agreed eligible bank-quarter
series at data/processed/atharva_bank_panel.csv. Collection/coverage definitions and
the future Ayush handoff are in docs/collection_and_integration.md. Broader bulk
downloads do not establish completion of Ayush's allocation. This is the Step 7
stopping point; full-scale training and submission require subsequent research work.

```powershell
uv run --locked risktrace review-protocol
uv run --locked risktrace build-analysis
```

The approved analysis build verifies original source hashes, rebuilds raw/derived
data, freezes explicit split keys and training-only preprocessing, and records
lineage in data/manifests/analysis_v1.json. No test performance is opened by it.

Atharva Sheersh Pandey owns half the banks and the primary technical/ML pipeline.
The user revised the allocation on 27 October 2026: Ayush Sinha now owns independent
baseline ML replication, development calibration/attribution diagnostics and an
alert-explanation prototype, alongside his half's source review and finance cases.
See docs/revised_work_allocation.md for chronology, acceptance criteria and the
five-page editable handoff under output/documents/. These are assigned tasks, not
claims that Ayush's work or review has been completed.
The bank allocation is separate from the chronological model-evaluation split.

## Frozen results and reproduction

The observable test contains 12,783 reports and four distinct failed banks.
XGBoost and all graph variants detect 0/4 at their frozen validation-derived
thresholds; logistic detects 1/4 at achieved FPR 2.005%. Explanation rankings can
differ between legitimate conditional/pipeline targets while mean current-input
probability gaps are only 0.015143 percentage points. Read the limitations before
interpreting either number.

```powershell
uv run --locked python scripts/build_figures.py
uv run --locked python scripts/build_manuscript.py
uv run --isolated --locked --extra dev --python .venv\Scripts\python.exe python scripts/verify_research_artifacts.py --recompute-predictions --require-clean-env
```

The verifier checks saved weights and reproduces inference/tables; it does not
rerun 297 development training fits. Restore the exact preserved source snapshot
and canonical data first; see docs/reproduction_and_package.md. The final test is
already inspected. Running more experiments does not create a new holdout.
