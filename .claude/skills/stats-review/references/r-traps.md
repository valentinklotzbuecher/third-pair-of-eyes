# R defaults that silently change a statistic

Defaults and behaviours that make R compute something other than what the text
describes, or something another package or SAS would compute differently. Each was
checked on R 4.3 with `survival` 3.5 and `rpact` 3.4; check the product's own versions
when a finding rests on one. A hit is a lead: it becomes a finding when its effect on a
printed number, or on what a reader understands, has been run.

## Tests and intervals

| Call | Default | Why it matters |
|---|---|---|
| `chisq.test()` | `correct = TRUE` (Yates continuity correction for 2 × 2 tables) | conservative p-values; differs from an uncorrected test named in the text |
| `prop.test()` | `correct = TRUE`; interval is Wilson with continuity correction | differs from a Wald interval or an exact one |
| `power.prop.test()` | normal approximation, no continuity correction, no `correct` argument | a sample size from `power.prop.test()` with a planned `prop.test()` or `chisq.test()` analysis (corrected) overstates the power actually achieved |
| `binom.test()` | exact (Clopper–Pearson) interval | wider than Wilson; name which one the text means |
| `t.test()` | `var.equal = FALSE` (Welch) | the text may say "t-test" meaning the pooled test |
| `power.t.test()` | `sd = 1`, `strict = FALSE` (ignores the far tail) | a forgotten `sd` silently treats the difference as standardised |
| `wilcox.test()` | `exact = NULL` (exact for small samples without ties), `correct = TRUE` | p-values change with ties and sample size; no estimate of a location shift without `conf.int = TRUE` |
| `p.adjust()` | `method = "holm"` | the text may say Bonferroni |
| `confint()` on `glm` | profile-likelihood intervals | `confint.default()` gives Wald intervals; SAS defaults to Wald; they differ in small samples |
| `quantile()` | `type = 7` | SAS (`PCTLDEF = 5`) and other software give different quartiles and medians of small samples |
| `cor()` | `use = "everything"` | one `NA` makes the result `NA`; `"complete.obs"` and `"pairwise.complete.obs"` use different rows |

## Models

| Call | Default | Why it matters |
|---|---|---|
| `anova()` on `lm`/`glm` | sequential (type I) sums of squares | a covariate's test depends on its position in the formula; `car::Anova()` gives type II/III |
| `glm()` | `family = gaussian` | a forgotten `family` fits a linear model to a binary outcome |
| factor reference level | first level in alphabetical (or locale) order | the coefficient's comparison may not be the one the table labels |
| `as.numeric(factor)` | returns the level codes | a numeric variable stored as a factor becomes 1, 2, 3 |
| `coxph()` | `ties = "efron"` | SAS PROC PHREG defaults to Breslow; estimates differ with many ties |
| `survdiff()` | `rho = 0` (log-rank) | the text may name a weighted test |
| `lme4::lmer()` | `REML = TRUE`; no p-values | `lmerTest` adds Satterthwaite degrees of freedom; `emmeans` picks Kenward–Roger, Satterthwaite or asymptotic depending on what is installed and on data-size limits (`pbkrtest.limit`, `lmerTest.limit`); the product should state the method |
| `mice::mice()` | `m = 5`, `maxit = 5`; method by variable type | five imputations is often too few (`../modules/missing-data-diagnostics/`) |
| `predict()` on `glm` | `type = "link"` | log-odds where the text reports probabilities |

## Survival design and summaries

| Call | Default | Why it matters |
|---|---|---|
| `rpact::getSampleSizeSurvival()`, `getPowerSurvival()` | `eventTime = 12`, `dropoutTime = 12`, `accrualTime = c(0, 12)` | event probabilities (`pi1`, `pi2`) are read at `eventTime` and dropout rates at `dropoutTime`, in the same time unit as accrual and follow-up; mixing days and months, or leaving the defaults for an endpoint whose horizon is not 12 units, changes the design without an error |
| `survfit()` | `conf.type = "log"` | other software defaults to log–log; intervals differ near 0 and 1 |
| `summary(survfit, times = )` | `extend = FALSE` | requested times beyond the last observation are dropped silently, so a "survival at 24 months" row can vanish |
| median follow-up | not a default: computed by hand | the median of observed times understates follow-up; use the reverse Kaplan–Meier |

## Data handling

| Behaviour | Why it matters |
|---|---|
| `table()` has `useNA = "no"` | missing values vanish from counts and denominators |
| `mean()`, `sum()`, `sd()` have `na.rm = FALSE` | one `NA` gives `NA`; code that sets `na.rm = TRUE` everywhere changes the denominator silently |
| `dplyr::filter()` drops rows where the condition is `NA` | a filter on a variable with missing values removes those participants |
| `merge()` has `all = FALSE` (inner join) | unmatched participants disappear; `dplyr` joins duplicate rows on many-to-many matches |
| `cut()` has `right = TRUE`, `include.lowest = FALSE` | a value equal to the lowest break becomes `NA`; boundary values fall into the lower class |
| `ifelse()` drops attributes | dates become numbers |
| `difftime()` with `units = "auto"` | for date-times, the unit depends on the size of the difference; set `units` before `as.numeric()` |
| `round()` rounds halves to even, and decimal halves depend on floating-point representation | `round(2.5)` is 2 and `round(0.15, 1)` is 0.1; SAS and Excel round halves up, so reported numbers can differ in the last digit |
| `sprintf("%.1f", 0.25)` gives `"0.2"` | formatting rounds the same way; tables built with `sprintf()` or `format()` inherit it |
| `sample()` on a single number `n` samples from `1:n` | a resampling loop over a vector that has shrunk to length one changes meaning |
| `set.seed()` sample kind changed in R 3.6.0 | code written for R < 3.6 reproduces only with `RNGkind(sample.kind = "Rounding")` |
