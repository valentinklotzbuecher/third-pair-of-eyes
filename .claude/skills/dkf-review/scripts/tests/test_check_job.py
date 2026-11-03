import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest  # noqa: E402

import check_job  # noqa: E402
import jobfiles as jf  # noqa: E402
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
         "| small-n-diagnostics | not applicable | no such feature |",
         "| small-n-diagnostics | not run — depth quick | quick |")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "only depth quick skips" in out
    j2 = make_job(os.path.join(os.path.dirname(job), "quick"), depth="quick")
    edit(os.path.join(j2, "analysis/code-and-data/module-walk.md"),
         "| small-n-diagnostics | not applicable | no such feature |",
         "| small-n-diagnostics | not run — depth quick | quick |")
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


def test_verdict_may_move_a_row_that_names_its_evidence(job, capsys):
    p = os.path.join(job, "SYNTHESIS.md")
    edit(p, "1 not established / 0 narrower / 1 hold", "1 not established / 1 narrower / 0 hold")
    edit(p, "| primary | holds | 100 gives 80% | — | — | settled |",
         "| primary | narrower | 100 gives 80% at the stated rate | moved: work/logs/rate.log | — | settled |")
    code, out = gate(job, "verdict", capsys)
    assert code == 0, out


def test_moved_row_must_name_its_evidence(job, capsys):
    p = os.path.join(job, "SYNTHESIS.md")
    edit(p, "1 not established / 0 narrower / 1 hold", "1 not established / 1 narrower / 0 hold")
    edit(p, "| primary | holds | 100 gives 80% | — | — | settled |",
         "| primary | narrower | 100 gives 80% at the stated rate | — | — | settled |")
    code, out = gate(job, "verdict", capsys)
    assert code == 1 and "moves from 'holds' to 'narrower'" in out


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


def test_intake_records_required(job, capsys):
    os.remove(os.path.join(job, "00_INTAKE.md"))
    os.remove(os.path.join(job, "PROGRESS.md"))
    code, out = gate(job, "document", capsys)
    assert code == 1
    assert "00_INTAKE.md is missing" in out and "PROGRESS.md is missing" in out


def test_intake_numbers_questions(job, capsys):
    edit(os.path.join(job, "00_INTAKE.md"), "Q2. Should", "2. Should")
    code, out = gate(job, "intake", capsys)
    assert code == 1 and "question Q2" in out


def test_report_sections_and_finding_fields(job, capsys):
    p = os.path.join(job, "review/document-REPORT.md")
    edit(p, "## Scope assumptions\n\nNone.\n\n", "")
    edit(p, "bears on: the control rate (ST02)\n", "")
    edit(p, "fix: cite it.\n", "")
    code, out = gate(job, "document", capsys)
    assert code == 1
    assert "no `## Scope assumptions` section" in out
    assert "lacks `bears on:`" in out
    assert "WARN" in out and "lacks `fix:`" in out


def test_within_band_needs_tolerance(job, capsys):
    p = os.path.join(job, "analysis/document/arithmetic-checks.csv")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("A2,Table 5,power,81%,MC,80.6%,simulation,work/scripts/arith.R,within-band,\n")
    code, out = gate(job, "document", capsys)
    assert code == 1 and "within-band without the band" in out


def test_consistency_unverified_here_accepted(job, capsys):
    edit(os.path.join(job, "analysis/document/consistency-matrix.csv"), ",consistent,", ",unverified-here,")
    code, out = gate(job, "document", capsys)
    assert code == 0, out


def test_fired_module_report_needs_sections(job, capsys):
    write(os.path.join(job, "analysis/code-and-data/simulation-diagnostics-REPORT.md"),
          "# Simulation\n\n## Status\n\nCOMPLETE\n\n## Findings\n\nNone.\n")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "simulation-diagnostics-REPORT.md has no `## Coverage`" in out


def test_module_walk_reads_the_decision_cell_only(job, capsys):
    # "not run here" and "plan/analysis" in the evidence text do not change the decision
    code, out = gate(job, "code-and-data", capsys)
    assert code == 0, out


def test_module_walk_list_format_and_unknown_decision(job, capsys):
    p = os.path.join(job, "analysis/code-and-data/module-walk.md")
    edit(p, "| bayesian-diagnostics | not applicable | no such feature |",
         "- bayesian-diagnostics: not applicable — no priors")
    assert gate(job, "code-and-data", capsys)[0] == 0
    edit(p, "| observational-diagnostics | not applicable |", "| observational-diagnostics | maybe |")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "decision for observational-diagnostics is 'maybe'" in out


def test_module_walk_missing_row(job, capsys):
    p = os.path.join(job, "analysis/code-and-data/module-walk.md")
    edit(p, "| prediction-model-diagnostics | not applicable | no such feature |\n", "")
    code, out = gate(job, "code-and-data", capsys)
    assert code == 1 and "no row for prediction-model-diagnostics" in out


def short_product(root, pages=2):
    write(os.path.join(root, "review/intake-scan.json"),
          json.dumps({"pdfs": [{"path": "01_product/example.pdf", "pages": str(pages)}]}))


def test_size_class_from_intake_scan(job):
    assert jf.size_class(job) in ("short", "long")
    short_product(job, 2)
    assert jf.size_class(job) == "short"
    short_product(job, 25)
    assert jf.size_class(job) == "long"
    os.remove(os.path.join(job, "review/intake-scan.json"))
    assert jf.size_class(job) == "long"


def test_long_report_fails_only_for_a_short_product(job, capsys):
    p = os.path.join(job, "review/document-REPORT.md")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("\n" + "word " * 2000 + "\n")
    short_product(job, 2)
    code, out = gate(job, "document", capsys)
    assert code == 1 and "a stage report for a short product" in out
    short_product(job, 40)
    code, out = gate(job, "document", capsys)
    assert "a stage report for a" not in out


def test_long_synthesis_fails_for_a_short_product(job, capsys):
    short_product(job, 2)
    with open(os.path.join(job, "SYNTHESIS.md"), "a", encoding="utf-8") as fh:
        fh.write("\n" + "word " * 4000 + "\n")
    code, out = gate(job, "verdict", capsys)
    assert code == 1 and "V2" in out and "a synthesis for a short product" in out
