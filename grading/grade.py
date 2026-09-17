#!/usr/bin/env python3
import argparse
import datetime
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

def load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if not sep:
                continue
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


load_dotenv()

# The leading -? can misread a hyphen/en-dash in a range like "9-10" as a
# negative sign, producing -10.0 instead of 10.0. Currently harmless since
# it doesn't affect matching, but worth knowing if a future expected value
# is itself negative.
NUMBER_RE = re.compile(r"-?\d[\d,]*\.?\d*")
NUMBER_TOLERANCE = 0.01
NO_RESULT_REASON = "no result recorded for this case"

JUDGE_MODEL = "claude-haiku-4-5-20251001"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

JUDGE_PROMPT_TEMPLATE = """You are grading a candidate answer against a reference answer for factual correctness.

Question: {prompt}

Reference answer: {expected}

Candidate answer: {output}

Judge the candidate answer strictly. Mark it FAIL if it contains ANY incorrect factual claim, even if the rest of the answer is broadly correct or close to the reference answer. Do not give credit for being "close enough" - a single wrong fact, date, name, number, or causal claim is enough to fail the answer. Only mark it PASS if every factual claim in the candidate answer is correct and consistent with the reference answer.

State your verdict once and do not revise it. Do not reconsider or second-guess your answer after stating it. Your first stated verdict is final.

Respond with exactly one line: the word PASS or FAIL, followed by a single sentence explaining why. Do not include anything else."""


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


def extract_numbers(text):
    """Return every number found in text, in order, as a list of floats.

    Examples:
        extract_numbers("5,280") -> [5280.0]
        extract_numbers("5280 feet") -> [5280.0]
        extract_numbers("growth of 12%") -> [12.0]
        extract_numbers("144 divided by 12 is **12**.") -> [144.0, 12.0, 12.0]
            (confirms markdown bold formatting around numbers doesn't
            interfere with extraction)
    """
    if not text:
        return []
    return [float(m.replace(",", "")) for m in NUMBER_RE.findall(text)]


def extract_number(text):
    numbers = extract_numbers(text)
    return numbers[0] if numbers else None


def latest_results_file():
    files = glob.glob("results/*.jsonl")
    if not files:
        sys.exit("No results/*.jsonl files found. Pass --results path/to/file.jsonl.")
    return max(files, key=os.path.getmtime)


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


# Checks every number in the output, not just the first or last: the model
# may restate the input before answering, or append an unrelated-but-true
# number afterward (a caveat, a citation, a "check my work" aside), and the
# correct answer can land anywhere among those. This can still misfire if a
# wrong number in the output happens to coincide with the expected value,
# but that's rarer than the model producing more than one true number.
def grade_number(output, expected):
    want_num = extract_number(expected)
    if want_num is None:
        return False, f"case error: no number in expected value '{expected}'"
    got_nums = extract_numbers(output)
    if not got_nums:
        return False, f"no number found in output '{output}'"
    for got_num in got_nums:
        if abs(got_num - want_num) <= NUMBER_TOLERANCE:
            return True, f"{got_num} within {NUMBER_TOLERANCE} of {want_num} (matched among {got_nums})"
    return False, f"none of {got_nums} within {NUMBER_TOLERANCE} of {want_num}"


