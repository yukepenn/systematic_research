"""r1h: SESSION-RESET late-T2 hypothesis — armed latch resets at first bar of session.

Custom T2 automaton (PB-late semantics + per-session reset) over the core Solar ladder;
entries = T1 flips (reverse) + these T2s when flat; B1 + D-gate as registered.
Acid tests: (1) 01-17 gains exactly the 20:48@14712.75 short (-274.18);
(2) 01-10/01-11 stay clean (no spurious T2); (3) Jan residuals; (4) master aggregate.
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
print("[r1h] ledger + core ladder ...", flush=True)
b = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
core = solar_wave(b["close"], SolarWaveParams(), start_up=False)
n = b["n"]
opn, close, high, low = b["open"], b["close"], b["high"], b["low"]
first_bar, last_bar = b["first_bar"], b["last_bar"]
tarr = b["time"]
tv = core.trend_vector
ts_arr = core.trailing_stop
is_up = core.is_up
base_sig = core.signal_trade.astype(np.int64)   # +-1 flips, +-3 strengthen
flip = np.abs(base_sig) == 1
t3 = np.abs(base_sig) == 3
PS = 10

mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60).astype(np.int64)
soi = np.zeros(n, dtype=np.int64)
cur = 0
for i in range(n):
    if first_bar[i]:
        cur = i
    soi[i] = cur
mins_open = ((tarr - tarr[soi]).astype("timedelta64[s]").astype(np.int64) // 60).astype(np.int64)


def late_t2(session_reset: bool) -> np.ndarray:
    """PB-late automaton; returns +-2 fire array."""
    fire = np.zeros(n, dtype=np.int64)
    armed = True
    next_pb = -(1 << 60)
    for t in range(n):
        if session_reset and first_bar[t]:
            armed = True
            next_pb = -(1 << 60)
        if flip[t]:
            armed = True
            next_pb = -(1 << 60)
            continue
        up = bool(is_up[t])
        tvv = tv[t]
        if np.isnan(tvv):
            continue
        open_beyond = (opn[t] < tvv) if up else (opn[t] > tvv)
        close_beyond = (close[t] < tvv) if up else (close[t] > tvv)
        close_inside = (close[t] > tvv) if up else (close[t] < tvv)
        if (not armed or open_beyond) and close_inside and t > next_pb:
            fire[t] = 1 if up else -1
            next_pb = t + PS
        if close_beyond:
            armed = False
        elif close_inside:
            armed = True
        if t3[t]:
            armed = True
    return fire


def run_integrated(t2sig, X=1600, K=3, C=1000, use_t2=True):
    trades = []
    pos = 0; epx = 0.0; ei = -1
    pe = 0; px = False; pr = 0
    cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; prior = 0.0

    def realize(i, p, kind):
        nonlocal pos, cum, hi
        pnl = pos * (p - epx) * POINT_VALUE - 2 * 2.09
        trades.append({"dir": pos, "ei": ei, "xi": i, "et": str(tarr[ei]), "xt": str(tarr[i]),
                       "pnl": pnl, "kind": kind,
                       "hold": float((tarr[i] - tarr[ei]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        cum += pnl; hi = max(hi, cum)
        if pnl <= 0:
            consec[pos] += 1
        else:
            consec[pos] = 0
        pos = 0

    def ok(d, i):
        if prior <= -C and mins_open[i] <= 360:
            return False
        if hi >= X and mod[i] >= 720:
            if cum < 0:
                return False
            if consec[d] >= K:
                return False
        return True

    for i in range(n):
        if first_bar[i]:
            prior = cum; cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}
        if px and pos != 0:
            realize(i, opn[i], "flip"); px = False
        if pr != 0:
            if pos != 0:
                realize(i, opn[i], "flip")
            if ok(pr, i):
                pos = pr; epx, ei = opn[i], i
            pr = 0
        if pe != 0 and pos == 0:
            if ok(pe, i):
                pos = pe; epx, ei = opn[i], i
            pe = 0
        pe = 0
        sig = base_sig[i]
        t2 = t2sig[i] if use_t2 else 0
        if last_bar[i]:
            if pos != 0:
                realize(i, close[i], "sc")
            px = False; pe = 0; pr = 0
            continue
        dec = not first_bar[i]
        if pos != 0 and not np.isnan(ts_arr[i]):
            hitx = (pos > 0 and close[i] <= ts_arr[i]) or (pos < 0 and close[i] >= ts_arr[i])
            if hitx:
                if dec and sig == -pos and abs(sig) == 1 and i >= BARS_REQUIRED:
                    pr = sig
                else:
                    px = True
                continue
        if pos == 0 and i >= BARS_REQUIRED and dec:
            if abs(sig) == 1:
                pe = 1 if sig > 0 else -1
            elif t2 != 0:
                pe = t2
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


def jan_score(trades):
    by = defaultdict(list)
    for t in trades:
        d = sed[sess_id[t["xi"]]]
        if d in TGT:
            by[d].append(t)
    rm_t, cents, nosol = 0, 0, 0
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
    return rm_t, cents, nosol, " ".join(det)


def agg(trades):
    p = np.array([t["pnl"] for t in trades]); d = np.array([t["dir"] for t in trades])
    h = np.array([t["hold"] for t in trades]); w = p > 0
    gl = p[~w].sum()
    eq = np.cumsum(p); dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return (f"n={len(p)} L{int((d>0).sum())}/S{int((d<0).sum())} net={p.sum():.2f} wr={w.mean()*100:.2f} "
            f"pf={p[w].sum()/-gl:.3f} dd={dd.min():.2f} hold={h.mean():.2f} ({h[d>0].mean():.2f}/{h[d<0].mean():.2f}) "
            f"lw={p.max():.2f} ll={p.min():.2f}")


print("TARGET: n=4351 L2166/S2185 net=292172.82 wr=40.29 pf=1.18 dd=-32677.42 hold=94.15 (105.85/82.56)", flush=True)
for name, sr, use_t2 in [("T2reset", True, True), ("T2carry", False, True), ("noT2", True, False)]:
    t2s = late_t2(sr)
    tr = run_integrated(t2s, use_t2=use_t2)
    rm, cents, nosol, det = jan_score(tr)
    print(f"[r1h] {name}: {agg(tr)}", flush=True)
    print(f"      Jan rm={rm} cents={cents} nosol={nosol} | {det}", flush=True)
    # acid test: the 01-16-eve short
    hits = [t for t in tr if t["et"].startswith("2023-01-16T20:48")]
    print(f"      20:48 trade: {hits}", flush=True)

with open(os.path.join(OUT, "r1h_done.txt"), "w") as f:
    f.write("see console/json")
print("[r1h] done", flush=True)
