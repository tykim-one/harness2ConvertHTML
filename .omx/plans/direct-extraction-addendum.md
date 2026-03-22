# Direct HWP Extraction Addendum

## Clarified requirement
- The final target is **direct HWP extraction**.
- `today_major_economy/` is **not** the desired long-term conversion engine output path; it is the **gold-standard reference bundle** produced when the original `일일 주요 경제지표` document was successfully converted.
- The reference bundle should therefore be used as a **structural + visual target** for building the real HWP conversion pipeline.

## Updated interpretation
- Current harness work remains useful, but only as a **baseline harness / oracle / evaluator scaffold**.
- The real converter must eventually do:
  1. `HWP -> extracted structure / IR`
  2. `IR -> editable HTML/CSS/runtime payload`
  3. `generated output -> compare against reference bundle + captures`
- In other words, **reference-runtime reuse is a temporary bootstrap strategy**, not the final architecture.

## Updated next-stage execution goals
1. Build a direct HWP extraction stage that can emit document structure close to the reference bundle's semantics.
2. Derive a canonical IR/schema from the successful reference artifacts (`HTML`, `CSS`, `tokens`, `extracted_fields.json`).
3. Build an HTML renderer that emits the same binding/runtime structure from extracted IR rather than copying the reference bundle.
4. Keep the current harness as the regression/evaluation loop for measuring extraction quality.

## Concrete next work items
### 1) Freeze the reference as the oracle schema
- Treat `today_major_economy/` as the canonical target specimen.
- Extract from it the required structural contract:
  - block ids
  - semantic fields
  - table ids and cell keys
  - font/token expectations
  - editable runtime hooks

### 2) Define the HWP-to-IR boundary
- Design the minimum IR needed to express the sample document:
  - page/section
  - paragraph/block
  - text runs and font attributes
  - tables, rows, cells
  - semantic labels where recoverable
  - assets / style tokens

### 3) Build the first true extractor path
- Start with the current sample HWP only.
- Produce extracted JSON/IR from the HWP directly.
- Measure extracted coverage against the oracle fields/tables in `today_major_economy/extracted_fields.json`.

### 4) Replace reference-copy generation with IR-driven generation
- Renderer should output:
  - editable HTML
  - CSS/token artifacts
  - payload/state seed
- But the output should now be generated from extracted IR, not from copying `reference/` into `generated/`.

### 5) Keep the harness as the judge
- Runtime contract verification stays.
- Reference immutability stays.
- Visual review and later `$visual-verdict` stay.
- The difference is that the harness should validate a **true extracted result**, not a reference-reused result.

## Acceptance shift
### Current baseline acceptance
- "Harness runs and truthfully reports readiness"

### Real milestone acceptance
- "Given the original HWP, the pipeline directly extracts and renders an editable HTML artifact whose structure and UI fidelity converge toward the `today_major_economy/` reference."
