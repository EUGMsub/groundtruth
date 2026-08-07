import json
import argparse
from datetime import date
import os

def read_cases(filepath):
    cases = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                case = json.loads(line)
                cases.append(case)
    return cases

def generate_run_id():
    today = date.today().isoformat()
    counter = 1
    while os.path.exists(f"results/{today}-{counter}.jsonl"):
        counter += 1
    return f"{today}-{counter}"

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True)
    args = parser.parse_args()

    cases = read_cases(args.cases)
    run_id = generate_run_id()
    output_path = write_results(cases, run_id)

    print(f"Wrote {len(cases)} results to {output_path}")

if __name__ == "__main__":
    main()
