import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import annotate_source  # noqa: E402
import check_issue_coverage  # noqa: E402
import issues as iss  # noqa: E402
import render_review  # noqa: E402

SYNTHESIS = """\
# Synthesis — Example trial (ex26Test1, rev. 100)

Verification: OPEN · 1 not established / 1 narrower / 1 hold

## Status

COMPLETE.

## What the product establishes and what it does not

Bottom line.

## Cross-cutting findings

None.

## Statement ledger

| Statement (location) | Kind | Centrality | Holds | Kernel | Not established | Strongest defence | Status |
|---|---|---|---|---|---|---|---|
| "N = 100 gives 80% power" (Summary, p. 1; ST01) | calculation | primary | holds | x | — | — | settled |
| "dropout 10% gives 100" (p. 3; ST02) | calculation | primary | narrower | 94 needed | formula | — | settled |
| "control rate 0.40" (p. 2; ST03) | assumption | supporting | not established | none | source | — | settled |

## Recomputation table

None.

## Answers to the assignment questions

### Q1. Is N driven by the effect?

Yes.

basis: ST01
status: answered

### Q2. What about competing risks?

The documents do not say.

basis: none
status: cannot be answered from the materials

## Data and reproducibility

None.

## Findings

### F1. The control rate has no source
bears on: the control rate (ST03)
where: text
evidence: x

Body.

fix: cite it.

### F2. Dropout formula multiplies instead of dividing
bears on: the randomised N (ST02)
where: text and code
evidence: y

Body.

fix: divide.

### F3. A caption shows 0.58
bears on: the planning values (ST01)
where: text
evidence: z

Body.

fix: correct the caption.

## Limits of this review

Data not shared.

## Counts

None.
"""

ISSUES = """\
---
product: Example trial SSE (ex26Test1, rev. 100)
statistical-product: example_SSE001.pdf
status: COMPLETE
depth: standard
data-mode: none
date: 2026-10-27
---

## Assignment

- Name of the statistical product: example_SSE001.pdf
- Important issues for reviewer:
  1. Is N driven by the effect?
  2. What about competing risks?
- Other documents this document depends on:
  - Study protocol v1

## General comments

The sample size is reproduced; the control rate needs a source.

## Issues

### 1. The control-group rate has no source
severity: Major
change: text
clarification: no
category: Sample size
evidence: established
location: Table 3, p. 2
anchor: 01_product/example.qmd:12
sources: SYNTHESIS.md

The rate of 0.40 is stated without a source.

Fix: cite the source.

### 2. The dropout allowance multiplies instead of dividing
severity: Major
change: text and code
clarification: no
category: Sample size
evidence: established
location: Statistical comparison framework, p. 3
anchor: 01_product/example.qmd:5
sources: SYNTHESIS.md

84 × 1.10 = 92.4; 84 / 0.90 = 93.3.

### 3. A figure caption shows 0.58
severity: Minor
change: text
clarification: no
category: Numerical consistency
evidence: established
location: Figure 1 caption, p. 4
sources: SYNTHESIS.md

The caption says 0.58; the text and code use 0.57.

## Answers to the assignment

### Q1. Is N driven by the effect?

Yes: the effect moves N most.

status: answered

### Q2. What about competing risks?

The documents do not say how deaths are handled.

status: cannot be answered from the materials

## Not checked

- Patient data were not shared.
"""

COVERAGE = """\
`ST02` → issue 2 ("dropout allowance")
`ST03` → issue 1 ("control-group rate")
`F1` → issue 1 ("control-group rate")
`F2` → issue 2 ("dropout allowance")
`F3` → issue 3 ("figure caption")
"""

