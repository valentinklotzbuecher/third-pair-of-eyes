"""recompute.py -- helpers for the document check's arithmetic.

A port of the stats-review suite's assets/recompute.R (third-pair-of-eyes) to the Python
standard library, so the checks run in a chat's code sandbox without R or extra
packages. Import it from a check script:

    import sys
    sys.path.insert(0, "<folder of this skill>/scripts")
    from recompute import *

Every function returns plain numbers, tuples or dicts, to print and to enter in the
check log. Tested against recompute.R in third-pair-of-eyes/chat-skills/tests.
"""
import math
import re
from statistics import NormalDist

__all__ = [
    "qnorm", "pnorm", "pt", "qt",
    "number_token", "parse_printed", "printed_decimals", "round_half_up",
    "agree", "agree_band", "agree_interval",
    "pct", "check_pct", "check_sum", "grim_ok",
    "se_from_ci", "p_from_ci", "ci_from_p", "ci_asymmetry",
    "wilson_ci", "rd_ci", "rr_ci", "or_ci",
    "inflate_dropout", "round_up_to", "n_two_means", "n_two_props",
    "events_schoenfeld", "hazard_from_surv", "event_prob", "design_effect", "mcse_prop",
]

# ---- Distributions ----------------------------------------------------------------

_NORMAL = NormalDist()


def qnorm(p):
    return _NORMAL.inv_cdf(p)


def pnorm(x):
    return _NORMAL.cdf(x)


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 500):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)),
                   -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + aa / c
            c = c if abs(c) > tiny else tiny
            delta = d * c
            h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def _ibeta(a, b, x):
    """Regularised incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                     + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def pt(t, df):
    """Distribution function of Student's t with df degrees of freedom (df > 0)."""
    tail = 0.5 * _ibeta(df / 2.0, 0.5, df / (df + t * t))
    return 1.0 - tail if t > 0 else tail


def qt(p, df):
    """Quantile of Student's t, by bisection on pt()."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must lie in (0, 1)")
    lo, hi = -1.0, 1.0
    while pt(lo, df) > p:
        lo *= 2.0
    while pt(hi, df) < p:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if pt(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo <= 1e-14 * max(1.0, abs(mid)):
            break
    return 0.5 * (lo + hi)

# ---- Agreement with a printed value -----------------------------------------------


def number_token(printed):
    """The first number in a printed string, as text: handles "12.30%", "−0.20"
    (Unicode minus), "1,234", "0.57 (95% CI ...)", "12 weeks"."""
    s = str(printed).replace("−", "-")
    s = re.sub(r"(?<=[0-9]),(?=[0-9]{3})", "", s)
    m = re.search(r"-?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", s)
    return m.group(0) if m else None


def parse_printed(printed):
    s = number_token(printed)
    return None if s is None else float(s)


def printed_decimals(printed):
    """Number of decimals in a printed number given as text ("12.30" -> 2, "84" -> 0)."""
    s = number_token(printed)
    if s is None or "." not in s:
        return 0
    return len(re.sub(r"[eE].*$", "", s.split(".", 1)[1]))


def round_half_up(x, digits=0):
    """Round half away from zero (SAS, Excel), as opposed to round half to even."""
    m = 10.0 ** digits
    return math.copysign(math.floor(abs(x) * m + 0.5 + 1e-9) / m, x)


def _all_equal(target, current, tolerance=1.5e-8):
    """R's all.equal() for two numbers: relative difference unless |target| is tiny."""
    diff = abs(target - current)
    scale = abs(target)
    return (diff / scale if scale > tolerance else diff) <= tolerance


def agree(printed, computed, tol=1e-9):
    """Compare a printed value (text, so its decimals are known) with a computed one:
    "match" within tolerance; "rounding" when equal after rounding the computed value
    to the printed precision (either rounding rule); "mismatch" otherwise."""
    if isinstance(printed, (list, tuple)) or isinstance(computed, (list, tuple)):
        raise TypeError("agree() compares one printed value with one computed value")
    p = parse_printed(printed)
    if p is None or computed is None or math.isnan(computed):
        return None
    if abs(p - computed) <= tol * max(1.0, abs(p)):
        return "match"
    d = printed_decimals(printed)
    if _all_equal(p, round(computed, d)) or _all_equal(p, round_half_up(computed, d)):
        return "rounding"
    return "mismatch"


