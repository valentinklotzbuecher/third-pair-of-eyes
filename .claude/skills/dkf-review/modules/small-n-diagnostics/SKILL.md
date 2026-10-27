---
name: small-n-diagnostics
description: >-
  Diagnostics for small samples and few clusters: what the design could detect,
  whether a null carries information, small-sample inference for mixed models and
  cluster-robust errors, overfitting from too many covariates, exaggeration of
  significant estimates, and the special logic of pilot and feasibility studies.
  Invoke from `code-and-data` whenever participants, clusters or centres are few, the
  product is a pilot or feasibility study, or a null result carries weight.
---

# Small-N diagnostics

A small sample cuts both ways: too little power to detect a plausible effect, and too
few degrees of freedom for the model put on it. A null proves nothing on its own, a
significant estimate from a small trial is likely to be too large, and a precise-
looking interval may owe its precision to a large-sample approximation that does not
hold. The checks put numbers on both directions. Adapted from the upstream
`small-n-diagnostics` module, for R and clinical designs.

Trigger: few participants (as a rule of thumb, fewer than about 50 per arm), few
clusters or centres (fewer than about 40), a pilot or feasibility study, or a null or
near-null result that the product interprets. `NOT_APPLICABLE` when the design has
ample units and no null carries weight.

## Core checks

- **What the design could detect.** The minimum detectable effect at 80% power for the
  achieved or planned N, compared in the claim's own units with the planning effect and
  with effects the literature makes plausible: "this design could detect X; the
  plausible effect is Y" (`../../references/methods/cohen_1988_effect_sizes.md`).
- **Nulls.** A non-significant result is informative only for the range its interval
  excludes. "No difference", "no effect" or "comparable" needs an equivalence or
  non-inferiority argument with a stated margin (`../../references/methods/eggers_tunon_dafoe_2024_placebo_tests.md`
  for the equivalence logic); otherwise the text says what the data cannot exclude,
  with the interval (Altman and Bland 1995).
- **Exaggeration.** For a significant estimate from a low-powered design, the expected
  exaggeration ratio and the chance of a wrong sign at a plausible true effect
  (`../../references/methods/gelman_carlin_2014_type_ms.md`), stated where the product
  interprets the size of the effect.
- **Small-sample inference.** Mixed models and MMRM with Kenward–Roger or
  Satterthwaite degrees of freedom; cluster-robust errors with few clusters use CR2
  with Satterthwaite degrees of freedom (`clubSandwich`; Pustejovsky and Tipton 2018) or
  a cluster-level analysis (Leyrat et al. 2018), not the default sandwich estimator;
  GEE with a small-sample correction; exact or permutation tests for small two-arm
  comparisons. Where a model-based p-value and a permutation p-value disagree
  materially, the disagreement is the finding. For few clusters with unequal sizes,
  the effective number of clusters and the leverage of the largest ones
  (`../../references/methods/mackinnon_nielsen_webb_2023_few_clusters.md`; its Stata
  commands have R equivalents in `fwildclusterboot` and `clubSandwich`).
- **Overfitting.** Covariates or parameters approaching the number of participants or
  events manufacture fit and unstable estimates; re-estimate with the prespecified
  minimal set where data are shared, and check separation in logistic models.
- **Pilot and feasibility studies.** Objectives are feasibility parameters (recruitment,
  retention, adherence, variance of the outcome) with precision targets and progression
  criteria; a hypothesis test of efficacy in a pilot is underpowered by design and its
  result is not evidence for or against the intervention (CONSORT pilot extension,
  Eldridge et al. 2016). A sample size justified by a rule of thumb (12 per group,
  Julious 2005) is stated as such.

## Report back

Lead with what the design could detect against the plausible effect, how each null is
worded, and where large-sample inference is relied on with too few units. Account for
coverage. Record every power and precision threat under `## Leads for later stages`
for `statements`, whether or not the result is a null: the detectable-effect
comparison decides whether a null is informative.
