"""R8 part A: OTR-VF-CAND1 frozen cluster vs the three post-6/21 flagship
windows (TRUE OOS) + part B June TP overlay bound. No knobs touched."""
import csv
import json
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
import run_r7b_signal_id as R7B  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R8_JUNE2026", "out")
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(ROOT, "research", "original_trader_reconstruction", "data")

CLUSTER = [("T_C", "P_MED", "C_DIR", "H1a", "X_OPP", "none"),
           ("T_C", "P_MED", "C_DIR", "H1a", "X_OPP", "strong_only"),
           ("T_C", "P_Q75", "C_REC", "H1a", "X_OPP", "none"),
           ("T_D", "P_IN", "C_REC", "H1c", "X_FLIP", "none")]


def build_bars(csv_path, start, end):
    df = pd.read_csv(csv_path, parse_dates=["time"])
    df = df[(df["time"] >= start) & (df["time"] <= end)].reset_index(drop=True)
    t = df["time"].values.astype("datetime64[s]")
    fb = np.zeros(len(df), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(len(df), bool); lb[:-1] = fb[1:]; lb[-1] = True
    c = df["close"].values; v = df["volume"].values.astype(float)
    o = df["open"].values
    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    e20 = ema(c, 20)
    delta = np.sign(c - o) * v
    cvd = np.zeros(len(c)); run = 0.0
    for i in range(len(c)):
        if fb[i]:
            run = 0.0
        run += delta[i]; cvd[i] = run
    cs = np.zeros(len(c)); cs[20:] = cvd[20:] - cvd[:-20]
    return dict(n=len(df), t=t, o=o, h=df["high"].values, l=df["low"].values,
                c=c, lb=lb, lv=lv, cvd_slope=cs,
                post_upgrade=np.ones(len(df), bool)), e20


def main():
    tgt = {r["report_start"]: r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8"))}
    bars, e20 = build_bars(os.path.join(DATA, "nq0926_junjul2026_1m.csv"),
                           "2026-06-14", "2026-08-01")
    trends = {k: trend_states(k, bars["c"], bars["l"], bars["h"], bars["lv"], e20)
              for k in {m[0] for m in CLUSTER}}
    windows = [("6/21/2026", "2026-06-20 18:00", "2026-06-26 17:00"),
               ("6/28/2026", "2026-06-27 18:00", "2026-07-10 17:00"),
               ("7/12/2026", "2026-07-11 18:00", "2026-07-31 17:00")]
    metrics = W3 + W2 + W1
    out_rows = []
    print("=== R8-A: frozen cluster, TRUE OOS ===")
    for m in CLUSTER:
        name = "|".join(m)
        trl = R7B.run_member(bars, trends[m[0]], m[1], m[2], m[3], m[4], m[5])
        json.dump(trl, open(os.path.join(OUT, f"trades_{name.replace('|','_')}.json"), "w"),
                  default=str)
        for wn, lo, hi in windows:
            w = [x for x in trl if pd.Timestamp(lo) <= pd.Timestamp(x["et"]) <= pd.Timestamp(hi)]
            fp = fingerprint(w)
            r = tgt[wn]
            tgtm = {k: num(r.get(k)) for k in metrics}
            if fp is None:
                print(f"{name:>44} {wn:>10} NO TRADES")
                continue
            d = distance({k: norm_err(k, fp.get(k), tgtm.get(k)) for k in metrics})
            out_rows.append(dict(member=name, window=wn, dist=round(d, 4),
                                 n=fp["trades_all"], tgt_n=int(tgtm["trades_all"]),
                                 net=round(fp["net_all"]), tgt_net=round(tgtm["net_all"]),
                                 wr=round(fp["wr_all"], 1), hold=round(fp["avg_time_min_all"], 1),
                                 ll=round(fp["largest_loss_all"])))
            print(f"{name:>44} {wn:>10} d={d:.3f} n={fp['trades_all']}({int(tgtm['trades_all'])}) "
                  f"net={fp['net_all']:8.0f}({tgtm['net_all']:8.0f}) wr={fp['wr_all']:5.1f} "
                  f"hold={fp['avg_time_min_all']:5.1f} ll={fp['largest_loss_all']:6.0f}", flush=True)
    pd.DataFrame(out_rows).to_csv(os.path.join(OUT, "r8a_oos.csv"), index=False)

    # ---- part B: June TP overlay bound (H1 gross sum) ----
    print("\n=== R8-B: June TP overlay bound ===")
    lead = CLUSTER[0]
    trl = json.load(open(os.path.join(OUT, f"trades_{'_'.join(lead)}.json")))
    # CAND2-S sleeve on SEP26 (new180 era params, stop 65)
    sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                    "solar_family", "src"))
    from run_r5_weekly import build as s_build, run_m  # noqa: E402
    from solarwave import SolarWaveParams  # noqa: E402
    df = pd.read_csv(os.path.join(DATA, "nq0926_junjul2026_1m.csv"), parse_dates=["time"])
    df = df[(df["time"] >= "2026-06-14") & (df["time"] <= "2026-08-01")].reset_index(drop=True)
    bb = s_build(df, SolarWaveParams(offset_multiplier_stop=180.0, slowdown_scan=3,
                                     weak_weak_split=6, pullback_split=9))
    s_tr = run_m(bb, stop_pts=65)
    tp_windows = [("TP 6/14-6/18", "2026-06-13 18:00", "2026-06-18 17:00", 78, 42.31, 34.10)]
    for wn, lo, hi, tp_n, tp_wr, tp_hold in tp_windows:
        vf_w = [x for x in trl if pd.Timestamp(lo) <= pd.Timestamp(x["et"]) <= pd.Timestamp(hi)]
        s_w = [x for x in s_tr if pd.Timestamp(lo) <= pd.Timestamp(x["et"]) <= pd.Timestamp(hi)]
        n_sum = len(vf_w) + len(s_w)
        holds = [x["hold"] for x in vf_w + s_w]
        print(f"{wn}: VF-lead {len(vf_w)} + CAND2-S {len(s_w)} = {n_sum} vs TP n={tp_n}; "
              f"mean hold {np.mean(holds):.1f} vs TP {tp_hold}", flush=True)
    print("[r8] done")


if __name__ == "__main__":
    main()
