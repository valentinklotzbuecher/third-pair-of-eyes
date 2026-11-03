---
name: dkf-consistency-review
description: >-
  Compile a finished `dkf-review` run into the DKF consistency-review form for the
  human reviewer: Assignment, Decision boxes (computed), General comments, Major and
  Minor issues, Answers to the issues listed in the assignment, and what the review
  could not check. Writes the issue ledger ISSUES.md, gates it for facts, coverage and
  register, renders CONSISTENCY_REVIEW.md/.html (and .org), and can write REVIEW
  comments into a copy of the Quarto source. Use when asked for "the consistency
  review", "the review form", "the reviewer's draft" or to "write up the review".
metadata:
  version: "0.1.1"
  based-on: "research_skills `review-digest` 0.9.1 (isitcredible/research_skills@766f28f)"
---

# Consistency review

Turns a `dkf-review` run into what the second statistician reads and edits:

- **`ISSUES.md`**: the issue ledger (authored here, gated here);
- **`CONSISTENCY_REVIEW.md` / `.html` / `.org`**: rendered from the ledger by
  `scripts/render_review.py`, never written by hand; the Decision boxes are computed;
- **`work/annotated/<file>.REVIEW.qmd`**: optional, a copy of the source with
  `REVIEW` comments at the anchored lines (`scripts/annotate_source.py`);
- **`ERRATA.md`**: defects found in upstream artifacts (internal).

The output is a draft for a colleague. The human reviewer owns the final consistency
review and edits the rendered form freely.

Two rules shape everything. **Extraction, not re-adjudication**: whether each
statement holds, what survives, what was checked and what was not come from
`SYNTHESIS.md` as it stands. A finding that looks wrong is an `ERRATA.md` item for the
verdict stage, never an in-place fix. **The subject is the product, never the
review's process**: no sentence reports what the review suspected, ran or discarded;
review artifacts, row IDs and stage names never appear in rendered prose (provenance
lives in `sources:`).

**Severity is assigned here** (Major or Minor) as the DKF form needs it: a default
from the statement rows each issue carries, from which the compiler may depart with a
stated reason. **Where the fix lies** (text, R code, both, or a clarification) comes
from each finding's `where:` line in the synthesis.

## Steps

Commands run from the job root (the folder holding `SYNTHESIS.md`); `scripts/` is this
skill's directory.

0. **Check the inputs are current.** `SYNTHESIS.md` exists and its Status is not
   `BLOCKED`. At depth `full`, the audit's `HANDOFF.md` and `HANDOFF.manifest.json`
   exist. An `INTERIM` synthesis compiles and renders as a preview, never final.
