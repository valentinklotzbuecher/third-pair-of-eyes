# LLM-Assisted Clinical Document Review

Minimal prototype for manual LLM-assisted pre-human review of clinical research documents.

**Security warning:** never share or commit API keys. Keep them only in local secrets files (for example `~/.Renviron`) that are git-ignored.

## Prototype Entry Point

Use `review_prototype.qmd` as the active document.

Current report behavior:
- HTML report output (`review_prototype.html`)
- intro/instructions collapsed at top
- compact run summary strip (document, models, estimated total cost)
- additional runtime settings in a collapsed details block
- setup/helpers + manual API chunks grouped in collapsed reference callout
- latest saved OpenAI and Anthropic outputs shown as provider cards
- per-provider metadata (collapsed), Top 3 Major Issues preview, full review text
- summary section with cost breakdown + prompt used for model calls

API call chunks are intentionally `eval: false`, so render does not execute API requests.

## Quick Start

```bash
# 1) Put input files in review_examples/
#    - one .pdf
#    - one .qmd

# 2) Set API keys locally (for example in ~/.Renviron):
#    OPENAI_API_KEY=...
#    ANTHROPIC_API_KEY=...

# 3) In RStudio, run interactive API chunks as needed
#    (OpenAI submit/poll, Anthropic review)

# 4) Render report (safe; no API chunk execution)
quarto render review_prototype.qmd --to html
```

## Key Paths

| Path | Purpose |
|------|---------|
| `review_prototype.qmd` | Active prototype report |
| `review_examples/` | Input files (`.pdf` + `.qmd`) |
| `review_results/prototype_jobs/` | OpenAI background job records |
| `review_results/prototype_runs/` | Saved model outputs (`.md` + `.json`) |
| `archive/legacy_document_review/` | Archived previous workflow |

## Requirements

R:
```r
install.packages(c("reticulate", "flextable"))
```

Python:
```r
reticulate::py_install(c("openai", "anthropic"), pip = TRUE)
```

## License

Internal use only - Department of Clinical Research
