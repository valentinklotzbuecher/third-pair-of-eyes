#!/usr/bin/env python3
"""check_job.py — the stats-review gate: assert that a stage's artifacts exist and are
checkable facts.

    python3 check_job.py --root <job> [--stage intake|document|code-and-data|
                                       statements|challenge|verdict|all]

A stage is not COMPLETE until its gate passes. Standard library only; reads only the
review's own artifacts and 00_ASSIGNMENT.md, never a data file.

intake (also run by every later stage)
  I1  00_INTAKE.md exists, records `Suite version:`, the data mode and the depth, and
      numbers the assignment questions Q1, Q2, …; AGENTS.md and PROGRESS.md exist.
      They are written before any stage work.
  I2  In data mode shared, a job with a .gitignore keeps work/logs, work/results,
      work/challenge and work/pkg out of commits (the job's shared-mode block).
stage reports (every stage report and module report; each within its length
limit for the product's size class, failing above 1.25 times it)
  R1  `## Status`, `## Findings`, `## Leads for later stages`, `## Scope assumptions`
      and `## Coverage` sections; every `### <ID>. <title>` finding block carries
      `bears on:` and `evidence:` lines (missing `where:` or `fix:` WARN).
document
  D1  review/document-REPORT.md passes R1.
  D2  analysis/document/consistency-matrix.csv: required columns, at least one row,
      `status` in {consistent, differs, missing-in-product, missing-elsewhere,
      unverified-here, not-applicable}, `evidence` filled.
  D3  analysis/document/arithmetic-checks.csv: required columns, at least one row;
      `result` in {match, rounding, within-band, mismatch, NONE_FOUND}; a
      `within-band` row states its band in `tolerance`; every non-NONE_FOUND row
      names a `script` that exists; NONE_FOUND only as the single row.
  D4  analysis/document/sensitivity-claims.csv: `classification` in {SUPPORTED,
      QUALIFIED, CONTRADICTED, UNRESOLVED, NONE_FOUND}, `evidence` filled,
      NONE_FOUND only as the single row; a header-only file FAILs.
  D5  report and manuscript products: analysis/document/sap-adherence.csv with rows,
      `status` in {performed as specified, performed with deviation, omitted, post hoc}.
code-and-data
  C1  review/code-and-data-REPORT.md and every fired module's report pass R1.
  C2  analysis/code-and-data/spec-map.csv: rows; `status` in {identical, differs,
      not-implemented, no-code}; `identical`/`differs` rows carry a `code_ref`
      of the form file:line.
  C3  feasibility-matrix.csv and construction-ledger.md exist and are not empty.
  C4  battery-manifest.csv: columns, enums (`state`, `validity`, `row_role`,
      `data_mode`); `data_mode` never above the assignment's mode (`shared` rows need
      mode shared; `synthetic` rows need mode synthetic or shared); artifact-bearing
      states (done, NONREPRODUCED, PROXY) name an existing artifact.
  C5  results.csv: columns; every artifact-bearing manifest row has a results row
      (by spec_id = id, or by artifact); rows with data_mode `synthetic` carry no
      `printed_value` (a synthetic run is never compared with a printed number);
      NONREPRODUCED needs a printed value.
  C6  module-walk.md exists; every module it marks fired has a report under
      analysis/code-and-data/ that is not a NOT_APPLICABLE stub; every module marked
      not applicable has its stub. At depth `quick`, `NOT_RUN — depth quick` rows are
      accepted.
  C7  sample-size-diagnostics fired → assumption-ledger.csv with rows, `warrant` in
      {SOURCED, DERIVED, CONTESTED, TRANSPORTED, UNANCHORED, CONVENIENCE},
      `effect_on_N` filled for every row not SOURCED.
statements
  S1  review/statements-REPORT.md passes R1 and has a table with `Centrality` and
      `Holds` columns.
  S2  analysis/statements/statement-ledger.csv: columns; unique `ST` IDs; enums for
      kind, centrality, holds, status; kernel and evidence filled; not_established
      filled unless holds = holds; at least one primary row.
  S3  analysis/statements/questions.csv has one row per assignment question, `status`
      in {answered, partly answered, cannot be answered from the materials}.
challenge (depth standard and full only)
  X1  review/challenge-REPORT*.md exists with sections (a) to (g).
verdict
  V2  SYNTHESIS.md within its length limit (see Proportion in ../SKILL.md).
  V1  SYNTHESIS.md: title, header line `Verification: <word> · <n> not established /
      <n> narrower / <n> hold` matching the ledger counts; the required sections in
      order; the statement-ledger table carries every ledger ID, with valid Holds;
      every `### F` finding has `bears on:`, `where:` (text | code | text and code |
      unresolved), `evidence:` and `fix:`; one `### Q` block per question.

Exit 0 on PASS, 1 on FAIL. WARN lines do not change the exit code.
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jobfiles as jf  # noqa: E402

AD = "analysis/document"
ACD = "analysis/code-and-data"
AST = "analysis/statements"

MODULES = ("sample-size-diagnostics", "simulation-diagnostics", "estimand-diagnostics",
           "rct-diagnostics", "missing-data-diagnostics", "time-to-event-diagnostics",
           "multiplicity-diagnostics", "regression-model-diagnostics",
           "observational-diagnostics", "prediction-model-diagnostics",
           "bayesian-diagnostics", "small-n-diagnostics")

ENUM = {
    "consistency_status": {"consistent", "differs", "missing-in-product",
                           "missing-elsewhere", "unverified-here", "not-applicable"},
    "arith_result": {"match", "rounding", "within-band", "mismatch", "none_found"},
    "sens_class": {"supported", "qualified", "contradicted", "unresolved", "none_found"},
    "sap_status": {"performed as specified", "performed with deviation", "omitted", "post hoc"},
    "spec_status": {"identical", "differs", "not-implemented", "no-code"},
    "state": {"done", "nonreproduced", "proxy", "blocked", "data_not_shared",
              "not_run", "not_applicable"},
    "validity": {"clean", "unvalidated", "invalid"},
    "row_role": {"verdict-bearing", "rebuttal", "harness"},
    "data_mode": {"none", "synthetic", "shared"},
    "warrant": {"sourced", "derived", "contested", "transported", "unanchored", "convenience"},
    "kind": {"result", "calculation", "assumption", "specification", "interpretation"},
    "centrality": {"primary", "supporting", "peripheral"},
    "holds": {"holds", "narrower", "not established"},
    "status": {"settled", "interim", "untested", "unverifiable", "unverified-here"},
    "q_status": {"answered", "partly answered", "cannot be answered from the materials"},
    "where": {"text", "code", "text and code", "unresolved"},
}
ARTIFACT_STATES = {"done", "nonreproduced", "proxy"}
REPORT_SECTIONS = ("Status", "Findings", "Leads for later stages", "Scope assumptions",
                   "Coverage")
MODE_RANK = {"none": 0, "synthetic": 1, "shared": 2}

SYNTHESIS_SECTIONS = [
    "Status", "What the product establishes and what it does not", "Cross-cutting findings",
    "Statement ledger", "Recomputation table", "Answers to the assignment questions",
    "Data and reproducibility", "Findings", "Limits of this review", "Counts",
]
SHARED_IGNORE = ("work/logs/", "work/results/", "work/challenge/", "work/pkg/")
EVIDENCE_PATH = re.compile(r"\b(?:review|work|analysis|0\d_\w+)/[\w./-]+|\b[\w-]+/[\w./-]*\.\w{1,5}\b")
HEADER = re.compile(r"^Verification:\s*(\w+)\s*·\s*(\d+)\s+not established\s*/\s*(\d+)\s+narrower"
                    r"\s*/\s*(\d+)\s+holds?\s*$")


class Gate:
    def __init__(self, root):
        self.root = root
        self.fails, self.warns = [], []

    def fail(self, code, msg):
        self.fails.append(f"{code} {msg}")

    def warn(self, code, msg):
        self.warns.append(f"{code} {msg}")

    def path(self, rel):
        return os.path.join(self.root, rel)

    def exists(self, rel):
        return os.path.exists(self.path(rel))

    def csv(self, code, rel, required, min_rows=1):
        cols, rows = jf.load_csv(self.path(rel))
        if cols is None:
            self.fail(code, f"{rel} is missing.")
            return None
        missing = [c for c in required if c not in cols]
        if missing:
            self.fail(code, f"{rel} lacks columns: {', '.join(missing)}.")
            return None
        if len(rows) < min_rows:
            self.fail(code, f"{rel} has no rows: a header-only file cannot be told from a "
                            "skipped step.")
            return None
        return rows

    def enum(self, code, rel, rows, col, key, allow_blank=False):
        for i, r in enumerate(rows, 2):
            v = (r.get(col) or "").strip().lower()
            if not v and allow_blank:
                continue
            if v not in ENUM[key]:
                self.fail(code, f"{rel} line {i}: {col} = {r.get(col)!r}; expected one of "
                                f"{', '.join(sorted(ENUM[key]))}.")

    def report(self, code, rel, sections=REPORT_SECTIONS):
        if not self.exists(rel):
            self.fail(code, f"{rel} is missing.")
            return None
        titles = {t.strip().lower() for _, t, _ in jf.md_sections(self.path(rel))}
        for s in sections:
            if s.lower() not in titles:
                self.fail(code, f"{rel} has no `## {s}` section.")
        text = open(self.path(rel), encoding="utf-8").read()
        self.finding_fields(code, rel, text)
        self.length(code, rel, text, "module report" if rel.startswith("analysis/")
                    else "stage report")
        return text

    def length(self, code, rel, text, kind):
        """Proportion: a report or synthesis longer than TOLERANCE times its limit for
        the product's size class fails."""
        size = jf.size_class(self.root)
        limit = jf.WORD_LIMITS[size][kind]
        n = jf.word_count(text)
        if n > limit * jf.TOLERANCE:
            self.fail(code, f"{rel} is {n} words; a {kind} for a {size} product is at most "
                            f"about {limit} (fails above {int(limit * jf.TOLERANCE)}). Cut "
                            "repetition and narrative, not checks or evidence paths.")

    def finding_fields(self, code, rel, text):
        """Every `### <ID>. <title>` block under `## Findings` names what it bears on
        and its evidence; `where:` and `fix:` are expected (WARN)."""
        m = re.search(r"(?ms)^## Findings\s*$(.*?)(?=^## |\Z)", text)
        if not m:
            return
        for block in re.split(r"(?m)^### ", m.group(1))[1:]:
            title = block.splitlines()[0].strip()
            if not re.match(r"[A-Z]{1,5}\d+\.", title):
                continue
            low = block.lower()
            for key in ("bears on:", "evidence:"):
                if key not in low:
                    self.fail(code, f"{rel}: finding `{title[:50]}` lacks `{key}`.")
            for key in ("where:", "fix:"):
                if key not in low:
                    self.warn(code, f"{rel}: finding `{title[:50]}` lacks `{key}`.")


