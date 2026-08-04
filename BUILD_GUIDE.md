# Ground Truth — Build Guide

*An eval harness · triplicate build order*

You write down questions you already know the answer to. It asks an AI those questions. It tells you which ones it got wrong, and what changed since last time. Built by three people in six weeks, for anyone building anything with AI.

3 tracks (pick your own) · 6 weeks + setup · ~3 hrs/week per person · no schedule overlap needed · MIT licence

---

## A. Why this exists

> When you build anything with an AI — a prompt, an agent, a skill — you change it and hope it got better. Most people check by trying two or three examples by hand. That doesn't scale, and it doesn't catch the things that quietly broke while you were fixing something else.
>
> Ground Truth makes "did that change help?" a question with an answer. You write down questions you already know the answer to. It asks the AI those questions. It tells you what it got wrong, and what changed since last time.

## B. Rules of the project

1. No graphical interface. Commands go in, files come out. A screen is a whole second project.
2. No database. Plain text files only. Everything here fits in files you can open and read.
3. Python's standard library first. You will add exactly one outside package the whole project.
4. If it doesn't run from the command line, it isn't done.
5. Don't add a feature that isn't in this guide until version 1 ships. Every project like this dies of extra ideas, not missing ones.

## C. The contract

Three files in a line. Each track owns exactly one as its output. Everyone builds against the *shape*, not against each other's progress, so nobody is ever waiting. If the file you need doesn't exist yet, write a fake one with three lines in it and carry on. Agree on these in setup week, then stop changing them.

### `cases/*.jsonl` — produced by Track 01

One question per line, with the answer you already know.

```
{"id": "units-001", "domain": "units", "prompt": "How many feet are in one mile? Answer with just the number.", "expected": "5280", "match": "number", "tier": "easy", "notes": "exact by definition"}
```

### `results/<run_id>.jsonl` — produced by Track 02

What the AI actually said, saved unedited, including failures.

```
{"id": "units-001", "run_id": "2026-08-09-1", "model": "claude-sonnet-4-6", "output": "5280", "error": null}
```

### `graded/<run_id>.jsonl` + `report.md` — produced by Track 03

Passed or failed, the reason, and a report a stranger can read.

```
{"id": "units-001", "run_id": "2026-08-09-1", "passed": true, "match": "number", "expected": "5280", "got": "5280", "why": "number matched within tolerance"}
```

## D. Pick a track

Any of the three people can take any track. Nothing depends on what you already know — every track is Python, files, and the command line. Choose by what you want to be able to do at the end, not by what you're already comfortable with, and settle it between yourselves.

---

## Setup week — everyone, about an hour

Before week one:

1. **Everyone** — Make a GitHub account. github.com, free. Skip if you already have one.
2. **One person** — Create the repository. New repository → name it `groundtruth` → Public → tick "Add a README file" → under License choose MIT. That licence dropdown is what makes it open source; one click now, annoying to add later.
3. **Same person** — Add the other two. Settings → Collaborators → add their GitHub usernames. They get an email invite they have to accept.
4. **Everyone** — Install Git. Mac: open Terminal, type `git --version`, accept the install prompt. Windows: git-scm.com, take all the defaults.
5. **Everyone** — Check Python is there. Type `python3 --version`. If you see 3-point-something you're set. If not, install from python.org — and on Windows tick "Add Python to PATH" during install.
6. **Everyone** — Open Claude Code and confirm it starts. You'll work inside the project folder, so open the repo folder in it once cloned.
7. **Everyone** — Clone the repo. `git clone https://github.com/USERNAME/groundtruth.git` then `cd groundtruth`.
8. **One person** — Make the folders and push. Create `cases/ runner/ grading/ results/ graded/` and paste the three file shapes into README.md. Git ignores empty folders, so put a `.gitkeep` file inside each.
9. **Everyone** — Practise git before any real work. Make `CONTRIBUTORS.md`, add your name, then branch → commit → push → pull request → someone else merges. Do this on something harmless so the git part is out of the way before it can cost a real week.

