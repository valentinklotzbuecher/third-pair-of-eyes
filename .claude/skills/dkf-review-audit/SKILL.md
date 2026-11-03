---
name: dkf-review-audit
description: >-
  Mechanical audit-and-fix pass over a completed `dkf-review` run, used at depth
  `full` or when a review is reused. Checks completeness (every stage and fired
  module ran; every printed table and figure, every code chunk and every file the
  code reads is covered; every assignment question is answered) and mechanical
  errors (scripts re-run clean, numbers match the print, the right row, findings
  propagated, every number traceable). Rates no statement: a correction a ledger row,
  an answer or the bottom line rests on goes back to the verdict stage. Declares the
  evidence handoff for the consistency review.
metadata:
  version: "0.2.0"
  based-on: "research_skills `audit-review` 0.9.1 (isitcredible/research_skills@766f28f)"
---

# Audit a review

Check a completed `dkf-review` run for **completeness** and **mechanical errors**, fix
what fails, and leave the run's own reports correct. The audit decides nothing about
what the evidence establishes: whether a statement holds is the verdict stage's call,
and the audit routes any correction that bears on it back there (step 4). The product
is the corrected reports, not a report about the audit. Corrections go into the run's
own files; the audit's scripts and logs go under `work/audit/`. The only new files the
audit writes elsewhere are:

- `CHANGELOG.md`: the corrections list (the only file that says old → new);
- `coverage.csv` (generated) and `coverage-na.csv` (your not-applicable rulings);
- `spec-drift.csv` (generated, with your dispositions);
- `HANDOFF.md` and the generated `HANDOFF.manifest.json`: the evidence the
  consistency review may cite.

Corrected reports read as if they were right first time: every sentence makes sense to
a reader who never saw the earlier draft. Name the substance, never a bare section
number or row ID as a noun (`dkf-review` rule 10). The data-protection rules of
`dkf-review` (rule 11) bind the audit: it reads only what the assignment clears.

## Ground rules

- The run's logs, manifest and synthesis are what you are checking, not evidence that
  it is right. A number that reproduces is not thereby correct: re-running a script
  says nothing about whether it matches print, comes from the right row, or whether the
  calculation is sound.
- A fix produces evidence. Never edit a report to say PASS. A FAIL is either the
  review's error (fix it) or correct work showing the *product* fails (keep it). Never
  fix away a true finding.
- The checklist is the `dkf-review` skill at the version the run records (`Suite
  version:` in `00_INTAKE.md`); `check_spec_drift.py` lists what the run was never asked
  to do. Record the version you audit against in `CHANGELOG.md`.
