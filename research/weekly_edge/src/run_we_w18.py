"""WE_W18 ALLWEATHER (spec preregistered): trend(ACTIVE) + a quiet-regime complement.

BUILD 2006-2017 | TEST 2018-2021 | CONFIRM 2022-2026/07, in that order.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W18_ALLWEATHER", "out")
os.makedirs(OUT, exist_ok=True)
# amendment_1: windows re-cut INSIDE the modern regime per owner redirection
WINDOWS = [("BUILD", "2022-01-01", "2023-12-31 17:00"),
           ("TEST", "2024-01-01", "2025-06-30 17:00"),
           ("CONFIRM", "2025-07-01", "2026-07-31 17:00")]


def atr_arr(D):
    tr = np.maximum(D["h"] - D["l"], np.maximum(np.abs(D["h"] - np.roll(D["c"], 1)),
                                                np.abs(D["l"] - np.roll(D["c"], 1))))
    tr[0] = D["h"][0] - D["l"][0]
    a = pd.Series(tr).rolling(14, min_periods=1).mean().values
    return np.concatenate([[a[0]], a[:-1]])


def sess_vwap(D):
    pv = 0.0; vv = 0.0
    out = np.full(D["n"], np.nan)
    for i in range(D["n"]):
        if D["fb"][i]:
            pv = 0.0; vv = 0.0
        pv += D["c"][i] * D["v"][i]; vv += D["v"][i]
        out[i] = pv / vv if vv > 0 else np.nan
    return np.concatenate([[np.nan], out[:-1]])          # value known at i-1


def generic_fade(D, active, entry_ok, target_arr, stop=None, max_per=3):
    """Generic quiet-regime mean-reversion driver. entry_ok(i) -> -1/0/+1 (already causal)."""
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    pos = 0; epx = 0.0; eti = -1; pend = 0; cnt = 0
    for i in range(n):
        if fb[i]:
            cnt = 0
        if pend != 0 and pos == 0:
            pos = pend; epx, eti = o[i], i; cnt += 1
        pend = 0
        if pos != 0 and stop is not None:
            lvl = epx - pos * stop
            if (l[i] <= lvl) if pos > 0 else (h[i] >= lvl):
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                px = o[i] if gap else lvl
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (px - epx) * PV - COMM_RT))
                pos = 0
        if pos != 0 and not np.isnan(target_arr[i]):
            tg = target_arr[i]
            if (h[i] >= tg) if pos > 0 else (l[i] <= tg):
                px = o[i] if ((o[i] >= tg) if pos > 0 else (o[i] <= tg)) else tg
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (px - epx) * PV - COMM_RT))
                pos = 0
        if lb[i]:
            if pos != 0:
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * (c[i] - epx) * PV - COMM_RT))
                pos = 0
            continue
        if pos == 0 and cnt < max_per and active[i] and i >= 25:
            s = int(entry_ok[i])
            if s != 0:
                pend = s
    return trades


def run_window(tag, a, b):
    t0 = _time.time()
    D = load_deep(a, b)
    W1.DEV_END = pd.Timestamp(b).date()
    rng_, dmove, atr14, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    ACTIVE = (norm <= 0) | (ratio >= 0.8)
    QUIET = (norm > 0) & (ratio < 0.8)
    at = atr_arr(D)
    vw = sess_vwap(D)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL, dS = lag_b(cd >= 0), lag_b(cd <= 0)
    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    res = {}
    res["T_both"] = fills(D, tgn, allow_long=dL & ACTIVE, allow_short=dS & ACTIVE)
    res["T_long"] = fills(D, tgn, allow_long=dL & ACTIVE,
                          allow_short=np.zeros(D["n"], bool))
    # Q1 fade vwap
    cprev = np.concatenate([[D["c"][0]], D["c"][:-1]])
    for k in (1.0, 1.5, 2.0):
        e = np.zeros(D["n"], np.int8)
        dev = cprev - vw
        ok = ~np.isnan(vw) & (at > 0)
        e[ok & (dev >= k * at)] = -1
        e[ok & (dev <= -k * at)] = 1
        res[f"Q1_fadevwap_k{k}"] = generic_fade(D, QUIET, e, vw, stop=130.0)
    # Q2 fade prior-day range extreme -> session open
    n_sess = D["n_sess"]
    idx = np.arange(D["n"])
    sess_hi = np.zeros(n_sess); sess_lo = np.zeros(n_sess); sess_op = np.zeros(n_sess)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        sess_hi[s] = D["h"][m].max(); sess_lo[s] = D["l"][m].min(); sess_op[s] = D["o"][m[0]]
    phi = np.concatenate([[np.nan], sess_hi[:-1]])[D["sid"]]
    plo = np.concatenate([[np.nan], sess_lo[:-1]])[D["sid"]]
    opn = sess_op[D["sid"]]
    e2 = np.zeros(D["n"], np.int8)
    ok2 = ~np.isnan(phi)
    e2[ok2 & (cprev >= phi)] = -1
    e2[ok2 & (cprev <= plo)] = 1
    res["Q2_faderail"] = generic_fade(D, QUIET, e2, opn, stop=130.0)
    # Q3 Bollinger mean reversion (20, 2 sigma) -> mean
    ma = pd.Series(D["c"]).rolling(20).mean().values
    sd = pd.Series(D["c"]).rolling(20).std().values
    ma_l = np.concatenate([[np.nan], ma[:-1]]); sd_l = np.concatenate([[np.nan], sd[:-1]])
    e3 = np.zeros(D["n"], np.int8)
    ok3 = ~np.isnan(ma_l) & (sd_l > 0)
    e3[ok3 & (cprev >= ma_l + 2 * sd_l)] = -1
    e3[ok3 & (cprev <= ma_l - 2 * sd_l)] = 1
    res["Q3_mrband"] = generic_fade(D, QUIET, e3, ma_l, stop=130.0)

    stats = {}
    for nm, trl in res.items():
        if len(trl) < 50:
            stats[nm] = None
            continue
        wt = week_table(trl, D, lambda x: x["xt"])
        r = summarize(wt, D, "dev")
        st = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
        stats[nm] = dict(n=len(trl), mean=r["mean"], pos=r["pos"], worst=r["worst"],
                         sharpe=r["sharpe"], stress=st, wt=wt, tpw=r["tpw"])
    print(f"  {tag} done [{_time.time()-t0:.0f}s]", flush=True)
    return D, stats


def main():
    out = open(os.path.join(OUT, "allweather.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    all_stats = {}
    for tag, a, b in WINDOWS:
        D, st = run_window(tag, a, b)
        all_stats[tag] = (D, st)
        P(f"\n=== {tag} ({a} .. {b}) ===")
        P(f"{'engine':<20}{'n':>7}{'wkMean':>9}{'pos%':>7}{'worst':>10}{'sharpe':>8}"
          f"{'stress':>8}{'tpw':>7}")
        for nm, s in st.items():
            if s is None:
                P(f"{nm:<20} too few trades")
                continue
            P(f"{nm:<20}{s['n']:>7}{s['mean']:>9,.0f}{s['pos']:>7.1f}{s['worst']:>10,.0f}"
              f"{s['sharpe']:>8.3f}{s['stress']:>8,.0f}{s['tpw']:>7.1f}")

    # ---- selection BY THE RULE on BUILD, then TEST, then CONFIRM ----
    Db, sb = all_stats["BUILD"]
    quiet = {k: v for k, v in sb.items() if k.startswith("Q") and v}
    P("\n=== SELECTION (rule: best quiet engine on BUILD by Sharpe, stress>0) ===")
    elig = {k: v for k, v in quiet.items() if v["stress"] > 0 and v["sharpe"] > 0}
    if not elig:
        P("NO quiet engine is positive+stress-positive on BUILD -> FAIL per spec.")
        P("Honest conclusion: the quiet regime is not tradeable by mean reversion, and what we")
        P("own is a regime-dependent long-volatility instrument, not an all-weather system.")
    else:
        pick = max(elig, key=lambda k: elig[k]["sharpe"])
        P(f"selected: {pick} (BUILD Sharpe {elig[pick]['sharpe']:.3f}, "
          f"stress ${elig[pick]['stress']:,.0f})")
        for tag in ("BUILD", "TEST", "CONFIRM"):
            D, st = all_stats[tag]
            for tname in ("T_both", "T_long"):
                if st.get(tname) is None or st.get(pick) is None:
                    continue
                p = {}
                for src in (st[tname]["wt"], st[pick]["wt"]):
                    for s_, (net, ntr) in src.items():
                        aa = p.setdefault(s_, [0.0, 0]); aa[0] += net; aa[1] += ntr
                W1.DEV_END = pd.Timestamp(dict((w[0], w[2]) for w in WINDOWS)[tag]).date()
                r = summarize(p, D, "dev")
                stv = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
                P(f"  {tag:<8} {tname}+{pick:<18} wkMean {r['mean']:>7,.0f}  "
                  f"pos {r['pos']:>5.1f}%  worst {r['worst']:>9,.0f}  "
                  f"sharpe {r['sharpe']:>6.3f}  stress {stv:>7,.0f}")
    out.close()


if __name__ == "__main__":
    main()
