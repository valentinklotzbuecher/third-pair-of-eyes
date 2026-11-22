# Tests for assets/make_codebook.R and assets/synthesize.R.
# Run: Rscript scripts/tests/test_synthetic.R   (from the stats-synthetic-data skill folder)

args <- commandArgs(trailingOnly = TRUE)
assets <- if (length(args)) args[[1]] else "assets"
source(file.path(assets, "make_codebook.R"))
source(file.path(assets, "synthesize.R"))

failures <- 0L
check <- function(desc, cond) {
  if (isTRUE(cond)) cat("ok   ", desc, "\n") else {
    cat("FAIL ", desc, "\n"); failures <<- failures + 1L
  }
}

set.seed(1)
tmp <- tempfile("synth"); dir.create(tmp)

# ---- codebook from a fake "real" dataset -------------------------------------------
n <- 120
real <- data.frame(
  patient_id = sprintf("P-%04d", sample(1000:9999, n)),
  arm = sample(c("NIR", "Placebo"), n, replace = TRUE),
  centre = sample(c("Basel", "Bern", "Zurich", "Rare1", "Rare2"), n, replace = TRUE,
                  prob = c(.45, .3, .21, .02, .02)),
  age = round(rnorm(n, 62, 11)),
  score = round(runif(n, 0, 2), 2),
  rand_date = as.Date("2026-01-15") + sample(0:300, n, replace = TRUE),
  comment = paste("free text", sample(1e6, n)),
  stringsAsFactors = FALSE)
real$score[sample(n, 3)] <- NA          # rare missingness (< 5)
real$age[sample(n, 30)] <- NA           # 25% missing
attr(real$age, "label") <- "Age at randomisation (years)"
cb <- make_codebook(list(baseline = real), id_vars = "patient_id", k = 5)
c1 <- cb$codebook
row <- function(v) c1[c1$variable == v, ]
check("codebook has one row per variable", nrow(c1) == ncol(real))
check("identifier gives a format, no values",
      row("patient_id")$type == "id" && !grepl("P-[0-9]{4}", row("patient_id")$note))
check("free text gives no values", row("comment")$type == "text" &&
        row("comment")$levels == "" && row("comment")$min == "")
cent <- row("centre")
check("rare levels pooled and not named", cent$n_rare_levels >= 1 &&
        !grepl("Rare", cent$levels))
props <- as.numeric(sub("^.*=", "", strsplit(cent$levels, " | ", fixed = TRUE)[[1]]))
check("common levels named with proportions rounded to 0.05",
      grepl("Basel=0\\.[0-9]{2}", cent$levels) && all(abs(props * 20 - round(props * 20)) < 1e-9))
check("numeric range rounded outward",
      as.numeric(row("age")$min) <= min(real$age, na.rm = TRUE) &&
        as.numeric(row("age")$max) >= max(real$age, na.rm = TRUE))
check("missingness rounded to 0.05", row("age")$p_missing == "0.25")
check("rare missingness reported as rare", row("score")$p_missing == "rare")
check("label kept", row("age")$label == "Age at randomisation (years)")
check("dates at month resolution", grepl("^\\d{4}-\\d{2}$", row("rand_date")$min))
check("structure rounds rows to 10", cb$structure$n_rows == 120 && cb$structure$n_ids == 120)
files <- write_codebook(cb, file.path(tmp, "codebook"))
check("codebook files written", all(file.exists(files)))
txt <- paste(readLines(files[1]), collapse = "\n")
check("no identifier value in the written codebook", !any(vapply(real$patient_id, grepl, logical(1), x = txt, fixed = TRUE)))
check("no free-text value in the written codebook", !grepl("free text [0-9]", txt))

# ---- contract -> synthetic data -----------------------------------------------------
contract <- data.frame(
  dataset = "baseline",
  variable = c("patient_id", "arm", "centre", "age", "score", "rand_date"),
  type = c("id", "factor", "factor", "integer", "double", "date"),
  levels = c(NA, "NIR=0.5 | Placebo=0.5", "Basel | Bern | Zurich", NA, NA, NA),
  unit = NA, min = c(NA, NA, NA, "18", "0", "2026-01"), max = c(NA, NA, NA, "90", "2", "2026-12"),
  missing_codes = NA, p_missing = c(0, 0, 0, 0.1, 0, 0),
  role = c("id", "arm", "centre", "covariate", "outcome", "other"),
  source = "test", stringsAsFactors = FALSE)
