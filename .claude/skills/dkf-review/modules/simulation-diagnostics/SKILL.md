---
name: simulation-diagnostics
description: >-
  Diagnostics for a load-bearing number produced by Monte Carlo simulation: a
  simulated power or sample size, operating characteristics of a design, a simulated
  type I error. Writes the simulation out as ADEMP, checks that the data-generating
  mechanism produces the stated planning values, that the analysis inside the loop is
  the planned one, that Monte Carlo error and grid search do not decide the answer,
  and that seeds and saved results reproduce. Invoke from `code-and-data` whenever a
  load-bearing number comes from simulation.
---

# Simulation diagnostics

A simulation is a calculation whose inputs are a data-generating mechanism and an
analysis. It can be exactly right about the wrong mechanism. Check the mechanism and
the analysis against what the product says, then check the Monte Carlo machinery.
Engineering rules for loops, seeds and output: `../../references/simulation-harness.md`.

Trigger: any load-bearing number from simulation, including a simulated sample size,
power curve, type I error or operating characteristic. `NOT_APPLICABLE` when every
load-bearing number has a closed form; name them.

## Core checks

- **ADEMP, written out** (Morris, White and Crowther 2019): the aim; the
  data-generating mechanisms (every parameter, its value and its source in the
  assumption ledger); the estimand; the method (the analysis applied to each simulated
  dataset); the performance measures (power as the share of replicates meeting which
  criterion, type I error, bias, coverage). Each element is located in the code
  (`file:line`) and in the text; a mismatch is a specification-map row.
- **The mechanism produces the stated planning values.** Generate one very large
  dataset (or many replicates) from the product's own generator and compare the
  realised quantities with the printed planning values: marginal rates and means per
  arm, the expected effect, correlations, event rates at the stated horizon, the share
  of non-evaluable participants. A latent correlation used to generate correlated
  binary or ordinal outcomes is not the correlation of the observed categories; say
  which one the product states and which one the code sets. A mechanism that does not
  reproduce the printed planning values is a finding whatever the power it yields.
- **The analysis inside the loop is the planned analysis**, or the product says what it
  approximates and in which direction (an unadjusted test standing in for an adjusted
  model is usually conservative; a normal approximation for a small binary trial may
  not be). The decision rule matches the text (two-sided interval excludes zero;
  one-sided in the favourable direction; both).
- **Monte Carlo error.** For a simulated power p from R replicates, MCSE = √(p(1 − p)/R)
  (0.8 at R = 5,000: 0.57 percentage points). Report it beside every simulated number
  the product prints, and check any MCSE the product states. A difference between two
  simulated numbers smaller than about 2·√2·MCSE is not a difference.
- **Grid search.** "The smallest grid value reaching 80% power" selects on noise: with
  5,000 replicates, a grid point whose true power is 79.0% passes 80% with probability
  about 4%, and among several grid points just below the target the chance that one of
  them passes is correspondingly larger. Fit a smooth power curve over the grid (a logistic or probit
  regression of the replicate-level rejections on N, or on log N), read the N at which
  the fitted power crosses the target, and compare with the product's N; run more
  replicates near the crossing where the two differ by more than the grid step.
- **Type I error and sanity under the null.** Where the product reports a simulated
  null, check it was run with the same generator and analysis at a relevant N; where it
  does not, run one: a test whose simulated size is materially above alpha makes every
  power number beside it optimistic.
- **Reproducibility.** Where `set.seed()` sits; whether parallel workers get
  independent streams (`future.seed = TRUE`, `RNGkind("L'Ecuyer-CMRG")`); whether the
  same seed reproduces the printed numbers exactly on the delivered package versions.
  Results the document loads from a saved file (`.rds`, `.rda`) need the code that
  made them in the job, run with the settings the text states (replicates, grid,
  inputs): a saved result with no generating code, or made with other settings, is
  *unverifiable as delivered* or a finding.
- **Runtime.** Run the product's simulation first at a reduced replicate count (enough
  to see the code path work and the curve's shape), then, where a printed number is
  compared, at the delivered count in the background with start and end markers.
  Record both, and never compare a reduced-count number with a printed number as if it
  were a reproduction.

## Report back

Lead with whether the mechanism reproduces the stated planning values, whether the
analysis is the planned one, and how the product's N compares with the N from a fitted
power curve with its Monte Carlo error. Account for coverage: what ran, at how many
replicates, under which seed, and what was blocked. Put the mechanism mismatches and
the MCSE-qualified numbers under `## Leads for later stages` for `statements`.
