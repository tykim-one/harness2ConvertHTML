# Follow-up Team Fix Prompts

## Goal
Fix the current kickoff run so the sample harness passes the narrow runtime-verification gate without widening scope into full fidelity tuning.

## Current failure evidence
- Failing run: `harness/artifacts/260121-major-economy/runs/20260322T065802Z`
- Run status: `harness/artifacts/260121-major-economy/runs/20260322T065802Z/metadata/run_status.json`
- Runtime verification report: `harness/artifacts/260121-major-economy/runs/20260322T065802Z/metadata/runtime_contract_verification.json`
- Relevant sample manifest: `harness/samples/260121-major-economy/sample.manifest.json`

## Proven issues to fix
1. Runtime verification fails because generated HTML references missing font assets:
   - `assets/fonts/HumanMyeongjo.woff2`
   - `assets/fonts/HCIPoppy.woff2`
2. Capture gate likely treats `.gitkeep` as a real capture artifact, causing a false `review-ready` status.

## Recommended launch command
```bash
omx team ralph 3:team-executor "Fix the current milestone-1 harness kickoff for the HWP sample. Use harness/artifacts/260121-major-economy/runs/20260322T065802Z/metadata/runtime_contract_verification.json and run_status.json as the failure truth. Keep scope narrow: fix missing-font handling and capture-gate false positives, then rerun python3 scripts/run_sample.py --sample harness/samples/260121-major-economy/sample.manifest.json until runtime verification passes or remaining gaps are explicitly proven." 
```

## Leader launch prompt
```text
Fix the current milestone-1 harness kickoff for the HWP sample.

Ground truth:
- Failing run: harness/artifacts/260121-major-economy/runs/20260322T065802Z
- Runtime verification report: harness/artifacts/260121-major-economy/runs/20260322T065802Z/metadata/runtime_contract_verification.json
- Run status: harness/artifacts/260121-major-economy/runs/20260322T065802Z/metadata/run_status.json
- Sample manifest: harness/samples/260121-major-economy/sample.manifest.json
- Main runner: scripts/run_sample.py

What is already true:
- The golden-case harness scaffold exists.
- Reference immutability already passes.
- The failure is now narrow and should stay narrow.

Required fixes:
1. Resolve runtime verification failure caused by missing font assets referenced by the generated HTML.
2. Fix capture-gate logic so placeholder files like .gitkeep do not count as real capture assets.
3. Rerun the sample pipeline and update the result so review status and pass/fail state reflect reality.

Constraints:
- Do not redesign the harness.
- Do not widen into full visual-fidelity tuning.
- Preserve non-destructive reference handling.
- Keep diffs small and reversible.
- You are not alone in the codebase; coordinate and do not revert another lane's work.

Definition of done:
- Missing-font handling is corrected or downgraded in a principled, explicit way.
- Capture gate no longer treats .gitkeep or equivalent placeholders as real capture evidence.
- A fresh run of python3 scripts/run_sample.py --sample harness/samples/260121-major-economy/sample.manifest.json is produced.
- The fresh run status truthfully reports review eligibility and runtime verification result.
- Final evidence names changed files, commands run, and any remaining gaps.
```

## Lane split

### Lane 1 — Font handling
```text
You own Lane 1: missing-font handling.

Ground truth:
- harness/artifacts/260121-major-economy/runs/20260322T065802Z/metadata/runtime_contract_verification.json

Task:
- Find why generated HTML references HumanMyeongjo.woff2 and HCIPoppy.woff2 even though those assets are not present in the current frozen reference runtime.
- Implement the smallest correct fix so runtime verification reflects a sound contract.

Acceptable solutions:
- copy/resolve the required assets if they exist in the intended source of truth, or
- stop emitting references to unavailable fonts when that is the intended contract, or
- explicitly adjust verification/runtime generation only if the contract should permit these missing assets.

Guardrails:
- Keep scope tight to font handling.
- Do not silently weaken verification without a principled reason grounded in the current sample contract.
- You are not alone in the codebase; do not revert other lanes.

Verification:
- Show the relevant changed files.
- Show how the missing-font condition is resolved or intentionally reclassified.
- Report exact commands run.
```

### Lane 2 — Capture gate / review status
```text
You own Lane 2: capture-gate truthfulness.

Ground truth:
- harness/samples/260121-major-economy/capture/.gitkeep
- harness/artifacts/260121-major-economy/runs/20260322T065802Z/metadata/run_status.json
- scripts/run_sample.py

Task:
- Fix the capture-pack detection logic so placeholder files like .gitkeep do not count as real capture evidence.
- Ensure review status becomes truthful: if no real captures exist, the run should be review-blocked rather than review-ready.

Guardrails:
- Keep scope tight to capture detection and run status truthfulness.
- Do not redesign the review system.
- You are not alone in the codebase; do not revert other lanes.

Verification:
- Prove .gitkeep-only state no longer reports review-ready.
- Report exact files changed and commands run.
```

### Lane 3 — Re-run + verification evidence
```text
You own Lane 3: fresh rerun and proof.

Ground truth:
- scripts/run_sample.py
- harness/samples/260121-major-economy/sample.manifest.json
- latest failing run under harness/artifacts/260121-major-economy/runs/20260322T065802Z

Task:
- After the narrow fixes land, rerun the sample pipeline.
- Collect the new run id, run_status.json, runtime_contract_verification.json, and any review summary artifacts.
- Report whether the kickoff slice now passes, partially passes, or still fails, with concrete reasons.

Guardrails:
- Focus on proof, not speculative extra fixes.
- If a remaining failure exists, isolate it precisely.
- You are not alone in the codebase; do not revert other lanes.

Verification:
- Report the new run directory.
- Report PASS/FAIL/PARTIAL with exact artifact paths.
- Report commands run.
```

## Final verifier prompt
```text
Verify the narrow follow-up fix for the HWP harness kickoff.

What must be proven:
1. The missing-font failure from harness/artifacts/260121-major-economy/runs/20260322T065802Z/metadata/runtime_contract_verification.json is resolved or intentionally reclassified with a principled contract change.
2. Placeholder files like .gitkeep no longer cause false review-ready status.
3. A fresh run of python3 scripts/run_sample.py --sample harness/samples/260121-major-economy/sample.manifest.json was executed.
4. The new run_status.json truthfully reports review eligibility and runtime verification state.
5. Reference immutability still holds.

Evidence targets:
- scripts/run_sample.py
- scripts/verify_runtime_contract.py
- any helper files changed for font handling or capture detection
- newest run directory under harness/artifacts/260121-major-economy/runs/

Output format:
- Verdict: PASS / FAIL / PARTIAL
- Evidence: file paths and commands
- Gaps: any unresolved failure
- Risks: what should be tackled next, if anything
```

## Practical note
Use this as a **narrow fix-pass**, not a new feature sprint. The goal is to turn the existing kickoff scaffold into an honest, green-or-explicitly-blocked baseline.
