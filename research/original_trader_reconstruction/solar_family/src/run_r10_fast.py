"""R10: Feb-2025 fast build — TrendVector-cycle machine test
(runs/OTR_R10_FEB2025_FAST/spec.yaml)."""
import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams, solar_wave_full  # noqa: E402
from otr_engine import POINT_VALUE, BARS_REQUIRED  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R10_FEB2025_FAST", "out")
os.makedirs(OUT, exist_ok=True)


def build(sub, params):
    t = sub["time"].values.astype("datetime64[s]")
    gap = np.diff(t).astype("timedelta64[m]").astype(np.int64)
    fb = np.zeros(len(sub), bool); fb[0] = True; fb[1:] = gap > 60
    lb = np.zeros(len(sub), bool); lb[:-1] = fb[1:]; lb[-1] = True
    r = solar_wave_full(sub["open"].values, sub["high"].values, sub["low"].values,
                        sub["close"].values, params, start_up=False)
    mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    soi = np.zeros(len(sub), np.int64); cur = 0
    for i in range(len(sub)):
        if fb[i]:
            cur = i
        soi[i] = cur
    mo = ((t - t[soi]).astype("timedelta64[s]").astype(np.int64) // 60)
    return dict(t=t, o=sub["open"].values, h=sub["high"].values, l=sub["low"].values,
                c=sub["close"].values, fb=fb, lb=lb, st=r.signal_trade.astype(int),
                ts=r.trailing_stop, tv=r.trend_vector, up=r.is_up.astype(bool),
                mod=mod, mo=mo, n=len(sub))


def run_fast(bb, tv_cycle=True, X=1600, K=3, C=700, X2=2500, cap=1000, cd=3,
             ll=None, comm=0.0):
    t, o, h, l, c, fb, lb, st, ts, tv, up, mod, mo, n = (bb[k] for k in
        ("t", "o", "h", "l", "c", "fb", "lb", "st", "ts", "tv", "up", "mod", "mo", "n"))
    trades = []; pos = 0; epx = 0.0; ei = -1; pe = 0; px = False; pr = 0
    cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; prior = 0.0; n_sess = 0
    last_exit = -10**9

    def realize(i, p, kind):
        nonlocal pos, cum, hi, n_sess, last_exit
        pnl = pos * (p - epx) * POINT_VALUE - 2 * comm
        trades.append({"d": pos, "et": str(t[ei]), "xt": str(t[i]), "pnl": pnl,
                       "xi": i, "kind": kind,
                       "hold": float((t[i] - t[ei]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        cum += pnl; hi = max(hi, cum)
        consec[pos] = consec[pos] + 1 if pnl <= 0 else 0
        n_sess += 1; last_exit = i; pos = 0

    def ok(d, i):
        if ll is not None and cum <= -ll:
            return False
        if prior <= -C and mo[i] <= 360:
            return False
        if n_sess >= cap:
            return False
        thr = X if mod[i] >= 720 else X2
        if hi >= thr:
            if cum < 0:
                return False
            if consec[d] >= K:
                return False
        return True

    for i in range(n):
        if fb[i]:
            prior = cum; cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; n_sess = 0
        if px and pos != 0:
            realize(i, o[i], "rule"); px = False
        if pr != 0:
            if pos != 0:
                realize(i, o[i], "flip")
            if ok(pr, i):
                pos = pr; epx, ei = o[i], i
            pr = 0
        if pe != 0 and pos == 0:
            if ok(pe, i):
                pos = pe; epx, ei = o[i], i
            pe = 0
        pe = 0
        sig = st[i]
        if lb[i]:
            if pos != 0:
                realize(i, c[i], "sc")
            px = False; pe = 0; pr = 0
            continue
        dec = not fb[i]
        if pos != 0:
            # T1-flip reversal path (chains) via TS touch
            if not np.isnan(ts[i]):
                hitx = (pos > 0 and c[i] <= ts[i]) or (pos < 0 and c[i] >= ts[i])
                if hitx:
                    if dec and abs(sig) == 1 and np.sign(sig) == -pos and i >= BARS_REQUIRED:
                        pr = int(np.sign(sig))
                    else:
                        px = True
                    continue
            # TV-cycle exit: close strictly beyond TV against the position
            if tv_cycle and not np.isnan(tv[i]):
                beyond = (pos > 0 and c[i] < tv[i]) or (pos < 0 and c[i] > tv[i])
                if beyond:
                    px = True
                    continue
        if pos == 0 and dec and i >= BARS_REQUIRED and (i - last_exit) >= cd:
            if abs(sig) == 1:
                pe = 1 if sig > 0 else -1
            elif tv_cycle and abs(sig) == 2:
                pe = 1 if sig > 0 else -1
    return trades


TGT = [("2025-02-26", "2025-02-26", 15, None, None),
       ("2025-02-27", "2025-02-27", 90, -331.0, None),
       ("2025-02-28", "2025-02-28", 21, -945.0, 19.6),
       ("2025-03-02", "2025-03-03", 26, -869.0, 44.7),
       ("2025-03-04", "2025-03-05", 70, -742.0, 31.8),
       ("2025-03-06", "2025-03-07", 47, -596.0, 31.1),
       ("2025-03-09", "2025-03-10", 33, -704.0, 24.4),
       ("2025-03-12", "2025-03-14", 60, -619.0, 41.2)]


def main():
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2025-01-20") & (df["time"] <= "2025-03-15 17:00")].reset_index(drop=True)
    members = {}
    for mode, early in (("E", True), ("L", False)):
        bb = build(seg, SolarWaveParams(pullback_early=early))
        for lltag, ll in (("noLL", None), ("LL2500", 2500.0)):
            members[f"F_TV2{mode}_{lltag}"] = run_fast(bb, tv_cycle=True, ll=ll)
        if mode == "E":
            members["F_T1_control"] = run_fast(bb, tv_cycle=False)
    print(f"{'window':>22} {'tgt n':>6} {'tgt AL':>7} {'tgt hold':>8} | " +
          " | ".join(f"{m}: n AL hold" for m in members))
    rows = []
    for d0, d1, tn, tal, th in TGT:
        lo = np.datetime64(pd.Timestamp(d0) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        hi = np.datetime64(pd.Timestamp(d1)) + np.timedelta64(17, "h")
        line = f"{d0+'..'+d1[-5:]:>22} {tn:>6} {str(tal):>7} {str(th):>8}"
        for m, trl in members.items():
            w = [x for x in trl if lo <= np.datetime64(x["et"]) <= hi]
            if not w:
                line += f" | {m}: 0"
                continue
            p = np.array([x["pnl"] for x in w]); hh = np.mean([x["hold"] for x in w])
            losses = p[p <= 0]
            al = losses.mean() if len(losses) else 0
            line += f" | {len(w):>3} {al:>6.0f} {hh:>5.1f}"
            rows.append(dict(window=d0, member=m, n=len(w), tgt_n=tn,
                             al=round(al), tgt_al=tal, hold=round(hh, 1), tgt_hold=th,
                             net=round(p.sum())))
        print(line, flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "r10_grid.csv"), index=False)
    print("\nsummary |n err| by member:")
    d = pd.DataFrame(rows)
    d["nerr"] = abs(d.n - d.tgt_n) / d.tgt_n
    print((d.groupby("member")["nerr"].mean() * 100).round(1).to_string())


if __name__ == "__main__":
    main()
