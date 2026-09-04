#!/usr/bin/env python3
"""Compare two graded JSONL runs and show which cases changed pass/fail state."""
import argparse
import json
import re
import sys


def load_graded(path):
    passed_by_id = {}
    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                sys.exit(f"{path}:{line_number}: invalid JSON ({e})")
            passed_by_id[record["id"]] = record["passed"]
    return passed_by_id


def natural_key(case_id):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", case_id)]


def print_list(title, case_ids):
    print(f"{title} ({len(case_ids)})")
    if not case_ids:
        print("  none")
    for case_id in sorted(case_ids, key=natural_key):
        print(f"  {case_id}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Compare two graded JSONL runs by case id.")
    parser.add_argument("old", help="path to the earlier graded JSONL file")
    parser.add_argument("new", help="path to the later graded JSONL file")
    args = parser.parse_args()

    old = load_graded(args.old)
    new = load_graded(args.new)

    common_ids = set(old) & set(new)
    only_old = set(old) - set(new)
    only_new = set(new) - set(old)

    regressions = [i for i in common_ids if old[i] and not new[i]]
    newly_passing = [i for i in common_ids if not old[i] and new[i]]
    still_failing = [i for i in common_ids if not old[i] and not new[i]]

    print(f"Comparing {args.old} -> {args.new}")
    print()
    print_list("REGRESSIONS (newly failing)", regressions)
    print_list("NEWLY PASSING", newly_passing)
    print_list("STILL FAILING (failed in both)", still_failing)

    if only_old or only_new:
        print(f"Note: {len(only_old)} case(s) only in {args.old}, "
              f"{len(only_new)} case(s) only in {args.new} — skipped in comparison.")


if __name__ == "__main__":
    main()
