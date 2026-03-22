from __future__ import annotations

import argparse
from pathlib import Path

from harness_utils import (
    build_runtime_index,
    load_manifest,
    parse_font_faces,
    read_json,
    relative_to_repo,
    resolve_manifest_path,
    table_field_to_cell_ref,
    write_json,
)


def _check_required_hooks(html_text: str, runtime_index, required_hooks: list[str]) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for hook in required_hooks:
        if hook in {"window.DailyIndicatorsTemplate", "window.applyDailyIndicatorsData", "collectState"}:
            results[hook] = hook in html_text
        elif hook == ".editable-block":
            results[hook] = "editable-block" in runtime_index.classes
        elif hook == "#runtime-font-faces":
            results[hook] = "runtime-font-faces" in runtime_index.ids
        elif hook == "data-semantic-field":
            results[hook] = bool(runtime_index.semantic_fields)
        elif hook == "data-table-field":
            results[hook] = bool(runtime_index.table_fields)
        elif hook == "data-table-id":
            results[hook] = bool(runtime_index.table_cells)
        elif hook == "data-cell-key":
            results[hook] = bool(runtime_index.table_cells)
        else:
            results[hook] = hook in html_text
    return results


def run_verify_runtime_contract(manifest: dict, run_dir: str | Path) -> dict:
    run_root = resolve_manifest_path(run_dir)
    generated_dir = run_root / "generated"
    metadata_dir = run_root / "metadata"
    html_name = Path(manifest["reference"]["html"]).name
    fields_name = Path(manifest["reference"]["fields"]).name
    render_report_path = metadata_dir / "render_ir_to_html.json"
    render_report = read_json(render_report_path) if render_report_path.exists() else {}

    html_path = resolve_manifest_path(render_report.get("main_generated_html", generated_dir / html_name))
    payload_path = resolve_manifest_path(render_report.get("main_generated_payload", generated_dir / "generated_payload.json"))
    state_path = resolve_manifest_path(render_report.get("main_generated_state_seed", generated_dir / "generated_state_seed.json"))

    html_text = html_path.read_text(encoding="utf-8")
    runtime_index = build_runtime_index(html_text)
    required_hooks = manifest["runtime_contract"]["required_hooks"]
    hook_results = _check_required_hooks(html_text, runtime_index, required_hooks)

    extracted_fields = read_json(run_root / "reference" / fields_name)
    unresolved: list[dict] = []
    for entry in extracted_fields:
        if entry.get("semantic_field") and entry["semantic_field"] not in runtime_index.semantic_fields:
            unresolved.append({"kind": "semantic_field", "value": entry["semantic_field"], "block_id": entry.get("block_id")})
        if entry.get("table_field") and entry.get("table_id"):
            cell_ref = table_field_to_cell_ref(entry["table_field"])
            if not cell_ref:
                unresolved.append({"kind": "table_field_parse", "value": entry["table_field"]})
            else:
                table_id, cell_key = cell_ref
                if entry["table_field"] not in runtime_index.table_fields:
                    unresolved.append({"kind": "table_field", "value": entry["table_field"]})
                if (table_id, cell_key) not in runtime_index.table_cells:
                    unresolved.append({"kind": "table_cell", "table_id": table_id, "cell_key": cell_key})
        if entry.get("block_id") and entry["block_id"] not in runtime_index.block_ids:
            unresolved.append({"kind": "block_id", "value": entry["block_id"]})

    payload = read_json(payload_path)
    payload_shape_ok = (
        isinstance(payload, dict)
        and {"meta", "blocks", "fields", "semanticFields", "tables"}.issubset(payload.keys())
    )
    state_seed = read_json(state_path)
    state_shape_ok = (
        isinstance(state_seed, dict)
        and {"meta", "blocks", "semanticFields", "tables"}.issubset(state_seed.keys())
        and all(isinstance(value, dict) and isinstance(value.get("cells"), dict) for value in state_seed["tables"].values())
    )

    missing_fonts: list[dict[str, str]] = []
    for face in parse_font_faces(html_text):
        candidate = html_path.parent / face["url"]
        if not candidate.exists():
            missing_fonts.append({"family": face["family"], "url": face["url"]})

    run_status_path = run_root / "metadata" / "run_status.json"
    run_status = read_json(run_status_path) if run_status_path.exists() else {}
    capture_gate_ok = True
    if not run_status.get("capture_assets_found") and run_status.get("review_status") != "conversion-only / review-blocked":
        capture_gate_ok = False

    report = {
        "passed": render_report.get("generation_mode") == "ir-main-direct"
        and all(hook_results.values())
        and not unresolved
        and payload_shape_ok
        and state_shape_ok
        and not missing_fonts
        and capture_gate_ok,
        "generation_mode": render_report.get("generation_mode", "unknown"),
        "generated_from_ir": render_report.get("generation_mode") == "ir-main-direct",
        "required_hooks": hook_results,
        "unresolved_mappings": unresolved,
        "payload_shape_ok": payload_shape_ok,
        "state_shape_ok": state_shape_ok,
        "missing_fonts": missing_fonts,
        "capture_gate_ok": capture_gate_ok,
        "generated_html": relative_to_repo(html_path),
        "generated_payload": relative_to_repo(payload_path),
        "generated_state_seed": relative_to_repo(state_path),
        "oracle_coverage": render_report.get("oracle_coverage", {}),
        "oracle_mismatches_preview": render_report.get("oracle_mismatches_preview", []),
        "remaining_reference_scaffolding": render_report.get("remaining_reference_scaffolding", []),
        "traceability": render_report.get("traceability", {}),
    }
    write_json(metadata_dir / "runtime_contract_verification.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "--manifest", dest="manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    report = run_verify_runtime_contract(manifest, args.run_dir)
    print("PASS" if report["passed"] else "FAIL")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
