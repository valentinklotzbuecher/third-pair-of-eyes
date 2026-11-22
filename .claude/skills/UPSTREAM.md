# Upstream: research_skills

The skills in this folder are a derivative of **research_skills** by The Catalogue of
Errors Ltd ([isitcredible.com](https://isitcredible.com)), released under the MIT
licence (`LICENSE-research_skills`, which must stay beside the derived files).

- Upstream: https://github.com/isitcredible/research_skills
- Fork used: https://github.com/valentinklotzbuecher/research_skills_
- Derived from: version **0.9.1**, commit `766f28f1f18de5af7707e10915798d75bd31f41e`
  (2026-10-27)

Upstream reviews published economics papers with replication packages. This suite
keeps its architecture (staged review, fresh-context challenge, a single verdict,
mechanical audit, gated deliverable, progress file, agents-and-cost rules) and its
epistemic rules (the record, coverage as a list, traceable numbers, the burden on the
product, both-direction challenge), and replaces the domain: DKF statistical products
(SSE, protocol statistics sections, SAP, report, manuscript) in Quarto/R, clinical
diagnostic modules, data-protection rules with optional synthetic data, and the DKF
consistency-review form as the deliverable.

## Verbatim copies

Unchanged files; update them by copying the upstream version.

| Here | Upstream |
|---|---|
| `LICENSE-research_skills` | `LICENSE` |
| `stats-consistency-review/ai-sweep/` (whole folder) | `review-digest/ai-sweep/` |
| `stats-consistency-review/scripts/build_manifest.py`, `corpus_rules.py`, `style-questions.json` | `review-digest/scripts/` |
| `stats-consistency-review/scripts/tests/conftest.py`, `test_build_manifest.py`, `test_check_facts.py`, `test_check_style.py` | `review-digest/scripts/tests/` |
| `stats-review/references/anomaly-tests.md` | `review/references/anomaly-tests.md` |
| `stats-review/references/methods/*.md` (16 cribs; list in its `README.md`) | `review/references/methods/` |

## Adapted files

Rewritten for the clinical setting; compare with the upstream file when upstream
changes.

| Here | Upstream source |
|---|---|
| `stats-review/SKILL.md` | `review/SKILL.md` |
| `stats-review/document/SKILL.md` | `review/paper/SKILL.md` |
| `stats-review/code-and-data/SKILL.md` | `review/code-and-data/SKILL.md` |
| `stats-review/statements/SKILL.md` | `review/claims/SKILL.md` |
| `stats-review/challenge/SKILL.md` | `review/challenge/SKILL.md` |
| `stats-review/verdict/SKILL.md` | `review/verdict/SKILL.md` |
| `stats-review/modules/rct-diagnostics/` | `review/modules/experiment-diagnostics/` |
| `stats-review/modules/small-n-diagnostics/` | `review/modules/small-n-diagnostics/` |
| `stats-review/modules/sample-size-diagnostics/` (warrant grades) | `review/modules/whimsical-assumptions-diagnostics/` |
| `stats-review/modules/simulation-diagnostics/` | `review/modules/quantitative-model-diagnostics/`, `review/references/simulation-harness.md` |
| `stats-review/modules/observational-diagnostics/` (adjustment sets) | `review/modules/controls-samples-diagnostics/` |
| `stats-review/references/simulation-harness.md`, `construction-validity.md`, `source-protocol.md`, `literature-protocol.md` | same names in `review/references/` |
| `stats-review/references/statement-test-matrix.md` | `review/references/claim-test-matrix.md` |
| `stats-review/assets/report-template.md` and the ledger CSV templates | `review/assets/` |
| `stats-review/scripts/check_job.py` | `review/scripts/check_manifest.py` (concept) |
| `stats-review/scripts/check_suite_version.py` and its test | `review/scripts/check_suite_version.py` |
| `stats-review/spec-changes.csv` (format; rows restart at R001) | `review/spec-changes.csv` |
| `stats-review-audit/SKILL.md`, `references/audit-cases.md` | `audit-review/` |
| `stats-review-audit/scripts/check_spec_drift.py` and its test | `audit-review/scripts/check_spec_drift.py` |
| `stats-review-audit/scripts/check_coverage.py` | `audit-review/scripts/check_coverage.py` (concept) |
| `stats-consistency-review/SKILL.md` | `review-digest/SKILL.md` |
| `stats-consistency-review/scripts/check_facts.py`, `check_style.py` | `review-digest/scripts/` (DKF fields; failures-only rule limited to the issue list) |
| `stats-consistency-review/scripts/check_issue_coverage.py`, `render_review.py` | `review-digest/scripts/check_ledger_coverage.py`, `render_digest.py` (concepts) |

## New here

The clinical modules `estimand`, `missing-data`, `time-to-event`, `multiplicity`,
`regression-model`, `prediction-model` and `bayesian`; the references
`product-profiles.md`, `data-access.md`, `clinical-guidelines.md`, `estimands.md`,
`quarto-r-audit.md`, `r-traps.md`, `worked-cases.md`; the assignment, intake, agents and progress templates, the
consistency matrix, arithmetic checks, SAP adherence, specification map, assumption
ledger and questions templates, `recompute.R` and `inline_values.R`; `jobfiles.py`, `scan_job.py`,
`new_job.py` and the job `.gitignore` it writes (`assets/job-gitignore`); the whole
`stats-synthetic-data` skill; `issues.py`, `annotate_source.py` and
`check_dispositions.py`.

## Outside this folder

`../../chat-skills/stats-document-check/` condenses `stats-review/document/SKILL.md`
(adapted from upstream `review/paper/SKILL.md`) for Claude chat, with a Python port of
the document stage's helpers in `recompute.R` and unchanged copies of three references
(new here); it carries `LICENSE-research_skills`.

## Not carried over

The econometric modules (IV, difference-in-differences, RDD, shift-share, synthetic
control, panel, time series, cross-sectional, scale-sensitive, theory, quantitative
model, whimsical assumptions, controls and samples) except where adapted above; the
design matrix and software examples; 44 econometric method cribs;
`check_inference.py` (Stata bootstrap gate); `deposit_inventory.py` and
`prewhiten.R`; the fairness scanner gate (replaced by a manual collegial-register
pass); the evaluator digest renderer. For a product with an econometric design, the
code-and-data stage points to the upstream module of that design when the upstream
suite is installed beside this one.

## Following upstream

`../../tools/upstream_diff.sh <path to a research_skills clone>` lists what changed
upstream since the commit above in the files this suite derives from, with the
upstream changelog. Port what applies, bump the suite version in all four
`SKILL.md` files, add rows to `stats-review/spec-changes.csv` for changed requirements,
and update the commit recorded here.
