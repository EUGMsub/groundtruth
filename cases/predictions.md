# Hard-tier predictions

Written 2026-09-03, before any hard-tier case had been run against a model. Predictions and reasoning below are filled in by hand, not generated.

Predicted PASS on 9 of 13 hard cases, including 5 of the 6 knowledge-based traps. If that holds, the knowledge traps don't work on this model and only the structural failures (tokenization, multi-digit arithmetic) are genuinely hard. That would be the main finding.

| Case ID | Question (short) | Prediction (PASS/FAIL) | Reasoning |
|---|---|---|---|
| case-32 | Why does the Moon go through phases? (misconception trap: Earth's shadow) | PASS | Famous misconception; models correct it reflexively. |
| case-37 | Why is it colder atop a mountain despite being closer to the Sun? (misconception trap: distance to Sun) | PASS | Same — famous misconception, models correct it reflexively. |
| case-40 | Why does refrigeration keep food from spoiling? (misconception trap: kills vs. slows bacteria) | PASS | Same — famous misconception, models correct it reflexively. |
| case-41 | How many times does 'e' appear in 'bookkeeper'? | FAIL | Tokenization; can't see individual letters. |
| case-42 | Spell 'algorithm' backwards | FAIL | Same root cause as case-41; reversal invites transposition. |
| case-43 | Which is longer: 5,000 days or 15 years? | PASS | *Confidence: medium.* The conversion is one multiplication and the "answer using digits" instruction nudges it toward computing rather than eyeballing. The numeral illusion is a human bias more than a model one. |
| case-44 | 6,847,593 + 5,298,678 | FAIL | Every column carries. |
| case-45 | 4th letter from the end of 'government' | FAIL | Positional indexing into a token. |
| case-46 | What does 'enervate' mean? | PASS | *Confidence: high.* "Enervate" is a standard dictionary word and the fact that it's commonly misused is itself heavily documented. The model has seen the correction more than the mistake. |
| case-47 | Capital of Morocco | PASS | *Confidence: high.* Capital-vs-largest-city is the most standard geography trivia there is. Rabat/Casablanca sits right next to Canberra/Sydney in every quiz. |
| case-48 | Mary Shelley's 1826 plague novel (besides Frankenstein) | PASS | *Confidence: low.* Going against my own reversal-curse reasoning here. The Last Man got a big pandemic-era revival, new Penguin and Broadview editions, a lot of coverage. It's less obscure than it was ten years ago. But I'm genuinely unsure and could see the retrieval failing. |
| case-49 | Which state is the original Portland (namesake of Portland, OR) in? | PASS | *Confidence: medium.* Assumed this was obscure when I wrote it, but one source called it a story every third-grader in Oregon knows. That changed my mind. Retracting my original assumption. |
| case-50 | Does 'quantum leap' mean a huge change or the smallest possible change? | PASS | *Confidence: medium.* "A quantum leap is actually tiny" is a popular science-communication correction in its own right. The model has likely absorbed the correction, not just the idiom. |

## Results (2026-09-17)

Scored 8/13. All 5 misses were FAIL predictions on structural cases (41, 42, 44, 45) that passed, plus case-40.

My stated hypothesis — "knowledge traps don't work, only structural failures are genuinely hard" — was wrong in both halves. The structural cases passed too. Tokenization and multi-digit arithmetic are not reliable failure modes on this model.

What actually failed: 6 of 7 failures were judge-mode cases — long explanatory answers containing a factual error. That's a different failure mode than anything I designed for, and the one worth targeting in a future hard tier.

Open question: case-61 failed on exact-match-with-a-sentence, the same false-fail pattern I fixed in week 6. Needs the same fix.
