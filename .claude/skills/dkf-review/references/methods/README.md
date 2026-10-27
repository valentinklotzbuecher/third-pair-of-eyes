# references/methods/

General-purpose method cribs, copied unchanged from the upstream `research_skills`
suite (`review/references/methods/`, v0.9.1). They are distilled, page-referenced
summaries written and source-audited upstream; their examples come from economics, but
the methods apply to clinical studies. The clinical sources are in
`../clinical-guidelines.md`.

| File | Used for |
|---|---|
| `cohen_1988_effect_sizes.md` | standardised effect sizes; minimum detectable effects |
| `gelman_carlin_2014_type_ms.md` | Type S and Type M (exaggeration) errors in low-powered designs |
| `gelman_stern_2006_difference_test.md` | "significant in A, not in B" is not a test of a difference (subgroups) |
| `gelman_loken_2013_forking_paths.md` | data-contingent analysis choices |
| `simmons_nelson_simonsohn_2011_false_positive.md` | undisclosed analytic flexibility |
| `eggers_tunon_dafoe_2024_placebo_tests.md` | equivalence testing; why non-rejection is not balance |
| `cinelli_forney_pearl_2024_bad_controls.md` | good and bad controls (mediators, colliders, M-bias) |
| `cinelli_hazlett_2020_sensitivity.md` | sensitivity to unmeasured confounding |
| `young_2019_channelling_fisher.md` | randomisation inference against conventional inference |
| `morgan_rubin_2012_rerandomization.md` | inference under restricted randomisation |
| `abadie_athey_imbens_wooldridge_2023_clustering.md` | when and at what level to cluster |
| `mackinnon_nielsen_webb_2023_few_clusters.md` | few or unequal clusters (Stata commands; R equivalents in `clubSandwich`, `fwildclusterboot`) |
| `gelman_hullman_kennedy_2024_causal_quartets.md` | average effects that hide heterogeneity |
| `fu_slough_2026_hte_mechanisms.md` | reading mechanisms from effect heterogeneity |
| `olken_2015_preanalysis.md` | what a pre-analysis plan pins down; reading deviations |
| `tosh_etal_2025_piranha.md` | many large effects on one outcome cannot all be true |

To update them, copy the newer versions from upstream and record the version in
`../../../UPSTREAM.md`.
