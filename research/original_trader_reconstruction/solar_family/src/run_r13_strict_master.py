"""R13 (authorised by runs/OTR_R11_INVERSE/amendment_1.yaml):
master-window readout of the exit-comparison rule.

INCLUSIVE (close <= TrailingStop, campaign-1 V0 convention) vs
STRICT    (close <  TrailingStop, == exit only on a genuine trend flip)
crossed with the incumbent D-gate ON/OFF, over the trader's master backtest window.

PREREGISTERED PREDICTION (amendment_1): STRICT moves master trade count and average hold
TOWARD the EARLY_LONG target relative to INCLUSIVE. Incumbent INCLUSIVE fit on record:
n = 4598 (+5.7% vs the 4351 target), hold 95.56 min.
"""
import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams  # noqa: E402
import inverse_core as IC  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R11_INVERSE", "out")
os.makedirs(OUT, exist_ok=True)
PV = 20.0
BR = 20
COMM = 4.18

# EARLY_LONG master target (TARGET_WINDOWS.csv, evidence class A, screenshot-derived)
TGT = dict(n=4351, net=292000.0, wr=40.29, pf=1.18, dd=-32700.0, hold=94.0, tpd=8.26)


def run_master(bb, exit_strict, gate=True, X=1600.0, K=3, C=700.0, X2=2500.0,
               cap=20, cd=3, comm=COMM, stop_pts=None):
    """Incumbent CAND2 automaton with the exit comparison as a switch."""
    t, o, h, l, c = (bb[k] for k in ("t", "o", "h", "l", "c"))
    fb, lb, st, ts, n = (bb[k] for k in ("fb", "lb", "st", "ts", "n"))
    mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    soi = np.zeros(n, np.int64); cur = 0
    for i in range(n):
        if fb[i]:
            cur = i
        soi[i] = cur
    mo = ((t - t[soi]).astype("timedelta64[s]").astype(np.int64) // 60)

    trades = []; pos = 0; epx = 0.0; ei = -1; pe = 0; px = False; pr = 0
    cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; prior = 0.0; n_sess = 0
    last_exit = -10 ** 9

    def realize(i, p):
        nonlocal pos, cum, hi, n_sess, last_exit
        pnl = pos * (p - epx) * PV - comm
        trades.append(dict(d=pos, ei=ei, xi=i, pnl=pnl,
                           hold=float((t[i] - t[ei]).astype("timedelta64[s]")
                                      .astype(np.int64)) / 60.0))
        cum += pnl; hi = max(hi, cum)
        consec[pos] = consec[pos] + 1 if pnl <= 0 else 0
        n_sess += 1; last_exit = i; pos = 0

    def ok(d, i):
        if not gate:
            return True
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
            realize(i, o[i]); px = False
        if pr != 0:
            if pos != 0:
                realize(i, o[i])
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
                realize(i, c[i])
            px = False; pe = 0; pr = 0
            continue
        dec = not fb[i]
        if pos != 0 and stop_pts is not None:
            lvl = epx - pos * stop_pts
            if (l[i] <= lvl) if pos > 0 else (h[i] >= lvl):
                gapped = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                realize(i, o[i] if gapped else lvl)
                px = False; pe = 0; pr = 0
                continue
        if pos != 0 and not np.isnan(ts[i]):
            hit = (((pos > 0 and c[i] < ts[i]) or (pos < 0 and c[i] > ts[i]))
                   if exit_strict else
                   ((pos > 0 and c[i] <= ts[i]) or (pos < 0 and c[i] >= ts[i])))
            if hit:
                if dec and abs(sig) == 1 and np.sign(sig) == -pos and i >= BR:
                    pr = int(np.sign(sig))
                else:
                    px = True
                continue
        if pos == 0 and abs(sig) == 1 and i >= BR and dec and (i - last_exit) >= cd:
            pe = 1 if sig > 0 else -1
    return trades


def fp(trades, n_sessions):
    p = np.array([x["pnl"] for x in trades])
    hh = np.array([x["hold"] for x in trades])
    d = np.array([x["d"] for x in trades])
    w = p > 0
    eq = np.cumsum(p)
    dd = float((eq - np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]).min())
    return dict(n=len(p), net=float(p.sum()), wr=float(w.mean() * 100),
                pf=float(p[w].sum() / -p[~w].sum()), dd=dd, hold=float(hh.mean()),
                tpd=len(p) / n_sessions,
                n_long=int((d > 0).sum()), n_short=int((d < 0).sum()),
                avg_win=float(p[w].mean()), avg_loss=float(p[~w].mean()),
                largest_loss=float(p.min()))


def main():
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2023-01-02 18:00") &
             (df["time"] <= "2025-02-01 17:00")].reset_index(drop=True)
    bb = IC.prepare(seg, SolarWaveParams())
    ns = int(bb["fb"].sum())
    print(f"bars {bb['n']:,}  sessions {ns}  "
          f"{seg['time'].iloc[0]} .. {seg['time'].iloc[-1]}\n")
    print(f"TARGET (EARLY_LONG)   n={TGT['n']:>5} net={TGT['net']:>10,.0f} "
          f"wr={TGT['wr']:>5.2f} pf={TGT['pf']:>5.3f} dd={TGT['dd']:>9,.0f} "
          f"hold={TGT['hold']:>6.1f} tpd={TGT['tpd']:>5.2f}\n")
    rows = []
    hdr = (f"{'variant':<26} {'n':>5} {'dn%':>7} {'net':>11} {'wr':>6} {'pf':>6} "
           f"{'dd':>10} {'hold':>7} {'dhold%':>7} {'tpd':>5}")
    print(hdr); print("-" * len(hdr))
    for strict in (False, True):
        for gate in (True, False):
            tr = run_master(bb, exit_strict=strict, gate=gate)
            f = fp(tr, ns)
            name = f"{'STRICT' if strict else 'INCLUSIVE'}_{'gate' if gate else 'nogate'}"
            dn = 100 * (f["n"] - TGT["n"]) / TGT["n"]
            dh = 100 * (f["hold"] - TGT["hold"]) / TGT["hold"]
            print(f"{name:<26} {f['n']:>5} {dn:>+6.1f}% {f['net']:>11,.0f} "
                  f"{f['wr']:>6.2f} {f['pf']:>6.3f} {f['dd']:>10,.0f} "
                  f"{f['hold']:>7.2f} {dh:>+6.1f}% {f['tpd']:>5.2f}")
            rows.append(dict(variant=name, **{k: round(v, 4) for k, v in f.items()},
                             dn_pct=round(dn, 2), dhold_pct=round(dh, 2)))
    with open(os.path.join(OUT, "r13_master_exitrule.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    inc = next(r for r in rows if r["variant"] == "INCLUSIVE_gate")
    stc = next(r for r in rows if r["variant"] == "STRICT_gate")
    print("\n=== PREREGISTERED PREDICTION (amendment_1) ===")
    print(f"  |dn%|   INCLUSIVE {abs(inc['dn_pct']):.2f}  ->  STRICT {abs(stc['dn_pct']):.2f}  "
          f"{'TOWARD target (PASS)' if abs(stc['dn_pct']) < abs(inc['dn_pct']) else 'AWAY (FAIL)'}")
    print(f"  |dhold%| INCLUSIVE {abs(inc['dhold_pct']):.2f}  ->  STRICT {abs(stc['dhold_pct']):.2f}  "
          f"{'TOWARD target (PASS)' if abs(stc['dhold_pct']) < abs(inc['dhold_pct']) else 'AWAY (FAIL)'}")


if __name__ == "__main__":
    main()
