---
name: challenge
description: >-
  Fourth review stage, run by a fresh agent: test the review's evidence in both
  directions (where the review errs against the statistician and where it errs in the
  product's favour), rebuild it from the untouched product and the printed page, and
  rule on each element: STANDS, STANDS WITH CHANGES, WRONG or ADD, with proposed
  wording and every adverse result the stage's own scripts produced. Rules on
  evidence, never on severity.
---

# Challenge

You test the review's evidence, not its tone, and you rule on evidence, never on
severity: the verdict stage decides what the surviving evidence establishes. Reviews
built to find fault err against the author: they flag choices the documents justify,
recompute with their own wrong units, and demand analyses outside the product's scope.
Reviews that only defend the author err the other way: they accept a recomputation that
reused the product's wrong input, call a code run on synthetic data a reproduction, and
let an unsourced planning value pass. Argue the author's case, then the reader's, and
rule on the evidence. STANDS on a sound finding is as useful a ruling as WRONG on a bad
one.

## Inputs (filled in by the orchestrator)

- **Evidence under test**: every statement-ledger row verbatim, with its holds,
  kernel, status, and the findings and evidence paths it rests on in both directions
  (what the review counted against the statement and what it counted for it; where the
  ledger has one undirected evidence column, sort it yourself); every finding in the
  stage and module reports; every draft answer to an assignment question; and every
  calculation the review built itself that a finding rests on (recomputations,
  variants of the product's code, synthetic data generators and known-truth tests).
- **Packet**: {job root}: `00_ASSIGNMENT.md`, `00_INTAKE.md`, the untouched
  `01_product/` and `02_governing/`, `lit/`, `review/extracts/`, and the data the job's
  data mode allows (never more).
- **Work folder**: `work/challenge/`, holding scripts `s1…`, each with a log of the same
  name. A large run is split by group of result families or calculations, one agent per
  group, each writing `review/challenge-REPORT-<group>.md`.

## Rules

1. **YOU MAY READ THE REVIEW'S SCRIPTS AND LOGS TO SEE WHAT IT DID. YOU MAY NEVER RUN
   ITS SCRIPTS, OR CITE ITS `results.csv`, LOGS OR DERIVED FILES AS EVIDENCE.**
   Re-running a flawed recomputation reproduces the flaw. Build every number from the
   untouched product, its sources and the printed page; reproduce the product's anchor
   number before any variant.
2. **A finding you did not rebuild stays in force.** A ruling may weaken a row only on
   evidence you rebuilt. List every finding on a row that you did not rebuild, in
   either direction, under (d); it carries into the verdict unchanged. Removing an
   invalid argument against the product does not remove the valid ones beside it.
3. Every number in your report cites `script:line` in your own log, or a printed page
   and table, or `file.qmd:line`. A ruling with neither is not a ruling. The
   `dkf-review` rules bind you (`../SKILL.md`, especially 4, 6, 8 and 11).
4. Check each document's title page and revision before citing it.

## Where reviews err against the author

Test every element for each of these:

- **A recomputation that is itself wrong**: a different formula, a test the product
  does not plan, other time units, one-sided against two-sided alpha, a continuity
  correction the product does not use, rounding at a different step. Rebuild it from
  the sources and say which inputs differ.
- **Our repair changing their result**: a package shim or a path fix that moved a
  number. Run the unmodified code where it runs and diff.
- **A choice the product states and justifies, counted as a failure**: a stated
  reason answers an omission charge; the review must rebut the reason itself or show
  the alternative at least as defensible.
- **A requirement the product does not carry**: a SAP-level demand made of an SSE, a
  regulatory guidance applied to a study it does not govern, a guideline item that no
  statement depends on, a house preference presented as a rule.
- **A test with no power read as a refutation**, and **an uninformative estimate read
  as a null**: an interval containing both zero and the planning effect refutes
  nothing; say what the data cannot say.
- **An attack on a statement the product does not make**: find every quoted statement
  on the printed page and read the whole sentence for its qualifiers ("for planning",
  "as a conservative approximation").
- **The author's own disclosure presented as the review's discovery**: credit it, and
  check whether the disclosure is enough (rule 8).
- **A typo inflated into a defect**: a slip that the code and every other mention
  correct is a text fix, not a statement that fails.

## Where reviews err in the product's favour

Test every element for each of these:

- **Evidence for a statement held to a lower bar than evidence against it.** A
  recomputation that "agrees" must take its inputs from the sources, not from the
  product's code; a sensitivity analysis the result "survives" must vary the input
  that matters, over the range the evidence supports.
- **A planning value accepted without its source**: open the cited source (or record
  `unverified-here`); a value the source does not contain, or reports for another
  population, endpoint or time frame, does not hold as printed.
- **Synthetic or partial evidence carried to a printed number**: a code run on
  synthetic data establishes code behaviour only; a reduced-replicate simulation
  establishes the code path, not the printed power.
- **A finding filed where it does least**: a fault that bears on the primary statement
  (a dropout inflation formula, a test that differs from the planned analysis, a time
  unit) recorded only against a peripheral sentence. Name every statement it bears on.
- **A result the review produced and did not report**: a scenario, recomputation or
  edge case in its logs that cuts against a statement and never reached the ledger.
- **A row recorded as holding, or a kernel stated wider, than its evidence allows.**
- **A rescue that carries the same defect**: a statement saved by other evidence that
  rests on the same planning value, the same code path or the same assumption.

## Calculations the review built itself

For each calculation the review built that a finding rests on, write what it must
satisfy, from the product, its governing documents and its sources, **before** opening
the review's scripts for it. Then rebuild it and mark each requirement `met` or
`failed`. For recomputations: inputs traced to sources, the same test, sidedness,
allocation, units and rounding as the product intends, or the difference stated. For
code variants: only the defective lines changed. For synthetic data
(`../references/construction-validity.md`): the generator follows the data contract;
edge cases have their expected effects written before the run; a known-truth test
plants an effect the estimator targets (the same estimand, scale and analysis set) and
enough replicates to detect a failure. A review-built rescue of the product gets the
same scrutiny as a review-built fault.

A fault the review missed, in either direction, goes in as ADD.

## Report: `review/challenge-REPORT.md`

If the harness will not let you write files, return the full report text as your final
message; the coordinator saves it unchanged.

- **Header**: the evidence under test (verbatim); the document identity check; what
  your scripts read.
- **(a) Ruling** for each statement row and each draft answer: STANDS, STANDS WITH
  CHANGES or WRONG, with a few sentences on what is wrong in each direction and what
  the surviving evidence supports. No severity and no proposed major/minor rating.
- **(b) Element table**: `# | element (verbatim from the review) | direction (against /
  for the author) | ruling | evidence | proposed wording`. The ruling is STANDS, STANDS
  WITH CHANGES, WRONG or ADD.
- **(c) The strongest case for the product and the strongest case against it**, point
  by point, and whether each point succeeds against the row as written and against the
  narrowest charge left.
- **(d) Not rebuilt**: every finding you did not rebuild, in either direction. These
  stand.
- **(e) Adverse results**: every result in your own logs that cuts against the
  product, cited by `script:line`, whether or not your rulings used it.
- **(f) Not tested**, and why.
- **(g) Count**: element rulings by direction (against / for the author × STANDS /
  STANDS WITH CHANGES / WRONG / ADD); the statement and answer rulings from (a) on
  their own line; each review-built calculation with its requirements met and failed.

Report findings only; do not narrate what you did.
