# stats_review: project notes

This repository holds agent skills for AI-assisted consistency review of DKF
statistical products (`.claude/skills/`), adapted from research_skills. `README.md` is
the user guide. The earlier API prototype is in `archive/` and is not maintained.

## Running a review

- Use the `dkf-review` skill, then `dkf-consistency-review` (and `dkf-review-audit`
  first at depth `full`). Jobs live in `jobs/<job>/`, which git ignores: never commit
  or copy job contents elsewhere.
- **Before starting a review of a real product, confirm with the user**: a
  standard-depth review runs many agent turns for tens of minutes or longer and costs
  far more than a single model call. Say which depth and data mode the assignment
  sets. This is the coordinating session's job, done once before any stage agent is
  dispatched; stage agents do not ask, and write anything they need from the user
  under "Requests for the operator" in the job's `00_INTAKE.md`.
- **Billing.** Reviews are meant to run on the Claude subscription Claude Code is
  logged in with. When confirming, check whether `ANTHROPIC_API_KEY` is set without
  printing it (`[ -n "${ANTHROPIC_API_KEY:-}" ] && echo set`); if it is, tell the user
  the run may be billed to that key instead, and that `/status` shows which.
- **Clearance first, every time.** Run
  `python3 .claude/skills/dkf-review/scripts/scan_job.py --root jobs/<job>` before
  opening any file in a job. On a non-zero exit, stop and tell the user what the scan
  reported. Never open, print or summarise a file the assignment's data mode does not
  clear, not even "to check whether it is real data". Never read patient-level data
  unless the data mode is `shared` with a recorded clearance.
- Web searches use general terms only (condition, intervention, endpoint), never
  internal IDs, unpublished results or data.
- Long computations (simulations) run in the background with start and end markers
  in their logs; record them in the job's `PROGRESS.md`.
- Dispatch fired module agents one at a time, each finishing its report before the
  next starts, unless the user asks for parallel runs: in the trial, four parallel
  module agents used up a subscription session's allowance, and one at a time a usage
  limit stops at most one part-way.
- When the user asks to continue a job, resume from its `PROGRESS.md` under the
  `dkf-review` progress-file rules.

## Developing the skills

- The four skills share one version (`metadata.version` in each `SKILL.md`). A change
  to what a run, audit or consistency review must do bumps the version in all four and
  adds a row to `.claude/skills/dkf-review/spec-changes.csv`; wording-only changes bump
  the version without a row. Check with
  `python3 .claude/skills/dkf-review/scripts/check_suite_version.py`; tag a settled
  version as `skills-vX.Y.Z`.
- Run the tests before committing (from `.claude/skills/`):
  `python3 -m pytest -q -p no:cacheprovider dkf-review/scripts/tests dkf-review-audit/scripts/tests dkf-consistency-review/scripts/tests dkf-consistency-review/ai-sweep/scripts/tests dkf-synthetic-data/scripts/tests`
- Gate scripts use the Python standard library only; recomputation and synthetic-data
  helpers are R (base R and `stats`), each with a test script.
- Keep `.claude/skills/UPSTREAM.md` current: which files are verbatim upstream copies,
  which are adapted, which are new. `tools/upstream_diff.sh <research_skills clone>`
  lists upstream changes since the recorded commit; port what applies and update the
  recorded commit.
- Skill text follows the upstream register: terse, rule-first, every requirement
  checkable, no narrative of the procedure. Name the substance, never a bare section
  number or ID.
- Fold what a real run gets wrong into the skills in general terms. Examples and
  worked cases use invented numbers that mirror no reviewed product: a product's own
  numbers prime the next review of it, and job contents never leave the job.
