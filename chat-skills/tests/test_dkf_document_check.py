"""Tests for the chat skill dkf-document-check: its helpers, its upload ZIP and its
copies of the suite's files.

Run from the repository root:  python3 -m pytest -q -p no:cacheprovider chat-skills/tests
The comparison with recompute.R runs when Rscript is installed.
"""
import ast
import importlib.util
import math
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHAT = ROOT / "chat-skills"
SKILL = CHAT / "dkf-document-check"
SUITE = ROOT / ".claude" / "skills"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rc = _load("recompute", SKILL / "scripts" / "recompute.py")
build_zip = _load("build_zip", CHAT / "build_zip.py")


def near(a, b, tol=1e-6):
    """R's all.equal(): relative difference unless the target is tiny."""
    scale = abs(b)
    return (abs(a - b) / scale if scale > tol else abs(a - b)) <= tol


# ---- recompute.py: the cases of the suite's test_recompute.R ----------------------

def test_printed_values():
    assert rc.number_token("12.30%") == "12.30"
    assert rc.parse_printed("−0.20") == -0.20
    assert rc.parse_printed("1,234") == 1234
    assert rc.parse_printed("12 weeks") == 12
    assert rc.parse_printed("no number") is None
    assert rc.printed_decimals("12.30") == 2
    assert rc.printed_decimals("84") == 0
    assert rc.round_half_up(2.5) == 3
    assert rc.round_half_up(-2.5) == -3
    assert near(rc.round_half_up(0.125, 2), 0.13)


def test_agreement():
    assert rc.agree("0.5", 0.5) == "match"
    assert rc.agree("33.3", 100 / 3) == "rounding"
    assert rc.agree("3", 2.5) == "rounding"
    assert rc.agree("33.4", 100 / 3) == "mismatch"
    assert rc.check_pct("33.3%", 17, 51) == "rounding"
    assert rc.check_sum([10, 5, 30], 50)["result"] == "mismatch"
    assert rc.check_sum([10, 5, 30, 30, 5, 5, 15], 100)["result"] == "match"
    assert rc.agree_band("81%", 80.4, band=1.2) == "within-band"
    assert rc.agree_band("81%", 78.0, band=1.2) == "mismatch"
    assert rc.agree_band("80.4", 80.42, band=1) == "rounding"
    assert rc.agree_interval("0.20", 0.196, 0.204) == "within-band"
    assert rc.agree_interval("0.25", 0.196, 0.204) == "mismatch"
    with pytest.raises(TypeError):
        rc.agree(["1", "2"], 1)


def test_grim():
    assert rc.grim_ok("2.40", 10)
    assert not rc.grim_ok("2.47", 10)
    assert rc.grim_ok("2.47", 15)


def test_intervals_and_p_values():
    assert near(rc.se_from_ci(-1.96, 1.96), 1, 1e-3)
    assert near(rc.p_from_ci(1.96, 0, 3.92), 0.05, 1e-3)
    lo, hi = rc.ci_from_p(0.7, rc.p_from_ci(0.7, 0.5, 0.98, ratio=True), ratio=True)
    assert near(lo, 0.5) and near(hi, 0.98)
    assert abs(rc.ci_asymmetry(2, 1, 4, ratio=True)) < 1e-12
    assert abs(rc.ci_asymmetry(2, 1, 4)) > 0.1
    lo, hi = rc.wilson_ci(7, 20)  # R: prop.test(7, 20, correct = FALSE)
    assert near(lo, 0.181191824101082, 1e-8) and near(hi, 0.567145723314764, 1e-8)
    rd = rc.rd_ci(56, 70, 48, 80)  # Newcombe (1998), method 10: 0.0524 to 0.3339
    assert abs(rd["lo"] - 0.0524) < 5e-4 and abs(rd["hi"] - 0.3339) < 5e-4
    assert near(rc.rr_ci(20, 100, 10, 100)["est"], 2)
    assert near(rc.or_ci(20, 100, 10, 100)["est"], (20 * 90) / (80 * 10))


