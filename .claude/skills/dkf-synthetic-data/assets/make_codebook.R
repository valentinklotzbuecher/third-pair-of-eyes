# make_codebook.R -- a disclosure-controlled codebook of an analysis dataset.
#
# For the statistician, to run LOCALLY on the real data, where the data are allowed to
# be. The codebook (not the data) can then be checked and handed to a review that runs
# in data mode `synthetic`, so the dummy data match the variable names, types, levels
# and structure the analysis code expects. Base R only.
#
#   source("make_codebook.R")
#   cb <- make_codebook(list(baseline = baseline_df, visits = visits_df),
#                       id_vars = "patient_id", k = 5)
#   write_codebook(cb, "codebook")    # codebook/codebook.csv, codebook/structure.csv
#
# What the codebook contains, per variable: name, label, type; for categorical
# variables the levels with at least `k` records (rarer levels are pooled and not
# named) and, optionally, their proportions rounded to 0.05; for numeric variables the
# range rounded outward to two significant digits and the median rounded to two
# significant digits (suppressed with fewer than `k` non-missing values); for dates the
# range at month resolution; missingness rounded to 0.05 ("rare" when 1 to k - 1
# records are missing). Identifier and free-text columns get a format description, never
# values. Per dataset: rows and identifiers rounded to 10, rows per identifier.
#
# READ THE OUTPUT BEFORE HANDING IT OVER. Delete anything you would not show a colleague
# outside the study: an unusual level name or variable name can itself be disclosive.

signif_floor <- function(x, digits = 2) {
  if (!is.finite(x) || x == 0) return(x)
  e <- floor(log10(abs(x))) - digits + 1
  floor(x / 10^e) * 10^e
}

signif_ceiling <- function(x, digits = 2) {
  if (!is.finite(x) || x == 0) return(x)
  e <- floor(log10(abs(x))) - digits + 1
  ceiling(x / 10^e) * 10^e
}

round_to <- function(x, step) round(x / step) * step

var_type <- function(x, free_text_share = 0.5, free_text_min = 20) {
  if (inherits(x, "Date")) return("date")
  if (inherits(x, c("POSIXct", "POSIXlt"))) return("datetime")
  if (is.ordered(x)) return("ordered")
  if (is.factor(x)) return("factor")
  if (!is.null(attr(x, "labels"))) return("factor")          # haven_labelled
  if (is.logical(x)) return("logical")
  if (is.character(x)) {
    u <- length(unique(x[!is.na(x)]))
    n <- sum(!is.na(x))
    if (n > 0 && u >= free_text_min && u / n > free_text_share) return("text")
    return("factor")
  }
  if (is.integer(x)) return("integer")
  if (is.numeric(x)) {
    v <- x[is.finite(x)]
    if (length(v) && all(abs(v - round(v)) < 1e-9)) return("integer")
    return("double")
  }
  "other"
}

id_format <- function(x) {
  v <- as.character(x[!is.na(x)])
  if (!length(v)) return("empty")
  classes <- c(if (any(grepl("[A-Za-z]", v))) "letters",
               if (any(grepl("[0-9]", v))) "digits",
               if (any(grepl("[^A-Za-z0-9]", v))) "separators")
  sprintf("identifier: %d to %d characters (%s)", min(nchar(v)), max(nchar(v)),
          paste(classes, collapse = ", "))
}

level_summary <- function(x, k, proportions) {
  if (!is.null(attr(x, "labels")) && !is.factor(x)) {
    labs <- attr(x, "labels")
    x <- factor(x, levels = unname(labs), labels = paste0(unname(labs), "=", names(labs)))
  }
  tab <- table(x, useNA = "no")
  keep <- tab[tab >= k]
  rare <- sum(tab > 0 & tab < k)
  n <- sum(tab)
  lev <- if (length(keep) == 0) "" else if (proportions && n > 0) {
    paste(sprintf("%s=%.2f", names(keep), round_to(as.numeric(keep) / n, 0.05)), collapse = " | ")
  } else paste(names(keep), collapse = " | ")
  list(levels = lev, n_rare_levels = rare)
}