QMD = """---
title: x
---

Text line five.

```{r}
#| label: sim
x <- 1
y <- 2
z <- 3
res <- 4
```
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def make(tmp, issues=ISSUES, coverage=COVERAGE):
    j = str(tmp)
    write(f"{j}/SYNTHESIS.md", SYNTHESIS)
    write(f"{j}/ISSUES.md", issues)
    write(f"{j}/ISSUES.coverage.md", coverage)
    write(f"{j}/01_product/example.qmd", QMD)
    return j


def test_parse_issues(tmp_path):
    j = make(tmp_path)
    led = iss.read_issues(f"{j}/ISSUES.md")
    assert [i["number"] for i in led["issues"]] == [1, 2, 3]
    assert led["issues"][1]["fields"]["change"] == "text and code"
    assert led["issues"][0]["body"].startswith("The rate of 0.40")
    assert led["answers"][1]["status"] == "cannot be answered from the materials"
    assert "Name of the statistical product" in led["sections"]["assignment"]


def test_parse_synthesis(tmp_path):
    j = make(tmp_path)
    syn = iss.read_synthesis(f"{j}/SYNTHESIS.md")
    assert {r["id"]: r["holds"] for r in syn["rows"]} == {
        "ST01": "holds", "ST02": "narrower", "ST03": "not established"}
    assert syn["blocks"]["F2"]["where"] == "text and code"
    assert syn["blocks"]["F1"]["statements"] == ["ST03"]
    assert [q["q"] for q in syn["questions"]] == [1, 2]


def test_decision_boxes(tmp_path):
    j = make(tmp_path)
    led = iss.read_issues(f"{j}/ISSUES.md")
    ticks = [t for t, _ in iss.decision(led["issues"], led["answers"])]
    # minor text (issue 3), major text (1, 2), no minor code, major code (2), clarification (Q2)
    assert ticks == [True, True, False, True, True]


def test_default_severity():
    assert iss.default_severity([{"holds": "not established", "centrality": "supporting"}]) == "Major"
    assert iss.default_severity([{"holds": "narrower", "centrality": "primary"}]) == "Major"
    assert iss.default_severity([{"holds": "narrower", "centrality": "supporting"}]) == "Minor"
    assert iss.default_severity([]) == "Minor"


def test_coverage_passes(tmp_path, capsys):
    j = make(tmp_path)
    assert check_issue_coverage.main([f"{j}/ISSUES.md"]) == 0, capsys.readouterr().out


def test_coverage_missing_disposition_fails(tmp_path, capsys):
    j = make(tmp_path, coverage=COVERAGE.replace('`F3` → issue 3 ("figure caption")\n', ""))
    assert check_issue_coverage.main([f"{j}/ISSUES.md"]) == 1
    assert "`F3` has no disposition" in capsys.readouterr().out


def test_primary_row_cannot_go_to_not_checked(tmp_path, capsys):
    cov = COVERAGE.replace('`ST02` → issue 2 ("dropout allowance")', "`ST02` → not checked")
    j = make(tmp_path, coverage=cov)
    assert check_issue_coverage.main([f"{j}/ISSUES.md"]) == 1
    assert "must map to an issue" in capsys.readouterr().out


def test_severity_departure_needs_reason(tmp_path, capsys):
    j = make(tmp_path, issues=ISSUES.replace("severity: Major\nchange: text\n",
                                             "severity: Minor\nchange: text\n", 1))
    assert check_issue_coverage.main([f"{j}/ISSUES.md"]) == 1
    out = capsys.readouterr().out
    assert "departs from the default Major without severity-reason" in out
    j2 = make(tmp_path / "b", issues=ISSUES.replace(
        "severity: Major\nchange: text\n",
        "severity: Minor\nseverity-reason: the source exists, only the citation is missing\nchange: text\n", 1))
    assert check_issue_coverage.main([f"{j2}/ISSUES.md"]) == 0


def test_change_must_cover_where(tmp_path, capsys):
    j = make(tmp_path, issues=ISSUES.replace("change: text and code", "change: text"))
    check_issue_coverage.main([f"{j}/ISSUES.md"])
    assert "does not cover where = code, text" in capsys.readouterr().out


def test_bad_vocabulary_fails(tmp_path, capsys):
    j = make(tmp_path, issues=ISSUES.replace("category: Numerical consistency", "category: Typos"))
    assert check_issue_coverage.main([f"{j}/ISSUES.md"]) == 1
    assert "category = 'Typos'" in capsys.readouterr().out


def test_render_preview_and_form(tmp_path, capsys):
    j = make(tmp_path)
    assert render_review.main([f"{j}/ISSUES.md", "--org"]) == 0
    md = open(f"{j}/CONSISTENCY_REVIEW.md", encoding="utf-8").read()
    assert "> **Preview, not final:**" in md
    assert "- [x] Statistical product needs minor changes in the text" in md
    assert "- [ ] Statistical product needs minor changes in the R programming" in md
    assert "- [x] Clarifications required" in md
    major = md.split("### Major issues")[1].split("### Minor issues")[0]
    assert "The control-group rate has no source" in major and "figure caption" not in major
    assert "[text and R code]" in major
    org = open(f"{j}/CONSISTENCY_REVIEW.org", encoding="utf-8").read()
    assert org.startswith("*** CONSISTENCY REVIEW\n**** Assignment")
    assert "***** Answer to issues listed in 'Assignment'" in org
    assert "- [X] Statistical product needs major changes in the text" in org
    page = open(f"{j}/CONSISTENCY_REVIEW.html", encoding="utf-8").read()
    assert page.startswith("<!doctype html>") and "&#9746;" in page or "checkbox" in page


def test_finalize_refuses_without_gate_records(tmp_path, capsys):
    j = make(tmp_path)
    assert render_review.main([f"{j}/ISSUES.md", "--finalize"]) == 1
    out = capsys.readouterr().out
    assert "ISSUES.facts.md has no gate record" in out
    assert not os.path.exists(f"{j}/CONSISTENCY_REVIEW.md")


def test_finalize_with_gate_records(tmp_path, capsys):
    j = make(tmp_path)
    sha = iss.sha256_file(f"{j}/ISSUES.md")
    write(f"{j}/ISSUES.facts.md", f"gate: fresh-context — 2026-10-27 — sha256:{sha[:12]}\n")
    with open(f"{j}/ISSUES.coverage.md", "a", encoding="utf-8") as fh:
        fh.write(f"gate: fresh-context — 2026-10-27 — sha256:{sha[:12]}\n")
    assert render_review.main([f"{j}/ISSUES.md", "--finalize"]) == 0, capsys.readouterr().out
    md = open(f"{j}/CONSISTENCY_REVIEW.md", encoding="utf-8").read()
    assert "Preview" not in md and "final=yes" in md


def test_finalize_refuses_full_depth_without_handoff(tmp_path, capsys):
    j = make(tmp_path, issues=ISSUES.replace("depth: standard", "depth: full"))
    sha = iss.sha256_file(f"{j}/ISSUES.md")
    write(f"{j}/ISSUES.facts.md", f"gate: x — sha256:{sha[:12]}\n")
    with open(f"{j}/ISSUES.coverage.md", "a", encoding="utf-8") as fh:
        fh.write(f"gate: x — sha256:{sha[:12]}\n")
    assert render_review.main([f"{j}/ISSUES.md", "--finalize"]) == 1
    assert "HANDOFF.manifest.json" in capsys.readouterr().out


def test_simple_markdown_converter():
    page = render_review.simple_md("# T\n\n- [x] done\n- [ ] open\n\n1. **A** (p. 2)\n\n   Body `x`.\n\n> note\n")
    assert "<h1>T</h1>" in page and "&#9746; done" in page and "&#9744; open" in page
    assert "<ol><li><strong>A</strong> (p. 2)<p>Body <code>x</code>.</p></li></ol>" in page
    assert "<blockquote>" in page


def test_annotate_source(tmp_path, capsys):
    j = make(tmp_path)
    assert annotate_source.main([f"{j}/ISSUES.md"]) == 0
    out = open(f"{j}/work/annotated/example.REVIEW.qmd", encoding="utf-8").read().split("\n")
    assert out[3].startswith("<!-- REVIEW: annotated copy")
    i5 = out.index("Text line five.")
    assert out[i5 - 1] == "<!-- REVIEW (Major 2): The dropout allowance multiplies instead of dividing -->"
    i12 = out.index("res <- 4")
    assert out[i12 - 1] == "# REVIEW (Major 1): The control-group rate has no source"
    assert open(f"{j}/01_product/example.qmd", encoding="utf-8").read() == QMD


def test_form_labels_number_within_severity():
    issues = [{"fields": {"severity": s}} for s in ("Major", "Minor", "Major", "minor")]
    assert iss.form_labels(issues) == ["Major 1", "Minor 1", "Major 2", "Minor 2"]


def test_form_length_limit_for_a_short_product(tmp_path, capsys):
    j = make(tmp_path)
    os.makedirs(f"{j}/review", exist_ok=True)
    with open(f"{j}/review/intake-scan.json", "w", encoding="utf-8") as fh:
        json.dump({"pdfs": [{"path": "01_product/example.pdf", "pages": "2"}]}, fh)
    assert check_issue_coverage.main([f"{j}/ISSUES.md"]) == 0, capsys.readouterr().out
    text = open(f"{j}/ISSUES.md", encoding="utf-8").read()
    text = text.replace("## Answers to the assignment", "Padding " + "word " * 1400 + "\n\n## Answers to the assignment", 1)
    with open(f"{j}/ISSUES.md", "w", encoding="utf-8") as fh:
        fh.write(text)
    assert check_issue_coverage.main([f"{j}/ISSUES.md"]) == 1
    assert "the form for a short product" in capsys.readouterr().out


def test_simple_md_wrapped_number_is_not_a_list():
    # a body line that wraps to begin with "147)" continues the paragraph (only a list
    # starting at 1 may interrupt one), so the reference is kept and no list starts
    page = render_review.simple_md("1. **Dropout** (p. 2)\n\n   Randomising 66 per group (qmd:76,\n"
                                   "   147) leaves 52.8 evaluable.\n\n   Fix: divide by 0.8.\n")
    assert "(qmd:76, 147) leaves 52.8 evaluable." in page
    assert 'start="147"' not in page and page.count("<ol") == 1
    top = render_review.simple_md("Text that ends (see\n12) for detail.\n\n1. a list\n")
    assert "<p>Text that ends (see 12) for detail.</p>" in top and "<ol><li>a list</li></ol>" in top


def test_simple_md_bullet_continuation_stays_in_its_sentence():
    page = render_review.simple_md("- The cited sources were not\n  provided, so they were not checked.\n"
                                   "- Second limit.\n")
    assert page == "<ul><li>The cited sources were not provided, so they were not checked.</li>" \
                   "<li>Second limit.</li></ul>"
    nested = render_review.simple_md("1. Item text\n   - sub one\n   - sub two\n2. Next item\n")
    assert nested == "<ol><li>Item text<ul><li>sub one</li><li>sub two</li></ul></li><li>Next item</li></ol>"