---

## Track 01 · Cases

**Owns:** `cases/`
**Job:** The question format, the validator, and the starter set that ships with the repo.
**You'll learn:** Reading and writing files in Python, JSON, and designing a format two other people depend on.
**Hardest part:** Writing questions that have exactly one defensible answer — harder than it sounds, and it's the whole foundation.
**Amount of code:** Least of the three.

### Week 1 — Write the format down and make ten cases

**Goal:** Turn things you know into lines a script can check.

- Make a file `cases/starter.jsonl`.
- Write 10 questions with answers nobody could argue with. Good starter subjects: unit conversions, percentages of round numbers, well-known dates, spelling, capital cities.
- One JSON object per line. No commas at the end of lines, no square brackets wrapped around the file — that's what makes it JSONL instead of JSON.
- Fill in the `notes` field on each one saying why that answer is correct. Future you will need it.
- Commit and push. The other two tracks build against this file.

- **What you should see:** `wc -l cases/starter.jsonl` prints 10.
- **Done when:** Ten lines, each valid JSON, each with a single answer you'd bet money on.
- **Worth knowing:** If two reasonable people could disagree about the answer, it isn't a case yet. Rewrite it or cut it. A vague case makes the whole report untrustworthy.
- **If you run out of time:** Five cases, all unit conversions.

Starter prompt:
> I'm making a file called cases/starter.jsonl for an eval project. Each line is a JSON object with the keys: id, domain, prompt, expected, match, tier, notes. Help me write 10 cases about unit conversions and simple percentages where the expected answer is a short number or word. Show me the lines in the chat first and explain what each field is for — don't create the file yet, I want to understand it before I use it.

### Week 2 — Write a script that catches your typos

**Goal:** Stop trusting yourself to hand-check a growing file.

- Write `cases/validate.py`. It reads every `.jsonl` file in `cases/`.
- For each line it checks three things: the line is valid JSON, it has all the required keys, and the id hasn't been used anywhere else.
- It prints a total count and lists every problem with the filename and line number.
- Run it. Fix what it finds. It will find things.
- Grow the set to 30 cases across at least three different subjects.

- **What you should see:** `python3 cases/validate.py` prints something like `cases/starter.jsonl · 30 cases · 0 problems`.
- **Done when:** The validator runs clean on 30 cases.
- **Worth knowing:** Make the error messages say exactly which line is wrong and what's missing. You are the person who will read them most.
- **If you run out of time:** Get the validator working on your original 10. Growing to 30 can wait.

Starter prompt:
> Write a Python script that reads every .jsonl file in a folder called cases/. For each line it should check the line is valid JSON, that it has the keys id, domain, prompt, expected, match and tier, and that no id appears twice across all the files. Print a total count and list any problems with the filename and line number. Use only the Python standard library. I'm new to Python — explain each part as you write it.

### Week 3 — Decide how each answer gets checked

**Goal:** Not every correct answer looks the same.

- There are four ways to check an answer. `exact`: matches character for character. `contains`: the expected text appears somewhere in the answer. `number`: pull the number out and compare it. `judge`: the answer is a sentence or two, so a second AI call decides.
- Write all four into `cases/README.md` with an example of each.
- Go back through every case and set the right match type.
- Add 10 new cases that need `judge` — questions where you want an explanation, not a word.
- Update `validate.py` to reject any case whose match type isn't one of the four.

- **What you should see:** validate.py now fails a case if you type `match: exactly` instead of `match: exact`.
- **Done when:** Every case has a match type you could defend out loud, and the README explains all four.
- **Worth knowing:** Most beginners set everything to `exact` and then wonder why a correct answer fails. An AI that answers "5,280 feet" is right; `exact` says it's wrong. `contains` and `number` exist for that reason.
- **If you run out of time:** Three match types, skip `judge` entirely — it can be added in week 5.

