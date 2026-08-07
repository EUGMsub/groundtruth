#!/usr/bin/env python3
import argparse
import glob
import json
import os
import re
import sys

NUMBER_RE = re.compile(r"-?\d[\d,]*\.?\d*")
NUMBER_TOLERANCE = 0.01


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


def extract_number(text):
    if not text:
        return None
    match = NUMBER_RE.search(text)
    if not match:
        return None
    return float(match.group().replace(",", ""))


def latest_results_file():
    files = sorted(glob.glob("results/*.jsonl"))
    if not files:
        sys.exit("No results/*.jsonl files found. Pass --results path/to/file.jsonl.")
    return files[-1]


def grade_exact(output, expected):
    got, want = normalize(output), normalize(expected)
    if got == want:
        return True, "exact match"
    return False, f"expected '{want}', got '{got}'"


def grade_contains(output, expected):
    got, want = normalize(output), normalize(expected)
    if want in got:
        return True, f"'{want}' found in output"
    return False, f"'{want}' not found in output"


def grade_number(output, expected):
    want_num = extract_number(expected)
    if want_num is None:
        return False, f"case error: no number in expected value '{expected}'"
    got_num = extract_number(output)
    if got_num is None:
        return False, f"no number found in output '{output}'"
    diff = abs(got_num - want_num)
    if diff <= NUMBER_TOLERANCE:
        return True, f"{got_num} within {NUMBER_TOLERANCE} of {want_num}"
    return False, f"{got_num} not within {NUMBER_TOLERANCE} of {want_num} (diff {diff})"


GRADERS = {
    "exact": grade_exact,
    "contains": grade_contains,
    "number": grade_number,
}


def grade_case(case, result):
    if result is None:
        return False, None, "no result recorded for this case"

    match_type = case.get("match")
    grader = GRADERS.get(match_type)
    if grader is None:
        return False, result.get("output"), f"unknown match type '{match_type}'"

    passed, why = grader(result.get("output"), case.get("expected"))
    return passed, result.get("output"), why


def main():
    parser = argparse.ArgumentParser(description="Grade a results file against a cases file.")
    parser.add_argument("--cases", default="cases/starter.jsonl", help="path to the cases JSONL file")
    parser.add_argument("--results", default=None, help="path to the results JSONL file (defaults to the newest file in results/)")
    args = parser.parse_args()

    results_path = args.results or latest_results_file()

    cases = load_jsonl(args.cases)
    results = load_jsonl(results_path)
    results_by_id = {r["id"]: r for r in results}

    # Prefer the run_id recorded on the results themselves (the contract puts
    # it on every line); fall back to the filename if the file is empty.
    run_id = results[0]["run_id"] if results else os.path.splitext(os.path.basename(results_path))[0]

    passed_count = 0
    graded_lines = []
    for case in cases:
        result = results_by_id.get(case["id"])
        passed, got, why = grade_case(case, result)
        if passed:
            passed_count += 1
        graded_lines.append({
            "id": case["id"],
            "run_id": run_id,
            "passed": passed,
            "match": case.get("match"),
            "expected": case.get("expected"),
            "got": got,
            "why": why,
        })

    os.makedirs("graded", exist_ok=True)
    graded_path = os.path.join("graded", f"{run_id}.jsonl")
    with open(graded_path, "w", encoding="utf-8") as f:
        for line in graded_lines:
            f.write(json.dumps(line) + "\n")

    print(f"{passed_count} / {len(cases)} passed")
    print(f"wrote {graded_path}")


if __name__ == "__main__":
    main()
