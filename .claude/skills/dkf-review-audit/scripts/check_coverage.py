#!/usr/bin/env python3
"""check_coverage.py — completeness over the product's printed surface and its source,
not just the review's own index. Adapted from the upstream research_skills
audit-review script for Quarto/R statistical products.

Run from anywhere:   python3 check_coverage.py --root <job>   (writes coverage.csv)

FAIL rows (exit 1) — fix by doing the missing work, or rule the item not applicable
with a reason in coverage-na.csv (`ref,reason`):

1. PRINTED SURFACE. Every `Table <id>` and `Figure <id>` in the rendered product's
   text (review/extracts/ dumps of 01_product PDFs, else pdftotext of the PDFs in
   01_product/) must be named in a ledger (analysis/**.csv) — the arithmetic checks,
   specification map, sensitivity claims, consistency matrix, manifest, results or
   statement ledger. Named only in a report: WARN (confirm it was checked).
2. SOURCE SURFACE. Every R chunk of the product's Quarto source (by label, or
   `chunk@<line>` when unlabelled) must be named in the specification map, a ledger,
   a report or a log under work/logs/: a chunk never named was never read.
3. FILES READ. Every file the code reads (review/intake-scan.json) must be named in
   analysis/code-and-data/feasibility-matrix.csv or a report.
4. NO SURFACE. No readable product text and no Quarto source FAILs: an unenumerated
   surface is not a covered one.

Exit 0 on PASS, 1 on FAIL.
"""
import argparse
import csv
import glob
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "dkf-review", "scripts"))
import jobfiles as jf  # noqa: E402

REF = re.compile(r"\b(Table|Figure|Fig\.)\s+((?:[A-Z]\.?)?\d+[A-Za-z]?)\b")
CHUNK_OPEN = re.compile(r"^\s*```+\s*\{\s*r\b([^}]*)\}\s*$", re.I)
CHUNK_CLOSE = re.compile(r"^\s*```+\s*$")
LABEL_OPT = re.compile(r"^\s*#\|\s*label\s*:\s*(\S+)")


def product_text(root):
    texts = []
    for p in sorted(glob.glob(os.path.join(root, "review", "extracts", "*01_product*"))) + \
            sorted(glob.glob(os.path.join(root, "review", "extracts", "product*"))):
        texts.append(open(p, encoding="utf-8", errors="replace").read())
    if texts:
        return "\n".join(texts)
    if shutil.which("pdftotext"):
        for p in sorted(glob.glob(os.path.join(root, "01_product", "**", "*.pdf"), recursive=True)):
            r = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True)
            texts.append(r.stdout)
    return "\n".join(texts)


def norm_ref(kind, ident):
    kind = "Figure" if kind.lower().startswith("fig") else "Table"
    return f"{kind} {ident.replace('.', '')}"


def printed_refs(text):
    return sorted({norm_ref(k, i) for k, i in REF.findall(text)},
                  key=lambda r: (r.split()[0], [int(x) if x.isdigit() else x
                                                for x in re.split(r"(\d+)", r.split()[1])]))


def chunks(qmd_path, root):
    out = []
    lines = open(qmd_path, encoding="utf-8", errors="replace").read().splitlines()
    inside, label, start = False, None, 0
    for n, line in enumerate(lines, 1):
        if not inside:
            m = CHUNK_OPEN.match(line)
            if m:
                inside, start = True, n
                header = m.group(1).strip(" ,")
                first = header.split(",")[0].strip() if header else ""
                label = first if first and "=" not in first else None
            continue
        lm = LABEL_OPT.match(line)
        if lm:
            label = lm.group(1).strip("'\"")
            continue
        if CHUNK_CLOSE.match(line):
            out.append({"ref": label or f"chunk@{start}", "file": os.path.relpath(qmd_path, root),
                        "line": start, "end": n, "labelled": bool(label)})
            inside = False
    return out


def corpus(root, pattern_dirs):
    """{relpath: text} for ledgers, reports and logs."""
    out = {}
    for pat in pattern_dirs:
        for p in glob.glob(os.path.join(root, pat), recursive=True):
            if os.path.isfile(p):
                out[os.path.relpath(p, root)] = open(p, encoding="utf-8", errors="replace").read()
    return out


def mentioned(ref, texts):
    kind, ident = (ref.split(" ", 1) + [""])[:2] if ref.startswith(("Table ", "Figure ")) else (None, None)
    if kind:
        pats = [rf"\b{kind}\s*{re.escape(ident)}\b"]
        if kind == "Figure":
            pats.append(rf"\bFig\.?\s*{re.escape(ident)}\b")
        if kind == "Table":
            pats.append(rf"\bTab\.?\s*{re.escape(ident)}\b")
        rx = re.compile("|".join(pats), re.I)
    else:
        rx = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(ref)}(?![A-Za-z0-9_-])")
    return [p for p, t in texts.items() if rx.search(t)]


