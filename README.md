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
for what was kept, adapted and replaced.

The review is an aid to the human consistency review, not a replacement. It says what
it checked, on what evidence, and what it could not check.

**Status: version 0.4.0.** Three runs on a synthetic demonstration SSE with six
planted issues (DEMO-TKA, two pages; kept outside this repository so no run can read
its answer key) found all six and sized each one; one run also caught an error in the
answer key. The two at depth `standard` (version 0.1) took about 3.4 and 1.6 hours of
model time, $72 and $27 at API list prices, and wrote texts several times the length
of the product. Version 0.2 added the two-agent `quick` depth and length limits that
follow the product's size: its run took 34 minutes from start to finished form, $10
at API list prices, with a form of about 1,100 words. Version 0.3 hands the review to
the human reviewer (`REVIEWER.md`, `DISPOSITIONS.md`) and keeps each review with its
product; it has not yet been run on the demo. A trial on one real SSE ran the first
two stages. The data modes `synthetic` and `shared` have not yet run on a real
product.

Version 0.4 renames the skills so they read well outside DKF: `stats-review`,
`stats-review-audit`, `stats-consistency-review`, `stats-synthetic-data` and the chat
skill `stats-document-check` (they were `dkf-review` and so on); what they do is
unchanged. A job made with an earlier version names the old folders; read `dkf-<name>`
as `stats-<name>`.

## The skills

| Skill | What it does |
|---|---|
| [`stats-review`](.claude/skills/stats-review/SKILL.md) | The review, in five stages: **document** (versions, consistency with protocol/SAP/registry, printed numbers and their arithmetic, design and estimand), **code-and-data** (code against text, Quarto/R mechanics, runs under the job's data mode, assumption and fragility checks, twelve clinical diagnostic modules), **statements** (a ledger of the product's load-bearing statements: holds, narrower or not established), **challenge** (a fresh agent tests the evidence in both directions) and **verdict** (a fresh agent writes `SYNTHESIS.md` and answers the assignment questions). |
| [`stats-synthetic-data`](.claude/skills/stats-synthetic-data/SKILL.md) | Builds dummy data so the code can run without patient data: from the code's data contract, from a disclosure-controlled codebook the statistician makes locally, or from dummy data the statistician supplies; adds edge cases and known-truth replicates. |
| [`stats-review-audit`](.claude/skills/stats-review-audit/SKILL.md) | Mechanical audit of a finished review (depth `full`): coverage of every table, figure and code chunk, re-runs, print checks; corrections go back to the verdict. |
| [`stats-consistency-review`](.claude/skills/stats-consistency-review/SKILL.md) | Compiles the review into the DKF form (`CONSISTENCY_REVIEW.md`, `.html`, `.org`) with computed Decision boxes, after fact, coverage and register gates; can write `REVIEW` comments into a copy of the `.qmd`. |

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
[`data-access.md`](.claude/skills/stats-review/references/data-access.md).

## Running a review

A review lives with the product: its job folder sits in the product's own repository
and is committed there. This repository only provides the skills and stays free of
reviews (its `jobs/` folder is for trials and the synthetic demo, and is git-ignored).

1. **Make the skills available.** Either on the web or locally.

   *Claude Code on the web* (claude.ai/code), for a product in a private GitHub
   repository. Once:
   - Connect GitHub at claude.ai/connect-github. The Claude GitHub App must be
     installed on the product's repository; this one is reached through your access
     as a collaborator.
   - In a cloud environment (the environment menu in the session's title bar, then
     Edit), paste [`tools/web_setup.sh`](tools/web_setup.sh) under Setup script. It
     installs R with knitr and rmarkdown, Quarto, Poppler and mistune, which the cloud
     image lacks; add the product's R packages there as `r-cran-*` lines.
   - Network access must allow package managers and github.com. A literature search
     needs wider access; without it the review records the check as waived.
   - Set no `ANTHROPIC_API_KEY` among the environment's variables (see "Running on a
     Claude subscription").

   For each review, start a session in that environment with both the product's
   repository and this one selected. The session works on its own branch of the
   product's repository: merge the job folder there (step 5). Each session clones this
   repository fresh, so it always runs the current skills.

   *Locally*, link the four skill folders into your user skills once:

   ```bash
   mkdir -p ~/.claude/skills
   for s in stats-review stats-review-audit stats-consistency-review stats-synthetic-data; do
     ln -s "$PWD/.claude/skills/$s" ~/.claude/skills/$s
   done
   ```

   Products held outside GitHub (SVN, a network drive) are reviewed locally.
2. **Create the job beside the product**, from the product's repository:

   ```bash
   python3 ~/.claude/skills/stats-review/scripts/new_job.py review/2026-11-12_quick \
     --product SSE001.qmd SSE001.pdf --governing ../protocol/protocol_v1.2.pdf
   ```

   On the web the script sits in this repository's clone
   (`../stats_review/.claude/skills/stats-review/scripts/new_job.py` from the product's
   clone), or ask Claude to create the job. A product whose source reads other files
   (saved simulation results, a `_quarto.yml`) is given as its folder:
   `--product path/to/product_folder/`. The job
   gets its own `.gitignore`, which keeps copies of the product and its documents,
   literature and any data out of every commit.
