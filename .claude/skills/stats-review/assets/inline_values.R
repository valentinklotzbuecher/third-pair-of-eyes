# inline_values.R -- trace the inline `r ...` expressions of a Quarto or R Markdown source.
#
# knitr::purl() extracts code chunks only, so a run of the purled script never evaluates
# the inline expressions that put numbers into the prose. After running the document's
# chunks, evaluate the inline expressions in the same session and save the table:
#
#   source("<stats-review skill>/assets/inline_values.R")
#   ex <- inline_exprs("work/pkg/product.qmd")
#   iv <- eval_inline(ex, envir = globalenv())      # the session that ran the chunks
#   write.csv(iv, "work/results/inline-values.csv", row.names = FALSE)
#
# Each row: source line, expression, and the value as R formats it. Compare it with the
# printed text (the extract) in the specification map. Base R only; tested by
# scripts/tests/test_recompute.R.

inline_exprs <- function(path) {
  lines <- readLines(path, warn = FALSE, encoding = "UTF-8")
  start <- 1L
  if (length(lines) && trimws(lines[1]) == "---") {
    close <- which(trimws(lines[-1]) %in% c("---", "..."))
    if (length(close)) start <- close[1] + 2L
  }
  inside <- FALSE
  rows <- list()
  for (i in seq_along(lines)) {
    if (i < start) next
    ln <- lines[i]
    if (!inside && grepl("^\\s*```+\\s*\\{", ln)) { inside <- TRUE; next }
    if (inside && grepl("^\\s*```+\\s*$", ln)) { inside <- FALSE; next }
    if (inside) next
    hits <- regmatches(ln, gregexpr("`r[ \t]+[^`]+`", ln))[[1]]
    for (h in hits) {
      rows[[length(rows) + 1L]] <- data.frame(
        line = i, expr = sub("`$", "", sub("^`r[ \t]+", "", h)), stringsAsFactors = FALSE)
    }
  }
  if (!length(rows)) return(data.frame(line = integer(), expr = character(),
                                       stringsAsFactors = FALSE))
  do.call(rbind, rows)
}

eval_inline <- function(exprs, envir = globalenv()) {
  exprs$value <- vapply(exprs$expr, function(e) {
    v <- tryCatch(eval(parse(text = e), envir = envir),
                  error = function(err) structure(paste0("ERROR: ", conditionMessage(err)),
                                                  class = "inline_error"))
    if (inherits(v, "inline_error")) return(unclass(v))
    paste(format(v), collapse = " ")
  }, character(1), USE.NAMES = FALSE)
  exprs$error <- startsWith(exprs$value, "ERROR: ")
  exprs
}
