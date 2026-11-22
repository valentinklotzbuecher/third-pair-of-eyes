# [Stage] Report — [Product title]

The technical record of what this stage established, findings first. Every claim
resolves to an artifact a reader can re-run or check: a script and log, a row in a
ledger, a printed location (page, table, row) or `file.qmd:line`. No narrative of the
procedure.

## Status

`COMPLETE`, `INTERIM` (name what is missing) or `BLOCKED` (give the exact evidence),
the data mode the stage ran under, and one or two sentences on what the stage found
and on what evidence. `COMPLETE` means every applicable check ran and its output was
inspected, not that a file exists. A `PROXY` counts only if it covers the requirement
and states its limits.

## Findings

Most important first (within each group, where the stage groups them), one block each.
Stages number findings `D1` (document), `C1` (code-and-data), `S1` (statements). A
module report uses its own prefix: SS sample-size, SIM simulation, EST estimand, RCT
rct, MD missing-data, TTE time-to-event, MULT multiplicity, RM regression-model, OBS
observational, PM prediction-model, BAY bayesian, SN small-n.

### [D1 / C1 / S1 / SS1]. [Title]
bears on: [the statements this finding touches, named]
where: [text | code | text and code | unresolved]
evidence: [paths to script and log, ledger row, or printed location / file:line]

What is wrong, the printed value against what was found, and its effect: the primary
quantity before and after (an N, a power, an estimate), in its own units. State the
direction: a defect that makes the product conservative is written as conservative.
Say so plainly when a correction leaves the result unchanged.

fix: [what would resolve it, concretely]

A blocked check (exact file, command, error), a check limited by the data mode, and a
justified `NOT_APPLICABLE` are recorded here too, so the gap is visible.

## [Sections the stage requires]

Each section the stage's SKILL requires beyond these goes here, between Findings and
Leads: for `statements`, the supportable version of each primary statement, the
statement ledger, the statement-test matrix and the draft answers.

## Leads for later stages

Checks to run, values to trace, statements to test, questions to answer — each naming
its source.

## Scope assumptions

Limits this stage relied on ("the simulation was re-run at 1,000 replicates", "the
pinned package versions could not be installed; installed versions used"), each with
its evidence. A later stage that overturns one re-checks everything that rested on it.

## Coverage

Documents, code and data examined (and under which data mode); which result families
and calculations this stage reached and which it left open.
