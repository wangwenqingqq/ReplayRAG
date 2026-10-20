# Gate0 protocol — DRAFT,not executable experiment admission

## Scientific question

On independently held-out chart identities,does an intervention-validated repair
program improve continuation success more than an equally validated generic
program,without increasing harmful changes to initially correct reasoning?

Do not claim that replay success proves causality. A successful continuation may
be due to resampling,additional compute,answer leakage or a stronger verifier.
Nor are failure memory,local recovery or visual applicability new by themselves.
The nearest prior art and scope are recorded in `PRIOR_ART.md`.

## Stage A:inputs and runtime qualification

1. Pin the official ChartQA commit and verify all six QA-file Git identities.
2. Audit image identities across train/val/test and label disagreement for the
   same exact chart/query. Keep original data intact;never silently relabel it.
3. Prepare identity-only candidate pools:32 train,32 val,128 test questions,
   half human and half augmented per split,one question per image-blob identity.
   Exclude cross-split image identities before selecting.These counts are not
   a confirmatory power calculation and no test model outcome may be inspected.
4. Check selected rows for conflicting labels and visually audit any admitted
   examples before interpreting an incorrect answer as a reasoning failure.
5. Locate an existing readable VLM checkpoint;freeze its config,weights,
   tokenizer,processor,chat template,dtype,backend and software identities.
6. Inspect idle GPU ownership and acquire a campaign lock immediately before
   launch.Do not change mounts,GPU settings or foreign processes.

Current runtime checkpoint:an existing VLM path is unresolved. No model weights
are downloaded and no model or GPU target is admitted by this draft.

## Stage B:cheap development feasibility,not a paper result

After a separate execution freeze,first use at most16 training charts and four
initial rollouts per question,with at most512 newly generated tokens per rollout.
This proposed64-call ceiling is only for identifying whether qualified failed
and successful traces can be paired;it does not authorize the later matrix.
Freeze image-resolution and visual-token limits before launch.

Use explicit inspectable observations/operations,not claims about the model's
hidden internal causal state.Localize an externally expressed error and preserve
the identical prefix for all continuation arms. Ground-truth answers and tables
may be used offline for scoring,not in online error detection or memory queries.
If no reproducible,non-answer-specific failure/repair pair can be established,
stop before building a retrieval system;absence in this small sample is not a
universal impossibility result.

## Stage C:matched memory construction and replay selection

Use the same construction examples and teacher budget to create two candidate
types:generic procedures and state-conditioned repair procedures. Neither type
may retain source answers,instance-specific numbers or identifying chart labels.
References to visual regions must be typed and applicable,not copied test boxes.

| Memory type | Unvalidated | Controlled-replay selected |
|---|---|---|
| Generic procedure | G-U | G-V,strong keeper |
| Repair procedure | R-U | R-V,candidate |

Keep candidate counts,memory cardinality,length limits,teacher/manual curation
effort,retrieval capacity and replay-selection budgets equal. If one pool has
too few admitted entries,report feasibility failure;do not fill it with weaker
items or silently reduce the other arm after test outcomes are known.

Replay selection uses val only and must compare each injected item with an
identical prefix continued without the item,under predeclared paired seeds.
Equal-length generic reflection is an additional control. One lucky success is
not sufficient to admit a memory. Freeze the selection statistic,minimum support
and acceptance threshold after development but before any test feature/outcome
inspection. These values are currently unresolved;the full comparison cannot run.

## Stage D:independent fixed test

Freeze checkpoint/code/prompts/retrieval/routing/parameters and one primary
comparison:R-V versus G-V. Retain G-U,R-U,no-memory continuation and generic
reflection controls. Retrieve using only the currently available question,image
and predicted error state. Oracle error localization is a diagnostic upper bound.

Both memory types must be evaluated from the same state and under the same
continuation budget. Also compare a budget-matched restart from the original
question:preserving a contaminated prefix might be worse than starting over.
Separate token-budget comparisons from latency-budget comparisons;neither
implies the other. Include vision-token,crop/OCR,query,verification and rejected
candidate costs.All test attempts and failures are retained;no test-time tuning.

Primary outcomes:
- Paired accuracy difference R-V minus G-V,on the complete predeclared population.
- Wrong-to-right and right-to-wrong transitions;net gain is their difference
  divided by the full population,not only the selected failure subset.
- Repair success conditional on a qualified initial error and harmful-repair
  rate conditional on initial correctness,with separate denominators.
- Retrieval applicability/hit rate,actual token/visual-token use and end-to-end
  time.Include the shared prefix cost;do not count it as free compute.

Resample whole chart identities with paired seeds retained inside each chart.
Determine confirmatory sample size from development variance before test access.
The128-chart candidate pool is not automatically powered for a small effect.
Freeze confidence and material-gain/harm thresholds before testing.

## Decisions

- INVALID_STOP:leakage,source/quality/isolation failure or unmatched budgets.
- NO_GO:adequately powered evidence shows no useful net advantage over G-V or
  resampling;do not rescue the thesis by more system packaging.
- INCONCLUSIVE:too few qualified errors,wide intervals or unresolved annotations.
  Preserve the uncertainty;do not call it a negative mechanism proof or a GO.
- CONDITIONAL_RESEARCH_ONLY:positive controlled pilot evidence warrants a
  separately frozen larger study;it does not establish novelty or GPU efficiency.

Using oracle error labels only,or benefitting only from extra sampling,is not a
deployable Repair Memory result.Image-disjoint tests support only cross-image
claims;cross-template/source claims require an additional audited grouping.
