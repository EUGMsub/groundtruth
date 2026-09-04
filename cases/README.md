# cases/ — README

## What a case is

A **case** is one test question for the eval: a prompt to send a language model, the correct answer, and instructions for how to check whether the model's answer counts as correct. This folder holds the full set of cases — the "eval set" — that gets run against a model to measure how often it answers correctly, and where specifically it fails.

## The fields

Every case is one JSON object with these seven fields. ("JSON" is a plain-text way of writing structured data as `"key": value` pairs inside curly braces `{ }` — more on the exact syntax rules further down.)

- **`id`** — a unique name for the case, like `"case-01"`. Every case in every file needs a different id; nothing else uses it except to identify the case in results and reports.
- **`domain`** — a short category label, like `"geography"` or `"math"`. Used for coverage reporting (are we testing a broad spread of topics, or all clustered in one area?), not for grading.
- **`prompt`** — the exact question sent to the model, word for word. If the model needs an instruction about how to format its answer (e.g. "answer with just the city name"), that instruction goes here, inside the prompt.
- **`expected`** — the correct answer, or (for `judge` cases) a plain statement of the facts a correct answer must contain. This is the standard the answer gets graded against — never a "model answer" written the way you'd expect the AI to phrase it, just the bar it has to clear.
- **`match`** — which of four grading methods to use: `exact`, `contains`, `number`, or `judge`. Most people default to exact and then wonder why correct answers fail. It's the most restrictive option, not the safest — read the Match Types section before choosing.

  Quick decision rule:
  - Number answer → `number`
  - Sentence or explanation → `judge`
  - Word or phrase the model will likely wrap in a sentence → `contains`
  - `exact` only if the prompt tells the model to answer with nothing else

- **`tier`** — a difficulty label, currently `"easy"` or `"hard"`. `"easy"` cases are things a model should get right close to 100% of the time. `"hard"` cases are ones you specifically expect a model to get wrong, or where you're testing a known weak spot.
- **`notes`** — a sentence or two of context for a human reader: why this case is worth having, why the match type was chosen, or (for `"hard"` cases) what wrong answer you predict and why it's tempting. Never read by the grading code — it's documentation, not data.

## A full worked example

Here's one real case from `cases/starter.jsonl`, field by field:

```json
{"id": "case-07", "domain": "biology", "prompt": "What does DNA stand for?", "expected": "deoxyribonucleic acid", "match": "contains", "tier": "easy", "notes": "Short fixed phrase every correct expansion must include verbatim, regardless of whether the answer also spells out the acronym first."}
```

- `"id": "case-07"` — the seventh case in the file; no other case anywhere uses this id.
- `"domain": "biology"` — this case is about biology, for coverage-counting purposes.
- `"prompt": "What does DNA stand for?"` — this exact sentence is what gets sent to the model.
- `"expected": "deoxyribonucleic acid"` — the required phrase, not a full sentence. It's the standard the answer is checked against, not a sample answer to copy.
- `"match": "contains"` — a model will almost always answer this in a full sentence ("DNA stands for deoxyribonucleic acid.") or spell out the acronym first, so the grader just checks that the phrase `"deoxyribonucleic acid"` appears somewhere in the answer, ignoring capitalization — it doesn't require the answer to be *only* that phrase.
- `"tier": "easy"` — this is a basic fact a model should reliably get right, not a trap.
- `"notes": "Short fixed phrase..."` — explains for a human reader why `contains` (not `exact`) is the right call here: the required phrase is fixed and short, but the surrounding sentence isn't.

## Adding cases

There are two ways to add a case:

1. **Append to `cases/starter.jsonl`.** This is the main case file and where most new cases should go. Add your new case as a new line at the end of the file, continuing the id numbering (if the last case is `case-56`, your new case is `case-57`).
2. **Create a new `.jsonl` file in `cases/`.** Useful if you're adding a distinct batch of cases that deserves its own file (for example, cases from a different source, or a themed set). Both `validate.py` and `coverage.py` automatically read every `.jsonl` file in the folder, so a new file is picked up with no extra setup. Case ids still need to be unique across *all* files, not just within the new one.