def check_intake(g, assign):
    rel = "00_INTAKE.md"
    if not g.exists(rel):
        g.fail("I1", "00_INTAKE.md is missing: write the intake records (from "
                     "assets/INTAKE-template.md) before any stage work.")
    else:
        text = open(g.path(rel), encoding="utf-8").read()
        if not re.search(r"(?im)^\W*Suite version\W*:?\W*\d+\.\d+", text):
            g.fail("I1", "00_INTAKE.md does not record `Suite version:`.")
        for key in ("data mode", "depth"):
            if key not in text.lower():
                g.fail("I1", f"00_INTAKE.md does not record the {key}.")
        nq = len((assign or {}).get("questions", []))
        for q in range(1, nq + 1):
            if not re.search(rf"\bQ{q}\b", text):
                g.fail("I1", f"00_INTAKE.md does not number the assignment question Q{q}.")
    for rel in ("AGENTS.md", "PROGRESS.md"):
        if not g.exists(rel) or os.path.getsize(g.path(rel)) == 0:
            g.fail("I1", f"{rel} is missing or empty.")
    if jf.data_mode(assign) == "shared" and g.exists(".gitignore"):
        active = {ln.strip() for ln in open(g.path(".gitignore"), encoding="utf-8")
                  if ln.strip() and not ln.lstrip().startswith("#")}
        missing = [p for p in SHARED_IGNORE if p not in active]
        if missing:
            g.fail("I2", f".gitignore lets {', '.join(missing)} into commits: in data mode "
                         "shared the review's work files may hold values derived from patient "
                         "data. Activate the shared-mode block of the job's .gitignore.")


