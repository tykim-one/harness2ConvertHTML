# Deep Interview Spec: HWP Editable HTML Harness

## Metadata

- Profile: `standard`
- Rounds: `4`
- Final ambiguity: `0.179`
- Threshold: `0.20`
- Context type: `brownfield`
- Interview transcript: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/.omx/interviews/hwp-editable-html-harness-20260321T033016Z.md`
- Context snapshot: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/.omx/context/hwp-editable-html-harness-20260320T175911Z.md`

## Clarity Breakdown

| Dimension | Score | Notes |
| --- | ---: | --- |
| Intent | 0.90 | Long-term goal is a reusable document-conversion agent and harness that accumulate implementation and review knowledge. |
| Outcome | 0.92 | First milestone is a single sample HWP reproduced end-to-end as high-fidelity editable HTML. |
| Scope | 0.80 | No hard predeclared v1 exclusions; scope may expand as needed to deliver the sample milestone. |
| Constraints | 0.80 | Autonomous implementation choices are allowed if they improve final fidelity and usefulness. |
| Success | 0.82 | Acceptance is anchored to `today_major_economy/` quality or better plus editability and layout fidelity. |
| Context | 0.78 | Brownfield workspace already contains a sample source document and target-like extracted artifacts. |

## Intent

The user wants to eventually build a robust document-conversion agent and harness for formats such as HWP, PDF, and Docs-like inputs. The immediate goal is not broad generalization but proving the workflow on one representative HWP document while capturing enough process knowledge that the harness, skill set, and agent can evolve over time.

## Desired Outcome

Produce an end-to-end workflow for the sample source document `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/260121 일일 주요경제지표.hwp` that:

- captures the original document first
- uses the original source plus capture references during conversion
- outputs editable HTML rather than a flattened image rendering
- reaches UI fidelity at least as strong as the existing `today_major_economy/` reference output
- supports iterative user review and feedback incorporation

## In Scope

- One sample HWP document as the first milestone
- Original document capture and storage as reference material
- Conversion workflow that uses both the source file and captured reference during HTML generation/refinement
- Editable HTML output with accompanying CSS/fonts/assets as needed
- Harness behavior that preserves the conversation/implementation trail well enough to improve future runs
- Iterative refinement based on manual user review

## Out-of-Scope / Non-goals

- No hard predefined exclusions were declared for v1
- Scope may expand if needed to achieve the sample-fidelity milestone
- Even without explicit non-goals, the first milestone remains centered on the single sample HWP rather than broad format generalization

## Decision Boundaries

OMX may decide autonomously, without additional confirmation, as long as the result improves fidelity and usefulness:

- HTML structure and representation strategy
- intermediate artifact and metadata formats
- capture method and comparison method
- harness logging / memory / record format
- how to sequence extraction, comparison, and refinement steps

The preserved priority order is:

1. Maximize sync with the original UI for the sample HWP
2. Keep the HTML truly editable
3. Fold learnings back into a reusable harness/agent direction

## Constraints

- Do not introduce new dependencies unless explicitly requested
- Output must remain editable HTML
- The user will manually review intermediate outputs and provide feedback
- Existing workspace artifacts are authoritative context, especially:
  - `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.html`
  - `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.css`
  - `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_common.css`
  - `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/extracted_fields.json`

## Testable Acceptance Criteria

- The sample HWP can be processed end-to-end into editable HTML
- Result quality is `today_major_economy/` level or better
- The rendered HTML is visually near-identical to the original document under human review
- Text remains editable in the produced HTML
- Tables, headers, fonts, spacing, and overall structure do not show major mismatches versus the original/reference
- The workflow stores enough artifacts and notes to support continued iterative improvement of the harness

## Assumptions Exposed + Resolutions

- Assumption: the first useful deliverable might be a generic multi-format harness
  - Resolution: no; first prove the system on a single sample HWP
- Assumption: v1 needs strict exclusions
  - Resolution: no; the user does not want to predefine hard non-goals
- Assumption: implementation choices need frequent confirmation
  - Resolution: no; autonomous decision-making is allowed if the final result is good
- Assumption: success might be loosely subjective
  - Resolution: anchor acceptance to `today_major_economy/` quality or better and include explicit editability/layout fidelity requirements

## Technical Context Findings

- Workspace shape is reference-artifact heavy, not a mature app/service codebase
- The sample source is `260121 일일 주요경제지표.hwp`
- The `today_major_economy/` directory already contains a target-like HTML/CSS/font bundle and extracted field mappings
- `extracted_fields.json` includes semantic keys and table-coordinate mappings that are likely useful for harness verification and structured refinement
- No screenshot capture artifacts for the original document were present in the workspace at interview time

## Execution Handoff Contract

Recommended next lane: `$ralplan`

- Input artifact: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/.omx/specs/deep-interview-hwp-editable-html-harness.md`
- Why recommended: requirements are now clear, but the implementation still benefits from an explicit plan that turns the sample-fidelity goal into concrete build, verification, and iteration phases.

Alternative lanes:

- `$autopilot` if direct planning + execution should start immediately from this spec
- `$ralph` if persistent sequential completion pressure is preferred
- `$team` if the work is split into meaningful parallel lanes

## Residual Risk

- No hard v1 non-goals means scope can drift unless future planning keeps the sample-HWP milestone as the active center of gravity
- Acceptance remains human-reviewed rather than numerically scored, so the harness will need strong artifact capture to make iterative comparisons reliable
