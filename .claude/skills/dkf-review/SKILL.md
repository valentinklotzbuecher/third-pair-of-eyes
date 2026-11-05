---
name: dkf-review
description: >-
  Pre-human consistency review of a DKF statistical product written in Quarto/R: a
  sample size estimation (SSE), the statistics sections of a protocol, a statistical
  analysis plan (SAP), a statistical analysis report or a results manuscript. Reads
  the rendered document against its source code and the documents that govern it
  (protocol, SSE, SAP, registry entry), recomputes what can be recomputed without
  patient data, runs the code on synthetic data where data cannot be shared,
  challenges every finding in a fresh context, and records statement by statement
  what the product establishes. Use when asked to review, check or consistency-review
  a statistical product, an SSE, a SAP or a statistical report.
metadata:
  version: "0.3.0"
  based-on: "research_skills `review` 0.9.1 (isitcredible/research_skills@766f28f)"
---

# DKF statistical review

Establish whether a statistical product says what its evidence supports and whether
its code does what its text says, before a second statistician does the consistency
review. The review prepares that human review; it does not replace it. It reports what
it found, with the evidence, and what it could not check, with the reason.

The strongest form a criticism takes is *"the product does not establish this"*:
assert the gap, never the opposite claim, which would be the same overclaim the review
exists to catch. A full review that finds no fault is a valid outcome, reported as
such.

The review establishes what is true; it rates nothing. Each load-bearing statement of
the product is recorded as holding, holding only in narrower form, or not established,
with what survives. Whether a finding is a major or a minor issue, and whether it
calls for changes to the text, to the code or for a clarification, is decided when the
consistency review is written (`dkf-consistency-review`).

## Products

| Product | `product_type` | Load-bearing statements |
|---|---|---|
| Sample size estimation | `sse` | target N (randomised and evaluable), power, alpha and sidedness, the effect and every planning value, the analysis the calculation assumes |
| Protocol, statistics sections | `protocol` | the SSE statements plus endpoints, estimand, randomisation, analysis overview, interim analyses |
| Statistical analysis plan | `sap` | estimands, analysis sets, primary and key secondary analyses, intercurrent events and missing data, sensitivity analyses, multiplicity |
| Statistical analysis report | `report` | results, their interpretation and the conclusions, against the SAP |
| Results manuscript | `manuscript` | abstract and conclusions, against the report and the SAP |
| Anything else | `other` | stated in `00_ASSIGNMENT.md` |

`references/product-profiles.md` gives each type's governing documents, core checks,
core modules and what is out of scope.

## Rules that bind every stage

