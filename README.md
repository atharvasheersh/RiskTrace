# RiskTrace

Research feasibility project on bank-failure forecasts and dependency-aware graph
explanation evaluation. **The novelty and publication prospects are unproven.**
Current scope: Steps 1--7, before full temporal GNN training or manuscript submission.

## Setup (PowerShell)

```powershell
uv sync --locked --extra dev
uv run --locked risktrace check-config
uv run --locked pytest -q
```

Python 3.11/3.12; pinned dependencies and uv.lock. Configuration:
configs/data_spec.yaml. Research scope: docs/research_spec.md. Source/label contract:
docs/population_and_labels.md and docs/data_dictionary.csv. Literature and journal
evidence are in docs; provisional citations in paper/references.bib.

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

Atharva Sheersh Pandey owns half the banks and all technical/ML work. Ayush Sinha
owns the other half, finance literature, documentation and cases, with no ML tasks.
The bank allocation is separate from the chronological model-evaluation split.
