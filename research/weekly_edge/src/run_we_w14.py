"""WE_W14 ORTHO (spec preregistered): orthogonal-sleeve hunt + true-delta validation."""
from __future__ import annotations

import glob
import os
import re
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, load, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w06a import available_move                                   # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W14_ORTHO", "out")
os.makedirs(OUT, exist_ok=True)


def agg_targets(D, minutes, volmults):
    """Solar13 targets computed on `minutes`-aggregates, mapped back to the 1-min clock
    (value at 1-min bar i is the aggregate decision known at i-1)."""
    df = pd.DataFrame({"time": pd.to_datetime(D["t"]), "open": D["o"], "high": D["h"],
                       "low": D["l"], "close": D["c"], "volume": D["v"],
                       "sid": D["sid"]})
    grp = (np.arange(D["n"]) // 1)  # placeholder
    # aggregate within session by fixed minute buckets
    mo = np.zeros(D["n"], np.int64)
    idx = np.arange(D["n"])
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        mo[m] = np.arange(len(m))
    bucket = D["sid"].astype(np.int64) * 100000 + (mo // minutes)
    g = df.assign(b=bucket).groupby("b", sort=True)
    agg = g.agg(time=("time", "last"), open=("open", "first"), high=("high", "max"),
                low=("low", "min"), close=("close", "last"),
                volume=("volume", "sum")).reset_index()
    Dx = dict(D)
    t2 = agg["time"].values.astype("datetime64[s]")
    n2 = len(agg)
    fb2 = np.zeros(n2, bool); fb2[0] = True
    fb2[1:] = np.diff(agg["b"].values // 100000) != 0
    lb2 = np.zeros(n2, bool); lb2[:-1] = fb2[1:]; lb2[-1] = True
    sid2 = np.cumsum(fb2) - 1
    Dx.update(n=n2, t=t2, o=agg["open"].values, h=agg["high"].values, l=agg["low"].values,
              c=agg["close"].values, v=agg["volume"].values, fb=fb2, lb=lb2, sid=sid2,
              n_sess=sid2[-1] + 1)
    idx2 = np.arange(n2)
    last_of = np.zeros(Dx["n_sess"], np.int64)
    last_of[sid2[lb2]] = idx2[lb2]
    Dx["sess_end"] = t2[last_of] + np.timedelta64(minutes * 60, "s")
    tg2 = sm14_1m(Dx, max(1, 460 // minutes), return_targets=True, volmults=volmults)
    # map back: bar i on the 1-min clock uses the aggregate decision from the PREVIOUS bucket
    bmap = pd.Series(np.arange(n2), index=agg["b"].values)
    bi = bmap.reindex(bucket).values
    out = np.zeros(D["n"], np.int8)
    prev = np.where(bi > 0, bi - 1, 0)
    out[:] = tg2[prev]
    out[bi == 0] = 0
    return out


def orb_trades(D):
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    hm = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    trades = []
    pos = 0; epx = 0.0; eti = -1; hi = lo = np.nan; done = {1: False, -1: False}
    orb = []
    for i in range(n):
        if fb[i]:
            hi = lo = np.nan; done = {1: False, -1: False}; orb = []
        if 571 <= hm[i] <= 585:
            orb.append(i)
            if hm[i] == 585:
                hi = max(h[j] for j in orb); lo = min(l[j] for j in orb)
        if pos != 0 and (lb[i] or (not np.isnan(hi) and
                                   ((c[i - 1] < lo) if pos > 0 else (c[i - 1] > hi)))):
            px = c[i] if lb[i] else o[i]
            trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                               pnl=pos * (px - epx) * PV - COMM_RT))
            pos = 0
        if lb[i]:
            continue
        if pos == 0 and not np.isnan(hi) and i > 0 and hm[i] <= 950:
            if c[i - 1] > hi and not done[1]:
                pos = 1; epx, eti = o[i], i; done[1] = True
            elif c[i - 1] < lo and not done[-1]:
                pos = -1; epx, eti = o[i], i; done[-1] = True
    return trades


def vwaptrend_targets(D):
    n = D["n"]
    pv = 0.0; vv = 0.0
    vw = np.full(n, np.nan)
    for i in range(n):
        if D["fb"][i]:
            pv = 0.0; vv = 0.0
        pv += D["c"][i] * D["v"][i]; vv += D["v"][i]
        vw[i] = pv / vv if vv > 0 else np.nan
    slope = np.concatenate([[0.0], np.diff(vw)])
    tgt = np.zeros(n, np.int8)
    ok = ~np.isnan(vw)
    tgt[ok & (D["c"] > vw) & (slope > 0)] = 1
    tgt[ok & (D["c"] < vw) & (slope < 0)] = -1
    return np.concatenate([[0], tgt[:-1]]).astype(np.int8)


def true_delta_session(path):
    d = pd.read_parquet(path)
    d["time"] = pd.to_datetime(d["time"])
    tr = d[d.bip == 0].copy()
    bid = d[d.bip == 1][["time", "price"]].rename(columns={"price": "bid"})
    ask = d[d.bip == 2][["time", "price"]].rename(columns={"price": "ask"})
    tr = pd.merge_asof(tr.sort_values("time"), bid.sort_values("time"), on="time")
    tr = pd.merge_asof(tr, ask.sort_values("time"), on="time")
    sgn_ba = np.where(tr["price"] >= tr["ask"], 1, np.where(tr["price"] <= tr["bid"], -1, 0))
    dp = np.sign(np.diff(tr["price"].values, prepend=tr["price"].values[0]))
    last = 0; ud = np.zeros(len(tr), np.int8)
    for i in range(len(tr)):
        if dp[i] != 0:
            last = int(dp[i])
        ud[i] = last
    tr["m"] = tr["time"].dt.floor("min")
    tr["ba"] = sgn_ba * tr["volume"]
    tr["ud"] = ud * tr["volume"]
    tr["px_last"] = tr["price"]
    g = tr.groupby("m").agg(ba=("ba", "sum"), ud=("ud", "sum"),
                            close=("px_last", "last"), vol=("volume", "sum"))
    return g


def main():
    t0 = _time.time()
    D = load()
    n_sess, tarr = D["n_sess"], D["t"]
    idx = np.arange(D["n"])
    avail = np.zeros(n_sess)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        avail[s], _, _, _ = available_move(D["c"], m[0], m[-1] + 1)
    big = avail >= 500
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    ok08 = (norm <= 0) | (ratio >= 0.8)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    dL, dS = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)
    NAR = [6, 8, 10, 12, 14, 16]
    tgn = sm14_1m(D, 460, return_targets=True, volmults=NAR)
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    s4 = fills(D, tgn, allow_long=dL & ok08, allow_short=dS & ok08)
    print(f"bases ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "ortho.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    def wvec(trl):
        wt = week_table(trl, D, lambda x: x["xt"])
        d = {}
        for s, (net, _) in wt.items():
            d[D["wk"][s]] = d.get(D["wk"][s], 0.0) + net
        return wt, d

    wt1, wv1 = wvec(s1)
    wt4, wv4 = wvec(s4)
    port_wt = {}
    for src in (wt1, wt4):
        for s, (net, ntr) in src.items():
            a = port_wt.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
    port_wv = {}
    for s, (net, _) in port_wt.items():
        port_wv[D["wk"][s]] = port_wv.get(D["wk"][s], 0.0) + net
    rp = summarize(port_wt, D, "dev")
    P(f"PORTFOLIO (S1 + S4n.evidence): dev Sharpe {rp['sharpe']:.3f}  "
      f"mean ${rp['mean']:,.0f}  pos {rp['pos']:.1f}%  worst ${rp['worst']:,.0f}\n")

    def corr_with_port(d):
        ws = sorted(set(port_wv) | set(d))
        a = np.array([port_wv.get(w, 0.0) for w in ws])
        b = np.array([d.get(w, 0.0) for w in ws])
        return float(np.corrcoef(a, b)[0, 1])

    P("=== AXIS A: ORTHOGONAL SLEEVE HUNT ===")
    P(f"{'candidate':<14}{'n':>7}{'net':>12}{'wkMean':>8}{'wkShrp':>8}{'strs':>8}"
      f"{'corr':>7}  admission")
    cands = {}
    tg5 = agg_targets(D, 5, NAR)
    print(f"   5-min targets [{_time.time()-t0:.0f}s]", flush=True)
    tg15 = agg_targets(D, 15, NAR)
    print(f"   15-min targets [{_time.time()-t0:.0f}s]", flush=True)
    hm = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
          .astype(np.int64) // 60)
    asia = (hm >= 1080) | (hm <= 179)
    cands["C1_SOLAR5"] = fills(D, tg5, allow_long=dL & ok08, allow_short=dS & ok08)
    cands["C2_SOLAR15"] = fills(D, tg15, allow_long=dL & ok08, allow_short=dS & ok08)
    cands["C3_ORB"] = orb_trades(D)
    cands["C4_VWAPTREND"] = fills(D, vwaptrend_targets(D), allow_long=dL & ok08,
                                  allow_short=dS & ok08)
    cands["C5_ASIA"] = fills(D, tgn, allow_long=dL & ok08 & asia,
                             allow_short=dS & ok08 & asia)
    rows = []
    admitted = []
    for nm, trl in cands.items():
        if len(trl) < 100:
            P(f"{nm:<14}{len(trl):>7}  too few trades")
            continue
        wt, wv = wvec(trl)
        r = summarize(wt, D, "dev")
        st = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
        cr = corr_with_port(wv)
        adm = "PASS(i)" if st > 0 else "FAIL(i) stress<=0"
        if st > 0:
            adm = f"PASS(i,ii) corr {cr:.2f}" if abs(cr) < 0.30 else f"FAIL(ii) corr {cr:.2f}"
        P(f"{nm:<14}{len(trl):>7}{sum(x['pnl'] for x in trl):>12,.0f}{r['mean']:>8,.0f}"
          f"{r['sharpe']:>8.3f}{st:>8,.0f}{cr:>7.2f}  {adm}")
        rows.append(dict(axis="A", name=nm, n=len(trl), wk_mean=round(r["mean"]),
                         wk_sharpe=round(r["sharpe"], 3), stress=round(st),
                         corr=round(cr, 2), admission=adm))
        if st > 0 and abs(cr) < 0.30:
            admitted.append((nm, wt))
    P(f"\ncandidates passing (i)+(ii): {[a[0] for a in admitted] or 'NONE'}")
    for nm, wt in admitted:
        p2 = {s: list(v) for s, v in port_wt.items()}
        for s, (net, ntr) in wt.items():
            a = p2.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
        r2 = summarize(p2, D, "dev"); rh2 = summarize(p2, D, "hold")
        st2 = float((np.array(r2["_net"]) - STRESS_RT * np.array(r2["_ntr"])).mean())
        ok3 = (r2["sharpe"] > rp["sharpe"] and r2["worst"] >= rp["worst"] * 1.15)
        P(f"  + {nm:<12} -> portfolio Sharpe {r2['sharpe']:.3f} (was {rp['sharpe']:.3f})  "
          f"mean ${r2['mean']:,.0f}  worst ${r2['worst']:,.0f}  strs ${st2:,.0f}  "
          f"hold {rh2['sharpe']:.3f}  {'ADMITTED' if ok3 else 'REJECTED at (iii)'}")
        rows.append(dict(axis="A3", name=f"port+{nm}", wk_mean=round(r2["mean"]),
                         wk_sharpe=round(r2["sharpe"], 3), stress=round(st2),
                         admission="ADMITTED" if ok3 else "REJECTED(iii)"))

    # ---------------- AXIS B ----------------
    P("\n=== AXIS B: TRUE-DELTA VALIDATION (tick substrate) ===")
    files = sorted(glob.glob(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                          "raw", "NQ", "s2*.parquet")))
    files = [f for f in files if "_rth" not in os.path.basename(f)]
    agree_ba, agree_ud, corr_ba, corr_ud, nb = [], [], [], [], 0
    for f in files[:40]:
        try:
            g = true_delta_session(f)
        except Exception as e:                      # noqa: BLE001
            print(f"   skip {os.path.basename(f)}: {e}", flush=True)
            continue
        if len(g) < 200:
            continue
        cl = g["close"].values
        proxy = np.sign(np.diff(cl, prepend=cl[0])) * g["vol"].values
        for name, col, agl, crl in (("ba", "ba", agree_ba, corr_ba),
                                    ("ud", "ud", agree_ud, corr_ud)):
            tv = g[col].values
            m = (tv != 0) & (proxy != 0)
            if m.sum() > 50:
                agl.append(float((np.sign(tv[m]) == np.sign(proxy[m])).mean()))
                crl.append(float(np.corrcoef(np.cumsum(tv), np.cumsum(proxy))[0, 1]))
        nb += 1
    P(f"sessions used: {nb}")
    P(f"BidAsk-mode  vs proxy: bar sign-agreement {np.mean(agree_ba)*100:.1f}%  "
      f"cumulative-series corr {np.mean(corr_ba):.3f}")
    P(f"UpDownTick   vs proxy: bar sign-agreement {np.mean(agree_ud)*100:.1f}%  "
      f"cumulative-series corr {np.mean(corr_ud):.3f}")
    rows.append(dict(axis="B", name="fidelity_ba", corr=round(float(np.mean(corr_ba)), 3),
                     admission=f"agree {np.mean(agree_ba)*100:.1f}%"))
    rows.append(dict(axis="B", name="fidelity_ud", corr=round(float(np.mean(corr_ud)), 3),
                     admission=f"agree {np.mean(agree_ud)*100:.1f}%"))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
