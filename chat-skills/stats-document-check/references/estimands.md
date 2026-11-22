# Estimands (ICH E9(R1)) in brief

The reference for `estimand-diagnostics` and for the design critique in the document
stage. Read the addendum itself before quoting it.

## The five attributes

1. **Treatment conditions**: the intervention and the comparator, including the
   regimen and what is allowed around it (background therapy, rescue).
2. **Population**: the patients the question is about, as defined by eligibility (or a
   principal stratum).
3. **Variable (endpoint)**: what is measured on each patient, when, and how it is
   derived or scored.
4. **Intercurrent events and their strategies**: events after treatment starts that
   affect the interpretation or existence of the measurements (discontinuation, switch,
   rescue medication, death, events that make the endpoint unmeasurable), each with a
   strategy.
5. **Population-level summary**: the measure that compares the treatment conditions
   (difference in means, risk difference or ratio, odds ratio, hazard ratio, difference
   in restricted mean survival time).

## The five strategies

| Strategy | Question it answers | Data and analysis it needs |
|---|---|---|
| Treatment policy | effect of being assigned the treatment, whatever happens after the event | outcomes collected after the event; every randomised participant; missing data handled with assumptions that fit (retrieved dropout, reference-based imputation) |
| Hypothetical | effect in a scenario where the event would not occur (e.g. no rescue available) | the scenario stated; data after the event set aside; modelling or imputation under assumptions that fit the scenario, typically MAR given the observed history |
| Composite variable | the event is part of the outcome (e.g. death or rescue counted as failure, or as the worst score) | the event folded into the variable with a stated rule |
| While on treatment | effect while patients stay on treatment (or alive) | the variable defined over the time on treatment; comparisons account for different durations |
| Principal stratum | effect in the subpopulation defined by potential occurrence of the event (e.g. those who would comply under either arm) | strong identifying assumptions, stated and defended |

## Sensitivity and supplementary analyses

- **Sensitivity analyses** keep the estimand and vary the assumptions of the primary
  estimator (for missing data: delta-adjusted or tipping-point imputation; for
  intercurrent events: alternative imputation under the same strategy). They show
  whether the conclusion depends on an untestable assumption.
- **Supplementary analyses** target other estimands (per-protocol, a different
  strategy). They add information but do not show the primary result is robust.

## Common misalignments

- A treatment-policy estimand with follow-up that stops at treatment discontinuation:
  the data the strategy needs are not collected, and the analysis silently becomes
  hypothetical.
- A per-protocol set used as the primary analysis of a treatment-policy estimand.
- Last observation carried forward described as conservative or as treatment policy;
  it is neither in general.
- Death treated with a treatment-policy strategy for an endpoint that does not exist
  after death.
- Censoring at an intercurrent event in a time-to-event analysis without stating that
  this is a hypothetical strategy that assumes independent censoring.
- A sample size whose effect comes from on-treatment or completer analyses in the
  literature, used for a treatment-policy estimand (usually optimistic).
