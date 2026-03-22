# Execution-Ready Kickoff

## Default assumptions for kickoff
- Start with **HWP-first** on the current sample document.
- Treat the current HTML/CSS/JSON bundle as the initial reference baseline.
- Use a **copy-first, non-destructive** setup so existing artifacts remain untouched.
- Defer multi-format support until the golden-case harness and evaluator loop are working.

## Suggested first execution slice
1. Create a canonical case directory for the current sample.
2. Copy the current source/reference artifacts into that case.
3. Add a manifest that points to source, reference HTML/CSS, fonts, and extracted field mappings.
4. Add a run directory contract for generated output, reports, and patches.
5. Add a first evaluator contract that checks visual/structural/editability outputs exist.

## Recommended directory target
```text
cases/
  golden/
    daily-economic-indicators/
      source/
      reference/
      generated/
      reports/
      patches/
      metadata/
```

## Executable next-step commands

### 1) Create the first golden-case skeleton
```bash
mkdir -p cases/golden/daily-economic-indicators/{source,reference,generated,reports,patches,metadata}
```

### 2) Copy the current source document into the case
```bash
cp "260121 일일 주요경제지표.hwp" cases/golden/daily-economic-indicators/source/
```

### 3) Copy the current reference bundle into the case
```bash
cp today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.html cases/golden/daily-economic-indicators/reference/
cp today_major_economy/daily_economic_indicators_common.css cases/golden/daily-economic-indicators/reference/
cp today_major_economy/daily_economic_indicators_fidelity_fit_headerfix.css cases/golden/daily-economic-indicators/reference/
cp today_major_economy/extracted_fields.json cases/golden/daily-economic-indicators/reference/
cp today_major_economy/daily_economic_indicators_fidelity_fit_headerfix_tokens.json cases/golden/daily-economic-indicators/reference/
mkdir -p cases/golden/daily-economic-indicators/reference/assets/fonts
cp today_major_economy/assets/fonts/*.woff2 cases/golden/daily-economic-indicators/reference/assets/fonts/
```

### 4) Add the first manifest file
```bash
cat > cases/golden/daily-economic-indicators/metadata/case-manifest.json <<'JSON'
{
  "caseId": "daily-economic-indicators",
  "source": {
    "type": "hwp",
    "path": "source/260121 일일 주요경제지표.hwp"
  },
  "reference": {
    "html": "reference/daily_economic_indicators_fidelity_fit_headerfix.html",
    "commonCss": "reference/daily_economic_indicators_common.css",
    "fitCss": "reference/daily_economic_indicators_fidelity_fit_headerfix.css",
    "tokens": "reference/daily_economic_indicators_fidelity_fit_headerfix_tokens.json",
    "fields": "reference/extracted_fields.json",
    "fontsDir": "reference/assets/fonts"
  },
  "runsDir": "generated",
  "reportsDir": "reports",
  "patchesDir": "patches"
}
JSON
```

### 5) Add the first evaluator contract file
```bash
cat > cases/golden/daily-economic-indicators/metadata/evaluator-contract.md <<'MD'
# Evaluator Contract

## Visual fidelity
- Save original-reference render artifacts
- Save generated-html render artifacts
- Save full-page diff and hotspot summary

## Structural fidelity
- Compare semantic field coverage against extracted_fields.json
- Compare table ids and cell-address coverage

## Editability
- Verify editable blocks remain editable
- Verify field-bound blocks preserve identifiers
- Verify exportable state/report artifact exists
MD
```

## Definition of done for this kickoff slice
- The case folder exists.
- The current sample is fully copied into the case without mutating the original `today_major_economy/` folder.
- A manifest exists and resolves all current reference assets.
- An evaluator contract exists and names the three quality axes.
- The repo is ready for an executor to implement the actual runner/evaluator against this contract.

## Recommended handoff order
1. Executor: build case skeleton + manifest support
2. Executor: build run/output contract
3. Executor: build evaluator report generation
4. Verifier: validate artifact completeness against the contract
5. Only then: start agent-driven fit improvements
