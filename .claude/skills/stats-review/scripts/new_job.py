#!/usr/bin/env python3
"""new_job.py — create a stats-review job folder.

    python3 new_job.py <job folder> [--product FILE_OR_DIR ...] [--governing FILE ...]
                                    [--previous FILE ...] [--lit FILE ...]

Creates the packet layout (01_product/, 02_governing/, 03_previous/, lit/), copies
the files given into it, and writes 00_ASSIGNMENT.md from the template for the
operator to fill in. It never creates 04_data/ or 05_synthetic/ (those need a data
mode that clears them) and never overwrites an existing assignment.

A product given as a directory is copied whole (the Quarto source refers to its files
by relative path); single files are copied into 01_product/.
"""
import argparse
import os
import shutil
import sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL, "assets", "ASSIGNMENT-template.md")
GITIGNORE = os.path.join(SKILL, "assets", "job-gitignore")


def copy_into(src, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    if os.path.isdir(src):
        for name in os.listdir(src):
            s = os.path.join(src, name)
            d = os.path.join(dest_dir, name)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        return f"{src}/ -> {dest_dir}/"
    shutil.copy2(src, dest_dir)
    return f"{src} -> {dest_dir}/"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("job")
    ap.add_argument("--product", nargs="*", default=[])
    ap.add_argument("--governing", nargs="*", default=[])
    ap.add_argument("--previous", nargs="*", default=[])
    ap.add_argument("--lit", nargs="*", default=[])
    a = ap.parse_args(argv)

    for f in a.product + a.governing + a.previous + a.lit:
        if not os.path.exists(f):
            print(f"no such file: {f}", file=sys.stderr)
            return 2
    job = os.path.abspath(a.job)
    for d in ("01_product", "02_governing", "03_previous", "lit"):
        os.makedirs(os.path.join(job, d), exist_ok=True)
    done = []
    for files, d in ((a.product, "01_product"), (a.governing, "02_governing"),
                     (a.previous, "03_previous"), (a.lit, "lit")):
        for f in files:
            done.append(copy_into(f, os.path.join(job, d)))
    assignment = os.path.join(job, "00_ASSIGNMENT.md")
    if os.path.exists(assignment):
        done.append("00_ASSIGNMENT.md exists: left unchanged")
    else:
        shutil.copy2(TEMPLATE, assignment)
        done.append("00_ASSIGNMENT.md written from the template")
    ignore = os.path.join(job, ".gitignore")
    if os.path.exists(ignore):
        done.append(".gitignore exists: left unchanged")
    else:
        shutil.copy2(GITIGNORE, ignore)
        done.append(".gitignore written: copies of the product, literature and data stay out "
                    "of any commit")
    print(f"Job folder: {job}")
    for line in done:
        print(f"  {line}")
    print("Next: fill in 00_ASSIGNMENT.md (product type, questions, clearance, data mode,\n"
          "depth), then run\n"
          f"  python3 {os.path.join(SKILL, 'scripts', 'scan_job.py')} --root {job}\n"
          "and ask the agent to review the product with the stats-review skill.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
