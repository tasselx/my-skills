#!/usr/bin/env python3
"""Execute batch image renaming from a JSON mapping.

Usage:
    python rename_images.py <directory> <mapping_json>

mapping_json is a JSON string or file path:
    [{"from": "old_name.png", "to": "new_name.png"}, ...]

After renaming, prints results and cleans up the contact sheet if present.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def execute_renames(directory: str, mapping: list[dict]) -> dict:
    results = {"success": [], "skipped": [], "errors": []}
    dir_path = Path(directory)

    for entry in mapping:
        src = dir_path / entry["from"]
        dst = dir_path / entry["to"]

        if not src.exists():
            results["errors"].append({"from": entry["from"], "to": entry["to"], "error": "source not found"})
            continue

        if src.name == dst.name:
            results["skipped"].append({"file": entry["from"], "reason": "name unchanged"})
            continue

        if dst.exists():
            results["errors"].append({"from": entry["from"], "to": entry["to"], "error": "target already exists"})
            continue

        try:
            src.rename(dst)
            results["success"].append({"from": entry["from"], "to": entry["to"]})
        except OSError as e:
            results["errors"].append({"from": entry["from"], "to": entry["to"], "error": str(e)})

    contact_sheet = dir_path / ".contact_sheet.png"
    if contact_sheet.exists():
        contact_sheet.unlink()
        results["cleaned_up"] = ".contact_sheet.png removed"

    return results


def main():
    parser = argparse.ArgumentParser(description="Batch rename images from JSON mapping")
    parser.add_argument("directory", help="Directory containing images")
    parser.add_argument("mapping", help="JSON string or path to JSON file with rename mapping")
    args = parser.parse_args()

    directory = os.path.expanduser(args.directory)
    if not os.path.isdir(directory):
        print(f"ERROR: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    if os.path.isfile(args.mapping):
        with open(args.mapping) as f:
            mapping = json.load(f)
    else:
        mapping = json.loads(args.mapping)

    results = execute_renames(directory, mapping)
    print(json.dumps(results, ensure_ascii=False, indent=2))

    if results["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
