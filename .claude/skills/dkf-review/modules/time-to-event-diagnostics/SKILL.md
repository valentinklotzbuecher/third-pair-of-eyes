---
name: time-to-event-diagnostics
description: >-
  Diagnostics for time-to-event endpoints: time origin and units, censoring rules and
  their independence, competing events, the proportional-hazards assumption and what
  the hazard ratio means without it, follow-up quantification, and event-driven
  sample sizes. Invoke from `code-and-data` whenever an endpoint is a time to an event,
  or a calculation rests on event rates.
---

# Time-to-event diagnostics

A survival analysis is three definitions (time zero, the event, censoring) and an
effect measure. Most errors live in the definitions and in units, and they do not show
in the output.

Trigger: a time-to-event endpoint, censoring, a competing event, a follow-up
statement, or a sample size computed from event rates or hazards. `NOT_APPLICABLE`
when no load-bearing result or calculation involves time to an event.

## Core checks

- **Definitions, written out**: time zero (randomisation, treatment start, a
  procedure, a landmark such as day 61 after ablation), the event (and which
  occurrence: first, second, any), censoring (end of study, loss to follow-up,
  withdrawal, a competing event) and the administrative end of follow-up. Each matches
  across text, code and governing documents. A time zero that starts after
  randomisation (a landmark, a post-treatment window) makes the comparison conditional
  on surviving event-free to the landmark: state which population that is, and whether
  events before the landmark are excluded, counted, or handled as a competing event.
- **Units.** Every rate, hazard, median and time point in one unit, or converted
  explicitly: days versus months versus years in input values, in `rpact`, `gsDesign`
  or `survival` calls, and in tables. A calculation that reads a 12-month event
  probability but follows participants for 304 days needs its rate converted
  accordingly (`../../references/r-traps.md`).
- **Censoring.** Censoring is assumed independent of the event given the model; for
  censoring at treatment discontinuation, switching or an intercurrent event this is a
  hypothetical-strategy assumption (`../estimand-diagnostics/`), stated or not.
  Censoring patterns by arm (reverse Kaplan–Meier for follow-up, Schemper and Smith
  1996) are reported where data are shared.
- **Competing events.** Death (or another event) that prevents the event of interest:
  censoring it estimates a hypothetical quantity and makes 1 − Kaplan–Meier overstate
  the cumulative incidence; the cumulative incidence function (Aalen–Johansen) and
  cause-specific or subdistribution hazards answer different questions (Austin, Lee
  and Fine 2016). A composite including death is an alternative. The product says
  which question it answers.
- **Proportional hazards.** A hazard ratio from a Cox model is an average over the
  follow-up when hazards are not proportional; check the plan for assessing it
  (Schoenfeld residuals, `cox.zph`; log–log plots) and what is reported if it fails
  (restricted mean survival time, Royston and Parmar 2013; time-varying effects;
  milestone analyses). A sample size under proportional hazards for a treatment
  expected to act late or wane needs a sensitivity scenario, not a sentence.
- **Tests and models agree.** Log-rank versus Cox score versus Wald test (practically
  equivalent without covariates and large samples); stratified log-rank or Cox model
  for the stratification factors; ties handling (`coxph` defaults to Efron, SAS PHREG
  to Breslow). A log-rank test reported beside a stratified Cox model needs the
  stratification stated for both.
- **Event-driven sample size.** Power comes from the number of events (Schoenfeld:
  events = (z₁₋α/₂ + z₁₋β)² / (p(1 − p)(log HR)²) with allocation proportion p);
  the number of participants follows from the event probability under the accrual and
  follow-up pattern, and dropout. Check each step, the assumed distribution (often
  exponential), and whether the planned analysis is event-driven (the analysis
  triggered at the target number of events) or calendar-driven.
- **Follow-up and censoring in summaries.** Median follow-up computed by reverse
  Kaplan–Meier, not as the median observed time; Kaplan–Meier curves with numbers at
  risk; survival at a time point read with `summary(fit, times = …)` and the interval
  method named.

## Report back

Lead with definition and unit mismatches, the handling of competing events and
non-proportional hazards against what the statements claim, and the recomputed events
and N where a sample size depends on them. Account for coverage. Put each under
`## Leads for later stages` for `statements`.
