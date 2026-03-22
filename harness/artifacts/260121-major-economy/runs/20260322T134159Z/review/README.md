# Review Bundle

- Run ID: `20260322T134159Z`
- Review status: `conversion-only / review-blocked`
- Capture assets found: `False`
- Pipeline passed: `True`
- Acceptance ready: `False`
- Runtime contract passed: `True`
- Runtime generation mode: `ir-main-direct`
- Reference immutability passed: `True`
- Direct extraction ready: `True`
- IR ready: `True`
- Main generated path from IR: `True`
- Extraction warning count: `240`
- Fallback field count: `0`

## Direct outputs

- Extracted XML: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/metadata/extracted_hwp.xml`
- Extracted IR: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/metadata/extracted_hwp_ir.json`
- Main generated HTML: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/generated/daily_economic_indicators_fidelity_fit_headerfix.html`
- Main generated payload: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/generated/generated_payload.json`
- Main generated state seed: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/generated/generated_state_seed.json`
- Direct preview HTML: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/generated/direct_hwp_extraction_preview.html`
- Direct preview payload: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/generated/direct_hwp_extraction_preview.json`

## Oracle coverage

- Coverage: `817` / `817`
- Mismatch count: `0`
- Mismatch preview: `[]`
- Transform report: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/metadata/transform_hwp_xml_to_ir.json`

## Extraction warnings

