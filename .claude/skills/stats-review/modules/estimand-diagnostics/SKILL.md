---
name: estimand-diagnostics
description: >-
  Diagnostics for the estimand framework (ICH E9(R1)): whether each primary and key
  secondary estimand is defined by its five attributes, whether every plausible
  intercurrent event has a strategy, and whether the estimator, the handling of
  missing data and the sensitivity analyses target that estimand. Invoke from
  `code-and-data` whenever a product defines, implies or analyses a primary or key
  secondary estimand.
---

# Estimand diagnostics

The estimand is the question; the estimator is how the data answer it. Most analysis
plans that are internally consistent still answer a question other than the one they
state, usually through what happens after an intercurrent event. This module writes the
question down attribute by attribute and checks that every downstream choice answers
it. Background and the five strategies: `../../references/estimands.md`.

Trigger: a protocol, SAP, report or SSE with a primary or key secondary comparison.
For an SSE, a light pass: the estimand the calculation targets and any intercurrent
event the calculation ignores. `NOT_APPLICABLE` for purely descriptive products.

## Core checks

- **The five attributes**, for each primary and key secondary estimand, as stated and as
  implied by the analysis, in a table in the module report: treatment conditions;
  population; variable (endpoint, including its time point or window and scoring);
  intercurrent events with the strategy for each; population-level summary (difference
  in means, risk difference, ratio, hazard ratio, restricted mean). An attribute that is
  stated nowhere is filled from the analysis and flagged as implied.
- **Intercurrent events, listed from the disease and the treatment**, not only from the
  product: discontinuation or modification of the assigned treatment, rescue or
  prohibited medication, switching, death, and events that make the endpoint
  unmeasurable or undefined (surgery, progression, terminal events). For each: the
  strategy (treatment policy, hypothetical, composite, while on treatment, principal
  stratum), whether data are collected after the event, and how the analysis handles
  them. A plausible event with no strategy is a finding on the specification.
- **Death and truncation.** Where the endpoint does not exist after death (a symptom
  score, a laboratory value, a toxicity grade), a treatment-policy strategy cannot apply
  to death; the estimand needs a composite (death as the worst value), while-alive or
  principal-stratum handling, stated. Check how the analysis and, for an SSE, the
  simulation treat it.
- **Estimator alignment.**
  - Treatment policy: every randomised participant analysed in the assigned arm; data
    after the intercurrent event collected and used; missing outcomes handled under
    assumptions consistent with the strategy (retrieved-dropout or reference-based
    imputation rather than an assumption that participants who stopped treatment
    behave like those who continued). An analysis on the per-protocol set, or one that
    discards post-event data, does not target it.
  - Hypothetical: the hypothetical scenario stated ("had rescue medication not been
    available"); data after the event excluded or down-weighted consistently;
    imputation or modelling under an assumption that fits the scenario, typically MAR
    given the observed history.
  - Composite: the scoring of the event in the outcome, and whether the summary measure
    still means what the text says (a mean with a fixed worst value; a ranked or
    win-ratio summary).
  - While on treatment: the summary is defined over the time on treatment, and arms
    with different exposure durations are compared knowingly.
  - Principal stratum: the stratum, its identification assumptions, and why a
    randomised comparison of that stratum is credible.
  In time-to-event analyses, censoring at an intercurrent event is a hypothetical
  strategy that assumes independent censoring; say so where the product does not.
- **Sensitivity versus supplementary analyses.** Sensitivity analyses target the same
  estimand under different assumptions (for missing data: tipping-point or
  delta-adjusted imputation); supplementary analyses target other estimands (a
  per-protocol analysis). A "sensitivity analysis" that changes the estimand cannot
  support the robustness of the primary result.
- **Sample size and estimand.** The calculation's effect, its dropout allowance and its
  handling of intercurrent events match the estimand: a treatment-policy effect is
  usually smaller than an on-treatment effect from the literature; inflating N for
  dropout assumes missing outcomes, which the treatment-policy strategy then has to
  handle (`../missing-data-diagnostics/`).

## Report back

Lead with each estimand's attribute table, the intercurrent events without a
strategy, and every place where the estimator, the missing-data handling or a
sensitivity analysis targets a different estimand from the one stated, with the
direction this is likely to move the estimate where the evidence says. Account for
coverage. Put each misalignment under `## Leads for later stages`: a specification
that does not target its stated estimand is, at best, `narrower`.
