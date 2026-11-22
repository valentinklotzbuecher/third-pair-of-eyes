#!/usr/bin/env python3
"""check_issue_coverage.py — the coverage and severity gate for the consistency review.

    python3 check_issue_coverage.py ISSUES.md [--synthesis SYNTHESIS.md]

The corpus-to-ledger direction: every finding the verdict declared reaches the
consistency review, and every issue carries the severity its findings imply or says
why not.

Declared findings (from SYNTHESIS.md):
  - every statement-ledger row whose Holds is `narrower` or `not established` (ST ids);
  - every cross-cutting finding (G ids) and every finding (F ids);
  - every assignment question (Q ids), which needs an answer block in ISSUES.md.

Dispositions live in ISSUES.coverage.md, one per line, the id in backticks:
  `F3` → issue 2                 `G1` → issues 1, 3        `ST04` → issue 2
  `F7` → not checked             `F8` → general comments   `F9` — excluded: <reason>

FAIL (exit 1):
  - the general comments, issues and answers longer than 1.25 times the form's
    length limit for the product's size class (issues.FORM_WORDS);
  - a declared finding with no disposition, or a disposition naming an issue that
    does not exist;
  - a primary or supporting statement row that does not hold, mapped only to
    `not checked`, `general comments` or `excluded`;
  - an issue with a field outside its vocabulary (severity Major|Minor; change text |
    code | text and code | none; clarification yes|no; category; evidence);
  - an issue whose severity departs from the default without `severity-reason:`;
  - a question with no answer block in ISSUES.md.
WARN:
  - an issue's `change:` does not cover the `where:` of the findings mapped to it, or a
    finding with `where: unresolved` maps to an issue without `clarification: yes`;
  - an issue no disposition maps anything to (a finding the verdict never declared).

Default severity: the most severe over the statement rows the issue carries, directly
or through the `bears on:` line of a mapped finding:
  not established × primary or supporting → Major; narrower × primary → Major;
  anything else → Minor.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issues as iss  # noqa: E402

DISP = re.compile(r"`((?:ST|F|G|Q)\d+)`\s*(→|->|—|--)\s*(.+?)\s*$")


def read_dispositions(path):
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        m = DISP.search(line)
        if not m:
            continue
        ident, target = m.group(1), m.group(3).strip()
        nums = []
        kind = "other"
        if re.match(r"(?i)issues?\b", target):
            kind = "issue"
            nums = [int(n) for n in re.findall(r"\d+", target.split("(")[0])]
        elif re.match(r"(?i)not checked", target):
            kind = "not checked"
        elif re.match(r"(?i)general comments", target):
            kind = "general comments"
        elif re.match(r"(?i)excluded", target):
            kind = "excluded"
        out.setdefault(ident, []).append({"kind": kind, "issues": nums, "raw": target})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ledger")
    ap.add_argument("--synthesis", default=None)
    a = ap.parse_args(argv)
    ledger = os.path.abspath(a.ledger)
    root = os.path.dirname(ledger)
    syn_path = a.synthesis or os.path.join(root, "SYNTHESIS.md")
    led = iss.read_issues(ledger)
    syn = iss.read_synthesis(syn_path)
    disp = read_dispositions(os.path.join(root, "ISSUES.coverage.md"))
    fails, warns = [], []
    size = iss.size_class(root)
    limit, n = iss.FORM_WORDS[size], iss.form_words(led)
    if n > limit * iss.TOLERANCE:
        fails.append(f"the general comments, issues and answers run to {n} words; the form "
                     f"for a {size} product is at most about {limit} (fails above "
                     f"{int(limit * iss.TOLERANCE)}). Shorten the issue bodies to the problem, "
                     "its evidence and the fix; detail stays in SYNTHESIS.md")
    numbers = {i["number"] for i in led["issues"]}
    rows = {r["id"]: r for r in syn["rows"] if r.get("id")}

    # field vocabulary
    for i in led["issues"]:
        f, n = i["fields"], i["number"]
        if n is None:
            fails.append(f"issue `{i['heading']}` is not numbered `### <n>. <title>`")
        checks = (("severity", iss.SEVERITIES, False), ("change", iss.CHANGES, True),
                  ("clarification", ("yes", "no"), True), ("category", iss.CATEGORIES, False),
                  ("evidence", iss.EVIDENCE, True))
        for key, allowed, lower in checks:
            v = f.get(key, "").strip()
            ok = (v.lower() in [x.lower() for x in allowed]) if v else False
            if not ok:
                fails.append(f"issue {n}: {key} = {v!r}; expected one of {', '.join(allowed)}")

    # declared findings
    declared = [r for r in syn["rows"] if r.get("holds") in ("narrower", "not established")]
    obligations = [(r["id"], "statement") for r in declared if r.get("id")] + \
                  [(k, "finding") for k in sorted(syn["blocks"])]
    carried = {n: set() for n in numbers}           # issue -> statement ids it carries
    where = {n: set() for n in numbers}
    unresolved = {n: False for n in numbers}
    mapped_issues = set()
    for ident, kind in obligations:
        ds = disp.get(ident)
        if not ds:
            fails.append(f"`{ident}` has no disposition in ISSUES.coverage.md")
            continue
        for d in ds:
            if d["kind"] == "issue":
                bad = [n for n in d["issues"] if n not in numbers]
                if bad or not d["issues"]:
                    fails.append(f"`{ident}` → {d['raw']}: no such issue")
                for n in d["issues"]:
                    if n not in numbers:
                        continue
                    mapped_issues.add(n)
                    if ident.startswith("ST"):
                        carried[n].add(ident)
                    else:
                        blk = syn["blocks"].get(ident, {})
                        carried[n].update(s for s in blk.get("statements", [])
                                          if rows.get(s, {}).get("holds") in ("narrower", "not established"))
                        w = blk.get("where") or ""
                        if w == "unresolved":
                            unresolved[n] = True
                        elif w:
                            where[n].update({"text and code": {"text", "code"}}.get(w, {w}))
        if ident.startswith("ST"):
            r = rows.get(ident, {})
            if r.get("centrality") in ("primary", "supporting") and \
                    not any(d["kind"] == "issue" for d in ds):
                fails.append(f"`{ident}` ({r.get('centrality')}, {r.get('holds')}) must map to an "
                             "issue, not only to not checked, general comments or excluded")
        for d in ds:
            if d["kind"] == "excluded" and not re.search(r"excluded\s*:\s*\S", d["raw"]):
                fails.append(f"`{ident}` excluded without a reason")

    # severity defaults and departures
    departures = []
    for i in led["issues"]:
        n = i["number"]
        if n is None:
            continue
        default = iss.default_severity([rows[s] for s in carried.get(n, ()) if s in rows])
        sev = i["fields"].get("severity", "").strip().capitalize()
        if sev in iss.SEVERITIES and sev != default:
            departures.append(f"issue {n}: {sev} (default {default})")
            if not i["fields"].get("severity-reason", "").strip():
                fails.append(f"issue {n}: severity {sev} departs from the default {default} "
                             "without severity-reason:")
        ch = i["fields"].get("change", "").strip().lower()
        have = {"text and code": {"text", "code"}, "none": set()}.get(ch, {ch})
        if where.get(n) and not where[n] <= have:
            warns.append(f"issue {n}: change `{ch}` does not cover where = "
                         f"{', '.join(sorted(where[n]))} of its findings")
        if unresolved.get(n) and i["fields"].get("clarification", "").strip().lower() != "yes":
            warns.append(f"issue {n}: carries a finding with where: unresolved but "
                         "clarification is not yes")
        if n not in mapped_issues:
            warns.append(f"issue {n} carries no declared finding (check it is in SYNTHESIS.md)")

    # questions
    answered = {a["q"] for a in led["answers"] if a["q"] is not None and a["answer"]}
    for q in syn["questions"]:
        if q["q"] not in answered:
            fails.append(f"question Q{q['q']} has no answer block in ISSUES.md")

    for d in departures:
        print(f"DEPARTURE {d}")
    for w in warns:
        print(f"WARN {w}")
    for f in fails:
        print(f"FAIL {f}")
    print(f"{'FAIL' if fails else 'PASS'}: {len(obligations)} declared findings, "
          f"{len(led['issues'])} issues, {len(syn['questions'])} questions; "
          f"ledger sha256:{led['sha256'][:12]}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
