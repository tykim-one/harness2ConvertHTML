# Test Spec: HWP Editable HTML Harness

## Scope

This test spec covers milestone 1 only:

- sample source: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/260121 일일 주요경제지표.hwp`
- canonical reference bundle: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/`
- execution target: frozen reference-runtime reuse plus Python orchestration

## Required Command

The harness must provide:

```bash
python3 scripts/run_sample.py --sample harness/samples/260121-major-economy/sample.manifest.json
```

## Acceptance Test Matrix

### 1. Manifest Contract

Pass when:
- `harness/samples/260121-major-economy/sample.manifest.json` exists
- manifest resolves source HWP, canonical reference HTML/CSS, extracted field mapping, font root, and run artifact paths
- manifest declares allowed mutations, forbidden mutations, and capture-pack policy

Fail when:
- any canonical path is missing
- manifest omits runtime hooks or capture-pack policy

### 2. Reference Immutability

Pass when:
- pre/post hash comparison shows `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/` is byte-for-byte unchanged

Fail when:
- any file under `today_major_economy/` is modified during a run

### 3. Freeze / Copy Stage

Pass when:
- each run creates `harness/artifacts/260121-major-economy/runs/<run-id>/reference/`
- copied reference includes:
  - `daily_economic_indicators_fidelity_fit_headerfix.html`
  - `daily_economic_indicators_common.css`
  - `daily_economic_indicators_fidelity_fit_headerfix.css`
  - `extracted_fields.json`
  - `assets/fonts/`

Fail when:
- copied reference is incomplete
- freeze stage rewrites canonical source files instead of copying them

### 4. Runtime Hook Preservation

Pass when generated HTML preserves:
- `window.DailyIndicatorsTemplate`
- `window.applyDailyIndicatorsData`
- `.editable-block`
- `data-semantic-field`
- `data-table-field`
- `data-table-id`
- `data-cell-key`
- `#runtime-font-faces`
- `collectState()`

Fail when:
- any required hook or selector is missing

### 5. Mapping Contract Preservation

Pass when every entry in `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/extracted_fields.json` resolves by one of these rules:
- if `semantic_field` exists, a matching `data-semantic-field` exists in generated output
- if `table_field` matches `tables.<tableId>.r<row>c<col>`, derive `cell_key` as `r<row>c<col>` and find matching `data-table-id="<tableId>"` plus `data-cell-key="<cell_key>"`
- if only `block_id` exists, the runtime preserves the corresponding block binding and exported-state entry

Fail when:
- any mapped semantic/table/block entry cannot be resolved

### 6. Exported-State Contract

Pass when `collectState()` returns JSON with this concrete structure:

```json
{
  "meta": {},
  "blocks": {},
  "semanticFields": {},
  "tables": {
    "<tableId>": {
      "cells": {
        "<cellKey>": "<html>"
      }
    }
  }
}
```

Fail when:
- any top-level section is missing
- table edits are not exported as `tables[tableId].cells[cellKey]`

### 7. Font Resolution

Pass when:
- copied or generated HTML resolves required font files from copied `assets/fonts/`
- no external office/image binary is needed for font fidelity inside the generated bundle

Fail when:
- referenced font files are missing
- generated output depends on unresolved font URLs

### 8. Capture-Pack Gating

Pass when:
- if capture assets exist under `runs/<run-id>/capture/`, the run is eligible for full fidelity review
- if capture assets are absent, the run is explicitly marked `conversion-only / review-blocked`

Fail when:
- capture assets are absent but the run is still treated as review-complete
- capture status is not recorded

### 9. Review Bundle Completeness

Pass when the run directory contains:
- frozen reference copy
- generated output
- verification outputs
- run metadata
- capture pack or explicit review-blocked marker
- review checklist / notes bundle

Fail when:
- a reviewer cannot inspect source capture state, reference state, and generated state together

## Manual Fidelity Gate

A run can satisfy final milestone acceptance only when:
- capture pack is present
- review is not blocked
- the user judges the result at least `today_major_economy` quality
- tables, headers, fonts, spacing, and editability show no major regressions

## Suggested Verification Ownership

- `executor`: manifest, freeze/copy flow, generation flow
- `verifier`: runtime hook preservation, mapping preservation, immutability, capture gating
- `test-engineer`: automated contract assertions, exported-state checks, run-status checks

## Exit Criteria

Planning is execution-ready when:
- `prd-hwp-editable-html-harness.md` exists
- this test spec exists
- both documents agree on runtime contract, capture gating, and acceptance rules
