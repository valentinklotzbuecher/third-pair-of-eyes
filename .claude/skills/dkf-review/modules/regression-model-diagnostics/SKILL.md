---
name: regression-model-diagnostics
description: >-
  Diagnostics for regression models in clinical analyses: whether the fitted model is
  the specified one, covariate choice and adjustment, functional form, model
  assumptions and convergence, overfitting, repeated-measures and clustered structures
  (MMRM, mixed models, GEE), ordinal and count models, and how effects are summarised
  and back-transformed. Invoke from `code-and-data` whenever a load-bearing result
  comes from a regression model.
---

# Regression-model diagnostics

A model is a list of choices: outcome scale, covariates, functional form, variance
structure, link and summary. Each can be specified correctly in the text and
implemented differently in the code, and each can change what the coefficient means.

Trigger: any load-bearing estimate from a linear, generalised linear, mixed (MMRM),
GEE, ordinal, count or ANCOVA model. `NOT_APPLICABLE` when every load-bearing result is
an unadjusted comparison; name them.

## Core checks

- **The fitted model is the specified one.** Read it from the fitted object (`formula()`,
  `family()`, `nobs()`, random-effects structure, weights, offsets, contrasts), not from
  the code text, and compare with the specification map: outcome and its scale,
  covariates and how each enters (linear, spline, categorical with which reference
  level), interactions, random effects and covariance structure, link, and the rows
  actually used. A model fitted on fewer rows than the analysis set it claims (rows
  dropped for missing covariates) is a finding unless stated.
- **Covariates.** In randomised comparisons: prespecified prognostic covariates and the
  stratification factors (EMA guideline on adjustment for baseline covariates; FDA 2023
  guidance; Morris et al. 2022), never post-baseline variables, never covariates
  selected by significance or by observed imbalance. A continuous covariate
  dichotomised loses information; a baseline value of the outcome enters as a
  covariate (ANCOVA), not as a change score alone, unless stated. In non-randomised
  comparisons, covariates come from a causal argument (`../observational-diagnostics/`).
- **Effect summary on the right scale.** Odds ratios are not risk ratios when the
  outcome is common; adjusted odds ratios are conditional and not collapsible, so they
  differ from unadjusted ones even without confounding. A marginal risk difference or
  ratio from a logistic model needs standardisation (g-computation) with its own
  interval. Back-transformed estimates (`exp()` of log-scale coefficients, `emmeans`
  with `type = "response"`) name what they are (geometric mean ratio, not a mean
  difference).
- **Assumptions and fit.** Linear models: residual spread and outliers, influence of
  single participants (leave-one-out where data are shared); functional form for
  continuous covariates (splines over arbitrary categories). Logistic models:
  separation and sparse cells (warnings about fitted probabilities of 0 or 1),
  events per variable. Count models: overdispersion (Poisson against negative binomial
  or quasi-Poisson), offsets for exposure time. Ordinal models: the proportional-odds
  assumption checked or argued. A model whose warnings are hidden by `warning: false`
  is checked with the warnings visible.
- **Repeated measures and clustering.** MMRM: the covariance structure (unstructured
  where feasible, with its fallback order prespecified), visit as categorical, the
  treatment-by-visit interaction, the contrast at the primary visit, and small-sample
  degrees of freedom (Kenward–Roger or Satterthwaite; `lme4` alone reports no p-values,
  and `lmerTest` or `emmeans` choose the method). Mixed models: random-effects
  structure and singular fits; GEE: working correlation and robust variance, and the
  small-sample correction when clusters are few. Convergence warnings are read, not
  suppressed.
- **Software defaults** that change the statistic: `anova()` on `lm` gives sequential
  (type I) sums of squares; reference levels set by alphabetical factor order;
  `contrasts` options; `glm` without `family` is Gaussian (`../../references/r-traps.md`).
- **Overfitting.** Many covariates for few events or participants inflate estimates and
  understate uncertainty in small samples (`../small-n-diagnostics/`); in prediction
  models this is the central issue (`../prediction-model-diagnostics/`).

## Report back

Lead with every difference between the specified and the fitted model, covariate
choices that change the estimand or bias the estimate, effect summaries on the wrong
scale, and suppressed warnings that matter. Account for coverage. Put each under
`## Leads for later stages` for `statements`.
