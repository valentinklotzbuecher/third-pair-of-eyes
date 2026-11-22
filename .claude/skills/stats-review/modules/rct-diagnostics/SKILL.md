---
name: rct-diagnostics
description: >-
  Diagnostics for randomised trials: the randomisation scheme and whether the analysis
  respects it (stratification and minimisation factors, centres, clusters), analysis
  sets, baseline comparisons, attrition and noncompliance, and the special features of
  cluster, crossover, factorial, stepped-wedge and adaptive designs. Invoke from
  `code-and-data` whenever a result or calculation rests on randomised allocation.
---

# RCT diagnostics

Randomisation buys comparability at baseline and nothing after it. The analysis must
respect how the randomisation was done, and everything that happens after it
(exclusions, dropout, noncompliance, unblinding) can rebuild the selection problem it
removed. Adapted from the upstream `experiment-diagnostics` module.

Trigger: randomised allocation behind any result or calculation. `NOT_APPLICABLE` for
non-randomised designs (use `observational-diagnostics`).

## Core checks

- **The randomisation as implemented.** Method (simple, permuted blocks, stratified
  blocks, minimisation), allocation ratio, block sizes (fixed or variable, and
  concealed), stratification factors and the number of strata against the expected
  number of participants per stratum, who generates and conceals the sequence. Check
  the description is the same in every document (`analysis/document/consistency-matrix.csv`).
  Blocks too large for small centres or strata leave imbalance; many strata with few
  participants each give the stratification nothing to work with.
- **The analysis respects the randomisation.** Stratification and minimisation factors
  belong in the primary model (Kahan and Morris 2012; EMA guideline on adjustment for
  baseline covariates); leaving them out makes the standard errors conservative and is
  a finding unless the product says why (for example, too few participants per
  centre, with centre handled another way). Centres in a multicentre trial: fixed or
  random effects, or stratification only, chosen before the data. Clustered allocation
  is analysed at the cluster level or with a model that accounts for it
  (`../small-n-diagnostics/` when clusters are few).
- **Analysis sets.** The full analysis set includes every randomised participant, with
  the exceptions ICH E9 allows (failure of an objective eligibility criterion assessed
  before randomisation; no treatment taken, under a blinded rule; no data after
  randomisation), each stated in advance. Exclusions that depend on post-randomisation
  behaviour or outcome turn a randomised comparison into an observational one. The
  per-protocol set is defined by pre-specified deviations, and the safety set by the
  treatment actually received. Check that every table states its set and that the
  counts flow (`analysis/document/arithmetic-checks.csv`).
- **Baseline tables.** In a randomised trial, a significance test of baseline
  differences tests the randomisation, not comparability, and is discouraged (CONSORT;
  Senn 1994): a baseline table with p-values is a minor finding. Imbalance matters by
  its size on prognostic covariates, not by its p-value; covariates chosen for
  adjustment because they look imbalanced are data-driven choices (prefer the
  pre-specified set).
- **Post-randomisation conditioning.** A model that adjusts for, or a subset defined
  by, a variable measured after randomisation (adherence, an intermediate outcome, a
  post-baseline measurement) re-imports bias; hand it to `regression-model-diagnostics`
  with the variable named.
- **Attrition and missing outcomes**, overall and by arm, with reasons. A differential
  that is not statistically significant is not clearance: what matters is whether
  plausible departures from the missing-data assumption move the result
  (`../missing-data-diagnostics/`).
- **Noncompliance and crossover.** Take-up by arm; the primary comparison as
  randomised; any complier-average or per-protocol estimate presented as supplementary,
  with its assumptions (exclusion restriction, monotonicity) stated.
- **Blinding and assessment.** Who knew the allocation (participants, care providers,
  outcome assessors, statisticians); a subjective outcome assessed unblinded is a
  limit the interpretation must carry.

## Conditional checks

- **Cluster randomised**: the ICC used in design and the one observed (where data are
  shared); the analysis level; identification and recruitment of participants after
  cluster randomisation (a source of selection bias); CONSORT cluster extension.
- **Stepped-wedge**: secular time trends in the model; the correlation structure
  (exchangeable versus decaying within-cluster correlation); the number of clusters
  and steps.
- **Crossover**: washout, carryover and period effects; the analysis as within-patient
  comparison with period in the model; handling of participants who complete only one
  period.
- **Factorial**: whether the interaction is assumed absent, tested, or powered;
  main-effect claims under an interaction.
- **Non-inferiority and equivalence**: the margin and its justification, the analysis
  sets (both full and per-protocol, consistent conclusions), one-sided alpha.
- **Adaptive and group-sequential designs**: every adaptation rule and stopping
  boundary pre-specified, type I error control demonstrated (by theory or by
  simulation, `../simulation-diagnostics/`), and estimates adjusted for the stopping
  rule where the product reports them after early stopping.
- **Small trials**: randomisation inference using the actual assignment mechanism
  (permuting within strata, re-deriving every assignment-derived column from the
  permuted labels) as a check on model-based p-values
  (`../../references/methods/young_2019_channelling_fisher.md`).

## Report back

Lead with what each check found and what it costs the statements: a scheme the
analysis does not respect, exclusions that break randomisation, differential
attrition, blinding limits. Account for coverage: what you ran, what was
`NOT_APPLICABLE` and why, what was blocked. Put take-up, attrition and analysis-set
findings under `## Leads for later stages` for `statements`: who was analysed decides
which population a result describes.
