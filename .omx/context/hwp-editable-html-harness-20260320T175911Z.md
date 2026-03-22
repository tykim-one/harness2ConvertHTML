# Context Snapshot

- Task statement: Build an agent and harness that convert source documents such as HWP, DOCS, and PDF into editable HTML while preserving the original UI as closely as possible.
- Desired outcome: A repeatable conversion workflow that first captures the original document, then uses the original file plus capture images as references to generate high-fidelity editable HTML.
- Stated solution: Use the original source document `260121 일일 주요경제지표.hwp` and the extracted assets under `today_major_economy/` as the current reference baseline for near-identical UI reproduction.
- Probable intent hypothesis: The user needs a reliable, layout-faithful document-to-editable-HTML system with a harness that can evaluate or guide conversion quality against a visual/reference target.

## Known Facts / Evidence

- Workspace contains the source document `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/260121 일일 주요경제지표.hwp`.
- Workspace contains reference artifacts under `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/`.
- Reference artifacts include:
  - `daily_economic_indicators_fidelity_fit_headerfix.html`
  - `daily_economic_indicators_fidelity_fit_headerfix.css`
  - `daily_economic_indicators_common.css`
  - `extracted_fields.json`
  - bundled fonts under `assets/fonts/`
- `extracted_fields.json` encodes semantic/table field mappings such as `header.title`, `stock.summary.*`, and dense table cell coordinates.
- The workspace currently contains no captured screenshots or PDF/image render references for the original document.
- This repository appears to be a reference-artifact workspace rather than an already-implemented app/service codebase.

## Constraints

- Output must be editable HTML, not a flat image-only rendering.
- Visual fidelity to the original UI is a primary quality axis.
- Existing extracted field values and current HTML/CSS output imply a structured conversion target, not just OCR text extraction.
- No additional dependencies should be introduced unless explicitly requested.

## Unknowns / Open Questions

- Is `today_major_economy/` the gold-standard target to reproduce, or only a partial prototype/reference?
- What exact deliverable is required first: conversion engine, evaluation harness, capture pipeline, end-to-end orchestration, or all of them?
- What document sources are truly in scope for the first milestone: only HWP, or HWP + PDF + DOC/DOCX/Google Docs?
- What fidelity threshold counts as success: visual diff tolerance, DOM editability requirements, field extraction completeness, or manual acceptability?
- Should the harness produce pass/fail scoring, side-by-side review artifacts, reusable prompts, or automated regression snapshots?
- What is explicitly out of scope for the first version?
- Which decisions may be made autonomously without additional confirmation?

## Decision-Boundary Unknowns

- Whether OMX may choose the first milestone architecture without user confirmation.
- Whether OMX may optimize for a single sample document before generalizing.
- Whether OMX may prioritize visual fidelity over semantic cleanliness in HTML structure.
- Whether screenshot capture/rendering may rely on local desktop tooling or must remain pure CLI/server-side.

## Likely Touchpoints

- `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/260121 일일 주요경제지표.hwp`
- `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.html`
- `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.css`
- `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/daily_economic_indicators_common.css`
- `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/extracted_fields.json`

## Interview Findings So Far

- First milestone priority: reproduce a single sample HWP as editable HTML end-to-end with near-identical UI fidelity to the original.
- Review mode: the user will manually inspect intermediate results and provide iterative feedback.
- Long-term direction: encode the evolving conversation, implementation choices, and review learnings into the harness/skills/agent so the system improves over time toward a robust document conversion agent + harness.
- Non-goals: no hard predefined v1 exclusions were declared; scope may expand as needed in service of the sample-fidelity milestone.
- Decision boundaries: OMX may autonomously choose HTML structure, intermediate artifact format, capture/comparison method, and harness record format, provided the final result aligns closely with the original UI.
- Acceptance bar: `today_major_economy/` quality level or better is considered a pass, and the pass bar also includes visual near-identity, true text editability, and no major breakage in tables/header/font/spacing.
