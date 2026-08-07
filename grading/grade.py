#!/usr/bin/env python3
import argparse
import glob
import json
import sys


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                sys.exit(f"{path}:{line_number}: invalid JSON ({e})")
    return records


def normalize(text):
    return (text or "").strip().lower()


def latest_results_file():
    files = sorted(glob.glob("results/*.jsonl"))
    if not files:
        sys.exit("No results/*.jsonl files found. Pass --results path/to/file.jsonl.")
    return files[-1]


def main():
    parser = argparse.ArgumentParser(description="Grade a results file against a cases file.")
    parser.add_argument("--cases", default="cases/starter.jsonl", help="path to the cases JSONL file")
    parser.add_argument("--results", default=None, help="path to the results JSONL file (defaults to the newest file in results/)")
    args = parser.parse_args()

    results_path = args.results or latest_results_file()

    cases = load_jsonl(args.cases)
    results = load_jsonl(results_path)

    # A dict keyed by id turns "find the result for this case" into a single
    # lookup instead of rescanning the whole results list for every case.
    results_by_id = {r["id"]: r for r in results}

    passed = 0
    unmatched = 0
    for case in cases:
        result = results_by_id.get(case["id"])
        if result is None:
            unmatched += 1
            continue
        if normalize(result.get("output")) == normalize(case.get("expected")):
            passed += 1

    if unmatched:
        print(f"note: {unmatched} case(s) had no matching result in {results_path} and were counted as failed", file=sys.stderr)

    print(f"{passed} / {len(cases)} passed")


if __name__ == "__main__":
    main()
