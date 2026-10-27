# Tests for assets/recompute.R. Run: Rscript scripts/tests/test_recompute.R
# (from the dkf-review skill directory, or with the path to recompute.R as argument).

args <- commandArgs(trailingOnly = TRUE)
here <- if (length(args)) args[[1]] else "assets/recompute.R"
source(here)

failures <- 0L
check <- function(desc, cond) {
  if (isTRUE(cond)) cat("ok   ", desc, "\n") else {
    cat("FAIL ", desc, "\n"); failures <<- failures + 1L
  }
}
near <- function(a, b, tol = 1e-6) isTRUE(all.equal(unname(a), unname(b), tolerance = tol))

# printed values
check("number_token handles percent", number_token("12.30%") == "12.30")
check("number_token handles Unicode minus", parse_printed("−0.20") == -0.20)
check("number_token handles thousands separator", parse_printed("1,234") == 1234)
check("number_token ignores units", parse_printed("12 weeks") == 12)
check("printed_decimals 2", printed_decimals("12.30") == 2)
check("printed_decimals 0", printed_decimals("84") == 0)
check("round_half_up 2.5 -> 3", round_half_up(2.5) == 3)
check("round_half_up -2.5 -> -3", round_half_up(-2.5) == -3)
check("round_half_up 0.125, 2 -> 0.13", near(round_half_up(0.125, 2), 0.13))

# agreement
check("agree exact", agree("0.5", 0.5) == "match")
check("agree rounding", agree("33.3", 100 / 3) == "rounding")
check("agree rounding half up (R rounds 2.5 to 2)", agree("3", 2.5) == "rounding")
check("agree mismatch", agree("33.4", 100 / 3) == "mismatch")
check("check_pct 17/51 = 33.3%", check_pct("33.3%", 17, 51) == "rounding")
check("check_sum mismatch", check_sum(c(10, 5, 30), 50)$result == "mismatch")
check("check_sum match", check_sum(c(10, 5, 30, 30, 5, 5, 15), 100)$result == "match")

# GRIM: n = 10 integers, mean printed to 2 decimals -> must be a multiple of 0.1
check("grim attainable 2.40 with n = 10", grim_ok("2.40", 10))
check("grim not attainable 2.47 with n = 10", !grim_ok("2.47", 10))
check("grim attainable 2.47 with n = 15 (37/15 = 2.4667)", grim_ok("2.47", 15))

# intervals and p-values
se <- se_from_ci(-1.96, 1.96)
check("se_from_ci symmetric", near(se, 1, 1e-3))
check("p_from_ci est 1.96 se 1 gives 0.05",
      near(p_from_ci(1.96, 1.96 - 1.96, 1.96 + 1.96), 0.05, 1e-3))
ci <- ci_from_p(0.7, p_from_ci(0.7, 0.5, 0.98, ratio = TRUE), ratio = TRUE)
check("ci_from_p inverts p_from_ci on ratio scale", near(ci, c(0.5, 0.98), 1e-6))
check("ci_asymmetry zero on log scale", abs(ci_asymmetry(2, 1, 4, ratio = TRUE)) < 1e-12)
check("ci_asymmetry nonzero on linear scale", abs(ci_asymmetry(2, 1, 4)) > 0.1)

# Wilson against prop.test without continuity correction
w <- wilson_ci(7, 20)
pt <- suppressWarnings(prop.test(7, 20, correct = FALSE))$conf.int
check("wilson_ci equals prop.test(correct = FALSE)", near(w, as.numeric(pt), 1e-8))

# Newcombe hybrid score interval: worked example from Newcombe (1998), method 10,
# 56/70 vs 48/80: difference 0.2000, 95% CI 0.0524 to 0.3339.
rd <- rd_ci(56, 70, 48, 80)
check("rd_ci Newcombe example lower", near(rd[["lo"]], 0.0524, 1e-3))
check("rd_ci Newcombe example upper", near(rd[["hi"]], 0.3339, 1e-3))

rr <- rr_ci(20, 100, 10, 100)
check("rr_ci estimate", near(rr[["est"]], 2))
or <- or_ci(20, 100, 10, 100)
check("or_ci estimate", near(or[["est"]], (20 * 90) / (80 * 10)))

# sample size building blocks
check("inflate divide 84, 0.1 -> 93.33", near(inflate_dropout(84, 0.1), 93.333333, 1e-6))
check("inflate multiply 84, 0.1 -> 92.4", near(inflate_dropout(84, 0.1, "multiply"), 92.4))
check("round_up_to 94 by 10 -> 100", round_up_to(94, 10) == 100)
check("round_up_to 93.3 by 4 -> 96", round_up_to(93.3, 4) == 96)

pp <- power.prop.test(p1 = 0.40, p2 = 0.57, power = 0.8)$n
np <- n_two_props(0.40, 0.57)[["n1"]]
check("n_two_props equals power.prop.test", near(np, pp, 1e-4))

pm <- power.t.test(delta = 0.5, sd = 1, power = 0.8)$n
nm <- n_two_means(0.5, 1)[["n1"]]
check("n_two_means within 0.5 of power.t.test", abs(nm - pm) < 0.5)

# Schoenfeld: HR 0.7, alpha 0.05, power 0.8, 1:1 -> 247 events (rounded up)
check("events_schoenfeld HR 0.7 -> 247", ceiling(events_schoenfeld(0.7)) == 247)

h <- hazard_from_surv(0.40, 304)
check("event_prob at the same horizon recovers 1 - S", near(event_prob(h, 304), 0.60))
check("design_effect m = 20, icc = 0.05 -> 1.95", near(design_effect(20, 0.05), 1.95))
check("design_effect with cv inflates", design_effect(20, 0.05, cv = 0.5) > 1.95)

check("mcse 0.8 at 5000 -> 0.00566", near(mcse_prop(0.8, 5000), 0.005657, 1e-3))

# power curve: true power from a logistic curve, many replicates -> crossing near truth
set.seed(1)
n <- seq(60, 120, by = 6)
true_p <- plogis(-9 + 2.4 * log(n))
R <- 5000
rej <- rbinom(length(n), R, true_p)
pc <- power_curve_crossing(n, rej, R, target = 0.8)
truth <- exp((qlogis(0.8) + 9) / 2.4)
check("power_curve_crossing within 2% of truth", abs(pc$crossing / truth - 1) < 0.02)
check("power_curve_crossing reports first grid point", !is.na(pc$first_grid_reaching_target))

cat(if (failures == 0L) "PASS\n" else sprintf("%d FAILED\n", failures))
quit(status = if (failures == 0L) 0L else 1L)
