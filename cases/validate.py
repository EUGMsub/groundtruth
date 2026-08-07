#!/usr/bin/env python3
"""Validate every .jsonl file in cases/: valid JSON, required keys, unique ids."""
import glob
import json
import sys

REQUIRED_KEYS = ["id", "domain", "prompt", "expected", "match", "tier"]


def find_case_files():
    return sorted(glob.glob("cases/*.jsonl"))


def validate_files(paths):
    problems = []
    seen_ids = {}  # id -> (path, line_number) of first occurrence
    total_cases = 0

    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                total_cases += 1

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    problems.append(f"{path} line {line_number}: invalid JSON ({e})")
                    continue

                if not isinstance(record, dict):
                    problems.append(f"{path} line {line_number}: JSON value is not an object")
                    continue

                for key in REQUIRED_KEYS:
                    if key not in record:
                        problems.append(f"{path} line {line_number}: missing key '{key}'")

                case_id = record.get("id")
                if case_id is not None:
                    if case_id in seen_ids:
                        first_path, first_line = seen_ids[case_id]
                        problems.append(
                            f"{path} line {line_number}: duplicate id '{case_id}' "
                            f"(first seen in {first_path} line {first_line})"
                        )
                    else:
                        seen_ids[case_id] = (path, line_number)

    return total_cases, problems


def main():
    paths = find_case_files()
    if not paths:
        print("No .jsonl files found in cases/", file=sys.stderr)
        sys.exit(1)

    total_cases, problems = validate_files(paths)
    print(f"{total_cases} case(s) found")

    if problems:
        for problem in problems:
            print(problem)
        sys.exit(1)

    print("No problems found.")


if __name__ == "__main__":
    main()
