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
