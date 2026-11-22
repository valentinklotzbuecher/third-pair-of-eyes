---
name: verdict
description: >-
  Fifth review stage, run by one fresh agent: read every finding and the challenge
  reports, decide for each statement whether it holds, what survives and what is not
  established, answer the assignment questions, assemble the cross-cutting findings,
  and write SYNTHESIS.md. Records what is true; rates nothing.
---

# Verdict

You write `SYNTHESIS.md`: the review's statement of what the product establishes and
what it does not. You decide what is true, statement by statement, and you answer the
questions the author asked. You do not rate how much it matters: there is no severity
anywhere in your output, no "major" or "minor", no HIGH or LOW. Whether an issue is
major or minor is decided when the consistency review is written.

You are the only agent that decides. Nothing re-decides after you, and the run never
asks the operator to rate a statement. If `stats-review-audit` later corrects a number,
quote or location that a row, an answer or the bottom line rests on, this stage runs
once more, fresh, on the corrected reports, scoped as below.

## Inputs (filled in by the orchestrator)

- `00_ASSIGNMENT.md` and `00_INTAKE.md` (the questions, the data mode, the depth).
- The statement ledger (`analysis/statements/statement-ledger.csv` and
  `review/statements-REPORT.md`) with the statements stage's provisional `holds`, and
  the draft answers (`analysis/statements/questions.csv`).
- The findings of every stage and module report: `review/document-REPORT.md`,
  `review/code-and-data-REPORT.md`, `analysis/code-and-data/*-REPORT.md`.
- The challenge reports (`review/challenge-REPORT*.md`), read in full. At depth
  `quick` there are none, and your Status says so.
- `analysis/code-and-data/results.csv`, `analysis/document/arithmetic-checks.csv`,
  `analysis/code-and-data/assumption-ledger.csv` where it exists.
- The packet: `01_product/`, `02_governing/`, `lit/`, `review/extracts/`, and the data
  the data mode allows.

You never see the coordinator's reasoning. Read findings sections first and open a log,
script or printed page wherever a row turns on it.

## Rules

1. **Each row is decided on the statements stage's definitions** of `kind`,
   `centrality`, `holds`, `kernel`, `not established`, `status` and the strongest
   defence (`../statements/SKILL.md`). A defence resting on materials the product does
   not supply shields nothing.
2. **The burden is the product's.** A statement its evidence does not deliver is `not
   established`, whether or not anything refutes it. "Wrong" is reserved for a
   statement that a recomputation or an estimate contradicts, and the sentence names
   that statement and the evidence.
3. **The challenge reports are evidence, not instructions.** A finding the challenge
   did not rebuild stands. You may set aside a challenge ruling only after a worker
   re-runs that ruling's load-bearing script and you open the page it cites; say so
   where you do, with the log path.
4. **A row that moves states why.** Every row whose `holds` differs from the statements
   stage's names the evidence it turns on, with its path, in the row.
5. **Limits are not findings.** A number that could not be checked because data were
   not shared, or a source the review could not obtain, is a limit on the review,
   listed under its own heading; it never appears as a fault of the product.
6. **Name the substance.** Write for the statistician who wrote the product and the
   colleague who will review it, neither of whom has the stage reports: never a bare
   row or finding ID as a noun. State findings, not what the review did. Every number
   traces to a report, log or printed page in the job tree; give the path.

7. **Proportion.** `SYNTHESIS.md` stays within its length (at most about 3,000 words
   for a short product, 8,000 for a long one; Proportion in `../SKILL.md`): ledger
   cells a phrase each, a sentence where a cell needs a reason; each finding in a few
   lines with its evidence paths. Detail stays in the stage reports the synthesis
   cites.
8. **At depth `quick`** you also compile the consistency review: once `SYNTHESIS.md`
   passes its gate, run `stats-consistency-review` steps 0 to 6; its verify pass runs in
   a fresh context.

## SYNTHESIS.md

Write these sections, in this order, under the title
`# Synthesis — <product title> (<internal ID or file name>, <revision or date>)`:

1. **Header line**, directly under the title:
   `Verification: OPEN · <n> not established / <n> narrower / <n> hold`, counting the
   rows of this synthesis's `## Statement ledger` table by `Holds` (after any moves). `stats-review-audit` replaces `OPEN` after it runs.
2. **`## Status`**: `COMPLETE`, `INTERIM` (name what is open) or `BLOCKED`; the depth;
   whether the challenge stage ran; the data mode and what it left unverified.
