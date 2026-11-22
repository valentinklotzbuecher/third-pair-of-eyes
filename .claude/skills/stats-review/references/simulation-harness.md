# Simulation and resampling harness

Engineering rules for Monte Carlo runs: re-running a product's simulation, building an
independent one, generating synthetic data replicates, resampling. The modules decide
what to simulate; this file is how to simulate without artifacts that look like
findings. Adapted from the upstream harness, for R.

## Gate the generator, not just the outcome

Before interpreting any simulation result, validate the data-generating mechanism on
its own: generate one large dataset and check every component (arm sizes, marginal
rates and means, correlations, missingness, event times) against the values it is
meant to have, with no analysis in between. A generator with `NaN` or degenerate
components will still produce a "power"; the degeneracy is the explanation. Calibrate
the generator from the stated planning values, and label any value the review chose
itself.

## Numerically stable fitting

Inside a loop, fit with the functions the product uses or with `qr.coef(qr(X), y)`,
never `solve(crossprod(X))`. A `tryCatch` that swaps in another estimator on failure
silently mixes methods across replicates: count failures and report them instead.
Covariances come from the fitted object (`vcov(fit)`), not a hand-rolled formula.

## Analyse what the product's analysis sees

Extract the analysis data from the fitted call (`model.frame(fit)`, `nobs(fit)`) or the
product's own analysis-set code, not from the raw input. A simulated dataset missing
one derived column produces estimates near zero in every replicate, which reads as a
failed method and is a harness failure.

## Finiteness and sanity gates on every reported distribution

- Count replicates with finite results; require a stated minimum share before reporting
  a simulated power or p-value, and report the count.
- Check finite mean and SD and min < max for every reported distribution. A zero SD, or
  the same value across seeds when the draws are random, means the harness failed (a
  frozen RNG, a cached object reused across replicates).
- Report per-replicate failures (non-convergence, separation, singular fits) separately
  from the performance measures; a power computed only over converged replicates says
  so.
- For a permutation or randomisation test, compute the p-value from the permutation
  distribution with the test's own formula; check that the number of permutations does
  not exceed the number of distinct assignments.

## Incremental output and real seeds

Write each replicate's estimate, standard error, decision and any warning to a results
file inside the loop (or return a data frame per replicate and bind once), so a run that
dies mid-way leaves usable output. Use one `set.seed()` per run and independent
parallel streams (`future.seed = TRUE`, or `RNGkind("L'Ecuyer-CMRG")` with
`parallel::mclapply`); check that the drawn quantities vary across replicates. Record
the replicate count, seeds, R version, RNG kind and package versions.

## Monte Carlo error

Report the Monte Carlo standard error beside every simulated performance measure
(for a proportion p over R replicates, √(p(1 − p)/R)). Two simulated values that differ
by less than about three combined MCSEs are not different.

## Runtime

Size runs to finish in a few minutes: a reduced replicate count to check the code
path, the full count in the background (with start and end markers in the log) only
where a printed number is compared. Never report a reduced-count result as a
reproduction of a full-count printed number.

## Reporting

Report per scenario: replicates run and converged, the finite-result share, the
drawn-value SD (frozen-RNG check), the distribution of the performance measure, and
which replicates were dropped and why. The record must let a reader tell "the design
has this power" from "the harness produced garbage".
