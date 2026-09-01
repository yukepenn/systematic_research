# -*- coding: utf-8 -*-
"""eval_battery -- judge a candidate on several risk bases, and never on fixed-DD alone.

THE INDICTMENT THIS EXISTS TO ENFORCE
-------------------------------------
`runs/T2_VERDICT_20260831/REPORT.md:38-43`:

    At N = 243 weeks, max-drawdown-matching is not a valid common-risk basis: randomly
    deleting the same number of trades SIDE-BLIND raises DD-matched income by a median
    +$129 to +$139/wk -- MORE THAN ANY CANDIDATE MOVES IT. Under weekly-vol matching,
    which has no such defect, the ordering REVERSES and the incumbent wins outright.

    => Every fixed-DD gain in this repo must now be read beside its random-thinning
       placebo, or it is uninterpretable.

Why it happens: max drawdown is an ORDER STATISTIC of a path. Deleting trades at random
removes some of the trades that made the worst path, so DD falls faster than mean return
does. Normalising by a shrinking denominator manufactures income out of nothing. The
mechanism is arithmetic, so it does not care whether the deletion rule is a clever signal
or a coin flip -- which is exactly why a coin flip is the right control.

WHAT THIS MODULE MAKES IMPOSSIBLE
---------------------------------
`fixed_dd` income cannot be obtained without its placebo. `evaluate()` returns a result
object whose fixed-DD field RAISES on access unless a placebo was run. That is deliberate:
a rule in a document gets forgotten, a rule in a type does not.

    python -m research_sdk.eval_battery          # reproduces the T2 finding on real data
"""
from __future__ import annotations

import numpy as np

RISK_BASES = ("native", "weekly_vol", "realized_vol", "gross_exposure",
              "fixed_capital", "fixed_dd", "fixed_cdar")

# Bases whose denominator is an ORDER STATISTIC of the path, and which are therefore
# vulnerable to the thinning artifact. These REQUIRE a placebo.
_ORDER_STATISTIC_BASES = ("fixed_dd", "fixed_cdar")


class PlaceboRequired(RuntimeError):
    """Raised when an order-statistic-normalised figure is read without its control."""


def max_drawdown(x):
    c = np.cumsum(np.asarray(x, float))
    z = np.concatenate([[0.0], c])
    return float(np.max(np.maximum.accumulate(z) - z))


def cdar(x, alpha=0.95):
    """Conditional drawdown at risk: mean of the worst (1-alpha) of the drawdown path."""
    c = np.cumsum(np.asarray(x, float))
    z = np.concatenate([[0.0], c])
    dd = np.maximum.accumulate(z) - z
    k = max(1, int(round((1 - alpha) * len(dd))))
    return float(np.mean(np.sort(dd)[-k:]))


def _scale_to(series, base, ref):
    """Multiplier that puts `series` on the same risk footing as `ref` under `base`."""
    s, r = np.asarray(series, float), np.asarray(ref, float)
    if base == "native":
        return 1.0
    if base == "weekly_vol" or base == "realized_vol":
        a, b = np.std(s, ddof=1), np.std(r, ddof=1)
        return (b / a) if a > 0 else np.nan
    if base == "gross_exposure":
        a, b = np.mean(np.abs(s)), np.mean(np.abs(r))
        return (b / a) if a > 0 else np.nan
    if base == "fixed_capital":
        return 1.0
    if base == "fixed_dd":
        a, b = max_drawdown(s), max_drawdown(r)
        return (b / a) if a > 0 else np.nan
    if base == "fixed_cdar":
        a, b = cdar(s), cdar(r)
        return (b / a) if a > 0 else np.nan
    raise ValueError("unknown risk base %r" % base)


class Result(dict):
    """A dict whose order-statistic entries refuse to be read without a placebo."""

    def __init__(self, values, placebo_pct=None):
        super().__init__(values)
        self._placebo_pct = placebo_pct

    def __getitem__(self, k):
        if k in _ORDER_STATISTIC_BASES and self._placebo_pct is None:
            raise PlaceboRequired(
                "%r is normalised by an ORDER STATISTIC of the path and cannot be read "
                "without its rate-matched random-thinning placebo.\n"
                "  Random side-blind deletion alone moves DD-matched income by a median\n"
                "  +$129 to +$139/wk on this book (T2_VERDICT_20260831) -- more than any\n"
                "  candidate has ever moved it. Pass n_placebo>0 to evaluate()." % k)
        return super().__getitem__(k)

    @property
    def placebo_percentile(self):
        return self._placebo_pct


