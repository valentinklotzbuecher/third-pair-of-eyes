---
name: missing-data-diagnostics
description: >-
  Diagnostics for missing outcome and covariate data: the amount and pattern by arm,
  the assumption the primary analysis makes and whether it fits the estimand, how
  multiple imputation is implemented, and whether sensitivity analyses vary that
  assumption. Invoke from `code-and-data` whenever outcomes are missing, participants
  drop out, data are imputed, or an analysis set removes randomised participants.
---

# Missing-data diagnostics

Every analysis of incomplete data assumes something about the values it cannot see.
The questions are which assumption, whether it fits the estimand, whether the code
implements it, and whether the conclusion survives plausible departures from it. The
missing-data assumption can never be tested from the observed data; it can only be
stated, justified and varied.

Trigger: missing outcomes or key covariates, dropout, imputation of any kind
(including last observation carried forward or single imputation), or an analysis
set that removes randomised participants. For an SSE, a light pass: the dropout
allowance and what it assumes. `NOT_APPLICABLE` when no load-bearing analysis has
missing data and the product says so with counts.

## Core checks

- **Amount and pattern.** Missing outcomes overall, by arm and by visit, with reasons
  where reported; monotone dropout versus intermittent missingness; missing baseline
  covariates. Differences by arm in amount or reason are recorded, whatever their
  p-value.
- **The assumption, named.** Complete-case analysis is valid under MCAR, or under MAR
  given the covariates in the model when missingness depends only on them; a mixed
  model or MMRM on all available data assumes MAR given the observed history; multiple
  imputation assumes MAR given the imputation model unless it is reference-based or
  delta-adjusted. Last observation carried forward and baseline carried forward are
  single imputations that understate variance and assume something specific about
  the trajectory; they are not conservative in general (EMA guideline on missing data).
  Record the assumption the primary analysis makes, whether the product names it, and
  whether it fits the estimand's strategy for the events that cause the missingness
  (`../estimand-diagnostics/`).
- **Multiple imputation, as implemented.** The imputation model includes the outcome,
  the treatment arm (or imputes by arm), every variable in the analysis model,
  interactions and non-linear terms the analysis uses, and auxiliary variables that
  predict missingness; it is imputed on the scale and in the form the analysis uses.
  The number of imputations is adequate (at least the percentage of incomplete cases is
  a common rule, White et al. 2011; `mice` defaults to 5); the seed is set; Rubin's
  rules pool the estimates (`mice::pool`), not an average of p-values; the method per
  variable is appropriate (`mice` defaults: predictive mean matching for numeric,
  logistic regression for binary, polytomous for unordered factors, proportional odds
  for ordered). Passive imputation or just-another-variable for derived quantities
  (a total score, a ratio, a change from baseline) is stated and consistent.
- **Sensitivity analyses vary the assumption.** For the primary endpoint, a
  tipping-point or delta-adjusted analysis (or reference-based imputation, jump to
  reference, copy reference) shows how far the missing-data assumption must move to
  change the conclusion (Cro et al. 2020). A sensitivity analysis that keeps the same
  assumption (complete cases versus MI under MAR) does not test it.
- **Code against text.** The rows the code drops (`na.omit`, `complete.cases`, model
  defaults that silently drop incomplete rows, `filter()` on a condition that is `NA`)
  against the counts the text reports; the analysis set each table claims against the
  rows its model used (`nobs()`).
- **Dropout allowance in a sample size.** An allowance of d% assumes d% of outcomes
  missing at the primary time point and treats them as lost information; the planned
  analysis must then handle those participants in a way consistent with the estimand
  (a treatment-policy estimand still includes them).

## Report back

Lead with the assumption behind the primary analysis, whether it fits the estimand,
whether the code implements the stated method, and whether any sensitivity analysis
varies the assumption, with how far it has to move. Account for coverage. Put each
misfit under `## Leads for later stages` for `statements`.
