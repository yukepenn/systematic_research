"""champion_eval.py - the risk VECTOR every GENESIS III candidate is judged on.

WHY THIS MODULE EXISTS
----------------------
Two measured failures in this repository make a shared evaluator mandatory rather than nice to have.

1. FIXED-DRAWDOWN MATCHING IS CONTAMINATED AS A SOLE YARDSTICK.
   T2 measured that STATE-BLIND RANDOM DELETION of trades raises drawdown-matched income by
   +$129-139/week - about the same magnitude as most candidate "improvements". Money-at-a-common-
   maxDD rewards path smoothing, and thinning smooths paths for free. A rule that wins only on
   fixed-DD has demonstrated nothing.

2. NINE OR TEN EXPOSURE-REDUCING RULES IN A ROW LOOKED GOOD AND WERE WORTHLESS.
   Every one of them removed trades. None beat its own random-thinning control.

So this module enforces two things by construction:

  * `risk_vector()` returns RETURN, VOLATILITY, TAIL, CAPITAL, RELIABILITY together. Fixed-DD is
    one field among many and is never returned alone.
  * `thinning_placebo()` exists, and `champion_report()` REFUSES to emit a verdict for any
    candidate that reduces exposure unless the placebo was run. Not a convention - a hard error.

WHAT THIS MODULE DELIBERATELY DOES NOT DO
-----------------------------------------
It does not decide promotion. It computes comparable numbers. A promotion still requires a
preregistered spec, a coded falsifier, and a locked challenge. Nothing here shortcuts that.

It also does not compute a p-value on the level of a strategy's returns. Weekly P&L in this book is
extremely concentrated (P1's top decile of trades exceeds 100% of net), so the only inference used
here is a DEPENDENCE-PRESERVING stationary bootstrap on the weekly DIFFERENCE series. A t-statistic
is printed beside it as a diagnostic and is never the test.

CONVENTIONS (repo-standard, asserted not assumed)
-------------------------------------------------
  session date  ->  ISO week, via date.isocalendar()[:2]
  point value   ->  $20/NQ point;  commission $4.36 per contract round turn
  drawdown      ->  on the WEEKLY cumulative series, in dollars, peak-to-trough
  ES95          ->  mean of the worst 5% of weeks (a tail AVERAGE, not a quantile)

Usage:
    python -m research_sdk.champion_eval --selftest
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, datetime

import numpy as np

PV = 20.0
COMM_RT = 4.36


# ==================================================================================================
# Trade ledger -> weekly series
# ==================================================================================================

def iso_week(d) -> str:
    if isinstance(d, str):
        d = datetime.fromisoformat(d[:19]).date() if len(d) > 10 else date.fromisoformat(d)
    elif isinstance(d, datetime):
        d = d.date()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def weekly_from_trades(dates, pnl, all_weeks=None):
    """Aggregate a trade ledger to a weekly $ series.

    all_weeks: if given, the full week index to reindex onto, so that a candidate which simply does
    not trade in a week contributes 0 rather than silently shortening the series. Comparing two
    strategies on different week indices is a real error and this parameter is how it is avoided.
    """
    pnl = np.asarray(pnl, dtype=float)
    wk = np.array([iso_week(d) for d in dates])
    if all_weeks is None:
        all_weeks = sorted(set(wk))
    idx = {w: i for i, w in enumerate(all_weeks)}
    out = np.zeros(len(all_weeks))
    for w, p in zip(wk, pnl):
        j = idx.get(w)
        if j is not None:
            out[j] += p
    return np.array(all_weeks), out


# ==================================================================================================
# Primitives
# ==================================================================================================

def max_drawdown(weekly: np.ndarray) -> tuple[float, int]:
    """(maxDD in dollars as a POSITIVE number, duration in weeks) on the cumulative series."""
    c = np.cumsum(weekly)
    peak = np.maximum.accumulate(c)
    dd = peak - c
    i = int(np.argmax(dd)) if len(dd) else 0
    mdd = float(dd[i]) if len(dd) else 0.0
    # duration: length of the longest stretch spent below a running peak
    below = dd > 1e-12
    best = cur = 0
    for b in below:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return mdd, int(best)


def expected_shortfall(weekly: np.ndarray, alpha: float = 0.95) -> float:
    """Mean of the worst (1-alpha) fraction of weeks. Returned as a NEGATIVE number when losing."""
    n = len(weekly)
    if n == 0:
        return 0.0
    # The epsilon is NOT cosmetic. 1.0 - 0.95 == 0.050000000000000044 in IEEE754, so
    # ceil(100 * (1.0 - 0.95)) == 6, not 5 - every ES95 would silently average one extra week.
    # Caught by the hand-computed self-test on np.arange(100.).
    k = max(1, int(math.ceil(n * (1.0 - alpha) - 1e-9)))
    return float(np.mean(np.sort(weekly)[:k]))


def downside_sd(weekly: np.ndarray, mar: float = 0.0) -> float:
    d = weekly[weekly < mar] - mar
    return float(np.sqrt(np.mean(d ** 2))) if len(d) else 0.0


def fixed_dd_income(weekly: np.ndarray, target_dd: float) -> float:
    """Weekly $ after linearly rescaling the series so its own maxDD equals target_dd.

    This is scale-invariant ALGEBRA on an existing series, not leverage applied to a strategy: it
    answers "at a common risk budget, who earns more". It cannot manufacture edge, but it also
    cannot be read as a deployable size - see the module docstring's warning about thinning.
    """
    mdd, _ = max_drawdown(weekly)
    if mdd <= 0:
        return float("inf") if weekly.sum() > 0 else 0.0
    return float(np.mean(weekly) * (target_dd / mdd))


def stationary_bootstrap(x: np.ndarray, n_draws: int, mean_block: float, rng) -> np.ndarray:
    """Politis-Romano stationary bootstrap of the MEAN of x. Preserves serial dependence.

    Independent weekly resampling is WRONG for this book and is not offered as an option.
    """
    n = len(x)
    if n == 0:
        return np.zeros(n_draws)
    p = 1.0 / max(mean_block, 1.0)
    out = np.empty(n_draws)
    for b in range(n_draws):
        idx = np.empty(n, dtype=np.int64)
        i = rng.integers(0, n)
        for t in range(n):
            idx[t] = i
            if rng.random() < p:
                i = rng.integers(0, n)
            else:
                i = (i + 1) % n
        out[b] = x[idx].mean()
    return out


def top_k_share(trade_pnl: np.ndarray, frac: float) -> float:
    """Share of NET carried by the top `frac` of trades by P&L. Can exceed 1.0 - that is the point."""
    if len(trade_pnl) == 0:
        return float("nan")
    net = trade_pnl.sum()
    k = max(1, int(round(len(trade_pnl) * frac)))
    top = np.sort(trade_pnl)[-k:].sum()
    return float(top / net) if net != 0 else float("nan")


# ==================================================================================================
# The risk vector
# ==================================================================================================

@dataclass
class RiskVector:
    name: str
    n_weeks: int = 0
    n_trades: int = 0
    contract_round_turns: float = 0.0
    # RETURN
    net_total: float = 0.0
    net_per_week: float = 0.0
    median_per_week: float = 0.0
    pct_positive_weeks: float = 0.0
    # VOLATILITY
    weekly_sd: float = 0.0
    downside_sd: float = 0.0
    # TAIL
    es95: float = 0.0
    worst_week: float = 0.0
    worst_5_sessions: float = 0.0
    max_dd: float = 0.0
    dd_duration_weeks: int = 0
    # CAPITAL
    peak_contracts: int = 0
    capital_proxy: float = 0.0
    # RELIABILITY
    fixed_dd_income: float = 0.0
    top_1pct_share: float = float("nan")
    top_10pct_share: float = float("nan")
    by_year: dict = field(default_factory=dict)
    loyo: dict = field(default_factory=dict)
    # provenance
    exposure_reducing: bool = False
    placebo_ran: bool = False

    def as_dict(self):
        return asdict(self)


def risk_vector(name, dates, pnl, qty=None, all_weeks=None, target_dd: float = 20245.0,
                session_pnl=None) -> RiskVector:
    pnl = np.asarray(pnl, dtype=float)
    qty = np.ones(len(pnl)) if qty is None else np.asarray(qty, dtype=float)
    weeks, w = weekly_from_trades(dates, pnl, all_weeks)

    rv = RiskVector(name=name)
    rv.n_weeks, rv.n_trades = len(w), len(pnl)
    rv.contract_round_turns = float(qty.sum())

    rv.net_total = float(pnl.sum())
    rv.net_per_week = float(np.mean(w)) if len(w) else 0.0
    rv.median_per_week = float(np.median(w)) if len(w) else 0.0
    rv.pct_positive_weeks = float(np.mean(w > 0)) if len(w) else 0.0

    rv.weekly_sd = float(np.std(w, ddof=1)) if len(w) > 1 else 0.0
    rv.downside_sd = downside_sd(w)

    rv.es95 = expected_shortfall(w, 0.95)
    rv.worst_week = float(np.min(w)) if len(w) else 0.0
    rv.max_dd, rv.dd_duration_weeks = max_drawdown(w)

    if session_pnl is not None and len(session_pnl):
        rv.worst_5_sessions = float(np.sort(np.asarray(session_pnl, float))[:5].sum())

    rv.peak_contracts = int(qty.max()) if len(qty) else 0
    # Deliberately crude and deliberately NAMED: peak contracts x an NQ overnight-margin order of
    # magnitude, plus the observed maxDD. This is a comparability proxy, not a margin calculation.
    rv.capital_proxy = rv.peak_contracts * 25000.0 + rv.max_dd

    rv.fixed_dd_income = fixed_dd_income(w, target_dd)
    rv.top_1pct_share = top_k_share(pnl, 0.01)
    rv.top_10pct_share = top_k_share(pnl, 0.10)

    yrs = np.array([int(str(w_)[:4]) for w_ in weeks])
    for y in sorted(set(yrs.tolist())):
        m = yrs == y
        rv.by_year[int(y)] = dict(weeks=int(m.sum()), net=float(w[m].sum()),
                                  per_week=float(w[m].mean()) if m.sum() else 0.0)
    for y in sorted(set(yrs.tolist())):
        m = yrs != y
        rv.loyo[int(y)] = float(np.mean(w[m])) if m.sum() else 0.0
    return rv


# ==================================================================================================
# §26 - the mandatory random-thinning placebo
# ==================================================================================================

def thinning_placebo(dates, pnl, qty, keep_frac: float, n_draws: int = 1000,
                     all_weeks=None, target_dd: float = 20245.0, seed: int = 20260831,
                     match: str = "count") -> dict:
    """STATE-BLIND random reduction matched to a candidate's exposure reduction.

    `match`:
      "count"    - keep the same NUMBER of trades the candidate keeps
      "exposure" - keep trades until the same TOTAL CONTRACT count is reached

    The comparison that matters is not "did the filter make money" but "did it beat a coin flip that
    removed the same amount of exposure". If the placebo's 95th percentile exceeds the candidate,
    the candidate has demonstrated no information value, whatever its raw P&L says.
    """
    rng = np.random.default_rng(seed)
    pnl = np.asarray(pnl, float)
    qty = np.asarray(qty, float)
    n = len(pnl)
    if all_weeks is None:
        all_weeks = sorted({iso_week(d) for d in dates})

    fixdd, netwk = np.empty(n_draws), np.empty(n_draws)
    if match == "count":
        k = max(1, int(round(n * keep_frac)))
    for b in range(n_draws):
        if match == "count":
            sel = rng.choice(n, size=k, replace=False)
        else:
            order = rng.permutation(n)
            target = qty.sum() * keep_frac
            cum = np.cumsum(qty[order])
            take = int(np.searchsorted(cum, target) + 1)
            sel = order[:take]
        d = [dates[i] for i in sel]
        _, w = weekly_from_trades(d, pnl[sel], all_weeks)
        fixdd[b] = fixed_dd_income(w, target_dd)
        netwk[b] = float(np.mean(w))
    fixdd = fixdd[np.isfinite(fixdd)]
    return dict(
        n_draws=int(n_draws), keep_frac=float(keep_frac), match=match,
        fixdd_mean=float(np.mean(fixdd)), fixdd_p50=float(np.percentile(fixdd, 50)),
        fixdd_p95=float(np.percentile(fixdd, 95)), fixdd_p99=float(np.percentile(fixdd, 99)),
        netwk_mean=float(np.mean(netwk)), netwk_p95=float(np.percentile(netwk, 95)),
    )


# ==================================================================================================
# §35 / §44 - the incumbent comparison
# ==================================================================================================

def incremental(base_weekly: np.ndarray, cand_weekly: np.ndarray, n_draws: int = 10000,
                mean_block: float = 4.0, seed: int = 20260831) -> dict:
    """Candidate vs incumbent, matched three ways so leverage cannot masquerade as diversification.

    Matched-vol / matched-ES / matched-capital all SCALE THE INCUMBENT UP to the combined book's
    risk. If `base + candidate` cannot beat `k x base` at the same risk, the candidate has added
    nothing that more of the incumbent would not have added more cheaply.
    """
    rng = np.random.default_rng(seed)
    b, c = np.asarray(base_weekly, float), np.asarray(cand_weekly, float)
    if len(b) != len(c):
        raise ValueError(f"week index mismatch: base {len(b)} vs candidate {len(c)} - "
                         "reindex both onto the same all_weeks before calling")
    comb = b + c

    def sd(x): return float(np.std(x, ddof=1)) if len(x) > 1 else 0.0

    out = dict(
        base_per_week=float(np.mean(b)), cand_per_week=float(np.mean(c)),
        combined_per_week=float(np.mean(comb)),
        correlation=float(np.corrcoef(b, c)[0, 1]) if sd(b) > 0 and sd(c) > 0 else float("nan"),
        base_sd=sd(b), cand_sd=sd(c), combined_sd=sd(comb),
        base_es95=expected_shortfall(b), combined_es95=expected_shortfall(comb),
        base_maxdd=max_drawdown(b)[0], combined_maxdd=max_drawdown(comb)[0],
    )

    # --- risk-matched incumbent: scale the BASE to the COMBINED book's risk, three ways ---------
    for label, num, den in (("vol", out["combined_sd"], out["base_sd"]),
                            ("es", out["combined_es95"], out["base_es95"]),
                            ("dd", out["combined_maxdd"], out["base_maxdd"])):
        k = (num / den) if den not in (0.0,) and np.isfinite(den) else float("nan")
        out[f"scaled_base_k_{label}"] = float(k)
        out[f"scaled_base_per_week_{label}"] = float(np.mean(b) * k) if np.isfinite(k) else float("nan")
        out[f"increment_vs_scaled_{label}"] = (float(np.mean(comb) - np.mean(b) * k)
                                               if np.isfinite(k) else float("nan"))

    # --- worst-incumbent-state contribution -----------------------------------------------------
    k = max(1, int(math.ceil(len(b) * 0.10)))
    worst = np.argsort(b)[:k]
    out["base_worst_decile_per_week"] = float(np.mean(b[worst]))
    out["cand_in_base_worst_decile"] = float(np.mean(c[worst]))

    # --- dependence-preserving inference on the DIFFERENCE, not on the level --------------------
    diff = comb - b
    boot = stationary_bootstrap(diff, n_draws, mean_block, rng)
    out["diff_mean"] = float(np.mean(diff))
    out["diff_ci90"] = [float(np.percentile(boot, 5)), float(np.percentile(boot, 95))]
    out["diff_ci90_excludes_zero"] = bool(out["diff_ci90"][0] > 0 or out["diff_ci90"][1] < 0)
    sdd = float(np.std(diff, ddof=1)) if len(diff) > 1 else 0.0
    out["diff_t_DIAGNOSTIC_ONLY"] = (float(np.mean(diff) / (sdd / math.sqrt(len(diff))))
                                     if sdd > 0 else float("nan"))
    return out


# ==================================================================================================
# The report - refuses to bless an exposure-reducing candidate with no placebo
# ==================================================================================================

class PlaceboRequired(RuntimeError):
    pass


def champion_report(base: RiskVector, cand: RiskVector, inc: dict,
                    placebo: dict | None = None) -> str:
    if cand.exposure_reducing and placebo is None:
        raise PlaceboRequired(
            f"candidate '{cand.name}' reduces exposure "
            f"({cand.n_trades} trades / {cand.contract_round_turns:.0f} ctrRT vs base "
            f"{base.n_trades} / {base.contract_round_turns:.0f}) but no random-thinning placebo was "
            "supplied. GENESIS III section 26 makes it mandatory: nine prior exposure-reducing "
            "rules looked good and none beat its own state-blind control. Run thinning_placebo() "
            "and pass it in."
        )
    L = []
    A = L.append
    A(f"{'metric':<34}{base.name:>16}{cand.name:>16}")
    A("-" * 66)
    for lab, a, b in (
        ("net / week", base.net_per_week, cand.net_per_week),
        ("median / week", base.median_per_week, cand.median_per_week),
        ("% positive weeks", base.pct_positive_weeks, cand.pct_positive_weeks),
        ("weekly SD", base.weekly_sd, cand.weekly_sd),
        ("downside SD", base.downside_sd, cand.downside_sd),
        ("ES95 (worst 5% mean)", base.es95, cand.es95),
        ("worst week", base.worst_week, cand.worst_week),
        ("max drawdown", base.max_dd, cand.max_dd),
        ("DD duration (weeks)", base.dd_duration_weeks, cand.dd_duration_weeks),
        ("capital proxy", base.capital_proxy, cand.capital_proxy),
        ("fixed-DD income / wk", base.fixed_dd_income, cand.fixed_dd_income),
        ("top 1% share of net", base.top_1pct_share, cand.top_1pct_share),
        ("top 10% share of net", base.top_10pct_share, cand.top_10pct_share),
        ("trades", base.n_trades, cand.n_trades),
        ("contract round turns", base.contract_round_turns, cand.contract_round_turns),
    ):
        A(f"{lab:<34}{a:>16,.4g}{b:>16,.4g}")
    A("")
    A(f"correlation with incumbent      {inc['correlation']:>10.4f}")
    A(f"combined net/week               {inc['combined_per_week']:>10,.2f}"
      f"   (base {inc['base_per_week']:,.2f})")
    for lab in ("vol", "es", "dd"):
        A(f"increment vs risk-matched base [{lab:>3}]  {inc[f'increment_vs_scaled_{lab}']:>10,.2f}"
          f"   (k = {inc[f'scaled_base_k_{lab}']:.4f})")
    A(f"candidate in incumbent's worst decile   {inc['cand_in_base_worst_decile']:>10,.2f}"
      f"   (incumbent there {inc['base_worst_decile_per_week']:,.2f})")
    A(f"diff mean {inc['diff_mean']:,.2f}   bootstrap 90% CI "
      f"[{inc['diff_ci90'][0]:,.2f}, {inc['diff_ci90'][1]:,.2f}]"
      f"   excludes 0: {inc['diff_ci90_excludes_zero']}")
    A(f"  (t = {inc['diff_t_DIAGNOSTIC_ONLY']:.3f} - DIAGNOSTIC ONLY, not the test)")
    if placebo is not None:
        A("")
        A(f"RANDOM-THINNING PLACEBO  match={placebo['match']}  keep={placebo['keep_frac']:.3f}  "
          f"draws={placebo['n_draws']}")
        A(f"  placebo fixed-DD/wk  mean {placebo['fixdd_mean']:,.2f}   "
          f"p95 {placebo['fixdd_p95']:,.2f}   p99 {placebo['fixdd_p99']:,.2f}")
        A(f"  candidate fixed-DD/wk     {cand.fixed_dd_income:,.2f}")
        beat = cand.fixed_dd_income > placebo["fixdd_p95"]
        A(f"  CANDIDATE BEATS ITS OWN STATE-BLIND CONTROL: {'YES' if beat else 'NO'}"
          + ("" if beat else "  <- no demonstrated information value"))
    return "\n".join(L)


# ==================================================================================================
# Self-test - synthetic cases with answers known in advance
# ==================================================================================================

def selftest() -> int:
    checks = []

    def chk(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    rng = np.random.default_rng(7)

    # --- primitives against hand-computable answers ------------------------------------------
    w = np.array([10.0, -5.0, -5.0, 20.0])          # cum 10,5,0,20 ; peak 10 ; maxDD 10
    mdd, dur = max_drawdown(w)
    chk("maxDD hand-check", abs(mdd - 10.0) < 1e-9, f"got {mdd}")
    chk("DD duration hand-check", dur == 2, f"got {dur}")
    chk("maxDD of a monotone series is 0", max_drawdown(np.array([1.0, 2, 3]))[0] == 0.0)

    x = np.arange(100.0)
    chk("ES95 = mean of worst 5", abs(expected_shortfall(x, 0.95) - np.mean([0, 1, 2, 3, 4])) < 1e-9)
    chk("downside SD ignores gains", abs(downside_sd(np.array([5.0, -3.0])) - 3.0) < 1e-9)

    # fixed-DD is pure rescaling: doubling every week must leave fixed-DD income UNCHANGED
    a = rng.normal(100, 500, 200)
    chk("fixed-DD is scale invariant",
        abs(fixed_dd_income(a, 20245.0) - fixed_dd_income(2 * a, 20245.0)) < 1e-6)

    p = np.array([100.0] * 90 + [1000.0] * 10)      # top 10% = 10000 of net 19000
    chk("top-10% share", abs(top_k_share(p, 0.10) - 10000 / 19000) < 1e-9)
    p2 = np.array([-100.0] * 95 + [1000.0] * 5)     # net -4500; top 5% = 5000 -> share < 0
    chk("top-k share may exceed 1 or go negative", top_k_share(p2, 0.05) < 0)

    # --- iso week -----------------------------------------------------------------------------
    chk("iso_week str", iso_week("2022-01-03") == "2022-W01", iso_week("2022-01-03"))
    chk("iso_week datetime", iso_week(datetime(2022, 1, 2, 12)) == "2021-W52",
        iso_week(datetime(2022, 1, 2, 12)))

    # --- weekly reindexing: a candidate that skips weeks must NOT shorten the series ----------
    dts = ["2022-01-03", "2022-01-17"]
    aw = ["2022-W01", "2022-W02", "2022-W03"]
    _, ww = weekly_from_trades(dts, [10.0, 20.0], aw)
    chk("reindex fills gaps with 0", list(ww) == [10.0, 0.0, 20.0], str(ww))

    # --- bootstrap ----------------------------------------------------------------------------
    z = rng.normal(5.0, 1.0, 300)
    bs = stationary_bootstrap(z, 400, 4.0, np.random.default_rng(1))
    chk("bootstrap centres on the sample mean", abs(np.mean(bs) - z.mean()) < 0.25,
        f"{np.mean(bs):.3f} vs {z.mean():.3f}")
    chk("bootstrap has spread", np.std(bs) > 0)

    # --- incremental: a candidate identical to the base cannot beat a risk-matched base -------
    base_w = rng.normal(1500, 3000, 240)
    inc = incremental(base_w, base_w.copy(), n_draws=300)
    chk("clone correlation is 1", abs(inc["correlation"] - 1.0) < 1e-9)
    chk("clone k_vol == 2", abs(inc["scaled_base_k_vol"] - 2.0) < 1e-6,
        f"{inc['scaled_base_k_vol']}")
    chk("clone increment vs risk-matched base == 0",
        abs(inc["increment_vs_scaled_vol"]) < 1e-6, f"{inc['increment_vs_scaled_vol']}")
    chk("week-index mismatch raises",
        _raises(lambda: incremental(base_w, base_w[:-1])))

    # --- THE LOAD-BEARING GUARD ---------------------------------------------------------------
    dates = [f"2022-{1 + (i // 60):02d}-{1 + (i % 27):02d}" for i in range(300)]
    pnl = rng.normal(120, 900, 300)
    qty = np.ones(300)
    allw = sorted({iso_week(d) for d in dates})
    rv_base = risk_vector("BASE", dates, pnl, qty, allw)
    keep = np.sort(rng.choice(300, 200, replace=False))
    rv_cand = risk_vector("THIN", [dates[i] for i in keep], pnl[keep], qty[keep], allw)
    rv_cand.exposure_reducing = True
    _, bw = weekly_from_trades(dates, pnl, allw)
    _, cw = weekly_from_trades([dates[i] for i in keep], pnl[keep], allw)
    inc2 = incremental(bw, cw, n_draws=200)
    chk("exposure-reducing candidate without placebo RAISES",
        _raises(lambda: champion_report(rv_base, rv_cand, inc2)))
    pl = thinning_placebo(dates, pnl, qty, keep_frac=200 / 300, n_draws=60, all_weeks=allw)
    txt = champion_report(rv_base, rv_cand, inc2, pl)
    chk("with placebo it reports", "RANDOM-THINNING PLACEBO" in txt)
    chk("placebo p95 >= p50", pl["fixdd_p95"] >= pl["fixdd_p50"])
    # a RANDOM thinning must not systematically beat its own random control
    chk("random thinning does not beat its own control",
        rv_cand.fixed_dd_income <= pl["fixdd_p99"],
        f"cand {rv_cand.fixed_dd_income:.1f} vs p99 {pl['fixdd_p99']:.1f}")
    chk("non-reducing candidate needs no placebo",
        isinstance(champion_report(rv_base, risk_vector("X", dates, pnl, qty, allw), inc2), str))

    # --- risk vector never returns fixed-DD alone ---------------------------------------------
    d = rv_base.as_dict()
    for f_ in ("es95", "worst_week", "max_dd", "weekly_sd", "top_10pct_share",
               "capital_proxy", "by_year", "loyo"):
        chk(f"risk vector carries {f_}", f_ in d)

    width = max(len(c[0]) for c in checks)
    npass = sum(c[1] for c in checks)
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<{width}}  {detail}")
    print(f"\nselftest {npass}/{len(checks)}")
    return 0 if npass == len(checks) else 1


def _raises(fn) -> bool:
    try:
        fn()
        return False
    except Exception:
        return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
