---
name: code-and-data
description: >-
  Second review stage: read the Quarto/R code against the text (specification map,
  chunk mechanics, R defaults), run it under the job's data mode (no data, synthetic
  data or shared data), audit the data or the data contract, stress the product's
  assumptions and choices with the fragility battery, and dispatch the diagnostic
  modules the design calls for.
---

# Code and data

Find out whether the code does what the text says, whether it produces what the
document prints, and whether each result or calculation survives defensible
alternatives. A result that survives every valid check is reported as strong: the
battery is a test, not a fault-finder.

Ground rules:
- **No finding without a construction**: an executed script, a recomputation, a
  counterexample, or a code–text mismatch cited at `file:line` whose effect on the
  printed number has been run where the code runs. Never a verbal argument.
- **The anchor is the product's code, executed** in `work/pkg/`, every repair logged,
  failed repairs too (under "Tried and failed" in `PROGRESS.md`).
- **A blocked check needs proof**: the exact file, command, error and attempted
  repair, or the data mode that rules it out.
- **Verification is not reanalysis.** "The delivered code does not produce the printed
  number" is a narrow, high-confidence failure; "a different defensible choice gives a
  different answer" is a weaker disagreement. Keep them apart.
- **The data mode is a hard limit** (`../references/data-access.md`). Never read data
  the assignment does not clear; never print row-level values in a log or report.

## A. Code against text (before running anything)

1. **Extract the printed specifications** from the rendered product: for every
   calculation and analysis, the outcome and its derivation, the population and
   analysis set, the model or test, covariates, strata and random effects, the handling
   of missing values and intercurrent events, time points and windows, the effect
   measure and interval method, alpha and sidedness; for a sample size, the test,
   effect, planning values, power, allocation, dropout allowance and rounding rule.
2. **Trace the code**: what each chunk computes (by label, or by line range for an
   unlabelled chunk), where data are read, filtered, derived and modelled, and where
   every inline `r` expression in the prose comes from. `knitr::purl()` drops inline
   expressions: after a run, evaluate them in the run's session with
   `../assets/inline_values.R` and save `work/results/inline-values.csv` (line,
   expression, value), which the specification map compares with the print.
3. **Specification map**, `analysis/code-and-data/spec-map.csv` (template
   `../assets/spec-map.csv`), one row per printed specification element:
   `printed_ref | element | printed_value | code_ref (file:line) | code_value | status
   | discrepancy`, `status` one of `identical`, `differs`, `not-implemented`,
   `no-code` (a printed element no code produces). A number typed into the prose gets
   its own `no-code` row even when the element it describes is implemented elsewhere.
   A printed specification with no row has not been audited. For every
   `differs`, search the code for other places that implement the same element: a slip
   found once may recur.
4. **Quarto and R mechanics** (`../references/quarto-r-audit.md`): chunks with
   `eval: false` whose results the text cites; `error: true`; `warning: false` or
   `message: false` around model fits, where they hide convergence and singularity
   warnings; `cache: true` with dependencies the cache does not track; `include:
   false` chunks that compute reported numbers; numbers typed into prose that the code
   computes elsewhere; seeds (where `set.seed()` sits, parallel streams); package
   pinning (`groundhog` date or `renv.lock`) against the R and package versions the
   rendered PDF records; absolute paths; files the document reads but does not create
   (a saved simulation result, a lookup table) and whether the code that made them is in
   the job. A saved result with no generating code is *unverifiable as delivered*; one
   whose generating code is in the source (often an `eval: false` chunk) but which was
   not delivered is regenerated in section B.
5. **R defaults** (`../references/r-traps.md`): sweep the code for defaults that
   silently change the statistic (continuity corrections, Welch versus pooled
   variance, sequential sums of squares, ties handling, `NA` handling in `table()`,
   `filter()` and `mean()`, reference levels, time units in survival design functions,
   rounding). Each hit is a lead until its effect on a printed number is known.
6. **Feasibility matrix**, `analysis/code-and-data/feasibility-matrix.csv`: `exhibit |
   required inputs | input status | runs under data mode`, one row per exhibit, each
   input with its status (`input: status; input: status`), status one of `in job`,
   `created by the code`, `regenerated by the review`, `synthetic`, `not shared`,
   `missing`, `not needed`. Required before any "cannot be checked" statement; one
   genuine input falsifies the blanket.

## B. Run the code