def chunk_mentioned(c, texts):
    """A chunk counts as named when a text says `chunk <label>`, `<label> chunk`,
    `` `<label>` ``, `label: <label>`, `chunk@<line>`, or cites `<file>:<n>` with n inside
    the chunk. A bare word such as "setup" in prose does not count."""
    lab = re.escape(c["ref"])
    base = re.escape(os.path.basename(c["file"]))
    rx = re.compile(rf"chunk[\s`'\"(]*{lab}\b|\b{lab}[`'\"]?\s+chunk|`{lab}`|label:\s*{lab}\b"
                    if c["labelled"] else rf"\b{lab}\b", re.I)
    lines = re.compile(rf"{base}:(\d+)")
    hits = []
    for p, t in texts.items():
        if rx.search(t) or any(c["line"] <= int(m) <= c["end"] for m in lines.findall(t)):
            hits.append(p)
    return hits


def load_na(path):
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as fh:
        return {r["ref"].strip(): r.get("reason", "").strip() for r in csv.DictReader(fh)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--na", default=None, help="default <root>/coverage-na.csv")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    na = load_na(a.na or os.path.join(root, "coverage-na.csv"))
    ledgers = corpus(root, ["analysis/**/*.csv"])
    reports = corpus(root, ["review/*-REPORT*.md", "analysis/**/*.md", "SYNTHESIS.md"])
    logs = corpus(root, ["work/logs/**/*"])
    rows, fails, warns = [], [], []

    def record(kind, ref, status, where, note=""):
        if status == "FAIL" and ref in na:
            status, note = "NA", na[ref] or "ruled not applicable"
            if not na[ref]:
                fails.append(f"{kind} {ref}: coverage-na.csv gives no reason")
        rows.append({"surface": kind, "ref": ref, "status": status,
                     "where": "; ".join(where[:4]), "note": note})
        if status == "FAIL":
            fails.append(f"{kind} {ref}: {note}")
        elif status == "WARN":
            warns.append(f"{kind} {ref}: {note}")

    text = product_text(root)
    qmds = [p for p in glob.glob(os.path.join(root, "01_product", "**", "*"), recursive=True)
            if p.lower().endswith((".qmd", ".rmd"))]
    if not text.strip() and not qmds:
        fails.append("no readable product text and no Quarto source: nothing to cover")

    for ref in printed_refs(text):
        led = mentioned(ref, ledgers)
        if led:
            record("printed", ref, "OK", led)
        else:
            rep = mentioned(ref, reports)
            if rep:
                record("printed", ref, "WARN", rep, "named only in reports; confirm it was checked")
            else:
                record("printed", ref, "FAIL", [], "named in no ledger or report")

    everything = {**ledgers, **reports, **logs}
    for q in qmds:
        for c in chunks(q, root):
            where = chunk_mentioned(c, everything)
            if where:
                record("chunk", c["ref"], "OK", where)
            else:
                record("chunk", c["ref"], "FAIL", [],
                       f"{c['file']}:{c['line']} is named in no ledger, report or log")

    scan_path = os.path.join(root, "review", "intake-scan.json")
    if os.path.exists(scan_path):
        scan = json.load(open(scan_path, encoding="utf-8"))
        feas = {k: v for k, v in ledgers.items() if k.endswith("feasibility-matrix.csv")}
        for src in scan.get("quarto_sources", []):
            for fr in src.get("files_read", []):
                target = str(fr.get("target", ""))
                if not target:
                    continue
                base = os.path.basename(target)
                hit = [p for p, t in {**feas, **reports}.items() if target in t or base in t]
                record("file read", target, "OK" if hit else "FAIL", hit,
                       "" if hit else f"read at {src['path']}:{fr.get('line')} but in no "
                                      "feasibility row or report")
    else:
        warns.append("review/intake-scan.json missing: files read by the code not checked "
                     "(run dkf-review's scan_job.py)")

    with open(os.path.join(root, "coverage.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["surface", "ref", "status", "where", "note"])
        w.writeheader()
        w.writerows(rows)
    for wmsg in warns:
        print(f"WARN {wmsg}")
    for f in fails:
        print(f"FAIL {f}")
    n = {s: sum(1 for r in rows if r["status"] == s) for s in ("OK", "WARN", "FAIL", "NA")}
    print(f"{'FAIL' if fails else 'PASS'}: {len(rows)} items — {n['OK']} covered, "
          f"{n['WARN']} warn, {n['FAIL']} uncovered, {n['NA']} not applicable; wrote coverage.csv")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
