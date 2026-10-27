# synthesize.R -- generate synthetic data from a data contract, plant edge cases and
# known effects, and check generated data against the contract. Base R only.
#
#   source("<dkf-synthetic-data skill>/assets/synthesize.R")
#   contract  <- read_contract("work/synthetic/contract.csv")
#   structure <- read_structure("work/synthetic/structure.csv")
#   set.seed(20261027)
#   base <- synth_dataset(contract, "baseline", n = 100)
#   chk  <- check_contract(base, contract, "baseline")
#
# Contract columns (work/synthetic/contract.csv):
#   dataset, variable, type, levels, unit, min, max, missing_codes, p_missing, role, source
# type: id, integer, double, factor, ordered, logical, character, date, datetime
# levels: "A | B | C", optionally with proportions "A=0.40 | B=0.35 | C=0.25"
# role: id, arm, stratum, centre, outcome, covariate, time, event, visit, other
# Tested by scripts/tests/test_synthetic.R.

read_contract <- function(path) {
  ct <- utils::read.csv(path, stringsAsFactors = FALSE, na.strings = c("", "NA"),
                        check.names = FALSE)
  need <- c("dataset", "variable", "type")
  miss <- setdiff(need, names(ct))
  if (length(miss)) stop("contract lacks columns: ", paste(miss, collapse = ", "))
  for (col in c("levels", "unit", "min", "max", "missing_codes", "p_missing", "role", "source"))
    if (!col %in% names(ct)) ct[[col]] <- NA
  ct
}

read_structure <- function(path) utils::read.csv(path, stringsAsFactors = FALSE,
                                                 na.strings = c("", "NA"))

# "A=0.4 | B | C=0.25" -> list(levels = c("A","B","C"), prob = c(.4, NA, .25))
parse_levels <- function(s) {
  if (is.null(s) || is.na(s) || !nzchar(trimws(s))) return(list(levels = character(), prob = numeric()))
  parts <- trimws(strsplit(s, "|", fixed = TRUE)[[1]])
  parts <- parts[nzchar(parts)]
  lev <- sub("=[0-9.]+$", "", parts)
  prob <- suppressWarnings(as.numeric(ifelse(grepl("=[0-9.]+$", parts),
                                             sub("^.*=", "", parts), NA)))
  list(levels = trimws(lev), prob = prob)
}

fill_prob <- function(prob, k) {
  if (!length(prob) || all(is.na(prob))) return(rep(1 / k, k))
  rest <- max(0, 1 - sum(prob, na.rm = TRUE))
  prob[is.na(prob)] <- if (any(is.na(prob))) rest / sum(is.na(prob)) else 0
  if (sum(prob) <= 0) return(rep(1 / k, k))
  prob / sum(prob)
}

num_or <- function(x, default) {
  v <- suppressWarnings(as.numeric(x))
  if (length(v) == 0 || is.na(v)) default else v
}

as_date_bound <- function(x, end = FALSE) {
  if (is.null(x) || is.na(x) || !nzchar(x)) return(NA)
  x <- trimws(as.character(x))
  if (grepl("^\\d{4}-\\d{2}$", x)) {
    d <- as.Date(paste0(x, "-01"))
    if (end) d <- seq(d, by = "1 month", length.out = 2)[2] - 1
    return(d)
  }
  as.Date(x)
}

