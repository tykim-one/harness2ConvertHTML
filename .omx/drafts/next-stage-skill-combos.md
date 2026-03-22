# Next-Stage Skill Combos

## Current baseline
- Harness pipeline is green at the runtime-contract level.
- Current fresh run: `harness/artifacts/260121-major-economy/runs/20260322T071228Z`
- Current status: `conversion-only / review-blocked`
- Reason acceptance is blocked: no real capture images yet.

## Recommendation in one line
Use **`$team` to make the sample visually reviewable**, then use **`$visual-verdict` as the authoritative iteration gate**, and finish with **`verifier`**.

---

## Phase 1 — Make the sample review-ready

### Recommended skill combo
- **Skill:** `$team`
- **Mode:** `team ralph`
- **Worker prompt:** `team-executor`
- **Optional support:** `$note`

### Why
The pipeline works, but the sample is still blocked on real capture evidence. This is a bounded implementation pass that may touch capture ingestion, rendering hooks, or review artifact plumbing.

### Use when
- you want to ingest real screenshots/captures into the harness
- you want each run to become visually reviewable instead of `review-blocked`

### Recommended prompt
```text
Make the 260121-major-economy sample review-ready.

Ground truth:
- Current green pipeline run: harness/artifacts/260121-major-economy/runs/20260322T071228Z
- Current status is conversion-only / review-blocked because no real capture assets exist
- Sample capture directory: harness/samples/260121-major-economy/capture/
- Visual review checklist: harness/review/visual-checklist.md

Task:
- Add the smallest correct mechanism to make this sample visually reviewable.
- If capture images can be generated or ingested inside the repo flow, wire that path in.
- If full automatic capture generation is not feasible under current constraints, make the capture contract explicit and keep the run truthfully blocked until real captures are provided.
- Preserve the existing green runtime-contract baseline.

Definition of done:
- A fresh run is either truly review-ready with real capture assets, or explicitly and honestly blocked with a documented capture contract.
- The run/report artifacts make it obvious what images are compared.
- No regression to runtime_contract_passed or reference_immutable_passed.
```

### Recommended command
```bash
omx team ralph 3:team-executor "Make the 260121-major-economy sample review-ready. Use harness/artifacts/260121-major-economy/runs/20260322T071228Z as the current baseline. Keep scope narrow: add or formalize real capture ingestion/render evidence, preserve the green runtime-contract pipeline, and rerun python3 scripts/run_sample.py --sample harness/samples/260121-major-economy/sample.manifest.json to produce a truthful review-ready-or-explicitly-blocked result."
```

---

## Phase 2 — Visual fidelity iteration

### Recommended skill combo
- **Skill:** `$visual-verdict`
- **Execution support:** `$team` or direct `executor`
- **Worker prompt:** `team-executor` for parallel fixes, `executor` for single-lane fixes
- **Closeout:** `verifier`

### Why
Once real reference images exist, visual tuning should no longer be subjective. `$visual-verdict` gives a deterministic JSON verdict and should become the gate before the next edit.

### Use when
- you have at least one real reference image and one generated screenshot
- you need to iteratively improve spacing, typography, table geometry, or styling fidelity

### Visual-verdict prompt template
```text
reference_images:
- harness/samples/260121-major-economy/capture/page-1-reference.png

generated_screenshot:
- harness/artifacts/260121-major-economy/runs/<run-id>/review/generated-page-1.png

category_hint: document-report

Return JSON only.
Focus on:
- top title box alignment
- summary table geometry
- market table column widths and row heights
- typography / letter spacing drift
- whether the overall page still looks like the same Korean economic report
```

### How to operate the loop
1. Run the sample pipeline.
2. Produce/update generated screenshot.
3. Run `$visual-verdict`.
4. If score < 90, edit only the next highest-impact mismatch.
5. Rerun the sample.
6. Run `$visual-verdict` again.
7. Repeat until 90+ or a hard blocker is identified.

### Recommended fix prompt after a verdict
```text
Use the latest $visual-verdict JSON as the source of truth.
Implement only the next highest-impact visual fix for the 260121-major-economy sample.
Preserve semantic/table bindings and editability.
Do not broaden scope beyond the mismatches named in the verdict.
After the edit, rerun the sample pipeline and produce the next generated screenshot for another $visual-verdict pass.
```

---

## Phase 3 — Acceptance proof

### Recommended skill combo
- **Prompt:** `verifier`
- **Optional skill:** `$note`
- **Shutdown/cleanup:** `$cancel`

### Why
At the end, we need proof that the result is not only visually close, but also still editable and structurally faithful.

### Final verifier prompt
```text
Verify the 260121-major-economy sample for milestone-1 acceptance.

What must be proven:
1. The latest run is review-ready with real capture evidence.
2. Runtime contract still passes.
3. Reference immutability still passes.
4. Visual review artifacts exist for reference vs generated output.
5. The latest visual-verdict score is at least 90, or the remaining blocker is explicitly documented.
6. Editability and semantic/table binding are still intact.

Evidence targets:
- latest run_status.json
- latest runtime_contract_verification.json
- latest reference_immutability.json
- latest review artifacts and screenshots
- latest visual-verdict JSON
```

---

## Practical recommendation by moment

### Right now
- **Use:** `$team`
- **Prompt:** `team-executor`
- **Goal:** move from `review-blocked` to `review-ready`

### As soon as real captures exist
- **Use:** `$visual-verdict`
- **Prompt support:** `team-executor` or `executor`
- **Goal:** iterative fidelity tuning

### When you think it is done
- **Use:** `verifier`
- **Then:** `$cancel`
- **Goal:** prove acceptance, then cleanly end the mode

## Simple cheat sheet
- **No capture yet?** → `$team` + `team-executor`
- **Capture exists, tuning fidelity?** → `$visual-verdict` + `team-executor`
- **Need final proof?** → `verifier`
