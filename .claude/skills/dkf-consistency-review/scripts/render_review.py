#!/usr/bin/env python3
"""render_review.py — render the consistency-review ledger (ISSUES.md) in the DKF
consistency-review form.

    python3 render_review.py ISSUES.md [--out-stem CONSISTENCY_REVIEW] [--org]
                                       [--finalize]

Writes <stem>.md (the form in Markdown), <stem>.html (self-contained, print-ready)
and, with --org, <stem>.org (the Emacs org layout of the DKF template). The Decision
boxes are computed from the issues, never written by hand:

  minor/major changes in the text   ← a Minor/Major issue with change text or text and code
  minor/major changes in the code   ← a Minor/Major issue with change code or text and code
  clarifications required           ← an issue with clarification: yes, or a question that
                                      cannot be answered from the materials

Without --finalize the output is a preview and says so at the top. --finalize
refuses (exit 1, nothing written) unless: the ledger's status is COMPLETE; the fact
gate and the coverage gate were ruled on this exact ledger revision
(ISSUES.facts.md and ISSUES.coverage.md carry `gate: … sha256:<first 12>`); the
coverage gate passes now; and, when a HANDOFF.manifest.json exists (required at depth
full), every declared input still has its recorded hash.

Markdown is converted with `mistune` when installed, else with a small built-in
converter that covers what this script writes.
"""
import argparse
import datetime
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issues as iss  # noqa: E402

SKILL_VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SKILL.md")


def suite_version():
    try:
        m = re.search(r'^\s*version:\s*"?([0-9][^"\s]*)"?', open(SKILL_VERSION_FILE).read(), re.M)
        return m.group(1) if m else "?"
    except OSError:
        return "?"


def indent(text, n=3):
    return "\n".join((" " * n + ln) if ln.strip() else "" for ln in text.split("\n"))


def build_markdown(led, final, problems):
    meta, secs = led["meta"], led["sections"]
    product = meta.get("product") or meta.get("statistical-product") or "statistical product"
    out = [f"# Consistency review: {product}", ""]
    facts = [f"**Prepared:** {meta.get('date') or datetime.date.today().isoformat()}",
             f"**Review depth:** {meta.get('depth', 'standard')}",
             f"**Patient data:** {data_mode_words(meta.get('data-mode', 'none'))}"]
    out += [" · ".join(facts), ""]
    out += ["> Pre-human review prepared by an AI agent with the DKF review skills "
            f"(v{suite_version()}). It prepares the consistency review by a second "
            "statistician and does not replace it.", ""]
    if not final:
        why = "; ".join(problems) if problems else "rendered without --finalize"
        out += [f"> **Preview, not final:** {why}.", ""]
    out += ["## Assignment", "", secs.get("assignment", "").strip() or "(not given)", ""]
    out += ["## Review", "", "### Decision", ""]
    for ticked, label in iss.decision(led["issues"], led["answers"]):
        out.append(f"- [{'x' if ticked else ' '}] {label}")
    out += ["", "### General comments", "", secs.get("general comments", "").strip(), ""]
    labels = iss.form_labels(led["issues"])
    for sev, title in (("Major", "Major issues"), ("Minor", "Minor issues")):
        out += [f"### {title}", ""]
        items = [(int(lab.split()[-1]), i) for lab, i in zip(labels, led["issues"])
                 if lab.split()[0] == sev]
        if not items:
            out += ["None identified.", ""]
        for k, i in items:
            loc = i["fields"].get("location", "").strip()
            tag = []
            ch = i["fields"].get("change", "").strip().lower()
            if ch and ch != "none":
                tag.append({"text": "text", "code": "R code",
                            "text and code": "text and R code"}.get(ch, ch))
            if i["fields"].get("clarification", "").strip().lower() == "yes":
                tag.append("needs clarification")
            head = f"{k}. **{i['title']}**"
            if loc:
                head += f" ({loc})"
            if tag:
                head += f" [{', '.join(tag)}]"
            out += [head, "", indent(i["body"]), ""]
    out += ["### Answers to the issues listed in the assignment", ""]
    if not led["answers"]:
        out += ["No questions were listed.", ""]
    for a in sorted(led["answers"], key=lambda a: a["q"] or 0):
        out += [f"{a['q']}. *{a['question']}*", "", indent(a["answer"]), ""]
    nc = secs.get("not checked", "").strip()
    if nc:
        out += ["### What this review could not check", "", nc, ""]
    out += ["---", "",
            f"<!-- dkf-consistency-review build: ledger={os.path.basename(led['path'])} "
            f"sha256={led['sha256']} final={'yes' if final else 'no'} "
            f"generated={datetime.datetime.now().isoformat(timespec='seconds')} -->", ""]
    return "\n".join(out)


def data_mode_words(mode):
    return {"none": "not shared with the AI agent",
            "synthetic": "not shared; code run on synthetic data",
            "shared": "shared under the recorded clearance"}.get((mode or "").strip().lower(), mode)


