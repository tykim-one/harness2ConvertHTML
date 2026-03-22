from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from harness_utils import (
    build_runtime_index,
    load_manifest,
    parse_font_faces,
    parse_linked_css,
    read_json,
    relative_to_repo,
    resolve_manifest_path,
    write_json,
)


def run_extract_reference_metadata(manifest: dict, run_dir: str | Path) -> dict:
    run_root = resolve_manifest_path(run_dir)
    reference_dir = run_root / "reference"
    metadata_dir = run_root / "metadata"
    html_name = Path(manifest["reference"]["html"]).name
    fields_name = Path(manifest["reference"]["fields"]).name

    html_path = reference_dir / html_name
    fields_path = reference_dir / fields_name
    html_text = html_path.read_text(encoding="utf-8")
    fields = read_json(fields_path)
    runtime_index = build_runtime_index(html_text)
    font_faces = parse_font_faces(html_text)

    hook_counts = {
        "window.DailyIndicatorsTemplate": html_text.count("window.DailyIndicatorsTemplate"),
        "window.applyDailyIndicatorsData": html_text.count("window.applyDailyIndicatorsData"),
        "collectState": html_text.count("collectState"),
        "editable-block-count": len([name for name in runtime_index.classes if name == "editable-block"]),
        "semantic-field-count": len(runtime_index.semantic_fields),
        "table-field-count": len(runtime_index.table_fields),
        "table-cell-count": len(runtime_index.table_cells),
        "block-id-count": len(runtime_index.block_ids),
    }

    table_ids = Counter(entry["table_id"] for entry in fields if entry.get("table_id"))
    metadata = {
        "reference_dir": relative_to_repo(reference_dir),
        "linked_css": parse_linked_css(html_text),
        "font_faces": [
            {
                **face,
                "exists": (html_path.parent / face["url"]).exists(),
            }
            for face in font_faces
        ],
        "runtime_hooks": hook_counts,
        "field_summary": {
            "total": len(fields),
            "semantic_fields": sum(1 for entry in fields if entry.get("semantic_field")),
            "table_fields": sum(1 for entry in fields if entry.get("table_field")),
            "block_ids": sum(1 for entry in fields if entry.get("block_id")),
            "table_ids": dict(table_ids),
        },
    }
    write_json(metadata_dir / "reference_metadata.json", metadata)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "--manifest", dest="manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    metadata = run_extract_reference_metadata(manifest, args.run_dir)
    print(metadata["reference_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
