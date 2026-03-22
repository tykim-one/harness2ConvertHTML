from __future__ import annotations

import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

from harness_utils import load_manifest, read_json, relative_to_repo, resolve_manifest_path, write_json

MATCH_REPLACEMENTS = str.maketrans({
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "」": ")",
    "「": "(",
})
WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    return WHITESPACE_RE.sub(" ", html.unescape(value or "").translate(MATCH_REPLACEMENTS)).strip()


def extract_paragraph_text(paragraph: ET.Element) -> str:
    parts: list[str] = []
    for text_node in paragraph.iter("Text"):
        if text_node.text:
            parts.append(text_node.text)
    return normalize_text("".join(parts))


def extract_charshape_ids(paragraph: ET.Element) -> list[int]:
    ids: list[int] = []
    for text_node in paragraph.iter("Text"):
        value = text_node.attrib.get("charshape-id")
        if value and value.isdigit():
            ids.append(int(value))
    return sorted(set(ids))


def collect_doc_structure(root: ET.Element) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    paragraphs: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    counters = Counter()

    body = root.find("BodyText")
    if body is None:
        return paragraphs, tables, counters

    for section_index, section in enumerate(body.iter("SectionDef")):
        counters["sections"] += 1
        for paragraph in section.iter("Paragraph"):
            paragraph_id = paragraph.attrib.get("paragraph-id", "")
            text = extract_paragraph_text(paragraph)
            record = {
                "section_index": section_index,
                "paragraph_id": paragraph_id,
                "style_id": paragraph.attrib.get("style-id"),
                "parashape_id": paragraph.attrib.get("parashape-id"),
                "charshape_ids": extract_charshape_ids(paragraph),
                "text": text,
                "in_table": bool(list(paragraph.iterfind("ancestor::TableCell"))) if False else False,
            }
            paragraphs.append(record)
            counters["paragraphs"] += 1

        for table_index, table in enumerate(section.iter("TableControl"), start=len(tables)):
            rows: list[dict[str, Any]] = []
            for row_index, row in enumerate(table.iter("TableRow")):
                cells: list[dict[str, Any]] = []
                for cell in row.iter("TableCell"):
                    paragraph_ids = []
                    cell_text_parts = []
                    for paragraph in cell.iter("Paragraph"):
                        paragraph_id = paragraph.attrib.get("paragraph-id", "")
                        if paragraph_id:
                            paragraph_ids.append(paragraph_id)
                        text = extract_paragraph_text(paragraph)
                        if text:
                            cell_text_parts.append(text)
                    cells.append(
                        {
                            "row": int(cell.attrib.get("row", row_index)),
                            "col": int(cell.attrib.get("col", len(cells))),
                            "rowspan": int(cell.attrib.get("rowspan", 1)),
                            "colspan": int(cell.attrib.get("colspan", 1)),
                            "paragraph_ids": paragraph_ids,
                            "text": normalize_text(" ".join(cell_text_parts)),
                        }
                    )
                    counters["table_cells"] += 1
                rows.append({"row_index": row_index, "cells": cells})
                counters["table_rows"] += 1
            tables.append({"table_index": table_index, "rows": rows})
            counters["tables"] += 1

    paragraph_lookup = {entry["paragraph_id"]: entry for entry in paragraphs if entry["paragraph_id"]}
    paragraph_ids_in_tables = {
        paragraph_id
        for table in tables
        for row in table["rows"]
        for cell in row["cells"]
        for paragraph_id in cell["paragraph_ids"]
    }
    for paragraph_id in paragraph_ids_in_tables:
        if paragraph_id in paragraph_lookup:
            paragraph_lookup[paragraph_id]["in_table"] = True

    return paragraphs, tables, dict(counters)


def compute_oracle_coverage(reference_fields: list[dict[str, Any]], paragraphs: list[dict[str, Any]], tables: list[dict[str, Any]]) -> dict[str, Any]:
    paragraph_texts = [normalize_text(entry["text"]) for entry in paragraphs if entry.get("text")]
    cell_texts = [normalize_text(cell["text"]) for table in tables for row in table["rows"] for cell in row["cells"] if cell.get("text")]
    searchable = paragraph_texts + cell_texts

    matched_labels: list[str] = []
    unmatched_labels: list[str] = []
    for entry in reference_fields:
        reference_value = normalize_text(str(entry.get("value", "")))
        if not reference_value:
            continue
        matched = any(reference_value in candidate or candidate in reference_value for candidate in searchable if candidate)
        if matched:
            matched_labels.append(entry.get("label") or entry.get("semantic_field") or entry.get("table_field") or entry.get("block_id") or reference_value)
        else:
            unmatched_labels.append(entry.get("label") or entry.get("semantic_field") or entry.get("table_field") or entry.get("block_id") or reference_value)

    reference_table_ids = sorted({entry["table_id"] for entry in reference_fields if entry.get("table_id")})
    return {
        "reference_field_total": len([entry for entry in reference_fields if normalize_text(str(entry.get("value", "")))]),
        "reference_field_values_matched": len(matched_labels),
        "matched_field_labels": matched_labels,
        "unmatched_field_labels": unmatched_labels,
        "reference_table_ids": reference_table_ids,
        "extracted_table_count": len(tables),
        "extracted_paragraph_count": len(paragraphs),
    }


def run_transform_hwp_xml_to_ir(manifest: dict, run_dir: str | Path) -> dict:
    run_root = resolve_manifest_path(run_dir)
    metadata_dir = run_root / "metadata"
    extracted_xml_path = metadata_dir / "extracted_hwp.xml"
    ir_path = metadata_dir / "extracted_hwp_ir.json"
    schema_path = resolve_manifest_path("harness/samples/260121-major-economy/hwp_ir.schema.json")

    root = ET.parse(extracted_xml_path).getroot()
    paragraphs, tables, doc_counts = collect_doc_structure(root)
    reference_fields = read_json(manifest["reference"]["fields"])
    coverage = compute_oracle_coverage(reference_fields, paragraphs, tables)

    summary_info = {}
    summary = root.find("HwpSummaryInfo")
    if summary is not None:
        for property_node in summary.iter("Property"):
            label = property_node.attrib.get("id-label")
            value = property_node.attrib.get("value")
            if label and value:
                summary_info[label] = value

    ir = {
        "schema_version": "hwp-ir.v1",
        "schema_path": relative_to_repo(schema_path),
        "source": {
            "sample_id": manifest["sample_id"],
            "hwp": relative_to_repo(manifest["source"]["hwp"]),
            "xml_artifact": relative_to_repo(extracted_xml_path),
        },
        "summary_info": summary_info,
        "doc_info": doc_counts,
        "paragraphs": paragraphs,
        "tables": tables,
        "coverage": coverage,
    }
    write_json(ir_path, ir)

    report = {
        "ir_path": relative_to_repo(ir_path),
        "schema_path": relative_to_repo(schema_path),
        "paragraph_count": len(paragraphs),
        "table_count": len(tables),
        "reference_field_values_matched": coverage["reference_field_values_matched"],
        "reference_field_total": coverage["reference_field_total"],
        "unmatched_field_preview": coverage["unmatched_field_labels"][:15],
    }
    write_json(metadata_dir / "transform_hwp_xml_to_ir.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "--manifest", dest="manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    report = run_transform_hwp_xml_to_ir(manifest, args.run_dir)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
