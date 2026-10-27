# Population, outcomes and collection contract

Contract v1, 27 October 2026; empirical feasibility remains to be checked in Step 5.
One observation is one **CERT / quarter-end financial report**, not one bank.
CERT is the FDIC certificate identifier; names are descriptive, not join keys.
RSSDID is an optional bank identifier; no holding-company statements are joined.

## Historical population

Use every 2010Q1--2025Q4 report with USD 1 billion <= ASSET < USD 250 billion
and BKCLASS in N/NM/SM/SB/SI/SL (commercial banks and domestic savings institutions).
Exclude foreign branches, uninsured trusts and credit unions. Do not filter by
current ACTIVE status. The operational size band is not a regulatory definition
of a regional bank. Savings institutions expand the initial commercial-bank idea
to the insured depository-bank population; report results by class before pooling.
The unique CERT union defines the allocation population. A bank can enter/exit the
size band; eligibility applies separately to each date. Do not backfill a failed
bank with its acquirer's financial statements or merge different certificates.

The agreed required series is **all eligible historical bank-quarters** for the
assigned CERT, rather than 64 fabricated records per bank. Financials outside the
band are optional context and must have a separate eligibility flag if added.
For every quarter, source-reported matching counts and returned unique keys must
agree. Missing scheduled quarters between a bank's first and last eligible report
are recorded as gaps; size-band exits and mergers can explain them but require
separate lifecycle/source verification. Such gaps are not filled with zeros.
Eligibility is financial-report based: absent institutions with no financial report
cannot be certified as fully enumerated from this endpoint alone.

## Sources and field semantics

Use official FDIC BankFind financials and failures endpoints; FFIEC bulk downloads
are the fallback, not BHC FR Y-9C data. Public API currently needs no key. FDIC
documents JSON/CSV output, numeric filter ranges, and a 10,000-row page maximum.
Schema files were retrieved and read directly from:

* https://api.fdic.gov/banks/docs/risview_properties.yaml
* https://api.fdic.gov/banks/docs/failure_properties.yaml
* https://api.fdic.gov/banks/docs/swagger.yaml
* https://api.fdic.gov/banks/docs
* https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx

Amounts are treated as USD thousands; the API docs explicitly use this convention
for deposit filters. Step 5 must cross-check actual amount/ratio consistency and
record available metadata. NETINC is an auxiliary flow, not a quarterly flow or
annualized ROA unless its YTD convention and denominator are explicitly handled.
DEPUNINS covers domestic offices and insured territorial branches; **divide by
DEPDOM**, not total DEP including foreign offices. DEPINS is not assumed equal to
DEP minus DEPUNINS. Do not construct false accounting identities across scopes.

Main graph features: EQTOT/ASSET, CHBAL/ASSET, LNLSNET/ASSET, SC/ASSET,
NCLNLS/LNLSGR. The last is noncurrent loan share, not a probability of default.
Uninsured domestic deposits / DEPDOM is optional until coverage/scope is checked.
No claim that securities are liquid at book value or equity is regulatory capital.
Duration gap, maturity mismatch and depositor concentration are unavailable in this
contract. Do not invent proxies under those names. No market-data requirement.

## Outcomes, availability and censoring

Join failures by CERT. The failure table also includes assistance: exclude A/A and
REP. Include charter-termination receivership transaction codes P&A, PA, PI, IDT,
PO and MGR; investigate any unexpected/new codes before assigning a label.
FAILDATE is the effective date of cessation as a private going concern, per FDIC.
Retain all source failure records with type, including excluded records, for audit.

availability_date = report_date + 60 calendar days is a **lag assumption**, not a
verified public-release timestamp. A positive primary label requires
availability_date < failure_date <= availability_date + 12 calendar months.
Use the same rule with 3 months for the secondary label. If already failed by the
availability date, exclude the observation as unusable for forecasting. A known
event within horizon is positive even if the full horizon exceeds the cutoff.
Otherwise censor when the horizon ends after 2026-10-27. Missing failure-list entry
is a nonfailure outcome only conditional on the source's completeness.

An acquisition without recorded failure is a competing event, not a failure.
This initial binary endpoint treats no recorded failure as 0 while observable;
merger/exit timing is not yet completely reconstructed. Report this limitation;
do not interpret the label as every form of economic distress. A later competing-
risk/lifecycle analysis is required before a strong finance claim.

Chronological report-date splits: training through 2018, validation 2019--2021,
final test 2022--2025. Purge training outcome windows reaching validation availability
and validation outcome windows reaching test availability; all preprocessing fits
training only. Pilot uses 2010--2012 only. Never tune on final-test features/labels;
Step 7 may ingest and QA them without model development. Full-panel event counts
are descriptive feasibility checks, not an excuse to alter the target.

## Missingness, validity and workload

Keep blanks/null/suppressed fields missing; never convert them to zero. No ratio
with nonpositive denominator. Reject duplicate keys instead of arbitrary dedup.
Check ASSET ~= LIAB + EQTOT (tolerance max(5 thousand, 1e-5 * ASSET)), nonnegative
cash/loans/securities/deposits, and valid ranges. Negative equity is plausible
distress; preserve it if accounting is valid. Flag rather than silently clip
scope inconsistencies. Main-feature complete and accounting-valid rows form a
restricted usable subset; source rows are retained regardless. Publication must
analyze exclusions, reporting changes and missingness over time.

Allocate sorted SHA256('RiskTrace-v1:' + CERT) values alternately to Atharva and
Ayush. Odd count gives Atharva the one extra bank. This is deterministic, balanced
by bank count, independent of outcomes, not a statistical train/test split.
Each person owns the entire agreed eligible series for their banks, not half of
each time series. Finalize only after all quarter counts and coverage are checked.
Atharva owns the primary software/ML pipeline. Ayush owns finance literature,
source verification, cases and his half's collection, plus the independent ML
replication and development explanation tasks assigned on 27 October 2026.
See revised_work_allocation.md. The event-sufficiency paragraphs below preserve
the original planning requirements; actual completed counts and limits are in
dataset_freeze.md and steps_8_14_report.md.

Step 3 event sufficiency is **unknown pending actual extraction**. Step 5 will
count distinct failed CERTs and positive bank-quarters separately. Repeated positive
quarters for one bank are not independent events. A tiny event count restricts the
audit to feasibility and requires uncertainty estimates at the bank level.

## Pilot amendments (v1.1, Step 5)

The initial EQ identity flagged 1,239 of 7,900 reports. Official schema includes
the distinct EQTOT field (Total Equity Capital). A four-bank source cross-check
confirmed ASSET = LIAB + EQTOT while EQ differed. Add EQTOT to the contract and use
it for the accounting check and equity feature; retain original EQ for provenance.
Do not treat the original residual as bank misreporting or silently impute EQTOT.
This is a source-semantics correction, not outcome-driven feature selection.

Outcome censoring uses min(configured as_of, failure API index creation date),
currently 2026-08-25. Retrieval on 2026-10-27 does not imply an up-to-date index.
This conservative bound still does not prove completeness or fix revision bias.
