# recompute.R -- helpers for the review's arithmetic checks and recomputations.
#
# Source it from a job script:  source("<dkf-review skill>/assets/recompute.R")
# Base R and `stats` only. Every function returns plain numbers or a named list, so a
# script can print it to its log and write it to analysis/document/arithmetic-checks.csv.
#
# Tested by scripts/tests/test_recompute.R.

# ---- Agreement with a printed value ----------------------------------------------

# The first number in a printed string, as text: handles "12.30%", "−0.20" (Unicode
# minus), "1,234", "0.57 (95% CI ...)", "12 weeks".
number_token <- function(printed) {
  s <- gsub("−", "-", as.character(printed))   # Unicode minus sign
  s <- gsub("(?<=[0-9]),(?=[0-9]{3})", "", s, perl = TRUE)
  m <- regmatches(s, regexpr("-?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?", s))
  if (length(m) == 0) NA_character_ else m
}

parse_printed <- function(printed) as.numeric(number_token(printed))

# Number of decimals in a printed number given as text ("12.30" -> 2, "84" -> 0).
printed_decimals <- function(printed) {
  s <- number_token(printed)
  if (is.na(s) || !grepl("\\.", s)) return(0L)
  nchar(sub("[eE].*$", "", sub("^[^.]*\\.", "", s)))
}

# Round half away from zero (SAS, Excel), as opposed to R's round half to even.
round_half_up <- function(x, digits = 0) {
  m <- 10^digits
  sign(x) * floor(abs(x) * m + 0.5 + 1e-9) / m
}

# Compare a printed value (text, so its decimals are known) with a computed one.
# "match": equal within tolerance; "rounding": equal after rounding the computed
# value to the printed precision (either rounding rule); "mismatch" otherwise.
agree <- function(printed, computed, tol = 1e-9) {
  p <- parse_printed(printed)
  if (is.na(p) || is.na(computed)) return(NA_character_)
  if (abs(p - computed) <= tol * max(1, abs(p))) return("match")
  d <- printed_decimals(printed)
  if (isTRUE(all.equal(p, round(computed, d))) ||
      isTRUE(all.equal(p, round_half_up(computed, d)))) return("rounding")
  "mismatch"
}

# ---- Counts, percentages, totals --------------------------------------------------

pct <- function(n, N) 100 * n / N

# Does a printed percentage match n / N at its printed precision?
check_pct <- function(printed, n, N) agree(printed, pct(n, N))

# Do the parts add up to the printed total?
check_sum <- function(parts, total) {
  s <- sum(parts)
  list(sum = s, total = total, result = if (isTRUE(all.equal(s, total))) "match" else "mismatch")
}

# GRIM: is a reported mean of integer data attainable with n records of `items` items?
# Pass the mean as printed text so its decimals are known ("2.47"). Only meaningful
# when the grain 1 / (n * items) is coarser than the printed precision.
grim_ok <- function(mean, n, items = 1, digits = NULL) {
  if (is.null(digits)) digits <- printed_decimals(mean)
  m <- parse_printed(mean)
  grain <- n * items
  k <- round(m * grain) + (-2:2)
  any(abs(round(k / grain, digits) - m) < 1e-9 |
        abs(round_half_up(k / grain, digits) - m) < 1e-9)
}

# ---- Intervals and p-values ---------------------------------------------------------

# Standard error implied by a symmetric interval (on the log scale for ratios).
se_from_ci <- function(lo, hi, ratio = FALSE, level = 0.95) {
  z <- qnorm(1 - (1 - level) / 2)
  if (ratio) (log(hi) - log(lo)) / (2 * z) else (hi - lo) / (2 * z)
}

# Two-sided p-value from an estimate and its interval (Altman and Bland 2011),
# using the exact normal tail rather than their approximation.
p_from_ci <- function(est, lo, hi, ratio = FALSE, level = 0.95) {
  se <- se_from_ci(lo, hi, ratio, level)
  z <- if (ratio) log(est) / se else est / se
  2 * pnorm(-abs(z))
}

# Interval from an estimate and its two-sided p-value (Altman and Bland 2011).
ci_from_p <- function(est, p, ratio = FALSE, level = 0.95) {
  z <- qnorm(1 - p / 2)
  zc <- qnorm(1 - (1 - level) / 2)
  if (ratio) {
    se <- abs(log(est)) / z
    exp(log(est) + c(-1, 1) * zc * se)
  } else {
    se <- abs(est) / z
    est + c(-1, 1) * zc * se
  }
}

# Is the estimate at the centre of its interval on the scale the method implies?
# Returns the relative asymmetry (0 = symmetric).
ci_asymmetry <- function(est, lo, hi, ratio = FALSE) {
  if (ratio) { est <- log(est); lo <- log(lo); hi <- log(hi) }
  ((hi - est) - (est - lo)) / (hi - lo)
}

# Wilson score interval for one proportion.
wilson_ci <- function(x, n, level = 0.95) {
  z <- qnorm(1 - (1 - level) / 2)
  p <- x / n
  centre <- (p + z^2 / (2 * n)) / (1 + z^2 / n)
  half <- z * sqrt(p * (1 - p) / n + z^2 / (4 * n^2)) / (1 + z^2 / n)
  c(centre - half, centre + half)
}

