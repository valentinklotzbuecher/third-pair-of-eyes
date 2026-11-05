"""issues.py — readers for the consistency-review ledger (ISSUES.md) and for the
parts of SYNTHESIS.md the gates need. Standard library only; shared by
check_issue_coverage.py, render_review.py and annotate_source.py.

ISSUES.md layout (see the skill's SKILL.md):

    ---
    product: …            statistical-product: …     status: COMPLETE|INTERIM|BLOCKED
    verification: …       depth: …                   data-mode: …        date: …
    ---
    ## Assignment                 (rendered verbatim)
    ## General comments
    ## Issues                     ### 1. Title  +  field lines  +  body
    ## Answers to the assignment  ### Q1. Question  +  body  +  status: line
    ## Not checked                bullet list of the review's limits
"""
import hashlib
import json
import os
import re

ISSUE_FIELDS = ("severity", "severity-reason", "change", "clarification", "category",
                "evidence", "location", "anchor", "sources")
SEVERITIES = ("Major", "Minor")
CHANGES = ("text", "code", "text and code", "none")
CATEGORIES = ("Design and estimand", "Sample size", "Analysis specification",
              "Numerical consistency", "Code and reproducibility", "Interpretation",
              "Reporting")
EVIDENCE = ("established", "strong", "plausible", "unresolved")
Q_STATUS = ("answered", "partly answered", "cannot be answered from the materials")
FIELD = re.compile(r"^([a-z][a-z-]*)\s*:\s*(.*?)\s*$", re.I)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def split_front_matter(text):
    meta, body = {}, text
    if text.startswith("---"):
        parts = text.split("\n")
        for i in range(1, len(parts)):
            if parts[i].strip() == "---":
                for line in parts[1:i]:
                    m = re.match(r"^\s*([A-Za-z][\w-]*)\s*:\s*(.*?)\s*(?:#.*)?$", line)
                    if m:
                        meta[m.group(1).lower()] = m.group(2)
                body = "\n".join(parts[i + 1:])
                break
    return meta, body


def h2_sections(body):
    """{lowercased title: text} for every `## ` section (fences respected)."""
    out, title, buf, fence = {}, None, [], False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"^##\s+(.*?)\s*$", line)
        if m:
            if title is not None:
                out[title] = "\n".join(buf).strip("\n")
            title, buf = m.group(1).strip().lower(), []
        elif title is not None:
            buf.append(line)
    if title is not None:
        out[title] = "\n".join(buf).strip("\n")
    return out


def h3_blocks(text):
    """[(heading, [lines])] for every `### ` block in a section."""
    blocks, head, buf = [], None, []
    for line in text.split("\n"):
        m = re.match(r"^###\s+(.*?)\s*$", line)
        if m:
            if head is not None:
                blocks.append((head, buf))
            head, buf = m.group(1), []
        elif head is not None:
            buf.append(line)
    if head is not None:
        blocks.append((head, buf))
    return blocks


def parse_fields(lines, names):
    """Leading `key: value` lines (keys in `names`) and the remaining body text."""
    fields, i = {}, 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines):
        m = FIELD.match(lines[i].strip())
        if not m or m.group(1).lower() not in names:
            break
        fields[m.group(1).lower()] = m.group(2)
        i += 1
    return fields, "\n".join(lines[i:]).strip()


def read_issues(path):
    text = open(path, encoding="utf-8").read()
    meta, body = split_front_matter(text)
    secs = h2_sections(body)
    issues = []
    for head, lines in h3_blocks(secs.get("issues", "")):
        m = re.match(r"^(\d+)\.\s+(.*)$", head)
        fields, rest = parse_fields(lines, ISSUE_FIELDS)
        issues.append({"number": int(m.group(1)) if m else None,
                       "title": m.group(2).strip() if m else head, "heading": head,
                       "fields": fields, "body": rest})
    answers = []
    for head, lines in h3_blocks(secs.get("answers to the assignment", "")):
        m = re.match(r"^Q(\d+)\.\s+(.*)$", head)
        body_lines, status = [], None
        for ln in lines:
            sm = re.match(r"^\s*status\s*:\s*(.*?)\s*$", ln, re.I)
            if sm:
                status = sm.group(1).strip().lower()
            elif not re.match(r"^\s*basis\s*:", ln, re.I):
                body_lines.append(ln)
        answers.append({"q": int(m.group(1)) if m else None,
                        "question": m.group(2).strip() if m else head,
                        "answer": "\n".join(body_lines).strip(), "status": status})
    return {"path": path, "meta": meta, "sections": secs, "issues": issues,
            "answers": answers, "sha256": sha256_file(path)}


