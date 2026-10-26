# Step 8 analysis freeze

The user approved annual expanding-origin development validation for 2012--2020
on 27 October 2026. See protocol_decision.md and configs/splits.yaml. The original
2022--2025 performance holdout is retained; no test metric has been inspected.

`risktrace build-analysis` reconstructs all 51,339 records directly from the
checksum-verified official financial/failure JSON snapshots, rather than trusting
the previous derived CSV. All 22 raw fields reconcile exactly with the preserved
panel; zero value conflicts or duplicate source keys. The source is centrally
downloaded FDIC bulk, **not a verified submission from Ayush**. No new collaborator
file was found in the supplied workspace material. Ownership remains 807 banks
per person, and finance/source review by Ayush is pending.

The active dataset version and SHA256 are recorded in
data/manifests/analysis_v1.json. It identifies the ignored local canonical CSV,
source manifest, preprocessing JSON and committed gzip split-key file. Data files
cannot be overwritten with different content. The earlier Step 7 source/processed
snapshots are preserved. A first uncommitted build without the conservative history
reset column is preserved locally but is not the active analysis version.

There are 190,255 explicit train/validation/test memberships across nine development
folds and the final fit/test. All validation years are retained, including years
with no failures; pooled validation is 26,104 quarters from 1,213 banks, including
17 positive quarters from six distinct banks. The final fit uses 31,319 records,
1,295 banks and 22 positive banks, with report dates through 2020Q4. Full-horizon,
usable final-test membership is 12,783 quarters. These are eligibility counts, not
predictions or evidence of model quality.

Each annual model origin is 30 May. All training outcome windows end strictly
before its origin, for both classes. Final static weights fit as of 30 May 2022;
settings and calibration cannot use 2021 labels maturing afterward. Five named
ratios alone enter the model. Median, mean and scale are fitted on each exact
training membership and saved with its key hash and maximum horizon end. Core
undefined ratios are excluded by the established usability contract; imputation
does not turn structural zero-loan ratios into valid training examples.

Identifier audit: three CERTs change RSSDID (32541, 35525, 4999), six RSSDIDs are
shared across multiple CERTs, and 224 CERTs have multiple historical names. The
flagged source records are committed under results/analysis. Do not merge entities
by name or RSSD alone. CERT remains the FDIC outcome unit; recurrent histories reset
on missing reports, unusable records and RSSD changes. Historical legal succession
and merger competing-risk interpretation remain a finance/source limitation.

Raw amounts retain USD-thousands convention, EQTOT closes the balance identity,
and derived ratios are independently recalculated. Optional domestic uninsured
deposit scope stays outside the model. The outcome cutoff is preserved at
2026-08-25; revised API snapshots and assumed 60-day availability prevent a strict
point-in-time backtest claim. No 2000--2009 observations enter this freeze.

Reproduce with `uv run --locked risktrace build-analysis`. The build regenerates
the same canonical and split bytes; changed versions must have new identifiers
and documented rationale. Do not silently call collection, source accuracy or
authorship review complete because internal checks pass.
