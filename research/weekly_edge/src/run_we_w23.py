"""WE_W23 PRODUCTION (spec preregistered): attack the weekly-dollar gap where it actually is."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly, sharpe                       # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W23_PRODUCTION", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
HIS_WORST = -42235.0
HIS_WEEK = 8583.0


def signed_fills(D, size_arr, halt=None):
    """size_arr carries the SIGNED desired position (… -1, 0, +1 …). Session halt optional."""
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    p = 0; epx = 0.0; eti = -1; spnl = 0.0; halted = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; halted = False
        want = int(size_arr[i - 1]) if i > 0 and not fb[i] else 0
        if halted:
            want = 0
        if want != p:
            if p != 0:
                u = abs(p)
                pnl = np.sign(p) * u * (o[i] - epx) * PV - COMM_RT * u
                trades.append(dict(d=int(np.sign(p)), u=u, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pnl))
                spnl += pnl
                if halt is not None and spnl <= -halt:
                    halted = True; want = 0
            p = want
            if p != 0:
                epx, eti = o[i], i
        if lb[i] and p != 0:
            u = abs(p)
            pnl = np.sign(p) * u * (c[i] - epx) * PV - COMM_RT * u
            trades.append(dict(d=int(np.sign(p)), u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0
    return trades


def build_side_paths(D, side):
    """32 config position paths for one side ('long' or 'short')."""
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL, dS = lag_b(cd >= 0), lag_b(cd <= 0)
    TG = {k: sm14_1m(D, 460, return_targets=True, volmults=v) for k, v in MEMBERS.items()}
    paths, blocked = {}, {}
    for mem in MEMBERS:
        for q in QS:
            for dg in (True, False):
                okq = np.ones(D["n"], bool) if q is None else ((norm <= 0) | (ratio >= q))
                tg = TG[mem]
                if side == "long":
                    a = okq & (dL if dg else True)
                    paths[(mem, q, dg)] = np.where((tg > 0) & a, 1, 0).astype(np.int8)
                    blocked[(mem, q, dg)] = np.where((tg > 0) & ~okq, 1, 0).astype(np.int8)
                else:
                    a = okq & (dS if dg else True)
                    paths[(mem, q, dg)] = np.where((tg < 0) & a, -1, 0).astype(np.int8)
                    blocked[(mem, q, dg)] = np.where((tg < 0) & ~okq, -1, 0).astype(np.int8)
    return paths, blocked, ratio, norm


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    pl, bl, ratio, norm = build_side_paths(D, "long")
    ps, bs, _, _ = build_side_paths(D, "short")
    fl = np.vstack([pl[k] for k in pl]).mean(axis=0)
    fs = -np.vstack([ps[k] for k in ps]).mean(axis=0)          # fraction voting short
    fbl = np.vstack([bl[k] for k in bl]).mean(axis=0)
    print(f"paths ready [{_time.time()-t0:.0f}s]", flush=True)
    tarr = D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), D["n"] - 1))
        return wkmap[int(D["sid"][i])]

    out = open(os.path.join(OUT, "prod.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []

    def rep(nm, d, note=""):
        s, net, pos = sharpe(d)
        v = np.array(list(d.values()))
        P(f"{nm:<32}{len(v):>7}{net:>12,.0f}{v.mean():>9,.0f}{pos:>8.1f}{v.min():>10,.0f}"
          f"{s:>8.3f}  {note}")
        rows.append(dict(name=nm, net=round(net), wk_mean=round(v.mean()),
                         pos=round(pos, 1), worst=round(v.min()), sharpe=round(s, 3)))
        return s, float(v.min()), float(v.mean())

    P(f"{'variant':<32}{'weeks':>7}{'net':>12}{'wkMean':>9}{'pos%':>8}{'worst':>10}"
      f"{'sharpe':>8}")
    L = (fl >= 0.5).astype(np.int8)
    e5h = signed_fills(D, L, halt=1300)
    d_e5 = weekly(e5h, wk_of, A, B)
    s_e5, w_e5, m_e5 = rep("E5halt1300 (1 contract, long)", d_e5)
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    d_s1 = weekly(s1, wk_of, A, B)
    d_pair = {w: d_e5.get(w, 0.0) + d_s1.get(w, 0.0) for w in set(d_e5) | set(d_s1)}
    s_p, w_p, m_p = rep("E5halt1300 + S1 (<=2)", d_pair)

    P("\n--- Q1 SHORT-SIDE VOTE as an independent sleeve ---")
    S = -(fs >= 0.5).astype(np.int8)
    for H in (None, 1300):
        trl = signed_fills(D, S, halt=H)
        d = weekly(trl, wk_of, A, B)
        tag = f"SHORT vote halt {H if H else 'none'}"
        rep(tag, d)
        dcomb = {w: d_e5.get(w, 0.0) + d.get(w, 0.0) for w in set(d_e5) | set(d)}
        s2, w2, m2 = rep(f"  E5halt + {tag}", dcomb)
        gain = 100 * (m2 - m_e5) / abs(m_e5)
        deg = 100 * (w_e5 - w2) / abs(w_e5)
        P(f"     production +{gain:.1f}% vs tail degradation {deg:+.1f}% -> "
          f"{'ADOPT' if (s2 > s_e5 and deg < gain) else 'reject'}")
        d3 = {w: d_pair.get(w, 0.0) + d.get(w, 0.0) for w in set(d_pair) | set(d)}
        rep(f"  E5halt + S1 + {tag}", d3)

    P("\n--- Q2 THROTTLE COST: what the blocked bars would have produced ---")
    Lall = (np.vstack([pl[k] for k in pl]).mean(axis=0) >= 0.5)
    Lblk = (fbl >= 0.5)
    only_blocked = (Lblk & ~Lall).astype(np.int8)
    d_blk = weekly(signed_fills(D, only_blocked, halt=1300), wk_of, A, B)
    rep("throttled-away production only", d_blk)
    for frac_size, tag in ((0, "size 0 (current)"), (1, "size 1 (no throttle)")):
        arr = (Lall.astype(np.int8) if frac_size == 0
               else np.maximum(Lall.astype(np.int8), only_blocked))
        rep(f"  throttled regime at {tag}", weekly(signed_fills(D, arr, halt=1300),
                                                   wk_of, A, B))

    P("\n--- Q3 EXPOSURE LADDER (Sharpe is exposure-invariant; the tail is not) ---")
    P(f"{'contracts':<12}{'wkMean':>10}{'worst':>12}{'annual~':>12}")
    for k in (1, 2, 3, 4, 5):
        P(f"{k:<12}{k*m_p:>10,.0f}{k*w_p:>12,.0f}{k*m_p*52:>12,.0f}")

    P("\n--- Q4 MATCHED-TAIL BENCHMARK vs his displayed record ---")
    k_match = HIS_WORST / w_p
    P(f"his displayed: ${HIS_WEEK:,.0f}/wk with worst week ${HIS_WORST:,.0f} "
      f"(GROSS, in-sample sheets, version-churned, display-selected - R34)")
    P(f"ours at matched tail: {k_match:.1f} contracts -> ${k_match*m_p:,.0f}/wk NET, "
      f"full 205-week sample, frozen, no runtime selection")
    P(f"efficiency per unit of tail: his {HIS_WEEK/abs(HIS_WORST):.3f} vs "
      f"ours {m_p/abs(w_p):.3f} ({HIS_WEEK/abs(HIS_WORST)/(m_p/abs(w_p)):.2f}x)")
    P("ASYMMETRY RESTATED: his numerator is gross and curated; ours is net and complete.")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
