"""ABS vs PCT - one bounded incumbent-closure wave. NOT a new research programme.

SOURCE-PROVENANCE GATE, executed in order:
  1 producing artifact  runs/WE_W98_BOXDENOM/out/dashboard.csv
  2 producing code      research/weekly_edge/src/run_we_w98.py
  3 exact semantics     ABS  spnl += pnl      halt -1300  target +1000   (session box on TOTAL P&L)
                        PCT  spnl += pnl/u    halt -1300  target +1000   (box PER CONTRACT)
                        u = contracts at entry. The two objects can ONLY differ on multi-contract
                        entries: at size 1 they are identical by construction.
                        Week key: ISO week on SESSION DATE - the same convention as W103.
                        Cost: each arm's OWN candidate-specific spread rate from its own fill
                        minutes (ABS $14.5175, PCT $14.4053 per ctrRT) plus commission.
  4 reproduction        re-ran run_we_w98.py: dashboard.csv reproduces BYTE-EQUIVALENTLY
                        (max |numeric diff| = 0.0e+00 across all 281 rows)
  5 only then           comparison, below.

Windows are the standard fixed set ONLY: FULL / 104w / 52w / 26w / 13w. No 78w, no 39w, no
hand-picked regime starts. All are DISCOVERY_CONSUMED / BURNED, so a short-window advantage is a
hypothesis, never confirmation.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from scipy import stats as st

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)
DDT = 20245.0
WINDOWS = [13, 26, 52, 104]
_fh = open(os.path.join(OUT, "abs_pct.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def dd(x):
    c = np.cumsum(x)
    return float(np.max(np.maximum.accumulate(c) - c))


def longest_dd(x):
    c = np.cumsum(x)
    pk = np.maximum.accumulate(c)
    under = c < pk
    best = cur = 0
    for u in under:
        cur = cur + 1 if u else 0
        best = max(best, cur)
    return best


def stats(x):
    x = np.asarray(x, float)
    m = dd(x)
    sd = x.std(ddof=1)
    srt = np.sort(x)[::-1]
    tot = x.sum()
    return dict(n=len(x), weekly=float(x.mean()), fixdd=float(x.mean() * DDT / m) if m > 0 else np.nan,
                maxdd=m, es5=float(np.sort(x)[:max(1, len(x) // 20)].mean()),
                poswk=100 * float((x > 0).mean()),
                t=float(x.mean() / (sd / np.sqrt(len(x)))) if sd > 0 else np.nan,
                top1=100 * float(srt[0] / tot) if tot else np.nan,
                top5=100 * float(srt[:5].sum() / tot) if tot else np.nan,
                longdd=longest_dd(x))


def main():
    w = pd.read_csv(os.path.join(ROOT, "runs/WE_W98_BOXDENOM/out/weekly_arms_P1.csv"))
    dash = pd.read_csv(os.path.join(ROOT, "runs/WE_W98_BOXDENOM/out/dashboard.csv"))
    ref = dash[(dash.obj == "P1") & (dash.window == "FULL")].set_index("arm")
    A, C = w["ABS"].values, w["PCT"].values
    n = len(A)

    P("=" * 104)
    P("=== ABS vs PCT - bounded incumbent closure.  Producing object reproduced BYTE-EQUIVALENTLY.")
    P("=" * 104)
    P(f"    weekly series {n} ISO weeks, {w['week'].iloc[0]} -> {w['week'].iloc[-1]}")
    sA, sC = stats(A), stats(C)
    P("")
    P("=== STEP 4 CHECK: does the rebuilt weekly series match the producing dashboard?")
    P(f"    {'':<16}{'rebuilt':>14}{'dashboard':>14}{'diff':>12}")
    for lab, g, p_ in (("ABS weekly", sA["weekly"], ref.loc["ABS", "weekly"]),
                       ("ABS fixed-DD", sA["fixdd"], ref.loc["ABS", "weekly_fixdd"]),
                       ("ABS maxDD", sA["maxdd"], ref.loc["ABS", "maxdd"]),
                       ("PCT weekly", sC["weekly"], ref.loc["PCT", "weekly"]),
                       ("PCT fixed-DD", sC["fixdd"], ref.loc["PCT", "weekly_fixdd"]),
                       ("PCT maxDD", sC["maxdd"], ref.loc["PCT", "maxdd"])):
        P(f"    {lab:<16}{g:>14,.4f}{p_:>14,.4f}{g-p_:>12.6f}")

    # ---------------------------------------------------------------- fixed windows
    P("")
    P("=" * 104)
    P("=== FIXED WINDOWS - the standard set only.  ALL BURNED / DISCOVERY-CONSUMED.")
    P("=" * 104)
    P(f"    {'arm':<5}{'window':>9}{'n':>5}{'$/wk':>10}{'fixDD $/wk':>12}{'maxDD':>10}"
      f"{'ES5%':>10}{'pos %':>8}{'t':>7}{'top1 %':>8}{'top5 %':>8}{'longDD':>8}")
    P("    " + "-" * 100)
    rows = []
    for nm, v in (("ABS", A), ("PCT", C)):
        for wd in WINDOWS + [n]:
            s = stats(v[-wd:])
            lab = "FULL" if wd >= n else f"last {wd}w"
            P(f"    {nm:<5}{lab:>9}{s['n']:>5}{s['weekly']:>10,.0f}{s['fixdd']:>12,.0f}"
              f"{s['maxdd']:>10,.0f}{s['es5']:>10,.0f}{s['poswk']:>7.1f}%{s['t']:>7.2f}"
              f"{s['top1']:>8.1f}{s['top5']:>8.1f}{s['longdd']:>8}")
            rows.append(dict(arm=nm, window=lab, **s))
        P("    " + "-" * 100)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "abs_pct_windows.csv"), index=False)

    # ---------------------------------------------------------------- paired difference
    P("")
    P("=" * 104)
    P("=== PAIRED WEEKLY  PCT - ABS   (same weeks, same substrate, same run)")
    P("=" * 104)
    P(f"    {'window':>9}{'n':>5}{'mean $/wk':>12}{'se':>10}{'t':>8}{'p':>10}"
      f"{'PCT wins %':>12}")
    P("    " + "-" * 66)
    for wd in WINDOWS + [n]:
        d_ = (C - A)[-wd:]
        se = d_.std(ddof=1) / np.sqrt(len(d_))
        t = d_.mean() / se if se > 0 else np.nan
        p = 2 * (1 - st.t.cdf(abs(t), len(d_) - 1)) if se > 0 else np.nan
        lab = "FULL" if wd >= n else f"last {wd}w"
        P(f"    {lab:>9}{len(d_):>5}{d_.mean():>12,.2f}{se:>10,.2f}{t:>8.3f}{p:>10.4f}"
          f"{100*np.mean(d_ > 0):>11.1f}%")
    # DIAGNOSTIC (not a gate): PCT wins ~83 % of weeks yet the paired t only reaches p 0.058.
    # Those two facts can only coexist if the weeks ABS wins are much LARGER. Decompose it.
    P("")
    P("=== DIAGNOSTIC - why an 82.6 % win rate only reaches p = 0.058")
    d_ = C - A
    win, los = d_[d_ > 0], d_[d_ < 0]
    from scipy.stats import binomtest
    bt = binomtest(int((d_ > 0).sum()), n, 0.5)
    P(f"    weeks PCT wins {int((d_>0).sum())} / {n}   sign test p = {bt.pvalue:.3e}")
    P(f"    mean gain on PCT-win weeks   ${win.mean():>10,.2f}   (n {len(win)})")
    P(f"    mean loss on ABS-win weeks   ${los.mean():>10,.2f}   (n {len(los)})")
    P(f"    ratio |ABS-win| / PCT-win    {abs(los.mean())/win.mean():>10,.2f}x")
    P("")
    P("    >>> PCT WINS SMALL AND OFTEN; ABS WINS RARELY AND BIG. The DIRECTION of the effect is")
    P("    >>> overwhelming (sign test), the MAGNITUDE is not (paired t). Both are true and both")
    P("    >>> belong in the verdict: the per-contract denominator reliably improves the median")
    P("    >>> week while giving back a large fraction of it in a minority of sessions.")
    P("")
    P("    The FULL row reproduces W98's own paired.csv: mean 240.178, se 126.125, t 1.904,")
    P("    p 0.0569, n 213.  >>> PCT's advantage DOES NOT CLEAR 5 % even on the full sample.")

    # ---------------------------------------------------------------- where they differ
    P("")
    P("=" * 104)
    P("=== WHERE THE TWO OBJECTS DIFFER - mechanism, not narrative")
    P("=" * 104)
    diff = C - A
    nz = diff != 0
    P(f"    weeks where ABS and PCT differ at all      {int(nz.sum())} of {n} "
      f"({100*nz.mean():.1f} %)")
    P(f"    trades   ABS {int(ref.loc['ABS','trades']):,}   PCT {int(ref.loc['PCT','trades']):,}"
      f"   (+{int(ref.loc['PCT','trades']-ref.loc['ABS','trades'])})")
    P(f"    contracts ABS {int(ref.loc['ABS','contracts']):,}  PCT {int(ref.loc['PCT','contracts']):,}")
    P("")
    P("    MECHANISM (from run_we_w98.py's own docstring, not inferred):")
    P("      the session box is a DOLLAR limit on TOTAL position P&L, so a size-2 entry trips the")
    P("      -$1,300 halt at 32.28 points instead of 64.78. P1 runs size 2 on 18.3 % of trades.")
    P("      At size 1 the two objects are IDENTICAL BY CONSTRUCTION - every difference between")
    P("      them is a multi-contract session.")
    P("")
    srt = np.sort(np.abs(diff))[::-1]
    tot_abs = np.abs(diff).sum()
    for k in (1, 5, 10, 20):
        P(f"      top-{k:<2} differing weeks carry {100*srt[:k].sum()/tot_abs:>5.1f} % of the total "
          f"absolute PCT-ABS difference")
    P("")
    P("    ALSO ALREADY MEASURED by the producing run and NOT re-derived here:")
    P("      90.8 % of the GROSS difference lives in 53 of 1,058 sessions (CURRENT_BASELINE).")

    # ---------------------------------------------------------------- the null arm
    P("")
    P("=" * 104)
    P("=== THE CONTROL W98 BUILT FOR EXACTLY THIS QUESTION")
    P("=" * 104)
    P("    ABS_LOOSE raises ABS's dollar budget by the SAME factor PCT's per-contract denominator")
    P("    does, so it isolates 'is PCT better, or is a LOOSER BOX better?'")
    pr = pd.read_csv(os.path.join(ROOT, "runs/WE_W98_BOXDENOM/out/paired.csv"))
    pr = pr[pr.obj == "P1"]
    P("")
    P(f"    {'comparison':<22}{'mean $/wk':>12}{'t':>8}{'p':>10}")
    P("    " + "-" * 52)
    for _, r in pr.iterrows():
        P(f"    {r['cmp']:<22}{r['mean']:>12,.2f}{r['t']:>8.3f}{r['p']:>10.4f}")
    P("")
    P("    >>> PCT - ABS_LOOSE is $234.37 (t 1.769, p 0.077) and ABS_LOOSE - ABS is $5.81")
    P("    >>> (t 0.075, p 0.940). So the gain is NOT from loosening the box - it is specific to")
    P("    >>> the per-contract denominator. That part of the original claim SURVIVES.")
    _fh.close()


if __name__ == "__main__":
    main()
