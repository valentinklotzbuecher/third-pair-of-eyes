---
name: multiplicity-diagnostics
description: >-
  Diagnostics for multiple comparisons and selective inference: families of
  hypotheses and the error rate each controls, several primary endpoints, arms or
  time points, interim analyses and stopping rules, claims on secondary endpoints,
  and subgroup or effect-modification claims. Invoke from `code-and-data` whenever
  more than one hypothesis could support a confirmatory claim, or a subgroup or
  secondary result is presented as a finding.
---

# Multiplicity diagnostics

A confirmatory claim is only as strong as the error rate behind it. Several
endpoints, arms, time points, looks or subgroups each give one more chance for a
false positive, and the product must say which family of hypotheses its claims draw on
and how the error rate over that family is controlled, or present the extra results
as descriptive.

Trigger: more than one primary endpoint, arm or time point; interim analyses; a
claim on a secondary endpoint; a subgroup or effect-modification claim; a
specification chosen among several. `NOT_APPLICABLE` when one prespecified primary
hypothesis carries every confirmatory claim and secondary results are presented
without inferential claims. Candidate endpoint definitions compared in an SSE to choose
the primary endpoint are a design choice, not multiplicity, unless more than one of
them is to carry a confirmatory claim.

## Core checks

- **Families and error rates.** Each confirmatory claim maps to a prespecified family
  and a procedure that controls the family-wise error rate (Bonferroni or Holm,
  hierarchical fixed-sequence testing, gatekeeping, graphical procedures; Bretz et al.
  2009) or states why control is not needed (co-primary endpoints that must all
  succeed need no adjustment for type I error but lose power; a single primary with
  descriptive secondaries). Record each family, procedure and alpha in the module
  report. A claim outside every controlled family is descriptive, and the text must
  read that way.
- **Implementation.** The order of a hierarchy is followed in the report (testing
  stops at the first non-rejection; later "significant" results are descriptive);
  adjusted p-values come from the stated method (`p.adjust` method named); the alpha
  in the sample size matches the alpha in the analysis.
- **Interim analyses.** Number and timing of looks (information fractions), the
  spending function or boundaries (O'Brien–Fleming, Pocock, Lan–DeMets), binding or
  non-binding futility, what happens to alpha at the final analysis, and the sample
  size inflation that the boundaries require. A report after early stopping reports
  estimates that account for it or says they are biased away from the null. An
  unplanned look is a finding.
- **Subgroups and effect modification.** A subgroup claim needs a direct test of
  interaction, not a significant result in one subgroup beside a non-significant one in
  another (`../../references/methods/gelman_stern_2006_difference_test.md`); it is
  credible when prespecified with a direction, few in number, supported by a
  significant interaction within the trial, consistent across related outcomes and
  biologically plausible (Sun et al. 2010; ICEMAN, Schandelmaier et al. 2020). Report
  forest plots on the effect scale with interaction p-values. A subgroup finding
  failing these is exploratory and written so.
- **Specification choice.** Where the product could have analysed the primary endpoint
  several ways (definitions, windows, covariate sets, transformations) and reports one,
  the choice was made before the data or the forks are counted
  (`../../references/methods/gelman_loken_2013_forking_paths.md`). Candidate endpoint
  definitions compared in an SSE are a design choice; the same comparison made after
  unblinding is selection.
- **Many secondary outcomes.** A table of twenty secondary outcomes with one starred is
  read as one in twenty; the text claims nothing confirmatory from it.

## Report back

Lead with each confirmatory claim's family and error-rate control, every claim outside
a controlled family, interim-analysis gaps, and subgroup claims that fail the
credibility criteria. Account for coverage. Put each under
`## Leads for later stages` for `statements`.
