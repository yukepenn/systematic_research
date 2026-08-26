"""WE_W65 phase 1 - is the NQ/ES divergence mean-reverting, and is the reversion bigger than
two round turns of friction?

Relative value has never been tested in this repo - a repo-wide search for pairs / stat-arb /
cointegration / hedge ratio / market-neutral returned zero instances, and every two-instrument
study traded NQ outright while the other instrument fed a signal. No two-legged position has
ever been opened here.

A dollar-neutral spread is decorrelated with a directional trend follower BY CONSTRUCTION. That
does not make it profitable; it makes the decoupling non-accidental, which is the half this
campaign has never secured.

This file is the STOPPING RULE. It measures whether the divergence reverts and whether the
reversion clears TWO round turns of friction. No rule is built and no backtest is run.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W65_RELVALUE", "out")
os.makedirs(OUT, exist_ok=True)
NQP = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                   "nq1m_2005_202605.parquet")
ESP = os.path.join(ROOT, "runs", "SM1M_ES_SUBSTRATE", "out", "es_1m_2022_2026.parquet")
PV_NQ, PV_ES = 20.0, 50.0
COMM_NQ, COMM_ES = 4.36, 4.36          # per round turn per contract, same broker schedule
STRESS_TICK_NQ, STRESS_TICK_ES = 10.0, 12.5   # 2 ticks of slippage: NQ 0.25*20, ES 0.25*50
BETA_WIN = 390                          # trailing minutes for the causal beta (one RTH day)
HORIZONS = (1, 5, 15, 30, 60, 120)
QS = (0.80, 0.90, 0.95, 0.99)
RNG = np.random.default_rng(20260865)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "relvalue.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    nq = pd.read_parquet(NQP, columns=["time", "open", "close"])
    es = pd.read_parquet(ESP, columns=["time", "open", "close"])
    nq["time"] = pd.to_datetime(nq["time"]); es["time"] = pd.to_datetime(es["time"])
    M = nq.merge(es, on="time", suffixes=("_nq", "_es"))
    M = M[M["time"] >= "2022-01-02"].sort_values("time").reset_index(drop=True)
    P_(f"=== joined on exact minute timestamps: {len(M):,} bars "
       f"{M['time'].min()} -> {M['time'].max()} [{_time.time()-t0:.0f}s]")

    t = M["time"].values.astype("datetime64[s]")
    fb = np.zeros(len(M), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    sid = np.cumsum(fb) - 1
    n_sess = int(sid[-1] + 1)
    P_(f"   {n_sess:,} sessions detected on the joined clock")

    cn, ce = M["close_nq"].values, M["close_es"].values
    on, oe = M["open_nq"].values, M["open_es"].values
    rn = np.zeros(len(M)); re = np.zeros(len(M))
    rn[1:] = np.diff(cn) / cn[:-1]
    re[1:] = np.diff(ce) / ce[:-1]
    rn[fb] = 0.0; re[fb] = 0.0            # no return across a session gap

    # ---- causal beta: trailing regression of NQ returns on ES returns, LAGGED --------------
    s_xy = pd.Series(rn * re).rolling(BETA_WIN, min_periods=120).sum().shift(1).values
    s_xx = pd.Series(re * re).rolling(BETA_WIN, min_periods=120).sum().shift(1).values
    beta = np.where(s_xx > 1e-18, s_xy / np.maximum(s_xx, 1e-18), np.nan)
    beta = np.clip(np.nan_to_num(beta, nan=1.0), 0.2, 3.0)
    P_(f"   causal beta (trailing {BETA_WIN} min, lagged): median {np.nanmedian(beta):.3f}, "
       f"5th-95th {np.nanpercentile(beta,5):.3f}-{np.nanpercentile(beta,95):.3f}")

    # ---- divergence: cumulative residual return within a session, reset each session -------
    resid = rn - beta * re
    div = np.zeros(len(M))
    acc = 0.0
    for i in range(len(M)):
        if fb[i]:
            acc = 0.0
        acc += resid[i]
        div[i] = acc                       # in RETURN units, i.e. fraction of NQ notional

    # =====================================================================================
    # PHASE 1a/1b/1c - variance ratio, half-life, autocorrelation
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 1a: VARIANCE RATIO of the divergence "
       f"(<1 mean-reverting, 1 random walk, >1 trending)")
    P_(f"{'='*112}")
    P_("With a circular-BLOCK bootstrap by session, because a variance ratio on 1.5 M")
    P_("overlapping observations looks precise and is not.\n")
    d1 = np.zeros(len(M)); d1[1:] = np.diff(div); d1[fb] = 0.0
    sess_bounds = np.flatnonzero(fb).tolist() + [len(M)]
    rows = []
    P_(f"{'horizon (min)':<16}{'variance ratio':>17}{'bootstrap 5th-95th':>26}"
       f"{'OU half-life (min)':>21}{'autocorr of changes':>21}")
    for k in HORIZONS:
        dk = np.zeros(len(M))
        dk[k:] = div[k:] - div[:-k]
        same = sid[k:] == sid[:-k]
        mk = np.zeros(len(M), bool); mk[k:] = same
        v1 = float(np.var(d1[~fb], ddof=1))
        vk = float(np.var(dk[mk], ddof=1))
        vr = vk / (k * v1) if v1 > 0 else np.nan
        # block bootstrap by session
        bs = []
        starts = np.array(sess_bounds[:-1]); ends = np.array(sess_bounds[1:])
        for _ in range(200):
            pick = RNG.integers(0, len(starts), len(starts))
            idx = np.concatenate([np.arange(starts[p], ends[p]) for p in pick[:200]])
            a1 = d1[idx]; a1 = a1[a1 != 0]
            ak = dk[idx][mk[idx]]
            if len(a1) > 100 and len(ak) > 100 and a1.var(ddof=1) > 0:
                bs.append(float(ak.var(ddof=1) / (k * a1.var(ddof=1))))
        bs = np.array(bs)
        # OU half-life from the AR(1) of the divergence level, within session
        lag = np.zeros(len(M)); lag[1:] = div[:-1]
        ok = (~fb) & np.isfinite(div) & np.isfinite(lag)
        b_ = float(np.polyfit(lag[ok], div[ok], 1)[0])
        hl = float(-np.log(2) / np.log(abs(b_))) if 0 < abs(b_) < 1 else np.inf
        ac = float(pd.Series(d1[~fb]).autocorr(k))
        P_(f"{k:<16}{vr:>17.4f}"
           f"{f'{np.percentile(bs,5):.4f} - {np.percentile(bs,95):.4f}' if len(bs) else 'n/a':>26}"
           f"{hl:>21.1f}{ac:>21.4f}")
        rows.append(dict(horizon=k, vr=vr, vr_lo=float(np.percentile(bs, 5)) if len(bs) else np.nan,
                         vr_hi=float(np.percentile(bs, 95)) if len(bs) else np.nan,
                         halflife=hl, autocorr=ac))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "varratio.csv"), index=False)

    # =====================================================================================
    # PHASE 1d - THE ECONOMIC TEST, which is the stopping rule
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 1d: THE STOPPING RULE - is the reversion bigger than TWO "
       f"round turns?")
    P_(f"{'='*112}")
    P_("A dollar-neutral position: 1 NQ against beta x (PV_NQ x price_NQ)/(PV_ES x price_ES) ES.")
    P_("Friction charged on BOTH legs. Base = commission only; stress adds 2 ticks a leg.")
    fric_base = COMM_NQ + COMM_ES
    P_(f"   base friction  = ${fric_base:.2f} per round turn of the PAIR")
    P_(f"   stress friction= ${fric_base + STRESS_TICK_NQ + STRESS_TICK_ES:.2f} "
       f"(2 ticks each leg)")
    fric_str = fric_base + STRESS_TICK_NQ + STRESS_TICK_ES
    notional = PV_NQ * cn                              # dollars per unit of divergence-return
    # causal threshold: trailing quantile of |div| over the prior 60 sessions, same-minute-free
    absdiv = np.abs(div)
    trail_q = {}
    for q in QS:
        s = pd.Series(absdiv).rolling(20 * 390, min_periods=5000).quantile(q).shift(1).values
        trail_q[q] = s
    P_(f"\n{'threshold':<12}{'horizon':>9}{'events':>10}{'mean reversion $':>19}"
       f"{'median $':>12}{'vs base friction':>18}{'vs stress':>12}{'verdict':>12}")
    econ = []
    best = -1e18
    for q in QS:
        thr = trail_q[q]
        for k in HORIZONS:
            fwd = np.full(len(M), np.nan)
            fwd[:-k] = div[k:] - div[:-k]
            same = np.zeros(len(M), bool); same[:-k] = sid[k:] == sid[:-k]
            hit = np.isfinite(thr) & (absdiv > thr) & same & np.isfinite(fwd)
            if hit.sum() < 200:
                continue
            # a reverting position: short the divergence, so P&L = -sign(div) * change * notional
            pnl = -np.sign(div[hit]) * fwd[hit] * notional[hit]
            mean_ = float(pnl.mean()); med_ = float(np.median(pnl))
            v = ("TRADEABLE" if mean_ > fric_str else
                 ("base only" if mean_ > fric_base else "no"))
            P_(f"{f'q{int(q*100)}':<12}{k:>9}{int(hit.sum()):>10}{mean_:>19,.2f}"
               f"{med_:>12,.2f}{mean_-fric_base:>+18,.2f}{mean_-fric_str:>+12,.2f}{v:>12}")
            econ.append(dict(q=q, horizon=k, n=int(hit.sum()), mean=mean_, median=med_,
                             net_base=mean_ - fric_base, net_stress=mean_ - fric_str))
            best = max(best, mean_ - fric_str)
    pd.DataFrame(econ).to_csv(os.path.join(OUT, "reversion.csv"), index=False)
    P_(f"\n=== THE PREREGISTERED STOPPING RULE ===")
    if best <= 0:
        P_(f"   NO threshold x horizon cell has a mean reversion exceeding TWO round turns at")
        P_(f"   stress friction (best is {best:+,.2f} $). The wave STOPS HERE.")
        P_(f"   RECORDED: the NQ/ES divergence is not tradeable at this frequency with this")
        P_(f"   construction. That is one script and no backtest, and it is consistent with the")
        P_(f"   repo's own prior ('at best weakly mean-reverting standalone').")
    else:
        E = pd.DataFrame(econ)
        top = E.sort_values("net_stress", ascending=False).head(5)
        P_(f"   {int((E['net_stress'] > 0).sum())} of {len(E)} cells clear TWO round turns at")
        P_(f"   stress friction. The five largest:")
        P_(f"{'q':<8}{'horizon':>9}{'events':>10}{'mean $':>14}{'net of stress':>16}")
        for _, r in top.iterrows():
            P_(f"{f'q{int(r.q*100)}':<8}{int(r.horizon):>9}{int(r.n):>10}{r['mean']:>14,.2f}"
               f"{r['net_stress']:>+16,.2f}")
        P_(f"\n   -> phase 2 is AUTHORISED. This is NOT a result: the cells overlap heavily,")
        P_(f"      no position sizing, session-close flattening or path dependence is modelled,")
        P_(f"      and no null has been run.")
    P_(f"\n=== STATUS: measurement only. Nothing adopted, no rule built. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
