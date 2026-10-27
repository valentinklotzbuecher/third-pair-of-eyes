---
name: document
description: >-
  First review stage, no code: identity and versions of every document, consistency
  of the product with its governing documents and earlier versions (SAP adherence
  for a report), printed consistency and arithmetic, and the design, estimand and
  method critique.
---

# Document

Read the product as an argument before touching code. Four questions: is it the
document it says it is, and does it agree with the documents that govern it; do its
printed numbers agree with each other and with their own arithmetic; does the design
and analysis answer the question the product says it answers; and what must the code
stage check? No code runs in this stage except the arithmetic scripts of section 2.

## 1. Documents, versions and consistency

**Identity.** For every document in the packet record title, version or revision,
date and status (draft, interim, final) from its title page and footer, and the
registry identifiers it carries. A product whose title page, footer revision and
source revision disagree has a version problem; record it.

**Consistency matrix.** `analysis/document/consistency-matrix.csv`
(template `../assets/consistency-matrix.csv`), one row per design element that appears
in more than one document: `element | product | protocol | sap | sse | registry |
other | status | evidence`, each cell the value as printed with its location, and
`status` one of `consistent`, `differs`, `missing-in-product`, `missing-elsewhere`,
`not-applicable`. Walk at least these elements, as far as the product type covers
them (`../references/product-profiles.md`):

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
acknowledge it; which document is right is often not for the review to decide (the
fix is a clarification), but where the product's own code settles it, say so. A value
the same document states twice differently (an endpoint window of days 61–365 in one
section and 61–360 in another) is recorded here too, with both locations.

**Earlier versions.** Where `03_previous/` holds earlier versions, write
`analysis/document/drift-table.md`: for each number, assumption or specification that
moved between adjacent versions, before and after with locations, classified
**number moved** (with % change), **assumption changed**, **design changed**,
**specification changed** or **statement reframed** (a hedge dropped, a scope
widened). A change is a lead, not a fault: the question is whether the current version
is consistent and justified, and whether a moved assumption moved everything that
depends on it (an effect size revised while N stayed fixed, a dropout rate changed in
the text but not in the calculation).

**SAP adherence** (reports and manuscripts). `analysis/document/sap-adherence.csv`
(template `../assets/sap-adherence.csv`): every analysis the SAP pre-specifies, as
`performed as specified`, `performed with deviation` (disclosed or not), or `omitted`
(disclosed or not); then every analysis in the product the SAP does not pre-specify,
labelled `post hoc` (and whether the product labels it so). An undisclosed deviation
or omission on a primary or key secondary analysis is a finding; a disclosed,
justified deviation is engaged on its stated reason (rule 8).

**Registry.** Where a registry entry is in the packet, compare primary outcome, time
frame, sample size and key secondary outcomes with the product. An undisclosed
difference in the primary outcome or its time frame is a finding.

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
  numbers it depends on, and log each in `analysis/document/arithmetic-checks.csv`
  (template `../assets/arithmetic-checks.csv`): `id | location | quantity | printed |
  inputs (with locations) | recomputed | method | script | result | note`, `result`
  one of `match`, `rounding` (agrees to the printed precision), `mismatch`. Typical
  checks, with functions in `../assets/recompute.R`: percentages from counts; sums and
  totals; an inflation for dropout (N / (1 − d) is the usual convention; N × (1 + d)
  under-inflates and is a finding unless stated); rounding up to an even number or a
  multiple of the block size; risk and mean differences, ratios and their intervals
  (an interval for a ratio is symmetric on the log scale); a p-value against its
  interval (Altman and Bland's method, `p_from_ci()`); an expected mean score or event
  rate from component values and weights. Every recomputation runs as a script under
  `work/scripts/` with a log; none is done in prose.
- **Statements of sensitivity and robustness.** Every sentence of the form "results
  are robust / similar / not sensitive to X", "the sample size is primarily driven by
  Y", "power remains above Z% under …" is a testable claim about a printed table or
  figure. Open the exhibit, check every scenario the sentence covers, and classify it
  in `analysis/document/sensitivity-claims.csv` (`claim | location | cited_exhibit |
  scenarios_covered | classification | evidence`) as `SUPPORTED`, `QUALIFIED`,
  `CONTRADICTED` or `UNRESOLVED`. A scan that finds none writes one row
  `NONE_FOUND` naming the search terms; a header-only file cannot be told from a
  skipped scan. A general statement backed by a check on a subset of scenarios is a
  lead for `code-and-data`.
- Figures: axis labels, units and captions name the plotted quantity; a reference
  line or annotated value matches the text.

This section appears in the report even when everything agrees; a later blocked stage
does not excuse skipping it.

## 3. Design, estimand and method

Follow the product's profile (`../references/product-profiles.md`) for what is core.

- **The question and the estimand.** Name the design (parallel-group, cluster,
  crossover, stepped-wedge, single-arm, observational cohort, prediction model,
  diagnostic accuracy) and the estimand the product targets, attribute by attribute
  (ICH E9(R1); `../references/estimands.md`). A primary analysis that estimates a
  different estimand from the one stated (a per-protocol set for a treatment-policy
  estimand, complete cases under a strategy that needs every randomised participant)
  is a finding, passed to `estimand-diagnostics`.
- **The calculation and the analysis agree.** A sample size computed for one test
  (log-rank, a proportions test, a t-test) and an analysis planned with another (a
  stratified Cox model, an adjusted linear model) is not by itself an error: adjusted
  analyses usually gain power. Record which is used where, whether the product says
  so, and whether the difference runs in the conservative direction; pass it to
  `sample-size-diagnostics`.
- **Logic gaps.** Post-randomisation exclusions; analysis sets defined by
  post-randomisation behaviour; an outcome measured differently by arm; a composite
  whose components could move in opposite directions or carry very different
  clinical weight; a time window that starts at a post-randomisation event (immortal
  time); conditions that bind differently across the compared groups.
- **Covariates.** Post-baseline covariates in a model of a randomised comparison;
  stratification factors left out of the analysis without a reason; prognostic
  covariates chosen after seeing the data; in observational comparisons, adjustment
  sets with mediators or colliders (`../references/methods/cinelli_forney_pearl_2024_bad_controls.md`).
- **Reporting guideline.** Read the product against the guideline its type calls for
  (SPIRIT for a protocol, the Gamble et al. SAP guideline, CONSORT and its extensions
  for a trial report, STROBE, TRIPOD+AI, STARD; `../references/clinical-guidelines.md`).
  An item that is missing becomes a finding only when a load-bearing statement depends
  on it or a reader could not implement or interpret the product without it; the
  checklist is a lead, not the review.
- **The assignment questions.** For each question in `00_INTAKE.md`, note what this
  stage found that bears on it and what the code stage must establish to answer it.

Structural and substantive problems only: no comments on wording, layout or code
style unless they change a number, a definition or what a reader will understand.

## Output

`review/document-REPORT.md` from `../assets/report-template.md`, with findings `D1, D2,
…` grouped under documents and versions, printed consistency and arithmetic, and design
and method (bold labels; finding blocks keep the template's `###` heads), most
important first within each, the gravest named in Status; the artifacts above; leads
for `code-and-data` (specifications to trace, numbers to recompute, sensitivity
scenarios to complete, covariates to check) and for `statements` (reframed or
unsupported statements, questions and what bears on them).
