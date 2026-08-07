# CLAUDE.md — working rules for this repo

> This file is read automatically by Claude Code at the start of every session.
> If Claude edits a file outside your track's folder, stop it immediately.

This is a three-person project. Each person works one track and owns one folder.
Read this before making changes.

## Folder ownership
- cases/      → Track 01 (Cases).   Owner: Erick
- runner/     → Track 02 (Runner).  Owner: Jen
- grading/    → Track 03 (Grader).  Owner: Paulet
- results/    → written by the Runner. Read-only for everyone else.
- graded/     → written by the Grader. Read-only for everyone else.

## Rules for editing
- Only edit files in the folder for the track being worked on this session.
- Do NOT edit another track's folder without the owner asking for it. If a change
  seems to require touching another folder, stop and say so instead of doing it.
- If you need a file another track owns and it doesn't exist yet, create a
  throwaway stub in your OWN folder instead — not theirs.
- Shared root files (README.md, BUILD_GUIDE.md, this file) can be edited by anyone,
  but call it out in the commit message.
- Never overwrite files in results/ or graded/ — those are run outputs.

## Workflow (this is the real safeguard, not this file)
- Always work on a branch, never commit straight to main.
- Branch names: owner-track-week, e.g. erick-cases-week1.
- Push the branch, open a pull request, and let SOMEONE ELSE merge it.
- Pull main before starting each session.

## Ground rules
- Standard library only, plus the one allowed package (anthropic) in the runner.
- If stuck more than 30 minutes, paste the error and what you tried.