cpath <- file.path(tmp, "contract.csv")
utils::write.csv(contract, cpath, row.names = FALSE, na = "")
ct <- read_contract(cpath)
set.seed(2)
base <- synth_dataset(ct, "baseline", n = 400)
check("synthetic rows", nrow(base) == 400)
check("ids unique and synthetic", !anyDuplicated(base$patient_id) && all(grepl("^SYN-", base$patient_id)))
check("factor levels from contract", identical(levels(base$centre), c("Basel", "Bern", "Zurich")))
check("integer within range", all(base$age[!is.na(base$age)] >= 18 & base$age[!is.na(base$age)] <= 90))
check("dates within month bounds", min(base$rand_date) >= as.Date("2026-01-01") &&
        max(base$rand_date) <= as.Date("2026-12-31"))
chk <- check_contract(base, ct, "baseline")
check("generated data pass the contract check", all(chk$ok))
bad <- base; bad$age[1] <- 150; bad$centre <- factor(as.character(bad$centre), levels = c(levels(bad$centre), "Geneva")); bad$centre[2] <- "Geneva"
chk2 <- check_contract(bad, ct, "baseline")
check("contract check catches out-of-range and unknown levels",
      !chk2$ok[chk2$variable == "age" & chk2$check == "range"] &&
        !chk2$ok[chk2$variable == "centre" & chk2$check == "levels within contract"])

# repeated measures
ctv <- rbind(contract[contract$variable %in% c("patient_id", "arm"), ],
             data.frame(dataset = "baseline", variable = "visit", type = "factor",
                        levels = "W0 | W4 | W12", unit = NA, min = NA, max = NA,
                        missing_codes = NA, p_missing = 0, role = "visit", source = "test"))
vis <- synth_dataset(ctv, "baseline", n = 10, grain = "visit")
check("visit grain expands ids by visits", nrow(vis) == 30 && all(table(vis$patient_id) == 3))

# ---- known truth -------------------------------------------------------------------
set.seed(3)
est <- replicate(200, {
  d <- synth_dataset(ct, "baseline", n = 200)
  d <- plant_effect(d, "score", "arm", "NIR", effect = -0.2, sd = 0.5)
  unname(coef(lm(score ~ arm, data = d))[2])
})
# arm levels NIR, Placebo -> coefficient is Placebo - NIR = +0.2
check("planted mean difference recovered", abs(mean(est) - 0.2) < 0.02)
set.seed(4)
d <- synth_dataset(ct, "baseline", n = 4000)
d <- plant_effect(d, "score", "arm", "NIR", effect = log(2), scale = "logit", p0 = 0.3)
fit <- glm(score ~ relevel(arm, "Placebo"), family = binomial, data = d)
check("planted log odds ratio recovered", abs(coef(fit)[2] - log(2)) < 0.15)
d <- plant_tte(d, "time", "event", "arm", "NIR", hr = 0.6, rate0 = 1 / 300, followup = 304)
if (requireNamespace("survival", quietly = TRUE)) {
  cf <- survival::coxph(survival::Surv(time, event) ~ relevel(arm, "Placebo"), data = d)
  check("planted hazard ratio recovered", abs(exp(coef(cf)) - 0.6) < 0.06)
}
check("administrative censoring at follow-up", max(d$time) <= 304)
d2 <- plant_missing(d, "age", p = 0.3, mechanism = "MAR", depends_on = "score", strength = 1)
check("MAR missingness hits the target share", abs(mean(is.na(d2$age)) - (0.3 + 0.1 * 0.7)) < 0.05 ||
        abs(mean(is.na(d2$age)) - 0.3) < 0.06)

# ---- edge cases ---------------------------------------------------------------------
set.seed(5)
e <- edge_cases(base, ct, "baseline", outcome = "score", id = "patient_id")
check("edge cases listed", nrow(e$expectations) >= 4)
check("expectations left for the generator to state", all(e$expectations$expected_effect == ""))
check("duplicated id planted", anyDuplicated(e$data$patient_id) > 0)
check("missing outcome planted", sum(is.na(e$data$score)) >= 2)

# ---- symbols in code ----------------------------------------------------------------
qmd <- file.path(tmp, "x.qmd")
writeLines(c("---", "title: x", "---", "```{r}", "#| label: a",
             "d <- readRDS('dat/x.rds')", "d$bmi <- d$weight / d$height^2",
             "fit <- lm(score ~ arm + age, data = d)", "```"), qmd)
s <- symbols_in_code(qmd)
check("symbols include formula and $ names", all(c("score", "arm", "age", "weight", "height") %in% s$name))
check("assigned objects excluded", !any(c("d", "fit") %in% s$name))

cat(if (failures == 0L) "PASS\n" else sprintf("%d FAILED\n", failures))
quit(status = if (failures == 0L) 0L else 1L)
