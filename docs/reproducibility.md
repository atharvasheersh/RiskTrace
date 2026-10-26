# Reproducibility and evidence formats

Use Python 3.11 or 3.12. `uv.lock` resolves exact versions and artifact hashes;
`uv sync --locked --extra dev` recreates the environment. Run from repository root.
The data contract is configs/data_spec.yaml, not duplicated constants in notebooks.
Source code and environment are reproducible; an API can revise historical records.
The source checksum identifies what was actually used, not immutable API content.

Raw responses live under data/raw (ignored); processed panels under data/processed
(ignored). Commit small summaries, allocation and manifests. A source-manifest record
contains URL, endpoint, query parameters, UTC retrieval time, relative local path,
SHA256, byte length, source total and returned count. Failed requests retain error,
URL, attempt and time in an issue log; never put credentials in URLs/manifests.

Experiment records must include config, seed, data and parameter fingerprints,
train/evaluation period, sample count, metric definitions, actual outputs, timing
and limitations. Invalid perturbations are counted, not silently regenerated until
they pass. Necessity and sufficiency are signed model-probability responses, not
causal effects. Conditional and full-pipeline interventions answer different targets.

No dependency installations change global Python. No raw source is manually edited.
Download scripts should be idempotent, validate caches against a recorded SHA256,
check API total counts and uniqueness, retry boundedly and save partial provenance.
Repeated execution can require internet unless cached raw files and lock artifacts
are present. Preserve the original raw snapshot for revision-aware replication.
