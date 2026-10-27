# stats_review: project notes

This repository holds agent skills for AI-assisted consistency review of DKF
statistical products (`.claude/skills/`), adapted from research_skills. The earlier
API prototype is in `archive/` and is not maintained.

## Running a review

- Use the `dkf-review` skill, then `dkf-consistency-review` (and `dkf-review-audit`
  first at depth `full`). Jobs live in `jobs/<job>/`, which git ignores: never commit
  or copy job contents elsewhere.
- **Before starting a review of a real product, confirm with the user**: a
  standard-depth review runs many agent turns for tens of minutes or longer and costs
  far more than a single model call. Say which depth and data mode the assignment
  sets.
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
