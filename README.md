# LLM-Assisted Clinical Document Review

Minimal prototype for manual LLM-assisted pre-human review of clinical research documents.

**Security warning:** never share or commit API keys. Keep them only in local secrets files (e.g., `.Renviron`) that are git-ignored.

## Current Workflow (Prototype)

Use `review_prototype.qmd` as the active entry point.

It supports:
- OpenAI background-mode submission + polling (manual chunks)
- Anthropic direct call with extended reasoning (manual chunk)
- Review context from both PDF and Quarto source
- Prompt-size control via `code_context_mode` to reduce token burn

All API call chunks are `eval: false` by design, so rendering the document does not run any API requests.

## Quick Start

```bash
# 1) Put input files in review_examples/
#    - one .pdf
#    - one .qmd

# 2) Edit params in review_prototype.qmd

# 3) Render safely (no API calls will run)
quarto render review_prototype.qmd

# 4) Run API chunks manually inside Quarto editor/notebook
```

## Key Files

| File | Purpose |
|------|---------|
| `review_prototype.qmd` | Active minimal prototype |
| `review_examples/` | Input files (.pdf + .qmd) |
| `review_results/prototype_jobs/` | OpenAI background job records |
| `review_results/prototype_runs/` | Saved model outputs (.md + .json) |
| `archive/legacy_document_review/` | Archived previous workflow |

## Requirements

R:
```r
install.packages("reticulate")
```

Python:
```r
reticulate::py_install(c("openai", "anthropic"), pip = TRUE)
```

## License

Internal use only - Department of Clinical Research
