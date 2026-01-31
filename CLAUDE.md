# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains tools for LLM-assisted review of clinical research documents, specifically for the Department of Clinical Research statistics team. It supports reviewing:
- Statistical Analysis Plans (SAPs)
- Sample Size Estimations
- Full Analysis Reports

## Quick Start

```bash
# 1. Copy and configure API keys
cp .Renviron.example .Renviron
# Edit .Renviron with your API keys

# 2. Place your document pair in review_examples/
#    - One .pdf file (rendered output)
#    - One .qmd file (source code)

# 3. Edit document_review.qmd params section:
#    - Set provider (openai, anthropic, google)
#    - Set review_type (sample_size, analysis_plan, full_report)
#    - Add reviewer_questions if needed

# 4. Render the review
quarto render document_review.qmd
```

## Workflow

1. **Place files**: Put your PDF + QMD pair in `review_examples/`
2. **Configure**: Edit the `params:` section in `document_review.qmd`:

```yaml
params:
  review_folder: "review_examples"
  review_type: "sample_size"
  provider: "anthropic"
  model: "claude-opus-4-20250514"  # or leave empty for provider default
  reviewer_questions: |
    1. Is the assumed treatment effect realistic?
    2. Should we consider a futility interim analysis?
```

**Available models** (examples with date versions):
- OpenAI: `gpt-4o`, `gpt-4o-2024-11-20`, `gpt-5-pro-2025-10-06`, `gpt-5.2-pro-2025-12-11`
- Anthropic: `claude-sonnet-4-20250514`, `claude-opus-4-20250514`
- Google: `gemini-2.0-flash`, `gemini-2.5-pro-preview-05-06`

3. **Render**: Run `quarto render document_review.qmd`
4. **Output**: Get both `document_review.html` and `document_review.pdf`

## Review Types

- `sample_size` - Sample size justification (assumptions, calculations, sensitivity)
- `analysis_plan` - SAP review (estimand framework, methods, implementation clarity)
- `full_report` - Full statistical report (SAP adherence, results, conclusions)

## Providers

- `openai` - GPT-4o
- `anthropic` - Claude Sonnet (recommended)
- `google` - Gemini Flash

## Build Commands

```bash
# Standard review (edit params in YAML, then render)
quarto render document_review.qmd

# Command-line parameter override
quarto render document_review.qmd -P provider:openai -P review_type:analysis_plan

# Interactive version (Shiny app for exploration)
quarto preview document_review_interactive.qmd
```

## Output & Results

Each review generates:
- **HTML/PDF report** with the review output
- **Usage summary table** showing model, tokens, and cost
- **Saved results** in `review_results/` folder:
  - `.md` file for human reading
  - `.json` file for programmatic comparison

Results are timestamped and never overwrite, enabling model comparison:
```
review_results/
  SSE_example_anthropic_claude_opus_4_20250514_20250131_143052.md
  SSE_example_anthropic_claude_opus_4_20250514_20250131_143052.json
  SSE_example_openai_gpt_4o_20250131_144215.md
  SSE_example_openai_gpt_4o_20250131_144215.json
```

## Architecture

- **document_review.qmd**: Parameterized report (main workflow)
- **document_review_interactive.qmd**: Interactive Shiny app (demos/exploration)
- **review_results/**: Saved review outputs for comparison
- **theme-dark.scss**: Dark purple theme
- **.Renviron**: API keys (copy from .Renviron.example)

Legacy files:
- **LLM_testing.qmd**: Original test document (OpenAI only)
- **methods.qmd**: Extended multi-model evaluation pipeline

## Dependencies

R:
- `reticulate`

Python:
- `openai`
- `anthropic`
- `google-generativeai`

Install Python packages:
```r
reticulate::py_install(c("openai", "anthropic", "google-generativeai"), pip = TRUE)
```

For interactive version, also install:
```r
install.packages(c("shiny", "markdown"))
```

## Configuration

API keys are read from `.Renviron` (R convention). Copy `.Renviron.example` to `.Renviron` and add your keys:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

Optional model overrides:
```
LLM_REVIEW_MODEL_OPENAI=gpt-4o
LLM_REVIEW_MODEL_ANTHROPIC=claude-sonnet-4-20250514
LLM_REVIEW_MODEL_GOOGLE=gemini-2.0-flash
```

## Notes

- Place exactly one PDF and one QMD file in `review_examples/`
- Both files are reviewed together: PDF for output, QMD for code/methodology
- Reviews cover both ICH E9(R1) estimand framework and general statistical correctness
- Output format matches human consistency review (Decision checkboxes, Major/Minor Issues)
- Reviewer questions are answered in a dedicated section of the output
