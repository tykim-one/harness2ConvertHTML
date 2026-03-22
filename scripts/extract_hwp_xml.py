from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from harness_utils import load_manifest, relative_to_repo, resolve_manifest_path, write_json, write_text

DEFAULT_HWP5PROC = ".venv-pyhwp/bin/hwp5proc"


def resolve_hwp5proc_path() -> Path:
    override = os.environ.get("HWP5PROC_PATH", "").strip()
    candidate = override or DEFAULT_HWP5PROC
    path = resolve_manifest_path(candidate)
    if not path.exists():
        raise FileNotFoundError(
            f"hwp5proc not found at {path}. Set HWP5PROC_PATH or install pyhwp into .venv-pyhwp."
        )
    return path


def run_extract_hwp_xml(manifest: dict, run_dir: str | Path) -> dict:
    run_root = resolve_manifest_path(run_dir)
    metadata_dir = run_root / "metadata"
    source_hwp = resolve_manifest_path(manifest["source"]["hwp"])
    copied_source_hwp = run_root / "source" / source_hwp.name
    hwp_path = copied_source_hwp if copied_source_hwp.exists() else source_hwp

    hwp5proc = resolve_hwp5proc_path()
    xml_output = metadata_dir / "extracted_hwp.xml"
    stderr_output = metadata_dir / "extract_hwp_xml.stderr.log"

    command = [str(hwp5proc), "xml", str(hwp_path)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        stderr_output.write_text(result.stderr, encoding="utf-8")
        raise RuntimeError(
            f"hwp5proc xml failed with exit code {result.returncode}. See {relative_to_repo(stderr_output)}"
        )

    write_text(xml_output, result.stdout)
    write_text(stderr_output, result.stderr)

    warnings = [line for line in result.stderr.splitlines() if line.strip()]
    report = {
        "tool": "hwp5proc",
        "command": command,
        "source_hwp": relative_to_repo(hwp_path),
        "extracted_xml": relative_to_repo(xml_output),
        "stderr_log": relative_to_repo(stderr_output),
        "xml_size_bytes": xml_output.stat().st_size,
        "warning_count": len(warnings),
        "warnings_preview": warnings[:10],
    }
    write_json(metadata_dir / "extract_hwp_xml.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "--manifest", dest="manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    report = run_extract_hwp_xml(manifest, args.run_dir)
    print(report["extracted_xml"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
