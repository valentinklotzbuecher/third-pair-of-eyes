# Product profiles

What each product type is reviewed against, which statements carry it, which checks
and modules are core (they run at every depth), and what is out of scope. The
assignment can narrow or widen the scope; record any change in `00_INTAKE.md`.

## Reading the DKF product fields

Quarto sources built on the DKF `dkfreporting` template carry product fields in their
YAML `params` (for example `product-type`, `internal-dkf-id`, `level-of-assumptions`,
`influence-on-protocol`, `multicentre`, `type-of-review`, `final-product-risk`,
`estimated-time-for-review`). `scan_job.py` reads them into `review/intake-scan.json`.
Record them in `00_INTAKE.md`, and use them as defaults the assignment can override:

| Field | Use in the review |
|---|---|
| `product-type` | the product type below (SSE → `sse`, SAP → `sap`, report types → `report`) |
| `level-of-assumptions: high` | every planning value gets a source check in `sample-size-diagnostics` and a sensitivity range |
| `influence-on-protocol: yes` | the consistency matrix against the protocol is core, whatever the type |
| `multicentre: yes` | centre handling in randomisation and analysis is core (`rct-diagnostics`) |
| `final-product-risk` (high) | suggests depth `full` |
| `type-of-review` | recorded; the review prepares that type of human review |

Fields left empty in the template are recorded as empty, not guessed.

## `sse`: sample size estimation

- **Record**: the rendered SSE (often "Statistical aspects of the study protocol") and
  its Quarto source, plus any saved simulation results it loads.
- **Governing documents**: the protocol or protocol draft (endpoint, design,
  allocation, analysis); the sources cited for planning values (`lit/`); earlier SSE
  versions.
- **Load-bearing statements**: the target N (evaluable and randomised); power, alpha
  and sidedness; the target effect and its rationale; every planning value; the
  analysis the calculation assumes; the dropout or non-evaluable allowance and the
  rounding; statements about sensitivity ("N is driven mainly by …"); feasibility.
- **Core checks**: independent recomputation by a second method; source and warrant of
  every planning value; test behind the calculation against the planned analysis;
  dropout formula and rounding; sensitivity statements against their tables; printed
  consistency (captions, summary and text agree); the code reproduces the printed
  numbers (no patient data are needed).
- **Core modules**: `sample-size-diagnostics`; `simulation-diagnostics` when the
  calculation simulates; `estimand-diagnostics` (light pass: the estimand the effect
  refers to and the intercurrent events the calculation ignores);
  `time-to-event-diagnostics` for event-driven designs; `small-n-diagnostics` when the
  target is below about 50 evaluable participants per arm or 40 clusters.
- **Out of scope**: the full analysis plan; the completeness of the protocol.

## `protocol`: statistics sections of a protocol

- **Record**: the protocol sections on outcomes, sample size, randomisation and
  blinding, statistical methods, interim analyses and data monitoring.
- **Governing documents**: the SSE, registry entry, earlier protocol versions; SPIRIT
  2025 for completeness.
- **Load-bearing statements**: the SSE statements, plus the primary endpoint
  definition, the estimand, randomisation and stratification, the primary analysis,
  missing-data handling, interim analyses and stopping rules, multiplicity.
- **Core modules**: `sample-size-diagnostics`, `estimand-diagnostics`,
  `rct-diagnostics`, and `multiplicity-diagnostics` or `missing-data-diagnostics` where
  the protocol makes claims they cover.
- **Out of scope**: non-statistical protocol sections, except where they define an
  endpoint, a population or a procedure the statistics depend on.

## `sap`: statistical analysis plan

- **Record**: the SAP, with its mock tables and any analysis code delivered with it
  (often programmed on dummy data before database lock).
- **Governing documents**: the protocol (the SAP may refine but not contradict it
  without saying so), the SSE, the registry entry, the CRF or data dictionary.
- **Load-bearing statements**: estimands and their attributes; analysis sets; the
  primary analysis (model, covariates, handling of intercurrent events and missing
  data); sensitivity and supplementary analyses; key secondary analyses; multiplicity;
  interim analyses; subgroups; safety analyses; derived-variable definitions.
- **Core checks**: completeness against the SAP guideline (Gamble et al. 2017) for the
  items the analyses depend on; consistency with the protocol and SSE; each
  specification unambiguous enough that two statisticians would implement it the same
  way; code (if delivered) against text, run on synthetic data where the data mode
  allows.
- **Core modules**: `estimand-diagnostics`, `rct-diagnostics` or
  `observational-diagnostics`, `missing-data-diagnostics`,
  `regression-model-diagnostics`, `multiplicity-diagnostics`, and the design-specific
  modules.
- **Out of scope**: results (there are none); a plan is judged as a plan.

## `report`: statistical analysis report

- **Record**: the rendered report (interim, final, DSMB) and its Quarto source.
- **Governing documents**: the SAP above all, then the protocol, SSE and registry
  entry; earlier report versions (an interim report, a previous data cut).
- **Load-bearing statements**: the primary result and its interpretation; key secondary
  results; sensitivity analyses cited as support; safety statements; conclusions and
  summary.
- **Core checks**: SAP adherence (every prespecified analysis performed, deviations
  disclosed, post hoc analyses labelled); participant flow; printed consistency and
  arithmetic in every table; code against text; execution under the data mode
  (patient data are usually not shared: then synthetic data for the code paths, and
  `unverified-here` for the printed numbers).
- **Core modules**: every module whose condition holds.
- **Out of scope**: the clinical interpretation beyond what the statistics support.

## `manuscript`: results manuscript

- **Record**: the manuscript as submitted or drafted, with its tables and supplement.
- **Governing documents**: the statistical report and the SAP (the manuscript's
  numbers should be the report's), the protocol, the registry entry, the reporting
  guideline for the design (CONSORT 2025 and extensions, STROBE, TRIPOD+AI, STARD).
- **Load-bearing statements**: the abstract and the conclusions, sentence by sentence;
  the primary result; any causal, generalising or practice-changing language.
- **Core checks**: every number against the report; spin (a non-significant primary
  outcome reported as positive via secondary results or subgroups); the reporting
  guideline items the claims rest on.
- **Core modules**: as for a report, emphasising `multiplicity-diagnostics` and
  `small-n-diagnostics` for claims beyond the primary outcome.

## `other`

Randomisation-list specifications, DSMB reports, data-management checks, feasibility
analyses. The assignment states the load-bearing statements and the governing
documents; the review follows the closest profile above and records the choice.