def none_found_rule(g, code, rel, rows, col):
    nf = [r for r in rows if (r.get(col) or "").strip().upper() == "NONE_FOUND"]
    if nf and len(rows) > 1:
        g.fail(code, f"{rel}: NONE_FOUND appears beside other rows.")
    return bool(nf)


def check_document(g, assign):
    g.report("D1", "review/document-REPORT.md")
    rel = f"{AD}/consistency-matrix.csv"
    rows = g.csv("D2", rel, ["element", "product", "status", "evidence"])
    if rows:
        g.enum("D2", rel, rows, "status", "consistency_status")
        for i, r in enumerate(rows, 2):
            if not (r.get("evidence") or "").strip():
                g.fail("D2", f"{rel} line {i}: evidence is empty.")
    rel = f"{AD}/arithmetic-checks.csv"
    rows = g.csv("D3", rel, ["id", "location", "printed", "recomputed", "script", "result"])
    if rows:
        g.enum("D3", rel, rows, "result", "arith_result")
        for i, r in enumerate(rows, 2):
            if (r.get("result") or "").strip().lower() == "within-band" and \
                    not (r.get("tolerance") or "").strip():
                g.fail("D3", f"{rel} line {i}: within-band without the band in `tolerance`.")
        if not none_found_rule(g, "D3", rel, rows, "result"):
            for i, r in enumerate(rows, 2):
                s = (r.get("script") or "").strip()
                if not s or not g.exists(s.split(":")[0]):
                    g.fail("D3", f"{rel} line {i}: script {s!r} does not exist under the job.")
    rel = f"{AD}/sensitivity-claims.csv"
    rows = g.csv("D4", rel, ["claim", "classification", "evidence"])
    if rows:
        g.enum("D4", rel, rows, "classification", "sens_class")
        none_found_rule(g, "D4", rel, rows, "classification")
        for i, r in enumerate(rows, 2):
            if not (r.get("evidence") or "").strip():
                g.fail("D4", f"{rel} line {i}: evidence is empty.")
    if jf.product_type(assign) in ("report", "manuscript"):
        rel = f"{AD}/sap-adherence.csv"
        rows = g.csv("D5", rel, ["analysis", "status"])
        if rows:
            g.enum("D5", rel, rows, "status", "sap_status")


