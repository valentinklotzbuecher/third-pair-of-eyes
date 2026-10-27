"""Shared test helpers: a minimal dkf-review job that passes every gate.

Not named conftest.py so that it never collides with the consistency-review
skill's conftest when all suites run in one pytest call."""
import os
import sys
import textwrap


SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS)

ASSIGNMENT = """\
# Assignment

## Product

- Statistical product: example_SSE001.pdf
- Product type: {ptype}
- Title: Example trial
- Internal ID: ex26Test1
- Version: rev. 100
- Author(s): A. Statistician
- Human reviewer: B. Reviewer

## Important issues for reviewer

1. Is the sample size driven mainly by the treatment effect?
2. Should non-proportional hazards be discussed?

## Other documents this product depends on

- Study protocol: 02_governing/protocol_v1_2026-01-01.pdf

## Clearance

- Documents: SSE text and code, no patient data (test)
- Data mode: {mode}
- Non-patient files: {npf}
- Data clearance: {clearance}

## Review settings

- Depth: {depth}
"""

QMD = """\
---
title: Statistical Aspects of the Study Protocol
author: 'A. Statistician'
params:
  internal-dkf-id: 'ex26Test1'
  product-type: SSE
  level-of-assumptions: 'high'
  final-product-risk:
format:
  dkf-pdf:
    toc: false
---

\\svnid{$Id: example_SSE001.qmd 100 2026-07-30 11:10:17Z tester $}

```{r}
#| label: setup
#| include: false
library("groundhog")
gh_date <- "2026-06-24"
groundhog.library("dplyr", date = gh_date)
calc_file <- "dat/calc.rds"
```

```{r}
#| label: sim
#| eval: false
set.seed(42)
res <- readRDS(calc_file)
```

The sample size is `r 100` participants.
"""

MODULE_WALK = "\n".join(
    ["# Module walk", "", "| Module | Decision | Condition and evidence |", "|---|---|---|",
     "| sample-size-diagnostics | fired | target N stated |",
     "| simulation-diagnostics | fired | simulated power; the plan/analysis is not run here |"] +
    [f"| {m} | not applicable | no such feature |" for m in (
        "estimand-diagnostics", "rct-diagnostics", "missing-data-diagnostics",
        "time-to-event-diagnostics", "multiplicity-diagnostics",
        "regression-model-diagnostics", "observational-diagnostics",
        "prediction-model-diagnostics", "bayesian-diagnostics", "small-n-diagnostics")]
) + "\n"

