---
name: dkf-document-check
description: Document check of a statistical product (a sample size estimation, the statistics sections of a protocol, a statistical analysis plan, a statistical report or a results manuscript) before a second statistician reviews it. Checks identity and versions, consistency with the governing documents, the printed numbers and their arithmetic, and the design, estimand and method; recomputes printed numbers with scripts; returns findings, tables and a check log. Does not run the product's code. Use when asked to check, review or consistency-review such a document in a chat.
metadata:
  version: "0.1.1"
  based-on: "stats_review dkf-review document stage, suite 0.3.1 (stage text unchanged since 0.1.0)"
---

# Document check

The first stage of the DKF consistency review, on its own, for a chat. Read the product
as an argument before touching code, with four questions: is it the document it says it
is, and does it agree with the documents that govern it; do its printed numbers agree
with each other and with their own arithmetic; does the design and analysis answer the
question the product says it answers; and what must a review of the code check? The
result is a draft for the second statistician, who owns the review.

## Rules

- **Data.** Work only on documents the user has cleared for this chat. Never open
  patient-level data: an attached data file stays unopened, and the report says so.
- **The print decides.** Findings rest on the rendered product. The Quarto or R source
  may be read for the revision line and to see where a printed number comes from; what
  only the source shows (a hidden setting, a replicate count, a code comment) is a lead
  for the code review, or is cited only as corroboration.
- **No product code runs.** Your own scripts run for every recomputation: import
  `scripts/recompute.py`, beside this file. Nothing is recomputed in prose. A question
  that needs the product's code to run is a lead, not a finding.
- **Missing documents.** A comparison that needs a document that is not attached is
  recorded as `not in chat`; the report names the document, and nothing is guessed
  about its content.
- **Substance only.** Structural and substantive problems; no comments on wording,
  layout or code style unless they change a number, a definition or what a reader will
  understand.
- **References.** `references/` holds unchanged copies of the full suite's product
  profiles, estimand reference and guideline map. Their mentions of other stages,
  modules, scripts and job files belong to the full suite and do not apply here.

## 1. Documents, versions and consistency

**Identity.** For every document received, record title, version or revision, date and
status (draft, interim, final) from its title page and footer, and the registry
identifiers it carries. A product whose title page, footer revision and source revision
disagree has a version problem; record it.

**Consistency table.** One row per design element, with the columns `element | product
| protocol | sap | sse | registry | other | status | evidence`: each cell the value as
printed with its location (`other` holds the user's questions, a second statement of
the element inside the product, or a document not named in the columns), and `status`
one of `consistent`, `differs`, `missing-in-product`, `missing-elsewhere`, `not in chat`
or `not-applicable`. With no governing document attached, the table still records each
element as the product states it (once or several times) and as the user's questions
state it. Walk at least these elements, as far as the product type covers them
(`references/product-profiles.md`):

- primary endpoint: definition, measurement, time frame or window, scoring;
- estimand attributes: population, treatment conditions, variable, intercurrent
  events and their strategies, population-level summary;
- eligibility; interventions and comparator; allocation ratio;
- randomisation: method, stratification factors, block sizes or minimisation; blinding;
- sample size: N randomised and evaluable, power, alpha and sidedness, target effect,
  planning values, dropout or non-evaluable allowance;
- primary analysis: model or test, covariates, analysis set, handling of missing data;
- interim analyses and stopping rules; multiplicity; key secondary endpoints;
  subgroups; safety analyses; follow-up and visit windows.

A value that differs between documents is a finding when the product does not
acknowledge it; which document is right is often not for the check to decide (the fix
is a clarification), but where the product's own code settles it, say so. A value the
same document states twice differently is recorded too, with both locations.

**Earlier versions**, where attached: a drift table of every number, assumption or
specification that moved between adjacent versions, before and after with locations,
classified **number moved** (with % change), **assumption changed**, **design changed**,
**specification changed** or **statement reframed** (a hedge dropped, a scope widened).
A change is a lead, not a fault: the question is whether the current version is
consistent and justified, and whether a moved assumption moved everything that depends
on it.

**SAP adherence** (reports and manuscripts, with the SAP attached): every analysis the
SAP pre-specifies, as `performed as specified`, `performed with deviation` (disclosed or
not) or `omitted` (disclosed or not); then every analysis the SAP does not pre-specify,
labelled `post hoc`, and whether the product labels it so. An undisclosed deviation or
omission on a primary or key secondary analysis is a finding; a disclosed, justified
deviation is engaged on its stated reason.

**Registry**, where attached: primary outcome, time frame, sample size and key secondary
outcomes against the product. An undisclosed difference in the primary outcome or its
time frame is a finding.

## 2. Printed consistency and arithmetic

Walk every summary, table, figure, caption and conclusion of the rendered product.

- A number stated in more than one place (summary, text, table, figure, caption) is the
  same everywhere, to the stated rounding. A planning value in a caption that differs
  from the one in the text and the code is a finding even when the plotted curve is
  right.
- Ns and denominators flow: randomised = analysed + excluded with reasons, per arm;
  every table's N matches its analysis set; a percentage's denominator is stated or
  recoverable.
