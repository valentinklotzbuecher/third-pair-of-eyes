---
name: sample-size-diagnostics
description: >-
  Diagnostics for a sample size or power calculation: an independent recomputation by
  a second method, every planning value traced to its source and graded for warrant,
  the effect of each value on N, the match between the test the calculation assumes
  and the analysis the trial will use, dropout and rounding rules, and the statements
  the product makes about sensitivity. Invoke from `code-and-data` whenever a product
  states a sample size, a power or a detectable effect.
---

# Sample-size diagnostics

A sample size is a function of its planning values. The number is only as credible as
the least credible input it is sensitive to, and a recomputation that reuses the
product's own inputs checks only the arithmetic. This module checks the arithmetic, the
inputs and the match between what was calculated and what will be analysed.

Trigger: a stated sample size, power or minimum detectable effect anywhere in the
product. `NOT_APPLICABLE` when the product states none.

## Core checks

- **The design question, written out.** One line per calculation: the endpoint and its
  scale; the effect measure and the target effect; the test or model the calculation
  assumes; alpha, sidedness and power; the allocation ratio; every nuisance parameter
  (control-group rate or mean, SD, correlation, event probability, accrual and
  follow-up, cluster size and ICC, number of measurements); the allowance for dropout or
  non-evaluable participants and the rounding rule. A calculation whose design question
  cannot be written out from the product is *unverifiable as delivered* at the missing
  item.
- **Recompute by a second method** (`work/scripts/ss_*.R`, with logs), taking inputs
  from the printed text and its sources, not from the product's code: a closed form
  where one exists (`power.t.test`, `power.prop.test`, Schoenfeld's or Freedman's
  formula for events, the ANCOVA design factor 1 − ρ², a design effect 1 + (m − 1)·ICC),
  a different package, or an independent simulation where the product simulates
  (`../simulation-diagnostics/`). Record in `results.csv`: printed N or power, the
  recomputed value, the method, and the inputs with their locations. Agreement within
  the method's known differences (normal approximation versus exact, continuity
  correction, Monte Carlo error) is agreement; anything else is traced to its cause
  before it is written up: a different input, a different test, units, sidedness, a
  rounding step.
- **Planning values and their warrant.** Every input goes to
  `analysis/code-and-data/assumption-ledger.csv` (template
  `../../assets/assumption-ledger.csv`): `id | assumption | value | location | source_cited
  | source_checked | warrant | effect_on_N | artifact | note`. Open each cited source
  (`../../references/source-protocol.md`) and grade the warrant:
  - `SOURCED`: the source reports the value for a comparable population, endpoint,
    intervention and time frame;
  - `DERIVED`: computed from sourced values by a stated rule (pooling arms, weighting
    by case mix); recompute the derivation;
  - `CONTESTED`: sources disagree, or the value sits at the favourable end of the
    reported range; record the range;
  - `TRANSPORTED`: sourced, but for another population, setting, endpoint definition
    or time frame, and the product does not say how it was adapted;
  - `UNANCHORED`: no source; or the source does not contain the value;
  - `CONVENIENCE`: chosen to make the calculation work (a round effect size with no
    clinical or empirical anchor, a correlation "assumed modest").
  The target effect is graded twice: is it plausible (the evidence for an effect of
  that size) and is it important (a minimal clinically important difference or a
  stated rationale; DELTA² guidance, Cook et al. 2018, `../../references/clinical-guidelines.md`).
  An effect justified only as "what the budget allows" is a finding of disclosure, not
  of arithmetic.
- **Sensitivity of N to each input.** For every input graded anything but `SOURCED`,
  recompute N (or power at the fixed N) across the range the evidence supports, and
  enter the movement in `effect_on_N`. An input that moves N beyond the planned
  recruitment, or power below the stated target, across its supported range is the
  finding; an input that barely moves N is reported as such, whatever its grade. Where
  the product prints a sensitivity table, check that the text's summary of it is
  supported (`analysis/document/sensitivity-claims.csv`), and extend it where it varies
  the inputs that matter least.