def module_walk(g, depth):
    """{module: 'fired'|'not applicable'|'not run'} from module-walk.md: a table
    `| Module | Decision | Condition and evidence |` (or list items `- <module>:
    <decision> — <evidence>`), the decision read from its own cell, never from the
    evidence text."""
    rel = f"{ACD}/module-walk.md"
    if not g.exists(rel):
        g.fail("C6", f"{rel} is missing.")
        return {}
    text = open(g.path(rel), encoding="utf-8").read()
    decisions = {}
    for line in text.splitlines():
        cells = None
        if line.strip().startswith("|"):
            cells = [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]
        else:
            lm = re.match(r"^\s*[-*]\s+`?([a-z-]+)`?\s*:\s*(.+)$", line)
            if lm:
                cells = [lm.group(1), re.split(r"\s+[—–(-]\s*|\s*\(", lm.group(2), maxsplit=1)[0]]
        if not cells or len(cells) < 2 or cells[0] not in MODULES:
            continue
        d = re.sub(r"[\s_]+", " ", cells[1].strip().lower())
        if d.startswith("fired"):
            decisions[cells[0]] = "fired"
        elif d.startswith(("not applicable", "n/a")):
            decisions[cells[0]] = "not applicable"
        elif d.startswith("not run"):
            decisions[cells[0]] = "not run"
        else:
            decisions[cells[0]] = "unknown:" + cells[1][:40]
    out = {}
    for m in MODULES:
        state = decisions.get(m)
        if state is None:
            g.fail("C6", f"{rel} has no row for {m}: every module gets a row "
                         "`| <module> | <decision> | <evidence> |`.")
            continue
        if state.startswith("unknown:"):
            g.fail("C6", f"{rel}: decision for {m} is {state[8:]!r}; write `fired`, "
                         "`not applicable` or `not run — depth quick`.")
            continue
        if state == "not run" and depth != "quick":
            g.fail("C6", f"{m} is marked not run at depth {depth}: only depth quick skips "
                         "modules.")
        out[m] = state
    for m, state in out.items():
        rep = f"{ACD}/{m}-REPORT.md"
        if state == "fired":
            if not g.exists(rep) or os.path.getsize(g.path(rep)) == 0:
                g.fail("C6", f"{m} fired but {rep} is missing or empty.")
            elif re.search(r"^Status:\s*NOT_APPLICABLE", open(g.path(rep), encoding="utf-8").read(),
                           re.M):
                g.fail("C6", f"{m} fired but its report is a NOT_APPLICABLE stub.")
            else:
                g.report("C1", rep)
        elif state == "not applicable" and not g.exists(rep):
            g.fail("C6", f"{m} is not applicable but has no stub at {rep} "
                         "(`Status: NOT_APPLICABLE — <reason>`).")
    return out


