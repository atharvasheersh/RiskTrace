# RiskTrace Steps 8 to 14 execution and handoff

Updated27October2026. Research implementation and a reviewable manuscript/package
are prepared. **The study does not establish high novelty, useful graph warnings
or Q1 submission readiness.** No submission, author approval, acceptance or
publication is claimed. The latest user request gives Ayush substantive ML tasks;
the revised allocation supersedes the earlier no-ML restriction.

## Stage status

| Step | Status | Evidence and remaining work |
|---|---|---|
|8 Merge and freeze|Computationally complete; finance/source review provisional|Official-source canonical rebuild, conflict/unit/identifier checks, immutable role keys, training-only transforms and leakage audit. No Ayush submission received. User approved annual2012--2020 rolling validation.|
|9 Baselines|Complete bounded exploratory runs|135 development fits: prevalence, logistic, XGBoost and GRU. Same eligible keys and information clocks; thresholds selected on pooled validation. Sparse-event calibration limitations remain.|
|10 Graph models|Complete bounded exploratory runs|162 development fits: staticGAT, GAT+GRU, random and state controls; k3/7. Frozen pre-test plan committed before performance opening. No useful graph superiority established.|
|11 Explanations|Computational audit complete; financial/alert interpretation limited|Equal two-edge attention/mask/random comparison and all-population seed11 financial audit, with historical replay, exclusions, support diagnostics and null controls. All masks explain nonfailure; not a validated risk-alert explainer.|
|12 Robustness and cases|Technical work complete; finance cases provisional|Crossed institution/year resampling, seed/graph/component/report-year checks, four proposed cases and matched controls. Ayush selection and finance review pending.|
|13 Manuscript and verification|Review package complete; human/scientific approval pending|Editable TeX/Markdown/JSON,13-page reviewPDF,17 reference records,114 empirical claim entries plus method source map. AI technical audit,28 tests and isolated inference/table/figure reproduction completed.|
|14 Publication|Preparation partial; no submission|Conditional venue checks, planning cover letter, approval register and readiness checklist. Current guide/ranking/fees, author declarations and explicit approvals unresolved.|

## Dataset and clocks

Version `analysis-v1-15e5448d4a96`:51,339 eligible bank-quarter reports,
1,614 individual FDIC-insured bankCERTs,2010Q1--2025Q4, operational assets
USD1B inclusive to250B exclusive. CanonicalCSV SHA256:
`15e5448d4a9698cf3c1c44917abeb18e786afd573f8df5d47c00f7d9e83424d2`.
The digest above is the canonicalCSV digest; official raw files have separate
per-response hashes in the source manifests.

Each collaborator has807 banks. Atharva's collection has25,517 reports with123
financially unusable retained flags and23,852 usable labeled rows before purging.
The centrally assembled wider official panel is not attributed to Ayush. All64
eligible quarter totals and recorded asset-band interruptions were reconciled.

Revised snapshots use an assumed60-day reporting lag, not verified historical
publication vintages. Failure observation is capped at25August2026. CERT is the
bank outcome unit; three CERTs changeRSSD, sixRSSDs spanCERTs and224CERTs change
names. No cross-CERT splicing; states reset at gaps/unusable reports/RSSD changes.
Historical roster completeness, legal succession, merger competing events and
deposit-scope interpretation remain finance/source limitations.

Annual validation2012--2020 contains26,104 records,17 positive quarters and six
failed banks. All training labels, both classes, require the entire outcome window
to mature strictly before that fold's forecast origin. The final fit at30May2022
uses31,319 mature records through2020Q4 and22 distinct failed banks. Nominal
test2022--2025 becomes observable reports2022Q1--2025Q1:12,783 records,16 positive
quarters and four failed banks. Late2025 horizons are censored;2021 covariates
may warm recurrent states, but immature2021 labels cannot fit/select that model.

## Main results

Development AP: XGBoost0.204230, logistic0.196702, staticGAT0.068351,
GAT+GRU0.060116. The graph model's slightly better development Brier is not a
superiority result. Held-out AP: XGBoost0.006225, GAT+GRU0.001961 and
logistic0.017785. XGBoost and every graph model detect0/4 failure events at
unchanged development thresholds. Logistic detects1/4 at achievedFPR2.005%, with
a332-day warning for that detected event only. These are not matched1%testFPR
comparisons. No threshold or model is reselected on the test.

