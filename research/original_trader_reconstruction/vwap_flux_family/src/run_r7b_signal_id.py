"""R7 pass 2 (amendment 1): H1c manual-verbatim CLV + version-aware strength
gate on surviving pass-1 structures. Same scoring, same discipline."""
import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from vf_core import vf_levels  # noqa: E402
from run_r5_weekly import fingerprint, num, norm_err, distance, W3, W2, W1  # noqa: E402
from run_r7_signal_id import ema, trend_states  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R7_VF_SIGNAL_ID", "out")
PV = 20.0
STOP = 130.0
QTY_PER_TREND = 3
SPLIT = 5
CLOSE_THR = 0.10
UPGRADE = np.datetime64("2026-02-24T00:00:00")


def run_member(bars, tr, P, C, H, X, gate):
    n = bars["n"]
    o, h, l, c = bars["o"], bars["h"], bars["l"], bars["c"]
    t, lb = bars["t"], bars["lb"]
    lv = bars["lv"]
    cvd_slope = bars["cvd_slope"]
    post = bars["post_upgrade"]
    MIN, Q25, FV, Q75, MAX = (lv[:, k] for k in range(5))
    trades = []
    pos = 0; epx = 0.0; ei = -1
    pe = 0; px = False
    cnt = {1: 0, -1: 0}; last_sig = {1: -10**9, -1: -10**9}
    prev_tr = 0

    def realize(i, p, kind):
        nonlocal pos
        trades.append({"d": pos, "et": str(t[ei]), "xt": str(t[i]),
                       "pnl": pos * (p - epx) * PV, "kind": kind,
                       "hold": float((t[i] - t[ei]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        pos = 0

    for i in range(n):
        if px and pos != 0:
            realize(i, o[i], "rule"); px = False
        if pe != 0 and pos == 0:
            pos = pe; epx, ei = o[i], i
        pe = 0
        if pos != 0:
            lvl = epx - pos * STOP
            hit = l[i] <= lvl if pos > 0 else h[i] >= lvl
            if hit:
                gap = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                realize(i, o[i] if gap else lvl, "stop")
        if lb[i]:
            if pos != 0:
                realize(i, c[i], "sc")
            px = False; pe = 0
            continue
        if np.isnan(MAX[i]):
            continue
        ti = tr[i]
        if ti != prev_tr:
            cnt = {1: 0, -1: 0}
            prev_tr = ti
        sig = 0
        rng = h[i] - l[i]
        if ti != 0 and rng > 0:
            if ti > 0:
                rail = MAX[i] if P == "P_IN" else (Q75[i] if P == "P_Q75" else FV[i])
                touched = l[i] <= rail
                conf = (c[i] > o[i]) if C == "C_DIR" else (c[i] >= rail)
                top_frac = (h[i] - c[i]) / rng
                clv = top_frac <= CLOSE_THR if H == "H1a" else top_frac >= CLOSE_THR
                if touched and conf and clv:
                    sig = 1
            else:
                rail = MIN[i] if P == "P_IN" else (Q25[i] if P == "P_Q75" else FV[i])
                touched = h[i] >= rail
                conf = (c[i] < o[i]) if C == "C_DIR" else (c[i] <= rail)
                bot_frac = (c[i] - l[i]) / rng
                clv = bot_frac <= CLOSE_THR if H == "H1a" else bot_frac >= CLOSE_THR
                if touched and conf and clv:
                    sig = -1
        if sig != 0 and gate == "strong_only" and post[i]:
            if np.sign(cvd_slope[i]) != sig:
                sig = 0
        if sig != 0:
            if cnt[sig] >= QTY_PER_TREND or (i - last_sig[sig]) < SPLIT:
                sig = 0
        if pos != 0:
            hit = (sig == -pos) if X == "X_OPP" else (ti == -pos)
            if hit:
                if X == "X_OPP" and sig == -pos:
                    px = True; pe = sig
                    cnt[sig] += 1; last_sig[sig] = i
                else:
                    px = True
                continue
        if pos == 0 and sig != 0 and pe == 0:
            pe = sig
            cnt[sig] += 1; last_sig[sig] = i
    return trades


def main():
    tgt = [r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8"))
        if r["report_end"] and pd.Timestamp(r["report_end"]) <= pd.Timestamp("2026-05-29")]
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-11") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
    t = seg["time"].values.astype("datetime64[s]")
    fb = np.zeros(len(seg), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(len(seg), bool); lb[:-1] = fb[1:]; lb[-1] = True
    c = seg["close"].values; v = seg["volume"].values.astype(float)
    o_ = seg["open"].values
    print("[r7b] cloud ...", flush=True)
    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    e20 = ema(c, 20)
    # bar-level CVD proxy (input-faithful to the bar-data reimplementation reading)
    delta = np.sign(c - o_) * v
    cvd = np.zeros(len(c))
    run = 0.0
    for i in range(len(c)):
        if fb[i]:
            run = 0.0
        run += delta[i]
        cvd[i] = run
    cvd_slope = np.zeros(len(c))
    cvd_slope[20:] = cvd[20:] - cvd[:-20]
    bars = dict(n=len(seg), t=t, o=o_, h=seg["high"].values, l=seg["low"].values,
                c=c, lb=lb, lv=lv, cvd_slope=cvd_slope, post_upgrade=(t >= UPGRADE))

    structures = [("T_C", "P_MED"), ("T_C", "P_Q75"), ("T_A", "P_IN"),
                  ("T_D", "P_IN"), ("T_B", "P_IN"), ("T_D", "P_Q75")]
    trends = {k: trend_states(k, c, bars["l"], bars["h"], lv, e20)
              for k in {s[0] for s in structures}}
    wins = []
    for r in tgt:
        lo = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        hi = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, lo, hi))
    metrics = W3 + W2 + W1
    rows = []
    members = [(T, P, C, H, X, G)
               for (T, P) in structures for C in ("C_DIR", "C_REC")
               for H in ("H1a", "H1c") for X in ("X_OPP", "X_FLIP")
               for G in ("none", "strong_only")]
    print(f"[r7b] {len(members)} members", flush=True)
    grid = open(os.path.join(OUT, "r7b_grid.csv"), "w", newline="")
    gw = csv.writer(grid)
    gw.writerow(["member", "window", "distance", "n", "tgt_n", "net", "tgt_net"])
    for mi, (T, P, C, H, X, G) in enumerate(members):
        name = f"{T}|{P}|{C}|{H}|{X}|{G}"
        trl = run_member(bars, trends[T], P, C, H, X, G)
        dists = []; fail_net = None
        for r, lo, hi in wins:
            w = [x for x in trl if lo <= np.datetime64(x["et"]) <= hi]
            fp = fingerprint(w)
            if fp is None:
                dists.append(2.0)
                gw.writerow([name, r["report_start"], "", 0, r["trades_all"], 0, r["net_all"]])
                continue
            tgtm = {m: num(r.get(m)) for m in metrics}
            d = distance({m: norm_err(m, fp.get(m), tgtm.get(m)) for m in metrics})
            dists.append(d)
            if r["report_start"] == "3/22/2026":
                fail_net = fp["net_all"]
            gw.writerow([name, r["report_start"], f"{d:.4f}", fp["trades_all"],
                         r["trades_all"], f"{fp['net_all']:.0f}", r["net_all"]])
        rows.append((float(np.mean(dists)), float(np.max(dists)), name, fail_net, len(trl)))
        if mi % 16 == 0:
            print(f"  [{mi}] {name} mean={rows[-1][0]:.3f}", flush=True)
    grid.close()
    rows.sort()
    print("\n=== r7b top 20 ===")
    for md, wd, name, fn, ntr in rows[:20]:
        dq = " DQ" if (fn is not None and fn > 0) else ""
        print(f"{name:>40} mean={md:.3f} worst={wd:.3f} failwk={fn if fn is not None else float('nan'):8.0f} ntr={ntr}{dq}")
    with open(os.path.join(OUT, "r7b_summary.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["mean", "worst", "member", "fail_net", "ntr"])
        for row in rows:
            w.writerow(row)


if __name__ == "__main__":
    main()