3. **Fill in `00_ASSIGNMENT.md`**: product type, the questions for the reviewer, the
   documents it depends on, what is cleared, the data mode, the depth.
4. **Ask the agent**: *"Review the product in review/2026-11-12_quick with stats-review,
   then write the consistency review."* It runs the clearance scan, states the depth,
   data mode and size class, asks you to check your usage, and waits for your go-ahead.
   A run that stops part-way resumes from the job's `PROGRESS.md`.
5. **Commit the job folder** in the product's repository (on the web: merge the
   session's branch there).
6. **The human reviewer** starts from the job's `REVIEWER.md`: the form
   (`CONSISTENCY_REVIEW.html`, editable as `.org`), the source with `REVIEW` comments
   (`work/annotated/`), links from each issue to the scripts and logs behind it, and
   `DISPOSITIONS.md`, where the reviewer marks each issue kept, edited or dropped.
   Questions go to Claude Code opened in the job folder: it answers from the evidence,
   re-runs with changed inputs in `work/followup/`, and changes the form only when
   asked.

**Depth.** `quick` for a short SSE or a re-review: two agents (a review agent for the
first three stages, a fresh verdict agent that also writes the form) and no challenge
stage. `standard` (default) for a first review: one agent per stage and the challenge.
`full` adds the audit, for high-risk products. A product of at most 10 rendered pages
counts as short: its review writes less (a form of about 1,000 words) and works the
clinical modules into the code-and-data agent. Measure on your own products before
routine use.

**Running on a Claude subscription.** The skills run inside Claude Code, so a review
counts against your subscription's usage limits instead of API credits, as long as
Claude Code is logged in with the subscription:

- Claude Code uses `ANTHROPIC_API_KEY` instead of the subscription whenever that
  variable is set ([help article](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-max-plan)).
  The old prototype put the key in `~/.Renviron`, and a terminal opened from RStudio
  can inherit it. Remove it from the environment Claude Code starts in, and check
  `/status` before a run.
- Usage limits are per session window and per week. Check your usage (`/usage`)
  before a run. On the demo SSE, a `standard` run without modules used about one
  5-hour window of active work on our account; one run started with the weekly window at 97% and
  then waited four days. Start with room to spare, never run two reviews at once on
  one account, prefer `quick` for routine SSEs, and resume a stopped run from its
  `PROGRESS.md` once the limit resets (step 4).
- Data terms depend on the plan. On personal plans (Pro, Max), whether chats and
  coding sessions may be used for model training is a privacy setting
  ([Anthropic's consumer terms](https://www.anthropic.com/news/updates-to-our-consumer-terms));
  commercial plans (Team, Enterprise, Education) and the API are not covered by it.
  Check the setting and the DKF rules before clearing any document.

## Trying the first stage in chat

`chat-skills/stats-document-check.zip` is the document stage on its own, for Claude
chat: upload it under Customize, Skills (code execution on), attach a product you may
send and ask for a document check. It shows what the agents are told to do and returns
findings, a consistency table and a check log, but it runs no product code; see
[`chat-skills/README.md`](chat-skills/README.md).

## Using these skills as a colleague

- Run reviews from your product's repository, as above. Don't push to this repository
  or keep reviews here.
- Report a problem, or something a review got wrong, as a GitHub issue in general
  terms: what kind of product, what the review did, what it should have done. Leave
  out the product's name, numbers and text; they stay in the job.
- Start with depth `quick` and data mode `none` on a product that already had its
  human review, and compare the two.

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
chat-skills/           stand-alone skills for Claude chat, outside the suite
jobs/                  trial and demo jobs only (git-ignored)
tools/upstream_diff.sh what changed upstream since the fork
tools/web_setup.sh     setup script for a Claude Code on the web environment
CLAUDE.md              instructions for Claude Code in this repository
AGENTS.md              pointer to CLAUDE.md for other coding agents
```

## Tests

```bash
cd .claude/skills
python3 -m pytest -q -p no:cacheprovider stats-review/scripts/tests stats-review-audit/scripts/tests \
  stats-consistency-review/scripts/tests stats-consistency-review/ai-sweep/scripts/tests \
  stats-synthetic-data/scripts/tests ../../chat-skills/tests
python3 stats-review/scripts/check_suite_version.py
```

The R helpers (`recompute.R`, `make_codebook.R`, `synthesize.R`) have their own test
scripts, run by the Python suite when `Rscript` is installed.

## Licence

Internal use, Department of Clinical Research, University of Basel. The files derived
from research_skills keep its MIT licence and copyright notice
([`LICENSE-research_skills`](.claude/skills/LICENSE-research_skills)).
