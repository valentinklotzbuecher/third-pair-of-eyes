# stats_review: project notes

This repository holds agent skills for AI-assisted consistency review of DKF
statistical products (`.claude/skills/`), adapted from research_skills. `README.md` is
the user guide. The earlier API prototype is in `archive/` and is not maintained.

## Running a review

- Use the `dkf-review` skill, then `dkf-consistency-review` (and `dkf-review-audit`
  first at depth `full`). The `dkf-review` skill's "Before the run" rules (where the
  job lives, clearance, confirmation, usage, billing) bind here too.
- Real reviews live in the product's own repository, never here. This repository's
  `jobs/` holds trial and demo jobs only and stays git-ignored: never commit a job here
  or copy its contents elsewhere. The one exception is a synthetic demonstration
  product the user names (such as DEMO-TKA from `scto-ai-review`): its review outputs
  may be copied where the user asks.

## Developing the skills

- The four skills share one version (`metadata.version` in each `SKILL.md`). A change
  to what a run, audit or consistency review must do bumps the version in all four and
  adds a row to `.claude/skills/dkf-review/spec-changes.csv`; wording-only changes bump
  the version without a row. Check with
  `python3 .claude/skills/dkf-review/scripts/check_suite_version.py`; tag a settled
  version as `skills-vX.Y.Z`.
- Run the tests before committing (from `.claude/skills/`):
  `python3 -m pytest -q -p no:cacheprovider dkf-review/scripts/tests dkf-review-audit/scripts/tests dkf-consistency-review/scripts/tests dkf-consistency-review/ai-sweep/scripts/tests dkf-synthetic-data/scripts/tests ../../chat-skills/tests`
- Gate scripts use the Python standard library only; recomputation and synthetic-data
  helpers are R (base R and `stats`), each with a test script.
- `chat-skills/` holds stand-alone skills for Claude chat, outside the suite and its
  version: each carries its own `metadata.version` and names the suite version it
  follows in `metadata.based-on`. Their helpers use the Python standard library only (a
  chat's sandbox may have no R); copies of suite files stay identical. A change to what
  the document stage requires is ported to `dkf-document-check`. After any change run
  `python3 chat-skills/build_zip.py`; the tests check the ZIP, the copies and the port
  of `recompute.R`.
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