1. **The document as delivered for review is the record.** Read the title page,
   version or revision line and date of every document (product, protocol, SAP,
   registry entry) and record them at intake. Every statement and number resolves to
   the rendered product. Where only the Quarto source was delivered, the source as its
   own code renders it is the record, and every number cited from it comes from a
   logged run. A rendered document that the delivered source no longer produces (a
   printed number the code does not compute, a revision line that differs from the
   source's) is a finding.
2. **Coverage is a list, not an impression.** The consistency matrix, specification
   map, arithmetic checks, check manifest and statement ledger are the record of what
   was checked. "I looked carefully" is not.
3. **Every number the review reports traces to a saved script and its log** in the
   job tree, re-run clean before it is cited. Mental arithmetic is not a number.
4. **Every number, quote and location attributed to the product is pinned** to the
   printed page, table and row (`Table 3, row "Mucositis/stomatitis", p. 3`) or to
   `file.qmd:line`, and checked there, never against the review's own output, an
   earlier version or memory. A quote keeps its qualifying clause ("under the main
   planning assumptions", "for planning"). Numbers compared as like for like share
   endpoint, population, analysis set, time point and scale; a comparison across them
   says what differs and draws no conclusion that needs them to match.
5. **A blocked stage still reads the print.** Without data, every printed table is
   still checked for internal consistency and arithmetic: percentages against counts,
   totals, intervals against estimates and p-values, flow-diagram sums. Without
   runnable code, every printed specification is still checked against the governing
   documents.
6. **A calculation the review builds itself is unvalidated until checked.** An
   independent recomputation (a sample size by a second method, a recomputed
   percentage, a re-derived interval) records each input with its source location, the
   method, and the script and log. Where code ships, a variant is built as a copy of
   the shipped code in `work/pkg/` with only the changed lines different, and the diff
   is saved; re-deriving from scratch silently drops the product's own rules. A repair
   made only to get the code to run (a package shim, a path) is logged; a repair that
   moves a number beyond the reproduction tolerance is a variant, never the product's
   result. Synthetic data the review generates is a calculation it built (rule 8).
7. **Status words mean what they say.** `COMPLETE` = every applicable check ran and its
   output was inspected. `INTERIM` = required work the review can still do is
   unfinished (name it), including a stage the harness cannot start in a fresh context
   and a question waiting on the operator. `BLOCKED` = nothing can be anchored (give
   the exact evidence). A check that the product's own materials make impossible (a
   planning value with no source, a source named only in a code comment or in a file
   that was not delivered, a saved result with no code that made it, an analysis the
   text names but never specifies) is *unverifiable as delivered*: a finding. A saved
   result that was not delivered but whose generating code is in the source is
   regenerated, not a finding. A check the review could not run because of its own
   limits (patient data not shared under the job's data mode, a cited source it could
   not obtain, an exact value its environment cannot reproduce, such as other package
   versions or parallel streams) is `unverified-here`: a limit on the review, never a
   finding against the product.
   Status rolls up: one `INTERIM` check makes its stage `INTERIM`, and one `INTERIM`
   stage report or ledger row makes the run `INTERIM`.
8. **A check counted for or against the product must be able to count.** Before a
   check counts against a statement, or for it (a recomputation that "agrees", a
   sensitivity analysis the result "survives", a power the design "achieves"), record
   beside it:
   - **What it could detect.** A recomputation that reuses the product's own wrong
     input reproduces the error; a second method must take its inputs from the
     sources, not from the product's code. A null, the product's or the review's, is
     informative only for the range its interval excludes; an interval that contains
     both zero and the planning effect is uninformative, written as what the data
     cannot say, with the numbers.
   - **The specification the design requires.** A test of a stratified trial without
     the strata, a cluster trial analysed per patient, or a sample size for a test the
     analysis will not use is the review's error, whatever it returns.
   - **What the product already did.** A check it ran, or a choice it states and
     justifies, is engaged on its terms: rebut the check or the justification, or show
     the alternative at least as defensible; never count it as an omission.
   - **What the data mode allows.** A run on synthetic data establishes how the code
     behaves; it never supports or contradicts a printed number.
9. **Inference at the level the design demands.** Clustered or centre-randomised
   designs account for the clustering; stratified randomisation puts the
   stratification factors in the analysis or says why not; repeated measures model
   the within-participant correlation; small samples use small-sample methods
   (Kenward–Roger or Satterthwaite degrees of freedom for mixed models, CR2 with
   Satterthwaite degrees of freedom for cluster-robust errors with few clusters, exact
   or permutation tests). A charge that inference is wrong is quantified: the
   re-estimated standard-error ratio where data allow, otherwise a design effect at a
   stated intra-cluster correlation, labelled as a sensitivity.
10. **Name the substance, never a bare locator or ID.** Write for a reader who does not
    hold the product's table of contents, the stage reports or this skill in memory.
    Name what is meant in words ("the dropout allowance (Statistical comparison
    framework, p. 3)"), never a bare section number, a review-internal section, or a
    bare row or finding ID ("ST04", "C2") as a noun. A locator or ID may follow in
    parentheses once the thing has been named. The rule binds prose (reports, the
    synthesis, messages); IDs in ledger cells, `bears on:` lines and `sources:` fields
    are fine.
11. **Data protection comes first.** Open only what `00_ASSIGNMENT.md` clears.
    Patient-level data is never opened, printed, copied or quoted unless the data mode
    is `shared`; even then, review artifacts carry aggregates only: no row-level
    values, no identifiers, no cell below 5 that the delivered document does not
    already print. A data file the assignment does not clear stops the run before
    anything reads it: record its name and size only, and ask the operator (unattended:
    write `BLOCKED — UNCLEARED DATA: <path>` in `00_INTAKE.md` and end). Web searches use
    general terms (condition, intervention, endpoint), never internal IDs, unpublished
    results or data. `references/data-access.md` has the full rules.
12. **The reader is a colleague.** A finding is about the product: what is wrong, the
    evidence, what it changes, and a concrete fix. No motive, no blame, no taste: a
    preference that no guideline, DKF convention or stated requirement backs is not a
    finding. Typos matter only where they change a number, a definition or a reader's
    understanding.

## Before the run

These rules travel with the skill: they bind wherever it runs. The coordinating session
applies them once, before any stage agent starts; stage agents never ask the user and
write what they need under "Requests for the operator" in `00_INTAKE.md`.

- **Where the job lives.** Beside the product, in the product's own repository
  (`review/<yyyy-mm-dd>_<depth>/`), committed there under the `.gitignore` that
  `new_job.py` writes: the review, its evidence and its outputs, never copies of the
  product or its documents, literature or data. Never in the repository that holds
  these skills. In data mode `shared`, activate that `.gitignore`'s shared-mode block
  before intake (gate I2).
- **Clearance first.** Run the clearance scan before opening any file in the job
  (Intake, step 1). Never open, print or summarise a file the data mode does not
  clear, not even to check whether it is real data.
- **Confirm once.** Tell the user the depth and data mode the assignment sets, the size
  class the scan prints and what the run needs (on a short SSE, depth `quick` took
  about half an hour of model time and `standard` about one 5-hour usage window), and
  wait for the go-ahead. Ask them to check their usage (`/usage`); suggest waiting or
  `quick` when the weekly window is above about 70%. Never start a second review while
  one runs on the same account.
- **Billing.** Check whether `ANTHROPIC_API_KEY` is set without printing it
  (`[ -n "${ANTHROPIC_API_KEY:-}" ] && echo set`); if it is, tell the user the run may
  be billed to that key rather than their subscription (`/status` shows which).

## Intake

The operator prepares the job folder (`python3 <dkf-review skill>/scripts/new_job.py
<job>` creates it, with its `.gitignore`) and fills in `00_ASSIGNMENT.md` from
`assets/ASSIGNMENT-template.md`: the product and its type, the questions for the
reviewer, the documents it depends on, what has been cleared for sending to the model
provider, the data mode and the depth.

1. **Clearance first.** Run `python3 <dkf-review skill>/scripts/scan_job.py --root
   <job>` before opening anything. It inventories the job (names, sizes, hashes; it
   never opens a data file), checks the assignment's clearance fields, flags every
   data-like file the data mode does not clear, reads the YAML of the Quarto source
   (title, params, including the `dkfreporting` product fields) and the metadata of
   each PDF (creation date, and the R and package versions the DKF template writes
   into the Keywords field), and writes `review/intake-scan.json`. A non-zero exit is
   a clearance failure: stop and ask (unattended: `BLOCKED`, rule 11).
2. **Layout.** The job root holds:

   ```
   00_ASSIGNMENT.md           written by the operator
   01_product/                the product as delivered: rendered document(s) and the Quarto
                              source tree with every file the render reads; never edited
   02_governing/              protocol, SAP, SSE, registry entry, CRF or data dictionary,
                              each named <kind>_<version>_<yyyy-mm-dd>.<ext>
   03_previous/               earlier versions of the product, named <rev or date>_<file>
   04_data/                   patient-level data; only in data mode `shared`; never edited
   05_synthetic/              codebook or dummy data supplied by the statistician; only in
                              data mode `synthetic`
   lit/                       sources the product cites, <Author>_<Year>_<ShortTitle>.pdf
   ```

   Move files the operator dropped at the root into this layout; never rename files
   inside `01_product/` (the source refers to them by path).
3. **Records, before any stage work.** Write `PROGRESS.md`, `AGENTS.md` and
   `00_INTAKE.md` from `assets/PROGRESS-template.md`, `assets/AGENTS-template.md` and
   `assets/INTAKE-template.md` now, from the assignment and the scan: settings, the
   questions verbatim numbered `Q1, Q2, …`, the inventory, the DKF product fields and
   the render environment where the scan found them, and `Suite version: <x>` copied
   from this skill's `metadata.version` (so a later audit knows what the run was asked
   to do). Document identities (title, version, date) are filled in as the documents
   are read; a field not yet known says so. `check_job.py --stage intake` must pass
   before the document stage starts; every later gate re-checks it.
