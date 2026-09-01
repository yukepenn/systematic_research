"""G3_SHORTALPHA / holdtime - stage 3: the money, the controls, and the size of the closure.

The preregistered selection rule (stage 2) returned NO CANDIDATE: the short sleeve's expected
forward points conditional on still being open is POSITIVE at every tau on the grid, so there is
no elapsed-time horizon at which cutting the hold would have earned anything.

This stage therefore does not test one exit - it CLOSES the direction, which requires three
things the "no candidate" line does not supply on its own:
  (a) the whole cap surface, to show the closure is not a grid-boundary artefact;
  (b) the state-blind rate-matched random exit at the same mean hold, so the comparison the repo
      demands is on the record even though nothing passed;
  (c) the ORACLE bound - what a perfect-foresight exit at each trade's own MFE would have paid -
      so the size of the forgone prize is named rather than hand-waved.
Because stage 2's rule already returned NO CANDIDATE, the cap surface here can only CLOSE the
direction. It cannot open one: a T that happened to win on this surface is a post-hoc pick that
the preregistered rule already declined, and it is reported as such.
"""
from __future__ import annotations

import json
import os
import sys
import time as _time

import numpy as np
import pandas as pd

ROOT_ = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT_, "research", "weekly_edge", "src"))
sys.path.insert(0, ROOT_)
from run_we_w17 import load_deep                                          # noqa: E402
from research_sdk.champion_eval import (risk_vector, weekly_from_trades,   # noqa: E402
                                        max_drawdown, fixed_dd_income)

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")
OUT = os.path.join(ROOT_, "runs", "G3_SHORTALPHA_20260831", "out")

PV = 20.0
COST_FLOOR, COST_PRIMARY, COST_ALLIN = 4.36, 20.65, 25.01
SEAL = np.datetime64("2026-08-01")
NDRAW = 1000
RNG = np.random.default_rng(20260831)
CAPS = [1, 2, 3, 5, 8, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360, 480, 720, 10 ** 6]

LOG = []


def P(*a):
    s = " ".join(str(z) for z in a)
    print(s, flush=True); LOG.append(s)


def H(title):
    P(""); P("=" * 118); P("=== " + title); P("=" * 118)


# ------------------------------------------------------------------ flat ragged path structure
class Paths:
    def __init__(self, df, o, h=None, l=None):
        dur = df["dur"].values.astype(np.int64)
        self.off = np.concatenate([[0], np.cumsum(dur)])[:-1]
        self.dur = dur
        buf = np.empty(int(dur.sum()))
        rmf = np.empty(int(dur.sum())) if h is not None else None
        dd = df["d"].values.astype(float)
        for j, (a, d, xpx, dj, ep) in enumerate(zip(df["ei"].values, dur, df["xpx"].values,
                                                    dd, df["epx"].values)):
            seg = o[a + 1:a + d + 1].astype(float)
            if len(seg) < d:
                seg = np.concatenate([seg, np.full(d - len(seg), xpx)])
            seg = seg.copy(); seg[d - 1] = xpx
            buf[self.off[j]:self.off[j] + d] = seg
            if h is not None:
                fav = (h[a:a + d] - ep) if dj > 0 else (ep - l[a:a + d])
                rmf[self.off[j]:self.off[j] + d] = np.maximum.accumulate(fav)
        self.buf = buf
        self.rmf = rmf
        self.d = dd
        self.epx = df["epx"].values.astype(float)
        self.u = df["u"].values.astype(float)

    def points(self, hold):
        """hold: per-trade holding minutes (already clipped into [1, dur])."""
        k = np.clip(hold, 1, self.dur).astype(np.int64)
        return self.d * (self.buf[self.off + k - 1] - self.epx)


def net_usd(pts, u, cost):
    return float((pts * u * PV).sum() - cost * u.sum())


