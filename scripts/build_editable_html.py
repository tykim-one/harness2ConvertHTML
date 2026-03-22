from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from harness_utils import (
    copy_tree,
    load_manifest,
    make_payload_from_fields,
    make_state_seed,
    read_json,
    relative_to_repo,
    resolve_manifest_path,
    table_field_to_cell_ref,
    utc_run_id,
    write_json,
    write_text,
)

MATCH_REPLACEMENTS = str.maketrans({
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "」": ")",
    "「": "(",
})
WHITESPACE_RE = re.compile(r"\s+")


def normalize_match(value: str) -> str:
    return WHITESPACE_RE.sub(" ", html.unescape(value or "").translate(MATCH_REPLACEMENTS)).strip()


def build_ir_candidates(ir: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for paragraph in ir.get("paragraphs", []):
        text = str(paragraph.get("text", ""))
        normalized = normalize_match(text)
        if normalized:
            candidates.append(
                {
                    "text": text,
                    "normalized": normalized,
                    "source": "paragraph",
                    "paragraph_id": paragraph.get("paragraph_id"),
                }
            )
    for table in ir.get("tables", []):
        for row in table.get("rows", []):
            for cell in row.get("cells", []):
                text = str(cell.get("text", ""))
                normalized = normalize_match(text)
                if normalized:
                    candidates.append(
                        {
                            "text": text,
                            "normalized": normalized,
                            "source": "table_cell",
                            "table_index": table.get("table_index"),
                            "row": cell.get("row"),
                            "col": cell.get("col"),
                        }
                    )
    return candidates


def resolve_reference_fields_from_ir(reference_fields: list[dict[str, Any]], ir: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates = build_ir_candidates(ir)
    resolved_fields: list[dict[str, Any]] = []
    derived = 0
    fallback = 0
    fallback_labels: list[str] = []

    for entry in reference_fields:
        reference_value = str(entry.get("value", ""))
        normalized_reference = normalize_match(reference_value)
        chosen = None
        best_score = -1
        best_length_delta = 10**9
        for candidate in candidates:
            normalized_candidate = candidate["normalized"]
            score = -1
            if normalized_candidate == normalized_reference:
                score = 4
            elif normalized_reference and normalized_reference in normalized_candidate:
                score = 3
            elif normalized_candidate and normalized_candidate in normalized_reference:
                score = 2
            if score < 0:
                continue
            length_delta = abs(len(normalized_candidate) - len(normalized_reference))
            if score > best_score or (score == best_score and length_delta < best_length_delta):
                chosen = candidate
                best_score = score
                best_length_delta = length_delta
        resolved_entry = dict(entry)
        if chosen is not None:
            resolved_entry["value"] = chosen["text"]
            resolved_entry["resolved_from_ir"] = True
            resolved_entry["resolved_source"] = chosen["source"]
            derived += 1
        else:
            resolved_entry["resolved_from_ir"] = False
            resolved_entry["resolved_source"] = "oracle_fallback"
            fallback += 1
            fallback_labels.append(
                str(
                    entry.get("label")
                    or entry.get("semantic_field")
                    or entry.get("table_field")
                    or entry.get("block_id")
                    or reference_value
                )
            )
        resolved_fields.append(resolved_entry)

    resolution = {
        "derived_field_count": derived,
        "fallback_field_count": fallback,
        "fallback_labels": fallback_labels[:25],
    }
    return resolved_fields, resolution


def build_table_map(entries: list[dict[str, Any]]) -> tuple[list[str], dict[str, dict[str, Any]]]:
    ordered_table_ids: list[str] = []
    tables: dict[str, dict[str, Any]] = {}
    for entry in entries:
        table_id = entry.get("table_id")
        table_field = entry.get("table_field")
        if not table_id or not table_field:
            continue
        parsed = table_field_to_cell_ref(table_field)
        if not parsed:
            continue
        _, cell_key = parsed
        row_str, col_str = cell_key[1:].split("c")
        row = int(row_str)
        col = int(col_str)
        if table_id not in tables:
            tables[table_id] = {"rows": {}, "order": len(ordered_table_ids)}
            ordered_table_ids.append(table_id)
        tables[table_id]["rows"].setdefault(row, {}).setdefault(col, []).append(entry)
    return ordered_table_ids, tables


def build_main_html(
    resolved_fields: list[dict[str, Any]],
    run_id: str,
    review_status: str,
    resolution: dict[str, Any],
    html_name: str,
    common_css_name: str,
    fit_css_name: str,
) -> str:
    ordered_table_ids, table_map = build_table_map(resolved_fields)
    body_parts: list[str] = []
    emitted_tables: set[str] = set()

    for entry in resolved_fields:
        table_id = entry.get("table_id")
        table_field = entry.get("table_field")
        if table_id and table_field:
            if table_id in emitted_tables:
                continue
            emitted_tables.add(table_id)
            table = table_map.get(table_id, {"rows": {}})
            row_html: list[str] = []
            for row_index in sorted(table["rows"]):
                cells_html: list[str] = []
                for col_index in sorted(table["rows"][row_index]):
                    cell_entries = table["rows"][row_index][col_index]
                    first_entry = cell_entries[0]
                    parsed = table_field_to_cell_ref(first_entry["table_field"])
                    _, cell_key = parsed if parsed else (table_id, f"r{row_index}c{col_index}")
                    cell_blocks: list[str] = []
                    for cell_entry in cell_entries:
                        value = html.escape(str(cell_entry.get("value", ""))) or "&nbsp;"
                        semantic_attr = (
                            f' data-semantic-field="{html.escape(str(cell_entry.get("semantic_field", "")))}"'
                            if cell_entry.get("semantic_field")
                            else ""
                        )
                        cell_blocks.append(
                            "<div class=\"editable-block fi-table-block\" contenteditable=\"true\""
                            " data-block-id=\"{block_id}\" data-table-id=\"{table_id}\" data-cell-key=\"{cell_key}\""
                            " data-table-field=\"{table_field}\"{semantic_attr}>{value}</div>".format(
                                block_id=html.escape(str(cell_entry.get("block_id", ""))),
                                table_id=html.escape(str(table_id)),
                                cell_key=html.escape(cell_key),
                                table_field=html.escape(str(cell_entry.get("table_field", ""))),
                                semantic_attr=semantic_attr,
                                value=value,
                            )
                        )
                    cells_html.append(
                        "<td data-table-id=\"{table_id}\" data-cell-key=\"{cell_key}\">{blocks}</td>".format(
                            table_id=html.escape(str(table_id)),
                            cell_key=html.escape(cell_key),
                            blocks="".join(cell_blocks),
                        )
                    )
                row_html.append(f"<tr>{''.join(cells_html)}</tr>")
            body_parts.append(
                f'<section class="ir-main-table-wrap" data-table-id="{html.escape(str(table_id))}"><table class="fi-table ir-main-table" data-table-id="{html.escape(str(table_id))}">{"".join(row_html)}</table></section>'
            )
            continue

        value = html.escape(str(entry.get("value", ""))) or "&nbsp;"
        semantic_attr = (
            f' data-semantic-field="{html.escape(str(entry.get("semantic_field", "")))}"'
            if entry.get("semantic_field")
            else ""
        )
        body_parts.append(
            "<p class=\"editable-block fi-semantic-block\" contenteditable=\"true\" data-block-id=\"{block_id}\"{semantic_attr}>{value}</p>".format(
                block_id=html.escape(str(entry.get("block_id", ""))),
                semantic_attr=semantic_attr,
                value=value,
            )
        )

    title_entry = next((entry for entry in resolved_fields if entry.get("semantic_field") == "header.title"), None)
    title = str(title_entry.get("value", html_name)) if title_entry else html_name
    meta_json = json.dumps(
        {
            "runId": run_id,
            "reviewStatus": review_status,
            "generationMode": "ir-main",
            "derivedFieldCount": resolution["derived_field_count"],
            "fallbackFieldCount": resolution["fallback_field_count"],
        },
        ensure_ascii=False,
    )

    return f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <title>{html.escape(title)}</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <meta name=\"harness-run-id\" content=\"{html.escape(run_id)}\" />
  <link rel=\"stylesheet\" href=\"{html.escape(common_css_name)}\" />
  <link rel=\"stylesheet\" href=\"{html.escape(fit_css_name)}\" />
  <style>
    body {{ background:#eee; margin:0; padding:16px; }}
    .Paper {{ background:#fff; max-width:1100px; margin:0 auto; padding:24px; box-shadow:0 2px 16px rgba(0,0,0,.08); }}
    .editable-block {{ min-height:1.2em; }}
    .ir-main-table {{ width:100%; border-collapse:collapse; margin:12px 0 24px; }}
    .ir-main-table td {{ border:1px solid #999; padding:6px; vertical-align:top; }}
  </style>
  <style id=\"runtime-font-faces\"></style>
  <script>
    window.DailyIndicatorsTemplate = {meta_json};
    window.applyDailyIndicatorsData = function(payload) {{
      document.querySelectorAll('.editable-block').forEach(function(node) {{
        const blockId = node.dataset.blockId;
        if (blockId && payload.blocks && Object.prototype.hasOwnProperty.call(payload.blocks, blockId)) {{
          node.textContent = payload.blocks[blockId];
          return;
        }}
        const semanticField = node.dataset.semanticField;
        if (semanticField && payload.fields && Object.prototype.hasOwnProperty.call(payload.fields, semanticField)) {{
          node.textContent = payload.fields[semanticField];
          return;
        }}
        const tableId = node.dataset.tableId;
        const cellKey = node.dataset.cellKey;
        if (tableId && cellKey && payload.tables && payload.tables[tableId] && payload.tables[tableId].cells && Object.prototype.hasOwnProperty.call(payload.tables[tableId].cells, cellKey)) {{
          node.textContent = payload.tables[tableId].cells[cellKey];
        }}
      }});
    }};
    window.collectState = function() {{
      const state = {{ meta: {{ source: 'ir-main-generated', runId: '{html.escape(run_id)}' }}, blocks: {{}}, semanticFields: {{}}, tables: {{}} }};
      document.querySelectorAll('.editable-block').forEach(function(node) {{
        const text = (node.textContent || '').trim();
        if (node.dataset.blockId) state.blocks[node.dataset.blockId] = text;
        if (node.dataset.semanticField) state.semanticFields[node.dataset.semanticField] = text;
        if (node.dataset.tableId && node.dataset.cellKey) {{
          if (!state.tables[node.dataset.tableId]) state.tables[node.dataset.tableId] = {{ cells: {{}} }};
          state.tables[node.dataset.tableId].cells[node.dataset.cellKey] = text;
        }}
      }});
      return state;
    }};
    window.addEventListener('DOMContentLoaded', async function () {{
      document.body.setAttribute('data-harness-run-id', '{html.escape(run_id)}');
      document.body.setAttribute('data-harness-review-status', '{html.escape(review_status)}');
      try {{
        const response = await fetch('generated_payload.json');
        if (!response.ok) throw new Error('payload fetch failed: ' + response.status);
        const payload = await response.json();
        window.applyDailyIndicatorsData(payload);
        document.body.setAttribute('data-harness-payload', 'loaded');
      }} catch (error) {{
        document.body.setAttribute('data-harness-payload', 'failed');
        console.error('[harness] payload load failed', error);
      }}
    }});
  </script>
</head>
<body>
  <div class=\"Paper\">{''.join(body_parts)}</div>
</body>
</html>
"""


def run_build_editable_html(manifest: dict, run_dir: str | Path, run_status: dict | None = None) -> dict:
    run_root = resolve_manifest_path(run_dir)
    reference_dir = run_root / "reference"
    generated_dir = run_root / "generated"
    metadata_dir = run_root / "metadata"
    copy_tree(reference_dir, generated_dir)

    html_name = Path(manifest["reference"]["html"]).name
    common_css_name = Path(manifest["reference"]["shared_css"]).name
    fit_css_name = Path(manifest["reference"]["fit_css"]).name
    fields_name = Path(manifest["reference"]["fields"]).name
    html_path = generated_dir / html_name
    ir_path = metadata_dir / "extracted_hwp_ir.json"

    reference_fields = read_json(reference_dir / fields_name)
    ir = read_json(ir_path)
    run_id = (run_status or {}).get("run_id") or utc_run_id()
    review_status = (run_status or {}).get("review_status") or "unknown"

    resolved_fields, resolution = resolve_reference_fields_from_ir(reference_fields, ir)
    payload = make_payload_from_fields(resolved_fields, [])
    payload["meta"] = {
        "runId": run_id,
        "reviewStatus": review_status,
        "generationMode": "ir-main",
        "derivedFieldCount": resolution["derived_field_count"],
        "fallbackFieldCount": resolution["fallback_field_count"],
    }
    payload["semanticFields"] = dict(payload.get("fields", {}))
    state_seed = make_state_seed(run_id, resolved_fields)
    state_seed["meta"].update(
        {
            "reviewStatus": review_status,
            "generationMode": "ir-main",
            "derivedFieldCount": resolution["derived_field_count"],
            "fallbackFieldCount": resolution["fallback_field_count"],
        }
    )

    main_html = build_main_html(
        resolved_fields,
        run_id,
        review_status,
        resolution,
        html_name,
        common_css_name,
        fit_css_name,
    )
    write_json(generated_dir / "generated_payload.json", payload)
    write_json(generated_dir / "generated_state_seed.json", state_seed)
    write_text(html_path, main_html)

    report = {
        "generated_dir": relative_to_repo(generated_dir),
        "generated_html": relative_to_repo(html_path),
        "generated_payload": relative_to_repo(generated_dir / "generated_payload.json"),
        "generated_state_seed": relative_to_repo(generated_dir / "generated_state_seed.json"),
        "generation_mode": "ir-main",
        "derived_field_count": resolution["derived_field_count"],
        "fallback_field_count": resolution["fallback_field_count"],
        "fallback_labels_preview": resolution["fallback_labels"],
    }
    write_json(metadata_dir / "build_editable_html.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "--manifest", dest="manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--run-status")
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    run_status = read_json(args.run_status) if args.run_status else None
    report = run_build_editable_html(manifest, args.run_dir, run_status)
    print(report["generated_html"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