Copy `01_product/` (which holds every non-patient file the source reads) to
`work/pkg/`; in data mode `shared`, the code reads patient data from `04_data/` through
a path set in the working copy, never by copying the data into `work/`. Run it
unmodified first, then repair only what stops it running (rule 6 of the skill), with
every repair logged and diffed. Where Quarto is installed, render; otherwise extract
the code with `knitr::purl(input, documentation = 0)` and run it with `Rscript`, and
record which. Run with a UTF-8 locale (`LC_ALL=C.UTF-8` or the product's own) and with
`options(warn = 1)` set through a profile (`R_PROFILE_USER`), so that warnings the
chunk options suppress are printed to the log; record both.

- **A saved result that was not delivered** but whose generating code is in the source
  (an `eval: false` chunk the document tells the reader to run) is regenerated by
  running that code as the product instructs, in the working copy, logged. This is
  part of running the product, not a variant; the comparison with the print follows
  the tolerance rule below.
- **A package that cannot be installed** (no network, no CRAN access) and has no
  installed substitute is replaced by a stand-in that the product's code calls
  unmodified (a local shim package or functions defined before the product's code
  runs). The stand-in is a calculation the review built (rule 6): write down what it
  must do from the package's documentation and the product's calls, validate it with
  a test, and record the runs that use it as `PROXY` in the manifest. Where no faithful
  stand-in can be built, run an independent implementation instead and label it so.

**Reproduction tolerance**, in every mode where a number is produced: exact match on
N, counts and degrees of freedom; relative difference below 1e-4 on estimates and
standard errors, or agreement to the printed rounding. Outside tolerance →
`NONREPRODUCED`, a finding with the difference and the repair log. Never widen the
tolerance or drop a cell to turn a mismatch into a match. A Monte Carlo number
reproduces exactly only with the same seed, R version, RNG kind and parallel stream
assignment; otherwise it is compared against its Monte Carlo error band (two numbers
differ when they are more than about 2·√2 MCSE apart, plus the printed rounding), and
a quantity chosen by a first crossing on a noisy grid (the smallest N reaching a power)
is judged through the fitted curve and pooled replicates
(`../modules/simulation-diagnostics/`), not by exact match. A run that agrees within
the band but cannot reproduce exactly because of the review's environment is `PROXY`,
and the exact value is `unverified-here`.

**Data mode `none`.** Run every chunk that needs no patient data: sample size
calculations, simulations, tables of planning values, anything computed from constants
or from files in the job. Long simulations run first at a reduced replicate count to
check the code path, then at the delivered count in the background where a printed
number is compared (`../modules/simulation-diagnostics/`). Chunks that read patient
data are recorded `DATA_NOT_SHARED` in the manifest, once per result family.

**Data mode `synthetic`.** Build the synthetic data with the `dkf-synthetic-data`
skill (or take the statistician's from `05_synthetic/`) into `work/synthetic/`:
the data contract, the generator, and three datasets: `base` (plausible values),
`edge` (boundary values, missing values, absent factor levels, duplicate or
out-of-window records, each with its expected effect on the analysis sets written in
advance) and `truth` (a known effect, and known missingness where the analysis claims
to handle it). Place each where the code reads its data, and run the code unmodified.
Check and record:
- the code runs end to end on `base` and on `edge`, or fails with a message a user
  would understand; a crash on a value the CRF allows is a finding;
- analysis-set counts on `edge` equal the counts expected by construction; derived
  variables equal a direct computation of the printed definition on the same data;
- the fitted models are the specified ones (formula, family and link, random effects,
  strata, weights, contrasts), read from the fitted objects, not from the code text;
- each table and figure pulls from the object the text says it does;
- on `truth`, over replicate datasets, the estimator recovers the planted effect
  within Monte Carlo error, and interval coverage is near nominal where the replicate
  count allows; the stated missing-data method behaves as stated.
Nothing in synthetic mode supports or contradicts a printed number.

**Data mode `shared`.** Reproduce the anchors natively: estimate, N, interval, p-value,
and the primary and key secondary tables, under the tolerance rule above.

**Reconcile code with print cell by cell** (any mode where a number is produced):
outcome, transform and units as the table claims; every subgroup and analysis set
rebuilt against all the columns it feeds; mismatch triage in order: rounding, reference
categories, variance estimator or interval method, which chunk produced the table. Do
not write "reproduces" before this comparison exists.

## C. Data audit

**Mode `shared`**, the lite pass, always:
- the analysis population against the randomisation list or enrolment log: arm as
  randomised versus arm as analysed, duplicates, participants missing from the
  analysis without a stated reason;
- impossible or implausible values (ages, dates in the wrong order such as treatment
  before randomisation, visits outside their windows), units, coding of missing values
  (`-99`, `999`), and digit preference in measured values (`../references/anomaly-tests.md`);
- derived variables recomputed from their components; aggregates recomputed from
  subgroup cells.
Escalate (full source checks, influence of outlying participants, missingness
patterns) when a load-bearing variable is derived or imputed, an anomaly survives, or
missingness is material. Findings go to `analysis/code-and-data/data-findings.csv`
(template `../assets/data-findings.csv`, written only in this mode) on the evidence
ladder below. Review artifacts
carry aggregates only (rule 11).

**Modes `none` and `synthetic`**, the data-contract audit: the variables the code reads
against the CRF or data dictionary (where supplied) and the definitions in the SAP or
product: names, types, units, codes and levels, missing-value codes, date formats,
visit structure. It is recorded in the specification map and the report. A derived
variable whose code does not implement its printed definition is a finding in any
mode. A product that reads no patient data (most SSEs) records the audit as not
applicable, with that reason.

**Evidence ladder**: (1) documentation gap → (2) verified error → (3) undisclosed
discretion → (4) misrepresentation → (5) fabrication. Never use a higher rung's language
on a lower rung's evidence; rule out innocent explanations (wrong version, wrong file,
the review's own bug) first. In an internal review rungs 4 and 5 need documentary
evidence and are escalated to the operator, never written into a report on inference.

## D. Assumptions and fragility

**Construction ledger**, `analysis/code-and-data/construction-ledger.md`: every
analytic choice the result depends on (derivations, exclusions with counts against the
stated N, windows, imputation, transformations, rounding, simulation settings with
seeds) and every discretionary choice not forced by the design or the governing
documents. A choice the text justifies stays on the ledger with the justification
beside it: the question is whether the alternative is as defensible, not whether a
reason was given. A shared object lists its users on a `consumers: F1, F2` line.

**Planning values** (SSE and protocol products): the stage enters every input of a
sample size calculation in `analysis/code-and-data/assumption-ledger.csv` (id,
assumption, value, location, the source cited); `sample-size-diagnostics` completes
the source check, the warrant grade and the effect on N, so the stage leaves those
cells empty for it. Conventions (alpha, power, sidedness, allocation, rounding rule)
are design choices and go to the construction ledger.

**Manifest**, `analysis/code-and-data/battery-manifest.csv` (template
`../assets/battery-manifest.csv`), one row per check, an unrunnable check a row too:
`id | family | hypothesis | spec | data_mode | artifact | seed | state | validity |
row_role | notes`.
- `state`: `done` (executed and inspected) · `NONREPRODUCED` · `PROXY` (name the
  substitute and its limits) · `BLOCKED` · `DATA_NOT_SHARED` · `NOT_RUN` ·
  `NOT_APPLICABLE`.
- `validity`: `clean` · `unvalidated` (a review-built calculation awaiting its patch or
  input record) · `invalid` (degenerate, wrongly specified, or unable to detect what it
  tests; say which).
- `row_role`: `verdict-bearing`; `rebuttal` (a re-run of the product's own number:
  stability of that number, not an independent test); or `harness` (a check on the
  review's own machinery: a stand-in's validation, a generator gate, whether the
  product runs as delivered).
- A run that stops is `BLOCKED` with its error. A check that yields no number still
  gets a results row, with the outcome in `notes` and `estimate` empty.
- `data_mode`: `none`, `synthetic` or `shared`, the mode the check ran under.

**Results**, `analysis/code-and-data/results.csv` (schema `../assets/results.csv`):
every check that produced a number, with the printed value beside it where one exists.

**The checks.** Where a module fires for a result family, checks 2 to 4 for that
family are the module's; the stage runs them only for families no module covers, and
otherwise only as far as reconciling the run with the print needs.
1. **Finish the product's own sensitivity analyses**: a scenario the text claims but
   the table covers only in part is extended by editing the product's code.
2. **Recompute independently** what the product's statements rest on: a sample size by
   a second method, a simulated power by an independent simulation or closed form, an
   expected rate from its components (`sample-size-diagnostics`,
   `simulation-diagnostics`).
3. **Inference** at the level of randomisation and clustering, small-sample methods
   where units are few, multiplicity per family of claims, a direct test of a
   difference wherever the text contrasts "significant in A, not in B"
   (`../references/methods/gelman_stern_2006_difference_test.md`).
4. **Choices the product avoided**: the defensible alternatives it did not try (a
   stratified analysis, the prespecified covariates, a different handling of
   intercurrent events, a less optimistic planning value within the cited range), run
   where the mode allows, and named as untested where it does not.
5. **Modules**: for every result family and calculation, walk the table below and fire
   every module whose condition holds; record the walk in
   `analysis/code-and-data/module-walk.md` as a table `| Module | Decision | Condition
   and evidence |`, one row per module, the decision exactly `fired`, `not applicable`
   or (depth `quick` only) `not run — depth quick`; the gate reads that column. Each
   fired module runs as its own job from its `SKILL.md` and writes
   `analysis/code-and-data/<module>-REPORT.md`; a module ruled not applicable writes a
   stub whose marker line is `Status: NOT_APPLICABLE — <the failed condition>`. At
   depth `quick`, only the core modules of the product's profile fire, and the walk
   records the others as `NOT_RUN — depth quick`.

   | Feature of any result family or calculation | Module (`../modules/`) |
   |---|---|
   | A sample size, a power calculation, or a statement about power or detectable effects | `sample-size-diagnostics` |
   | A load-bearing number from Monte Carlo simulation (simulated power, operating characteristics, a simulated null) | `simulation-diagnostics` |
   | A primary or key secondary estimand, intercurrent events, a treatment-policy, hypothetical, composite, while-on-treatment or principal-stratum strategy (a light pass for an SSE) | `estimand-diagnostics` |
   | Randomised allocation | `rct-diagnostics` |
   | Missing outcomes, dropout, imputation, or an analysis set that removes randomised participants (a light pass for an SSE's dropout allowance) | `missing-data-diagnostics` |
   | A time-to-event endpoint, censoring, competing events or follow-up | `time-to-event-diagnostics` |
   | Several primary endpoints, arms or time points, interim analyses, claims on secondary endpoints, or subgroup claims | `multiplicity-diagnostics` |
   | A load-bearing estimate from a regression model (linear, generalised linear, mixed or MMRM, GEE, ordinal, count, ANCOVA), or such a model as the planned primary analysis of a protocol or SAP | `regression-model-diagnostics` |
   | A non-randomised comparison of treatments or exposures | `observational-diagnostics` |
   | Development or validation of a prediction or prognostic model; diagnostic accuracy | `prediction-model-diagnostics` |
   | A Bayesian analysis or design | `bayesian-diagnostics` |
   | Fewer than about 50 evaluable participants per arm or 40 clusters at the planned or achieved size; a pilot or feasibility study; a load-bearing null | `small-n-diagnostics` |
   | Difference-in-differences, regression discontinuity, instrumental variables, interrupted time series, synthetic control | the upstream `research_skills` module for the design if installed beside this suite; otherwise `NOT_RUN` with that reason |

   **Fired modules.** For a short product (Proportion in `../SKILL.md`) the stage agent
   works through each fired module itself after the walk, writing each module's report
   at `analysis/code-and-data/<module>-REPORT.md` (at most about 600 words). For a long
   product the fired modules run as their own agents, one at a time, after A–D and the
   walk; the stage agent resumes to fold them in, finish its report and run the gate.
   Each module, in either form, writes its own report, puts its leads under that report's
   `## Leads for later stages`, keeps scripts and logs in `work/scripts/` and
   `work/logs/` with names prefixed by the module, and appends its rows to
   `results.csv` and `battery-manifest.csv` under a file lock
   (`flock analysis/code-and-data/.ledger.lock -c '<append command>'`), in the stage's
   column order, with IDs prefixed by the module's report prefix. The shared ledgers
   are `results.csv`, `battery-manifest.csv`, `spec-map.csv`, `assumption-ledger.csv`
   and `construction-ledger.md`. Once modules have appended, no builder regenerates a
   shared ledger from scratch.

   Simulation and resampling loops follow `../references/simulation-harness.md`.
6. **Account for survival**: name each surviving check's role beside the statement it
   bears on; a re-run of the product's own number is stability, not corroboration; a
   margin with no valid test is recorded as untested.

**Gate.** `python3 <dkf-review skill>/scripts/check_job.py --root <job> --stage
code-and-data` must pass before `COMPLETE`. Run it once the fired modules have
reported; before that, failures for missing module reports are expected and the stage
is `INTERIM`.

## Output

`review/code-and-data-REPORT.md` from `../assets/report-template.md`, findings `C1, C2,
…`, with sections for code against text (including Quarto mechanics and R defaults),
execution (what ran, under which data mode, what reproduced and what did not), data
or data-contract audit, and the battery; every artifact above; the module reports.
Each unresolved item says whether it is feasible and whether a statement depends on
it; a feasible item a statement depends on is either run or explicitly waived by the
operator. Leads for `statements`: what survives, under what, and which margins are
untested or unverifiable here.

`COMPLETE` = every family anchored or recorded `DATA_NOT_SHARED`, every artifact built,
applicable checks done with inspected output, the gate passing. `INTERIM` = a required
check or artifact missing (name it). `BLOCKED` = nothing anchorable, with the exact
evidence; the printed tables are still read.
