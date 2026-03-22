from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from build_editable_html import run_build_editable_html
from build_review_bundle import run_build_review_bundle
from extract_hwp_xml import run_extract_hwp_xml
from extract_reference_metadata import run_extract_reference_metadata
from render_ir_to_html import run_render_ir_to_html
from freeze_reference_runtime import run_freeze_reference_runtime
from transform_hwp_xml_to_ir import run_transform_hwp_xml_to_ir
from harness_utils import (
    ensure_dir,
    load_manifest,
    relative_to_repo,
    resolve_manifest_path,
    snapshot_tree_hashes,
    utc_run_id,
    write_json,
)
from verify_reference_immutable import run_verify_reference_immutable
from verify_runtime_contract import run_verify_runtime_contract


def _copy_capture_pack(manifest: dict, run_root: Path) -> tuple[bool, str, int]:
    capture_cfg = manifest["capture_pack"]
    capture_src = resolve_manifest_path(capture_cfg["source_dir"])
    capture_dest = ensure_dir(run_root / "capture")
    files: list[Path] = []
    if capture_src.exists():
        files = [
            path
            for path in capture_src.rglob("*")
            if path.is_file() and not path.name.startswith(".")
        ]
        if files:
            for source_file in files:
                relative = source_file.relative_to(capture_src)
                target = capture_dest / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target)
    found = bool(files)
    if found:
        return True, "review-ready", len(files)
    return False, "conversion-only / review-blocked", 0


def _append_history(run_root: Path, run_status: dict) -> None:
    history_path = resolve_manifest_path("harness/history/260121-major-economy.md")
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"- `{run_status['run_id']}` | review_status=`{run_status['review_status']}`"
            f" | runtime_passed=`{run_status['runtime_contract_passed']}`"
            f" | immutable=`{run_status['reference_immutable_passed']}`"
            f" | generation_mode=`{run_status.get('runtime_generation_mode')}`"
            f" | oracle_coverage=`{run_status.get('oracle_coverage', {}).get('matched_field_count')}/{run_status.get('oracle_coverage', {}).get('reference_field_total')}`"
            f" | oracle_mismatches=`{run_status.get('oracle_coverage', {}).get('mismatch_count')}`"
            f" | fallback_fields=`{run_status.get('fallback_field_count')}`\n"
        )



def run_sample(manifest_path: str) -> dict:
    manifest = load_manifest(manifest_path)
    run_id = utc_run_id()
    runs_root = ensure_dir(manifest["artifacts"]["runs_root"])
    run_root = ensure_dir(runs_root / run_id)
    metadata_dir = ensure_dir(run_root / "metadata")

    capture_assets_found, review_status, capture_file_count = _copy_capture_pack(manifest, run_root)
    status = {
        "run_id": run_id,
        "sample_id": manifest["sample_id"],
        "capture_assets_found": capture_assets_found,
        "capture_file_count": capture_file_count,
        "review_status": review_status,
        "paths": {
            "run_dir": relative_to_repo(run_root),
            "metadata_dir": relative_to_repo(metadata_dir),
        },
    }
    write_json(metadata_dir / "run_status.json", status)

    reference_root = resolve_manifest_path("today_major_economy")
    before_snapshot = snapshot_tree_hashes(reference_root)
    write_json(metadata_dir / "reference_hashes_before.json", before_snapshot)

    freeze_report = run_freeze_reference_runtime(manifest, run_root)
    extract_report = run_extract_hwp_xml(manifest, run_root)
    ir_report = run_transform_hwp_xml_to_ir(manifest, run_root)
    metadata_report = run_extract_reference_metadata(manifest, run_root)
    build_report = run_build_editable_html(manifest, run_root, status)
    render_report = run_render_ir_to_html(manifest, run_root, status)
    status["paths"].update(
        {
            "source_dir": freeze_report["source_dir"],
            "reference_dir": freeze_report["reference_dir"],
            "generated_dir": build_report["generated_dir"],
        }
    )
    status["direct_extraction_ready"] = True
    status["ir_ready"] = True
    status["main_generated_from_ir"] = render_report["generation_mode"] == "ir-main-direct"
    status["oracle_coverage"] = render_report["oracle_coverage"]
    status["oracle_mismatch_count"] = render_report["oracle_coverage"]["mismatch_count"]
    status["remaining_reference_scaffolding"] = render_report["remaining_reference_scaffolding"]
    write_json(metadata_dir / "run_status.json", status)

    after_snapshot = snapshot_tree_hashes(reference_root)
    write_json(metadata_dir / "reference_hashes_after.json", after_snapshot)

    immutability = run_verify_reference_immutable(
        metadata_dir / "reference_hashes_before.json",
        metadata_dir / "reference_hashes_after.json",
        metadata_dir / "reference_immutability.json",
    )
    runtime_report = run_verify_runtime_contract(manifest, run_root)
    status.update(
        {
            "reference_immutable_passed": immutability["passed"],
            "runtime_contract_passed": runtime_report["passed"],
            "runtime_generation_mode": runtime_report.get("generation_mode"),
            "fallback_field_count": build_report.get("fallback_field_count"),
            "paths": {
                **status["paths"],
                "review_dir": relative_to_repo(run_root / "review"),
            },
            "reports": {
                "freeze": relative_to_repo(metadata_dir / "freeze_reference_runtime.json"),
                "extract_hwp_xml": relative_to_repo(metadata_dir / "extract_hwp_xml.json"),
                "transform_hwp_xml_to_ir": relative_to_repo(metadata_dir / "transform_hwp_xml_to_ir.json"),
                "metadata": relative_to_repo(metadata_dir / "reference_metadata.json"),
                "build": relative_to_repo(metadata_dir / "build_editable_html.json"),
                "render_ir_to_html": relative_to_repo(metadata_dir / "render_ir_to_html.json"),
                "runtime_verification": relative_to_repo(metadata_dir / "runtime_contract_verification.json"),
                "reference_immutability": relative_to_repo(metadata_dir / "reference_immutability.json"),
            },
            "direct_outputs": {
                "extracted_xml": extract_report["extracted_xml"],
                "ir": ir_report["ir_path"],
                "preview_html": render_report["preview_html"],
                "preview_payload": render_report["preview_payload"],
                "main_generated_html": render_report["main_generated_html"],
                "main_generated_payload": render_report["main_generated_payload"],
                "main_generated_state_seed": render_report["main_generated_state_seed"],
            },
        }
    )
    status["pipeline_passed"] = status["reference_immutable_passed"] and status["runtime_contract_passed"]
    status["acceptance_ready"] = status["pipeline_passed"] and status["capture_assets_found"] and status["review_status"] != "conversion-only / review-blocked"
    status["overall_passed"] = status["acceptance_ready"]
    write_json(metadata_dir / "run_status.json", status)
    review_report = run_build_review_bundle(manifest, run_root)
    status["reports"]["review_summary"] = review_report["summary"]
    status["reports"]["upgrade_targets"] = review_report["upgrade_targets"]
    status["next_upgrade_targets"] = review_report.get("next_upgrade_targets", [])
    write_json(metadata_dir / "run_status.json", status)
    _append_history(run_root, status)
    return status



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True)
    args = parser.parse_args()
    status = run_sample(args.sample)
    print(status["paths"]["run_dir"])
    print(status["review_status"])
    print("PASS" if status["pipeline_passed"] else "FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
