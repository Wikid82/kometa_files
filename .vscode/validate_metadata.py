#!/usr/bin/env python3
"""Validate all Kometa metadata files against kometa-metadata.schema.json.

On-demand full-library sweep for the same structural checks the Red Hat YAML
extension applies live in the editor (catches flattened-indentation bugs where
url_poster/seasons end up as siblings of an item ID instead of nested under it).

Output lines are formatted `path:line: message` so the VS Code problemMatcher
turns them into clickable entries in the Problems tab. Exits non-zero if any
file fails to parse or violates the schema.
"""
import glob
import json
import os
import re
import sys

try:
    import yaml
    from jsonschema import Draft7Validator
except ImportError as e:
    sys.exit(f"Missing dependency: {e.name}. Install with: pip install pyyaml jsonschema")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # kometa_files/
SCHEMA_PATH = os.path.join(HERE, "kometa-metadata.schema.json")


def find_line(path, key):
    """Best-effort: line number where `key:` is defined (1 if not found)."""
    if key is None:
        return 1
    pat = re.compile(r"^\s*" + re.escape(str(key)) + r"\s*:")
    try:
        with open(path, encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                if pat.match(line):
                    return i
    except OSError:
        pass
    return 1


def main():
    validator = Draft7Validator(json.load(open(SCHEMA_PATH)))
    files = glob.glob(os.path.join(ROOT, "libraries", "*", "metadata", "**", "*.yml"),
                      recursive=True)
    print(f"Validating {len(files)} metadata files against kometa-metadata.schema.json\n")

    bad_files = 0
    for f in sorted(files):
        rel = os.path.relpath(f, ROOT)
        try:
            data = yaml.safe_load(open(f, encoding="utf-8"))
        except yaml.YAMLError as e:
            mark = getattr(e, "problem_mark", None)
            line = (mark.line + 1) if mark else 1
            print(f"{rel}:{line}: YAML parse error: {getattr(e, 'problem', e)}")
            bad_files += 1
            continue
        if data is None:
            continue
        errs = sorted(validator.iter_errors(data), key=lambda e: str(list(e.path)))
        if errs:
            bad_files += 1
            for e in errs:
                key = e.path[-1] if e.path else None
                where = "/".join(str(p) for p in e.path) or "(root)"
                print(f"{rel}:{find_line(f, key)}: at metadata/{where}: {e.message}")

    print(f"\n=== {bad_files} of {len(files)} files have problems ===")
    sys.exit(1 if bad_files else 0)


if __name__ == "__main__":
    main()
