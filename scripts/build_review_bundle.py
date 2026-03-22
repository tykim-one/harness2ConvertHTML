from __future__ import annotations

import argparse
from pathlib import Path

from harness_utils import load_manifest, read_json, relative_to_repo, resolve_manifest_path, write_json, write_text


def _read_optional_json(path: Path) -> dict:
    return read_json(path) if path.exists() else {}


def build_upgrade_targets(
    *,
    run_status: dict,
    runtime_verification: dict,
    extract_report: dict,
    transform_report: dict,
    build_report: dict,
    render_report: dict,
) -> list[dict]:
    targets: list[dict] = []
    warning_count = int(extract_report.get("warning_count") or 0)
    if warning_count > 0:
        targets.append(
            {
                "priority": "medium",
                "category": "extractor-warnings",
                "issue": f"pyhwp emitted {warning_count} extraction warnings",
                "recommended_action": "Classify recurring pyhwp warnings and decide which require normalization or parser-specific cleanup.",
                "evidence": extract_report.get("stderr_log"),
            }
        )

    mismatch_count = int(runtime_verification.get("oracle_coverage", {}).get("mismatch_count") or 0)
    if mismatch_count > 0:
        targets.append(
            {
                "priority": "high",
                "category": "oracle-mismatch",
                "issue": f"{mismatch_count} oracle field values were not matched by the IR-driven path",
                "recommended_action": "Inspect unmatched oracle labels and improve XML-to-IR mapping or paragraph/table text normalization.",
                "evidence": runtime_verification.get("oracle_mismatches_preview", []),
            }
        )

    unresolved_mappings = runtime_verification.get("unresolved_mappings", [])
    if unresolved_mappings:
        targets.append(
            {
                "priority": "high",
                "category": "runtime-mapping",
                "issue": f"{len(unresolved_mappings)} runtime mappings are unresolved",
                "recommended_action": "Ensure every oracle block/table field is emitted into the runtime DOM with matching block ids / semantic fields / cell keys.",
                "evidence": unresolved_mappings[:10],
            }
        )

    fallback_count = int(build_report.get("fallback_field_count") or 0)
    if fallback_count > 0:
        targets.append(
            {
                "priority": "high",
                "category": "reference-fallback",
                "issue": f"{fallback_count} fields still rely on oracle fallback resolution",
                "recommended_action": "Reduce fallback usage by deriving more field values from IR-native paragraph/table structures.",
                "evidence": build_report.get("fallback_labels_preview", []),
            }
        )

    for item in render_report.get("remaining_reference_scaffolding", []):
        targets.append(
            {
                "priority": "medium",
                "category": "reference-scaffolding",
                "issue": item,
                "recommended_action": "Track and reduce this scaffold once the direct path can carry the equivalent information or styling safely.",
                "evidence": None,
            }
        )

    if run_status.get("review_status") == "conversion-only / review-blocked":
        targets.append(
            {
                "priority": "medium",
                "category": "visual-acceptance",
                "issue": "Final fidelity acceptance is blocked because capture assets are missing",
                "recommended_action": "Add real source-document capture images so the harness can move from review-blocked to review-ready and start visual comparison.",
                "evidence": run_status.get("paths", {}).get("review_dir"),
            }
        )

    if not targets:
        targets.append(
            {
                "priority": "low",
                "category": "next-pass",
                "issue": "No immediate structural/runtime blockers detected",
                "recommended_action": "Proceed to visual-fidelity tuning and reduce remaining reference scaffolding opportunistically.",
                "evidence": render_report.get("main_generated_html"),
            }
        )
    return targets