Starter prompt:
> Here are three of my eval cases: [paste them]. For each one, tell me which match type fits best out of exact, contains, number, or judge, and why. Then point out any case where the way I've written the expected answer will cause a correct response to be marked wrong.

### Week 4 — Build the set that's designed to fail

**Goal:** Anyone can write questions an AI gets right. This is the week that makes the project interesting.

- Write 10 cases where you expect the AI to be confidently wrong: common misconceptions, trick phrasing, questions where the intuitive answer isn't correct, numbers people routinely misremember.
- Tag each one `"tier": "hard"`.
- Before anybody runs them, write down which ones you think will fail. Put it in `cases/predictions.md` with today's date.

- **What you should see:** `cases/predictions.md` exists and is dated before the first hard run.
- **Done when:** Ten hard cases, and a dated predictions file written before any results exist.
- **Worth knowing:** Predicting before you measure is the difference between testing something and confirming what you already believed. When results come back, how wrong your predictions were is genuinely the most interesting thing the project produces.
- **If you run out of time:** Five hard cases and five predictions.

Starter prompt:
> I'm building an eval set. Give me 10 types of question where a language model is likely to answer confidently and be wrong — common misconceptions, trick phrasings, facts people routinely misremember. For each, explain the trap. Don't write the cases yet, just give me the question types.

### Week 5 — Find your own gaps

**Goal:** Know what your set doesn't cover before someone else points it out.

- Write `cases/coverage.py`. It prints three small tables: how many cases by subject, by match type, and by tier.
- Look at the tables and find the thinnest cell.
- Add 10 cases wherever the count is lowest.

- **What you should see:** `python3 cases/coverage.py` prints three plain-text tables.
- **Done when:** Coverage runs and no cell in any table is zero.
- **Worth knowing:** A set that's 90% easy unit conversions will show a 95% pass rate and tell you nothing. Balance is what makes the number mean something.
- **If you run out of time:** Just the subject table.

