#!/usr/bin/env python3
"""scan_job.py — intake scan and clearance guard for a stats-review job.

Run from anywhere before the review opens any file:

    python3 scan_job.py --root <job> [--out review/intake-scan.json]

What it does (standard library only; it never reads the contents of a data file —
data files are listed by name, size and sha256 only):

1. Reads 00_ASSIGNMENT.md: product, product type, questions, dependencies,
   clearance (`Documents:`, `Data mode:`, `Non-patient files:`, `Data clearance:`),
   depth.
2. Inventories the packet (00_*, 01_product/, 02_governing/, 03_previous/, 04_data/,
   05_synthetic/, lit/ and anything else outside the review's own review/,
   analysis/ and work/ folders), classifying data-like files by extension.
3. Applies the clearance guard (references/data-access.md):
   - mode `none`: data-like files only inside 01_product/ and only if listed under
     `Non-patient files:`; 04_data/ and 05_synthetic/ must be empty;
   - mode `synthetic`: additionally anything in 05_synthetic/; 04_data/ empty;
   - mode `shared`: additionally anything in 04_data/, and `Data clearance:` filled.
4. Reads the Quarto sources in 01_product/: front matter (title, author, date,
   params including the dkfreporting product fields), an SVN `$Id$` line, chunk
   labels and the chunk options worth auditing (eval: false, cache: true,
   error: true, warning: false, message: false, include: false), package loading
   (groundhog dates, renv), set.seed lines, files the code reads, inline `r` count.
5. Reads PDF metadata with `pdfinfo` (when installed): title, author, creation
   date, pages, the R and package versions the DKF template writes into Keywords,
   and a footer revision (`rev. N`) from `pdftotext`.
6. Compares the source's SVN revision with the PDF's footer revision.

Writes review/intake-scan.json and prints a summary.
Exit 0 = clearance OK; 1 = clearance or assignment failure (stop the run);
2 = usage error.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jobfiles as jf  # noqa: E402

SUITE_VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SKILL.md")

CHUNK_OPEN = re.compile(r"^\s*```+\s*\{\s*([A-Za-z]+)([^}]*)\}\s*$")
CHUNK_CLOSE = re.compile(r"^\s*```+\s*$")
OPT_LINE = re.compile(r"^\s*#\|\s*([A-Za-z.\-]+)\s*:\s*(.*?)\s*$")
AUDIT_OPTS = {
    "eval": {"false"}, "cache": {"true"}, "error": {"true"},
    "warning": {"false"}, "message": {"false"}, "include": {"false"},
}
READ_CALL = re.compile(
    r"\b(readRDS|read_rds|load|read\.csv|read_csv|read\.table|read_delim|fread|"
    r"read_excel|read_xlsx|read_sav|read_dta|read_sas|read_parquet|read_feather|"
    r"source)\s*\(\s*([^)]*)\)")
STRING_ARG = re.compile(r"""["']([^"']+)["']""")


def suite_version():
    try:
        text = open(SUITE_VERSION_FILE, encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r'^\s*version:\s*"?([0-9][^"\s]*)"?', text, re.M)
    return m.group(1) if m else None


def sha256(path, limit=None):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def walk_packet(root):
    """[(relpath, size, is_dir_infra)] for every file outside the review's folders."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        parts = [] if rel_dir == "." else rel_dir.split(os.sep)
        if parts and parts[0] in jf.REVIEW_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = sorted(d for d in dirnames
                             if not (not parts and d in jf.REVIEW_DIRS))
        infra = any(p in jf.INFRA_DIRS for p in parts)
        for name in sorted(filenames):
            rel = os.path.normpath(os.path.join(rel_dir, name))
            out.append((rel, os.path.getsize(os.path.join(dirpath, name)), infra))
    return out


