#!/usr/bin/env python3
"""check_dispositions.py — the human reviewer's decision on every issue of the form.

    python3 check_dispositions.py DISPOSITIONS.md [--ledger ISSUES.md] [--json]

`render_review.py` writes DISPOSITIONS.md as a template beside ISSUES.md: one line per
issue, labelled as in the form, with the issue's title on the next line. The reviewer
replaces `undecided`:

    - Major 1: kept
    - Minor 2: edited — the SD comes from a second source as well
    - Major 3: dropped — the protocol defines the estimand

FAIL (exit 1):
  - an issue of the current ISSUES.md with no line, or still `undecided`;
  - a decision other than kept, edited or dropped;
  - `edited` or `dropped` without a reason;
  - a label that is not an issue of the form;
  - a title under a label that is not that issue's title (the issues changed after the
    template was written: check each label before relying on it).
Prints the counts; --json prints them as one JSON object, for tracking across reviews.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issues as iss  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dispositions")
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    path = os.path.abspath(a.dispositions)
    ledger = a.ledger or os.path.join(os.path.dirname(path), "ISSUES.md")
    led = iss.read_issues(ledger)
    decided, meta = iss.read_dispositions(path)
    labels = iss.form_labels(led["issues"])
    titles = {lab: i["title"] for lab, i in zip(labels, led["issues"])}
    fails = []
    for lab in labels:
        d = decided.get(lab)
        if d is None:
            fails.append(f"{lab} ({titles[lab][:60]}) has no line")
            continue
        if d["decision"] == "undecided":
            fails.append(f"{lab} is still undecided")
        elif d["decision"] not in iss.DECISIONS:
            fails.append(f"{lab}: {d['decision']!r} is not kept, edited or dropped")
        elif d["decision"] in ("edited", "dropped") and not d["reason"]:
            fails.append(f"{lab}: {d['decision']} needs a reason after a dash")
        if d["title"] and d["title"] != titles[lab]:
            fails.append(f"{lab}: the title under it is not the issue's title "
                         f"({titles[lab][:60]!r}); the issues changed after the template "
                         "was written")
    for lab in decided:
        if lab not in titles:
            fails.append(f"{lab} is not an issue of the form")
    counts = {k: sum(1 for lab in labels if decided.get(lab, {}).get("decision") == k)
              for k in iss.DECISIONS}
    by_sev = {sev: {k: sum(1 for lab in labels if lab.startswith(sev)
                           and decided.get(lab, {}).get("decision") == k) for k in iss.DECISIONS}
              for sev in ("Major", "Minor")}
    summary = {"issues": len(labels), **counts, "major": by_sev["Major"], "minor": by_sev["Minor"],
               "reviewer": meta.get("reviewer", ""), "date": meta.get("date", ""),
               "complete": not fails}
    if a.json:
        print(json.dumps(summary))
    for f in fails:
        print(f"  FAIL  {f}")
    print(f"{'PASS' if not fails else 'FAIL'}: {counts['kept']} kept, {counts['edited']} edited, "
          f"{counts['dropped']} dropped of {len(labels)} issues")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
