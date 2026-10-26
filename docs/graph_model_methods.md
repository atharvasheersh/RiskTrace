# Step 10 graph model and control specification

Inputs, folds, horizons and per-fold preprocessing are identical to the baselines.
No failure labels or future aggregate statistics construct edges. At each quarter,
only financially usable banks existing at the forecast origin are active. Current
quarter features of other active banks are assumed available under the same 60-day
lag; this is a contemporaneous multi-bank forecast setting, not access to future
periods. Historical snapshots remain revised, not verified point-in-time vintages.

Primary graph: directed financial-composition kNN in standardized five-ratio space,
k=3 or 7, excluding self from the neighbor budget, with an additional permanent
self edge. Ties use sorted CERT order. Neighbors are targets of each receiving
bank's aggregation. These are similarity links, not observed interbank exposures.
Training-fitted scaling stays frozen at inference and within explanation audits.

Static GAT: one learned linear projection, one attention head with additive
query/source score and LeakyReLU(.2), softmax over self/valid neighbors, ELU aggregate,
and logistic readout. Temporal GAT+GRU passes the GAT representation through a
shared own-bank GRUCell before the readout. Hidden width is 8, with two candidate
graphs k=3/7. The bounded neural optimizer, 40 epochs, class weighting, prior
correction and three seeds match the baseline budget. This is a deliberately small
architecture/search, not an exhaustive GNN comparison or architectural novelty.

The already-trained no-graph GRU is the temporal control. Additional temporal GAT
controls use k=3: random neighbors with fixed seed/current-node set, and an exogenous
state-first neighbor ordering with deterministic ties. The latter fills from other
states when fewer than k same-state banks exist. These fixed controls receive one
configuration each, not an extra test-selected search. Random graphs preserve
out-degree; they are not claimed to preserve every structural property of the
feature graph. All current metadata are report-specific; no future headquarters
or charter labels are substituted.

Recurrent states reset at unavailable/unusable reports or RSSD changes. GRU state
is per CERT; there is no cross-certificate entity splicing or learned bank-ID
embedding. Graph nodes never aggregate other banks' recurrent hidden states: their
messages contain contemporaneous projected ratios. The actual dependency contract
and efficient explanation replay must respect this implementation.

Graph caches include input/active-node/metadata/builder fingerprints; training and
evaluation graph SHA256s are logged. Tests verify inactive future nodes cannot
enter current neighborhoods, permutation/index equivariance, attention normalization,
local versus batched predictions and temporal nonanticipation. Checkpoints, candidate
metrics and OOF predictions are generated from a committed implementation before
any final-test opening. Report extra cost and negative predictive findings directly.

Architecture reference: Velickovic et al., Graph Attention Networks (ICLR 2018
author version), https://arxiv.org/abs/1710.10903. The implementation is a small
specified variant with one head and no dropout, not a claim to reproduce all
settings/benchmark results of that paper.