def run_build_review_bundle(manifest: dict, run_dir: str | Path) -> dict:
    run_root = resolve_manifest_path(run_dir)
    review_dir = run_root / "review"
    metadata_dir = run_root / "metadata"
    review_dir.mkdir(parents=True, exist_ok=True)

    run_status = read_json(metadata_dir / "run_status.json")
    runtime_verification = read_json(metadata_dir / "runtime_contract_verification.json")
    immutability = read_json(metadata_dir / "reference_immutability.json")
    checklist_path = resolve_manifest_path("harness/review/visual-checklist.md")
    extract_report = _read_optional_json(metadata_dir / "extract_hwp_xml.json")
    transform_report = _read_optional_json(metadata_dir / "transform_hwp_xml_to_ir.json")
    build_report = _read_optional_json(metadata_dir / "build_editable_html.json")
    render_report = _read_optional_json(metadata_dir / "render_ir_to_html.json")
    upgrade_targets = build_upgrade_targets(
        run_status=run_status,
        runtime_verification=runtime_verification,
        extract_report=extract_report,
        transform_report=transform_report,
        build_report=build_report,
        render_report=render_report,
    )
    upgrade_targets_path = review_dir / "upgrade_targets.json"
    write_json(upgrade_targets_path, upgrade_targets)

    direct_outputs = run_status.get("direct_outputs", {})
    summary = {
        "run_id": run_status["run_id"],
        "review_status": run_status["review_status"],
        "capture_assets_found": run_status["capture_assets_found"],
        "pipeline_passed": run_status.get("pipeline_passed"),
        "acceptance_ready": run_status.get("acceptance_ready"),
        "runtime_contract_passed": runtime_verification["passed"],
        "runtime_generation_mode": runtime_verification.get("generation_mode"),
        "oracle_coverage": runtime_verification.get("oracle_coverage", {}),
        "oracle_mismatches_preview": runtime_verification.get("oracle_mismatches_preview", []),
        "extraction_warning_count": extract_report.get("warning_count"),
        "fallback_field_count": build_report.get("fallback_field_count"),
        "remaining_reference_scaffolding": render_report.get("remaining_reference_scaffolding", []),
        "reference_immutable": immutability["passed"],
        "direct_extraction_ready": run_status.get("direct_extraction_ready"),
        "ir_ready": run_status.get("ir_ready"),
        "main_generated_from_ir": run_status.get("main_generated_from_ir"),
        "next_upgrade_targets": upgrade_targets,
        "direct_outputs": direct_outputs,
        "upgrade_targets_path": relative_to_repo(upgrade_targets_path),
        "paths": {
            "source": run_status["paths"]["source_dir"],
            "reference": run_status["paths"]["reference_dir"],
            "generated": run_status["paths"]["generated_dir"],
            "metadata": run_status["paths"]["metadata_dir"],
        },
    }
    write_json(review_dir / "review_summary.json", summary)

    markdown = f"""# Review Bundle

- Run ID: `{run_status['run_id']}`
- Review status: `{run_status['review_status']}`
- Capture assets found: `{run_status['capture_assets_found']}`
- Pipeline passed: `{run_status.get('pipeline_passed')}`
- Acceptance ready: `{run_status.get('acceptance_ready')}`
- Runtime contract passed: `{runtime_verification['passed']}`
- Runtime generation mode: `{runtime_verification.get('generation_mode')}`
- Reference immutability passed: `{immutability['passed']}`
- Direct extraction ready: `{run_status.get('direct_extraction_ready')}`
- IR ready: `{run_status.get('ir_ready')}`
- Main generated path from IR: `{run_status.get('main_generated_from_ir')}`
- Extraction warning count: `{extract_report.get('warning_count')}`
- Fallback field count: `{build_report.get('fallback_field_count')}`

## Direct outputs

- Extracted XML: `{direct_outputs.get('extracted_xml')}`
- Extracted IR: `{direct_outputs.get('ir')}`
- Main generated HTML: `{direct_outputs.get('main_generated_html')}`
- Main generated payload: `{direct_outputs.get('main_generated_payload')}`
- Main generated state seed: `{direct_outputs.get('main_generated_state_seed')}`
- Direct preview HTML: `{direct_outputs.get('preview_html')}`
- Direct preview payload: `{direct_outputs.get('preview_payload')}`

## Oracle coverage

- Coverage: `{runtime_verification.get('oracle_coverage', {}).get('matched_field_count')}` / `{runtime_verification.get('oracle_coverage', {}).get('reference_field_total')}`
- Mismatch count: `{runtime_verification.get('oracle_coverage', {}).get('mismatch_count')}`
- Mismatch preview: `{runtime_verification.get('oracle_mismatches_preview')}`
- Transform report: `{relative_to_repo(metadata_dir / 'transform_hwp_xml_to_ir.json')}`

## Extraction warnings

- Warning count: `{extract_report.get('warning_count')}`
- Warning log: `{extract_report.get('stderr_log')}`
- Warning preview: `{extract_report.get('warnings_preview')}`

## Remaining reference scaffolding

{chr(10).join(f'- {item}' for item in render_report.get('remaining_reference_scaffolding', [])) or '- none'}

## Next upgrade targets

- Upgrade targets JSON: `{relative_to_repo(upgrade_targets_path)}`
{chr(10).join(f"- [{item['priority']}] {item['category']}: {item['issue']} -> {item['recommended_action']}" for item in upgrade_targets)}

## Paths

- Source: `{run_status['paths']['source_dir']}`
- Reference: `{run_status['paths']['reference_dir']}`
- Generated: `{run_status['paths']['generated_dir']}`
- Metadata: `{run_status['paths']['metadata_dir']}`

## Notes

- If review status is `conversion-only / review-blocked`, final fidelity acceptance is blocked until capture files are provided.
- Use the checklist below during manual review.

## Checklist

{checklist_path.read_text(encoding='utf-8')}
"""
    write_text(review_dir / "README.md", markdown)
    return {
        "review_dir": relative_to_repo(review_dir),
        "summary": relative_to_repo(review_dir / "review_summary.json"),
        "upgrade_targets": relative_to_repo(upgrade_targets_path),
        "next_upgrade_targets": upgrade_targets,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "--manifest", dest="manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    report = run_build_review_bundle(manifest, args.run_dir)
    print(report["review_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
