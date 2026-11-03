#!/usr/bin/env python3
"""annotate_source.py — write REVIEW comments into a copy of the product's Quarto
source, the way DKF reviewers annotate a .qmd ("see REVIEW comments in qmd file").

    python3 annotate_source.py ISSUES.md [--out-dir work/annotated]

For every issue with an `anchor:` field (one or more `path:line` separated by `;`,
paths from the job root, e.g. `01_product/SSE001.qmd:342`), a comment is inserted
above that line in a copy of the file:

    inside an R chunk:   # REVIEW (Minor 1): <title>
    in prose or YAML:    <!-- REVIEW (Major 2): <title> -->

The label is the issue's number in the rendered form (Major and Minor issues are
numbered separately), so a comment points at the form's item.

The copy goes to <out-dir>/<file name with .REVIEW before the extension>; the
delivered product is never edited. A note under the front matter says the copy is
annotated. Anchors that point outside the file are reported and skipped.
"""
import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issues as iss  # noqa: E402

CHUNK_OPEN = re.compile(r"^\s*```+\s*\{\s*([A-Za-z]+)")
FENCE = re.compile(r"^\s*```+")


def chunk_engine_by_line(lines):
    """[engine or None] per line: the engine of the chunk the line sits in."""
    out, engine = [], None
    for ln in lines:
        if engine is None:
            m = CHUNK_OPEN.match(ln)
            out.append(None)
            if m:
                engine = m.group(1).lower()
            continue
        if FENCE.match(ln):
            out.append(None)
            engine = None
            continue
        out.append(engine)
    return out


def front_matter_end(lines):
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return i + 1
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ledger")
    ap.add_argument("--out-dir", default=None, help="default <job>/work/annotated")
    a = ap.parse_args(argv)
    ledger = os.path.abspath(a.ledger)
    root = os.path.dirname(ledger)
    out_dir = a.out_dir or os.path.join(root, "work", "annotated")
    led = iss.read_issues(ledger)
    label_of = {id(i): lab for i, lab in zip(led["issues"], iss.form_labels(led["issues"]))}
    anchors = {}
    for i in led["issues"]:
        for anc in re.split(r"\s*;\s*", i["fields"].get("anchor", "").strip()):
            m = re.match(r"^(.+?):(\d+)$", anc)
            if not m:
                continue
            anchors.setdefault(m.group(1), []).append((int(m.group(2)), i))
    if not anchors:
        print("no anchors in the ledger: nothing to annotate")
        return 0
    os.makedirs(out_dir, exist_ok=True)
    problems = 0
    for rel, items in anchors.items():
        src = os.path.join(root, rel)
        if not os.path.exists(src):
            print(f"SKIP {rel}: no such file")
            problems += 1
            continue
        lines = open(src, encoding="utf-8").read().split("\n")
        engines = chunk_engine_by_line(lines)
        for line_no, issue in sorted(items, key=lambda t: -t[0]):
            if not 1 <= line_no <= len(lines):
                print(f"SKIP {rel}:{line_no}: outside the file ({len(lines)} lines)")
                problems += 1
                continue
            text = f"REVIEW ({label_of[id(issue)]}): {issue['title']}"
            eng = engines[line_no - 1]
            target = lines[line_no - 1]
            pad = target[:len(target) - len(target.lstrip())]
            if eng in ("r", "python"):
                comment = f"{pad}# {text}"
            else:
                comment = f"<!-- {text.replace('--', '-')} -->"
            lines.insert(line_no - 1, comment)
        fm = front_matter_end(lines)
        note = (f"<!-- REVIEW: annotated copy written {datetime.date.today().isoformat()} by "
                f"dkf-consistency-review from {os.path.basename(ledger)}; the delivered file is "
                "unchanged. -->")
        lines.insert(fm, note)
        base, ext = os.path.splitext(os.path.basename(rel))
        dest = os.path.join(out_dir, f"{base}.REVIEW{ext}")
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"wrote {os.path.relpath(dest, root)} ({len(items)} comments)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
