# 260121 Major Economy Sample

This sample is the milestone-1 execution target for the editable HTML harness.

## Required Inputs

- Source HWP: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/260121 일일 주요경제지표.hwp`
- Canonical reference bundle: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/today_major_economy/`
- Sample manifest: `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/harness/samples/260121-major-economy/sample.manifest.json`

## Capture Pack

Place original-document capture files under:

- `/Users/tykim/Documents/workspace/onelineai/convertToHtmlHarness/harness/samples/260121-major-economy/capture/`

If this directory is empty, runs are still allowed, but they are marked `conversion-only / review-blocked` and cannot satisfy final fidelity acceptance.

## Expected Run Output

Each run creates:

- `harness/artifacts/260121-major-economy/runs/<run-id>/source/`
- `harness/artifacts/260121-major-economy/runs/<run-id>/reference/`
- `harness/artifacts/260121-major-economy/runs/<run-id>/generated/`
- `harness/artifacts/260121-major-economy/runs/<run-id>/review/`
- `harness/artifacts/260121-major-economy/runs/<run-id>/metadata/`
