from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def ensure_dir(path: str | Path) -> Path:
    resolved = repo_path(path)
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def read_json(path: str | Path) -> Any:
    return json.loads(repo_path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: Any) -> Path:
    target = repo_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def write_text(path: str | Path, content: str) -> Path:
    target = repo_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with repo_path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_tree_hashes(root: str | Path) -> dict[str, str]:
    resolved = repo_path(root)
    if not resolved.exists():
        return {}
    results: dict[str, str] = {}
    for file_path in sorted(p for p in resolved.rglob("*") if p.is_file()):
        results[str(file_path.relative_to(resolved))] = sha256_file(file_path)
    return results


def copy_file(src: str | Path, dest: str | Path) -> Path:
    source = repo_path(src)
    target = repo_path(dest)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def copy_tree(src: str | Path, dest: str | Path) -> Path:
    source = repo_path(src)
    target = repo_path(dest)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return target


def load_manifest(path: str | Path) -> dict[str, Any]:
    manifest = read_json(path)
    manifest["_manifest_path"] = str(repo_path(path))
    return manifest


def relative_to_repo(path: str | Path) -> str:
    return str(repo_path(path).relative_to(REPO_ROOT))


def parse_font_faces(html_text: str) -> list[dict[str, str]]:
    matches = re.finditer(
        r'@font-face\{font-family:"([^"]+)";src:url\("([^"]+)"\)(?: format\("([^"]+)"\))?',
        html_text,
    )
    faces: list[dict[str, str]] = []
    for match in matches:
        faces.append(
            {
                "family": match.group(1),
                "url": match.group(2),
                "format": match.group(3) or "",
            }
        )
    return faces


def parse_linked_css(html_text: str) -> list[str]:
    return re.findall(r'<link[^>]+href="([^"]+)"', html_text)


def table_field_to_cell_ref(table_field: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"tables\.([^.]+)\.(r\d+c\d+)", table_field)
    if not match:
        return None
    return match.group(1), match.group(2)


@dataclass
class RuntimeIndex:
    semantic_fields: set[str]
    table_fields: set[str]
    table_cells: set[tuple[str, str]]
    block_ids: set[str]
    ids: set[str]
    classes: set[str]


class RuntimeIndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.semantic_fields: set[str] = set()
        self.table_fields: set[str] = set()
        self.table_cells: set[tuple[str, str]] = set()
        self.block_ids: set[str] = set()
        self.ids: set[str] = set()
        self.classes: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if attr_map.get("data-semantic-field"):
            self.semantic_fields.add(attr_map["data-semantic-field"])
        if attr_map.get("data-table-field"):
            self.table_fields.add(attr_map["data-table-field"])
        if attr_map.get("data-table-id") and attr_map.get("data-cell-key"):
            self.table_cells.add((attr_map["data-table-id"], attr_map["data-cell-key"]))
        if attr_map.get("data-block-id"):
            self.block_ids.add(attr_map["data-block-id"])
        if attr_map.get("id"):
            self.ids.add(attr_map["id"])
        if attr_map.get("class"):
            for class_name in attr_map["class"].split():
                if class_name:
                    self.classes.add(class_name)

    def as_index(self) -> RuntimeIndex:
        return RuntimeIndex(
            semantic_fields=self.semantic_fields,
            table_fields=self.table_fields,
            table_cells=self.table_cells,
            block_ids=self.block_ids,
            ids=self.ids,
            classes=self.classes,
        )


def build_runtime_index(html_text: str) -> RuntimeIndex:
    parser = RuntimeIndexParser()
    parser.feed(html_text)
    return parser.as_index()


def resolve_manifest_path(value: str) -> Path:
    return repo_path(value)


def make_payload_from_fields(extracted_fields: list[dict[str, Any]], font_faces: list[dict[str, str]]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "fields": {},
        "blocks": {},
        "tables": {},
        "fonts": {"faces": {}},
    }
    for entry in extracted_fields:
        value = entry.get("value", "")
        semantic_field = entry.get("semantic_field")
        block_id = entry.get("block_id")
        table_field = entry.get("table_field")
        table_id = entry.get("table_id")
        if semantic_field:
            payload["fields"][semantic_field] = value
        if block_id:
            payload["blocks"][block_id] = value
        if table_field and table_id:
            cell_ref = table_field_to_cell_ref(table_field)
            if cell_ref:
                _, cell_key = cell_ref
                payload["tables"].setdefault(table_id, {"cells": {}})
                payload["tables"][table_id]["cells"][cell_key] = value
    for face in font_faces:
        payload["fonts"]["faces"].setdefault(face["family"], [])
        item: dict[str, str] = {"url": face["url"]}
        if face.get("format"):
            item["format"] = face["format"]
        payload["fonts"]["faces"][face["family"]].append(item)
    return payload


def make_state_seed(run_id: str, extracted_fields: list[dict[str, Any]]) -> dict[str, Any]:
    state: dict[str, Any] = {
        "meta": {"runId": run_id, "source": "harness-seed"},
        "blocks": {},
        "semanticFields": {},
        "tables": {},
    }
    for entry in extracted_fields:
        value = entry.get("value", "")
        if entry.get("block_id"):
            state["blocks"][entry["block_id"]] = value
        if entry.get("semantic_field"):
            state["semanticFields"][entry["semantic_field"]] = value
        if entry.get("table_id") and entry.get("table_field"):
            cell_ref = table_field_to_cell_ref(entry["table_field"])
            if cell_ref:
                _, cell_key = cell_ref
                state["tables"].setdefault(entry["table_id"], {"cells": {}})
                state["tables"][entry["table_id"]]["cells"][cell_key] = value
    return state