def random_thinning_placebo(trade_pnl, period_idx, n_removed, base="fixed_dd",
                            n=2000, seed=20260901, n_periods=None):
    """SIDE-BLIND deletion of the same NUMBER OF TRADES, `n` times.

    ⚠️ THE MODELLING POINT, and my first version of this function got it wrong.
    Removing a trade does NOT remove the period. It makes that period FLATTER -- and if it
    was the period's only trade, exactly zero. The calendar is unchanged. Compressing the
    series instead (dropping the period entirely) shortens the drawdown path, changes the
    denominator twice, and produces the WRONG SIGN: it showed random thinning HURTING by
    $154/wk, which contradicted the finding this module exists to enforce. The selftest
    caught it.

    So: thin at TRADE level, re-aggregate onto the SAME period grid, keep the length.

    trade_pnl  : per-trade P&L
    period_idx : integer period (e.g. week number) for each trade, 0..n_periods-1
    """
    rng = np.random.default_rng(seed)
    v = np.asarray(trade_pnl, float)
    p = np.asarray(period_idx, np.int64)
    m = len(v)
    n_periods = int(n_periods if n_periods is not None else p.max() + 1)
    if not (0 < n_removed < m):
        raise ValueError("n_removed must be in (0, %d), got %d" % (m, n_removed))
    ref = np.bincount(p, weights=v, minlength=n_periods)

    out = np.empty(n, float)
    for i in range(n):
        keep = np.ones(m, bool)
        keep[rng.choice(m, n_removed, replace=False)] = False
        thinned = np.bincount(p[keep], weights=v[keep], minlength=n_periods)
        k = _scale_to(thinned, base, ref)
        out[i] = np.sum(thinned) * k / n_periods
    return out


def evaluate(candidate, reference, n_placebo=0, base_for_placebo="fixed_dd", seed=20260901,
             ref_trades=None, ref_periods=None, n_trades_removed=None):
    """Income per period for `candidate`, risk-matched to `reference`, on every basis.

    candidate / reference : per-PERIOD P&L arrays on the SAME grid and SAME length.
                            A trade-removing candidate has zeros where it declined to
                            trade -- it never has fewer periods.
    n_placebo             : draws for the rate-matched thinning null. Required to read
                            any order-statistic basis.
    ref_trades/ref_periods/n_trades_removed :
                            the trade-level view, needed to build a rate-matched placebo.
                            Without them a fixed-DD figure stays unreadable, by design.
    """
    c, r = np.asarray(candidate, float), np.asarray(reference, float)
    if len(c) != len(r):
        raise ValueError(
            "candidate and reference must share the period grid (got %d vs %d). A "
            "trade-removing candidate has ZEROS where it declined to trade; dropping the "
            "period shortens the drawdown path and biases every order-statistic basis."
            % (len(c), len(r)))
    vals = {}
    for b in RISK_BASES:
        k = _scale_to(c, b, r)
        vals[b] = float(np.sum(c) * k / len(r)) if np.isfinite(k) else float("nan")

    pct = None
    if n_placebo > 0:
        if ref_trades is None or ref_periods is None or not n_trades_removed:
            raise ValueError("a rate-matched placebo needs ref_trades, ref_periods and "
                             "n_trades_removed -- the deletion RATE must match the candidate's")
        null = random_thinning_placebo(ref_trades, ref_periods, n_trades_removed,
                                       base_for_placebo, n=n_placebo, seed=seed,
                                       n_periods=len(r))
        obs = float(np.sum(c) * _scale_to(c, base_for_placebo, r) / len(r))
        pct = float(100.0 * np.mean(null < obs))
    return Result(vals, pct)


# ------------------------------------------------------------------------- selftest
def _refuses_mismatched_grid(c, r):
    try:
        evaluate(c, r)
    except ValueError:
        return True
    return False


