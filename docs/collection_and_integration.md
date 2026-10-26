# Full-half collection and integration instructions

Atharva owns approximately 50% of eligible CERTs and all software/ML. Ayush owns
the remaining CERTs, finance literature, source documentation and financial cases;
no ML implementation, training, tuning or technical evaluation is assigned to him.

## Reproduce collection

```powershell
uv sync --locked --extra dev
uv run --locked risktrace collect-half
uv run --locked pytest -q
uv run --locked python scripts/verify_snapshot.py
```

The command downloads all 64 quarter-filtered official files, reusing checksum-
validated pilot caches. It checks each source total, unique CERT/date keys and
eligibility, then creates the allocation. SHA256('RiskTrace-v1:' + canonical CERT)
ascending order is alternated between Atharva and Ayush. Atharva gets the extra bank
if the total is odd. The register is data/bank_allocation.csv; do not change it
mid-collection or treat allocation as a model train/test split.

The completed snapshot contains 1,614 eligible banks and 51,339 bank-quarters.
Atharva and Ayush each have 807 banks. Atharva's 25,517 source-backed eligible
quarters are collected, including 123 financially unusable rows kept with flags;
23,852 rows are financially usable and have an observable primary label before
split purging. All 22 raw fields are present/nonmissing. Reporting-lag censoring
and model-split purging are separate from raw collection completeness.

All 579 interruptions across Atharva's 105 interrupted bank histories, and all 554
across Ayush's 120 interrupted histories, were checked by **unfiltered historical
financial queries**. Every interruption has a source report outside the asset band;
zero remain unresolved. Six source queries and their hashes are in gap_validation
manifests. This resolves those eligibility gaps, not all merger/competing-risk
questions or independent historical-roster completeness.

## Files and completion definitions

* data/raw: exact JSON responses plus metadata sidecars (local, Git ignored).
* data/manifests/full_sources.json: all successful URLs, parameters, retrieval
  timestamps, hashes, byte counts, returned counts and index versions.
* data/manifests/full_request_issues.json: failed attempts, if any.
* data/processed/full_panel.csv: broader official eligible panel (local, ignored).
* data/processed/atharva_bank_panel.csv: Atharva's allocated records, source fields,
  ratios, availability/label/censor/purge/QA flags and owner (local, ignored).
* data/manifests/processed_datasets.json: generated-file hashes/config/source link.
* results/full_data_summary.json: quarter-source totals and all-population QA.
* results/collection_coverage.json: owner-level expected/collected/unusable counts.
* results/bank_period_gaps.csv: interruption quarters between first/last eligibility.
* results/atharva_missing_fields.csv and atharva_unusable_records.csv: unresolved
  missingness and failed checks. No values are guessed or overwritten.

Expected coverage is defined by eligible official financial-report keys reconciled
to API counts. It is **not independent proof that every historical insured bank was
present in the source**, nor 64 required reports for each CERT. A size-band exit,
merger or absent filing can interrupt an observed series. Gaps are explicit and
require historical lifecycle review before asserting complete institution histories.
Collected is separate from usable: censoring, unavailable ratios and invalid fields
do not make a source row disappear. Final-test records are ingested/QA'd only;
their values and outcomes are not used for tuning the development pilot.

Event-feasibility QA finds 22 distinct positive training banks, zero positive
validation banks (2019--2021), and four distinct positive test banks, after financial
checks, censoring and purging. See event_feasibility_by_split.csv. The planned
validation block is unsuitable for failure-based model selection. Do not tune on
the final test to compensate or silently broaden the label. A research-protocol
decision is required before Step 8 onward.

## Ayush handoff

The broader bulk cache contains records across both allocations, as permitted by
the task. That does **not** mean Ayush has submitted or checked his collection.
His status remains 'submission not received or checked'. He may use official bulk
sources and must return his complete eligible series using the exact raw column
names in configs/data_spec.yaml, including CERT and YYYYMMDD REPDTE. Keep source
URLs, retrieval dates, units, file hashes, missing values and any definition changes.
He should also verify source/finance semantics and investigate gaps and cases.

For a future submitted CSV:

```powershell
uv run --locked risktrace verify-integration --file C:/path/to/ayush_raw.csv
```

This checks raw columns, canonical CERTs, duplicate/quarter keys, ownership, unexpected
records, expected coverage and financial validity. It writes nothing to the panel.
After schema/key checks, Atharva must compare substantive field values and source
provenance, reconcile revisions, recompute all derived columns/labels centrally and
reject overlapping or inconsistent records. This command alone does not certify
source accuracy or change Ayush's completion status. No actual submission was received.

No statement claims these historical revised snapshots were available to a predictor
in real time. Follow the availability, censoring, lifecycle and revision limitations
in population_and_labels.md before predictive research proceeds.
