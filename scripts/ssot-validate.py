#!/usr/bin/env python3
"""Validate Trade SSOT files, including ref resolution across the config/ssot tree."""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required: pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent
SSOT_DIR = REPO / "config" / "ssot"

# All key suffixes that are treated as references between SSOT files
REF_SUFFIXES = ("_ref", "ref")


def is_ref_key(key):
    return key.endswith(REF_SUFFIXES) and not key.endswith("_href")


def load_all_ssot():
    data = {}
    for path in SSOT_DIR.rglob("*.yml"):
        if path.name == "template.yml":
            continue
        rel = path.relative_to(SSOT_DIR).as_posix()
        try:
            data[rel] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            print(f"YAML_ERROR {rel}: {e}")
            data[rel] = None
    return data


def get_path(obj, path_parts):
    for p in path_parts:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(p)
        if obj is None:
            return None
    return obj


def is_placeholder(ref):
    return "<" in ref or ">" in ref or "..." in ref or "*" in ref or ref.startswith(".")


def resolve_ref(ref, source_file, all_data):
    if ref is None:
        return None
    if is_placeholder(ref):
        return None  # template / placeholder, not validated
    if ref.startswith("/") or ref.startswith(".."):
        return None  # external file, not validated
    if "#" in ref:
        target, _, path = ref.partition("#")
        if not target:
            target = source_file
    elif ".yml" not in ref and "/" not in ref:
        # bare dotted key path in the same file
        target = source_file
        path = ref
    else:
        target = ref
        path = ""

    target = target.removeprefix("config/ssot/").removeprefix("./")
    if target not in all_data:
        return f"missing file: {target}"
    doc = all_data[target]
    if doc is None:
        return f"unparseable file: {target}"
    if path:
        parts = path.split(".")
        value = get_path(doc, parts)
        if value is None:
            return f"missing key '{path}' in {target}"
    return None


def scan_refs(obj, source_file, all_data, found=None):
    if found is None:
        found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if is_ref_key(key) and isinstance(value, (str, list)):
                refs = value if isinstance(value, list) else [value]
                for r in refs:
                    found.append((source_file, key, r))
            else:
                scan_refs(value, source_file, all_data, found)
    elif isinstance(obj, list):
        for item in obj:
            scan_refs(item, source_file, all_data, found)
    return found


def main():
    all_data = load_all_ssot()
    errors = []
    for rel, doc in all_data.items():
        if doc is None:
            continue
        for src_file, key, ref in scan_refs(doc, rel, all_data):
            error = resolve_ref(ref, src_file, all_data)
            if error:
                errors.append(f"{src_file}: {key}={ref} -> {error}")

    if errors:
        print("=== SSOT ref validation errors ===")
        for e in errors:
            print(e)
        print(f"\n{len(errors)} error(s)")
        return 1
    print(f"OK: {len(all_data)} SSOT file(s) parsed; no broken refs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