def check_code_and_data(g, assign):
    mode = jf.data_mode(assign) or "none"
    depth = jf.depth(assign)
    g.report("C1", "review/code-and-data-REPORT.md")
    rel = f"{ACD}/spec-map.csv"
    rows = g.csv("C2", rel, ["printed_ref", "element", "printed_value", "code_ref", "status"])
    if rows:
        g.enum("C2", rel, rows, "status", "spec_status")
        for i, r in enumerate(rows, 2):
            if (r.get("status") or "").strip().lower() in ("identical", "differs") and \
                    not re.search(r"\S+:\d+", r.get("code_ref") or ""):
                g.fail("C2", f"{rel} line {i}: code_ref {r.get('code_ref')!r} is not file:line.")
    for rel in (f"{ACD}/feasibility-matrix.csv", f"{ACD}/construction-ledger.md"):
        if not g.exists(rel) or os.path.getsize(g.path(rel)) == 0:
            g.fail("C3", f"{rel} is missing or empty.")
    rel = f"{ACD}/battery-manifest.csv"
    man = g.csv("C4", rel, ["id", "family", "hypothesis", "spec", "data_mode", "artifact",
                            "seed", "state", "validity", "row_role"])
    if man:
        for col, key in (("state", "state"), ("validity", "validity"),
                         ("row_role", "row_role"), ("data_mode", "data_mode")):
            g.enum("C4", rel, man, col, key)
        for i, r in enumerate(man, 2):
            dm = (r.get("data_mode") or "").strip().lower()
            if dm in MODE_RANK and MODE_RANK[dm] > MODE_RANK.get(mode, 0):
                g.fail("C4", f"{rel} line {i}: a `{dm}` check in a job whose data mode is `{mode}`.")
            st = (r.get("state") or "").strip().lower()
            art = (r.get("artifact") or "").strip()
            if st in ARTIFACT_STATES:
                if not art or art.upper() == "NA":
                    g.fail("C4", f"{rel} line {i}: state {st} needs an artifact.")
                else:
                    for a in re.split(r"[;,]\s*", art):
                        if a and not g.exists(a):
                            g.fail("C4", f"{rel} line {i}: artifact {a} does not exist.")
            if not (r.get("seed") or "").strip():
                g.fail("C4", f"{rel} line {i}: seed is blank (write NA for deterministic checks).")
    rel = f"{ACD}/results.csv"
    res = g.csv("C5", rel, ["spec_id", "data_mode", "printed_value", "estimate", "state",
                            "artifact"], min_rows=0)
    if res is not None and man:
        ids = {(r.get("spec_id") or "").strip() for r in res}
        arts = {(r.get("artifact") or "").strip() for r in res}
        for r in man:
            if (r.get("state") or "").strip().lower() in ARTIFACT_STATES:
                if r["id"].strip() not in ids and (r.get("artifact") or "").strip() not in arts:
                    g.fail("C5", f"manifest row {r['id']} ({r['state']}) has no results.csv row.")
        for i, r in enumerate(res, 2):
            dm = (r.get("data_mode") or "").strip().lower()
            if dm == "synthetic" and (r.get("printed_value") or "").strip():
                g.fail("C5", f"{rel} line {i}: a synthetic-data result carries a printed value; "
                             "synthetic runs are never compared with printed numbers.")
            if (r.get("state") or "").strip().lower() == "nonreproduced" and \
                    not (r.get("printed_value") or "").strip():
                g.fail("C5", f"{rel} line {i}: NONREPRODUCED without the printed value.")
    walk = module_walk(g, depth)
    if walk.get("sample-size-diagnostics") == "fired":
        rel = f"{ACD}/assumption-ledger.csv"
        rows = g.csv("C7", rel, ["id", "assumption", "value", "source_cited", "warrant",
                                 "effect_on_N"])
        if rows:
            g.enum("C7", rel, rows, "warrant", "warrant")
            for i, r in enumerate(rows, 2):
                if (r.get("warrant") or "").strip().lower() != "sourced" and \
                        not (r.get("effect_on_N") or "").strip():
                    g.fail("C7", f"{rel} line {i}: effect_on_N is empty for a planning value "
                                 "that is not SOURCED.")


