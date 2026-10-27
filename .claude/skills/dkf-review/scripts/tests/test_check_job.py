import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest  # noqa: E402

import check_job  # noqa: E402
from jobfixture import make_job, write  # noqa: E402


@pytest.fixture
def job(tmp_path):
    return make_job(tmp_path / "job")


def gate(root, stage="all", capsys=None):
    code = check_job.main(["--root", str(root), "--stage", stage])
    out = capsys.readouterr().out if capsys else ""
    return code, out


def edit(path, old, new):
    text = open(path, encoding="utf-8").read()
    assert old in text, old
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new))


def test_complete_job_passes(job, capsys):
    code, out = gate(job, capsys=capsys)
    assert code == 0, out
    assert "PASS" in out


def test_header_only_ledger_fails(job, capsys):
    p = os.path.join(job, "analysis/document/sensitivity-claims.csv")
    write(p, "claim,location,cited_exhibit,scenarios_covered,classification,evidence\n")
    code, out = gate(job, "document", capsys)
    assert code == 1 and "D4" in out and "header-only" in out


def test_none_found_beside_rows_fails(job, capsys):
    p = os.path.join(job, "analysis/document/sensitivity-claims.csv")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("none,,,,NONE_FOUND,searched robust/similar\n")
    code, out = gate(job, "document", capsys)
    assert code == 1 and "NONE_FOUND appears beside" in out


def test_arithmetic_script_must_exist(job, capsys):
    edit(os.path.join(job, "analysis/document/arithmetic-checks.csv"),
         "work/scripts/arith.R", "work/scripts/missing.R")
    code, out = gate(job, "document", capsys)
    assert code == 1 and "missing.R" in out


def test_report_product_needs_sap_adherence(tmp_path, capsys):
    j = make_job(tmp_path / "job", ptype="report")
    code, out = gate(j, "document", capsys)
    assert code == 1 and "sap-adherence.csv is missing" in out


def test_spec_map_needs_file_line(job, capsys):
    edit(os.path.join(job, "analysis/code-and-data/spec-map.csv"),
         "example_SSE001.qmd:40", "the setup chunk")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "not file:line" in out


def test_synthetic_check_in_none_mode_fails(job, capsys):
    edit(os.path.join(job, "analysis/code-and-data/battery-manifest.csv"),
         "B1,N,recompute N,closed form,none", "B1,N,recompute N,closed form,synthetic")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "a `synthetic` check in a job whose data mode is `none`" in out


def test_synthetic_result_with_printed_value_fails(tmp_path, capsys):
    j = make_job(tmp_path / "job", mode="synthetic")
    edit(os.path.join(j, "analysis/code-and-data/results.csv"),
         "RES,B1,N,N,none,100", "RES,B1,N,N,synthetic,100")
    code, out = gate(j, "code-and-data", capsys)
    assert code == 1 and "synthetic runs are never compared" in out


def test_done_row_needs_results_row(job, capsys):
    p = os.path.join(job, "analysis/code-and-data/results.csv")
    lines = open(p, encoding="utf-8").read().splitlines()
    write(p, lines[0] + "\n")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "no results.csv row" in out


def test_fired_module_with_stub_fails(job, capsys):
    write(os.path.join(job, "analysis/code-and-data/simulation-diagnostics-REPORT.md"),
          "Status: NOT_APPLICABLE — none\n")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "NOT_APPLICABLE stub" in out


def test_not_run_module_only_at_quick_depth(job, capsys):
    edit(os.path.join(job, "analysis/code-and-data/module-walk.md"),
         "- small-n-diagnostics: not applicable (no such feature)",
         "- small-n-diagnostics: NOT_RUN — depth quick")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "only depth quick skips" in out
    j2 = make_job(os.path.join(os.path.dirname(job), "quick"), depth="quick")
    edit(os.path.join(j2, "analysis/code-and-data/module-walk.md"),
         "- small-n-diagnostics: not applicable (no such feature)",
         "- small-n-diagnostics: NOT_RUN — depth quick")
    assert gate(j2, "code-and-data", capsys)[0] == 0


def test_assumption_effect_required(job, capsys):
    edit(os.path.join(job, "analysis/code-and-data/assumption-ledger.csv"),
         "UNANCHORED,+20 at 0.35", "UNANCHORED,")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "effect_on_N is empty" in out


def test_statement_ledger_enums_and_ids(job, capsys):
    p = os.path.join(job, "analysis/statements/statement-ledger.csv")
    edit(p, "ST02,assumption", "S2,assumption")
    edit(p, "supporting,not established", "supporting,refuted")
    code, out = gate(job, "statements", capsys)
    assert code == 1
    assert "is not ST<number>" in out and "'refuted'" in out


def test_question_rows_must_match(job, capsys):
    p = os.path.join(job, "analysis/statements/questions.csv")
    lines = open(p, encoding="utf-8").read().splitlines()
    write(p, "\n".join(lines[:2]) + "\n")
    code, out = gate(job, "statements", capsys)
    assert code == 1 and "1 rows for 2 assignment questions" in out


def test_challenge_required_at_standard_depth(job, capsys):
    os.remove(os.path.join(job, "review/challenge-REPORT.md"))
    code, out = gate(job, "challenge", capsys)
    assert code == 1 and "INTERIM" in out


def test_quick_depth_needs_no_challenge(tmp_path, capsys):
    j = make_job(tmp_path / "job", depth="quick")
    os.remove(os.path.join(j, "review/challenge-REPORT.md"))
    code, out = gate(j, "challenge", capsys)
    assert code == 0 and "WARN" in out


def test_synthesis_counts_must_match_ledger(job, capsys):
    edit(os.path.join(job, "SYNTHESIS.md"), "1 not established / 0 narrower / 1 hold",
         "0 not established / 0 narrower / 2 hold")
    code, out = gate(job, "verdict", capsys)
    assert code == 1 and "header counts" in out


def test_synthesis_sections_in_order(job, capsys):
    p = os.path.join(job, "SYNTHESIS.md")
    text = open(p, encoding="utf-8").read()
    text = text.replace("## Limits of this review\n\nNone.\n\n", "")
    text = text.replace("## Status", "## Limits of this review\n\nNone.\n\n## Status")
    write(p, text)
    code, out = gate(job, "verdict", capsys)
    assert code == 1 and "out of order" in out


def test_finding_needs_where_and_fix(job, capsys):
    edit(os.path.join(job, "SYNTHESIS.md"), "where: text", "where: the caption")
    edit(os.path.join(job, "SYNTHESIS.md"), "fix: cite the source of 0.40.", "")
    code, out = gate(job, "verdict", capsys)
    assert code == 1
    assert "lacks `fix:`" in out and "expected text, code" in out


def test_synthesis_must_carry_every_ledger_row(job, capsys):
    p = os.path.join(job, "SYNTHESIS.md")
    text = open(p, encoding="utf-8").read()
    write(p, re.sub(r"(?m)^\| \"control rate.*\n", "", text))
    code, out = gate(job, "verdict", capsys)
    assert code == 1 and "lacks rows: ST02" in out
