"""WE_W44 NT8 PARITY (spec preregistered): is the hand-transcribed 1-minute port correct?

Every number in this campaign rests on `sm14_1m`, a Python port of SolarWaveOneContractNQ_v5
transcribed by hand in W01. Every B1 check since has compared new code AGAINST that port,
which validates the new code and not the port. This run compares the port against the ORIGINAL
C# executed by NinjaTrader's own Strategy Analyzer engine on the same instrument and window.

Primary comparison is the DECISION SERIES (fraction of bars on which the two objects hold the
same position), because P&L can agree by luck and a decision series cannot.
"""
from __future__ import annotations

import ast
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, sm14_1m                        # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W44_NT8PARITY", "out")
os.makedirs(OUT, exist_ok=True)


def main():
    nt = pd.read_csv(os.path.join(OUT, "nt8_trades.csv"))
    ent = [ast.literal_eval(x) for x in nt["entry"]]
    exi = [ast.literal_eval(x) for x in nt["exit"]]
    nt8 = pd.DataFrame(dict(
        et=[pd.Timestamp(e["time"]) for e in ent],
        xt=[pd.Timestamp(x["time"]) for x in exi],
        epx=[e["price"] for e in ent], xpx=[x["price"] for x in exi],
        dirn=[1 if e["market_position"] == "Long" else -1 for e in ent],
        pnl=nt["ProfitCurrency"].values - nt["Commission"].values))
    nt8 = nt8.sort_values("et").reset_index(drop=True)
    a, b = nt8["et"].min(), nt8["xt"].max()
    out = open(os.path.join(OUT, "parity.txt"), "w", encoding="utf-8")

    def P_(*x):
        print(*x, flush=True); print(*x, file=out)
    P_(f"=== NT8 Strategy Analyzer (SolarWaveOneContractNQ_v5, shipped defaults) ===")
    P_(f"   backtest spans {a} -> {b}; comparison restricted to the WARM window below")

    # W44 amendment 1: the port needs the SAME warm-up the C# gets. sigma needs 460
    # bars, the HTF tilt needs 50 session closes and B-MOM needs 14 RTH days, so both
    # engines are only comparable well after their own first bar. The port is loaded
    # from 2025-11 and the comparison is restricted to WARM below.
    D = load_deep("2025-11-01", "2026-07-31 17:00")
    tarr = D["t"]
    tg = sm14_1m(D, 460, return_targets=True)
    # port fills: decision at bar i, next-bar-open fill (the campaign's own convention)
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    rows = []
    p = 0; epx = 0.0; eti = -1
    for i in range(n):
        want = int(tg[i - 1]) if i > 0 and not fb[i] else 0
        if want != p:
            if p != 0:
                rows.append(dict(et=pd.Timestamp(str(t[eti])), xt=pd.Timestamp(str(t[i])),
                                 epx=epx, xpx=o[i], dirn=p,
                                 pnl=p * (o[i] - epx) * PV - COMM_RT))
            p = want
            if p != 0:
                epx, eti = o[i], i
        if lb[i] and p != 0:
            rows.append(dict(et=pd.Timestamp(str(t[eti])), xt=pd.Timestamp(str(t[i])),
                             epx=epx, xpx=c[i], dirn=p,
                             pnl=p * (c[i] - epx) * PV - COMM_RT))
            p = 0
    py = pd.DataFrame(rows)
    WARM = pd.Timestamp("2026-04-01")
    a = max(a, WARM)
    nt8 = nt8[(nt8["et"] >= a) & (nt8["et"] <= b)].reset_index(drop=True)
    py = py[(py["et"] >= a) & (py["et"] <= b)].reset_index(drop=True)
    py.to_csv(os.path.join(OUT, "py_trades.csv"), index=False)
    P_(f"\n=== Python port sm14_1m(D, 460) on the same window ===")
    P_(f"   {len(py)} trades | net ${py['pnl'].sum():,.2f} | long "
       f"{int((py['dirn'] > 0).sum())} / short {int((py['dirn'] < 0).sum())}")

    # ---- decision series ---------------------------------------------------------------
    m = (tarr >= np.datetime64(a)) & (tarr <= np.datetime64(b))
    idx = np.where(m)[0]
    pos_py = np.zeros(len(idx), np.int8)
    p = 0
    for k, i in enumerate(idx):
        want = int(tg[i - 1]) if i > 0 and not fb[i] else 0
        if fb[i]:
            p = 0
        p = want
        pos_py[k] = p
    pos_nt = np.zeros(len(idx), np.int8)
    ts = pd.to_datetime(tarr[idx])
    for _, r in nt8.iterrows():
        sel = (ts >= r["et"]) & (ts < r["xt"])
        pos_nt[np.asarray(sel)] = r["dirn"]
    agree = float((pos_py == pos_nt).mean() * 100)
    both_in = ((pos_py != 0) & (pos_nt != 0))
    same_dir = float((pos_py[both_in] == pos_nt[both_in]).mean() * 100) if both_in.sum() else 0
    P_(f"\n=== DECISION SERIES over {len(idx):,} 1-minute bars ===")
    P_(f"   identical position on {agree:.2f} % of bars")
    P_(f"   NT8 in the market {100*(pos_nt != 0).mean():.1f} % | port "
       f"{100*(pos_py != 0).mean():.1f} % | both in the market together "
       f"{100*both_in.mean():.1f} % (same direction on {same_dir:.1f} % of those)")
    dis = np.where(pos_py != pos_nt)[0]
    if len(dis):
        P_(f"\n   first 12 disagreement runs:")
        runs = np.split(dis, np.where(np.diff(dis) != 1)[0] + 1)
        for r in runs[:12]:
            P_(f"     {ts[r[0]]} -> {ts[r[-1]]}  ({len(r)} bars)  "
               f"port {pos_py[r[0]]:+d} vs NT8 {pos_nt[r[0]]:+d}")
        P_(f"   total disagreement runs: {len(runs)}, median length "
           f"{int(np.median([len(r) for r in runs]))} bars")
    P_(f"\n=== PREREGISTERED VERDICT ===")
    dn = abs(len(py) - len(nt8)) / max(len(nt8), 1) * 100
    v = ("PORT VALIDATED" if agree >= 99 and dn <= 2 else
         ("PORT MOSTLY RIGHT - disagreement localised, report before proceeding"
          if agree >= 90 else "PORT SUSPECT - resolving this outranks all new research"))
    P_(f"   decision agreement {agree:.2f} % | trade-count difference {dn:.1f} % -> {v}")
    out.close()


if __name__ == "__main__":
    main()