def agree_band(printed, computed, band):
    """As agree(), else "within-band" when |printed - computed| <= band (Monte Carlo
    error, the precision of a figure read). Record the band in `tolerance`."""
    a = agree(printed, computed)
    if a is None or a != "mismatch":
        return a
    return "within-band" if abs(parse_printed(printed) - computed) <= band else "mismatch"


def agree_interval(printed, lo, hi):
    """Is a printed value inside the interval its rounded inputs allow? `lo` and `hi`
    are the smallest and largest values the quantity can take given the printed
    precision of its inputs."""
    p = parse_printed(printed)
    if p is None:
        return None
    half = 0.5 * 10.0 ** (-printed_decimals(printed))
    inside = p + half >= min(lo, hi) - 1e-12 and p - half <= max(lo, hi) + 1e-12
    return "within-band" if inside else "mismatch"

# ---- Counts, percentages, totals --------------------------------------------------


def pct(n, N):
    return 100.0 * n / N


def check_pct(printed, n, N):
    """Does a printed percentage match n / N at its printed precision?"""
    return agree(printed, pct(n, N))


def check_sum(parts, total):
    """Do the parts add up to the printed total?"""
    s = sum(parts)
    return {"sum": s, "total": total, "result": "match" if _all_equal(s, total) else "mismatch"}


def grim_ok(mean, n, items=1, digits=None):
    """GRIM: is a reported mean of integer data attainable with n records of `items`
    items? Pass the mean as printed text so its decimals are known ("2.47")."""
    if digits is None:
        digits = printed_decimals(mean)
    m = parse_printed(mean)
    grain = n * items
    centre = round(m * grain)
    for k in range(centre - 2, centre + 3):
        if (abs(round(k / grain, digits) - m) < 1e-9
                or abs(round_half_up(k / grain, digits) - m) < 1e-9):
            return True
    return False

# ---- Intervals and p-values -------------------------------------------------------


def se_from_ci(lo, hi, ratio=False, level=0.95):
    """Standard error implied by a symmetric interval (on the log scale for ratios)."""
    z = qnorm(1 - (1 - level) / 2)
    return (math.log(hi) - math.log(lo)) / (2 * z) if ratio else (hi - lo) / (2 * z)


def p_from_ci(est, lo, hi, ratio=False, level=0.95):
    """Two-sided p-value from an estimate and its interval (Altman and Bland 2011),
    with the exact normal tail."""
    se = se_from_ci(lo, hi, ratio, level)
    z = (math.log(est) if ratio else est) / se
    return 2 * pnorm(-abs(z))


def ci_from_p(est, p, ratio=False, level=0.95):
    """Interval from an estimate and its two-sided p-value (Altman and Bland 2011)."""
    z = qnorm(1 - p / 2)
    zc = qnorm(1 - (1 - level) / 2)
    if ratio:
        se = abs(math.log(est)) / z
        return (math.exp(math.log(est) - zc * se), math.exp(math.log(est) + zc * se))
    se = abs(est) / z
    return (est - zc * se, est + zc * se)


def ci_asymmetry(est, lo, hi, ratio=False):
    """Relative asymmetry of an estimate within its interval (0 = symmetric)."""
    if ratio:
        est, lo, hi = math.log(est), math.log(lo), math.log(hi)
    return ((hi - est) - (est - lo)) / (hi - lo)


def wilson_ci(x, n, level=0.95):
    """Wilson score interval for one proportion."""
    z = qnorm(1 - (1 - level) / 2)
    p = x / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (centre - half, centre + half)


def rd_ci(x1, n1, x2, n2, method="newcombe", level=0.95):
    """Risk difference p1 - p2 with a Newcombe hybrid score interval (method 10, 1998)
    or a Wald interval."""
    p1, p2 = x1 / n1, x2 / n2
    d = p1 - p2
    if method == "wald":
        z = qnorm(1 - (1 - level) / 2)
        se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        return {"est": d, "lo": d - z * se, "hi": d + z * se}
    if method != "newcombe":
        raise ValueError("method is 'newcombe' or 'wald'")
    l1, u1 = wilson_ci(x1, n1, level)
    l2, u2 = wilson_ci(x2, n2, level)
    return {"est": d,
            "lo": d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2),
            "hi": d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)}