- **Arithmetic checks.** Recompute every derivable printed number from the printed
  numbers it depends on, and log each in a check log with the columns `id | location |
  quantity | printed | inputs (with locations) | recomputed | method | result |
  tolerance | note`; `method` is the function call or formula; `result` is one of
  `match`, `rounding` (agrees to the printed precision), `within-band` (agrees within a
  stated band: Monte Carlo error, the precision of a figure read, an interval implied
  by rounded inputs; the band goes in `tolerance`) or `mismatch`; `note` says what the
  check could detect where that is not obvious. A mismatch explained by Monte Carlo
  error or by printed rounding is recorded with its explanation and is not raised as a
  finding. Typical checks, with functions in `scripts/recompute.py`: percentages from
  counts; sums and totals; an inflation for dropout (N / (1 − d) is the usual
  convention; N × (1 + d) under-inflates and is a finding unless stated); rounding up to
  an even number or a multiple of the block size; risk and mean differences, ratios and
  their intervals (an interval for a ratio is symmetric on the log scale); a p-value
  against its interval (Altman and Bland's method, `p_from_ci()`); an expected mean
  score or event rate from component values and weights. `agree()`, `agree_band()` and
  `agree_interval()` give the `result`.
- **Statements of sensitivity, robustness and adequacy.** Every sentence of the form
  "results are robust / similar / not sensitive to X", "the sample size is primarily
  driven by Y", "power remains above Z% under …", "a conservative approximation",
  "consistent with the feasibility estimate", "the most consequential uncertainty" is a
  testable claim about a printed table, figure or stated fact. Open the exhibit, check
  every scenario the sentence covers, and classify it in a table `claim | location |
  cited_exhibit | scenarios_covered | classification | evidence` as `SUPPORTED`,
  `QUALIFIED`, `CONTRADICTED` or `UNRESOLVED`. A scan that finds none says so and names
  its search terms. A general statement backed by a check on a subset of scenarios is a
  lead for the code review.
- **Figures.** Axis labels, units and captions name the plotted quantity; a reference
  line or annotated value matches the text. A plotted value is read with a script where
  the PDF allows it, otherwise by eye, with the precision of the reading as the band.

This section appears in the report even when everything agrees.

## 3. Design, estimand and method

Follow the product's profile (`references/product-profiles.md`) for what is core.

- **The question and the estimand.** Name the design (parallel-group, cluster,
  crossover, stepped-wedge, single-arm, observational cohort, prediction model,
  diagnostic accuracy) and the estimand the product targets, attribute by attribute
  (ICH E9(R1); `references/estimands.md`). A primary analysis that estimates a different
  estimand from the one stated (a per-protocol set for a treatment-policy estimand,
  complete cases under a strategy that needs every randomised participant) is a
  finding.
- **The calculation and the analysis agree.** A sample size computed for one test
  (log-rank, a proportions test, a t-test) and an analysis planned with another (a
  stratified Cox model, an adjusted linear model) is not by itself an error: adjusted
  analyses usually gain power. Record which is used where, whether the product says so,
  and whether the difference runs in the conservative direction.
- **Logic gaps.** Post-randomisation exclusions; analysis sets defined by
  post-randomisation behaviour; an outcome measured differently by arm; a composite
  whose components could move in opposite directions or carry very different clinical
  weight; a time window that starts at a post-randomisation event (immortal time);
  conditions that bind differently across the compared groups.
- **Covariates.** Post-baseline covariates in a model of a randomised comparison;
  stratification factors left out of the analysis without a reason; prognostic
  covariates chosen after seeing the data; in observational comparisons, adjustment
  sets with mediators or colliders.
- **Reporting guideline.** Read the product against the guideline its type calls for
  (SPIRIT for a protocol, the Gamble et al. SAP guideline, CONSORT and its extensions
  for a trial report, STROBE, TRIPOD+AI, STARD; `references/clinical-guidelines.md`). A
  missing item becomes a finding only when a load-bearing statement depends on it or a
  reader could not implement or interpret the product without it; the checklist is a
  lead, not the check.
- **The user's questions.** For each question the user asked, note what this check
  found that bears on it and what the code review must establish to answer it.

## Output

In the reply, in this order:

1. **Status.** What was received (the identity of each document), what is missing, and
   in one or two sentences what the check found and on what evidence.
2. **Findings** `D1, D2, …`, grouped under documents and versions, printed consistency
   and arithmetic, and design and method, most important first within each. Each
   finding gives: its title; where it is (page, section, table, and `file.qmd:line`
   where the source shows it); the statement it bears on; the evidence (check-log ids,
   printed locations); what is wrong, the printed value against what was found, and its
   effect on the primary quantity (an N, a power, an estimate) in its own units, with
   the direction (a defect that makes the product conservative is written as
   conservative); and `fix:` what would resolve it, concretely.
3. **Tables.** The consistency table, the check log and the sensitivity-statement table,
   each saved as a CSV file the user can download; the check log is also shown in the
   reply.
4. **Leads for the code review.** What only running the code can settle, each naming
   its source.
5. **Not covered.** The documents that were not attached, and every question that needs
   the product's code to run.

Plain register: every number with its source; no hedging beyond the evidence; no
narrative of the procedure.
