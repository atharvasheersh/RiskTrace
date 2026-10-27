# Independent technical verification

Checked27October2026. A separate read-only AI reviewer audited the implementation
and outputs. This is not external peer review, finance validation or author
approval. The primary agent also executed the fresh-environment reproduction below.

## Independent checks completed

* All28tests passed. The reviewer separately checked190,255 role memberships and
  all10 preprocessing objects, strict horizon-maturity cutoffs and exact training
  statistics.
* Three-month and twelve-month labels were reconciled against original failure
  source responses rather than trusting the derived label panel.
* All23 final checkpoint-fit records and their artifact hashes were checked.
  Nine common evaluation populations, metrics, thresholds and event warnings
  reconciled. Recreated primary seed11 temporal-GAT probabilities differed by at
  most approximately1.6e-9 in the independent check.
* Actual full-snapshot versus target-local replay agreed in six interventions,
  including a historical RSSD reset. The shortcut is valid for this model's
  contemporaneous-input messages and own-bank recurrence, not arbitrary TGNNs.
* Explanation budgets, denominators, invalid-attempt counts, paired gaps and null
  controls reconciled. Every edge target explains predicted nonfailure. Signed
  necessity is not a universal method-quality ranking.
* Crossed bootstrap outputs, undefined-draw counts and case/control matching were
  independently regenerated/checked. Four figures were visually reviewed.
* The working manuscript's headline values and percentage-point conversions were
  checked. Wording was corrected from ambiguous 'failure counts' to
  'invalid-attempt counts', and fixed-k random neighbors are not represented as
  preserving the entire degree sequence. Ranking differences between legitimate
  targets are not described as within-target stochastic instability.

## Findings and disposition

1. **Detailed invalid-control ledgers were missing.** Original counts and case
   outputs were present. `scripts/supplement_control_ledgers.py` replayed the same
   frozen controls and asserted agreement with original case values/counts,
   exporting508 invalid/unavailable records per family. No primary result changed.
   See `results/explanations/reporting_corrections.json` and commitdeabc6c.
2. **The analysis plan binds preprocessing indirectly through a mutable manifest.**
   A self-consistent change to that manifest and preprocessing could evade the
   plan's original data/split guard. No such change occurred: both reviewer and
   `scripts/verify_research_artifacts.py` compare the manifest's data, split and
   preprocessing digests with the original committed Step8 record51e3652, and
   check the tracked preprocessing copy. The current study matches. The frozen
   plan has not been silently changed after opening test results. A future protocol
   must directly bind preprocessing and the analysis manifest, and test mutation
   rejection; this architectural hardening remains future work.
3. **The first numeric evidence map was incomplete.** It has been expanded to114
   source-selected empirical entries, plus `method_claim_sources.csv` for periods,
   constants, case identifiers and derived percentages. The primary verifier
   reconciles all114 entries; independent human author review remains required.

## Fresh environment reproduction

`uv run --isolated --locked --extra dev --offline --python .venv/Scripts/python.exe`
constructed a separate environment from the unchanged numerical lock on the same
Windows machine. It installed36packages. Results:

* 28 tests passed in 35.64 seconds.
* Inference from all 23 saved fits reproduced all nine primary result tables. The
 largest ensemble probability difference from saved CSV values is below3e-9;
 the declared tolerance is1e-6. Thresholds and labels were not refitted.
* The 114-entry empirical claim map reconciled to its saved sources.
* Four PNG/SVG figure pairs rebuilt byte-identically. The figure generator removes
 SVG date metadata and fixes its hash salt; no figure values are hand-edited.

See `results/reproduction/verification.json`,
`principal_table_reproduced.csv` and `figures.json` for exact environment, hashes,
model differences and scope. This reproduces inference/tables/figures on the
preserved snapshot; it does not claim to rerun297 training fits, independently
collect data, validate economic interpretations or establish cross-machine
bitwise determinism.

## Document checks

The editable TeX project compiled successfully using the desktop compiler after
its first initialization timed out while downloading the TeX runtime. The review
PDF is a separate ReportLab layout from the same structured content, not an export
of the compiled TeX pagination. All13 review-PDF pages were rendered and inspected.

The revised allocation DOCX has five pages. The packaged LibreOffice renderer
failed because no soffice executable is installed/bundled on this Windows host.
Microsoft Word exported the actual DOCX to a local QA PDF; Poppler rendered every
page, and all five pages were inspected. An inherited blue title border was removed
and the final version re-rendered. QA images/PDF are not public deliverables.
