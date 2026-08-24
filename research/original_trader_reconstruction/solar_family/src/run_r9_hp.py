"""R9: hp-build identification — pullback-qualified (T2) entries vs T1 control
(runs/OTR_R9_HP_BUILD/spec.yaml). Frozen wrapper; entry_mode x era only."""
import csv
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solarwave import SolarWaveParams  # noqa: E402
from otr_engine import POINT_VALUE, BARS_REQUIRED  # noqa: E402
from run_r5_weekly import build, num, fingerprint, norm_err, distance, W3, W2, W1  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R9_HP_BUILD", "out")
os.makedirs(OUT, exist_ok=True)


def run_hp(bb, entry_abs=1, X=1600, K=3, C=700, X2=2500, cap=20, cd=3,
           stop_pts=65, comm=0.0):
    """Same automaton as R5 run_m; entry_abs selects the entering signal class
    (1 = T1 flips w/ reversal chains; 2 = T2 pullbacks, no reversal path)."""
    t, o, h, l, c, fb, lb, st, ts, mod, mo, n = (bb[k] for k in
        ("t", "o", "h", "l", "c", "fb", "lb", "st", "ts", "mod", "mo", "n"))
    trades = []; pos = 0; epx = 0.0; ei = -1; pe = 0; px = False; pr = 0
    cum = 0.0; hi = 0.0; consec = {1: 0, -1: 0}; prior = 0.0; n_sess = 0
    last_exit = -10**9

    def realize(i, p, kind):
        nonlocal pos, cum, hi, n_sess, last_exit
        pnl = pos * (p - epx) * POINT_VALUE - 2 * comm
        trades.append({"d": pos, "et": str(t[i - 0]) if False else str(t[ei]),
                       "xt": str(t[i]), "pnl": pnl, "xi": i, "kind": kind,
                       "hold": float((t[i] - t[ei]).astype("timedelta64[s]").astype(np.int64)) / 60.0})
        cum += pnl; hi = max(hi, cum)
        consec[pos] = consec[pos] + 1 if pnl <= 0 else 0
        n_sess += 1; last_exit = i; pos = 0

    def ok(d, i):
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
            realize(i, o[i], "flip"); px = False
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
        if pos != 0 and stop_pts is not None:
            lvl = epx - pos * stop_pts
            hit = (l[i] <= lvl) if pos > 0 else (h[i] >= lvl)
            if hit:
                gap_ = (o[i] <= lvl) if pos > 0 else (o[i] >= lvl)
                realize(i, o[i] if gap_ else lvl, "stop")
        sig = st[i]
        if lb[i]:
            if pos != 0:
                realize(i, c[i], "sc")
            px = False; pe = 0; pr = 0
            continue
        dec = not fb[i]
        if pos != 0 and not np.isnan(ts[i]):
            hitx = (pos > 0 and c[i] <= ts[i]) or (pos < 0 and c[i] >= ts[i])
            if hitx:
                if dec and abs(sig) == entry_abs and np.sign(sig) == -pos and i >= BARS_REQUIRED:
                    pr = int(np.sign(sig))
                else:
                    px = True
                continue
        if pos == 0 and abs(sig) == entry_abs and i >= BARS_REQUIRED and dec and (i - last_exit) >= cd:
            pe = 1 if sig > 0 else -1
    return trades


def main():
    tgt_rows = list(csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2025S.csv"), encoding="utf-8")))
    mach = {f"{r['report_start']}->{r['report_end']}":
            ("dev" if "machine dev" in r["notes"] else "hp") for r in tgt_rows}
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2025-06-15") & (df["time"] <= "2026-01-24 17:00")].reset_index(drop=True)

    P = {"old_L": SolarWaveParams(pullback_early=False),
         "old_E": SolarWaveParams(),
         "new_L": SolarWaveParams(offset_multiplier_stop=180.0, slowdown_scan=3,
                                  weak_weak_split=6, pullback_split=9, pullback_early=False),
         "new_E": SolarWaveParams(offset_multiplier_stop=180.0, slowdown_scan=3,
                                  weak_weak_split=6, pullback_split=9)}
    bb = {}
    for k, prm in P.items():
        print(f"[r9] wave {k}", flush=True)
        bb[k] = build(seg, prm)

    runsv = {}
    for pk in P:
        mode_tag = "T2L" if pk.endswith("_L") else "T2E"
        runsv[(pk, mode_tag)] = run_hp(bb[pk], entry_abs=2)
    # T1 control (mode-independent of early/late): use old_E and new_E streams
    runsv[("old_E", "T1")] = run_hp(bb["old_E"], entry_abs=1)
    runsv[("new_E", "T1")] = run_hp(bb["new_E"], entry_abs=1)

    metrics = W3 + W2 + W1
    rows = []
    gpath = os.path.join(OUT, "r9_grid.csv")
    g = open(gpath, "w", newline=""); gw = csv.writer(g)
    gw.writerow(["window", "mach", "member", "distance", "n", "tgt_n", "net",
                 "tgt_net", "wr", "tgt_wr", "avg_win", "tgt_avg_win", "hold", "tgt_hold"])
    for r in tgt_rows:
        d0, d1 = r["report_start"], r["report_end"]
        try:
            lo = np.datetime64(pd.Timestamp(d0) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
            hi_ = np.datetime64(pd.Timestamp(d1)) + np.timedelta64(17, "h")
        except Exception:
            continue
        wname = f"{d0}->{d1}"
        era = "old" if pd.Timestamp(d1) <= pd.Timestamp("2025-10-25") else "new"
        tgtm = {m: num(r.get(m)) for m in metrics + ["avg_win_all"]}
        for (pk, mode), trl in runsv.items():
            if not pk.startswith(era):
                continue
            w = [x for x in trl if lo <= np.datetime64(x["et"]) <= hi_]
            fp = fingerprint(w)
            if fp is None:
                continue
            d = distance({m: norm_err(m, fp.get(m), tgtm.get(m)) for m in metrics})
            rows.append(dict(window=wname, mach=mach[wname], member=mode, dist=d,
                             dn=(fp["trades_all"] - tgtm["trades_all"]) / tgtm["trades_all"]))
            gw.writerow([wname, mach[wname], mode, f"{d:.4f}", fp["trades_all"],
                         int(tgtm["trades_all"]), f"{fp['net_all']:.0f}", tgtm["net_all"],
                         f"{fp['wr_all']:.1f}", tgtm["wr_all"],
                         f"{fp['avg_win_all']:.0f}", tgtm["avg_win_all"],
                         f"{fp['avg_time_min_all']:.1f}", tgtm["avg_time_min_all"]])
    g.close()
    d = pd.DataFrame(rows)
    print("\n=== mean §40 distance by machine x member ===")
    print(d.groupby(["mach", "member"])["dist"].agg(["mean", "count"]).round(3).to_string())
    print("\n=== mean count error dn% by machine x member ===")
    print((d.groupby(["mach", "member"])["dn"].mean() * 100).round(1).to_string())
    print("\n=== D2: the two +18.5k hp weeks ===")
    for _, r in pd.read_csv(gpath).iterrows():
        if r["window"] in ("11/2/2025->11/7/2025", "11/16/2025->11/21/2025"):
            print(f"  {r['window']} {r['member']:>4} n={r['n']}({r['tgt_n']}) net={r['net']}({r['tgt_net']}) "
                  f"wr={r['wr']}({r['tgt_wr']}) aw={r['avg_win']}({r['tgt_avg_win']})")


if __name__ == "__main__":
    main()