def test_sample_size_building_blocks():
    assert near(rc.inflate_dropout(84, 0.1), 93.333333, 1e-6)
    assert near(rc.inflate_dropout(84, 0.1, "multiply"), 92.4)
    assert rc.round_up_to(94, 10) == 100
    assert rc.round_up_to(93.3, 4) == 96
    assert near(rc.n_two_props(0.40, 0.57)["n1"], 134.486544438736, 1e-4)  # power.prop.test
    assert abs(rc.n_two_means(0.5, 1)["n1"] - 63.7657637142739) < 0.5    # power.t.test
    assert math.ceil(rc.events_schoenfeld(0.7)) == 247
    assert near(rc.event_prob(rc.hazard_from_surv(0.40, 304), 304), 0.60)
    assert near(rc.design_effect(20, 0.05), 1.95)
    assert rc.design_effect(20, 0.05, cv=0.5) > 1.95
    assert near(rc.mcse_prop(0.8, 5000), 0.005657, 1e-3)


def test_t_distribution():
    assert near(rc.qt(0.975, 10), 2.22813885198627, 1e-10)
    assert near(rc.qt(0.9, 3.5), 1.5765766051364, 1e-10)
    assert near(rc.pt(-1.3, 7.5), 0.116063389407804, 1e-10)
    assert near(rc.pt(2.2, 120), 0.985138801087382, 1e-10)
    assert rc.pt(0, 4) == 0.5
    for p, df in ((0.025, 2), (0.6, 33.3), (0.999, 15)):
        assert near(rc.pt(rc.qt(p, df), df), p, 1e-10)


def test_helpers_need_only_the_standard_library():
    tree = ast.parse((SKILL / "scripts" / "recompute.py").read_text(encoding="utf-8"))
    imported = {a.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for a in node.names}
    imported |= {node.module.split(".")[0] for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom)}
    assert imported <= {"math", "re", "statistics"}
    assert all(hasattr(rc, name) for name in rc.__all__)


# ---- recompute.py against the suite's recompute.R ---------------------------------

NUMERIC = [
    ("qt(0.8, 125.6)", lambda: rc.qt(0.8, 125.6)),
    ("pt(-2.7, 3.2)", lambda: rc.pt(-2.7, 3.2)),
    ("se_from_ci(0.5, 0.98, ratio = TRUE)", lambda: rc.se_from_ci(0.5, 0.98, ratio=True)),
    ("p_from_ci(-3.1, -5.9, -0.3)", lambda: rc.p_from_ci(-3.1, -5.9, -0.3)),
    ("ci_from_p(0.7, 0.03, ratio = TRUE)[1]", lambda: rc.ci_from_p(0.7, 0.03, ratio=True)[0]),
    ("ci_from_p(-2.1, 0.2)[2]", lambda: rc.ci_from_p(-2.1, 0.2)[1]),
    ("ci_asymmetry(2, 1.1, 3.9, ratio = TRUE)", lambda: rc.ci_asymmetry(2, 1.1, 3.9, ratio=True)),
    ("wilson_ci(3, 41, level = 0.9)[1]", lambda: rc.wilson_ci(3, 41, level=0.9)[0]),
    ("rd_ci(56, 70, 48, 80)[['lo']]", lambda: rc.rd_ci(56, 70, 48, 80)["lo"]),
    ("rd_ci(12, 40, 7, 45, 'wald')[['hi']]", lambda: rc.rd_ci(12, 40, 7, 45, "wald")["hi"]),
    ("rr_ci(20, 100, 10, 100)[['lo']]", lambda: rc.rr_ci(20, 100, 10, 100)["lo"]),
    ("or_ci(31, 120, 18, 115)[['hi']]", lambda: rc.or_ci(31, 120, 18, 115)["hi"]),
    ("n_two_means(0.5, 1)[['n1']]", lambda: rc.n_two_means(0.5, 1)["n1"]),
    ("n_two_means(12, 30, alpha = 0.025, power = 0.9, k = 2, sided = 1)[['n1']]",
     lambda: rc.n_two_means(12, 30, alpha=0.025, power=0.9, k=2, sided=1)["n1"]),
    ("n_two_props(0.2, 0.3, k = 1.5, correct = TRUE)[['n1']]",
     lambda: rc.n_two_props(0.2, 0.3, k=1.5, correct=True)["n1"]),
    ("events_schoenfeld(0.75, power = 0.9, alloc = 0.4)",
     lambda: rc.events_schoenfeld(0.75, power=0.9, alloc=0.4)),
    ("design_effect(12, 0.03, cv = 0.4)", lambda: rc.design_effect(12, 0.03, cv=0.4)),
    ("inflate_dropout(84, 0.15)", lambda: rc.inflate_dropout(84, 0.15)),
    ("mcse_prop(0.83, 1000)", lambda: rc.mcse_prop(0.83, 1000)),
]