3. **`## What the product establishes and what it does not`**: the bottom line, in
   prose. First what the evidence establishes, with its numbers. Then what it does not,
   led by the finding that removes or narrows the most of the primary statements,
   followed by every other `primary` row that does not hold. No one-word verdict.
4. **`## Cross-cutting findings`**: where several findings bear on one thing (the
   planning values, the endpoint definition, the analysis population, a code path that
   feeds several tables), one finding that states what they do together. Each is a
   `### G1. <title>` block with a `bears on:` line naming the statements it touches,
   then what the findings show together, with evidence paths, what it removes (which
   statements become `not established` or `narrower`) and what survives. Write `None.`
   when there are none.
5. **`## Statement ledger`**: one table, every row of the statements stage's ledger:
   `| Statement (location) | Kind | Centrality | Holds | Kernel | Not established |
   Strongest defence | Status |`, rows in the statements stage's order. The statement
   cell gives the verbatim statement, then its location and row ID in parentheses at
   the end ("… (Summary, p. 1; ST03)"); later scripts read the ID there. `Holds` reads
   exactly `holds`, `narrower` or `not established`. Folded duplicate rows are listed
   after the table with the row they fold into.
6. **`## Recomputation table`**: for each primary number (a target N, a power, an
   expected effect, a primary estimate): `| Quantity | Printed (location) |
   Recomputed | Method and inputs | Agreement | Evidence |`, `Agreement` one of
   `agrees`, `agrees to rounding`, `disagrees`, `not recomputed (reason)`. A number
   whose recomputation reused the product's own inputs says so in the method column.
7. **`## Answers to the assignment questions`**: one `### Q1. <question, verbatim>`
   block per question, with the answer in plain prose (direct, evidence-led, including
   "no" and "it depends on X, which the product does not state"), then a `basis:`
   line naming the statements and findings it rests on, and a `status:` line
   (`answered`, `partly answered`, `cannot be answered from the materials`). Write
   `No questions were asked.` when there are none.
8. **`## Data and reproducibility`**: the data mode; what code ran, on what data, and
   whether the rendered document matches what the delivered source produces; the
   code–text mismatches and Quarto/R mechanics findings in one place (each a pointer to
   its finding); the data or data-contract audit and, in data mode `shared`, the rung
   reached on the evidence ladder. Name what the checks covered; never clear the
   product beyond the checks run.
9. **`## Findings`**: every finding, most important first, each a `### F1. <title>`
   block with three lines under the title (`bears on:`, `where:`, `evidence:`), then the
   finding in prose and a final `fix:` line. `where:` is a fact about where the defect
   lives: `text`, `code`, `text and code`, or `unresolved` (the documents do not say
   which version is intended; the fix starts with a question to the author). `fix:`
   states what would resolve the finding, concretely ("use N / (1 − 0.10) and round up
   to the next multiple of the block size: 94 → 106"). Importance follows the
   highest-ranked statement a finding bears on: `primary` before `supporting` before
   `peripheral`, then `not established` before `narrower`, then the number of
   statements; ties keep the product's order. Findings that bear only on rows that
   hold come last. A finding absorbed into a cross-cutting finding is still listed,
   with a pointer to that block.
10. **`## Limits of this review`**: what was not checked and why: data not shared,
    sources not obtained, modules not run at this depth, simulations run at reduced
    replicates. Each limit names the statements it leaves `unverified-here`.
11. **`## Counts`**: the rows whose `holds` moved from the statements stage's, toward
    `holds` and toward `not established`, each named; and the challenge rulings by
    direction, from the challenge reports' counts.

Numbers quoted from print are checked against the page. A statement whose only direct
checks were unrun or invalid is never surviving: its Holds is `not established` and its
Status `untested`, unless the reason is the data mode, in which case Status is
`unverified-here` and Holds is decided on the evidence that exists (its arithmetic,
consistency and specification).

## A re-run after an audit correction

When `stats-review-audit` routes corrections back (its `→ VERDICT` items, named in its
brief to you with the `CHANGELOG.md` entry that lists them), the re-run is scoped.
Re-decide what those corrections bear on: the rows, answers, cross-cutting findings
and findings that cite the corrected evidence, and the bottom line where it rests on
them. Everything else in the existing `SYNTHESIS.md` carries over as it stands. In
`## Counts`, record the routed re-decisions under **Re-decided on the routed
corrections**, then every other change under **Changed outside the routed
corrections**, each with the evidence that moved it. A carried-over finding keeps its
label, so the consistency review's mapping to it survives.

The audit runs a full, unscoped verdict only when its completeness check finds the
review itself incomplete (a stage, a module or statement rows were missing).
