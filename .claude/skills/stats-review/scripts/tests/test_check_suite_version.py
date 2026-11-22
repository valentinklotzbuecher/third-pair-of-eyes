#!/usr/bin/env python3
"""Tests for check_suite_version.py.

Ported from the upstream research_skills test. Run with pytest or unittest.
"""
import subprocess
import sys
sys.dont_write_bytecode = True  # never leave __pycache__ in the skill folder
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_suite_version.py"
HEADER = "id,version,date,kind,scope,requirement,source,removed,note\n"
ROWS = ("R001,0.1,2026-09-12,baseline,stats-review,Requirement history begins.,stats-review/SKILL.md,,\n"
        "R002,0.2,2026-09-22,added,module:small-n-diagnostics,Report the MDE.,"
        "stats-review/modules/small-n-diagnostics/SKILL.md,,\n")
SUITE = ("stats-review", "stats-review-audit", "stats-consistency-review", "stats-synthetic-data")


def skill(name, version):
    meta = f'metadata:\n  version: "{version}"\n' if version else ""
    return f"---\nname: {name}\ndescription: x\n{meta}---\n\n# {name}\n"


class SuiteVersionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.make("0.2", "0.2", "0.2", "0.2")

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, *versions, rows=ROWS):
        for name, v in zip(SUITE, versions):
            (self.root / name).mkdir(exist_ok=True)
            (self.root / name / "SKILL.md").write_text(skill(name, v))
        (self.root / "stats-review/spec-changes.csv").write_text(HEADER + rows)

    def run_check(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True)

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.root), *args], check=True,
                       capture_output=True)

    def test_pass_without_git(self):
        r = self.run_check("--no-git")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_versions_must_agree(self):
        self.make("0.2", "0.2", "0.2", "0.1")
        r = self.run_check("--no-git")
        self.assertEqual(r.returncode, 1)
        self.assertIn("versions differ", r.stdout)

    def test_missing_version(self):
        self.make("0.2", None, "0.2", "0.2")
        r = self.run_check("--no-git")
        self.assertIn("stats-review-audit/SKILL.md: no metadata.version", r.stdout)

    def test_row_newer_than_suite(self):
        self.make("0.1", "0.1", "0.1", "0.1")
        r = self.run_check("--no-git")
        self.assertIn("newer than the suite version", r.stdout)

    def test_bad_rows(self):
        self.make("0.2", "0.2", "0.2", "0.2", rows=ROWS + "R002,0.x,2026-13-01,tweak,review,,x,2026-01-01,\n")
        out = self.run_check("--no-git").stdout
        for msg in ("duplicate id", "unparseable", "not YYYY-MM-DD", "kind 'tweak'",
                    "empty requirement"):
            self.assertIn(msg, out)

    def test_removed_before_added(self):
        self.make("0.2", "0.2", "0.2", "0.2", rows=ROWS + "R003,0.2,2026-09-22,added,review,x,x,2026-09-01,\n")
        self.assertIn("removed before it was added", self.run_check("--no-git").stdout)

    def test_change_after_tag_needs_bump(self):
        self.git("init", "-q")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x")
        self.git("tag", "skills-v0.2")
        self.assertEqual(self.run_check().returncode, 0)
        (self.root / "stats-review/new.md").write_text("new rule\n")
        r = self.run_check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("suite changed since skills-v0.2", r.stdout)
        self.make("0.2.1", "0.2.1", "0.2.1", "0.2.1")
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("skills-v0.2.1 is not tagged yet", r.stdout)

    def test_version_older_than_tag(self):
        self.git("init", "-q")
        self.git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                 "--allow-empty", "-m", "x")
        self.git("tag", "skills-v0.5")
        r = self.run_check()
        self.assertIn("older than tag skills-v0.5", r.stdout)


if __name__ == "__main__":
    unittest.main()