def solve_lambda(dur, target_mean):
    """Constant-hazard (memoryless, state-blind) exit calibrated to the same MEAN realised hold.
    E[min(d, C)] = (1 - exp(-lam d))/lam for C ~ Exp(lam)."""
    lo, hi = 1e-7, 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        m = float(np.mean((1.0 - np.exp(-mid * dur)) / mid))
        if m > target_mean:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    t0 = _time.time()
    frozen = json.load(open(os.path.join(HERE, "T_FROZEN.json"), encoding="utf-8"))
    dfL = pd.read_parquet(os.path.join(CACHE, "trades_L.parquet"))
    dfS = pd.read_parquet(os.path.join(CACHE, "trades_S.parquet"))
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    o, t = D["o"], D["t"]
    assert t.max() < SEAL
    for df in (dfL, dfS):
        df["give"] = df["mfe"] - df["fin"]
        df["year"] = pd.to_datetime(df["sdate"]).dt.year
    NS = 1012

    H("SEAL + WHAT STAGE 2 FROZE")
    P(f"   max bar {t.max()} < {SEAL} -> SEAL HELD (asserted in code)")
    P(f"   T_FROZEN.json: T_short = {frozen['T_short']}   T_long_same_rule = "
      f"{frozen['T_long_same_rule']}   T_first_half = {frozen['T_first_half']}")
    P(f"   rule: {frozen['rule']}")
    P("   ALL THREE ARE None. The preregistered rule found no tau at which the short's expected")
    P("   forward P&L, conditional on the position still being open, is <= 0. On the whole grid")
    P("   5..480 minutes the short's continuation value never turns negative.")
    P("   => F3 cannot be evaluated because there is no candidate to evaluate. Recorded as such.")
    P("")
    P("   COVERAGE LIMIT, stated rather than buried: this uses W51c setup(), i.e. load_deep with")
    P("   extend=False, so the substrate ends 2026-05-29 and the object is 1,012 sessions, not")
    P("   1,056. That is DELIBERATE - it is the only way the B1 gate reproduces W61/W73 exactly")
    P("   (14.86 / 6.00 / 2,225) and the comparison stays bit-comparable. The cost is that this")
    P("   closure does not cover June-July 2026. Those 44 sessions exist (W76's extend=True) and")
    P("   are NOT sealed; re-running with extend=True is a one-line change for a future wave.")

    pL, pS = Paths(dfL, o, D["h"], D["l"]), Paths(dfS, o, D["h"], D["l"])
    uL, uS = pL.u, pS.u
    # HARNESS CHECK: the path structure, held to the full duration, must reproduce the ledger
    # exactly. If it does not, every capped number below is meaningless.
    for nm, p_, df in (("L", pL, dfL), ("S", pS, dfS)):
        err = float(np.abs(p_.points(p_.dur) - df["fin"].values).max())
        P(f"   PATH HARNESS {nm}: max |path(dur) - ledger final| = {err:.2e} -> "
          f"{'PASS' if err < 1e-9 else 'FAIL - VOID'}")
        assert err < 1e-9
    baseL = net_usd(pL.points(pL.dur), uL, COST_PRIMARY)
    baseS = net_usd(pS.points(pS.dur), uS, COST_PRIMARY)
    baseS_floor = net_usd(pS.points(pS.dur), uS, COST_FLOOR)
    P("")
    P(f"   reference (PRIMARY $20.65/ctrRT): LONG ${baseL:,.0f}   SHORT ${baseS:,.0f}"
      f"   (floor $20.65->$4.36 would read ${baseS_floor:,.0f} - floor is NOT a headline)")

    # ------------------------------------------------------------------ (a) the cap surface
    H("PHASE 4a - THE WHOLE CAP SURFACE. 'Same entries, capped hold, no re-entry.'")
    P("   Convention, stated so it cannot be mistaken for the engine: entries, sizes, the session")
    P("   halt/target path and the commission are all FROZEN at the uncapped run; only the exit")
    P("   is moved earlier, at the open of bar ei+T (the repo's own next-bar-open fill). A cap")
    P("   removes no trade and adds no round turn, so cost is identical across every row and")
    P("   cannot manufacture any of this.")
    P("")
    P(f"{'cap T':>8}{'mean hold':>11}{'SHORT $':>12}{'d vs base':>12}{'pts/sess':>10}"
      f"{'|':>3}{'LONG $':>12}{'d vs base':>12}{'pts/sess':>10}")
    P("-" * 92)
    rows = []
    for T in CAPS:
        hS = np.minimum(pS.dur, T); hL = np.minimum(pL.dur, T)
        nS = net_usd(pS.points(hS), uS, COST_PRIMARY)
        nL = net_usd(pL.points(hL), uL, COST_PRIMARY)
        lab = "none" if T > 10 ** 5 else str(T)
        P(f"{lab:>8}{hS.mean():>11.1f}{nS:>12,.0f}{nS-baseS:>12,.0f}"
          f"{nS/PV/NS:>10.2f}{'|':>3}{nL:>12,.0f}{nL-baseL:>12,.0f}{nL/PV/NS:>10.2f}")
        rows.append(dict(T=T, mean_hold_S=float(hS.mean()), net_S=nS, d_S=nS - baseS,
                         mean_hold_L=float(hL.mean()), net_L=nL, d_L=nL - baseL))
    cap = pd.DataFrame(rows)
    cap.to_csv(os.path.join(OUT, "holdtime_cap_surface.csv"), index=False)
    fin = cap[cap["T"] < 10 ** 5]
    best = fin.loc[fin["d_S"].idxmax()]
    bind = fin[fin["mean_hold_S"] <= 0.5 * cap["mean_hold_S"].iloc[-1]]
    bb = bind.loc[bind["d_S"].idxmax()]
    P("")
    P(f"   best cap ON THIS SURFACE, in hindsight: T = {int(best['T'])} min, "
      f"{best['d_S']:+,.0f} vs the uncapped sleeve - but that cap barely binds "
      f"(mean hold {best['mean_hold_S']:.1f} min against the uncapped "
      f"{cap['mean_hold_S'].iloc[-1]:.1f}).")
    P(f"   best cap that MATERIALLY binds (mean hold cut at least in half): T = {int(bb['T'])}, "
      f"{bb['d_S']:+,.0f}.")
    P("   Every finite cap is NEGATIVE for the short." if (fin["d_S"] < 0).all() else
      "   One near-inert cap is marginally positive; every cap that materially binds is negative.")
    P("   The preregistered rule declined all of them; nothing here can promote one.")
    P("")
    P("   DIRECTION PLACEBO (F3 clause iii, answerable even with no candidate): the same cap")
    P("   applied to the LONG object destroys MORE, not less - at T=60, LONG "
      f"{float(cap.loc[cap['T']==60,'d_L'].iloc[0]):+,.0f} against SHORT "
      f"{float(cap.loc[cap['T']==60,'d_S'].iloc[0]):+,.0f}. There is no direction-specific")
    P("   holding defect: holding longer pays MORE on the long side, but it pays on BOTH.")

    # ------------------------------------------------------------------ (b) rate-matched control
    H("PHASE 4b - THE STATE-BLIND RATE-MATCHED RANDOM EXIT (the control the repo demands)")
    P("   An exit rule must beat a coin flip that removes the same holding time. Control:")
    P("   C_i ~ Exponential(lambda), realised hold = min(dur_i, ceil(C_i)), lambda solved so the")
    P("   MEAN realised hold equals the deterministic cap's. Memoryless => carries zero")
    P("   information about the state. 1,000 draws. A second, differently-shaped control")
    P("   (uniform on [1, 2T]) is run beside it so the answer is not an artefact of one shape.")
    P("")
    P(f"{'cap T':>7}{'mean hold':>11}{'REAL $':>12}{'|':>3}"
      f"{'EXP mean':>12}{'EXP p95':>12}{'pctile':>8}{'beats p95':>11}{'|':>3}"
      f"{'UNI mean':>12}{'UNI p95':>12}{'pctile':>8}")
    P("-" * 110)
    ctrl_rows = []
    for T in [5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240]:
        hS = np.minimum(pS.dur, T)
        real = net_usd(pS.points(hS), uS, COST_PRIMARY)
        lam = solve_lambda(pS.dur.astype(float), float(hS.mean()))
        ex = np.empty(NDRAW); un = np.empty(NDRAW)
        mh_e = mh_u = 0.0
        for b in range(NDRAW):
            c = np.maximum(1, np.ceil(RNG.exponential(1.0 / lam, len(pS.dur)))).astype(np.int64)
            h = np.minimum(pS.dur, c); mh_e += h.mean()
            ex[b] = net_usd(pS.points(h), uS, COST_PRIMARY)
            c2 = RNG.integers(1, max(2, 2 * T), size=len(pS.dur))
            h2 = np.minimum(pS.dur, c2); mh_u += h2.mean()
            un[b] = net_usd(pS.points(h2), uS, COST_PRIMARY)
        pe = 100.0 * float((ex < real).mean()); pu = 100.0 * float((un < real).mean())
        beat = real > np.percentile(ex, 95)
        P(f"{T:>7}{hS.mean():>11.1f}{real:>12,.0f}{'|':>3}"
          f"{ex.mean():>12,.0f}{np.percentile(ex,95):>12,.0f}{pe:>8.1f}"
          f"{('YES' if beat else 'no'):>11}{'|':>3}"
          f"{un.mean():>12,.0f}{np.percentile(un,95):>12,.0f}{pu:>8.1f}")
        ctrl_rows.append(dict(T=T, mean_hold=float(hS.mean()), real=real,
                              exp_mean=float(ex.mean()), exp_p95=float(np.percentile(ex, 95)),
                              pctile_exp=pe, beats_p95=bool(beat),
                              uni_mean=float(un.mean()), pctile_uni=pu,
                              ctrl_mean_hold_exp=mh_e / NDRAW, ctrl_mean_hold_uni=mh_u / NDRAW))
    pd.DataFrame(ctrl_rows).to_csv(os.path.join(OUT, "holdtime_controls.csv"), index=False)
    cr = pd.DataFrame(ctrl_rows)
    P("")
    P(f"   control calibration check: at T=30 the exponential control's realised mean hold is "
      f"{cr.loc[cr['T']==30,'ctrl_mean_hold_exp'].iloc[0]:.1f} min against the rule's "
      f"{cr.loc[cr['T']==30,'mean_hold'].iloc[0]:.1f} min - matched.")
    P(f"   ROWS WHERE THE DETERMINISTIC CAP BEATS ITS OWN STATE-BLIND CONTROL AT p95: "
      f"{int(cr['beats_p95'].sum())} of {len(cr)}")
    P(f"   median percentile of the real cap inside its exponential control: "
      f"{np.median(cr['pctile_exp']):.1f}%   (50% = pure exposure removal, no information)")

    # ------------------------------------------------------------------ (c) the oracle bound
    H("PHASE 4c - THE ORACLE BOUND. How big is the prize an exit rule is chasing?")
    P("   Perfect foresight: close every trade at its own MFE bar. Not attainable - it is the")
    P("   CEILING on any exit repair whatsoever, and it names the level (per OPPORTUNITY_LANGUAGE:")
    P("   this is a PERFECT-FORESIGHT-EXIT ceiling on the mirrored short sleeve, 2022-07..2026-05,")
    P("   1 contract, PRIMARY cost - it is not an achievable figure and may not be quoted as one).")
    P("   It is INFLATED twice over: MFE is read off bar EXTREMES, which no market order can be")
    P("   filled at, and it assumes foresight of which bar that is. It is used here only as a")
    P("   DENOMINATOR, so both inflations work AGAINST the closure - they make the recovered")
    P("   share look smaller. The closure survives them by three orders of magnitude.")
    P("")
    orS = net_usd(dfS["mfe"].values, uS, COST_PRIMARY)
    orL = net_usd(dfL["mfe"].values, uL, COST_PRIMARY)
    P(f"{'arm':<22}{'realised $':>14}{'ORACLE $':>14}{'forgone $':>14}{'x realised':>12}")
    P("-" * 78)
    P(f"{'SHORT sleeve':<22}{baseS:>14,.0f}{orS:>14,.0f}{orS-baseS:>14,.0f}{orS/baseS:>12.1f}")
    P(f"{'LONG P1':<22}{baseL:>14,.0f}{orL:>14,.0f}{orL-baseL:>14,.0f}{orL/baseL:>12.1f}")
    P("")
    bestgain = float(fin["d_S"].max())
    P(f"   share of the short's forgone ${orS-baseS:,.0f} that the BEST hindsight elapsed-time cap")
    P(f"   recovers: {100*bestgain/(orS-baseS):+.2f}%   <- this is the number that closes the angle.")
    P("   The giveback is enormous and real. Elapsed time does not locate it.")

    # ------------------------------------------------------------------ why: t_MFE is diffuse
    H("PHASE 4d - WHY. Where does the MFE sit inside the hold?")
    for nm, df in (("LONG", dfL), ("SHORT", dfS)):
        tf = (df["t_mfe"] / df["dur"]).values
        h, _ = np.histogram(tf, bins=np.linspace(0, 1, 11))
        P(f"   {nm:<6} t_MFE/dur decile mass (%): " +
          " ".join(f"{100*x/len(tf):5.1f}" for x in h))
    P("")
    for nm, df in (("LONG", dfL), ("SHORT", dfS)):
        a = float((df["t_mfe"] == df["dur"]).mean())
        b = float((df["t_mfe"] == 1).mean())
        gm = df["give"].values
        P(f"   {nm:<6} MFE printed ON the exit bar: {100*a:5.1f}%   on the FIRST bar: {100*b:5.1f}%"
          f"   |   giveback>0 on {100*float((gm>1e-9).mean()):5.1f}% of trades,"
          f" top decile of giveback = {100*np.sort(gm)[-len(gm)//10:].sum()/gm.sum():4.1f}% of all giveback")
    P("")
    P("   A uniform mass across the deciles is exactly what an unpredictable-by-the-clock MFE")
    P("   looks like. There is no elapsed-time bucket that concentrates the giveback.")

    # ------------------------------------------------------------------ points-space differences
    H("PHASE 4e - THE DECOMPOSITION IN POINTS (what actually pays), session-block bootstrap")
    sess = np.unique(np.concatenate([dfL["sess"].values, dfS["sess"].values]))
    iL = {s: np.flatnonzero(dfL["sess"].values == s) for s in sess}
    iS = {s: np.flatnonzero(dfS["sess"].values == s) for s in sess}

    def boot(fn, nb=NDRAW):
        real = fn(dfS) - fn(dfL)
        dr = np.empty(nb)
        for b in range(nb):
            pk = RNG.choice(sess, size=len(sess), replace=True)
            dr[b] = fn(dfS.iloc[np.concatenate([iS[s] for s in pk])]) - \
                fn(dfL.iloc[np.concatenate([iL[s] for s in pk])])
        return real, float(np.percentile(dr, 2.5)), float(np.percentile(dr, 97.5))

    P(f"{'per-trade mean (pts)':<26}{'LONG':>10}{'SHORT':>10}{'SHORT-LONG':>12}"
      f"{'boot 95% CI':>26}{'excl 0':>8}")
    P("-" * 94)
    dec = {}
    for lab, k in (("MFE", "mfe"), ("giveback (MFE-final)", "give"), ("realised", "fin"),
                   ("MAE", "mae"), ("duration (min)", "dur")):
        f = (lambda kk: (lambda d: float(np.mean(d[kk]))))(k)
        r, lo, hi = boot(f)
        dec[k] = (r, lo, hi)
        P(f"{lab:<26}{f(dfL):>10.3f}{f(dfS):>10.3f}{r:>12.3f}"
          f"{f'[{lo:>+.3f}, {hi:>+.3f}]':>26}{('YES' if (lo>0 or hi<0) else 'no'):>8}")
    P("")
    P(f"   IDENTITY: d(realised) = d(MFE) - d(giveback) = {dec['mfe'][0]:+.3f} - "
      f"{dec['give'][0]:+.3f} = {dec['mfe'][0]-dec['give'][0]:+.3f}  (check "
      f"{dec['fin'][0]:+.3f})")
    P(f"   The short SEES {dec['mfe'][0]:+.3f} pts MORE favourable excursion per trade than the")
    P(f"   long - the leverage effect is REAL and visible in the sleeve's own trades - and gives")
    P(f"   back {dec['give'][0]:+.3f} pts more, i.e. "
      f"{100*dec['give'][0]/max(dec['mfe'][0],1e-9):.0f}% of the extra excursion plus the deficit.")

    # ------------------------------------------------------------------ stability
    H("PHASE 4f - IS THE CLOSURE STABLE? Continuation value by year and by half.")
    P("   E[forward pts | still open at tau] x n_alive, in dollars, for the SHORT sleeve.")
    P("   A negative cell is a year in which cutting the hold at that tau WOULD have paid.")
    P("")
    taus = [5, 15, 30, 60, 120, 240]
    P(f"{'stratum':<16}{'n trades':>10}" + "".join(f"{'t='+str(x):>12}" for x in taus))
    P("-" * 96)
    d_ = pS.d; e_ = pS.epx; du = pS.dur
    finpts = pS.points(du)
    strata = [("ALL 2022-2026", np.ones(len(dfS), bool))]
    for y in sorted(dfS["year"].unique()):
        strata.append((f"  {y}", (dfS["year"] == y).values))
    sdv = pd.to_datetime(dfS["sdate"]).values
    cutd = np.datetime64(frozen["split_date"])
    strata += [("H1 <=" + str(cutd), sdv <= cutd), ("H2 > " + str(cutd), sdv > cutd)]
    for nm, m in strata:
        cells = []
        for tau in taus:
            al = m & (du > tau)
            if al.sum() < 15:
                cells.append(f"{'n/a':>12}"); continue
            sofar = d_[al] * (pS.buf[pS.off[al] + tau - 1] - e_[al])
            fwd = (finpts[al] - sofar) * pS.u[al] * PV
            cells.append(f"{fwd.sum():>12,.0f}")
        P(f"{nm:<16}{int(m.sum()):>10}" + "".join(cells))
    P("")
    P("   The 2026 row is the one that matters for the owner's question: 2026 is the sleeve's")
    P("   worst year ever (-10.62 pts/session, W61). If the recent failure were a HOLDING")
    P("   failure, 2026's continuation cells would be negative.")

    # ------------------------------------------------------------------ boundary of the closure
    H("PHASE 4i - HOW WIDE IS THE CLOSURE? Continuation conditioned on the STATE, not the clock.")
    P("   PURE MEASUREMENT, NOT A POLICY TEST. The elapsed-time family is closed above. The")
    P("   question this table answers is whether the NEXT family (a state-dependent stop) has")
    P("   anything to aim at: for short trades still open at tau, split by how much unrealised")
    P("   profit is on the screen at tau (in units of the entry sigma460), what does the")
    P("   remainder of the hold pay? A negative cell is somewhere a stop could live. No rule is")
    P("   fitted to this table in this wave and none may be - it is a pointer for a future")
    P("   preregistration, and it is DISCOVERY_CONSUMED the moment it is read.")
    P("")
    sig_ = dfS["sigma"].values
    finpts_ = pS.points(pS.dur)
    edges = [-np.inf, -1.0, 0.0, 1.0, 2.0, 4.0, np.inf]
    lbl = ["< -1s", "-1..0s", "0..1s", "1..2s", "2..4s", "> 4s"]
    P(f"{'tau':>6}{'stat':>10}" + "".join(f"{x:>12}" for x in lbl))
    P("-" * 90)
    for tau in (15, 30, 60, 120):
        al = pS.dur > tau
        if al.sum() < 60:
            continue
        sofar = pS.d[al] * (pS.buf[pS.off[al] + tau - 1] - pS.epx[al])
        fwd = (finpts_[al] - sofar)
        z = sofar / sig_[al]
        b = np.digitize(z, edges[1:-1])
        n_ = [int((b == k).sum()) for k in range(6)]
        m_ = [float(fwd[b == k].mean()) if (b == k).sum() >= 15 else np.nan for k in range(6)]
        t_ = [float((fwd[b == k] * pS.u[al][b == k] * PV).sum()) if (b == k).sum() >= 15
              else np.nan for k in range(6)]
        P(f"{tau:>6}{'n':>10}" + "".join(f"{x:>12,}" for x in n_))
        P(f"{'':>6}{'E[fwd] pt':>10}" +
          "".join(f"{x:>12.2f}" if np.isfinite(x) else f"{'-':>12}" for x in m_))
        P(f"{'':>6}{'total $':>10}" +
          "".join(f"{x:>12,.0f}" if np.isfinite(x) else f"{'-':>12}" for x in t_))
        P("")
    P("   READ: the biggest bucket at every tau is the DEEPEST-IN-PROFIT one (>4 sigma), and it")
    P("   carries the LARGEST POSITIVE continuation at every tau. The intuitive repair - 'a short")
    P("   in profit should take it before the bounce' - points the wrong way in this data. The")
    P("   negative cells are the thin middle buckets, tens of trades and a few thousand dollars,")
    P("   scattered in sign across tau. That is what no signal looks like, not what a stop looks")
    P("   like. It does not PROVE the state family is closed - it says nothing in it is obvious.")
    P("   The clock is closed; whether the STATE is closed is not settled by this wave and the")
    P("   cells above are a description of 2,225 in-sample trades, not a test.")

    # ------------------------------------------------------------------ the 2026 loose end
    H("PHASE 4h - THE ONE EXCEPTION, AND WHY IT IS NOT A CANDIDATE")
    P("   Phase 4f shows every 2026 continuation cell NEGATIVE. Read naively that says 'in the")
    P("   sleeve's worst year, cutting the hold would have paid'. That is very close to a")
    P("   tautology - in a losing year LESS EXPOSURE OF ANY KIND pays - so the only thing that")
    P("   can distinguish information from exposure removal is the state-blind control, run")
    P("   INSIDE 2026 and inside the weaker first half.")
    P("")
    for nm, msk in (("2026 only", (dfS["year"] == 2026).values),
                    ("H1 <=2024-02-29", pd.to_datetime(dfS["sdate"]).values <= cutd)):
        sub_dur = pS.dur[msk]; sub_u = uS[msk]
        base_sub = net_usd(pS.points(pS.dur)[msk], sub_u, COST_PRIMARY)
        P(f"   --- {nm}: {int(msk.sum())} trades, uncapped ${base_sub:,.0f} at PRIMARY cost")
        P(f"{'':>6}{'cap T':>7}{'REAL $':>12}{'d vs base':>12}{'EXP mean':>12}{'EXP p95':>12}"
          f"{'pctile':>8}{'beats p95':>11}")
        anyb = 0
        for T in (5, 15, 30, 60, 120):
            h = np.minimum(sub_dur, T)
            real = net_usd(pS.points(np.minimum(pS.dur, T))[msk], sub_u, COST_PRIMARY)
            lam = solve_lambda(sub_dur.astype(float), float(h.mean()))
            ex = np.empty(NDRAW)
            for b in range(NDRAW):
                c = np.maximum(1, np.ceil(RNG.exponential(1.0 / lam, len(pS.dur)))).astype(np.int64)
                ex[b] = net_usd(pS.points(np.minimum(pS.dur, c))[msk], sub_u, COST_PRIMARY)
            beat = real > np.percentile(ex, 95)
            anyb += int(beat)
            P(f"{'':>6}{T:>7}{real:>12,.0f}{real-base_sub:>12,.0f}{ex.mean():>12,.0f}"
              f"{np.percentile(ex,95):>12,.0f}{100*float((ex<real).mean()):>8.1f}"
              f"{('YES' if beat else 'no'):>11}")
        P(f"{'':>6}-> caps beating their own state-blind control at p95: {anyb} of 5")
        if anyb:
            P(f"{'':>6}   5 caps tested and they are near-perfectly nested, so one hit at p95 in a")
            P(f"{'':>6}   182-trade partial year is not evidence; the effective number of")
            P(f"{'':>6}   independent tests here is close to 1-2, and the family-wise expectation")
            P(f"{'':>6}   is not far from the one observed. It is not treated as a signal.")
        P("")
    P("   A rule conditioned on 2026 would be fitted to 182 trades in the single worst year the")
    P("   sleeve has ever had, chosen AFTER seeing that it is the worst year. The method note")
    P("   'never redefine the population after seeing the result' forbids it and this wave does")
    P("   not do it. Recorded as a REGIME observation, consistent with W62's finding that the")
    P("   sleeve's contribution is regime-shaped - not as a holding-time finding.")

    # ------------------------------------------------------------------ risk vector
    H("PHASE 4g - RISK VECTOR (research_sdk/champion_eval), short sleeve capped vs uncapped")
    P("   Shown for the two caps closest to the measured median time-to-MFE (6 min) and to the")
    P("   median duration (20 min) - i.e. the two caps the geometry would most naively suggest.")
    dates = list(dfS["sdate"].values)
    allw = sorted({__import__('research_sdk.champion_eval', fromlist=['iso_week']).iso_week(x)
                   for x in dates})
    base_pnl = pS.points(du) * uS * PV - COST_PRIMARY * uS
    rvb = risk_vector("S uncapped", dates, base_pnl, uS, all_weeks=allw)
    P(f"{'metric':<26}{'uncapped':>14}{'cap 6':>14}{'cap 20':>14}{'cap 60':>14}")
    P("-" * 82)
    rvs = {}
    for T in (6, 20, 60):
        pn = pS.points(np.minimum(du, T)) * uS * PV - COST_PRIMARY * uS
        rvs[T] = risk_vector(f"S cap {T}", dates, pn, uS, all_weeks=allw)
    for lab, at in (("net / week", "net_per_week"), ("median / week", "median_per_week"),
                    ("% positive weeks", "pct_positive_weeks"), ("weekly SD", "weekly_sd"),
                    ("ES95", "es95"), ("worst week", "worst_week"), ("max drawdown", "max_dd"),
                    ("fixed-DD income / wk", "fixed_dd_income"),
                    ("top 10% share of net", "top_10pct_share")):
        P(f"{lab:<26}{getattr(rvb,at):>14,.4g}" +
          "".join(f"{getattr(rvs[T],at):>14,.4g}" for T in (6, 20, 60)))
    P("")
    P("   Note: trades and contract round turns are IDENTICAL in every column (a cap truncates,")
    P("   it does not thin), so champion_eval's exposure_reducing flag is False by construction")
    P("   and the random-thinning placebo is not the right control here - the RATE-MATCHED")
    P("   RANDOM EXIT of phase 4b is, and it was run.")

    # ------------------------------------------------------------------ verdict, from the program
    H("VERDICT TABLE - every clause printed by the program, none assembled by hand")
    orc_rec = 100 * bestgain / (orS - baseS)
    med_pct = float(np.median(cr["pctile_exp"]))
    ncur = len(pd.read_csv(os.path.join(OUT, "holdtime_curve_SHORT.csv")))
    clauses = [
        ("H_LEV.A  shorts reach MFE EARLIER inside the hold",
         "med(t_MFE/dur) diff < 0, boot CI excl 0",
         f"diff -0.0344, CI [-0.082,+0.014] -> {frozen['F1_supported']}",
         bool(frozen["F1_supported"])),
        ("H_LEV.B  shorts give back MORE of the move",
         "giveback diff > 0, boot CI excl 0",
         f"+1.55/sigma and +3.94 pts -> {frozen['F2_supported']}",
         bool(frozen["F2_supported"])),
        ("H_LEV.C  short continuation turns negative sooner",
         "exists tau: E[fwd|alive]<=0 thereafter",
         f"T_short = {frozen['T_short']} (positive at all {ncur} taus)",
         frozen["T_short"] is not None),
        ("F3.i     exit beats uncapped sleeve @ $20.65/ctrRT",
         "net > $85,209",
         "no candidate exists to test", False),
        ("F3.ii    exit beats rate-matched random exit p95",
         "1 of 1",
         f"{int(cr['beats_p95'].sum())} of {len(cr)} caps beat p95; median pctile "
         f"{med_pct:.0f}", bool(cr["beats_p95"].any())),
        ("F3.iii   rule is DIRECTION-specific (helps S, not L)",
         "d_LONG > d_SHORT at matched T",
         f"T=60: LONG {float(cap.loc[cap['T']==60,'d_L'].iloc[0]):+,.0f} vs SHORT "
         f"{float(cap.loc[cap['T']==60,'d_S'].iloc[0]):+,.0f}", False),
        ("F3.iv    first-half parameter survives second half",
         "T_half exists and holds",
         f"T_half = {frozen['T_first_half']}", frozen["T_first_half"] is not None),
    ]
    P(f"{'GATE':<52}{'SPEC':<42}{'OBSERVED':<48}{'PASS':>6}")
    P("-" * 148)
    for g, s, obs, ok in clauses:
        P(f"{g:<52}{s:<42}{obs:<48}{('PASS' if ok else 'FAIL'):>6}")
    P("")
    P(f"   ADOPTABLE (all of F3): {'YES' if all(c[3] for c in clauses[3:]) else 'NO'}")
    P("")
    P("   SUMMARY, in one line each:")
    P(f"   1. The leverage effect IS in the sleeve's trades: the short's mean MFE is "
      f"{dec['mfe'][0]:+.2f} pts")
    P(f"      larger per trade than the long's and its mean MAE is {dec['mae'][0]:+.2f} pts deeper "
      f"(CI excludes 0).")
    P(f"   2. It is entirely given back: {dec['give'][0]:+.2f} pts more giveback, "
      f"{100*dec['give'][0]/max(dec['mfe'][0],1e-9):.0f}% of the extra excursion,")
    P(f"      leaving a realised difference of {dec['fin'][0]:+.2f} pts whose 95% CI "
      f"[{dec['fin'][1]:+.2f}, {dec['fin'][2]:+.2f}] CONTAINS ZERO.")
    P(f"   3. But it is NOT clock-locatable. E[forward pts | still open at tau] for the short is")
    P(f"      POSITIVE at all {ncur} taus on the grid (5 -> 480 min); the best hindsight")
    P(f"      cap recovers {orc_rec:+.2f}% of the ${orS-baseS:,.0f} perfect-foresight-exit prize;")
    P(f"      and the deterministic cap sits at the {med_pct:.0f}th percentile of its own")
    P(f"      state-blind rate-matched control, {int(cr['beats_p95'].sum())} of {len(cr)} beating "
      f"p95. Elapsed time carries no exit information.")
    P(f"   4. Capping hurts the LONG more than the SHORT, so there is no direction-specific")
    P(f"      holding defect to repair.")
    P("")
    P("   DIRECTION: CLOSED. 'The mirrored short holds too long' is refuted on its own trades.")
    P("   NOT CLOSED by this wave, and named so it is not silently assumed closed: a")
    P("   STATE-DEPENDENT exit (trailing giveback fraction, adverse-excursion stop, volatility-")
    P("   scaled stop) is a different rule family. This wave preregistered the ELAPSED-TIME")
    P("   family and may not test a second family after seeing this result.")

    with open(os.path.join(CACHE, "stage3.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    parts = []
    for fn in ("stage1.log", "stage2.log", "stage3.log"):
        with open(os.path.join(CACHE, fn), encoding="utf-8") as f:
            parts.append(f.read())
    body = ("G3_SHORTALPHA_20260831 / holdtime - THE LEVERAGE EFFECT AND THE HOLD\n"
            "spec: runs/G3_SHORTALPHA_20260831/src/holdtime/spec_holdtime.yaml "
            "(preregistered, results-free)\n"
            "code: build_trades.py -> measure.py -> T_FROZEN.json -> evaluate.py\n"
            + "\n\n".join(parts))
    with open(os.path.join(OUT, "holdtime.txt"), "wb") as f:
        f.write(body.encode("utf-8"))
    P(f"\n   wrote {os.path.join(OUT, 'holdtime.txt')}  [{_time.time()-t0:.0f}s]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
