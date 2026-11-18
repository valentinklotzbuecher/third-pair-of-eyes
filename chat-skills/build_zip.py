#!/usr/bin/env python3
"""Build the upload ZIP of each chat skill in this folder.

Claude chat takes a skill as a ZIP whose top level is the skill's folder, named as the
skill. Run after any change to a skill folder, from anywhere:

    python3 chat-skills/build_zip.py

Entries are sorted and carry a fixed timestamp, so an unchanged folder rebuilds to the
same contents; caches and editor files are left out. Standard library only.
"""
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_PARTS = {"__pycache__", ".pytest_cache"}
SKIP_NAMES = {".DS_Store", "Thumbs.db"}
STAMP = (1980, 1, 1, 0, 0, 0)


def skill_files(folder):
    """The files of a skill folder that belong in its ZIP, in a stable order."""
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder)
        if (p.is_file() and not SKIP_PARTS.intersection(rel.parts)
                and p.name not in SKIP_NAMES and p.suffix != ".pyc"):
            yield p


def build(folder, out):
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in skill_files(folder):
            info = zipfile.ZipInfo(f"{folder.name}/{p.relative_to(folder).as_posix()}", STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())


def main():
    skills = [d for d in sorted(HERE.iterdir()) if (d / "SKILL.md").is_file()]
    for d in skills:
        out = HERE / f"{d.name}.zip"
        build(d, out)
        print(f"wrote {out.relative_to(HERE.parent)}")
    return 0 if skills else 1


if __name__ == "__main__":
    sys.exit(main())