def rr_ci(x1, n1, x2, n2, level=0.95):
    """Risk ratio with a Wald interval on the log scale."""
    z = qnorm(1 - (1 - level) / 2)
    rr = (x1 / n1) / (x2 / n2)
    se = math.sqrt(1 / x1 - 1 / n1 + 1 / x2 - 1 / n2)
    return {"est": rr, "lo": math.exp(math.log(rr) - z * se), "hi": math.exp(math.log(rr) + z * se)}


def or_ci(x1, n1, x2, n2, level=0.95):
    """Odds ratio with a Wald interval on the log scale."""
    z = qnorm(1 - (1 - level) / 2)
    a, b, c, d = x1, n1 - x1, x2, n2 - x2
    odds = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return {"est": odds, "lo": math.exp(math.log(odds) - z * se),
            "hi": math.exp(math.log(odds) + z * se)}

# ---- Sample size building blocks -------------------------------------------------


def inflate_dropout(n, d, method="divide"):
    """Randomised N from evaluable N and the share d without an evaluable endpoint.
    "divide" (N / (1 - d)) is the usual convention; "multiply" (N * (1 + d))
    under-inflates and is given only to reproduce a product that used it."""
    if method == "divide":
        return n / (1 - d)
    if method == "multiply":
        return n * (1 + d)
    raise ValueError("method is 'divide' or 'multiply'")


def round_up_to(n, multiple):
    return math.ceil(n / multiple) * multiple


def n_two_means(delta, sd, alpha=0.05, power=0.8, k=1, sided=2):
    """Per-arm N for a difference in means, normal approximation with a t correction
    (one iteration), allocation ratio k = n2 / n1."""
    za, zb = qnorm(1 - alpha / sided), qnorm(power)
    n1 = (1 + 1 / k) * sd ** 2 * (za + zb) ** 2 / delta ** 2
    df = n1 * (1 + k) - 2
    ta, tb = qt(1 - alpha / sided, df), qt(power, df)
    n1 = (1 + 1 / k) * sd ** 2 * (ta + tb) ** 2 / delta ** 2
    return {"n1": n1, "n2": k * n1}


def n_two_props(p1, p2, alpha=0.05, power=0.8, k=1, sided=2, correct=False):
    """Per-arm N for two proportions (Fleiss), optionally with a continuity correction."""
    za, zb = qnorm(1 - alpha / sided), qnorm(power)
    pbar = (p1 + k * p2) / (1 + k)
    d = abs(p1 - p2)
    n1 = (za * math.sqrt(pbar * (1 - pbar) * (1 + 1 / k))
          + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / k)) ** 2 / d ** 2
    if correct:
        n1 = n1 / 4 * (1 + math.sqrt(1 + 2 * (1 + 1 / k) / (n1 * d))) ** 2
    return {"n1": n1, "n2": k * n1}


def events_schoenfeld(hr, alpha=0.05, power=0.8, alloc=0.5, sided=2):
    """Required number of events for a log-rank or Cox comparison (Schoenfeld 1983);
    `alloc` is the proportion allocated to one arm."""
    za, zb = qnorm(1 - alpha / sided), qnorm(power)
    return (za + zb) ** 2 / (alloc * (1 - alloc) * math.log(hr) ** 2)


def hazard_from_surv(S, t):
    """Exponential hazard from a survival proportion S at time t."""
    return -math.log(S) / t


def event_prob(hazard, t):
    """Event probability over a follow-up window, given an exponential hazard."""
    return 1 - math.exp(-hazard * t)


def design_effect(m, icc, cv=0.0):
    """Design effect for cluster sizes with mean m and coefficient of variation cv."""
    return 1 + ((cv ** 2 + 1) * m - 1) * icc


def mcse_prop(p, R):
    """Monte Carlo standard error of a proportion estimated from R replicates."""
    return math.sqrt(p * (1 - p) / R)