- **The test behind the calculation versus the planned analysis.** Compare with the
  primary analysis in the product, protocol and SAP. A calculation for an unadjusted
  test with an adjusted analysis planned is usually conservative, and fine when stated;
  a calculation for a more powerful analysis than the one planned (a parametric test
  for an endpoint the SAP analyses non-parametrically, an ANCOVA gain claimed with no
  baseline measurement, events computed for a log-rank test where the analysis
  dichotomises) is a finding. A simulated power should simulate the planned analysis,
  or say why a simpler one approximates it and in which direction.
- **Dropout and non-evaluable allowance.** The usual convention is N_randomised =
  N_evaluable / (1 − d). N × (1 + d) under-inflates (for d = 0.10: 1.10 versus 1.111),
  a finding unless the product states it. Check that the allowance matches the
  estimand: under a treatment-policy strategy with missing outcomes imputed or modelled,
  inflating N treats dropout as loss of information, and the analysis must match that
  assumption (`../missing-data-diagnostics/`). Check where rounding happens (per arm,
  total, to the block size, to a multiple of 10) and that the final N is what the
  rounding gives.
- **Design-specific inputs.**
  - *Time-to-event*: power comes from events; check the number of events, the event
    probability under accrual and follow-up, censoring and dropout timing, and the
    time units of every rate (`../time-to-event-diagnostics/`). In `rpact` and similar
    design functions, event probabilities are read at `eventTime` and dropout at
    `dropoutTime` (both 12 by default) in the same unit as accrual and follow-up:
    mixing days and months, or leaving the defaults where the endpoint horizon is not 12
    units, silently changes the design (`../../references/r-traps.md`).
  - *Cluster and stepped-wedge designs*: design effect with the ICC's source, variation
    in cluster size (coefficient of variation), the number of clusters and its
    small-sample consequence (`../small-n-diagnostics/`).
  - *Repeated measures and ANCOVA*: the correlation with baseline and its source; the
    number of post-baseline measurements and how they enter the analysis.
  - *Non-inferiority and equivalence*: the margin, its justification (ICH E10, EMA and
    FDA guidance), one-sided alpha 0.025 or two-sided 0.05 consistently, and the
    expected true difference (often assumed zero, which is optimistic if the new
    treatment is expected to be slightly worse).
  - *Several primary endpoints, arms or looks*: alpha as adjusted by the multiplicity
    rule, power defined for the right event (each endpoint, all endpoints, at least
    one), and inflation for interim analyses (`../multiplicity-diagnostics/`).
  - *Binary and ordinal endpoints*: which test (with or without continuity correction,
    exact), risk difference versus ratio versus odds ratio, proportional odds for an
    ordinal shift; for a composite score analysed as a mean, the distribution the
    simulation or formula assumes.
  - *Pilot and feasibility studies*: a sample size justified by estimation precision
    or feasibility, not by power for a hypothesis the pilot will not test; a power
    calculation in a pilot is a finding unless the pilot tests efficacy.
- **Feasibility.** Where the product states recruitment (eligible patients per year,
  participation rate), compare the target N with the recruitment period: a target that
  needs more patients than the stated pool is a finding for the author to address.

## Report back

Lead with what each check found and what it costs the statements: the recomputed N
against the printed one; the inputs graded `UNANCHORED`, `CONVENIENCE`, `CONTESTED` or
`TRANSPORTED` and how far each moves N; the mismatch, if any, between the calculation
and the planned analysis. Account for coverage: what you ran, what was
`NOT_APPLICABLE` and why, what was blocked. Put every assumption with its warrant and
its effect on N under `## Leads for later stages` for `statements`: the warrant of the
planning values is what decides whether the primary sample-size statement holds,
holds only in a narrower scenario, or is not established.
