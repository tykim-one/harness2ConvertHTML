# Revised Consensus Plan: HWP Editable HTML Harness

## Requirements Summary

Milestone 1 remains one sample only: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/260121 일일 주요경제지표.hwp` must produce editable HTML with fidelity at least as strong as `today_major_economy/`, while preserving the existing semantic/table addressing and editable runtime behavior already present in the reference bundle. `today_major_economy/` is canonical input evidence and must remain immutable.

## RALPLAN-DR

### Principles

1. Reuse the frozen reference runtime before inventing new HTML/CSS architecture.
2. Preserve editability, semantic/table addressing, and export behavior together.
3. Keep milestone 1 sample-scoped, artifact-rich, and reversible.
4. Freeze canonical references; extract metadata from them, never normalize by rewriting them.
5. Prefer Python orchestration because `python3` is available and no local office/image conversion binaries exist in `PATH`.

### Decision Drivers

1. Fastest credible path to a one-sample result is reusing the working HTML/CSS/runtime already in `today_major_economy/`.
2. Verification must prove behavior, not just copied values: semantic hooks, table hooks, runtime API, export JSON, and bundled fonts must survive.
3. Missing local HWP render/capture tooling means the harness must treat capture input as an explicit external artifact, not an assumed local step.

### Options

#### Option A: Frozen reference-runtime reuse + Python orchestration

Use Python scripts to freeze/copy the existing reference HTML/CSS/font/runtime contract into per-run artifacts, inject sample-specific data through the existing editable runtime hooks, and verify behavior.

Pros:
- Directly exploits proven runtime hooks and bundled font faces already in `today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.html`
- Avoids milestone-1 template authoring risk
- Fits current environment: `python3` available, no dependency on missing office/image binaries

Cons:
- Intentionally sample-biased
- Generalization to other layouts is deferred

#### Option B: Parser-first IR pipeline

Parse HWP into a new canonical intermediate representation and generate milestone-1 HTML/CSS from that IR.

Pros:
- Better long-term abstraction boundary
- Cleaner path to multi-format support later

Cons:
- Stronger architecture, but weaker milestone-1 leverage
- Does not use the already-proven editable runtime contract
- Higher risk without local HWP conversion/render tooling

#### Option C: HTML/CSS rebuild from scratch

Author new canonical templates and recreate the page structure independently of the existing reference runtime.

Pros:
- Full control over generated markup
- Potentially cleaner long-term ownership if reuse proved insufficient

Cons:
- Not justified by current evidence
- Highest fidelity regression risk for milestone 1
- Reimplements behavior already present in the reference bundle

## Recommendation

Choose Option A. Keep Python as the orchestration layer, but do not author new canonical HTML/CSS templates for milestone 1. Template/rebuild work is deferred unless runtime reuse is proven insufficient by verification evidence.

## Manifest / Runtime Contract

Create and treat the following as the explicit sample contract:

- `harness/samples/260121-major-economy/sample.manifest.json`
- `harness/samples/260121-major-economy/README.md`
- `harness/artifacts/260121-major-economy/runs/.gitkeep`

The manifest must declare:

- Source HWP: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/260121 일일 주요경제지표.hwp`
- Canonical reference HTML: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.html`
- Canonical shared CSS: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_common.css`
- Canonical fit CSS: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.css`
- Canonical field mapping: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/extracted_fields.json`
- Canonical token metadata if needed: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_fidelity_fit_headerfix_tokens.json`
- Canonical font asset root: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/assets/fonts/`
- Required runtime hooks to preserve:
  - `window.DailyIndicatorsTemplate`
  - `window.applyDailyIndicatorsData`
  - `.editable-block`
  - `data-semantic-field`
  - `data-table-field`
  - `data-table-id`
  - `#runtime-font-faces`
  - `collectState()` JSON export path
- Allowed mutations:
  - per-run copied HTML/CSS/assets under `harness/artifacts/260121-major-economy/runs/<run-id>/`
  - injected payload/state JSON
  - per-run review metadata and capture pack references
- Forbidden mutations:
  - any write to `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/`
- Capture pack input:
  - externally produced original-document screenshots/PDF/images plus metadata placed under `harness/artifacts/260121-major-economy/runs/<run-id>/capture/`

## Concrete Implementation Steps

1. Define the frozen sample contract.
Create `harness/samples/260121-major-economy/sample.manifest.json` and `harness/samples/260121-major-economy/README.md` with the explicit paths and runtime contract above.

Acceptance criteria:
- The manifest resolves every canonical reference path, font root, mapping source, and capture pack location.
- The manifest states allowed and forbidden mutations explicitly.

2. Replace normalization with freeze/copy + metadata extraction.
Create `scripts/freeze_reference_runtime.py` and `scripts/extract_reference_metadata.py`. These scripts copy the canonical HTML/CSS/font bundle into `harness/artifacts/260121-major-economy/runs/<run-id>/reference/` and emit extracted metadata only; they must not rewrite canonical files.

Acceptance criteria:
- A run creates a frozen copy of the reference bundle under `runs/<run-id>/reference/`.
- Metadata extraction reports runtime hooks, linked CSS files, font-face paths, and field/table coverage.
- File hashes for `today_major_economy/` are unchanged before and after the run.

