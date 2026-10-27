import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest  # noqa: E402

import jobfiles as jf  # noqa: E402
import scan_job  # noqa: E402
from jobfixture import make_job, write  # noqa: E402


@pytest.fixture
def job(tmp_path):
    return make_job(tmp_path / "job")


def scan(root):
    code = scan_job.main(["--root", str(root)])
    with open(os.path.join(str(root), "review", "intake-scan.json"), encoding="utf-8") as fh:
        return code, json.load(fh)


def test_valid_job_passes(job):
    code, rep = scan(job)
    assert code == 0, rep["clearance"]
    assert rep["settings"] == {"product_type": "sse", "data_mode": "none", "depth": "standard",
                               "non_patient_files": ["dat/calc.rds"]}
    assert rep["assignment"]["questions"][0].startswith("Is the sample size")
    assert rep["assignment"]["dependencies"] == [
        "Study protocol: 02_governing/protocol_v1_2026-01-01.pdf"]


def test_quarto_source_is_read(job):
    _, rep = scan(job)
    q = rep["quarto_sources"][0]
    assert q["params"]["internal-dkf-id"] == "ex26Test1"
    assert q["params"]["final-product-risk"] == {}
    assert q["svn_id"]["revision"] == "100"
    opts = {(f["chunk"], f["option"]) for f in q["flagged_chunk_options"]}
    assert ("sim", "eval: false") in opts and ("setup", "include: false") in opts
    assert {"line": 29, "call": "readRDS", "target": "dat/calc.rds"} in q["files_read"]
    dplyr = [p for p in q["packages"] if p["package"] == "dplyr"][0]
    assert dplyr["date"] == "2026-06-24"
    assert q["inline_r"] == 1
    assert q["set_seed"] and q["set_seed"][0]["code"] == "set.seed(42)"


def test_missing_assignment_fails(tmp_path):
    write(str(tmp_path / "01_product" / "a.qmd"), "---\ntitle: x\n---\n")
    code, rep = scan(tmp_path)
    assert code == 1
    assert "00_ASSIGNMENT.md is missing" in rep["clearance"]["errors"][0]


def test_unlisted_data_file_fails(tmp_path):
    j = make_job(tmp_path / "job", npf="none")
    code, rep = scan(j)
    assert code == 1
    assert any("UNCLEARED DATA: 01_product/dat/calc.rds" in e for e in rep["clearance"]["errors"])


def test_data_folder_needs_shared_mode(job):
    write(os.path.join(job, "04_data", "trial.csv"), "id\n1\n")
    code, rep = scan(job)
    assert code == 1
    assert any("04_data" in e and "`none`" in e for e in rep["clearance"]["errors"])


def test_synthetic_folder_needs_synthetic_mode(job):
    write(os.path.join(job, "05_synthetic", "codebook.csv"), "var\nx\n")
    code, rep = scan(job)
    assert code == 1
    j2 = make_job(os.path.join(os.path.dirname(job), "job2"), mode="synthetic")
    write(os.path.join(j2, "05_synthetic", "codebook.csv"), "var\nx\n")
    assert scan(j2)[0] == 0


def test_shared_mode_needs_data_clearance(tmp_path):
    j = make_job(tmp_path / "job", mode="shared", clearance="not applicable")
    code, rep = scan(j)
    assert code == 1
    assert any("Data clearance" in e for e in rep["clearance"]["errors"])
    j2 = make_job(tmp_path / "job2", mode="shared",
                  clearance="PI and DPO approved anonymised extract, DTA 2026-01")
    write(os.path.join(j2, "04_data", "trial.csv"), "id\n1\n")
    assert scan(j2)[0] == 0


def test_placeholders_fail(tmp_path):
    j = make_job(tmp_path / "job", ptype="<sse | protocol | sap | report | manuscript | other>",
                 mode="<none | synthetic | shared>")
    code, rep = scan(j)
    assert code == 1
    errs = " ".join(rep["clearance"]["errors"])
    assert "Product type" in errs and "Data mode" in errs


def test_data_files_are_hashed_never_parsed(job):
    _, rep = scan(job)
    item = [i for i in rep["inventory"] if i["path"].endswith("calc.rds")][0]
    assert item["class"] == "data-like" and len(item["sha256"]) == 64


def test_review_folders_are_not_inventoried(job):
    _, rep = scan(job)
    assert not any(i["path"].startswith(("review", "analysis", "work"))
                   for i in rep["inventory"])


def test_front_matter_parser_handles_lists_and_blocks():
    fm = jf.front_matter("---\ntitle: 'A: B'\nauthor:\n  - name: X\n  - Y\nabstract: |\n"
                         "  line one: with colon\n  line two\nparams:\n  a: 1\n  b:\n---\nbody")
    assert fm["title"] == "A: B"
    assert fm["author"] == ["name: X", "Y"]
    assert fm["abstract"] == "line one: with colon line two"
    assert fm["params"] == {"a": "1", "b": {}}
