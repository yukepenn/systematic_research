"""Bisect SM14 OneLot ops-window semantics to reproduce results.csv row 318 exactly."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "src/analytics")
from sm01_solarsim import load_bars_3m, _fill

MNQ_COMM, MNQ_PV = 0.65, 2.0

def onelot(bars, M, a, b, comm, pv, exits_in_window=False, block_gt_1630=False):
    n = len(bars)
    o = bars["open"].to_numpy(); h = bars["high"].to_numpy()
    l = bars["low"].to_numpy(); c = bars["close"].to_numpy()
    last = bars["is_last_of_sess"].to_numpy()
    hm = bars["time"].dt.hour.to_numpy() * 100 + bars["time"].dt.minute.to_numpy()
    cash = 0.0; p = 0; pend = 0
    fills = 0; entries = 0
    daily = {}; prev_eq = 0.0
    sd = bars["sess_date"].to_numpy()
    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv; cash -= abs(d) * comm
            if (p == 0 and pend != 0) or (p != 0 and pend != 0 and np.sign(pend) != np.sign(p)):
                entries += 1
            p = pend; fills += 1
        if last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv; cash -= abs(p) * comm
            fills += 1; p = 0; pend = 0
        else:
            m = M[t]; tgt = p
            blocked_entry = (hm[t] > 1630 if block_gt_1630 else hm[t] >= 1630) and hm[t] < 1803
            if hm[t] == 1639:
                tgt = 0
            elif blocked_entry:
                if p != 0 and exits_in_window and hm[t] < 1639:
                    if p == 1 and m <= b: tgt = 0
                    if p == -1 and m >= -b: tgt = 0
                elif p != 0 and hm[t] > 1639:
                    tgt = 0
                else:
                    tgt = p
            else:
                if p == 0:
                    tgt = 1 if m >= a else (-1 if m <= -a else 0)
                elif p == 1:
                    tgt = -1 if m <= -a else (0 if m <= b else 1)
                else:
                    tgt = 1 if m >= a else (0 if m >= -b else -1)
            pend = tgt
        if last[t]:
            eq = cash + p * c[t] * pv
            daily[sd[t]] = eq - prev_eq; prev_eq = eq
    dl = pd.Series(daily)
    eqd = dl.cumsum(); mdd = (eqd.cummax() - eqd).max()
    return dl.sum(), fills, entries, mdd

bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = sess <= pd.Timestamp("2026-05-31")
bars_dev = bars[dev].reset_index(drop=True)
M = np.load("runs/SM14_ONELOT_DAYMARGIN/out/M_target.npy")[dev.to_numpy()]

print("target: net 27287, trades 4039, maxDD 6374")
for ew in (False, True):
    for bg in (False, True):
        net, fills, entries, mdd = onelot(bars_dev, M, 3, 1, MNQ_COMM, MNQ_PV, ew, bg)
        print(f"exits_in_window={ew} block>1630={bg}: net={net:.0f} fills={fills} entries={entries} maxDD={mdd:.0f}")
