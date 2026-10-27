# Construction validity: checks on calculations the review built

The challenge stage's reference for calculations the review built itself
(`../challenge/SKILL.md`). A construction bug reproduces cleanly on every re-run; these
checks exist because re-execution cannot see it. Adapted from the upstream file, with
the econometric command traps replaced by the constructions a clinical review builds.

## Independent recomputations

A recomputation counts as independent only if its inputs come from the printed text
and the cited sources, not from the product's code.

- **Inputs.** List each input with its source location; compare with the product's
  inputs and say which differ.
- **Method.** The same test, sidedness, allocation, units and rounding as the product
  intends, or the difference stated with its expected direction (normal approximation
  versus exact; continuity correction; unadjusted versus adjusted analysis).
- **Units and horizons.** Rates, hazards and probabilities on the same time scale; an
  event probability at 12 months is not one at 304 days.
- **Agreement is a control, not validation.** A recomputation that agrees with the
  product to the last digit after taking its inputs from the product's code checks the
  arithmetic only.

## Synthetic data and known-truth tests

The question every check answers: **does the generated data exercise the code the way
real data would, and could the test have failed?**

- **Contract.** The generator produces every variable the code reads, with the types,
  levels, units, visit structure and missing-value codes the data contract states;
  rebuilding the contract from the generated data reproduces it.
- **Edge cases, written before the run.** Each edge case (a missing outcome, an
  out-of-window visit, a duplicated record, an absent factor level, a boundary value)
  has its expected effect on the analysis sets and derived variables written down
  before the code runs; the check compares against that expectation, not against
  whatever the code produced.
- **Known truth.** The planted effect is on the estimand the analysis targets (same
  scale, same analysis set, same handling of intercurrent events); its size is large
  enough, and the replicate count high enough, that a wrong estimator (wrong arm
  coding, a dropped covariate, a sign error) would visibly fail. A known-truth test
  that would pass with a broken estimator tests nothing.
- **Planted missingness** follows the mechanism the analysis claims to handle (MAR
  given observed covariates for a MAR method), and one departure from it shows the
  method is sensitive where it should be.

## Stochastic procedures: resampling, permutation, simulated assignment

- **Assignment units.** Permutations and resamples move units at the level that was
  randomised (participant, cluster, centre) and stay within strata.
- **Derived columns.** Every column derived from the assignment (treatment dummies,
  period indicators, cluster-level treatment) is re-derived from the permuted labels;
  regenerating from the observed labels must reproduce the shipped columns exactly.
- **Statistic and tail.** Name the statistic and the tail, and verify the code computes
  that tail.
- **Inspect draws.** Dump a few generated assignments or datasets and check them by eye
  against the design: arm sizes, strata, support.

## Product-attributed constructions

A calculation the review presents as "the product's specification" must be the
product's: resolve the attribution against the printed text and the code at
`file:line` before building on it. An analogue built because the exact object cannot be
built (data not shared) is labelled as the closest feasible analogue, never as the
product's analysis.

## Derived quantities

A ratio, share or bound computed from estimates carries the uncertainty of its inputs.
Two numbers that agree to several decimals across different samples, windows or
methods coincide until shown to be the same object.
