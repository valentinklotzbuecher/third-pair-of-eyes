---
name: observational-diagnostics
description: >-
  Diagnostics for non-randomised comparisons of treatments or exposures: the target
  trial the analysis emulates, time zero and immortal time, the adjustment set and its
  causal justification, propensity-score methods (overlap, balance, weights), and
  sensitivity to unmeasured confounding. Invoke from `code-and-data` whenever a
  result compares treatments or exposures that were not randomised.
---

# Observational diagnostics

Without randomisation, the comparison is only as good as the argument that the
groups would have had the same outcomes had they been treated alike. That argument
lives in the design (who is compared, from when) and in the adjustment set (which
confounders, measured how), and it can be broken by adjusting for the wrong variables
as easily as by missing the right ones.

Trigger: a comparison of treatments, exposures or policies not assigned at random,
including registry, cohort, case–control and before–after designs. `NOT_APPLICABLE`
for randomised comparisons and purely descriptive results.

## Core checks

- **The target trial.** Write the trial the analysis emulates (Hernán and Robins 2016):
  eligibility, treatment strategies, assignment, time zero, follow-up, outcome, causal
  contrast, analysis. Eligibility, assignment and the start of follow-up must coincide
  at time zero; a gap between them produces immortal-time or prevalent-user bias
  (exposure defined by something that happens after follow-up starts, or by surviving
  long enough to be treated). Check the code's definition of time zero and exposure
  against the text.
- **The adjustment set.** Each covariate is justified as a confounder (a common cause of
  exposure and outcome, measured before exposure), ideally from a stated causal
  diagram. Mediators (on the path from exposure to outcome), colliders (common effects,
  including selection into the sample), descendants of the outcome and near-instruments
  are bad controls (`../../references/methods/cinelli_forney_pearl_2024_bad_controls.md`);
  "pre-exposure, so it is safe" is not a sufficient argument (M-bias). Name the most
  important confounders the data lack and how the product addresses them.
- **Propensity-score methods.** Overlap (distributions of the score by group; trimming
  rules prespecified), covariate balance after weighting or matching measured by
  standardised mean differences (not p-values), extreme weights and their handling
  (stabilised or truncated weights, effective sample size), the estimand the method
  targets (ATE with inverse-probability weights, ATT with matching or ATT weights,
  overlap population with overlap weights), and variance that accounts for the
  estimated score and for matching (Austin and Stuart 2015). A doubly robust estimator
  states both models.
- **Sensitivity to unmeasured confounding.** The E-value for the estimate and the
  confidence limit nearest the null (VanderWeele and Ding 2017), or a robustness value
  benchmarked against measured covariates
  (`../../references/methods/cinelli_hazlett_2020_sensitivity.md`); negative-control
  outcomes or exposures where the design offers them. "We adjusted for all known
  confounders" is not a sensitivity analysis.
- **Language.** Causal verbs (reduces, prevents, improves) need the design and the
  sensitivity analysis to carry them; an association is reported as an association.
- **Other designs.** Difference-in-differences, regression discontinuity, instrumental
  variables, interrupted time series and synthetic control have their own diagnostics
  in the upstream `research_skills` modules; use them if installed, otherwise record
  `NOT_RUN` with that reason.

## Report back

Lead with the target-trial mismatches (time zero, immortal time), bad controls and
missing key confounders, balance and overlap failures, and the size of unmeasured
confounding that would explain the result away. Account for coverage. Put each under
`## Leads for later stages` for `statements`.
