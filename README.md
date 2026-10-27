# AI-assisted consistency review for DKF statistical products

Agent skills that prepare the consistency review of a DKF statistical product (sample
size estimation, protocol statistics sections, statistical analysis plan, statistical
report, results manuscript) before a second statistician reviews it. An AI agent reads
the rendered document against its Quarto/R source and the documents that govern it,
recomputes what can be recomputed, runs the code where the data rules allow, has every
finding challenged by a fresh agent, and writes a draft in the DKF consistency-review
form: Decision boxes, General comments, Major and Minor issues, and answers to the
questions in the assignment.

The skills are adapted from Joe Francis's
[research_skills](https://github.com/isitcredible/research_skills) (The Catalogue of
Errors Ltd, MIT licence, v0.9.1); see [`.claude/skills/UPSTREAM.md`](.claude/skills/UPSTREAM.md)
for what was kept, adapted and replaced. The earlier single-call API prototype is in
[`archive/`](archive/README.md).

The review is an aid to the human consistency review, not a replacement. It says what
it checked, on what evidence, and what it could not check.

## The skills

| Skill | What it does |
|---|---|
| [`dkf-review`](.claude/skills/dkf-review/SKILL.md) | The review, in five stages: **document** (versions, consistency with protocol/SAP/registry, printed numbers and their arithmetic, design and estimand), **code-and-data** (code against text, Quarto/R mechanics, runs under the job's data mode, assumption and fragility checks, twelve clinical diagnostic modules), **statements** (a ledger of the product's load-bearing statements: holds, narrower or not established), **challenge** (a fresh agent tests the evidence in both directions) and **verdict** (a fresh agent writes `SYNTHESIS.md` and answers the assignment questions). |
| [`dkf-synthetic-data`](.claude/skills/dkf-synthetic-data/SKILL.md) | Builds dummy data so the code can run without patient data: from the code's data contract, from a disclosure-controlled codebook the statistician makes locally, or from dummy data the statistician supplies; adds edge cases and known-truth replicates. |
| [`dkf-review-audit`](.claude/skills/dkf-review-audit/SKILL.md) | Mechanical audit of a finished review (depth `full`): coverage of every table, figure and code chunk, re-runs, print checks; corrections go back to the verdict. |
| [`dkf-consistency-review`](.claude/skills/dkf-consistency-review/SKILL.md) | Compiles the review into the DKF form (`CONSISTENCY_REVIEW.md`, `.html`, `.org`) with computed Decision boxes, after fact, coverage and register gates; can write `REVIEW` comments into a copy of the `.qmd`. |

Clinical modules: sample size, simulation, estimand (ICH E9(R1)), RCT, missing data,
time-to-event, multiplicity and subgroups, regression models, observational
comparisons, prediction models, Bayesian analyses, small samples.

## Data protection

Everything the agent reads goes to the model provider. What may be read is decided in
the job's `00_ASSIGNMENT.md` before the run, and the review never widens it.

| Data mode | The agent reads | What the review can establish |
|---|---|---|
| `none` (default) | documents and code | everything that needs no patient data: sample size and simulation code, arithmetic on printed numbers, code read against text |
| `synthetic` | + dummy data (built from the code, or from a codebook made locally with `make_codebook.R`) | that the code runs and implements the stated specification, and that its estimators recover known effects; never a printed number |
| `shared` | + patient-level data, only with a recorded clearance (who approved it, on what basis) | reproduction of printed numbers |

Before the agent opens anything, `scan_job.py` checks the clearance fields and stops
the run when a data file sits where the data mode does not allow it. Reports and
manuscripts with unpublished results need the documents' clearance too. At the time
of writing the DKF has no zero-data-retention agreement with a model provider; check
the current DKF rules before clearing anything beyond the default. Details:
[`data-access.md`](.claude/skills/dkf-review/references/data-access.md).

## Running a review

1. Clone this repository and start Claude Code in it (`claude`); the skills in
   `.claude/skills/` load automatically.
2. Create a job folder (job folders under `jobs/` are never committed):

   ```bash
   python3 .claude/skills/dkf-review/scripts/new_job.py jobs/2026-10_SSE001_NIR \
     --product path/to/SSE001_NIR.qmd path/to/SSE001_NIR.pdf \
     --governing path/to/protocol_v1.2.pdf
   ```

   A product with other files its source reads (saved simulation results, a
   `_quarto.yml`) is given as its folder: `--product path/to/product_folder/`.
3. Fill in `jobs/<job>/00_ASSIGNMENT.md`: product type, the questions for the
   reviewer, the documents it depends on, what is cleared, the data mode, the depth.
4. Ask the agent: *"Review the product in jobs/2026-10_SSE001_NIR with dkf-review, then
   write the consistency review."* It runs the clearance scan first and stops on any
   problem.
5. Read `jobs/<job>/CONSISTENCY_REVIEW.html` (and `work/annotated/*.REVIEW.qmd`), then
   edit the form as the human reviewer.

**Depth.** `quick` (no challenge stage; core modules only) for a short SSE or a
re-review; `standard` (default) for a first review; `full` adds the audit, for
high-risk products. A full multi-agent review runs many agent turns and costs one to
two orders of magnitude more than the single-call prototype did; measure on your own
products before routine use.

## Requirements

- Claude Code, or another agent harness that can start fresh subagents (the challenge
  and verdict stages need fresh contexts; without them the run is marked `INTERIM`).
  For other harnesses, link or copy the four folders in `.claude/skills/` into the
  harness's skills directory, side by side.
- Python 3.10 or later; standard library only, plus `pytest` for the tests and
  optionally `mistune` for HTML rendering.
- R with the packages the product uses (the review records any version difference
  from the product's `groundhog` date or `renv.lock`); Quarto if available.
- Poppler's `pdftotext`, `pdfinfo`, `pdftoppm` and `pdftocairo` (text, metadata,
  page images, and figure values read from the PDF's vector graphics).

## Repository layout

```
.claude/skills/        the four skills, LICENSE-research_skills, UPSTREAM.md
jobs/                  review jobs (git-ignored; one folder per product review)
tools/upstream_diff.sh what changed upstream since the fork
archive/               the earlier API prototype
CLAUDE.md              instructions for Claude Code in this repository
```

## Tests

```bash
cd .claude/skills
python3 -m pytest -q -p no:cacheprovider dkf-review/scripts/tests dkf-review-audit/scripts/tests \
  dkf-consistency-review/scripts/tests dkf-consistency-review/ai-sweep/scripts/tests \
  dkf-synthetic-data/scripts/tests
python3 dkf-review/scripts/check_suite_version.py
```

The R helpers (`recompute.R`, `make_codebook.R`, `synthesize.R`) have their own test
scripts, run by the Python suite when `Rscript` is installed.

## Licence

Internal use, Department of Clinical Research, University of Basel. The files derived
from research_skills keep its MIT licence and copyright notice
([`LICENSE-research_skills`](.claude/skills/LICENSE-research_skills)).
