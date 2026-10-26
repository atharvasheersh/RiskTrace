# Novelty assessment

Checked 27 October 2026. This is a targeted scoping review, not a systematic proof
that no equivalent research exists. See `literature_matrix.csv` and
`literature_search_log.json` for claim-level scope and implementation evidence.

## Decision after literature review

**Continue with a small evaluation pilot; do not claim a new GNN architecture or
confirmed high novelty.** The candidate gap survives as a narrow, provisional
bank-specific audit question. It does not yet justify a Q1 submission.

Already established:

* Temporal graph models of banks and construction sensitivity: ST-GAT and the
  temporal multiplex banking preprint.
* Financial explanation fidelity: CF3, including factual/counterfactual reasoning.
* Distribution-shift-aware evaluation: DSE, GInX-Eval, and Robust Fidelity.
* Explanation uncertainty, fragility, robustification, and certification: EU-GNN,
  Fragile, curvature-based explanations, and XGNNCert.
* Financial risk under incomplete network information: Ahn, Chen, and Kim.
* Degenerate explanations missed by common metrics: the ICLR 2026 author version
  of GNN Explanations that do not Explain.

The proposed distinction is to specify and propagate raw financial dependencies
through derived ratios, similarity edges, and affected temporal states while
auditing an unchanged trained pipeline. It is not merely another graph perturbation,
robustness score, uncertainty ensemble, or attention-versus-explainer comparison.

## Implementation checks

Two GInX-Eval files and a Robust-Fidelity file were inspected. GInX's hard degradation
routine filters explanatory edges and trains on degraded graph data. Robust Fidelity's
selected routine samples masks over supplied graph edges and uses supplied node
features. Neither inspected path implements the proposed bank raw-record dependency
contract. This is a bounded file-level observation; neither project was reproduced,
and an exhaustive implementation equivalence check has not been completed.

CF3's joint feature/edge reasoning is particularly important overlap. A manuscript
must explain why a deterministic bank preprocessing dependency is a distinct target
rather than simply restating joint attribution. DSE's generated completions and
GInX's retraining address OOD evaluation but must not be represented as frozen-model
paired audits. Generic consistency across graph constructions is supporting evidence,
not the primary new claim.

## Necessary pilot evidence

1. Verify a known computational dependence on synthetic controls. Include a fixed
   exogenous-graph control where rebuilding should make no difference.
2. Use financial input changes with explicit constraints; recompute dependent
   features/edges while preserving unchanged parameters and initial temporal state.
3. Separate input invalidity and OOD effects from dependency effects. Report invalid
   attempts rather than silently filtering them away.
4. Report signed and absolute response changes, necessity/sufficiency, feature-rank
   agreement, seeds, graph definitions, and costs at comparable explanation sizes.
5. A bank pilot must use development records and be labeled exploratory. Predictive
   quality, independent failure counts, and calibration condition interpretation.

## Journal-level bar and stop conditions

A convincing paper would need a material empirical finding, a justified evaluator,
strong existing-method comparisons, trustworthy event labels, independent temporal
evaluation, and reproducible artifacts. Proving a difference in a constructed toy
example alone is not a contribution of that strength.

If differences disappear under valid financial perturbations, the narrower method
claim should be rejected or revised. If equivalent prior implementations are found,
report replication/application rather than first-method novelty. If the bank pilot
has too few events or weak forecasts, restrict claims to a computational audit and
state that finance significance is unestablished. Negative results do not guarantee
publication. Step 6 records the actual continue/narrow/reconsider decision.

## Search limits and citation status

The 13-row matrix distinguishes primary-method text from abstracts and selected
code inspections. Some current banking studies are preprints. Rankings and venue
identity are separate from a method's credibility. The bibliography currently
contains minimal title/year/URL records; add verified authors, venue, DOI, and final
publication details before manuscript submission, rather than inventing metadata.
