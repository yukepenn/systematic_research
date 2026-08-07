"""B01e — DR05-H5 gap-fade NULL control (seq 231). Preregistered negative
control: fading NQ RTH opening gaps >= 0.35% (09:30 ET open vs prior 16:00 ET
close) toward the prior close, fixed 11:30 ET time stop, has NO after-cost edge.
Null CONFIRMED if avg trade < $55 at slip-1 or < 4/5 years positive.
Constants frozen in DR-05.md; no adjustment permitted.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BARS = os.path.join(ROOT, "runs", "B01A_BARS_1M", "nq_1m_2022_2026.csv")
TICK, PV, RT = 0.25, 20.0, 4.36


def main():
    bars = pd.read_csv(BARS, parse_dates=["time"])
    bars["date"] = bars.time.dt.date
    m = bars.time.dt.hour * 60 + bars.time.dt.minute
    rows = []
    prior_close = None
    prior_day = None
    for d, g in bars.groupby("date"):
        gm = m.loc[g.index]
        c1600 = g.loc[gm[gm == 960].index]          # bar closing 16:00
        open930 = g.loc[gm[gm == 571].index]        # bar closing 09:31 (open ~09:30)
        if prior_close is not None and len(open930):
            o = open930.iloc[0].open
            gap = (o - prior_close) / prior_close
            if abs(gap) >= 0.0035:
                side = -np.sign(gap)                 # fade toward prior close
                entry = o + (TICK if side > 0 else -TICK)   # slip-1
                stop_idx = gm[gm == 690].index       # bar closing 11:30
                seg = g.loc[open930.index[0]:(stop_idx[0] if len(stop_idx) else g.index[-1])]
                tgt = prior_close
                exit_px = None
                for r in seg.itertuples():
                    if r.low <= tgt <= r.high:
                        exit_px = tgt
                        break
                if exit_px is None:
                    exit_px = seg.iloc[-1].close
                exit_px -= (TICK if side > 0 else -TICK)
                rows.append(dict(date=d, year=pd.Timestamp(d).year,
                                 gap_pct=round(100 * gap, 3), side=int(side),
                                 pnl=round(side * (exit_px - entry) * PV - RT, 2)))
        if len(c1600):
            prior_close, prior_day = c1600.iloc[0].close, d
    tr = pd.DataFrame(rows)
    yr = tr.groupby("year").pnl.sum()
    avg = tr.pnl.mean()
    pos = int((yr > 0).sum())
    confirmed = bool(avg < 55 or pos < 4)
    print(f"n {len(tr)} | net ${tr.pnl.sum():,.2f} | avg ${avg:.2f} | "
          f"pos-years {pos}/{len(yr)}")
    print("yearly: " + "  ".join(f"{y}:{v:,.0f}" for y, v in yr.items()))
    print(f"NULL {'CONFIRMED' if confirmed else 'REJECTED - escalate with fresh prereg'}")
    tr.to_csv(os.path.join(ROOT, "research", "04_complementary_family",
                           "b01e_gap_trades.csv"), index=False)


if __name__ == "__main__":
    main()