# One variable of length n from a contract row.
synth_variable <- function(row, n) {
  type <- tolower(row$type)
  lv <- parse_levels(row$levels)
  x <- switch(type,
    id = sprintf("SYN-%05d", seq_len(n)),
    integer = {
      lo <- num_or(row$min, 0); hi <- num_or(row$max, max(lo + 10, 10))
      as.integer(round(stats::runif(n, lo - 0.5, hi + 0.5)))
    },
    double = {
      lo <- num_or(row$min, 0); hi <- num_or(row$max, lo + 1)
      stats::runif(n, lo, hi)
    },
    factor = , ordered = , character = {
      levs <- if (length(lv$levels)) lv$levels else c("A", "B")
      v <- sample(levs, n, replace = TRUE, prob = fill_prob(lv$prob, length(levs)))
      if (type == "character") v else factor(v, levels = levs, ordered = type == "ordered")
    },
    logical = {
      p <- num_or(lv$prob[match("TRUE", lv$levels)], 0.5)
      stats::runif(n) < p
    },
    date = , datetime = {
      lo <- as_date_bound(row$min); hi <- as_date_bound(row$max, end = TRUE)
      if (is.na(lo)) lo <- as.Date("2025-01-01")
      if (is.na(hi)) hi <- lo + 365
      d <- lo + floor(stats::runif(n, 0, as.numeric(hi - lo) + 1))
      if (type == "datetime") as.POSIXct(d) + stats::runif(n, 0, 86399) else d
    },
    stop("unknown contract type '", row$type, "' for ", row$variable))
  # integers: clamp after rounding
  if (type == "integer" && !is.na(num_or(row$min, NA))) x <- pmax(x, as.integer(num_or(row$min, NA)))
  if (type == "integer" && !is.na(num_or(row$max, NA))) x <- pmin(x, as.integer(num_or(row$max, NA)))
  pm <- num_or(row$p_missing, 0)
  if (type != "id" && pm > 0) x[stats::runif(n) < pm] <- NA
  x
}

# A dataset from the contract. grain = "participant" (n rows) or "visit" (n ids times
# the levels of the variable with role `visit`); ids are shared across datasets when
# `ids` is given.
synth_dataset <- function(contract, dataset, n, grain = c("participant", "visit"), ids = NULL) {
  grain <- match.arg(grain)
  rows <- contract[contract$dataset == dataset, , drop = FALSE]
  if (!nrow(rows)) stop("no contract rows for dataset ", dataset)
  idrow <- rows[tolower(rows$type) == "id" | (!is.na(rows$role) & rows$role == "id"), , drop = FALSE]
  if (is.null(ids)) ids <- sprintf("SYN-%05d", seq_len(n))
  if (grain == "visit") {
    vrow <- rows[!is.na(rows$role) & rows$role == "visit", , drop = FALSE]
    if (!nrow(vrow)) stop("grain 'visit' needs a contract row with role 'visit'")
    visits <- parse_levels(vrow$levels[1])$levels
    frame <- expand.grid(.id = ids, .visit = visits, stringsAsFactors = FALSE)
    frame <- frame[order(match(frame$.id, ids)), ]
  } else {
    frame <- data.frame(.id = ids, stringsAsFactors = FALSE)
  }
  m <- nrow(frame)
  out <- list()
  for (i in seq_len(nrow(rows))) {
    r <- rows[i, ]
    if (nrow(idrow) && r$variable == idrow$variable[1]) { out[[r$variable]] <- frame$.id; next }
    if (grain == "visit" && !is.na(r$role) && r$role == "visit") {
      out[[r$variable]] <- if (tolower(r$type) %in% c("factor", "ordered"))
        factor(frame$.visit, levels = visits, ordered = tolower(r$type) == "ordered") else
        utils::type.convert(frame$.visit, as.is = TRUE)
      next
    }
    out[[r$variable]] <- synth_variable(r, m)
  }
  as.data.frame(out, stringsAsFactors = FALSE, optional = TRUE)
}

# Recompute the outcome so that the arm effect is known. scale "identity": outcome =
# baseline + effect in the treated arm (continuous); "logit": binary outcome with
# the given log-odds ratio around control probability p0; "log": counts with the given
# log rate ratio around control mean mu0.
plant_effect <- function(df, outcome, arm, treated, effect,
                         scale = c("identity", "logit", "log"),
                         p0 = 0.3, mu0 = 2, sd = 1, base = NULL) {
  scale <- match.arg(scale)
  t <- as.character(df[[arm]]) == as.character(treated)
  n <- nrow(df)
  df[[outcome]] <- switch(scale,
    identity = (if (is.null(base)) stats::rnorm(n, 0, sd) else base) + effect * t,
    logit = as.integer(stats::runif(n) < stats::plogis(stats::qlogis(p0) + effect * t)),
    log = stats::rpois(n, mu0 * exp(effect * t)))
  df
}

