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
| `dkf-consistency-review/ai-sweep/` (whole folder) | `review-digest/ai-sweep/` |
| `dkf-consistency-review/scripts/build_manifest.py`, `corpus_rules.py`, `style-questions.json` | `review-digest/scripts/` |
| `dkf-consistency-review/scripts/tests/conftest.py`, `test_build_manifest.py`, `test_check_facts.py`, `test_check_style.py` | `review-digest/scripts/tests/` |
| `dkf-review/references/anomaly-tests.md` | `review/references/anomaly-tests.md` |
| `dkf-review/references/methods/*.md` (16 cribs; list in its `README.md`) | `review/references/methods/` |

## Adapted files

Rewritten for the clinical setting; compare with the upstream file when upstream
changes.

| Here | Upstream source |
|---|---|
| `dkf-review/SKILL.md` | `review/SKILL.md` |
| `dkf-review/document/SKILL.md` | `review/paper/SKILL.md` |
| `dkf-review/code-and-data/SKILL.md` | `review/code-and-data/SKILL.md` |
| `dkf-review/statements/SKILL.md` | `review/claims/SKILL.md` |
| `dkf-review/challenge/SKILL.md` | `review/challenge/SKILL.md` |
| `dkf-review/verdict/SKILL.md` | `review/verdict/SKILL.md` |
| `dkf-review/modules/rct-diagnostics/` | `review/modules/experiment-diagnostics/` |
| `dkf-review/modules/small-n-diagnostics/` | `review/modules/small-n-diagnostics/` |
| `dkf-review/modules/sample-size-diagnostics/` (warrant grades) | `review/modules/whimsical-assumptions-diagnostics/` |
| `dkf-review/modules/simulation-diagnostics/` | `review/modules/quantitative-model-diagnostics/`, `review/references/simulation-harness.md` |
| `dkf-review/modules/observational-diagnostics/` (adjustment sets) | `review/modules/controls-samples-diagnostics/` |
| `dkf-review/references/simulation-harness.md`, `construction-validity.md`, `source-protocol.md`, `literature-protocol.md` | same names in `review/references/` |
| `dkf-review/references/statement-test-matrix.md` | `review/references/claim-test-matrix.md` |
| `dkf-review/assets/report-template.md` and the ledger CSV templates | `review/assets/` |
| `dkf-review/scripts/check_job.py` | `review/scripts/check_manifest.py` (concept) |
| `dkf-review/scripts/check_suite_version.py` and its test | `review/scripts/check_suite_version.py` |
| `dkf-review/spec-changes.csv` (format; rows restart at R001) | `review/spec-changes.csv` |
| `dkf-review-audit/SKILL.md`, `references/audit-cases.md` | `audit-review/` |
| `dkf-review-audit/scripts/check_spec_drift.py` and its test | `audit-review/scripts/check_spec_drift.py` |
| `dkf-review-audit/scripts/check_coverage.py` | `audit-review/scripts/check_coverage.py` (concept) |
| `dkf-consistency-review/SKILL.md` | `review-digest/SKILL.md` |
| `dkf-consistency-review/scripts/check_facts.py`, `check_style.py` | `review-digest/scripts/` (DKF fields; failures-only rule limited to the issue list) |
| `dkf-consistency-review/scripts/check_issue_coverage.py`, `render_review.py` | `review-digest/scripts/check_ledger_coverage.py`, `render_digest.py` (concepts) |

## New here

The clinical modules `estimand`, `missing-data`, `time-to-event`, `multiplicity`,
`regression-model`, `prediction-model` and `bayesian`; the references
`product-profiles.md`, `data-access.md`, `clinical-guidelines.md`, `estimands.md`,
`quarto-r-audit.md`, `r-traps.md`, `worked-cases.md`; the assignment template, the
consistency matrix, arithmetic checks, SAP adherence, specification map, assumption
ledger and questions templates, and `recompute.R`; `jobfiles.py`, `scan_job.py`,
`new_job.py`; the whole `dkf-synthetic-data` skill; `issues.py` and
`annotate_source.py`.

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
`SKILL.md` files, add rows to `dkf-review/spec-changes.csv` for changed requirements,
and update the commit recorded here.
