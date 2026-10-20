# ChartQA metadata gate: closure and open boundaries

## Decision

**Metadata closure passes; model admission remains blocked.** No model call or
GPU experiment has occurred. The selected identities are preparation candidates,
not a qualified or powered confirmatory cohort. ReplayRAG remains a research
hypothesis, not an admitted novelty or demonstrated repair mechanism.

## Measured data inventory

Upstream: [official ChartQA](https://github.com/vis-nlp/ChartQA), commit
`044eabfc306abfe9340c5741f0093aefc5973d06`.

| Original split | Human QA | Augmented QA | Total QA | Referenced PNG names | Unique image blobs |
|---|---:|---:|---:|---:|---:|
| Train | 7,398 | 20,901 | 28,299 | 18,317 | 18,271 |
| Validation | 960 | 960 | 1,920 | 1,056 | 1,055 |
| Test | 1,250 | 1,250 | 2,500 | 1,509 | 1,509 |

The audit covered **32,719 QA records**, with no missing referenced PNG filename
and no referenced chart lacking a corresponding CSV filename. Only tree
identities were inspected: image pixels, table contents and visual annotations
were not downloaded or validated.

Byte-identical image identities overlap across original splits: train/test
**10**, train/validation **5**, validation/test **1**. These are pairwise counts,
not a count of independent leakage events or a measured model accuracy effect.
There are **74 groups** with the same image blob and exactly the same question
text but nonidentical serialized labels. They require adjudication; ties,
underspecified questions and annotation mistakes are not distinguished. They
must not be described as 74 established annotation errors.

## Candidate identity pools

The predeclared seed `2026102001` yields 32 train, 32 validation and 128 test
candidate identities, balanced by human/augmented question origin. Selection
uses no model outcomes. Each candidate uses a different image blob, and any
image blob present in multiple original splits is excluded.

An independent raw-label grouping check finds **zero** selected identities in
the 74 label-variant groups. This does not clear the global data-review flag,
establish answer correctness, establish cross-template/source independence, or
constitute a sample-size justification. No test model output has been produced.
The public candidate projection excludes evaluator-only label hashes.

## Reproduction and evidence preservation

The completed audit made 17 requests and downloaded 13,979,601 metadata bytes.
The closure verifies the 23 retained run files against their census, rechecks
all six QA Git-blob identities, reconstructs every returned Git tree, replays
the deterministic selection and checks executed-source hashes.

A separate, retained commit metadata request resolves the root tree identity
`f131fa9e0003ec7724d9d5a9eaf76705734e4c42`. This is additional closure input, not
one of the original 17 audit downloads. The root-tree API response echoes its
commit argument in its `sha` field; it must not be mistaken for the tree object's
hash. A first verifier-development assertion caught that distinction; it changed
neither the original audit nor its candidates.

The first metadata attempt stopped on anonymous GitHub API quota exhaustion.
Its partial evidence and original source are retained. A separately registered
second attempt used the existing credential helper in memory, with unchanged
data identity, selection seed and download budgets. No model/GPU result was
replaced. See `evidence/ATTEMPT_LEDGER.json`.

Run the synthetic checks with ordinary Python (not `python -O`):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 test_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 test_verifier.py
```

After obtaining the authorized raw metadata via `audit_chartqa.py` and retaining
the upstream Git commit API JSON, verify without network access:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 verify_audit.py \
  --audit /private/audit \
  --commit-metadata /private/upstream_commit.json \
  --output /new/public/metadata_export
```

The upstream commit JSON is available from GitHub's official
`repos/vis-nlp/ChartQA/git/commits/044eabfc306abfe9340c5741f0093aefc5973d06`
API endpoint. Raw data and commit author metadata are not redistributed here.
API response bytes can vary across requests; retain a census of each new run,
rather than demanding byte identity of all JSON wrappers across API versions.

## Resource boundary and next action

A read-only preflight found existing Torch/Transformers runtimes and candidate
idle GPUs on the intended shared host. However, the checked NAS directory names
resolved to empty overlay directories, with no NAS filesystem mounted in that
SSH namespace. No readable Qwen-VL checkpoint was found in the bounded paths
checked. This is not proof that the server has no such weights.

A subsequently supplied model root could not be listed: an ancestor is mode
`0750` and the execution account is neither its owner nor a member of its group.
Its contents remain unknown. No elevated read or permission modification was
attempted; an owner-authorized readable path is required.

No weights were downloaded; no mounts, GPU settings or other users' services
were changed. The next required input is an accessible NAS/checkpoint path.
Then pin the complete model/runtime and image-processing identity, review the
selected inputs, and freeze a separate bounded smoke/development contract.
The draft comparison protocol still has unresolved replay-selection and power
criteria and does not authorize the full model matrix.

## Retained implementation limits

A read-only review found two non-blocking issues in the frozen audit source.
The global review flag does not include the missing-CSV count, so future users
must also inspect `referenced_images_without_table` directly. It is zero for
every split in this run. The cumulative byte ceiling is checked after each
response is received, not enforced as a pre-read network ceiling; a future
stopped attempt could receive more than that budget. This run received less
than the ceiling. Neither issue changes the measured findings. They are retained
as future-run hardening work, not silently patched into the executed source.
