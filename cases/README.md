# Match Types

Every case in `cases/starter.jsonl` has a `match` field that says how to score a model's answer against `expected`. There are four types: `exact`, `contains`, `number`, and `judge`.

**The most common beginner mistake is defaulting every case to `exact`.** It feels safest, but real model answers rarely come back as a bare token — they come back as sentences, or with units, or with extra phrasing. If a case asks "How many feet are in a mile?" and the model answers `"5,280 feet"`, that answer is correct. An `exact` match will fail it anyway, because `"5,280 feet"` is not character-for-character equal to `"5280"`. That's not a model problem, it's a match-type problem — `contains` and `number` exist specifically to score answers like this correctly.

---

## exact

**Definition:** The answer must match `expected` character for character, after lowercasing and trimming whitespace.

**Worked example** — `cases/starter.jsonl` case-01:
```json
{"id": "case-01", "domain": "geography", "prompt": "What is the capital of Australia?", "expected": "Canberra", "match": "exact", "tier": "easy"}
```
- ✅ Passes: `"Canberra"` — lowercases/trims to `"canberra"`, identical to expected.
- ❌ Fails: `"The capital of Australia is Canberra."` — correct information, but after lowercasing/trimming it's a whole sentence, not `"canberra"`, so it's not equal.

**Use this when:** there is exactly one acceptable string and no acceptable variation in wording — single tokens like element symbols, city names, or short proper nouns (case-03 `K`, case-10 `Mercury`, case-17 `Fe`).

---

## contains

**Definition:** The `expected` text must appear somewhere inside the answer, ignoring capitalization.

**Worked example** — `cases/starter.jsonl` case-07:
```json
{"id": "case-07", "domain": "biology", "prompt": "What does DNA stand for?", "expected": "deoxyribonucleic acid", "match": "contains", "tier": "easy"}
```
- ✅ Passes: `"DNA stands for deoxyribonucleic acid."` — the expected phrase appears in the answer, case-insensitively.
- ❌ Fails: `"DNA stands for genetic acid."` — the required phrase `"deoxyribonucleic acid"` never appears, even though the answer is trying to answer the same question.

**Use this when:** the correct answer can be phrased multiple ways (a short lead-in, extra words, a full name vs. a short name) but must include one specific required phrase — acronym expansions (case-09, case-27, case-28), author names where "Shakespeare" and "William Shakespeare" are both right (case-05, case-25), or single-word facts a model tends to wrap in a sentence (case-20 `mitochondria`, case-21 `gene`, case-29 `Moon`).

---

## number

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

## judge

**Definition:** The answer is a sentence or two of free-form reasoning, so a second AI call reads it against a rubric and decides pass/fail — there's no fixed string or number to compare against.

**Worked example** — `cases/starter.jsonl` case-34:
```json
{"id": "case-34", "domain": "computer science", "prompt": "Why is binary search generally faster than checking every item one by one (linear search) in a sorted list?", "expected": "Binary search compares the target to the middle element and eliminates half of the remaining items each step, so it needs far fewer comparisons than checking each item in order, especially as the list grows large.", "match": "judge", "tier": "easy"}
```
- ✅ Passes: `"Because it cuts the search space in half with each comparison instead of scanning every element, so it takes way fewer steps on a big list."` — different wording, same mechanism (halving the remaining space each step).
- ❌ Fails: `"Because computers are good at math."` — on-topic-sounding, but doesn't explain the actual mechanism the rubric requires (comparing to the middle, discarding half), so the judge rejects it.

**Use this when:** correctness depends on the *reasoning* or *explanation*, not a specific string or number — there's no fixed phrase you could `contains`-match on, because many differently-worded answers are equally correct and many similar-sounding ones are wrong.