4. **Extracts.** Dump the product, the governing documents and every `lit/` work the
   review quotes with `pdftotext -layout` into `review/extracts/`; later quote checks
   read only these.
5. **Required.** The rendered product, or its source where no render exists. Missing
   both stops the run. A governing document the product relies on ("as specified in
   the protocol") and that is not in the job is requested once under "Requests for
   the operator" in `00_INTAKE.md`; unattended, or when the assignment says it is not
   provided, every check resting on it is `unverified-here` and the stage can still
   be `COMPLETE`.

**The operator and stage agents.** Only the coordinating session talks to the
operator, and it confirms the run (depth, data mode, expected cost) before dispatching
any stage. A stage agent that needs something from the operator writes the request
under "Requests for the operator" in `00_INTAKE.md`, continues by rule, and names the
request in its report; the coordinator relays it.

## Job tree

```
<job>/
├── 00_ASSIGNMENT.md · 00_INTAKE.md · AGENTS.md · PROGRESS.md · .gitignore
│                  packet folders (above)
├── CONSISTENCY_REVIEW.md/.html/.org · ISSUES*.md · REVIEWER.md
│                  DISPOSITIONS.md (all written by dkf-consistency-review)
├── review/        document-REPORT.md · code-and-data-REPORT.md · statements-REPORT.md ·
│   │              challenge-REPORT.md · intake-scan.json
│   └── extracts/  pdftotext dumps of the packet and of every quoted source
├── analysis/
│   ├── document/       consistency-matrix.csv · arithmetic-checks.csv ·
│   │                   sensitivity-claims.csv · sap-adherence.csv (reports and manuscripts) ·
│   │                   drift-table.md (when earlier versions exist)
│   ├── code-and-data/  spec-map.csv · feasibility-matrix.csv · construction-ledger.md ·
│   │                   battery-manifest.csv · results.csv · data-findings.csv (shared) ·
│   │                   assumption-ledger.csv (SSE) · module-walk.md · <module>-REPORT.md
│   └── statements/     statement-ledger.csv · questions.csv · driver-matrix.csv
├── work/          pkg/ (working copy of 01_product) · synthetic/ · scripts/ · logs/ ·
│                  results/ · challenge/ · annotated/ · digest/ · followup/
└── SYNTHESIS.md   the verdict stage's deliverable
```

`01_product/`, `02_governing/` and `04_data/` stay untouched; runs and repairs happen
in `work/pkg/` with every diff saved. All computation lives under `work/`, never
`/tmp`.

## Data modes

Set in `00_ASSIGNMENT.md`; `references/data-access.md` has the rules and the wording for
each limit.

| Mode | The review may read | What runs can establish |
|---|---|---|
| `none` (default) | documents and code | everything that needs no patient data: sample size and simulation code, arithmetic on printed numbers, code read against text |
| `synthetic` | + dummy data, built by `dkf-synthetic-data` from the code's data contract, or supplied by the statistician in `05_synthetic/` | that the code runs, that the data flow and the models are the ones the text describes, that the estimators recover known effects; never a printed number |
| `shared` | + patient-level data in `04_data/`, cleared for this use (the clearance is recorded in the assignment) | reproduction of the printed numbers and a data audit |

A printed number that depends on data the mode does not allow is recorded
`unverified-here — data not shared`, once per result family, and the arithmetic and
consistency checks of rule 5 still run on it.

## Depth

| Depth | Agents | What runs | Typical use |
|---|---|---|---|
| `quick` | two, then the form's verify pass | a **review agent** runs document, code-and-data (the profile's core modules worked through in the same agent) and statements, each with its report and gate; a fresh **verdict agent** writes `SYNTHESIS.md` and compiles the consistency review. No challenge stage, which the synthesis states in its status | a short product (an SSE, a protocol statistics section); a re-review of a revised product |
| `standard` (default) | one per stage, then the form's compile and verify | all five stages and every module whose condition holds: worked through in the code-and-data agent for a short product, as their own agents one at a time for a long one | a first review |
| `full` | standard, then `dkf-review-audit` | standard, and the audit before the consistency review | high-risk products: confirmatory reports, high DKF risk, strong influence on the protocol |

