"""OTR_R32 Part A (spec preregistered): the loss-mechanism diagnostic.

The only relationship that survived R31's out-of-sample extension is
    corr(ATR, HIS avg_loss) = -0.509 (17 windows) -> -0.515 (23 windows).
His average LOSS shrinks as volatility rises.  Our incumbent does the opposite (+0.775).

A FIXED hard stop predicts HIS sign to be POSITIVE: at higher volatility the stop is reached more
often, losses pile up at the cap and drag the average up.  So his negative sign implies the hard
stop is NOT his dominant loss mechanism.  This measures the stop-out share directly.
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from vf_core import vf_levels                                     # noqa: E402
from vf_layer_ab import layer_a                                   # noqa: E402
from run_r5_weekly import num                                     # noqa: E402
from run_r7_signal_id import ema, trend_states                    # noqa: E402
from run_r30c_exitfamilies import layer_b_exit                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R32_JOINT_ENTRY_EXIT", "out")
os.makedirs(OUT, exist_ok=True)
STOP = 130.0
CAP = 2600.0


def main():
    opp = {r["image_id"]: r for r in csv.DictReader(open(os.path.join(
        ROOT, "runs", "OTR_R30_ENTRY_EXIT_DECOMP", "out",
        "opportunity_by_window.csv"), encoding="utf-8"))}
    tgt = [r for r in csv.DictReader(open(os.path.join(
        ROOT, "research", "original_trader_reconstruction", "screenshot_forensics",
        "derived", "targets_weekly_2026V.csv"), encoding="utf-8")) if r["image_id"] in opp]

    print("=" * 96)
    print("A1 - HIS avg_loss as a fraction of the -$2,600 cap (17 windows with ATR available)")
    print("=" * 96)
    hisA, hisF, hisL = [], [], []
    print(f"{'window':<24}{'atr':>7}{'avg_loss':>10}{'/cap':>8}")
    for r in tgt:
        al = abs(num(r.get("avg_loss_all"))); a = float(opp[r["image_id"]]["atr14"])
        hisA.append(a); hisF.append(al / CAP); hisL.append(al)
        print(f"{r['report_start']}->{r['report_end']:<11}{a:>7.2f}{al:>10.0f}{al/CAP:>8.3f}")
    hisA, hisF, hisL = np.array(hisA), np.array(hisF), np.array(hisL)
    print(f"\n   his avg_loss/cap: min {hisF.min():.3f}  median {np.median(hisF):.3f}  "
          f"max {hisF.max():.3f}")
    print(f"   corr(ATR, his avg_loss)     = {np.corrcoef(hisA, hisL)[0,1]:+.3f}")
    print(f"   corr(ATR, his avg_loss/cap) = {np.corrcoef(hisA, hisF)[0,1]:+.3f}")

    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-11") & (df["time"] <= "2026-05-29 17:00")].reset_index(drop=True)
    t = seg["time"].values.astype("datetime64[s]")
    o, hi, lo, c = (seg[k].values.astype(float) for k in ("open", "high", "low", "close"))
    v = seg["volume"].values.astype(float)
    fb = np.zeros(len(seg), bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(len(seg), bool); lb[:-1] = fb[1:]; lb[-1] = True
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - np.roll(c, 1)), np.abs(lo - np.roll(c, 1))))
    tr[0] = hi[0] - lo[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values
    lv = vf_levels(t, c, v, 60, 5, lifecycle="anchor", formula="percentile_linear")
    bars = dict(n=len(seg), t=t, o=o, h=hi, l=lo, c=c, lb=lb, lv=lv)
    trend = trend_states("T_C", c, lo, hi, lv, ema(c, 20))
    sig = layer_a(bars, trend, "P_MED", "C_DIR", "H1a")
    wins = []
    for r in tgt:
        a = np.datetime64(pd.Timestamp(r["report_start"]) - pd.Timedelta(days=1)) + np.timedelta64(18, "h")
        b = np.datetime64(pd.Timestamp(r["report_end"])) + np.timedelta64(17, "h")
        wins.append((r, a, b))

    print("\n" + "=" * 96)
    print("A2 - stop-out share of LOSING trades, per exit family, and what it does to avg_loss")
    print("=" * 96)
    print(f"{'exit family':<20}{'avgLoss':>9}{'/cap':>7}{'stopShare':>11}"
          f"{'c(ATR,share)':>14}{'c(ATR,avgLoss)':>16}   matches his sign?")
    rows = []
    for fam, prm in (("X_OPP", None), ("X_TREND", None), ("X_FV", None), ("X_BAND", None),
                     ("X_TRAIL_PTS", 25), ("X_TRAIL_PTS", 50), ("X_TRAIL_PTS", 80),
                     ("X_TARGET", 60), ("X_TIMEOUT", 60)):
        trl = layer_b_exit(bars, trend, sig, atr, fam, prm)
        A, SH, AL = [], [], []
        for r, a, b in wins:
            w = [x for x in trl if a <= np.datetime64(x["et"]) <= b]
            L = [x for x in w if x["pnl"] <= 0]
            if len(L) < 4:
                continue
            A.append(float(opp[r["image_id"]]["atr14"]))
            SH.append(np.mean([1.0 if x["kind"] == "stop" else 0.0 for x in L]))
            AL.append(abs(np.mean([x["pnl"] for x in L])))
        A, SH, AL = np.array(A), np.array(SH), np.array(AL)
        cs = float(np.corrcoef(A, SH)[0, 1]); ca = float(np.corrcoef(A, AL)[0, 1])
        m = "YES" if ca < 0 else ""
        nm = f"{fam}{'' if prm is None else ' '+str(prm)}"
        print(f"{nm:<20}{AL.mean():>9.0f}{AL.mean()/CAP:>7.3f}{SH.mean():>11.3f}"
              f"{cs:>14.3f}{ca:>16.3f}   {m}")
        rows.append(dict(family=nm, avg_loss=round(float(AL.mean()), 1),
                         frac_of_cap=round(float(AL.mean() / CAP), 3),
                         stop_share=round(float(SH.mean()), 3),
                         corr_atr_stopshare=round(cs, 3), corr_atr_avgloss=round(ca, 3)))

    print("\n" + "=" * 96)
    print("VERDICT")
    print("=" * 96)
    print(f"   his corr(ATR, avg_loss) = {np.corrcoef(hisA, hisL)[0,1]:+.3f}   "
          f"his avg_loss/cap median = {np.median(hisF):.3f}")
    neg = [r for r in rows if r["corr_atr_avgloss"] < 0]
    print(f"   families reproducing his NEGATIVE sign: {len(neg)} of {len(rows)}")
    for r in neg:
        print(f"      {r['family']:<18} corr {r['corr_atr_avgloss']:+.3f}  "
              f"stop share {r['stop_share']:.3f}  avg_loss/cap {r['frac_of_cap']:.3f}")
    if not neg:
        print("      NONE.  A2's registered consequence fires: no exit mechanism explains the one")
        print("      regularity that survived out of sample, leaving an exposure/sizing law as the")
        print("      only remaining candidate for it.")
    lowcap = [r for r in rows if abs(r["frac_of_cap"] - np.median(hisF)) < 0.10]
    print(f"\n   families whose avg_loss/cap is within 0.10 of his median: {len(lowcap)}")
    for r in lowcap:
        print(f"      {r['family']:<18} {r['frac_of_cap']:.3f} vs his {np.median(hisF):.3f}")

    with open(os.path.join(OUT, "loss_mechanism.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