Primary current-input paired audit:12,780 matched cases,10,995 complete audits,
mean gap0.015143percentagepoints, maximum3.951038pp, top-one disagreement13.49%
among complete audits, paired threshold disagreement0.8764% among matched cases.
Lag1:12,509 matched cases,10,689 complete, mean0.006993pp, top-one13.66%.
The primary lags attempt177,023 subsets;14,420 are invalid, recorded without
resampling. Historical/current unattempted exclusions are separately logged.
All12,783 edge targets predictp1<0.5; optimized masks therefore explain nonfailure.
Signed p1 response cannot alone establish a superior explanation method.

Five hundred paired institution-component/year bootstrap draws retain common
weights across models. AP is undefined in82; AP percentile ranges condition on418
defined draws. Coverage is not established with four events/four report-year
blocks. Seed variation is sensitivity, not an independent-data confidence interval.
Case packets distinguish Republic Bank27332/2024 from First Republic59017/2023;
SVB24735 and Signature57053 fail in2023. Interpretations are retrospective and
pending finance review, not prospective issuance or causal explanations.

## Verification and failures

See `independent_verification.md`. The independent AI reviewer checked labels,
all190,255 role memberships,10 preprocessing objects,23 checkpoint fits, metrics,
actual replay, explanations, bootstrap outputs and case matching. Original missing
control-attempt details were supplemented without changing case results. The plan's
indirect preprocessing binding remains a future hardening issue; current digests
match the original51e3652 manifest. No frozen numerical source was changed after
the first test opening.

An isolated environment from the unchanged lock passed28tests in35.64seconds,
recreated all23 saved-fit forecasts/nine primary tables within1e-6 (actual maximum
ensemble difference below3e-9), checked114 empirical claims, and regenerated all
eight figure files byte-identically. This is inference/table/figure reproduction,
not a claim to retrain all297 development fits or recollect independent vintages.

Compute was localCPU, two threads per fit, on a12-logical-processor/approximately
16.8GBRAM Windows host. No paid compute was used. Per-fit wall times and versions
are saved in development/final manifests; financial-audit times in its run manifest.
Do not interpret summed fit times as the total session wall time. The environment
install initially hit transient dependency-network errors; an unchanged-source retry
succeeded. A CRLF/LF equality guard failed before test computation and was repaired
before the scientific plan was recommitted. TeX initialization timed out once, then
compiled; the DOCX renderer lacked LibreOffice, so Word/Poppler provided actual
document QA. No failed run is represented as successful evidence.

## Artifacts and Git provenance

Repository root: `C:/Users/admin/Desktop/Ayush Finance Paper/RiskTrace`.
Key outputs: `paper/manuscript/`, `output/pdf/RiskTrace_Manuscript_Draft.pdf`,
`output/documents/RiskTrace_Revised_Work_Allocation_Ayush_Atharva.docx`,
`docs/claim_evidence_map.csv`, `docs/method_claim_sources.csv`,
`results/reproduction/`, `artifacts/models/` and `paper/submission/`.
The localZIP path and exact included code version/hash are recorded by the package
builder in `results/reproduction/package_manifest.json` after the reviewed release
commit; raw data, environments and large caches are excluded fromGit.

Existing pushed stage commits:51e3652 dataset;d4c158d baseline implementation;
8a16565 baseline results;b83a7bc graph implementation;5058b1f graph development;
3cfda90 final-evaluation/audit implementation;38f98d2 initial plan;efe8166 technical
newline guard;86f3f7c corrected pre-test plan;92a58f9 final predictions;deabc6c
explanations/ledgers;c2edb7e robustness/cases/figures. Later manuscript, allocation
and package-registry commits are identifiable by their detailed Git subjects and
ordinary pushed history. No PR, forced push or history rewrite was performed.

## Next chronological work

1. Ayush verifies his allocated source/entity data and implements one-fold
   independent logistic/XGBoost replication; Atharva reviews the smoke run.
2. Ayush completes fixed-setting rolling replication, development calibration,
   attribution diagnostics, case interpretation and close-method comparisons.
3. Both specify the exploratory development-only alert-explanation target;
   Ayush prototypes it and Atharva verifies temporal/dependency handling.
4. Integrate genuine corrections with explicit versions. Decide whether to pursue
   a modest audit/negative-result paper or a separately designed stronger study
   with credible new evaluation data. Do not reuse this test as unseen.
5. Select/check the venue, current category/yearQ1 evidence, guide, anonymity,
   fees, disclosures and data/code rules. Agree actual author contributions/order,
   affiliations, funding/conflicts, rights and license.
6. Reproduce the exact final version, obtain both authors' explicit approval,
   then obtain user authorization before any external submission or charges.
   Respond only to real reviews; publication remains conditional on acceptance.

The earlier16-week submission-readiness target needs revision after the scientific
direction decision. The immediate deliverable is a rigorous reviewable package,
not an unsupported positive paper or an invented publication outcome.