def classify(rel, infra):
    ext = os.path.splitext(rel)[1].lower()
    if infra:
        return "infrastructure"
    if ext in jf.DATA_EXTENSIONS:
        return "data-like"
    if ext in (".qmd", ".rmd", ".r", ".py", ".sas", ".do", ".yml", ".yaml", ".bib",
               ".tex", ".scss", ".css", ".lua"):
        return "source"
    if ext in (".pdf", ".docx", ".doc", ".html", ".htm", ".md", ".txt", ".pptx"):
        return "document"
    if ext in (".png", ".jpg", ".jpeg", ".svg", ".gif", ".tif", ".tiff"):
        return "image"
    return "other"


def top(rel):
    return rel.split(os.sep)[0]


def listed_non_patient(rel, listed):
    """True when `rel` (inside 01_product/) matches a `Non-patient files:` entry, by
    path relative to 01_product/, by path from the job root, or by basename."""
    inner = rel.split(os.sep, 1)[1] if os.sep in rel else rel
    for entry in listed:
        e = os.path.normpath(entry.replace("/", os.sep))
        if e in (inner, rel) or os.path.basename(e) == os.path.basename(rel) \
                and os.sep not in e:
            return True
        if e.endswith(os.sep + "*") and inner.startswith(e[:-1]):
            return True
    return False


def clearance(assign, inventory):
    errors, warnings = [], []
    if assign is None:
        errors.append("00_ASSIGNMENT.md is missing: copy assets/ASSIGNMENT-template.md "
                      "into the job root and fill it in.")
        return errors, warnings
    ptype = jf.product_type(assign)
    if ptype not in jf.PRODUCT_TYPES:
        errors.append(f"Product type is {ptype!r}; expected one of {', '.join(jf.PRODUCT_TYPES)}.")
    mode = jf.data_mode(assign)
    if mode not in jf.DATA_MODES:
        errors.append(f"Data mode is {mode!r}; expected one of {', '.join(jf.DATA_MODES)}.")
    if not jf.field(assign, "documents"):
        errors.append("Clearance `Documents:` is empty: state what may be sent to the "
                      "model provider and who cleared it.")
    dc = jf.field(assign, "data_clearance")
    if mode == "shared" and (not dc or dc.lower() in ("not applicable", "n/a", "none")):
        errors.append("Data mode `shared` needs `Data clearance:` naming who approved "
                      "processing of which data by which provider, on what basis.")
    if not jf.field(assign, "depth"):
        warnings.append("Depth not set: using `standard`.")
    elif jf.field(assign, "depth").lower() not in jf.DEPTHS:
        warnings.append(f"Depth {jf.field(assign, 'depth')!r} not recognised: using `standard`.")
    if not jf.field(assign, "statistical_product"):
        warnings.append("`Statistical product:` is empty.")
    if not assign.get("questions"):
        warnings.append("No questions under 'Important issues for reviewer'.")
    if mode not in jf.DATA_MODES:
        return errors, warnings

    listed = jf.non_patient_files(assign)
    for item in inventory:
        rel, kind, t = item["path"], item["class"], top(item["path"])
        if t == "04_data" and mode != "shared":
            errors.append(f"UNCLEARED DATA: {rel} ({item['size']} bytes) is in 04_data/ "
                          f"but the data mode is `{mode}`.")
            continue
        if t == "05_synthetic" and mode == "none":
            errors.append(f"UNCLEARED DATA: {rel} is in 05_synthetic/ but the data mode is "
                          "`none`; set `Data mode: synthetic` if it is synthetic.")
            continue
        if kind != "data-like":
            continue
        if t == "04_data" and mode == "shared":
            continue
        if t == "05_synthetic" and mode in ("synthetic", "shared"):
            continue
        if t == "01_product" and listed_non_patient(rel, listed):
            continue
        errors.append(f"UNCLEARED DATA: {rel} ({item['size']} bytes) is data-like and not "
                      "cleared. If it holds no patient data, list it under "
                      "`Non-patient files:`; otherwise move it out of the job.")
    for entry in listed:
        hit = [i for i in inventory if i["path"].startswith("01_product")
               and listed_non_patient(i["path"], [entry])]
        if not hit:
            warnings.append(f"`Non-patient files:` lists {entry!r}, which is not in 01_product/.")
    return errors, warnings


