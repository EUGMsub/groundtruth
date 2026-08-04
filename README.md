# groundtruth

## The contract

`cases/*.jsonl` — produced by Track 01. One question per line, with the answer you already know:
```
{"id": "units-001", "domain": "units", "prompt": "How many feet are in one mile? Answer with just the number.", "expected": "5280", "match": "number", "tier": "easy", "notes": "exact by definition"}
```

`results/<run_id>.jsonl` — produced by Track 02. What the AI actually said, saved unedited:
```
{"id": "units-001", "run_id": "2026-08-09-1", "model": "claude-sonnet-4-6", "output": "5280", "error": null}
```

`graded/<run_id>.jsonl` + `report.md` — produced by Track 03. Passed or failed, the reason, and a readable report:
```
{"id": "units-001", "run_id": "2026-08-09-1", "passed": true, "match": "number", "expected": "5280", "got": "5280", "why": "number matched within tolerance"}
```