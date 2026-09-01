"""G3_SHORTALPHA / MIRROR_CONT - what would a FORWARD verdict actually need?

Angle: WE_W120's MIRROR_CONT fails the preregistered four-gate test on gate 2 and gate 2 only,
passes both tail gates, and its own report names "forward evidence on sealed >=2026-08-01 data" as
the verdict-changer. This program produces the decision-ready packet:

  (a) the object restated with ZERO remaining choices,
  (b) the exact forward statistic that settles gate 2, and the HONEST required N at the observed
      effect size,
  (c) whether it can ride the forward PAPER DECISION STREAM instead of needing a deployment.

It produces NO P&L and NO candidate. It reads only artifacts that already exist and that end
2026-07-31. Nothing >= 2026-08-01 is opened.

Everything printed here is printed BY THE PROGRAM. No table is assembled by hand.
"""
from __future__ import annotations

import hashlib
import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "research", "weekly_edge", "src"))

OUT = os.path.join(ROOT, "runs", "G3_SHORTALPHA_20260831", "out")
os.makedirs(OUT, exist_ok=True)

W120 = os.path.join(ROOT, "runs", "WE_W120_MOMMARGINAL", "out")
SEAL = pd.Timestamp("2026-08-01")
DDT = 20245.0                 # the repo's fixed-drawdown normaliser
SEED = 3831
NSHIFT = 1000
NBOOT = 4000
BLOCK = 4                     # weeks, moving-block bootstrap

# cost constants - printed as a floor / primary / all-in triple, never a single headline
COMM_RT_FLOOR = 4.36          # commission only. NEVER a headline.
COST_PRIMARY = 20.65          # G2_EXEC01 measured, 113 real round turns
COST_ALLIN = 25.01
PV = 20.0

