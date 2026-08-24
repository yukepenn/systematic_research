"""OTR_R1_SERIES r1g: INTEGRATION — late-T2 signals + B1 first-bar drop + D equity gate.

Registered model: spec amendment 2 (1e1edf2). Gate evaluated at FILL time with the
same-bar exit already realized (per hunt_D_result state ordering).
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
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")

print("[r1g] loading ledger + regenerating LATE-mode signals ...", flush=True)
b = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
res = solar_wave_full(b["open"], b["high"], b["low"], b["close"],
                      SolarWaveParams(pullback_early=False), start_up=False)
st = res.signal_trade.astype(np.int64)
ts_arr = res.trailing_stop
n = b["n"]
close, opn = b["close"], b["open"]
first_bar, last_bar = b["first_bar"], b["last_bar"]
tarr = b["time"]
mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60).astype(np.int64)

# minutes since session open per bar
sess_open_i = np.zeros(n, dtype=np.int64)
cur = 0
for i in range(n):
    if first_bar[i]:
        cur = i
    sess_open_i[i] = cur
mins_open = ((tarr - tarr[sess_open_i]).astype("timedelta64[s]").astype(np.int64) // 60).astype(np.int64)

COMM = 2.09


def run_integrated(X, K, C, entry_types=(1, 2), use_b1=True, use_gate=True):
    trades = []
    pos = 0
    entry_px = 0.0
    entry_i = -1
    pend_entry = 0
    pend_exit = False
    pend_reverse = 0
    # D-gate state
    cum = 0.0
    high = 0.0
    consec = {1: 0, -1: 0}
    prior = 0.0

    def realize(i_exit, px_exit, kind):
        nonlocal pos, cum, high
        pnl = pos * (px_exit - entry_px) * POINT_VALUE - 2 * COMM
        trades.append({"dir": pos, "entry_i": entry_i, "exit_i": i_exit,
                       "entry_time": str(tarr[entry_i]), "exit_time": str(tarr[i_exit]),
                       "pnl": pnl, "exit_kind": kind,
                       "hold_min": float((tarr[i_exit] - tarr[entry_i]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        cum += pnl
        high = max(high, cum)
        if pnl <= 0:
            consec[pos] += 1
        else:
            consec[pos] = 0
        pos = 0

    def gate_ok(d, i):
        """Entry gate at FILL bar i for direction d (+1/-1)."""
        if not use_gate:
            return True
        if prior <= -C and mins_open[i] <= 360:
            return False
        if high >= X and mod[i] >= 720:
            if cum < 0:
                return False
            if consec[d] >= K:
                return False
        return True

    for i in range(n):
        if first_bar[i]:
            prior = cum
            cum = 0.0
            high = 0.0
            consec = {1: 0, -1: 0}

        # fills
        if pend_exit and pos != 0:
            realize(i, opn[i], "flip")
            pend_exit = False
        if pend_reverse != 0:
            if pos != 0:
                realize(i, opn[i], "flip")
            if gate_ok(pend_reverse, i):
                pos = pend_reverse
                entry_px, entry_i = opn[i], i
            pend_reverse = 0
        if pend_entry != 0 and pos == 0:
            if gate_ok(pend_entry, i):
                pos = pend_entry
                entry_px, entry_i = opn[i], i
            pend_entry = 0
        pend_entry = 0

        sig = st[i]

        # session close
        if last_bar[i]:
            if pos != 0:
                realize(i, close[i], "session_close")
            pend_exit = False
            pend_entry = 0
            pend_reverse = 0
            continue

        # B1: no entry decision on the session's first bar
        decision_allowed = not (use_b1 and first_bar[i])

        # exit first
        if pos != 0:
            line = ts_arr[i]
            if not np.isnan(line):
                hit = (pos > 0 and close[i] <= line) or (pos < 0 and close[i] >= line)
                if hit:
                    if decision_allowed and sig == -pos and abs(sig) == 1 and i >= BARS_REQUIRED:
                        pend_reverse = sig
                    else:
                        pend_exit = True
                    continue

        # entry when flat
        if pos == 0 and sig != 0 and i >= BARS_REQUIRED and decision_allowed:
            if abs(sig) in entry_types:
                pend_entry = 1 if sig > 0 else -1
    return trades


def agg(trades):
    p = np.array([t["pnl"] for t in trades])
    d = np.array([t["dir"] for t in trades])
    h = np.array([t["hold_min"] for t in trades])
    w = p > 0
    gl = p[~w].sum()
    eq = np.cumsum(p)
    dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return {"n": len(trades), "L": int((d > 0).sum()), "S": int((d < 0).sum()),
            "net": round(float(p.sum()), 2), "wr": round(float(w.mean() * 100), 2),
            "pf": round(float(p[w].sum() / -gl), 3) if gl < 0 else None,
            "dd": round(float(dd.min()), 2), "hold": round(float(h.mean()), 2),
            "holdL": round(float(h[d > 0].mean()), 2), "holdS": round(float(h[d < 0].mean()), 2),
            "lw": round(float(p.max()), 2), "ll": round(float(p.min()), 2)}


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
        d = sed[sess_id[t["exit_i"]]]
        if d in TGT:
            by[d].append(t)
    total_rm, cents, nosol = 0, 0, 0
    detail = []
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
                w = [x for x in p if x > 0]
                l = [x for x in p if x <= 0]
                if len(w) != nW or len(l) != nL:
                    continue
                if abs(max(w) - LW) > 75 or abs(min(l) - LL) > 75:
                    continue
                err = abs(sum(w) - gW) + abs(sum(l) - gL) + abs(max(w) - LW) + abs(min(l) - LL)
                if best is None or err < best[0]:
                    best = (err, rem)
        if best is None:
            nosol += 1
            detail.append(f"{day[-5:]}:n{len(ours)}/{n_t} NOSOL")
        else:
            total_rm += len(best[1])
            if best[0] < 0.02:
                cents += 1
            detail.append(f"{day[-5:]}:n{len(ours)}/{n_t} rm{len(best[1])} ${best[0]:.0f}")
    return total_rm, cents, nosol, " ".join(detail)


MASTER = "TARGET: n=4351 L2166/S2185 net=292172.82 wr=40.29 pf=1.18 dd=-32677.42 hold=94.15 (105.85/82.56) lw=7705.82 ll=-4449.18"
print(MASTER, flush=True)

results = []
for label, kw in [
    ("BASE_T1_early(ref)", None),  # skip, known
    ("LATE_T12_nogate", dict(X=0, K=99, C=1e12, use_gate=False)),
    ("LATE_T12_B1_nogate", dict(X=0, K=99, C=1e12, use_gate=False, use_b1=True)),
    ("INTEGRATED_X1600_K3_C1000", dict(X=1600, K=3, C=1000)),
    ("INT_X1550_C500", dict(X=1550, K=3, C=500)),
    ("INT_X1750_C1000", dict(X=1750, K=3, C=1000)),
    ("INT_X1900_C1300", dict(X=1900, K=3, C=1300)),
    ("INT_T1only_X1600", dict(X=1600, K=3, C=1000, entry_types=(1,))),
]:
    if kw is None:
        continue
    tr = run_integrated(**kw)
    a = agg(tr)
    rm, cents, nosol, detail = jan_score(tr)
    results.append({"label": label, "agg": a, "jan_rm": rm, "jan_cents": cents, "jan_nosol": nosol})
    print(f"[r1g] {label}: n={a['n']} L{a['L']}/S{a['S']} net={a['net']} wr={a['wr']} pf={a['pf']} "
          f"dd={a['dd']} hold={a['hold']} ({a['holdL']}/{a['holdS']}) lw={a['lw']} ll={a['ll']}", flush=True)
    print(f"       Jan: rm={rm} cents={cents} nosol={nosol} | {detail}", flush=True)

with open(os.path.join(OUT, "r1g_integration.json"), "w") as f:
    json.dump(results, f, indent=1, default=str)
print("[r1g] done", flush=True)