TEXT = [
    ('agree("12.35", 12.345)', lambda: rc.agree("12.35", 12.345)),
    ('agree("12.3", 12.345)', lambda: rc.agree("12.3", 12.345)),
    ('agree("0.05", 0.0499999)', lambda: rc.agree("0.05", 0.0499999)),
    ('agree_band("47.1%", 46.6, 0.6)', lambda: rc.agree_band("47.1%", 46.6, 0.6)),
    ('agree_interval("1.4", 1.35, 1.44)', lambda: rc.agree_interval("1.4", 1.35, 1.44)),
    ('check_pct("12.5%", 5, 40)', lambda: rc.check_pct("12.5%", 5, 40)),
    ('grim_ok("3.17", 12)', lambda: rc.grim_ok("3.17", 12)),
    ('grim_ok("3.18", 12)', lambda: rc.grim_ok("3.18", 12)),
]


@pytest.mark.skipif(shutil.which("Rscript") is None, reason="Rscript not installed")
def test_matches_recompute_R(tmp_path):
    lines = [f'source("{(SUITE / "dkf-review" / "assets" / "recompute.R").as_posix()}")']
    lines += [f'cat(sprintf("%.17g", {expr}), "\\n", sep = "")' for expr, _ in NUMERIC]
    lines += [f'cat(as.character({expr}), "\\n", sep = "")' for expr, _ in TEXT]
    script = tmp_path / "cases.R"
    script.write_text("\n".join(lines) + "\n", encoding="utf-8")
    out = subprocess.run(["Rscript", str(script)], capture_output=True, text=True, check=True)
    got = out.stdout.split()
    assert len(got) == len(NUMERIC) + len(TEXT), out.stderr
    for (expr, fn), r in zip(NUMERIC, got):
        assert near(fn(), float(r), 1e-9), f"{expr}: Python {fn()!r}, R {r}"
    for (expr, fn), r in zip(TEXT, got[len(NUMERIC):]):
        py = fn()
        py = str(py).upper() if isinstance(py, bool) else py
        assert py == r, f"{expr}: Python {py!r}, R {r}"


# ---- The skill's files and its upload ZIP -----------------------------------------

def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md must open with a frontmatter block"
    return {k: v for k, v in re.findall(r"^([a-z-]+):[ \t]*(.*)$", m.group(1), re.M)}


def test_frontmatter_meets_the_upload_rules():
    meta = frontmatter(SKILL / "SKILL.md")
    name, desc = meta["name"], meta["description"]
    assert name == SKILL.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64
    assert "claude" not in name and "anthropic" not in name
    assert 0 < len(desc) <= 1024
    assert "<" not in desc and ">" not in desc
    assert ": " not in desc and not desc.startswith(("'", '"', ">", "|", "-"))
    assert "metadata" in meta


def test_paths_named_in_the_skill_exist():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    named = set(re.findall(r"`((?:scripts|references)/[^`]+)`", text))
    assert named, "SKILL.md names its scripts and references"
    for rel in named:
        assert (SKILL / rel).is_file(), rel


def test_copies_match_the_suite():
    for ref in sorted((SKILL / "references").iterdir()):
        suite_ref = SUITE / "dkf-review" / "references" / ref.name
        assert ref.read_bytes() == suite_ref.read_bytes(), (
            f"references/{ref.name} differs from the suite's copy: copy it again and "
            "rebuild the ZIP")
    assert ((SKILL / "LICENSE-research_skills").read_bytes()
            == (SUITE / "LICENSE-research_skills").read_bytes())


def test_zip_matches_the_folder():
    zpath = CHAT / f"{SKILL.name}.zip"
    assert zpath.is_file(), "run python3 chat-skills/build_zip.py"
    want = {f"{SKILL.name}/{p.relative_to(SKILL).as_posix()}": p.read_bytes()
            for p in build_zip.skill_files(SKILL)}
    with zipfile.ZipFile(zpath) as z:
        got = {n: z.read(n) for n in z.namelist()}
    assert f"{SKILL.name}/SKILL.md" in got
    assert sorted(got) == sorted(want), "ZIP entries differ: run python3 chat-skills/build_zip.py"
    stale = [n for n in want if got[n] != want[n]]
    assert not stale, f"stale in the ZIP: {stale}; run python3 chat-skills/build_zip.py"