# Risk difference p1 - p2 with a Newcombe hybrid score interval (method 10, 1998)
# or a Wald interval.
rd_ci <- function(x1, n1, x2, n2, method = c("newcombe", "wald"), level = 0.95) {
  method <- match.arg(method)
  p1 <- x1 / n1; p2 <- x2 / n2; d <- p1 - p2
  if (method == "wald") {
    z <- qnorm(1 - (1 - level) / 2)
    se <- sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return(c(est = d, lo = d - z * se, hi = d + z * se))
  }
  w1 <- wilson_ci(x1, n1, level); w2 <- wilson_ci(x2, n2, level)
  lo <- d - sqrt((p1 - w1[1])^2 + (w2[2] - p2)^2)
  hi <- d + sqrt((w1[2] - p1)^2 + (p2 - w2[1])^2)
  c(est = d, lo = lo, hi = hi)
}

# Risk ratio and odds ratio with Wald intervals on the log scale.
rr_ci <- function(x1, n1, x2, n2, level = 0.95) {
  z <- qnorm(1 - (1 - level) / 2)
  rr <- (x1 / n1) / (x2 / n2)
  se <- sqrt(1 / x1 - 1 / n1 + 1 / x2 - 1 / n2)
  c(est = rr, lo = exp(log(rr) - z * se), hi = exp(log(rr) + z * se))
}

or_ci <- function(x1, n1, x2, n2, level = 0.95) {
  z <- qnorm(1 - (1 - level) / 2)
  a <- x1; b <- n1 - x1; c <- x2; d <- n2 - x2
  or <- (a * d) / (b * c)
  se <- sqrt(1 / a + 1 / b + 1 / c + 1 / d)
  c(est = or, lo = exp(log(or) - z * se), hi = exp(log(or) + z * se))
}

# ---- Sample size building blocks --------------------------------------------------

# Randomised N from evaluable N and the share d without an evaluable endpoint.
# "divide" (N / (1 - d)) is the usual convention; "multiply" (N * (1 + d))
# under-inflates and is given only to reproduce a product that used it.
inflate_dropout <- function(n, d, method = c("divide", "multiply")) {
  method <- match.arg(method)
  if (method == "divide") n / (1 - d) else n * (1 + d)
}

round_up_to <- function(n, multiple) ceiling(n / multiple) * multiple

# Per-arm N for a difference in means, normal approximation with a t correction
# (one iteration), allocation ratio k = n2 / n1.
n_two_means <- function(delta, sd, alpha = 0.05, power = 0.8, k = 1, sided = 2) {
  za <- qnorm(1 - alpha / sided); zb <- qnorm(power)
  n1 <- (1 + 1 / k) * sd^2 * (za + zb)^2 / delta^2
  df <- n1 * (1 + k) - 2
  ta <- qt(1 - alpha / sided, df); tb <- qt(power, df)
  n1 <- (1 + 1 / k) * sd^2 * (ta + tb)^2 / delta^2
  c(n1 = n1, n2 = k * n1)
}

# Per-arm N for two proportions (Fleiss), optionally with a continuity correction.
n_two_props <- function(p1, p2, alpha = 0.05, power = 0.8, k = 1, sided = 2,
                        correct = FALSE) {
  za <- qnorm(1 - alpha / sided); zb <- qnorm(power)
  pbar <- (p1 + k * p2) / (1 + k); d <- abs(p1 - p2)
  n1 <- (za * sqrt(pbar * (1 - pbar) * (1 + 1 / k)) +
           zb * sqrt(p1 * (1 - p1) + p2 * (1 - p2) / k))^2 / d^2
  if (correct) n1 <- n1 / 4 * (1 + sqrt(1 + 2 * (1 + 1 / k) / (n1 * d)))^2
  c(n1 = n1, n2 = k * n1)
}

# Required number of events for a log-rank / Cox comparison (Schoenfeld 1983);
# `alloc` is the proportion allocated to one arm.
events_schoenfeld <- function(hr, alpha = 0.05, power = 0.8, alloc = 0.5, sided = 2) {
  za <- qnorm(1 - alpha / sided); zb <- qnorm(power)
  (za + zb)^2 / (alloc * (1 - alloc) * log(hr)^2)
}

# Exponential hazard from a survival proportion S at time t, and the event
# probability over a follow-up window.
hazard_from_surv <- function(S, t) -log(S) / t
event_prob <- function(hazard, t) 1 - exp(-hazard * t)

# Design effect for cluster sizes with mean m and coefficient of variation cv.
design_effect <- function(m, icc, cv = 0) 1 + ((cv^2 + 1) * m - 1) * icc

# ---- Monte Carlo ------------------------------------------------------------------

mcse_prop <- function(p, R) sqrt(p * (1 - p) / R)

# N at which a fitted power curve crosses `target`. `n` is the grid, `rejections`
# the number of replicates rejecting at each grid point, `R` replicates per point.
# Fits a binomial GLM of power on log(n); returns the crossing and, for reference,
# the first grid point whose simulated power reaches the target.
power_curve_crossing <- function(n, rejections, R, target = 0.8,
                                 link = c("logit", "probit")) {
  link <- match.arg(link)
  R <- rep_len(R, length(n))
  fit <- suppressWarnings(glm(cbind(rejections, R - rejections) ~ log(n),
                              family = binomial(link = link)))
  b <- coef(fit)
  eta <- if (link == "logit") qlogis(target) else qnorm(target)
  crossing <- exp((eta - b[[1]]) / b[[2]])
  simulated <- rejections / R
  first_grid <- if (any(simulated >= target)) min(n[simulated >= target]) else NA_real_
  list(crossing = crossing, first_grid_reaching_target = first_grid,
       coef = b, deviance = deviance(fit), df = df.residual(fit))
}
