from __future__ import annotations

import argparse
from pathlib import Path

from harness_utils import read_json, write_json


def run_verify_reference_immutable(before_path: str | Path, after_path: str | Path, output_path: str | Path) -> dict:
    before = read_json(before_path)
    after = read_json(after_path)
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(path for path in before if path in after and before[path] != after[path])
    report = {
        "passed": not (added or removed or changed),
        "added": added,
        "removed": removed,
        "changed": changed,
    }
    write_json(output_path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = run_verify_reference_immutable(args.before, args.after, args.output)
    print("PASS" if report["passed"] else "FAIL")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
