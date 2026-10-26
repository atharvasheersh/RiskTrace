# Development data feasibility (Step 5)

Executed 27 October 2026 using FDIC structured API. FFIEC bulk-download facilities
were checked first; the official filtered JSON API supplies the agreed fields with
less unrelated data than full Call Report archives. No manual statement searches
were needed. Final evaluation reports (2022--2025) were not used in this pilot.

## Actual coverage

* 12 quarters, 2010Q1--2012Q4; **7,900 bank-quarters / 793 distinct CERTs**.
* All quarter source totals equal returned unique keys; no duplicate keys.
* All 22 requested raw fields present and nonmissing in this sample; every insurer
  code is DIF. This is not proof of uniform reporting definitions over 2010--2025.
* 7,830 rows meet accounting/range/main-feature checks; 7,812 are also usable for
  the 12-month label. 18 rows were already failed by assumed availability.
* 50 positive bank-quarters represent **18 distinct positive banks**, not 50 events.
  Only three positive labeled quarters occur in 2012, a weak holdout for model claims.
* The failure API returns 384 records since 2010 through the requested cutoff.
  Its index creation date is 25 August 2026; censoring uses this conservative bound.

Results/pilot_data_summary.json records quarter counts, raw-field coverage and
checksums. The full local panel is data/processed/pilot_panel.csv (ignored, ~public
bank financials). A 12-row nonrepresentative excerpt is committed for inspection.

## Corrections and unresolved issues

1. **Accounting field:** EQ differed from EQTOT. The initial check would have
   excluded 1,239 rows. Official schema plus four source records established the
   correct identity with EQTOT; the rerun has no accounting-identity failures.
   The initial summary and source manifests are retained, clearly named v1.
2. Two reports fail the conservative range checks. Retain source values and mark
   them unusable, not zero-fill or fix them. Missing derived ratios can occur with
   zero gross loans even when every raw field is present. See quality_issues and
   feature_coverage CSV for exact exclusions.
3. Source numeric checks reproduce CHBALR and EQR from the raw amounts to 1e-8
   percentage points. The dollars-in-thousands convention follows official API
   documentation. These checks establish internal consistency, not source accuracy.
4. The first acquisition attempt sorted by ID, which the endpoint cannot sort.
   Three HTTP 400 attempts are preserved in pilot_initial_query_issues.json. The
   successful workflow sorts by CERT / FAILDATE. No missing data were invented.
5. Report dates are observed; public-availability dates are still report + 60 days.
   The index is a revised snapshot. Neither point-in-time vintages nor historical
   publication timestamps were obtained. This prevents a strict deployment-backtest
   claim. Mergers and competing exits remain an explicit limitation.
6. Uninsured-share reporting scope needs finance review despite nonmissing values.
   Exclude it from the core pilot. Duration gap and depositor concentration are
   unavailable; no renamed substitutes are used.

## Reproduction and decision

Run `uv run --locked risktrace pilot-data` then `uv run --locked pytest -q`.
The workflow verifies cached hashes, source totals, keys, quarter dates, eligible
asset band and labels. Raw response and metadata sidecars are separate from
processed CSVs; committed manifests permit reacquisition and snapshot comparison.
API data may change, so reproduce exact results from the preserved local cache.

Six focused tests pass. Real-source ratio assertions passed. The data are adequate
for a small mechanism/engineering pilot. They are **not adequate for a publishable
generalization claim**: rare independent failures, only three positive 2012 quarters,
availability assumptions, revision bias and incomplete lifecycle verification remain.
Proceed to the minimal synthetic paired audit and a clearly limited bank-data
implementation check; do not interpret a high pilot score as publication evidence.