SYNTHESIS = """\
# Synthesis — Example trial (ex26Test1, rev. 100)

Verification: OPEN · 1 not established / 0 narrower / 1 hold

## Status

COMPLETE. Depth standard; challenge ran; data mode none.

## What the product establishes and what it does not

The target N of 100 holds; the control rate is not sourced.

## Cross-cutting findings

None.

## Statement ledger

| Statement (location) | Kind | Centrality | Holds | Kernel | Not established | Strongest defence | Status |
|---|---|---|---|---|---|---|---|
| "100 participants give 80% power" (Summary, p. 1; ST01) | calculation | primary | holds | 100 gives 80% | — | — | settled |
| "control rate 0.40" (p. 2; ST02) | assumption | supporting | not established | none | the rate's source | pilot data | settled |

## Recomputation table

| Quantity | Printed (location) | Recomputed | Method and inputs | Agreement | Evidence |
|---|---|---|---|---|---|
| N | 100 (p. 1) | 100 | closed form | agrees | work/logs/ss.log |

## Answers to the assignment questions

### Q1. Is the sample size driven mainly by the treatment effect?

Yes.

basis: ST01
status: answered

### Q2. Should non-proportional hazards be discussed?

Not applicable to a binary endpoint.

basis: ST01
status: answered

## Data and reproducibility

Data mode none; the code reproduces the printed N.

## Findings

### F1. The control rate has no source
bears on: the control rate (ST02)
where: text
evidence: analysis/code-and-data/assumption-ledger.csv

The rate is unsourced.

fix: cite the source of 0.40.

## Limits of this review

None.

## Counts

No rows moved.
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def make_job(root, ptype="sse", mode="none", npf="dat/calc.rds (saved simulation results)",
             clearance="not applicable", depth="standard"):
    """Write a complete minimal job under `root` and return its path."""
    j = str(root)
    write(f"{j}/00_ASSIGNMENT.md", ASSIGNMENT.format(ptype=ptype, mode=mode, npf=npf,
                                                     clearance=clearance, depth=depth))
    write(f"{j}/01_product/example_SSE001.qmd", QMD)
    write(f"{j}/01_product/dat/calc.rds", "not really rds")
    write(f"{j}/02_governing/protocol_v1_2026-01-01.txt", "protocol text")
    rep = ("# Report\n\n## Status\n\nCOMPLETE\n\n## Findings\n\n"
           "### D1. The control rate has no source\nbears on: the control rate (ST02)\n"
           "where: text\nevidence: work/logs/ss.log\n\nBody.\n\nfix: cite it.\n\n"
           "## Leads for later stages\n\nNone.\n\n## Scope assumptions\n\nNone.\n\n"
           "## Coverage\n\nAll.\n")
    write(f"{j}/00_INTAKE.md", "# Intake\n\nSuite version: 0.1.0\nData mode: none\nDepth: standard\n\n"
          "Q1. Is the sample size driven mainly by the treatment effect?\n"
          "Q2. Should non-proportional hazards be discussed?\n")
    write(f"{j}/AGENTS.md", "# Review job\n")
    write(f"{j}/PROGRESS.md", "# Progress\n\n## Done\n")
    for s in ("document", "code-and-data"):
        write(f"{j}/review/{s}-REPORT.md", rep)
    write(f"{j}/review/statements-REPORT.md", rep + textwrap.dedent("""
        | Statement | Centrality | Holds |
        |---|---|---|
        | 100 participants | primary | holds |
        """))
    write(f"{j}/review/challenge-REPORT.md",
          "# Challenge\n\n(a) r\n(b) e\n(c) c\n(d) n\n(e) a\n(f) n\n(g) c\n")
    write(f"{j}/work/scripts/arith.R", "1+1\n")
    write(f"{j}/work/logs/ss.log", "N = 100\n")
    ad, acd, ast = f"{j}/analysis/document", f"{j}/analysis/code-and-data", f"{j}/analysis/statements"
    write(f"{ad}/consistency-matrix.csv",
          "element,product,protocol,sap,sse,registry,other,status,evidence\n"
          "primary endpoint,score at week 12 (p. 1),score at week 12 (s. 8),,,,,consistent,extracts\n")
    write(f"{ad}/arithmetic-checks.csv",
          "id,location,quantity,printed,inputs,recomputed,method,script,result,note\n"
          "A1,p. 1,randomised N,100,84 / 0.9,93.3,inflate,work/scripts/arith.R,match,\n")
    write(f"{ad}/sensitivity-claims.csv",
          "claim,location,cited_exhibit,scenarios_covered,classification,evidence\n"
          "N is driven by the effect,p. 3,Table 4,all,SUPPORTED,work/logs/ss.log\n")
    write(f"{acd}/spec-map.csv",
          "printed_ref,element,printed_value,code_ref,code_value,status,discrepancy\n"
          "p. 2,alpha,0.05,example_SSE001.qmd:40,0.05,identical,\n")
    write(f"{acd}/feasibility-matrix.csv",
          "exhibit,required_inputs,input_status,runs_under_data_mode\nTable 4,planning values,in job,yes\n")
    write(f"{acd}/construction-ledger.md", "# Construction ledger\n\n- alpha 0.05\n")
    write(f"{acd}/battery-manifest.csv",
          "id,family,hypothesis,spec,data_mode,artifact,seed,state,validity,row_role,notes\n"
          "B1,N,recompute N,closed form,none,work/logs/ss.log,NA,done,clean,verdict-bearing,\n"
          "B2,report,printed table,needs data,none,NA,NA,data_not_shared,clean,verdict-bearing,\n")
    write(f"{acd}/results.csv",
          "record_type,spec_id,family,quantity,data_mode,printed_value,printed_location,estimate,"
          "std_error,ci_low,ci_high,p_value,n,method,seed,state,validity,row_role,artifact,notes\n"
          "RES,B1,N,N,none,100,p. 1,100,,,,,,closed form,NA,done,clean,verdict-bearing,"
          "work/logs/ss.log,\n")
    write(f"{acd}/module-walk.md", MODULE_WALK)
    write(f"{acd}/sample-size-diagnostics-REPORT.md", rep)
    write(f"{acd}/simulation-diagnostics-REPORT.md", rep)
    for m in ("estimand-diagnostics", "rct-diagnostics", "missing-data-diagnostics",
              "time-to-event-diagnostics", "multiplicity-diagnostics",
              "regression-model-diagnostics", "observational-diagnostics",
              "prediction-model-diagnostics", "bayesian-diagnostics", "small-n-diagnostics"):
        write(f"{acd}/{m}-REPORT.md", "Status: NOT_APPLICABLE — no such feature\n")
    write(f"{acd}/assumption-ledger.csv",
          "id,assumption,value,location,source_cited,source_checked,warrant,effect_on_N,artifact,note\n"
          "A1,control rate,0.40,p. 2,none,no,UNANCHORED,+20 at 0.35,work/logs/ss.log,\n")
    write(f"{ast}/statement-ledger.csv",
          "row_id,kind,statement,location,centrality,holds,kernel,not_established,"
          "strongest_defence,defence_tested,status,evidence\n"
          "ST01,calculation,100 participants give 80% power,p. 1,primary,holds,100 gives 80%,,,"
          "no,settled,work/logs/ss.log\n"
          "ST02,assumption,control rate 0.40,p. 2,supporting,not established,none,the source,"
          "pilot data,no,settled,assumption-ledger\n")
    write(f"{ast}/questions.csv",
          "q_id,question,answer,basis,status,evidence\n"
          "Q1,Is the sample size driven mainly by the treatment effect?,Yes,ST01,answered,log\n"
          "Q2,Should non-proportional hazards be discussed?,No,ST01,answered,log\n")
    write(f"{ast}/driver-matrix.csv", "driver_id,statement\nDR1,ST01\n")
    write(f"{j}/SYNTHESIS.md", SYNTHESIS)
    return j

