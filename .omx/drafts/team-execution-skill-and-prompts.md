# Team Execution Skill + Prompt Draft

## Recommendation

### Primary skill
- **Use:** `$team`
- **Why:** this phase is no longer pure planning; it has clear parallel lanes with bounded ownership (case skeleton, manifest/run contract, evaluator contract, verification).

### Worker role prompt
- **Use:** `team-executor`
- **Why:** conservative supervised delivery fits the current kickoff better than fully autonomous executor fanout.

### Verification role prompt
- **Use:** `verifier`
- **Why:** we need explicit proof that the kickoff contract was actually established, not just claimed.

### Optional linked follow-up
- **Use:** `team ralph`
- **Why:** good when you want team delivery first and Ralph to keep the verification/fix loop running until the kickoff slice is genuinely complete.

## Recommended default launch

```bash
omx team ralph 3:team-executor "Build the first golden-case harness kickoff for the current HWP sample using .omx/plans/document-conversion-harness-roadmap.md and .omx/plans/document-conversion-harness-kickoff.md as the source of truth."
```

## Recommended lane split

### Lane 1 — Case skeleton + manifest
**Ownership:**
- `cases/golden/daily-economic-indicators/**`
- any minimal loader/helper needed to resolve the case manifest

**Goal:**
- establish the golden-case directory
- place source/reference assets safely
- create and validate the manifest contract

### Lane 2 — Run/report contract
**Ownership:**
- generated run directory contract
- report/output naming contract
- metadata describing run artifacts

**Goal:**
- define where generated HTML, reports, diffs, and metadata land per run
- keep outputs deterministic and regression-friendly

### Lane 3 — Evaluator scaffold + verification
**Ownership:**
- evaluator contract implementation scaffold
- structural/editability/visual report placeholders or first checks
- verification of kickoff completeness

**Goal:**
- prove the harness can evaluate the three quality axes
- report what is implemented vs placeholder vs missing

## Leader launch prompt

Use this as the task text for the team launch:

```text
Implement the first execution slice of the document-conversion harness for this repo.

Context:
- Source plan: .omx/plans/document-conversion-harness-roadmap.md
- Kickoff handoff: .omx/plans/document-conversion-harness-kickoff.md
- Current reference assets live under today_major_economy/
- Source document is 260121 일일 주요경제지표.hwp

Mission:
Build the first golden-case harness scaffold so this repository can treat the current HWP sample as a repeatable baseline case.

Required outcomes:
1. Introduce a canonical golden-case structure for the current sample.
2. Preserve the existing today_major_economy/ artifacts as untouched baseline input.
3. Create a manifest/run/report/evaluator contract that future conversion runs can target.
4. Verify the kickoff slice with concrete artifact evidence.

Lane guidance:
- Lane 1: case skeleton + source/reference asset placement + manifest
- Lane 2: run/output/report contract
- Lane 3: evaluator scaffold + kickoff verification

Constraints:
- Keep diffs small and reversible.
- Reuse existing artifacts; do not redesign the whole system.
- Do not widen into full multi-format support.
- Maintain editability as a first-class quality axis, not only visual fidelity.
- If a shared file must be touched, coordinate carefully and avoid overwriting another lane's work.

Definition of done:
- There is a canonical case for the current sample.
- The manifest resolves source/reference assets.
- The run/report contract is explicit.
- Evaluator coverage for visual/structural/editability is represented in code or contract files.
- Verification evidence names the created artifacts and any remaining gaps.
```

## Worker prompt templates

### Prompt for Lane 1 — team-executor
```text
You own Lane 1: golden-case skeleton + manifest.

Files/areas you may own:
- cases/golden/daily-economic-indicators/**
- minimal adjacent manifest-loading code only if required for correctness

Task:
- Create the canonical case structure for the current HWP sample.
- Copy or reference the current source/reference artifacts safely.
- Add the first case manifest so source, HTML/CSS, tokens, fonts, and extracted field mappings are resolvable.

Guardrails:
- You are not alone in the codebase; do not revert edits made by other lanes.
- Keep ownership tight to case structure and manifest.
- Preserve today_major_economy/ as baseline input; do not mutate it.

Verification:
- Prove the case exists.
- Prove the manifest resolves the expected assets.
- Report exact files changed and commands run.
```

### Prompt for Lane 2 — team-executor
```text
You own Lane 2: run/output/report contract.

Files/areas you may own:
- generated output contract files
- report directory conventions
- metadata that defines per-run outputs
- narrow adjacent helper code only if required

Task:
- Define how each harness run stores generated output, reports, diffs, and metadata.
- Make the layout deterministic enough for future regression runs.
- Keep the design aligned with .omx/plans/document-conversion-harness-kickoff.md.

Guardrails:
- You are not alone in the codebase; do not revert edits made by other lanes.
- Do not implement full evaluator logic unless needed for the contract.
- Prefer simple, explicit structures over abstractions.

Verification:
- Show the run/output/report contract artifacts.
- Show how a future run would write outputs.
- Report exact files changed and commands run.
```

### Prompt for Lane 3 — team-executor
```text
You own Lane 3: evaluator scaffold + kickoff verification.

Files/areas you may own:
- evaluator contract/scaffold files
- verification/report scaffolding
- minimal checks for visual/structural/editability evidence

Task:
- Establish the first evaluator scaffold for the golden case.
- Ensure visual fidelity, structural fidelity, and editability are each represented.
- Verify the kickoff slice and clearly separate implemented checks from placeholders.

Guardrails:
- You are not alone in the codebase; do not revert edits made by other lanes.
- Keep scope on kickoff proof, not full fidelity tuning.
- Missing automation is acceptable only if the gap is made explicit and testable.

Verification:
- Show where each of the three quality axes is captured.
- Show the artifact/report path a verifier can inspect.
- Report exact files changed and commands run.
```

## Final verifier prompt

Use this after the team claims completion:

```text
Verify the kickoff slice for the document-conversion harness.

What must be proven:
1. A canonical golden case exists for the current HWP sample.
2. Existing today_major_economy/ artifacts remain usable as untouched baseline input.
3. A manifest resolves source/reference HTML/CSS/tokens/fonts/field mappings.
4. A run/report contract exists for future generated outputs.
5. Visual fidelity, structural fidelity, and editability are each represented in the evaluator scaffold or contract.

Evidence targets:
- .omx/plans/document-conversion-harness-roadmap.md
- .omx/plans/document-conversion-harness-kickoff.md
- new case files under cases/golden/daily-economic-indicators/
- any runner/evaluator/report contract files introduced by the team

Output format:
- Verdict: PASS / FAIL / PARTIAL
- Evidence: file paths and commands
- Gaps: what is still missing
- Risks: what could block the next execution slice
```

## Practical recommendation
- **Start with:** `$team`
- **Worker role:** `team-executor`
- **Finish with:** `verifier`
- **Best default command:** `omx team ralph 3:team-executor "..."`

Reason: we want supervised parallel delivery now, and a persistent verification/fix loop right after, without jumping prematurely into document-specific fidelity tuning.