3. Build the milestone-1 runtime-reuse orchestration.
Create `scripts/build_editable_html.py` and `scripts/run_sample.py`. These scripts must start from the frozen copied reference runtime, inject sample-specific payload/state, and emit generated output under `runs/<run-id>/generated/` without introducing new canonical templates.

Acceptance criteria:
- Generated HTML still exposes `window.DailyIndicatorsTemplate`, `window.applyDailyIndicatorsData`, and exportable `collectState()` behavior.
- `data-semantic-field`, `data-table-field`, and `data-table-id` addressing remain intact for required mapped blocks/cells.
- The generated bundle resolves fonts from copied `assets/fonts/`.

4. Add behavior-first verification and review artifacts.
Create `scripts/verify_runtime_contract.py`, `scripts/verify_reference_immutable.py`, `scripts/build_review_bundle.py`, `harness/review/visual-checklist.md`, and `harness/RUNBOOK.md`.

Acceptance criteria:
- Verification fails on missing `data-semantic-field`, missing `data-table-field`, missing runtime API, broken JSON export, unresolved copied font paths, or writes into `today_major_economy/`.
- Review bundle includes capture pack inputs, frozen reference copy, generated output, verification results, and run metadata in one run directory.

## Tight Acceptance Criteria

1. One command runs the sample manifest end to end and produces a new `run-id` under `harness/artifacts/260121-major-economy/runs/`.
2. The workflow preserves semantic/table addressing from `today_major_economy/extracted_fields.json`, not merely the visible values.
3. The generated output preserves editable runtime behavior: edit mode toggle, field application path, runtime font injection path, and JSON export via `collectState()`.
4. Bundled fonts resolve from the copied artifact bundle with no dependency on external office/image binaries.
5. `today_major_economy/` remains byte-for-byte unchanged throughout the run.
6. The review bundle is sufficient for manual fidelity review against the capture pack and frozen reference.

## Verification Steps

1. Run `python3 scripts/run_sample.py --sample harness/samples/260121-major-economy/sample.manifest.json`.
2. Check `runs/<run-id>/reference/` contains copied `daily_economic_indicators_fidelity_fit_headerfix.html`, `daily_economic_indicators_common.css`, `daily_economic_indicators_fidelity_fit_headerfix.css`, `extracted_fields.json`, and copied `assets/fonts/`.
3. Verify the generated HTML contains required hooks and selectors:
   - `data-semantic-field`
   - `data-table-field`
   - `data-table-id`
   - `window.DailyIndicatorsTemplate`
   - `window.applyDailyIndicatorsData`
   - `collectState`
   - `runtime-font-faces`
4. Verify mapped semantic and table addresses from `today_major_economy/extracted_fields.json` still resolve in generated output for representative blocks and cells.
5. Verify exported JSON from the runtime contains semantic/table edits in the expected structure.
6. Verify copied font URLs under `generated/` or `reference/` resolve to existing files.
7. Verify `today_major_economy/` immutability with before/after hash comparison.

## ADR

Decision:
Use frozen reference-runtime reuse plus Python orchestration for milestone 1.

Drivers:
- The reference HTML already contains bundled font faces and editable runtime hooks.
- Shared CSS and fit CSS already encode the styling/table contract.
- Semantic/table mappings already exist in `today_major_economy/extracted_fields.json`.
- `python3` and `node` exist, but no local office/image conversion binaries were found in `PATH`.

Alternatives considered:
- Parser-first IR pipeline
- HTML/CSS rebuild from scratch

Why chosen:
It is the strongest milestone-1 path that preserves proven behavior while minimizing fidelity risk and avoiding unsupported local tool assumptions.

Consequences:
- Milestone 1 stays reference-runtime-centric and sample-scoped.
- Parser-first or rebuild work is deferred until runtime reuse is shown insufficient by evidence.

Follow-ups:
- After milestone 1 passes, decide whether the next investment is parser-first IR, broader document adapters, or automated capture tooling.

## Available Agent Types and Staffing Guidance

Available agent types:
`planner`, `architect`, `critic`, `executor`, `verifier`, `test-engineer`, `researcher`, `writer`, `explore`

Recommended staffing:
- `executor` at medium: implement manifest, freeze/copy flow, run orchestration, and runtime-preserving generation
- `verifier` at medium: prove runtime hook preservation, mapping preservation, font resolution, and `today_major_economy/` immutability
- `test-engineer` at medium: harden representative semantic/table contract checks and export JSON assertions
- `architect` at high, checkpoint only: challenge any proposal that drifts from reuse into premature rebuild
- `critic` at high, checkpoint only: test whether any newly proposed abstraction is justified by evidence

Launch guidance:
- `team` path if splitting into lanes: manifest/freeze, runtime orchestration, verification
- `ralph` path if one agent should drive sequential execution after planning

## Team -> Ralph Verification Path

Use `team` to implement the three lanes in parallel:
- Lane 1: manifest + freeze/copy + metadata extraction
- Lane 2: runtime-reuse build orchestration
- Lane 3: verification + review bundle

Then hand the integrated branch to `ralph` for final end-to-end execution, evidence review, immutability confirmation, and acceptance verification against the criteria above.