# ---- Markdown to HTML ------------------------------------------------------------------

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_to_html(md):
    try:
        import mistune  # type: ignore
        render = mistune.create_markdown(plugins=["table", "task_lists"])
        return render(md)
    except Exception:  # noqa: BLE001 — fall back to the built-in converter
        return simple_md(md)


def simple_md(md):
    """Headings, paragraphs, block quotes, rules, pipe tables, and nested ordered and
    unordered lists (with task boxes) — the subset this script writes."""
    lines = md.split("\n")
    out, i = [], 0

    ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")

    def next_nonblank(j):
        while j < len(lines) and not lines[j].strip():
            j += 1
        return j

    def list_block(i, base):
        first = ITEM.match(lines[i])
        ordered = first.group(2)[0].isdigit()
        tag = "ol" if ordered else "ul"
        attrs = (f' start="{first.group(2)[:-1]}"'
                 if ordered and first.group(2)[:-1] not in ("1", "") else "")
        html_ = [f"<{tag}{attrs}>"]
        while i < len(lines):
            m = ITEM.match(lines[i])
            if m is None:
                if not lines[i].strip():
                    j = next_nonblank(i + 1)
                    mj = ITEM.match(lines[j]) if j < len(lines) else None
                    if mj and len(mj.group(1)) == base and mj.group(2)[0].isdigit() == ordered:
                        i = j
                        continue
                    if mj and len(mj.group(1)) > base:
                        i = j
                        continue
                break
            ind = len(m.group(1))
            if ind < base:
                break
            if ind > base:
                sub, i = list_block(i, ind)
                if html_[-1].endswith("</li>"):
                    html_[-1] = html_[-1][:-5] + sub + "</li>"
                else:
                    html_.append(f"<li>{sub}</li>")
                continue
            if m.group(2)[0].isdigit() != ordered:
                break
            item = m.group(3)
            box = re.match(r"^\[([ xX])\]\s+(.*)$", item)
            if box:
                item = ("&#9746; " if box.group(1).lower() == "x" else "&#9744; ") + inline(box.group(2))
                cls = ' class="task"'
            else:
                item, cls = inline(item), ""
            i += 1
            paras, cur = [], []
            while i < len(lines):
                ln = lines[i]
                if not ln.strip():
                    j = next_nonblank(i + 1)
                    if j < len(lines) and re.match(r"^\s{%d,}\S" % (base + 2), lines[j]) \
                            and not ITEM.match(lines[j]):
                        if cur:
                            paras.append(" ".join(cur))
                            cur = []
                        i = j
                        continue
                    break
                if ITEM.match(ln):
                    break
                if len(ln) - len(ln.lstrip()) >= base + 2 or cur:
                    cur.append(ln.strip())
                    i += 1
                    continue
                break
            if cur:
                paras.append(" ".join(cur))
            body = "".join(f"<p>{inline(p)}</p>" for p in paras)
            html_.append(f"<li{cls}>{item}{body}</li>")
        html_.append(f"</{tag}>")
        return "".join(html_), i

    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("<!--"):
            out.append(ln)
            i += 1
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if h:
            n = len(h.group(1))
            out.append(f"<h{n}>{inline(h.group(2))}</h{n}>")
            i += 1
            continue
        if re.match(r"^-{3,}\s*$", ln):
            out.append("<hr>")
            i += 1
            continue
        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").rstrip())
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(buf))}</p></blockquote>")
            continue
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1].strip().lstrip("|")):
            hdr = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in hdr) +
                       "</tr></thead><tbody>" + "".join(
                           "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows) +
                       "</tbody></table>")
            continue
        if ITEM.match(ln):
            block, i = list_block(i, len(ln) - len(ln.lstrip()))
            out.append(block)
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|>|\s*(?:[-*+]|\d+[.)])\s|-{3,}\s*$)", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)


CSS = """
:root { --ink:#2F393E; --muted:#5b676d; --accent:#00858C; --line:#d6dfe1; --bg:#ffffff;
        --soft:#eef6f5; }
@media (prefers-color-scheme: dark) { :root { --ink:#e6eceb; --muted:#a9b6b8; --accent:#5cc3c8;
        --line:#3a4448; --bg:#1b2124; --soft:#243035; } }
html { background: var(--bg); }
body { font: 15px/1.55 "Source Sans Pro", "Segoe UI", system-ui, sans-serif; color: var(--ink);
       background: var(--bg); max-width: 860px; margin: 2rem auto; padding: 0 16px; }
h1 { font-size: 1.6rem; margin: 0 0 .4rem; color: var(--accent); }
h2 { font-size: 1.25rem; border-bottom: 2px solid var(--accent); padding-bottom: .2rem; margin-top: 2rem; }
h3 { font-size: 1.05rem; margin-top: 1.5rem; }
blockquote { margin: .8rem 0; padding: .5rem .9rem; background: var(--soft);
             border-left: 4px solid var(--accent); color: var(--muted); }
blockquote p { margin: 0; }
li { margin: .35rem 0; } li.task { list-style: none; margin-left: -1.2rem; }
li p { margin: .35rem 0; }
code { font-size: .92em; background: var(--soft); padding: 0 .25em; border-radius: 3px; }
table { border-collapse: collapse; margin: .8rem 0; } th, td { border: 1px solid var(--line); padding: .3rem .5rem; }
hr { border: 0; border-top: 1px solid var(--line); margin: 2rem 0 1rem; }
@media print { body { margin: 0; max-width: none; font-size: 11pt; } blockquote { break-inside: avoid; } }
"""


