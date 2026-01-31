# LLM-Assisted Clinical Document Review

A Quarto-based tool for LLM-assisted review of clinical research documents, developed for the Department of Clinical Research statistics team.

## Features

- **Multi-provider support**: OpenAI (GPT-4o, GPT-5), Anthropic (Claude Sonnet/Opus), Google (Gemini)
- **ICH E9(R1) aligned**: Review prompts based on estimand framework guidelines
- **Three review types**: Sample Size Estimation, Statistical Analysis Plan, Full Report
- **Token & cost tracking**: Automatic usage logging with cost calculation
- **Result archiving**: All reviews saved for model comparison

## Quick Start

```bash
# 1. Configure API keys
cp .Renviron.example .Renviron
# Edit .Renviron with your keys

# 2. Place documents in review_examples/
#    - One .pdf (rendered output)
#    - One .qmd (source code)

# 3. Configure review in document_review.qmd params section

# 4. Render
quarto render document_review.qmd
```

## Configuration

Edit the `params:` section in `document_review.qmd`:

```yaml
params:
  review_folder: "review_examples"
  review_type: "sample_size"      # or: analysis_plan, full_report
  provider: "anthropic"           # or: openai, google
  model: "claude-opus-4-20250514" # or leave empty for default
  reviewer_questions: |
    1. Is the dropout assumption justified?
    2. Are the effect size assumptions realistic?
```

## Output

Each review generates:
- **HTML/PDF report** with formatted review output
- **Usage summary** (model, tokens, cost)
- **Archived results** in `review_results/` (.md + .json)

## Review Types

| Type | Use Case |
|------|----------|
| `sample_size` | Sample size estimation/justification |
| `analysis_plan` | Statistical Analysis Plan (SAP) |
| `full_report` | Complete statistical analysis report |

## Supported Models

| Provider | Models |
|----------|--------|
| OpenAI | `gpt-4o`, `gpt-5`, `gpt-5-pro-*`, `gpt-5.2-pro-*` |
| Anthropic | `claude-sonnet-4-*`, `claude-opus-4-*` |
| Google | `gemini-2.0-flash`, `gemini-2.5-pro` |

## Files

| File | Description |
|------|-------------|
| `document_review.qmd` | Main parameterized report |
| `document_review_interactive.qmd` | Shiny app version |
| `review_results/` | Archived review outputs |
| `review_examples/` | Input documents |
| `.Renviron` | API keys (not tracked) |

## Requirements

**R packages:**
```r
install.packages("reticulate")
```

**Python packages:**
```r
reticulate::py_install(c("openai", "anthropic", "google-generativeai"), pip = TRUE)
```

## License

Internal use only - Department of Clinical Research
