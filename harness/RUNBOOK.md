# Harness Runbook

## Primary command

```bash
source .venv-pyhwp/bin/activate
HWP5PROC_PATH=.venv-pyhwp/bin/hwp5proc python3 scripts/run_sample.py --sample harness/samples/260121-major-economy/sample.manifest.json
```

## What the run does

1. Creates a fresh run directory
2. Copies the source HWP and canonical reference bundle into the run
3. Runs direct extraction with `hwp5proc xml`
4. Saves extracted XML as a repo-managed intermediate artifact
5. Transforms extracted XML into the sample IR
6. Generates:
   - main generated HTML path
   - runtime payload/state
   - direct preview HTML
7. Verifies:
   - runtime contract
   - reference immutability
8. Writes a review bundle plus next-upgrade targets

## Direct outputs to inspect first

- Extracted XML: `harness/artifacts/260121-major-economy/runs/<run-id>/metadata/extracted_hwp.xml`
- Extracted IR: `harness/artifacts/260121-major-economy/runs/<run-id>/metadata/extracted_hwp_ir.json`
- Main generated HTML: `harness/artifacts/260121-major-economy/runs/<run-id>/generated/daily_economic_indicators_fidelity_fit_headerfix.html`
- Main generated payload: `harness/artifacts/260121-major-economy/runs/<run-id>/generated/generated_payload.json`
- Main generated state seed: `harness/artifacts/260121-major-economy/runs/<run-id>/generated/generated_state_seed.json`
- Direct preview HTML: `harness/artifacts/260121-major-economy/runs/<run-id>/generated/direct_hwp_extraction_preview.html`

## Review bundle outputs

- Review summary: `harness/artifacts/260121-major-economy/runs/<run-id>/review/review_summary.json`
- Upgrade targets: `harness/artifacts/260121-major-economy/runs/<run-id>/review/upgrade_targets.json`
- Manual review notes: `harness/artifacts/260121-major-economy/runs/<run-id>/review/README.md`

## Upgrade loop

Each run should answer these questions:

1. What did direct extraction produce?
2. What oracle fields/cells still mismatch?
3. What runtime mappings are unresolved?
4. What still relies on reference scaffolding?
5. What are the next highest-value upgrades?

Use the generated `upgrade_targets.json` to drive the next implementation pass.

## Review status

- If capture files exist, the run is review-eligible
- If capture files are missing, the run is `conversion-only / review-blocked`

## Project-local harness docs

- Upgrade checklist: `harness/UPGRADE_CHECKLIST.md`
- Proto-skill / execution spec: `harness/PROJECT_HARNESS_SKILL_DRAFT.md`