def read_synthesis(path):
    """Statement rows, cross-cutting (G) and finding (F) blocks, question (Q) blocks."""
    text = open(path, encoding="utf-8").read()
    _, body = split_front_matter(text)
    secs = h2_sections(body)
    rows = []
    for line in secs.get("statement ledger", "").split("\n"):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0].lower().startswith("statement") or set(cells[0]) <= set("-: "):
            continue
        idm = re.search(r"\b(ST\d+)\b[^|]*$", cells[0])
        rows.append({"id": idm.group(1) if idm else None, "cells": cells})
    header = None
    for line in secs.get("statement ledger", "").split("\n"):
        if line.strip().startswith("|") and "holds" in line.lower():
            header = [c.strip().lower() for c in line.strip().strip("|").split("|")]
            break
    if header:
        for r in rows:
            d = dict(zip(header, r["cells"]))
            r["centrality"] = d.get("centrality", "").lower()
            r["holds"] = d.get("holds", "").lower()
    blocks = {}
    for sec in ("cross-cutting findings", "findings"):
        for head, lines in h3_blocks(secs.get(sec, "")):
            m = re.match(r"^([FG]\d+)\.\s+(.*)$", head)
            if not m:
                continue
            joined = "\n".join(lines)
            where = re.search(r"(?im)^where:\s*(.+?)\s*$", joined)
            bears = re.search(r"(?im)^bears on:\s*(.+?)\s*$", joined)
            blocks[m.group(1)] = {"title": m.group(2), "where": where.group(1).lower() if where else None,
                                  "bears_on": bears.group(1) if bears else "",
                                  "statements": re.findall(r"\bST\d+\b", bears.group(1) if bears else "")}
    questions = []
    for head, lines in h3_blocks(secs.get("answers to the assignment questions", "")):
        m = re.match(r"^Q(\d+)\.\s+(.*)$", head)
        if m:
            st = re.search(r"(?im)^status:\s*(.+?)\s*$", "\n".join(lines))
            questions.append({"q": int(m.group(1)), "question": m.group(2),
                              "status": st.group(1).lower() if st else None})
    header_line = next((ln.strip() for ln in body.split("\n") if ln.strip().startswith("Verification:")), "")
    return {"rows": rows, "blocks": blocks, "questions": questions, "header": header_line,
            "status": secs.get("status", "")}


# Proportion, kept in step with dkf-review/scripts/jobfiles.py: a product of at most
# SHORT_PAGES rendered pages is short. FORM_WORDS limits the words of ISSUES.md's
# general comments, issues and answers; the gate fails above TOLERANCE times it.
SHORT_PAGES = 10
TOLERANCE = 1.25
FORM_WORDS = {"short": 1000, "long": 3000}


def size_class(root):
    try:
        with open(os.path.join(root, "review", "intake-scan.json"), encoding="utf-8") as fh:
            scan = json.load(fh)
    except (OSError, ValueError):
        return "long"
    pages = [int(str(r.get("pages", "")).strip()) for r in scan.get("pdfs", [])
             if str(r.get("path", "")).replace("\\", "/").startswith("01_product/")
             and str(r.get("pages", "")).strip().isdigit()]
    return "short" if pages and sum(pages) <= SHORT_PAGES else "long"


def form_words(led):
    secs = led["sections"]
    body = "\n".join(secs.get(k, "") if isinstance(secs.get(k, ""), str)
                     else "\n".join(secs.get(k, []))
                     for k in ("general comments", "issues", "answers to the assignment"))
    return len(re.findall(r"\S+", body))


# Evidence links. A file in an issue's `sources:` is linked from the form when it exists
# in the job and would be committed with it: never a copy of the product, its documents,
# literature or data (kept in step with dkf-review/assets/job-gitignore).
NEVER_LINKED = ("01_product/", "02_governing/", "03_previous/", "04_data/", "05_synthetic/",
                "lit/", "work/synthetic/", "review/extracts/")
COPY_EXTENSIONS = (".qmd", ".pdf", ".docx", ".html")
DATA_EXTENSIONS = (".sas7bdat", ".sav", ".dta", ".xpt", ".parquet", ".feather", ".rds",
                   ".rda", ".rdata", ".xls", ".xlsx")


def linkable(root, rel):
    rel = rel.strip().replace("\\", "/").lstrip("./")
    low = rel.lower()
    if not rel or rel.startswith(NEVER_LINKED) or low.endswith(DATA_EXTENSIONS):
        return False
    if rel.startswith("work/pkg/") and low.endswith(COPY_EXTENSIONS):
        return False
    return os.path.isfile(os.path.join(root, rel))


