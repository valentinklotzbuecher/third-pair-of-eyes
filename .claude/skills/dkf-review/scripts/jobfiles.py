"""jobfiles.py — shared readers for a dkf-review job folder.

Standard library only. Imported by scan_job.py and check_job.py here, and by the
dkf-review-audit and dkf-consistency-review scripts (they add this folder to
sys.path). Nothing here opens a data file: the readers touch only the assignment,
intake, ledgers and reports the review itself writes, plus Quarto source text.
"""
import csv
import json
import os
import re

PRODUCT_TYPES = ("sse", "protocol", "sap", "report", "manuscript", "other")
DATA_MODES = ("none", "synthetic", "shared")
DEPTHS = ("quick", "standard", "full")

# Extensions treated as data-like by the clearance guard (lower case, with dot).
DATA_EXTENSIONS = frozenset({
    ".csv", ".tsv", ".rds", ".rda", ".rdata", ".sav", ".zsav", ".por", ".dta",
    ".sas7bdat", ".sas7bcat", ".xpt", ".xlsx", ".xls", ".xlsm", ".ods",
    ".parquet", ".feather", ".arrow", ".sqlite", ".db", ".mdb", ".accdb",
    ".h5", ".hdf5", ".fst", ".qs", ".json", ".ndjson", ".jsonl",
})
# Directories that hold tooling or caches, never inputs under review.
INFRA_DIRS = frozenset({".git", ".svn", ".quarto", "_extensions", "renv",
                        "__pycache__", ".Rproj.user", "_freeze", "site_libs"})
# Folders the review itself writes.
REVIEW_DIRS = frozenset({"review", "analysis", "work"})
PACKET_DIRS = ("01_product", "02_governing", "03_previous", "04_data",
               "05_synthetic", "lit")

PLACEHOLDER = re.compile(r"^\s*<[^>]*>\s*$")
FIELD_LINE = re.compile(r"^\s*[-*]\s+([A-Za-z][A-Za-z ()/'-]*?)\s*:\s*(.*?)\s*$")


# Proportion. A product of at most SHORT_PAGES rendered pages is "short"; its review
# runs fewer agents and writes less. The limits are word targets the skills state; the
# gates fail only above TOLERANCE times a limit, so a slightly long report is not
# rewritten.
SHORT_PAGES = 10
TOLERANCE = 1.25
WORD_LIMITS = {
    "short": {"stage report": 1500, "module report": 600, "challenge report": 1500,
              "synthesis": 3000},
    "long": {"stage report": 4000, "module report": 2000, "challenge report": 4000,
             "synthesis": 8000},
}


def product_pages(root):
    """Rendered pages of the product's PDFs (under 01_product/), from the intake scan;
    None when the scan or the page counts are missing."""
    try:
        with open(os.path.join(root, "review", "intake-scan.json"), encoding="utf-8") as fh:
            scan = json.load(fh)
    except (OSError, ValueError):
        return None
    pages = [int(str(r.get("pages", "")).strip()) for r in scan.get("pdfs", [])
             if str(r.get("path", "")).replace("\\", "/").startswith("01_product/")
             and str(r.get("pages", "")).strip().isdigit()]
    return sum(pages) if pages else None


def size_class(root):
    """`short` for a product of at most SHORT_PAGES rendered pages, else `long` (also
    when the page count is unknown, so an unknown size never tightens a limit)."""
    n = product_pages(root)
    return "short" if n is not None and n <= SHORT_PAGES else "long"


def word_count(text):
    return len(re.findall(r"\S+", text or ""))


def is_placeholder(value):
    """True for an unfilled template value such as `<none | synthetic | shared>`."""
    return value is None or not value.strip() or bool(PLACEHOLDER.match(value))


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def norm_key(key):
    return re.sub(r"[^a-z0-9]+", "_", key.strip().lower()).strip("_")


def read_assignment(root):
    """Parse 00_ASSIGNMENT.md. Returns a dict with the `- Field: value` lines (keys
    normalised: `data_mode`, `product_type`, `documents`, …), `questions` (the
    numbered items under the questions heading), `dependencies` (bullets under the
    documents heading) and `path`. Returns None when the file is missing."""
    path = os.path.join(root, "00_ASSIGNMENT.md")
    if not os.path.exists(path):
        return None
    text = strip_comments(open(path, encoding="utf-8").read())
    out = {"path": path, "questions": [], "dependencies": []}
    section = ""
    for line in text.splitlines():
        h = re.match(r"^\s*#{1,6}\s+(.*?)\s*$", line)
        if h:
            section = h.group(1).lower()
            continue
        if "issues for reviewer" in section or section.startswith("question"):
            q = re.match(r"^\s*(\d+)[.)]\s+(.*\S)\s*$", line)
            if q and not is_placeholder(q.group(2)):
                out["questions"].append(q.group(2))
            continue
        if "depends on" in section or "other documents" in section:
            b = re.match(r"^\s*[-*]\s+(.*\S)\s*$", line)
            if b and not re.search(r"<[^>]*>", b.group(1)):
                out["dependencies"].append(b.group(1))
            continue
        m = FIELD_LINE.match(line)
        if m:
            out[norm_key(m.group(1))] = m.group(2)
    return out


