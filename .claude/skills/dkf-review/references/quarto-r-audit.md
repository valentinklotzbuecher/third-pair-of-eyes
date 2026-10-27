# Quarto and R mechanics: what to audit

The code-and-data stage reads the source for the ways a Quarto document can print
something its code does not compute, hide something its code does, or fail to
reproduce on another machine. Each hit goes to the specification map or the
construction ledger with `file:line`; it becomes a finding when it changes, or could
change, a printed number or what a reader understands.

## Chunk options

| Option | What to check |
|---|---|
| `eval: false` | Is any number, table or statement in the text produced by this chunk, or by an earlier run of it? A results table from an unevaluated chunk, or a value copied from one into prose, is not reproducible from the document. |
| `include: false`, `echo: false` | Harmless for display; check that hidden chunks computing reported numbers are in the specification map. |
| `error: true` | The document renders through errors; search the rendered output for error text and check that no reported number comes from a failed chunk. |
| `warning: false`, `message: false` | Around model fits, simulations or package loading, these hide convergence, singularity, separation and version warnings. Re-run with warnings visible (`options(warn = 1)` set in a profile through `R_PROFILE_USER`, which chunk options do not override) and record what it prints. |
| `cache: true` | Cached chunks do not re-run when upstream data or code change unless `dependson`/`cache.extra` say so; a stale cache can print numbers the current code no longer computes. Re-render with the cache cleared. |
| `freeze` (project option) | Frozen computations are reused across renders; check the freeze is current with the source. |
| `output: asis` | Generated markdown; check the generating code, not only its output. |

Project and document-level `execute:` options apply to every chunk unless overridden;
read them first.

## Numbers in prose

- A number typed into the prose that the code also computes is a consistency risk:
  list every such number in the specification map as `no-code` and compare it with the
  code's value.
- Inline `` `r expr` `` expressions are the reproducible form. Trace each to the object
  it reads; check rounding (`round()`, `format()`, `sprintf()`), units and whether the
  object is the one the sentence describes.
- `params` values used in the text and in the code are the same values; a parameter
  overridden at render time (`quarto render -P`) is recorded.

## Reproducibility

- **Seeds**: `set.seed()` before every random step that a reported number depends on,
  set once in a way that makes the order of chunks irrelevant, or re-set per
  simulation; parallel code uses independent streams (`future.seed = TRUE`, or
  `RNGkind("L'Ecuyer-CMRG")` with `parallel`). Record the RNG kind (`RNGkind()`); the
  sample kind changed in R 3.6.0, so older code reproduces only with the old setting.
- **Package versions**: `groundhog.library(pkg, date)` or `renv.lock` pin versions;
  compare with the R and package versions the rendered PDF records (the DKF template
  writes them into the PDF Keywords field; `scan_job.py` extracts them). A render made
  with versions other than the pinned ones is recorded. Where the pinned versions
  cannot be installed for the review, shim and log (`../SKILL.md`, Running it).
- **Paths**: absolute paths, `setwd()`, files read from outside the project, network
  drives. Each is a reproducibility finding when it stops the code running elsewhere.
- **External files**: every file the code reads, and whether the code that created it is
  in the job: saved simulation results (`.rds`, `.rda`), lookup tables, derived
  datasets. A file no delivered code creates is *unverifiable as delivered*; check its
  timestamp and contents against the settings the text states.
- **Session information**: `sessionInfo()` or `xfun::session_info()` in the rendered
  document or its metadata.

## Stale renders

The rendered document must be what the delivered source produces. Compare:

- the revision or date in the PDF footer and title page with the source's version
  line (an SVN `$Id$` keyword, a git hash, a date in the YAML);
- the PDF's creation date with the source's last change;
- a sample of printed numbers with what the code computes (all of them for an SSE).

A mismatch is a finding: the reviewer may be reading numbers the current code does not
produce.

## Templates

DKF products built on the `dkfreporting` template carry product metadata in YAML
`params` and render to `dkf-pdf`, `dkf-docx` or `dkf-html`. The template's own code
(title page, metadata, styling) is not part of the review unless it changes content.
