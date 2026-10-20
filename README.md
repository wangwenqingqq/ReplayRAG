# ReplayRAG: controlled visual-repair memory pilot

**Status:preparation only.** The hypothesis is that state-conditioned repair
memory,selected by controlled replay,can outperform equally validated generic
procedure memory on unseen charts. Novelty and efficacy are not established.

This initial repository contains a CPU-only provenance and split audit of the
official ChartQA snapshot,a deterministic identity-only candidate cohort,and a
draft falsification protocol. There is no VLM runner,repair library,trained
retriever or GPU result yet. Model selection and the final experiment contract
remain unresolved;do not treat the draft as a frozen model campaign.

## Reproduce the metadata audit

Use ordinary Python3 with its standard library.No dependency installation or
GPU is needed.All output paths must be fresh.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 test_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 audit_chartqa.py --work /new/private/audit
```

If GitHub's anonymous API quota is exhausted,use `--github-auth`. This reads the
existing Git credential helper in memory,only sends the token to GitHub's API,
denies HTTP redirects,and never logs or persists the token. It does not modify
authentication settings. Failed runs are not automatically resumed or replaced.

The source is pinned to `vis-nlp/ChartQA` commit
`044eabfc306abfe9340c5741f0093aefc5973d06`. Downloaded QA metadata stays outside
Git. Image/table **tree identities** are inspected without downloading the images
or table contents. Git image-blob equality detects byte-identical charts,not
perceptually equivalent re-encodings or common chart templates.

`AUDIT_CONTRACT.json` freezes this metadata-only audit. It does not freeze the
model comparison. See `GATE0_PROTOCOL_DRAFT.md` for unresolved admission gates.

## Current result

The completed audit covers 32,719 QA records. It identifies byte-identical charts
across splits and 74 same-image/same-question groups with differing labels.
The 192 identity-only candidates avoid these identified conflicts, but template
independence and answer correctness remain unreviewed. The checked NAS paths are
not mounted in the current execution namespace, and a subsequently supplied model
root is not traversable by the execution account. Model admission is blocked.
See [the report](REPORT.md), [claim-evidence ledger](CLAIM_EVIDENCE.md), and
[`evidence/metadata_r2/`](evidence/metadata_r2/) for results and offline closure.

## Attribution and redistribution

ChartQA's upstream repository and dataset cards declare GPL-3.0. No dataset
images,QA contents,annotations,tables or upstream code are redistributed here.
Obtain authorized original inputs from the [official repository](https://github.com/vis-nlp/ChartQA)
or its linked dataset. This repository's original audit code has its own license;
that does not relicense the external benchmark or its source charts.
