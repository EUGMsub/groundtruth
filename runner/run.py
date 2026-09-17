import json
import argparse
from datetime import date
import os
import sys
import time
import uuid

import anthropic

LIVE_MODEL = "claude-sonnet-4-6"
LIVE_CALL_PAUSE_SECONDS = 1


def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

def read_cases(filepath):
    cases = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                case = json.loads(line)
                cases.append(case)
    return cases

def filter_cases(cases, filter_arg):
    field, _, value = filter_arg.partition("=")
    if not _:
        raise ValueError(f"--filter must be field=value, got: {filter_arg!r}")
    return [case for case in cases if str(case.get(field)) == value]

def generate_run_id():
    today = date.today().isoformat()
    suffix = uuid.uuid4().hex[:8]
    return f"{today}-{suffix}"

def read_multiline_answer():
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)

def write_results(cases, run_id):
    output_path = f"results/{run_id}.jsonl"
    with open(output_path, "w") as f:
        for case in cases:
            result = {
                "id": case["id"],
                "run_id": run_id,
                "model": "stub",
                "output": "STUB: " + case["prompt"],
                "error": None
            }
            f.write(json.dumps(result) + "\n")
    return output_path

def write_results_manual(cases, run_id):
    output_path = f"results/{run_id}.jsonl"
    saved = 0
    with open(output_path, "w") as f:
        try:
            for i, case in enumerate(cases, start=1):
                print(f"\n--- Case {i} of {len(cases)}: {case['id']} ---")
                print(case["prompt"])
                print("(paste your answer, then press Enter on a blank line to finish)")
                answer = read_multiline_answer()

                result = {
                    "id": case["id"],
                    "run_id": run_id,
                    "model": "manual",
                    "output": answer,
                    "error": None
                }
                f.write(json.dumps(result) + "\n")
                saved += 1
        except KeyboardInterrupt:
            print(f"\nInterrupted — saved {saved} answers to {output_path}")
            sys.exit(0)
    return output_path

def write_results_live(cases, run_id, model=LIVE_MODEL):
    load_env()
    client = anthropic.Anthropic()

    output_path = f"results/{run_id}.jsonl"
    with open(output_path, "w") as f:
        for i, case in enumerate(cases, start=1):
            print(f"[{i}/{len(cases)}] {case['id']}...", end=" ", flush=True)

            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": case["prompt"]}],
                )
                answer = next(
                    block.text for block in response.content if block.type == "text"
                )
                result = {
                    "id": case["id"],
                    "run_id": run_id,
                    "model": model,
                    "output": answer,
                    "error": None,
                }
                print("ok")
            except Exception as e:
                result = {
                    "id": case["id"],
                    "run_id": run_id,
                    "model": model,
                    "output": None,
                    "error": str(e),
                }
                print(f"error: {e}")

            f.write(json.dumps(result) + "\n")

            if i < len(cases):
                time.sleep(LIVE_CALL_PAUSE_SECONDS)
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True)
    parser.add_argument("--manual", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--filter", default=None, help="field=value, e.g. domain=science")
    parser.add_argument("--model", default=LIVE_MODEL, help="model to use in --live mode")
    args = parser.parse_args()

    cases = read_cases(args.cases)
    if args.filter is not None:
        cases = filter_cases(cases, args.filter)
    if args.limit is not None:
        cases = cases[:args.limit]
    run_id = generate_run_id()

    if args.manual:
        output_path = write_results_manual(cases, run_id)
    elif args.live:
        output_path = write_results_live(cases, run_id, model=args.model)
    else:
        output_path = write_results(cases, run_id)

    print(f"Wrote {len(cases)} results to {output_path}")

if __name__ == "__main__":
    main()