def evidence(root, issue):
    """The files behind one issue, from its `sources:` field, that the form may link."""
    out = []
    for rel in re.split(r"[;,]", issue["fields"].get("sources", "")):
        rel = re.sub(r"\s.*$", "", rel.strip()).replace("\\", "/").lstrip("./")
        if rel and rel not in out and linkable(root, rel):
            out.append(rel)
    return out


# Dispositions: the human reviewer's decision on each issue, one line per form label,
# `- Major 1: kept`, `- Minor 2: edited — <reason>`, `- Major 3: dropped — <reason>`,
# with the issue's title on the next line.
DECISIONS = ("kept", "edited", "dropped")
DISP_LINE = re.compile(r"^-\s+(Major|Minor)\s+(\d+)\s*:\s*([A-Za-z]+)\s*(?:[—–-]+\s*(.*?))?\s*$")


def dispositions_template(led):
    product = led["meta"].get("product") or "statistical product"
    out = [f"# Dispositions: {product}", "",
           "For the reviewer: after each label write `kept`, `edited` or `dropped`; after",
           "`edited` or `dropped`, a dash and the reason. Then run `check_dispositions.py`",
           "on this file. Your decisions show how far the draft could be used.", "",
           "reviewer:", "date:", ""]
    for lab, i in zip(form_labels(led["issues"]), led["issues"]):
        out += [f"- {lab}: undecided", f"  {i['title']}"]
    return "\n".join(out) + "\n"


def read_dispositions(path):
    """{label: {"decision", "reason", "title"}} plus the reviewer and date fields."""
    lines = open(path, encoding="utf-8").read().split("\n")
    out, meta = {}, {}
    for k, line in enumerate(lines):
        fm = re.match(r"^(reviewer|date)\s*:\s*(.*?)\s*$", line)
        if fm:
            meta[fm.group(1)] = fm.group(2)
            continue
        m = DISP_LINE.match(line)
        if not m:
            continue
        nxt = lines[k + 1] if k + 1 < len(lines) else ""
        title = nxt.strip() if nxt.startswith((" ", "\t")) and nxt.strip() else ""
        out[f"{m.group(1)} {int(m.group(2))}"] = {"decision": m.group(3).lower(),
                                                 "reason": (m.group(4) or "").strip(),
                                                 "title": title}
    return out, meta


def form_labels(issues):
    """Each issue's label as the rendered form lists it ("Major 2", "Minor 1"): issues
    are numbered within their severity, in ledger order. One list, aligned with
    `issues`, used by the form, the org form and the annotated source alike."""
    seen, labels = {}, []
    for i in issues:
        sev = i["fields"].get("severity", "").strip().capitalize() or "Issue"
        seen[sev] = seen.get(sev, 0) + 1
        labels.append(f"{sev} {seen[sev]}")
    return labels


def default_severity(rows):
    """Default severity from the statement rows an issue carries."""
    sev = "Minor"
    for r in rows:
        h, c = r.get("holds", ""), r.get("centrality", "")
        if h == "not established" and c in ("primary", "supporting"):
            return "Major"
        if h == "narrower" and c == "primary":
            sev = "Major"
    return sev


def decision(issues, answers=()):
    """The five DKF decision boxes from the issues' severity, change and clarification."""
    def has(sev, kinds):
        return any(i["fields"].get("severity", "").strip().capitalize() == sev
                   and i["fields"].get("change", "").strip().lower() in kinds for i in issues)
    text_k, code_k = ("text", "text and code"), ("code", "text and code")
    clar = any(i["fields"].get("clarification", "").strip().lower() == "yes" for i in issues) or \
        any((a.get("status") or "") == "cannot be answered from the materials" for a in answers)
    return [
        (has("Minor", text_k), "Statistical product needs minor changes in the text"),
        (has("Major", text_k), "Statistical product needs major changes in the text "
                               "(second review necessary)"),
        (has("Minor", code_k), "Statistical product needs minor changes in the R programming"),
        (has("Major", code_k), "Statistical product needs major changes in the R programming "
                               "(second review necessary)"),
        (clar, "Clarifications required about code or methods (meeting or communication)"),
    ]


def gate_record_ok(path, sha):
    """True when `path` carries a `gate: … sha256:<first 12>` line for this ledger."""
    if not os.path.exists(path):
        return False
    text = open(path, encoding="utf-8").read()
    return bool(re.search(rf"(?im)^gate:.*sha256:{sha[:12]}\b", text))