Either way, don't edit an existing case's `id` or delete existing cases without a reason — other people's tooling and past results may refer to those ids.

## JSONL format rules

The file extension is `.jsonl`, short for "JSON Lines." It is **not** one big JSON document — it's a plain text file where **each line is its own complete, independent JSON object**. This is different from a normal JSON file and it trips people up the first time, so the rules:

- **One case per line.** Each line is a full `{ ... }` object, with all seven fields inside it.
- **No commas between lines.** In a JSON array you'd separate items with commas; here you don't — each line stands alone.
- **No enclosing brackets.** Don't wrap the whole file in `[` and `]` like a JSON array — that would make it one JSON array instead of many JSON-Lines objects, and every tool here would break.
- **No trailing commas.** Inside a single case's `{ ... }`, the last field must not have a comma after it (`"tier": "easy",}` is invalid; `"tier": "easy"}` is correct).
- **Double quotes only.** JSON requires `"double quotes"` around every key and every string value — not `'single quotes'`.
- **A trailing blank line at the end of the file is fine** and normal (most editors add one automatically); blank lines are otherwise skipped by both scripts, so don't rely on one to separate anything meaningfully.

The safest way to add a case without breaking the format: copy an existing line, paste it as a new line, and edit the values in place rather than typing a case from scratch.

## Running the checks

From the repository root (not from inside `cases/`), run:

```
python cases/validate.py
```

This checks every `.jsonl` file in `cases/` for: valid JSON on every line, all seven required fields present, a recognized `match` value, and no duplicate ids. Clean output looks like:

```
56 case(s) found
No problems found.
```

If something's wrong, it prints one line per problem, naming the file, line number, and issue (e.g. `cases/starter.jsonl line 12: missing key 'tier'`), and exits with a non-zero status — fix every line it lists and rerun until you see "No problems found."

```
python cases/coverage.py
```

This doesn't check for errors — it prints three small tables (counts by domain, by match type, and by tier) so you can see at a glance whether the set is well spread across topics, or lopsided. There's no "clean" output to aim for here, just a sanity check that you haven't, say, added ten cases all in the same domain, or left a domain with only one case in it.

Run both after adding or editing any case, before committing.

## The standard for a good case

**If two reasonable, informed people could disagree about the correct answer, it isn't a case yet.** Every case needs exactly one answer that isn't up for debate — not "the answer most people would say," not "the answer that's usually right," but a fact (or, for `judge` cases, a mechanism) that doesn't have a live expert or textbook disagreement behind it. If you're tempted to write a case and you find yourself thinking "well, technically..." or "some sources say...", that's the signal to either pick a less contestable angle on the same topic or drop the case.

This standard applies whether the case is easy or hard. A `"hard"` case is allowed to be a question models predictably get *wrong* — that's the point of a hard case — but it still needs exactly one answer that's actually right.

---

## Match Types

Every case in `cases/starter.jsonl` has a `match` field that says how to score a model's answer against `expected`. There are four types: `exact`, `contains`, `number`, and `judge`.

**The most common beginner mistake is defaulting every case to `exact`.** It feels safest, but real model answers rarely come back as a bare token — they come back as sentences, or with units, or with extra phrasing. If a case asks "How many feet are in a mile?" and the model answers `"5,280 feet"`, that answer is correct. An `exact` match will fail it anyway, because `"5,280 feet"` is not character-for-character equal to `"5280"`. That's not a model problem, it's a match-type problem — `contains` and `number` exist specifically to score answers like this correctly.

---

### exact

**Definition:** The answer must match `expected` character for character, after lowercasing and trimming whitespace.

