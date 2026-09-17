# groundtruth

## The contract

`cases/*.jsonl` — produced by Track 01. One question per line, with the answer you already know:
```
{"id": "units-001", "domain": "units", "prompt": "How many feet are in one mile? Answer with just the number.", "expected": "5280", "match": "number", "tier": "easy", "notes": "exact by definition"}
```

`results/<run_id>.jsonl` — produced by Track 02. What the AI actually said, saved unedited:
```
{"id": "units-001", "run_id": "2026-08-09-a3f9c2d1", "model": "claude-sonnet-4-6", "output": "5280", "error": null}
```

`graded/<run_id>.jsonl` + `report.md` — produced by Track 03. Passed or failed, the reason, and a readable report:
```
{"id": "units-001", "run_id": "2026-08-09-a3f9c2d1", "passed": true, "match": "number", "expected": "5280", "got": "5280", "why": "number matched within tolerance"}
```

## Usage

This section assumes you've never run a Python program from a terminal before. A **terminal** (also called a command line or shell) is the text-based window where you type commands instead of clicking things — on Windows that's PowerShell or Git Bash, on Mac/Linux it's usually called Terminal.

### 1. Clone the repo

**Cloning** means downloading a copy of this project (with its full history) onto your computer. In your terminal, run:

```
git clone https://github.com/EUGMsub/groundtruth.git
cd groundtruth
```

The second command moves your terminal *into* the project folder — everything below assumes you're standing inside it.

### 2. Install the dependency

The runner uses one external Python package: **`anthropic`**, the official library for calling Claude's API. A "package" is just reusable code someone else wrote that you install rather than rewrite. Install it with:

```
python3 -m pip install anthropic
```

`pip` is Python's package installer — `python3 -m pip install X` is the standard way to add package `X` to your Python setup.

### 3. Set up your API key

The `--live` mode (step 5c below) needs an **API key** — a private password-like string that authenticates your requests to Anthropic and lets them bill your account for usage. Never share it or commit it to git.

1. Create a file named `.env` in the project root (same folder as this README).
2. Put one line in it:
   ```
   ANTHROPIC_API_KEY=your-actual-key-here
   ```
3. Save the file. `.env` is already listed in `.gitignore`, so git will never track or upload it.

If you skip this step, the default (stub) and `--manual` modes still work fine — only `--live` needs a key.

### 4. Where output goes

Every run — no matter the mode — writes one file to the `results/` folder, named `<run_id>.jsonl` (e.g. `results/2026-09-03-a3f9c2d1.jsonl`). A **run ID** is today's date plus a short random suffix, so multiple runs on the same day — even from different clones — don't collide or overwrite each other. `.jsonl` means "JSON Lines" — one JSON object per line, one line per case. The terminal will print the exact path when the run finishes.

### 5. Running the cases

All commands below are run from the project root and follow this shape:

```
python3 runner/run.py --cases <path-to-cases-file> [mode flag] [options]
```

`--cases` is required and points at a cases file, e.g. `cases/starter.jsonl`.

#### 5a. Default (stub) run

No mode flag needed — this is the default. It doesn't call any AI model; it just writes a placeholder answer (`"STUB: <the question>"`) for every case. Useful for checking the pipeline works before spending any API credits.

```
python3 runner/run.py --cases cases/starter.jsonl
```

#### 5b. `--manual` mode

Prints each question one at a time and waits for you to type (or paste) the answer yourself, then press Enter on a blank line to move to the next one. Use this when you want to hand-grade what a human would answer.

```
python3 runner/run.py --cases cases/starter.jsonl --manual
```

#### 5c. `--live` mode

Actually calls the Claude API for every case and records the real answer. Requires the `.env` API key from step 3.

```
python3 runner/run.py --cases cases/starter.jsonl --live
```

`--live` supports three optional flags, which can be combined:

- **`--model <model-id>`** — which Claude model to use (e.g. `claude-sonnet-4-6`, `claude-haiku-4-5`). Defaults to `claude-sonnet-4-6` if you don't set it.
  ```
  python3 runner/run.py --cases cases/starter.jsonl --live --model claude-haiku-4-5
  ```
- **`--limit N`** — only run the first N cases. Handy for a quick, cheap test before running the whole file.
  ```
  python3 runner/run.py --cases cases/starter.jsonl --live --limit 3
  ```
- **`--filter field=value`** — only run cases where that field matches that value (e.g. only the `math` domain). Check `cases/starter.jsonl` to see what fields exist on each case.
  ```
  python3 runner/run.py --cases cases/starter.jsonl --live --filter domain=math
  ```

All three can be used together, e.g. testing on 2 math cases with Haiku before committing to a full run:

```
python3 runner/run.py --cases cases/starter.jsonl --live --filter domain=math --limit 2 --model claude-haiku-4-5
```