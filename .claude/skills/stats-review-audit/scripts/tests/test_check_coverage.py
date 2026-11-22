import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import check_coverage  # noqa: E402

QMD = """---
title: x
---

```{r setup, include=FALSE}
library(stats)
```

```{r}
#| label: sim
res <- readRDS("dat/calc.rds")
```

```{r}
x <- 1
```
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def make(tmp, covered=True):
    j = str(tmp)
    write(f"{j}/01_product/p.qmd", QMD)
    write(f"{j}/review/extracts/01_product_p.txt",
          "Summary\nTable 1: Planning values\nAs shown in Table 2 and Figure 1.\n")
    write(f"{j}/review/intake-scan.json", json.dumps({"quarto_sources": [
        {"path": "01_product/p.qmd", "files_read": [{"line": 11, "call": "readRDS",
                                                     "target": "dat/calc.rds"}]}]}))
    write(f"{j}/analysis/document/arithmetic-checks.csv",
          "id,location,quantity\nA1,Table 1,N\n" + ("A2,Table 2 row 3,power\n" if covered else ""))
    write(f"{j}/analysis/code-and-data/spec-map.csv",
          "printed_ref,element,code_ref\nFigure 1,curve,p.qmd:9 (chunk sim)\n"
          + ("Table 1,setup,p.qmd:5 (chunk setup)\nsummary,x,p.qmd:15 (chunk@14)\n" if covered else ""))
    write(f"{j}/analysis/code-and-data/feasibility-matrix.csv",
          "exhibit,required_inputs,input_status,runs_under_data_mode\n"
          + ("Figure 1,dat/calc.rds,in job,yes\n" if covered else ""))
    write(f"{j}/review/document-REPORT.md", "## Status\n\n## Findings\n")
    return j


def rows(j):
    with open(os.path.join(j, "coverage.csv"), newline="", encoding="utf-8") as fh:
        return {(r["surface"], r["ref"]): r for r in csv.DictReader(fh)}


def test_full_coverage_passes(tmp_path, capsys):
    j = make(tmp_path)
    assert check_coverage.main(["--root", j]) == 0, capsys.readouterr().out
    r = rows(j)
    assert r[("printed", "Table 2")]["status"] == "OK"
    assert r[("chunk", "chunk@14")]["status"] == "OK"
    assert r[("file read", "dat/calc.rds")]["status"] == "OK"


def test_uncovered_items_fail(tmp_path, capsys):
    j = make(tmp_path, covered=False)
    assert check_coverage.main(["--root", j]) == 1
    out = capsys.readouterr().out
    assert "printed Table 2" in out and "chunk setup" in out and "chunk chunk@14" in out
    assert "file read dat/calc.rds" in out


def test_na_ruling_needs_reason(tmp_path, capsys):
    j = make(tmp_path, covered=False)
    write(f"{j}/coverage-na.csv", "ref,reason\nTable 2,\nsetup,library loading only\n"
          "chunk@14,trivial\ndat/calc.rds,checked in the simulation module report\n")
    assert check_coverage.main(["--root", j]) == 1
    out = capsys.readouterr().out
    assert "Table 2: coverage-na.csv gives no reason" in out
    assert "chunk setup" not in out.replace("Table 2", "")


def test_report_only_mention_warns(tmp_path, capsys):
    j = make(tmp_path)
    write(f"{j}/review/extracts/01_product_p.txt", "Table 1 Table 2 Figure 1 Table 3\n")
    write(f"{j}/review/document-REPORT.md", "## Status\n\nTable 3 was read.\n## Findings\n")
    assert check_coverage.main(["--root", j]) == 0
    assert "WARN printed Table 3" in capsys.readouterr().out


def test_bare_word_does_not_cover_a_chunk(tmp_path, capsys):
    j = make(tmp_path)
    write(f"{j}/analysis/code-and-data/spec-map.csv",
          "printed_ref,element,code_ref\nFigure 1,curve,p.qmd:9 (chunk sim)\n"
          "Table 1,the setup of the trial,somewhere\nsummary,x,p.qmd:15 (chunk@14)\n")
    assert check_coverage.main(["--root", j]) == 1
    assert "chunk setup" in capsys.readouterr().out


def test_file_line_inside_chunk_covers_it(tmp_path, capsys):
    j = make(tmp_path)
    write(f"{j}/analysis/code-and-data/spec-map.csv",
          "printed_ref,element,code_ref\nFigure 1,curve,p.qmd:10\n"
          "Table 1,alpha,p.qmd:6\nsummary,x,p.qmd:15\n")
    assert check_coverage.main(["--root", j]) == 0, capsys.readouterr().out
