# Initial Consensus Plan: Sample HWP Editable HTML Harness

## Requirements Summary

Milestone 1 is one sample only: `260121 일일 주요경제지표.hwp` must produce editable HTML with fidelity at least as strong as `today_major_economy/`. The plan uses the existing reference HTML/CSS/fonts and `extracted_fields.json` as baselines, keeps `today_major_economy/` immutable, and treats original-document capture as a required input because no local HWP render/capture toolchain exists.

## RALPLAN-DR

### Principles

1. Fidelity to the original sample and reference bundle comes first.
2. Output must remain genuinely editable HTML, not an image-backed approximation.
3. Reuse existing style and field knowledge before introducing new abstractions.
4. Keep milestone 1 sample-scoped, reversible, and artifact-rich.
5. Do not depend on new packages or missing desktop binaries for the first pass.

### Decision Drivers

1. Reach a credible one-sample result quickly with the current environment.
2. Preserve a repeatable artifact trail for later refinement and reuse.
3. Avoid stalling on unavailable `.hwp` rendering/conversion tools.

### Viable Options

#### Option A: Python-first sample harness with capture-backed refinement

Pros: works with current `python3`; fits manifest, artifact, JSON verification, and run-history tasks; avoids blocking on missing office/image tools.  
Cons: does not solve HWP rendering by itself; can become sample-specific if the artifact contract is weak.

#### Option B: Node-first sample harness

Pros: better future path for browser-based rendering checks and DOM inspection; can later absorb richer review tooling.  
Cons: adds complexity now without solving missing HWP capture; lower immediate leverage than Python for artifact orchestration.

#### Option C: Manual HTML clone only

Pros: fastest visible output.  
Cons: weak harness value; poor repeatability, review trace, and future reuse.

### Recommendation

Choose Option A. Frame it as a sample harness around known inputs, not as a generic `.hwp` parser. Defer parser-first extraction and browser-diff automation until the sample contract, capture flow, and review loop are stable.

## Concrete Implementation Steps

1. Define the sample contract.
Create `harness/samples/260121-major-economy/sample.manifest.json`, `harness/samples/260121-major-economy/README.md`, and `harness/artifacts/260121-major-economy/runs/.gitkeep`.

2. Add capture ingest and frozen reference normalization.
Create `scripts/ingest_source_capture.py` and `scripts/normalize_reference.py` to place source captures plus a normalized snapshot of `today_major_economy/` under `harness/artifacts/260121-major-economy/runs/<run-id>/`.

3. Build the first editable-output path.
Create `scripts/build_editable_html.py`, `harness/templates/editable-document.html`, `harness/templates/editable-common.css`, and `harness/templates/editable-fit.css`. Reuse `today_major_economy/assets/fonts/` and `today_major_economy/extracted_fields.json` as baseline inputs.

4. Add verification and review artifacts.
Create `scripts/verify_fields.py`, `scripts/build_review_bundle.py`, `harness/review/visual-checklist.md`, and per-run `review/` output capturing field parity, editability smoke results, and review notes.

5. Add one manifest-driven entrypoint and history.
Create `scripts/run_sample.py`, `harness/RUNBOOK.md`, and `harness/history/260121-major-economy.md` so each iteration runs ingest -> normalize -> build -> verify -> review into a fresh `run-id`.

## Acceptance Criteria

1. One command can run the sample workflow end to end from the manifest.
2. Each run writes a new artifact directory and preserves prior evidence.
3. Generated output is editable HTML/CSS/assets and does not mutate `today_major_economy/`.
4. Required semantic and table-mapped values from `today_major_economy/extracted_fields.json` are present in output or explicitly failed.
5. A reviewer can compare source captures, generated output, and the frozen reference from one review bundle.
6. User review judges the sample at least `today_major_economy` quality with no major regression in tables, headers, fonts, spacing, or editability.

## Risks / Mitigations

- No automated capture tool is available.
Mitigation: make manual or externally produced capture ingestion a first-class artifact contract.

- The harness could overfit the reference bundle.
Mitigation: keep a manifest, normalized artifacts, and per-run evidence so the contract survives future generator replacement.

- Visual fidelity could improve while editability regresses.
Mitigation: include explicit editability smoke checks in verification.

- Font/render variance could distort review outcomes.
Mitigation: reuse bundled fonts and record render assumptions in run metadata.

## Verification Steps

1. Validate manifest paths for the sample HWP, reference HTML/CSS/assets, and output locations.
2. Run `python3 scripts/run_sample.py --sample harness/samples/260121-major-economy/sample.manifest.json`.
3. Confirm a unique `run-id` directory is created without overwriting prior runs.
4. Confirm source captures, normalized reference files, output HTML/CSS, and review artifacts exist in that run.
5. Run field verification and fail on missing required mapped values.
6. Perform manual review against source captures and `today_major_economy/`.

## ADR Seed

Decision: use a reference-first, Python-led sample harness for milestone 1.

Drivers: current environment lacks HWP render tooling; the repo already contains a strong reference bundle; the first priority is one working sample before generalization.

Alternatives considered: Node-first sample harness, manual HTML clone only, parser-first HWP-to-IR pipeline.

Why chosen: best balance of immediate fidelity, repeatable artifacts, and low dependency risk.

Consequences: milestone 1 is intentionally sample-biased and capture-backed; broader parser/generalization work moves to later milestones.

Follow-ups: after the sample passes, decide whether the next investment is parser-first IR work or automated capture tooling.

## Available Agent Types And Staffing Guidance

Available agent types: `planner`, `architect`, `critic`, `executor`, `verifier`, `test-engineer`, `researcher`, `writer`, `explore`.

Recommended later staffing:
- `executor` (medium): implement manifest, scripts, templates, and run loop.
- `verifier` (medium): validate artifact layout, baseline immutability, and evidence completeness.
- `test-engineer` (medium): harden manifest/path/run-id and field-parity checks.
- `architect` (high, checkpoint): review whether sample-specific structure remains contained.

Launch guidance:
- `ralph` if one agent should carry the sample milestone sequentially with verification after each stage.
- `team` if splitting into lanes: ingestion/manifest, generator/templates, verification/review bundle.

Team -> ralph verification path:
Use `team` to build the lanes, then hand the integrated branch to `ralph` for final run-through, evidence review, and acceptance verification.