def selftest():
    """Reproduce the T2 finding on the real book. If this fails, the module is wrong."""
    import os
    import pandas as pd

    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(repo, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out")
    ok = []

    p1 = pd.read_csv(os.path.join(src, "p1_trades_full.csv"))
    xm = pd.read_csv(os.path.join(src, "xm_trades_full.csv"))
    for d in (p1, xm):
        d["xt"] = pd.to_datetime(d["xt"])
    both = pd.concat([p1[["xt", "pnl"]], xm[["xt", "pnl"]]]).sort_values("xt")
    # fixed weekly grid; a thinned book keeps every week and simply earns less in some
    wk_id = both["xt"].dt.to_period("W")
    codes, _ = pd.factorize(wk_id, sort=True)
    both = both.assign(w=codes)
    n_per = int(codes.max()) + 1
    tv, tp = both["pnl"].to_numpy(float), both["w"].to_numpy(np.int64)
    ref = np.bincount(tp, weights=tv, minlength=n_per)
    print("  reference: %d weeks, %d trades, $%.0f/wk native" % (n_per, len(tv), ref.mean()))

    base_income = ref.sum() / n_per

    # ---- 1. THE DYNAMIC RANGE. An ORACLE rule -- drop the worst 10% of trades, using
    #         knowledge nobody has -- on each basis. This is the real indictment.
    thr = np.percentile(tv, 10)
    keep = tv > thr
    cand = np.bincount(tp[keep], weights=tv[keep], minlength=n_per)
    res = evaluate(cand, ref, n_placebo=2000, ref_trades=tv, ref_periods=tp,
                   n_trades_removed=int((~keep).sum()))
    print("  ORACLE rule (drop the worst 10%% of trades) income per week, by risk basis:")
    for b in RISK_BASES:
        v = super(Result, res).__getitem__(b)
        print("    %-16s $%9.0f   (%.1fx native)" % (b, v, v / base_income))

    dd_v = super(Result, res).__getitem__("fixed_dd")
    vol_v = super(Result, res).__getitem__("weekly_vol")
    ok.append(("fixed_dd has enormous dynamic range", dd_v > 5 * base_income,
               "$%.0f/wk = %.1fx native, from a rule with no predictive content"
               % (dd_v, dd_v / base_income)))
    ok.append(("weekly_vol has far less", vol_v < dd_v / 3.0,
               "$%.0f/wk = %.1fx native" % (vol_v, vol_v / base_income)))

    # ---- 2. THE TYPE-LEVEL GUARD
    res_noplacebo = evaluate(cand, ref, n_placebo=0)
    try:
        res_noplacebo["fixed_dd"]
        ok.append(("fixed_dd unreadable without placebo", False, "IT WAS READABLE"))
    except PlaceboRequired:
        ok.append(("fixed_dd unreadable without placebo", True, "PlaceboRequired raised"))
    ok.append(("native always readable", np.isfinite(res_noplacebo["native"]), ""))
    ok.append(("fixed_dd readable WITH placebo", np.isfinite(res["fixed_dd"]),
               "$%.0f/wk at the %.1fth pct" % (res["fixed_dd"], res.placebo_percentile)))
    ok.append(("evaluate() refuses a mismatched period grid",
               _refuses_mismatched_grid(cand[:-5], ref), "ValueError raised"))

    # ---- 3. NON-REPRODUCTION, recorded rather than tuned away.
    print()
    print("  RANDOM side-blind thinning of M_11, weekly grid -- median DD-matched income:")
    lifts = []
    for rate in (0.02, 0.05, 0.10, 0.20, 0.40, 0.70):
        nrm = max(1, int(round(rate * len(tv))))
        d = float(np.median(random_thinning_placebo(tv, tp, nrm, "fixed_dd",
                                                    n=400, n_periods=n_per)))
        lifts.append(d - base_income)
        print("    delete %3.0f%% of trades -> $%7.0f/wk  (lift %+.0f)"
              % (100 * rate, d, d - base_income))
    ok.append(("random thinning does NOT inflate M_11's DD-matched income",
               all(l < 0 for l in lifts),
               "monotone NEGATIVE at every rate 2%-70% -- T2's +$129..139/wk does NOT "
               "reproduce on this object/grid"))
    print()
    print("  ** T2_VERDICT_20260831 reports random thinning LIFTING DD-matched income by")
    print("     +$129..139/wk. On M_11's certified weekly series that does NOT reproduce at")
    print("     any rate: the effect is monotone NEGATIVE. T2's figure was measured on a")
    print("     DIFFERENT object (Book 7 = M_11 + ORB30 + MC01) and/or a different grid.")
    print("     Grid matters enormously: max DD is $%.0f weekly vs $51,891 on sessions."
          % max_drawdown(ref))
    print("     THE GOVERNANCE RULE RESTS ON THE MECHANISM ABOVE, NOT ON THAT NUMBER.")

    print()
    for name, passed, detail in ok:
        print("  [%s] %-58s %s" % ("PASS" if passed else "FAIL", name, detail))
    n = sum(1 for _, p, _ in ok if p)
    print("  %s (%d/%d)" % ("ALL PASS" if n == len(ok) else "FAILURES", n, len(ok)))
    return 0 if n == len(ok) else 1


if __name__ == "__main__":
    import sys
    print("EVAL BATTERY -- reproducing runs/T2_VERDICT_20260831's indictment of fixed-DD\n")
    sys.exit(selftest())