def build_html(md, title):
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>\n"
            f"{md_to_html(md)}\n</body></html>\n")


def org_inline(s):
    s = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"/\1/", s)
    return re.sub(r"`([^`]+)`", r"~\1~", s)


def build_org(led):
    """The DKF template's org layout: *** CONSISTENCY REVIEW, **** Assignment, …"""
    secs = led["sections"]
    out = ["*** CONSISTENCY REVIEW", "**** Assignment"]
    out += [org_inline(ln) for ln in secs.get("assignment", "").strip().split("\n")]
    out += ["**** Review", "***** Decision"]
    for ticked, label in iss.decision(led["issues"], led["answers"]):
        out.append(f"- [{'X' if ticked else ' '}] {label}")
    out += ["***** General Comments"]
    out += [org_inline(ln) for ln in secs.get("general comments", "").strip().split("\n")]
    labels = iss.form_labels(led["issues"])
    for sev, title in (("Major", "Major Issues"), ("Minor", "Minor Issues")):
        out.append(f"***** {title}")
        for lab, i in zip(labels, led["issues"]):
            if lab.split()[0] != sev:
                continue
            loc = i["fields"].get("location", "").strip()
            out.append(f"{lab.split()[-1]}. *{org_inline(i['title'])}*" + (f" ({loc})" if loc else ""))
            out += ["  " + org_inline(ln) if ln.strip() else "" for ln in i["body"].split("\n")]
    out.append("***** Answer to issues listed in 'Assignment'")
    for a in sorted(led["answers"], key=lambda a: a["q"] or 0):
        out.append(f"- /{org_inline(a['question'])}/")
        out += ["  " + org_inline(ln) if ln.strip() else "" for ln in a["answer"].split("\n")]
    nc = secs.get("not checked", "").strip()
    if nc:
        out += ["***** Not checked by the AI review"] + [org_inline(ln) for ln in nc.split("\n")]
    return "\n".join(out) + "\n"


def finalize_problems(led, root):
    problems = []
    if (led["meta"].get("status") or "").strip().upper() != "COMPLETE":
        problems.append(f"ledger status is {led['meta'].get('status') or 'missing'}, not COMPLETE")
    for name in ("ISSUES.facts.md", "ISSUES.coverage.md"):
        if not iss.gate_record_ok(os.path.join(root, name), led["sha256"]):
            problems.append(f"{name} has no gate record for this ledger revision "
                            f"(sha256:{led['sha256'][:12]})")
    import check_issue_coverage  # noqa: E402
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        cov = check_issue_coverage.main([led["path"]])
    if cov != 0:
        problems.append("the coverage gate fails (run check_issue_coverage.py)")
    man = os.path.join(root, "HANDOFF.manifest.json")
    depth = (led["meta"].get("depth") or "").strip().lower()
    if os.path.exists(man):
        data = json.load(open(man, encoding="utf-8"))
        for p, rec in data.get("inputs", {}).items():
            full = os.path.join(root, p)
            if isinstance(rec, dict) and rec.get("sha256"):
                if not os.path.exists(full) or iss.sha256_file(full) != rec["sha256"]:
                    problems.append(f"accepted input {p} changed since the handoff")
    elif depth == "full":
        problems.append("depth full needs the audit's HANDOFF.manifest.json")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ledger")
    ap.add_argument("--out-stem", default="CONSISTENCY_REVIEW")
    ap.add_argument("--org", action="store_true")
    ap.add_argument("--finalize", action="store_true")
    a = ap.parse_args(argv)
    ledger = os.path.abspath(a.ledger)
    root = os.path.dirname(ledger)
    led = iss.read_issues(ledger)
    problems = finalize_problems(led, root)
    if a.finalize and problems:
        for p in problems:
            print(f"REFUSED {p}")
        print("FINALIZE REFUSED: nothing written.")
        return 1
    final = a.finalize and not problems
    md = build_markdown(led, final, problems)
    stem = os.path.join(root, a.out_stem)
    with open(stem + ".md", "w", encoding="utf-8") as fh:
        fh.write(md)
    title = "Consistency review: " + (led["meta"].get("product") or "statistical product")
    with open(stem + ".html", "w", encoding="utf-8") as fh:
        fh.write(build_html(md, title))
    written = [stem + ".md", stem + ".html"]
    if a.org:
        with open(stem + ".org", "w", encoding="utf-8") as fh:
            fh.write(build_org(led))
        written.append(stem + ".org")
    boxes = iss.decision(led["issues"], led["answers"])
    print("Decision: " + "; ".join(("[x] " if t else "[ ] ") + l.split(" (")[0] for t, l in boxes))
    for w in written:
        print(f"wrote {os.path.relpath(w, root)}")
    print("FINAL" if final else "PREVIEW" + (f" ({'; '.join(problems)})" if problems else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