def grade_judge(output, expected, prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return False, "case error: ANTHROPIC_API_KEY not set"

    judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
        prompt=prompt or "(prompt unavailable)",
        expected=expected,
        output=output if output not in (None, "") else "(empty output)",
    )

    body = json.dumps({
        "model": JUDGE_MODEL,
        "max_tokens": 250,
        "messages": [{"role": "user", "content": judge_prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return False, f"judge call failed: {e}"

    verdict = response["content"][0]["text"].strip()
    calls = re.findall(r"\b(PASS|FAIL)\b", verdict, re.IGNORECASE)
    passed = bool(calls) and calls[-1].upper() == "PASS"
    return passed, verdict


GRADERS = {
    "exact": grade_exact,
    "contains": grade_contains,
    "number": grade_number,
}


def grade_case(case, result):
    if result is None:
        return False, None, NO_RESULT_REASON

    match_type = case.get("match")
    output = result.get("output")
    expected = case.get("expected")

    if match_type == "judge":
        passed, why = grade_judge(output, expected, case.get("prompt"))
        return passed, output, why

    grader = GRADERS.get(match_type)
    if grader is None:
        return False, output, f"unknown match type '{match_type}'"

    passed, why = grader(output, expected)
    return passed, output, why


TIER_ORDER = {"easy": 0, "medium": 1, "hard": 2}


# Pass Rate is computed over answered cases only (excludes Not Run), so a
# case that was never run doesn't get silently counted as a failure and
# drag the percentage down — Not Run is shown as its own column instead.
def build_breakdown_table(title, key, description, cases_by_id, graded_lines):
    answered = {}
    passed = {}
    not_run = {}
    for g in graded_lines:
        value = cases_by_id.get(g["id"], {}).get(key, "unknown")
        if g["why"] == NO_RESULT_REASON:
            not_run[value] = not_run.get(value, 0) + 1
            continue
        answered[value] = answered.get(value, 0) + 1
        if g["passed"]:
            passed[value] = passed.get(value, 0) + 1

    all_values = set(answered) | set(not_run)

    def sort_key(value):
        return (TIER_ORDER.get(value, 99), value)

    lines = [f"## Pass Rate by {title}", "", description, ""]
    lines.append(f"| {title} | Passed | Answered | Pass Rate | Not Run |")
    lines.append("|---|---|---|---|---|")
    for value in sorted(all_values, key=sort_key):
        p, a, nr = passed.get(value, 0), answered.get(value, 0), not_run.get(value, 0)
        rate = f"{(p / a * 100):.0f}%" if a else "—"
        lines.append(f"| {value} | {p} | {a} | {rate} | {nr} |")
    lines.append("")
    return lines


def build_report(cases, results_by_id, graded_lines, run_id):
    cases_by_id = {c["id"]: c for c in cases}
    total = len(graded_lines)
    not_run_lines = [g for g in graded_lines if g["why"] == NO_RESULT_REASON]
    answered_count = total - len(not_run_lines)
    passed_count = sum(1 for g in graded_lines if g["passed"])
    pass_rate = (passed_count / answered_count * 100) if answered_count else 0.0
    model = next((r.get("model") for r in results_by_id.values() if r.get("model")), "unknown")
    date = datetime.date.today().isoformat()

    lines = ["# Grading Report", ""]
    lines.append(
        f"**Date:** {date} · **Run:** {run_id} · **Model:** {model} · "
        f"**Pass rate:** {passed_count}/{answered_count} answered ({pass_rate:.0f}%) · "
        f"**Not run:** {len(not_run_lines)}"
    )
    lines.append("")

    lines.extend(build_breakdown_table(
        "Domain", "domain", "Domain = subject area of the question.", cases_by_id, graded_lines))
    lines.extend(build_breakdown_table(
        "Tier", "tier", "Tier = difficulty level assigned when the case was written.", cases_by_id, graded_lines))

    lines.append("## Failures")
    lines.append("")
    failures = [g for g in graded_lines if not g["passed"] and g["why"] != NO_RESULT_REASON]
    if not failures:
        lines.append("None — every answered case passed.")
    for g in failures:
        prompt = cases_by_id.get(g["id"], {}).get("prompt", "(prompt unavailable)")
        got_display = g["got"] if g["got"] not in (None, "") else "(empty output)"
        lines.append(f"### {g['id']}")
        lines.append(f"- Prompt: {prompt}")
        lines.append(f"- Expected: {g['expected']}")
        lines.append(f"- Got: {got_display}")
        lines.append("")

    lines.append("## Not Run")
    lines.append("")
    if not not_run_lines:
        lines.append("None — every case was answered.")
    for g in not_run_lines:
        prompt = cases_by_id.get(g["id"], {}).get("prompt", "(prompt unavailable)")
        lines.append(f"### {g['id']}")
        lines.append(f"- Prompt: {prompt}")
        lines.append(f"- Expected: {g['expected']}")
        lines.append("")

    lines.append("## Cases")
    lines.append("")
    lines.append("| ID | Match | Result |")
    lines.append("|---|---|---|")
    for g in graded_lines:
        if g["why"] == NO_RESULT_REASON:
            mark = "NOT RUN"
        else:
            mark = "PASS" if g["passed"] else "FAIL"
        lines.append(f"| {g['id']} | {g['match']} | {mark} |")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


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

    report_path = "report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(build_report(cases, results_by_id, graded_lines, run_id))

    print(f"{passed_count} / {len(cases)} passed")
    print(f"wrote {graded_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
