# Direct HWP Extraction: Skill + Prompt Set

## What we are optimizing for
- Final target is **direct HWP extraction**.
- `today_major_economy/` is the **oracle/reference target**, not the intended long-term generation path.
- The harness should remain the judge.
- The converter should move from:
  - `HWP -> extracted IR`
  - `IR -> editable HTML/CSS/payload`
  - `generated output -> compare against oracle`

---

## Recommended sequence

### Phase A — Extraction strategy sanity check (optional but smart)
- **Prompt role:** `dependency-expert`
- **When to use:** when we still need to choose the actual HWP parsing approach/toolchain safely
- **Why:** direct HWP extraction can go sideways fast if we choose a weak parser or an opaque dependency path

#### Recommended dependency-expert prompt
```text
Evaluate the best practical approach for direct HWP extraction for this repository.

Context:
- Final target is direct HWP extraction, not reference-runtime reuse.
- The oracle/reference bundle is today_major_economy/.
- Initial scope is a single sample file: 260121 일일 주요경제지표.hwp
- Expected output is editable HTML with semantic/table bindings and high fidelity.
- Current implementation language and scripts are Python-first.
- We prefer the smallest dependency surface that can reliably expose document structure needed for tables, text runs, and style information.

Need from you:
1. Recommend the strongest approach for extracting structure from HWP for a Python-oriented pipeline.
2. Compare 2-3 viable approaches if they exist.
3. Call out maintenance, practicality, license, and fidelity risks.
4. Tell us whether to use a library, a converter bridge, or an intermediate-format path.
5. Keep the answer action-oriented for immediate implementation follow-up.
```

---

### Phase B — Real extractor implementation
- **Skill:** `$team`
- **Mode:** `team ralph`
- **Worker prompt:** `team-executor`
- **Why:** this is now real implementation work with multiple bounded lanes, and we want the Ralph verification loop attached from the start

#### Recommended launch command
```bash
omx team ralph 3:team-executor "Build the first true direct-HWP extraction pipeline for the sample 260121 일일 주요경제지표.hwp. Use today_major_economy/ as the oracle/reference target and keep the current harness as the judge. Replace reference-copy generation with HWP -> IR -> editable HTML generation for the sample, while preserving runtime contract verification and regression reporting."
```

#### Recommended team-executor prompt
```text
Build the first true direct-HWP extraction pipeline for the sample 260121 일일 주요경제지표.hwp.

Ground truth:
- Final target is direct HWP extraction.
- today_major_economy/ is the successful reference bundle and should be treated as the oracle target.
- Current harness and run pipeline are useful and should remain as the evaluation loop.
- Reference-runtime reuse was only a bootstrap baseline and should not be the final generation strategy.

Mission:
Implement the first extraction-driven path for the sample document so the pipeline can move toward:
1. HWP -> extracted IR
2. IR -> editable HTML/CSS/payload
3. Generated result -> validated by the existing harness

Required outcomes:
1. Define the minimum IR/schema needed for this sample.
2. Add the first direct extraction stage from the HWP into that IR.
3. Add or adapt the renderer so generated output is driven by extracted IR rather than by copying the reference bundle into generated output.
4. Preserve the current runtime contract checks and run artifact reporting.
5. Measure extraction coverage against the oracle artifacts, especially extracted_fields.json and table/semantic bindings.

Constraints:
- Keep scope to the single sample HWP.
- Do not widen into generic multi-format support yet.
- Do not regress the harness truthfulness we already established.
- Preserve editability and binding structure as first-class requirements.
- Keep diffs tight and reversible.
- You are not alone in the codebase; coordinate and do not revert other lanes.

Suggested lane split:
- Lane 1: oracle schema + IR contract
- Lane 2: HWP direct extraction into IR
- Lane 3: IR-driven renderer + harness wiring

Definition of done:
- A direct extraction path exists for the sample HWP.
- The pipeline no longer depends on copying the oracle reference bundle as the primary generation method.
- A fresh run produces generated output from extracted structure.
- Runtime contract verification still works.
- Coverage or mismatch against the oracle is reported concretely.
```

---

### Phase C — Proof that direct extraction is real
- **Prompt role:** `verifier`
- **Why:** we need to prove that the generated artifact is coming from extracted HWP structure, not disguised reference reuse

#### Recommended verifier prompt
```text
Verify that the current sample pipeline performs true direct HWP extraction rather than reference-copy generation.

What must be proven:
1. The pipeline reads 260121 일일 주요경제지표.hwp and produces extracted intermediate structure.
2. Generated HTML/CSS/payload are derived from extracted IR, not primarily from copying today_major_economy/ into generated output.
3. Runtime contract verification still passes or any remaining gap is explicitly documented.
4. The output preserves editable/runtime binding requirements.
5. The run artifacts make oracle comparison possible.

Evidence targets:
- extraction-stage scripts and outputs
- renderer/generation scripts and outputs
- latest run_status.json
- latest runtime_contract_verification.json
- any IR JSON/schema artifacts introduced for the sample

Output format:
- Verdict: PASS / FAIL / PARTIAL
- Evidence: commands, files, and artifacts
- Gaps: what is still not truly extraction-driven
- Risks: next blockers to reach oracle-level fidelity
```

---

### Phase D — Later fidelity tuning
- **Skill:** `$visual-verdict`
- **Support prompt:** `team-executor` or `executor`
- **Use only after:** real capture/reference images are available and the extraction-driven path is actually producing generated pages

#### Recommended visual-verdict prompt
```text
reference_images:
- harness/samples/260121-major-economy/capture/page-1-reference.png

generated_screenshot:
- harness/artifacts/260121-major-economy/runs/<run-id>/review/generated-page-1.png

category_hint: document-report

Return JSON only.
Focus on:
- title box placement
- summary table geometry
- dense table spacing
- typography and letter-spacing fidelity
- whether the page still matches the overall identity of the reference economic report
```

---

## Simple recommendation
### If you want the single best next move right now
- **Skill:** `$team`
- **Prompt:** `team-executor`
- **Mode:** `team ralph`
- **Reason:** we are now building the real HWP direct-extraction path, not just tuning the harness

### If you want the lowest-risk setup
1. `dependency-expert`
2. `$team` + `team-executor`
3. `verifier`
4. later `$visual-verdict`

## One-line cheat sheet
- **Need to choose extraction approach first?** → `dependency-expert`
- **Need to build the real direct extractor?** → `$team` + `team-executor`
- **Need to prove it's truly extraction-driven?** → `verifier`
- **Need to tune UI fidelity after that?** → `$visual-verdict`