## Proportion

A review is read by a colleague in the time a review takes. Its size follows the
product's, by size class: **short** is at most 10 rendered pages (the intake scan's
page count of the PDFs in `01_product/`), **long** is anything larger or of unknown
size (`scripts/jobfiles.py`, `size_class`).

| Words, at most about | Short | Long |
|---|---|---|
| Stage report (document, code-and-data, statements) | 1,500 | 4,000 |
| Module report | 600 | 2,000 |
| Challenge report | 1,500 | 4,000 |
| `SYNTHESIS.md` | 3,000 | 8,000 |
| The form's general comments, issues and answers | 1,000 | 3,000 |

The gates fail a text above 1.25 times its limit. Cut repetition and narrative, never
a check, a number or an evidence path; detail that does not fit stays in the work files
the text points to. For a short product the statement ledger keeps at most 15 rows.

## Stages

Run in order. Each stage is its own job: open its `SKILL.md` and produce its report and
artifacts. Applicability is decided per result family or calculation
(`NOT_APPLICABLE` with a reason), never for the product as a whole.

1. **`document/`**, no code: identity and versions of every document, consistency of
   the product with its governing documents and earlier versions (and, for a report,
   adherence to the SAP), printed consistency and arithmetic, and the design, estimand
   and method critique.
2. **`code-and-data/`**: the code read against the text (the specification map and the
   Quarto/R mechanics), the code run under the job's data mode, the data or
   data-contract audit, the assumption and fragility battery, and the diagnostic
   modules the design calls for.