def ledger_rows(g, code="S2"):
    rel = f"{AST}/statement-ledger.csv"
    return rel, g.csv(code, rel, ["row_id", "kind", "statement", "location", "centrality",
                                  "holds", "kernel", "not_established", "strongest_defence",
                                  "status", "evidence"])


def check_statements(g, assign):
    text = g.report("S1", "review/statements-REPORT.md")
    if text is not None:
        ok = any(any(h.lower() == "centrality" for h in hdr) and any(h.lower() == "holds"
                 for h in hdr) for hdr, _ in jf.md_tables(text))
        if not ok:
            g.fail("S1", "review/statements-REPORT.md has no table with Centrality and Holds "
                         "columns.")
    rel, rows = ledger_rows(g)
    if rows:
        for col in ("kind", "centrality", "holds", "status"):
            g.enum("S2", rel, rows, col, col)
        seen = set()
        for i, r in enumerate(rows, 2):
            rid = (r.get("row_id") or "").strip()
            if not re.fullmatch(r"ST\d+", rid):
                g.fail("S2", f"{rel} line {i}: row_id {rid!r} is not ST<number>.")
            if rid in seen:
                g.fail("S2", f"{rel} line {i}: duplicate row_id {rid}.")
            seen.add(rid)
            for col in ("statement", "kernel", "evidence"):
                if not (r.get(col) or "").strip():
                    g.fail("S2", f"{rel} line {i}: {col} is empty.")
            if (r.get("holds") or "").strip().lower() in ("narrower", "not established") and \
                    not (r.get("not_established") or "").strip():
                g.fail("S2", f"{rel} line {i}: holds is {r['holds']} but not_established is empty.")
        if not any((r.get("centrality") or "").strip().lower() == "primary" for r in rows):
            g.fail("S2", f"{rel} has no primary row.")
    questions = (assign or {}).get("questions", [])
    rel = f"{AST}/questions.csv"
    qrows = g.csv("S3", rel, ["q_id", "question", "answer", "basis", "status"],
                  min_rows=0)
    if qrows is not None:
        if len(qrows) != len(questions):
            g.fail("S3", f"{rel} has {len(qrows)} rows for {len(questions)} assignment questions.")
        g.enum("S3", rel, qrows, "status", "q_status")


