"""r1j (amendment 4): CAND2 gate semantics — FILL-bar (incumbent) vs
DECISION-close projection (NT8-native). Master window, canonical ledger,
$4.18/RT. Readouts: decision-flip count, Jan-2023 label score, master drift.
"""
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

print("[r1j] ledger + wave ...", flush=True)
b = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
core = solar_wave(b["close"], SolarWaveParams(), start_up=False)
n = b["n"]
opn, close = b["open"], b["close"]
first_bar, last_bar = b["first_bar"], b["last_bar"]
tarr = b["time"]
ts_arr = core.trailing_stop
sig_arr = core.signal_trade.astype(np.int64)

mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
soi = np.zeros(n, np.int64); cur = 0
for i in range(n):
    if first_bar[i]:
        cur = i
    soi[i] = cur
mo = ((tarr - tarr[soi]).astype("timedelta64[s]").astype(np.int64) // 60)


def run(mode, X=1600, K=3, C=700, X2=2500, cap=20, cd=3, comm_side=2.09):
    """mode: 'fill' (incumbent) or 'decision' (NT8-native projection)."""
    trades = []
    pos = 0; epx = 0.0; ei = -1; pe = 0; px = False; pr = 0
    cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; prior = 0.0; n_sess = 0
    last_exit = -10**9
    flips = []   # bars where the two semantics would disagree (evaluated in-run)

    def realize(i, p, kind):
        nonlocal pos, cum, hi, n_sess, last_exit
        pnl = pos * (p - epx) * POINT_VALUE - 2 * comm_side
        trades.append({"d": pos, "et": str(tarr[ei]), "xt": str(tarr[i]), "pnl": pnl,
                       "xi": i, "kind": kind,
                       "hold": float((tarr[i] - tarr[ei]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        cum += pnl; hi = max(hi, cum)
        consec[pos] = consec[pos] + 1 if pnl <= 0 else 0
        n_sess += 1; last_exit = i; pos = 0

    def ok(d, i, cum_, hi_, ns_, cl_, cs_):
        if prior <= -C and mo[i] <= 360:
            return False
        if ns_ >= cap:
            return False
        thr = X if mod[i] >= 720 else X2
        if hi_ >= thr:
            if cum_ < 0:
                return False
            if (cl_ if d > 0 else cs_) >= K:
                return False
        return True

    for i in range(n):
        if first_bar[i]:
            prior = cum; cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; n_sess = 0
        if px and pos != 0:
            realize(i, opn[i], "flip"); px = False
        if pr != 0:
            if pos != 0:
                realize(i, opn[i], "flip")
            if mode == "fill":
                allowed = ok(pr, i, cum, hi, n_sess, consec[1], consec[-1])
            else:
                allowed = True   # decision mode already gated at decision time
            if allowed:
                pos = pr; epx, ei = opn[i], i
            pr = 0
        if pe != 0 and pos == 0:
            if mode == "fill":
                allowed = ok(pe, i, cum, hi, n_sess, consec[1], consec[-1])
            else:
                allowed = True
            if allowed:
                pos = pe; epx, ei = opn[i], i
            pe = 0
        pe = 0
        sig = sig_arr[i]
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
                    if mode == "decision":
                        proj = pos * (close[i] - epx) * POINT_VALUE - 2 * comm_side
                        pc = cum + proj; ph = max(hi, pc)
                        pcl = (consec[1] + 1 if pos > 0 and proj <= 0 else (0 if pos > 0 else consec[1]))
                        pcs = (consec[-1] + 1 if pos < 0 and proj <= 0 else (0 if pos < 0 else consec[-1]))
                        if ok(sig, i, pc, ph, n_sess + 1, pcl, pcs):
                            pr = sig
                        else:
                            px = True
                    else:
                        pr = sig
                else:
                    px = True
                continue
        if pos == 0 and abs(sig) == 1 and i >= BARS_REQUIRED and dec and (i - last_exit) >= cd:
            if mode == "decision":
                if ok(sig, i, cum, hi, n_sess, consec[1], consec[-1]):
                    pe = 1 if sig > 0 else -1
            else:
                pe = 1 if sig > 0 else -1
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
            det.append(f"{day[-5:]}:NOSOL(n{len(ours)}/{n_t})")
        else:
            rm_t += len(best[1])
            if best[0] < 0.02:
                cents += 1
            det.append(f"{day[-5:]}:rm{len(best[1])}${best[0]:.0f}")
    return rm_t, cents, nosol, " ".join(det)


def agg(trades):
    p = np.array([t["pnl"] for t in trades]); d = np.array([t["d"] for t in trades])
    h = np.array([t["hold"] for t in trades]); w = p > 0
    gl = p[~w].sum()
    eq = np.cumsum(p); dd = eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    cw = cl = mw = ml = 0
    for s in np.where(w, 1, -1):
        if s > 0: cw += 1; cl = 0
        else: cl += 1; cw = 0
        mw, ml = max(mw, cw), max(ml, cl)
    return (f"n={len(p)} L{int((d>0).sum())}/S{int((d<0).sum())} net={p.sum():.2f} wr={w.mean()*100:.2f} "
            f"pf={p[w].sum()/-gl:.3f} dd={dd.min():.2f} hold={h.mean():.2f} "
            f"({h[d>0].mean():.2f}/{h[d<0].mean():.2f}) consec {mw}/{ml}")


print("TARGET: n=4351 net=292172.82 wr=40.29 pf=1.18 dd=-32677.42 hold=94.15 consec 8/15", flush=True)
res = {}
for mode in ("fill", "decision"):
    tr = run(mode)
    res[mode] = tr
    rm, cents, nosol, det = jan_score(tr)
    print(f"\n[{mode}] {agg(tr)}", flush=True)
    print(f"  Jan labels: rm={rm} cent-days={cents} nosol={nosol} | {det}", flush=True)

sf = {(t["et"], t["xt"], t["d"]) for t in res["fill"]}
sd = {(t["et"], t["xt"], t["d"]) for t in res["decision"]}
print(f"\n[diff] fill-only={len(sf-sd)} decision-only={len(sd-sf)} common={len(sf&sd)}", flush=True)
only_f = sorted(sf - sd)[:12]; only_d = sorted(sd - sf)[:12]
for x in only_f:
    print(f"  fill-only {x}", flush=True)
for x in only_d:
    print(f"  dec-only  {x}", flush=True)
