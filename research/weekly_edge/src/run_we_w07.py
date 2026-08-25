"""WE_W07 DIRECTION (spec preregistered): attack the wrong-side + chop problem.

Primary readout is session-level (RIGHT / WRONG / CHOP / CAPTURE); weekly metrics are guards.
Every mask is causal and its known-at bar is documented in the spec.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, load, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                  # noqa: E402
from run_we_w06a import available_move                                    # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                     # noqa: E402
import inverse_core as IC                                                 # noqa: E402
from run_r13_strict_master import run_master                              # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W07_DIRECTION", "out")
os.makedirs(OUT, exist_ok=True)


def ema_np(x, p):
    a = 2.0 / (p + 1)
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def cross_agreement(D):
    """X1: sign(close - EMA20) on ES/RTY/YM at bar i-1, aligned to the NQ clock by timestamp."""
    base = pd.DataFrame({"time": pd.to_datetime(D["t"])})
    total = np.zeros(D["n"])
    for k, f in (("ES", "es"), ("RTY", "rty"), ("YM", "ym")):
        d = pd.read_parquet(os.path.join(ROOT, "runs", f"SM1M_{k}_SUBSTRATE", "out",
                                         f"{f}_1m_2022_2026.parquet"))
        d["time"] = pd.to_datetime(d["time"])
        c = d["close"].values.astype(float)
        s = np.sign(c - ema_np(c, 20))
        s = np.concatenate([[0.0], s[:-1]])            # lag one bar -> decision-bar info
        m = base.merge(pd.DataFrame({"time": d["time"], "s": s}), on="time", how="left")
        total += m["s"].fillna(0.0).values
        print(f"   {k} merged, {m['s'].notna().mean()*100:.1f}% coverage", flush=True)
    return total


def session_features(D):
    """X2 overnight, X3 opening range, X4 prior-session efficiency. All causal."""
    n, sid, n_sess = D["n"], D["sid"], D["n_sess"]
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    hm = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64))
    hhmm = (hm // 3600) * 100 + (hm // 60) % 60
    rth = (hhmm >= 931) & (hhmm <= 1700)
    x2 = np.zeros(n, np.int8)
    x3 = np.zeros(n, np.int8)
    eff = np.zeros(n_sess)
    idx = np.arange(n)
    for s in range(n_sess):
        m = idx[sid == s]
        cs = c[m]
        eff[s] = abs(cs[-1] - cs[0]) / max(np.abs(np.diff(cs)).sum(), 1e-9)
        on = m[hhmm[m] < 931]
        rt = m[(hhmm[m] >= 931) & (hhmm[m] <= 1700)]
        if len(on) > 10 and len(rt) > 0:
            mid = (h[on].max() + l[on].min()) / 2.0
            x2[rt] = 1 if o[rt[0]] > mid else -1
        if len(rt) > 20:
            orb = rt[:15]
            hi, lo = h[orb].max(), l[orb].min()
            after = rt[15:]
            x3[after] = np.where(c[after] > hi, 1, np.where(c[after] < lo, -1, 0))
            x3[after] = np.concatenate([[0], x3[after][:-1]])   # lag one bar
    # X4: chop flag per session = eff below trailing-60 33rd pct (excludes current session)
    chop = np.zeros(n_sess, bool)
    for s in range(20, n_sess):
        w = eff[max(0, s - 60):s]
        if len(w) >= 20:
            chop[s] = eff[s - 1] < np.percentile(w, 33)
    return x2, x3, chop[sid], rth


def session_metrics(D, trades, avail, adir, tarr):
    n_sess = D["n_sess"]
    bysess = {}
    for x in trades:
        i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))
        bysess.setdefault(int(D["sid"][i]), []).append(x)
    right = wrong = chop = notrade = 0
    cap = 0.0
    for s in range(n_sess):
        xs = bysess.get(s)
        if not xs:
            notrade += 1
            continue
        pts = sum(x["pnl"] for x in xs) / PV
        cap += pts
        netd = np.sign(sum(x["d"] for x in xs))
        if netd != 0 and adir[s] != 0 and netd != adir[s]:
            wrong += 1
        elif pts > 0:
            right += 1
        else:
            chop += 1
    f = 100.0 / n_sess
    return dict(RIGHT=round(right * f, 1), WRONG=round(wrong * f, 1), CHOP=round(chop * f, 1),
                NOTRADE=round(notrade * f, 1), CAPTURE=round(100 * cap / avail.sum(), 2),
                pts=round(cap))


def main():
    t0 = _time.time()
    D = load()
    tarr = D["t"]
    n_sess = D["n_sess"]
    idx = np.arange(D["n"])
    starts = np.zeros(n_sess, np.int64); ends = np.zeros(n_sess, np.int64)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        starts[s], ends[s] = m[0], m[-1] + 1
    avail = np.zeros(n_sess); adir = np.zeros(n_sess, np.int8)
    for s in range(n_sess):
        avail[s], adir[s], _, _ = available_move(D["c"], starts[s], ends[s])
    print(f"available ready [{_time.time()-t0:.0f}s]", flush=True)

    agree = cross_agreement(D)
    x2, x3, chopf, rth = session_features(D)
    print(f"features ready; chop sessions {100*chopf[starts].mean():.1f}% "
          f"[{_time.time()-t0:.0f}s]", flush=True)

    def lag(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL0, aS0 = lag(cd_arr >= 0), lag(cd_arr <= 0)

    NARROW = [6, 8, 10, 12, 14, 16]
    tgn = sm14_1m(D, 460, return_targets=True, volmults=NARROW)
    bb = IC.prepare(D["df"], SolarWaveParams())
    tr1_raw = run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)
    s1_trades = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]),
                      xt=str(bb["t"][x["xi"]])) for x in tr1_raw]
    print(f"bases ready [{_time.time()-t0:.0f}s]", flush=True)

    # masks (True = entry allowed)
    def cross_mask(K):
        okL = ~((agree <= -K) )
        okS = ~((agree >= K))
        return okL, okS
    masks = {"BASE": (aL0, aS0)}
    for K in (2, 3):
        cl, cs = cross_mask(K)
        masks[f"T1_cross{K}"] = (aL0 & cl, aS0 & cs)
    masks["T2_on"] = (aL0 & ~((x2 == -1) & rth), aS0 & ~((x2 == 1) & rth))
    masks["T3_or"] = (aL0 & ~((x3 == -1) & rth), aS0 & ~((x3 == 1) & rth))
    masks["T4_eff"] = (aL0 & ~chopf, aS0 & ~chopf)

    out = open(os.path.join(OUT, "direction.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    P(f"available {avail.sum():,.0f} pts over {n_sess} sessions "
      f"({avail.mean():.1f}/session)\n")
    P(f"{'variant':<16}{'RIGHT':>7}{'WRONG':>7}{'CHOP':>7}{'NOTR':>7}{'CAPT%':>7}"
      f"{'pts':>9}{'wkMean':>9}{'wkPos':>7}{'wkWorst':>10}{'wkShrp':>8}{'stress':>8}")
    rows = []
    results = {}
    for nm, (aL, aS) in masks.items():
        trl = fills(D, tgn, allow_long=aL, allow_short=aS)
        sm_ = session_metrics(D, trl, avail, adir, tarr)
        wt = week_table(trl, D, lambda x: x["xt"])
        r = summarize(wt, D, "dev")
        stress = np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])
        results[nm] = (trl, wt, sm_, r)
        P(f"{nm:<16}{sm_['RIGHT']:>7}{sm_['WRONG']:>7}{sm_['CHOP']:>7}{sm_['NOTRADE']:>7}"
          f"{sm_['CAPTURE']:>7}{sm_['pts']:>9,}{r['mean']:>9,.0f}{r['pos']:>7.1f}"
          f"{r['worst']:>10,.0f}{r['sharpe']:>8.3f}{stress.mean():>8,.0f}")
        rows.append(dict(base="S4n.gdl", variant=nm, **sm_, wk_mean=round(r["mean"]),
                         wk_pos=round(r["pos"], 1), wk_worst=round(r["worst"]),
                         wk_sharpe=round(r["sharpe"], 3),
                         stress=round(float(stress.mean()))))

    # T5 STACK, formed BY THE RULE: components that raise RIGHT without breaking guards
    base_sm = results["BASE"][2]; base_r = results["BASE"][3]
    picked = []
    for nm in ("T1_cross2", "T1_cross3", "T2_on", "T3_or", "T4_eff"):
        s_, r_ = results[nm][2], results[nm][3]
        if (s_["RIGHT"] > base_sm["RIGHT"] and r_["sharpe"] >= base_r["sharpe"] - 0.02
                and r_["worst"] >= base_r["worst"] * 1.15):
            picked.append(nm)
    P(f"\nT5 stack components selected BY THE RULE: {picked if picked else 'NONE'}")
    if picked:
        aL, aS = aL0.copy(), aS0.copy()
        for nm in picked:
            aL &= masks[nm][0]; aS &= masks[nm][1]
        trl = fills(D, tgn, allow_long=aL, allow_short=aS)
        sm_ = session_metrics(D, trl, avail, adir, tarr)
        wt = week_table(trl, D, lambda x: x["xt"])
        r = summarize(wt, D, "dev")
        rh = summarize(wt, D, "hold")
        stress = np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])
        P(f"{'T5_stack':<16}{sm_['RIGHT']:>7}{sm_['WRONG']:>7}{sm_['CHOP']:>7}"
          f"{sm_['NOTRADE']:>7}{sm_['CAPTURE']:>7}{sm_['pts']:>9,}{r['mean']:>9,.0f}"
          f"{r['pos']:>7.1f}{r['worst']:>10,.0f}{r['sharpe']:>8.3f}{stress.mean():>8,.0f}")
        P(f"   holdout: mean {rh['mean']:,.0f}  pos {rh['pos']:.1f}%  "
          f"sharpe {rh['sharpe']:.3f}  worst {rh['worst']:,.0f}")
        rows.append(dict(base="S4n.gdl", variant="T5_stack", **sm_, wk_mean=round(r["mean"]),
                         wk_pos=round(r["pos"], 1), wk_worst=round(r["worst"]),
                         wk_sharpe=round(r["sharpe"], 3),
                         stress=round(float(stress.mean()))))
        # portfolio with S1
        p = {}
        for src in (week_table(s1_trades, D, lambda x: x["xt"]), wt):
            for s, (net, ntr) in src.items():
                a = p.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
        rp, rph = summarize(p, D, "dev"), summarize(p, D, "hold")
        P(f"\nS1 + T5_stack   dev mean {rp['mean']:,.0f}  pos {rp['pos']:.1f}%  "
          f"worst {rp['worst']:,.0f}  sharpe {rp['sharpe']:.3f}   |   "
          f"hold mean {rph['mean']:,.0f}  pos {rph['pos']:.1f}%  sharpe {rph['sharpe']:.3f}")

    # S1 base session metrics for reference
    sm1 = session_metrics(D, s1_trades, avail, adir, tarr)
    P(f"\n{'S1 (ref)':<16}{sm1['RIGHT']:>7}{sm1['WRONG']:>7}{sm1['CHOP']:>7}"
      f"{sm1['NOTRADE']:>7}{sm1['CAPTURE']:>7}{sm1['pts']:>9,}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
