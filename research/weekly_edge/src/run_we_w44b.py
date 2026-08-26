"""WE_W44 amendment 1: the port is not wrong, it is on a DIFFERENT CLOCK - and now we can test that.

The C# reads `AddDataSeries(SignalInstrument, BarsPeriodType.Minute, 3)` and drives its entire
decision stack from `BarsInProgress == 1`, i.e. the Solar ratchet runs on THREE-MINUTE bars and
only the execution happens on the primary series. `sm14_1m` runs the same stack on ONE-MINUTE
bars - a declared W01 port choice ("VolPeriod counted in 1-min bars"), but a 3x finer clock.

Predicted consequences, all of which read 1 observed: the port trades ~2.6x more often, holds
shorter, is in the market less, and agrees on DIRECTION 80.7 % of the time when both are in.

This run tests the implication: does the port on a 3-MINUTE clock reproduce the C#?
Two anchorings are tried because NT8's grid and the port's are not obviously the same:
  (a) the W41 anchoring, where a bar boundary falls on the 09:31 bar
  (b) plain session-start anchoring, which is what NT8's standard grid does
The data has already been proven identical: NT8's prices differ from the parquet's by a
CONSTANT -282.25 points with standard deviation 0.00, and every quantity in the ratchet is a
price DIFFERENCE, so a constant offset cannot change a single decision.
"""
from __future__ import annotations

import ast
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, sm14_1m                                     # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from we_clocks import _pack, expand                                      # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W44_NT8PARITY", "out")
WARM = pd.Timestamp("2026-04-01")


def clock3(D, anchor_0931):
    hm = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
          .astype(np.int64))
    hhmmss = (hm // 3600) * 10000 + ((hm // 60) % 60) * 100
    idx = np.arange(D["n"])
    groups = []
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        if anchor_0931:
            a = np.where(hhmmss[m] == 93100)[0]
            a0 = int(a[0]) if len(a) else 0
        else:
            a0 = 0
        g = np.arange(len(m)) - a0
        blk = np.floor_divide(g + 2, 3)
        for b in np.unique(blk):
            groups.append(m[blk == b])
    return _pack(D, groups)


def main():
    nt = pd.read_csv(os.path.join(OUT, "nt8_trades.csv"))
    ent = [ast.literal_eval(x) for x in nt["entry"]]
    exi = [ast.literal_eval(x) for x in nt["exit"]]
    nt8 = pd.DataFrame(dict(et=[pd.Timestamp(e["time"]) for e in ent],
                            xt=[pd.Timestamp(x["time"]) for x in exi],
                            dirn=[1 if e["market_position"] == "Long" else -1 for e in ent]))
    nt8 = nt8[nt8["et"] >= WARM].sort_values("et").reset_index(drop=True)
    b = nt8["xt"].max()
    out = open(os.path.join(OUT, "parity_b.txt"), "w", encoding="utf-8")

    def P_(*x):
        print(*x, flush=True); print(*x, file=out)
    P_("=== THE C# RUNS ITS DECISION STACK ON A 3-MINUTE SECONDARY SERIES ===")
    P_("   SolarWaveOneContractNQ_v5.cs line 150: "
       "AddDataSeries(SignalInstrument, BarsPeriodType.Minute, 3)")
    P_("   line 367: `if (BarsInProgress != 1) return;` - the whole stack is driven by the")
    P_("   3-minute series; only execution happens on the primary series.")
    P_("   sm14_1m runs the same stack on 1-MINUTE bars (a declared W01 port choice).")
    P_(f"\n   data already proven identical: constant basis -282.25 pts, std 0.00, and every")
    P_(f"   quantity in the ratchet is a price DIFFERENCE, so the offset changes no decision.")

    D = load_deep("2025-11-01", "2026-07-31 17:00")
    tarr = D["t"]
    m = (tarr >= np.datetime64(WARM)) & (tarr <= np.datetime64(b))
    idx = np.where(m)[0]
    ts = pd.to_datetime(tarr[idx])
    pos_nt = np.zeros(len(idx), np.int8)
    for _, r in nt8.iterrows():
        pos_nt[np.asarray((ts >= r["et"]) & (ts < r["xt"]))] = r["dirn"]

    def score(nm, tg):
        pos = np.zeros(D["n"], np.int8)
        for i in range(D["n"]):
            pos[i] = 0 if D["fb"][i] else int(tg[i - 1]) if i > 0 else 0
        pp = pos[idx]
        agree = float((pp == pos_nt).mean() * 100)
        bi = (pp != 0) & (pos_nt != 0)
        sd = float((pp[bi] == pos_nt[bi]).mean() * 100) if bi.sum() else 0.0
        flips = int((np.diff(pp) != 0).sum())
        P_(f"{nm:<34}{agree:>9.2f}{100*(pp != 0).mean():>10.1f}{100*bi.mean():>10.1f}"
           f"{sd:>10.1f}{flips:>9}")
        return agree

    P_(f"\n{'port variant':<34}{'agree%':>9}{'inMkt%':>10}{'bothIn%':>10}{'sameDir%':>10}"
       f"{'flips':>9}")
    nt_flips = int((np.diff(pos_nt) != 0).sum())
    P_(f"{'NT8 reference':<34}{100.0:>9.2f}{100*(pos_nt != 0).mean():>10.1f}"
       f"{'-':>10}{'-':>10}{nt_flips:>9}")
    best = ("1-min", score("port on 1-min (incumbent)", sm14_1m(D, 460, return_targets=True)))
    for anc, lab in ((True, "3-min, anchored at 09:31"), (False, "3-min, session-anchored")):
        Dc, ec = clock3(D, anc)
        for vp, vlab in ((460, "sigma=460 bars"), (153, "sigma=153 bars (=460/3 wall-clock)")):
            tgc = sm14_1m(Dc, vp, return_targets=True)
            a_ = score(f"{lab}, {vlab}", expand(tgc, ec, D["n"]))
            if a_ > best[1]:
                best = (f"{lab}, {vlab}", a_)
    P_(f"\n=== BEST: {best[0]} at {best[1]:.2f} % decision agreement ===")
    P_("   verdict thresholds from the spec: >=99 % validated | 90-99 % mostly right | "
       "<90 % suspect")
    out.close()


if __name__ == "__main__":
    main()
