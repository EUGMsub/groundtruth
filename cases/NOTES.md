# Cases — notes

## v2 ideas

### Word-boundary match type ("word")

**Motivation:** Short expected values like chemical symbols (`K`, `Fe`, `Ag`) fail under both existing match strategies:
- `exact`: requires constraining the prompt (e.g., "Answer with just the symbol, nothing else"), following the pattern in case-42/45/47/49.
- `contains`: unsafe — `K` matches the `k` in "like"; `Ag` matches incidental letter sequences in English prose.

**Proposal:** Add a new `"word"` match type that checks for the expected string as a **whole token**, bounded by non-alphanumeric characters (regex: `\bexpected\b`, case-sensitive). This lets bare symbols pass when the model outputs them as standalone tokens (e.g., "**K**", "**Fe**", "**Ag**" in bold) while avoiding substring false positives.

**Scope:** Requires changes to:
- `grading/grade.py` — add word-boundary matching logic
- `cases/validate.py` — accept `"word"` as a valid match type
- `README.md` — document the new match type

**Status:** Declined for v1 under rule 5 (no new features before v1 ships). Hold for v2.
