"""R7: bounded structural identification of Signal_Trend + Signal_Trade
(runs/OTR_R7_VF_SIGNAL_ID/spec.yaml). All numeric constants are the trader's
panel values; only STRUCTURE varies. Scoring = §40 distance + failure-week
geometry; PnL never a selection objective.
"""
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

OUT = os.path.join(ROOT, "runs", "OTR_R7_VF_SIGNAL_ID", "out")
os.makedirs(OUT, exist_ok=True)
PV = 20.0
STOP = 130.0
QTY_PER_TREND = 3
SPLIT = 5
CLOSE_THR = 0.10


def ema(x, period):
    a = 2.0 / (period + 1)
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out


def trend_states(kind, close, low, high, lv, e20):
    n = len(close)
    MIN, Q25, FV, Q75, MAX = (lv[:, k] for k in range(5))
    st = np.zeros(n, np.int8)
    cur = 0
    for i in range(n):
        if np.isnan(MAX[i]):
            st[i] = cur
            continue
        if kind == "T_A":
            if close[i] > MAX[i]:
                cur = 1
            elif close[i] < MIN[i]:
                cur = -1
        elif kind == "T_B":
            if low[i] > MAX[i]:
                cur = 1
            elif high[i] < MIN[i]:
                cur = -1
        elif kind == "T_C":
            sl = e20[i] - e20[i - 1] if i else 0.0
            if close[i] > FV[i] and sl > 0:
                cur = 1
            elif close[i] < FV[i] and sl < 0:
                cur = -1
        elif kind == "T_D":
            if e20[i] > FV[i]:
                cur = 1
            elif e20[i] < FV[i]:
                cur = -1
        st[i] = cur
    return st