3. **`statements/`**: the statement ledger (for each load-bearing statement: how
   central it is, whether it holds, what survives, what is not established, the
   strongest defence) and draft answers to the assignment questions. Provisional
   until the verdict.
4. **`challenge/`**, required before a verdict at depths `standard` and `full`: a fresh
   agent on the verdict model, never the context that wrote the stage reports, gets
   `challenge/SKILL.md`, the packet and the evidence under test (every ledger row and
   draft answer verbatim, every finding, every calculation the review built, with
   evidence paths in both directions). It rebuilds what it tests from the untouched
   product and the printed page and rules STANDS, STANDS WITH CHANGES, WRONG or ADD.
   Before a WRONG or STANDS WITH CHANGES ruling is relied on, a worker re-runs its
   load-bearing script and opens the page it cites.
5. **`verdict/`**: one fresh agent on the verdict model, given `verdict/SKILL.md` and
   the inputs it names, writes `SYNTHESIS.md`: the bottom line, the cross-cutting
   findings, the final statement ledger, the recomputation table, the answers to the
   assignment questions, the data and reproducibility status, the findings and the
   counts. It never sees the coordinator's reasoning. Nothing re-decides after it.

Then, at depth `full`, `dkf-review-audit`; then `dkf-consistency-review` compiles the
consistency review in the DKF form. At depth `quick` the first three stages run in one
review agent, each still ending with its report and gate, and the verdict agent
compiles the consistency review after its own gate passes.

## Stage reports