# Exponential event times with a hazard ratio, administrative censoring at `followup`.
plant_tte <- function(df, time, event, arm, treated, hr, rate0, followup) {
  t <- as.character(df[[arm]]) == as.character(treated)
  tt <- stats::rexp(nrow(df), rate = rate0 * ifelse(t, hr, 1))
  df[[event]] <- as.integer(tt <= followup)
  df[[time]] <- pmin(tt, followup)
  df
}

# Set values of `var` to NA: MCAR with probability p, or MAR with log-odds of
# missingness increasing by `strength` per SD of `depends_on`.
plant_missing <- function(df, var, p, mechanism = c("MCAR", "MAR"), depends_on = NULL,
                          strength = 1) {
  mechanism <- match.arg(mechanism)
  n <- nrow(df)
  if (mechanism == "MCAR") {
    miss <- stats::runif(n) < p
  } else {
    z <- as.numeric(df[[depends_on]])
    z <- (z - mean(z, na.rm = TRUE)) / stats::sd(z, na.rm = TRUE)
    z[is.na(z)] <- 0
    a <- stats::uniroot(function(a) mean(stats::plogis(a + strength * z)) - p, c(-20, 20))$root
    miss <- stats::runif(n) < stats::plogis(a + strength * z)
  }
  df[[var]][miss] <- NA
  attr(df, "planted_missing") <- c(attr(df, "planted_missing"), stats::setNames(sum(miss), var))
  df
}

# Edge cases for one dataset: returns the modified data and one row per planted case.
# `expected_effect` is left empty: the generator script states it, from the product's
# printed definitions, before the product's code runs.
edge_cases <- function(df, contract, dataset, outcome = NULL, id = NULL) {
  rows <- contract[contract$dataset == dataset, , drop = FALSE]
  cases <- list()
  add <- function(case, r, planted) cases[[length(cases) + 1]] <<-
    data.frame(case = case, dataset = dataset, rows = paste(r, collapse = ";"),
               planted = planted, expected_effect = "", stringsAsFactors = FALSE)
  n <- nrow(df)
  pick <- function(k) sample.int(n, min(k, n))
  if (!is.null(outcome) && outcome %in% names(df)) {
    r <- pick(2); df[[outcome]][r] <- NA
    add("missing outcome", r, sprintf("%s set to NA", outcome))
  }
  num <- rows[tolower(rows$type) %in% c("integer", "double") & !is.na(rows$min) &
                (is.na(rows$role) | rows$role != "outcome"), , drop = FALSE]
  if (nrow(num)) {
    v <- num$variable[1]; r <- pick(2)
    df[[v]][r[1]] <- num_or(num$min[1], 0)
    if (length(r) > 1 && !is.na(num_or(num$max[1], NA))) df[[v]][r[2]] <- num_or(num$max[1], NA)
    add("boundary values", r, sprintf("%s set to its contract min and max", v))
    r <- pick(1); df[[v]][r] <- NA
    add("missing covariate", r, sprintf("%s set to NA", v))
  }
  fac <- rows[tolower(rows$type) %in% c("factor", "ordered") & !is.na(rows$levels) &
                (is.na(rows$role) | !rows$role %in% c("arm", "visit")), , drop = FALSE]
  if (nrow(fac)) {
    v <- fac$variable[1]
    levs <- parse_levels(fac$levels[1])$levels
    if (length(levs) >= 3 && is.factor(df[[v]])) {
      absent <- levs[length(levs)]
      r <- which(as.character(df[[v]]) == absent)
      if (length(r)) df[[v]][r] <- levs[1]
      add("absent factor level", r, sprintf("no records with %s = %s", v, absent))
    }
  }
  if (!is.null(id) && id %in% names(df) && n >= 2) {
    df <- rbind(df, df[1, , drop = FALSE])
    add("duplicated identifier", nrow(df), sprintf("row 1 duplicated (%s %s)", id, df[[id]][1]))
  }
  list(data = df, expectations = do.call(rbind, cases))
}