- Warning count: `240`
- Warning log: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/metadata/extract_hwp_xml.stderr.log`
- Warning preview: `['undefined UnderlineStyle value: 15', "defined name/values: {'SOLID': UnderlineStyle.SOLID, 'DASHED': UnderlineStyle.DASHED, 'DOTTED': UnderlineStyle.DOTTED, 'DASH_DOT': UnderlineStyle.DASH_DOT, 'DASH_DOT_DOT': UnderlineStyle.DASH_DOT_DOT, 'LONG_DASHED': UnderlineStyle.LONG_DASHED, 'LARGE_DOTTED': UnderlineStyle.LARGE_DOTTED, 'DOUBLE': UnderlineStyle.DOUBLE, 'LOWER_WEIGHTED': UnderlineStyle.LOWER_WEIGHTED, 'UPPER_WEIGHTED': UnderlineStyle.UPPER_WEIGHTED, 'MIDDLE_WEIGHTED': UnderlineStyle.MIDDLE_WEIGHTED}", 'undefined UnderlineStyle value: 15', "defined name/values: {'SOLID': UnderlineStyle.SOLID, 'DASHED': UnderlineStyle.DASHED, 'DOTTED': UnderlineStyle.DOTTED, 'DASH_DOT': UnderlineStyle.DASH_DOT, 'DASH_DOT_DOT': UnderlineStyle.DASH_DOT_DOT, 'LONG_DASHED': UnderlineStyle.LONG_DASHED, 'LARGE_DOTTED': UnderlineStyle.LARGE_DOTTED, 'DOUBLE': UnderlineStyle.DOUBLE, 'LOWER_WEIGHTED': UnderlineStyle.LOWER_WEIGHTED, 'UPPER_WEIGHTED': UnderlineStyle.UPPER_WEIGHTED, 'MIDDLE_WEIGHTED': UnderlineStyle.MIDDLE_WEIGHTED}", 'undefined UnderlineStyle value: 15', "defined name/values: {'SOLID': UnderlineStyle.SOLID, 'DASHED': UnderlineStyle.DASHED, 'DOTTED': UnderlineStyle.DOTTED, 'DASH_DOT': UnderlineStyle.DASH_DOT, 'DASH_DOT_DOT': UnderlineStyle.DASH_DOT_DOT, 'LONG_DASHED': UnderlineStyle.LONG_DASHED, 'LARGE_DOTTED': UnderlineStyle.LARGE_DOTTED, 'DOUBLE': UnderlineStyle.DOUBLE, 'LOWER_WEIGHTED': UnderlineStyle.LOWER_WEIGHTED, 'UPPER_WEIGHTED': UnderlineStyle.UPPER_WEIGHTED, 'MIDDLE_WEIGHTED': UnderlineStyle.MIDDLE_WEIGHTED}", 'undefined UnderlineStyle value: 15', "defined name/values: {'SOLID': UnderlineStyle.SOLID, 'DASHED': UnderlineStyle.DASHED, 'DOTTED': UnderlineStyle.DOTTED, 'DASH_DOT': UnderlineStyle.DASH_DOT, 'DASH_DOT_DOT': UnderlineStyle.DASH_DOT_DOT, 'LONG_DASHED': UnderlineStyle.LONG_DASHED, 'LARGE_DOTTED': UnderlineStyle.LARGE_DOTTED, 'DOUBLE': UnderlineStyle.DOUBLE, 'LOWER_WEIGHTED': UnderlineStyle.LOWER_WEIGHTED, 'UPPER_WEIGHTED': UnderlineStyle.UPPER_WEIGHTED, 'MIDDLE_WEIGHTED': UnderlineStyle.MIDDLE_WEIGHTED}", 'undefined UnderlineStyle value: 15', "defined name/values: {'SOLID': UnderlineStyle.SOLID, 'DASHED': UnderlineStyle.DASHED, 'DOTTED': UnderlineStyle.DOTTED, 'DASH_DOT': UnderlineStyle.DASH_DOT, 'DASH_DOT_DOT': UnderlineStyle.DASH_DOT_DOT, 'LONG_DASHED': UnderlineStyle.LONG_DASHED, 'LARGE_DOTTED': UnderlineStyle.LARGE_DOTTED, 'DOUBLE': UnderlineStyle.DOUBLE, 'LOWER_WEIGHTED': UnderlineStyle.LOWER_WEIGHTED, 'UPPER_WEIGHTED': UnderlineStyle.UPPER_WEIGHTED, 'MIDDLE_WEIGHTED': UnderlineStyle.MIDDLE_WEIGHTED}"]`

## Remaining reference scaffolding

- Common/fitted CSS and font assets are still staged from the frozen reference bundle.
- Oracle coverage currently uses today_major_economy/extracted_fields.json for mismatch reporting.

## Next upgrade targets

- Upgrade targets JSON: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/review/upgrade_targets.json`
- [medium] extractor-warnings: pyhwp emitted 240 extraction warnings -> Classify recurring pyhwp warnings and decide which require normalization or parser-specific cleanup.
- [medium] reference-scaffolding: Common/fitted CSS and font assets are still staged from the frozen reference bundle. -> Track and reduce this scaffold once the direct path can carry the equivalent information or styling safely.
- [medium] reference-scaffolding: Oracle coverage currently uses today_major_economy/extracted_fields.json for mismatch reporting. -> Track and reduce this scaffold once the direct path can carry the equivalent information or styling safely.
- [medium] visual-acceptance: Final fidelity acceptance is blocked because capture assets are missing -> Add real source-document capture images so the harness can move from review-blocked to review-ready and start visual comparison.

## Paths

- Source: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/source`
- Reference: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/reference`
- Generated: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/generated`
- Metadata: `harness/artifacts/260121-major-economy/runs/20260322T134159Z/metadata`

## Notes

- If review status is `conversion-only / review-blocked`, final fidelity acceptance is blocked until capture files are provided.
- Use the checklist below during manual review.

## Checklist

# Visual Review Checklist

- 원본 capture와 generated HTML 렌더 결과를 나란히 비교했는가
- 표의 열 폭, 행 높이, 헤더 강조가 크게 어긋나지 않는가
- 글꼴과 자간이 눈에 띄게 깨지지 않는가
- 편집 모드 전환과 내용 수정이 실제로 가능한가
- semantic/table binding이 깨져 특정 셀 업데이트가 누락되지 않았는가
- capture가 없으면 반드시 `review-blocked` 상태로 남겼는가