**Worked example** — `cases/starter.jsonl` case-01:
```json
{"id": "case-01", "domain": "geography", "prompt": "What is the capital of Australia?", "expected": "Canberra", "match": "exact", "tier": "easy"}
```
- ✅ Passes: `"Canberra"` — lowercases/trims to `"canberra"`, identical to expected.
- ❌ Fails: `"The capital of Australia is Canberra."` — correct information, but after lowercasing/trimming it's a whole sentence, not `"canberra"`, so it's not equal.

**Use this when:** there is exactly one acceptable string and no acceptable variation in wording — single tokens like element symbols, city names, or short proper nouns (case-03 `K`, case-10 `Mercury`, case-17 `Fe`).

---

### contains

**Definition:** The `expected` text must appear somewhere inside the answer, ignoring capitalization.

**Worked example** — `cases/starter.jsonl` case-07:
```json
{"id": "case-07", "domain": "biology", "prompt": "What does DNA stand for?", "expected": "deoxyribonucleic acid", "match": "contains", "tier": "easy"}
```
- ✅ Passes: `"DNA stands for deoxyribonucleic acid."` — the expected phrase appears in the answer, case-insensitively.
- ❌ Fails: `"DNA stands for genetic acid."` — the required phrase `"deoxyribonucleic acid"` never appears, even though the answer is trying to answer the same question.

**Use this when:** the correct answer can be phrased multiple ways (a short lead-in, extra words, a full name vs. a short name) but must include one specific required phrase — acronym expansions (case-09, case-27, case-28), author names where "Shakespeare" and "William Shakespeare" are both right (case-05, case-25), or single-word facts a model tends to wrap in a sentence (case-20 `mitochondria`, case-21 `gene`, case-29 `Moon`).

---

### number

**Definition:** Pull the numeric value out of the answer and compare it to `expected`, allowing a small tolerance.

**Worked example** — `cases/starter.jsonl` case-02:
```json
{"id": "case-02", "domain": "math", "prompt": "What is 17 times 6?", "expected": "102", "match": "number", "tier": "easy"}
```
- ✅ Passes: `"17 times 6 is 102."` — the number `102` is extracted from the sentence and equals expected.
- ❌ Fails: `"17 times 6 is 103."` — the extracted number, `103`, is outside tolerance of the expected `102`.

This is also the match type behind the `"5,280 feet"` case from the intro: the extractor strips the comma and unit, pulls out `5280`, and compares it numerically — so formatting differences don't cause false failures the way `exact` would.

**Use this when:** the answer is a number that a model will naturally embed in prose, with punctuation (`1,918`), units, or trivial rounding — arithmetic (case-02, case-06, case-08, case-11, case-12, case-13), dates (case-04, case-23, case-24), and counts (case-16, case-19).

---

### judge

**Definition:** The answer is a sentence or two of free-form reasoning, so a second AI call reads it against a rubric and decides pass/fail — there's no fixed string or number to compare against.

**Worked example** — `cases/starter.jsonl` case-34:
```json
{"id": "case-34", "domain": "computer science", "prompt": "Why is binary search generally faster than checking every item one by one (linear search) in a sorted list?", "expected": "Binary search compares the target to the middle element and eliminates half of the remaining items each step, so it needs far fewer comparisons than checking each item in order, especially as the list grows large.", "match": "judge", "tier": "easy"}
```
- ✅ Passes: `"Because it cuts the search space in half with each comparison instead of scanning every element, so it takes way fewer steps on a big list."` — different wording, same mechanism (halving the remaining space each step).
- ❌ Fails: `"Because computers are good at math."` — on-topic-sounding, but doesn't explain the actual mechanism the rubric requires (comparing to the middle, discarding half), so the judge rejects it.

**Use this when:** correctness depends on the *reasoning* or *explanation*, not a specific string or number — there's no fixed phrase you could `contains`-match on, because many differently-worded answers are equally correct and many similar-sounding ones are wrong.