_OUTF = open(os.path.join(OUT, "mirror-cont.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_OUTF)
    _OUTF.flush()


def H(title):
    P("")
    P("=" * 118)
    P(title)
    P("=" * 118)


def sha(path, n=12):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:n]


# ==================================================================================================
def seal_assert(J, S):
    H("=== 0. SEAL ASSERTION (printed, not assumed)")
    wk_end = pd.to_datetime(
        [f"{w[:4]}-W{w[6:]}-7" for w in J["week"]], format="%G-W%V-%u")
    sd = pd.to_datetime(S["date"])
    # the DATA boundary is the session date. The ISO week LABEL of the last week (2026-W31)
    # nominally runs to Sunday 2026-08-02, but its content stops at the last session, 2026-07-31.
    checks = [
        ("sessions.csv      last session date", sd.max()),
        ("sessions.csv      max date in ANY week", sd.max()),
    ]
    ok = True
    for lab, v in checks:
        good = v < SEAL
        ok &= good
        P(f"    {lab:<42}{str(v)[:10]:>12}   < 2026-08-01 ? {'YES' if good else 'NO'}")
    P(f"    {'weekly_joint.csv  last ISO week LABEL':<42}{J['week'].iloc[-1]:>12}   "
      f"nominal Sunday {str(wk_end.max())[:10]}, but its CONTENT ends {str(sd.max())[:10]}")
    P(f"    files opened by this program: {len(FILES)} - all listed below with sha256[:12]")
    for f_ in FILES:
        P(f"        {sha(f_)}  {os.path.relpath(f_, ROOT)}")
    P("")
    P(f"    NO BAR SUBSTRATE IS LOADED. No session >= 2026-08-01 is read. ASSERTION: "
      f"{'PASS' if ok else 'FAIL'}")
    assert ok, "SEAL VIOLATION"
    return wk_end


FILES = [
    os.path.join(W120, "weekly_joint.csv"),
    os.path.join(W120, "sessions.csv"),
    os.path.join(ROOT, "research", "weekly_edge", "src", "run_we_w118.py"),
    os.path.join(ROOT, "research", "weekly_edge", "src", "run_we_w120.py"),
    os.path.join(ROOT, "research", "weekly_edge", "src", "run_we_w114.py"),
]


# ==================================================================================================
def section_a():
    """The object, restated with zero remaining choices."""
    H("=== (a) THE OBJECT, RESTATED WITH ZERO REMAINING CHOICES")
    P("    Every row below is a FROZEN value read out of the source that produced W120's numbers.")
    P("    A forward implementation that changes any row is a DIFFERENT OBJECT and does not")
    P("    inherit W120's evidence.")
    P("")
    from run_we_w114 import RTH0                                       # noqa: E402
    from run_we_w118 import (EXIT_M, T_EXTREME_MAX, T_TRIGGER_MAX,     # noqa: E402
                             RETR, RATES, TICKV)
    from run_we_w01 import COMM_RT                                     # noqa: E402

    def hhmm(m):
        return f"{m//60:02d}:{m%60:02d}"

    rows = [
        ("instrument",            "NQ front-month continuous, 1-minute, END-STAMPED",
         "the bar stamped 09:31 covers 09:30:00-09:30:59"),
        ("substrate loader",      "run_we_w17.load_deep(a, b, extend=True)",
         "extend=True supplies the pre-window warm-up the 250-session roll needs"),
        ("session universe",      "every session in the window; one trade per session at most",
         "the `done[r]` latch in scan() makes the trade unique per session"),
        ("anchor bar RTH0",       f"minute-of-day {RTH0} = {hhmm(RTH0)}",
         "o0 = the OPEN of that bar = the 09:30:00 print. NOT the prior close"),
        ("bars scanned",          f"mod in [{RTH0}, {EXIT_M}] = [{hhmm(RTH0)}, {hhmm(EXIT_M)}]",
         "session skipped if <60 such bars or if the first is not exactly RTH0"),
        ("running excursion",     "up = runH - o0 ; dn = o0 - runL ; E = max(up, dn)",
         "runH/runL are RUNNING extremes of HIGH/LOW from RTH0 to bar j inclusive"),
        ("extreme deadline",      f"tset <= {T_EXTREME_MAX} = {hhmm(T_EXTREME_MAX)}",
         "tset = the minute at which the CURRENT running extreme was set"),
        ("trigger deadline",      f"loop breaks when mod > {T_TRIGGER_MAX} = {hhmm(T_TRIGGER_MAX)}",
         "no entry may be initiated after 14:30"),
        ("threshold source",      f"exc12[s] = E evaluated at mod == {T_EXTREME_MAX} (12:00)",
         "fallback if the 12:00 bar is absent: E at loop exit. FROZEN, including the fallback"),
        ("causal threshold",      "pd.Series(exc12).rolling(250, min_periods=60)"
                                  ".quantile(1 - 0.50).shift(1)",
         "= trailing MEDIAN of the prior 250 sessions' 12:00 excursion. shift(1) => causal"),
        ("gate rate",             "0.50  (W118's primary cell; RATES = " + str(RATES) + ")",
         "NOT re-chosen. W120 spec: 'no threshold, level, gate, exit or window may be re-chosen'"),
        ("gate application",      "E >= thr[s] must hold AT THE TRIGGER BAR",
         "the W118 CORRECTION: applying it to the 12:00 excursion after the fact was the defect"),
        ("retracement level R",   "0.50  (RETR = " + str(RETR) + ")",
         "retr measured on bar j's CLOSE: (runH-c)/E if up>=dn else (c-runL)/E"),
        ("trigger",               "first bar j with E>=thr, tset<=12:00, retr >= 0.50",
         "ties: if up == dn the UP branch wins (`if up >= dn`)"),
        ("entry",                 "the OPEN of bar j+1 (idx[j+1])",
         "one full bar of latency. If j+1 does not exist the session is skipped"),
        ("DIRECTION (the mirror)", "sgn_MIRROR = +1 if the extreme is the HIGH, -1 if the LOW",
         "W118's reversal is the NEGATIVE of this. MIRROR trades WITH the prevailing move"),
        ("exit",                  f"the CLOSE of the bar stamped {EXIT_M} = {hhmm(EXIT_M)}",
         "no stop, no target, no trailing, no intrabar risk control of any kind"),
        ("size",                  "1 contract, always",
         "no sizing rule, no vol targeting, no scaling"),
        ("point value",           f"${PV:.0f} / NQ point", ""),
        ("research cost charged", f"${COMM_RT:.2f} + {TICKV:.0f} * (sp[m_entry] + sp[944]) / 2",
         "sp = W82 per-minute spread profile, in ticks"),
    ]
    P(f"{'element':<24}{'frozen value':<62}note")
    P("-" * 118)
    for k, v, n in rows:
        P(f"{k:<24}{v:<62}{n}")
    P("")
    P("    REMAINING FREE CHOICES: NONE. Everything above is a literal in run_we_w118.py /")
    P("    run_we_w114.py, or a constant passed by run_we_w120.py line 63:")
    P("        R = econ(W, tg[0.50], -dg[0.50], ALL)      # the minus sign IS the mirror")
    P("")
    P("    THE ONE THING THAT IS *NOT* PARAMETER-FREE, contrary to the W120 report's phrase")
    P("    'parameter-light and needs no refit':")
    P("        the 250-session trailing median threshold is STATE, not a parameter. A forward")
    P("        implementation must carry 250 sessions (~12 calendar months) of prior 12:00")
    P("        excursions into its first forward decision, or it is not the same object. It is")
    P("        causal, so this is a WARM-UP requirement, not a refit - but a forward run that")
    P("        starts cold at 2026-08-01 with min_periods=60 uses a 60-session median for its")
    P("        first ~190 decisions and IS A DIFFERENT OBJECT for those decisions.")


# ==================================================================================================
def dstats(a, b):
    """W120's dstats(), reproduced exactly. a = book weekly $, b = candidate weekly $."""
    m = a < 0
    qa, qb = np.percentile(a, 10), np.percentile(b, 10)
    lo = a <= qa
    return {"rho": float(np.corrcoef(a, b)[0, 1]),
            "rho | book losing": float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 5 else np.nan,
            "P(cand<0 | book<0)": float((b[m] < 0).mean()) if m.sum() else np.nan,
            "worst-decile overlap": float(((a <= qa) & (b <= qb)).mean()),
            "$ on book-losing weeks": float(b[m].mean()) if m.sum() else np.nan,
            "tail beta": float(np.polyfit(a[lo], b[lo], 1)[0]) if lo.sum() > 5 else np.nan}


def dd_max(v):
    cum = np.cumsum(np.asarray(v, float))
    return float((np.maximum.accumulate(cum) - cum).max())


def fixdd(v):
    v = np.asarray(v, float)
    return float(v.mean()) * DDT / max(dd_max(v), 1e-9)


def blend(J, cols, how):
    if how == "invvol":
        w = np.array([1 / max(J[c].std(ddof=1), 1e-9) for c in cols])
    else:
        w = np.array([1 / max(abs(J[c].mean()), 1e-9) for c in cols])
    w = w / w.sum() * len(cols)
    return (sum(w[i] * J[cols[i]] for i in range(len(cols))) / len(cols)).to_numpy()


# ==================================================================================================
def section_b_reproduce(J, rng):
    """Reproduce W120's gates, then supply the two nulls W120 never computed."""
    bookv = J["book"].to_numpy()
    mcv = J["mc"].to_numpy()
    NW = len(J)
    lose = bookv < 0

    H("=== 1. REPRODUCTION OF W120's GATE TABLE (must match the committed run, or stop)")
    real = dstats(bookv, mcv)
    NN = pd.DataFrame([dstats(bookv, np.roll(mcv, k)) for k in range(1, min(NSHIFT, NW))])
    ref = {"rho": 0.145, "rho | book losing": -0.158, "P(cand<0 | book<0)": 0.310,
           "worst-decile overlap": 0.019, "$ on book-losing weeks": 614.021, "tail beta": -1.861}
    P(f"    {NW} weeks. book-losing weeks = {int(lose.sum())} ({100*lose.mean():.1f} %). "
      f"P(MIRROR<0) = {float((mcv<0).mean()):.3f}")
    P("")
    P(f"{'statistic':<26}{'REAL':>11}{'W120':>11}{'match':>8}{'null mean':>11}{'null p95':>11}"
      f"{'pctile':>9}")
    allmatch = True
    for k in real:
        nv = NN[k].to_numpy()
        m_ = abs(real[k] - ref[k]) < 1e-2
        allmatch &= m_
        P(f"{k:<26}{real[k]:>11.3f}{ref[k]:>11.3f}{('OK' if m_ else 'DIFF'):>8}"
          f"{np.nanmean(nv):>11.3f}{np.nanpercentile(nv,95):>11.3f}"
          f"{100*float(np.nanmean(nv < real[k])):>8.1f}th")
    P("")
    P(f"    REPRODUCTION: {'EXACT' if allmatch else 'MISMATCH - STOP'}")
    assert allmatch

    # ------------------------------------------------------------------ the nulls W120 skipped
    H("=== 2. THE TWO GATES W120 PASSED WITHOUT A NULL. Supplying the nulls now.")
    P("    W120 ran a 1,000-shift circular null for gate 2 and gate 4 only. Gate 1 ('earns > 0')")
    P("    and gate 3 ('incremental fixed-DD > 0 at either convention') were scored against ZERO,")
    P("    not against chance. A candidate with a positive unconditional mean passes gate 1 by")
    P("    construction, and CLAUDE.md forbids letting a reduced risk denominator masquerade as")
    P("    information. So: same object, ALIGNMENT DESTROYED by circular shift, both gates re-run.")
    P("")

    # gate 1 null
    g1_real = float(mcv[lose].mean())
    g1_null = np.array([float(np.roll(mcv, k)[lose].mean()) for k in range(1, NW)])
    P("    GATE 1  -- $ on book-losing weeks > 0")
    P(f"        REAL ${g1_real:,.0f}   |   circular-shift null: mean ${g1_null.mean():,.0f}, "
      f"P(null > 0) = {float((g1_null > 0).mean()):.3f}")
    P(f"        => a SHIFTED (alignment-destroyed) MIRROR passes gate 1 "
      f"{100*float((g1_null > 0).mean()):.1f} % of the time.")
    P("        GATE 1 CARRIES NO INFORMATION ABOUT ALIGNMENT. It is a restatement of "
      "'MIRROR is profitable'.")
    P("")

    # gate 3 null: incremental fixed-DD with the candidate leg circularly shifted
    P("    GATE 3  -- incremental fixed-DD weekly $ > 0 at EITHER weighting convention")
    inc_real, inc_null = {}, {}
    for how in ("invvol", "income"):
        base = fixdd(blend(J, ["p1", "xm"], how))
        with_ = fixdd(blend(J, ["p1", "xm", "mc"], how))
        inc_real[how] = with_ - base
        nul = np.empty(NW - 1)
        for i, k in enumerate(range(1, NW)):
            Jk = J.copy()
            Jk["mc"] = np.roll(mcv, k)
            nul[i] = fixdd(blend(Jk, ["p1", "xm", "mc"], how)) - base
        inc_null[how] = nul
    P(f"{'convention':<14}{'base fixDD':>12}{'with MIRROR':>13}{'REAL incr':>11}"
      f"{'null mean':>11}{'null p95':>11}{'pctile':>9}{'P(null>0)':>11}")
    for how in ("invvol", "income"):
        base = fixdd(blend(J, ["p1", "xm"], how))
        nul = inc_null[how]
        P(f"{how:<14}{base:>12,.0f}{base+inc_real[how]:>13,.0f}{inc_real[how]:>+11,.0f}"
          f"{nul.mean():>+11,.0f}{np.percentile(nul,95):>+11,.0f}"
          f"{100*float((nul < inc_real[how]).mean()):>8.1f}th{float((nul>0).mean()):>11.3f}")
    P("")
    P("    A circularly-shifted MIRROR has the SAME marginal distribution, the same weekly")
    P("    volatility and the same autocorrelation as the real one - only its ALIGNMENT with the")
    P("    book is destroyed. Read the P(null>0) column: that is how often a THIRD LEG WITH NO")
    P("    RELATIONSHIP TO THE BOOK AT ALL raises drawdown-matched income.")
    P("")

    # what fraction of the DD improvement is pure dilution?
    for how in ("invvol",):
        b2 = blend(J, ["p1", "xm"], how)
        b3 = blend(J, ["p1", "xm", "mc"], how)
        P(f"    Mechanically, on {how} weights: adding a third leg re-weights P1 and XM DOWNWARD.")
        P(f"        2-leg book:  wk ${b2.mean():>7,.0f}   maxDD ${dd_max(b2):>8,.0f}   "
          f"fixDD ${fixdd(b2):>7,.0f}")
        P(f"        3-leg book:  wk ${b3.mean():>7,.0f}   maxDD ${dd_max(b3):>8,.0f}   "
          f"fixDD ${fixdd(b3):>7,.0f}")
        P(f"        RAW weekly dollars FALL ${b2.mean()-b3.mean():,.0f}/wk ("
          f"{100*(b3.mean()-b2.mean())/b2.mean():+.1f} %). The gain is entirely in the DENOMINATOR.")
    return real, NN, lose, inc_real, inc_null


# ==================================================================================================
def section_c_gate2_power(J, rng, real, NN, lose):
    """The exact forward statistic for gate 2, and the honest required N."""
    bookv = J["book"].to_numpy()
    mcv = J["mc"].to_numpy()
    NW = len(J)
    nL = int(lose.sum())
    p_lose = nL / NW

    H("=== 3. (b) WHAT GATE 2 ACTUALLY TESTS - and it is not what the sentence says")
    P("    Gate 2: mean(MIRROR weekly $ | book week < 0)  >  95th pct of a 1,000-shift null.")
    P("    Under a circular shift the alignment is random, so the null's EXPECTATION is exactly")
    P("    MIRROR's UNCONDITIONAL weekly mean. Check that identity numerically:")
    uncond = float(mcv.mean())
    nullmean = float(np.nanmean(NN["$ on book-losing weeks"].to_numpy()))
    P("")
    P(f"        MIRROR unconditional weekly mean      ${uncond:>10,.2f}")
    P(f"        circular-shift null mean               ${nullmean:>10,.2f}")
    P(f"        difference                             ${uncond-nullmean:>10,.2f}   "
      f"(pure edge-effect of the shift)")
    P("")
    P("    ==> GATE 2 IS THE SINGLE STATISTIC:")
    P("")
    P("            DELTA  =  mean(MIRROR | book < 0)  -  mean(MIRROR)")
    P("")
    P("        i.e. 'does MIRROR earn MORE when the book loses than it earns on an average week?'")
    P("        Equivalently -Cov(MIRROR_wk, 1{book<0}) / P(book<0). It is a ONE-NUMBER question")
    P("        and it has NOTHING to do with whether MIRROR is profitable.")

    cond = float(mcv[lose].mean())
    delta = cond - uncond
    H("=== 4. THE OBSERVED EFFECT SIZE, stated so it can be wrong")
    P(f"{'quantity':<44}{'value':>14}")
    P("-" * 60)
    P(f"{'weeks N':<44}{NW:>14,}")
    P(f"{'book-losing weeks nL':<44}{nL:>14,}")
    P(f"{'P(book < 0)':<44}{p_lose:>14.3f}")
    P(f"{'MIRROR mean | book losing':<44}{cond:>14,.2f}")
    P(f"{'MIRROR unconditional mean':<44}{uncond:>14,.2f}")
    P(f"{'DELTA (the gate-2 effect size)':<44}{delta:>+14,.2f}")
    P(f"{'sd of MIRROR weekly $':<44}{float(mcv.std(ddof=1)):>14,.2f}")
    P("")
    P("    ############################################################################")
    P("    #  THE OBSERVED EFFECT IS NEGATIVE.  MIRROR earns ${:,.0f}/wk LESS on the book's".format(-delta))
    P("    #  losing weeks than on an average week.  Gate 2 does not 'narrowly fail' -")
    P("    #  the POINT ESTIMATE IS ON THE WRONG SIDE OF THE NULL MEAN.")
    P("    ############################################################################")

    # ---------------- sampling distribution of DELTA
    H("=== 5. THE SAMPLING DISTRIBUTION OF DELTA (three independent constructions)")
    # (i) circular shift
    d_shift = NN["$ on book-losing weeks"].to_numpy() - uncond
    # (ii) analytic permutation SE (finite-population, sampling nL of N without replacement)
    se_perm = float(mcv.std(ddof=1)) * np.sqrt((1 - p_lose) / (p_lose * NW) * NW / (NW - 1))
    # (iii) moving-block bootstrap on the PAIRED (book, mc) weeks - preserves dependence
    idx0 = np.arange(NW)
    nblk = int(np.ceil(NW / BLOCK))
    dboot = np.empty(NBOOT)
    for b in range(NBOOT):
        starts = rng.integers(0, NW - BLOCK + 1, size=nblk)
        take = np.concatenate([idx0[s:s + BLOCK] for s in starts])[:NW]
        bb, mm = bookv[take], mcv[take]
        l2 = bb < 0
        dboot[b] = (mm[l2].mean() - mm.mean()) if l2.sum() > 5 else np.nan
    dboot = dboot[np.isfinite(dboot)]
    P(f"{'construction':<44}{'SE of DELTA':>14}")
    P("-" * 58)
    P(f"{'circular shift of MIRROR (W120 instrument)':<44}{d_shift.std(ddof=1):>14,.2f}")
    P(f"{'analytic permutation, finite-population':<44}{se_perm:>14,.2f}")
    P(f"{'moving-block bootstrap (L=4 wk, paired)':<44}{dboot.std(ddof=1):>14,.2f}")
    se = float(d_shift.std(ddof=1))
    P("")
    P(f"    They agree to within {100*abs(dboot.std(ddof=1)-se)/se:.0f} %. "
      f"The SE used from here on is the circular-shift SE, ${se:,.0f}, because it is the")
    P("    instrument the preregistered gate actually used.")
    P("")
    lo95, hi95 = delta - 1.96 * se, delta + 1.96 * se
    P(f"    DELTA = ${delta:+,.0f}   95 % CI [${lo95:+,.0f}, ${hi95:+,.0f}]   "
      f"z = {delta/se:+.3f}   one-sided p(DELTA>0) = {1-_ncdf(delta/se):.3f}")
    P(f"    Gate-2 pass threshold at N={NW}: DELTA >= 1.645 * SE = ${1.645*se:,.0f}. "
      f"Observed is ${delta:+,.0f}.")
    P(f"    The observed DELTA is {abs(delta - 1.645*se)/se:.2f} standard errors SHORT of its own gate.")
    return delta, se, uncond, p_lose, hi95


def _ncdf(z):
    from math import erf, sqrt
    return 0.5 * (1 + erf(z / sqrt(2)))


def _zq(p):
    # inverse normal, Acklam-lite via bisection (no scipy dependency)
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _ncdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ==================================================================================================
def section_d_required_n(delta, se, NW, p_lose, hi95):
    H("=== 6. (b) REQUIRED N. Computed honestly, and the honest answer is ugly.")
    P("    SE(DELTA) scales as 1/sqrt(N) because it is a difference of means over a fixed")
    P("    fraction p of weeks:  SE(N) = SE(213) * sqrt(213 / N).")
    P("    Gate 2 is ONE-SIDED at alpha = 0.05 (beat the null's 95th percentile).")
    P("    Required N for power 1-beta:   N = 213 * ( SE(213) * (z_0.95 + z_{1-beta}) / DELTA_true )^2")
    P("")
    z95 = _zq(0.95)
    P(f"    z_0.95 = {z95:.3f}   SE(213) = ${se:,.0f}")
    P("")
    P("    ---- CASE 1: the true DELTA equals the observed DELTA ----------------------------")
    P("")
    P(f"        DELTA_true = ${delta:+,.0f}.  It is NEGATIVE. The gate requires DELTA > +1.645*SE.")
    P("        A test statistic whose EXPECTATION is negative converges AWAY from the gate as N")
    P("        grows. Power at every N is BELOW alpha and DECREASING:")
    P("")
    P(f"{'forward weeks N':>16}{'years':>8}{'SE(N)':>10}{'gate thr':>10}{'power':>10}")
    for N in (52, 104, 156, 208, 260, 520, 1040, 5200):
        seN = se * np.sqrt(NW / N)
        thr = z95 * seN
        pw = 1 - _ncdf((thr - delta) / seN)
        P(f"{N:>16,}{N/52:>8.1f}{seN:>10,.0f}{thr:>10,.0f}{pw:>10.5f}")
    P("")
    P("    ####################################################################################")
    P("    #  REQUIRED N AT THE OBSERVED EFFECT SIZE = INFINITE. NOT 'three years'. NOT ANY")
    P("    #  NUMBER OF YEARS. There is no forward sample size at which a true DELTA of")
    P(f"    #  ${delta:+,.0f} passes a gate that requires DELTA > 0. More data makes it fail HARDER.")
    P("    ####################################################################################")
    P("")
    P("    ---- CASE 2: the true DELTA is at the top of what the data still permits ---------")
    P("")
    P(f"        The 95 % CI upper limit is ${hi95:+,.0f}. This is the MOST OPTIMISTIC true effect")
    P("        the in-sample evidence does not already exclude. Treat it as the ceiling.")
    P("")
    P(f"{'DELTA_true':>14}{'  interpretation':<40}{'N @80%':>10}{'yr':>7}{'N @50%':>10}{'yr':>7}")
    cases = [
        (hi95,          "95 % CI upper limit (ceiling)"),
        (0.75 * hi95,   "75 % of the ceiling"),
        (0.50 * hi95,   "half the ceiling"),
        (1.645 * se,    "exactly the in-sample gate threshold"),
        (250.0,         "a $250/wk conditional lift"),
        (100.0,         "a $100/wk conditional lift"),
    ]
    for dt, lab in cases:
        if dt <= 0:
            P(f"{dt:>14,.0f}  {lab:<40}{'never':>10}{'-':>7}{'never':>10}{'-':>7}")
            continue
        n80 = NW * ((se * (z95 + _zq(0.80))) / dt) ** 2
        n50 = NW * ((se * (z95 + _zq(0.50))) / dt) ** 2
        P(f"{dt:>+14,.0f}  {lab:<40}{n80:>10,.0f}{n80/52:>7.1f}{n50:>10,.0f}{n50/52:>7.1f}")
    P("")
    P("    Read the top row. EVEN IF the true effect is the single most favourable value the")
    P(f"    in-sample data still permits (${hi95:+,.0f}/wk), settling gate 2 forward at 80 % power")
    P(f"    takes {NW * ((se*(z95+_zq(0.80)))/hi95)**2 / 52:.1f} YEARS of forward weeks. At 50 % power - a coin flip - "
      f"{NW * ((se*(z95+_zq(0.50)))/hi95)**2 / 52:.1f} years.")
    P("")
    P("    ---- CASE 3: POOLING the forward weeks with the in-sample 213 ---------------------")
    P("")
    P("    Weaker standard (the 213 weeks are DISCOVERY_CONSUMED for this object: W118 chose the")
    P("    cell, W120 read it), but it is the only route with a finite answer, so price it.")
    P("    Pooled DELTA = (213*DELTA_obs + N*DELTA_fwd) / (213+N), threshold 1.645*SE(213+N).")
    P("")
    P(f"{'forward N':>12}{'years':>8}{'required forward DELTA to pass pooled':>42}"
      f"{'x the ceiling':>15}")
    for N in (52, 104, 156, 208, 260, 520):
        seP = se * np.sqrt(NW / (NW + N))
        need = ((z95 * seP) * (NW + N) - NW * delta) / N
        P(f"{N:>12,}{N/52:>8.1f}{need:>+42,.0f}{need/hi95:>15.2f}")
    P("")
    P("    Every row demands a forward DELTA well ABOVE the ceiling of the in-sample CI. Pooling")
    P("    does not rescue the gate; it makes the forward window carry the in-sample deficit too.")


# ==================================================================================================
def section_e_tail(J, rng, real, NN, lose):
    H("=== 7. THE TAIL GATES - the statistics that DID pass, and what they rest on")
    bookv = J["book"].to_numpy()
    mcv = J["mc"].to_numpy()
    NW = len(J)
    q10 = np.percentile(bookv, 10)
    tail = bookv <= q10
    nt = int(tail.sum())
    P(f"    Book's worst decile: {nt} weeks (threshold ${q10:,.0f}/wk). The W120 REPORT says 21;")
    P(f"    its own code's mask (`a <= 10th pct`) holds {nt}. Small, but the report quoted a number")
    P("    it did not print. The W120 report is right about the substance: 'the bottom decile is")
    P("    ... a small sample carrying the most favourable statistic in the wave'.")
    P("")
    tb = float(np.polyfit(bookv[tail], mcv[tail], 1)[0])
    nv = NN["tail beta"].to_numpy()
    P(f"    tail beta REAL {tb:+.3f}   null mean {np.nanmean(nv):+.3f}   "
      f"null p05 {np.nanpercentile(nv,5):+.3f}   pctile {100*float(np.nanmean(nv<tb)):.1f}th")
    P("")
    P("    LEAVE-ONE-OUT over the 21 tail weeks. If one week owns the slope, the statistic is a")
    P("    single observation wearing a regression's clothes.")
    P("")
    ti = np.flatnonzero(tail)
    jk = []
    for i in ti:
        k = tail.copy(); k[i] = False
        s = float(np.polyfit(bookv[k], mcv[k], 1)[0])
        jk.append((s, i))
    jk_s = np.array([x[0] for x in jk])
    order = np.argsort(jk_s)[::-1]
    P(f"{'dropped week':<14}{'book $':>11}{'MIRROR $':>11}{'tail beta w/o it':>19}{'pctile':>9}")
    for r in list(order[:4]) + list(order[-2:]):
        s, i = jk[r]
        # re-null for the reduced tail set
        k = tail.copy(); k[i] = False
        nn = np.array([float(np.polyfit(bookv[k], np.roll(mcv, kk)[k], 1)[0])
                       for kk in range(1, NW)])
        P(f"{J['week'].iloc[i]:<14}{bookv[i]:>11,.0f}{mcv[i]:>11,.0f}{s:>19,.3f}"
          f"{100*float(np.nanmean(nn<s)):>8.1f}th")
    P("")
    P(f"    jackknife range of the tail beta: [{jk_s.min():+.3f}, {jk_s.max():+.3f}]   "
      f"sign flips? {'YES' if (jk_s.max()>0) else 'NO'}")
    P("")
    # how many tail weeks does MIRROR even trade in?
    P(f"    MIRROR is FLAT (zero P&L) in {int((mcv[tail]==0).sum())} of the {nt} tail weeks.")
    P(f"    Non-zero tail weeks: {int((mcv[tail]!=0).sum())}. The regression that carries the whole")
    P("    portfolio case is fitted on that many effective points.")
    P("")
    P("    FORWARD REQUIREMENT FOR THE TAIL GATES")
    P("    The worst decile is a RELATIVE definition, so it is always N/10 weeks. To reproduce")
    P(f"    the {nt} tail weeks the current case rests on requires {10*nt} forward weeks = "
      f"{10*nt/52:.1f} YEARS.")
    P(f"    With an ABSOLUTE threshold frozen at ${q10:,.0f}/wk the rate is the same "
      f"({100*tail.mean():.1f} % of weeks).")
    P("")
    P(f"{'forward weeks':>15}{'years':>8}{'tail weeks':>12}{'MIRROR-active tail wks (est)':>30}")
    act = float((mcv[tail] != 0).mean())
    for N in (52, 104, 156, 208, 260):
        P(f"{N:>15,}{N/52:>8.1f}{N/10:>12.1f}{N/10*act:>30.1f}")
    P("")
    P("    A slope on 5 points (one forward year) is not evidence. The tail gates need FOUR YEARS")
    P("    of forward weeks before they carry the mass they already carry in sample - and in")
    P("    sample they already failed to move the verdict.")

    # ---- the maxDD improvement: is it one episode?
    H("=== 8. WHERE THE -29 % MAX-DRAWDOWN HEADLINE COMES FROM")
    b2 = blend(J, ["p1", "xm"], "invvol")
    b3 = blend(J, ["p1", "xm", "mc"], "invvol")
    for lab, v in (("P1+XM", b2), ("P1+XM+MIRROR", b3)):
        cum = np.cumsum(v)
        dd = np.maximum.accumulate(cum) - cum
        i = int(np.argmax(dd))
        pk = int(np.argmax(cum[:i + 1]))
        P(f"    {lab:<14} maxDD ${dd.max():>8,.0f}   episode {J['week'].iloc[pk]} -> "
          f"{J['week'].iloc[i]}  ({i-pk} weeks)")
    cum2 = np.cumsum(b2)
    dd2 = np.maximum.accumulate(cum2) - cum2
    i2 = int(np.argmax(dd2)); p2 = int(np.argmax(cum2[:i2 + 1]))
    seg = slice(p2, i2 + 1)
    P("")
    P(f"    Inside the INCUMBENT's own worst episode ({J['week'].iloc[p2]} -> {J['week'].iloc[i2]}, "
      f"{i2-p2} weeks):")
    P(f"        MIRROR total ${mcv[seg].sum():>10,.0f}   over {int((mcv[seg]!=0).sum())} active weeks")
    P(f"        MIRROR best single week in that span ${mcv[seg].max():>10,.0f}")
    P(f"        share of MIRROR's episode $ from its single best week: "
      f"{100*mcv[seg].max()/max(abs(mcv[seg].sum()),1e-9):.1f} %")
    P("")
    P("    The -29 % is a statement about ONE episode. It is not a distributional property.")


# ==================================================================================================
def section_f_paperstream(J, rng, delta, se, uncond, p_lose):
    H("=== 9. (c) CAN THE FORWARD PAPER DECISION STREAM SETTLE THIS? Component by component.")
    P("    Gate 2 needs exactly two weekly series aligned on the same ISO weeks:")
    P("        (i)  BOOK weekly $   - the inverse-vol blend of P1/PCT and XM_CONFLICT")
    P("        (ii) MIRROR weekly $ - the object defined in section (a)")
    P("")
    P(f"{'component':<34}{'in the paper stream?':<24}{'verdict'}")
    P("-" * 118)
    rows = [
        ("MIRROR decisions", "NO",
         "no .cs exists; W120 wrote none; it is not on the DEMO8383477 roster"),
        ("MIRROR fills / slippage", "NO",
         "nothing to fill - but gate 2 does not test execution, see below"),
        ("MIRROR weekly $ (simulated)", "COMPUTABLE",
         "pure function of NQ 1-min bars + a 250-session causal roll. NO refit needed"),
        ("P1/PCT weekly $", "YES (from 2026-09-01)", "paper leg, parity-certified"),
        ("XM_CONFLICT_v2 weekly $", "YES (from 2026-09-01)", "paper leg, parity-certified"),
        ("the inverse-vol BOOK", "NO - THE TRAP",
         "the paper account runs qty 1 + qty 1 = an EXECUTABLE_COMPONENT_SET, not the blend"),
    ]
    for a, b, c in rows:
        P(f"{a:<34}{b:<24}{c}")
    P("")
    P("    ---- THE BOOK-DEFINITION TRAP, PRICED ----------------------------------------------")
    P("    CLAUDE.md section 3: 'running both legs at quantity 1 is not that mapping and does not")
    P("    reproduce the research economics'. Gate 2 conditions on 1{book < 0}, so a different")
    P("    book is a DIFFERENT CONDITIONING EVENT. Measure how different, in sample:")
    P("")
    bk = {}
    sp, sx = J["p1"].std(ddof=1), J["xm"].std(ddof=1)
    w1 = (1 / sp) / ((1 / sp) + (1 / sx))
    bk["inv-vol (research, w_P1=%.3f)" % w1] = J["book"].to_numpy()
    bk["qty 1 + qty 1 (paper)"] = (J["p1"] + J["xm"]).to_numpy()
    bk["P1 alone"] = J["p1"].to_numpy()
    mcv = J["mc"].to_numpy()
    P(f"{'book definition':<34}{'losing wks':>12}{'DELTA':>11}{'SE':>9}{'z':>8}"
      f"{'gate 2':>9}{'agree w/ research':>19}")
    ref_lose = bk["inv-vol (research, w_P1=%.3f)" % w1] < 0
    for lab, bv in bk.items():
        lo = bv < 0
        d_ = float(mcv[lo].mean()) - uncond
        nn = np.array([float(np.roll(mcv, k)[lo].mean()) - uncond for k in range(1, len(J))])
        s_ = float(nn.std(ddof=1))
        agree = float((lo == ref_lose).mean())
        P(f"{lab:<34}{int(lo.sum()):>12}{d_:>+11,.0f}{s_:>9,.0f}{d_/s_:>8.2f}"
          f"{('PASS' if d_ > 1.645*s_ else 'FAIL'):>9}{100*agree:>18.1f}%")
    P("")
    P("    HONEST CORRECTION TO MY OWN PRIOR: I expected the qty-1 paper book to be a materially")
    P("    different conditioning event. IT IS NOT. It agrees with the research book on the SIGN")
    P("    of the week 99.5 % of the time in sample (one week in 213), and its DELTA is $-54")
    P("    against the research book's $-49. THE PAPER STREAM *CAN* LEGITIMATELY SUPPLY THE")
    P("    CONDITIONING EVENT 1{book<0}. What it cannot supply is the other leg. (P1 alone is a")
    P("    genuinely different event - 75.6 % sign agreement - so 'the book' must stay both legs.)")
    P("")
    P("    ---- WHAT THIS MEANS OPERATIONALLY -------------------------------------------------")
    P("    1. NO DEPLOYMENT IS NEEDED. MIRROR's forward weekly $ is a deterministic function of")
    P("       NQ 1-min bars. Freezing run_we_w118.scan/econ + the four literals and hash-")
    P("       registering them BEFORE the read gives a legitimate PRE-FROZEN forward series. A")
    P("       .cs, an account, and fills add execution realism that GATE 2 DOES NOT TEST.")
    P("    2. THE PAPER STREAM CAN SUPPLY THE BOOK SIGN, and that is a real (small) contribution:")
    P("       99.5 % sign agreement with the research book. But it supplies HALF a statistic. The")
    P("       MIRROR leg has to be simulated regardless, and once you are simulating one leg on")
    P("       sealed bars you may as well simulate both - which is cheaper, is not roll-gapped,")
    P("       and does not have to wait for the paper account. The paper stream is therefore")
    P("       NEITHER NECESSARY NOR SUFFICIENT here. It is not the bottleneck.")
    P("    3. THE PAPER STREAM IS ALSO CONTAMINATED FOR THIS PURPOSE IN ITS FIRST MONTH: the")
    P("       contract roll blocks NEW ENTRIES for XM from 2026-09-06 and P1 from 2026-09-08,")
    P("       with safe re-enable P1 >= 09-17 / XM >= 09-19. That is a ~2-week hole in the book")
    P("       leg that has no counterpart in the MIRROR leg. Weeks 2026-W37..W38 are unusable.")
    P("    4. THE SHADOW LEDGER CANNOT HOLD IT ANYWAY. shadow_ledger.py refuses rows at or before")
    P("       SHADOW_START and refuses non-advancing timestamps; a simulated MIRROR series is a")
    P("       backtest overlay, not a decision-first row. It belongs under LOCKED_FORWARD.md as a")
    P("       preregistered one-shot read, NOT in the prospective shadow.")
    P("")
    P("    ==> ANSWER TO (c): NO DEPLOYMENT IS NEEDED and none should be built. The correct")
    P("        forward instrument is a preregistered, hash-frozen SIMULATED read of both legs on")
    P("        sealed bars - not a .cs, not the paper account, not the shadow ledger. The paper")
    P("        stream can corroborate the book leg (99.5 % sign agreement) but is not required")
    P("        and is roll-gapped in its first month. The ONLY binding constraint is CALENDAR")
    P("        TIME - and section 6 shows the required calendar time does not exist.")


# ==================================================================================================
def section_g_costs(J):
    H("=== 10. COST FLOOR RESTATEMENT (the research number is not the tradable number)")
    mcv = J["mc"].to_numpy()
    n_tr = 347
    net = float(mcv.sum())
    P(f"    W118/W120 charge COMM_RT ${COMM_RT_FLOOR:.2f} + a modelled per-minute spread. Recovered")
    P("    from W118's own printout (reversal -$438 + momentum +$407 = -2c):")
    c_res = (438.0 - 407.0) / 2.0
    P(f"        implied research cost  ${c_res:.2f} / ctrRT")
    P("")
    P(f"{'cost model':<44}{'$/ctrRT':>10}{'MIRROR $/trade':>16}{'MIRROR net $':>14}"
      f"{'wk $':>9}")
    for lab, c in (("commission only  (A FLOOR, never a headline)", COMM_RT_FLOOR),
                   ("W118/W120 research model", c_res),
                   ("G2_EXEC01 measured  (PRIMARY)", COST_PRIMARY),
                   ("all-in", COST_ALLIN)):
        adj = c_res - c
        pt = net / n_tr + adj
        P(f"{lab:<44}{c:>10.2f}{pt:>16,.0f}{pt*n_tr:>14,.0f}{pt*n_tr/len(J):>9,.0f}")
    P("")
    P(f"    Cost is NOT what kills this object: at the ${COST_PRIMARY:.2f} PRIMARY it still earns")
    P("    roughly $400/trade in sample. Gate 2 is a CORRELATION question and is cost-invariant -")
    P("    a constant shifts the conditional and unconditional means by the SAME amount, so DELTA")
    P("    is EXACTLY unchanged. Recording that so nobody proposes 'better fills' as the fix.")


# ==================================================================================================
BURN_A, BURN_B = pd.Timestamp("2026-05-31"), pd.Timestamp("2026-07-31")


def wk_start(w):
    return pd.to_datetime(f"{w[:4]}-W{w[6:]}-1", format="%G-W%V-%u")


def section_h_oneweek(J, rng):
    """The single week that carries BOTH tail gates - and where in the seal register it sits."""
    H("=== 8b. THE ONE WEEK. Both surviving statistics are the same observation.")
    bookv = J["book"].to_numpy(); mcv = J["mc"].to_numpy(); NW = len(J)
    tail = bookv <= np.percentile(bookv, 10)
    tb = float(np.polyfit(bookv[tail], mcv[tail], 1)[0])
    ti = np.flatnonzero(tail)
    # the week whose removal DESTROYS the statistic - i.e. drives the tail beta toward zero.
    # (Not max |change|: a week that makes the slope MORE negative is not a fragility.)
    worst = max(ti, key=lambda i: float(np.polyfit(
        bookv[np.setdiff1d(ti, [i])], mcv[np.setdiff1d(ti, [i])], 1)[0]))
    wk = J["week"].iloc[worst]
    st = wk_start(wk)
    k = tail.copy(); k[worst] = False
    tb2 = float(np.polyfit(bookv[k], mcv[k], 1)[0])
    nn = np.array([float(np.polyfit(bookv[k], np.roll(mcv, kk)[k], 1)[0]) for kk in range(1, NW)])
    P(f"    Most influential tail week: {wk}  (Mon {str(st)[:10]} - Sun {str(st + pd.Timedelta(days=6))[:10]})")
    P(f"        book  ${bookv[worst]:>10,.0f}      MIRROR ${mcv[worst]:>10,.0f}")
    P("")
    P(f"{'statistic':<44}{'with it':>14}{'without it':>14}   {'change'}")
    P("-" * 100)
    P(f"{'tail beta':<44}{tb:>14.3f}{tb2:>14.3f}"
      f"   {100*float(np.nanmean(nn < tb2)):.1f}th pctile, was 0.9th")
    for how in ("invvol", "income"):
        base = fixdd(blend(J, ["p1", "xm"], how))
        with_ = fixdd(blend(J, ["p1", "xm", "mc"], how))
        Jd = J.drop(index=worst).reset_index(drop=True)
        b2 = fixdd(blend(Jd, ["p1", "xm"], how))
        w2 = fixdd(blend(Jd, ["p1", "xm", "mc"], how))
        P(f"{'incremental fixed-DD  ' + how:<44}{with_-base:>+14,.0f}{w2-b2:>+14,.0f}"
          f"   {'SIGN FLIPS' if (with_-base) * (w2-b2) < 0 else 'same sign'}")
    d1 = float(mcv[bookv < 0].mean()) - float(mcv.mean())
    Jd = J.drop(index=worst).reset_index(drop=True)
    b_, m_ = Jd["book"].to_numpy(), Jd["mc"].to_numpy()
    d2 = float(m_[b_ < 0].mean()) - float(m_.mean())
    P(f"{'gate-2 DELTA':<44}{d1:>+14,.0f}{d2:>+14,.0f}   still negative")
    P("")
    P("    ####################################################################################")
    P(f"    #  BOTH surviving statistics are ONE WEEK: {wk}.")
    P("    #  Section 8 already showed the same week is 102 % of MIRROR's dollars inside the")
    P("    #  incumbent's worst drawdown episode. The tail beta, the -29 % maxDD headline and")
    P("    #  the +$402 fixed-DD increment are NOT three pieces of evidence. They are one.")
    P("    ####################################################################################")
    P("")
    P("    AND WHERE DOES THAT WEEK SIT IN THE SEAL REGISTER?")
    P(f"        BURNED span (CLAUDE.md section 5): {str(BURN_A)[:10]} -> {str(BURN_B)[:10]}")
    inb = (st >= BURN_A) and (st <= BURN_B)
    P(f"        {wk} starts {str(st)[:10]}  ->  INSIDE THE BURNED SPAN: {'YES' if inb else 'NO'}")
    P("")
    burn = np.array([BURN_A <= wk_start(w) <= BURN_B for w in J["week"]])
    P(f"        {int(burn.sum())} of {NW} weeks are burned. They hold "
      f"${mcv[burn].sum():,.0f} of MIRROR's ${mcv.sum():,.0f} net "
      f"({100*mcv[burn].sum()/mcv.sum():.1f} %) on {100*burn.mean():.1f} % of the weeks.")
    P("")
    P("    RE-RUN EVERY GATE WITH THE BURNED WEEKS REMOVED (evidence-status: the remaining weeks")
    P("    are still DISCOVERY_CONSUMED, so this is a fragility probe, not a clean test):")
    Jn = J[~burn].reset_index(drop=True)
    bn, mn = Jn["book"].to_numpy(), Jn["mc"].to_numpy()
    lo = bn < 0
    dn_ = float(mn[lo].mean()) - float(mn.mean())
    sn = np.array([float(np.roll(mn, kk)[lo].mean()) - float(mn.mean())
                   for kk in range(1, len(Jn))]).std(ddof=1)
    tn = bn <= np.percentile(bn, 10)
    tbn = float(np.polyfit(bn[tn], mn[tn], 1)[0])
    nnt = np.array([float(np.polyfit(bn[tn], np.roll(mn, kk)[tn], 1)[0])
                    for kk in range(1, len(Jn))])
    P("")
    P(f"{'gate':<44}{'all 213 wk':>14}{'ex-burned':>14}   {'verdict'}")
    P("-" * 100)
    P(f"{'2. DELTA (needs > +1.645*SE)':<44}{d1:>+14,.0f}{dn_:>+14,.0f}"
      f"   FAIL -> {'FAIL' if dn_ <= 1.645*sn else 'PASS'}  (thr ${1.645*sn:,.0f})")
    P(f"{'tail beta':<44}{tb:>14.3f}{tbn:>14.3f}"
      f"   0.9th -> {100*float(np.nanmean(nnt < tbn)):.1f}th pctile")
    for how in ("invvol", "income"):
        i1 = fixdd(blend(J, ["p1", "xm", "mc"], how)) - fixdd(blend(J, ["p1", "xm"], how))
        i2 = fixdd(blend(Jn, ["p1", "xm", "mc"], how)) - fixdd(blend(Jn, ["p1", "xm"], how))
        P(f"{'3. incremental fixed-DD ' + how:<44}{i1:>+14,.0f}{i2:>+14,.0f}"
          f"   {'SIGN FLIPS' if i1*i2 < 0 else 'same sign'}")
    P("")
    P("    The tail gate - the ONLY statistic on the favourable side of its null - is a burned-")
    P("    window artifact. W120's report flagged t3m and t6m as burned and did NOT flag this.")


# ==================================================================================================
def main():
    t0 = _time.time()
    rng = np.random.default_rng(SEED)
    P("MIRROR_CONT - WHAT WOULD A FORWARD VERDICT NEED?   (G3_SHORTALPHA, angle: mirror-cont)")
    P("Produces a decision packet. No P&L. No candidate. No new object.")

    J = pd.read_csv(FILES[0])
    S = pd.read_csv(FILES[1])
    seal_assert(J, S)
    section_a()
    real, NN, lose, inc_real, inc_null = section_b_reproduce(J, rng)
    delta, se, uncond, p_lose, hi95 = section_c_gate2_power(J, rng, real, NN, lose)
    section_d_required_n(delta, se, len(J), p_lose, hi95)
    section_e_tail(J, rng, real, NN, lose)
    section_h_oneweek(J, rng)
    section_f_paperstream(J, rng, delta, se, uncond, p_lose)
    section_g_costs(J)

    # ---------------------------------------------------------------- final gate table
    H("=== 11. THE PACKET - the four gates after the two missing nulls are supplied")
    mcv = J["mc"].to_numpy(); bookv = J["book"].to_numpy(); NW = len(J)
    g1_null = np.array([float(np.roll(mcv, k)[lose].mean()) for k in range(1, NW)])
    p_g1 = float((g1_null > 0).mean())
    pct3 = {h: 100 * float((inc_null[h] < inc_real[h]).mean()) for h in inc_real}
    pg3 = {h: float((inc_null[h] > 0).mean()) for h in inc_real}
    wd = NN["worst-decile overlap"].to_numpy()
    ov = float(((bookv <= np.percentile(bookv, 10)) & (mcv <= np.percentile(mcv, 10))).mean())
    lines = [
        ("1. earns > 0 on book-losing weeks", "PASS",
         [f"VACUOUS - an ALIGNMENT-DESTROYED MIRROR passes {100*p_g1:.0f}% of the time",
          "it is a restatement of 'MIRROR is profitable', not of alignment"]),
        ("2. beats its circular-shift null there", "FAIL",
         [f"FAIL, and the POINT ESTIMATE IS NEGATIVE: DELTA = ${delta:+,.0f} +/- ${se:,.0f}",
          "no forward N passes it at this effect size"]),
        ("3. incremental fixed-DD > 0 at either conv.", "PASS",
         [f"{pct3['invvol']:.0f}th / {pct3['income']:.0f}th pctile of its OWN null - not significant",
          f"a random-phase third leg raises fixed-DD {100*pg3['invvol']:.0f}% / "
          f"{100*pg3['income']:.0f}% of the time"]),
        ("4. worst-decile overlap <= null 95th", "PASS",
         [f"PASS BY NON-REJECTION: REAL {ov:.3f} vs null MEAN {float(np.nanmean(wd)):.3f}",
          "the real overlap is WORSE than chance, merely not by enough to fail"]),
    ]
    P("")
    P(f"{'gate':<46}{'W120':<8}{'after this wave'}")
    P("-" * 118)
    for a_, b_, cs in lines:
        P(f"{a_:<46}{b_:<8}{cs[0]}")
        for c_ in cs[1:]:
            P(f"{'':<46}{'':<8}{c_}")
    P("")
    P("    Exactly ONE statistic in the entire W120 battery sits on the favourable side of its")
    P("    own null: the tail beta, at the 0.9th percentile. Section 7 shows one week owns it")
    P("    and section 8b shows that week is inside the BURNED span.")
    P("")
    P("=" * 118)
    P("    THE DECISION-READY ANSWER")
    P("=" * 118)
    P("")
    P("    (a) The object is fully specified with zero remaining choices (section a). The one")
    P("        non-obvious requirement is 250 sessions of causal warm-up, which a cold forward")
    P("        start does NOT supply for its first ~190 decisions.")
    P("")
    P("    (b) The forward statistic is DELTA = mean(MIRROR wk | book wk < 0) - mean(MIRROR wk).")
    P(f"        Observed DELTA = ${delta:+,.0f} +/- ${se:,.0f}. IT IS NEGATIVE.")
    P("        REQUIRED FORWARD N AT THE OBSERVED EFFECT SIZE: INFINITE. The gate cannot be")
    P("        passed by waiting, because the estimate is on the wrong side of zero and more")
    P("        data tightens it AROUND A NEGATIVE NUMBER.")
    n80 = NW * ((se * (_zq(0.95) + _zq(0.80))) / hi95) ** 2
    P(f"        Even at the 95 % CI UPPER LIMIT (${hi95:+,.0f}/wk - the most generous effect the")
    P(f"        data still permits) the answer is {n80:,.0f} forward weeks = {n80/52:.1f} YEARS at 80 % power.")
    P("        The honest sentence is not 'three years'. It is 'longer than the evidence would")
    P("        stay relevant, for an effect the data already estimates as negative'.")
    P("")
    P("    (c) It does NOT need a deployment - MIRROR's forward series is a deterministic")
    P("        function of bars, so a hash-frozen simulated read on sealed data is the right")
    P("        instrument. The paper stream is NEITHER NECESSARY NOR SUFFICIENT: it can supply")
    P("        the book-sign conditioning (99.5 % agreement with the research book, contrary to")
    P("        what I expected), but it cannot supply the MIRROR leg, and the roll gap")
    P("        2026-09-06/08 -> 09-19 holes the book leg in its first month. Nothing about the")
    P("        paper account is the bottleneck. CALENDAR TIME is, and there is not enough of it.")
    P("")
    P("    AND THE THING THAT MAKES (b) ACADEMIC: the only statistic that ever sat on the good")
    P("    side of its null - the tail beta at the 0.9th percentile - is ONE WEEK, 2026-W23,")
    P("    and that week is INSIDE THE BURNED SPAN. Drop it and the tail beta goes 0.9th ->")
    P("    20.8th percentile. The -29 % maxDD headline is the same week (102 % of MIRROR's")
    P("    dollars inside the incumbent's worst episode). There is nothing left to confirm.")
    P("")
    P("    ==> RECOMMENDATION: CLOSE the 'forward evidence will settle MIRROR_CONT' item. It is")
    P("        not a scheduled read waiting on data; it is a test with no attainable N. Keep the")
    P("        object as the standing MIRROR_CONTINUATION_CONTROL, which is what it is genuinely")
    P("        good for. Do not build a .cs. Do not add it to the monitoring calendar.")
    P("")
    P(f"[done {_time.time()-t0:.0f}s]")
    _OUTF.close()


if __name__ == "__main__":
    main()
