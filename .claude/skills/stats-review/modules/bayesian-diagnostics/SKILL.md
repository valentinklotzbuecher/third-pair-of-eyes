---
name: bayesian-diagnostics
description: >-
  Diagnostics for Bayesian analyses and designs: priors and their justification and
  sensitivity, computation (convergence, effective sample size, divergences),
  posterior summaries and decision rules, and the frequentist operating
  characteristics of Bayesian designs. Invoke from `code-and-data` whenever a
  load-bearing result or design decision is Bayesian.
---

# Bayesian diagnostics

A Bayesian result is the prior, the likelihood and the computation together. The
review checks each, and checks that the decision rule the product uses means what the
text says.

Trigger: a Bayesian model, a posterior probability or credible interval used for a
claim, a Bayesian sample size or adaptive design. `NOT_APPLICABLE` otherwise.

## Core checks

- **Priors.** Every prior stated with its parameters and the reason for it (previous
  trials, expert elicitation, weakly informative defaults); informative priors on the
  treatment effect justified and their effective sample size stated; a sensitivity
  analysis with at least one sceptical and one non-informative alternative where the
  conclusion depends on the prior. Priors on variance parameters in hierarchical models
  matter with few groups.
- **Computation.** Convergence (R-hat near 1 by the rank-normalised version, Vehtari
  et al. 2021; at most 1.01 is the usual threshold), bulk and tail effective sample
  sizes, divergent transitions and tree-depth warnings in Stan-based tools (`brms`,
  `rstanarm`, `cmdstanr`), number of chains, iterations and the seed. A result reported
  with unresolved divergences or warnings hidden by chunk options is a finding.
- **Model checking.** Posterior predictive checks for the features the claim relies on;
  the likelihood matches the outcome type and the design (clustering, repeated
  measures).
- **Summaries and decisions.** Posterior medians or means with credible intervals;
  posterior probabilities of clinically meaningful effects (not only of an effect
  above zero); decision thresholds (a posterior probability above 0.95, say) stated in
  advance. A posterior probability is not a p-value and the text does not treat it as
  one. Reporting follows the Bayesian Analysis Reporting Guidelines (Kruschke 2021).
- **Designs.** For Bayesian adaptive or sample-size designs: the operating
  characteristics (type I error, power, expected sample size, probability of early
  stopping) estimated by simulation over the relevant scenarios
  (`../simulation-diagnostics/`), and whether the regulatory or ethics context requires
  frequentist error control.

## Report back

Lead with unjustified or influential priors, computational problems, and decision
rules that do not mean what the text says. Account for coverage. Put each under
`## Leads for later stages` for `statements`.