Starter prompt:
> Write a Python script that reads all my cases/*.jsonl files and prints three small plain-text tables to the terminal: count by domain, count by match type, and count by tier. Standard library only, no extra packages.

### Week 6 — Hand it to someone else

**Goal:** The set is only worth something if other people can add to it.

- Write `cases/README.md` properly: what a case is, every field explained, one full worked example, how to add a new file, how to run the validator.
- Ask a teammate to add 5 cases using only your README.
- Do not answer any questions while they do it. Write down every place they get stuck.
- Fix those places.

- **What you should see:** A teammate's 5 new cases pass validate.py on the first or second try.
- **Done when:** Someone added 5 valid cases without messaging you once.
- **Worth knowing:** Every question they have to ask you is a gap in the README. That's the actual test this week — not whether the cases work, but whether the document does.
- **If you run out of time:** Have them add 2 cases instead of 5.

Starter prompt:
> Read this README I wrote for people adding eval cases to my project: [paste it]. Pretend you've never seen this project before. What are the three places you'd get stuck or guess wrong? Quote the exact sentence that's unclear.

---

## Track 02 · Runner

**Owns:** `runner/`
**Job:** The script that reads the cases, asks the AI, and saves the answers.
**You'll learn:** Command-line arguments, talking to an API, handling errors so one failure doesn't kill a run, and keeping secrets out of a public repo.
**Hardest part:** Everything that can go wrong on a network call — and there's a lot. This track is where the money and the security live.
**Amount of code:** Most of the three.

### Week 1 — Fake the whole pipeline

**Goal:** Prove the file plumbing works before spending a cent or debugging a login.

- Write `runner/run.py`. It reads a cases file and writes `results/<run_id>.jsonl`.
- For now the output is fake: the literal text `STUB: ` followed by the prompt. Set model to `"stub"` and error to `null`.
- `run_id` is today's date plus a counter, like `2026-08-09-1`.
- No API key. No cost. No authentication.

- **What you should see:** `python3 runner/run.py --cases cases/starter.jsonl` creates a new file in `results/` with one line per case.
- **Done when:** Ten cases go in, ten results come out, every line has all five keys.
- **Worth knowing:** This feels like doing nothing. It isn't. If you start with real API calls you will spend two weeks debugging authentication and never find out that your file writing was broken the whole time. Separate the problems.
- **If you run out of time:** Hardcode the filenames instead of using flags — flags can come in week 4.

Starter prompt:
> Write a Python script runner/run.py that reads a JSONL file of cases (keys: id, domain, prompt, expected, match) and writes a results JSONL file where each line has id, run_id, model, output and error. For now set output to the string 'STUB: ' plus the prompt, model to 'stub', and error to null. run_id should be today's date plus a counter. Standard library only. Explain the file reading and writing carefully — I'm new to Python.

### Week 2 — Paste mode

**Goal:** Get real answers in without any account setup, and unblock the Grader immediately.

- Add a `--manual` mode. It prints one case prompt at a time and waits for you to paste an answer.
- Handle answers spanning several lines — end the answer with a blank line.
- It saves what you paste into the results file, correctly formatted.
- Run 10 real cases by hand: copy each prompt into Claude, copy the answer back.

- **What you should see:** A real results file exists that the Grader can work on, still with no API key anywhere.
- **Done when:** Ten real answers saved through manual mode.
- **Worth knowing:** This week matters more than it looks. It means the Grader has real data in week 2 instead of waiting until week 4, and manual mode stays useful forever for spot-checking one case.
- **If you run out of time:** Handle single-line answers only.

Starter prompt:
> Add a --manual mode to my run.py. In manual mode it should print each case prompt one at a time, wait for me to paste an answer and press enter on a blank line to finish, then save that as the output for that case. Show me the change and explain how the input loop works.

### Week 3 — Real calls

**Goal:** The script talks to the model itself.

- Install the package: `pip3 install anthropic`.
- Create a file called `.env` with your API key in it.
- Add `.env` to `.gitignore` first, before you commit anything at all. Then run `git status` and confirm `.env` is not in the list.
- Get one single call working end to end and print the answer. Stop and check it.
- Only then wrap it in the loop over all cases.

- **What you should see:** `python3 runner/run.py --all --limit 3` produces three real answers in a results file.
- **Done when:** Real answers from the model land in the results file.
- **Worth knowing:** Cost — a few hundred short calls is cents, not dollars; keep `--limit 3` on while testing. Security — an API key pushed to a public repo has to be deleted and replaced, and bots find them within minutes. Check `git status` before every single commit this week.
- **If you run out of time:** Get one call working and stop there. That's a legitimate week's work for a first API integration.

Starter prompt:
> Help me add real Anthropic API calls to my run.py. I want the key read from a .env file and never written in the code. Walk me through it in this order: installing the package, creating .env, adding .env to .gitignore, confirming git isn't tracking it, then making one single API call work. Stop after the single call works so I can test it before we loop.

### Week 4 — Make it survive a bad night

**Goal:** One failed call shouldn't destroy a forty-case run.

- Wrap each call in error handling. When one fails, write the error message into the `error` field, set output to null, and keep going.
- Add `--limit N` so you can test on 3 cases instead of 40.
- Add `--filter domain=units` so people can run only part of the set.
- Add a short pause between calls so you don't get rate limited.

- **What you should see:** The run prints something like `30 cases · 28 ok · 2 errors`, and finishes.
- **Done when:** A full run completes even when some calls fail, and every failure is visible in the file.
- **Worth knowing:** Save the failures rather than hiding them. A case that errored is different from a case that answered wrongly, and the Grader needs to tell the difference.
- **If you run out of time:** Just the error handling. Flags can wait until week 6.

Starter prompt:
> My run.py crashes if a single API call fails and I lose the whole run. Change it so each call is wrapped in error handling — on failure it records the error message in the 'error' field, sets output to null, and carries on. Then add --limit and --filter command line flags using argparse, and explain what argparse is doing.

### Week 5 — Runs become things you can compare

**Goal:** This is the feature the entire tool exists for.

- Every run writes to its own file. Never overwrite an old one.
- Add a `--model` flag, and record which model was used on every single line.
- Do two runs of the same cases and keep both.

- **What you should see:** Two files in `results/` with different run ids, and you can tell which is which without opening them.
- **Done when:** Two complete runs sit side by side.
- **Worth knowing:** Recording the model on every line rather than once at the top of the file is deliberate. It means the Grader never has to look anywhere else to know what produced an answer.
- **If you run out of time:** Skip the `--model` flag, just make sure runs don't overwrite each other.

Starter prompt:
> Change my runner so every run writes to its own file at results/<run_id>.jsonl instead of one shared file, and add a --model flag whose value gets recorded on every line. Then show me a command to list all my past runs from the terminal.

### Week 6 — One command

**Goal:** Somebody who didn't build it should be able to run it.

- Write the usage section of the main README: how to install, how to set the key, how to run, where the output lands.
- Add one script that does the standard run, so people don't have to remember flags.
- Watch a teammate run it on their own machine using only the README. Say nothing while they do it.
- Fix whatever broke.

- **What you should see:** A teammate gets a results file on their own machine without asking you a question.
- **Done when:** Someone else ran it from the README alone.
- **Worth knowing:** Assume the reader has never used a terminal. Every command goes on its own line, and anything they must replace with their own value gets said explicitly.
- **If you run out of time:** Write the README section and test it on yourself from a fresh clone in a different folder.

Starter prompt:
> Write the usage section of a README for my eval runner. Assume the reader has never run Python from a command line before. Cover cloning, installing dependencies, setting the API key, running it, and where the results end up. Short numbered steps, and explain any jargon the first time it appears.

---

## Track 03 · Grader

**Owns:** `grading/`
**Job:** The comparison logic, the verdicts, and the report people actually read.
**You'll learn:** Comparing strings and numbers in code, writing files meant for humans, using an AI to grade free text — and writing the standard it grades by.
**Hardest part:** Deciding what counts as correct and being able to defend it. The code is the easy half.
**Amount of code:** Produces something visible soonest; you get a real number in your first sitting.

### Week 1 — Print a number

**Goal:** Something visible on day one.

- Write `grading/grade.py`. It reads a cases file and a results file and matches them up by id.
- Exact match only for now: lowercase both, strip the spaces off the ends, compare.
- Print one line: `18 / 30 passed`.

- **What you should see:** `python3 grading/grade.py` prints a single line like `18 / 30 passed`.
- **Done when:** A number appears in the terminal. It does not have to be a good number.
- **Worth knowing:** If the Runner only has stub results so far, use those. Every case will fail, and that's fine — you're testing your code, not the AI. A grader that correctly reports `0 / 30` is working.
- **If you run out of time:** Match only the first five cases while you get the file matching right.

Starter prompt:
> Write a Python script grading/grade.py that reads two JSONL files: a cases file (id, prompt, expected, match) and a results file (id, output). Match them up by id. For now count a case as passed if output equals expected after lowercasing and stripping whitespace. Print 'X / Y passed'. Standard library only, and explain how you're matching the two files together — that's the part I don't understand yet.

### Week 2 — The other ways to be right

**Goal:** Exact match fails on almost every real answer.

- Add `contains`: the expected text appears anywhere in the answer, ignoring capitals.
- Add `number`: pull the first number out of the answer and compare it to expected, allowing a small tolerance.
- Write `graded/<run_id>.jsonl` with one line per case: id, run_id, passed, match, expected, got, why.

- **What you should see:** Every non-judge case grades correctly, and each graded line has a readable `why`.
- **Done when:** The three simple match types work and you can see the reason behind every verdict.
- **Worth knowing:** Test your number extraction on `"5,280"`, `"5280 feet"`, `"about 5280"` and `"5,280.0"` before you trust it. Commas are what break it first.
- **If you run out of time:** Add `contains` only; number matching can come in week 3.

Starter prompt:
> Extend my grader to handle three match types instead of one: exact, contains, and number. For number, extract the first number from the model's answer and compare it to the expected value with a tolerance of 0.01. Each graded line should include a short 'why' explaining the verdict. Show me the number extraction on its own first — I want to see how it handles '5,280 feet' and '25%'.

### Week 3 — The report

**Goal:** A file people read, instead of a terminal they have to run.

- Write `report.md`. Summary line at the top: date, run id, model, pass rate.
- Then a table of every case with a pass or fail mark.
- Then a Failures section showing, for each one, the prompt, the expected answer, and what actually came back.

- **What you should see:** You can open report.md, read it top to bottom, and know what to fix without opening any other file.
- **Done when:** Someone reads the report and understands the state of the project without asking a question.
- **Worth knowing:** Put failures near the top and successes further down. Nobody reads a report to admire the things that worked.
- **If you run out of time:** Summary line and the failures section; the full table can wait.

Starter prompt:
> Write a Python function that takes my graded results and produces a report.md file. Structure: a one-line summary with the date, run id, model and pass rate at the top, then a markdown table of all cases with a pass or fail mark, then a '## Failures' section where each failure shows the prompt, the expected answer, and what the model actually said. Keep the markdown simple enough that it still reads fine as plain text.

### Week 4 — Judge mode

**Goal:** Grade the answers that can't be checked by string matching.

- For cases with `match: judge`, send the model's answer and the expected answer to Claude and ask for a verdict.
- Write the rubric strictly. Something like: mark it FAIL if any factual claim is wrong, even when the overall answer is close.
- Have it return only PASS or FAIL and one sentence of reasoning. Nothing else.
- Hand-check 10 verdicts yourself. Where you disagree, change the rubric, not the case.

- **What you should see:** Judge cases grade, and the one-sentence reasons are specific enough to act on.
- **Done when:** You've spot-checked ten verdicts by hand and agreed with at least eight.
- **Worth knowing:** A generous judge makes the entire project worthless — everything passes and the number stops meaning anything. When in doubt, make the rubric harsher. Using a model to grade another model's output is called LLM-as-judge, and the rubric is the whole craft of it.
- **If you run out of time:** Get one judge case working end to end and stop. Volume next week.

Starter prompt:
> I need to grade free-text answers against an expected answer using a second Claude call. Write me the function, and help me write the grading prompt so it's strict: it should fail any answer containing an incorrect factual claim even if the response is broadly close. It should return only PASS or FAIL plus one sentence. Show me the grading prompt as separate text so I can edit the wording myself.

### Week 5 — Compare two runs

**Goal:** This is what makes it a harness rather than a quiz marker.

- Write `grading/compare.py`. It takes two run ids.
- It prints three lists: newly passing, newly failing, still failing.
- Newly failing goes at the top, labelled clearly as regressions.

- **What you should see:** You change a prompt, run it again, and compare tells you exactly which cases got worse.
- **Done when:** The regression list works on two real runs.
- **Worth knowing:** A regression is something that used to work and now doesn't. It's the single most useful thing this tool produces, because it's the thing nobody catches by hand.
- **If you run out of time:** Print only the newly-failing list — it's the one that matters most.

Starter prompt:
> Write a script that takes two graded JSONL files from different runs and prints three lists by case id: cases that newly pass, cases that newly fail, and cases that failed in both. Put newly failing at the top and label it clearly as regressions.

### Week 6 — Readable cold

**Goal:** A stranger opens the report and understands it in thirty seconds.

- Add a header block on every report: date, run id, model, overall pass rate.
- Add pass rate broken out by subject and by tier, so a low score points at where the problem is.
- Give a report to someone outside the project. Ask them what they think it says.

- **What you should see:** Someone who didn't build it explains the report back to you correctly.
- **Done when:** The report survives contact with a person who has no context.
- **Worth knowing:** This is the file that ends up in the repo's README as the sample output. It's the thing most people will ever see of the project, so it's worth more polish than it looks like it deserves.
- **If you run out of time:** Just the header block with date, model and overall pass rate.

Starter prompt:
> Here is my current report.md: [paste it]. I want someone who has never seen this project to understand it in thirty seconds. Tell me what's confusing, what's missing from the header, and what I should cut. Be blunt.

---

## Reference

### Version 1 is finished when all of this is true

- The README says what this is in the first two sentences, before any installation instructions.
- A starter case set ships inside the repo, so it does something the moment someone clones it.
- One command goes from cases to a report.
- A LICENSE file exists.
- There is no API key anywhere in the repo or anywhere in its history.
- A sample report is pasted or screenshotted into the README.
- Someone outside the three of you cloned it and got a report out.

### Working agreement — how three people who never overlap stay in one repo

- **Only edit your own folder.** Each track owns one folder. If you never touch someone else's, you'll almost never hit a merge conflict — the single thing most likely to stop a beginner cold.
- **Branch, push, let someone else merge.** Nobody pushes straight to main, including whoever set the repo up.
- **One message a week, three lines.** You won't be working at the same time, so this is the whole coordination system: what I finished, what's broken, what I need from someone else.
- **Thirty minutes stuck is the limit.** Past half an hour, open Claude and paste the error along with what you were trying to do. Getting unstuck quickly is the skill this project is actually building.
- **Commit at the end of every session,** even when it's unfinished and ugly. Uncommitted work sitting on one laptop for a week is how three-person projects quietly become one-person projects.
- **Write down what confused you.** Keep a NOTES.md in your folder. Everything that confused you is a line the README is missing.

### Git — the eight commands you'll actually use

| Command | What it does |
|---|---|
| `git clone <url>` | Copy a repo from GitHub onto your machine. Once. |
| `git status` | What have I changed, and what is git tracking? Run this constantly. |
| `git checkout -b my-branch` | Make a new branch and switch to it. Name it like `polet-week2`. |
| `git add .` | Stage everything you've changed, ready to commit. |
| `git commit -m "message"` | Save the staged changes with a short note. |
| `git push -u origin my-branch` | Send your branch to GitHub. `-u` is only needed the first time. |
| `git checkout main` | Switch back to the main branch. |
| `git pull` | Get everyone else's merged work. Do this before each session. |

### Errors you will hit, and what they mean

| Error | What's happening |
|---|---|
| `command not found: python3` | Python isn't installed, or on Windows wasn't added to PATH. Try `python` first. |
| `ModuleNotFoundError: No module named 'anthropic'` | The package isn't installed in the Python you're running. `pip3 install anthropic`; if that fails, ask Claude which Python your terminal is using. |
| `JSONDecodeError` | A line in a .jsonl file isn't valid JSON. Usually a trailing comma, a smart quote pasted from a document, or a line break mid-line. |
| `Permission denied (publickey)` | Git can't authenticate with GitHub. Simplest fix: use the HTTPS repo URL instead of SSH. |
| `Your branch is behind 'origin/main'` | Someone merged since you started. `git pull`, resolve, carry on. |
| `CONFLICT (content): Merge conflict in ...` | Two people edited the same lines. Paste the conflicted file into Claude and ask it to explain the markers before touching anything. |
| `401 authentication_error` | Key missing, wrong, or .env isn't being read. Print the first four characters to check it loads — never the whole thing. |

### When you're stuck — say it like this

- **Something errored:** "I ran this: [command]. I got this error: [paste all of it]. I'm a beginner — explain what went wrong before you fix it, then give me the fix."
- **You don't understand code in front of you:** "Explain this file line by line, assuming I've written maybe 50 lines of Python in my life: [paste]."
- **You don't know how to start the week:** "Here's my goal this week: [goal and done-when]. Here's my project right now: [folder structure]. Give me three approaches from simplest to most robust, tell me which one a beginner should pick, and why."
- **It works but you don't trust it:** "This works but I'm not sure it's right: [paste]. What would break it? Give me three inputs that would make it fail."
- **Claude wrote something you don't understand:** "You just gave me code I can't follow. Rewrite it the simplest possible way, even if it's longer or less clever, and explain why each part is there. I need to maintain this myself."
- **You're about to add something clever:** "I want to add [idea] to my project. Talk me out of it. What does it cost in complexity, and what breaks if I skip it? Assume I have three hours a week."

### Glossary

| Term | Definition |
|---|---|
| API | A way for one program to talk to another over the internet. |
| API key | A long secret string that proves a request is yours and gets billed to you. Treat it like a password; never in the code, never in the repo. |
| argparse | Python's built-in tool for reading command-line flags, so people can type --limit 3. |
| branch | A parallel copy of the project where you work without affecting anyone else until it's merged. |
| clone | Making your own local copy of a repo that lives on GitHub. |
| CLI | Command-line interface. A program you run by typing rather than clicking. |
| commit | A saved snapshot of your changes with a note. Small frequent commits beat one huge one. |
| dependency | An outside package your project needs. Every one is something that can break, which is why this project has exactly one. |
| .env | A plain text file holding secrets like API keys. It stays on your machine and is never committed. |
| environment variable | A value your program reads from outside its own code; the normal way to hand a secret to a script. |
| eval / evaluation | Testing an AI's output against answers you already know are correct. |
| flag / argument | Extra instructions typed after a command, like --limit 3. |
| .gitignore | A file listing things git should pretend it can't see. .env belongs here on day one. |
| ground truth | The answer you already know is correct, that the AI's answer is measured against. The project is named after it. |
| JSON | A text format for structured data using curly braces and key-value pairs. |
| JSONL | JSON Lines. One complete JSON object per line, no commas between lines, no brackets around the file. |
| key / value / field | In `{"id": "units-001"}`, id is the key, "units-001" is the value, and the pair is a field. |
| LLM-as-judge | Using an AI model to grade another AI's answer. Only as good as the rubric. |
| main | The primary branch, the version everyone treats as real. |
| markdown | Simple plain-text formatting with # for headings and * for lists. |
| merge conflict | Git can't decide between two people's edits to the same lines. Avoidable by staying in your own folder. |
| MIT license | A short permissive open source licence. Picking it is what makes the repo genuinely open source. |
| open source | Code anyone can read, use and build on, published with a licence saying so. Public without a licence isn't the same thing. |
| package / pip | A package is code someone else wrote that you install; pip is the tool that installs it for Python. |
| pass rate | The share of cases that got the right answer. Only meaningful when you know what's in the set. |
| pull request (PR) | A request to merge your branch into main, giving someone else a chance to look first. |
| push / pull | Push sends your commits to GitHub; pull brings other people's down. |
| README | The file GitHub shows on a repo's front page. The most important file in a project meant to be found. |
| regression | Something that used to work and now doesn't. Catching these is the main reason this tool is worth building. |
| repository (repo) | A project folder whose full history git tracks, usually with a copy on GitHub. |
| rubric | The written standard a judge grades against. A vague rubric makes a generous judge, and a generous judge makes the pass rate meaningless. |
| run / run_id | One pass of all your cases through a model; the run_id labels it so runs can be compared. |
| script | A single file of code you run start to finish, like run.py. |
| standard library | Everything Python can do with nothing installed. It's a lot, and using it means fewer things to break. |
| stub / mock | A fake stand-in used to test everything around it before the real thing is connected. |
| terminal | The window where you type commands instead of clicking. Also called command line, shell, or console. |
| tolerance | How close a number has to be to count as correct. Without one, 5280.0 and 5280 disagree. |
| try / except | Python's way of attempting something risky and deciding what to do when it fails, rather than crashing. |
| validator | A script whose only job is checking your data is well-formed. |

---

**The end goal:** a public repo where anyone clones it, drops in their own questions-with-known-answers, runs one command, and gets a report telling them where their AI is wrong. It ships with a starter set, so it works the moment it's downloaded.