# Re-derive types, levels, ranges and missingness from generated data and compare with
# the contract. Returns one row per check; `ok` FALSE marks a mismatch.
check_contract <- function(df, contract, dataset) {
  rows <- contract[contract$dataset == dataset, , drop = FALSE]
  out <- list()
  rec <- function(v, check, expected, observed, ok) out[[length(out) + 1]] <<-
    data.frame(variable = v, check = check, expected = as.character(expected),
               observed = as.character(observed), ok = ok, stringsAsFactors = FALSE)
  for (i in seq_len(nrow(rows))) {
    r <- rows[i, ]; v <- r$variable; type <- tolower(r$type)
    if (!v %in% names(df)) { rec(v, "present", "yes", "no", FALSE); next }
    x <- df[[v]]
    obs_type <- if (inherits(x, "Date")) "date" else if (inherits(x, "POSIXct")) "datetime" else
      if (is.ordered(x)) "ordered" else if (is.factor(x)) "factor" else if (is.logical(x)) "logical" else
      if (is.integer(x)) "integer" else if (is.numeric(x)) "double" else "character"
    want <- if (type == "id") c("character", "integer", "double") else
      if (type == "integer") c("integer", "double") else type
    rec(v, "type", type, obs_type, obs_type %in% want)
    if (type %in% c("factor", "ordered", "character")) {
      levs <- parse_levels(r$levels)$levels
      if (length(levs)) {
        extra <- setdiff(unique(as.character(x[!is.na(x)])), levs)
        rec(v, "levels within contract", paste(levs, collapse = "|"),
            paste(extra, collapse = "|"), length(extra) == 0)
      }
    }
    if (type %in% c("integer", "double")) {
      lo <- num_or(r$min, -Inf); hi <- num_or(r$max, Inf)
      xv <- x[!is.na(x)]
      if (length(xv)) rec(v, "range", sprintf("[%s, %s]", lo, hi),
                          sprintf("[%s, %s]", min(xv), max(xv)), min(xv) >= lo && max(xv) <= hi)
    }
    pm <- num_or(r$p_missing, 0)
    obs_pm <- mean(is.na(x))
    rec(v, "missing share", pm, round(obs_pm, 3),
        abs(obs_pm - pm) <= max(0.05, 3 * sqrt(max(pm * (1 - pm), 0.01) / length(x))))
  }
  do.call(rbind, out)
}

# Candidate column names in a Quarto/R source: symbols used as variables, names after
# `$`, strings inside `[[ ]]`, minus objects the code assigns. A starting list for the
# contract, not the contract.
symbols_in_code <- function(path) {
  lines <- readLines(path, warn = FALSE)
  if (grepl("\\.(qmd|rmd)$", tolower(path))) {
    inside <- FALSE; keep <- character()
    for (ln in lines) {
      if (!inside && grepl("^\\s*```+\\s*\\{r", ln)) { inside <- TRUE; next }
      if (inside && grepl("^\\s*```+\\s*$", ln)) { inside <- FALSE; next }
      if (inside && !grepl("^\\s*#\\|", ln)) keep <- c(keep, ln)
    }
    lines <- keep
  }
  pd <- utils::getParseData(parse(text = lines, keep.source = TRUE))
  pd <- pd[pd$terminal, , drop = FALSE]
  pd <- pd[order(pd$line1, pd$col1), , drop = FALSE]
  sym <- pd$text[pd$token == "SYMBOL"]
  dollar <- pd$text[pd$token == "SYMBOL" & c(FALSE, head(pd$token, -1) == "'$'")]
  assigned <- unique(c(
    pd$text[pd$token == "SYMBOL" & c(tail(pd$token, -1) %in% c("LEFT_ASSIGN", "EQ_ASSIGN"), FALSE)],
    pd$text[pd$token == "SYMBOL_FORMALS"]))
  strings <- gsub("^[\"']|[\"']$", "", pd$text[pd$token == "STR_CONST"])
  tab <- sort(table(setdiff(c(sym, dollar), assigned)), decreasing = TRUE)
  data.frame(name = names(tab), uses = as.integer(tab),
             after_dollar = names(tab) %in% dollar,
             also_a_string = names(tab) %in% strings, stringsAsFactors = FALSE)
}
