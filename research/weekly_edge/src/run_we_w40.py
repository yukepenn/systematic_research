"""WE_W40 SECOND MODEL (spec preregistered): four mechanisms that are NOT a trend ratchet.

A fade EVENT (value reversion as an event, not the state rule W11/W18 falsified)
B volatility-EXPANSION event (the ratchet flips on retracement; this fires on expansion)
C sweep-and-reclaim event (a liquidity/stop-run mechanism, not a trend mechanism)
D complement-set supervised model (trades ONLY bars where Solar holds nothing - structural
  orthogonality rather than hoped-for orthogonality)

Every axis reports its correlation with the long object AND its CONDITIONAL correlation inside
the long object's worst-decile weeks, because a sleeve that decouples in calm weeks and
re-couples in bad ones is worthless. Portfolio claims are time-weighted exposure-matched.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote, sfills                             # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from we_quality import build_context                                     # noqa: E402
from we_features import build_universe                                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W40_SECOND", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
WF0 = np.datetime64("2023-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260840)


# ------------------------------------------------------------------ axis builders
def axis_fade(D, X, k=2.0, giveback=0.30, cut=None):
    """A: enter AGAINST an extension once it gives back `giveback` of its peak."""
    n = D["n"]
    c, o = D["c"], D["o"]
    atr = np.maximum(X["atr_l"], 1e-9)
    vw = np.zeros(n); pv = vv = 0.0
    for i in range(n):
        if D["fb"][i]:
            pv = vv = 0.0
        pv += c[i] * D["v"][i]; vv += D["v"][i]
        vw[i] = pv / vv if vv > 0 else c[i]
    ext = (c - vw) / atr                       # decision-bar value (uses c[i], filled at i+1)
    pos = np.zeros(n, np.int8)
    peak = 0.0; side = 0; held = 0; hold_from = -1
    for i in range(n):
        if D["fb"][i]:
            peak = 0.0; side = 0; held = 0
        e = ext[i]
        if held != 0:
            done = (e >= 0) if held > 0 else (e <= 0)      # exit on the VWAP touch
            if done or (cut is not None and i - hold_from >= cut):
                held = 0
            pos[i] = held
            if held != 0:
                continue
        if abs(e) >= k:
            if side == 0 or np.sign(e) != side:
                side = int(np.sign(e)); peak = abs(e)
            peak = max(peak, abs(e))
        if side != 0 and peak >= k and abs(e) <= peak * (1 - giveback):
            held = -side                      # fade the extension
            hold_from = i
            side = 0; peak = 0.0
        pos[i] = held
    return pos


def axis_volexp(D, X, up=1.6, down=1.0, look=15):
    """B: fire on the ONSET of realised-vol expansion, in the direction of the displacement."""
    n = D["n"]
    c = D["c"]
    ret = np.diff(c, prepend=c[0])
    rs = pd.Series(ret).rolling(look, min_periods=5).std().values
    rl = pd.Series(ret).rolling(120, min_periods=30).std().values
    r = np.nan_to_num(rs / np.maximum(rl, 1e-9), nan=1.0)
    disp = c - np.concatenate([[c[0]] * look, c[:-look]])
    pos = np.zeros(n, np.int8)
    held = 0
    for i in range(n):
        if D["fb"][i]:
            held = 0
        if held != 0 and r[i] < down:
            held = 0
        if held == 0 and i > 0 and r[i] >= up > r[i - 1] and disp[i] != 0:
            held = int(np.sign(disp[i]))
        pos[i] = held
    return pos


def axis_sweep(D, cut=23, m=3):
    """C: extreme is taken out and price closes back inside within m bars -> fade the sweep."""
    n = D["n"]
    h, l, c = D["h"], D["l"], D["c"]
    idx = np.arange(n)
    pos = np.zeros(n, np.int8)
    hi = lo = np.nan
    held = 0; since = -1
    up_at = dn_at = -10 ** 9
    up_lvl = dn_lvl = np.nan
    for i in range(n):
        if D["fb"][i]:
            hi = lo = np.nan; held = 0; up_at = dn_at = -10 ** 9
        if held != 0:
            if i - since >= cut:
                held = 0
            pos[i] = held
            if held != 0:
                if not np.isnan(hi):
                    hi = max(hi, h[i]); lo = min(lo, l[i])
                else:
                    hi, lo = h[i], l[i]
                continue
        if not np.isnan(hi):
            if h[i] > hi:
                up_at, up_lvl = i, hi
            if l[i] < lo:
                dn_at, dn_lvl = i, lo
            if i - up_at <= m and c[i] < up_lvl:
                held, since = -1, i
            elif i - dn_at <= m and c[i] > dn_lvl:
                held, since = 1, i
            hi = max(hi, h[i]); lo = min(lo, l[i])
        else:
            hi, lo = h[i], l[i]
        pos[i] = held
    return pos


def axis_complement(D, F, names, flat, horizon=30, lam=10.0, q=0.90):
    """D: ridge on the forward return, refit quarterly on trailing-12m FLAT bars only."""
    n = D["n"]
    c = D["c"]
    atr = np.maximum(pd.Series(np.abs(np.diff(c, prepend=c[0]))).rolling(
        240, min_periods=30).mean().values, 1e-9)
    fwd = (np.concatenate([c[horizon:], [c[-1]] * horizon]) - c) / atr
    # bar-i information at index i (we_features lags by one; un-lag for the decision bar)
    M = np.vstack([np.concatenate([F[k][1:], F[k][-1:]])
                   for k in names]).T.astype(np.float32)
    t = D["t"]
    qtr = pd.PeriodIndex(pd.to_datetime(t), freq="Q")
    pred = np.zeros(n); thr = np.full(n, np.inf)
    for qp in qtr.unique():
        qs = np.datetime64(qp.start_time.to_pydatetime())
        if qs < WF0:
            continue
        fitm = (t >= qs - np.timedelta64(365, "D")) & (t < qs - np.timedelta64(1, "D")) & flat
        tstm = (qtr == qp).values
        if fitm.sum() < 5000 or tstm.sum() == 0:
            continue
        Xf = M[fitm].astype(np.float64); yf = fwd[fitm]
        mu, sd = Xf.mean(0), np.maximum(Xf.std(0), 1e-9)
        Z = (Xf - mu) / sd
        beta = np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ yf)
        pf = Z @ beta
        thr[tstm] = float(np.quantile(np.abs(pf), q))
        pred[tstm] = ((M[tstm] - mu) / sd) @ beta
    pos = np.zeros(n, np.int8)
    held = 0; since = -1
    for i in range(n):
        if D["fb"][i]:
            held = 0
        if held != 0 and i - since >= horizon:
            held = 0
        if held == 0 and flat[i] and abs(pred[i]) >= thr[i] and np.isfinite(thr[i]):
            held, since = int(np.sign(pred[i])), i
        pos[i] = held
    return pos, pred


# ------------------------------------------------------------------ main
def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]

    def nsess(a, b):
        m = (tarr >= a) & (tarr < b)
        return len(np.unique(D["sid"][m]))
    NS = nsess(WF0, B)
    out = open(os.path.join(OUT, "second.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---- long reference + B1 ---------------------------------------------------------
    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)
    LONG = fills_qexit(D, posL, szQ0, scQ0)
    ptsf = np.array([x["pnl"] for x in LONG if A <= np.datetime64(x["et"]) < B]).sum() \
        / PV / nsess(A, B)
    P_(f"=== B1: long object {ptsf:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(ptsf-14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")
    if abs(ptsf - 14.72) >= 0.6:
        out.close(); return
    F, CLS = build_universe(D)
    names = list(F)

    def wser(trl, a=WF0, b=B):
        d = weekly(trl, wk_of, a, b)
        return d
    wL = wser(LONG)
    keys = sorted(wL)
    vL = np.array([wL[k] for k in keys])

    def expo(trl, a=WF0, b=B):
        return float(sum(x.get("u", 1)
                         * ((np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                            / np.timedelta64(1, "m"))
                         for x in trl if a <= np.datetime64(x["et"]) < b))

    rows = []
    hdr = (f"{'axis':<26}{'n':>6}{'pts':>7}{'$/tr':>8}{'wk$':>8}{'wk+%':>6}{'worst':>9}"
           f"{'CVaR5':>9}{'shrp':>7}{'eff':>7}{'stress':>8}{'corr':>7}{'corrDD':>8}{'ovlp':>7}")

    def rep(nm, trl, posarr=None):
        d = wser(trl)
        v = np.array([d.get(k, 0.0) for k in keys])
        s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        p = np.array([x["pnl"] for x in trl if WF0 <= np.datetime64(x["et"]) < B])
        if len(p) == 0:
            p = np.array([0.0])
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cvar = float(np.sort(v)[:nw].mean())
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        st = float((v - STRESS_RT * len(p) / max(len(v), 1)).mean())
        cor = float(np.corrcoef(v, vL)[0, 1]) if v.std() > 0 else 0.0
        dd = np.argsort(vL)[:max(3, len(vL) // 10)]
        cdd = float(np.corrcoef(v[dd], vL[dd])[0, 1]) if v[dd].std() > 0 else 0.0
        ov = float((posarr[posL != 0] != 0).mean() * 100) if posarr is not None else np.nan
        P_(f"{nm:<26}{len(p):>6}{p.sum()/PV/NS:>7.2f}{p.mean():>8.1f}{v.mean():>8,.0f}"
           f"{(v>0).mean()*100:>6.1f}{v.min():>9,.0f}{cvar:>9,.0f}{s:>7.3f}{eff:>7.3f}"
           f"{st:>8,.0f}{cor:>7.2f}{cdd:>8.2f}{ov:>7.1f}")
        r = dict(axis=nm, n=len(p), pts=round(float(p.sum() / PV / NS), 2),
                 per_trade=round(float(p.mean()), 1), wk=round(float(v.mean())),
                 wkpos=round(float((v > 0).mean() * 100), 1), worst=round(float(v.min())),
                 cvar5=round(cvar), sharpe=round(s, 3), eff=round(eff, 3), stress=round(st),
                 corr=round(cor, 3), corr_dd=round(cdd, 3),
                 overlap=None if posarr is None else round(ov, 1))
        rows.append(r); return r

    P_(f"\n=== STANDALONE + INDEPENDENCE (2023-07 -> 2026-08; corr vs the long object; "
       f"corrDD = correlation inside the long object's worst-decile weeks) ===")
    P_(hdr)
    rL = rep("LONG reference", LONG, posL)

    flat = (posL == 0)
    P_(f"   (Solar holds a position on {100-flat.mean()*100:.1f} % of bars)")
    axes = {}
    axes["A fade event k2.0"] = axis_fade(D, X, 2.0, 0.30)
    axes["A fade event k1.5"] = axis_fade(D, X, 1.5, 0.30)
    axes["B vol-expansion 1.6"] = axis_volexp(D, X, 1.6, 1.0)
    axes["C sweep+reclaim"] = axis_sweep(D)
    pd_, prd = axis_complement(D, F, names, flat)
    axes["D complement ridge"] = pd_
    for nm, pa in axes.items():
        rep(nm, sfills(D, pa, halt=1300.0, target=1000.0), pa)

    # ---- portfolio, time-weighted exposure matched ------------------------------------
    P_(f"\n=== EXPOSURE-MATCHED PAIRS (long scaled to the pair's contract-minutes) "
       f"[{_time.time()-t0:.0f}s] ===")
    P_(f"{'pair':<34}{'wk$':>9}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}{'shrp':>8}"
       f"{'eff':>8}{'cvEff':>8}")

    def pair(nm, trl2):
        comb = LONG + trl2
        sc = expo(comb) / max(expo(LONG), 1e-9)
        for tag, tl, k in ((f"long x{sc:.2f} alone", LONG, sc), (nm, comb, 1.0)):
            d = wser(tl)
            v = np.array([d.get(x, 0.0) for x in keys]) * k
            nw = max(1, int(np.ceil(0.05 * len(v))))
            cv = float(np.sort(v)[:nw].mean())
            s = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
            P_(f"{tag:<34}{v.mean():>9,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
               f"{cv:>10,.0f}{s:>8.3f}"
               f"{v.mean()/abs(v.min()):>8.3f}{v.mean()/abs(cv):>8.3f}")
    for nm, pa in axes.items():
        pair(f"long + {nm}", sfills(D, pa, halt=1300.0, target=1000.0))

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