def run_member(bars, tr, P, C, H, X):
    n = bars["n"]
    o, h, l, c = bars["o"], bars["h"], bars["l"], bars["c"]
    t, lb = bars["t"], bars["lb"]
    lv = bars["lv"]
    MIN, Q25, FV, Q75, MAX = (lv[:, k] for k in range(5))
    trades = []
    pos = 0; epx = 0.0; ei = -1
    pe = 0; px = False
    ep_id = 0; cnt = {1: 0, -1: 0}; last_sig = {1: -10**9, -1: -10**9}
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
            ep_id += 1; cnt = {1: 0, -1: 0}
            prev_tr = ti
        # ---- Signal_Trade candidate ----
        sig = 0
        rng = h[i] - l[i]
        if ti != 0 and rng > 0:
            if ti > 0:
                rail = MAX[i] if P == "P_IN" else (Q75[i] if P == "P_Q75" else FV[i])
                touched = l[i] <= rail
                conf = (c[i] > o[i]) if C == "C_DIR" else (c[i] >= rail)
                clv = ((h[i] - c[i]) / rng <= CLOSE_THR) if H == "H1a" else ((c[i] - l[i]) / rng <= CLOSE_THR)
                if touched and conf and clv:
                    sig = 1
            else:
                rail = MIN[i] if P == "P_IN" else (Q25[i] if P == "P_Q75" else FV[i])
                touched = h[i] >= rail
                conf = (c[i] < o[i]) if C == "C_DIR" else (c[i] <= rail)
                clv = ((c[i] - l[i]) / rng <= CLOSE_THR) if H == "H1a" else ((h[i] - c[i]) / rng <= CLOSE_THR)
                if touched and conf and clv:
                    sig = -1
        if sig != 0:
            if cnt[sig] >= QTY_PER_TREND or (i - last_sig[sig]) < SPLIT:
                sig = 0
        # ---- exits ----
        if pos != 0:
            if X == "X_OPP":
                hit = sig == -pos
            elif X == "X_FLIP":
                hit = ti == -pos
            else:  # X_MED
                hit = (pos > 0 and c[i] < FV[i]) or (pos < 0 and c[i] > FV[i])
            if hit:
                if X == "X_OPP" and sig == -pos:
                    px = True
                    pe = sig            # SAR on opposite signal
                    cnt[sig] += 1; last_sig[sig] = i
                else:
                    px = True
                continue
        # ---- entries ----
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
    print("[r7] cloud ...", flush=True)
    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    e20 = ema(c, 20)
    bars = dict(n=len(seg), t=t, o=seg["open"].values, h=seg["high"].values,
                l=seg["low"].values, c=c, lb=lb, lv=lv)

    trends = {k: trend_states(k, c, bars["l"], bars["h"], lv, e20)
              for k in ("T_A", "T_B", "T_C", "T_D")}

    wins = []
    for r in tgt:
        lo = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        hi = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, lo, hi))

    metrics = W3 + W2 + W1
    gpath = os.path.join(OUT, "r7_grid.csv")
    g = open(gpath, "w", newline=""); gw = csv.writer(g)
    gw.writerow(["member", "window", "distance", "n", "tgt_n", "net", "tgt_net",
                 "wr", "hold", "ll", "fail_week_net"])
    summary = []
    members = [(T, P, C, H, X)
               for T in trends for P in ("P_IN", "P_Q75", "P_MED")
               for C in ("C_DIR", "C_REC") for H in ("H1a", "H1b")
               for X in ("X_OPP", "X_FLIP", "X_MED")]
    print(f"[r7] {len(members)} members x {len(wins)} windows", flush=True)
    for mi, (T, P, C, H, X) in enumerate(members):
        name = f"{T}|{P}|{C}|{H}|{X}"
        trl = run_member(bars, trends[T], P, C, H, X)
        dists = []; fail_net = None; nz = 0
        for r, lo, hi in wins:
            w = [x for x in trl if lo <= np.datetime64(x["et"]) <= hi]
            fp = fingerprint(w)
            if fp is None:
                gw.writerow([name, r["report_start"], "", 0, r["trades_all"], 0,
                             r["net_all"], "", "", "", ""])
                dists.append(2.0)
                continue
            nz += 1
            tgtm = {m: num(r.get(m)) for m in metrics}
            errs = {m: norm_err(m, fp.get(m), tgtm.get(m)) for m in metrics}
            d = distance(errs)
            dists.append(d)
            if r["report_start"] == "3/22/2026":
                fail_net = fp["net_all"]
            gw.writerow([name, r["report_start"], f"{d:.4f}", fp["trades_all"],
                         r["trades_all"], f"{fp['net_all']:.0f}", r["net_all"],
                         f"{fp['wr_all']:.1f}", f"{fp['avg_time_min_all']:.1f}",
                         f"{fp['largest_loss_all']:.0f}",
                         f"{fail_net:.0f}" if fail_net is not None else ""])
        md = float(np.mean(dists))
        summary.append((md, float(np.max(dists)), name, fail_net, nz, len(trl)))
        if mi % 24 == 0:
            print(f"  [{mi}/{len(members)}] {name} mean={md:.3f}", flush=True)
    g.close()
    summary.sort()
    print("\n=== top 15 members by mean §40 distance ===")
    print(f"{'member':>34} {'mean':>6} {'worst':>6} {'failwk_net':>10} {'wins':>4} {'ntr':>5}")
    for md, wd, name, fn, nz, ntr in summary[:15]:
        fq = "DQ" if (fn is not None and fn > 0) else ""
        print(f"{name:>34} {md:6.3f} {wd:6.3f} {fn if fn is not None else float('nan'):10.0f} {nz:4d} {ntr:5d} {fq}")
    print("\n=== bottom 3 ===")
    for md, wd, name, fn, nz, ntr in summary[-3:]:
        print(f"{name:>34} {md:6.3f} {wd:6.3f}")
    with open(os.path.join(OUT, "r7_summary.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["mean_dist", "worst_dist", "member", "fail_week_net", "windows_traded", "total_trades"])
        for row in summary:
            w.writerow(row)
    print("[r7] done", flush=True)


if __name__ == "__main__":
    main()
