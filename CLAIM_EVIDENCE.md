# Claim-evidence ledger

Experiment: `ReplayRAG_20261020_ChartQA_Metadata_Gate0A`. All measured claims
below use the pinned source and contract in `AUDIT_CONTRACT.json`; closure date
2026-10-20. Raw QA and catalogs remain private; reproducible identities and
aggregates are in `evidence/metadata_r2/`.

| ID | Claim and exact scope | Status | Evidence | Material caveat / permitted wording |
|---|---|---|---|---|
| M1 | 32,719 records inspected at the pinned ChartQA commit | measured | AUDIT_RESULTS, DOWNLOADS, CENSUS, CLOSURE | Metadata only; no pixel or answer adjudication |
| M2 | Train/test, train/val, val/test contain 10/5/1 common image blobs | measured | AUDIT_RESULTS; independently reconstructed tree identities | Exact bytes, not perceptual/source-family leakage |
| M3 | 74 exact image/question groups have nonidentical labels | measured | AUDIT_RESULTS; independent raw-label closure | Label variants, not established annotation errors |
| M4 | All 192 selected candidates are byte-identity disjoint and avoid the identified conflicting groups | measured | CANDIDATE_IDENTITIES, CLOSURE | Identity-only pools; global review flag remains true |
| M5 | Existing model runtimes are visible, but checked NAS names are not mounted in the current namespace | partial | Private read-only preflight; sanitized REPORT resource section | Bounded path check; no universal absence claim |
| R1 | Repair memory beats equally validated generic procedures under matched budgets | unknown | No evidence; GATE0_PROTOCOL_DRAFT | No model comparison performed |
| R2 | Controlled replay measures transferable causal repair utility | unknown | No evidence; paired-prefix/seeding controls proposed | A successful continuation alone does not establish this |
| R3 | Repair-state plus visual evidence is a distinct non-incremental contribution | unknown | PRIOR_ART; no decisive same-contract comparison | Novelty NOT_ADMITTED, not automatically rejected |
| R4 | Cross-template transfer and end-to-end benefit | unknown | No evidence | Exact-byte disjointness and CPU audit do not establish either |
