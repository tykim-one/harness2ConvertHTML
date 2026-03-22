from __future__ import annotations

import argparse
from pathlib import Path

from harness_utils import copy_file, copy_tree, ensure_dir, load_manifest, relative_to_repo, resolve_manifest_path, write_json


def run_freeze_reference_runtime(manifest: dict, run_dir: str | Path) -> dict:
    run_root = ensure_dir(run_dir)
    source_dir = ensure_dir(run_root / "source")
    reference_dir = ensure_dir(run_root / "reference")
    metadata_dir = ensure_dir(run_root / "metadata")

    source_hwp = resolve_manifest_path(manifest["source"]["hwp"])
    copied_source = copy_file(source_hwp, source_dir / source_hwp.name)

    copied_files: dict[str, str] = {"source_hwp": relative_to_repo(copied_source)}
    reference = manifest["reference"]
    for key in ("html", "shared_css", "fit_css", "fields", "tokens"):
        if reference.get(key):
            src = resolve_manifest_path(reference[key])
            copied = copy_file(src, reference_dir / src.name)
            copied_files[key] = relative_to_repo(copied)

    font_root = resolve_manifest_path(reference["font_root"])
    assets_root = font_root.parent
    copied_assets = copy_tree(assets_root, reference_dir / assets_root.name)
    copied_files["assets_root"] = relative_to_repo(copied_assets)

    report = {
        "run_dir": relative_to_repo(run_root),
        "source_dir": relative_to_repo(source_dir),
        "reference_dir": relative_to_repo(reference_dir),
        "copied_files": copied_files,
    }
    write_json(metadata_dir / "freeze_reference_runtime.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", "--manifest", dest="manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    report = run_freeze_reference_runtime(manifest, args.run_dir)
    print(report["reference_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
