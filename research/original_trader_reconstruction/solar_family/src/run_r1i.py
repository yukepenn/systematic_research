"""r1i: FIRST-BAR BREAKOUT GATE — deferred always-in-intent model.

Model: intent = Solar wave direction (T1 flips). Position realized only when the
decision bar's CLOSE is beyond the session FIRST BAR's extreme in the intent
direction (long: close > firstbar.high; short: close < firstbar.low). Holding
positions exit on inclusive TS-touch (reverse only if the new direction passes the
gate at that close, else flat+deferred). Session-close flat. No T2/T3 signals needed.
"""
import json
import os
import sys
from collections import defaultdict
from itertools import combinations

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, POINT_VALUE, BARS_REQUIRED  # noqa: E402
from solarwave import SolarWaveParams, solar_wave  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")
print("[r1i] ledger + ladder ...", flush=True)
b = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
core = solar_wave(b["close"], SolarWaveParams(), start_up=False)
n = b["n"]
opn, close, high, low = b["open"], b["close"], b["high"], b["low"]
first_bar, last_bar = b["first_bar"], b["last_bar"]
tarr = b["time"]
ts_arr = core.trailing_stop
is_up = core.is_up.astype(bool)
sig = core.signal_trade.astype(np.int64)


def run_fbgate(strict=True, comm_side=2.09):
    trades = []
    pos = 0; epx = 0.0; ei = -1
    pend_entry = 0; pend_exit = False; pend_rev = 0
    fb_hi = np.nan; fb_lo = np.nan

    def realize(i, p, kind):
        nonlocal pos
        pnl = pos * (p - epx) * POINT_VALUE - 2 * comm_side
        trades.append({"dir": pos, "ei": ei, "xi": i, "et": str(tarr[ei]), "xt": str(tarr[i]),
                       "pnl": pnl, "kind": kind,
                       "hold": float((tarr[i] - tarr[ei]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        pos = 0

    def gate(d, i):
        if np.isnan(fb_hi):
            return False
        if d > 0:
            return close[i] > fb_hi if strict else close[i] >= fb_hi
        return close[i] < fb_lo if strict else close[i] <= fb_lo

    for i in range(n):
        # fills first
        if pend_exit and pos != 0:
            realize(i, opn[i], "flip")
            pend_exit = False
        if pend_rev != 0:
            if pos != 0:
                realize(i, opn[i], "flip")
            pos = pend_rev
            epx, ei = opn[i], i
            pend_rev = 0
        if pend_entry != 0 and pos == 0:
            pos = pend_entry
            epx, ei = opn[i], i
            pend_entry = 0
        pend_entry = 0

        if first_bar[i]:
            fb_hi, fb_lo = high[i], low[i]

        intent = 1 if is_up[i] else -1

        if last_bar[i]:
            if pos != 0:
                realize(i, close[i], "sc")
            pend_exit = False
            pend_entry = 0
            pend_rev = 0
            continue

        if first_bar[i] or i < BARS_REQUIRED:
            continue

        # holding: exit on inclusive TS touch (flip bars included)
        if pos != 0:
            line = ts_arr[i]
            if not np.isnan(line):
                hit = (pos > 0 and close[i] <= line) or (pos < 0 and close[i] >= line)
                if hit:
                    if intent == -pos and gate(intent, i):
                        pend_rev = intent
                    else:
                        pend_exit = True
                    continue

        # flat: deferred realization when gate passes in intent direction
        if pos == 0 and gate(intent, i):
            pend_entry = intent
    return trades


TGT = {"2023-01-03": (4, 5863.28, 8, -6163.44, 3050.82, -1179.18),
       "2023-01-04": (5, 3859.10, 9, -5007.60, 1865.82, -899.18),
       "2023-01-05": (2, 2611.64, 4, -2641.72, 2310.82, -889.18),
       "2023-01-06": (5, 6314.10, 5, -3320.90, 4210.82, -1384.18),
       "2023-01-09": (2, 6116.64, 1, -854.18, 3170.82, -854.18),
       "2023-01-10": (5, 3744.10, 4, -2551.72, 1370.82, -1084.18),
       "2023-01-11": (2, 3106.64, 2, -1338.36, 2190.82, -749.18),
       "2023-01-12": (5, 4704.10, 11, -8025.98, 1535.82, -1204.18),
       "2023-01-13": (3, 3337.46, 3, -1912.54, 1885.82, -809.18),
       "2023-01-16": (2, 641.64, 1, -34.18, 555.82, -34.18),
       "2023-01-17": (3, 1322.46, 3, -1737.54, 590.82, -1089.18)}
sess_id = b["session_id"]
last_idx = {}
for i in range(n):
    last_idx[sess_id[i]] = i
sed = {sid: str(tarr[i])[:10] for sid, i in last_idx.items()}


def jan_score(trades, verbose=False):
    by = defaultdict(list)
    for t in trades:
        d = sed[sess_id[t["xi"]]]
        if d in TGT:
            by[d].append(t)
    rm_t = cents = nosol = 0
    det = []
    for day in sorted(TGT):
        nW, gW, nL, gL, LW, LL = TGT[day]
        ours = by.get(day, [])
        n_t = nW + nL
        k = len(ours) - n_t
        best = None
        if 0 <= k <= 7:
            for rem in combinations(range(len(ours)), k):
                keep = [t for j, t in enumerate(ours) if j not in rem]
                p = [t["pnl"] for t in keep]
                w = [x for x in p if x > 0]; l = [x for x in p if x <= 0]
                if len(w) != nW or len(l) != nL:
                    continue
                if abs(max(w) - LW) > 75 or abs(min(l) - LL) > 75:
                    continue
                err = abs(sum(w) - gW) + abs(sum(l) - gL) + abs(max(w) - LW) + abs(min(l) - LL)
                if best is None or err < best[0]:
                    best = (err, rem)
        if best is None:
            nosol += 1
            det.append(f"{day[-5:]}:n{len(ours)}/{n_t} NOSOL")
        else:
            rm_t += len(best[1])
            if best[0] < 0.02:
                cents += 1
            det.append(f"{day[-5:]}:n{len(ours)}/{n_t} rm{len(best[1])} ${best[0]:.0f}")
        if verbose and day == "2023-01-17":
            for t in ours:
                print(f"      0117 {'L' if t['dir']>0 else 'S'} {t['et'][5:16]}->{t['xt'][11:16]} {t['pnl']:.2f}", flush=True)
    return rm_t, cents, nosol, " ".join(det)


def agg(trades):
    p = np.array([t["pnl"] for t in trades]); d = np.array([t["dir"] for t in trades])
    h = np.array([t["hold"] for t in trades]); w = p > 0
    gl = p[~w].sum()
    eq = np.cumsum(p); dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    cw = cl = mw = ml = 0
    for s in np.where(w, 1, -1):
        if s > 0: cw += 1; cl = 0
        else: cl += 1; cw = 0
        mw, ml = max(mw, cw), max(ml, cl)
    return (f"n={len(p)} L{int((d>0).sum())}/S{int((d<0).sum())} net={p.sum():.2f} wr={w.mean()*100:.2f} "
            f"pf={p[w].sum()/-gl:.3f} dd={dd.min():.2f} hold={h.mean():.2f} ({h[d>0].mean():.2f}/{h[d<0].mean():.2f}) "
            f"lw={p.max():.2f} ll={p.min():.2f} consec {mw}/{ml}")


print("TARGET: n=4351 L2166/S2185 net=292172.82 wr=40.29 pf=1.18 dd=-32677.42 hold=94.15 (105.85/82.56) lw=7705.82 ll=-4449.18 consec 8/15", flush=True)
for name, strict in [("FBGATE_strict", True), ("FBGATE_inclusive", False)]:
    tr = run_fbgate(strict=strict)
    rm, cents, nosol, det = jan_score(tr, verbose=(name == "FBGATE_strict"))
    print(f"[r1i] {name}: {agg(tr)}", flush=True)
    print(f"      Jan rm={rm} cents={cents} nosol={nosol} | {det}", flush=True)
    hits = [t for t in tr if t["et"].startswith("2023-01-16T20:48")]
    print(f"      MLK resume 20:48: {[(h['et'][5:16], round(h['pnl'],2)) for h in hits]}", flush=True)

print("[r1i] done", flush=True)
