from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

from harness_utils import (
    load_manifest,
    read_json,
    relative_to_repo,
    resolve_manifest_path,
    table_field_to_cell_ref,
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


def label_for_entry(entry: dict[str, Any]) -> str:
    return str(
        entry.get("label")
        or entry.get("semantic_field")
        or entry.get("table_field")
        or entry.get("block_id")
        or entry.get("value")
        or "unknown"
    )


def build_visible_paragraphs(ir: dict[str, Any]) -> list[dict[str, Any]]:
    paragraphs: list[dict[str, Any]] = []
    for index, entry in enumerate(ir.get("paragraphs", [])):
        text = str(entry.get("text", "")).strip()
        if not text or entry.get("in_table"):
            continue
        paragraph_id = str(entry.get("paragraph_id") or index)
        block_id = f"ir-paragraph:{paragraph_id}"
        paragraphs.append(
            {
                **entry,
                "text": text,
                "block_id": block_id,
                "candidate_id": f"candidate:{block_id}",
            }
        )
    return paragraphs


def build_visible_tables(ir: dict[str, Any]) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    for table in ir.get("tables", []):
        table_index = int(table.get("table_index", len(tables)))
        table_id = f"ir-table-{table_index}"
        rows: list[dict[str, Any]] = []
        for row_index, row in enumerate(table.get("rows", [])):
            cells: list[dict[str, Any]] = []
            for col_index, cell in enumerate(row.get("cells", [])):
                row_number = int(cell.get("row", row_index))
                col_number = int(cell.get("col", col_index))
                cell_key = f"r{row_number}c{col_number}"
                block_id = f"{table_id}:{cell_key}"
                cells.append(
                    {
                        **cell,
                        "row": row_number,
                        "col": col_number,
                        "cell_key": cell_key,
                        "table_id": table_id,
                        "table_index": table_index,
                        "block_id": block_id,
                        "candidate_id": f"candidate:{block_id}",
                        "text": str(cell.get("text", "")).strip(),
                    }
                )
            rows.append({"row_index": int(row.get("row_index", row_index)), "cells": cells})
        tables.append({"table_index": table_index, "table_id": table_id, "rows": rows})
    return tables


def build_ir_candidates(
    paragraphs: list[dict[str, Any]],
    tables: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        normalized = normalize_match(paragraph["text"])
        if not normalized:
            continue
        candidates.append(
            {
                "candidate_id": paragraph["candidate_id"],
                "kind": "paragraph",
                "block_id": paragraph["block_id"],
                "text": paragraph["text"],
                "normalized": normalized,
                "paragraph_id": paragraph.get("paragraph_id"),
            }
        )
    for table in tables:
        for row in table["rows"]:
            for cell in row["cells"]:
                normalized = normalize_match(cell["text"])
                if not normalized:
                    continue
                candidates.append(
                    {
                        "candidate_id": cell["candidate_id"],
                        "kind": "table_cell",
                        "block_id": cell["block_id"],
                        "text": cell["text"],
                        "normalized": normalized,
                        "table_id": cell["table_id"],
                        "cell_key": cell["cell_key"],
                    }
                )
    return candidates


def resolve_reference_fields(
    reference_fields: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, list[str]], dict[str, Any], list[dict[str, Any]]]:
    resolved_fields: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    candidate_semantics: dict[str, list[str]] = {}
    nonempty_total = 0

    for entry in reference_fields:
        reference_value = str(entry.get("value", ""))
        normalized_reference = normalize_match(reference_value)
        if not normalized_reference:
            continue
        nonempty_total += 1
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

        if chosen is None:
            mismatches.append(
                {
                    "label": label_for_entry(entry),
                    "semantic_field": entry.get("semantic_field"),
                    "table_field": entry.get("table_field"),
                    "block_id": entry.get("block_id"),
                    "reference_value": reference_value,
                }
            )
            continue

        resolved = {
            **entry,
            "resolved_from_ir": True,
            "resolved_source": chosen["kind"],
            "resolved_candidate_id": chosen["candidate_id"],
            "resolved_block_id": chosen["block_id"],
            "resolved_value": chosen["text"],
            "resolved_table_id": chosen.get("table_id"),
            "resolved_cell_key": chosen.get("cell_key"),
            "proxy_block_id": str(entry.get("block_id") or f"oracle-proxy:{len(resolved_fields)}"),
        }
        resolved_fields.append(resolved)
        if entry.get("semantic_field"):
            candidate_semantics.setdefault(chosen["candidate_id"], []).append(str(entry["semantic_field"]))

    oracle_coverage = {
        "reference_field_total": nonempty_total,
        "matched_field_count": len(resolved_fields),
        "mismatch_count": len(mismatches),
        "matched_semantic_field_count": sum(1 for entry in resolved_fields if entry.get("semantic_field")),
        "matched_table_field_count": sum(1 for entry in resolved_fields if entry.get("table_field")),
    }
    return resolved_fields, candidate_semantics, oracle_coverage, mismatches


def build_runtime_payload_state(
    *,
    paragraphs: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    resolved_fields: list[dict[str, Any]],
    run_id: str,
    review_status: str,
    traceability: dict[str, str],
    oracle_coverage: dict[str, Any],
    remaining_reference_scaffolding: list[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    meta = {
        "runId": run_id,
        "reviewStatus": review_status,
        "generationMode": "ir-main-direct",
        "traceability": traceability,
        "oracleCoverage": oracle_coverage,
        "remainingReferenceScaffolding": remaining_reference_scaffolding,
    }
    payload: dict[str, Any] = {
        "meta": meta,
        "fields": {},
        "semanticFields": {},
        "blocks": {},
        "tables": {},
        "fonts": {"faces": {}},
    }
    state_seed: dict[str, Any] = {
        "meta": {**meta, "source": "ir-main-direct"},
        "blocks": {},
        "semanticFields": {},
        "tables": {},
    }

    for paragraph in paragraphs:
        value = paragraph["text"]
        payload["blocks"][paragraph["block_id"]] = value
        state_seed["blocks"][paragraph["block_id"]] = value

    for table in tables:
        payload["tables"].setdefault(table["table_id"], {"cells": {}})
        state_seed["tables"].setdefault(table["table_id"], {"cells": {}})
        for row in table["rows"]:
            for cell in row["cells"]:
                value = cell["text"]
                payload["blocks"][cell["block_id"]] = value
                state_seed["blocks"][cell["block_id"]] = value
                payload["tables"][table["table_id"]]["cells"][cell["cell_key"]] = value
                state_seed["tables"][table["table_id"]]["cells"][cell["cell_key"]] = value

    for resolved in resolved_fields:
        value = resolved["resolved_value"]
        proxy_block_id = resolved["proxy_block_id"]
        payload["blocks"][proxy_block_id] = value
        state_seed["blocks"][proxy_block_id] = value

        semantic_field = resolved.get("semantic_field")
        if semantic_field:
            payload["fields"][semantic_field] = value
            payload["semanticFields"][semantic_field] = value
            state_seed["semanticFields"][semantic_field] = value

        table_field = resolved.get("table_field")
        if table_field:
            parsed = table_field_to_cell_ref(str(table_field))
            if parsed:
                table_id, cell_key = parsed
                payload["tables"].setdefault(table_id, {"cells": {}})
                state_seed["tables"].setdefault(table_id, {"cells": {}})
                payload["tables"][table_id]["cells"][cell_key] = value
                state_seed["tables"][table_id]["cells"][cell_key] = value

    return payload, state_seed


def render_preview(ir: dict[str, Any], reference_fields: list[dict[str, Any]]) -> str:
    title = ir.get("summary_info", {}).get("PIDSI_TITLE", "Direct HWP Extraction Preview")
    paragraphs = ir.get("paragraphs", [])
    tables = ir.get("tables", [])
    coverage = ir.get("coverage", {})

    paragraph_items = []
    for entry in paragraphs[:40]:
        text = html.escape(entry.get("text", ""))
        if not text:
            continue
        paragraph_items.append(
            f'<p class="ir-paragraph" data-paragraph-id="{entry.get("paragraph_id", "")}" contenteditable="true">{text}</p>'
        )

    table_sections = []
    for table in tables[:8]:
        rows_html = []
        for row in table.get("rows", []):
            cells_html = []
            for cell in row.get("cells", []):
                cell_text = html.escape(cell.get("text", "")) or "&nbsp;"
                data_cell_key = f'r{cell.get("row", 0)}c{cell.get("col", 0)}'
                cells_html.append(
                    f'<td data-table-id="table_{table.get("table_index", 0)}" data-cell-key="{data_cell_key}" contenteditable="true">{cell_text}</td>'
                )
            rows_html.append(f"<tr>{''.join(cells_html)}</tr>")
        table_sections.append(
            f'<section class="ir-table-wrap"><h2>Extracted Table {table.get("table_index", 0)}</h2><table class="ir-table">{"".join(rows_html)}</table></section>'
        )

    matched = coverage.get("reference_field_values_matched", 0)
    total = coverage.get("reference_field_total", 0)
    unmatched = coverage.get("unmatched_field_labels", [])[:20]
    unmatched_html = "".join(f"<li>{html.escape(str(item))}</li>" for item in unmatched)
    semantic_bindings = [entry for entry in reference_fields if entry.get("semantic_field")][:20]
    binding_html = "".join(
        f'<li data-semantic-field="{html.escape(entry.get("semantic_field", ""))}">{html.escape(str(entry.get("value", "")))}</li>'
        for entry in semantic_bindings
    )

    return f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <title>{html.escape(str(title))}</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <style>
    body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 24px; background: #f4f4f4; color: #111; }}
    .page {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 24px; box-shadow: 0 2px 16px rgba(0,0,0,.08); }}
    .meta {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-bottom: 24px; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 12px; background: #fafafa; }}
    .ir-paragraph {{ margin: 0 0 10px; line-height: 1.5; }}
    .ir-table-wrap {{ margin-top: 24px; overflow-x: auto; }}
    .ir-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    .ir-table td {{ border: 1px solid #999; padding: 6px; vertical-align: top; }}
    .ir-bindings {{ margin-top: 24px; }}
  </style>
  <script>
    window.collectState = function () {{
      return {{
        meta: {{ source: 'direct-hwp-preview' }},
        blocks: {{}},
        semanticFields: {{}},
        tables: {{}}
      }};
    }};
  </script>
</head>
<body>
  <main class=\"page\">
    <h1>{html.escape(str(title))}</h1>
    <div class=\"meta\">
      <div class=\"card\"><strong>Paragraphs</strong><div>{len(paragraphs)}</div></div>
      <div class=\"card\"><strong>Tables</strong><div>{len(tables)}</div></div>
      <div class=\"card\"><strong>Oracle coverage</strong><div>{matched} / {total}</div></div>
    </div>
    <section class=\"ir-text\">{''.join(paragraph_items)}</section>
    {''.join(table_sections)}
    <section class=\"ir-bindings\">
      <h2>Oracle semantic field sample</h2>
      <ul>{binding_html}</ul>
      <h2>Unmatched oracle labels (preview)</h2>
      <ul>{unmatched_html or '<li>none</li>'}</ul>
    </section>
  </main>
</body>
</html>
"""


def build_main_html(
    *,
    title: str,
    paragraphs: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    resolved_fields: list[dict[str, Any]],
    candidate_semantics: dict[str, list[str]],
    run_id: str,
    review_status: str,
    common_css_name: str,
    fit_css_name: str,
    meta_payload: dict[str, Any],
    oracle_coverage: dict[str, Any],
    mismatches: list[dict[str, Any]],
    remaining_reference_scaffolding: list[str],
    traceability: dict[str, str],
) -> str:
    body_parts: list[str] = []
    for paragraph in paragraphs:
        semantic_fields = candidate_semantics.get(paragraph["candidate_id"], [])
        semantic_attr = ""
        if len(semantic_fields) == 1:
            semantic_attr = f' data-semantic-field="{html.escape(semantic_fields[0])}"'
        body_parts.append(
            "<p class=\"editable-block ir-paragraph-block\" contenteditable=\"true\""
            " data-block-id=\"{block_id}\" data-ir-paragraph-id=\"{paragraph_id}\"{semantic_attr}>{value}</p>".format(
                block_id=html.escape(paragraph["block_id"]),
                paragraph_id=html.escape(str(paragraph.get("paragraph_id", ""))),
                semantic_attr=semantic_attr,
                value=html.escape(paragraph["text"]) or "&nbsp;",
            )
        )

    for table in tables:
        row_html: list[str] = []
        for row in table["rows"]:
            cells_html: list[str] = []
            for cell in row["cells"]:
                semantic_fields = candidate_semantics.get(cell["candidate_id"], [])
                semantic_attr = ""
                if len(semantic_fields) == 1:
                    semantic_attr = f' data-semantic-field="{html.escape(semantic_fields[0])}"'
                cells_html.append(
                    "<td data-table-id=\"{table_id}\" data-cell-key=\"{cell_key}\">"
                    "<div class=\"editable-block ir-table-cell-block\" contenteditable=\"true\""
                    " data-block-id=\"{block_id}\" data-table-id=\"{table_id}\" data-cell-key=\"{cell_key}\""
                    " data-table-field=\"tables.{table_id}.{cell_key}\"{semantic_attr}>{value}</div>"
                    "</td>".format(
                        table_id=html.escape(table["table_id"]),
                        cell_key=html.escape(cell["cell_key"]),
                        block_id=html.escape(cell["block_id"]),
                        semantic_attr=semantic_attr,
                        value=html.escape(cell["text"]) or "&nbsp;",
                    )
                )
            row_html.append(f"<tr>{''.join(cells_html)}</tr>")
        body_parts.append(
            f'<section class="ir-main-table-wrap" data-ir-table-index="{table["table_index"]}"><table class="fi-table ir-main-table" data-table-id="{html.escape(table["table_id"])}">{"".join(row_html)}</table></section>'
        )

    proxy_nodes: list[str] = []
    for index, resolved in enumerate(resolved_fields):
        attrs = [
            'class="editable-block runtime-contract-proxy"',
            'contenteditable="true"',
            'hidden',
            f'data-block-id="{html.escape(resolved["proxy_block_id"])}"',
            f'data-oracle-label="{html.escape(label_for_entry(resolved))}"',
            f'data-oracle-source="{html.escape(resolved["resolved_source"])}"',
        ]
        semantic_field = resolved.get("semantic_field")
        if semantic_field:
            attrs.append(f'data-semantic-field="{html.escape(str(semantic_field))}"')
        table_field = resolved.get("table_field")
        if table_field:
            parsed = table_field_to_cell_ref(str(table_field))
            if parsed:
                table_id, cell_key = parsed
                attrs.append(f'data-table-id="{html.escape(table_id)}"')
                attrs.append(f'data-cell-key="{html.escape(cell_key)}"')
                attrs.append(f'data-table-field="{html.escape(str(table_field))}"')
        proxy_nodes.append(
            "<div {attrs}>{value}</div>".format(
                attrs=" ".join(attrs),
                value=html.escape(resolved["resolved_value"]) or "&nbsp;",
            )
        )

    notes = remaining_reference_scaffolding + [
        f"Oracle mismatches currently visible: {len(mismatches)}",
    ]
    note_html = "".join(f"<li>{html.escape(note)}</li>" for note in notes)
    mismatch_preview = "".join(
        f"<li>{html.escape(item['label'])}</li>" for item in mismatches[:10]
    )
    traceability_json = json.dumps(traceability, ensure_ascii=False)
    template_meta = json.dumps(meta_payload, ensure_ascii=False)

    return f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <title>{html.escape(title)}</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <meta name=\"harness-run-id\" content=\"{html.escape(run_id)}\" />
  <meta name=\"harness-generation-mode\" content=\"ir-main-direct\" />
  <meta name=\"harness-ir-artifact\" content=\"{html.escape(traceability['ir'])}\" />
  <meta name=\"harness-xml-artifact\" content=\"{html.escape(traceability['extracted_xml'])}\" />
  <link rel=\"stylesheet\" href=\"{html.escape(common_css_name)}\" />
  <link rel=\"stylesheet\" href=\"{html.escape(fit_css_name)}\" />
  <style>
    body {{ background:#eee; margin:0; padding:16px; }}
    .Paper {{ background:#fff; max-width:1100px; margin:0 auto; padding:24px; box-shadow:0 2px 16px rgba(0,0,0,.08); }}
    .editable-block {{ min-height:1.2em; }}
    .ir-main-meta {{ display:grid; gap:12px; grid-template-columns:repeat(4,minmax(0,1fr)); margin-bottom:20px; }}
    .ir-main-card {{ border:1px solid #ddd; border-radius:8px; padding:12px; background:#fafafa; }}
    .ir-main-table {{ width:100%; border-collapse:collapse; margin:12px 0 24px; }}
    .ir-main-table td {{ border:1px solid #999; padding:6px; vertical-align:top; }}
    .ir-main-notes {{ margin:24px 0; }}
    .runtime-contract-proxy {{ display:none; }}
  </style>
  <style id=\"runtime-font-faces\"></style>
  <script type=\"application/json\" id=\"ir-traceability\">{html.escape(traceability_json)}</script>
  <script>
    window.DailyIndicatorsTemplate = {template_meta};
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
      const state = {{ meta: {{ source: 'ir-main-direct', runId: '{html.escape(run_id)}' }}, blocks: {{}}, semanticFields: {{}}, tables: {{}} }};
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
      document.body.setAttribute('data-harness-generation-mode', 'ir-main-direct');
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
  <div class=\"Paper\">
    <h1>{html.escape(title)}</h1>
    <div class=\"ir-main-meta\">
      <div class=\"ir-main-card\"><strong>Paragraphs</strong><div>{len(paragraphs)}</div></div>
      <div class=\"ir-main-card\"><strong>Tables</strong><div>{len(tables)}</div></div>
      <div class=\"ir-main-card\"><strong>Oracle matched</strong><div>{oracle_coverage['matched_field_count']} / {oracle_coverage['reference_field_total']}</div></div>
      <div class=\"ir-main-card\"><strong>Review status</strong><div>{html.escape(review_status)}</div></div>
    </div>
    <section class=\"ir-main-notes\">
      <h2>IR main-path notes</h2>
      <ul>{note_html}</ul>
      <h3>Oracle mismatch preview</h3>
      <ul>{mismatch_preview or '<li>none</li>'}</ul>
    </section>
    <section class=\"ir-main-content\">{''.join(body_parts)}</section>
    <section id=\"runtime-contract-proxies\" hidden aria-hidden=\"true\">{''.join(proxy_nodes)}</section>
  </div>
</body>
</html>
"""


def run_render_ir_to_html(manifest: dict, run_dir: str | Path, run_status: dict[str, Any] | None = None) -> dict[str, Any]:
    run_root = resolve_manifest_path(run_dir)
    generated_dir = run_root / "generated"
    metadata_dir = run_root / "metadata"
    ir_path = metadata_dir / "extracted_hwp_ir.json"
    xml_path = metadata_dir / "extracted_hwp.xml"
    html_name = Path(manifest["reference"]["html"]).name
    common_css_name = Path(manifest["reference"]["shared_css"]).name
    fit_css_name = Path(manifest["reference"]["fit_css"]).name
    preview_html_path = generated_dir / "direct_hwp_extraction_preview.html"
    preview_payload_path = generated_dir / "direct_hwp_extraction_preview.json"
    main_html_path = generated_dir / html_name
    main_payload_path = generated_dir / "generated_payload.json"
    main_state_path = generated_dir / "generated_state_seed.json"
    oracle_resolution_path = metadata_dir / "oracle_runtime_resolution.json"

    ir = read_json(ir_path)
    reference_fields = read_json(manifest["reference"]["fields"])
    run_id = (run_status or {}).get("run_id") or main_html_path.parent.name
    review_status = (run_status or {}).get("review_status") or "unknown"
    paragraphs = build_visible_paragraphs(ir)
    tables = build_visible_tables(ir)
    candidates = build_ir_candidates(paragraphs, tables)
    resolved_fields, candidate_semantics, oracle_coverage, mismatches = resolve_reference_fields(reference_fields, candidates)
    traceability = {
        "extracted_xml": relative_to_repo(xml_path),
        "ir": relative_to_repo(ir_path),
        "renderer": relative_to_repo(Path(__file__)),
    }
    remaining_reference_scaffolding = [
        "Common/fitted CSS and font assets are still staged from the frozen reference bundle.",
        "Oracle coverage currently uses today_major_economy/extracted_fields.json for mismatch reporting.",
    ]
    payload, state_seed = build_runtime_payload_state(
        paragraphs=paragraphs,
        tables=tables,
        resolved_fields=resolved_fields,
        run_id=run_id,
        review_status=review_status,
        traceability=traceability,
        oracle_coverage=oracle_coverage,
        remaining_reference_scaffolding=remaining_reference_scaffolding,
    )

    title = ir.get("summary_info", {}).get("PIDSI_TITLE", "Direct HWP Extraction")
    preview_html = render_preview(ir, reference_fields)
    main_html = build_main_html(
        title=str(title),
        paragraphs=paragraphs,
        tables=tables,
        resolved_fields=resolved_fields,
        candidate_semantics=candidate_semantics,
        run_id=run_id,
        review_status=review_status,
        common_css_name=common_css_name,
        fit_css_name=fit_css_name,
        meta_payload=payload["meta"],
        oracle_coverage=oracle_coverage,
        mismatches=mismatches,
        remaining_reference_scaffolding=remaining_reference_scaffolding,
        traceability=traceability,
    )

    write_text(preview_html_path, preview_html)
    write_json(
        preview_payload_path,
        {
            "schema_version": ir.get("schema_version"),
            "paragraph_count": len(paragraphs),
            "table_count": len(tables),
            "coverage": ir.get("coverage", {}),
            "oracle_coverage": oracle_coverage,
            "oracle_mismatches_preview": mismatches[:25],
        },
    )
    write_text(main_html_path, main_html)
    write_json(main_payload_path, payload)
    write_json(main_state_path, state_seed)
    write_json(
        oracle_resolution_path,
        {
            "schema_version": "oracle-runtime-resolution.v1",
            "oracle_coverage": oracle_coverage,
            "resolved_fields": resolved_fields,
            "mismatches": mismatches,
        },
    )

    report = {
        "generation_mode": "ir-main-direct",
        "main_generated_html": relative_to_repo(main_html_path),
        "main_generated_payload": relative_to_repo(main_payload_path),
        "main_generated_state_seed": relative_to_repo(main_state_path),
        "preview_html": relative_to_repo(preview_html_path),
        "preview_payload": relative_to_repo(preview_payload_path),
        "oracle_resolution": relative_to_repo(oracle_resolution_path),
        "traceability": traceability,
        "oracle_coverage": oracle_coverage,
        "oracle_mismatches_preview": mismatches[:25],
        "remaining_reference_scaffolding": remaining_reference_scaffolding,
    }
    write_json(metadata_dir / "render_ir_to_html.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "--manifest", dest="manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--run-status")
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    run_status = read_json(args.run_status) if args.run_status else None
    report = run_render_ir_to_html(manifest, args.run_dir, run_status)
    print(report["main_generated_html"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