- **Back up with the repository, never with copies.** Commit the job tree before
  applying corrections (a job folder that is not a repository gets `git init`, local,
  no remote; the `jobs/` folder of the stats_review repository is git-ignored, so the
  job's own repository never reaches GitHub). Re-run in place and read drift with
  `git diff`.
- Size, route and run every worker by `dkf-review`'s *Agents and cost* section. Every
  audit task is mechanical; the one judgement task, a verdict re-run, is the verdict
  stage run by its own rules.
- Unattended, resolve every pause by rule: keep the evidence, record the call and the
  reason, continue.

## 1. Completeness: was everything covered?

Each miss is a FAIL, and the fix is to do the missing work, not to note it.

- **Stages and artifacts.** Run `python3 <dkf-review skill>/scripts/check_job.py --root
  <job> --stage all`. Every stage report and artifact exists and is substantive; every
  fired module has a report; the statement ledger has every column; the synthesis has
  every section. A run at depth `standard` or `full` without challenge reports gets the
  challenge stage now.
- **Spec drift.** Run `python3 <dkf-review-audit skill>/scripts/check_spec_drift.py --root
  <job> --write`, do each pending item or rule it `na: <reason>`, then run it without
  `--write` until it passes.
- **The printed product and its source.** Run `python3 <dkf-review-audit
  skill>/scripts/check_coverage.py --root <job>`. Every printed table and figure has a
  ledger row; every code chunk is named in the specification map, a ledger, a report or
  a log; every file the code reads has a feasibility row. Fix by deriving the row, or
  rule it not applicable with a reason in `coverage-na.csv`.
- **The statements.** Re-read the product's summary, conclusions and the sections its
  profile names. Every load-bearing sentence maps to a ledger row; a missing statement
  gets its row (and goes through the challenge stage before the verdict re-run).
- **The questions.** Every assignment question has an answer in `SYNTHESIS.md` that
  answers what was asked.
- **Gaps.** Every `BLOCKED`, `NOT_RUN` or "cannot be checked" carries its evidence (the
  file, command and error, or the data mode). A gap that is feasible and that a
  statement depends on is run now.
- **Data mode.** No check claims more than its data mode allows: a synthetic run is
  never cited for a printed number; nothing in the job was read that the assignment
  did not clear.

## 2. Mechanical errors: do the reports match the scripts, the logs and the print?

Work through what the primary statements rest on first.

a. **Re-run** the scripts the findings rest on (recomputations, simulations at their
   recorded seeds, arithmetic checks). A script that errors or prints a different
   number is a FAIL as serious as a wrong result; on any mismatch, widen the re-run.
b. **Print check.** Every number, quote and location attributed to the product matches
   the rendered product: open the printed page or `file.qmd:line`, never the review's
   own output. A wrong baseline voids every comparison made against it.
c. **Row check.** Each reproduced or recomputed number comes from the script and log
   row that computes *that statement's* quantity: same endpoint, analysis set, time
   point, method and units.
d. **Propagation.** Every logged anomaly names the statements it weakens; a corrected
   shared input (a planning value, a derived variable, a helper function) is re-run
   through every result family that uses it.
e. **Traceability.** Every reported number traces to a script and log in the job tree.

## 3. The corrections list

One item per FAIL in `CHANGELOG.md`: `file · location · old → new`, the new text
written as the finding itself, in final wording. Mark each `EVIDENCE` (needs a number
or artifact: produce it now) or `TEXT` (applied in step 5). An item that could change a
statement's `holds` or kernel, an answer to a question, a cross-cutting finding or the
bottom line is also marked `→ VERDICT`. Every TEXT item carries an **instance hunt**:
grep every report and the synthesis for the wrong number or phrase.

**Open items are only what this audit cannot do**: calls only the operator can make,
and work blocked outside the job (a source still unobtainable, data the mode does not
clear). Each states its evidence, what was attempted and what would close it.
Everything else is done in this audit.

## 4. Route to the verdict stage

If any item is marked `→ VERDICT`, apply the mechanical items first (step 5), then run
the verdict stage once, fresh, on the corrected reports, scoped to the routed
corrections (`<dkf-review skill>/verdict/SKILL.md`, "A re-run after an audit
correction"). Run it unscoped only when the completeness check added stages, modules
or statement rows. The audit decides no statement.

## 5. Apply

Apply every TEXT item yourself, with its instance hunt. Never infer: anything the list
does not cover that could change what a statement establishes is a `→ VERDICT` item.

## 6. Sweep and the header line

Grep the corrected files for draft residue ("previously stated", "was corrected", "the
audit found", "on re-examination") and for bare section numbers or row IDs used as
nouns; anything left becomes a TEXT item. Then set the first word of the synthesis
header line:

`Verification: TRUSTWORTHY | OPEN | UNSOUND · <n> not established / <n> narrower / <n> hold`

`Verification:` rates the review's own evidence, never the product. `TRUSTWORTHY`:
every load-bearing script re-ran clean in this audit and matches the reports and, where
the product prints the number, the print. `UNSOUND`: a load-bearing script still fails
or disagrees after this audit's corrections. `OPEN`: anything else (a load-bearing
check blocked or not re-run, open items, the audit `INTERIM`). Leave the counts as the
verdict stage wrote them.

## 7. Handoff

Write `HANDOFF.md` at the job root once corrections have landed:

- `status:` `COMPLETE` (only when `## conflicts` reads `none` and no statement row is
  `INTERIM`) / `INTERIM` / `BLOCKED`, a reason after `#`;
- `audit:` the date of this audit's `CHANGELOG.md` entry;
- `## inputs`: every artifact the findings rest on, one bare path per bullet;
- `## primaries`: the rendered product and its source, the governing documents, and
  `review/extracts/`;
- `## excluded`: `path | disposition | evidence`, disposition one of `superseded`,
  `withdrawn`, `exploratory`, `unresolved` or `not-evidence` (for example
  `00_INTAKE.md`, `PROGRESS.md`);
- `## conflicts`.

Run `python3 <dkf-consistency-review skill>/scripts/build_manifest.py HANDOFF.md` to
hash-bind it. If the handoff cannot honestly be completed, say so in its status.

Be direct: a FAIL softened to a "minor note", a gate forced green, or a mechanical error
left in place because fixing it would move a statement is the rubber stamp in another
form.
