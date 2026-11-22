"""Runs the R test suite for the synthetic-data assets when Rscript is installed."""
import os
import shutil
import subprocess

import pytest

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.skipif(shutil.which("Rscript") is None, reason="Rscript not installed")
def test_synthetic_r():
    r = subprocess.run(["Rscript", os.path.join(SKILL, "scripts", "tests", "test_synthetic.R"),
                        os.path.join(SKILL, "assets")],
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.strip().endswith("PASS")