1. **Compile `ISSUES.md`** in the format below, from `SYNTHESIS.md` (bottom line,
   statement ledger, cross-cutting findings, findings with `where:` and `fix:`,
   answers, limits) and the assignment. Numbers and quotations enter only from the
   synthesis and the stage reports, never paraphrased fresh from the product.
   - **One issue per problem a colleague would fix in one go.** A cross-cutting
     finding usually becomes one issue; several findings about the same table may
     become one issue. Every finding still maps somewhere (step 3).
   - **Each issue body** says what is wrong and where (printed location, and
     `file.qmd:line` for code), the evidence with its numbers, why it matters for the
     product's statements, and ends with the fix (from the finding's `fix:` line).
     Three to eight sentences; no hedging beyond what the evidence carries.
   - **Severity**: the default below, or a departure with `severity-reason:`.
     **change**: from the mapped findings' `where:` (`text`, `code`, `text and code`;
     `none` only for a pure question). **clarification: yes** when a mapped finding's
     `where:` is `unresolved` or the fix needs the author's decision.
   - **General comments**: two to five sentences: the overall state of the product
     and the highest-priority risk, conveying the synthesis's bottom line, led by the
     same finding and no softer than it. They may state what was confirmed when the
     assignment asked for confirmation ("the sample size of 270 is reproduced by an
     independent calculation").
   - **Answers**: one block per assignment question, from the synthesis's answers,
     in the reviewer's voice, direct ("Yes, …", "No, …", "It depends on …, which the
     product does not state"). Keep each answer's `status:` line.
   - **Not checked**: the synthesis's limits, as facts about the review's reach
     ("Patient data were not shared, so the printed results tables were checked for
     internal consistency only."), never as faults of the product.
   - **Anchors** (optional): `anchor: 01_product/<file>.qmd:<line>` where a REVIEW
     comment in the source would help the author find the spot.
2. **Fact gate.** `python3 scripts/check_facts.py ISSUES.md`: every quoted span must
   be found in a primary source (the product, governing documents, extracts, cited
   works; never the review's own prose) and every number in the job's corpus. A quote
   with an elision gets a line in `ISSUES.facts.md` confirming no qualifier was dropped.
   The judgment pass then confirms per hit that each number is the same quantity (N
   evaluable against N randomised, % against percentage points, months against days),
   and records `gate: <context> — <date> — sha256:<first 12 of ISSUES.md>` in
   `ISSUES.facts.md`. Re-run until it exits 0.
3. **Coverage gate.** Write `ISSUES.coverage.md`: one line per declared finding of the
   synthesis, its ID in backticks: `` `F3` → issue 2 ("title words") ``,
   `` `G1` → issues 1, 3 ``, `` `ST04` → issue 2 ``, `` `F7` → not checked ``,
   `` `F8` → general comments ``, `` `F9` — excluded: <reason> ``. Declared findings
   are every statement row that does not hold, every cross-cutting finding and every
   finding; a primary or supporting row that does not hold always maps to an issue.
   Run `python3 scripts/check_issue_coverage.py ISSUES.md` until it passes; it also
   computes each issue's default severity and lists departures. Record the `gate:` line.
4. **Register gate.** `python3 scripts/check_style.py ISSUES.md` runs the nested
   `ai-sweep` engine (machine register, exposed working) and the failures-only rule for
   the issue list: an issue reports what is wrong, never what checked out. Without a
   passage scanner (`PASSAGE_SCANNER` unset) the register layer is a manual pass over
   the whole ledger, recorded in `ISSUES.keeps.md` as
   `gate: manual pass — <date> — sha256:<first 12>`. In the same pass, read for the
   colleague register: no motive or blame ("the author ignored"), no sarcasm, no
   absolute language the evidence does not carry ("clearly wrong"), and every issue
   has a concrete fix. Rewrites change wording only, never a finding, a number or a
   severity.
5. **Render.** `python3 scripts/render_review.py ISSUES.md --org` writes a preview.
   `--finalize` refuses unless the ledger's status is `COMPLETE`, the fact and
   coverage gates were recorded on this exact ledger revision, the coverage gate
   passes, and (at depth `full`) the handoff manifest's inputs are unchanged.
6. **Annotate** (when issues carry anchors): `python3 scripts/annotate_source.py
   ISSUES.md` writes `work/annotated/<file>.REVIEW.qmd`; the delivered source is never
   edited.
7. **Verify**, in a fresh context where the harness allows: open
   `CONSISTENCY_REVIEW.html` and check that the Decision boxes follow from the issues,
   that every issue has a location and a fix, that the general comments carry the
   synthesis's bottom line, that every question is answered as asked, and that no
   rendered sentence's subject is the review's own activity. Save the record as
   `work/digest/verify-pass.md`, ending with its `gate:` line. A different bottom line
   is an `ERRATA.md` item for the verdict stage, never a reorder.

## Severity

The default for each issue is the most severe over the statement rows it carries
(mapped directly, or through the `bears on:` line of a mapped finding):

| Row's `holds` | `primary` | `supporting` | `peripheral` |
|---|---|---|---|
| `not established` | Major | Major | Minor |
| `narrower` | Major | Minor | Minor |

An issue that carries no row that fails defaults to Minor. "Major" in the DKF form
means a change that needs a second review; depart from the default with a
`severity-reason:` naming the fact that justifies it ("the slip is in one caption;
the code and four other mentions use the right value", "the missing source exists and
is cited elsewhere in the protocol"). `check_issue_coverage.py` lists every departure.

## ISSUES.md format

```markdown
---
product: <title> (<internal ID>, <revision>)
statistical-product: <file name from the assignment>
status: COMPLETE | INTERIM | BLOCKED        # from SYNTHESIS.md's Status
verification: <copied from the SYNTHESIS header line>      # internal
depth: quick | standard | full
data-mode: none | synthetic | shared
date: <yyyy-mm-dd>
---

## Assignment

- Name of the statistical product: <…>
- Important issues for reviewer:
  1. <question, verbatim>
- Other documents this document depends on:
  - <…>

## General comments

<two to five sentences>

## Issues

### 1. <title: the problem, stated as a fact>
severity: Major | Minor
severity-reason: <only when departing from the default>
change: text | code | text and code | none
clarification: yes | no
category: Design and estimand | Sample size | Analysis specification | Numerical consistency | Code and reproducibility | Interpretation | Reporting
evidence: established | strong | plausible | unresolved     # internal
location: <printed location; file.qmd:line for code>
anchor: <01_product/file.qmd:line; optional, internal>
sources: <;-separated paths from the job root, internal>

<body, ending with the fix>

## Answers to the assignment

### Q1. <question, verbatim>

<answer>

status: answered | partly answered | cannot be answered from the materials

## Not checked

- <limit of the review>
```

`location:` renders; `severity-reason:`, `evidence:`, `anchor:` and `sources:` never do.
Issues are numbered in reading order: the issue carrying the finding that leads the
bottom line first, then issues a later one rests on before that one, then the
product's own order. The renderer splits them into Major and Minor.

## Errata

`ERRATA.md` beside `ISSUES.md`, cumulative, items never deleted, each a `### E<n>.`
block with `status: open | closed` and `finding-bearing: yes | no`. A mechanical slip
in an upstream artifact that touches no finding is patched with a dated `CHANGELOG.md`
line. Anything that could change a statement's `holds`, an answer, or the bottom line
is `finding-bearing: yes`, routed to the verdict stage (through `dkf-review-audit` at
depth `full`), and blocks `--finalize` until closed.
