"""WE_W117 - what does the BOOK lose on, and is anything we already own positive there?

Spec: runs/WE_W117_LOSESTATE/spec.yaml, committed BEFORE this ran (f23a020).

Section 27: the most valuable new information is whatever earns when P1 loses, when XM loses, or
when both are flat. After 116 waves that state has never been described. Part A describes it.
Part B screens six ALREADY-FROZEN objects against it - no new mechanism, no fitted parameter.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w114 import Win, RTH0, MORN_B, DEC, EXIT                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W117_LOSESTATE", "out")
os.makedirs(OUT, exist_ok=True)
W110O = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out")
CALF = os.path.join(ROOT, "research", "04_complementary_family", "c01_announcement_calendar.csv")
DDT = 20245.0
SEED = 117
CLASSES = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "losestate.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    W = Win("2022-07-01", "2026-07-31 17:00", True, "MODERN")
    P_(f"    {len(W.sess_in):,} sessions [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ the book
    WK = pd.read_csv(os.path.join(W110O, "weekly.csv"))
    J = WK.set_index("week")[["p1", "xm"]].copy()
    sp, sx = J["p1"].std(ddof=1), J["xm"].std(ddof=1)
    w1 = (1 / sp) / ((1 / sp) + (1 / sx))
    J["book"] = w1 * J["p1"] + (1 - w1) * J["xm"]
    NW = len(J)
    lose = (J["book"] < 0).to_numpy()
    P_(f"    book = {w1:.3f} x P1/PCT + {1-w1:.3f} x XM (inverse-vol), {NW} weeks, "
       f"{int(lose.sum())} losing ({100*lose.mean():.1f} %)")

    # ------------------------------------------------------------------ weekly market state
    sess_close = W.at(1020)
    prevc = np.full(W.NS, np.nan); prevc[1:] = sess_close[:-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        sret = np.log(sess_close / prevc)
    hi = W.agg_hi = None
    m = (W.mod >= RTH0) & (W.mod <= 960)
    ii = np.flatnonzero(m)
    sh = np.full(W.NS, -np.inf); sl = np.full(W.NS, np.inf)
    np.maximum.at(sh, W.sid[ii], W.h[ii]); np.minimum.at(sl, W.sid[ii], W.l[ii])
    cal = pd.read_csv(CALF)
    cald = set(pd.to_datetime(cal["date"]).dt.date.tolist())
    ann = np.array([W.sdate[s].date() in cald for s in range(W.NS)], float)

    D = pd.DataFrame(dict(wk=W.wk, ret=sret[W.sess_in], hi=sh[W.sess_in], lo=sl[W.sess_in],
                          ann=ann[W.sess_in], kl=W.klass[W.sess_in]))
    G = D.groupby("wk")
    ST = pd.DataFrame(dict(
        nq_ret_pct=100 * G["ret"].sum(),
        nq_vol_pct=100 * G["ret"].std(ddof=0),
        rng_pts=G["hi"].max() - G["lo"].min(),
        ann_days=G["ann"].sum(),
        n_sess=G["ret"].size(),
    ))
    for c in CLASSES:
        ST[f"sh_{c}"] = G["kl"].apply(lambda v, c=c: float((v == c).mean()))
    J = J.join(ST, how="inner")
    lose = (J["book"] < 0).to_numpy()

    # ================================================================== PART A
    P_("")
    P_("=" * 124)
    P_("=== PART A - CHARACTERISE THE LOSING STATE. Diagnostic; nothing is traded here.")
    P_("=" * 124)
    e = np.cumsum(J["book"].to_numpy())
    dd = np.maximum.accumulate(e) - e
    P_(f"    book: ${J['book'].mean():,.0f}/wk, maxDD ${dd.max():,.0f}, "
       f"{int(lose.sum())} losing weeks, worst ${J['book'].min():,.0f}, "
       f"mean loss ${J['book'][lose].mean():,.0f}")
    runs, cur = [], 0
    for x in lose:
        cur = cur + 1 if x else 0
        runs.append(cur)
    P_(f"    longest losing streak {max(runs)} weeks; weeks in drawdown "
       f"{int((dd > 1e-9).sum())} of {NW} ({100*float((dd>1e-9).mean()):.1f} %)")

    P_("")
    P_(f"{'market state':<20}{'LOSING weeks':>15}{'WINNING weeks':>16}{'difference':>13}"
       f"{'perm p':>9}")
    for c, lab in (("nq_ret_pct", "NQ weekly return %"), ("nq_vol_pct", "daily vol %"),
                   ("rng_pts", "weekly range pts"), ("ann_days", "announcement days"),
                   ("sh_TREND-UP", "share TREND-UP"), ("sh_TREND-DOWN", "share TREND-DOWN"),
                   ("sh_RANGE", "share RANGE"), ("sh_MIXED", "share MIXED"),
                   ("sh_REVERSAL", "share REVERSAL")):
        v = J[c].to_numpy()
        g = np.isfinite(v)
        a, b = v[g & lose], v[g & ~lose]
        d0 = float(a.mean() - b.mean())
        nul = np.empty(2000)
        vv, ll = v[g], lose[g]
        for k in range(2000):
            pl = rng.permutation(ll)
            nul[k] = float(vv[pl].mean() - vv[~pl].mean())
        pv = float(np.mean(np.abs(nul) >= abs(d0)))
        P_(f"{lab:<20}{a.mean():>15.3f}{b.mean():>16.3f}{d0:>13.3f}{pv:>9.3f}"
           + ("  *" if pv < 0.05 else ""))
    P_("")
    P_(f"    correlation of book weekly $ with NQ weekly return: "
       f"{J['book'].corr(J['nq_ret_pct']):+.3f}")
    P_(f"    P(NQ week down | book loses) = "
       f"{float((J['nq_ret_pct'][lose] < 0).mean()):.3f}   "
       f"unconditional P(NQ week down) = {float((J['nq_ret_pct'] < 0).mean()):.3f}")
    P_("")
    P_("    WHICH LEG LOST on the book's losing weeks:")
    both = lose & (J["p1"] < 0).to_numpy() & (J["xm"] < 0).to_numpy()
    p1o = lose & (J["p1"] < 0).to_numpy() & ~(J["xm"] < 0).to_numpy()
    xmo = lose & ~(J["p1"] < 0).to_numpy() & (J["xm"] < 0).to_numpy()
    nei = lose & ~(J["p1"] < 0).to_numpy() & ~(J["xm"] < 0).to_numpy()
    for lab, m_ in (("BOTH legs lost", both), ("P1 only", p1o), ("XM only", xmo),
                    ("neither (rounding/zero XM)", nei)):
        P_(f"        {lab:<28}{int(m_.sum()):>5} weeks  "
           f"({100*float(m_.sum()/max(lose.sum(),1)):>5.1f} % of losing weeks)")

    # ================================================================== PART B
    P_("")
    P_("=" * 124)
    P_("=== PART B - WHAT IS POSITIVE THERE? Six ALREADY-FROZEN objects, no new mechanism.")
    P_("=" * 124)
    md = W.morn_dir()
    CAND = {}
    for lab, d_ in (("FM_LONG", np.where(md > 0, 1.0, 0.0)),
                    ("FM_SHORT", np.where(md < 0, -1.0, 0.0)),
                    ("ALWAYS_SHORT", np.where(W.win, -1.0, 0.0)),
                    ("FADE_MORNING", -md)):
        R = W.run(DEC, EXIT, d_)
        s = np.zeros(W.NS); s[R["take"]] = R["pnl"][R["take"]]
        CAND[lab] = pd.Series(s[W.sess_in]).groupby(W.wk).sum()

    TF = pd.read_csv(os.path.join(W110O, "trade_features.csv"))
    TF["date"] = pd.to_datetime(TF["date"])
    iso = TF["date"].dt.isocalendar()
    TF["wk"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    for lab, sel in (("XM_LONG", TF["is_long"] > 0.5), ("XM_SHORT", TF["is_long"] < 0.5)):
        CAND[lab] = TF[sel].groupby("wk")["pnl"].sum()

    for k in CAND:
        J[k] = CAND[k]
    J = J.fillna({k: 0.0 for k in CAND})
    lose = (J["book"] < 0).to_numpy()

    P_(f"{'candidate':<16}{'all wks $':>11}{'LOSING wks $':>14}{'null mean':>11}{'null p95':>11}"
       f"{'pctile':>9}{'vs ALWAYS_SHORT':>17}")
    res = {}
    asref = float(J["ALWAYS_SHORT"].to_numpy()[lose].mean())
    for k in ("FM_LONG", "FM_SHORT", "XM_LONG", "XM_SHORT", "ALWAYS_SHORT", "FADE_MORNING"):
        v = J[k].to_numpy()
        real = float(v[lose].mean())
        nul = np.array([float(np.roll(v, s)[lose].mean()) for s in range(1, NW)])
        p95 = float(np.nanpercentile(nul, 95))
        pc = 100 * float(np.nanmean(nul < real))
        res[k] = dict(all=float(v.mean()), lose=real, p95=p95, pct=pc)
        P_(f"{k:<16}{v.mean():>11,.0f}{real:>14,.0f}{np.nanmean(nul):>11,.0f}{p95:>11,.0f}"
           f"{pc:>8.1f}th{real-asref:>+17,.0f}")
    P_("")
    surv = [k for k, r in res.items()
            if r["lose"] > 0 and r["lose"] > r["p95"] and (k == "ALWAYS_SHORT" or r["lose"] > asref)]
    P_(f"    survivors of the per-candidate bar: {surv if surv else 'NONE'}")
    if surv:
        best = max(surv, key=lambda k: res[k]["lose"])
        mx = np.empty(2000)
        VS = {k: J[k].to_numpy() for k in res}
        for b in range(2000):
            s_ = rng.integers(1, NW)
            mx[b] = max(float(np.roll(VS[k], s_)[lose].mean()) for k in res)
        p95k = float(np.percentile(mx, 95))
        P_(f"    BEST-OF-6 bar (shared shift, correlation preserved): ${p95k:,.0f}   "
           f"best = {best} at ${res[best]['lose']:,.0f}   "
           f"{'CLEARS' if res[best]['lose'] > p95k else 'FAILS'}")
    else:
        P_("    No candidate clears its own bar, so the best-of-6 bar is not computed.")
    P_("")
    P_(f"    POWER, disclosed in the spec: {int(lose.sum())} losing weeks. sd of the weekly series")
    P_("    per candidate implies the smallest detectable mean at 80 % power is roughly:")
    for k in res:
        sd = float(J[k].std(ddof=1))
        P_(f"        {k:<16} sd ${sd:,.0f}  -> ~${2.8*sd/np.sqrt(max(lose.sum(),1)):,.0f}/wk")

    # ================================================================== PART C
    P_("")
    P_("=" * 124)
    P_("=== PART C - marginal value, run only for survivors")
    P_("=" * 124)
    if not surv:
        P_("    NOT RUN - nothing survived part B. Per the spec that is a RESULT: the book's losses")
        P_("    are not addressable by anything currently owned at this geometry.")
    else:
        def summ(v):
            vv = np.asarray(v, float); dp = dd_profile(vv); srt = np.sort(vv)
            return dict(wk=vv.mean(), maxdd=dp["maxdd"],
                        fixdd=vv.mean() * DDT / max(dp["maxdd"], 1e-9),
                        poswk=100 * float((vv > 0).mean()),
                        cvar=float(srt[:max(1, int(0.05 * len(srt)))].mean()))
        P_(f"{'book':<40}{'conv':<10}{'wk $':>9}{'maxDD':>10}{'wk$@fixDD':>11}"
           f"{'pos wk%':>9}{'CVaR5':>9}")
        b0 = summ(J["book"].to_numpy())
        P_(f"{'P1/PCT + XM (incumbent)':<40}{'inv-vol':<10}{b0['wk']:>9,.0f}{b0['maxdd']:>10,.0f}"
           f"{b0['fixdd']:>11,.0f}{b0['poswk']:>8.1f}%{b0['cvar']:>9,.0f}")
        for k in surv:
            for how in ("invvol", "income"):
                cols = ["p1", "xm", k]
                if how == "invvol":
                    w = np.array([1 / max(J[c].std(ddof=1), 1e-9) for c in cols])
                else:
                    w = np.array([1 / max(abs(J[c].mean()), 1e-9) for c in cols])
                w = w / w.sum() * len(cols)
                v = sum(w[i] * J[cols[i]] for i in range(3)) / 3
                s2 = summ(v.to_numpy())
                P_(f"{'P1/PCT + XM + ' + k:<40}{how:<10}{s2['wk']:>9,.0f}{s2['maxdd']:>10,.0f}"
                   f"{s2['fixdd']:>11,.0f}{s2['poswk']:>8.1f}%{s2['cvar']:>9,.0f}")
    J.to_csv(os.path.join(OUT, "weekly_state.csv"))
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
