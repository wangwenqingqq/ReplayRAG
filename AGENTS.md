# ReplayRAG working rules

- This is a falsification pilot,not an admitted novelty or production system.
- Keep technical documentation and comments in English.
- Preserve all failed attempts and raw evidence outside Git;never overwrite runs.
- Do not download model weights or change shared-host mounts/services automatically.
- A GPU run requires an accessible pinned VLM checkpoint,qualified inputs,a frozen
  model/execution contract,an idle-device check,and a task-owned campaign lock.
- Ground-truth labels,tables and annotation values are evaluator-only inputs.
  Neither a solver nor a retrieval query may receive them or their low-entropy hashes.
- Use equally sized and equally validated generic-procedure and repair memories.
  Retain no-memory resampling and reflection controls;charge the common prefix,
  query construction,image processing,verification and all continuation samples.
- Group by chart identity;exact-byte disjointness is not template/source independence.
- A metadata audit,synthetic unit test or a single successful replay is not evidence
  of causal repair benefit,cross-chart transfer,or end-to-end improvement.
- Publish only task-owned code,protocols,aggregate results and reproducible hashes.
  Do not redistribute benchmark images,QA text,labels,model weights or host configuration.