def scan_qmd(path, root):
    text = open(path, encoding="utf-8", errors="replace").read()
    fm = jf.front_matter(text)
    rec = {"path": os.path.relpath(path, root), "title": fm.get("title"),
           "author": fm.get("author"), "date": fm.get("date"),
           "params": fm.get("params") if isinstance(fm.get("params"), dict) else {},
           "formats": sorted(fm["format"].keys()) if isinstance(fm.get("format"), dict)
           else fm.get("format"),
           "execute": fm.get("execute") if isinstance(fm.get("execute"), dict) else {}}
    m = re.search(r"\$Id:\s+(\S+)\s+(\d+)\s+(\d{4}-\d{2}-\d{2})\s+(\S+)\s+(\S+)\s+\$", text)
    rec["svn_id"] = ({"file": m.group(1), "revision": m.group(2), "date": m.group(3),
                      "time": m.group(4), "user": m.group(5)} if m else None)
    chunks, flagged, seeds, packages, reads = [], [], [], [], []
    strings = dict(re.findall(r"^\s*([A-Za-z_.][A-Za-z0-9_.]*)\s*(?:<-|=)\s*[\"']([^\"']+)[\"']",
                              text, re.M))
    in_chunk, cur = False, None
    for n, line in enumerate(text.splitlines(), 1):
        if not in_chunk:
            mo = CHUNK_OPEN.match(line)
            if mo:
                in_chunk = True
                header = mo.group(2)
                lab = re.search(r"(?:^|,)\s*([A-Za-z0-9_.-]+)\s*(?:,|$)", header.strip(", "))
                cur = {"engine": mo.group(1).lower(), "start": n,
                       "label": lab.group(1) if lab and "=" not in lab.group(1) else None,
                       "options": {}}
                for k, v in re.findall(r"([A-Za-z.]+)\s*=\s*([A-Za-z]+)", header):
                    cur["options"][k.replace(".", "-")] = v.lower()
            continue
        if CHUNK_CLOSE.match(line):
            cur["end"] = n
            chunks.append(cur)
            for k, v in cur["options"].items():
                if v in AUDIT_OPTS.get(k, ()):
                    flagged.append({"chunk": cur["label"], "line": cur["start"],
                                    "option": f"{k}: {v}"})
            in_chunk, cur = False, None
            continue
        om = OPT_LINE.match(line)
        if om:
            key = om.group(1).replace(".", "-")
            cur["options"][key] = om.group(2).strip().lower()
            if key == "label":
                cur["label"] = om.group(2).strip()
            continue
        if cur["engine"] != "r":
            continue
        code = line.split("#", 1)[0]
        if "set.seed" in code:
            seeds.append({"line": n, "code": code.strip()})
        g = re.search(r"groundhog\.library\(\s*[\"']?([^,\"')]+)[\"']?\s*,\s*(?:date\s*=\s*)?"
                      r"([^)]+)\)", code)
        if g:
            gdate = g.group(2).strip().strip("\"'")
            packages.append({"line": n, "package": g.group(1).strip(),
                             "loader": "groundhog", "date": strings.get(gdate, gdate)})
        else:
            for lib in re.findall(r"\b(?:library|require)\(\s*[\"']?([A-Za-z0-9.]+)", code):
                packages.append({"line": n, "package": lib, "loader": "library"})
        gd = re.search(r"\bgh_date\s*(?:<-|=)\s*[\"']([0-9-]+)[\"']", code)
        if gd:
            packages.append({"line": n, "package": "(groundhog date)", "loader": "groundhog",
                             "date": gd.group(1)})
        for call, args in READ_CALL.findall(code):
            lit = STRING_ARG.search(args)
            first = args.split(",")[0].strip()
            target = lit.group(1) if lit else strings.get(first, first[:80])
            reads.append({"line": n, "call": call, "target": target})
    rec["chunks"] = [{"label": c["label"], "engine": c["engine"], "lines": [c["start"], c.get("end")]}
                     for c in chunks]
    rec["n_chunks"] = len(chunks)
    rec["flagged_chunk_options"] = flagged
    rec["set_seed"] = seeds
    rec["packages"] = packages
    rec["files_read"] = reads
    rec["inline_r"] = len(re.findall(r"`r\s+[^`]+`", text))
    rec["unfilled_params"] = unfilled_params(rec["params"])
    fname = rec["params"].get("file-name") if isinstance(rec["params"], dict) else None
    stem = os.path.splitext(os.path.basename(path))[0]
    rec["file_name_param_mismatch"] = bool(fname) and isinstance(fname, str) and fname != stem
    return rec


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def unfilled_params(params):
    """Template parameters that look unfilled: a value that repeats its own key
    (`study-hra-category: 'HRA Category'`), a `<…>` placeholder, or TBD/XXX."""
    out = []
    for k, v in (params or {}).items():
        if not isinstance(v, str) or not v.strip():
            continue
        nv, nk = _norm(v), _norm(k)
        if re.fullmatch(r"\s*<[^>]*>\s*", v) or nv in ("tbd", "xxx", "todo", "tba") or \
                (len(nv) >= 6 and nk.endswith(nv)):
            out.append(k)
    return out


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def scan_pdf(path, root):
    rec = {"path": os.path.relpath(path, root)}
    if shutil.which("pdfinfo"):
        info = {}
        for line in run(["pdfinfo", path]).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                info[k.strip()] = v.strip()
        for k in ("Title", "Author", "Subject", "Creator", "CreationDate", "ModDate", "Pages"):
            if k in info:
                rec[k.lower()] = info[k]
        kw = info.get("Keywords", "") or info.get("Producer", "")
        m = re.search(r"R version (\S+)(?: \(([^)]*)\))?(?: with packages (.*))?", kw)
        if m:
            rec["r_version"] = m.group(1)
            rec["r_release_date"] = m.group(2)
            if m.group(3):
                rec["packages"] = [p.strip() for p in m.group(3).split(",") if p.strip()]
    else:
        rec["note"] = "pdfinfo not installed: metadata not read"
    if shutil.which("pdftotext"):
        text = run(["pdftotext", "-layout", path, "-"])
        m = re.search(r"\brev\.?\s*(\d{3,})", text)
        rec["footer_revision"] = m.group(1) if m else None
        rec["text_chars"] = len(text)
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None, help="default: <root>/review/intake-scan.json")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        print(f"no such job folder: {root}", file=sys.stderr)
        return 2

    assign = jf.read_assignment(root)
    inventory = []
    for rel, size, infra in walk_packet(root):
        kind = classify(rel, infra)
        item = {"path": rel, "size": size, "class": kind}
        if kind != "infrastructure":
            item["sha256"] = sha256(os.path.join(root, rel))
        inventory.append(item)
    errors, warnings = clearance(assign, inventory)

    unplaced = [i["path"] for i in inventory
                if os.sep not in i["path"] and not i["path"].startswith("00_")
                and i["path"] not in ("AGENTS.md", "PROGRESS.md", "SYNTHESIS.md",
                                      "ISSUES.md", "CONSISTENCY_REVIEW.md",
                                      "CONSISTENCY_REVIEW.html", "CHANGELOG.md",
                                      "HANDOFF.md", "HANDOFF.manifest.json")
                and not i["path"].startswith(("ISSUES.", "CONSISTENCY_REVIEW"))]
    if unplaced:
        warnings.append("Files at the job root to move into the packet layout: "
                        + ", ".join(unplaced))
    product = [i for i in inventory if top(i["path"]) == "01_product"]
    if not product:
        errors.append("01_product/ is empty: the rendered product or its source is required.")

    qmds = [scan_qmd(os.path.join(root, i["path"]), root) for i in inventory
            if top(i["path"]) == "01_product" and i["path"].lower().endswith((".qmd", ".rmd"))
            and i["class"] != "infrastructure"]
    pdfs = [scan_pdf(os.path.join(root, i["path"]), root) for i in inventory
            if top(i["path"]) in ("01_product", "02_governing", "03_previous")
            and i["path"].lower().endswith(".pdf")]

    checks = {}
    prod_pdfs = [p for p in pdfs if p["path"].startswith("01_product")]
    for q in qmds:
        if q.get("file_name_param_mismatch"):
            warnings.append(f"{q['path']}: the `file-name` parameter "
                            f"({q['params'].get('file-name')!r}) differs from the file's name; "
                            "the product was renamed after it was rendered (the working copy may "
                            "need the original name, logged as a repair).")
        if q.get("unfilled_params"):
            warnings.append(f"{q['path']}: template parameters that look unfilled: "
                            + ", ".join(q["unfilled_params"]))
    svn = [q["svn_id"] for q in qmds if q.get("svn_id")]
    if svn and prod_pdfs:
        revs = {p.get("footer_revision") for p in prod_pdfs if p.get("footer_revision")}
        if revs:
            checks["revision_match"] = svn[0]["revision"] in revs
            checks["source_revision"] = svn[0]["revision"]
            checks["pdf_footer_revisions"] = sorted(revs)
            if not checks["revision_match"]:
                warnings.append(f"The source's SVN revision {svn[0]['revision']} differs from the "
                                f"PDF footer revision(s) {', '.join(sorted(revs))}: possible stale "
                                "render (check in code-and-data).")

    report = {
        "suite_version": suite_version(),
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "root": root,
        "assignment": ({k: v for k, v in assign.items() if k != "path"} if assign else None),
        "settings": ({"product_type": jf.product_type(assign), "data_mode": jf.data_mode(assign),
                      "depth": jf.depth(assign),
                      "non_patient_files": jf.non_patient_files(assign)} if assign else None),
        "clearance": {"ok": not errors, "errors": errors, "warnings": warnings},
        "inventory": inventory,
        "quarto_sources": qmds,
        "pdfs": pdfs,
        "checks": checks,
    }
    out = a.out or os.path.join(root, "review", "intake-scan.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    print(f"Job: {root}")
    if assign:
        s = report["settings"]
        print(f"Product type: {s['product_type']} · data mode: {s['data_mode']} · depth: {s['depth']}"
              f" · questions: {len(assign.get('questions', []))}")
    print(f"Files: {len(inventory)} ({sum(1 for i in inventory if i['class'] == 'data-like')} data-like)")
    for q in qmds:
        print(f"Quarto source {q['path']}: {q['n_chunks']} chunks, "
              f"{len(q['flagged_chunk_options'])} chunk options to audit, "
              f"{len(q['files_read'])} file reads, SVN rev {q['svn_id']['revision'] if q['svn_id'] else '—'}")
    for p in prod_pdfs:
        print(f"PDF {p['path']}: {p.get('pages', '?')} pages, created {p.get('creationdate', '?')}, "
              f"R {p.get('r_version', '?')}, footer rev {p.get('footer_revision', '—')}")
    pages = [int(p["pages"]) for p in prod_pdfs if str(p.get("pages", "")).isdigit()]
    if pages:
        size = "short" if sum(pages) <= jf.SHORT_PAGES else "long"
        print(f"Size class: {size} ({sum(pages)} rendered pages; Proportion in the stats-review "
              "skill sets the agents and the length limits)")
    for w in warnings:
        print(f"WARN {w}")
    for e in errors:
        print(f"FAIL {e}")
    print(f"Wrote {os.path.relpath(out, root)}")
    if errors:
        print("CLEARANCE FAILED — stop: no file may be opened until the operator resolves this.")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
