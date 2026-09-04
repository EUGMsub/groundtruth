#!/usr/bin/env python3
"""Summarize every .jsonl file in cases/: counts by domain, match type, and tier."""
import glob
import json
import sys
from collections import Counter


def find_case_files():
    return sorted(glob.glob("cases/*.jsonl"))


def load_records(paths):
    records = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    records.append(record)
    return records


def print_table(title, counts):
    print(title)
    width = max((len(str(key)) for key in counts), default=0)
    for key in sorted(counts):
        print(f"  {str(key).ljust(width)}  {counts[key]}")
    print()


def main():
    paths = find_case_files()
    if not paths:
        print("No .jsonl files found in cases/", file=sys.stderr)
        sys.exit(1)

    records = load_records(paths)
    print(f"{len(records)} case(s) found\n")

    print_table("By domain:", Counter(r.get("domain", "(missing)") for r in records))
    print_table("By match type:", Counter(r.get("match", "(missing)") for r in records))
    print_table("By tier:", Counter(r.get("tier", "(missing)") for r in records))


if __name__ == "__main__":
    main()