def check_challenge(g, assign):
    if jf.depth(assign) == "quick":
        g.warn("X1", "depth quick: no challenge stage; the synthesis must say so.")
        return
    reports = sorted(glob.glob(g.path("review/challenge-REPORT*.md")))
    if not reports:
        g.fail("X1", "review/challenge-REPORT*.md is missing: without the challenge the run is "
                     "INTERIM.")
        return
    for p in reports:
        raw = open(p, encoding="utf-8").read()
        text = raw.lower()
        for part in ("(a)", "(b)", "(c)", "(d)", "(e)", "(f)", "(g)"):
            if part not in text:
                g.fail("X1", f"{os.path.relpath(p, g.root)} lacks part {part}.")
        g.length("X1", os.path.relpath(p, g.root), raw, "challenge report")


def check_verdict(g, assign):
    rel = "SYNTHESIS.md"
    if not g.exists(rel):
        g.fail("V1", "SYNTHESIS.md is missing.")
        return
    text = open(g.path(rel), encoding="utf-8").read()
    lines = text.splitlines()
    g.length("V2", rel, text, "synthesis")
    if not lines or not lines[0].startswith("# Synthesis"):
        g.fail("V1", "SYNTHESIS.md does not start with `# Synthesis — …`.")
    header = next((ln.strip() for ln in lines[1:6] if ln.strip()), "")
    hm = HEADER.match(header)
    _, rows = ledger_rows(g, code="V1")
    tables = jf.md_tables(text)
    led = [t for t in tables if any(h.lower().startswith("statement") for h in t[0])
           and any(h.lower() == "holds" for h in t[0])]
    # The verdict's own ledger: row ID -> (holds, row text). The verdict may move a row
    # from the statements stage's rating; the header counts this table, not the CSV.
    table = {}
    if led:
        hdr, trows = led[0]
        hi = [h.lower() for h in hdr].index("holds")
        for tr in trows:
            m = re.search(r"\b(ST\d+)\)?\s*$", tr[0]) or re.search(r"\b(ST\d+)\b", tr[0])
            if m:
                table[m.group(1)] = ((tr[hi] if hi < len(tr) else "").strip().lower(),
                                     " | ".join(tr))
    if not hm:
        g.fail("V1", f"header line {header!r} is not `Verification: <word> · <n> not established "
                     "/ <n> narrower / <n> hold`.")
    elif table or rows:
        held = [h for h, _ in table.values()] if table else \
            [(r.get("holds") or "").strip().lower() for r in rows]
        counts = {h: held.count(h) for h in ("not established", "narrower", "holds")}
        printed = dict(zip(("not established", "narrower", "holds"), map(int, hm.group(2, 3, 4))))
        if printed != counts:
            g.fail("V1", f"header counts {printed} differ from the statement-ledger table's "
                         f"{counts}.")
        if hm.group(1).upper() not in ("OPEN", "TRUSTWORTHY", "UNSOUND"):
            g.fail("V1", f"Verification word {hm.group(1)!r} is not OPEN, TRUSTWORTHY or UNSOUND.")
    staged = {r["row_id"].strip(): (r.get("holds") or "").strip().lower() for r in rows or []}
    for rid, (h, rowtext) in sorted(table.items()):
        before = staged.get(rid)
        if before and h and h != before and not EVIDENCE_PATH.search(rowtext):
            g.fail("V1", f"statement-ledger table: {rid} moves from {before!r} to {h!r} without "
                         "naming the evidence it turns on (a path such as work/logs/<file>.log).")
    titles = [(lvl, t.strip()) for lvl, t, _ in jf.md_sections(g.path(rel))]
    h2 = [t for lvl, t in titles if lvl == 2]
    pos = -1
    for s in SYNTHESIS_SECTIONS:
        if s not in h2:
            g.fail("V1", f"SYNTHESIS.md lacks `## {s}`.")
            continue
        if h2.index(s) < pos:
            g.fail("V1", f"`## {s}` is out of order.")
        pos = h2.index(s)
    if not led:
        g.fail("V1", "SYNTHESIS.md has no statement-ledger table with a Holds column.")
    elif rows:
        hdr, trows = led[0]
        hi = [h.lower() for h in hdr].index("holds")
        ids = set()
        for tr in trows:
            m = re.search(r"\b(ST\d+)\)?\s*$", tr[0]) or re.search(r"\b(ST\d+)\b", tr[0])
            if m:
                ids.add(m.group(1))
            if hi < len(tr) and tr[hi].strip().lower() not in ENUM["holds"]:
                g.fail("V1", f"statement-ledger table: Holds {tr[hi]!r} is not holds, narrower "
                             "or not established.")
        missing = [r["row_id"] for r in rows if r["row_id"].strip() not in ids]
        if missing:
            g.fail("V1", f"statement-ledger table lacks rows: {', '.join(missing)}.")
    blocks = re.split(r"(?m)^### ", text)
    for b in blocks[1:]:
        title = b.splitlines()[0]
        if not re.match(r"F\d+\.", title):
            continue
        for key in ("bears on:", "where:", "evidence:", "fix:"):
            if key not in b.lower():
                g.fail("V1", f"finding `{title[:60]}` lacks `{key}`.")
        wm = re.search(r"(?im)^where:\s*(.+?)\s*$", b)
        if wm and wm.group(1).strip().lower() not in ENUM["where"]:
            g.fail("V1", f"finding `{title[:60]}`: where = {wm.group(1)!r}; expected text, code, "
                         "text and code, or unresolved.")
    nq = len((assign or {}).get("questions", []))
    qb = len(re.findall(r"(?m)^### Q\d+\.", text))
    if nq and qb != nq:
        g.fail("V1", f"SYNTHESIS.md answers {qb} questions; the assignment asks {nq}.")


STAGES = {
    "intake": check_intake,
    "document": check_document,
    "code-and-data": check_code_and_data,
    "statements": check_statements,
    "challenge": check_challenge,
    "verdict": check_verdict,
}


def main(argv=None):
    ap = argparse.ArgumentParser(description="stats-review stage gate")
    ap.add_argument("--root", default=".")
    ap.add_argument("--stage", default="all", choices=list(STAGES) + ["all"])
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    assign = jf.read_assignment(root)
    g = Gate(root)
    if assign is None:
        g.fail("A0", "00_ASSIGNMENT.md is missing.")
    stages = list(STAGES) if a.stage == "all" else \
        (["intake", a.stage] if a.stage != "intake" else ["intake"])
    for s in stages:
        STAGES[s](g, assign)
    for w in g.warns:
        print(f"WARN {w}")
    for f in g.fails:
        print(f"FAIL {f}")
    print("PASS" if not g.fails else f"FAIL ({len(g.fails)})")
    return 0 if not g.fails else 1


if __name__ == "__main__":
    sys.exit(main())