def field(assign, key, default=None):
    """A filled-in assignment field, lower-cased and stripped, or `default`."""
    if not assign:
        return default
    v = assign.get(key)
    if is_placeholder(v):
        return default
    return v.strip()


def data_mode(assign):
    v = field(assign, "data_mode")
    return v.lower() if v else None


def depth(assign):
    v = field(assign, "depth")
    return v.lower() if v and v.lower() in DEPTHS else "standard"


def product_type(assign):
    v = field(assign, "product_type")
    return v.lower() if v else None


def non_patient_files(assign):
    """Paths listed under `Non-patient files:` (comma or semicolon separated)."""
    v = field(assign, "non_patient_files")
    if not v or v.lower() in ("none", "n/a", "not applicable"):
        return []
    parts = re.split(r"[;,]", v)
    out = []
    for p in parts:
        p = re.sub(r"\(.*?\)", "", p).strip().strip("`")
        if p:
            out.append(p)
    return out


def load_csv(path):
    """(columns, rows) for a CSV the review wrote; rows are dicts. Missing → (None, [])."""
    if not os.path.exists(path):
        return None, []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = [r for r in reader if any((v or "").strip() for v in r.values())]
        return [c.strip() for c in (reader.fieldnames or [])], rows


def md_sections(path):
    """[(level, title, start_line)] of the markdown headings in a file."""
    if not os.path.exists(path):
        return []
    out = []
    in_fence = False
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            out.append((len(m.group(1)), m.group(2), n))
    return out


def md_tables(text):
    """Every pipe table in markdown text as (header_cells, [row_cells])."""
    tables = []
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].strip().startswith("|") and re.match(
                r"^\s*\|?\s*:?-{2,}", lines[i + 1].strip().lstrip("|")):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            tables.append((header, rows))
            i = j
        else:
            i += 1
    return tables


BLOCK_SCALAR = ("|", ">", "|-", ">-", "|+", ">+")


def front_matter(text):
    """Very small YAML front-matter reader for Quarto sources: nested mappings by
    indentation, scalars, block scalars and `- item` lists (list items are kept as
    text). Enough for title, author, date and params; anything it cannot read is
    skipped, never guessed. An empty value reads as {} (unset)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    body = []
    for line in lines[1:]:
        if line.strip() in ("---", "..."):
            break
        body.append(line)
    root = {}
    stack = [(-1, root, None, None)]          # (indent, container, parent, key)
    block = None                               # (indent, container, key, parts)
    for raw in body:
        indent = len(raw) - len(raw.lstrip(" "))
        if block is not None:
            if not raw.strip() or indent > block[0]:
                block[3].append(raw.strip())
                continue
            block[1][block[2]] = " ".join(p for p in block[3] if p)
            block = None
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = raw.strip()
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        _, container, parent, pkey = stack[-1]
        if line == "-" or line.startswith("- "):
            if isinstance(container, dict) and not container and parent is not None:
                lst = []
                parent[pkey] = lst
                stack[-1] = (stack[-1][0], lst, parent, pkey)
                container = lst
            if isinstance(container, list):
                container.append(unquote(line[1:].strip()))
            continue
        m = re.match(r"^([^:]+?):(?:\s+(.*)|\s*)$", line)
        if not m or not isinstance(container, dict):
            continue
        key = m.group(1).strip().strip("'\"")
        value = (m.group(2) or "").strip()
        if value in BLOCK_SCALAR:
            block = (indent, container, key, [])
        elif value == "":
            child = {}
            container[key] = child
            stack.append((indent, child, container, key))
        else:
            container[key] = unquote(value)
    if block is not None:
        block[1][block[2]] = " ".join(p for p in block[3] if p)
    return root


def unquote(value):
    v = value.strip()
    v = re.sub(r"\s+#.*$", "", v) if not v.startswith(("'", '"')) else v
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
    return v