Each stage writes `review/<stage>-REPORT.md` from `assets/report-template.md` (the
challenge stage uses its own format). The report is the handoff to later stages:
findings, leads, and **scope assumptions**, the limits a stage relied on ("the
simulation was re-run at 500 instead of 2,000 replicates", "all data are
synthetic"). A later stage that overturns a scope assumption re-checks, or flags, every
conclusion that rested on it.

## Progress file

Runs die mid-stage: a laptop sleeps, a session ends, a spawn fails. `PROGRESS.md` at
the job root is how the next session tells finished work from abandoned work. Create
it at intake; update it after every stage and every fired module, and before any long
computation starts:

- **Done**: each finished stage or module, with the exact paths of what it wrote.
- **Running**: live computations: command, log path, start time.
- **Decisions**: calls made by rule while unattended, each pointing to the artifact
  that records it.
- **Tried and failed**: every approach abandoned (a package that would not install, a
  model that would not converge, a source that could not be obtained), with the exact
  error and why it was dropped. Do not repeat an approach listed here unless something
  relevant has changed, and say what.
- **Next**: the one concrete step that resumes the work.

On resumption, read `PROGRESS.md` first, then confirm every path under Done exists and
every process under Running is alive or finished. `PROGRESS.md` is plumbing: nothing
from it goes into `SYNTHESIS.md`.

## Running it

- Commands and the review's own scripts run from the job root; `<dkf-review skill>` is
  this skill's directory. `python3` means a Python 3.10+ interpreter with the packages
  the repository README lists; `Rscript` means the R installation the product was
  written for, or the closest available, with the difference recorded.
- The product's own code runs from its working copy `work/pkg/`. Use `quarto render`
  where Quarto is installed; otherwise extract the code with `knitr::purl()` and run it
  with `Rscript`, recording which. Where the operator renamed the product file and the
  source refers to its own file name (a `file-name` parameter, a render helper), the
  working copy may restore the original name; log it as a repair. A product that pins packages with `groundhog` or `renv` is first run as
  delivered; where the pinned versions cannot be installed (no network, no CRAN
  access), shim the loader to the installed versions, log the shim and the version
  differences against the render environment read at intake, and record it as a scope
  assumption.
- Dispatch the agents Depth names: at `quick` two, at `standard` and `full` one per
  stage, and for a long product one per fired module, one at a time. Where the harness
  has no subagents, run them as serial passes. Check what exists before spawning: a
  module dropped because a spawn failed is a silent gap.
- **Usage.** A run on a subscription stops at the account's usage limits and resumes
  from `PROGRESS.md`. Never start two reviews at once on one account; record each wait
  under Running in `PROGRESS.md`.
- One continuous run. The sanctioned pauses are a clearance failure and a missing
  product. Unattended, resolve every other question by rule: record the call and the
  reason in the artifact it touches, and continue.
- **Analytic first.** Where an exact or closed-form calculation answers the question,
  compute it, and simulate only to confirm at the points that decide (a Monte Carlo
  standard error of at most 1 point at 80% power needs about 1,600 trials); never
  re-run a whole grid at high replicate counts.
- Size long computations to the machine (fewer Monte Carlo replicates for a code-path
  check, the full count only where a number is compared), launch them in the
  background with start and end markers in the log, and check for live processes
  before assigning any status. A synthesis written over live computation is
  `INTERIM`.
- Worked examples: `references/worked-cases.md`. R defaults that silently change a
  statistic: `references/r-traps.md`. Method notes: `references/methods/` and
  `references/clinical-guidelines.md`.

## Agents and cost

What a run costs is set by how long each agent lives, not by how much it writes:
every step re-reads the agent's whole context, so one long agent costs several times
what the same work costs split across short ones. None of this rations checking:
every check the stages require still runs.

"The operator's routing" is whatever the operator or the harness sets for which model
handles which kind of task; where nothing is set, every agent uses the session's model.

- **Route by kind of task.** *Mechanical* tasks (filing sources, dumping and reading
  printed pages, re-running scripts and diffing logs, building coverage and
  bookkeeping artifacts, generating synthetic data from a fixed contract) go to the
  model the routing assigns to mechanical work. *Judgement* tasks (every stage and
  module report, the statement ledger, the challenge and the verdict) go to the model
  it assigns to verdicts. A mechanical worker reports what it found (match or
  mismatch, the number, the file); it does not rate a statement.
- **Brief each agent for one bounded job** (a stage, a module, a group of result
  families) with a tool-call budget: for a short product about 50 for a stage agent
  and about 120 for the `quick` review agent; for a long product about 80 for a stage
  agent. An agent past 1.25 times its budget with work left writes its findings to
  their files and its state to `PROGRESS.md`, and stops; a fresh agent resumes from
  `PROGRESS.md`.
- **The coordinator stays thin.** The agent that dispatches stages and modules reads
  gate outputs and each report's `## Status`, never a stage's logs, scripts or page
  dumps. It never re-runs a stage's scripts and never re-decides a ruling: a doubt goes
  to a fresh worker with the script's path. Briefs name paths; they never paste files.
- **A subagent the harness bars from writing files** returns its report text in full;
  the coordinator saves it unchanged at the report's path.
- **Never hold a large context across a wait.** Size each computation to finish in
  under about four minutes; run anything longer in the background and work on
  something else, or record it under Running in `PROGRESS.md` and stop.
- **Read results, not dumps.** Inspect logs with `tail` and `grep`, tables by the rows
  and columns needed, long files by section; send bulky output to a file.
- **Text first, then the page.** Locate quotes and numbers in `review/extracts/`
  first; where a rule requires the page, render only that page
  (`pdftoppm -f N -l N -r 150`), cropped to the table or paragraph.
- **Figures are print.** A value read off a figure (a curve's crossing, an annotated
  point, an axis) is read from the PDF's vector graphics where possible
  (`pdftocairo -svg -f N -l N`, parsed by a script that maps path coordinates to the
  axes) and otherwise from the rendered page; either way the script and log are saved,
  and the read is recorded as approximate with its precision.