missing_summary <- function(x, k) {
  m <- sum(is.na(x))
  if (m == 0) return("0")
  if (m < k) return("rare")
  sprintf("%.2f", round_to(m / length(x), 0.05))
}

codebook_variable <- function(x, name, k, proportions, id_vars) {
  out <- data.frame(variable = name,
                    label = if (is.null(attr(x, "label"))) "" else as.character(attr(x, "label")),
                    type = var_type(x), levels = "", n_rare_levels = NA_integer_,
                    min = "", max = "", median = "", p_missing = missing_summary(x, k),
                    note = "", stringsAsFactors = FALSE)
  nn <- sum(!is.na(x))
  if (name %in% id_vars) {
    out$type <- "id"
    out$note <- id_format(x)
    return(out)
  }
  switch(out$type,
    factor = , ordered = , logical = {
      s <- level_summary(if (is.logical(x)) factor(x, levels = c(FALSE, TRUE)) else x,
                         k, proportions)
      out$levels <- s$levels
      out$n_rare_levels <- s$n_rare_levels
    },
    integer = , double = {
      if (nn >= k) {
        v <- as.numeric(x[is.finite(x)])
        out$min <- format(signif_floor(min(v)))
        out$max <- format(signif_ceiling(max(v)))
        out$median <- format(signif(stats::median(v), 2))
      } else out$note <- sprintf("fewer than %d non-missing values: range suppressed", k)
    },
    date = , datetime = {
      if (nn >= k) {
        d <- as.Date(x[!is.na(x)])
        out$min <- format(d[which.min(d)], "%Y-%m")
        out$max <- format(d[which.max(d)], "%Y-%m")
      } else out$note <- sprintf("fewer than %d non-missing values: range suppressed", k)
    },
    text = {
      out$note <- "free text: no values"
    },
    {
      out$note <- paste("class", paste(class(x), collapse = "/"), ": not summarised")
    })
  out
}

make_codebook <- function(datasets, id_vars = character(), k = 5, proportions = TRUE) {
  if (is.data.frame(datasets)) datasets <- list(data = datasets)
  if (is.null(names(datasets)) || any(names(datasets) == ""))
    stop("give the datasets as a named list, e.g. list(baseline = df)")
  vars <- list()
  structure_rows <- list()
  for (ds in names(datasets)) {
    df <- datasets[[ds]]
    rows <- lapply(names(df), function(v) codebook_variable(df[[v]], v, k, proportions, id_vars))
    vrows <- do.call(rbind, rows)
    vars[[ds]] <- cbind(dataset = ds, vrows, stringsAsFactors = FALSE)
    idv <- intersect(id_vars, names(df))
    st <- data.frame(dataset = ds,
                     n_rows = if (nrow(df) >= 10) round_to(nrow(df), 10) else sprintf("<10"),
                     key = paste(idv, collapse = "+"),
                     n_ids = "", rows_per_id_min = "", rows_per_id_median = "",
                     rows_per_id_max = "", stringsAsFactors = FALSE)
    if (length(idv)) {
      per <- as.vector(table(do.call(paste, c(df[idv], sep = "\r"))))
      st$n_ids <- if (length(per) >= 10) round_to(length(per), 10) else "<10"
      st$rows_per_id_min <- min(per)
      st$rows_per_id_median <- stats::median(per)
      st$rows_per_id_max <- max(per)
    }
    structure_rows[[ds]] <- st
  }
  list(codebook = do.call(rbind, vars), structure = do.call(rbind, structure_rows),
       k = k, made = format(Sys.time(), "%Y-%m-%d %H:%M"))
}

write_codebook <- function(cb, dir = "codebook") {
  dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  utils::write.csv(cb$codebook, file.path(dir, "codebook.csv"), row.names = FALSE, na = "")
  utils::write.csv(cb$structure, file.path(dir, "structure.csv"), row.names = FALSE, na = "")
  writeLines(c(sprintf("Codebook made %s with k = %d.", cb$made, cb$k),
               "Read codebook.csv and structure.csv before handing them over.",
               "Delete anything you would not show a colleague outside the study."),
             file.path(dir, "README.txt"))
  invisible(file.path(dir, c("codebook.csv", "structure.csv")))
}
